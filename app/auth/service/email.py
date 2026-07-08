import aiosmtplib
from fastapi import HTTPException, status
from redis.exceptions import RedisError
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.redis import EmailRedis
from app.auth.schemas import VerifyEmailResponse
from app.core.redis import redis_client
from app.core.utils.email import send_email
from app.core.utils.security import generate_6digits_safe, generate_token

CODE_EXPIRE_SECONDS = 5 * 60
VERIFY_EXPIRE_SECONDS = 10 * 60
RESEND_COOLDOWN_SECONDS = 60


async def send_verification_email(email: str) -> None:
    code = generate_6digits_safe()
    try:
        if await redis_client.exists(EmailRedis.cooldown(email)):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="잠시 후 다시 시도해주세요.",
            )

        await redis_client.set(EmailRedis.code(email), code, ex=CODE_EXPIRE_SECONDS)
        await redis_client.set(
            EmailRedis.cooldown(email), "1", ex=RESEND_COOLDOWN_SECONDS
        )
    except RedisError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="일시적으로 서비스를 이용할 수 없습니다. 잠시 후 다시 시도해주세요.",
        )
    try:
        await send_email(
            to=email,
            subject="[빈티지 하우스 리본] 이메일 인증 코드",
            body=f"인증 코드: {code}\n5분 이내에 입력해주세요.",
        )
    except aiosmtplib.SMTPException:
        await redis_client.delete(EmailRedis.code(email))
        await redis_client.delete(EmailRedis.cooldown(email))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="이메일 발송에 실패했습니다. 잠시 후 다시 시도해주세요.",
        )


async def verify_email(db: AsyncSession, email: str, code: str) -> VerifyEmailResponse:
    try:
        verify_code = await redis_client.get(EmailRedis.code(email))
    except RedisError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="일시적으로 서비스를 이용할 수 없습니다. 잠시 후 다시 시도해주세요.",
        )

    if verify_code is None or verify_code != code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="입력해 주신 코드가 다릅니다.",
        )
    try:
        user = await db.execute(select(User).where(User.email == email))
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="일시적으로 서비스를 이용할 수 없습니다. 잠시 후 다시 시도해주세요.",
        )

    if user.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 가입된 이메일 입니다.",
        )

    token = generate_token()
    try:
        await redis_client.set(
            EmailRedis.verify(token), email, ex=VERIFY_EXPIRE_SECONDS
        )
        await redis_client.delete(EmailRedis.code(email))
        await redis_client.delete(EmailRedis.cooldown(email))
    except RedisError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="일시적으로 서비스를 이용할 수 없습니다. 잠시 후 다시 시도해주세요.",
        )
    return VerifyEmailResponse(verify_token=token)
