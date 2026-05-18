"""Admin list filters and user creation edge cases."""

import pytest


@pytest.mark.asyncio
async def test_admin_list_users_by_status_active(client, admin_auth, student_user):
    response = await client.get(
        "/admin/users",
        params={"status": "active", "role": "student", "limit": 20},
        headers=admin_auth["headers"],
    )
    assert response.status_code == 200
    data = response.json().get("data", [])
    assert all(u.get("status") == "active" for u in data if u.get("status"))


@pytest.mark.asyncio
async def test_admin_create_student_requires_password(client, admin_auth):
    """Schema requires password for all roles (docs mention pending without password)."""
    response = await client.post(
        "/admin/users",
        json={
            "full_name": "Pending Student Probe",
            "email": "pending-student-probe@example.com",
            "role": "student",
        },
        headers=admin_auth["headers"],
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_admin_create_student_with_password_pending_status(client, admin_auth):
    response = await client.post(
        "/admin/users",
        json={
            "full_name": "Admin Created Student",
            "email": "admin-created-student-edge@example.com",
            "role": "student",
            "password": "StudentPass1!",
        },
        headers=admin_auth["headers"],
    )
    assert response.status_code == 201
    body = response.json()
    assert body.get("role") == "student"
    assert body.get("status") in ("pending", "active")

    await client.delete(
        f"/admin/users/{body['user_id']}",
        headers=admin_auth["headers"],
    )
