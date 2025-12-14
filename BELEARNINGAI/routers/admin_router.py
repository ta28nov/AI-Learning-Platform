"""
Admin Router
Định nghĩa routes cho admin management endpoints
Section 4.1: User Management (7 endpoints)
Section 4.2: Course Management (5 endpoints)
Section 4.3: Class Management (2 endpoints)
Section 4.4: Admin Analytics (3 endpoints)
Tổng: 17 endpoints
"""

from fastapi import APIRouter, Depends, status, Query
from typing import Optional
from middleware.auth import get_current_user
from controllers.admin_controller import (
    handle_list_users_admin,
    handle_get_user_detail_admin,
    handle_create_user_admin,
    handle_update_user_admin,
    handle_delete_user_admin,
    handle_change_user_role_admin,
    handle_reset_user_password_admin,
    handle_list_courses_admin,
    handle_get_course_detail_admin,
    handle_create_course_admin,
    handle_update_course_admin,
    handle_delete_course_admin,
    handle_list_classes_admin,
    handle_get_class_detail_admin
)
from schemas.admin import (
    AdminUserListResponse,
    AdminUserDetailResponse,
    AdminCreateUserRequest,
    AdminCreateUserResponse,
    AdminUpdateUserRequest,
    AdminUpdateUserResponse,
    AdminDeleteUserResponse,
    AdminChangeRoleRequest,
    AdminChangeRoleResponse,
    AdminResetPasswordRequest,
    AdminResetPasswordResponse,
    AdminCourseListResponse,
    AdminCourseDetailResponse,
    AdminCourseCreateRequest,
    AdminCourseCreateResponse,
    AdminCourseUpdateRequest,
    AdminCourseUpdateResponse,
    AdminDeleteCourseResponse,
    AdminClassListResponse,
    AdminClassDetailResponse
)


router = APIRouter(prefix="/admin", tags=["Admin"])


# ============================================================================
# ADMIN USER MANAGEMENT (Section 4.1)
# ============================================================================

@router.get(
    "/users",
    response_model=AdminUserListResponse,
    status_code=status.HTTP_200_OK,
    summary="Xem danh sách người dùng",
    description="Hiển thị tất cả users với filter (role, status), search (tên/email), sort"
)
async def list_users_admin(
    role: Optional[str] = Query(None, description="Filter role: student|instructor|admin"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter status: active|inactive"),
    keyword: Optional[str] = Query(None, description="Search tên hoặc email"),
    sort_by: str = Query("created_at", description="Field sort"),
    sort_order: str = Query("desc", description="asc|desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Section 4.1.1 - Xem danh sách người dùng (Admin)"""
    return await handle_list_users_admin(
        current_user=current_user,
        role=role,
        status_filter=status_filter,
        keyword=keyword,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit
    )


@router.get(
    "/users/{user_id}",
    response_model=AdminUserDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Xem hồ sơ người dùng chi tiết",
    description="Xem thông tin đầy đủ user: personal info, statistics, enrollments/classes"
)
async def get_user_detail_admin(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Section 4.1.2 - Xem hồ sơ người dùng chi tiết (Admin)"""
    return await handle_get_user_detail_admin(user_id, current_user)


@router.post(
    "/users",
    response_model=AdminCreateUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo tài khoản người dùng",
    description="Admin tạo user mới. Student: status pending, Instructor/Admin: nhập password và active ngay"
)
async def create_user_admin(
    user_data: AdminCreateUserRequest,
    current_user: dict = Depends(get_current_user)
):
    """Section 4.1.3 - Tạo tài khoản người dùng (Admin)"""
    return await handle_create_user_admin(user_data, current_user)


@router.put(
    "/users/{user_id}",
    response_model=AdminUpdateUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Cập nhật thông tin người dùng",
    description="Admin có thể update bất kỳ field nào của user"
)
async def update_user_admin(
    user_id: str,
    update_data: AdminUpdateUserRequest,
    current_user: dict = Depends(get_current_user)
):
    """Section 4.1.4 - Cập nhật thông tin người dùng (Admin)"""
    return await handle_update_user_admin(user_id, update_data, current_user)


@router.delete(
    "/users/{user_id}",
    response_model=AdminDeleteUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Xóa người dùng",
    description="Xóa vĩnh viễn user. Kiểm tra dependencies (classes, enrollments, personal courses)"
)
async def delete_user_admin(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Section 4.1.5 - Xóa người dùng (Admin)"""
    return await handle_delete_user_admin(user_id, current_user)


@router.put(
    "/users/{user_id}/role",
    response_model=AdminChangeRoleResponse,
    status_code=status.HTTP_200_OK,
    summary="Thay đổi vai trò người dùng",
    description="Nâng/hạ role (Student ↔ Instructor ↔ Admin). Check impact trước khi thay đổi"
)
async def change_user_role_admin(
    user_id: str,
    role_data: AdminChangeRoleRequest,
    current_user: dict = Depends(get_current_user)
):
    """Section 4.1.6 - Thay đổi vai trò người dùng (Admin)"""
    return await handle_change_user_role_admin(user_id, role_data, current_user)


@router.post(
    "/users/{user_id}/reset-password",
    response_model=AdminResetPasswordResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset mật khẩu người dùng",
    description="Force reset password cho user. Admin gửi password mới qua kênh khác"
)
async def reset_user_password_admin(
    user_id: str,
    password_data: AdminResetPasswordRequest,
    current_user: dict = Depends(get_current_user)
):
    """Section 4.1.7 - Reset mật khẩu người dùng (Admin)"""
    return await handle_reset_user_password_admin(user_id, password_data, current_user)


# ============================================================================
# ADMIN COURSE MANAGEMENT (Section 4.2)
# ============================================================================

@router.get(
    "/courses",
    response_model=AdminCourseListResponse,
    status_code=status.HTTP_200_OK,
    summary="Xem tất cả khóa học",
    description="List all courses (public + personal) với filter (author, status, category, type), search"
)
async def list_courses_admin(
    author_id: Optional[str] = Query(None, description="Filter author (owner_id)"),
    status_param: Optional[str] = Query(None, alias="status", description="draft|published|archived"),
    category: Optional[str] = Query(None, description="Filter category"),
    course_type: Optional[str] = Query(None, description="public|personal"),
    keyword: Optional[str] = Query(None, description="Search tên course"),
    sort_by: str = Query("created_at", description="Field sort"),
    sort_order: str = Query("desc", description="asc|desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Section 4.2.1 - Xem tất cả khóa học (Admin)"""
    return await handle_list_courses_admin(
        current_user=current_user,
        author_id=author_id,
        status=status_param,
        category=category,
        course_type=course_type,
        keyword=keyword,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit
    )


@router.get(
    "/courses/{course_id}",
    response_model=AdminCourseDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Xem chi tiết khóa học",
    description="Xem thông tin đầy đủ course: metadata, modules/lessons structure, analytics"
)
async def get_course_detail_admin(
    course_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Section 4.2.2 - Xem chi tiết khóa học (Admin)"""
    return await handle_get_course_detail_admin(course_id, current_user)


@router.post(
    "/courses",
    response_model=AdminCourseCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo khóa học chính thức",
    description="Admin tạo official course (public). Có thể thiết kế modules, lessons, publish ngay"
)
async def create_course_admin(
    course_data: AdminCourseCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Section 4.2.3 - Tạo khóa học chính thức (Admin)"""
    return await handle_create_course_admin(course_data, current_user)


@router.put(
    "/courses/{course_id}",
    response_model=AdminCourseUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Chỉnh sửa bất kỳ khóa học nào",
    description="Admin có quyền sửa BẤT KỲ course nào (bao gồm personal courses của user)"
)
async def update_course_admin(
    course_id: str,
    update_data: AdminCourseUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Section 4.2.4 - Chỉnh sửa bất kỳ khóa học nào (Admin)"""
    return await handle_update_course_admin(course_id, update_data, current_user)


@router.delete(
    "/courses/{course_id}",
    response_model=AdminDeleteCourseResponse,
    status_code=status.HTTP_200_OK,
    summary="Xóa khóa học",
    description="Xóa vĩnh viễn course. Kiểm tra impact (enrollments, classes) trước khi xóa"
)
async def delete_course_admin(
    course_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Section 4.2.5 - Xóa khóa học (Admin)"""
    return await handle_delete_course_admin(course_id, current_user)


# ============================================================================
# Section 4.3: CLASS MONITORING FOR ADMIN
# ============================================================================

@router.get(
    "/classes",
    response_model=AdminClassListResponse,
    status_code=status.HTTP_200_OK,
    summary="Danh sách lớp học",
    description="Lấy danh sách tất cả classes với instructor info và statistics"
)
async def list_classes_admin(
    page: int = Query(1, ge=1, description="Số trang"),
    limit: int = Query(20, ge=1, le=100, description="Số items per page"),
    search: Optional[str] = Query(None, description="Tìm kiếm theo tên class"),
    instructor_filter: Optional[str] = Query(None, description="Lọc theo instructor ID"),
    status_filter: Optional[str] = Query(None, description="Lọc theo status"),
    sort_by: str = Query("created_at", description="Field để sort"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Thứ tự sort"),
    current_user: dict = Depends(get_current_user)
):
    """Section 4.3.1 - Danh sách lớp học (Admin)"""
    return await handle_list_classes_admin(
        page, limit, search, instructor_filter, status_filter, 
        sort_by, sort_order, current_user
    )


@router.get(
    "/classes/{class_id}",
    response_model=AdminClassDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Chi tiết lớp học",
    description="Xem thông tin đầy đủ class: instructor, students, progress, statistics"
)
async def get_class_detail_admin(
    class_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Section 4.3.2 - Chi tiết lớp học (Admin)"""
    return await handle_get_class_detail_admin(class_id, current_user)


# ============================================================================
# ADMIN ANALYTICS (Section 4.4.2-4.4.4)
# ============================================================================

@router.get(
    "/analytics/users-growth",
    status_code=status.HTTP_200_OK,
    summary="Thống kê tăng trưởng người dùng",
    description="Phân tích tăng trưởng người dùng theo thời gian với breakdown theo role"
)
async def get_users_growth_analytics(
    time_range: str = Query("30d", regex="^(7d|30d|90d)$", description="Khoảng thời gian"),
    role_filter: Optional[str] = Query(None, description="Lọc theo role cụ thể"),
    current_user: dict = Depends(get_current_user)
):
    """Section 4.4.2 - Thống kê tăng trưởng người dùng (Admin)"""
    from controllers.dashboard_controller import handle_get_users_growth_analytics
    return await handle_get_users_growth_analytics(time_range, role_filter, current_user)


@router.get(
    "/analytics/courses",
    status_code=status.HTTP_200_OK,
    summary="Phân tích khóa học chuyên sâu",
    description="Analytics khóa học: top courses, completion rates, creation trends"
)
async def get_course_analytics(
    time_range: str = Query("30d", regex="^(7d|30d|90d)$", description="Khoảng thời gian"),
    category_filter: Optional[str] = Query(None, description="Lọc theo danh mục"),
    current_user: dict = Depends(get_current_user)
):
    """Section 4.4.3 - Phân tích khóa học (Admin)"""
    from controllers.dashboard_controller import handle_get_course_analytics
    return await handle_get_course_analytics(time_range, category_filter, current_user)


@router.get(
    "/analytics/system-health",
    status_code=status.HTTP_200_OK,
    summary="Giám sát sức khỏe hệ thống",
    description="Metrics hệ thống: database, performance, alerts, utilization"
)
async def get_system_health(
    current_user: dict = Depends(get_current_user)
):
    """Section 4.4.4 - Giám sát sức khỏe hệ thống (Admin)"""
    from controllers.dashboard_controller import handle_get_system_health
    return await handle_get_system_health(current_user)

