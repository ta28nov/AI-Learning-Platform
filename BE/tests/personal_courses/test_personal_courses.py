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
async def test_create_from_prompt_malformed_ai_learning_outcomes(client, student_auth, monkeypatch):
    """BE must not 500 when Gemini returns loose learning_outcomes (missing skill_tag, etc.)."""

    async def loose_ai(*args, **kwargs):
        return {
            "title": "Loose AI Course",
            "description": "x" * 40,
            "category": "Programming",
            "level": "beginner",  # non-canonical casing
            "modules": [
                {
                    "title": "Module A",
                    "description": "Intro",
                    "learning_outcomes": [
                        "Plain string outcome",
                        {"only_desc": "dict without description key", "skill_tag": "x"},
                        {"description": "Valid pair", "skill_tag": "ok"},
                    ],
                    "lessons": [
                        {"title": "", "content": "body", "order": "1"},
                    ],
                }
            ],
        }

    monkeypatch.setattr(
        "services.personal_courses_service.generate_course_from_prompt",
        loose_ai,
    )

    response = await client.post(
        "/courses/from-prompt",
        json={
            "prompt": "I want to learn Python basics for data analysis over 4 weeks",
            "level": "Beginner",
        },
        headers=student_auth["headers"],
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body.get("id") or body.get("course_id")
    mod0 = body["modules"][0]
    assert all("description" in lo and "skill_tag" in lo for lo in mod0["learning_outcomes"])


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
