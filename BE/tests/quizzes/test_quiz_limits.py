"""Quiz attempt limits."""

import uuid

import pytest

from models.models import EnrollmentDocument, QuizDocument


@pytest.mark.asyncio
async def test_quiz_attempt_exceeds_max_attempts(client, student_auth, student_user):
    course_id = str(uuid.uuid4())
    lesson_id = str(uuid.uuid4())
    qid = str(uuid.uuid4())
    quiz = QuizDocument(
        lesson_id=lesson_id,
        course_id=course_id,
        title="Max Attempts Quiz",
        description="Single attempt allowed",
        time_limit_minutes=15,
        passing_score=70.0,
        max_attempts=1,
        is_draft=False,
        questions=[
            {
                "id": qid,
                "type": "multiple_choice",
                "question_text": "2+2?",
                "options": ["3", "4"],
                "correct_answer": "4",
                "points": 10,
                "is_mandatory": True,
                "order": 1,
            }
        ],
        question_count=1,
        total_points=10,
        mandatory_question_count=1,
        created_by=student_user.id,
    )
    await quiz.insert()
    await EnrollmentDocument(
        user_id=student_user.id,
        course_id=course_id,
        status="active",
    ).insert()

    payload = {
        "answers": [{"question_id": qid, "selected_option": "4"}],
        "time_spent_minutes": 1,
    }
    first = await client.post(
        f"/quizzes/{quiz.id}/attempt",
        json=payload,
        headers=student_auth["headers"],
    )
    assert first.status_code == 201

    second = await client.post(
        f"/quizzes/{quiz.id}/attempt",
        json=payload,
        headers=student_auth["headers"],
    )
    assert second.status_code == 403
    assert "lượt" in second.json().get("detail", "").lower() or "max" in second.json().get("detail", "").lower()
