import pytest



@pytest.fixture
async def test_read_root(client):
    response = await client.get("/")

    assert response.status_code == 200
    assert response.json() == {"hello": "fastapi", "test": "이거잘 반영돼는거 맞죠?"}
