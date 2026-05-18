"""AI chat endpoints with mocked Gemini."""

import pytest


@pytest.mark.asyncio
async def test_send_chat_message(client, student_auth, sample_course_with_enrollment, mock_ai):
    course_id = sample_course_with_enrollment["course_id"]
    response = await client.post(
        f"/chat/course/{course_id}",
        json={"question": "What is this course about?"},
        headers=student_auth["headers"],
    )
    assert response.status_code == 201
    data = response.json()
    assert "answer" in data


@pytest.mark.asyncio
async def test_chat_history(client, student_auth, mock_ai):
    response = await client.get("/chat/history", headers=student_auth["headers"])
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_chat_unauthorized(client, sample_course_with_enrollment):
    course_id = sample_course_with_enrollment["course_id"]
    response = await client.post(
        f"/chat/course/{course_id}",
        json={"question": "Hello"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_conversation_detail_and_delete(
    client, student_auth, sample_course_with_enrollment, mock_ai
):
    course_id = sample_course_with_enrollment["course_id"]
    sent = await client.post(
        f"/chat/course/{course_id}",
        json={"question": "Explain module 1"},
        headers=student_auth["headers"],
    )
    assert sent.status_code == 201
    conversation_id = sent.json().get("conversation_id")

    if conversation_id:
        detail = await client.get(
            f"/chat/conversations/{conversation_id}",
            headers=student_auth["headers"],
        )
        assert detail.status_code == 200

        delete_one = await client.delete(
            f"/chat/history/{conversation_id}",
            headers=student_auth["headers"],
        )
        assert delete_one.status_code == 200

    await client.post(
        f"/chat/course/{course_id}",
        json={"question": "Another question"},
        headers=student_auth["headers"],
    )
    delete_all = await client.delete("/chat/conversations", headers=student_auth["headers"])
    assert delete_all.status_code == 200
