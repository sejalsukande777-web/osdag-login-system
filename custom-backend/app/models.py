import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Login security tracking
    failed_login_attempts = Column(Integer, default=0)
    lockout_until = Column(DateTime, nullable=True)

    files = relationship("UserFile", back_populates="owner", cascade="all, delete-orphan")


class UserFile(Base):
    # keeping this simple - just text content in the db instead of actual file
    # uploads/storage, since the task says seeded sample files are fine
    __tablename__ = "user_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    content = Column(Text, nullable=True)  # simple text content standing in for file bytes
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="files")


class RevokedToken(Base):
    # keeps track of tokens that got logged out. every request checks this table
    # so a logged-out token actually stops working instead of just being ignored
    # by the frontend
    __tablename__ = "revoked_tokens"

    jti = Column(String, primary_key=True)
    revoked_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)  # so old rows can get cleaned up later
