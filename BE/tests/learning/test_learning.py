"""Learning modules and lessons tests."""

import pytest


@pytest.mark.asyncio
async def test_get_course_modules(client, student_auth, sample_course_with_enrollment):
    course_id = sample_course_with_enrollment["course_id"]
    response = await client.get(
        f"/courses/{course_id}/modules",
        headers=student_auth["headers"],
    )
    assert response.status_code == 200
    data = response.json()
    assert "modules" in data
    assert len(data["modules"]) >= 1


@pytest.mark.asyncio
async def test_get_lesson_content(client, student_auth, sample_course_with_enrollment):
    ctx = sample_course_with_enrollment
    response = await client.get(
        f"/courses/{ctx['course_id']}/lessons/{ctx['lesson_id']}",
        headers=student_auth["headers"],
    )
    assert response.status_code == 200
    assert response.json()["id"] == ctx["lesson_id"]


@pytest.mark.asyncio
async def test_complete_lesson(client, student_auth, sample_course_with_enrollment):
    ctx = sample_course_with_enrollment
    response = await client.post(
        f"/courses/{ctx['course_id']}/lessons/{ctx['lesson_id']}/complete",
        headers=student_auth["headers"],
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_course_modules_not_found(client, student_auth):
    response = await client.get(
        "/courses/00000000-0000-0000-0000-000000000099/modules",
        headers=student_auth["headers"],
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_module_detail(client, student_auth, sample_course_with_enrollment):
    ctx = sample_course_with_enrollment
    response = await client.get(
        f"/courses/{ctx['course_id']}/modules/{ctx['module_id']}",
        headers=student_auth["headers"],
    )
    assert response.status_code == 200
    assert response.json()["id"] == ctx["module_id"]


@pytest.mark.asyncio
async def test_get_module_outcomes(client, student_auth, sample_course_with_enrollment):
    ctx = sample_course_with_enrollment
    response = await client.get(
        f"/courses/{ctx['course_id']}/modules/{ctx['module_id']}/outcomes",
        headers=student_auth["headers"],
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_module_resources(client, student_auth, sample_course_with_enrollment):
    ctx = sample_course_with_enrollment
    response = await client.get(
        f"/courses/{ctx['course_id']}/modules/{ctx['module_id']}/resources",
        headers=student_auth["headers"],
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_generate_module_assessment(client, student_auth, sample_course_with_enrollment, mock_ai):
    ctx = sample_course_with_enrollment
    response = await client.post(
        f"/courses/{ctx['course_id']}/modules/{ctx['module_id']}/assessments/generate",
        json={"assessment_type": "practice", "question_count": 5},
        headers=student_auth["headers"],
    )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_get_module_detail_with_prerequisites(client, student_auth, student_user):
    """Module có prerequisites trả enriched objects, không 500 (UIUX-HV-05)."""
    import uuid
    from datetime import datetime

    from models.models import Course, EmbeddedLesson, EmbeddedModule, Enrollment

    course_id = str(uuid.uuid4())
    module1_id = str(uuid.uuid4())
    module2_id = str(uuid.uuid4())
    lesson_id = str(uuid.uuid4())

    module1 = EmbeddedModule(
        id=module1_id,
        title="Foundations",
        description="First module",
        order=1,
        learning_outcomes=[],
        lessons=[
            EmbeddedLesson(
                id=lesson_id,
                title="Intro",
                order=1,
                content="Hello",
                duration_minutes=10,
                is_published=True,
            )
        ],
        total_lessons=1,
        total_duration_minutes=10,
    )
    module2 = EmbeddedModule(
        id=module2_id,
        title="Advanced Topics",
        description="Second module",
        order=2,
        prerequisites=[module1_id],
        learning_outcomes=[],
        lessons=[],
        total_lessons=0,
        total_duration_minutes=0,
    )
    course = Course(
        id=course_id,
        title="Prereq Course",
        description="Test prerequisites",
        category="Programming",
        level="Beginner",
        status="published",
        owner_id=student_user.id,
        owner_type="admin",
        modules=[module1, module2],
        total_modules=2,
        total_lessons=1,
        total_duration_minutes=10,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    await course.insert()
    await Enrollment(
        user_id=student_user.id,
        course_id=course_id,
        status="active",
    ).insert()

    response = await client.get(
        f"/courses/{course_id}/modules/{module2_id}",
        headers=student_auth["headers"],
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == module2_id
    assert len(data["prerequisites"]) == 1
    assert data["prerequisites"][0]["id"] == module1_id
    assert data["prerequisites"][0]["title"] == "Foundations"


@pytest.mark.asyncio
async def test_instructor_lesson_content_without_enrollment(
    client, instructor_auth, instructor_with_class
):
    """GV có lớp gắn khóa public có thể đọc lesson để soạn quiz (UIUX-GV-07)."""
    from models.models import Course

    course_id = instructor_with_class["course_id"]
    course = await Course.get(course_id)
    lesson_id = course.modules[0].lessons[0].id

    response = await client.get(
        f"/courses/{course_id}/lessons/{lesson_id}",
        headers=instructor_auth["headers"],
    )
    assert response.status_code == 200
    assert response.json()["id"] == lesson_id
