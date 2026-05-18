"""POST /auth/register tests."""

import pytest

from tests.helpers.factories import register_payload


@pytest.mark.asyncio
async def test_register_success(client):
    payload = register_payload()
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["role"] == "student"
    assert data["status"] == "active"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    payload = register_payload(email="dup@example.com")
    first = await client.post("/auth/register", json=payload)
    assert first.status_code == 201
    second = await client.post("/auth/register", json=payload)
    assert second.status_code == 400
    assert "đã được sử dụng" in second.json()["detail"]


@pytest.mark.asyncio
async def test_register_weak_password_validation(client):
    payload = register_payload()
    payload["password"] = "weak"
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_email(client):
    payload = register_payload()
    payload["email"] = "not-an-email"
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 422
