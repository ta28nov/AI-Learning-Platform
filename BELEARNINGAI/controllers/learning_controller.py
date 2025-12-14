"""
Learning Controller - Xử lý requests module & lesson
Tuân thủ: CHUCNANG.md Section 2.4.1-2.4.2, ENDPOINTS.md learning_router

Controller này xử lý 6 endpoints:
- GET /courses/{course_id}/modules/{module_id} - Chi tiết module
- GET /courses/{course_id}/lessons/{lesson_id} - Nội dung lesson
- GET /courses/{course_id}/modules - Danh sách modules
- GET /courses/{course_id}/modules/{module_id}/outcomes - Learning outcomes
- GET /courses/{course_id}/modules/{module_id}/resources - Tài nguyên
- POST /courses/{course_id}/modules/{module_id}/assessments/generate - Sinh quiz module
"""

import logging
from typing import Dict, Optional
from fastapi import HTTPException, status
from datetime import datetime, timedelta

# Import schemas
from schemas.learning import (
    ModuleDetailResponse,
    LessonContentResponse,
    CourseModulesResponse,
    ModuleOutcomesResponse,
    ModuleResourcesResponse,
    ModuleAssessmentGenerateRequest,
    ModuleAssessmentGenerateResponse
)

# Import models
from models.models import Quiz, generate_uuid

# Import services
from services import learning_service, enrollment_service, course_service
from services.ai_service import generate_module_quiz

# Setup logger
logger = logging.getLogger(__name__)


# ============================================================================
# Section 2.4.1: XEM THÔNG TIN MODULE
# ============================================================================

async def handle_get_module_detail(
    course_id: str,
    module_id: str,
    current_user: Dict
) -> ModuleDetailResponse:
    """
    2.4.1: Lấy thông tin chi tiết module
    
    Hiển thị:
    - Tiêu đề và mô tả module
    - Cấp độ khó (Basic/Intermediate/Advanced)
    - Danh sách lessons theo thứ tự
    - Mục tiêu học tập (Learning Outcomes)
    - Thời lượng học ước tính
    - Tài nguyên đính kèm
    - Trạng thái hoàn thành của từng lesson
    
    Args:
        course_id: ID của course
        module_id: ID của module
        current_user: User hiện tại
        
    Returns:
        ModuleDetailResponse
        
    Raises:
        404: Course hoặc module không tồn tại
        403: Chưa đăng ký course
        
    Endpoint: GET /api/v1/courses/{course_id}/modules/{module_id}
    """
    user_id = current_user.get("user_id")
    
    # Kiểm tra course tồn tại
    course = await course_service.get_course_by_id(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khóa học không tồn tại"
        )
    
    # Kiểm tra user đã đăng ký course chưa
    enrollment = await enrollment_service.get_user_enrollment(user_id, course_id)
    if not enrollment or enrollment.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn cần đăng ký khóa học để xem module"
        )
    
    # Lấy module detail
    module_data = await learning_service.get_module_detail(
        course_id=course_id,
        module_id=module_id,
        user_id=user_id
    )
    
    if not module_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module không tồn tại"
        )
    
    return ModuleDetailResponse(**module_data)


# ============================================================================
# Section 2.4.2: XEM NỘI DUNG BÀI HỌC
# ============================================================================

async def handle_get_lesson_content(
    course_id: str,
    lesson_id: str,
    current_user: Dict
) -> LessonContentResponse:
    """
    2.4.2: Lấy nội dung chi tiết lesson
    
    Hiển thị:
    - Nội dung text/HTML
    - Video bài giảng (nếu có)
    - Tài liệu đính kèm
    - Tracking tự động: thời gian học, phần đã xem
    - Thông tin quiz kèm theo
    - Navigation (lesson trước/sau)
    
    Args:
        course_id: ID của course
        lesson_id: ID của lesson
        current_user: User hiện tại
        
    Returns:
        LessonContentResponse
        
    Raises:
        404: Course hoặc lesson không tồn tại
        403: Chưa đăng ký course hoặc lesson bị khóa
        
    Endpoint: GET /api/v1/courses/{course_id}/lessons/{lesson_id}
    """
    user_id = current_user.get("user_id")
    
    # Kiểm tra course tồn tại
    course = await course_service.get_course_by_id(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khóa học không tồn tại"
        )
    
    # Kiểm tra enrollment
    enrollment = await enrollment_service.get_user_enrollment(user_id, course_id)
    if not enrollment or enrollment.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn cần đăng ký khóa học để xem lesson"
        )
    
    # Lấy lesson content
    lesson_data = await learning_service.get_lesson_content(
        course_id=course_id,
        lesson_id=lesson_id,
        user_id=user_id
    )
    
    if not lesson_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson không tồn tại"
        )
    
    # Check if lesson is locked via navigation
    navigation = lesson_data.get("navigation", {})
    prev_lesson = navigation.get("previous_lesson")
    if prev_lesson and prev_lesson.get("id"):
        # Nếu có previous lesson, check xem nó đã completed chưa
        enrollment = await enrollment_service.get_user_enrollment(user_id, course_id)
        if enrollment and prev_lesson.get("id") not in enrollment.completed_lessons:
            # Previous lesson chưa completed, lesson này bị khóa
            if not lesson_data.get("completion_status", {}).get("is_completed"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Bạn cần hoàn thành bài học trước đó"
                )
    
    # Return service data directly - đã match với LessonContentResponse schema
    return LessonContentResponse(**lesson_data)


# ============================================================================
# ADDITIONAL ENDPOINTS (Notes trong ENDPOINTS.md)
# ============================================================================

async def handle_get_course_modules(
    course_id: str,
    current_user: Dict
) -> Dict:
    """
    Lấy danh sách tất cả modules trong course
    
    Args:
        course_id: ID của course
        current_user: User hiện tại
        
    Returns:
        Dict with modules list
        
    Endpoint: GET /api/v1/courses/{course_id}/modules
    """
    user_id = current_user.get("user_id")
    
    # Kiểm tra course tồn tại
    course = await course_service.get_course_by_id(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khóa học không tồn tại"
        )
    
    # Kiểm tra enrollment
    enrollment = await enrollment_service.get_user_enrollment(user_id, course_id)
    if not enrollment or enrollment.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn cần đăng ký khóa học"
        )
    
    # Lấy modules list
    modules_data = await learning_service.get_course_modules_list(
        course_id=course_id,
        user_id=user_id
    )
    
    if not modules_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy modules"
        )
    
    return modules_data


async def handle_get_module_outcomes(
    course_id: str,
    module_id: str,
    current_user: Dict
) -> Dict:
    """
    Lấy learning outcomes của module
    
    Args:
        course_id: ID của course
        module_id: ID của module
        current_user: User hiện tại
        
    Returns:
        Dict with outcomes
        
    Endpoint: GET /api/v1/courses/{course_id}/modules/{module_id}/outcomes
    """
    user_id = current_user.get("user_id")
    
    # Kiểm tra enrollment
    enrollment = await enrollment_service.get_user_enrollment(user_id, course_id)
    if not enrollment or enrollment.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn cần đăng ký khóa học"
        )
    
    # Lấy outcomes
    outcomes_data = await learning_service.get_module_outcomes(
        course_id=course_id,
        module_id=module_id,
        user_id=user_id
    )
    
    if not outcomes_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module không tồn tại"
        )
    
    return outcomes_data


async def handle_get_module_resources(
    course_id: str,
    module_id: str,
    current_user: Dict
) -> Dict:
    """
    Lấy tài nguyên học tập của module
    
    Args:
        course_id: ID của course
        module_id: ID của module
        current_user: User hiện tại
        
    Returns:
        Dict with resources
        
    Endpoint: GET /api/v1/courses/{course_id}/modules/{module_id}/resources
    """
    user_id = current_user.get("user_id")
    
    # Kiểm tra enrollment
    enrollment = await enrollment_service.get_user_enrollment(user_id, course_id)
    if not enrollment or enrollment.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn cần đăng ký khóa học"
        )
    
    # Lấy resources
    resources_data = await learning_service.get_module_resources(
        course_id=course_id,
        module_id=module_id
    )
    
    if not resources_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module không tồn tại"
        )
    
    return resources_data


async def handle_generate_module_assessment(
    course_id: str,
    module_id: str,
    request: ModuleAssessmentGenerateRequest,
    current_user: Dict
) -> Dict:
    """
    4.6: Generate AI-powered module assessment
    Tuân thủ API_SCHEMA.md - Response 201 Created
    
    Flow:
    1. Verify enrollment
    2. Get module with learning outcomes
    3. Call AI service to generate quiz questions (with fallback)
    4. Create Quiz document
    5. Return comprehensive response with full question details
    
    Args:
        course_id: Course ID
        module_id: Module ID
        request: ModuleAssessmentGenerateRequest with assessment_type, question_count, etc.
        current_user: Current user dict
        
    Returns:
        Dict matching API_SCHEMA.md structure with assessment_id, questions array, etc.
        
    Endpoint: POST /api/v1/courses/{course_id}/modules/{module_id}/assessments/generate
    """
    user_id = current_user.get("user_id")
    
    logger.info(f"Generating module assessment - user: {user_id}, course: {course_id}, module: {module_id}")
    
    # Verify course exists
    course = await course_service.get_course_by_id(course_id)
    if not course:
        logger.error(f"Course not found: {course_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khóa học không tồn tại"
        )
    
    # Verify enrollment (if not owner)
    if course.owner_id != user_id:
        enrollment = await enrollment_service.get_user_enrollment(user_id, course_id)
        if not enrollment or enrollment.status == "cancelled":
            logger.warning(f"User {user_id} not enrolled in course {course_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn cần đăng ký khóa học để tạo bài kiểm tra"
            )
    
    # Get module with learning outcomes
    module = None
    for mod in course.modules:
        if str(mod.id) == module_id:
            module = mod
            break
    
    if not module:
        logger.error(f"Module not found: {module_id} in course {course_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module không tồn tại trong khóa học này"
        )
    
    # Prepare learning outcomes for AI
    outcomes_list = []
    for outcome in module.learning_outcomes:
        outcomes_list.append({
            "id": str(outcome.get("id", generate_uuid())),
            "outcome": outcome.get("description", ""),
            "skill_tag": outcome.get("skill_tag", "general"),
            "is_mandatory": outcome.get("is_mandatory", False)
        })
    
    if not outcomes_list:
        logger.warning(f"Module {module_id} has no learning outcomes")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Module chưa có learning outcomes để tạo bài kiểm tra"
        )
    
    logger.info(f"Module has {len(outcomes_list)} learning outcomes")
    
    # Map difficulty_preference to difficulty for AI service
    difficulty_map = {
        "easy": "easy",
        "mixed": "medium",
        "hard": "hard"
    }
    difficulty = difficulty_map.get(request.difficulty_preference, "medium")
    
    # Call AI service to generate questions (with fallback on error)
    try:
        quiz_data = await generate_module_quiz(
            module_title=module.title,
            learning_outcomes=outcomes_list,
            module_description=module.description,
            question_count=request.question_count or 10,
            difficulty=difficulty,
            focus_outcomes=request.focus_topics  # Note: focus_topics are skill tags in request
        )
        logger.info(f"Quiz generated - {len(quiz_data['questions'])} questions, {quiz_data['total_points']} points")
    except Exception as e:
        # This should not happen anymore since we added fallback in AI service
        logger.error(f"Unexpected error in generate_module_quiz: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể tạo bài kiểm tra lúc này"
        )
    
    # CRITICAL FIX: Generate question_id for each question BEFORE saving to DB
    # This ensures question_id in response matches question_id in DB for quiz submission
    questions_with_ids = []
    for q in quiz_data["questions"]:
        # Generate unique question_id
        question_id = str(generate_uuid())
        
        # Add question_id to question data
        q_with_id = q.copy()
        q_with_id["question_id"] = question_id
        questions_with_ids.append(q_with_id)
    
    # Create Quiz document with questions that have question_id
    quiz_id = generate_uuid()
    quiz = Quiz(
        id=quiz_id,
        course_id=course_id,
        module_id=module_id,
        lesson_id="module-assessment",  # Special marker for module-level quiz
        title=f"Assessment: {module.title}",
        description=f"Bài kiểm tra {request.assessment_type} cho module {module.title}",
        quiz_type=request.assessment_type,  # review|practice|final_check
        questions=questions_with_ids,  # ← Use questions with question_id
        total_points=quiz_data["total_points"],
        question_count=len(questions_with_ids),
        mandatory_question_count=quiz_data.get("mandatory_count", 0),
        passing_score=70.0,  # 70% pass threshold
        time_limit_minutes=request.time_limit_minutes or 15,
        max_attempts=999 if request.assessment_type in ["review", "practice"] else 1,
        is_draft=False,
        deadline=None,
        created_by=user_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    await quiz.insert()
    logger.info(f"Quiz created successfully - id: {quiz_id}")
    
    # Calculate pass threshold percentage
    pass_threshold = int(quiz.passing_score) if quiz.passing_score else 70
    
    # Prepare questions array matching API_SCHEMA format
    # CRITICAL: Use the SAME question_id from DB
    questions_response = []
    for q in questions_with_ids:
        question_obj = {
            "question_id": q["question_id"],  # ← Use question_id from DB, not generate new!
            "order": q.get("order", 0),
            "question_text": q.get("question_text", q.get("question", "")),
            "question_type": q.get("type", "multiple_choice"),
            "difficulty": difficulty,
            "skill_tag": q.get("outcome_id", "general"),
            "points": q.get("points", 10),
            "is_mandatory": q.get("is_mandatory", False),
            "options": [{"option_id": chr(65 + i), "content": opt} for i, opt in enumerate(q.get("options", []))],
            "hint": q.get("explanation", "")[:100] if q.get("explanation") else None
        }
        questions_response.append(question_obj)
    
    # Prepare response matching API_SCHEMA.md
    created_at = datetime.utcnow()
    expires_at = created_at + timedelta(minutes=60)  # Expires in 60 minutes
    can_retake = request.assessment_type in ["review", "practice"]
    
    return {
        "assessment_id": quiz_id,
        "module_id": module_id,
        "module_title": module.title,
        "assessment_type": request.assessment_type,
        "question_count": len(quiz_data["questions"]),
        "time_limit_minutes": quiz.time_limit_minutes,
        "total_points": quiz.total_points,
        "pass_threshold": pass_threshold,
        "questions": questions_response,
        "instructions": f"Hoàn thành bài kiểm tra {request.assessment_type} trong {quiz.time_limit_minutes} phút. Đạt {pass_threshold}% để pass.",
        "created_at": created_at,
        "expires_at": expires_at,
        "can_retake": can_retake,
        "message": "Bài kiểm tra module đã được tạo thành công"
    }
