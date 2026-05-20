"""Instructor role: classes, quizzes, analytics, RBAC."""

from datetime import datetime, timedelta, timezone

import pytest


@pytest.mark.asyncio
async def test_instructor_list_quizzes_with_filters(
    client, instructor_auth, sample_course_with_enrollment, instructor_with_class
):
    course_id = sample_course_with_enrollment["course_id"]
    response = await client.get(
        "/quizzes",
        params={
            "course_id": course_id,
            "class_id": instructor_with_class["class_id"],
            "search": "Integration",
            "sort_by": "created_at",
            "sort_order": "desc",
            "skip": 0,
            "limit": 10,
        },
        headers=instructor_auth["headers"],
    )
    assert response.status_code == 200
    body = response.json()
    assert "data" in body or "quizzes" in body


@pytest.mark.asyncio
async def test_instructor_quiz_update_forbidden_for_student(
    client, student_auth, instructor_auth, sample_course_with_enrollment
):
    lesson_id = sample_course_with_enrollment["lesson_id"]
    created = await client.post(
        f"/lessons/{lesson_id}/quizzes",
        json={
            "title": "Instructor Only Quiz",
            "description": "Quiz owned by instructor for RBAC test",
            "time_limit": 15,
            "pass_threshold": 70,
            "questions": [
                {
                    "type": "multiple_choice",
                    "question_text": "1+1?",
                    "options": ["1", "2"],
                    "correct_answer": "2",
                    "points": 5,
                    "order": 1,
                }
            ],
        },
        headers=instructor_auth["headers"],
    )
    assert created.status_code == 201
    quiz_id = created.json()["quiz_id"]

    response = await client.put(
        f"/quizzes/{quiz_id}",
        json={"title": "Hacked Title"},
        headers=student_auth["headers"],
    )
    assert response.status_code == 403

    await client.delete(f"/quizzes/{quiz_id}", headers=instructor_auth["headers"])


@pytest.mark.asyncio
async def test_instructor_cannot_access_other_instructors_class(
    client, instructor_auth, instructor_with_class
):
    other = await _create_second_instructor(client)
    class_id = instructor_with_class["class_id"]
    response = await client.get(
        f"/classes/{class_id}",
        headers=other["headers"],
    )
    assert response.status_code in (403, 404)


@pytest.mark.asyncio
async def test_student_cannot_create_class_known_bug(
    client, student_auth, published_catalog_course
):
    """BUG-011: POST /classes does not check role — student currently gets 201."""
    now = datetime.now(timezone.utc)
    response = await client.post(
        "/classes",
        json={
            "name": "Student Created Class",
            "description": "Should be forbidden for student role",
            "course_id": published_catalog_course.id,
            "start_date": now.isoformat(),
            "end_date": (now + timedelta(days=30)).isoformat(),
            "max_students": 10,
        },
        headers=student_auth["headers"],
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_student_cannot_access_instructor_analytics(client, student_auth):
    for path in (
        "/analytics/instructor/classes",
        "/analytics/instructor/progress-chart",
        "/analytics/instructor/quiz-performance",
    ):
        response = await client.get(path, headers=student_auth["headers"])
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_instructor_analytics_with_class_filter(
    client, instructor_auth, instructor_with_class
):
    response = await client.get(
        "/analytics/instructor/classes",
        params={"class_id": instructor_with_class["class_id"]},
        headers=instructor_auth["headers"],
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_instructor_analytics_progress_chart_month(
    client, instructor_auth, instructor_with_class
):
    response = await client.get(
        "/analytics/instructor/progress-chart",
        params={"time_range": "month", "class_id": instructor_with_class["class_id"]},
        headers=instructor_auth["headers"],
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_instructor_dashboard_forbidden_for_student(client, student_auth):
    response = await client.get("/dashboard/instructor", headers=student_auth["headers"])
    assert response.status_code == 403


async def _create_second_instructor(client):
    from tests.helpers.auth import login_user, bearer
    from models.models import UserDocument
    from utils.security import hash_password

    user = UserDocument(
        full_name="Other Instructor",
        email="other-instructor-pytest@example.com",
        hashed_password=hash_password("TestPass1!"),
        role="instructor",
        status="active",
    )
    await user.insert()
    res = await login_user(client, user.email)
    return {"user": user, "headers": bearer(res.json()["access_token"])}
