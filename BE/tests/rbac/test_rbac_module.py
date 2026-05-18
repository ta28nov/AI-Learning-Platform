"""Unit tests for middleware.rbac permission maps and helpers."""

import inspect

import pytest
from fastapi import HTTPException

from middleware.rbac import (
    ADMIN_PERMISSIONS,
    INSTRUCTOR_PERMISSIONS,
    STUDENT_PERMISSIONS,
    Permission,
    Role,
    get_user_permissions,
    has_permission,
    require_role,
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


@pytest.mark.asyncio
async def test_require_role_hierarchy_allows_higher_roles():
    """rbac.require_role uses level >= required (admin may access instructor gate)."""
    checker = await require_role(Role.INSTRUCTOR)

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
    checker = await require_role(Role.ADMIN)
    assert (await checker({"user_id": "a1", "role": Role.ADMIN}))["role"] == Role.ADMIN

    with pytest.raises(HTTPException) as exc:
        await checker({"user_id": "i1", "role": Role.INSTRUCTOR})
    assert exc.value.status_code == 403


def test_rbac_shorthand_dependencies_are_broken_coroutines():
    """
    require_admin = require_role(Role.ADMIN) assigns a coroutine (missing await),
    so these cannot be used as FastAPI Depends() today.
    """
    from middleware import rbac as rbac_mod

    for name in ("require_student", "require_instructor", "require_admin"):
        dep = getattr(rbac_mod, name)
        assert inspect.iscoroutine(dep), (
            f"rbac.{name} should be awaited require_role(...); got {type(dep)}"
        )


def test_routers_do_not_import_rbac_dependencies():
    """RBAC middleware exists but is not wired on routers (controllers use string checks)."""
    import pathlib

    root = pathlib.Path(__file__).resolve().parents[2]
    router_dir = root / "routers"
    hits = []
    for path in router_dir.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "middleware.rbac" in text or "from middleware import rbac" in text:
            hits.append(path.name)
    assert hits == [], f"Expected no router RBAC imports, found: {hits}"
