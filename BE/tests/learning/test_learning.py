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
