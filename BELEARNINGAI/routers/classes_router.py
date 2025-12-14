"""
Classes Router - Quản lý lớp học và học viên
Sử dụng: FastAPI, class_controller
Tuân thủ: ENDPOINTS.md Classes Router
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional
from middleware.auth import get_current_user
from schemas.classes import (
    ClassCreateRequest, ClassCreateResponse,
    ClassListResponse,
    ClassDetailResponse,
    ClassUpdateRequest,
    ClassJoinRequest, ClassJoinResponse,
    ClassStudentListResponse,
    ClassStudentDetailResponse,
    ClassProgressResponse
)
from controllers import class_controller


router = APIRouter(
    prefix="/classes",
    tags=["Classes"]
)


# ============================================================================
# Section 3.1: CLASS MANAGEMENT ENDPOINTS
# ============================================================================

@router.post(
    "",
    response_model=ClassCreateResponse,
    status_code=201,
    summary="3.1.1: Tạo lớp học mới",
    description="""
    Instructor tạo lớp học mới từ public course.
    
    **Business Logic:**
    - Auto-generate invite_code (6-8 ký tự unique)
    - Validate course_id tồn tại
    - Status khởi tạo: "preparing"
    
    **Auth:** Bearer token (Instructor)
    """
)
async def create_class(
    request: ClassCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    return await class_controller.handle_create_class(request, current_user)


@router.get(
    "/my-classes",
    response_model=ClassListResponse,
    summary="3.1.2: Danh sách lớp của instructor",
    description="""
    Xem tất cả lớp học mà instructor đã tạo.
    
    **Features:**
    - Filter theo status (preparing/active/completed)
    - Sort theo created_at DESC
    - Hiển thị student count và overall progress
    
    **Auth:** Bearer token (Instructor)
    """
)
async def list_my_classes(
    status: Optional[str] = Query(None, description="Filter theo status"),
    current_user: dict = Depends(get_current_user)
):
    return await class_controller.handle_list_my_classes(status, current_user)


@router.get(
    "/{class_id}",
    response_model=ClassDetailResponse,
    summary="3.1.3: Chi tiết lớp học",
    description="""
    Xem thông tin chi tiết lớp học và danh sách học viên.
    
    **Features:**
    - Class info với invite_code
    - Danh sách students với progress
    - Statistics: lessons completed, avg quiz score
    
    **Auth:** Bearer token (Instructor - owner only)
    """
)
async def get_class_detail(
    class_id: str,
    current_user: dict = Depends(get_current_user)
):
    return await class_controller.handle_get_class_detail(class_id, current_user)


@router.put(
    "/{class_id}",
    summary="3.1.4: Cập nhật lớp học",
    description="""
    Chỉnh sửa thông tin lớp học.
    
    **Validation:**
    - Không giảm max_students dưới current student count
    - Không thay đổi start_date nếu đã bắt đầu
    
    **Auth:** Bearer token (Instructor - owner only)
    """
)
async def update_class(
    class_id: str,
    request: ClassUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    return await class_controller.handle_update_class(class_id, request, current_user)


@router.delete(
    "/{class_id}",
    summary="3.1.5: Xóa lớp học",
    description="""
    Xóa lớp học (với điều kiện).
    
    **Conditions:**
    - Chỉ xóa nếu: no students HOẶC status="completed"
    
    **Auth:** Bearer token (Instructor - owner only)
    """
)
async def delete_class(
    class_id: str,
    current_user: dict = Depends(get_current_user)
):
    return await class_controller.handle_delete_class(class_id, current_user)


# ============================================================================
# Section 3.2: STUDENT MANAGEMENT ENDPOINTS
# ============================================================================

@router.post(
    "/join",
    response_model=ClassJoinResponse,
    summary="3.2.1: Tham gia lớp bằng mã mời",
    description="""
    Student tham gia lớp học bằng invite code.
    
    **Validation:**
    - Class status="active"
    - Chưa đầy (student_count < max_students)
    - User chưa join
    
    **Side Effect:** Auto-create Enrollment với course
    
    **Auth:** Bearer token (Student)
    """
)
async def join_class_with_code(
    request: ClassJoinRequest,
    current_user: dict = Depends(get_current_user)
):
    return await class_controller.handle_join_class_with_code(request, current_user)


@router.get(
    "/{class_id}/students",
    response_model=ClassStudentListResponse,
    summary="3.2.2: Danh sách học viên trong lớp",
    description="""
    Xem danh sách học viên với progress và quiz average.
    
    **Features:**
    - Pagination (skip/limit)
    - Hiển thị progress, completed modules, quiz average, last activity
    
    **Auth:** Bearer token (Instructor - owner only)
    """
)
async def get_class_students(
    class_id: str,
    skip: int = Query(0, ge=0, description="Pagination skip"),
    limit: int = Query(50, ge=1, le=100, description="Pagination limit"),
    current_user: dict = Depends(get_current_user)
):
    return await class_controller.handle_get_class_students(class_id, skip, limit, current_user)


@router.get(
    "/{class_id}/students/{student_id}",
    response_model=ClassStudentDetailResponse,
    summary="3.2.3: Chi tiết hồ sơ học viên",
    description="""
    Xem hồ sơ chi tiết của học viên trong lớp.
    
    **Features:**
    - Quiz scores detail
    - Progress per module
    - Study metrics
    
    **Auth:** Bearer token (Instructor - owner only)
    """
)
async def get_student_detail(
    class_id: str,
    student_id: str,
    current_user: dict = Depends(get_current_user)
):
    return await class_controller.handle_get_student_detail(class_id, student_id, current_user)


@router.delete(
    "/{class_id}/students/{student_id}",
    summary="3.2.4: Xóa học viên khỏi lớp",
    description="""
    Xóa học viên khỏi lớp (soft delete).
    
    **Side Effect:** 
    - Remove từ class.student_ids
    - Update enrollment status="removed"
    - **KEEP progress data** (không xóa học lực)
    
    **Auth:** Bearer token (Instructor - owner only)
    """
)
async def remove_student(
    class_id: str,
    student_id: str,
    current_user: dict = Depends(get_current_user)
):
    return await class_controller.handle_remove_student(class_id, student_id, current_user)


@router.get(
    "/{class_id}/progress",
    response_model=ClassProgressResponse,
    summary="3.2.5: Tiến độ tổng thể của lớp",
    description="""
    Xem analytics về tiến độ học tập của cả lớp.
    
    **Features:**
    - Score distribution histogram
    - Module completion rates
    - Most/least completed lessons
    
    **Auth:** Bearer token (Instructor - owner only)
    """
)
async def get_class_progress(
    class_id: str,
    current_user: dict = Depends(get_current_user)
):
    return await class_controller.handle_get_class_progress(class_id, current_user)
