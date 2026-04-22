"""
Analytics Router
Định nghĩa routes cho analytics endpoints
Section 2.7.2-2.7.3 (Student), 3.4.2-3.4.4 (Instructor)
5 endpoints (Admin analytics đã chuyển sang admin_router)
"""

from fastapi import APIRouter, Depends, status, Query
from typing import Optional
from middleware.auth import get_current_user
from controllers.dashboard_controller import (
    handle_get_learning_stats,
    handle_get_progress_chart,
    handle_get_instructor_class_stats,
    handle_get_instructor_progress_chart,
    handle_get_instructor_quiz_performance
)
from schemas.dashboard import (
    LearningStatsResponse,
    ProgressChartResponse,
    InstructorClassStatsResponse,
    InstructorProgressChartResponse,
    InstructorQuizPerformanceResponse,
    AdminUsersGrowthResponse,
    AdminCourseAnalyticsResponse,
    AdminSystemHealthResponse
)


router = APIRouter(prefix="/analytics", tags=["Analytics"])


# ============================================================================
# STUDENT ANALYTICS (Section 2.7.2-2.7.3)
# ============================================================================

@router.get(
    "/learning-stats",
    response_model=LearningStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Thống kê học tập chi tiết",
    description="Metrics đầy đủ: lessons completed, quizzes passed/failed, avg score, courses breakdown"
)
async def get_learning_stats(
    current_user: dict = Depends(get_current_user)
):
    """Section 2.7.2 - Thống kê học tập"""
    return await handle_get_learning_stats(current_user)


@router.get(
    "/progress-chart",
    response_model=ProgressChartResponse,
    status_code=status.HTTP_200_OK,
    summary="Biểu đồ tiến độ theo thời gian",
    description="Line/bar chart thể hiện tiến độ qua ngày/tuần/tháng với lessons completed và hours spent"
)
async def get_progress_chart(
    time_range: str = Query("week", description="Khoảng thời gian: day (7 ngày), week (4 tuần), month (6 tháng)"),
    course_id: Optional[str] = Query(None, description="UUID khóa học (optional filter)"),
    current_user: dict = Depends(get_current_user)
):
    """Section 2.7.3 - Biểu đồ tiến độ"""
    return await handle_get_progress_chart(time_range, course_id, current_user)


# ============================================================================
# INSTRUCTOR ANALYTICS (Section 3.4.2-3.4.4)
# ============================================================================

@router.get(
    "/instructor/classes",
    response_model=InstructorClassStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Thống kê các lớp học của giảng viên",
    description="Per-class metrics: student_count, attendance_rate, avg_progress, quiz_completion, active_students"
)
async def get_instructor_class_stats(
    class_id: Optional[str] = Query(None, description="UUID lớp học (optional filter)"),
    current_user: dict = Depends(get_current_user)
):
    """Section 3.4.2 - Instructor class stats"""
    return await handle_get_instructor_class_stats(class_id, current_user)


@router.get(
    "/instructor/progress-chart",
    response_model=InstructorProgressChartResponse,
    status_code=status.HTTP_200_OK,
    summary="Biểu đồ tiến độ lớp học theo thời gian",
    description="Line/bar charts showing lessons_completed, quizzes_completed, active_students over time"
)
async def get_instructor_progress_chart(
    time_range: str = Query("week", description="Khoảng thời gian: day (7 ngày), week (4 tuần), month (6 tháng)"),
    class_id: Optional[str] = Query(None, description="UUID lớp học (optional filter)"),
    current_user: dict = Depends(get_current_user)
):
    """Section 3.4.3 - Instructor progress chart"""
    return await handle_get_instructor_progress_chart(time_range, class_id, current_user)


@router.get(
    "/instructor/quiz-performance",
    response_model=InstructorQuizPerformanceResponse,
    status_code=status.HTTP_200_OK,
    summary="Analytics hiệu quả quiz của giảng viên",
    description="Quiz performance: attempts, pass/fail rates, avg scores, hardest questions, score distribution"
)
async def get_instructor_quiz_performance(
    current_user: dict = Depends(get_current_user)
):
    """Section 3.4.4 - Instructor quiz performance"""
    return await handle_get_instructor_quiz_performance(current_user)
