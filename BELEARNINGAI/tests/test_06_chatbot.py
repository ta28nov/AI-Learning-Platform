"""
TEST NHÓM 6: CHATBOT HỖ TRỢ AI (2.6)
Tổng: 5 endpoints

Endpoints:
1. POST /api/v1/chat/course/{course_id} - Chat hỏi đáp về khóa học
2. GET /api/v1/chat/history - Xem lịch sử hội thoại
3. GET /api/v1/chat/conversations/{conversation_id} - Xem chi tiết conversation
4. DELETE /api/v1/chat/conversations - Xóa tất cả lịch sử chat
5. DELETE /api/v1/chat/history/{conversation_id} - Xóa từng conversation

Sử dụng test_variables để lưu trữ conversation_id và tái sử dụng.
"""
import pytest
from httpx import AsyncClient
from tests.conftest import assert_response_schema
from tests.test_variables import TestVariables


class TestChatWithCourse:
    """Test cases cho chat hỏi đáp về khóa học."""
    
    @pytest.mark.asyncio
    async def test_chat_with_course_new_conversation(self, client: AsyncClient, test_vars: TestVariables, test_course, test_enrollment):
        """Test chat với khóa học - tạo conversation mới."""
        headers = test_vars.get_headers("student1")
        course_id = test_vars.course_id
        
        payload = {
            "message": "Giải thích cho tôi về Python variables là gì?",
            "conversation_id": None  # Conversation mới
        }
        
        response = await client.post(
            f"/api/v1/chat/course/{course_id}",
            headers=headers,
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Lưu conversation_id vào test_vars để dùng lại
        test_vars.conversation_id = data["conversation_id"]
        
        # Kiểm tra response schema
        required_fields = ["conversation_id", "message_id", "user_message", "ai_response",
                          "timestamp", "course_context"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra AI đã trả lời
        assert len(data["ai_response"]) > 0
        assert data["user_message"] == payload["message"]
        assert data["course_context"]["course_id"] == course_id
        
        # Conversation ID phải được tạo mới
        assert data["conversation_id"] is not None
    
    @pytest.mark.asyncio
    async def test_chat_with_course_continue_conversation(self, client: AsyncClient, test_vars: TestVariables, test_course, test_enrollment):
        """Test chat tiếp tục conversation cũ."""
        headers = test_vars.get_headers("student1")
        course_id = test_vars.course_id
        
        # Tin nhắn đầu tiên - tạo conversation
        first_payload = {
            "message": "Python là gì?",
            "conversation_id": None
        }
        first_response = await client.post(
            f"/api/v1/chat/course/{course_id}",
            headers=headers,
            json=first_payload
        )
        conversation_id = first_response.json()["conversation_id"]
        test_vars.conversation_id = conversation_id
        
        # Tin nhắn thứ hai - tiếp tục conversation
        second_payload = {
            "message": "Cho tôi ví dụ về Python list",
            "conversation_id": conversation_id
        }
        second_response = await client.post(
            f"/api/v1/chat/course/{course_id}",
            headers=headers,
            json=second_payload
        )
        
        assert second_response.status_code == 200
        data = second_response.json()
        
        # Phải cùng conversation_id
        assert data["conversation_id"] == conversation_id
        assert len(data["ai_response"]) > 0
    
    @pytest.mark.asyncio
    async def test_chat_with_course_not_enrolled(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test chat với khóa học chưa đăng ký."""
        headers = test_vars.get_headers("student2")  # Chưa đăng ký
        course_id = test_vars.course_id
        
        payload = {
            "message": "Test message",
            "conversation_id": None
        }
        
        response = await client.post(
            f"/api/v1/chat/course/{course_id}",
            headers=headers,
            json=payload
        )
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_chat_with_course_empty_message(self, client: AsyncClient, test_vars: TestVariables, test_course, test_enrollment):
        """Test chat với message rỗng."""
        headers = test_vars.get_headers("student1")
        course_id = test_vars.course_id
        
        payload = {
            "message": "",  # Message rỗng
            "conversation_id": None
        }
        
        response = await client.post(
            f"/api/v1/chat/course/{course_id}",
            headers=headers,
            json=payload
        )
        
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_chat_with_course_without_auth(self, client: AsyncClient, test_vars: TestVariables):
        """Test chat không có token."""
        course_id = test_vars.course_id
        
        payload = {
            "message": "Test message",
            "conversation_id": None
        }
        
        response = await client.post(
            f"/api/v1/chat/course/{course_id}",
            json=payload
        )
        
        assert response.status_code == 401


class TestChatHistory:
    """Test cases cho xem lịch sử hội thoại."""
    
    @pytest.mark.asyncio
    async def test_get_chat_history_success(self, client: AsyncClient, test_vars: TestVariables):
        """Test xem lịch sử chat thành công."""
        headers = test_vars.get_headers("student1")
        
        # Tạo một số conversations trước
        from models.models import Conversation
        from datetime import datetime, timezone
        
        for i in range(3):
            conv = Conversation(
                user_id=test_vars.student1_user_id,
                course_id="test-course-id",
                title=f"Conversation {i+1}",
                messages=[
                    {
                        "role": "user",
                        "content": f"Question {i+1}",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    },
                    {
                        "role": "assistant",
                        "content": f"Answer {i+1}",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                ]
            )
            await conv.insert()
        
        # Lấy lịch sử
        response = await client.get("/api/v1/chat/history", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema
        required_fields = ["conversations", "total", "skip", "limit"]
        assert_response_schema(data, required_fields)
        
        # Phải có ít nhất 3 conversations
        assert data["total"] >= 3
        assert len(data["conversations"]) >= 3
    
    @pytest.mark.asyncio
    async def test_get_chat_history_empty(self, client: AsyncClient, test_vars: TestVariables):
        """Test xem lịch sử khi chưa có conversation nào."""
        headers = test_vars.get_headers("student3")  # Student chưa chat
        
        response = await client.get("/api/v1/chat/history", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total"] == 0
        assert len(data["conversations"]) == 0


class TestConversationDetail:
    """Test cases cho xem chi tiết conversation."""
    
    @pytest.mark.asyncio
    async def test_get_conversation_detail_success(self, client: AsyncClient, test_vars: TestVariables):
        """Test xem chi tiết conversation thành công."""
        headers = test_vars.get_headers("student1")
        
        # Tạo conversation với messages
        from models.models import Conversation
        from datetime import datetime, timezone
        
        conv = Conversation(
            user_id=test_vars.student1_user_id,
            course_id="test-course",
            title="Test Conversation",
            messages=[
                {
                    "id": "msg1",
                    "role": "user",
                    "content": "What is Python?",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                {
                    "id": "msg2",
                    "role": "assistant",
                    "content": "Python is a programming language...",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            ]
        )
        await conv.insert()
        test_vars.conversation_id = str(conv.id)
        
        # Lấy chi tiết
        response = await client.get(
            f"/api/v1/chat/conversations/{conv.id}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema
        required_fields = ["id", "title", "course_id", "messages", "created_at", "updated_at"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra messages
        assert len(data["messages"]) >= 2
    
    @pytest.mark.asyncio
    async def test_get_conversation_detail_not_owner(self, client: AsyncClient, test_vars: TestVariables):
        """Test xem conversation của người khác."""
        # Student1 tạo conversation
        from models.models import Conversation
        conv = Conversation(
            user_id=test_vars.student1_user_id,
            course_id="test-course",
            title="Student1 Conversation",
            messages=[]
        )
        await conv.insert()
        
        # Student2 cố gắng xem
        headers2 = test_vars.get_headers("student2")
        
        response = await client.get(
            f"/api/v1/chat/conversations/{conv.id}",
            headers=headers2
        )
        
        assert response.status_code == 403


class TestDeleteAllConversations:
    """Test cases cho xóa tất cả lịch sử chat."""
    
    @pytest.mark.asyncio
    async def test_delete_all_conversations_success(self, client: AsyncClient, test_vars: TestVariables):
        """Test xóa tất cả conversations thành công."""
        headers = test_vars.get_headers("student1")
        
        # Tạo một số conversations
        from models.models import Conversation
        for i in range(3):
            conv = Conversation(
                user_id=test_vars.student1_user_id,
                course_id="test-course",
                title=f"Conversation {i+1}",
                messages=[]
            )
            await conv.insert()
        
        # Xóa tất cả
        response = await client.delete("/api/v1/chat/conversations", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "deleted_count" in data
        assert data["deleted_count"] >= 3


class TestDeleteSingleConversation:
    """Test cases cho xóa từng conversation."""
    
    @pytest.mark.asyncio
    async def test_delete_single_conversation_success(self, client: AsyncClient, test_vars: TestVariables):
        """Test xóa một conversation thành công."""
        headers = test_vars.get_headers("student1")
        
        # Tạo conversation
        from models.models import Conversation
        conv = Conversation(
            user_id=test_vars.student1_user_id,
            course_id="test-course",
            title="To Delete",
            messages=[]
        )
        await conv.insert()
        
        # Xóa
        response = await client.delete(
            f"/api/v1/chat/history/{conv.id}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
    
    @pytest.mark.asyncio
    async def test_delete_single_conversation_not_owner(self, client: AsyncClient, test_vars: TestVariables):
        """Test xóa conversation của người khác."""
        # Student1 tạo conversation
        from models.models import Conversation
        conv = Conversation(
            user_id=test_vars.student1_user_id,
            course_id="test-course",
            title="Student1 Conversation",
            messages=[]
        )
        await conv.insert()
        
        # Student2 cố gắng xóa
        headers2 = test_vars.get_headers("student2")
        
        response = await client.delete(
            f"/api/v1/chat/history/{conv.id}",
            headers=headers2
        )
        
        assert response.status_code == 403
