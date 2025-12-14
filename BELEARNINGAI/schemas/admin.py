"""
Admin Schemas
Định nghĩa request/response schemas cho admin endpoints
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class AdminUserListItem(BaseModel):
    user_id: str = Field(..., description="UUID")
    full_name: str
    email: str
    avatar: Optional[str] = None
    role: str = Field(..., description="student|instructor|admin")
    status: str = Field(..., description="active|inactive|banned")
    created_at: datetime
    last_login_at: Optional[datetime] = None
    courses_enrolled: Optional[int] = Field(None, description="For student only")
    classes_created: Optional[int] = Field(None, description="For instructor only")


class UserSummary(BaseModel):
    total_users: int
    active_users: int
    new_users_this_month: int


class AdminUserListResponse(BaseModel):
    data: List[AdminUserListItem]
    total: int
    skip: int
    limit: int
    summary: UserSummary


class UserStatistics(BaseModel):
    enrolled_courses: Optional[int] = None
    completed_courses: Optional[int] = None
    average_score: Optional[float] = Field(None, description="0-100 for student")
    classes_teaching: Optional[int] = None
    students_taught: Optional[int] = None
    quizzes_created: Optional[int] = None


class CurrentEnrollment(BaseModel):
    course_id: str = Field(..., description="UUID")
    course_title: str
    progress: float = Field(..., description="0-100")
    enrolled_at: datetime
    status: str = Field(..., description="in-progress|completed|cancelled")


class TeachingClass(BaseModel):
    class_id: str = Field(..., description="UUID")
    class_name: str
    course_title: str
    student_count: int
    created_at: datetime


class ProfileInfo(BaseModel):
    phone: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class ActivitySummary(BaseModel):
    courses_enrolled: int
    classes_created: int
    total_study_hours: int
    login_streak_days: int


class AdminUserDetailResponse(BaseModel):
    user_id: str = Field(..., description="UUID")
    full_name: str
    email: str
    role: str = Field(..., description="student|instructor|admin")
    status: str = Field(..., description="active|inactive|banned")
    created_at: datetime
    last_login_at: Optional[datetime] = None
    profile: ProfileInfo
    activity_summary: ActivitySummary


class AdminCreateUserRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., description="Unique email")
    role: str = Field(..., description="student|instructor|admin")
    password: str = Field(..., min_length=8, description="Password required for all roles")
    bio: Optional[str] = Field(None, max_length=500)
    avatar: Optional[str] = None


class AdminCreateUserResponse(BaseModel):
    user_id: str = Field(..., description="UUID")
    full_name: str
    email: str
    role: str
    status: str = Field(..., description="active for instructor/admin, pending for student")
    created_at: datetime
    message: str


class AdminUpdateUserRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None
    status: Optional[str] = Field(None, description="active|inactive")


class AdminUpdateUserResponse(BaseModel):
    user_id: str = Field(..., description="UUID")
    full_name: str
    email: str
    updated_at: datetime
    message: str


class AdminDeleteUserResponse(BaseModel):
    user_id: str = Field(..., description="UUID")
    message: str


class RoleChangeImpact(BaseModel):
    description: str
    affected_classes: Optional[int] = None
    affected_enrollments: Optional[int] = None


class AdminChangeRoleRequest(BaseModel):
    new_role: str = Field(..., description="student|instructor|admin")


class AdminChangeRoleResponse(BaseModel):
    user_id: str = Field(..., description="UUID")
    old_role: str
    new_role: str
    impact: RoleChangeImpact
    updated_at: datetime
    message: str


class AdminResetPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=8)


class AdminResetPasswordResponse(BaseModel):
    user_id: str = Field(..., description="UUID")
    message: str
    note: str


class UsersByRole(BaseModel):
    student: int
    instructor: int
    admin: int


class CoursesStats(BaseModel):
    published: int
    draft: int


class AdminDashboardResponse(BaseModel):
    total_users: int
    users_by_role: UsersByRole
    total_courses: int
    courses_stats: CoursesStats
    total_classes: int
    active_classes: int
    total_enrollments: int


# ============================================================================
# ADMIN COURSE MANAGEMENT SCHEMAS (Section 4.2)
# ============================================================================

class CourseAuthor(BaseModel):
    user_id: str = Field(..., description="UUID")
    full_name: str
    email: str
    role: str = Field(..., description="admin|instructor|student")


class AdminCourseListItem(BaseModel):
    course_id: str = Field(..., description="UUID")
    title: str
    thumbnail_url: Optional[str] = None
    author: CourseAuthor
    course_type: str = Field(..., description="public|personal")
    enrollment_count: int
    status: str = Field(..., description="draft|published|archived")
    category: str
    level: str = Field(..., description="Beginner|Intermediate|Advanced")
    created_at: datetime
    updated_at: datetime


class AdminCourseListResponse(BaseModel):
    data: List[AdminCourseListItem]
    total: int
    skip: int
    limit: int
    has_next: bool


class ModuleSummary(BaseModel):
    module_id: str = Field(..., description="UUID")
    title: str
    order: int
    lesson_count: int
    estimated_hours: float


class CourseAnalytics(BaseModel):
    enrollment_count: int
    completion_rate: float = Field(..., description="0-100")
    avg_rating: Optional[float] = Field(None, description="0-5")
    total_students_active: int


class AdminCourseDetailResponse(BaseModel):
    course_id: str = Field(..., description="UUID")
    title: str
    description: str
    thumbnail_url: Optional[str] = None
    preview_video_url: Optional[str] = None
    category: str
    level: str
    language: str
    status: str = Field(..., description="draft|published|archived")
    course_type: str = Field(..., description="public|personal")
    author: CourseAuthor
    modules: List[ModuleSummary]
    total_duration_minutes: int
    prerequisites: List[str]
    learning_outcomes: List[dict]
    analytics: CourseAnalytics
    created_at: datetime
    updated_at: datetime


class AdminCourseCreateRequest(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=20, max_length=2000)
    category: str
    level: str = Field(..., description="Beginner|Intermediate|Advanced")
    language: str = Field(default="vi")
    thumbnail_url: Optional[str] = None
    preview_video_url: Optional[str] = None
    prerequisites: List[str] = Field(default_factory=list)
    learning_outcomes: List[dict] = Field(default_factory=list)
    status: str = Field(default="draft", description="draft|published")


class AdminCourseCreateResponse(BaseModel):
    course_id: str = Field(..., description="UUID")
    title: str
    status: str
    course_type: str = Field(default="public")
    created_by: str = Field(..., description="Admin user_id")
    created_at: datetime
    message: str


class AdminCourseUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=20, max_length=2000)
    category: Optional[str] = None
    level: Optional[str] = None
    language: Optional[str] = None
    thumbnail_url: Optional[str] = None
    preview_video_url: Optional[str] = None
    prerequisites: Optional[List[str]] = None
    learning_outcomes: Optional[List[dict]] = None
    status: Optional[str] = Field(None, description="draft|published|archived")


class AdminCourseUpdateResponse(BaseModel):
    course_id: str = Field(..., description="UUID")
    title: str
    status: str
    updated_at: datetime
    message: str


class CourseDeleteImpact(BaseModel):
    enrolled_students: int
    active_classes: int
    personal_courses_derived: int
    warning: str


class AdminDeleteCourseResponse(BaseModel):
    course_id: str = Field(..., description="UUID")
    title: str
    impact: CourseDeleteImpact
    message: str


# ============================================================================
# ADMIN CLASSES SCHEMAS (Section 4.3.1-4.3.2)
# ============================================================================

class AdminClassListItem(BaseModel):
    """Schema cho danh sách lớp học trong admin panel - API_SCHEMA Section 9.13"""
    class_id: str = Field(..., description="UUID lớp học")
    class_name: str = Field(..., description="Tên lớp học")
    course_title: str = Field(..., description="Khóa học gốc")
    instructor_name: str = Field(..., description="Tên giảng viên")
    student_count: int = Field(..., description="Số học viên hiện tại")
    status: str = Field(..., description="active|completed")
    created_at: datetime = Field(..., description="Ngày tạo lớp")


class AdminClassListResponse(BaseModel):
    """Response cho GET /api/v1/admin/classes"""
    data: List[AdminClassListItem]
    total: int = Field(..., description="Tổng số lớp học")
    skip: int = Field(..., description="Pagination offset")
    limit: int = Field(..., description="Pagination limit")


class AdminCourseInfo(BaseModel):
    """Thông tin khóa học trong admin class detail"""
    course_id: str = Field(..., description="UUID khóa học")
    title: str = Field(..., description="Tên khóa học")
    category: str = Field(..., description="Danh mục khóa học")


class AdminInstructorInfo(BaseModel):
    """Thông tin giảng viên trong admin class detail"""
    user_id: str = Field(..., description="UUID giảng viên")
    full_name: str = Field(..., description="Tên giảng viên")
    email: str = Field(..., description="Email giảng viên")


class AdminClassStats(BaseModel):
    """Thống kê lớp học trong admin class detail"""
    average_progress: float = Field(..., description="Tiến độ trung bình (0-100)")
    completion_rate: float = Field(..., description="Tỷ lệ hoàn thành (0-100)")
    active_students_today: int = Field(..., description="Số học viên hoạt động hôm nay")


class AdminClassDetailResponse(BaseModel):
    """Response cho GET /api/v1/admin/classes/{class_id}"""
    class_id: str = Field(..., description="UUID lớp học")
    class_name: str = Field(..., description="Tên lớp học")
    course: AdminCourseInfo = Field(..., description="Thông tin khóa học")
    instructor: AdminInstructorInfo = Field(..., description="Thông tin giảng viên")
    student_count: int = Field(..., description="Số học viên hiện tại")
    invite_code: str = Field(..., description="Mã mời tham gia")
    status: str = Field(..., description="preparing|active|completed")
    class_stats: AdminClassStats = Field(..., description="Thống kê lớp học")
    created_at: datetime = Field(..., description="Ngày tạo lớp")
    start_date: datetime = Field(..., description="Thời gian bắt đầu")
    end_date: datetime = Field(..., description="Thời gian kết thúc")
