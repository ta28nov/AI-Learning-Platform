"""
Dashboard Controller
Xử lý requests cho dashboard endpoints
Section 2.7.1
"""

from typing import Dict, Optional
from fastapi import HTTPException, status

from schemas.dashboard import (
    StudentDashboardResponse,
    LearningStatsResponse,
    ProgressChartResponse,
    InstructorDashboardResponse,
    InstructorClassStatsResponse,
    InstructorProgressChartResponse,
    InstructorQuizPerformanceResponse,
    AdminSystemDashboardResponse,
    AdminUsersGrowthResponse,
    AdminCourseAnalyticsResponse,
    AdminSystemHealthResponse
)
from services import dashboard_service


# ============================================================================
# Section 2.7.1: DASHBOARD TỔNG QUAN HỌC VIÊN
# ============================================================================

async def handle_get_student_dashboard(current_user: Dict) -> StudentDashboardResponse:
    """
    2.7.1: Lấy dashboard tổng quan học viên
    
    Flow:
    1. Extract user_id từ current_user
    2. Gọi dashboard_service để lấy dữ liệu
    3. Return dashboard với in_progress_courses và pending_quizzes
    
    Args:
        current_user: Dict chứa thông tin user từ JWT
        
    Returns:
        StudentDashboardResponse với thông tin dashboard
        
    Raises:
        HTTPException 500: Lỗi khi lấy dashboard data
    """
    user_id = current_user.get("user_id")
    
    try:
        dashboard_data = await dashboard_service.get_student_dashboard(user_id)
        return StudentDashboardResponse(**dashboard_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy dashboard: {str(e)}"
        )


# ============================================================================
# Section 2.7.2: THỐNG KÊ HỌC TẬP CHI TIẾT
# ============================================================================

async def handle_get_learning_stats(current_user: Dict) -> LearningStatsResponse:
    """
    2.7.2: Lấy thống kê học tập chi tiết
    
    Flow:
    1. Extract user_id từ current_user
    2. Gọi dashboard_service để tính toán metrics
    3. Return stats với breakdown theo course
    
    Args:
        current_user: Dict chứa thông tin user từ JWT
        
    Returns:
        LearningStatsResponse với các metrics học tập
        
    Raises:
        HTTPException 500: Lỗi khi tính toán stats
    """
    user_id = current_user.get("user_id")
    
    try:
        stats_data = await dashboard_service.get_learning_stats(user_id)
        return LearningStatsResponse(**stats_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy thống kê: {str(e)}"
        )


# ============================================================================
# Section 2.7.3: BIỂU ĐỒ TIẾN ĐỘ THEO THỜI GIAN
# ============================================================================

async def handle_get_progress_chart(
    time_range: str,
    course_id: str,
    current_user: Dict
) -> ProgressChartResponse:
    """
    2.7.3: Lấy dữ liệu biểu đồ tiến độ
    
    Flow:
    1. Extract user_id từ current_user
    2. Validate time_range (day/week/month)
    3. Gọi dashboard_service với filters
    4. Return chart data và summary
    
    Args:
        time_range: "day", "week", hoặc "month"
        course_id: Optional filter theo course
        current_user: Dict chứa thông tin user từ JWT
        
    Returns:
        ProgressChartResponse với chart_data và summary
        
    Raises:
        HTTPException 400: time_range không hợp lệ
        HTTPException 500: Lỗi khi tạo chart
    """
    user_id = current_user.get("user_id")
    
    # Validate time_range
    valid_ranges = ["day", "week", "month"]
    if time_range not in valid_ranges:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"time_range phải là một trong: {', '.join(valid_ranges)}"
        )
    
    try:
        chart_data = await dashboard_service.get_progress_chart(
            user_id=user_id,
            time_range=time_range,
            course_id=course_id if course_id else None
        )
        return ProgressChartResponse(**chart_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo biểu đồ: {str(e)}"
        )


# ============================================================================
# INSTRUCTOR DASHBOARD (Section 3.4.1-3.4.4)
# ============================================================================

async def handle_get_instructor_dashboard(current_user: Dict) -> InstructorDashboardResponse:
    """
    3.4.1: Instructor Dashboard Overview
    
    Business logic:
    - Verify instructor role
    - Get active classes count, total students, quizzes count
    - Calculate avg completion rate
    - Get recent classes (3 most recent)
    - Return quick actions
    
    Args:
        current_user: User hiện tại (instructor)
        
    Returns:
        InstructorDashboardResponse
        
    Raises:
        403: Không phải instructor
        500: Lỗi server
        
    Endpoint: GET /api/v1/dashboard/instructor
    """
    instructor_id = current_user.get("user_id")
    role = current_user.get("role")
    
    # Check instructor role
    if role != "instructor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ instructor mới có quyền truy cập dashboard này"
        )
    
    try:
        dashboard_data = await dashboard_service.get_instructor_dashboard(instructor_id)
        return InstructorDashboardResponse(**dashboard_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy instructor dashboard: {str(e)}"
        )


async def handle_get_instructor_class_stats(
    class_id: str,
    current_user: Dict
) -> InstructorClassStatsResponse:
    """
    3.4.2: Instructor Class Stats
    
    Business logic:
    - Verify instructor role
    - Get stats for all instructor's classes or specific class
    - Calculate per-class metrics: student_count, attendance_rate, avg_progress, quiz_completion
    - Calculate active_students (last 7 days)
    - Return aggregated totals
    
    Args:
        class_id: Optional filter by class
        current_user: User hiện tại (instructor)
        
    Returns:
        InstructorClassStatsResponse
        
    Raises:
        403: Không phải instructor
        500: Lỗi server
        
    Endpoint: GET /api/v1/analytics/instructor/classes?class_id=xxx
    """
    instructor_id = current_user.get("user_id")
    role = current_user.get("role")
    
    # Check instructor role
    if role != "instructor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ instructor mới có quyền truy cập analytics này"
        )
    
    try:
        stats_data = await dashboard_service.get_instructor_class_stats(
            instructor_id=instructor_id,
            class_id=class_id if class_id else None
        )
        return InstructorClassStatsResponse(**stats_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy class stats: {str(e)}"
        )


async def handle_get_instructor_progress_chart(
    time_range: str,
    class_id: str,
    current_user: Dict
) -> InstructorProgressChartResponse:
    """
    3.4.3: Instructor Progress Chart
    
    Business logic:
    - Verify instructor role
    - Get progress data for time_range: day (7 days), week (4 weeks), month (6 months)
    - Filter by class_id if provided
    - Track lessons_completed, quizzes_completed, active_students per period
    - Return chart_type, chart_data, summary
    
    Args:
        time_range: "day"|"week"|"month"
        class_id: Optional filter by class
        current_user: User hiện tại (instructor)
        
    Returns:
        InstructorProgressChartResponse
        
    Raises:
        400: Invalid time_range
        403: Không phải instructor
        500: Lỗi server
        
    Endpoint: GET /api/v1/analytics/instructor/progress-chart?time_range=week&class_id=xxx
    """
    instructor_id = current_user.get("user_id")
    role = current_user.get("role")
    
    # Check instructor role
    if role != "instructor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ instructor mới có quyền truy cập analytics này"
        )
    
    # Validate time_range
    valid_ranges = ["day", "week", "month"]
    if time_range not in valid_ranges:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"time_range phải là một trong: {', '.join(valid_ranges)}"
        )
    
    try:
        chart_data = await dashboard_service.get_instructor_progress_chart(
            instructor_id=instructor_id,
            time_range=time_range,
            class_id=class_id if class_id else None
        )
        return InstructorProgressChartResponse(**chart_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo progress chart: {str(e)}"
        )


async def handle_get_instructor_quiz_performance(
    current_user: Dict
) -> InstructorQuizPerformanceResponse:
    """
    3.4.4: Instructor Quiz Performance Analytics
    
    Business logic:
    - Verify instructor role
    - Get all quizzes created by instructor
    - For each quiz: calculate total_attempts, pass/fail counts, pass_rate, avg_score, avg_time
    - Find hardest questions (top 3 lowest correct rate)
    - Calculate overall statistics
    - Build score distribution
    
    Args:
        current_user: User hiện tại (instructor)
        
    Returns:
        InstructorQuizPerformanceResponse
        
    Raises:
        403: Không phải instructor
        500: Lỗi server
        
    Endpoint: GET /api/v1/analytics/instructor/quiz-performance
    """
    instructor_id = current_user.get("user_id")
    role = current_user.get("role")
    
    # Check instructor role
    if role != "instructor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ instructor mới có quyền truy cập analytics này"
        )
    
    try:
        performance_data = await dashboard_service.get_instructor_quiz_performance(instructor_id)
        return InstructorQuizPerformanceResponse(**performance_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy quiz performance: {str(e)}"
        )


# ============================================================================
# Section 4.4: ADMIN DASHBOARD & ANALYTICS
# ============================================================================

async def handle_get_admin_dashboard(current_user: Dict) -> AdminSystemDashboardResponse:
    """
    4.4.1: Dashboard tổng quan hệ thống cho admin
    
    Flow:
    1. Validate admin permission
    2. Gọi dashboard_service để lấy system metrics
    3. Return dashboard với breakdown theo role, course stats, class stats
    
    Args:
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminSystemDashboardResponse với các chỉ số quan trọng
        
    Raises:
        HTTPException 403: Không phải admin
        HTTPException 500: Lỗi khi lấy dashboard data
    """
    # Validate admin role
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ admin mới có quyền truy cập dashboard này"
        )
    
    try:
        dashboard_data = await dashboard_service.get_admin_system_dashboard()
        return AdminSystemDashboardResponse(**dashboard_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy admin dashboard: {str(e)}"
        )


async def handle_get_users_growth_analytics(
    time_range: str = "30d",
    role_filter: Optional[str] = None,
    current_user: Dict = None
) -> AdminUsersGrowthResponse:
    """
    4.4.2: Thống kê tăng trưởng người dùng theo thời gian
    
    Flow:
    1. Validate admin permission
    2. Gọi dashboard_service để lấy user growth data
    3. Return line chart data với breakdown theo role
    
    Args:
        time_range: Khoảng thời gian (7d|30d|90d)
        role_filter: Lọc theo vai trò cụ thể (optional)
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminUsersGrowthResponse với chart data và statistics
        
    Raises:
        HTTPException 403: Không phải admin
        HTTPException 400: Invalid time_range
        HTTPException 500: Lỗi server
    """
    # Validate admin role
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ admin mới có quyền truy cập analytics này"
        )
    
    # Validate time_range
    if time_range not in ["7d", "30d", "90d"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="time_range phải là: 7d, 30d, hoặc 90d"
        )
    
    try:
        growth_data = await dashboard_service.get_users_growth_analytics(time_range, role_filter)
        return AdminUsersGrowthResponse(**growth_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy user growth analytics: {str(e)}"
        )


async def handle_get_course_analytics(
    time_range: str = "30d",
    category_filter: Optional[str] = None,
    current_user: Dict = None
) -> AdminCourseAnalyticsResponse:
    """
    4.4.3: Phân tích khóa học chuyên sâu
    
    Flow:
    1. Validate admin permission
    2. Gọi dashboard_service để lấy course analytics
    3. Return top courses, completion rates, creation trends
    
    Args:
        time_range: Khoảng thời gian (7d|30d|90d)
        category_filter: Lọc theo danh mục (optional)
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminCourseAnalyticsResponse với course analytics data
        
    Raises:
        HTTPException 403: Không phải admin
        HTTPException 400: Invalid time_range
        HTTPException 500: Lỗi server
    """
    # Validate admin role
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ admin mới có quyền truy cập analytics này"
        )
    
    # Validate time_range
    if time_range not in ["7d", "30d", "90d"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="time_range phải là: 7d, 30d, hoặc 90d"
        )
    
    try:
        course_analytics = await dashboard_service.get_course_analytics(time_range, category_filter)
        return AdminCourseAnalyticsResponse(**course_analytics)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy course analytics: {str(e)}"
        )


async def handle_get_system_health(current_user: Dict) -> AdminSystemHealthResponse:
    """
    4.4.4: Giám sát sức khỏe hệ thống
    
    Flow:
    1. Validate admin permission
    2. Gọi dashboard_service để lấy system health metrics
    3. Return metrics với alerts nếu vượt ngưỡng
    
    Args:
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminSystemHealthResponse với metrics và alerts
        
    Raises:
        HTTPException 403: Không phải admin
        HTTPException 500: Lỗi server
    """
    # Validate admin role
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ admin mới có quyền truy cập system health"
        )
    
    try:
        health_data = await dashboard_service.get_system_health()
        return AdminSystemHealthResponse(**health_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy system health: {str(e)}"
        )
