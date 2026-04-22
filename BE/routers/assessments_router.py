"""
Assessments Router - Định nghĩa routes cho assessment endpoints
Tuân thủ: ENDPOINTS.md Assessment Router, API_SCHEMA.md Section 2
Version: 2.0 - Khớp với assessment_controller.py (Version 2.0)
"""

from fastapi import APIRouter, Depends, status
from typing import Dict
from schemas.assessment import (
    AssessmentGenerateRequest,
    AssessmentGenerateResponse,
    AssessmentSubmitRequest,
    AssessmentSubmitResponse,
    AssessmentResultsResponse
)
from controllers.assessment_controller import (
    handle_generate_assessment,
    handle_submit_assessment,
    handle_get_assessment_results
)
from middleware.auth import get_current_user


router = APIRouter(prefix="/assessments", tags=["Assessments - AI Dynamic Assessment"])


@router.post(
    "/generate",
    response_model=AssessmentGenerateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Sinh bộ câu hỏi đánh giá năng lực",
    description="""
    Tạo phiên đánh giá năng lực mới với câu hỏi được AI tự động sinh ra.
    
    **Phân bổ số lượng theo mức độ:**
    - **Beginner**: 15 câu (3 easy + 8 medium + 4 hard) - 15 phút
    - **Intermediate**: 25 câu (5 easy + 13 medium + 7 hard) - 22 phút
    - **Advanced**: 35 câu (7 easy + 18 medium + 10 hard) - 30 phút
    
    **Cơ chế:** Google Gemini API sinh câu hỏi bám sát nội dung khóa học có sẵn trong hệ thống.
    Mỗi lần làm bài sẽ có bộ câu hỏi khác nhau (không dùng ngân hàng câu hỏi).
    
    **Section:** 2.2.1 - CHUCNANG.md
    """
)
async def generate_assessment(
    request: AssessmentGenerateRequest,
    current_user: Dict = Depends(get_current_user)
) -> AssessmentGenerateResponse:
    """
    Endpoint: POST /api/v1/assessments/generate
    Controller: handle_generate_assessment
    """
    return await handle_generate_assessment(request, current_user)


@router.post(
    "/{session_id}/submit",
    response_model=AssessmentSubmitResponse,
    status_code=status.HTTP_200_OK,
    summary="Nộp bài đánh giá năng lực",
    description="""
    Gửi câu trả lời lên hệ thống để AI tự động chấm điểm.
    
    **Thuật toán tính điểm có trọng số:**
    - Câu dễ (Easy): 1 điểm
    - Câu trung bình (Medium): 2 điểm
    - Câu khó (Hard): 3 điểm
    
    **Công thức:** (Điểm đạt được / Tổng điểm tối đa) × 100
    
    AI sẽ phân tích sâu về năng lực: điểm mạnh/yếu, lỗ hổng kiến thức.
    
    **Section:** 2.2.2 - CHUCNANG.md
    """
)
async def submit_assessment(
    session_id: str,
    request: AssessmentSubmitRequest,
    current_user: Dict = Depends(get_current_user)
) -> AssessmentSubmitResponse:
    """
    Endpoint: POST /api/v1/assessments/{session_id}/submit
    Controller: handle_submit_assessment
    """
    return await handle_submit_assessment(session_id, request, current_user)


@router.get(
    "/{session_id}/results",
    response_model=AssessmentResultsResponse,
    status_code=status.HTTP_200_OK,
    summary="Xem kết quả và phân tích năng lực chi tiết",
    description="""
    Lấy kết quả đánh giá với phân tích đầy đủ từ AI.
    
    **Phân tích theo 4 khía cạnh:**
    1. **Điểm tổng thể** (0-100)
    2. **Phân loại trình độ thực tế**: Beginner (<60), Intermediate (60-80), Advanced (>80)
    3. **Xác định điểm mạnh/yếu** theo từng skill tag
    4. **Lỗ hổng kiến thức** cần ưu tiên khắc phục
    
    **Kết quả bao gồm:**
    - Score breakdown theo easy/medium/hard
    - Skill analysis chi tiết
    - Knowledge gaps với suggested actions
    - Time analysis
    - AI feedback tổng quan
    
    **Section:** 2.2.3 - CHUCNANG.md
    """
)
async def get_assessment_results(
    session_id: str,
    current_user: Dict = Depends(get_current_user)
) -> AssessmentResultsResponse:
    """
    Endpoint: GET /api/v1/assessments/{session_id}/results
    Controller: handle_get_assessment_results
    """
    return await handle_get_assessment_results(session_id, current_user)
