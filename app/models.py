# ------ IMPORTS ------
from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Float, JSON, Boolean
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
    save: Mapped["Save"] = relationship(back_populates = "user", cascade = "all, delete-orphan")

class Codes(Base):
    __tablename__ = "codes"

    login_code: Mapped[str] = mapped_column(String, unique = True, primary_key = True, index = True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone = True), nullable = False)
    os: Mapped[str] = mapped_column(String(25), nullable = False)
    country: Mapped[str] = mapped_column(String(32), nullable = False)

class Save(Base):
    __tablename__ = "saves"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key = True)
    user: Mapped[User] = relationship(back_populates = "save")
    save_id: Mapped[str] = mapped_column(String(SAVE_ID_LENGTH), nullable = False)

    biscuits: Mapped[float] = mapped_column(Float)
    total_biscuits: Mapped[float] = mapped_column(Float)
    total_playtime: Mapped[float] = mapped_column(Float)
    total_clicks: Mapped[int] = mapped_column(Integer)
    owned_upgrades: Mapped[dict[str, int]] = mapped_column(JSON)
    owned_achievements: Mapped[list[str]] = mapped_column(JSON)
    prestige: Mapped[int] = mapped_column(Integer)
    crumbs: Mapped[int] = mapped_column(Integer)
    owned_unlocks: Mapped[list[str]] = mapped_column(JSON)

class Session(Base):    
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, index = True)    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index = True)
    token_hash: Mapped[str] = mapped_column(String(64), nullable = False, index = True)    
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone = True), nullable = False)    
    expired: Mapped[bool] = mapped_column(Boolean, nullable = False)

    # os: Mapped[str] = mapped_column(String(25), nullable = False)
    # country: Mapped[str] = mapped_column(String(32), nullable = False)