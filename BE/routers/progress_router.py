"""
Progress Router
Định nghĩa routes cho progress tracking endpoints
Section 2.4.9
1 endpoint
"""

from fastapi import APIRouter, Depends, status
from middleware.auth import get_current_user
from controllers.progress_controller import handle_get_course_progress
from schemas.progress import ProgressCourseResponse


router = APIRouter(prefix="/progress", tags=["Progress"])


@router.get(
    "/course/{course_id}",
    response_model=ProgressCourseResponse,
    status_code=status.HTTP_200_OK,
    summary="Xem tiến độ học tập chi tiết",
    description="""
    Hiển thị tiến độ học tập theo course với thông tin:
    - Overall progress percent (0-100)
    - Chi tiết progress từng module và lesson
    - Thời gian học tổng (total_time_spent_minutes)
    - Thời gian ước tính còn lại (estimated_hours_remaining)
    - Streak days (học liên tục)
    - Điểm quiz trung bình (avg_quiz_score)
    """
)
async def get_course_progress(
    course_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Section 2.4.9 - Xem tiến độ học tập theo khóa học"""
    return await handle_get_course_progress(course_id, current_user)
