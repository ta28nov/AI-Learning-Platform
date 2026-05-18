"""Quiz endpoint tests."""

import pytest


@pytest.mark.asyncio
async def test_get_quiz_detail(client, student_auth, sample_quiz):
    response = await client.get(
        f"/quizzes/{sample_quiz.id}",
        headers=student_auth["headers"],
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_quiz.id
    assert data["question_count"] == 1


@pytest.mark.asyncio
async def test_get_quiz_unauthorized(client, sample_quiz):
    response = await client.get(f"/quizzes/{sample_quiz.id}")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_attempt_quiz_success(client, student_auth, sample_quiz):
    q = sample_quiz.questions[0]
    response = await client.post(
        f"/quizzes/{sample_quiz.id}/attempt",
        json={
            "answers": [{"question_id": q["id"], "selected_option": "4"}],
            "time_spent_minutes": 5,
        },
        headers=student_auth["headers"],
    )
    assert response.status_code == 201
    data = response.json()
    assert data["quiz_id"] == sample_quiz.id
    assert "score" in data


@pytest.mark.asyncio
async def test_attempt_quiz_not_found(client, student_auth):
    response = await client.post(
        "/quizzes/00000000-0000-0000-0000-000000000099/attempt",
        json={"answers": [], "time_spent_minutes": 1},
        headers=student_auth["headers"],
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_quizzes(client, student_auth, sample_quiz):
    response = await client.get(
        "/quizzes",
        params={"course_id": sample_quiz.course_id},
        headers=student_auth["headers"],
    )
    assert response.status_code == 200
    body = response.json()
    assert "quizzes" in body or "data" in body


@pytest.mark.asyncio
async def test_quiz_results_after_attempt(client, student_auth, sample_quiz):
    q = sample_quiz.questions[0]
    await client.post(
        f"/quizzes/{sample_quiz.id}/attempt",
        json={
            "answers": [{"question_id": q["id"], "selected_option": "4"}],
            "time_spent_minutes": 2,
        },
        headers=student_auth["headers"],
    )
    response = await client.get(
        f"/quizzes/{sample_quiz.id}/results",
        headers=student_auth["headers"],
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_quiz_retake(client, student_auth, sample_quiz):
    response = await client.post(
        f"/quizzes/{sample_quiz.id}/retake",
        headers=student_auth["headers"],
    )
    assert response.status_code == 201
    assert "new_quiz_id" in response.json() or "quiz_id" in response.json()


@pytest.mark.asyncio
async def test_generate_practice_success(client, student_auth, sample_course_with_enrollment, mock_ai):
    ctx = sample_course_with_enrollment
    response = await client.post(
        "/ai/generate-practice",
        json={
            "course_id": ctx["course_id"],
            "topic_prompt": "Python basics practice exercises",
            "difficulty": "medium",
            "question_count": 3,
        },
        headers=student_auth["headers"],
    )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_generate_practice_unauthorized(client, mock_ai):
    response = await client.post(
        "/ai/generate-practice",
        json={"topic_prompt": "test topic for practice", "question_count": 3},
    )
    assert response.status_code == 403
