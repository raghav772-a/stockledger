import pytest


@pytest.mark.asyncio
async def test_register_validation(client):
    response = await client.post("/api/v1/auth/register", json={"email": "bad", "password": "short"})
    assert response.status_code == 422
