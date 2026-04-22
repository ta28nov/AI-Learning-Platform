"""
Quiz Router
Định nghĩa routes cho quiz endpoints
Section 2.4.3-2.4.7 (Student) + 3.3 (Instructor)
10 endpoints
"""

from fastapi import APIRouter, Depends, status, Query
from typing import Optional
from middleware.auth import get_current_user
from controllers.quiz_controller import (
    handle_get_quiz_detail,
    handle_attempt_quiz,
    handle_get_quiz_results,
    handle_retake_quiz,
    handle_generate_practice_exercises,
    handle_create_quiz,
    handle_list_quizzes_with_filters,
    handle_update_quiz,
    handle_delete_quiz,
    handle_get_class_quiz_results
)
from schemas.quiz import (
    QuizDetailResponse,
    QuizAttemptRequest,
    QuizAttemptResponse,
    QuizResultsResponse,
    QuizRetakeResponse,
    PracticeExercisesGenerateRequest,
    PracticeExercisesGenerateResponse,
    QuizCreateRequest,
    QuizCreateResponse,
    QuizListResponse,
    QuizUpdateRequest,
    QuizUpdateResponse,
    QuizDeleteResponse,
    QuizClassResultsResponse
)


router = APIRouter(prefix="", tags=["Quizzes"])


# STUDENT ENDPOINTS (2.4.3-2.4.7)

@router.get(
    "/quizzes/{quiz_id}",
    response_model=QuizDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Xem chi tiết quiz",
    description="Hiển thị thông tin quiz: câu hỏi, thời gian, số lần làm, điểm tốt nhất"
)
async def get_quiz_detail(
    quiz_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Section 2.4.3 - Xem chi tiết quiz"""
    return await handle_get_quiz_detail(quiz_id, current_user)


@router.post(
    "/quizzes/{quiz_id}/attempt",
    response_model=QuizAttemptResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Làm bài quiz",
    description="Submit câu trả lời quiz và nhận kết quả chấm điểm"
)
async def attempt_quiz(
    quiz_id: str,
    attempt_data: QuizAttemptRequest,
    current_user: dict = Depends(get_current_user)
):
    """Section 2.4.4 - Làm bài quiz"""
    return await handle_attempt_quiz(quiz_id, attempt_data, current_user)


@router.get(
    "/quizzes/{quiz_id}/results",
    response_model=QuizResultsResponse,
    status_code=status.HTTP_200_OK,
    summary="Xem kết quả quiz chi tiết",
    description="Hiển thị điểm số, câu đúng/sai, giải thích từng câu, câu bắt buộc"
)
async def get_quiz_results(
    quiz_id: str,
    attempt_id: Optional[str] = Query(None, description="ID của attempt (nếu không có lấy gần nhất)"),
    current_user: dict = Depends(get_current_user)
):
    """Section 2.4.5 - Xem kết quả quiz"""
    return await handle_get_quiz_results(quiz_id, attempt_id, current_user)


@router.post(
    "/quizzes/{quiz_id}/retake",
    response_model=QuizRetakeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Làm lại quiz",
    description="Tạo quiz mới với câu hỏi tương tự (AI-generated) cho quiz đã fail"
)
async def retake_quiz(
    quiz_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Section 2.4.6 - Làm lại quiz"""
    return await handle_retake_quiz(quiz_id, current_user)


@router.post(
    "/ai/generate-practice",
    response_model=PracticeExercisesGenerateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Sinh bài tập luyện tập AI",
    description="AI tạo bài tập practice theo chủ đề, độ khó, loại câu hỏi"
)
async def generate_practice_exercises(
    practice_request: PracticeExercisesGenerateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Section 2.4.7 - Sinh bài tập luyện tập"""
    return await handle_generate_practice_exercises(practice_request, current_user)


# INSTRUCTOR ENDPOINTS (3.3.1-3.3.5)

@router.post(
    "/lessons/{lesson_id}/quizzes",
    response_model=QuizCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo quiz mới cho lesson",
    description="Giảng viên tạo quiz: câu hỏi, đáp án, thời gian, điểm pass"
)
async def create_quiz(
    lesson_id: str,
    quiz_data: QuizCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Section 3.3.1 - Tạo quiz (Instructor)"""
    return await handle_create_quiz(lesson_id, quiz_data, current_user)


@router.get(
    "/quizzes",
    response_model=QuizListResponse,
    status_code=status.HTTP_200_OK,
    summary="Danh sách quiz với filters",
    description="Lọc quiz theo khóa học, lesson, độ khó"
)
async def list_quizzes_with_filters(
    course_id: Optional[str] = Query(None, description="UUID khóa học"),
    class_id: Optional[str] = Query(None, description="UUID lớp học"),
    search: Optional[str] = Query(None, description="Tìm kiếm trong title/description"),
    sort_by: str = Query("created_at", description="Field sort: created_at|title|pass_rate"),
    sort_order: str = Query("desc", description="asc|desc"),
    skip: int = Query(0, ge=0, description="Pagination skip"),
    limit: int = Query(20, ge=1, le=100, description="Pagination limit"),
    current_user: dict = Depends(get_current_user)
):
    """Section 3.3.2 - Danh sách quiz (Instructor)"""
    return await handle_list_quizzes_with_filters(
        course_id, class_id, search, sort_by, sort_order, skip, limit, current_user
    )


@router.put(
    "/quizzes/{quiz_id}",
    response_model=QuizUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Cập nhật quiz",
    description="Sửa câu hỏi, thời gian, điểm pass (cảnh báo nếu đã có người làm)"
)
async def update_quiz(
    quiz_id: str,
    quiz_update: QuizUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Section 3.3.3 - Cập nhật quiz (Instructor)"""
    return await handle_update_quiz(quiz_id, quiz_update, current_user)


@router.delete(
    "/quizzes/{quiz_id}",
    response_model=QuizDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Xóa quiz",
    description="Xóa quiz (chỉ được xóa nếu chưa có người làm)"
)
async def delete_quiz(
    quiz_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Section 3.3.4 - Xóa quiz (Instructor)"""
    return await handle_delete_quiz(quiz_id, current_user)


@router.get(
    "/quizzes/{quiz_id}/class-results",
    response_model=QuizClassResultsResponse,
    status_code=status.HTTP_200_OK,
    summary="Thống kê kết quả quiz của cả lớp",
    description="Phân tích: điểm trung bình, phân bố điểm, xếp hạng, câu khó nhất"
)
async def get_class_quiz_results(
    quiz_id: str,
    class_id: str = Query(..., description="UUID lớp học"),
    current_user: dict = Depends(get_current_user)
):
    """Section 3.3.5 - Thống kê kết quả lớp (Instructor)"""
    return await handle_get_class_quiz_results(quiz_id, class_id, current_user)
