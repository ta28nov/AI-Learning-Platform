"""Recommendation API tests."""

import pytest

from tests.helpers.factories import assessment_generate_payload


@pytest.mark.asyncio
async def test_from_assessment_success(
    client, student_auth, evaluated_assessment_session, published_catalog_course, mock_ai
):
    session_id = evaluated_assessment_session["session_id"]
    response = await client.get(
        "/recommendations/from-assessment",
        params={"session_id": session_id},
        headers=student_auth["headers"],
    )
    assert response.status_code == 200
    data = response.json()
    assert "recommended_courses" in data or "courses" in data or "learning_path" in data


@pytest.mark.asyncio
async def test_from_assessment_not_evaluated(client, student_auth, mock_ai):
    gen = await client.post(
        "/assessments/generate",
        json=assessment_generate_payload(),
        headers=student_auth["headers"],
    )
    assert gen.status_code == 201
    session_id = gen.json()["session_id"]
    response = await client.get(
        "/recommendations/from-assessment",
        params={"session_id": session_id},
        headers=student_auth["headers"],
    )
    assert response.status_code in (400, 404, 422)


@pytest.mark.asyncio
async def test_from_assessment_unauthorized(client, evaluated_assessment_session):
    response = await client.get(
        "/recommendations/from-assessment",
        params={"session_id": evaluated_assessment_session["session_id"]},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_recommendations(client, student_auth, mock_ai):
    response = await client.get("/recommendations", headers=student_auth["headers"])
    assert response.status_code == 200
