from httpx import AsyncClient

from app.auth.models import User
from app.products.models import Product
from tests.utils import login


async def test_add_cart(client: AsyncClient, test_user: User, product: Product) -> None:
    headers = await login(client, test_user)
    response = await client.post(
        f"/api/v1/cart/{product.id}",
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["name"] == product.name


async def test_add_cart_unauthorized(client: AsyncClient, product: Product) -> None:
    response = await client.post(
        f"/api/v1/cart/{product.id}",
    )
    assert response.status_code == 401


async def test_add_cart_product_not_found(client: AsyncClient, test_user: User, product: Product) -> None:
    headers = await login(client, test_user)
    response = await client.post(
        "/api/v1/cart/wrong",
        headers=headers,
    )
    assert response.status_code == 404


async def test_add_cart_product_sold_out(client: AsyncClient, test_user: User, sold_out_product: Product) -> None:
    headers = await login(client, test_user)
    response = await client.post(
        f"/api/v1/cart/{sold_out_product.id}",
        headers=headers,
    )
    assert response.status_code == 400
