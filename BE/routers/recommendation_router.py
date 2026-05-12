"""
Recommendation Router
Định nghĩa routes cho AI recommendation endpoints
Section 2.2.4, 2.7.4
2 endpoints
"""

from fastapi import APIRouter, Depends, status, Query
from middleware.auth import get_current_user
from controllers.recommendation_controller import (
    handle_get_assessment_recommendations,
    handle_get_recommendations
)
from schemas.recommendation import (
    AssessmentRecommendationResponse,
    RecommendationResponse
)


router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get(
    "/from-assessment",
    response_model=AssessmentRecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Đề xuất lộ trình học tập từ đánh giá năng lực",
    description="AI sinh lộ trình cá nhân hóa dựa trên kết quả assessment: courses ưu tiên, thứ tự học, bài tập practice"
)
async def get_assessment_recommendations(
    session_id: str = Query(..., description="UUID phiên đánh giá năng lực"),
    current_user: dict = Depends(get_current_user)
):
    """Section 2.2.4 - Đề xuất lộ trình từ assessment"""
    return await handle_get_assessment_recommendations(session_id, current_user)


@router.get(
    "",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Đề xuất khóa học chung",
    description="AI đề xuất khóa học dựa trên lịch sử học tập và sở thích"
)
async def get_recommendations(
    current_user: dict = Depends(get_current_user)
):
    """Section 2.7.4 - Đề xuất khóa học tổng quan"""
    return await handle_get_recommendations(current_user)

