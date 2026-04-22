"""
Learning Schemas - Module & Lesson Content
Định nghĩa request/response schemas cho learning endpoints (Section 2.4.1-2.4.2)
Tuân thủ: CHUCNANG.md Section 2.4, ENDPOINTS.md learning_router
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict


# ============================================================================
# SECTION 2.4.1: XEM THÔNG TIN MODULE
# ============================================================================

class LessonSummaryInModule(BaseModel):
    """Summary của lesson trong module detail"""
    id: str = Field(..., description="UUID của lesson")
    title: str = Field(..., description="Tiêu đề lesson")
    order: int = Field(..., description="Thứ tự lesson trong module")
    duration_minutes: int = Field(..., description="Thời lượng ước tính (phút)")
    content_type: str = Field(..., description="text|video|mixed")
    has_quiz: bool = Field(False, description="Có quiz kèm theo không")
    is_completed: bool = Field(..., description="Trạng thái hoàn thành của user hiện tại")
    is_locked: bool = Field(False, description="Bị khóa do chưa hoàn thành lesson trước")


class LearningOutcome(BaseModel):
    """Mục tiêu học tập của module"""
    id: str = Field(..., description="UUID")
    outcome: str = Field(..., description="Mô tả mục tiêu cụ thể")
    skill_tag: str = Field(..., description="Tag để tracking, vd: 'python-functions'")
    is_mandatory: bool = Field(..., description="Kiến thức bắt buộc hay tùy chọn")


class ResourceItem(BaseModel):
    """Tài nguyên đính kèm"""
    id: str = Field(..., description="UUID")
    title: str = Field(..., description="Tên tài nguyên")
    type: str = Field(..., description="pdf|slide|code|video|link")
    url: str = Field(..., description="Link download/view")
    size_mb: float = Field(0.0, description="Kích thước file (MB), default 0")
    description: str = Field("", description="Mô tả ngắn, default empty string")


class ModuleDetailResponse(BaseModel):
    """
    Response cho GET /api/v1/courses/{course_id}/modules/{module_id}
    Section 2.4.1: Xem thông tin chi tiết module
    """
    id: str = Field(..., description="UUID của module")
    title: str = Field(..., description="Tiêu đề module")
    description: str = Field(..., description="Mô tả chi tiết module")
    difficulty: str = Field(..., description="Basic|Intermediate|Advanced")
    order: int = Field(..., description="Thứ tự module trong khóa học")
    
    # Lessons trong module
    lessons: List[LessonSummaryInModule] = Field(..., description="Danh sách lessons theo thứ tự")
    
    # Learning outcomes
    learning_outcomes: List[LearningOutcome] = Field(..., description="Mục tiêu học tập")
    
    # Thời lượng học
    estimated_hours: float = Field(..., description="Thời gian học ước tính (giờ)")
    
    # Tài nguyên đính kèm
    resources: List[ResourceItem] = Field(default_factory=list, description="Tài nguyên học tập")
    
    # Trạng thái của user hiện tại
    completion_status: str = Field(..., description="not-started|in-progress|completed")
    completed_lessons: int = Field(..., description="Số lessons đã hoàn thành")
    total_lessons: int = Field(..., description="Tổng số lessons")
    progress_percent: float = Field(..., description="% hoàn thành (0-100)")
    is_accessible: bool = Field(..., description="Module có thể truy cập (không bị khóa)")
    
    # Prerequisites
    prerequisites: List[str] = Field(default_factory=list, description="Danh sách module IDs tiên quyết")


# ============================================================================
# SECTION 2.4.2: XEM NỘI DUNG BÀI HỌC
# ============================================================================

class AttachmentFile(BaseModel):
    """Tài liệu đính kèm trong lesson"""
    id: str = Field(..., description="UUID")
    filename: str = Field(..., description="Tên file")
    file_type: str = Field(..., description="pdf|docx|code|other")
    url: str = Field(..., description="Link download")
    size_mb: float = Field(0.0, description="Kích thước file (MB), default 0 nếu không rõ")


class VideoInfo(BaseModel):
    """Thông tin video bài giảng"""
    url: str = Field(..., description="Link video")
    duration_seconds: int = Field(..., description="Thời lượng video (giây)")
    thumbnail_url: Optional[str] = Field(None, description="Link thumbnail")
    quality: List[str] = Field(default_factory=lambda: ["360p", "720p", "1080p"], description="Chất lượng có sẵn")


class NavigationLesson(BaseModel):
    """Thông tin lesson trong navigation - tuân thủ API_SCHEMA.md"""
    id: Optional[str] = Field(None, description="UUID lesson (null nếu không có)")
    title: Optional[str] = Field(None, description="Tiêu đề lesson (null nếu không có)")
    is_locked: Optional[bool] = Field(None, description="Bị khóa hay không (chỉ cho next_lesson)")


class QuizInfoInLesson(BaseModel):
    """Thông tin quiz kèm theo lesson - tuân thủ API_SCHEMA.md"""
    quiz_id: Optional[str] = Field(None, description="UUID quiz (null nếu has_quiz=false)")
    question_count: Optional[int] = Field(None, description="Số câu hỏi (null nếu has_quiz=false)")
    is_mandatory: Optional[bool] = Field(None, description="Bắt buộc làm quiz để tiếp tục (null nếu has_quiz=false)")


class CompletionStatusInLesson(BaseModel):
    """Trạng thái hoàn thành của lesson - tuân thủ API_SCHEMA.md"""
    is_completed: bool = Field(False, description="Đã hoàn thành chưa")
    completion_date: Optional[datetime] = Field(None, description="Ngày hoàn thành (null nếu chưa xong)")
    time_spent_minutes: int = Field(0, description="Thời gian đã học (phút)")
    video_progress_percent: Optional[float] = Field(None, description="0-100, tiến độ xem video (null nếu không có video)")


class LessonContentResponse(BaseModel):
    """
    Response cho GET /api/v1/courses/{course_id}/lessons/{lesson_id}
    Section 2.4.2: Xem nội dung bài học
    FIXED: Tuân thủ API_SCHEMA.md Section 4.2 với navigation và quiz_info nested
    """
    id: str = Field(..., description="UUID của lesson")
    course_id: str = Field(..., description="UUID của khóa học")
    title: str = Field(..., description="Tiêu đề lesson")
    module_id: Optional[str] = Field(None, description="UUID của module cha")
    module_title: Optional[str] = Field(None, description="Tên module")
    order: int = Field(..., description="Thứ tự lesson")
    duration_minutes: int = Field(..., description="Thời lượng ước tính")
    
    # Nội dung
    content_type: str = Field(..., description="text|video|mixed")
    text_content: Optional[str] = Field(None, description="Nội dung HTML/Markdown")
    video_info: Optional[VideoInfo] = Field(None, description="Thông tin video nếu có")
    attachments: List[AttachmentFile] = Field(default_factory=list, description="Tài liệu đính kèm")
    
    # Learning objectives - ADDED theo API_SCHEMA.md
    learning_objectives: List[str] = Field(default_factory=list, description="Mục tiêu cụ thể của bài học này")
    
    # Resources - ADDED theo API_SCHEMA.md
    resources: List[ResourceItem] = Field(default_factory=list, description="Tài nguyên học tập")
    
    # Navigation - FIXED: Nested objects theo API_SCHEMA.md
    navigation: Dict = Field(..., description="Navigation info with previous_lesson and next_lesson objects")
    # Structure: {
    #   "previous_lesson": {"id": str|null, "title": str|null},
    #   "next_lesson": {"id": str|null, "title": str|null, "is_locked": bool}
    # }
    
    # Quiz info - FIXED: Nested object theo API_SCHEMA.md (Dict để accept service response)
    has_quiz: bool = Field(False, description="Bài học có quiz kèm theo không")
    quiz_info: Dict = Field(..., description="Thông tin quiz kèm theo: {quiz_id: str|null, question_count: int|null, is_mandatory: bool|null}")
    
    # Completion status - FIXED: Nested object theo API_SCHEMA.md (Dict để accept service response)
    completion_status: Dict = Field(..., description="Trạng thái hoàn thành: {is_completed: bool, completion_date: datetime|null, time_spent_minutes: int, video_progress_percent: float|null}")
    
    # Timestamps
    created_at: datetime = Field(..., description="Ngày tạo")
    updated_at: datetime = Field(..., description="Ngày cập nhật")


# ============================================================================
# ADDITIONAL ENDPOINTS (Notes trong ENDPOINTS.md)
# ============================================================================

class ModuleListItem(BaseModel):
    """Item trong danh sách modules"""
    id: str = Field(..., description="UUID")
    title: str = Field(..., description="Tiêu đề module")
    description: str = Field("", description="Mô tả module")
    difficulty: str = Field(..., description="Basic|Intermediate|Advanced")
    order: int = Field(..., description="Thứ tự")
    lesson_count: int = Field(..., description="Số lượng lessons")
    total_lessons: int = Field(..., description="Tổng số lessons")
    completed_lessons: int = Field(0, description="Số lessons đã hoàn thành")
    estimated_hours: float = Field(..., description="Thời lượng ước tính")
    progress_percent: float = Field(0.0, description="% hoàn thành của user")
    is_accessible: bool = Field(True, description="Có thể truy cập hay không")
    is_locked: bool = Field(False, description="Bị khóa do chưa hoàn thành module trước")
    status: str = Field("not-started", description="not-started|in-progress|completed")


class CourseModulesResponse(BaseModel):
    """
    Response cho GET /api/v1/courses/{course_id}/modules
    Lấy danh sách tất cả modules trong khóa học
    """
    course_id: str = Field(..., description="UUID")
    course_title: str = Field(..., description="Tên khóa học")
    modules: List[ModuleListItem] = Field(..., description="Danh sách modules")
    total_modules: int = Field(..., description="Tổng số modules")
    completed_modules: int = Field(0, description="Số modules đã hoàn thành")


class ModuleOutcomesResponse(BaseModel):
    """
    Response cho GET /api/v1/courses/{course_id}/modules/{module_id}/outcomes
    Lấy chi tiết learning outcomes của module
    """
    module_id: str = Field(..., description="UUID")
    module_title: str = Field(..., description="Tên module")
    learning_outcomes: List[LearningOutcome] = Field(..., description="Danh sách outcomes")
    total_outcomes: int = Field(..., description="Tổng số outcomes")
    achieved_outcomes: int = Field(0, description="Số outcomes đã đạt được")
    completion_status: str = Field(..., description="not-started|in-progress|completed")
    overall_score: float = Field(0.0, description="Điểm trung bình (0-100)")
    skills_acquired: List[str] = Field(default_factory=list, description="Các skill tags đã đạt")
    areas_for_improvement: List[str] = Field(default_factory=list, description="Các khu vực cần cải thiện")


class ModuleResourcesResponse(BaseModel):
    """
    Response cho GET /api/v1/courses/{course_id}/modules/{module_id}/resources
    Lấy tất cả tài nguyên học tập của module
    """
    module_id: str = Field(..., description="UUID")
    module_title: str = Field(..., description="Tên module")
    resources: List[ResourceItem] = Field(..., description="Danh sách tài nguyên")
    total_resources: int = Field(..., description="Tổng số tài nguyên")
    mandatory_resources: int = Field(0, description="Số tài nguyên bắt buộc")
    resource_categories: List[str] = Field(default_factory=list, description="Các loại tài nguyên")
    resources_by_type: Dict[str, int] = Field(..., description="Số lượng theo từng type")


class ModuleAssessmentGenerateRequest(BaseModel):
    """
    Request cho POST /api/v1/courses/{course_id}/modules/{module_id}/assessments/generate
    Sinh quiz đánh giá tự động cho module
    Tuân thủ API_SCHEMA.md
    """
    assessment_type: str = Field("practice", description="review|practice|final_check")
    question_count: Optional[int] = Field(10, ge=5, le=15, description="Số câu hỏi muốn sinh (5-15)")
    difficulty_preference: Optional[str] = Field("mixed", description="easy|mixed|hard")
    focus_topics: Optional[List[str]] = Field(None, description="Danh sách skill tags cần tập trung")
    time_limit_minutes: Optional[int] = Field(15, description="Thời gian làm bài (phút)")


class ModuleAssessmentGenerateResponse(BaseModel):
    """Response cho endpoint sinh quiz module - tuân thủ API_SCHEMA.md"""
    assessment_id: str = Field(..., description="UUID bài kiểm tra được tạo")
    module_id: str = Field(..., description="UUID module")
    module_title: str = Field(..., description="Tiêu đề module")
    assessment_type: str = Field(..., description="review|practice|final_check")
    question_count: int = Field(..., description="Số câu hỏi thực tế")
    time_limit_minutes: int = Field(..., description="Thời gian làm bài")
    total_points: int = Field(..., description="Tổng điểm tối đa")
    pass_threshold: int = Field(..., description="Điểm pass tối thiểu (thường 70%)")
    questions: List[Dict] = Field(..., description="Danh sách câu hỏi chi tiết")
    instructions: str = Field(..., description="Hướng dẫn làm bài")
    created_at: datetime = Field(..., description="Thời gian tạo")
    expires_at: datetime = Field(..., description="Thời hạn làm bài")
    can_retake: bool = Field(..., description="Có thể làm lại hay không")
    message: str = Field(..., description="Thông báo")
