"""Course discovery API tests."""

import pytest


@pytest.mark.asyncio
async def test_search_courses(client, student_auth, published_catalog_course):
    response = await client.get(
        "/courses/search",
        params={"keyword": "Python"},
        headers=student_auth["headers"],
    )
    assert response.status_code == 200
    body = response.json()
    assert "courses" in body or "data" in body


@pytest.mark.asyncio
async def test_public_courses(client, published_catalog_course):
    response = await client.get("/courses/public")
    assert response.status_code == 200
    body = response.json()
    courses = body.get("courses", body.get("data", []))
    assert isinstance(courses, list)


@pytest.mark.asyncio
async def test_course_detail(client, student_auth, published_catalog_course):
    response = await client.get(
        f"/courses/{published_catalog_course.id}",
        headers=student_auth["headers"],
    )
    assert response.status_code == 200
    assert response.json()["id"] == published_catalog_course.id


@pytest.mark.asyncio
async def test_enrollment_status_not_enrolled(client, student_auth, published_catalog_course):
    response = await client.get(
        f"/courses/{published_catalog_course.id}/enrollment-status",
        headers=student_auth["headers"],
    )
    assert response.status_code == 200
    body = response.json()
    assert body.get("is_enrolled") is False or body.get("enrolled") is False


@pytest.mark.asyncio
async def test_enrollment_status_enrolled(client, student_auth, published_catalog_course):
    enroll = await client.post(
        "/enrollments",
        json={"course_id": published_catalog_course.id},
        headers=student_auth["headers"],
    )
    assert enroll.status_code == 201
    response = await client.get(
        f"/courses/{published_catalog_course.id}/enrollment-status",
        headers=student_auth["headers"],
    )
    assert response.status_code == 200
    body = response.json()
    assert body.get("is_enrolled") is True or body.get("enrolled") is True
