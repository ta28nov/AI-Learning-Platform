"""
Courses Router - Định nghĩa API endpoints cho khám phá khóa học
Tuân thủ: CHUCNANG.md Section 2.3.1-2.3.3, 2.3.7, ENDPOINTS.md

Router này đăng ký 4 endpoints:
- GET /api/v1/courses/search - Tìm kiếm khóa học
- GET /api/v1/courses/public - Danh sách khóa học công khai
- GET /api/v1/courses/{course_id} - Chi tiết khóa học
- GET /api/v1/courses/{course_id}/enrollment-status - Kiểm tra trạng thái đăng ký
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from schemas.course import (
    CourseSearchResponse,
    CourseListResponse,
    CourseDetailResponse,
    CourseEnrollmentStatusResponse
)
from controllers.course_controller import (
    handle_search_courses,
    handle_list_public_courses,
    handle_get_course_detail,
    handle_check_course_enrollment_status
)
from middleware.auth import get_current_user, get_optional_user


# Khởi tạo router với prefix
router = APIRouter(
    prefix="/courses",
    tags=["Courses - Khám phá khóa học"]
)


# ============================================================================
# GET /api/v1/courses/search - TÌM KIẾM KHÓA HỌC
# ============================================================================

@router.get(
    "/search",
    response_model=CourseSearchResponse,
    summary="Tìm kiếm khóa học",
    description="""
    Tìm kiếm khóa học theo từ khóa và filters.
    
    **Filters hỗ trợ:**
    - keyword: Tìm trong title và description
    - category: Programming, Math, Business, Languages
    - level: Beginner, Intermediate, Advanced
    
    **Pagination:**
    - skip: Bỏ qua bao nhiêu kết quả
    - limit: Số lượng kết quả tối đa (mặc định 12)
    
    **Trả về:**
    - Danh sách courses matching filters
    - Metadata: thời gian search, tổng số kết quả, filters applied
    - is_enrolled: true nếu user hiện tại đã đăng ký (yêu cầu đăng nhập)
    """
)
async def search_courses(
    keyword: Optional[str] = Query(None, description="Từ khóa tìm kiếm"),
    category: Optional[str] = Query(None, description="Danh mục: Programming, Math, Business, Languages"),
    level: Optional[str] = Query(None, description="Cấp độ: Beginner, Intermediate, Advanced"),
    skip: int = Query(0, ge=0, description="Bỏ qua bao nhiêu kết quả"),
    limit: int = Query(12, ge=1, le=50, description="Số lượng kết quả tối đa"),
    current_user: Optional[dict] = Depends(get_optional_user)
) -> CourseSearchResponse:
    """
    Endpoint tìm kiếm khóa học với filters
    Section 2.3.1
    """
    return await handle_search_courses(
        keyword=keyword,
        category=category,
        level=level,
        skip=skip,
        limit=limit,
        current_user=current_user
    )


# ============================================================================
# GET /api/v1/courses/public - DANH SÁCH KHÓA HỌC CÔNG KHAI
# ============================================================================

@router.get(
    "/public",
    response_model=CourseListResponse,
    summary="Lấy danh sách khóa học công khai",
    description="""
    Lấy tất cả khóa học đã publish (status='published').
    
    **Filters hỗ trợ:**
    - category: Lọc theo danh mục
    - level: Lọc theo cấp độ
    
    **Pagination:**
    - skip: Bỏ qua bao nhiêu kết quả
    - limit: Số lượng kết quả tối đa (mặc định 12)
    
    **Trả về:**
    - Danh sách courses đã publish
    - Metadata: thời gian search, tổng số kết quả
    - is_enrolled: true nếu user hiện tại đã đăng ký (yêu cầu đăng nhập)
    """
)
async def list_public_courses(
    category: Optional[str] = Query(None, description="Danh mục: Programming, Math, Business, Languages"),
    level: Optional[str] = Query(None, description="Cấp độ: Beginner, Intermediate, Advanced"),
    skip: int = Query(0, ge=0, description="Bỏ qua bao nhiêu kết quả"),
    limit: int = Query(12, ge=1, le=50, description="Số lượng kết quả tối đa"),
    current_user: Optional[dict] = Depends(get_optional_user)
) -> CourseListResponse:
    """
    Endpoint lấy danh sách courses public
    Section 2.3.2
    """
    return await handle_list_public_courses(
        category=category,
        level=level,
        skip=skip,
        limit=limit,
        current_user=current_user
    )


# ============================================================================
# GET /api/v1/courses/{course_id} - CHI TIẾT KHÓA HỌC
# ============================================================================

@router.get(
    "/{course_id}",
    response_model=CourseDetailResponse,
    summary="Xem chi tiết khóa học",
    description="""
    Lấy thông tin chi tiết của một khóa học.
    
    **Thông tin bao gồm:**
    - Thông tin cơ bản: title, description, category, level
    - Thông tin giảng viên: name, avatar
    - Cấu trúc khóa học: modules và lessons
    - Thống kê: enrollment_count, avg_rating, completion_rate
    - is_enrolled: trạng thái đăng ký của user hiện tại
    - is_completed: trạng thái hoàn thành của từng lesson (nếu đã đăng ký)
    
    **Lưu ý:**
    - Không yêu cầu đăng nhập để xem
    - Nếu đăng nhập, sẽ hiển thị thêm progress information
    """
)
async def get_course_detail(
    course_id: str,
    current_user: Optional[dict] = Depends(get_optional_user)
) -> CourseDetailResponse:
    """
    Endpoint lấy chi tiết course
    Section 2.3.3
    """
    return await handle_get_course_detail(
        course_id=course_id,
        current_user=current_user
    )


# ============================================================================
# GET /api/v1/courses/{course_id}/enrollment-status - KIỂM TRA ĐĂNG KÝ
# ============================================================================

@router.get(
    "/{course_id}/enrollment-status",
    response_model=CourseEnrollmentStatusResponse,
    summary="Kiểm tra trạng thái đăng ký khóa học",
    description="""
    Kiểm tra xem user hiện tại đã đăng ký khóa học chưa.
    
    **Yêu cầu:** Đăng nhập
    
    **Trả về:**
    - is_enrolled: true nếu đã đăng ký và status != 'cancelled'
    - enrollment_id: ID của enrollment (nếu có)
    - status: active, completed, hoặc cancelled
    - progress_percent: Tiến độ học (0-100)
    - can_access_content: true nếu được phép truy cập nội dung
    
    **Sử dụng:**
    Endpoint này được gọi trước khi cho phép user truy cập
    nội dung lesson/module để kiểm tra quyền.
    """
)
async def check_course_enrollment_status(
    course_id: str,
    current_user: dict = Depends(get_current_user)
) -> CourseEnrollmentStatusResponse:
    """
    Endpoint kiểm tra enrollment status
    Section 2.3.7
    """
    return await handle_check_course_enrollment_status(
        course_id=course_id,
        current_user=current_user
    )
