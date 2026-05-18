"""Personal courses API tests."""

import pytest


@pytest.mark.asyncio
async def test_create_from_prompt(client, student_auth, mock_ai):
    response = await client.post(
        "/courses/from-prompt",
        json={
            "prompt": "I want to learn Python basics for data analysis over 4 weeks",
            "level": "Beginner",
        },
        headers=student_auth["headers"],
    )
    assert response.status_code == 201
    body = response.json()
    course_id = body.get("course_id") or body.get("id")
    assert course_id

    listing = await client.get("/courses/my-personal", headers=student_auth["headers"])
    assert listing.status_code == 200

    detail = await client.get(
        f"/courses/personal/{course_id}",
        headers=student_auth["headers"],
    )
    assert detail.status_code == 200

    update = await client.put(
        f"/courses/personal/{course_id}",
        json={"title": "Updated Personal Course"},
        headers=student_auth["headers"],
    )
    assert update.status_code == 200

    delete = await client.delete(
        f"/courses/personal/{course_id}",
        headers=student_auth["headers"],
    )
    assert delete.status_code == 200


@pytest.mark.asyncio
async def test_create_personal_manual(client, student_auth):
    response = await client.post(
        "/courses/personal",
        json={
            "title": "My Manual Course",
            "description": "A personal course created manually for testing purposes",
            "category": "Programming",
            "level": "Beginner",
        },
        headers=student_auth["headers"],
    )
    assert response.status_code == 201
