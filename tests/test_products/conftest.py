import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.core.utils.security import hash_password
from app.products.models import Category, Product, ProductImage, Status


@pytest.fixture
async def admin_user(db: AsyncSession) -> User:
    user = User(
        email="admin@example.com",
        hashed_password=hash_password("Password@1"),
        name="admin",
        nickname="admin",
        is_admin=True,
    )
    db.add(user)
    await db.commit()
    return user


@pytest.fixture
async def normal_user(db: AsyncSession) -> User:
    user = User(
        email="user@example.com",
        hashed_password=hash_password("Password@1"),
        name="user",
        nickname="user",
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

    for order_number, key in enumerate(["products/test1.jpg", "products/test2.jpg"]):
        db.add(ProductImage(product_id=product.id, image_url=key, order_number=order_number))
    await db.commit()
    return product


@pytest.fixture
async def hidden_product(db: AsyncSession) -> Product:
    product = Product(
        name="product",
        description="description",
        size="large",
        price=10000,
        brand="brand",
        category=Category.TOP,
        status=Status.HIDDEN,
    )
    db.add(product)
    await db.commit()

    for order_number, key in enumerate(["products/test1.jpg", "products/test2.jpg"]):
        db.add(ProductImage(product_id=product.id, image_url=key, order_number=order_number))
    await db.commit()
    return product


@pytest.fixture
async def product_without_image(db: AsyncSession) -> Product:
    product = Product(
        name="no image product",
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
