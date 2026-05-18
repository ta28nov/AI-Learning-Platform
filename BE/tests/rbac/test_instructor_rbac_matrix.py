"""RBAC matrix: instructor-only surfaces vs controller string checks."""

from datetime import datetime, timedelta, timezone

import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path,params",
    [
        ("/dashboard/instructor", None),
        ("/analytics/instructor/classes", None),
        ("/analytics/instructor/progress-chart", {"time_range": "week"}),
        ("/analytics/instructor/quiz-performance", None),
    ],
)
async def test_student_forbidden_on_instructor_dashboard_analytics(
    client, student_auth, path, params
):
    response = await client.get(path, headers=student_auth["headers"], params=params or {})
    assert response.status_code == 403


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path,params",
    [
        ("/dashboard/instructor", None),
        ("/analytics/instructor/classes", None),
    ],
)
async def test_admin_forbidden_on_instructor_strict_routes(
    client, admin_auth, path, params
):
    """
    Controllers use `role != \"instructor\"` (exact match).
    rbac.py hierarchy would allow admin — implementation disagrees with middleware design.
    """
    response = await client.get(path, headers=admin_auth["headers"], params=params or {})
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_instructor_allowed_on_instructor_dashboard_analytics(
    client, instructor_auth, instructor_with_class
):
    dash = await client.get("/dashboard/instructor", headers=instructor_auth["headers"])
    assert dash.status_code == 200

    stats = await client.get(
        "/analytics/instructor/classes",
        headers=instructor_auth["headers"],
        params={"class_id": instructor_with_class["class_id"]},
    )
    assert stats.status_code == 200


@pytest.mark.asyncio
async def test_admin_allowed_on_quiz_list_instructor_branch(
    client, admin_auth, sample_course_with_enrollment
):
    """Quiz list treats admin like instructor; unlike dashboard handlers."""
    response = await client.get(
        "/quizzes",
        params={"course_id": sample_course_with_enrollment["course_id"], "limit": 5},
        headers=admin_auth["headers"],
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_admin_forbidden_on_quiz_create_update_delete(
    client, admin_auth, instructor_auth, sample_course_with_enrollment
):
    lesson_id = sample_course_with_enrollment["lesson_id"]
    create_body = {
        "title": "Admin RBAC Quiz",
        "description": "Should be instructor-only",
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
    }

    created = await client.post(
        f"/lessons/{lesson_id}/quizzes",
        json=create_body,
        headers=admin_auth["headers"],
    )
    assert created.status_code == 403

    created_ok = await client.post(
        f"/lessons/{lesson_id}/quizzes",
        json=create_body,
        headers=instructor_auth["headers"],
    )
    assert created_ok.status_code == 201
    quiz_id = created_ok.json()["quiz_id"]

    update = await client.put(
        f"/quizzes/{quiz_id}",
        json={"title": "Admin update attempt"},
        headers=admin_auth["headers"],
    )
    assert update.status_code == 403

    delete = await client.delete(f"/quizzes/{quiz_id}", headers=admin_auth["headers"])
    assert delete.status_code == 403

    await client.delete(f"/quizzes/{quiz_id}", headers=instructor_auth["headers"])


@pytest.mark.asyncio
async def test_student_forbidden_on_quiz_mutations(
    client, student_auth, instructor_auth, sample_course_with_enrollment
):
    lesson_id = sample_course_with_enrollment["lesson_id"]
    body = {
        "title": "Student RBAC Quiz",
        "description": "Forbidden",
        "time_limit": 10,
        "pass_threshold": 70,
        "questions": [
            {
                "type": "multiple_choice",
                "question_text": "2+2?",
                "options": ["3", "4"],
                "correct_answer": "4",
                "points": 5,
                "order": 1,
            }
        ],
    }
    create = await client.post(
        f"/lessons/{lesson_id}/quizzes", json=body, headers=student_auth["headers"]
    )
    assert create.status_code == 403


@pytest.mark.asyncio
async def test_class_routes_no_role_gate_on_create_and_my_classes(
    client, student_auth, instructor_auth, published_catalog_course
):
    """
    class_controller has no role check — any authenticated user can POST /classes
    and GET /classes/my-classes (scoped by JWT user_id as instructor_id).
    """
    now = datetime.now(timezone.utc)
    payload = {
        "name": "RBAC Class Probe",
        "description": "No role middleware on classes router",
        "course_id": published_catalog_course.id,
        "start_date": now.isoformat(),
        "end_date": (now + timedelta(days=14)).isoformat(),
        "max_students": 5,
    }

    student_create = await client.post(
        "/classes", json=payload, headers=student_auth["headers"]
    )
    assert student_create.status_code == 201

    student_list = await client.get(
        "/classes/my-classes", headers=student_auth["headers"]
    )
    assert student_list.status_code == 200

    instructor_list = await client.get(
        "/classes/my-classes", headers=instructor_auth["headers"]
    )
    assert instructor_list.status_code == 200


@pytest.mark.asyncio
async def test_student_cannot_access_other_instructor_class_detail(
    client, student_auth, instructor_with_class
):
    class_id = instructor_with_class["class_id"]
    response = await client.get(
        f"/classes/{class_id}", headers=student_auth["headers"]
    )
    assert response.status_code in (403, 404)


@pytest.mark.asyncio
async def test_instructor_class_crud_owned_class(
    client, instructor_auth, instructor_with_class
):
    class_id = instructor_with_class["class_id"]
    detail = await client.get(
        f"/classes/{class_id}", headers=instructor_auth["headers"]
    )
    assert detail.status_code == 200

    update = await client.put(
        f"/classes/{class_id}",
        json={"name": "RBAC Renamed Class"},
        headers=instructor_auth["headers"],
    )
    assert update.status_code == 200

    students = await client.get(
        f"/classes/{class_id}/students", headers=instructor_auth["headers"]
    )
    assert students.status_code == 200


@pytest.mark.asyncio
async def test_student_dashboard_accessible_without_role_check(
    client, instructor_auth
):
    """Student dashboard/analytics have no role!=student guard — instructor gets 200."""
    dash = await client.get("/dashboard/student", headers=instructor_auth["headers"])
    assert dash.status_code == 200

    stats = await client.get(
        "/analytics/learning-stats", headers=instructor_auth["headers"]
    )
    assert stats.status_code == 200
