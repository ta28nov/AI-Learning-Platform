"""
Auth Router - Định nghĩa routes cho authentication endpoints
Tuân thủ: ENDPOINTS.md auth router section, API_SCHEMA.md
"""

from fastapi import APIRouter, Depends, status
from schemas.auth import (
    RegisterRequest, RegisterResponse,
    LoginRequest, LoginResponse,
    LogoutResponse
)
from controllers.auth_controller import (
    handle_register,
    handle_login,
    handle_logout
)
from middleware.auth import get_current_user


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản mới",
    description="Tạo tài khoản mới với email, mật khẩu, tên đầy đủ. Vai trò mặc định là student. (Section 2.1.1)"
)
async def register(request: RegisterRequest):
    """
    Đăng ký tài khoản mới - POST /api/v1/auth/register
    
    **Thông tin bắt buộc:**
    - **full_name**: Tên đầy đủ (tối thiểu 2 từ, tối đa 100 ký tự)
    - **email**: Email hợp lệ và unique trong hệ thống
    - **password**: Mật khẩu (tối thiểu 8 ký tự, chứa số, chữ hoa, ký tự đặc biệt)
    
    **Returns:**
    - 201 Created: User được tạo thành công với thông tin cơ bản
    - 400 Bad Request: Email đã tồn tại hoặc validation error
    """
    return await handle_register(request)


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Đăng nhập hệ thống",
    description="Xác thực người dùng và trả về JWT access token (15 phút) + refresh token (7 ngày). (Section 2.1.2)"
)
async def login(request: LoginRequest):
    """
    Đăng nhập - POST /api/v1/auth/login
    
    **Thông tin bắt buộc:**
    - **email**: Email đã đăng ký
    - **password**: Mật khẩu tài khoản
    - **remember_me**: Ghi nhớ đăng nhập (gia hạn refresh token - 7 ngày nếu true, 1 ngày nếu false)
    
    **Returns:**
    - 200 OK: Access token, refresh token và thông tin user
    - 401 Unauthorized: Email hoặc password không đúng hoặc tài khoản inactive
    """
    return await handle_login(request)


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    summary="Đăng xuất tài khoản",
    description="Vô hiệu hóa token hiện tại và xóa tất cả refresh tokens. (Section 2.1.3)"
)
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Đăng xuất - POST /api/v1/auth/logout
    
    **Requires:** Bearer token trong Authorization header
    
    Xóa tất cả refresh tokens của user khỏi database để đảm bảo bảo mật
    (logout all devices)
    
    **Returns:**
    - 200 OK: Message xác nhận đăng xuất thành công
    """
    return await handle_logout(current_user["user_id"])
