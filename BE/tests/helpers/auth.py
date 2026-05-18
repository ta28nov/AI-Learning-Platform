"""Reusable auth helpers for API integration tests."""

from typing import Any, Dict, Tuple

from httpx import AsyncClient

from tests.helpers.factories import login_payload, register_payload


def bearer(access_token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


async def register_user(
    client: AsyncClient,
    email: str | None = None,
    password: str = "TestPass1!",
    full_name: str = "Nguyen Van Test",
) -> Dict[str, Any]:
    response = await client.post("/auth/register", json=register_payload(email, password, full_name))
    return response


async def login_user(
    client: AsyncClient,
    email: str,
    password: str = "TestPass1!",
    remember_me: bool = False,
) -> Dict[str, Any]:
    response = await client.post(
        "/auth/login",
        json=login_payload(email, password, remember_me),
    )
    return response


async def register_and_login(
    client: AsyncClient,
    email: str | None = None,
    password: str = "TestPass1!",
) -> Tuple[Dict[str, Any], str, str]:
    """Register then login; returns (user dict, access_token, refresh_token)."""
    reg = await register_user(client, email, password)
    assert reg.status_code == 201, reg.text
    email_used = reg.json()["email"]
    log = await login_user(client, email_used, password)
    assert log.status_code == 200, log.text
    data = log.json()
    return data["user"], data["access_token"], data["refresh_token"]
