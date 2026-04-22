"""
Quiz Controller - Xử lý requests quiz
Tuân thủ: CHUCNANG.md Section 2.4.3-2.4.7 + 3.3.1-3.3.5, ENDPOINTS.md quiz_router

Controller này xử lý 10 endpoints:
STUDENT FEATURES (2.4.3-2.4.7):
- GET /quizzes/{id} - Chi tiết quiz
- POST /quizzes/{id}/attempt - Làm quiz
- GET /quizzes/{id}/results - Xem kết quả
- POST /quizzes/{id}/retake - Làm lại quiz
- POST /ai/generate-practice - Sinh bài tập

INSTRUCTOR FEATURES (3.3.1-3.3.5):
- POST /lessons/{id}/quizzes - Tạo quiz mới
- GET /quizzes - List quizzes with filters
- PUT /quizzes/{id} - Update quiz
- DELETE /quizzes/{id} - Xóa quiz
- GET /quizzes/{id}/class-results - Xem kết quả cả lớp
"""

from typing import Dict, Optional, List
from fastapi import HTTPException, status
from datetime import datetime

# Import schemas
from schemas.quiz import (
    QuizDetailResponse,
    QuizAttemptRequest,
    QuizAttemptResponse,
    QuizResultsResponse,
    QuizRetakeResponse,
    RetakeQuestion,
    PracticeExercisesGenerateRequest,
    PracticeExercisesGenerateResponse,
    SourceInfo,
    Exercise,  # ← THÊM MỚI
    QuizCreateRequest,
    QuizCreateResponse,
    QuizListResponse,
    QuizUpdateRequest,
    QuizUpdateResponse,
    QuizDeleteResponse,
    QuizClassResultsResponse
)

# Import services
from services import quiz_service, enrollment_service, course_service, ai_service


# ============================================================================
# Section 2.4.3: XEM THÔNG TIN QUIZ
# ============================================================================

async def handle_get_quiz_detail(
    quiz_id: str,
    current_user: Dict
) -> QuizDetailResponse:
    """
    2.4.3: Lấy thông tin chi tiết quiz
    
    Hiển thị:
    - Tiêu đề và mô tả quiz
    - Danh sách câu hỏi (question_text, answers)
    - Passing score
    - Max attempts
    - Duration
    - Trạng thái attempts của user
    
    Args:
        quiz_id: ID của quiz
        current_user: User hiện tại
        
    Returns:
        QuizDetailResponse
        
    Raises:
        404: Quiz không tồn tại
        403: Chưa đăng ký course
        
    Endpoint: GET /api/v1/quizzes/{id}
    """
    user_id = current_user.get("user_id")
    
    # Lấy quiz
    quiz = await quiz_service.get_quiz_by_id(quiz_id)
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz không tồn tại"
        )
    
    # Kiểm tra enrollment nếu quiz thuộc course
    if quiz.course_id:
        enrollment = await enrollment_service.get_user_enrollment(user_id, quiz.course_id)
        if not enrollment or enrollment.status == "cancelled":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn cần đăng ký khóa học để xem quiz"
            )
    
    # Lấy attempts của user
    attempts = await quiz_service.get_user_quiz_attempts(user_id, quiz_id)
    
    return QuizDetailResponse(
        id=str(quiz.id),
        title=quiz.title,
        description=quiz.description,
        question_count=len(quiz.questions),  # Fix: add missing field
        time_limit=quiz.time_limit_minutes,  # Fix: correct field name
        pass_threshold=int(quiz.passing_score),  # Fix: correct field name and type
        mandatory_question_count=sum(1 for q in quiz.questions if q.get("is_mandatory", False)),  # Fix: calculate
        user_attempts=len(attempts),  # Fix: should be int, not list
        best_score=max([a.score for a in attempts]) if attempts else None,
        last_attempt_at=attempts[0].started_at if attempts else None
    )


# ============================================================================
# Section 2.4.4: LÀM QUIZ
# ============================================================================

async def handle_attempt_quiz(
    quiz_id: str,
    request: QuizAttemptRequest,
    current_user: Dict
) -> QuizAttemptResponse:
    """
    2.4.4: Submit answers cho quiz
    
    Business logic:
    - Chấm điểm: 70% threshold
    - Điều kiện pass: score >= 70% VÀ tất cả mandatory questions correct
    - Tính thời gian làm bài
    - Lưu attempt vào DB
    
    Args:
        quiz_id: ID của quiz
        request: QuizAttemptRequest (answers list)
        current_user: User hiện tại
        
    Returns:
        QuizAttemptResponse (score, passed, total_questions)
        
    Raises:
        404: Quiz không tồn tại
        403: Vượt quá max_attempts
        400: Thiếu answers
        
    Endpoint: POST /api/v1/quizzes/{id}/attempt
    """
    user_id = current_user.get("user_id")
    
    # Lấy quiz
    quiz = await quiz_service.get_quiz_by_id(quiz_id)
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz không tồn tại"
        )
    
    # Kiểm tra enrollment
    if quiz.course_id:
        enrollment = await enrollment_service.get_user_enrollment(user_id, quiz.course_id)
        if not enrollment or enrollment.status == "cancelled":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn cần đăng ký khóa học"
            )
    
    # Kiểm tra max attempts
    attempts = await quiz_service.get_user_quiz_attempts(user_id, quiz_id)
    if len(attempts) >= quiz.max_attempts and quiz.max_attempts > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Bạn đã hết lượt làm quiz (max: {quiz.max_attempts})"
        )
    
    # Validate answers
    if not request.answers or len(request.answers) != len(quiz.questions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phải trả lời tất cả câu hỏi"
        )
    
    # Chấm điểm
    score, passed = await quiz_service.grade_quiz_attempt(
        quiz=quiz,
        answers=request.answers
    )
    
    # Lưu attempt
    attempt = await quiz_service.create_quiz_attempt(
        quiz_id=quiz_id,
        user_id=user_id,
        answers=request.answers,
        score=score,
        passed=passed,
        time_spent_minutes=request.time_spent_minutes or 0
    )
    
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lưu kết quả quiz"
        )
    
    # Ensure submitted_at is set
    if not attempt.submitted_at:
        attempt.submitted_at = datetime.utcnow()
    
    return QuizAttemptResponse(
        attempt_id=str(attempt.id),
        quiz_id=str(quiz_id),
        score=attempt.score,
        passed=attempt.passed,
        total_questions=attempt.total_questions,
        correct_answers=attempt.correct_answers,
        time_spent_minutes=attempt.time_spent_seconds // 60,
        attempt_number=attempt.attempt_number,
        submitted_at=attempt.submitted_at,
        message="Chúc mừng! Bạn đã pass quiz" if attempt.passed else "Bạn chưa đạt điểm pass. Hãy thử lại!"
    )


# ============================================================================
# Section 2.4.5: XEM KẾT QUẢ QUIZ
# ============================================================================

async def handle_get_quiz_results(
    quiz_id: str,
    attempt_id: Optional[str],
    current_user: Dict
) -> QuizResultsResponse:
    """
    2.4.5: Xem kết quả chi tiết quiz attempt
    
    Hiển thị:
    - Score và passed status
    - Chi tiết từng câu: đúng/sai, explanation, link bài học
    - Thời gian làm bài
    
    Args:
        quiz_id: ID của quiz
        attempt_id: ID của attempt (nếu không có lấy attempt gần nhất)
        current_user: User hiện tại
        
    Returns:
        QuizResultsResponse
        
    Endpoint: GET /api/v1/quizzes/{id}/results?attempt_id=xxx
    """
    user_id = current_user.get("user_id")
    
    # Lấy quiz
    quiz = await quiz_service.get_quiz_by_id(quiz_id)
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz không tồn tại"
        )
    
    # Lấy attempt
    if attempt_id:
        attempt = await quiz_service.get_quiz_attempt_by_id(attempt_id)
        if not attempt or attempt.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attempt không tồn tại"
            )
    else:
        # Lấy attempt gần nhất
        attempts = await quiz_service.get_user_quiz_attempts(user_id, quiz_id)
        if not attempts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chưa có attempt nào"
            )
        attempt = attempts[0]
    
    # Build proper results structure
    results = await quiz_service.build_quiz_results(quiz, attempt)
    
    return QuizResultsResponse(
        attempt_id=str(attempt.id),
        quiz_id=str(quiz.id),
        total_score=attempt.score,
        status=attempt.status,
        pass_threshold=quiz.passing_score,
        results=results.get("question_results", []),
        mandatory_passed=attempt.mandatory_passed,
        can_retake=attempt.can_retake
    )


# ============================================================================
# Section 2.4.6: LÀM LẠI QUIZ
# ============================================================================

async def handle_retake_quiz(
    quiz_id: str,
    current_user: Dict
) -> QuizRetakeResponse:
    """
    2.4.6: Tạo quiz mới với câu hỏi tương tự (AI generated)
    
    Flow:
    - Lấy quiz gốc
    - Sử dụng AI để sinh câu hỏi mới (similar difficulty)
    - Tạo quiz mới
    - Return quiz_id mới
    
    Args:
        quiz_id: ID của quiz gốc
        current_user: User hiện tại
        
    Returns:
        QuizRetakeResponse (new_quiz_id)
        
    Endpoint: POST /api/v1/quizzes/{id}/retake
    """
    user_id = current_user.get("user_id")
    
    # Lấy quiz gốc
    original_quiz = await quiz_service.get_quiz_by_id(quiz_id)
    if not original_quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz không tồn tại"
        )
    
    # Kiểm tra enrollment
    if original_quiz.course_id:
        enrollment = await enrollment_service.get_user_enrollment(user_id, original_quiz.course_id)
        if not enrollment or enrollment.status == "cancelled":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn cần đăng ký khóa học"
            )
    
    # Generate new quiz attempt
    new_attempt = await quiz_service.create_new_attempt(user_id, original_quiz.id)
    
    # Sinh quiz mới bằng AI
    new_quiz = await quiz_service.generate_retake_quiz(original_quiz)
    
    return QuizRetakeResponse(
        new_attempt_id=str(new_attempt.id),
        quiz_id=str(original_quiz.id),
        message="Quiz mới đã được tạo với câu hỏi tương tự",
        questions=[
            RetakeQuestion(
                id=str(q.get("id", "")),
                content=q.get("question_text", ""),
                options=q.get("options", [])
            ) for q in new_quiz.questions
        ]
    )


# ============================================================================
# Section 2.4.7: SINH BÀI TẬP THỰC HÀNH
# ============================================================================

async def handle_generate_practice_exercises(
    request: PracticeExercisesGenerateRequest,
    current_user: Dict
) -> PracticeExercisesGenerateResponse:
    """
    2.4.7: Sinh bài tập thực hành tự động bằng AI
    
    Logic đơn giản: AI sinh bài tập dựa trên topic/lesson/course
    KHÔNG cần phân tích câu trả lời sai
    
    Args:
        request: PracticeExercisesGenerateRequest
        current_user: User hiện tại
        
    Returns:
        PracticeExercisesGenerateResponse
        
    Endpoint: POST /api/v1/ai/generate-practice
    """
    from models.models import Lesson, Course
    import uuid
    
    user_id = current_user.get("user_id")
    
    # 1. VALIDATE: Phải có ít nhất 1 trong 3
    if not request.lesson_id and not request.course_id and not request.topic_prompt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phải cung cấp ít nhất một trong: lesson_id, course_id, hoặc topic_prompt"
        )
    
    # 2. VERIFY & GET CONTEXT: Kiểm tra lesson/course tồn tại và lấy context
    lesson_title = None
    course_title = None
    learning_outcomes = []
    content_summary = ""
    
    if request.lesson_id:
        try:
            lesson = await Lesson.get(request.lesson_id)
            if not lesson:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy lesson với ID: {request.lesson_id}"
                )
            lesson_title = lesson.title
            
            # Get lesson content for context
            if hasattr(lesson, 'content') and lesson.content:
                # Extract text from content (limit to first 200 chars)
                content_summary = str(lesson.content)[:200]
            
            if hasattr(lesson, 'description') and lesson.description:
                content_summary = lesson.description[:200]
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy lesson với ID: {request.lesson_id}"
            )
    
    if request.course_id:
        try:
            course = await course_service.get_course_by_id(request.course_id)
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy course với ID: {request.course_id}"
                )
            course_title = course.title
            
            # Get learning outcomes from course modules
            if hasattr(course, 'modules') and course.modules:
                for module in course.modules[:3]:  # First 3 modules for context
                    if hasattr(module, 'learning_outcomes') and module.learning_outcomes:
                        for outcome in module.learning_outcomes:
                            if isinstance(outcome, dict):
                                learning_outcomes.append({
                                    "description": outcome.get("description", ""),
                                    "skill_tag": outcome.get("skill_tag", "")
                                })
                            elif hasattr(outcome, 'description'):
                                learning_outcomes.append({
                                    "description": outcome.description,
                                    "skill_tag": getattr(outcome, 'skill_tag', '')
                                })
            
            # Get course description
            if hasattr(course, 'description') and course.description:
                content_summary = course.description[:200]
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy course với ID: {request.course_id}"
            )
    
    # 3. PREPARE: Xác định topic và context để sinh bài tập
    topic = request.topic_prompt
    if not topic:
        if lesson_title:
            topic = f"Bài tập luyện tập cho lesson: {lesson_title}"
        elif course_title:
            topic = f"Bài tập luyện tập cho course: {course_title}"
        else:
            topic = "Bài tập luyện tập tổng hợp"
    
    # 4. GENERATE: Gọi AI service để sinh bài tập
    import sys
    print(f"\n🔍 DEBUG: Generating practice exercises", flush=True)
    print(f"  Topic: {topic}", flush=True)
    print(f"  Difficulty: {request.difficulty}", flush=True)
    print(f"  Question count: {request.question_count}", flush=True)
    print(f"  Practice type: {request.practice_type}", flush=True)
    print(f"  Learning outcomes: {len(learning_outcomes)}", flush=True)
    print(f"  Content summary length: {len(content_summary)}", flush=True)
    
    try:
        print(f"  Calling ai_service.generate_practice_exercises...", flush=True)
        exercises_data = await ai_service.generate_practice_exercises(
            topic=topic,
            difficulty=request.difficulty,
            question_count=request.question_count,
            practice_type=request.practice_type,
            focus_skills=request.focus_skills,
            learning_outcomes=learning_outcomes,  # ← THÊM CONTEXT
            content_summary=content_summary  # ← THÊM CONTEXT
        )
        
        print(f"  AI service returned: {len(exercises_data.get('exercises', []))} exercises", flush=True)
        
        # Convert to Exercise schema
        exercises = []
        for ex in exercises_data.get("exercises", []):
            exercises.append(Exercise(
                id=ex.get("id", str(uuid.uuid4())),
                type=ex.get("type", "theory"),
                question=ex.get("question", ""),
                options=ex.get("options"),
                correct_answer=ex.get("correct_answer", ""),
                explanation=ex.get("explanation", ""),
                difficulty=ex.get("difficulty", request.difficulty.capitalize()),
                related_skill=ex.get("related_skill", "general"),
                points=ex.get("points", 10)
            ))
        
        print(f"  ✅ Successfully converted {len(exercises)} exercises")
        
    except Exception as e:
        # Fallback nếu AI service fail
        import traceback
        print(f"\n❌ AI service failed!")
        print(f"  Error type: {type(e).__name__}")
        print(f"  Error message: {str(e)}")
        print(f"  Traceback:")
        traceback.print_exc()
        exercises = []
    
    # 5. RETURN: Response
    return PracticeExercisesGenerateResponse(
        practice_id=str(uuid.uuid4()),
        source=SourceInfo(
            lesson_id=request.lesson_id,
            course_id=request.course_id,
            topic_prompt=request.topic_prompt
        ),
        difficulty=request.difficulty,
        exercises=exercises,
        total_questions=len(exercises),
        estimated_time=len(exercises) * 2,  # 2 phút/câu
        created_at=datetime.utcnow(),
        message="Bài luyện tập đã được tạo thành công" if exercises else "Chức năng đang phát triển - sẽ tích hợp AI service"
    )


# ============================================================================
# INSTRUCTOR FEATURES - Section 3.3.1-3.3.5
# ============================================================================

async def handle_create_quiz(
    lesson_id: str,
    request: QuizCreateRequest,
    current_user: Dict
) -> QuizCreateResponse:
    """
    3.3.1: Instructor tạo quiz mới cho lesson
    
    Business logic:
    - Verify instructor role
    - Validate lesson exists
    - Create quiz with all configurations
    - Calculate total_points và mandatory_count
    - Generate preview_url
    
    Args:
        lesson_id: ID của lesson
        request: QuizCreateRequest
        current_user: User hiện tại
        
    Returns:
        QuizCreateResponse
        
    Raises:
        403: Không phải instructor
        404: Lesson không tồn tại
        400: Invalid data
        
    Endpoint: POST /api/v1/lessons/{lesson_id}/quizzes
    """
    from models.models import Lesson
    from schemas.quiz import QuizCreateResponse
    
    user_id = current_user.get("user_id")
    role = current_user.get("role")
    
    # Check instructor role
    if role != "instructor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ instructor mới có quyền tạo quiz"
        )
    
    # Validate lesson exists
    lesson = await Lesson.get(lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson không tồn tại"
        )
    
    # Validate questions
    if not request.questions or len(request.questions) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz phải có ít nhất 1 câu hỏi"
        )
    
    # Convert QuestionCreate objects to dict
    questions_data = []
    total_points = 0
    mandatory_count = 0
    
    for q in request.questions:
        q_dict = {
            "question_id": str(q.order),
            "type": q.type,
            "question_text": q.question_text,
            "options": q.options,
            "correct_answer": q.correct_answer,
            "explanation": q.explanation,
            "points": q.points,
            "is_mandatory": q.is_mandatory,
            "order": q.order
        }
        questions_data.append(q_dict)
        total_points += q.points
        if q.is_mandatory:
            mandatory_count += 1
    
    # Create quiz
    try:
        quiz = await quiz_service.create_quiz(
            lesson_id=lesson_id,
            course_id=lesson.course_id,
            created_by=user_id,
            title=request.title,
            description=request.description,
            questions=questions_data,
            time_limit_minutes=request.time_limit,
            passing_score=request.pass_threshold,
            max_attempts=request.max_attempts if request.max_attempts else 3
        )
        
        # Generate preview URL
        preview_url = f"/api/v1/quizzes/{quiz.id}/preview"
        
        return QuizCreateResponse(
            quiz_id=str(quiz.id),
            lesson_id=lesson_id,
            title=quiz.title,
            description=quiz.description,
            time_limit=quiz.time_limit_minutes or 0,
            pass_threshold=int(quiz.passing_score),
            max_attempts=quiz.max_attempts,
            deadline=request.deadline,
            is_draft=request.is_draft if request.is_draft is not None else False,
            question_count=len(questions_data),
            total_points=total_points,
            mandatory_count=mandatory_count,
            created_at=quiz.created_at,
            preview_url=preview_url,
            message="Quiz đã được tạo thành công"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo quiz: {str(e)}"
        )


async def handle_list_quizzes_with_filters(
    course_id: Optional[str],
    class_id: Optional[str],
    search: Optional[str],
    sort_by: str,
    sort_order: str,
    skip: int,
    limit: int,
    current_user: Dict
) -> QuizListResponse:
    """
    3.3.2: List quizzes với filters (instructor)
    
    Business logic:
    - Get instructor_id from JWT
    - Filter by course_id, class_id
    - Search in title/description
    - Sort by created_at/title/pass_rate
    - Paginate results
    - Calculate stats for each quiz
    
    Args:
        course_id, class_id, search, sort_by, sort_order, skip, limit
        current_user: User hiện tại
        
    Returns:
        QuizListResponse
        
    Endpoint: GET /api/v1/quizzes?role=instructor&course_id=xxx&class_id=xxx&search=xxx&sort_by=created_at&sort_order=desc&skip=0&limit=20
    """
    from schemas.quiz import QuizListResponse
    
    instructor_id = current_user.get("user_id")
    role = current_user.get("role")
    
    # Check instructor role
    if role != "instructor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ instructor mới có quyền xem danh sách này"
        )
    
    try:
        result = await quiz_service.list_quizzes_with_filters(
            instructor_id=instructor_id,
            course_id=course_id,
            class_id=class_id,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=limit
        )
        
        return QuizListResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy danh sách quiz: {str(e)}"
        )


async def handle_update_quiz(
    quiz_id: str,
    request: QuizUpdateRequest,
    current_user: Dict
) -> QuizUpdateResponse:
    """
    3.3.3: Update quiz (instructor)
    
    Business logic:
    - Verify instructor role and ownership
    - Count existing attempts - if > 0, add warning
    - Allow update but suggest new version
    - Update all provided fields
    - Process question actions (add/update/delete)
    
    Args:
        quiz_id: ID của quiz
        request: QuizUpdateRequest
        current_user: User hiện tại
        
    Returns:
        QuizUpdateResponse
        
    Raises:
        403: Không phải owner
        404: Quiz không tồn tại
        
    Endpoint: PUT /api/v1/quizzes/{quiz_id}
    """
    from schemas.quiz import QuizUpdateResponse
    
    instructor_id = current_user.get("user_id")
    role = current_user.get("role")
    
    # Check instructor role
    if role != "instructor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ instructor mới có quyền update quiz"
        )
    
    # Build update dict from request
    update_data = {}
    
    if request.title is not None:
        update_data["title"] = request.title
    
    if request.description is not None:
        update_data["description"] = request.description
    
    if request.time_limit is not None:
        update_data["time_limit_minutes"] = request.time_limit
    
    if request.pass_threshold is not None:
        update_data["passing_score"] = request.pass_threshold
    
    if request.max_attempts is not None:
        update_data["max_attempts"] = request.max_attempts
    
    # Process questions if provided
    if request.questions is not None:
        # Get current quiz to process actions
        quiz = await quiz_service.get_quiz_by_id(quiz_id)
        
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz không tồn tại"
            )
        
        current_questions = quiz.questions.copy()
        
        # Process each question action
        for q_update in request.questions:
            if q_update.action == "add":
                # Add new question
                new_q = {
                    "question_id": q_update.question_id or str(q_update.order),
                    "type": q_update.type,
                    "question_text": q_update.question_text,
                    "options": q_update.options,
                    "correct_answer": q_update.correct_answer,
                    "explanation": q_update.explanation,
                    "points": q_update.points,
                    "is_mandatory": q_update.is_mandatory,
                    "order": q_update.order
                }
                current_questions.append(new_q)
            
            elif q_update.action == "update":
                # Update existing question
                for i, q in enumerate(current_questions):
                    if q.get("question_id") == q_update.question_id:
                        current_questions[i] = {
                            "question_id": q_update.question_id,
                            "type": q_update.type,
                            "question_text": q_update.question_text,
                            "options": q_update.options,
                            "correct_answer": q_update.correct_answer,
                            "explanation": q_update.explanation,
                            "points": q_update.points,
                            "is_mandatory": q_update.is_mandatory,
                            "order": q_update.order
                        }
                        break
            
            elif q_update.action == "delete":
                # Delete question
                current_questions = [
                    q for q in current_questions
                    if q.get("question_id") != q_update.question_id
                ]
        
        update_data["questions"] = current_questions
    
    try:
        result = await quiz_service.update_quiz_instructor(
            quiz_id=quiz_id,
            instructor_id=instructor_id,
            **update_data
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz không tồn tại"
            )
        
        return QuizUpdateResponse(**result)
        
    except Exception as e:
        if "Unauthorized" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không phải người tạo quiz này"
            )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi update quiz: {str(e)}"
        )


async def handle_delete_quiz(
    quiz_id: str,
    current_user: Dict
) -> QuizDeleteResponse:
    """
    3.3.4: Xóa quiz (instructor)
    
    Business logic:
    - Verify instructor role and ownership
    - Count attempts - if > 0, REJECT delete
    - Only allow delete if no attempts
    
    Args:
        quiz_id: ID của quiz
        current_user: User hiện tại
        
    Returns:
        QuizDeleteResponse
        
    Raises:
        403: Không phải owner hoặc có attempts
        404: Quiz không tồn tại
        
    Endpoint: DELETE /api/v1/quizzes/{quiz_id}
    """
    from schemas.quiz import QuizDeleteResponse
    
    instructor_id = current_user.get("user_id")
    role = current_user.get("role")
    
    # Check instructor role
    if role != "instructor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ instructor mới có quyền xóa quiz"
        )
    
    try:
        result = await quiz_service.delete_quiz_instructor(
            quiz_id=quiz_id,
            instructor_id=instructor_id
        )
        
        return QuizDeleteResponse(**result)
        
    except Exception as e:
        error_msg = str(e)
        
        if "không tồn tại" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )
        
        if "Unauthorized" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không phải người tạo quiz này"
            )
        
        if "Không thể xóa" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xóa quiz: {error_msg}"
        )


async def handle_get_class_quiz_results(
    quiz_id: str,
    class_id: str,
    current_user: Dict
) -> QuizClassResultsResponse:
    """
    3.3.5: Xem kết quả quiz của cả lớp (instructor)
    
    Business logic:
    - Verify instructor role
    - Get all students in class
    - Get all quiz attempts
    - Calculate statistics (avg, median, pass rate, etc.)
    - Build histogram (score distribution)
    - Rank students by score
    - Find difficult questions
    
    Args:
        quiz_id: ID của quiz
        class_id: ID của class
        current_user: User hiện tại
        
    Returns:
        QuizClassResultsResponse
        
    Raises:
        403: Không phải instructor
        404: Quiz hoặc class không tồn tại
        
    Endpoint: GET /api/v1/quizzes/{quiz_id}/class-results?class_id={class_id}
    """
    from schemas.quiz import QuizClassResultsResponse
    
    role = current_user.get("role")
    
    # Check instructor role
    if role != "instructor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ instructor mới có quyền xem kết quả lớp"
        )
    
    try:
        result = await quiz_service.get_class_quiz_results(
            quiz_id=quiz_id,
            class_id=class_id
        )
        
        return QuizClassResultsResponse(**result)
        
    except Exception as e:
        error_msg = str(e)
        
        if "không tồn tại" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy kết quả lớp: {error_msg}"
        )
