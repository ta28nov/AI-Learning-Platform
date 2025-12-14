"""
Chat Service - Xử lý chatbot với context khóa học
Sử dụng: Beanie ODM, Google Gemini (via ai_service)
Tuân thủ: CHUCNANG.md Section 2.6
"""

from datetime import datetime
from typing import Optional, List, Dict
from models.models import Conversation
from services.ai_service import chat_with_course_context


# ============================================================================
# CONVERSATION CRUD
# ============================================================================

async def create_conversation(
    user_id: str,
    course_id: str,
    title: str = "New Conversation"
) -> Conversation:
    """
    Tạo conversation mới
    
    Args:
        user_id: ID của user
        course_id: ID của course
        title: Tiêu đề conversation
        
    Returns:
        Conversation document đã tạo
    """
    conversation = Conversation(
        user_id=user_id,
        course_id=course_id,
        title=title
    )
    
    await conversation.insert()
    return conversation


async def get_conversation_by_id(conversation_id: str) -> Optional[Conversation]:
    """
    Lấy conversation theo ID
    
    Args:
        conversation_id: ID của conversation
        
    Returns:
        Conversation document hoặc None
    """
    try:
        conversation = await Conversation.get(conversation_id)
        return conversation
    except Exception:
        return None


async def get_user_conversations(
    user_id: str,
    course_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
) -> List[Conversation]:
    """
    Lấy danh sách conversations của user
    
    Args:
        user_id: ID của user
        course_id: Filter theo course (optional)
        skip: Pagination skip
        limit: Pagination limit
        
    Returns:
        List Conversation documents
    """
    query = Conversation.find(Conversation.user_id == user_id)
    
    if course_id:
        query = query.find(Conversation.course_id == course_id)
    
    conversations = await query.skip(skip).limit(limit).to_list()
    return conversations


async def delete_conversation(conversation_id: str) -> bool:
    """
    Xóa conversation
    
    Args:
        conversation_id: ID của conversation
        
    Returns:
        True nếu xóa thành công, False nếu không tìm thấy
    """
    conversation = await get_conversation_by_id(conversation_id)
    
    if not conversation:
        return False
    
    await conversation.delete()
    return True


# ============================================================================
# CHAT MESSAGES (Section 2.6.1-2.6.3)
# ============================================================================

async def send_message(
    conversation_id: str,
    user_message: str
) -> Optional[Dict]:
    """
    Gửi tin nhắn và nhận phản hồi từ AI
    
    Args:
        conversation_id: ID của conversation
        user_message: Tin nhắn từ user
        
    Returns:
        Dict chứa:
        {
            "user_message": "...",
            "ai_response": "...",
            "timestamp": datetime
        }
        hoặc None nếu conversation không tồn tại
    """
    conversation = await get_conversation_by_id(conversation_id)
    
    if not conversation:
        return None
    
    # Lưu user message
    user_msg = {
        "role": "user",
        "content": user_message,
        "timestamp": datetime.utcnow()
    }
    conversation.messages.append(user_msg)
    
    # Lấy AI response với context
    ai_response_text = await chat_with_course_context(
        course_id=conversation.course_id,
        question=user_message,
        conversation_history=conversation.messages
    )
    
    # Lưu AI response
    ai_msg = {
        "role": "assistant",
        "content": ai_response_text,
        "timestamp": datetime.utcnow()
    }
    conversation.messages.append(ai_msg)
    
    conversation.updated_at = datetime.utcnow()
    await conversation.save()
    
    return {
        "user_message": user_message,
        "ai_response": ai_response_text,
        "timestamp": ai_msg["timestamp"]
    }


async def get_conversation_messages(
    conversation_id: str,
    skip: int = 0,
    limit: int = 50
) -> Optional[List[Dict]]:
    """
    Lấy messages trong conversation
    
    Args:
        conversation_id: ID của conversation
        skip: Bỏ qua số message đầu
        limit: Số lượng messages tối đa
        
    Returns:
        List messages hoặc None nếu conversation không tồn tại
    """
    conversation = await get_conversation_by_id(conversation_id)
    
    if not conversation:
        return None
    
    # Pagination trong list
    messages = conversation.messages[skip:skip+limit]
    return messages


async def clear_conversation_messages(conversation_id: str) -> Optional[Conversation]:
    """
    Xóa tất cả messages trong conversation
    
    Args:
        conversation_id: ID của conversation
        
    Returns:
        Conversation document đã update hoặc None
    """
    conversation = await get_conversation_by_id(conversation_id)
    
    if not conversation:
        return None
    
    conversation.messages = []
    conversation.updated_at = datetime.utcnow()
    
    await conversation.save()
    return conversation


# ============================================================================
# CONVERSATION MANAGEMENT
# ============================================================================

async def update_conversation_title(
    conversation_id: str,
    title: str
) -> Optional[Conversation]:
    """
    Cập nhật tiêu đề conversation
    
    Args:
        conversation_id: ID của conversation
        title: Tiêu đề mới
        
    Returns:
        Conversation document đã update hoặc None
    """
    conversation = await get_conversation_by_id(conversation_id)
    
    if not conversation:
        return None
    
    conversation.title = title
    conversation.updated_at = datetime.utcnow()
    
    await conversation.save()
    return conversation


async def get_recent_conversations(
    user_id: str,
    limit: int = 10
) -> List[Conversation]:
    """
    Lấy conversations gần đây của user
    
    Args:
        user_id: ID của user
        limit: Số lượng conversations
        
    Returns:
        List Conversation documents (sorted by updated_at desc)
    """
    conversations = await Conversation.find(
        Conversation.user_id == user_id
    ).sort(-Conversation.updated_at).limit(limit).to_list()
    
    return conversations
