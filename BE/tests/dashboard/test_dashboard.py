"""Dashboard endpoints by role."""

import pytest


@pytest.mark.asyncio
async def test_student_dashboard(client, student_auth):
    response = await client.get("/dashboard/student", headers=student_auth["headers"])
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_instructor_dashboard(client, instructor_auth):
    response = await client.get("/dashboard/instructor", headers=instructor_auth["headers"])
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_admin_dashboard(client, admin_auth):
    response = await client.get("/dashboard/admin", headers=admin_auth["headers"])
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_student_cannot_access_admin_dashboard(client, student_auth):
    response = await client.get("/dashboard/admin", headers=student_auth["headers"])
    assert response.status_code == 403
