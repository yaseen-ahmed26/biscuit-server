# ------ IMPORTS ------
from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Float, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

# ------ TABLES ------
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, index = True)
    username: Mapped[str] = mapped_column(String(30), unique = True, nullable = False)
    email: Mapped[str] = mapped_column(String(60), unique = True, nullable = False)
    password_hash: Mapped[str] = mapped_column(String(200), nullable = False)
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
    save_id: Mapped[str] = mapped_column(String(32), nullable = False)

    biscuits: Mapped[float] = mapped_column(Float)
    total_biscuits: Mapped[float] = mapped_column(Float)
    total_playtime: Mapped[float] = mapped_column(Float)
    total_clicks: Mapped[int] = mapped_column(Integer)
    bought_upgrades: Mapped[dict[str, int]] = mapped_column(JSON)
    completed_achievements: Mapped[list[str]] = mapped_column(JSON)

class Session(Base):    
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, index = True)    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index = True)
    token_hash: Mapped[str] = mapped_column(String(64), nullable = False, index = True)    
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone = True), nullable = False)    
    expired: Mapped[bool] = mapped_column(Boolean, nullable = False)

    os: Mapped[str] = mapped_column(String(25), nullable = False)
    country: Mapped[str] = mapped_column(String(32), nullable = False)