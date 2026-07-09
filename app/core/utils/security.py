import secrets

import bcrypt


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
