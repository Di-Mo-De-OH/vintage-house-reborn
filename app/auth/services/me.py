from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
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
