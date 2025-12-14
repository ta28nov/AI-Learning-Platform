"""
Course Schemas
Định nghĩa request/response schemas cho course endpoints
Bao gồm: search, list public, detail, enrollment status
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class CourseSearchFilters(BaseModel):
    """Filters cho tìm kiếm khóa học"""
    category: Optional[str] = Field(None, description="Danh mục: Programming|Math|Business|Languages")
    level: Optional[str] = Field(None, description="Cấp độ: Beginner|Intermediate|Advanced")
    duration_range: Optional[str] = Field(None, description="Khoảng thời lượng")


class SearchMetadata(BaseModel):
    """Metadata về quá trình tìm kiếm"""
    keyword_used: Optional[str] = Field(None, description="Từ khóa đã tìm")
    filters_applied: CourseSearchFilters = Field(..., description="Các bộ lọc đã áp dụng")
    search_time_ms: float = Field(..., description="Thời gian tìm kiếm (milliseconds)")


class CourseSearchItem(BaseModel):
    """Schema cho từng khóa học trong kết quả tìm kiếm"""
    id: str = Field(..., description="UUID khóa học")
    title: str = Field(..., description="Tên khóa học")
    description: str = Field(..., description="Mô tả ngắn gọn 2-3 câu")
    category: str = Field(..., description="Danh mục khóa học")
    level: str = Field(..., description="Cấp độ: Beginner|Intermediate|Advanced")
    thumbnail_url: Optional[str] = Field(None, description="URL ảnh đại diện")
    total_modules: int = Field(..., description="Số lượng modules")
    total_lessons: int = Field(..., description="Số lượng bài học")
    total_duration_minutes: int = Field(..., description="Tổng thời lượng học (phút)")
    enrollment_count: int = Field(..., description="Số học viên đã đăng ký")
    avg_rating: Optional[float] = Field(None, description="Điểm đánh giá trung bình 0-5")
    instructor_name: str = Field(..., description="Tên giảng viên")
    instructor_avatar: Optional[str] = Field(None, description="Avatar giảng viên")
    is_enrolled: bool = Field(..., description="User hiện tại đã đăng ký chưa")
    created_at: datetime = Field(..., description="Ngày tạo khóa học")


class CourseSearchResponse(BaseModel):
    """Response schema cho GET /api/v1/courses/search"""
    courses: List[CourseSearchItem] = Field(..., description="Danh sách khóa học tìm được")
    total: int = Field(..., description="Tổng số khóa học")
    skip: int = Field(..., description="Offset hiện tại")
    limit: int = Field(..., description="Giới hạn mỗi trang")
    search_metadata: SearchMetadata = Field(..., description="Metadata về tìm kiếm")


# Alias cho GET /api/v1/courses/public
CourseListResponse = CourseSearchResponse


class OwnerInfo(BaseModel):
    """Thông tin giảng viên của khóa học"""
    id: str = Field(..., description="UUID giảng viên")
    name: str = Field(..., description="Tên giảng viên")
    avatar_url: Optional[str] = Field(None, description="URL avatar")
    role: Optional[str] = Field(None, description="Role: admin|instructor|student")
    bio: Optional[str] = Field(None, description="Tiểu sử giảng viên")
    experience_years: Optional[int] = Field(None, description="Số năm kinh nghiệm")


class LearningOutcome(BaseModel):
    """Mục tiêu học tập của khóa học"""
    description: str = Field(..., description="Mục tiêu cụ thể, đo lường được")
    skill_tag: Optional[str] = Field(None, description="Kỹ năng liên quan")


class LessonSummary(BaseModel):
    """Tóm tắt thông tin lesson trong module"""
    id: str = Field(..., description="UUID lesson")
    title: str = Field(..., description="Tên lesson")
    order: int = Field(..., description="Thứ tự lesson trong module")
    duration_minutes: int = Field(..., description="Thời lượng lesson (phút)")
    content_type: str = Field(..., description="Loại nội dung: text|video|quiz|mixed")
    is_completed: bool = Field(..., description="Đã hoàn thành chưa (nếu user đã đăng ký)")


class ModuleSummary(BaseModel):
    """Tóm tắt thông tin module trong khóa học"""
    id: str = Field(..., description="UUID module")
    title: str = Field(..., description="Tên module")
    description: str = Field(..., description="Mô tả module")
    difficulty: str = Field(..., description="Độ khó: Basic|Intermediate|Advanced")
    estimated_hours: float = Field(..., description="Thời gian học ước tính (giờ)")
    lessons: List[LessonSummary] = Field(..., description="Danh sách lessons trong module")


class CourseStatistics(BaseModel):
    """Thống kê về khóa học"""
    total_modules: int = Field(..., description="Tổng số modules")
    total_lessons: int = Field(..., description="Tổng số lessons")
    total_duration_minutes: int = Field(..., description="Tổng thời lượng (phút)")
    enrollment_count: int = Field(..., description="Số học viên đã đăng ký")
    completion_rate: float = Field(..., description="Tỷ lệ hoàn thành trung bình 0-100")
    avg_rating: Optional[float] = Field(None, description="Điểm đánh giá trung bình 0-5")


class EnrollmentInfo(BaseModel):
    """Thông tin enrollment của user hiện tại"""
    is_enrolled: bool = Field(..., description="Đã đăng ký chưa")
    enrollment_id: Optional[str] = Field(None, description="UUID enrollment nếu đã đăng ký")
    enrolled_at: Optional[datetime] = Field(None, description="Thời gian đăng ký")
    progress_percent: Optional[float] = Field(None, description="Tiến độ học tập 0-100")
    can_access_content: bool = Field(..., description="Có thể truy cập nội dung không")


class CourseDetailResponse(BaseModel):
    """Response schema cho GET /api/v1/courses/{course_id}"""
    id: str = Field(..., description="UUID khóa học")
    title: str = Field(..., description="Tên khóa học")
    description: str = Field(..., description="Mô tả chi tiết đầy đủ")
    category: str = Field(..., description="Danh mục")
    level: str = Field(..., description="Cấp độ: Beginner|Intermediate|Advanced")
    thumbnail_url: Optional[str] = Field(None, description="URL ảnh đại diện")
    preview_video_url: Optional[str] = Field(None, description="URL video preview")
    language: str = Field(..., description="Ngôn ngữ: vi|en")
    status: str = Field(..., description="Trạng thái: published|draft|archived")
    owner_info: OwnerInfo = Field(..., description="Thông tin giảng viên")
    learning_outcomes: List[LearningOutcome] = Field(..., description="Mục tiêu học tập")
    prerequisites: List[str] = Field(..., description="Yêu cầu kiến thức đầu vào")
    modules: List[ModuleSummary] = Field(..., description="Danh sách modules")
    course_statistics: CourseStatistics = Field(..., description="Thống kê khóa học")
    enrollment_info: EnrollmentInfo = Field(..., description="Thông tin enrollment")
    created_at: datetime = Field(..., description="Ngày tạo")
    updated_at: datetime = Field(..., description="Ngày cập nhật cuối")


class CourseEnrollmentStatusResponse(BaseModel):
    """Response schema cho GET /api/v1/courses/{course_id}/enrollment-status"""
    is_enrolled: bool = Field(..., description="Đã đăng ký chưa")
    status: Optional[str] = Field(None, description="Trạng thái enrollment: active|completed|cancelled")
    enrollment_id: Optional[str] = Field(None, description="UUID enrollment")
    can_access_content: bool = Field(..., description="Có thể truy cập nội dung không")
    enrolled_at: Optional[datetime] = Field(None, description="Ngày đăng ký")
    progress_percent: Optional[float] = Field(None, description="Tiến độ 0-100")

