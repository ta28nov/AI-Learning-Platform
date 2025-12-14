"""
Chat Router
Định nghĩa routes cho AI chatbot endpoints
Section 2.6.1-2.6.5
5 endpoints
"""

from fastapi import APIRouter, Depends, status, Query
from middleware.auth import get_current_user
from controllers.chat_controller import (
    handle_send_chat_message,
    handle_get_chat_history,
    handle_get_conversation_detail,
    handle_delete_all_conversations,
    handle_delete_conversation
)
from schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatHistoryListResponse,
    ConversationDetailResponse,
    ChatDeleteAllResponse,
    ChatDeleteResponse
)


router = APIRouter(prefix="/chat", tags=["Chat AI"])


@router.post(
    "/course/{course_id}",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Gửi câu hỏi cho AI chatbot",
    description="Chatbot trả lời dựa trên nội dung khóa học (RAG), kèm nguồn lesson liên quan"
)
async def send_chat_message(
    course_id: str,
    message_data: ChatMessageRequest,
    current_user: dict = Depends(get_current_user)
):
    """Section 2.6.1 - Gửi tin nhắn chat"""
    return await handle_send_chat_message(course_id, message_data, current_user)


@router.get(
    "/history",
    response_model=ChatHistoryListResponse,
    status_code=status.HTTP_200_OK,
    summary="Lịch sử conversations",
    description="Danh sách conversations theo khóa học với pagination"
)
async def get_chat_history(
    course_id: str = Query(None, description="UUID khóa học để lọc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user)
):
    """Section 2.6.2 - Xem lịch sử chat"""
    return await handle_get_chat_history(course_id, skip, limit, current_user)


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Chi tiết conversation",
    description="Hiển thị toàn bộ messages trong conversation với AI summary"
)
async def get_conversation_detail(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Section 2.6.3 - Xem chi tiết conversation"""
    return await handle_get_conversation_detail(conversation_id, current_user)


@router.delete(
    "/conversations",
    response_model=ChatDeleteAllResponse,
    status_code=status.HTTP_200_OK,
    summary="Xóa toàn bộ lịch sử chat",
    description="Xóa tất cả conversations của user"
)
async def delete_all_conversations(
    current_user: dict = Depends(get_current_user)
):
    """Section 2.6.4 - Xóa toàn bộ lịch sử"""
    return await handle_delete_all_conversations(current_user)


@router.delete(
    "/history/{conversation_id}",
    response_model=ChatDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Xóa một conversation",
    description="Xóa conversation cụ thể"
)
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Section 2.6.5 - Xóa conversation"""
    return await handle_delete_conversation(conversation_id, current_user)

