# ------ IMPORTS ------
from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Float, JSON, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.constants import (
    USERNAME_MAX_LENGTH,
    EMAIL_MAX_LENGTH,
    PASSWORD_HASH_MAX_LENGTH,
    SAVE_ID_LENGTH
)

# ------ TABLES ------
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, index = True)
    username: Mapped[str] = mapped_column(String(USERNAME_MAX_LENGTH), unique = True, nullable = False)
    email: Mapped[str] = mapped_column(String(EMAIL_MAX_LENGTH), unique = True, nullable = False)
    password_hash: Mapped[str] = mapped_column(String(PASSWORD_HASH_MAX_LENGTH), nullable = False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone = True), default = lambda: datetime.now(UTC))
    saves: Mapped[list["Save"]] = relationship(back_populates = "user", cascade = "all, delete-orphan")

class Codes(Base):
    __tablename__ = "codes"

    login_code: Mapped[str] = mapped_column(String, unique = True, primary_key = True, index = True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone = True), nullable = False)
    os: Mapped[str] = mapped_column(String(25), nullable = False)
    country: Mapped[str] = mapped_column(String(32), nullable = False)
    game_id: Mapped[str] = mapped_column(String(32), nullable = False)

class Save(Base):
    __tablename__ = "saves"

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    user: Mapped[User] = relationship(back_populates = "saves")
    save_id: Mapped[str] = mapped_column(String(SAVE_ID_LENGTH), nullable = False)
    last_saved_at: Mapped[datetime] = mapped_column(DateTime(timezone = True), default = lambda: datetime.now(UTC))
    version_number: Mapped[float] = mapped_column(Float, default = 0.0)
    game_id: Mapped[str] = mapped_column(String(32), nullable = False)

    save_data: Mapped[dict] = mapped_column(JSON)

    __table_args__ = (UniqueConstraint("user_id", "game_id"),)

class Session(Base):    
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, index = True)    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index = True)
    token_hash: Mapped[str] = mapped_column(String(64), nullable = False, index = True)    
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone = True), nullable = False)    
    expired: Mapped[bool] = mapped_column(Boolean, nullable = False)