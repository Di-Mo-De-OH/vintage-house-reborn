from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.products.models import Category, Product, Status
from tests.utils import login


async def test_cart(client: AsyncClient, test_user: User, product: Product) -> None:
    headers = await login(client, test_user)
    await client.post(f"/api/v1/cart/{product.id}", headers=headers)
    response = await client.get("/api/v1/cart", headers=headers)
    assert response.status_code == 200

    body = response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["name"] == product.name
    assert body["items"][0]["price"] == product.price
    assert body["total_price"] == product.price


async def test_cart_empty(client: AsyncClient, test_user: User) -> None:
    headers = await login(client, test_user)
    response = await client.get("/api/v1/cart", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total_price"] == 0


async def test_cart_unauthorized(client: AsyncClient) -> None:
    response = await client.get("/api/v1/cart")
    assert response.status_code == 401


async def test_cart_multiple_items_total_price(
    client: AsyncClient, db: AsyncSession, test_user: User, product: Product
) -> None:
    product2 = Product(
        name="product2",
        description="description",
        size="medium",
        price=20000,
        brand="brand2",
        category=Category.BOTTOM,
        status=Status.ON_SALE,
    )
    db.add(product2)
    await db.commit()

    headers = await login(client, test_user)
    await client.post(f"/api/v1/cart/{product.id}", headers=headers)
    await client.post(f"/api/v1/cart/{product2.id}", headers=headers)

    response = await client.get("/api/v1/cart", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 2
    assert body["total_price"] == product.price + product2.price


async def test_cart_excludes_item_sold_out_after_adding(
    client: AsyncClient, db: AsyncSession, test_user: User, product: Product
) -> None:
    headers = await login(client, test_user)
    await client.post(f"/api/v1/cart/{product.id}", headers=headers)

    product.status = Status.SOLD_OUT
    await db.commit()

    response = await client.get("/api/v1/cart", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total_price"] == 0
