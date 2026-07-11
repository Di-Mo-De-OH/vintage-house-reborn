from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Session, SessionTransaction

from app.core.database import engine, get_db
from app.main import app


@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with engine.connect() as connection:
        await connection.begin()
        await connection.begin_nested()

        session_factory = async_sessionmaker(bind=connection, expire_on_commit=False, class_=AsyncSession)
        session = session_factory()

        @event.listens_for(session.sync_session, "after_transaction_end")
        def restart_savepoint(sess: Session, transaction: SessionTransaction) -> None:
            if transaction.nested and not transaction._parent.nested:
                sess.begin_nested()

        yield session

        await session.close()
        await connection.rollback()


@pytest.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as ac:
        yield ac
    app.dependency_overrides.clear()
