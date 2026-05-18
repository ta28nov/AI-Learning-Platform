"""POST /auth/refresh tests."""

import pytest

from tests.helpers.auth import register_and_login


@pytest.mark.asyncio
async def test_refresh_token_success(client):
    _, access, refresh = await register_and_login(client, email="refresh@example.com")
    assert access
    response = await client.post("/auth/refresh", json={"refresh_token": refresh})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "Bearer"


@pytest.mark.asyncio
async def test_refresh_invalid_token(client):
    response = await client.post("/auth/refresh", json={"refresh_token": "invalid.token.here"})
    assert response.status_code == 401
