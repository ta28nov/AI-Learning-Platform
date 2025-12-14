"""
Middleware xác thực JWT
Tuân thủ: CHUCNANG.md Section 2.1.2-2.1.3 (Authentication flow)
"""

from typing import Optional, Dict
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from utils.security import decode_token

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, str]:
    """
    Xác thực người dùng từ JWT access token trong Authorization header
    
    Args:
        credentials: Bearer token từ header Authorization
        
    Returns:
        dict: User payload chứa user_id (từ "sub"), email, role
        
    Raises:
        HTTPException 401: Token không hợp lệ, hết hạn, hoặc thiếu
        
    Theo CHUCNANG.md Section 2.1.2:
    - Access token có thời hạn 15 phút
    - Token type phải là "access" (không phải "refresh")
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Thiếu token xác thực",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        token = credentials.credentials
        payload = decode_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token không hợp lệ hoặc đã hết hạn",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Kiểm tra token type phải là "access"
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token type không hợp lệ",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Lấy user_id từ "sub" claim
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token thiếu thông tin user",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Trả về user info để sử dụng trong các handler
        return {
            "user_id": user_id,
            "email": payload.get("email"),
            "role": payload.get("role")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token không hợp lệ: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[Dict[str, str]]:
    """
    Xác thực người dùng từ JWT token (tùy chọn)
    
    Hàm này tương tự get_current_user nhưng không bắt buộc token.
    Nếu có token hợp lệ, trả về user info.
    Nếu không có token hoặc token không hợp lệ, trả về None.
    
    Args:
        credentials: Bearer token từ header Authorization (tùy chọn)
        
    Returns:
        dict: User payload chứa user_id, email, role nếu token hợp lệ
        None: Nếu không có token hoặc token không hợp lệ
        
    Usage:
        Dùng cho các endpoint có thể truy cập cả khi đăng nhập và không đăng nhập,
        nhưng có chức năng khác nhau tùy trạng thái (ví dụ: hiển thị is_enrolled)
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_token(token)
        
        if not payload:
            return None
        
        # Kiểm tra token type phải là "access"
        if payload.get("type") != "access":
            return None
        
        # Lấy user_id từ "sub" claim
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        # Trả về user info
        return {
            "user_id": user_id,
            "email": payload.get("email"),
            "role": payload.get("role")
        }
        
    except Exception:
        # Bỏ qua lỗi, trả về None
        return None


async def require_role(required_role: str):
    """
    Dependency để kiểm tra role của user
    
    Args:
        required_role: Role yêu cầu (student, instructor, admin)
        
    Returns:
        Function dependency để check role
        
    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_role("admin"))])
    """
    async def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        
        if user_role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Yêu cầu quyền {required_role}"
            )
        
        return current_user
    
    return role_checker


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[Dict[str, str]]:
    """
    Xác thực user tùy chọn - không throw error nếu không có token
    Dùng cho endpoints có thể access bởi cả guest và logged-in users
    
    Args:
        credentials: Bearer token tùy chọn từ header Authorization
        
    Returns:
        dict: User payload nếu có token hợp lệ, None nếu không có token
        
    Usage:
        - Universal search: guest có thể search nhưng logged-in users có thêm features
        - Public content: guest xem được basic, members xem được advanced
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_token(token)
        
        if not payload:
            return None
        
        # Validate token type
        if payload.get("type") != "access":
            return None
        
        # Extract user info
        user_data = {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "role": payload.get("role"),
            "full_name": payload.get("full_name", "")
        }
        
        # Validate required fields
        if not user_data["user_id"] or not user_data["email"]:
            return None
            
        return user_data
        
    except Exception:
        # Return None for any token errors instead of raising exception
        return None
