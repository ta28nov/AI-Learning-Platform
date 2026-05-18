"""POST /auth/login tests."""

import pytest

from tests.helpers.auth import login_user, register_user


@pytest.mark.asyncio
async def test_login_success(client):
    email = "login-ok@example.com"
    await register_user(client, email=email)
    response = await login_user(client, email)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "Bearer"
    assert data["user"]["email"] == email


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    email = "login-fail@example.com"
    await register_user(client, email=email)
    response = await login_user(client, email, password="WrongPass1!")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_email(client):
    response = await login_user(client, "nobody@example.com")
    assert response.status_code == 401
