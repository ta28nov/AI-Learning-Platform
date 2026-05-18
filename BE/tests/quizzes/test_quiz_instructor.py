"""Instructor quiz CRUD API tests."""

import pytest


@pytest.mark.asyncio
async def test_instructor_create_quiz(
    client, instructor_auth, sample_course_with_enrollment, instructor_with_class
):
    lesson_id = sample_course_with_enrollment["lesson_id"]
    response = await client.post(
        f"/lessons/{lesson_id}/quizzes",
        json={
            "title": "Instructor Quiz",
            "description": "Created in test",
            "time_limit": 30,
            "pass_threshold": 70,
            "questions": [
                {
                    "type": "multiple_choice",
                    "question_text": "2+2?",
                    "options": ["3", "4", "5"],
                    "correct_answer": "4",
                    "points": 10,
                    "is_mandatory": True,
                    "order": 1,
                }
            ],
        },
        headers=instructor_auth["headers"],
    )
    assert response.status_code == 201
    quiz_id = response.json().get("quiz_id")
    assert quiz_id

    update = await client.put(
        f"/quizzes/{quiz_id}",
        json={"title": "Updated Instructor Quiz"},
        headers=instructor_auth["headers"],
    )
    assert update.status_code == 200

    class_results = await client.get(
        f"/quizzes/{quiz_id}/class-results",
        params={"class_id": instructor_with_class["class_id"]},
        headers=instructor_auth["headers"],
    )
    assert class_results.status_code == 200

    delete = await client.delete(f"/quizzes/{quiz_id}", headers=instructor_auth["headers"])
    assert delete.status_code == 200


@pytest.mark.asyncio
async def test_student_cannot_create_quiz(client, student_auth, sample_course_with_enrollment):
    lesson_id = sample_course_with_enrollment["lesson_id"]
    response = await client.post(
        f"/lessons/{lesson_id}/quizzes",
        json={
            "title": "Student Quiz",
            "time_limit": 20,
            "pass_threshold": 60,
            "questions": [
                {
                    "type": "multiple_choice",
                    "question_text": "Q?",
                    "options": ["A", "B"],
                    "correct_answer": "A",
                    "points": 5,
                    "order": 1,
                }
            ],
        },
        headers=student_auth["headers"],
    )
    assert response.status_code == 403
