"""
User Profile Schemas
Định nghĩa request/response schemas cho user profile endpoints (1.4-1.5)
"""

from pydantic import BaseModel, HttpUrl, Field, field_validator
from datetime import datetime
from typing import Optional, List


class UserProfileResponse(BaseModel):
    """Schema response cho xem hồ sơ cá nhân - GET /api/v1/users/me"""
    id: str = Field(..., description="UUID user")
    full_name: str
    email: str
    role: str = Field(..., description="student|instructor|admin")
    avatar_url: Optional[str] = Field(None, description="URL ảnh đại diện, có thể null")
    bio: Optional[str] = Field(None, description="Mô tả bản thân (tối đa 500 ký tự), có thể null")
    learning_preferences: List[str] = Field(
        default_factory=list,
        description="Danh sách sở thích học tập: Programming, Math, Business, Languages..."
    )
    contact_info: Optional[str] = Field(None, description="Thông tin liên hệ, có thể null")
    created_at: datetime = Field(..., description="Ngày tạo tài khoản (ISO 8601)")
    updated_at: datetime = Field(..., description="Lần cập nhật cuối (ISO 8601)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "full_name": "Nguyễn Văn A",
                "email": "nguyenvana@example.com",
                "role": "student",
                "avatar_url": "https://example.com/avatar.jpg",
                "bio": "Passionate about learning programming and AI",
                "learning_preferences": ["Programming", "AI/ML", "Data Science"],
                "contact_info": "+84 123 456 789",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-20T14:25:00Z"
            }
        }


class UserProfileUpdateRequest(BaseModel):
    """Schema request cho cập nhật hồ sơ - PATCH /api/v1/users/me"""
    full_name: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        description="Tên đầy đủ (tùy chọn, tối thiểu 2 từ)"
    )
    avatar_url: Optional[str] = Field(
        None,
        description="URL ảnh hợp lệ (tùy chọn)"
    )
    bio: Optional[str] = Field(
        None,
        max_length=500,
        description="Mô tả bản thân (tùy chọn, tối đa 500 ký tự)"
    )
    contact_info: Optional[str] = Field(
        None,
        max_length=200,
        description="Thông tin liên hệ (tùy chọn)"
    )
    learning_preferences: Optional[List[str]] = Field(
        None,
        description="Danh sách sở thích học tập (tùy chọn)"
    )
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate full name có ít nhất 2 từ nếu được cung cấp"""
        if v is not None:
            words = v.strip().split()
            if len(words) < 2:
                raise ValueError('Full name must have at least 2 words')
            return v.strip()
        return v
    
    @field_validator('avatar_url')
    @classmethod
    def validate_avatar_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate avatar_url là URL hợp lệ nếu được cung cấp"""
        if v is not None and v.strip():
            # Basic URL validation
            if not (v.startswith('http://') or v.startswith('https://')):
                raise ValueError('Avatar URL must start with http:// or https://')
            return v.strip()
        return v
    
    @field_validator('bio')
    @classmethod
    def validate_bio_length(cls, v: Optional[str]) -> Optional[str]:
        """Validate bio không quá 500 ký tự"""
        if v is not None and len(v) > 500:
            raise ValueError('Bio must not exceed 500 characters')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "Nguyễn Văn A",
                "avatar_url": "https://example.com/new-avatar.jpg",
                "bio": "Updated bio - Passionate about learning programming and AI",
                "contact_info": "+84 987 654 321",
                "learning_preferences": ["Programming", "AI/ML", "Data Science", "Web Development"]
            }
        }


class UserProfileUpdateResponse(BaseModel):
    """Schema response cho cập nhật hồ sơ thành công - 200 OK"""
    id: str = Field(..., description="UUID user")
    full_name: str
    email: str
    role: str
    avatar_url: Optional[str] = Field(None, description="URL avatar, có thể null")
    bio: Optional[str] = Field(None, description="Mô tả bản thân, có thể null")
    learning_preferences: List[str] = Field(default_factory=list)
    contact_info: Optional[str] = Field(None, description="Thông tin liên hệ, có thể null")
    updated_at: datetime = Field(..., description="Thời gian cập nhật")
    message: str = Field(default="Cập nhật hồ sơ thành công")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "full_name": "Nguyễn Văn A",
                "email": "nguyenvana@example.com",
                "role": "student",
                "avatar_url": "https://example.com/new-avatar.jpg",
                "bio": "Updated bio - Passionate about learning programming and AI",
                "learning_preferences": ["Programming", "AI/ML", "Data Science", "Web Development"],
                "contact_info": "+84 987 654 321",
                "updated_at": "2024-01-21T09:15:00Z",
                "message": "Cập nhật hồ sơ thành công"
            }
        }
