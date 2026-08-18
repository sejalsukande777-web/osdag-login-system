import os
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, RevokedToken
from app.schemas import UserRegister, UserLogin, UserOut, TokenResponse
from app.auth import hash_password, verify_password, create_access_token, get_token_payload

router = APIRouter(prefix="/auth", tags=["auth"])

MAX_FAILED_LOGIN_ATTEMPTS = int(os.getenv("MAX_FAILED_LOGIN_ATTEMPTS", "5"))
LOCKOUT_MINUTES = int(os.getenv("LOCKOUT_MINUTES", "15"))

# using the same error message for every failure case (wrong password, no such
# email, account locked) so people can't figure out which emails are registered
GENERIC_LOGIN_ERROR = "Invalid email or password."


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        # not saying "email already registered" here on purpose, same reasoning as login
        raise HTTPException(status_code=400, detail="Unable to register with these details.")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    # if locked out, still throw the same generic error (not "account locked",
    # that would tell an attacker they've got a valid email)
    if user and user.lockout_until and user.lockout_until > datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=GENERIC_LOGIN_ERROR)

    if not user or not verify_password(payload.password, user.hashed_password):
        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= MAX_FAILED_LOGIN_ATTEMPTS:
                user.lockout_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_MINUTES)
                user.failed_login_attempts = 0  # reset so it doesn't just keep climbing
            db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=GENERIC_LOGIN_ERROR)

    # good login, clear out any failed attempts from before
    user.failed_login_attempts = 0
    user.lockout_until = None
    db.commit()

    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(payload: dict = Depends(get_token_payload), db: Session = Depends(get_db)):
    # a JWT is normally valid until it expires no matter what, so just deleting it
    # on the frontend isn't a real logout - someone could still replay the token.
    # storing the jti here means every future request gets checked against this
    # table and rejected even though the token itself hasn't technically expired yet
    jti = payload.get("jti")
    expires_at = datetime.utcfromtimestamp(payload.get("exp"))

    if not db.query(RevokedToken).filter(RevokedToken.jti == jti).first():
        db.add(RevokedToken(jti=jti, expires_at=expires_at))
        db.commit()

    return {"detail": "Logged out successfully."}
