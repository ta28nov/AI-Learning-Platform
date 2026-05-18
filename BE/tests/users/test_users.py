"""User profile API tests."""

import pytest


@pytest.mark.asyncio
async def test_get_me(client, student_auth):
    response = await client.get("/users/me", headers=student_auth["headers"])
    assert response.status_code == 200
    assert response.json()["email"] == student_auth["user"]["email"]


@pytest.mark.asyncio
async def test_get_me_unauthorized(client):
    response = await client.get("/users/me")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_patch_me(client, student_auth):
    response = await client.patch(
        "/users/me",
        json={"bio": "Integration test bio"},
        headers=student_auth["headers"],
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_patch_me_bio_too_long(client, student_auth):
    response = await client.patch(
        "/users/me",
        json={"bio": "x" * 501},
        headers=student_auth["headers"],
    )
    assert response.status_code == 422
