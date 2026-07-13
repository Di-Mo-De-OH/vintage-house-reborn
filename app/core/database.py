from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import DateTime, String, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from ulid import ULID

from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)
#  echo=True: ORM이 실행하는 실제 SQL 쿼리를 로그로 출력

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class BaseModel(DeclarativeBase):
    id: Mapped[str] = mapped_column(String(26), primary_key=True, default=lambda: str(ULID()))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


DbSession = Annotated[AsyncSession, Depends(get_db)]
