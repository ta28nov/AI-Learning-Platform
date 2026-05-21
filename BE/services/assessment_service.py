"""
Assessment Service - Xử lý đánh giá năng lực AI
Sử dụng: Beanie ODM, Google Gemini (via ai_service)
Tuân thủ: CHUCNANG.md Section 2.2
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict
from models.models import AssessmentSession
from services.ai_service import generate_assessment_questions, evaluate_assessment_answers


# ============================================================================
# ASSESSMENT SESSION CRUD
# ============================================================================

async def create_assessment_session(
    user_id: str,
    category: str,
    subject: str,
    level: str,
    focus_areas: Optional[List[str]] = None,
    custom_goals: Optional[str] = None,
) -> AssessmentSession:
    """
    Tạo phiên đánh giá mới với câu hỏi từ AI
    Tuân thủ CHUCNANG.md Section 2.2.1
    
    Số lượng câu hỏi và thời gian theo mức độ:
    - Beginner: 15 câu, 15 phút
    - Intermediate: 25 câu, 22 phút
    - Advanced: 35 câu, 30 phút
    
    Args:
        user_id: ID của user
        category: Danh mục
        subject: Chủ đề
        level: Mức độ (Beginner, Intermediate, Advanced)
        focus_areas: Các chủ đề con cần tập trung (optional)
        
    Returns:
        AssessmentSession document đã tạo
    """
    # Xác định số câu và thời gian theo mức độ
    if level == "Beginner":
        total_questions = 15
        time_limit_minutes = 15
    elif level == "Intermediate":
        total_questions = 25
        time_limit_minutes = 22
    elif level == "Advanced":
        total_questions = 35
        time_limit_minutes = 30
    else:
        total_questions = 15
        time_limit_minutes = 15
    
    # Generate questions sử dụng AI
    questions = await generate_assessment_questions(
        category=category,
        subject=subject,
        level=level,
        count=total_questions,
        focus_areas=focus_areas,
        custom_goals=custom_goals,
    )
    
    # Tính expiry time (60 phút từ khi tạo)
    expires_at = datetime.utcnow() + timedelta(minutes=60)
    
    session = AssessmentSession(
        user_id=user_id,
        category=category,
        subject=subject,
        level=level,
        focus_areas=focus_areas or [],
        custom_goals=(custom_goals or "").strip() or None,
        total_questions=total_questions,
        time_limit_minutes=time_limit_minutes,
        questions=questions,
        status="pending",
        expires_at=expires_at
    )
    
    await session.insert()
    return session


async def get_assessment_session(session_id: str) -> Optional[AssessmentSession]:
    """
    Lấy assessment session theo ID
    
    Args:
        session_id: ID của session
        
    Returns:
        AssessmentSession document hoặc None
    """
    try:
        session = await AssessmentSession.get(session_id)
        return session
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to retrieve assessment session: {session_id}, error: {str(e)}")
        return None


async def get_user_assessment_sessions(
    user_id: str,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
) -> List[AssessmentSession]:
    """
    Lấy danh sách assessment sessions của user
    
    Args:
        user_id: ID của user
        status: Filter theo status
        skip: Pagination skip
        limit: Pagination limit
        
    Returns:
        List AssessmentSession documents
    """
    if status:
        query = AssessmentSession.find(
            AssessmentSession.user_id == user_id,
            AssessmentSession.status == status,
        )
    else:
        query = AssessmentSession.find(AssessmentSession.user_id == user_id)

    sessions = await query.sort(-AssessmentSession.created_at).skip(skip).limit(limit).to_list()
    return sessions


def build_assessment_review_payload(session: AssessmentSession) -> Dict:
    """Ghép câu hỏi + câu trả lời đã lưu cho UI xem lại (read-only)."""
    answers_by_id: Dict[str, Dict] = {}
    for a in session.answers or []:
        qid = a.get("question_id")
        if qid:
            answers_by_id[qid] = a

    items: List[Dict] = []
    for q in session.questions or []:
        qid = q.get("question_id") or ""
        ans = answers_by_id.get(qid, {})
        content = ans.get("answer_content")
        if content is None:
            content = ""
        sel = ans.get("selected_option")
        opt_text = None
        opts = q.get("options")
        if sel is not None and isinstance(sel, int) and opts and isinstance(opts, list):
            if 0 <= sel < len(opts):
                opt_text = opts[sel]

        row = {
                "question_id": qid,
                "question_text": q.get("question_text") or "",
                "question_type": q.get("question_type") or "",
                "difficulty": q.get("difficulty"),
                "skill_tag": q.get("skill_tag"),
                "points": q.get("points"),
                "options": opts if isinstance(opts, list) else None,
                "correct_answer_hint": q.get("correct_answer_hint"),
                "answer_content": str(content),
                "selected_option": sel if isinstance(sel, int) else None,
                "selected_option_text": opt_text,
                "time_taken_seconds": int(ans.get("time_taken_seconds") or 0),
            }
        items.append(row)

    results_by_id = {r.get("question_id"): r for r in (session.per_question_results or [])}
    for row in items:
        rid = row.get("question_id")
        pr = results_by_id.get(rid)
        if pr:
            row["is_correct"] = pr.get("is_correct")
            row["grading_note"] = pr.get("explanation") or None

    return {
        "session_id": session.id,
        "category": session.category,
        "subject": session.subject,
        "level": session.level,
        "total_questions": session.total_questions,
        "overall_score": session.overall_score,
        "proficiency_level": session.proficiency_level,
        "evaluated_at": session.evaluated_at,
        "items": items,
    }


# ============================================================================
# ASSESSMENT SUBMISSION & EVALUATION (Section 2.2.3)
# ============================================================================

async def start_assessment(session_id: str) -> Optional[AssessmentSession]:
    """
    Bắt đầu làm assessment
    
    Args:
        session_id: ID của session
        
    Returns:
        AssessmentSession document đã update hoặc None
    """
    session = await get_assessment_session(session_id)
    
    if not session:
        return None
    
    if session.status != "pending":
        return None
    
    session.status = "in_progress"
    await session.save()
    return session


async def submit_assessment(
    session_id: str,
    answers: List[Dict],
    total_elapsed_seconds: Optional[int] = None,
) -> Optional[AssessmentSession]:
    """
    Submit câu trả lời và đánh giá kết quả
    
    Args:
        session_id: ID của session
        answers: List câu trả lời dạng [{"question_id": "q1", "answer": "Option A"}, ...]
        
    Returns:
        AssessmentSession document đã đánh giá hoặc None
    """
    session = await get_assessment_session(session_id)
    
    if not session:
        return None
    
    if session.status not in ["pending", "in_progress"]:
        return None
    
    # Kiểm tra expiry
    if datetime.utcnow() > session.expires_at:
        session.status = "evaluated"
        await session.save()
        return session
    
    # Lưu answers
    session.answers = answers
    session.submitted_at = datetime.utcnow()
    session.status = "submitted"
    
    # Evaluate sử dụng AI
    evaluation = await evaluate_assessment_answers(
        questions=session.questions,
        answers=answers,
        category=session.category,
        subject=session.subject
    )
    
    # Lưu kết quả - skill_analysis là dict chứa cả breakdown và analysis
    session.overall_score = evaluation["overall_score"]
    session.proficiency_level = evaluation["proficiency_level"]
    session.skill_analysis = {
        "skill_analysis": evaluation["skill_analysis"],
        "score_breakdown": evaluation["score_breakdown"],
        "overall_feedback": evaluation["overall_feedback"]
    }
    session.knowledge_gaps = evaluation["knowledge_gaps"]
    session.per_question_results = evaluation.get("per_question_results") or []
    cq = sum(
        1 for r in session.per_question_results if r.get("is_correct") is True
    )
    session.correct_answers = cq

    if total_elapsed_seconds is not None:
        session.total_elapsed_seconds = max(0, int(total_elapsed_seconds))
    
    session.status = "evaluated"
    session.evaluated_at = datetime.utcnow()
    
    await session.save()
    return session


# ============================================================================
# ASSESSMENT RESULTS
# ============================================================================

async def get_assessment_results(session_id: str) -> Optional[Dict]:
    """
    Lấy kết quả assessment đầy đủ
    
    Args:
        session_id: ID của session
        
    Returns:
        Dict chứa kết quả hoặc None
    """
    session = await get_assessment_session(session_id)
    
    if not session or session.status != "evaluated":
        return None
    
    return {
        "session_id": session.id,
        "category": session.category,
        "subject": session.subject,
        "level": session.level,
        "overall_score": session.overall_score,
        "proficiency_level": session.proficiency_level,
        "skill_analysis": session.skill_analysis,
        "knowledge_gaps": session.knowledge_gaps,
        "total_questions": session.total_questions,
        "submitted_at": session.submitted_at,
        "evaluated_at": session.evaluated_at
    }


async def delete_assessment_session(session_id: str) -> bool:
    """
    Xóa assessment session
    
    Args:
        session_id: ID của session
        
    Returns:
        True nếu xóa thành công, False nếu không tìm thấy
    """
    session = await get_assessment_session(session_id)
    
    if not session:
        return False
    
    await session.delete()
    return True
