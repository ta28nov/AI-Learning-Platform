"""Universal search API tests."""

import pytest


@pytest.mark.asyncio
async def test_universal_search(client, student_auth, published_catalog_course):
    response = await client.get(
        "/search",
        params={"q": "Python"},
        headers=student_auth["headers"],
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_search_history(client, student_auth):
    await client.get("/search", params={"q": "Python"}, headers=student_auth["headers"])
    response = await client.get("/search/history", headers=student_auth["headers"])
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_search_suggestions(client, published_catalog_course):
    response = await client.get("/search/suggestions", params={"q": "Py"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_search_analytics_admin(client, admin_auth):
    response = await client.get("/search/analytics", headers=admin_auth["headers"])
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_search_analytics_forbidden_for_student(client, student_auth):
    response = await client.get("/search/analytics", headers=student_auth["headers"])
    assert response.status_code == 403
