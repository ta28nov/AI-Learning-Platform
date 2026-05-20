"""
Auth Controller - Xử lý requests liên quan authentication
Tuân thủ: CHUCNANG.md Section 2.1, ENDPOINTS.md /auth/* routes, API_SCHEMA.md
"""

from datetime import datetime, timedelta
from typing import Dict
from fastapi import HTTPException, status
from schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    UserInfo,
    RefreshTokenRequest,
    RefreshTokenResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    VerifyEmailRequest,
    VerifyEmailResponse,
    ResendVerificationRequest,
    ResendVerificationResponse,
)
from services import auth_service, user_service
from models.models import User


async def handle_register(request: RegisterRequest) -> RegisterResponse:
    """
    Đăng ký tài khoản mới - POST /api/v1/auth/register (Section 2.1.1)
    
    Args:
        request: RegisterRequest chứa full_name, email, password
        
    Returns:
        RegisterResponse: Thông tin user mới được tạo
        
    Raises:
        HTTPException 400: Email đã tồn tại hoặc validation error
    """
    try:
        # Tạo user mới
        user = await user_service.create_user(
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            role="student"  # Mặc định là student
        )
        
        # Trả về response theo API_SCHEMA.md
        verification_token = await auth_service.issue_email_verification(str(user.id))
        return RegisterResponse(
            id=str(user.id),
            full_name=user.full_name,
            email=user.email,
            role=user.role,
            status=user.status,
            created_at=user.created_at,
            message="Đăng ký tài khoản thành công",
            verification_token=verification_token,
        )
    
    except ValueError as e:
        # Email đã tồn tại
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email {request.email} đã được sử dụng"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi tạo tài khoản"
        )


async def handle_login(request: LoginRequest) -> LoginResponse:
    """
    Đăng nhập hệ thống - POST /api/v1/auth/login (Section 2.1.2)
    
    Args:
        request: LoginRequest chứa email, password, remember_me
        
    Returns:
        LoginResponse: Access token, refresh token và thông tin user
        
    Raises:
        HTTPException 401: Email hoặc password không đúng hoặc tài khoản inactive
    """
    # Authenticate user
    # authenticate_user raises ValueError cho tài khoản inactive/suspended/deleted
    # Returns None cho sai email/password
    try:
        user = await auth_service.authenticate_user(
            email=request.email,
            password=request.password
        )
    except ValueError as e:
        # Tài khoản bị khóa/vô hiệu hóa — FE cần hiển thị lý do cụ thể
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác"
        )
    
    # Cập nhật last_login_at
    user.last_login_at = datetime.utcnow()
    await user.save()
    
    # Tạo access token (15 phút)
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    
    # Tạo refresh token (7 ngày nếu remember_me=true, 1 ngày nếu false)
    refresh_token_expires = timedelta(days=7 if request.remember_me else 1)
    refresh_token = auth_service.create_refresh_token(
        data={"sub": str(user.id)},
        expires_delta=refresh_token_expires
    )
    
    # Lưu refresh token vào database
    expires_at = datetime.utcnow() + refresh_token_expires
    await auth_service.save_refresh_token(
        user_id=str(user.id),
        token=refresh_token,
        expires_at=expires_at
    )
    
    # Trả về response theo API_SCHEMA.md
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
        user=UserInfo(
            id=str(user.id),
            full_name=user.full_name,
            email=user.email,
            role=user.role,
            avatar=user.avatar_url
        )
    )


async def handle_logout(user_id: str) -> LogoutResponse:
    """
    Đăng xuất tài khoản - POST /api/v1/auth/logout (Section 2.1.3)
    
    Args:
        user_id: UUID của user từ JWT token
        
    Returns:
        LogoutResponse: Message xác nhận đăng xuất thành công
    """
    # Xóa tất cả refresh tokens của user (logout all devices)
    await auth_service.delete_all_user_tokens(user_id)
    
    return LogoutResponse(message="Đăng xuất thành công")


async def logout_all(current_user_id: str) -> Dict:
    """
    Đăng xuất tất cả devices
    Endpoint: POST /auth/logout-all
    """
    count = await auth_service.delete_all_user_tokens(current_user_id)
    
    return {
        "message": f"Đã đăng xuất {count} phiên đăng nhập"
    }


async def handle_refresh_token(request: RefreshTokenRequest) -> RefreshTokenResponse:
    """
    Làm mới access token - POST /api/v1/auth/refresh
    
    Dùng refresh_token để tạo access_token mới khi token cũ hết hạn (15 phút).
    Không cần Bearer header vì access token đã hết hạn.
    
    Args:
        request: RefreshTokenRequest chứa refresh_token
        
    Returns:
        RefreshTokenResponse: access_token mới + token_type
        
    Raises:
        HTTPException 401: Refresh token không hợp lệ, hết hạn, hoặc bị thu hồi
    """
    # Validate refresh token (decode JWT + check DB)
    stored_token = await auth_service.validate_refresh_token(request.refresh_token)
    
    if not stored_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token không hợp lệ hoặc đã hết hạn"
        )
    
    # Lấy user từ DB để tạo access token mới
    user = await User.get(stored_token.user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Người dùng không tồn tại"
        )
    
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản đã bị vô hiệu hóa"
        )
    
    # Tạo access token mới (15 phút)
    new_access_token = auth_service.create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    
    return RefreshTokenResponse(
        access_token=new_access_token,
        token_type="Bearer"
    )


async def handle_forgot_password(request: ForgotPasswordRequest) -> ForgotPasswordResponse:
    """POST /auth/forgot-password — luôn 200 với message chung."""
    try:
        result = await auth_service.request_password_reset(request.email)
        return ForgotPasswordResponse(**result)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể xử lý yêu cầu quên mật khẩu",
        )


async def handle_verify_email(request: VerifyEmailRequest) -> VerifyEmailResponse:
    try:
        result = await auth_service.verify_email_with_token(request.token)
        return VerifyEmailResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể xác thực email",
        )


async def handle_resend_verification(request: ResendVerificationRequest) -> ResendVerificationResponse:
    try:
        result = await auth_service.request_email_verification(request.email)
        return ResendVerificationResponse(**result)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể gửi lại email xác thực",
        )


async def handle_reset_password(request: ResetPasswordRequest) -> ResetPasswordResponse:
    """POST /auth/reset-password"""
    try:
        result = await auth_service.reset_password_with_token(
            request.token,
            request.new_password,
        )
        return ResetPasswordResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể đặt lại mật khẩu",
        )
