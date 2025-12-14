"""
Auth Service - Xử lý authentication và authorization
Sử dụng: bcrypt (passlib), JWT (python-jose), MongoDB (Beanie)
Tuân thủ: CHUCNANG.md Section 2.1 (Login/Register/Token Management)
"""

from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from config.config import get_settings
from models.models import User, RefreshToken

settings = get_settings()


# ============================================================================
# PASSWORD HASHING với bcrypt
# ============================================================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash password sử dụng bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    # Giới hạn độ dài password để tránh lỗi bcrypt (max 72 bytes)
    password = password[:72]
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password với hashed password
    
    Args:
        plain_password: Plain text password từ user
        hashed_password: Hashed password trong database
        
    Returns:
        True nếu password khớp, False nếu không
    """
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================================
# JWT TOKEN CREATION
# ============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Tạo JWT access token với expiry 15 phút
    
    Args:
        data: Dict chứa thông tin để encode vào token (user_id, email, role)
        expires_delta: Custom expiration time (mặc định 15 phút)
        
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire, "type": "access"})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.secret_key, 
        algorithm=settings.algorithm
    )
    
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Tạo JWT refresh token với expiry 7 ngày
    
    Args:
        data: Dict chứa thông tin để encode vào token (user_id)
        expires_delta: Custom expiration time (mặc định 7 ngày)
        
    Returns:
        JWT refresh token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Sử dụng giá trị từ settings hoặc mặc định 7 ngày
        expire_days = getattr(settings, "refresh_token_expire_days", 7)
        expire = datetime.utcnow() + timedelta(days=expire_days)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.secret_key, 
        algorithm=settings.algorithm
    )
    
    return encoded_jwt


# ============================================================================
# JWT TOKEN VALIDATION
# ============================================================================

def decode_token(token: str) -> Optional[dict]:
    """
    Decode và validate JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload dict nếu valid, None nếu invalid
    """
    try:
        payload = jwt.decode(
            token, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        return None


async def validate_refresh_token(token: str) -> Optional[RefreshToken]:
    """
    Validate refresh token từ database
    
    Args:
        token: Refresh token string
        
    Returns:
        RefreshToken document nếu valid và chưa expired, None nếu invalid
    """
    # Decode token trước
    payload = decode_token(token)
    if not payload or payload.get("type") != "refresh":
        return None
    
    # Tìm token trong database
    refresh_token = await RefreshToken.find_one(RefreshToken.token == token)
    
    if not refresh_token:
        return None
    
    # Kiểm tra expiry
    if refresh_token.expires_at < datetime.utcnow():
        # Token đã hết hạn, xóa khỏi database
        await refresh_token.delete()
        return None
    
    return refresh_token


# ============================================================================
# REFRESH TOKEN MANAGEMENT trong MongoDB
# ============================================================================

async def save_refresh_token(user_id: str, token: str, expires_at: datetime) -> RefreshToken:
    """
    Lưu refresh token vào MongoDB
    
    Args:
        user_id: ID của user
        token: Refresh token string
        expires_at: Thời gian hết hạn
        
    Returns:
        RefreshToken document đã lưu
    """
    refresh_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    
    await refresh_token.insert()
    return refresh_token


async def delete_refresh_token(token: str) -> bool:
    """
    Xóa refresh token khỏi database (logout)
    
    Args:
        token: Refresh token string cần xóa
        
    Returns:
        True nếu xóa thành công, False nếu không tìm thấy
    """
    refresh_token = await RefreshToken.find_one(RefreshToken.token == token)
    
    if refresh_token:
        await refresh_token.delete()
        return True
    
    return False


async def delete_all_user_tokens(user_id: str) -> int:
    """
    Xóa tất cả refresh tokens của một user (logout all devices)
    
    Args:
        user_id: ID của user
        
    Returns:
        Số lượng tokens đã xóa
    """
    tokens = await RefreshToken.find(RefreshToken.user_id == user_id).to_list()
    count = len(tokens)
    
    for token in tokens:
        await token.delete()
    
    return count


# ============================================================================
# USER AUTHENTICATION
# ============================================================================

async def authenticate_user(email: str, password: str) -> Optional[User]:
    """
    Authenticate user bằng email và password
    
    Args:
        email: Email của user
        password: Plain text password
        
    Returns:
        User document nếu authentication thành công, None nếu thất bại
    """
    user = await User.find_one(User.email == email)
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    # Kiểm tra status
    if user.status != "active":
        return None
    
    return user


async def get_current_user_from_token(token: str) -> Optional[User]:
    """
    Lấy user từ access token
    
    Args:
        token: Access token string
        
    Returns:
        User document nếu token valid, None nếu invalid
    """
    payload = decode_token(token)
    
    if not payload or payload.get("type") != "access":
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    user = await User.get(user_id)
    
    if not user or user.status != "active":
        return None
    
    return user
