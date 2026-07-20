from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.products.models import Product


async def test_products_delete_success(
    client: AsyncClient, db: AsyncSession, admin_user: User, product: Product
) -> None:
    login_response = await client.post("/api/v1/auth/login", json={"email": admin_user.email, "password": "Password@1"})
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.delete(f"/api/v1/products/{product.id}", headers=headers)
    assert response.status_code == 204
    result = await db.execute(select(Product).where(Product.id == product.id))
    assert result.scalar_one_or_none() is None


async def test_products_delete_forbidden_for_non_admin(
    client: AsyncClient, normal_user: User, product: Product
) -> None:
    login_response = await client.post(
        "/api/v1/auth/login", json={"email": normal_user.email, "password": "Password@1"}
    )
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.delete(f"/api/v1/products/{product.id}", headers=headers)
    assert response.status_code == 403


async def test_products_delete_unauthorized(client: AsyncClient, product: Product) -> None:
    response = await client.delete(f"/api/v1/products/{product.id}")
    assert response.status_code == 401


async def test_products_delete_not_found_product(client: AsyncClient, admin_user: User) -> None:
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "Password@1"},
    )
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.delete("/api/v1/products/wrong", headers=headers)
    assert response.status_code == 404
