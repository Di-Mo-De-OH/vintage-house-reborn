from httpx import AsyncClient

from app.auth.models import User
from app.products.models import Category


async def test_create_success(client: AsyncClient, admin_user: User) -> None:
    login_response = await client.post("/api/v1/auth/login", json={"email": admin_user.email, "password": "Password@1"})
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    response = await client.post(
        "/api/v1/products",
        headers=headers,
        json={
            "name": "Test Product",
            "description": "Test Product",
            "size": "large",
            "category": Category.TOP,
            "price": 10000,
            "brand": "nike",
            "image_keys": ["products/test1.jpg", "products/test2.jpg"],
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Test Product"
    assert body["image_keys"] == ["products/test1.jpg", "products/test2.jpg"]


async def test_create_forbidden_for_non_admin(client: AsyncClient, normal_user: User) -> None:
    login_response = await client.post(
        "/api/v1/auth/login", json={"email": normal_user.email, "password": "Password@1"}
    )
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.post(
        "/api/v1/products",
        headers=headers,
        json={
            "name": "Test Product",
            "description": "Test Product",
            "size": "large",
            "category": Category.TOP,
            "price": 10000,
            "brand": "nike",
            "image_keys": ["products/test1.jpg", "products/test2.jpg"],
        },
    )
    assert response.status_code == 403


async def test_create_unauthorized(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/products",
        json={
            "name": "Test Product",
            "description": "Test Product",
            "size": "large",
            "category": Category.TOP,
            "price": 10000,
            "brand": "nike",
            "image_keys": ["products/test1.jpg", "products/test2.jpg"],
        },
    )
    assert response.status_code == 401


async def test_create_invalid_category(client: AsyncClient, admin_user: User) -> None:
    login_response = await client.post("/api/v1/auth/login", json={"email": admin_user.email, "password": "Password@1"})
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.post(
        "/api/v1/products",
        headers=headers,
        json={
            "name": "Test Product",
            "description": "Test Product",
            "size": "large",
            "price": 10000,
            "brand": "nike",
            "image_keys": ["products/test1.jpg", "products/test2.jpg"],
        },
    )
    assert response.status_code == 422


async def test_create_invalid_image_keys(client: AsyncClient, admin_user: User) -> None:
    login_response = await client.post("/api/v1/auth/login", json={"email": admin_user.email, "password": "Password@1"})
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.post(
        "/api/v1/products",
        headers=headers,
        json={
            "name": "Test Product",
            "description": "Test Product",
            "size": "large",
            "price": 10000,
            "brand": "nike",
            "category": Category.TOP,
        },
    )
    assert response.status_code == 422
