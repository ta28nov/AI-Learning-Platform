"""
Dashboard Router
Định nghĩa routes cho dashboard endpoints
Section 2.7.1, 3.4.1, 4.4.1
3 endpoints
"""

from fastapi import APIRouter, Depends, status
from middleware.auth import get_current_user
from controllers.dashboard_controller import (
    handle_get_student_dashboard,
    handle_get_instructor_dashboard,
    handle_get_admin_dashboard
)
from schemas.dashboard import (
    StudentDashboardResponse,
    InstructorDashboardResponse,
    AdminSystemDashboardResponse
)


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/student",
    response_model=StudentDashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Dashboard tổng quan học viên",
    description="Hiển thị khóa học đang học (3-5 gần nhất), quiz pending, lessons completed, điểm TB"
)
async def get_student_dashboard(
    current_user: dict = Depends(get_current_user)
):
    """Section 2.7.1 - Dashboard học viên"""
    return await handle_get_student_dashboard(current_user)


@router.get(
    "/instructor",
    response_model=InstructorDashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Dashboard tổng quan giảng viên",
    description="Hiển thị active classes, total students, quizzes created, avg completion rate, recent classes, quick actions"
)
async def get_instructor_dashboard(
    current_user: dict = Depends(get_current_user)
):
    """Section 3.4.1 - Dashboard giảng viên"""
    return await handle_get_instructor_dashboard(current_user)


@router.get(
    "/admin",
    response_model=AdminSystemDashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Dashboard tổng quan hệ thống",
    description="Dashboard admin với metrics quan trọng: users, courses, enrollments"
)
async def get_admin_dashboard(
    current_user: dict = Depends(get_current_user)
):
    """Section 4.4.1 - Dashboard tổng quan hệ thống (Admin)"""
    return await handle_get_admin_dashboard(current_user)
