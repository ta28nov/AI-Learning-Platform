"""Additional admin list filters, RBAC, and regression tests."""

import pytest
from datetime import datetime


@pytest.mark.asyncio
async def test_admin_list_users_by_role(client, admin_auth, student_user):
    response = await client.get(
        "/admin/users",
        params={"role": "student", "limit": 10, "skip": 0, "sort_by": "created_at", "sort_order": "desc"},
        headers=admin_auth["headers"],
    )
    assert response.status_code == 200
    assert isinstance(response.json().get("data", []), list)


@pytest.mark.asyncio
async def test_admin_list_users_with_keyword_known_bug(client, admin_auth):
    """BUG-012: keyword search on admin users."""
    response = await client.get(
        "/admin/users",
        params={"keyword": "student", "sort_by": "email", "sort_order": "asc"},
        headers=admin_auth["headers"],
    )
    assert response.status_code == 200
    assert isinstance(response.json().get("data", []), list)


@pytest.mark.asyncio
async def test_admin_list_courses_no_filter(client, admin_auth, published_catalog_course):
    response = await client.get("/admin/courses", headers=admin_auth["headers"])
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_admin_list_courses_with_keyword_known_bug(client, admin_auth):
    """BUG-010: keyword search on admin courses."""
    response = await client.get(
        "/admin/courses",
        params={"keyword": "Python"},
        headers=admin_auth["headers"],
    )
    assert response.status_code == 200
    assert "data" in response.json()


@pytest.mark.asyncio
async def test_admin_delete_course_known_bug(client, admin_auth, admin_user):
    """BUG-009: delete_course_admin triggers ExpressionField is not callable."""
    from models.models import CourseDocument

    course = CourseDocument(
        title="Admin Delete Target",
        description="Course targeted for admin delete regression test",
        category="Programming",
        level="Beginner",
        status="draft",
        owner_id=admin_user.id,
        owner_type="admin",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    await course.insert()

    response = await client.delete(
        f"/admin/courses/{course.id}",
        headers=admin_auth["headers"],
    )
    assert response.status_code == 200
    assert response.json()["course_id"] == course.id


@pytest.mark.asyncio
async def test_admin_list_classes_pagination(client, admin_auth, instructor_with_class):
    response = await client.get(
        "/admin/classes",
        params={"page": 1, "limit": 10},
        headers=admin_auth["headers"],
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_admin_list_classes_search_known_bug(client, admin_auth):
    """BUG-013: search filter on admin classes."""
    response = await client.get(
        "/admin/classes",
        params={"search": "Test", "status_filter": "active"},
        headers=admin_auth["headers"],
    )
    assert response.status_code == 200
    assert isinstance(response.json().get("data", []), list)


@pytest.mark.asyncio
async def test_admin_analytics_time_ranges_and_role_filter(client, admin_auth):
    for time_range in ("7d", "30d", "90d"):
        growth = await client.get(
            "/admin/analytics/users-growth",
            params={"time_range": time_range, "role_filter": "student"},
            headers=admin_auth["headers"],
        )
        assert growth.status_code == 200

        courses = await client.get(
            "/admin/analytics/courses",
            params={"time_range": time_range, "category_filter": "Programming"},
            headers=admin_auth["headers"],
        )
        assert courses.status_code == 200


@pytest.mark.asyncio
async def test_instructor_forbidden_on_admin_users_and_courses(client, instructor_auth):
    users = await client.get("/admin/users", headers=instructor_auth["headers"])
    assert users.status_code == 403

    courses = await client.get("/admin/courses", headers=instructor_auth["headers"])
    assert courses.status_code == 403

    classes = await client.get("/admin/classes", headers=instructor_auth["headers"])
    assert classes.status_code == 403


@pytest.mark.asyncio
async def test_student_forbidden_on_admin_endpoints(client, student_auth):
    for path in ("/admin/users", "/admin/courses", "/admin/classes"):
        response = await client.get(path, headers=student_auth["headers"])
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_create_instructor_user_and_list(client, admin_auth):
    create = await client.post(
        "/admin/users",
        json={
            "full_name": "Admin Created Instructor",
            "email": "admin-created-instructor@example.com",
            "role": "instructor",
            "password": "InstructorPass1!",
        },
        headers=admin_auth["headers"],
    )
    assert create.status_code == 201

    listing = await client.get(
        "/admin/users",
        params={"role": "instructor"},
        headers=admin_auth["headers"],
    )
    assert listing.status_code == 200
    emails = [u.get("email") for u in listing.json().get("data", [])]
    assert "admin-created-instructor@example.com" in emails

    await client.delete(
        f"/admin/users/{create.json()['user_id']}",
        headers=admin_auth["headers"],
    )
