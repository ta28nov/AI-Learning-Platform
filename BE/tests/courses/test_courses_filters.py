"""Course search filters and guest access."""

import pytest


@pytest.mark.asyncio
async def test_search_courses_with_category_and_level(
    client, published_catalog_course
):
    response = await client.get(
        "/courses/search",
        params={
            "keyword": "Python",
            "category": "Programming",
            "level": "Beginner",
            "skip": 0,
            "limit": 10,
        },
    )
    assert response.status_code == 200
    body = response.json()
    courses = body.get("courses", body.get("data", []))
    assert isinstance(courses, list)


@pytest.mark.asyncio
async def test_search_courses_guest_no_auth(client, published_catalog_course):
    response = await client.get(
        "/courses/search",
        params={"keyword": "Public"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_public_courses_pagination(client, published_catalog_course):
    response = await client.get(
        "/courses/public",
        params={"skip": 0, "limit": 5},
    )
    assert response.status_code == 200
