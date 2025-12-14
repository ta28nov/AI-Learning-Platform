"""
Dashboard Schemas
Định nghĩa request/response schemas cho dashboard endpoints
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class OverviewStats(BaseModel):
    total_courses_enrolled: int
    active_courses: int = Field(..., description="đang học")
    completed_courses: int
    total_lessons_completed: int
    total_study_hours: int
    current_streak_days: int = Field(..., description="số ngày học liên tiếp")


class PerformanceSummary(BaseModel):
    average_quiz_score: float = Field(..., description="0-100, điểm trung bình tất cả quiz")
    quiz_pass_rate: float = Field(..., description="0-100, tỷ lệ pass %")
    lessons_this_week: int = Field(..., description="số lessons hoàn thành tuần này")


class Recommendation(BaseModel):
    course_id: str = Field(..., description="UUID")
    title: str
    reason: str = Field(..., description="lý do gợi ý ngắn gọn")


class NextLesson(BaseModel):
    lesson_id: str = Field(..., description="UUID")
    title: str


class RecentCourse(BaseModel):
    course_id: str = Field(..., description="UUID")
    title: str
    thumbnail_url: Optional[str] = None
    progress_percent: float = Field(..., description="0-100")
    last_accessed: datetime
    next_lesson: NextLesson


class PendingQuiz(BaseModel):
    quiz_id: str = Field(..., description="UUID")
    title: str
    course_title: str
    lesson_title: str
    due_date: Optional[datetime] = None
    status: str = Field(..., description="not_started|failed - cần làm lại")


class StudentDashboardResponse(BaseModel):
    user_id: str = Field(..., description="UUID")
    full_name: str
    overview: OverviewStats
    recent_courses: List[RecentCourse]
    pending_quizzes: List[PendingQuiz]
    performance_summary: PerformanceSummary
    recommendations: List[Recommendation]


class CourseStats(BaseModel):
    course_id: str = Field(..., description="UUID")
    course_title: str
    lessons_completed: int
    quiz_score: float
    status: str


class LearningStatsResponse(BaseModel):
    lessons_completed: int
    quizzes_passed: int
    quizzes_failed: int
    avg_quiz_score: float = Field(..., description="0-100")
    completed_courses: int
    in_progress_courses: int
    cancelled_courses: int
    by_course: List[CourseStats]


class ChartDataPoint(BaseModel):
    date: str = Field(..., description="YYYY-MM-DD")
    lessons_completed: int
    hours_spent: float


class ChartSummary(BaseModel):
    total_lessons: int
    total_hours: float
    avg_per_day: float


class ProgressChartResponse(BaseModel):
    chart_data: List[ChartDataPoint]
    summary: ChartSummary


# ============================================================================
# INSTRUCTOR DASHBOARD SCHEMAS (Section 3.4.1-3.4.4)
# ============================================================================

class QuickAction(BaseModel):
    action_type: str = Field(..., description="create_quiz|view_progress|check_attendance")
    label: str
    link: str
    icon: str


class InstructorDashboardResponse(BaseModel):
    """
    3.4.1: Instructor Dashboard Overview
    Widgets: active classes count, total students, quizzes created, avg completion rate
    """
    active_classes_count: int
    total_students: int = Field(..., description="Total students across all classes")
    quizzes_created_count: int
    avg_completion_rate: float = Field(..., description="0-100")
    recent_classes: List[dict] = Field(default_factory=list, description="3 recent active classes")
    quick_actions: List[QuickAction]


class ClassStatItem(BaseModel):
    class_id: str = Field(..., description="UUID")
    class_name: str
    student_count: int
    attendance_rate: float = Field(..., description="0-100")
    avg_progress: float = Field(..., description="0-100")
    quiz_completion_rate: float = Field(..., description="0-100")
    active_students: int = Field(..., description="Students active in last 7 days")
    last_activity: datetime


class InstructorClassStatsResponse(BaseModel):
    """
    3.4.2: Instructor Class Stats
    Per-class metrics with filters and visualization data
    """
    classes: List[ClassStatItem]
    total_classes: int
    total_students: int
    avg_attendance: float = Field(..., description="0-100")
    avg_completion: float = Field(..., description="0-100")


class InstructorChartDataPoint(BaseModel):
    date: str = Field(..., description="YYYY-MM-DD")
    class_id: Optional[str] = None
    class_name: Optional[str] = None
    lessons_completed: int
    quizzes_completed: int
    active_students: int


class InstructorProgressChartResponse(BaseModel):
    """
    3.4.3: Instructor Progress Chart
    Line/bar charts showing progress over time (day/week/month)
    Can filter by specific class or view all classes
    """
    chart_type: str = Field(..., description="line|bar")
    time_range: str = Field(..., description="day|week|month")
    chart_data: List[InstructorChartDataPoint]
    summary: dict = Field(..., description="Total lessons, quizzes, students")


class QuizPerformanceItem(BaseModel):
    quiz_id: str = Field(..., description="UUID")
    quiz_title: str
    course_title: str
    class_name: Optional[str] = None
    total_attempts: int
    pass_count: int
    fail_count: int
    pass_rate: float = Field(..., description="0-100")
    avg_score: float = Field(..., description="0-100")
    avg_time_minutes: float
    hardest_questions: List[dict] = Field(default_factory=list, description="Top 3 hardest questions")
    created_at: datetime


class InstructorQuizPerformanceResponse(BaseModel):
    """
    3.4.4: Instructor Quiz Performance Analytics
    Detailed analytics on quiz effectiveness across all instructor's quizzes
    """
    quizzes: List[QuizPerformanceItem]
    total_quizzes: int
    total_attempts: int
    overall_pass_rate: float = Field(..., description="0-100")
    avg_score: float = Field(..., description="0-100")
    score_distribution: List[dict] = Field(default_factory=list, description="Score ranges with counts")


# ============================================================================
# ADMIN DASHBOARD SCHEMAS (Section 4.4.1-4.4.4)
# ============================================================================

class AdminUsersByRole(BaseModel):
    """Phân tách người dùng theo vai trò"""
    students: int = Field(..., description="Số lượng học viên")
    instructors: int = Field(..., description="Số lượng giảng viên")
    admins: int = Field(..., description="Số lượng quản trị viên")


class AdminCourseStats(BaseModel):
    """Thống kê khóa học"""
    public_courses: int = Field(..., description="Số khóa học công khai")
    personal_courses: int = Field(..., description="Số khóa học cá nhân")
    published_courses: int = Field(..., description="Số khóa học đã xuất bản")
    draft_courses: int = Field(..., description="Số khóa học nháp")


class AdminClassStats(BaseModel):
    """Thống kê lớp học"""
    active_classes: int = Field(..., description="Số lớp đang hoạt động")
    completed_classes: int = Field(..., description="Số lớp đã kết thúc")
    preparing_classes: int = Field(..., description="Số lớp đang chuẩn bị")


class AdminActivityStats(BaseModel):
    """Thống kê hoạt động hệ thống"""
    new_enrollments_this_week: int = Field(..., description="Đăng ký mới trong tuần")
    quizzes_completed_today: int = Field(..., description="Quiz hoàn thành hôm nay")
    active_users_today: int = Field(..., description="Người dùng hoạt động hôm nay")
    total_lesson_completions: int = Field(..., description="Tổng bài học đã hoàn thành")


class AdminSystemDashboardResponse(BaseModel):
    """
    4.4.1: Admin System Dashboard Response
    Trang chủ admin với các chỉ số quan trọng nhất
    """
    total_users: int = Field(..., description="Tổng số người dùng")
    users_by_role: AdminUsersByRole = Field(..., description="Phân tách theo vai trò")
    total_courses: int = Field(..., description="Tổng số khóa học")
    course_stats: AdminCourseStats = Field(..., description="Thống kê khóa học")
    total_classes: int = Field(..., description="Tổng số lớp học")
    class_stats: AdminClassStats = Field(..., description="Thống kê lớp học")
    activity_stats: AdminActivityStats = Field(..., description="Thống kê hoạt động")
    last_updated: datetime = Field(..., description="Thời gian cập nhật cuối")


class AdminUserGrowthDataPoint(BaseModel):
    """Điểm dữ liệu tăng trưởng người dùng"""
    date: str = Field(..., description="Ngày (YYYY-MM-DD)")
    new_students: int = Field(..., description="Học viên mới")
    new_instructors: int = Field(..., description="Giảng viên mới")
    new_admins: int = Field(..., description="Admin mới")
    total_new_users: int = Field(..., description="Tổng người dùng mới")
    active_users: int = Field(..., description="Người dùng hoạt động")


class AdminUserGrowthStats(BaseModel):
    """Thống kê tăng trưởng người dùng"""
    total_growth_rate: float = Field(..., description="Tỷ lệ tăng trưởng tổng (%)")
    student_growth_rate: float = Field(..., description="Tỷ lệ tăng trưởng học viên (%)")
    instructor_growth_rate: float = Field(..., description="Tỷ lệ tăng trưởng giảng viên (%)")
    user_retention_rate: float = Field(..., description="Tỷ lệ người dùng quay lại (%)")
    avg_daily_new_users: float = Field(..., description="Trung bình người dùng mới/ngày")


class AdminUsersGrowthResponse(BaseModel):
    """
    4.4.2: Admin Users Growth Analytics Response
    Biểu đồ tăng trưởng người dùng theo thời gian
    """
    time_range: str = Field(..., description="Khoảng thời gian (7d|30d|90d)")
    chart_data: List[AdminUserGrowthDataPoint] = Field(..., description="Dữ liệu biểu đồ")
    statistics: AdminUserGrowthStats = Field(..., description="Thống kê tổng hợp")


class AdminTopCourse(BaseModel):
    """Khóa học hàng đầu"""
    course_id: str = Field(..., description="UUID khóa học")
    title: str = Field(..., description="Tên khóa học")
    enrollments: int = Field(..., description="Số lượt đăng ký")
    completion_rate: float = Field(..., description="Tỷ lệ hoàn thành (%)")
    avg_quiz_score: float = Field(..., description="Điểm quiz trung bình (0-100)")
    instructor_name: str = Field(..., description="Tên giảng viên")
    created_at: datetime = Field(..., description="Ngày tạo")


class AdminCourseCreationTrend(BaseModel):
    """Xu hướng tạo khóa học"""
    date: str = Field(..., description="Ngày (YYYY-MM-DD)")
    public_courses_created: int = Field(..., description="Khóa học công khai được tạo")
    personal_courses_created: int = Field(..., description="Khóa học cá nhân được tạo")
    total_created: int = Field(..., description="Tổng khóa học được tạo")


class AdminCourseAnalyticsResponse(BaseModel):
    """
    4.4.3: Admin Course Analytics Response
    Dashboard chuyên sâu về course analytics
    """
    top_courses: List[AdminTopCourse] = Field(..., description="Top 10 khóa học phổ biến")
    overall_completion_rate: float = Field(..., description="Tỷ lệ hoàn thành chung (%)")
    avg_quiz_scores: float = Field(..., description="Điểm quiz trung bình toàn hệ thống (0-100)")
    creation_trend: List[AdminCourseCreationTrend] = Field(..., description="Xu hướng tạo khóa học theo thời gian")
    total_enrollments: int = Field(..., description="Tổng số lượt đăng ký")
    active_courses_percentage: float = Field(..., description="% khóa học đang hoạt động")


class AdminSystemHealthMetrics(BaseModel):
    """Metrics sức khỏe hệ thống"""
    api_response_time_ms: float = Field(..., description="Thời gian phản hồi API (ms)")
    error_rate_percentage: float = Field(..., description="Tỷ lệ lỗi (%)")
    database_query_time_ms: float = Field(..., description="Thời gian query database (ms)")
    database_connections: int = Field(..., description="Số kết nối database")
    storage_used_gb: float = Field(..., description="Dung lượng đã sử dụng (GB)")
    storage_total_gb: float = Field(..., description="Tổng dung lượng (GB)")
    storage_usage_percentage: float = Field(..., description="% dung lượng đã dùng")
    active_sessions: int = Field(..., description="Số phiên đăng nhập đang hoạt động")
    memory_usage_percentage: float = Field(..., description="% bộ nhớ đã sử dụng")
    cpu_usage_percentage: float = Field(..., description="% CPU đã sử dụng")


class AdminSystemHealthAlert(BaseModel):
    """Cảnh báo hệ thống"""
    alert_type: str = Field(..., description="warning|critical|info")
    message: str = Field(..., description="Nội dung cảnh báo")
    metric_name: str = Field(..., description="Tên metric")
    current_value: float = Field(..., description="Giá trị hiện tại")
    threshold_value: float = Field(..., description="Ngưỡng cảnh báo")
    timestamp: datetime = Field(..., description="Thời gian phát hiện")


class AdminSystemHealthResponse(BaseModel):
    """
    4.4.4: Admin System Health Response
    Metrics về hiệu suất và độ tin cậy hệ thống
    """
    status: str = Field(..., description="healthy|warning|critical")
    metrics: AdminSystemHealthMetrics = Field(..., description="Các chỉ số hệ thống")
    alerts: List[AdminSystemHealthAlert] = Field(..., description="Danh sách cảnh báo")
    uptime_hours: float = Field(..., description="Thời gian hoạt động (giờ)")
    last_checked: datetime = Field(..., description="Lần kiểm tra cuối")
