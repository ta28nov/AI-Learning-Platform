"""Assessment API tests (generate, submit, results) with mocked AI."""

from datetime import datetime, timezone

import pytest

from tests.helpers.factories import assessment_generate_payload


@pytest.mark.asyncio
async def test_generate_assessment_success(client, student_auth, mock_ai):
    response = await client.post(
        "/assessments/generate",
        json=assessment_generate_payload(),
        headers=student_auth["headers"],
    )
    assert response.status_code == 201
    data = response.json()
    assert "session_id" in data
    assert data["question_count"] == 15
    assert len(data["questions"]) == 15


@pytest.mark.asyncio
async def test_generate_assessment_unauthorized(client, mock_ai):
    response = await client.post(
        "/assessments/generate",
        json=assessment_generate_payload(),
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_generate_assessment_validation_error(client, student_auth, mock_ai):
    response = await client.post(
        "/assessments/generate",
        json={"category": "Programming"},
        headers=student_auth["headers"],
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_submit_and_results(client, student_auth, mock_ai):
    gen = await client.post(
        "/assessments/generate",
        json=assessment_generate_payload(),
        headers=student_auth["headers"],
    )
    assert gen.status_code == 201
    session_id = gen.json()["session_id"]
    questions = gen.json()["questions"]

    answers = [
        {
            "question_id": q["question_id"],
            "answer_content": "A",
            "selected_option": 0,
            "time_taken_seconds": 30,
        }
        for q in questions
    ]
    submit = await client.post(
        f"/assessments/{session_id}/submit",
        json={
            "answers": answers,
            "total_time_seconds": 300,
            "submitted_at": datetime.now(timezone.utc).isoformat(),
        },
        headers=student_auth["headers"],
    )
    assert submit.status_code == 200
    assert submit.json()["session_id"] == session_id

    results = await client.get(
        f"/assessments/{session_id}/results",
        headers=student_auth["headers"],
    )
    assert results.status_code == 200
    assert "overall_score" in results.json() or "assessment" in results.json()


@pytest.mark.asyncio
async def test_submit_nonexistent_session(client, student_auth, mock_ai):
    response = await client.post(
        "/assessments/00000000-0000-0000-0000-000000000099/submit",
        json={
            "answers": [
                {
                    "question_id": "q1",
                    "answer_content": "A",
                    "selected_option": 0,
                    "time_taken_seconds": 1,
                }
            ],
            "total_time_seconds": 0,
            "submitted_at": datetime.now(timezone.utc).isoformat(),
        },
        headers=student_auth["headers"],
    )
    assert response.status_code in (404, 400, 422)


@pytest.mark.asyncio
async def test_assessment_history(client, student_auth, evaluated_assessment_session):
    response = await client.get("/assessments/history", headers=student_auth["headers"])
    assert response.status_code == 200
    body = response.json()
    sessions = body.get("sessions", body.get("history", body.get("data", [])))
    assert isinstance(sessions, list)
    assert len(sessions) >= 1


@pytest.mark.asyncio
async def test_assessment_history_unauthorized(client):
    response = await client.get("/assessments/history")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_assessment_review_success(client, student_auth, evaluated_assessment_session):
    session_id = evaluated_assessment_session["session_id"]
    response = await client.get(
        f"/assessments/{session_id}/review",
        headers=student_auth["headers"],
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_assessment_review_not_evaluated(client, student_auth, mock_ai):
    from tests.helpers.factories import assessment_generate_payload

    gen = await client.post(
        "/assessments/generate",
        json=assessment_generate_payload(),
        headers=student_auth["headers"],
    )
    session_id = gen.json()["session_id"]
    response = await client.get(
        f"/assessments/{session_id}/review",
        headers=student_auth["headers"],
    )
    assert response.status_code in (400, 404, 422)
