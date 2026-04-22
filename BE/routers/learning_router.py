"""
Learning Router
Định nghĩa routes cho learning endpoints (modules, lessons)
Section 2.4.1-2.4.2 + Notes
6 endpoints
"""

from fastapi import APIRouter, Depends, status
from middleware.auth import get_current_user
from controllers.learning_controller import (
    handle_get_module_detail,
    handle_get_lesson_content,
    handle_get_course_modules,
    handle_get_module_outcomes,
    handle_get_module_resources,
    handle_generate_module_assessment
)
from schemas.learning import (
    ModuleDetailResponse,
    LessonContentResponse,
    CourseModulesResponse,
    ModuleOutcomesResponse,
    ModuleResourcesResponse,
    ModuleAssessmentGenerateRequest,
    ModuleAssessmentGenerateResponse
)


router = APIRouter(prefix="", tags=["Learning"])


# ============================================================================
# Section 2.4.1: XEM THÔNG TIN MODULE
# ============================================================================

@router.get(
    "/courses/{course_id}/modules/{module_id}",
    response_model=ModuleDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Xem chi tiết module",
    description="""
    Hiển thị thông tin chi tiết module:
    - Tiêu đề, mô tả, cấp độ khó
    - Danh sách lessons với trạng thái (completed/locked)
    - Learning outcomes
    - Tài nguyên đính kèm
    - Progress percent
    """
)
async def get_module_detail(
    course_id: str,
    module_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Section 2.4.1 - Xem thông tin chi tiết module"""
    return await handle_get_module_detail(course_id, module_id, current_user)


# ============================================================================
# Section 2.4.2: XEM NỘI DUNG BÀI HỌC
# ============================================================================

@router.get(
    "/courses/{course_id}/lessons/{lesson_id}",
    response_model=LessonContentResponse,
    status_code=status.HTTP_200_OK,
    summary="Xem nội dung lesson",
    description="""
    Hiển thị nội dung chi tiết lesson:
    - Nội dung text/HTML hoặc video
    - Tài liệu đính kèm (PDF, slides, code)
    - Tracking tự động (thời gian học, video progress)
    - Quiz kèm theo (nếu có)
    - Navigation (lesson trước/sau)
    - Trạng thái khóa lesson tiếp theo
    """
)
async def get_lesson_content(
    course_id: str,
    lesson_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Section 2.4.2 - Xem nội dung chi tiết lesson"""
    return await handle_get_lesson_content(course_id, lesson_id, current_user)


# ============================================================================
# ADDITIONAL ENDPOINTS (Notes)
# ============================================================================

@router.get(
    "/courses/{course_id}/modules",
    response_model=CourseModulesResponse,
    status_code=status.HTTP_200_OK,
    summary="Danh sách modules trong course",
    description="Hiển thị tất cả modules với progress và trạng thái khóa"
)
async def get_course_modules(
    course_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Lấy danh sách tất cả modules trong course"""
    return await handle_get_course_modules(course_id, current_user)


@router.get(
    "/courses/{course_id}/modules/{module_id}/outcomes",
    response_model=ModuleOutcomesResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy learning outcomes của module",
    description="Hiển thị các mục tiêu học tập và trạng thái đạt được"
)
async def get_module_outcomes(
    course_id: str,
    module_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Lấy learning outcomes của module"""
    return await handle_get_module_outcomes(course_id, module_id, current_user)


@router.get(
    "/courses/{course_id}/modules/{module_id}/resources",
    response_model=ModuleResourcesResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy tài nguyên học tập của module",
    description="Hiển thị tất cả resources (PDF, slides, code, video, links) được nhóm theo loại"
)
async def get_module_resources(
    course_id: str,
    module_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Lấy tài nguyên học tập của module"""
    return await handle_get_module_resources(course_id, module_id, current_user)


@router.post(
    "/courses/{course_id}/modules/{module_id}/assessments/generate",
    response_model=ModuleAssessmentGenerateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Sinh quiz đánh giá tự động cho module",
    description="Sử dụng AI để tạo quiz dựa trên learning outcomes và độ khó yêu cầu"
)
async def generate_module_assessment(
    course_id: str,
    module_id: str,
    request: ModuleAssessmentGenerateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Sinh quiz đánh giá tự động cho module bằng AI - returns Dict matching API_SCHEMA"""
    return await handle_generate_module_assessment(course_id, module_id, request, current_user)
