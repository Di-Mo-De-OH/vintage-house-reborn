from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.products.models import Category, Product, Status


async def test_products_read_success(
    client: AsyncClient,
    product: Product,
) -> None:
    response = await client.get("api/v1/products")
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["id"] == product.id
    assert body["items"][0]["name"] == product.name
    assert body["items"][0]["thumbnail"] is not None
    assert body["next_cursor"] is None


async def test_products_read_none_item(
    client: AsyncClient,
) -> None:
    response = await client.get("/api/v1/products")
    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["next_cursor"] is None


async def test_products_read_status_hidden(
    client: AsyncClient,
    hidden_product: Product,
) -> None:
    response = await client.get("/api/v1/products")
    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["next_cursor"] is None


async def test_products_read_without_images(
    client: AsyncClient,
    product_without_image: Product,
) -> None:
    response = await client.get("/api/v1/products")
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["id"] == product_without_image.id
    assert body["items"][0]["thumbnail"] is None


async def test_products_read_pagination(
    db: AsyncSession,
    client: AsyncClient,
) -> None:
    for i in range(3):
        db.add(
            Product(
                name=f"product{i}",
                description="description",
                size="large",
                price=10000,
                brand="brand",
                category=Category.TOP,
                status=Status.ON_SALE,
            )
        )
    await db.commit()

    first_response = await client.get("/api/v1/products", params={"limit": 2})
    assert first_response.status_code == 200
    first_body = first_response.json()
    assert len(first_body["items"]) == 2
    assert first_body["next_cursor"] is not None
    second_response = await client.get("/api/v1/products", params={"limit": 2, "cursor": first_body["next_cursor"]})
    assert second_response.status_code == 200
    second_body = second_response.json()
    assert len(second_body["items"]) == 1
    assert second_body["next_cursor"] is None

    first_ids = {item["id"] for item in first_body["items"]}
    second_ids = {item["id"] for item in second_body["items"]}
    assert first_ids.isdisjoint(second_ids)
