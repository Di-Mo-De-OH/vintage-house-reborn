from datetime import datetime, timedelta, timezone

from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import RefreshToken, User
from app.auth.schemas.login_logout import LoginRequest, LoginResponse
from app.core.config import settings
from app.core.utils.security import create_access_token, generate_refresh_token, hash_refresh_token, verify_password

SERVICE_UNAVAILABLE_DETAIL = "일시적으로 서비스를 이용할 수 없습니다. 잠시 후 다시 시도해주세요."


async def login(db: AsyncSession, request: LoginRequest) -> tuple[LoginResponse, str]:
    try:
        result = await db.execute(select(User).where(User.email == request.email))
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=SERVICE_UNAVAILABLE_DETAIL)

    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="아이디 또는 비밀번호가 틀렸습니다.")

    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="아이디 또는 비밀번호가 틀렸습니다.")

    access_token = create_access_token(user_id=user.id)
    refresh_token = generate_refresh_token()

    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(refresh_token),
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
    )
    try:
        await db.commit()
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=SERVICE_UNAVAILABLE_DETAIL)

    return LoginResponse(access_token=access_token), refresh_token


async def logout(db: AsyncSession, refresh_token: str | None) -> None:
    if refresh_token is None:
        return
    try:
        await db.execute(delete(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(refresh_token)))
        await db.commit()
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="일시적으로 서비스를 이용할 수 없습니다. 잠시 후 다시 시도해주세요.",
        )
