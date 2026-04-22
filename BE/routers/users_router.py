"""
Users Router - Định nghĩa routes cho user profile endpoints
Tuân thủ: ENDPOINTS.md users router section, API_SCHEMA.md
"""

from fastapi import APIRouter, Depends, status
from schemas.user import (
    UserProfileResponse,
    UserProfileUpdateRequest,
    UserProfileUpdateResponse
)
from controllers.user_controller import (
    handle_get_profile,
    handle_update_profile
)
from middleware.auth import get_current_user


router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Xem hồ sơ cá nhân",
    description="Hiển thị thông tin chi tiết người dùng đang đăng nhập: tên, email, avatar, bio, sở thích học tập. (Section 2.1.4)"
)
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    """
    Xem hồ sơ cá nhân - GET /api/v1/users/me
    
    **Requires:** Bearer token trong Authorization header
    
    **Returns:**
    - 200 OK: Thông tin chi tiết user (tên đầy đủ, email, avatar, bio cá nhân, sở thích học tập, thông tin liên hệ)
    - 404 Not Found: User không tồn tại
    
    **Note:** Tất cả thông tin như avatar_url, bio, contact_info có thể null (không bắt buộc)
    """
    return await handle_get_profile(current_user["user_id"])


@router.patch(
    "/me",
    response_model=UserProfileUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Cập nhật hồ sơ cá nhân",
    description="Chỉnh sửa thông tin cá nhân: tên đầy đủ, avatar, bio, thông tin liên hệ, sở thích học tập. (Section 2.1.5)"
)
async def update_my_profile(
    update_data: UserProfileUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Cập nhật hồ sơ - PATCH /api/v1/users/me
    
    **Requires:** Bearer token trong Authorization header
    
    **Tất cả các trường đều tùy chọn** - chỉ cập nhật những trường được gửi lên:
    - **full_name**: Tên đầy đủ (tùy chọn, tối thiểu 2 từ nếu cung cấp)
    - **avatar_url**: URL ảnh đại diện (tùy chọn, phải là URL hợp lệ)
    - **bio**: Mô tả bản thân (tùy chọn, tối đa 500 ký tự)
    - **contact_info**: Thông tin liên hệ (tùy chọn)
    - **learning_preferences**: Danh sách sở thích học tập (tùy chọn)
    
    **Returns:**
    - 200 OK: Thông tin user sau khi cập nhật kèm message "Cập nhật hồ sơ thành công"
    - 400 Bad Request: Dữ liệu không hợp lệ (full name < 2 từ, bio > 500 ký tự, URL không hợp lệ)
    - 404 Not Found: User không tồn tại
    """
    return await handle_update_profile(current_user["user_id"], update_data)
