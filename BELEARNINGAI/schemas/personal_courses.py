"""
Personal Courses Schemas
Định nghĩa request/response schemas cho personal courses endpoints
Section 2.5.1-2.5.5
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import List, Optional


# ============================================================================
# Section 2.5.1: TẠO KHÓA HỌC TỪ AI PROMPT
# ============================================================================

class CourseFromPromptRequest(BaseModel):
    """Request tạo khóa học từ AI prompt"""
    prompt: str = Field(
        ..., 
        min_length=20,
        max_length=1000,
        description="Mô tả bằng ngôn ngữ tự nhiên về chủ đề và mục tiêu học tập"
    )
    level: Optional[str] = Field(
        "Beginner",
        description="Cấp độ khóa học (Beginner, Intermediate, Advanced)"
    )
    estimated_duration_weeks: Optional[int] = Field(
        4,
        description="Thời lượng học tập ước tính (tuần)"
    )
    language: Optional[str] = Field(
        "vi",
        description="Ngôn ngữ khóa học (vi, en)"
    )
    
    @validator('level')
    def validate_level(cls, v):
        """Validate level must be one of the allowed values"""
        if v and v not in ["Beginner", "Intermediate", "Advanced"]:
            raise ValueError("Level must be one of: Beginner, Intermediate, Advanced")
        return v


class GeneratedLesson(BaseModel):
    """Lesson được AI sinh ra"""
    id: str = Field(..., description="UUID của lesson")
    title: str = Field(..., description="Tiêu đề lesson")
    order: int = Field(..., description="Thứ tự lesson")
    content_outline: str = Field(..., description="Outline nội dung chính")


class LearningOutcome(BaseModel):
    """Learning outcome structure - khớp với API_SCHEMA"""
    description: str = Field(..., description="Mục tiêu cụ thể, đo lường được")
    skill_tag: str = Field(..., description="Kỹ năng liên quan")


class GeneratedModule(BaseModel):
    """Module được AI sinh ra"""
    id: str = Field(..., description="UUID của module")
    title: str = Field(..., description="Tiêu đề module")
    description: str = Field(..., description="Mô tả module")
    order: int = Field(..., description="Thứ tự module")
    difficulty: str = Field("Basic", description="Độ khó (Basic, Intermediate, Advanced)")
    learning_outcomes: List[LearningOutcome] = Field(
        default_factory=list,
        description="Các mục tiêu học tập"
    )
    lessons: List[GeneratedLesson] = Field(
        default_factory=list,
        description="Danh sách lessons trong module"
    )


class CourseFromPromptResponse(BaseModel):
    """Response sau khi AI tạo khóa học"""
    id: str = Field(..., description="UUID khóa học")
    title: str = Field(..., description="Tiêu đề khóa học do AI sinh")
    description: str = Field(..., description="Mô tả khóa học")
    category: str
    level: str
    status: str = Field(default="draft", description="Trạng thái: draft")
    owner_id: str = Field(..., description="UUID người tạo")
    owner_type: str = Field(default="student", description="Loại người tạo")
    
    modules: List[GeneratedModule] = Field(
        default_factory=list,
        description="Danh sách modules đã được AI sinh"
    )
    
    message: str = Field(
        default="Khóa học draft đã được tạo, bạn có thể chỉnh sửa trước khi xuất bản",
        description="Thông báo"
    )
    created_at: datetime


# ============================================================================
# Section 2.5.2: TẠO KHÓA HỌC THỦ CÔNG
# ============================================================================

class PersonalCourseCreateRequest(BaseModel):
    """Request tạo khóa học thủ công"""
    title: str = Field(..., min_length=5, max_length=200, description="Tên khóa học")
    description: str = Field(..., min_length=20, max_length=2000, description="Mô tả ngắn")
    category: str = Field(..., description="Danh mục (Programming, Math, Business, Languages...)")
    level: str = Field(..., description="Cấp độ (Beginner, Intermediate, Advanced)")
    thumbnail_url: Optional[str] = Field(None, description="URL hình ảnh thumbnail")
    language: str = Field(default="vi", description="Ngôn ngữ khóa học")


class PersonalCourseCreateResponse(BaseModel):
    """Response sau khi tạo khóa học thủ công"""
    course_id: str = Field(..., description="UUID khóa học")
    title: str
    description: str
    category: str
    level: str
    status: str = Field(default="draft", description="Trạng thái: draft")
    message: str = Field(
        default="Khóa học đã được tạo. Bạn có thể thêm modules và lessons.",
        description="Thông báo"
    )
    created_at: datetime


# ============================================================================
# Section 2.5.3: XEM DANH SÁCH KHÓA HỌC CÁ NHÂN
# ============================================================================

class PersonalCourseListItem(BaseModel):
    """Item trong danh sách khóa học cá nhân"""
    id: str = Field(..., description="UUID khóa học")
    title: str
    description: str
    thumbnail_url: Optional[str] = None
    
    category: str
    level: str
    status: str = Field(..., description="draft|published|archived")
    
    # Thống kê
    modules_count: int = Field(..., description="Số modules đã tạo")
    lessons_count: int = Field(..., description="Số lessons đã tạo")
    total_duration_minutes: int = Field(..., description="Tổng thời lượng")
    
    created_at: datetime
    updated_at: datetime


class PersonalCourseListResponse(BaseModel):
    """Response danh sách khóa học cá nhân"""
    courses: List[PersonalCourseListItem] = Field(
        default_factory=list,
        description="Danh sách khóa học do học viên tạo"
    )
    total: int = Field(..., description="Tổng số khóa học")
    
    # Statistics
    draft_count: int = Field(..., description="Số khóa học draft")
    published_count: int = Field(..., description="Số khóa học published")
    archived_count: int = Field(..., description="Số khóa học archived")


# ============================================================================
# Section 2.5.4: CHỈNH SỬA KHÓA HỌC CÁ NHÂN
# ============================================================================

class LessonUpdateData(BaseModel):
    """Dữ liệu cập nhật lesson"""
    id: Optional[str] = Field(None, description="UUID (nếu update existing)")
    title: str
    order: int
    content: str = Field(..., description="Nội dung lesson (HTML/Markdown)")
    content_type: str = Field(default="text", description="text|video|mixed")
    video_url: Optional[str] = None
    duration_minutes: int = Field(default=0, description="Thời lượng lesson")
    resources: List[dict] = Field(default_factory=list, description="Tài nguyên đính kèm")


class ModuleUpdateData(BaseModel):
    """Dữ liệu cập nhật module"""
    id: Optional[str] = Field(None, description="UUID (nếu update existing)")
    title: str
    description: str
    order: int
    difficulty: str = Field(default="Basic", description="Basic|Intermediate|Advanced")
    estimated_hours: float = Field(default=0, description="Thời gian học ước tính")
    learning_outcomes: List[str] = Field(default_factory=list)
    lessons: List[LessonUpdateData] = Field(default_factory=list)


class PersonalCourseUpdateRequest(BaseModel):
    """Request cập nhật khóa học cá nhân"""
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=20, max_length=2000)
    category: Optional[str] = None
    level: Optional[str] = None
    thumbnail_url: Optional[str] = None
    status: Optional[str] = Field(None, description="draft|published|archived")
    
    # Cập nhật modules (thêm/xóa/sửa/sắp xếp)
    modules: Optional[List[ModuleUpdateData]] = Field(
        None,
        description="Danh sách modules mới (ghi đè hoàn toàn nếu có)"
    )
    
    learning_outcomes: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None


class PersonalCourseUpdateResponse(BaseModel):
    """Response sau khi cập nhật khóa học"""
    course_id: str
    title: str
    status: str
    modules_count: int
    lessons_count: int
    message: str = Field(default="Khóa học đã được cập nhật thành công")
    updated_at: datetime


# ============================================================================
# Section 2.5.5: XÓA KHÓA HỌC CÁ NHÂN
# ============================================================================

class PersonalCourseDeleteResponse(BaseModel):
    """Response sau khi xóa khóa học"""
    message: str = Field(default="Khóa học đã được xóa vĩnh viễn")
    course_id: str = Field(..., description="UUID khóa học đã xóa")
    course_title: str = Field(..., description="Tên khóa học đã xóa")
    deleted_at: datetime
