import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings


def generate_6digits_safe() -> str:
    """6자리 인증코드 발급을 위한 함수"""
    return f"{secrets.randbelow(1000000):06d}"


def generate_token() -> str:
    """email_token 발급을 위한 함수"""
    return secrets.token_urlsafe(24)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


def create_access_token(user_id: str) -> str:
    """기존 jwt 방식을 사용한 access_token 생성 함수"""
    expire_time = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire_time, "user_id": user_id}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def generate_refresh_token() -> str:
    """refresh_token 생성을 위한 무작위 문자열"""
    return secrets.token_urlsafe(32)


def hash_refresh_token(token: str) -> str:
    """refresh_token 해쉬화 함수"""
    return hashlib.sha256(token.encode()).hexdigest()
