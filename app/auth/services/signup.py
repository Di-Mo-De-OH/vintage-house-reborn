from fastapi import HTTPException, status
from redis.exceptions import RedisError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.schemas.signup import SignUpRequest
from app.auth.utils.redis import EmailRedis
from app.core.redis import redis_client
from app.core.utils.security import hash_password


async def signup(db: AsyncSession, request: SignUpRequest) -> User:
    try:
        email = await redis_client.get(EmailRedis.verify(request.verify_token))
    except RedisError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="일시적으로 서비스를 이용할 수 없습니다. 잠시 후 다시 시도해주세요.",
        )
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="이메일 인증이 필요합니다.",
        )
    password = hash_password(request.password)
    user = User(
        email=email, hashed_password=password, nickname=request.nickname, name=request.name, address=request.address
    )
    db.add(user)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 사용 중인 닉네임 입니다.")
    await redis_client.delete(EmailRedis.verify(request.verify_token))
    return user
