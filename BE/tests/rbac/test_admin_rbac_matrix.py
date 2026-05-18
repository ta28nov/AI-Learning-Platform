"""RBAC matrix: every /admin route must reject non-admin with 403."""

from typing import Any, Callable, Dict, List, Optional, Tuple

import pytest

RouteCase = Tuple[str, str, Optional[Dict[str, Any]], Optional[Dict[str, Any]]]


def _admin_read_routes(
    student_user,
    instructor_with_class,
    published_catalog_course,
) -> List[RouteCase]:
    class_id = instructor_with_class["class_id"]
    course_id = str(published_catalog_course.id)
    user_id = str(student_user.id)
    return [
        ("GET", "/admin/users", None, {"params": {"limit": 5, "skip": 0}}),
        ("GET", f"/admin/users/{user_id}", None, None),
        ("GET", "/admin/courses", None, None),
        ("GET", f"/admin/courses/{course_id}", None, None),
        ("GET", "/admin/classes", None, {"params": {"page": 1, "limit": 5}}),
        ("GET", f"/admin/classes/{class_id}", None, None),
        (
            "GET",
            "/admin/analytics/users-growth",
            None,
            {"params": {"time_range": "30d"}},
        ),
        (
            "GET",
            "/admin/analytics/courses",
            None,
            {"params": {"time_range": "30d"}},
        ),
        ("GET", "/admin/analytics/system-health", None, None),
    ]


def _admin_write_routes(student_user, published_catalog_course) -> List[RouteCase]:
    user_id = str(student_user.id)
    course_id = str(published_catalog_course.id)
    return [
        (
            "POST",
            "/admin/users",
            {
                "full_name": "RBAC Probe",
                "email": "rbac-probe-student@example.com",
                "role": "student",
                "password": "ProbePass1!",
            },
            None,
        ),
        (
            "PUT",
            f"/admin/users/{user_id}",
            {"full_name": "RBAC Updated Name"},
            None,
        ),
        (
            "PUT",
            f"/admin/users/{user_id}/role",
            {"new_role": "student", "impact": "RBAC matrix probe"},
            None,
        ),
        (
            "POST",
            f"/admin/users/{user_id}/reset-password",
            {"new_password": "NewProbePass1!"},
            None,
        ),
        (
            "POST",
            "/admin/courses",
            {
                "title": "RBAC Admin Course",
                "description": "Course body for RBAC matrix write probe test",
                "category": "Programming",
                "level": "Beginner",
                "status": "draft",
            },
            None,
        ),
        (
            "PUT",
            f"/admin/courses/{course_id}",
            {"title": "RBAC Updated"},
            None,
        ),
        ("DELETE", f"/admin/courses/{course_id}", None, None),
    ]


@pytest.fixture
def admin_read_routes(student_user, instructor_with_class, published_catalog_course):
    return _admin_read_routes(student_user, instructor_with_class, published_catalog_course)


@pytest.fixture
def admin_write_routes(student_user, published_catalog_course):
    return _admin_write_routes(student_user, published_catalog_course)


async def _request(client, method: str, path: str, headers, json_body, extra):
    kwargs: Dict[str, Any] = {"headers": headers}
    if json_body is not None:
        kwargs["json"] = json_body
    if extra:
        if "params" in extra:
            kwargs["params"] = extra["params"]
    return await client.request(method, path, **kwargs)


async def _assert_non_admin_denied(client, headers, routes, label: str):
    for method, path, body, extra in routes:
        response = await _request(client, method, path, headers, body, extra)
        assert response.status_code == 403, (
            f"{label} {method} {path} -> {response.status_code}: {response.text[:200]}"
        )


@pytest.mark.asyncio
async def test_student_denied_on_admin_read_routes(
    client, student_auth, admin_read_routes
):
    await _assert_non_admin_denied(
        client, student_auth["headers"], admin_read_routes, "student"
    )


@pytest.mark.asyncio
async def test_instructor_denied_on_admin_read_routes(
    client, instructor_auth, admin_read_routes
):
    await _assert_non_admin_denied(
        client, instructor_auth["headers"], admin_read_routes, "instructor"
    )


@pytest.mark.asyncio
async def test_student_denied_on_admin_write_routes(
    client, student_auth, admin_write_routes
):
    await _assert_non_admin_denied(
        client, student_auth["headers"], admin_write_routes, "student"
    )


@pytest.mark.asyncio
async def test_instructor_denied_on_admin_write_routes(
    client, instructor_auth, admin_write_routes
):
    await _assert_non_admin_denied(
        client, instructor_auth["headers"], admin_write_routes, "instructor"
    )


@pytest.mark.asyncio
async def test_admin_read_routes_not_forbidden(
    client, admin_auth, admin_read_routes
):
    """Admin may hit 200 or 500 (data bugs); must not be 403."""
    for method, path, body, extra in admin_read_routes:
        response = await _request(
            client, method, path, admin_auth["headers"], body, extra
        )
        assert response.status_code != 403, (
            f"admin {method} {path} -> {response.status_code}: {response.text[:200]}"
        )


@pytest.mark.asyncio
async def test_admin_dashboard_and_search_analytics_not_forbidden(
    client, admin_auth, student_auth, instructor_auth
):
    dash = await client.get("/dashboard/admin", headers=admin_auth["headers"])
    assert dash.status_code != 403

    search = await client.get("/search/analytics", headers=admin_auth["headers"])
    assert search.status_code != 403

    for auth in (student_auth, instructor_auth):
        blocked = await client.get("/dashboard/admin", headers=auth["headers"])
        assert blocked.status_code == 403
        blocked_search = await client.get(
            "/search/analytics", headers=auth["headers"]
        )
        assert blocked_search.status_code == 403
