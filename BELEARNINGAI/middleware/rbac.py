"""
Middleware kiểm soát truy cập dựa trên vai trò (RBAC)
Tuân thủ: CHUCNANG.md - Role-based permissions cho student/instructor/admin
Tích hợp với auth middleware để kiểm tra quyền truy cập
"""

from typing import Dict, List, Optional, Set
from fastapi import Depends, HTTPException, status
from middleware.auth import get_current_user, get_optional_user


# ============================================================================
# ROLE DEFINITIONS - Theo CHUCNANG.md Section 1.1
# ============================================================================

class Role:
    """Định nghĩa các vai trò trong hệ thống"""
    STUDENT = "student"       # Level 1 - Học tập và tự phát triển
    INSTRUCTOR = "instructor" # Level 2 - Giảng dạy và quản lý lớp học  
    ADMIN = "admin"          # Level 3 - Quản lý toàn hệ thống


# ============================================================================
# PERMISSION MAPPINGS - Theo 84 endpoints trong ENDPOINTS.md
# ============================================================================

class Permission:
    """Định nghĩa permissions cho từng endpoint group"""
    
    # Authentication & Profile (Section 2.1)
    AUTH_REGISTER = "auth:register"           # Public
    AUTH_LOGIN = "auth:login"                 # Public  
    AUTH_LOGOUT = "auth:logout"               # All authenticated
    USER_VIEW_PROFILE = "user:view_profile"   # Own profile
    USER_UPDATE_PROFILE = "user:update_profile" # Own profile
    
    # AI Assessment (Section 2.2)
    ASSESSMENT_GENERATE = "assessment:generate"    # Student
    ASSESSMENT_SUBMIT = "assessment:submit"        # Student (own)
    ASSESSMENT_VIEW_RESULTS = "assessment:view_results" # Student (own)
    
    # Course Discovery & Enrollment (Section 2.3)
    COURSE_SEARCH = "course:search"                # All authenticated
    COURSE_VIEW_PUBLIC = "course:view_public"      # All authenticated
    COURSE_VIEW_DETAIL = "course:view_detail"      # All authenticated
    COURSE_CHECK_ENROLLMENT = "course:check_enrollment" # Student (own)
    ENROLLMENT_CREATE = "enrollment:create"        # Student
    ENROLLMENT_VIEW_OWN = "enrollment:view_own"    # Student (own)
    ENROLLMENT_VIEW_DETAIL = "enrollment:view_detail" # Student (own)
    ENROLLMENT_CANCEL = "enrollment:cancel"        # Student (own)
    
    # Learning & Progress (Section 2.4)
    LEARNING_VIEW_MODULE = "learning:view_module"   # Student (enrolled)
    LEARNING_VIEW_LESSON = "learning:view_lesson"   # Student (enrolled)
    QUIZ_VIEW_DETAIL = "quiz:view_detail"          # Student (enrolled)
    QUIZ_ATTEMPT = "quiz:attempt"                  # Student (enrolled)
    QUIZ_VIEW_RESULTS = "quiz:view_results"        # Student (own attempts)
    QUIZ_RETAKE = "quiz:retake"                    # Student (own)
    PROGRESS_VIEW_COURSE = "progress:view_course"   # Student (own)
    
    # Personal Courses (Section 2.5)
    PERSONAL_COURSE_CREATE = "personal_course:create"   # Student
    PERSONAL_COURSE_VIEW_OWN = "personal_course:view_own" # Student (own)
    PERSONAL_COURSE_UPDATE = "personal_course:update"   # Student (own)
    PERSONAL_COURSE_DELETE = "personal_course:delete"   # Student (own)
    
    # AI Chat Support (Section 2.6)
    CHAT_SEND_MESSAGE = "chat:send_message"        # Student (enrolled)
    CHAT_VIEW_HISTORY = "chat:view_history"        # Student (own)
    CHAT_VIEW_CONVERSATION = "chat:view_conversation" # Student (own)
    CHAT_DELETE_CONVERSATION = "chat:delete_conversation" # Student (own)
    
    # Student Dashboard & Analytics (Section 2.7)
    DASHBOARD_STUDENT = "dashboard:student"         # Student (own)
    ANALYTICS_LEARNING_STATS = "analytics:learning_stats" # Student (own)
    ANALYTICS_PROGRESS_CHART = "analytics:progress_chart" # Student (own)
    RECOMMENDATION_VIEW = "recommendation:view"     # Student (own)
    
    # Instructor Class Management (Section 3.1-3.2)
    CLASS_CREATE = "class:create"                  # Instructor
    CLASS_VIEW_OWN = "class:view_own"             # Instructor (own classes)
    CLASS_UPDATE = "class:update"                 # Instructor (own classes)
    CLASS_DELETE = "class:delete"                 # Instructor (own classes)
    CLASS_VIEW_STUDENTS = "class:view_students"    # Instructor (own classes)
    CLASS_REMOVE_STUDENT = "class:remove_student"  # Instructor (own classes)
    CLASS_JOIN_WITH_CODE = "class:join_with_code"  # Student
    
    # Instructor Quiz Management (Section 3.3)
    QUIZ_CREATE = "quiz:create"                    # Instructor (own courses)
    QUIZ_MANAGE = "quiz:manage"                    # Instructor (own courses)
    QUIZ_VIEW_CLASS_RESULTS = "quiz:view_class_results" # Instructor (own classes)
    
    # Instructor Dashboard & Analytics (Section 3.4)
    DASHBOARD_INSTRUCTOR = "dashboard:instructor"   # Instructor (own data)
    ANALYTICS_INSTRUCTOR = "analytics:instructor"   # Instructor (own data)
    
    # Admin User Management (Section 4.1)
    ADMIN_USER_LIST = "admin:user_list"            # Admin
    ADMIN_USER_VIEW = "admin:user_view"            # Admin
    ADMIN_USER_CREATE = "admin:user_create"        # Admin
    ADMIN_USER_UPDATE = "admin:user_update"        # Admin
    ADMIN_USER_DELETE = "admin:user_delete"        # Admin
    ADMIN_USER_CHANGE_ROLE = "admin:user_change_role" # Admin
    ADMIN_USER_RESET_PASSWORD = "admin:user_reset_password" # Admin
    
    # Admin Course Management (Section 4.2)
    ADMIN_COURSE_LIST = "admin:course_list"        # Admin
    ADMIN_COURSE_VIEW = "admin:course_view"        # Admin
    ADMIN_COURSE_CREATE = "admin:course_create"    # Admin
    ADMIN_COURSE_UPDATE = "admin:course_update"    # Admin
    ADMIN_COURSE_DELETE = "admin:course_delete"    # Admin
    
    # Admin Class Monitoring (Section 4.3)
    ADMIN_CLASS_LIST = "admin:class_list"          # Admin
    ADMIN_CLASS_VIEW = "admin:class_view"          # Admin
    
    # Admin Dashboard & Analytics (Section 4.4)
    DASHBOARD_ADMIN = "dashboard:admin"            # Admin
    ANALYTICS_ADMIN = "analytics:admin"            # Admin
    
    # Universal Search (Section 5.1)
    SEARCH_GLOBAL = "search:global"                # All authenticated + guests


# ============================================================================
# ROLE-PERMISSION MAPPINGS
# ============================================================================

# Student permissions
STUDENT_PERMISSIONS = {
    # Authentication & Profile
    Permission.AUTH_LOGOUT,
    Permission.USER_VIEW_PROFILE,
    Permission.USER_UPDATE_PROFILE,
    
    # AI Assessment
    Permission.ASSESSMENT_GENERATE,
    Permission.ASSESSMENT_SUBMIT,
    Permission.ASSESSMENT_VIEW_RESULTS,
    
    # Course Discovery & Enrollment  
    Permission.COURSE_SEARCH,
    Permission.COURSE_VIEW_PUBLIC,
    Permission.COURSE_VIEW_DETAIL,
    Permission.COURSE_CHECK_ENROLLMENT,
    Permission.ENROLLMENT_CREATE,
    Permission.ENROLLMENT_VIEW_OWN,
    Permission.ENROLLMENT_VIEW_DETAIL,
    Permission.ENROLLMENT_CANCEL,
    
    # Learning & Progress
    Permission.LEARNING_VIEW_MODULE,
    Permission.LEARNING_VIEW_LESSON,
    Permission.QUIZ_VIEW_DETAIL,
    Permission.QUIZ_ATTEMPT,
    Permission.QUIZ_VIEW_RESULTS,
    Permission.QUIZ_RETAKE,
    Permission.PROGRESS_VIEW_COURSE,
    
    # Personal Courses
    Permission.PERSONAL_COURSE_CREATE,
    Permission.PERSONAL_COURSE_VIEW_OWN,
    Permission.PERSONAL_COURSE_UPDATE,
    Permission.PERSONAL_COURSE_DELETE,
    
    # AI Chat Support
    Permission.CHAT_SEND_MESSAGE,
    Permission.CHAT_VIEW_HISTORY,
    Permission.CHAT_VIEW_CONVERSATION,
    Permission.CHAT_DELETE_CONVERSATION,
    
    # Student Dashboard & Analytics
    Permission.DASHBOARD_STUDENT,
    Permission.ANALYTICS_LEARNING_STATS,
    Permission.ANALYTICS_PROGRESS_CHART,
    Permission.RECOMMENDATION_VIEW,
    
    # Class participation
    Permission.CLASS_JOIN_WITH_CODE,
    
    # Universal Search
    Permission.SEARCH_GLOBAL,
}

# Instructor permissions (includes all student permissions)
INSTRUCTOR_PERMISSIONS = STUDENT_PERMISSIONS | {
    # Class Management
    Permission.CLASS_CREATE,
    Permission.CLASS_VIEW_OWN,
    Permission.CLASS_UPDATE,
    Permission.CLASS_DELETE,
    Permission.CLASS_VIEW_STUDENTS,
    Permission.CLASS_REMOVE_STUDENT,
    
    # Quiz Management
    Permission.QUIZ_CREATE,
    Permission.QUIZ_MANAGE,
    Permission.QUIZ_VIEW_CLASS_RESULTS,
    
    # Instructor Dashboard & Analytics
    Permission.DASHBOARD_INSTRUCTOR,
    Permission.ANALYTICS_INSTRUCTOR,
}

# Admin permissions (includes all instructor permissions)
ADMIN_PERMISSIONS = INSTRUCTOR_PERMISSIONS | {
    # User Management
    Permission.ADMIN_USER_LIST,
    Permission.ADMIN_USER_VIEW,
    Permission.ADMIN_USER_CREATE,
    Permission.ADMIN_USER_UPDATE,
    Permission.ADMIN_USER_DELETE,
    Permission.ADMIN_USER_CHANGE_ROLE,
    Permission.ADMIN_USER_RESET_PASSWORD,
    
    # Course Management
    Permission.ADMIN_COURSE_LIST,
    Permission.ADMIN_COURSE_VIEW,
    Permission.ADMIN_COURSE_CREATE,
    Permission.ADMIN_COURSE_UPDATE,
    Permission.ADMIN_COURSE_DELETE,
    
    # Class Monitoring
    Permission.ADMIN_CLASS_LIST,
    Permission.ADMIN_CLASS_VIEW,
    
    # Admin Dashboard & Analytics
    Permission.DASHBOARD_ADMIN,
    Permission.ANALYTICS_ADMIN,
}

# Final role-permission mapping
ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    Role.STUDENT: STUDENT_PERMISSIONS,
    Role.INSTRUCTOR: INSTRUCTOR_PERMISSIONS,
    Role.ADMIN: ADMIN_PERMISSIONS
}


# ============================================================================
# RBAC MIDDLEWARE FUNCTIONS
# ============================================================================

async def require_role(required_role: str):
    """
    Dependency để kiểm tra user có role yêu cầu
    
    Args:
        required_role: Role cần thiết (student|instructor|admin)
        
    Returns:
        User dict nếu có đúng role
        
    Raises:
        HTTPException 403: Nếu user không có quyền
    """
    async def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        
        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Thiếu thông tin vai trò người dùng"
            )
        
        # Kiểm tra role hierarchy: admin > instructor > student
        role_hierarchy = {
            Role.STUDENT: 1,
            Role.INSTRUCTOR: 2, 
            Role.ADMIN: 3
        }
        
        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role, 999)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Yêu cầu quyền {required_role}. Bạn hiện có quyền {user_role}"
            )
        
        return current_user
    
    return role_checker


async def require_permission(permission: str):
    """
    Dependency để kiểm tra user có permission cụ thể
    
    Args:
        permission: Permission cần thiết (từ Permission class)
        
    Returns:
        User dict nếu có permission
        
    Raises:
        HTTPException 403: Nếu user không có permission
    """
    async def permission_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        
        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Thiếu thông tin vai trò người dùng"
            )
        
        # Lấy permissions của role
        user_permissions = ROLE_PERMISSIONS.get(user_role, set())
        
        if permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Không có quyền thực hiện hành động này. Yêu cầu permission: {permission}"
            )
        
        return current_user
    
    return permission_checker


async def require_any_role(allowed_roles: List[str]):
    """
    Dependency để kiểm tra user có ít nhất một trong các roles được phép
    
    Args:
        allowed_roles: Danh sách roles được phép
        
    Returns:
        User dict nếu có ít nhất một role được phép
        
    Raises:
        HTTPException 403: Nếu user không có role nào được phép
    """
    async def any_role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        
        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Thiếu thông tin vai trò người dùng"
            )
        
        if user_role not in allowed_roles:
            allowed_str = ", ".join(allowed_roles)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Yêu cầu một trong các quyền: {allowed_str}. Bạn hiện có quyền {user_role}"
            )
        
        return current_user
    
    return any_role_checker


async def require_ownership_or_admin(resource_owner_id: str):
    """
    Dependency để kiểm tra user là owner của resource hoặc là admin
    
    Args:
        resource_owner_id: ID của owner resource
        
    Returns:
        User dict nếu là owner hoặc admin
        
    Raises:
        HTTPException 403: Nếu không phải owner và không phải admin
    """
    async def ownership_checker(current_user: dict = Depends(get_current_user)):
        user_id = current_user.get("user_id")
        user_role = current_user.get("role")
        
        # Admin có thể truy cập mọi resource
        if user_role == Role.ADMIN:
            return current_user
        
        # Kiểm tra ownership
        if user_id != resource_owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn chỉ có thể truy cập tài nguyên của chính mình"
            )
        
        return current_user
    
    return ownership_checker


async def check_enrollment_access(course_id: str, user_id: str) -> bool:
    """
    Kiểm tra user có đang enrolled trong course không
    
    Args:
        course_id: ID của course
        user_id: ID của user
        
    Returns:
        bool: True nếu user enrolled hoặc là admin/instructor
        
    Note:
        Function này cần được implement trong service layer với database access
        Kiểm tra enrollment, class membership, course ownership
    """
    # Stub implementation - cần gọi service functions để check:
    # - Student: check enrollment trong course
    # - Instructor: check class ownership hoặc course creation
    # - Admin: full access
    return True  # Temporary allow all - implement proper logic


def has_permission(user_role: str, permission: str) -> bool:
    """
    Utility function để kiểm tra role có permission không
    
    Args:
        user_role: Role của user
        permission: Permission cần kiểm tra
        
    Returns:
        bool: True nếu có permission
    """
    user_permissions = ROLE_PERMISSIONS.get(user_role, set())
    return permission in user_permissions


def get_user_permissions(user_role: str) -> Set[str]:
    """
    Lấy tất cả permissions của một role
    
    Args:
        user_role: Role của user
        
    Returns:
        Set[str]: Tập hợp các permissions
    """
    return ROLE_PERMISSIONS.get(user_role, set())


# ============================================================================
# CONVENIENT ROLE DEPENDENCIES - Direct usage in routers
# ============================================================================

# Shorthand dependencies cho từng role
require_student = require_role(Role.STUDENT)
require_instructor = require_role(Role.INSTRUCTOR) 
require_admin = require_role(Role.ADMIN)

# Mixed role dependencies
require_instructor_or_admin = require_any_role([Role.INSTRUCTOR, Role.ADMIN])
require_any_authenticated = require_any_role([Role.STUDENT, Role.INSTRUCTOR, Role.ADMIN])

# Common permission dependencies
require_course_access = require_permission(Permission.COURSE_VIEW_DETAIL)
require_enrollment_management = require_permission(Permission.ENROLLMENT_CREATE)
require_quiz_management = require_permission(Permission.QUIZ_CREATE)
require_admin_access = require_permission(Permission.ADMIN_USER_LIST)