"""Search guest access and query filters."""

import pytest


@pytest.mark.asyncio
async def test_universal_search_guest_no_auth(client, published_catalog_course):
    response = await client.get("/search", params={"q": "Python", "page": 1, "limit": 10})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_universal_search_with_rating_and_instructor_params(
    client, student_auth, published_catalog_course
):
    """COV-002: rating + instructor query params accepted."""
    response = await client.get(
        "/search",
        params={
            "q": "Python",
            "rating": 0,
            "instructor": getattr(published_catalog_course, "instructor_id", None)
            or published_catalog_course.owner_id,
            "page": 1,
            "limit": 10,
        },
        headers=student_auth["headers"],
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_universal_search_with_filters(client, student_auth, published_catalog_course):
    response = await client.get(
        "/search",
        params={
            "q": "Python",
            "category": "Programming",
            "level": "Beginner",
            "page": 1,
            "limit": 10,
        },
        headers=student_auth["headers"],
    )
    assert response.status_code == 200
    body = response.json()
    assert "results_by_category" in body or "results" in body
