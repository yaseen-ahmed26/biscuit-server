# ------ IMPORTS ------
from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
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

class Codes(Base):
    __tablename__ = "codes"

    session_id: Mapped[str] = mapped_column(String, primary_key = True, index = True)
    login_code: Mapped[str] = mapped_column(String, unique = True, nullable = False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone = True), nullable = False)