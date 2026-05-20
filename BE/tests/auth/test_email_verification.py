"""POST /auth/verify-email and /auth/resend-verification."""

import pytest

from tests.helpers.auth import register_user


@pytest.mark.asyncio
async def test_verify_email_after_register(client):
    email = "verify-flow@example.com"
    password = "VerifyMe1!"

    reg = await register_user(client, email=email, password=password)
    assert reg.status_code == 201
    body = reg.json()
    assert body.get("verification_token"), "TESTING=true should expose token"

    verify = await client.post("/auth/verify-email", json={"token": body["verification_token"]})
    assert verify.status_code == 200
    assert verify.json().get("email_verified") is True

    again = await client.post("/auth/verify-email", json={"token": body["verification_token"]})
    assert again.status_code == 400


@pytest.mark.asyncio
async def test_resend_verification_unknown_email_still_200(client):
    response = await client.post(
        "/auth/resend-verification",
        json={"email": "nobody-verify@example.com"},
    )
    assert response.status_code == 200
    assert "message" in response.json()
    assert not response.json().get("verification_token")


@pytest.mark.asyncio
async def test_resend_verification_for_unverified_user(client):
    email = "resend-verify@example.com"
    await register_user(client, email=email, password="ResendMe1!")

    res = await client.post("/auth/resend-verification", json={"email": email})
    assert res.status_code == 200
    assert res.json().get("verification_token")
