"""
Course Controller - Quản lý chức năng khám phá và xem khóa học, admin course management
Tuân thủ: CHUCNANG.md Section 2.3.1-2.3.3, 2.3.7, 4.2, ENDPOINTS.md /courses/* routes

File này xử lý 4 endpoints student + 5 endpoints admin liên quan course.
"""

from typing import Dict, List, Optional
from fastapi import HTTPException, status
from datetime import datetime

# Import schemas
from schemas.course import (
    CourseSearchFilters,
    CourseSearchResponse,
    CourseSearchItem,
    SearchMetadata,
    CourseListResponse,
    CourseDetailResponse,
    OwnerInfo,
    ModuleSummary,
    LessonSummary,
    CourseStatistics,
    EnrollmentInfo,
    CourseEnrollmentStatusResponse
)
from schemas.admin import (
    AdminCourseListResponse,
    AdminCourseDetailResponse,
    AdminCourseCreateRequest,
    AdminCourseCreateResponse,
    AdminCourseUpdateRequest,
    AdminCourseUpdateResponse,
    AdminDeleteCourseResponse
)

# Import services
from services import course_service, enrollment_service
from models.models import User, Course


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def _convert_course_to_search_item(
    course: Course,
    user_id: Optional[str] = None
) -> CourseSearchItem:
    """
    Helper function: Convert Course document → CourseSearchItem
    
    Args:
        course: Course document
        user_id: ID của user (để check enrollment status)
        
    Returns:
        CourseSearchItem với đầy đủ thông tin
    """
    # Kiểm tra user đã đăng ký chưa
    is_enrolled = False
    if user_id:
        enrollment = await enrollment_service.get_user_enrollment(
            user_id=user_id,
            course_id=course.id
        )
        is_enrolled = (enrollment is not None and enrollment.status != "cancelled")
    
    # Lấy owner info
    try:
        owner = await User.get(course.owner_id)
        instructor_name = owner.full_name if owner else "Giảng viên"
        instructor_avatar = owner.avatar_url if owner else None
    except Exception:
        # Nếu không tìm thấy owner, dùng denormalized data
        instructor_name = course.instructor_name or "Giảng viên"
        instructor_avatar = course.instructor_avatar
    
    # Sử dụng thông tin đã denormalized trong Course document
    # (Module và Lesson là separate collections, không embed)
    total_modules = course.total_modules
    total_lessons = course.total_lessons
    total_duration_minutes = course.total_duration_minutes
    
    return CourseSearchItem(
        id=course.id,
        title=course.title,
        description=course.description,
        category=course.category,
        level=course.level,
        thumbnail_url=course.thumbnail_url,
        total_modules=total_modules,
        total_lessons=total_lessons,
        total_duration_minutes=total_duration_minutes,
        enrollment_count=course.enrollment_count,
        avg_rating=course.avg_rating,
        instructor_name=instructor_name,
        instructor_avatar=instructor_avatar,
        is_enrolled=is_enrolled,
        created_at=course.created_at
    )


# ============================================================================
# ============================================================================
# Section 2.3.1: TÌM KIẾM KHÓA HỌC
# ============================================================================

async def handle_search_courses(
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    level: Optional[str] = None,
    skip: int = 0,
    limit: int = 12,
    current_user: Optional[Dict] = None
) -> CourseSearchResponse:
    """
    2.3.1: Tìm kiếm khóa học theo nhiều tiêu chí
    
    Chức năng tìm kiếm khóa học với nhiều filter:
    - Từ khóa: tìm trong tên khóa học và mô tả
    - Danh mục: Programming, Math, Business, etc.
    - Cấp độ: Beginner, Intermediate, Advanced
    
    Args:
        keyword: Từ khóa tìm kiếm (tùy chọn)
        category: Danh mục (tùy chọn)
        level: Cấp độ (tùy chọn)
        skip: Bỏ qua bao nhiêu kết quả (pagination)
        limit: Số lượng kết quả tối đa (mặc định 12)
        current_user: User hiện tại (từ middleware auth)
        
    Returns:
        CourseSearchResponse với danh sách courses và metadata
        
    Endpoint: GET /api/v1/courses/search
    """
    search_start = datetime.utcnow()
    
    # Lấy user_id nếu có user đăng nhập
    user_id = current_user.get("user_id") if current_user else None
    
    # Tìm kiếm courses với filters
    if keyword:
        courses = await course_service.search_courses(
            search_term=keyword,
            category=category,
            level=level,
            skip=skip,
            limit=limit
        )
        # Đếm tổng số courses matching (tối ưu - không load documents)
        total = await course_service.count_courses(
            search_term=keyword,
            category=category,
            level=level,
            status="published"
        )
    else:
        # Không có keyword, lấy danh sách courses với filter
        courses = await course_service.get_courses_list(
            category=category,
            level=level,
            status="published",  # Chỉ lấy courses đã publish
            skip=skip,
            limit=limit
        )
        # Đếm tổng số courses matching (tối ưu - không load documents)
        total = await course_service.count_courses(
            category=category,
            level=level,
            status="published"
        )
    
    # Chuyển đổi sang CourseSearchItem bằng helper function
    course_items = []
    for course in courses:
        course_item = await _convert_course_to_search_item(course, user_id)
        course_items.append(course_item)
    
    # Tính thời gian search
    search_end = datetime.utcnow()
    search_time_ms = int((search_end - search_start).total_seconds() * 1000)
    
    # Tạo metadata với filters_applied object
    metadata = SearchMetadata(
        keyword_used=keyword,
        filters_applied=CourseSearchFilters(
            category=category,
            level=level,
            duration_range=None
        ),
        search_time_ms=search_time_ms
    )
    
    return CourseSearchResponse(
        courses=course_items,
        total=total,
        skip=skip,
        limit=limit,
        search_metadata=metadata
    )


# ============================================================================
# Section 2.3.2: DANH SÁCH KHÓA HỌC CÔNG KHAI
# ============================================================================

async def handle_list_public_courses(
    category: Optional[str] = None,
    level: Optional[str] = None,
    skip: int = 0,
    limit: int = 12,
    current_user: Optional[Dict] = None
) -> CourseListResponse:
    """
    2.3.2: Lấy danh sách khóa học công khai
    
    Hiển thị tất cả khóa học đã publish (status="published")
    Hỗ trợ filter theo category và level
    
    Args:
        category: Danh mục (tùy chọn)
        level: Cấp độ (tùy chọn)
        skip: Bỏ qua bao nhiêu kết quả (pagination)
        limit: Số lượng kết quả tối đa (mặc định 12)
        current_user: User hiện tại (từ middleware auth, tùy chọn)
        
    Returns:
        CourseListResponse (alias của CourseSearchResponse)
        
    Endpoint: GET /api/v1/courses/public
    """
    search_start = datetime.utcnow()
    
    # Lấy user_id nếu có user đăng nhập
    user_id = current_user.get("user_id") if current_user else None
    
    # Lấy danh sách courses published
    courses = await course_service.get_courses_list(
        category=category,
        level=level,
        status="published",
        skip=skip,
        limit=limit
    )
    
    # Đếm tổng số courses published matching filters (tối ưu - không load documents)
    total = await course_service.count_courses(
        category=category,
        level=level,
        status="published"
    )
    
    # Chuyển đổi sang CourseSearchItem bằng helper function
    course_items = []
    for course in courses:
        course_item = await _convert_course_to_search_item(course, user_id)
        course_items.append(course_item)
    
    # Tính thời gian search
    search_end = datetime.utcnow()
    search_time_ms = int((search_end - search_start).total_seconds() * 1000)
    
    # Tạo metadata với filters_applied object
    metadata = SearchMetadata(
        keyword_used=None,
        filters_applied=CourseSearchFilters(
            category=category,
            level=level,
            duration_range=None
        ),
        search_time_ms=search_time_ms
    )
    
    return CourseListResponse(
        courses=course_items,
        total=total,
        skip=skip,
        limit=limit,
        search_metadata=metadata
    )


# ============================================================================
# Section 2.3.3: CHI TIẾT KHÓA HỌC
# ============================================================================

async def handle_get_course_detail(
    course_id: str,
    current_user: Optional[Dict] = None
) -> CourseDetailResponse:
    """
    2.3.3: Xem chi tiết khóa học
    
    Hiển thị đầy đủ thông tin khóa học bao gồm:
    - Thông tin cơ bản (title, description, category, level)
    - Thông tin giảng viên (owner)
    - Cấu trúc modules và lessons
    - Thống kê (enrollment_count, avg_rating)
    - Trạng thái đăng ký của user hiện tại
    
    Args:
        course_id: ID của khóa học
        current_user: User hiện tại (từ middleware auth, tùy chọn)
        
    Returns:
        CourseDetailResponse với đầy đủ thông tin
        
    Raises:
        HTTPException 404: Nếu course không tồn tại
        
    Endpoint: GET /api/v1/courses/{course_id}
    """
    # Lấy course
    course = await course_service.get_course_by_id(course_id)
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khóa học không tồn tại"
        )
    
    # Lấy user_id nếu có user đăng nhập
    user_id = current_user.get("user_id") if current_user else None
    
    # Kiểm tra user đã đăng ký chưa và lấy thông tin enrollment
    enrollment = None
    is_enrolled = False
    if user_id:
        enrollment = await enrollment_service.get_user_enrollment(
            user_id=user_id,
            course_id=course.id
        )
        is_enrolled = (enrollment is not None and enrollment.status != "cancelled")
    
    # Lấy owner info
    try:
        owner = await User.get(course.owner_id)
        owner_info = OwnerInfo(
            id=course.owner_id,
            name=owner.full_name if owner else "Giảng viên",
            avatar_url=owner.avatar_url if owner else None,
            role=course.owner_type
        )
    except Exception:
        owner_info = OwnerInfo(
            id=course.owner_id,
            name=course.instructor_name or "Giảng viên",
            avatar_url=course.instructor_avatar,
            role=course.owner_type
        )
    
    # Lấy modules và lessons từ collections riêng (không embedded)
    from models.models import Module, Lesson
    modules = await Module.find(Module.course_id == course.id).sort("+order").to_list()
    
    modules_summary = []
    for module in modules:
        # Lấy lessons của module này
        lessons = await Lesson.find(Lesson.module_id == module.id).sort("+order").to_list()
        
        lessons_summary = []
        for lesson in lessons:
            # Kiểm tra lesson đã hoàn thành chưa (nếu user đã đăng ký)
            is_completed = False
            if user_id and is_enrolled:
                enrollment = await enrollment_service.get_user_enrollment(
                    user_id=user_id,
                    course_id=course.id
                )
                if enrollment:
                    is_completed = lesson.id in enrollment.completed_lessons
            
            lessons_summary.append(LessonSummary(
                id=lesson.id,
                title=lesson.title,
                order=lesson.order,
                duration_minutes=lesson.duration_minutes,
                content_type=lesson.content_type,
                is_completed=is_completed
            ))
        
        modules_summary.append(ModuleSummary(
            id=module.id,
            title=module.title,
            description=module.description,
            difficulty=module.difficulty,
            estimated_hours=module.estimated_hours,
            lessons=lessons_summary
        ))
    
    # Sử dụng thông tin đã denormalized trong Course
    course_statistics = CourseStatistics(
        total_modules=course.total_modules,
        total_lessons=course.total_lessons,
        total_duration_minutes=course.total_duration_minutes,
        enrollment_count=course.enrollment_count,
        avg_rating=course.avg_rating,
        completion_rate=0.0
    )
    
    # Tạo enrollment_info object
    enrollment_info = EnrollmentInfo(
        is_enrolled=is_enrolled,
        enrollment_id=str(enrollment.id) if enrollment else None,
        enrolled_at=enrollment.enrolled_at if enrollment else None,
        progress_percent=enrollment.progress_percent if enrollment else None,
        can_access_content=is_enrolled
    )
    
    return CourseDetailResponse(
        id=course.id,
        title=course.title,
        description=course.description,
        category=course.category,
        level=course.level,
        thumbnail_url=course.thumbnail_url,
        preview_video_url=course.preview_video_url,
        language=course.language,
        status=course.status,
        owner_info=owner_info,
        modules=modules_summary,
        learning_outcomes=course.learning_outcomes,
        prerequisites=course.prerequisites,
        course_statistics=course_statistics,
        enrollment_info=enrollment_info,
        created_at=course.created_at,
        updated_at=course.updated_at
    )


# ============================================================================
# Section 2.3.7: KIỂM TRA TRẠNG THÁI ĐĂNG KÝ
# ============================================================================

async def handle_check_course_enrollment_status(
    course_id: str,
    current_user: Dict
) -> CourseEnrollmentStatusResponse:
    """
    2.3.7: Kiểm tra trạng thái đăng ký khóa học của user
    
    Endpoint này dùng để kiểm tra xem user hiện tại đã đăng ký
    khóa học chưa trước khi cho phép truy cập nội dung.
    
    Args:
        course_id: ID của khóa học
        current_user: User hiện tại (bắt buộc - từ middleware auth)
        
    Returns:
        CourseEnrollmentStatusResponse với thông tin enrollment
        
    Raises:
        HTTPException 404: Nếu course không tồn tại
        
    Endpoint: GET /api/v1/courses/{course_id}/enrollment-status
    """
    # Kiểm tra course tồn tại
    course = await course_service.get_course_by_id(course_id)
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khóa học không tồn tại"
        )
    
    # Lấy user_id
    user_id = current_user.get("user_id")
    
    # Kiểm tra enrollment
    enrollment = await enrollment_service.get_user_enrollment(
        user_id=user_id,
        course_id=course_id
    )
    
    if not enrollment or enrollment.status == "cancelled":
        # Chưa đăng ký hoặc đã hủy
        return CourseEnrollmentStatusResponse(
            is_enrolled=False,
            enrollment_id=None,
            status=None,
            can_access_content=False,
            enrolled_at=None,
            progress_percent=0.0
        )
    
    # Đã đăng ký
    return CourseEnrollmentStatusResponse(
        is_enrolled=True,
        enrollment_id=str(enrollment.id),
        status=enrollment.status,
        can_access_content=True,
        enrolled_at=enrollment.enrolled_at,
        progress_percent=enrollment.progress_percent or 0.0
    )


# ============================================================================
# ADMIN COURSE MANAGEMENT HANDLERS (Section 4.2)
# ============================================================================

async def handle_list_courses_admin(
    current_user: dict,
    author_id: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    course_type: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    skip: int = 0,
    limit: int = 50
) -> AdminCourseListResponse:
    """
    4.2.1: Xem tất cả khóa học (Admin)
    GET /api/v1/admin/courses
    
    Args:
        current_user: Admin user
        author_id, status, category, course_type: Filters
        search, sort_by, sort_order: Query params
        skip, limit: Pagination
        
    Returns:
        AdminCourseListResponse
    """
    try:
        result = await course_service.list_all_courses_admin(
            author_id=author_id,
            status=status,
            category=category,
            course_type=course_type,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=limit
        )
        
        return AdminCourseListResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy danh sách courses: {str(e)}"
        )


async def handle_get_course_detail_admin(
    course_id: str,
    current_user: dict
) -> AdminCourseDetailResponse:
    """
    4.2.2: Xem chi tiết khóa học (Admin)
    GET /api/v1/admin/courses/{course_id}
    
    Args:
        course_id: ID của course
        current_user: Admin user
        
    Returns:
        AdminCourseDetailResponse
    """
    try:
        result = await course_service.get_course_detail_admin(course_id)
        return AdminCourseDetailResponse(**result)
    
    except Exception as e:
        if "không tồn tại" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy thông tin course: {str(e)}"
        )


async def handle_create_course_admin(
    course_data: AdminCourseCreateRequest,
    current_user: dict
) -> AdminCourseCreateResponse:
    """
    4.2.3: Tạo khóa học chính thức (Admin)
    POST /api/v1/admin/courses
    
    Args:
        course_data: Thông tin course mới
        current_user: Admin user
        
    Returns:
        AdminCourseCreateResponse
    """
    try:
        admin_id = current_user.get("user_id")
        
        result = await course_service.create_course_admin(
            admin_id=admin_id,
            title=course_data.title,
            description=course_data.description,
            category=course_data.category,
            level=course_data.level,
            language=course_data.language,
            thumbnail_url=course_data.thumbnail_url,
            preview_video_url=course_data.preview_video_url,
            prerequisites=course_data.prerequisites,
            learning_outcomes=course_data.learning_outcomes,
            status=course_data.status
        )
        
        return AdminCourseCreateResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo course: {str(e)}"
        )


async def handle_update_course_admin(
    course_id: str,
    update_data: AdminCourseUpdateRequest,
    current_user: dict
) -> AdminCourseUpdateResponse:
    """
    4.2.4: Chỉnh sửa bất kỳ khóa học nào (Admin)
    PUT /api/v1/admin/courses/{course_id}
    
    Args:
        course_id: ID của course
        update_data: Thông tin cập nhật
        current_user: Admin user
        
    Returns:
        AdminCourseUpdateResponse
    """
    try:
        result = await course_service.update_course_admin(
            course_id=course_id,
            title=update_data.title,
            description=update_data.description,
            category=update_data.category,
            level=update_data.level,
            language=update_data.language,
            thumbnail_url=update_data.thumbnail_url,
            preview_video_url=update_data.preview_video_url,
            prerequisites=update_data.prerequisites,
            learning_outcomes=update_data.learning_outcomes,
            status=update_data.status
        )
        
        return AdminCourseUpdateResponse(**result)
    
    except Exception as e:
        if "không tồn tại" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi cập nhật course: {str(e)}"
        )


async def handle_delete_course_admin(
    course_id: str,
    current_user: dict
) -> AdminDeleteCourseResponse:
    """
    4.2.5: Xóa khóa học (Admin)
    DELETE /api/v1/admin/courses/{course_id}
    
    Args:
        course_id: ID của course
        current_user: Admin user
        
    Returns:
        AdminDeleteCourseResponse
    """
    try:
        result = await course_service.delete_course_admin(course_id)
        return AdminDeleteCourseResponse(**result)
    
    except Exception as e:
        if "không tồn tại" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        if "Không thể xóa" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xóa course: {str(e)}"
        )

