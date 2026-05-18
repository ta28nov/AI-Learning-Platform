"""Enrollment list filters and status edge cases."""

from datetime import datetime

import pytest

from models.models import CourseDocument, EnrollmentDocument


@pytest.mark.asyncio
async def test_my_courses_filter_active(client, student_auth, published_catalog_course):
    enroll = await client.post(
        "/enrollments",
        json={"course_id": published_catalog_course.id},
        headers=student_auth["headers"],
    )
    assert enroll.status_code == 201

    active = await client.get(
        "/enrollments/my-courses",
        params={"status": "active"},
        headers=student_auth["headers"],
    )
    assert active.status_code == 200
    ids = [e.get("course_id") for e in active.json().get("enrollments", [])]
    assert published_catalog_course.id in ids


@pytest.mark.asyncio
async def test_my_courses_filter_cancelled(client, student_auth, published_catalog_course):
    enroll = await client.post(
        "/enrollments",
        json={"course_id": published_catalog_course.id},
        headers=student_auth["headers"],
    )
    enrollment_id = enroll.json().get("enrollment_id") or enroll.json().get("id")
    await client.delete(
        f"/enrollments/{enrollment_id}",
        headers=student_auth["headers"],
    )

    cancelled = await client.get(
        "/enrollments/my-courses",
        params={"status": "cancelled"},
        headers=student_auth["headers"],
    )
    assert cancelled.status_code == 200
    ids = [e.get("course_id") for e in cancelled.json().get("enrollments", [])]
    assert published_catalog_course.id in ids


@pytest.mark.asyncio
async def test_my_courses_filter_completed(client, student_auth, student_user):
    course = CourseDocument(
        title="Completed Filter Course",
        description="Course for completed enrollment filter test",
        category="Programming",
        level="Beginner",
        status="published",
        owner_id=student_user.id,
        owner_type="admin",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    await course.insert()
    enrollment = EnrollmentDocument(
        user_id=student_user.id,
        course_id=course.id,
        status="completed",
        progress_percent=100.0,
    )
    await enrollment.insert()

    response = await client.get(
        "/enrollments/my-courses",
        params={"status": "completed"},
        headers=student_auth["headers"],
    )
    assert response.status_code == 200
    ids = [e.get("course_id") for e in response.json().get("enrollments", [])]
    assert course.id in ids
