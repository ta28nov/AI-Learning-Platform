"""
Enrollment Controller - Xử lý đăng ký khóa học và quản lý enrollment
Tuân thủ: CHUCNANG.md Section 2.3.4-2.3.8, ENDPOINTS.md /enrollments/* routes

File này xử lý 4 endpoints liên quan đến đăng ký, xem danh sách và hủy đăng ký khóa học.
"""

from typing import Dict, List, Optional
from fastapi import HTTPException, status
from datetime import datetime

# Import schemas
from schemas.enrollment import (
    EnrollmentCreateRequest,
    EnrollmentCreateResponse,
    EnrollmentListItem,
    EnrollmentListResponse,
    EnrollmentSummary,
    EnrollmentDetailResponse,
    EnrollmentCancelResponse,
    NextLessonInfo
)

# Import services
from services import enrollment_service, course_service
from models.models import User, Course


# ============================================================================
# Section 2.3.4: ĐĂNG KÝ KHÓA HỌC
# ============================================================================

async def handle_enroll_course(
    request: EnrollmentCreateRequest,
    current_user: Dict
) -> EnrollmentCreateResponse:
    """
    2.3.4: Đăng ký khóa học mới
    
    User đăng ký vào một khóa học. Hệ thống sẽ:
    - Kiểm tra course tồn tại và published
    - Kiểm tra user chưa đăng ký trước đó
    - Tạo enrollment record với status="active"
    - Tăng enrollment_count của course
    
    Args:
        request: EnrollmentCreateRequest với course_id
        current_user: User hiện tại (từ middleware auth)
        
    Returns:
        EnrollmentCreateResponse với thông tin đăng ký
        
    Raises:
        HTTPException 404: Nếu course không tồn tại
        HTTPException 400: Nếu đã đăng ký rồi hoặc course chưa publish
        
    Endpoint: POST /api/v1/enrollments
    """
    user_id = current_user.get("user_id")
    course_id = request.course_id
    
    # Kiểm tra course tồn tại
    course = await course_service.get_course_by_id(course_id)
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khóa học không tồn tại"
        )
    
    # Kiểm tra course đã publish chưa
    if course.status != "published":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Khóa học chưa được công khai"
        )
    
    # Tạo enrollment
    try:
        enrollment = await enrollment_service.create_enrollment(
            user_id=user_id,
            course_id=course_id
        )
    except ValueError as e:
        # User đã đăng ký rồi
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    return EnrollmentCreateResponse(
        id=enrollment.id,
        user_id=enrollment.user_id,
        course_id=enrollment.course_id,
        course_title=course.title,
        status=enrollment.status,
        enrolled_at=enrollment.enrolled_at,
        progress_percent=enrollment.progress_percent,
        message=f"Đăng ký khóa học '{course.title}' thành công"
    )


# ============================================================================
# Section 2.3.5: DANH SÁCH KHÓA HỌC ĐÃ ĐĂNG KÝ
# ============================================================================

async def handle_list_my_enrollments(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: Dict = None
) -> EnrollmentListResponse:
    """
    2.3.5: Lấy danh sách các khóa học đã đăng ký ("My Courses")
    
    Hiển thị tất cả enrollments của user với:
    - Filter theo status (in-progress, completed, cancelled)
    - Thông tin course (title, thumbnail)
    - Tiến độ học (progress_percent)
    - Thông tin next_lesson để "Continue Learning"
    - Pagination
    
    Args:
        status: Filter theo status (tùy chọn)
        skip: Bỏ qua bao nhiêu kết quả (pagination)
        limit: Số lượng kết quả tối đa (mặc định 20)
        current_user: User hiện tại (từ middleware auth)
        
    Returns:
        EnrollmentListResponse với danh sách enrollments và summary
        
    Endpoint: GET /api/v1/enrollments/my-courses
    """
    user_id = current_user.get("user_id")
    
    # Lấy enrollments của user
    enrollments = await enrollment_service.get_user_enrollments(
        user_id=user_id,
        status=status,
        skip=skip,
        limit=limit
    )
    
    # Đếm tổng số enrollments
    all_enrollments = await enrollment_service.get_user_enrollments(
        user_id=user_id,
        status=status,
        skip=0,
        limit=10000
    )
    total = len(all_enrollments)
    
    # Chuyển đổi sang EnrollmentListItem
    enrollment_items = []
    for enrollment in enrollments:
        # Lấy course info
        course = await course_service.get_course_by_id(enrollment.course_id)
        
        if not course:
            continue  # Skip nếu course đã bị xóa
        
        # Tìm next lesson để học tiếp
        next_lesson_info = None
        if enrollment.status == "active" and hasattr(course, 'modules') and course.modules:
            # Tìm lesson đầu tiên chưa hoàn thành
            for module in course.modules:
                for lesson in module.lessons:
                    if lesson.id not in enrollment.completed_lessons:
                        next_lesson_info = NextLessonInfo(
                            lesson_id=lesson.id,
                            lesson_title=lesson.title,
                            module_title=module.title
                        )
                        break
                if next_lesson_info:
                    break
        
        enrollment_items.append(EnrollmentListItem(
            id=enrollment.id,
            course_id=enrollment.course_id,
            course_title=course.title,
            course_description=course.description or "",
            course_thumbnail=course.thumbnail_url,
            course_level=course.level,
            instructor_name=course.instructor_name or "N/A",
            status=enrollment.status,
            progress_percent=enrollment.progress_percent,
            enrolled_at=enrollment.enrolled_at,
            last_accessed_at=enrollment.last_accessed_at,
            completed_at=enrollment.completed_at,
            avg_quiz_score=enrollment.avg_quiz_score,
            total_time_spent_minutes=enrollment.total_time_spent_minutes,
            next_lesson=next_lesson_info
        ))
    
    # Tính summary
    all_enrollments_count = await enrollment_service.get_user_enrollments(
        user_id=user_id,
        status=None,
        skip=0,
        limit=10000
    )
    
    in_progress_count = sum(
        1 for e in all_enrollments_count 
        if e.status == "active"
    )
    completed_count = sum(
        1 for e in all_enrollments_count 
        if e.status == "completed"
    )
    cancelled_count = sum(
        1 for e in all_enrollments_count 
        if e.status == "cancelled"
    )
    
    summary = EnrollmentSummary(
        total_enrollments=len(all_enrollments_count),
        in_progress=in_progress_count,
        completed=completed_count,
        cancelled=cancelled_count
    )
    
    return EnrollmentListResponse(
        enrollments=enrollment_items,
        total=total,
        skip=skip,
        limit=limit,
        summary=summary
    )


# ============================================================================
# Section 2.3.6: CHI TIẾT ENROLLMENT
# ============================================================================

async def handle_get_enrollment_detail(
    enrollment_id: str,
    current_user: Dict
) -> EnrollmentDetailResponse:
    """
    2.3.6: Xem chi tiết enrollment
    
    Hiển thị thông tin đầy đủ về enrollment bao gồm:
    - Thông tin course cơ bản
    - Tiến độ chi tiết (completed_lessons, completed_modules)
    - Thống kê học tập (avg_quiz_score, total_time_spent)
    - Thông tin next_lesson
    
    Args:
        enrollment_id: ID của enrollment
        current_user: User hiện tại (từ middleware auth)
        
    Returns:
        EnrollmentDetailResponse với thông tin chi tiết
        
    Raises:
        HTTPException 404: Nếu enrollment không tồn tại
        HTTPException 403: Nếu không phải enrollment của user
        
    Endpoint: GET /api/v1/enrollments/{enrollment_id}
    """
    user_id = current_user.get("user_id")
    
    # Lấy enrollment
    enrollment = await enrollment_service.get_enrollment_by_id(enrollment_id)
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment không tồn tại"
        )
    
    # Kiểm tra quyền sở hữu
    if enrollment.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập enrollment này"
        )
    
    # Lấy course info
    course = await course_service.get_course_by_id(enrollment.course_id)
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khóa học không tồn tại"
        )
    
    # Lấy owner info
    owner = await User.get(course.owner_id)
    instructor_name = owner.full_name if owner else "Giảng viên"
    
    # Tính tổng lessons, modules
    total_modules = len(course.modules) if hasattr(course, 'modules') and course.modules else 0
    total_lessons = sum(len(module.lessons) for module in course.modules) if hasattr(course, 'modules') and course.modules else 0
    
    # Tìm next lesson
    next_lesson_info = None
    if enrollment.status == "active" and hasattr(course, 'modules') and course.modules:
        for module in course.modules:
            for lesson in module.lessons:
                if lesson.id not in enrollment.completed_lessons:
                    next_lesson_info = NextLessonInfo(
                        lesson_id=lesson.id,
                        lesson_title=lesson.title,
                        module_title=module.title
                    )
                    break
            if next_lesson_info:
                break
    
    return EnrollmentDetailResponse(
        id=enrollment.id,
        user_id=enrollment.user_id,
        course_id=enrollment.course_id,
        course_title=course.title,
        course_description=course.description or "",
        course_thumbnail=course.thumbnail_url,
        instructor_name=instructor_name,
        status=enrollment.status,
        progress_percent=enrollment.progress_percent,
        completed_lessons=len(enrollment.completed_lessons),
        total_lessons=total_lessons,
        completed_modules=len(enrollment.completed_modules),
        total_modules=total_modules,
        avg_quiz_score=enrollment.avg_quiz_score,
        enrolled_at=enrollment.enrolled_at,
        completed_at=enrollment.completed_at
    )


# ============================================================================
# Section 2.3.8: HỦY ĐĂNG KÝ KHÓA HỌC
# ============================================================================

async def handle_unenroll_course(
    enrollment_id: str,
    current_user: Dict
) -> EnrollmentCancelResponse:
    """
    2.3.8: Hủy đăng ký khóa học
    
    User hủy đăng ký khóa học. Hệ thống sẽ:
    - Kiểm tra quyền sở hữu
    - Cập nhật status thành "cancelled" (soft delete)
    - Giữ lại dữ liệu progress để user có thể tham khảo sau
    - Giảm enrollment_count của course
    
    Args:
        enrollment_id: ID của enrollment
        current_user: User hiện tại (từ middleware auth)
        
    Returns:
        EnrollmentCancelResponse với thông báo
        
    Raises:
        HTTPException 404: Nếu enrollment không tồn tại
        HTTPException 403: Nếu không phải enrollment của user
        HTTPException 400: Nếu enrollment đã cancelled rồi
        
    Endpoint: DELETE /api/v1/enrollments/{enrollment_id}
    """
    user_id = current_user.get("user_id")
    
    # Lấy enrollment
    enrollment = await enrollment_service.get_enrollment_by_id(enrollment_id)
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment không tồn tại"
        )
    
    # Kiểm tra quyền sở hữu
    if enrollment.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền hủy enrollment này"
        )
    
    # Kiểm tra đã hủy chưa
    if enrollment.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enrollment đã được hủy trước đó"
        )
    
    # Lấy course info
    course = await course_service.get_course_by_id(enrollment.course_id)
    course_title = course.title if course else "Khóa học"
    
    # Hủy enrollment
    cancelled_enrollment = await enrollment_service.cancel_enrollment(enrollment_id)
    
    if not cancelled_enrollment:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể hủy enrollment"
        )
    
    return EnrollmentCancelResponse(
        message=f"Đã hủy đăng ký khóa học '{course_title}' thành công.",
        note="Tiến độ học của bạn đã được lưu lại và có thể xem lại bất cứ lúc nào."
    )
