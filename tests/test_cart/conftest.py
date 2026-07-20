from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.core.redis import redis_client
from app.core.utils.security import hash_password
from app.products.models import Category, Product, Status


@pytest.fixture(autouse=True)
async def cleanup_redis() -> AsyncGenerator[None, None]:
    yield
    async for key in redis_client.scan_iter("cart:*"):
        await redis_client.delete(key)


@pytest.fixture
async def test_user(db: AsyncSession) -> User:
    user = User(
        email="cart_user@example.com",
        hashed_password=hash_password("Password@1"),
        name="tester",
        nickname="carttester",
    )
    db.add(user)
    await db.commit()
    return user


@pytest.fixture
async def product(db: AsyncSession) -> Product:
    product = Product(
        name="product",
        description="description",
        size="large",
        price=10000,
        brand="brand",
        category=Category.TOP,
        status=Status.ON_SALE,
    )
    db.add(product)
    await db.commit()
    return product


@pytest.fixture
async def sold_out_product(db: AsyncSession) -> Product:
    product = Product(
        name="sold out product",
        description="description",
        size="large",
        price=10000,
        brand="brand",
        category=Category.TOP,
        status=Status.SOLD_OUT,
    )
    db.add(product)
    await db.commit()
    return product
