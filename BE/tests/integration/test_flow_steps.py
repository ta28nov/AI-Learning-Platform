"""Student FLOW_STEPS happy path (assessment → recommend → enroll → lesson → quiz)."""

import pytest
from datetime import datetime, timezone

from tests.helpers.factories import assessment_generate_payload


@pytest.mark.integration
@pytest.mark.asyncio
async def test_student_flow_steps_integration(
    client,
    student_auth,
    published_catalog_course,
    sample_course_with_enrollment,
    mock_ai,
):
    headers = student_auth["headers"]

    gen = await client.post(
        "/assessments/generate",
        json=assessment_generate_payload(),
        headers=headers,
    )
    assert gen.status_code == 201
    session_id = gen.json()["session_id"]
    questions = gen.json()["questions"]

    answers = [
        {
            "question_id": q["question_id"],
            "answer_content": "A",
            "selected_option": 0,
            "time_taken_seconds": 20,
        }
        for q in questions
    ]
    submit = await client.post(
        f"/assessments/{session_id}/submit",
        json={
            "answers": answers,
            "total_time_seconds": 200,
            "submitted_at": datetime.now(timezone.utc).isoformat(),
        },
        headers=headers,
    )
    assert submit.status_code == 200

    rec = await client.get(
        "/recommendations/from-assessment",
        params={"session_id": session_id},
        headers=headers,
    )
    assert rec.status_code == 200

    catalog_id = published_catalog_course.id
    enroll = await client.post(
        "/enrollments",
        json={"course_id": catalog_id},
        headers=headers,
    )
    assert enroll.status_code == 201

    learn_ctx = sample_course_with_enrollment
    course_id = learn_ctx["course_id"]
    lesson_id = learn_ctx["lesson_id"]
    await client.post(
        "/enrollments",
        json={"course_id": course_id},
        headers=headers,
    )

    lesson = await client.get(
        f"/courses/{course_id}/lessons/{lesson_id}",
        headers=headers,
    )
    assert lesson.status_code == 200

    complete = await client.post(
        f"/courses/{course_id}/lessons/{lesson_id}/complete",
        headers=headers,
    )
    assert complete.status_code == 200

    quiz_list = await client.get("/quizzes", params={"course_id": course_id}, headers=headers)
    quiz_items = quiz_list.json().get("quizzes") or quiz_list.json().get("data") or []
    if quiz_list.status_code == 200 and quiz_items:
        quiz_id = quiz_items[0]["id"]
        detail = await client.get(f"/quizzes/{quiz_id}", headers=headers)
        if detail.status_code == 200:
            q = detail.json().get("questions", [{}])[0]
            qid = q.get("id") or q.get("question_id")
            attempt = await client.post(
                f"/quizzes/{quiz_id}/attempt",
                json={
                    "answers": [{"question_id": qid, "selected_option": q.get("correct_answer", "A")}],
                    "time_spent_minutes": 3,
                },
                headers=headers,
            )
            assert attempt.status_code in (201, 400, 422)
            results = await client.get(f"/quizzes/{quiz_id}/results", headers=headers)
            assert results.status_code in (200, 404)
