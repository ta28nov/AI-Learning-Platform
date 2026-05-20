"""
Auth Service - Xử lý authentication và authorization
Sử dụng: bcrypt (passlib), JWT (python-jose), MongoDB (Beanie)
Tuân thủ: CHUCNANG.md Section 2.1 (Login/Register/Token Management)
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from config.config import get_settings
from models.models import User, RefreshToken, PasswordResetTokenDocument, EmailVerificationTokenDocument

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
        User document nếu authentication thành công
        
    Raises:
        ValueError: Nếu tài khoản bị khóa/inactive (FE cần hiển thị lý do cụ thể)
        Returns None nếu sai email/password
    """
    user = await User.find_one(User.email == email)
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    # Phân biệt rõ lý do thất bại để FE hiển thị đúng message
    if user.status == "inactive":
        raise ValueError("Tài khoản đã bị vô hiệu hóa")
    if user.status == "suspended":
        raise ValueError("Tài khoản đã bị tạm khóa")
    if user.status == "deleted":
        raise ValueError("Tài khoản đã bị xóa")
    if user.status != "active":
        raise ValueError(f"Tài khoản không hoạt động (status: {user.status})")
    
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


# ============================================================================
# PASSWORD RESET (forgot / reset)
# ============================================================================

async def request_password_reset(email: str) -> Dict[str, Any]:
    """
    Tạo token reset (1 giờ). Luôn trả message chung — không lộ email có tồn tại hay không.
    """
    message = "Nếu email tồn tại trong hệ thống, bạn sẽ nhận hướng dẫn đặt lại mật khẩu."
    user = await User.find_one(User.email == email)
    if not user:
        return {"message": message}

    await PasswordResetTokenDocument.find(
        PasswordResetTokenDocument.user_id == user.id,
        PasswordResetTokenDocument.used == False,
    ).update({"$set": {"used": True}})

    token = secrets.token_urlsafe(32)
    doc = PasswordResetTokenDocument(
        user_id=user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=1),
        used=False,
    )
    await doc.insert()

    result: Dict[str, Any] = {"message": message}
    if settings.testing:
        result["reset_token"] = token
    return result


async def reset_password_with_token(token: str, new_password: str) -> Dict[str, str]:
    """Đổi mật khẩu bằng token; vô hiệu refresh tokens."""
    doc = await PasswordResetTokenDocument.find_one(
        PasswordResetTokenDocument.token == token,
        PasswordResetTokenDocument.used == False,
    )
    if not doc or doc.expires_at < datetime.utcnow():
        raise ValueError("Token không hợp lệ hoặc đã hết hạn")

    user = await User.get(doc.user_id)
    if not user:
        raise ValueError("Token không hợp lệ")

    user.hashed_password = hash_password(new_password)
    user.updated_at = datetime.utcnow()
    await user.save()

    doc.used = True
    await doc.save()
    await delete_all_user_tokens(user.id)

    return {"message": "Đặt lại mật khẩu thành công"}


# ============================================================================
# EMAIL VERIFICATION
# ============================================================================

async def issue_email_verification(user_id: str) -> Optional[str]:
    """Tạo token xác thực (24h). Trả token khi TESTING để pytest/E2E."""
    user = await User.get(user_id)
    if not user or user.email_verified:
        return None

    await EmailVerificationTokenDocument.find(
        EmailVerificationTokenDocument.user_id == user_id,
        EmailVerificationTokenDocument.used == False,
    ).update({"$set": {"used": True}})

    token = secrets.token_urlsafe(32)
    doc = EmailVerificationTokenDocument(
        user_id=user_id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=24),
        used=False,
    )
    await doc.insert()
    return token if settings.testing else None


async def request_email_verification(email: str) -> Dict[str, Any]:
    """Gửi lại link xác thực — message chung, không lộ email."""
    message = "Nếu email tồn tại và chưa xác thực, bạn sẽ nhận link xác thực."
    user = await User.find_one(User.email == email)
    if not user or user.email_verified:
        return {"message": message}

    token = await issue_email_verification(user.id)
    result: Dict[str, Any] = {"message": message}
    if settings.testing and token:
        result["verification_token"] = token
    return result


async def verify_email_with_token(token: str) -> Dict[str, Any]:
    doc = await EmailVerificationTokenDocument.find_one(
        EmailVerificationTokenDocument.token == token,
        EmailVerificationTokenDocument.used == False,
    )
    if not doc or doc.expires_at < datetime.utcnow():
        raise ValueError("Token không hợp lệ hoặc đã hết hạn")

    user = await User.get(doc.user_id)
    if not user:
        raise ValueError("Token không hợp lệ")

    user.email_verified = True
    user.updated_at = datetime.utcnow()
    await user.save()

    doc.used = True
    await doc.save()

    return {"message": "Xác thực email thành công", "email_verified": True}
