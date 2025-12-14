"""
Admin Controller
Xử lý requests cho admin management endpoints
Section 4.1-4.3
"""

from typing import Dict, Optional
from fastapi import HTTPException, status

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
from services import admin_service


# ============================================================================
# Section 4.1: QUẢN LÝ NGƯỜI DÙNG
# ============================================================================

async def handle_list_users_admin(
    role: Optional[str] = None,
    status_filter: Optional[str] = None,
    keyword: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    created_from: Optional[str] = None,
    created_to: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: Dict = None
) -> AdminUserListResponse:
    """
    4.1.1: Xem danh sách người dùng với filter, search, sort
    
    Flow:
    1. Validate admin permission
    2. Gọi admin_service.get_users_list với filters
    3. Return paginated list với autocomplete search
    
    Args:
        role: Lọc theo vai trò (student|instructor|admin)
        status_filter: Lọc theo trạng thái (active|inactive)
        keyword: Tìm kiếm theo tên hoặc email
        sort_by: Sắp xếp theo cột (full_name|email|created_at|role)
        sort_order: Thứ tự (asc|desc)
        created_from: Lọc từ ngày tạo (ISO 8601)
        created_to: Lọc đến ngày tạo (ISO 8601)
        skip: Pagination offset
        limit: Pagination limit (max 100)
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminUserListResponse với data, total, pagination info
        
    Raises:
        HTTPException 403: Không phải admin
        HTTPException 400: Invalid filter parameters
        HTTPException 500: Lỗi server
    """
    try:
        # Validate admin role
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ admin mới có quyền xem danh sách người dùng"
            )
        
        # Validate limit
        if limit > 100:
            limit = 100
            
        # Convert skip to page for admin service
        page = (skip // limit) + 1 if limit > 0 else 1
            
        users_data = await admin_service.get_users_list_admin(
            page=page,
            limit=limit,
            search=keyword,
            role_filter=role,
            status_filter=status_filter,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return AdminUserListResponse(**users_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy danh sách người dùng: {str(e)}"
        )


async def handle_get_user_detail_admin(
    user_id: str,
    current_user: Dict
) -> AdminUserDetailResponse:
    """
    4.1.2: Xem hồ sơ người dùng chi tiết
    
    Flow:
    1. Validate admin permission
    2. Gọi admin_service.get_user_detail với user_id
    3. Return thông tin đầy đủ với statistics
    
    Args:
        user_id: UUID của người dùng cần xem
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminUserDetailResponse với thông tin chi tiết
        
    Raises:
        HTTPException 403: Không phải admin
        HTTPException 404: Không tìm thấy user
        HTTPException 500: Lỗi server
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ admin mới có quyền xem chi tiết người dùng"
            )
        
        user_detail = await admin_service.get_user_detail_admin(user_id)
        return AdminUserDetailResponse(**user_detail)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy chi tiết người dùng: {str(e)}"
        )


async def handle_create_user_admin(
    user_data: AdminCreateUserRequest,
    current_user: Dict
) -> AdminCreateUserResponse:
    """
    4.1.3: Tạo tài khoản người dùng mới
    
    Flow:
    1. Validate admin permission
    2. Validate email unique
    3. Gọi admin_service.create_user
    
    Args:
        user_data: Thông tin tạo user mới
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminCreateUserResponse với thông tin user mới tạo
        
    Raises:
        HTTPException 403: Không phải admin
        HTTPException 400: Email đã tồn tại hoặc validation error
        HTTPException 500: Lỗi server
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ admin mới có quyền tạo tài khoản"
            )
        
        created_user = await admin_service.create_user_admin(user_data.dict())
        return AdminCreateUserResponse(**created_user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo tài khoản: {str(e)}"
        )


async def handle_update_user_admin(
    user_id: str,
    user_data: AdminUpdateUserRequest,
    current_user: Dict
) -> AdminUpdateUserResponse:
    """
    4.1.4: Cập nhật thông tin người dùng
    
    Flow:
    1. Validate admin permission
    2. Validate email unique (nếu thay đổi)
    3. Gọi admin_service.update_user
    4. Return updated info
    
    Args:
        user_id: UUID của người dùng cần cập nhật
        user_data: Dữ liệu cập nhật (partial)
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminUpdateUserResponse với thông tin đã cập nhật
        
    Raises:
        HTTPException 403: Không phải admin
        HTTPException 404: Không tìm thấy user
        HTTPException 400: Email đã tồn tại
        HTTPException 500: Lỗi server
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ admin mới có quyền cập nhật thông tin người dùng"
            )
        
        updated_user = await admin_service.update_user_admin(user_id, user_data.dict(exclude_unset=True))
        return AdminUpdateUserResponse(**updated_user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi cập nhật thông tin: {str(e)}"
        )


async def handle_delete_user_admin(
    user_id: str,
    current_user: Dict
) -> AdminDeleteUserResponse:
    """
    4.1.5: Xóa người dùng vĩnh viễn
    
    Flow:
    1. Validate admin permission
    2. Kiểm tra dependencies (classes, enrollments, courses)
    3. Gọi admin_service.delete_user nếu không có dependencies
    4. Return confirmation
    
    Args:
        user_id: UUID của người dùng cần xóa
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminDeleteUserResponse với confirmation
        
    Raises:
        HTTPException 403: Không phải admin
        HTTPException 404: Không tìm thấy user
        HTTPException 400: Không thể xóa do có dependencies
        HTTPException 500: Lỗi server
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ admin mới có quyền xóa người dùng"
            )
        
        deleted_info = await admin_service.delete_user_admin(user_id)
        return AdminDeleteUserResponse(**deleted_info)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xóa người dùng: {str(e)}"
        )


async def handle_change_user_role_admin(
    user_id: str,
    role_data: AdminChangeRoleRequest,
    current_user: Dict
) -> AdminChangeRoleResponse:
    """
    4.1.6: Thay đổi vai trò người dùng
    
    Flow:
    1. Validate admin permission
    2. Kiểm tra impact của việc thay đổi role
    3. Gọi admin_service.change_user_role
    4. Return impact analysis và confirmation
    
    Args:
        user_id: UUID của người dùng cần thay đổi role
        role_data: Vai trò mới
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminChangeRoleResponse với old/new role và impact
        
    Raises:
        HTTPException 403: Không phải admin
        HTTPException 404: Không tìm thấy user
        HTTPException 400: Không thể thay đổi role do ràng buộc
        HTTPException 500: Lỗi server
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ admin mới có quyền thay đổi vai trò"
            )
        
        role_change_result = await admin_service.change_user_role_admin(user_id, role_data.new_role)
        return AdminChangeRoleResponse(**role_change_result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi thay đổi vai trò: {str(e)}"
        )


async def handle_reset_user_password_admin(
    user_id: str,
    password_data: AdminResetPasswordRequest,
    current_user: Dict
) -> AdminResetPasswordResponse:
    """
    4.1.7: Reset mật khẩu người dùng
    
    Flow:
    1. Validate admin permission
    2. Validate password strength
    3. Gọi admin_service.reset_user_password
    4. Return confirmation
    
    Args:
        user_id: UUID của người dùng cần reset password
        password_data: Mật khẩu mới
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminResetPasswordResponse với confirmation
        
    Raises:
        HTTPException 403: Không phải admin
        HTTPException 404: Không tìm thấy user
        HTTPException 400: Mật khẩu không hợp lệ
        HTTPException 500: Lỗi server
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ admin mới có quyền reset mật khẩu"
            )
        
        reset_result = await admin_service.reset_user_password_admin(user_id, password_data.new_password)
        return AdminResetPasswordResponse(**reset_result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi reset mật khẩu: {str(e)}"
        )


# ============================================================================
# Section 4.2: QUẢN LÝ KHÓA HỌC (Admin Course Management)
# ============================================================================

async def handle_list_courses_admin(
    author: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    course_type: Optional[str] = None,
    keyword: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: Dict = None
) -> AdminCourseListResponse:
    """
    4.2.1: Xem tất cả khóa học (public + personal)
    
    Args:
        author: Lọc theo tác giả (instructor)
        status: Lọc theo trạng thái (draft|published|archived)
        category: Lọc theo danh mục
        course_type: Lọc theo loại (public|personal)
        keyword: Tìm kiếm theo tên khóa học
        skip: Pagination offset
        limit: Pagination limit
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminCourseListResponse với danh sách khóa học
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ admin mới có quyền xem tất cả khóa học"
            )
        
        # Convert skip to page
        page = (skip // limit) + 1 if limit > 0 else 1
        
        courses_data = await admin_service.get_courses_list_admin(
            page=page,
            limit=limit,
            search=keyword,
            category_filter=category,
            status_filter=status,
            instructor_filter=author,
            sort_by="created_at",
            sort_order="desc"
        )
        
        return AdminCourseListResponse(**courses_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy danh sách khóa học: {str(e)}"
        )


async def handle_get_course_detail_admin(
    course_id: str,
    current_user: Dict
) -> AdminCourseDetailResponse:
    """
    4.2.2: Xem chi tiết khóa học với preview capability
    
    Args:
        course_id: UUID khóa học
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminCourseDetailResponse với thông tin đầy đủ
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ admin mới có quyền xem chi tiết khóa học"
            )
        
        from services import course_service
        course_detail = await course_service.get_course_detail(course_id, current_user.get("user_id"))
        return AdminCourseDetailResponse(**course_detail)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy chi tiết khóa học: {str(e)}"
        )


async def handle_create_course_admin(
    course_data: AdminCourseCreateRequest,
    current_user: Dict
) -> AdminCourseCreateResponse:
    """
    4.2.3: Tạo khóa học chính thức (public course)
    
    Args:
        course_data: Dữ liệu khóa học mới
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminCourseCreateResponse với thông tin khóa học mới
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ admin mới có quyền tạo khóa học chính thức"
            )
        
        created_course = await admin_service.create_course_admin(course_data.dict())
        return AdminCourseCreateResponse(**created_course)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo khóa học: {str(e)}"
        )


async def handle_update_course_admin(
    course_id: str,
    course_data: AdminCourseUpdateRequest,
    current_user: Dict
) -> AdminCourseUpdateResponse:
    """
    4.2.4: Chỉnh sửa bất kỳ khóa học nào (kể cả personal)
    
    Args:
        course_id: UUID khóa học cần cập nhật
        course_data: Dữ liệu cập nhật
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminCourseUpdateResponse với thông tin đã cập nhật
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ admin mới có quyền chỉnh sửa khóa học"
            )
        
        updated_course = await admin_service.update_course_admin(course_id, course_data.dict(exclude_unset=True))
        return AdminCourseUpdateResponse(**updated_course)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi cập nhật khóa học: {str(e)}"
        )


async def handle_delete_course_admin(
    course_id: str,
    current_user: Dict
) -> AdminDeleteCourseResponse:
    """
    4.2.5: Xóa khóa học với impact analysis
    
    Args:
        course_id: UUID khóa học cần xóa
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminDeleteCourseResponse với impact analysis
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ admin mới có quyền xóa khóa học"
            )
        
        delete_result = await admin_service.delete_course_admin(course_id)
        return AdminDeleteCourseResponse(**delete_result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xóa khóa học: {str(e)}"
        )


# ============================================================================
# Section 4.3: GIÁM SÁT LỚP HỌC
# ============================================================================

async def handle_list_classes_admin(
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    instructor_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    current_user: Dict = None
) -> AdminClassListResponse:
    """
    4.3.1: Xem tất cả lớp học từ mọi giảng viên
    
    Flow:
    1. Validate admin permission
    2. Gọi admin_service.get_classes_list với filters
    3. Return thông tin lớp học với instructor và course info
    
    Args:
        instructor_id: Lọc theo giảng viên (UUID)
        course_id: Lọc theo khóa học gốc (UUID)
        status: Lọc theo trạng thái (preparing|active|completed)
        skip: Pagination offset
        limit: Pagination limit
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminClassListResponse với danh sách lớp học
        
    Raises:
        HTTPException 403: Không phải admin
        HTTPException 500: Lỗi server
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ admin mới có quyền xem tất cả lớp học"
            )
        
        classes_data = await admin_service.get_classes_list_admin(
            page=page,
            limit=limit,
            search=search,
            instructor_filter=instructor_filter,
            status_filter=status_filter,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return AdminClassListResponse(**classes_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy danh sách lớp học: {str(e)}"
        )


async def handle_get_class_detail_admin(
    class_id: str,
    current_user: Dict
) -> AdminClassDetailResponse:
    """
    4.3.2: Xem chi tiết lớp học (bất kỳ lớp nào)
    
    Flow:
    1. Validate admin permission
    2. Gọi admin_service.get_class_detail với class_id
    3. Return thông tin đầy đủ về lớp, instructor, students và stats
    
    Args:
        class_id: UUID lớp học cần xem
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminClassDetailResponse với thông tin chi tiết
        
    Raises:
        HTTPException 403: Không phải admin
        HTTPException 404: Không tìm thấy lớp học
        HTTPException 500: Lỗi server
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ admin mới có quyền xem chi tiết lớp học"
            )
        
        class_detail = await admin_service.get_class_detail_admin(class_id)
        return AdminClassDetailResponse(**class_detail)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy chi tiết lớp học: {str(e)}"
        )