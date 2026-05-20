"""Class join errors and delete rules."""

from datetime import datetime, timedelta, timezone

import pytest

from utils.security import hash_password


async def _student_auth_for_email(client, email: str):
    from models.models import UserDocument
    from tests.helpers.auth import bearer, login_user

    user = UserDocument(
        full_name="Edge Test Student",
        email=email,
        hashed_password=hash_password("TestPass1!"),
        role="student",
        status="active",
    )
    await user.insert()
    res = await login_user(client, email)
    assert res.status_code == 200
    return {"user": user, "headers": bearer(res.json()["access_token"])}


@pytest.mark.asyncio
async def test_join_class_invalid_invite_code(client, student_auth):
    response = await client.post(
        "/classes/join",
        json={"invite_code": "INVALID1"},
        headers=student_auth["headers"],
    )
    assert response.status_code == 400
    assert "mời" in response.json().get("detail", "").lower() or "invalid" in response.json().get("detail", "").lower()


@pytest.mark.asyncio
async def test_join_class_already_joined(client, student_auth, instructor_with_class):
    code = instructor_with_class["invite_code"]
    first = await client.post(
        "/classes/join",
        json={"invite_code": code},
        headers=student_auth["headers"],
    )
    assert first.status_code in (200, 201)

    second = await client.post(
        "/classes/join",
        json={"invite_code": code},
        headers=student_auth["headers"],
    )
    assert second.status_code == 400
    detail = second.json().get("detail", "").lower()
    assert "đã tham gia" in detail or "already" in detail


@pytest.mark.asyncio
async def test_join_class_preparing_status_rejected(
    client, student_auth, instructor_auth, published_catalog_course
):
    """BUG-014: preparing class rejects join until active."""
    now = datetime.now(timezone.utc)
    created = await client.post(
        "/classes",
        json={
            "name": "Preparing Class",
            "description": "Class not yet active for join",
            "course_id": published_catalog_course.id,
            "start_date": (now + timedelta(days=7)).isoformat(),
            "end_date": (now + timedelta(days=37)).isoformat(),
            "max_students": 10,
        },
        headers=instructor_auth["headers"],
    )
    assert created.status_code == 201
    invite = created.json().get("invite_code")

    response = await client.post(
        "/classes/join",
        json={"invite_code": invite},
        headers=student_auth["headers"],
    )
    assert response.status_code == 400
    assert "active" in response.json().get("detail", "").lower()


@pytest.mark.asyncio
async def test_join_class_when_full(
    client, instructor_auth, published_catalog_course
):
    now = datetime.now(timezone.utc)
    created = await client.post(
        "/classes",
        json={
            "name": "Full Class",
            "description": "Only one seat for join-full test",
            "course_id": published_catalog_course.id,
            "start_date": now.isoformat(),
            "end_date": (now + timedelta(days=30)).isoformat(),
            "max_students": 1,
        },
        headers=instructor_auth["headers"],
    )
    assert created.status_code == 201
    invite = created.json().get("invite_code")
    class_id = created.json().get("class_id") or created.json().get("id")

    from models.models import Class

    cls = await Class.get(class_id)
    cls.status = "active"
    await cls.save()

    student_a = await _student_auth_for_email(client, "join-full-a@example.com")
    student_b = await _student_auth_for_email(client, "join-full-b@example.com")

    first = await client.post(
        "/classes/join",
        json={"invite_code": invite},
        headers=student_a["headers"],
    )
    assert first.status_code in (200, 201)

    second = await client.post(
        "/classes/join",
        json={"invite_code": invite},
        headers=student_b["headers"],
    )
    assert second.status_code == 400
    assert "đầy" in second.json().get("detail", "").lower() or "full" in second.json().get("detail", "").lower()


@pytest.mark.asyncio
async def test_delete_class_with_students_rejected(
    client, student_auth, instructor_auth, instructor_with_class
):
    class_id = instructor_with_class["class_id"]
    join = await client.post(
        "/classes/join",
        json={"invite_code": instructor_with_class["invite_code"]},
        headers=student_auth["headers"],
    )
    assert join.status_code in (200, 201)

    response = await client.delete(
        f"/classes/{class_id}",
        headers=instructor_auth["headers"],
    )
    assert response.status_code == 400
    detail = response.json().get("detail", "").lower()
    assert "học viên" in detail or "student" in detail or "xóa" in detail
