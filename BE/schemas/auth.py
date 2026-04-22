"""
Authentication Schemas
Định nghĩa request/response schemas cho auth endpoints (2.1.1-2.1.3)
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional


class RegisterRequest(BaseModel):
    """Schema cho đăng ký tài khoản mới - POST /api/v1/auth/register"""
    full_name: str = Field(
        ..., 
        min_length=3, 
        max_length=100,
        description="Tên đầy đủ (bắt buộc, tối thiểu 2 từ, tối đa 100 ký tự)"
    )
    email: EmailStr = Field(
        ...,
        description="Email hợp lệ và unique trong hệ thống"
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Mật khẩu (tối thiểu 8 ký tự, chứa số, chữ hoa, ký tự đặc biệt)"
    )
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        """Validate full name có ít nhất 2 từ"""
        words = v.strip().split()
        if len(words) < 2:
            raise ValueError('Full name must have at least 2 words')
        return v.strip()
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password có đủ mạnh: số, chữ hoa, ký tự đặc biệt"""
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?' for char in v):
            raise ValueError('Password must contain at least one special character')
        return v


class RegisterResponse(BaseModel):
    """Schema response cho đăng ký thành công - 201 Created"""
    id: str = Field(..., description="UUID v4 của user được tạo")
    full_name: str
    email: str
    role: str = Field(default="student", description="Vai trò mặc định là student")
    status: str = Field(default="active", description="Trạng thái tài khoản")
    created_at: datetime = Field(..., description="Thời gian tạo tài khoản (ISO 8601)")
    message: str = Field(default="Đăng ký tài khoản thành công")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "full_name": "Nguyễn Văn A",
                "email": "nguyenvana@example.com",
                "role": "student",
                "status": "active",
                "created_at": "2024-01-15T10:30:00Z",
                "message": "Đăng ký tài khoản thành công"
            }
        }


class LoginRequest(BaseModel):
    """Schema cho đăng nhập - POST /api/v1/auth/login"""
    email: EmailStr = Field(..., description="Email đã đăng ký")
    password: str = Field(..., description="Mật khẩu tài khoản")
    remember_me: bool = Field(
        default=False,
        description="Ghi nhớ đăng nhập để gia hạn refresh token (7 ngày nếu true, 1 ngày nếu false)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "nguyenvana@example.com",
                "password": "MyPassword123!",
                "remember_me": True
            }
        }


class UserInfo(BaseModel):
    """Schema thông tin user trong LoginResponse"""
    id: str = Field(..., description="UUID user")
    full_name: str
    email: str
    role: str = Field(..., description="student|instructor|admin")
    avatar: Optional[str] = Field(None, description="URL avatar, có thể null")


class LoginResponse(BaseModel):
    """Schema response cho đăng nhập thành công - 200 OK"""
    access_token: str = Field(..., description="JWT token, thời hạn 15 phút")
    refresh_token: str = Field(..., description="JWT token, thời hạn 7 ngày (remember_me=true) hoặc 1 ngày")
    token_type: str = Field(default="Bearer", description="Loại token")
    user: UserInfo = Field(..., description="Thông tin user")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "Bearer",
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "full_name": "Nguyễn Văn A",
                    "email": "nguyenvana@example.com",
                    "role": "student",
                    "avatar": "https://example.com/avatar.jpg"
                }
            }
        }


class LogoutResponse(BaseModel):
    """Schema response cho đăng xuất - 200 OK"""
    message: str = Field(default="Đăng xuất thành công")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Đăng xuất thành công"
            }
        }


class RefreshTokenRequest(BaseModel):
    """Schema cho refresh token - POST /api/v1/auth/refresh"""
    refresh_token: str = Field(..., description="Refresh token hiện tại")


class RefreshTokenResponse(BaseModel):
    """Schema response cho refresh token thành công"""
    access_token: str = Field(..., description="JWT token mới, thời hạn 15 phút")
    token_type: str = Field(default="Bearer")
