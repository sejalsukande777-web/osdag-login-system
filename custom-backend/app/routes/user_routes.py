from fastapi import APIRouter, Depends

from app.models import User
from app.schemas import UserOut
from app.auth import get_current_user

router = APIRouter(tags=["users"])


@router.get("/me", response_model=UserOut)
def read_own_profile(current_user: User = Depends(get_current_user)):
    # no user_id param here on purpose - who you are comes only from the token,
    # so there's no way to pass in someone else's id and get their profile back
    return current_user
