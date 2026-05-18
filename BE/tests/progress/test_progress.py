"""Progress tracking API tests."""

import pytest


@pytest.mark.asyncio
async def test_course_progress(client, student_auth, sample_course_with_enrollment):
    course_id = sample_course_with_enrollment["course_id"]
    response = await client.get(
        f"/progress/course/{course_id}",
        headers=student_auth["headers"],
    )
    assert response.status_code == 200
    body = response.json()
    assert "progress_percent" in body or "overall_progress" in body or "modules" in body
