from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.schemas.me import MeUpdateRequest


async def update(db: AsyncSession, request: MeUpdateRequest, user: User) -> User:
    for key, value in request.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 사용 중인 닉네임입니다.")
    return user


async def delete(db: AsyncSession, user: User) -> None:
    try:
        await db.delete(user)
        await db.commit()
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="일시적으로 서비스를 이용할 수 없습니다. 잠시 후 다시 시도해주세요.",
        )
