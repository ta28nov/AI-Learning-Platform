"""Enrollment API tests."""

import pytest
from datetime import datetime

from models.models import CourseDocument


@pytest.mark.asyncio
async def test_list_my_courses_empty(client, student_auth):
    response = await client.get("/enrollments/my-courses", headers=student_auth["headers"])
    assert response.status_code == 200
    assert "enrollments" in response.json()


@pytest.mark.asyncio
async def test_enroll_and_list(client, student_auth, student_user):
    course = CourseDocument(
        title="Enrollable Course",
        description="Test enroll",
        category="Programming",
        level="Beginner",
        status="published",
        owner_id=student_user.id,
        owner_type="admin",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    await course.insert()

    enroll = await client.post(
        "/enrollments",
        json={"course_id": course.id},
        headers=student_auth["headers"],
    )
    assert enroll.status_code == 201

    listing = await client.get("/enrollments/my-courses", headers=student_auth["headers"])
    assert listing.status_code == 200
    ids = [e["course_id"] for e in listing.json().get("enrollments", [])]
    assert course.id in ids


@pytest.mark.asyncio
async def test_enroll_unauthorized(client):
    response = await client.post(
        "/enrollments",
        json={"course_id": "00000000-0000-0000-0000-000000000001"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_enrollment_detail(client, student_auth, published_catalog_course):
    enroll = await client.post(
        "/enrollments",
        json={"course_id": published_catalog_course.id},
        headers=student_auth["headers"],
    )
    assert enroll.status_code == 201
    enrollment_id = enroll.json().get("enrollment_id") or enroll.json().get("id")
    response = await client.get(
        f"/enrollments/{enrollment_id}",
        headers=student_auth["headers"],
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_enrollment_detail_forbidden(client, student_auth, instructor_auth, published_catalog_course):
    enroll = await client.post(
        "/enrollments",
        json={"course_id": published_catalog_course.id},
        headers=student_auth["headers"],
    )
    enrollment_id = enroll.json().get("enrollment_id") or enroll.json().get("id")
    response = await client.get(
        f"/enrollments/{enrollment_id}",
        headers=instructor_auth["headers"],
    )
    assert response.status_code in (403, 404)


@pytest.mark.asyncio
async def test_cancel_enrollment(client, student_auth, published_catalog_course):
    enroll = await client.post(
        "/enrollments",
        json={"course_id": published_catalog_course.id},
        headers=student_auth["headers"],
    )
    enrollment_id = enroll.json().get("enrollment_id") or enroll.json().get("id")
    response = await client.delete(
        f"/enrollments/{enrollment_id}",
        headers=student_auth["headers"],
    )
    assert response.status_code == 200
