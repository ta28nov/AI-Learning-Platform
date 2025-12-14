"""
Personal Courses Router
Định nghĩa routes cho personal courses endpoints
Section 2.5.1-2.5.5
5 endpoints
"""

from fastapi import APIRouter, Depends, status, Query
from typing import Optional
from middleware.auth import get_current_user
from controllers.personal_courses_controller import (
    handle_create_course_from_prompt,
    handle_create_personal_course,
    handle_list_my_personal_courses,
    handle_update_personal_course,
    handle_delete_personal_course
)
from schemas.personal_courses import (
    CourseFromPromptRequest,
    CourseFromPromptResponse,
    PersonalCourseCreateRequest,
    PersonalCourseCreateResponse,
    PersonalCourseListResponse,
    PersonalCourseUpdateRequest,
    PersonalCourseUpdateResponse,
    PersonalCourseDeleteResponse
)


router = APIRouter(prefix="/courses", tags=["Personal Courses"])


# ============================================================================
# Section 2.5.1: TẠO KHÓA HỌC TỪ AI PROMPT
# ============================================================================

@router.post(
    "/from-prompt",
    response_model=CourseFromPromptResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo khóa học từ AI prompt",
    description="""
    Học viên nhập mô tả bằng ngôn ngữ tự nhiên, AI sẽ tự động sinh:
    - Modules với thứ tự logic
    - Lessons cho mỗi module
    - Learning outcomes
    - Nội dung cơ bản
    
    Khóa học được tạo với status="draft", có thể chỉnh sửa sau.
    """
)
async def create_course_from_prompt(
    request: CourseFromPromptRequest,
    current_user: dict = Depends(get_current_user)
):
    """Section 2.5.1 - Tạo khóa học từ AI prompt"""
    return await handle_create_course_from_prompt(request, current_user)


# ============================================================================
# Section 2.5.2: TẠO KHÓA HỌC THỦ CÔNG
# ============================================================================

@router.post(
    "/personal",
    response_model=PersonalCourseCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo khóa học thủ công",
    description="""
    Tạo khóa học từ đầu với thông tin cơ bản:
    - Nhập title, description, category, level
    - Hệ thống tạo course trống với status="draft"
    - User tự thêm modules và lessons sau
    
    Phù hợp cho người muốn kiểm soát hoàn toàn nội dung.
    """
)
async def create_personal_course(
    request: PersonalCourseCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Section 2.5.2 - Tạo khóa học thủ công"""
    return await handle_create_personal_course(request, current_user)


# ============================================================================
# Section 2.5.3: XEM DANH SÁCH KHÓA HỌC CÁ NHÂN
# ============================================================================

@router.get(
    "/my-personal",
    response_model=PersonalCourseListResponse,
    status_code=status.HTTP_200_OK,
    summary="Danh sách khóa học cá nhân",
    description="""
    Hiển thị tất cả khóa học do học viên tạo:
    - Chỉ hiển thị cho người tạo và Admin
    - Filter theo status (draft/published/archived)
    - Search theo tên
    - Thống kê: số modules/lessons, thời lượng
    """
)
async def list_my_personal_courses(
    status: Optional[str] = Query(None, description="Filter theo status: draft|published|archived"),
    search: Optional[str] = Query(None, description="Tìm kiếm theo tên khóa học"),
    current_user: dict = Depends(get_current_user)
):
    """Section 2.5.3 - Xem danh sách khóa học cá nhân"""
    return await handle_list_my_personal_courses(status, search, current_user)


# ============================================================================
# Section 2.5.4: CHỈNH SỬA KHÓA HỌC CÁ NHÂN
# ============================================================================

@router.put(
    "/personal/{course_id}",
    response_model=PersonalCourseUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Chỉnh sửa khóa học cá nhân",
    description="""
    Sửa đổi mọi thành phần của khóa học:
    - Thông tin cơ bản (title, description, thumbnail)
    - Thêm/xóa/sắp xếp modules
    - Thêm/xóa/chỉnh sửa lessons
    - Cập nhật learning outcomes
    - Thay đổi status (draft → published)
    
    Auto-save: Mọi thay đổi được tự động lưu.
    """
)
async def update_personal_course(
    course_id: str,
    request: PersonalCourseUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Section 2.5.4 - Chỉnh sửa khóa học cá nhân"""
    return await handle_update_personal_course(course_id, request, current_user)


# ============================================================================
# Section 2.5.5: XÓA KHÓA HỌC CÁ NHÂN
# ============================================================================

@router.delete(
    "/personal/{course_id}",
    response_model=PersonalCourseDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Xóa khóa học cá nhân",
    description="""
    Xóa vĩnh viễn khóa học:
    - Chỉ owner mới được xóa
    - Tất cả modules, lessons sẽ bị xóa
    - Không thể khôi phục
    
    Cảnh báo sẽ hiển thị trước khi xóa.
    """
)
async def delete_personal_course(
    course_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Section 2.5.5 - Xóa khóa học cá nhân"""
    return await handle_delete_personal_course(course_id, current_user)
