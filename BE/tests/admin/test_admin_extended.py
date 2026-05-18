"""Admin endpoints not covered in Phase 2 smoke — plus regression tests for known bugs."""

import pytest
from datetime import datetime


# --- Known backend bugs (see docs/reports/TEST_ISSUES_AND_GAPS.md) ---


@pytest.mark.asyncio
async def test_admin_get_user_detail_known_bug(client, admin_auth, student_user):
    """BUG-001: service returns ISO strings; schema expects datetime."""
    response = await client.get(
        f"/admin/users/{student_user.id}",
        headers=admin_auth["headers"],
    )
    assert response.status_code == 500
    assert "created_at" in response.json().get("detail", "")


@pytest.mark.asyncio
async def test_admin_create_course_known_bug(client, admin_auth):
    """BUG-002: create_course_admin omits required Course.owner_id."""
    response = await client.post(
        "/admin/courses",
        json={
            "title": "Admin Bug Repro Course",
            "description": "Course used to reproduce missing owner_id validation error",
            "category": "Programming",
            "level": "Beginner",
            "status": "draft",
        },
        headers=admin_auth["headers"],
    )
    assert response.status_code == 500
    assert "owner_id" in response.json().get("detail", "")


@pytest.mark.asyncio
async def test_admin_get_course_detail_known_bug(client, admin_auth, published_catalog_course):
    """BUG-004: calls non-existent course_service.get_course_detail."""
    response = await client.get(
        f"/admin/courses/{published_catalog_course.id}",
        headers=admin_auth["headers"],
    )
    assert response.status_code == 500
    assert "get_course_detail" in response.json().get("detail", "")


@pytest.mark.asyncio
async def test_admin_update_course_response_known_bug(client, admin_auth, student_user):
    """BUG-005: update_course_admin response missing title/status for schema."""
    from models.models import CourseDocument

    course = CourseDocument(
        title="Admin Update Bug Course",
        description="Course for admin update response validation bug",
        category="Programming",
        level="Beginner",
        status="draft",
        owner_id=student_user.id,
        owner_type="admin",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    await course.insert()

    response = await client.put(
        f"/admin/courses/{course.id}",
        json={"title": "Admin Update Bug Course Renamed"},
        headers=admin_auth["headers"],
    )
    assert response.status_code == 500
    assert "AdminCourseUpdateResponse" in response.json().get("detail", "")


@pytest.mark.asyncio
async def test_admin_system_health_known_bug(client, admin_auth):
    """BUG-006: system health analytics datetime serialization."""
    response = await client.get(
        "/admin/analytics/system-health",
        headers=admin_auth["headers"],
    )
    assert response.status_code == 500
    assert "created_at" in response.json().get("detail", "") or "health" in response.json().get("detail", "").lower()


# --- Working admin endpoints ---


@pytest.mark.asyncio
async def test_admin_update_user(client, admin_auth):
    create = await client.post(
        "/admin/users",
        json={
            "full_name": "Update Target User",
            "email": "update-target-pytest@example.com",
            "role": "student",
            "password": "UpdatePass1!",
        },
        headers=admin_auth["headers"],
    )
    assert create.status_code == 201
    user_id = create.json()["user_id"]

    response = await client.put(
        f"/admin/users/{user_id}",
        json={"full_name": "Updated Name", "bio": "Updated by admin test"},
        headers=admin_auth["headers"],
    )
    assert response.status_code == 200

    await client.delete(f"/admin/users/{user_id}", headers=admin_auth["headers"])


@pytest.mark.asyncio
async def test_admin_reset_password(client, admin_auth):
    create = await client.post(
        "/admin/users",
        json={
            "full_name": "Reset Password User",
            "email": "reset-pw-pytest@example.com",
            "role": "student",
            "password": "OldPass123!",
        },
        headers=admin_auth["headers"],
    )
    user_id = create.json()["user_id"]

    response = await client.post(
        f"/admin/users/{user_id}/reset-password",
        json={"new_password": "NewPass123!"},
        headers=admin_auth["headers"],
    )
    assert response.status_code == 200

    await client.delete(f"/admin/users/{user_id}", headers=admin_auth["headers"])


@pytest.mark.asyncio
async def test_admin_get_class_detail(client, admin_auth, instructor_with_class):
    class_id = instructor_with_class["class_id"]
    response = await client.get(
        f"/admin/classes/{class_id}",
        headers=admin_auth["headers"],
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_admin_analytics_growth_and_courses(client, admin_auth):
    growth = await client.get(
        "/admin/analytics/users-growth",
        params={"time_range": "30d"},
        headers=admin_auth["headers"],
    )
    assert growth.status_code == 200

    courses = await client.get(
        "/admin/analytics/courses",
        params={"time_range": "30d"},
        headers=admin_auth["headers"],
    )
    assert courses.status_code == 200


@pytest.mark.asyncio
async def test_student_cannot_access_admin_analytics(client, student_auth):
    response = await client.get(
        "/admin/analytics/system-health",
        headers=student_auth["headers"],
    )
    assert response.status_code == 403
