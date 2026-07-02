from collections.abc import AsyncGenerator
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from app.core.config import settings
from ulid import ULID
from sqlalchemy import String, DateTime, func

engine = create_async_engine(settings.DATABASE_URL, echo=True)
# 실제로 어떤 db에 연결할지 나타냄 echo 값은 orm 발생시 어떤 로우 쿼리를 발생시키는지 보여줌

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class BaseModel(DeclarativeBase):
    id: Mapped[str] = mapped_column(
        String(26), primary_key=True, default=lambda: str(ULID())
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
