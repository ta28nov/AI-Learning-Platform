"""
Enrollments Router - Định nghĩa API endpoints cho đăng ký khóa học
Tuân thủ: CHUCNANG.md Section 2.3.4-2.3.8, ENDPOINTS.md

Router này đăng ký 4 endpoints:
- POST /api/v1/enrollments - Đăng ký khóa học
- GET /api/v1/enrollments/my-courses - Danh sách khóa học đã đăng ký
- GET /api/v1/enrollments/{enrollment_id} - Chi tiết enrollment
- DELETE /api/v1/enrollments/{enrollment_id} - Hủy đăng ký
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from schemas.enrollment import (
    EnrollmentCreateRequest,
    EnrollmentCreateResponse,
    EnrollmentListResponse,
    EnrollmentDetailResponse,
    EnrollmentCancelResponse
)
from controllers.enrollment_controller import (
    handle_enroll_course,
    handle_list_my_enrollments,
    handle_get_enrollment_detail,
    handle_unenroll_course
)
from middleware.auth import get_current_user


# Khởi tạo router với prefix
router = APIRouter(
    prefix="/enrollments",
    tags=["Enrollments - Đăng ký khóa học"]
)


# ============================================================================
# POST /api/v1/enrollments - ĐĂNG KÝ KHÓA HỌC
# ============================================================================

@router.post(
    "",
    response_model=EnrollmentCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký khóa học mới",
    description="""
    User đăng ký vào một khóa học.
    
    **Yêu cầu:** Đăng nhập
    
    **Request body:**
    - course_id: ID của khóa học muốn đăng ký
    
    **Kiểm tra:**
    - Course tồn tại và đã publish
    - User chưa đăng ký trước đó
    
    **Kết quả:**
    - Tạo enrollment record với status='active'
    - Tăng enrollment_count của course
    - Trả về thông tin enrollment
    
    **Lỗi:**
    - 404: Course không tồn tại
    - 400: Đã đăng ký rồi hoặc course chưa publish
    """
)
async def enroll_course(
    request: EnrollmentCreateRequest,
    current_user: dict = Depends(get_current_user)
) -> EnrollmentCreateResponse:
    """
    Endpoint đăng ký khóa học
    Section 2.3.4
    """
    return await handle_enroll_course(
        request=request,
        current_user=current_user
    )


# ============================================================================
# GET /api/v1/enrollments/my-courses - DANH SÁCH KHÓA HỌC ĐÃ ĐĂNG KÝ
# ============================================================================

@router.get(
    "/my-courses",
    response_model=EnrollmentListResponse,
    summary="Lấy danh sách khóa học đã đăng ký (My Courses)",
    description="""
    Lấy tất cả khóa học mà user đã đăng ký.
    
    **Yêu cầu:** Đăng nhập
    
    **Filters hỗ trợ:**
    - status: Lọc theo trạng thái
      * active (hoặc in-progress): Đang học
      * completed: Đã hoàn thành
      * cancelled: Đã hủy
    
    **Pagination:**
    - skip: Bỏ qua bao nhiêu kết quả
    - limit: Số lượng kết quả tối đa (mặc định 20)
    
    **Trả về:**
    - Danh sách enrollments với thông tin course
    - Tiến độ học (progress_percent)
    - Thông tin next_lesson để "Continue Learning"
    - Summary: tổng số enrollments, in-progress, completed, cancelled
    
    **Sử dụng:**
    - Hiển thị trang "My Courses" của user
    - Theo dõi tiến độ học tập
    """
)
async def list_my_enrollments(
    status: Optional[str] = Query(None, description="Filter theo status: active, completed, cancelled"),
    skip: int = Query(0, ge=0, description="Bỏ qua bao nhiêu kết quả"),
    limit: int = Query(20, ge=1, le=100, description="Số lượng kết quả tối đa"),
    current_user: dict = Depends(get_current_user)
) -> EnrollmentListResponse:
    """
    Endpoint lấy danh sách enrollments của user
    Section 2.3.5
    """
    return await handle_list_my_enrollments(
        status=status,
        skip=skip,
        limit=limit,
        current_user=current_user
    )


# ============================================================================
# GET /api/v1/enrollments/{enrollment_id} - CHI TIẾT ENROLLMENT
# ============================================================================

@router.get(
    "/{enrollment_id}",
    response_model=EnrollmentDetailResponse,
    summary="Xem chi tiết enrollment",
    description="""
    Lấy thông tin chi tiết về một enrollment.
    
    **Yêu cầu:** Đăng nhập và là chủ sở hữu enrollment
    
    **Thông tin bao gồm:**
    - Thông tin course cơ bản
    - Tiến độ chi tiết:
      * Số lessons đã hoàn thành / tổng số lessons
      * Số modules đã hoàn thành / tổng số modules
      * % tiến độ tổng thể
    - Thống kê học tập:
      * Điểm trung bình các quiz
      * Tổng thời gian học (phút)
    - Thông tin next_lesson để tiếp tục học
    - Timestamps: enrolled_at, last_accessed_at, completed_at
    
    **Lỗi:**
    - 404: Enrollment không tồn tại
    - 403: Không phải enrollment của user hiện tại
    """
)
async def get_enrollment_detail(
    enrollment_id: str,
    current_user: dict = Depends(get_current_user)
) -> EnrollmentDetailResponse:
    """
    Endpoint lấy chi tiết enrollment
    Section 2.3.6
    """
    return await handle_get_enrollment_detail(
        enrollment_id=enrollment_id,
        current_user=current_user
    )


# ============================================================================
# DELETE /api/v1/enrollments/{enrollment_id} - HỦY ĐĂNG KÝ
# ============================================================================

@router.delete(
    "/{enrollment_id}",
    response_model=EnrollmentCancelResponse,
    summary="Hủy đăng ký khóa học",
    description="""
    User hủy đăng ký một khóa học.
    
    **Yêu cầu:** Đăng nhập và là chủ sở hữu enrollment
    
    **Xử lý:**
    - Cập nhật status thành 'cancelled' (soft delete)
    - Giữ lại toàn bộ dữ liệu progress để user có thể tham khảo sau
    - Giảm enrollment_count của course
    
    **Lưu ý:**
    - Không xóa vĩnh viễn enrollment record
    - User có thể xem lại tiến độ cũ trong lịch sử
    - Nếu muốn đăng ký lại, cần tạo enrollment mới
    
    **Trả về:**
    - Thông báo hủy thành công
    - Xác nhận dữ liệu progress đã được bảo toàn
    
    **Lỗi:**
    - 404: Enrollment không tồn tại
    - 403: Không phải enrollment của user hiện tại
    - 400: Enrollment đã cancelled rồi
    """
)
async def unenroll_course(
    enrollment_id: str,
    current_user: dict = Depends(get_current_user)
) -> EnrollmentCancelResponse:
    """
    Endpoint hủy đăng ký khóa học
    Section 2.3.8
    """
    return await handle_unenroll_course(
        enrollment_id=enrollment_id,
        current_user=current_user
    )
