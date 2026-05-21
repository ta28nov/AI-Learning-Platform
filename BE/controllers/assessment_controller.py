"""
Assessment Controller - Xử lý requests đánh giá năng lực AI
Tuân thủ: CHUCNANG.md Section 2.2, ENDPOINTS.md, API_SCHEMA.md
Naming: snake_case theo Python convention
Version: 2.0 - Hoàn chỉnh theo API_SCHEMA.md
"""

from typing import Dict
from datetime import datetime
from fastapi import HTTPException, status
from schemas.assessment import (
    AssessmentGenerateRequest,
    AssessmentGenerateResponse,
    AssessmentSubmitRequest,
    AssessmentSubmitResponse,
    AssessmentResultsResponse,
    AssessmentInfo,
    ScoreBreakdown,
    ScoreBreakdownCategory,
    SkillAnalysis,
    KnowledgeGap,
    TimeAnalysis,
    AssessmentHistoryResponse,
    AssessmentHistoryItem,
    AssessmentReviewResponse,
    AssessmentReviewItem,
)
from services import assessment_service


async def handle_generate_assessment(
    request: AssessmentGenerateRequest,
    current_user: Dict
) -> AssessmentGenerateResponse:
    """
    Sinh bộ câu hỏi đánh giá năng lực
    Endpoint: POST /api/v1/assessments/generate
    Tuân thủ: CHUCNANG.md Section 2.2.1, API_SCHEMA.md Section 2.1
    
    Phân bổ số lượng theo mức độ:
    - Beginner: 15 câu (3 easy + 8 medium + 4 hard), 15 phút
    - Intermediate: 25 câu (5 easy + 13 medium + 7 hard), 22 phút
    - Advanced: 35 câu (7 easy + 18 medium + 10 hard), 30 phút
    
    Args:
        request: AssessmentGenerateRequest với category, subject, level, focus_areas
        current_user: Dict từ middleware chứa {user_id, email, role}
        
    Returns:
        AssessmentGenerateResponse với session_id và danh sách câu hỏi
        
    Raises:
        HTTPException 400: Invalid category/subject/level
        HTTPException 500: Lỗi sinh câu hỏi
    """
    try:
        user_id = current_user.get("user_id")
        
        # Tạo assessment session với AI
        session = await assessment_service.create_assessment_session(
            user_id=user_id,
            category=request.category,
            subject=request.subject,
            level=request.level,
            focus_areas=request.focus_areas,
            custom_goals=request.custom_goals,
        )
        
        return AssessmentGenerateResponse(
            session_id=session.id,
            category=session.category,
            subject=session.subject,
            level=session.level,
            question_count=session.total_questions,
            time_limit_minutes=session.time_limit_minutes,
            questions=session.questions,
            created_at=session.created_at,
            expires_at=session.expires_at,
            message="Bộ câu hỏi đánh giá đã được tạo thành công"
        )
        
    except ValueError as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Invalid assessment request - user: {user_id}, category: {request.category}, subject: {request.subject}, level: {request.level}, error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Assessment generation failed - user: {user_id}, category: {request.category}, subject: {request.subject}, level: {request.level}, error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi sinh câu hỏi: {str(e)}"
        )


async def handle_submit_assessment(
    session_id: str,
    request: AssessmentSubmitRequest,
    current_user: Dict
) -> AssessmentSubmitResponse:
    """
    Nộp bài đánh giá năng lực
    Endpoint: POST /api/v1/assessments/{session_id}/submit
    Tuân thủ: CHUCNANG.md Section 2.2.2, API_SCHEMA.md Section 2.2
    
    AI tự động chấm điểm dựa trên thuật toán có trọng số:
    - Easy: 1 điểm
    - Medium: 2 điểm
    - Hard: 3 điểm
    Công thức: (Điểm đạt được / Tổng điểm tối đa) × 100
    
    Args:
        session_id: UUID của phiên đánh giá
        request: AssessmentSubmitRequest với answers, total_time_seconds, submitted_at
        current_user: Dict từ middleware
        
    Returns:
        AssessmentSubmitResponse với status submitted
        
    Raises:
        HTTPException 404: Session không tồn tại
        HTTPException 403: Không có quyền truy cập
        HTTPException 400: Session expired, already submitted, invalid answers
    """
    try:
        user_id = current_user.get("user_id")
        
        # Lấy session và kiểm tra ownership
        session = await assessment_service.get_assessment_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment session không tồn tại"
            )
        
        if session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền truy cập session này"
            )
        
        # Đã chấm xong — idempotent cho client retry sau timeout/proxy trong khi server đã xử lý xong
        if session.status == "evaluated":
            time_taken_minutes = (
                request.total_time_seconds / 60.0 if request.total_time_seconds else 0.0
            )
            return AssessmentSubmitResponse(
                session_id=session.id,
                submitted_at=session.submitted_at or datetime.utcnow(),
                total_questions=session.total_questions,
                time_taken_minutes=round(time_taken_minutes, 1),
                status="evaluated",
                message="Bài làm đã được ghi nhận trước đó.",
            )
        
        if datetime.utcnow() > session.expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phiên đánh giá đã hết hạn"
            )
        
        # Chuyển đổi answers sang format cho service
        answers_list = [
            {
                "question_id": ans.question_id,
                "answer_content": ans.answer_content,
                "selected_option": ans.selected_option,
                "time_taken_seconds": ans.time_taken_seconds
            }
            for ans in request.answers
        ]
        
        # Submit và evaluate
        evaluated_session = await assessment_service.submit_assessment(
            session_id=session_id,
            answers=answers_list,
            total_elapsed_seconds=request.total_time_seconds,
        )
        
        if not evaluated_session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể submit bài đánh giá"
            )
        
        # Tính time_taken_minutes
        time_taken_minutes = request.total_time_seconds / 60.0
        
        return AssessmentSubmitResponse(
            session_id=evaluated_session.id,
            submitted_at=evaluated_session.submitted_at,
            total_questions=evaluated_session.total_questions,
            time_taken_minutes=round(time_taken_minutes, 1),
            status="submitted",
            message="Bài làm đã được nộp thành công. Kết quả sẽ có sau vài giây."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Assessment submission failed - session_id: {session_id}, user: {user_id}, answers_count: {len(request.answers)}, error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi submit bài: {str(e)}"
        )


async def handle_get_assessment_results(
    session_id: str,
    current_user: Dict
) -> AssessmentResultsResponse:
    """
    Xem kết quả và phân tích năng lực chi tiết
    Endpoint: GET /api/v1/assessments/{session_id}/results
    Tuân thủ: CHUCNANG.md Section 2.2.3, API_SCHEMA.md Section 2.3
    
    AI phân tích theo 4 khía cạnh:
    1. Điểm tổng thể (0-100)
    2. Phân loại trình độ (Beginner < 60, Intermediate 60-80, Advanced > 80)
    3. Điểm mạnh/yếu theo skill tag
    4. Lỗ hổng kiến thức cần khắc phục
    
    Args:
        session_id: UUID của phiên đánh giá
        current_user: Dict từ middleware
        
    Returns:
        AssessmentResultsResponse với phân tích đầy đủ
        
    Raises:
        HTTPException 404: Session không tồn tại hoặc chưa submit
        HTTPException 403: Không có quyền truy cập
    """
    try:
        user_id = current_user.get("user_id")
        
        # Lấy session và kiểm tra
        session = await assessment_service.get_assessment_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment session không tồn tại"
            )
        
        if session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền truy cập session này"
            )
        
        if session.status != "evaluated":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kết quả chưa sẵn sàng. Vui lòng submit bài trước."
            )
        
        # Chuẩn bị score_breakdown
        score_breakdown_data = session.skill_analysis.get("score_breakdown", {}) if session.skill_analysis else {}
        
        easy_data = score_breakdown_data.get("easy", {"correct": 0, "total": 0})
        medium_data = score_breakdown_data.get("medium", {"correct": 0, "total": 0})
        hard_data = score_breakdown_data.get("hard", {"correct": 0, "total": 0})
        
        easy_pct = (easy_data["correct"] / easy_data["total"] * 100) if easy_data["total"] > 0 else 0
        medium_pct = (medium_data["correct"] / medium_data["total"] * 100) if medium_data["total"] > 0 else 0
        hard_pct = (hard_data["correct"] / hard_data["total"] * 100) if hard_data["total"] > 0 else 0
        
        score_breakdown = ScoreBreakdown(
            easy_questions=ScoreBreakdownCategory(
                total=easy_data["total"],
                correct=easy_data["correct"],
                score_percentage=round(easy_pct, 1)
            ),
            medium_questions=ScoreBreakdownCategory(
                total=medium_data["total"],
                correct=medium_data["correct"],
                score_percentage=round(medium_pct, 1)
            ),
            hard_questions=ScoreBreakdownCategory(
                total=hard_data["total"],
                correct=hard_data["correct"],
                score_percentage=round(hard_pct, 1)
            )
        )
        
        # Chuẩn bị skill_analysis
        skill_analysis_data = session.skill_analysis.get("skill_analysis", []) if session.skill_analysis else []
        skill_analysis = [
            SkillAnalysis(**skill) for skill in skill_analysis_data
        ]
        
        # Chuẩn bị knowledge_gaps
        knowledge_gaps_data = session.knowledge_gaps if session.knowledge_gaps else []
        knowledge_gaps = [
            KnowledgeGap(**gap) for gap in knowledge_gaps_data
        ]
        
        # Tính time_analysis — ưu tiên total_elapsed_seconds từ lúc nộp bài (FE gửi total_time_seconds)
        n_answered = len(session.answers) if session.answers else 0
        n_questions = max(n_answered, session.total_questions or 0, 1)

        if getattr(session, "total_elapsed_seconds", None) is not None:
            total_time = max(0, int(session.total_elapsed_seconds))
        else:
            total_time = sum(
                ans.get("time_taken_seconds", 0) for ans in (session.answers or [])
            )

        avg_time = round(total_time / n_questions, 1) if n_questions else 0.0
        time_list = [
            ans.get("time_taken_seconds", 0) for ans in (session.answers or [])
        ]
        if time_list and sum(time_list) > 0:
            fastest_q = min(time_list)
            slowest_q = max(time_list)
        else:
            fastest_q = 0
            slowest_q = 0

        time_analysis = TimeAnalysis(
            total_time_seconds=total_time,
            average_time_per_question=avg_time,
            fastest_question_time=int(fastest_q),
            slowest_question_time=int(slowest_q),
        )
        
        # Tính correct_answers (ưu tiên số đếm từ per_question_results khi có)
        if session.correct_answers is not None:
            correct_answers = int(session.correct_answers)
        else:
            correct_answers = (
                easy_data["correct"] + medium_data["correct"] + hard_data["correct"]
            )
        
        # AI feedback
        ai_feedback = session.skill_analysis.get("overall_feedback", "") if session.skill_analysis else ""
        
        return AssessmentResultsResponse(
            session_id=session.id,
            assessment_info=AssessmentInfo(
                category=session.category,
                subject=session.subject,
                level=session.level,
                completed_at=session.evaluated_at or session.submitted_at
            ),
            overall_score=round(session.overall_score, 1) if session.overall_score else 0,
            proficiency_level=session.proficiency_level or "Beginner",
            total_questions=session.total_questions,
            correct_answers=correct_answers,
            score_breakdown=score_breakdown,
            skill_analysis=skill_analysis,
            knowledge_gaps=knowledge_gaps,
            time_analysis=time_analysis,
            ai_feedback=ai_feedback
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Assessment results retrieval failed - session_id: {session_id}, user: {user_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy kết quả: {str(e)}"
        )


async def handle_list_assessment_history(
    current_user: Dict,
    skip: int = 0,
    limit: int = 30,
) -> AssessmentHistoryResponse:
    """
    Danh sách phiên đánh giá của user (mới nhất trước).
    GET /api/v1/assessments/history
    """
    user_id = current_user.get("user_id")
    cap = min(max(limit, 1), 50)
    sessions = await assessment_service.get_user_assessment_sessions(
        user_id=user_id,
        skip=max(skip, 0),
        limit=cap,
    )
    items = [
        AssessmentHistoryItem(
            session_id=s.id,
            category=s.category,
            subject=s.subject,
            level=s.level,
            status=s.status,
            total_questions=s.total_questions,
            overall_score=s.overall_score,
            proficiency_level=s.proficiency_level,
            created_at=s.created_at,
            submitted_at=s.submitted_at,
            evaluated_at=s.evaluated_at,
        )
        for s in sessions
    ]
    return AssessmentHistoryResponse(sessions=items)


async def handle_get_assessment_review(
    session_id: str,
    current_user: Dict,
) -> AssessmentReviewResponse:
    """
    Xem lại toàn bộ câu hỏi và đáp án đã nộp (read-only).
    GET /api/v1/assessments/{session_id}/review
    """
    user_id = current_user.get("user_id")
    session = await assessment_service.get_assessment_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment session không tồn tại",
        )

    if session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền truy cập session này",
        )

    if session.status != "evaluated":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ xem lại được sau khi bài đã được chấm xong.",
        )

    payload = assessment_service.build_assessment_review_payload(session)
    items = [AssessmentReviewItem(**row) for row in payload["items"]]

    return AssessmentReviewResponse(
        session_id=payload["session_id"],
        category=payload["category"],
        subject=payload["subject"],
        level=payload["level"],
        total_questions=payload["total_questions"],
        overall_score=payload["overall_score"],
        proficiency_level=payload["proficiency_level"],
        evaluated_at=payload["evaluated_at"],
        items=items,
    )
