"""
Chat Schemas
Định nghĩa request/response schemas cho chat endpoints
Tuân thủ API_SCHEMA.md Section 2.6
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Literal


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class ChatMessageRequest(BaseModel):
    """Request schema cho chat message - Section 2.6.1"""
    question: str = Field(..., description="Câu hỏi của học viên")
    conversation_id: Optional[str] = Field(None, description="UUID conversation để duy trì context")
    context_type: Optional[Literal["lesson", "module", "general"]] = Field("general", description="Loại context")


# ============================================================================
# RESPONSE SCHEMAS - Section 2.6.1
# ============================================================================

class SourceInfo(BaseModel):
    """Thông tin nguồn trích dẫn từ course content"""
    type: str = Field(..., description="lesson|module|resource")
    id: str = Field(..., description="UUID")
    title: str = Field(..., description="Tiêu đề nguồn")
    excerpt: str = Field(..., description="Đoạn trích liên quan")


class RelatedLesson(BaseModel):
    """Bài học liên quan được suggest"""
    lesson_id: str = Field(..., description="UUID")
    title: str = Field(..., description="Tiêu đề bài học")
    url: str = Field(..., description="Link đến lesson")


class ChatMessageResponse(BaseModel):
    """Response schema cho chat message - Section 2.6.1"""
    conversation_id: str = Field(..., description="UUID conversation")
    message_id: str = Field(..., description="UUID của message này")
    question: str = Field(..., description="Câu hỏi đã gửi")
    answer: str = Field(..., description="Câu trả lời từ AI, markdown format")
    sources: List[SourceInfo] = Field(default_factory=list, description="Nguồn trích dẫn")
    related_lessons: List[RelatedLesson] = Field(default_factory=list, description="Bài học liên quan")
    timestamp: datetime = Field(..., description="Thời gian tạo message")
    tokens_used: Optional[int] = Field(None, description="Số tokens AI đã dùng (optional)")


# ============================================================================
# RESPONSE SCHEMAS - Section 2.6.2 (Chat History)
# ============================================================================

class ConversationListItem(BaseModel):
    """Item trong danh sách conversations"""
    conversation_id: str = Field(..., description="UUID")
    course_id: str = Field(..., description="UUID khóa học")
    course_title: str = Field(..., description="Tên khóa học")
    topic_summary: str = Field(..., description="Chủ đề chính được AI tóm tắt")
    message_count: int = Field(..., description="Số messages trong conversation")
    last_message_preview: str = Field(..., description="Preview message cuối, 100 ký tự")
    created_at: datetime = Field(..., description="Thời gian bắt đầu")
    last_updated: datetime = Field(..., description="Thời gian message cuối cùng")


class GroupedByDate(BaseModel):
    """Nhóm conversations theo thời gian"""
    today: List[str] = Field(default_factory=list, description="Conversation IDs hôm nay")
    yesterday: List[str] = Field(default_factory=list, description="Conversation IDs hôm qua")
    this_week: List[str] = Field(default_factory=list, description="Conversation IDs tuần này")
    older: List[str] = Field(default_factory=list, description="Conversation IDs cũ hơn")


class ChatHistoryListResponse(BaseModel):
    """Response schema cho chat history - Section 2.6.2"""
    conversations: List[ConversationListItem] = Field(..., description="Danh sách conversations")
    grouped_by_date: GroupedByDate = Field(..., description="Nhóm theo thời gian")
    total: int = Field(..., description="Tổng số conversations")
    skip: int = Field(..., description="Pagination skip")
    limit: int = Field(..., description="Pagination limit")


# ============================================================================
# RESPONSE SCHEMAS - Section 2.6.3 (Conversation Detail)
# ============================================================================

class MessageSource(BaseModel):
    """Nguồn trích dẫn trong message"""
    type: str = Field(..., description="lesson|module|resource")
    title: str = Field(..., description="Tiêu đề nguồn")
    url: str = Field(..., description="Link đến nguồn")


class Message(BaseModel):
    """Message trong conversation"""
    message_id: str = Field(..., description="UUID")
    role: str = Field(..., description="user|assistant")
    content: str = Field(..., description="Nội dung message, markdown format")
    timestamp: datetime = Field(..., description="Thời gian tạo message")
    sources: Optional[List[MessageSource]] = Field(None, description="Nguồn trích dẫn (optional)")


class CourseInfo(BaseModel):
    """Thông tin khóa học trong conversation detail"""
    course_id: str = Field(..., description="UUID")
    title: str = Field(..., description="Tên khóa học")
    thumbnail_url: Optional[str] = Field(None, description="URL ảnh thumbnail")


class ConversationDetailResponse(BaseModel):
    """Response schema cho conversation detail - Section 2.6.3"""
    conversation_id: str = Field(..., description="UUID conversation")
    course: CourseInfo = Field(..., description="Thông tin khóa học")
    created_at: datetime = Field(..., description="Thời gian bắt đầu conversation")
    last_updated: datetime = Field(..., description="Thời gian message cuối")
    message_count: int = Field(..., description="Số lượng messages")
    messages: List[Message] = Field(..., description="Danh sách messages")


# ============================================================================
# RESPONSE SCHEMAS - Section 2.6.4 & 2.6.5 (Delete)
# ============================================================================

class ChatDeleteResponse(BaseModel):
    """Response schema cho xóa một conversation - Section 2.6.5"""
    conversation_id: str = Field(..., description="UUID đã xóa")
    message: str = Field(..., description="Thông báo")
    deleted_at: datetime = Field(..., description="Thời gian xóa")


class ChatDeleteAllResponse(BaseModel):
    """Response schema cho xóa tất cả conversations - Section 2.6.4"""
    deleted_count: int = Field(..., description="Số conversations đã xóa")
    message: str = Field(..., description="Thông báo")
    deleted_at: datetime = Field(..., description="Thời gian xóa")
