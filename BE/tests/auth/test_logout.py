"""POST /auth/logout tests."""

import pytest

from tests.helpers.auth import bearer, register_and_login


@pytest.mark.asyncio
async def test_logout_success(client):
    _, access, _ = await register_and_login(client, email="logout@example.com")
    response = await client.post("/auth/logout", headers=bearer(access))
    assert response.status_code == 200
    assert "thành công" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_logout_without_token(client):
    response = await client.post("/auth/logout")
    assert response.status_code == 403
