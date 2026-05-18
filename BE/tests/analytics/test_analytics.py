"""Analytics API tests."""

import pytest


@pytest.mark.asyncio
async def test_learning_stats(client, student_auth):
    response = await client.get("/analytics/learning-stats", headers=student_auth["headers"])
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_progress_chart(client, student_auth):
    response = await client.get(
        "/analytics/progress-chart",
        params={"time_range": "week"},
        headers=student_auth["headers"],
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_instructor_class_stats(client, instructor_auth, instructor_with_class):
    response = await client.get(
        "/analytics/instructor/classes",
        headers=instructor_auth["headers"],
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_instructor_quiz_performance(client, instructor_auth):
    response = await client.get(
        "/analytics/instructor/quiz-performance",
        headers=instructor_auth["headers"],
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_instructor_progress_chart(client, instructor_auth, instructor_with_class):
    response = await client.get(
        "/analytics/instructor/progress-chart",
        params={"time_range": "week", "class_id": instructor_with_class["class_id"]},
        headers=instructor_auth["headers"],
    )
    assert response.status_code == 200
