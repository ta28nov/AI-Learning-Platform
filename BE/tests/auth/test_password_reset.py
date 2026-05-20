"""POST /auth/forgot-password and /auth/reset-password."""

import pytest

from tests.helpers.auth import register_user, login_user


@pytest.mark.asyncio
async def test_forgot_password_unknown_email_still_200(client):
    response = await client.post(
        "/auth/forgot-password",
        json={"email": "nobody-reset@example.com"},
    )
    assert response.status_code == 200
    assert "message" in response.json()
    assert not response.json().get("reset_token")


@pytest.mark.asyncio
async def test_forgot_and_reset_password_flow(client):
    email = "reset-flow@example.com"
    password = "OldPass1!"
    new_password = "NewPass9!"

    await register_user(client, email=email, password=password)

    forgot = await client.post("/auth/forgot-password", json={"email": email})
    assert forgot.status_code == 200
    body = forgot.json()
    assert body.get("reset_token"), "TESTING=true should expose token for tests"

    reset = await client.post(
        "/auth/reset-password",
        json={"token": body["reset_token"], "new_password": new_password},
    )
    assert reset.status_code == 200

    old_login = await login_user(client, email, password=password)
    assert old_login.status_code == 401

    new_login = await login_user(client, email, password=new_password)
    assert new_login.status_code == 200


@pytest.mark.asyncio
async def test_reset_password_invalid_token(client):
    response = await client.post(
        "/auth/reset-password",
        json={"token": "invalid-token-xyz", "new_password": "NewPass9!"},
    )
    assert response.status_code == 400
