"""Unit tests for middleware.rbac permission maps and helpers."""

import pytest
from fastapi import HTTPException

from middleware.rbac import (
    ADMIN_PERMISSIONS,
    INSTRUCTOR_PERMISSIONS,
    STUDENT_PERMISSIONS,
    Permission,
    Role,
    get_user_permissions,
    has_minimum_role,
    has_permission,
    require_role,
    require_student_only,
)


def test_student_permissions_include_core_learning():
    assert Permission.ENROLLMENT_CREATE in STUDENT_PERMISSIONS
    assert Permission.DASHBOARD_STUDENT in STUDENT_PERMISSIONS
    assert Permission.ADMIN_USER_LIST not in STUDENT_PERMISSIONS


def test_instructor_permissions_superset_of_student():
    assert STUDENT_PERMISSIONS.issubset(INSTRUCTOR_PERMISSIONS)
    assert Permission.CLASS_CREATE in INSTRUCTOR_PERMISSIONS
    assert Permission.QUIZ_CREATE in INSTRUCTOR_PERMISSIONS
    assert Permission.DASHBOARD_INSTRUCTOR in INSTRUCTOR_PERMISSIONS


def test_admin_permissions_superset_of_instructor():
    assert INSTRUCTOR_PERMISSIONS.issubset(ADMIN_PERMISSIONS)
    assert Permission.ADMIN_USER_LIST in ADMIN_PERMISSIONS
    assert Permission.DASHBOARD_ADMIN in ADMIN_PERMISSIONS


def test_has_permission_by_role():
    assert has_permission(Role.STUDENT, Permission.ENROLLMENT_CREATE) is True
    assert has_permission(Role.STUDENT, Permission.ADMIN_USER_LIST) is False
    assert has_permission(Role.INSTRUCTOR, Permission.QUIZ_CREATE) is True
    assert has_permission(Role.ADMIN, Permission.ADMIN_COURSE_DELETE) is True
    assert has_permission("unknown", Permission.AUTH_LOGOUT) is False


def test_get_user_permissions_matches_role_sets():
    assert get_user_permissions(Role.STUDENT) == STUDENT_PERMISSIONS
    assert get_user_permissions(Role.ADMIN) == ADMIN_PERMISSIONS


def test_has_minimum_role_hierarchy():
    assert has_minimum_role(Role.ADMIN, Role.INSTRUCTOR) is True
    assert has_minimum_role(Role.INSTRUCTOR, Role.INSTRUCTOR) is True
    assert has_minimum_role(Role.STUDENT, Role.INSTRUCTOR) is False


@pytest.mark.asyncio
async def test_require_role_hierarchy_allows_higher_roles():
    """rbac.require_role uses level >= required (admin may access instructor gate)."""
    checker = require_role(Role.INSTRUCTOR)

    admin_user = {"user_id": "a1", "role": Role.ADMIN}
    instructor_user = {"user_id": "i1", "role": Role.INSTRUCTOR}
    student_user = {"user_id": "s1", "role": Role.STUDENT}

    assert (await checker(admin_user)) == admin_user
    assert (await checker(instructor_user)) == instructor_user

    with pytest.raises(HTTPException) as exc:
        await checker(student_user)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_require_role_exact_admin_gate():
    checker = require_role(Role.ADMIN)
    assert (await checker({"user_id": "a1", "role": Role.ADMIN}))["role"] == Role.ADMIN

    with pytest.raises(HTTPException) as exc:
        await checker({"user_id": "i1", "role": Role.INSTRUCTOR})
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_require_student_only_rejects_instructor_and_admin():
    checker = require_student_only
    student_user = {"user_id": "s1", "role": Role.STUDENT}
    assert (await checker(student_user)) == student_user

    with pytest.raises(HTTPException) as exc:
        await checker({"user_id": "i1", "role": Role.INSTRUCTOR})
    assert exc.value.status_code == 403


def test_rbac_shorthand_dependencies_are_callable_for_fastapi():
    from middleware import rbac as rbac_mod

    for name in ("require_student_only", "require_instructor", "require_admin"):
        dep = getattr(rbac_mod, name)
        assert callable(dep), f"rbac.{name} must be Depends()-ready; got {type(dep)}"


def test_dashboard_and_analytics_routers_import_rbac():
    import pathlib

    root = pathlib.Path(__file__).resolve().parents[2]
    wired = []
    for name in ("dashboard_router.py", "analytics_router.py"):
        text = (root / "routers" / name).read_text(encoding="utf-8")
        if "middleware.rbac" in text:
            wired.append(name)
    assert wired == ["dashboard_router.py", "analytics_router.py"]
