"""
Personal Courses Controller
Xử lý requests cho personal courses endpoints
Section 2.5.1-2.5.5
"""

from typing import Dict, Optional
from fastapi import HTTPException, status, Query

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
from services import personal_courses_service


# ============================================================================
# Section 2.5.1: TẠO KHÓA HỌC TỪ AI PROMPT
# ============================================================================

async def handle_create_course_from_prompt(
    request: CourseFromPromptRequest,
    current_user: Dict
) -> CourseFromPromptResponse:
    """
    2.5.1: Tạo khóa học từ AI prompt
    
    Flow:
    1. Nhận prompt từ user
    2. Gọi AI service để sinh course structure
    3. Lưu draft vào DB
    4. Return course với modules/lessons đã sinh
    
    Args:
        request: CourseFromPromptRequest
        current_user: User hiện tại
        
    Returns:
        CourseFromPromptResponse
        
    Endpoint: POST /api/v1/courses/from-prompt
    """
    user_id = current_user.get("user_id")
    
    # Gọi service để tạo course từ AI
    try:
        course_data = await personal_courses_service.create_course_from_ai_prompt(
            user_id=user_id,
            prompt=request.prompt,
            level=request.level,
            estimated_duration_weeks=request.estimated_duration_weeks,
            language=request.language
        )
        return CourseFromPromptResponse(**course_data)
    except ValueError as e:
        # Validation errors from Pydantic
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        # Log the full error for debugging
        import traceback
        print(f"Error creating course from prompt:")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo khóa học từ AI: {str(e)}"
        )


# ============================================================================
# Section 2.5.2: TẠO KHÓA HỌC THỦ CÔNG
# ============================================================================

async def handle_create_personal_course(
    request: PersonalCourseCreateRequest,
    current_user: Dict
) -> PersonalCourseCreateResponse:
    """
    2.5.2: Tạo khóa học thủ công (empty course)
    
    Flow:
    1. Nhận thông tin cơ bản từ user
    2. Tạo course trống với status="draft"
    3. User sẽ tự thêm modules/lessons sau
    
    Args:
        request: PersonalCourseCreateRequest
        current_user: User hiện tại
        
    Returns:
        PersonalCourseCreateResponse
        
    Endpoint: POST /api/v1/courses/personal
    """
    user_id = current_user.get("user_id")
    
    course_data = await personal_courses_service.create_personal_course_manual(
        user_id=user_id,
        title=request.title,
        description=request.description,
        category=request.category,
        level=request.level,
        thumbnail_url=request.thumbnail_url,
        language=request.language
    )
    
    return PersonalCourseCreateResponse(**course_data)


# ============================================================================
# Section 2.5.3: XEM DANH SÁCH KHÓA HỌC CÁ NHÂN
# ============================================================================

async def handle_list_my_personal_courses(
    status_filter: Optional[str],
    search_query: Optional[str],
    current_user: Dict
) -> PersonalCourseListResponse:
    """
    2.5.3: Lấy danh sách khóa học cá nhân
    
    Hiển thị:
    - Chỉ khóa học do chính user tạo
    - Filter theo status (draft/published/archived)
    - Search theo tên
    - Thống kê: draft_count, published_count, archived_count
    
    Args:
        status_filter: Filter theo status
        search_query: Tìm kiếm theo tên
        current_user: User hiện tại
        
    Returns:
        PersonalCourseListResponse
        
    Endpoint: GET /api/v1/courses/my-personal?status=draft&search=python
    """
    user_id = current_user.get("user_id")
    
    courses_data = await personal_courses_service.list_my_personal_courses(
        user_id=user_id,
        status_filter=status_filter,
        search_query=search_query
    )
    
    return PersonalCourseListResponse(**courses_data)


# ============================================================================
# Section 2.5.4: CHỈNH SỬA KHÓA HỌC CÁ NHÂN
# ============================================================================

async def handle_update_personal_course(
    course_id: str,
    request: PersonalCourseUpdateRequest,
    current_user: Dict
) -> PersonalCourseUpdateResponse:
    """
    2.5.4: Cập nhật khóa học cá nhân
    
    Cho phép sửa:
    - Thông tin cơ bản (title, description, thumbnail)
    - Modules (thêm/xóa/sửa/sắp xếp)
    - Lessons trong modules
    - Learning outcomes
    - Status (draft → published)
    
    Args:
        course_id: ID khóa học
        request: PersonalCourseUpdateRequest
        current_user: User hiện tại
        
    Returns:
        PersonalCourseUpdateResponse
        
    Raises:
        403: Không phải owner
        404: Course không tồn tại
        
    Endpoint: PUT /api/v1/courses/personal/{course_id}
    """
    user_id = current_user.get("user_id")
    
    # Chuyển request thành dict để gửi vào service
    update_data = request.dict(exclude_unset=True)
    
    # Convert modules nếu có
    if "modules" in update_data and update_data["modules"]:
        modules_data = []
        for module in update_data["modules"]:
            module_dict = {
                "id": module.get("id"),
                "title": module["title"],
                "description": module["description"],
                "order": module["order"],
                "difficulty": module.get("difficulty", "Basic"),
                "estimated_hours": module.get("estimated_hours", 0),
                "learning_outcomes": module.get("learning_outcomes", []),
                "lessons": []
            }
            
            # Convert lessons
            for lesson in module.get("lessons", []):
                lesson_dict = {
                    "id": lesson.get("id"),
                    "title": lesson["title"],
                    "order": lesson["order"],
                    "content": lesson["content"],
                    "content_type": lesson.get("content_type", "text"),
                    "video_url": lesson.get("video_url"),
                    "duration_minutes": lesson.get("duration_minutes", 0),
                    "resources": lesson.get("resources", [])
                }
                module_dict["lessons"].append(lesson_dict)
            
            modules_data.append(module_dict)
        
        update_data["modules"] = modules_data
    
    # Call service
    course_data = await personal_courses_service.update_personal_course(
        user_id=user_id,
        course_id=course_id,
        update_data=update_data
    )
    
    if not course_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khóa học không tồn tại hoặc bạn không có quyền chỉnh sửa"
        )
    
    return PersonalCourseUpdateResponse(**course_data)


# ============================================================================
# Section 2.5.5: XÓA KHÓA HỌC CÁ NHÂN
# ============================================================================

async def handle_delete_personal_course(
    course_id: str,
    current_user: Dict
) -> PersonalCourseDeleteResponse:
    """
    2.5.5: Xóa khóa học cá nhân
    
    Điều kiện:
    - Chỉ owner mới được xóa
    - Xóa vĩnh viễn, không thể khôi phục
    - Tất cả modules, lessons sẽ bị xóa
    
    Args:
        course_id: ID khóa học
        current_user: User hiện tại
        
    Returns:
        PersonalCourseDeleteResponse
        
    Raises:
        403: Không phải owner
        404: Course không tồn tại
        
    Endpoint: DELETE /api/v1/courses/personal/{course_id}
    """
    user_id = current_user.get("user_id")
    
    result = await personal_courses_service.delete_personal_course(
        user_id=user_id,
        course_id=course_id
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khóa học không tồn tại hoặc bạn không có quyền xóa"
        )
    
    return PersonalCourseDeleteResponse(**result)
