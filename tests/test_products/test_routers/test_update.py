from httpx import AsyncClient

from app.auth.models import User
from app.products.models import Product
from tests.utils import login


async def test_update_success(client: AsyncClient, admin_user: User, product: Product) -> None:
    headers = await login(client, admin_user)

    response = await client.patch(
        f"/api/v1/products/{product.id}",
        headers=headers,
        json={
            "name": "update Product",
            "description": "update Product",
            "size": "small",
            "price": 100,
            "image_keys": ["products/updated_test1.jpg", "products/updated_test2.jpg"],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "update Product"
    assert body["description"] == "update Product"
    assert body["size"] == "small"
    assert body["price"] == 100
    assert [image["key"] for image in body["images"]] == [
        "products/updated_test1.jpg",
        "products/updated_test2.jpg",
    ]
    assert body["category"] == product.category


async def test_update_forbidden_for_non_admin(client: AsyncClient, normal_user: User, product: Product) -> None:
    headers = await login(client, normal_user)
    response = await client.patch(
        f"/api/v1/products/{product.id}",
        headers=headers,
        json={
            "name": "update Product",
        },
    )
    assert response.status_code == 403


async def test_update_unauthorized(client: AsyncClient, product: Product) -> None:
    response = await client.patch(
        f"/api/v1/products/{product.id}",
        json={
            "name": "update Product",
        },
    )
    assert response.status_code == 401


async def test_update_non_product(client: AsyncClient, admin_user: User, product: Product) -> None:
    headers = await login(client, admin_user)
    response = await client.patch(
        "/api/v1/products/worng.id",
        headers=headers,
        json={
            "name": "update Product",
        },
    )
    assert response.status_code == 404


async def test_update_one_product_change(client: AsyncClient, admin_user: User, product: Product) -> None:
    headers = await login(client, admin_user)
    response = await client.patch(
        f"/api/v1/products/{product.id}",
        headers=headers,
        json={
            "name": "update Product",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "update Product"
    assert body["description"] == "description"
    assert body["size"] == "large"
    assert body["price"] == 10000
    assert body["brand"] == "brand"
    assert body["category"] == product.category
    assert [image["key"] for image in body["images"]] == [
        "products/test1.jpg",
        "products/test2.jpg",
    ]


async def test_update_invalid(client: AsyncClient, admin_user: User, product: Product) -> None:
    headers = await login(client, admin_user)
    response = await client.patch(
        f"/api/v1/products/{product.id}",
        headers=headers,
        json={"category": "상의"},
    )
    assert response.status_code == 422
