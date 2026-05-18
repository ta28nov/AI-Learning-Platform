"""Admin management endpoints."""

import pytest


@pytest.mark.asyncio
async def test_admin_list_users(client, admin_auth):
    response = await client.get("/admin/users", headers=admin_auth["headers"])
    assert response.status_code == 200
    body = response.json()
    assert "data" in body or "users" in body


@pytest.mark.asyncio
async def test_student_cannot_list_users(client, student_auth):
    response = await client.get("/admin/users", headers=student_auth["headers"])
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_list_courses(client, admin_auth):
    response = await client.get("/admin/courses", headers=admin_auth["headers"])
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_admin_user_crud_smoke(client, admin_auth):
    create = await client.post(
        "/admin/users",
        json={
            "full_name": "Smoke Test User",
            "email": "smoke-user-pytest@example.com",
            "role": "student",
            "password": "SmokePass1!",
        },
        headers=admin_auth["headers"],
    )
    assert create.status_code == 201
    user_id = create.json().get("user_id")

    role = await client.put(
        f"/admin/users/{user_id}/role",
        json={"new_role": "instructor", "impact": "pytest smoke test"},
        headers=admin_auth["headers"],
    )
    assert role.status_code == 200

    delete = await client.delete(f"/admin/users/{user_id}", headers=admin_auth["headers"])
    assert delete.status_code == 200


@pytest.mark.asyncio
async def test_admin_list_classes(client, admin_auth, instructor_with_class):
    response = await client.get("/admin/classes", headers=admin_auth["headers"])
    assert response.status_code == 200
