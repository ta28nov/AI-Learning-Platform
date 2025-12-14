"""
User Controller - Xử lý requests liên quan user profile và admin user management
Tuân thủ: CHUCNANG.md Section 2.1.4-2.1.5, 4.1, API_SCHEMA.md
"""

from fastapi import HTTPException, status, Query
from models.models import User
from schemas.user import UserProfileResponse, UserProfileUpdateRequest, UserProfileUpdateResponse
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
    AdminResetPasswordResponse
)
from datetime import datetime
from typing import Optional
import services.user_service as user_service


async def handle_get_profile(user_id: str) -> UserProfileResponse:
    """
    Xem hồ sơ cá nhân - GET /api/v1/users/me (Section 2.1.4)
    
    Args:
        user_id: UUID của user từ JWT token
        
    Returns:
        UserProfileResponse: Thông tin chi tiết user
        
    Raises:
        HTTPException 404: User không tồn tại
    """
    try:
        # Lấy thông tin user từ database
        user = await User.get(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Trả về response theo API_SCHEMA.md
        return UserProfileResponse(
            id=str(user.id),
            full_name=user.full_name,
            email=user.email,
            role=user.role,
            avatar_url=user.avatar_url,
            bio=user.bio,
            learning_preferences=user.learning_preferences or [],
            contact_info=user.contact_info,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi lấy thông tin user"
        )


async def handle_update_profile(
    user_id: str,
    update_data: UserProfileUpdateRequest
) -> UserProfileUpdateResponse:
    """
    Cập nhật hồ sơ cá nhân - PATCH /api/v1/users/me (Section 2.1.5)
    
    Args:
        user_id: UUID của user từ JWT token
        update_data: Dữ liệu cập nhật (tất cả các trường đều tùy chọn)
        
    Returns:
        UserProfileUpdateResponse: Thông tin user sau khi cập nhật
        
    Raises:
        HTTPException 404: User không tồn tại
        HTTPException 400: Dữ liệu không hợp lệ
    """
    try:
        # Lấy user hiện tại
        user = await User.get(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Cập nhật các trường được cung cấp (chỉ update trường không null)
        update_dict = update_data.model_dump(exclude_unset=True)
        
        for field, value in update_dict.items():
            setattr(user, field, value)
        
        # Cập nhật thời gian updated_at
        user.updated_at = datetime.utcnow()
        
        # Lưu vào database
        await user.save()
        
        # Trả về response theo API_SCHEMA.md
        return UserProfileUpdateResponse(
            id=str(user.id),
            full_name=user.full_name,
            email=user.email,
            role=user.role,
            avatar_url=user.avatar_url,
            bio=user.bio,
            learning_preferences=user.learning_preferences or [],
            contact_info=user.contact_info,
            updated_at=user.updated_at,
            message="Cập nhật hồ sơ thành công"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi cập nhật thông tin user"
        )


# ============================================================================
# ADMIN USER MANAGEMENT HANDLERS (Section 4.1)
# ============================================================================

async def handle_list_users_admin(
    current_user: dict,
    role: Optional[str] = None,
    status_filter: Optional[str] = None,  # Match với router
    keyword: Optional[str] = None,  # Match với router (search → keyword)
    sort_by: str = "created_at",
    sort_order: str = "desc",
    skip: int = 0,
    limit: int = 50
) -> AdminUserListResponse:
    """
    4.1.1: Xem danh sách người dùng (Admin)
    GET /api/v1/admin/users
    
    Args:
        current_user: User dict từ JWT (phải là admin)
        role: Filter role
        status_filter: Filter status (match với router alias)
        keyword: Search tên hoặc email (match với router)
        sort_by: Field sort
        sort_order: asc|desc
        skip, limit: Pagination
        
    Returns:
        AdminUserListResponse
    """
    try:
        # Verify admin role (RBAC handled by middleware)
        result = await user_service.list_users_admin(
            role=role,
            status=status_filter,  # Pass as status to service
            search=keyword,  # Pass as search to service
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=limit
        )
        
        return AdminUserListResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy danh sách users: {str(e)}"
        )


async def handle_get_user_detail_admin(
    user_id: str,
    current_user: dict
) -> AdminUserDetailResponse:
    """
    4.1.2: Xem hồ sơ người dùng chi tiết (Admin)
    GET /api/v1/admin/users/{user_id}
    
    Args:
        user_id: ID của user cần xem
        current_user: Admin user
        
    Returns:
        AdminUserDetailResponse
    """
    try:
        result = await user_service.get_user_detail_admin(user_id)
        return AdminUserDetailResponse(**result)
    
    except Exception as e:
        if "không tồn tại" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy thông tin user: {str(e)}"
        )


async def handle_create_user_admin(
    user_data: AdminCreateUserRequest,
    current_user: dict
) -> AdminCreateUserResponse:
    """
    4.1.3: Tạo tài khoản người dùng (Admin)
    POST /api/v1/admin/users
    
    Args:
        user_data: Thông tin user mới
        current_user: Admin user
        
    Returns:
        AdminCreateUserResponse
    """
    try:
        result = await user_service.create_user_admin(
            full_name=user_data.full_name,
            email=user_data.email,
            role=user_data.role,
            password=user_data.password,
            bio=user_data.bio,
            avatar=user_data.avatar
        )
        
        return AdminCreateUserResponse(**result)
    
    except Exception as e:
        if "đã được sử dụng" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        if "bắt buộc" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo user: {str(e)}"
        )


async def handle_update_user_admin(
    user_id: str,
    update_data: AdminUpdateUserRequest,
    current_user: dict
) -> AdminUpdateUserResponse:
    """
    4.1.4: Cập nhật thông tin người dùng (Admin)
    PUT /api/v1/admin/users/{user_id}
    
    Args:
        user_id: ID của user cần update
        update_data: Thông tin cập nhật
        current_user: Admin user
        
    Returns:
        AdminUpdateUserResponse
    """
    try:
        result = await user_service.update_user_admin(
            user_id=user_id,
            full_name=update_data.full_name,
            email=update_data.email,
            bio=update_data.bio,
            avatar=update_data.avatar,
            status=update_data.status
        )
        
        return AdminUpdateUserResponse(**result)
    
    except Exception as e:
        if "không tồn tại" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        if "đã được sử dụng" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi cập nhật user: {str(e)}"
        )


async def handle_delete_user_admin(
    user_id: str,
    current_user: dict
) -> AdminDeleteUserResponse:
    """
    4.1.5: Xóa người dùng (Admin)
    DELETE /api/v1/admin/users/{user_id}
    
    Args:
        user_id: ID của user cần xóa
        current_user: Admin user
        
    Returns:
        AdminDeleteUserResponse
    """
    try:
        result = await user_service.delete_user_admin(user_id)
        return AdminDeleteUserResponse(**result)
    
    except Exception as e:
        if "không tồn tại" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        if "Không thể xóa" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xóa user: {str(e)}"
        )


async def handle_change_user_role_admin(
    user_id: str,
    role_data: AdminChangeRoleRequest,
    current_user: dict
) -> AdminChangeRoleResponse:
    """
    4.1.6: Thay đổi vai trò người dùng (Admin)
    PUT /api/v1/admin/users/{user_id}/role
    
    Args:
        user_id: ID của user
        role_data: Role mới
        current_user: Admin user
        
    Returns:
        AdminChangeRoleResponse
    """
    try:
        result = await user_service.change_user_role_admin(
            user_id=user_id,
            new_role=role_data.new_role
        )
        
        return AdminChangeRoleResponse(**result)
    
    except Exception as e:
        if "không tồn tại" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        if "Không thể" in str(e) or "đã có role" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi thay đổi role: {str(e)}"
        )


async def handle_reset_user_password_admin(
    user_id: str,
    password_data: AdminResetPasswordRequest,
    current_user: dict
) -> AdminResetPasswordResponse:
    """
    4.1.7: Reset mật khẩu người dùng (Admin)
    POST /api/v1/admin/users/{user_id}/reset-password
    
    Args:
        user_id: ID của user
        password_data: Password mới
        current_user: Admin user
        
    Returns:
        AdminResetPasswordResponse
    """
    try:
        result = await user_service.reset_user_password_admin(
            user_id=user_id,
            new_password=password_data.new_password
        )
        
        return AdminResetPasswordResponse(**result)
    
    except Exception as e:
        if "không tồn tại" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi reset password: {str(e)}"
        )

