from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import BaseModel


class User(BaseModel):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255))
    nickname: Mapped[str] = mapped_column(String(255), unique=True)
    address: Mapped[str | None] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"))


class RefreshToken(BaseModel):
    __tablename__ = "refresh_tokens"
    user_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(
        String(255),
        index=True,
        unique=True,
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
