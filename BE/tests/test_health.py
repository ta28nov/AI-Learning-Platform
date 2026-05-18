"""System health endpoint tests."""

import pytest


@pytest.mark.asyncio
async def test_health_check(health_client):
    response = await health_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
