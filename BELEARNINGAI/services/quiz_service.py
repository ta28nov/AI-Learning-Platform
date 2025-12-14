"""
Quiz Service - Xử lý quiz/bài kiểm tra trong lesson
Sử dụng: Beanie ODM, MongoDB
Tuân thủ: CHUCNANG.md Section 2.4.3-2.4.7
"""

from datetime import datetime
from typing import Optional, List, Dict
import copy
import random
from models.models import Quiz, QuizAttempt, Class, User, Lesson, Course, Enrollment


# ============================================================================
# QUIZ CRUD
# ============================================================================

async def create_quiz(
    lesson_id: str,
    course_id: str,
    created_by: str,
    title: str,
    description: str,
    questions: List[Dict],
    time_limit_minutes: Optional[int] = None,
    passing_score: float = 70.0,
    max_attempts: int = 3
) -> Quiz:
    """
    Tạo quiz mới cho lesson
    
    Args:
        lesson_id: ID của lesson
        course_id: ID của course
        created_by: ID của người tạo
        title: Tiêu đề quiz
        description: Mô tả
        questions: List câu hỏi
        time_limit_minutes: Giới hạn thời gian
        passing_score: Điểm đạt
        max_attempts: Số lần thử tối đa
        
    Returns:
        Quiz document đã tạo
    """
    quiz = Quiz(
        lesson_id=lesson_id,
        course_id=course_id,
        created_by=created_by,
        title=title,
        description=description,
        questions=questions,
        time_limit_minutes=time_limit_minutes,
        passing_score=passing_score,
        max_attempts=max_attempts
    )
    
    await quiz.insert()
    return quiz


async def get_quiz_by_id(quiz_id: str) -> Optional[Quiz]:
    """
    Lấy quiz theo ID
    
    Args:
        quiz_id: ID của quiz
        
    Returns:
        Quiz document hoặc None
    """
    try:
        quiz = await Quiz.get(quiz_id)
        return quiz
    except Exception:
        return None


async def get_quizzes_by_lesson(lesson_id: str) -> List[Quiz]:
    """
    Lấy tất cả quizzes của một lesson
    
    Args:
        lesson_id: ID của lesson
        
    Returns:
        List Quiz documents
    """
    quizzes = await Quiz.find(Quiz.lesson_id == lesson_id).to_list()
    return quizzes


async def get_quizzes_by_course(
    course_id: str,
    skip: int = 0,
    limit: int = 50
) -> List[Quiz]:
    """
    Lấy tất cả quizzes của một course
    
    Args:
        course_id: ID của course
        skip: Pagination skip
        limit: Pagination limit
        
    Returns:
        List Quiz documents
    """
    quizzes = await Quiz.find(
        Quiz.course_id == course_id
    ).skip(skip).limit(limit).to_list()
    
    return quizzes


async def update_quiz(
    quiz_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    questions: Optional[List[Dict]] = None,
    passing_score: Optional[float] = None
) -> Optional[Quiz]:
    """
    Cập nhật quiz
    
    Args:
        quiz_id: ID của quiz
        title, description, questions, passing_score: Fields cần update
        
    Returns:
        Quiz document đã update hoặc None
    """
    quiz = await get_quiz_by_id(quiz_id)
    
    if not quiz:
        return None
    
    if title is not None:
        quiz.title = title
    
    if description is not None:
        quiz.description = description
    
    if questions is not None:
        quiz.questions = questions
    
    if passing_score is not None:
        quiz.passing_score = passing_score
    
    quiz.updated_at = datetime.utcnow()
    await quiz.save()
    return quiz


async def delete_quiz(quiz_id: str) -> bool:
    """
    Xóa quiz
    
    Args:
        quiz_id: ID của quiz
        
    Returns:
        True nếu xóa thành công, False nếu không tìm thấy
    """
    quiz = await get_quiz_by_id(quiz_id)
    
    if not quiz:
        return False
    
    await quiz.delete()
    return True


# ============================================================================
# QUIZ ATTEMPT (Section 2.4.4-2.4.7)
# ============================================================================

async def create_quiz_attempt(
    quiz_id: str,
    user_id: str,
    answers: Optional[List[Dict]] = None,
    score: Optional[float] = None,
    passed: Optional[bool] = None,
    time_spent_minutes: Optional[int] = None
) -> Optional[QuizAttempt]:
    """
    Tạo và lưu lần thử quiz
    
    Args:
        quiz_id: ID của quiz
        user_id: ID của user
        answers: List câu trả lời (optional - nếu đã chấm điểm)
        score: Điểm số (optional - nếu đã chấm điểm)
        passed: Kết quả đậu/rớt (optional - nếu đã chấm điểm)
        time_spent_minutes: Thời gian làm bài (phút)
        
    Returns:
        QuizAttempt document đã tạo hoặc None nếu đã hết lượt thử
    """
    quiz = await get_quiz_by_id(quiz_id)
    
    if not quiz:
        return None
    
    # Kiểm tra số lần đã thử
    previous_attempts = await get_user_quiz_attempts(user_id, quiz_id)
    attempt_number = len(previous_attempts) + 1
    
    if len(previous_attempts) >= quiz.max_attempts and quiz.max_attempts > 0:
        return None  # Đã hết lượt thử
    
    # Tính thông tin chi tiết nếu có answers
    correct_answers = 0
    total_questions = len(quiz.questions)
    mandatory_correct = 0
    mandatory_total = sum(1 for q in quiz.questions if q.get("is_mandatory", False))
    
    if answers and score is not None:
        # Handle both dict and Pydantic model answers
        answer_map = {}
        for ans in answers:
            if hasattr(ans, 'question_id'):
                answer_map[ans.question_id] = ans
            else:
                answer_map[ans.get("question_id")] = ans
        
        for question in quiz.questions:
            q_id = question.get("question_id") or question.get("id")
            user_answer_obj = answer_map.get(q_id)
            
            # Extract answer from Pydantic model or dict
            if user_answer_obj:
                if hasattr(user_answer_obj, 'selected_option'):
                    user_answer = user_answer_obj.selected_option
                elif hasattr(user_answer_obj, 'answer'):
                    user_answer = user_answer_obj.answer
                else:
                    user_answer = user_answer_obj.get("answer") or user_answer_obj.get("student_answer")
            else:
                user_answer = None
            
            correct_answer = question.get("correct_answer")
            is_mandatory = question.get("is_mandatory", False)
            
            if str(user_answer).strip().lower() == str(correct_answer).strip().lower():
                correct_answers += 1
                if is_mandatory:
                    mandatory_correct += 1
    
    mandatory_passed = (mandatory_correct == mandatory_total) if mandatory_total > 0 else True
    
    # Convert AnswerItem objects to dicts if needed
    answers_list = []
    if answers:
        for ans in answers:
            if hasattr(ans, 'model_dump'):
                answers_list.append(ans.model_dump())
            elif isinstance(ans, dict):
                answers_list.append(ans)
            else:
                # Handle AnswerItem with direct attributes
                answers_list.append({
                    "question_id": getattr(ans, 'question_id', ''),
                    "selected_option": getattr(ans, 'selected_option', '')
                })
    
    attempt = QuizAttempt(
        quiz_id=quiz_id,
        user_id=user_id,
        answers=answers_list,
        score=score or 0.0,
        status="Pass" if passed else "Fail",
        passed=passed or False,
        attempt_number=attempt_number,
        correct_answers=correct_answers,
        total_questions=total_questions,
        mandatory_correct=mandatory_correct,
        mandatory_total=mandatory_total,
        mandatory_passed=mandatory_passed,
        submitted_at=datetime.utcnow() if answers else None,
        time_spent_seconds=(time_spent_minutes * 60) if time_spent_minutes else 0,
        can_retake=attempt_number < quiz.max_attempts
    )
    
    await attempt.insert()
    return attempt


async def submit_quiz_attempt(
    attempt_id: str,
    answers: List[Dict]
) -> Optional[QuizAttempt]:
    """
    Submit câu trả lời quiz và tính điểm
    
    Args:
        attempt_id: ID của attempt
        answers: List câu trả lời dạng [{"question_id": "q1", "answer": "A"}, ...]
        
    Returns:
        QuizAttempt document đã đánh giá hoặc None
    """
    attempt = await get_quiz_attempt(attempt_id)
    
    if not attempt:
        return None
    
    if attempt.submitted_at:
        return None  # Đã submit rồi
    
    quiz = await get_quiz_by_id(attempt.quiz_id)
    
    if not quiz:
        return None
    
    # Tính điểm
    correct_count = 0
    total_count = len(quiz.questions)
    
    answer_map = {ans["question_id"]: ans["answer"] for ans in answers}
    
    for question in quiz.questions:
        q_id = question.get("question_id") or question.get("id")
        user_answer = answer_map.get(q_id)
        correct_answer = question.get("correct_answer")
        
        if user_answer == correct_answer:
            correct_count += 1
    
    score = (correct_count / total_count * 100) if total_count > 0 else 0
    passed = score >= quiz.passing_score
    
    # Lưu kết quả
    attempt.answers = answers
    attempt.score = score
    attempt.passed = passed
    attempt.submitted_at = datetime.utcnow()
    attempt.time_spent_seconds = int(
        (attempt.submitted_at - attempt.started_at).total_seconds()
    )
    
    await attempt.save()
    return attempt


async def get_quiz_attempt(attempt_id: str) -> Optional[QuizAttempt]:
    """
    Lấy quiz attempt theo ID
    
    Args:
        attempt_id: ID của attempt
        
    Returns:
        QuizAttempt document hoặc None
    """
    try:
        attempt = await QuizAttempt.get(attempt_id)
        return attempt
    except Exception:
        return None


# Alias for compatibility
async def get_quiz_attempt_by_id(attempt_id: str) -> Optional[QuizAttempt]:
    """
    Alias for get_quiz_attempt - for compatibility with controller
    """
    return await get_quiz_attempt(attempt_id)


async def get_user_quiz_attempts(
    user_id: str,
    quiz_id: str
) -> List[QuizAttempt]:
    """
    Lấy tất cả attempts của user cho quiz
    
    Args:
        user_id: ID của user
        quiz_id: ID của quiz
        
    Returns:
        List QuizAttempt documents
    """
    attempts = await QuizAttempt.find(
        QuizAttempt.user_id == user_id,
        QuizAttempt.quiz_id == quiz_id
    ).to_list()
    
    return attempts


async def get_best_quiz_score(user_id: str, quiz_id: str) -> Optional[float]:
    """
    Lấy điểm cao nhất của user cho quiz
    
    Args:
        user_id: ID của user
        quiz_id: ID của quiz
        
    Returns:
        Điểm cao nhất hoặc None nếu chưa làm
    """
    attempts = await get_user_quiz_attempts(user_id, quiz_id)
    
    if not attempts:
        return None
    
    # Lấy attempt có submitted_at (đã submit)
    submitted = [a for a in attempts if a.submitted_at]
    
    if not submitted:
        return None
    
    return max(a.score for a in submitted)


async def grade_quiz_attempt(quiz: Quiz, answers: List[Dict]) -> tuple[float, bool]:
    """
    Chấm điểm quiz attempt
    
    Business logic:
    - Tính điểm: % câu đúng
    - Pass nếu: score >= passing_score VÀ tất cả mandatory questions correct
    
    Args:
        quiz: Quiz object
        answers: List câu trả lời từ user [{"question_id": "...", "answer": "..."}, ...]
        
    Returns:
        tuple (score: float, passed: bool)
    """
    print(f"\n🔍 DEBUG: Starting grade_quiz_attempt")
    print(f"📊 Total questions in quiz: {len(quiz.questions)}")
    print(f"📝 Total answers from user: {len(answers)}")
    
    correct_count = 0
    total_count = len(quiz.questions)
    mandatory_correct = 0
    mandatory_total = sum(1 for q in quiz.questions if q.get("is_mandatory", False))
    
    # Convert AnswerItem objects to dict for processing
    answer_map = {}
    for ans in answers:
        if hasattr(ans, 'question_id'):
            # AnswerItem object - access as attributes
            answer_map[ans.question_id] = ans.selected_option
            print(f"  📌 User answer: question_id={ans.question_id}, selected_option={ans.selected_option}")
        else:
            # Already a dict
            q_id = ans["question_id"]
            answer = ans.get("answer") or ans.get("student_answer") or ans.get("selected_option")
            answer_map[q_id] = answer
            print(f"  📌 User answer: question_id={q_id}, answer={answer}")
    
    print(f"\n🔍 Checking each question:")
    for idx, question in enumerate(quiz.questions):
        q_id = question.get("question_id") or question.get("id")
        user_answer = answer_map.get(q_id)
        correct_answer = question.get("correct_answer")
        is_mandatory = question.get("is_mandatory", False)
        
        print(f"\n  Question {idx + 1}:")
        print(f"    question_id: {q_id}")
        print(f"    user_answer: {user_answer}")
        print(f"    correct_answer: {correct_answer}")
        print(f"    is_mandatory: {is_mandatory}")
        
        if user_answer is None:
            print(f"    ❌ No answer found for this question_id!")
            continue
        
        if correct_answer is None:
            print(f"    ❌ No correct_answer in DB!")
            continue
        
        # Normalize for comparison
        user_ans_normalized = str(user_answer).strip().lower()
        correct_ans_normalized = str(correct_answer).strip().lower()
        
        print(f"    Comparing: '{user_ans_normalized}' vs '{correct_ans_normalized}'")
        
        # FLEXIBLE MATCHING:
        # 1. Exact match (case-insensitive)
        # 2. User answer is just option letter (A, B, C, D) and correct answer starts with it
        # 3. Correct answer contains user answer
        is_correct = False
        
        if user_ans_normalized == correct_ans_normalized:
            # Exact match
            is_correct = True
            print(f"    ✅ CORRECT (exact match)!")
        elif len(user_answer.strip()) == 1 and correct_ans_normalized.startswith(user_ans_normalized):
            # User submitted just "A" and correct answer is "a. python -m venv myenv"
            is_correct = True
            print(f"    ✅ CORRECT (option letter match)!")
        elif user_ans_normalized.startswith(correct_ans_normalized):
            # User submitted "A. python -m venv myenv" and correct answer is "A"
            is_correct = True
            print(f"    ✅ CORRECT (user answer starts with correct)!")
        elif correct_ans_normalized.startswith(user_ans_normalized + "."):
            # User submitted "A" and correct answer is "A. ..."
            is_correct = True
            print(f"    ✅ CORRECT (correct answer starts with user + dot)!")
        else:
            print(f"    ❌ WRONG!")
        
        if is_correct:
            correct_count += 1
            if is_mandatory:
                mandatory_correct += 1
    
    score = (correct_count / total_count * 100) if total_count > 0 else 0
    
    # Pass condition: score >= passing_score AND all mandatory questions correct
    mandatory_pass = (mandatory_correct == mandatory_total) if mandatory_total > 0 else True
    passed = (score >= quiz.passing_score) and mandatory_pass
    
    print(f"\n📊 GRADING RESULT:")
    print(f"  Correct: {correct_count}/{total_count}")
    print(f"  Score: {score}%")
    print(f"  Passing score: {quiz.passing_score}%")
    print(f"  Mandatory: {mandatory_correct}/{mandatory_total}")
    print(f"  Mandatory pass: {mandatory_pass}")
    print(f"  Final result: {'PASS' if passed else 'FAIL'}")
    
    return score, passed


async def build_quiz_results(quiz: Quiz, attempt: QuizAttempt) -> Dict:
    """
    Build chi tiết kết quả quiz với explanation
    
    Returns:
        Dict với structure QuizResultsResponse
    """
    answer_map = {ans.get("question_id"): ans for ans in attempt.answers}
    
    question_results = []
    correct_count = 0
    mandatory_correct = 0
    mandatory_total = 0
    
    for question in quiz.questions:
        q_id = question.get("question_id") or question.get("id")
        user_answer_obj = answer_map.get(q_id, {})
        
        # Get user answer from multiple possible fields
        user_answer = (
            user_answer_obj.get("selected_option") or 
            user_answer_obj.get("answer") or 
            user_answer_obj.get("student_answer") or 
            ""  # Default to empty string if None
        )
        
        correct_answer = question.get("correct_answer", "")
        is_mandatory = question.get("is_mandatory", False)
        
        # Use flexible matching logic (same as grade_quiz_attempt)
        is_correct = False
        if user_answer and correct_answer:
            user_ans_normalized = str(user_answer).strip().lower()
            correct_ans_normalized = str(correct_answer).strip().lower()
            
            if user_ans_normalized == correct_ans_normalized:
                is_correct = True
            elif len(str(user_answer).strip()) == 1 and correct_ans_normalized.startswith(user_ans_normalized):
                is_correct = True
            elif user_ans_normalized.startswith(correct_ans_normalized):
                is_correct = True
            elif correct_ans_normalized.startswith(user_ans_normalized + "."):
                is_correct = True
        
        if is_correct:
            correct_count += 1
            if is_mandatory:
                mandatory_correct += 1
        
        if is_mandatory:
            mandatory_total += 1
        
        question_results.append({
            "question_id": q_id,
            "question_content": question.get("question_text", ""),
            "question_type": question.get("type", "multiple_choice"),
            "options": question.get("options"),
            "student_answer": str(user_answer) if user_answer else "",  # Ensure string, never None
            "correct_answer": str(correct_answer) if correct_answer else "",
            "is_correct": is_correct,
            "is_mandatory": is_mandatory,
            "score": question.get("points", 1) if is_correct else 0,
            "explanation": question.get("explanation"),
            "related_lesson_link": f"/lessons/{quiz.lesson_id}" if quiz.lesson_id else None
        })
    
    return {
        "attempt_id": str(attempt.id),
        "quiz_id": str(quiz.id),
        "quiz_title": quiz.title,
        "score": round(attempt.score, 2),
        "passed": attempt.passed,
        "status": "pass" if attempt.passed else "fail",
        "correct_answers": correct_count,
        "total_questions": len(quiz.questions),
        "mandatory_correct": mandatory_correct,
        "mandatory_total": mandatory_total,
        "mandatory_passed": (mandatory_correct == mandatory_total) if mandatory_total > 0 else True,
        "time_spent_seconds": attempt.time_spent_seconds,
        "submitted_at": attempt.submitted_at,
        "can_retake": len(await get_user_quiz_attempts(attempt.user_id, quiz.id)) < quiz.max_attempts,
        "question_results": question_results
    }


async def generate_retake_quiz(original_quiz: Quiz) -> Quiz:
    """
    Generate quiz mới với câu hỏi tương tự (dùng AI)
    
    Args:
        original_quiz: Quiz gốc
        
    Returns:
        Quiz mới đã tạo
    """
    # TODO: Integrate with AI service to generate similar questions
    # For now, duplicate quiz with shuffled questions
    
    new_questions = copy.deepcopy(original_quiz.questions)
    random.shuffle(new_questions)
    
    # Update question IDs
    for i, q in enumerate(new_questions):
        q["question_id"] = f"q{i+1}"
        q["id"] = f"q{i+1}"
        q["order"] = i + 1
    
    new_quiz = Quiz(
        lesson_id=original_quiz.lesson_id,
        course_id=original_quiz.course_id,
        created_by=original_quiz.created_by,
        title=f"{original_quiz.title} (Retake)",
        description=f"Retake version of: {original_quiz.description}",
        questions=new_questions,
        time_limit_minutes=original_quiz.time_limit_minutes,
        passing_score=original_quiz.passing_score,
        max_attempts=original_quiz.max_attempts,
        question_count=len(new_questions),
        total_points=sum(q.get("points", 1) for q in new_questions)
    )
    
    await new_quiz.insert()
    return new_quiz


# ============================================================================
# QUIZ STATISTICS
# ============================================================================

async def get_quiz_stats(quiz_id: str) -> Dict:
    """
    Lấy thống kê cho quiz
    
    Args:
        quiz_id: ID của quiz
        
    Returns:
        Dict chứa thống kê
    """
    attempts = await QuizAttempt.find(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.submitted_at != None
    ).to_list()
    
    if not attempts:
        return {
            "total_attempts": 0,
            "average_score": 0,
            "pass_rate": 0,
            "avg_time_seconds": 0
        }
    
    total = len(attempts)
    avg_score = sum(a.score for a in attempts) / total
    passed = sum(1 for a in attempts if a.passed)
    pass_rate = (passed / total * 100)
    avg_time = sum(a.time_spent_seconds for a in attempts) / total
    
    return {
        "total_attempts": total,
        "average_score": avg_score,
        "pass_rate": pass_rate,
        "avg_time_seconds": int(avg_time)
    }


# ============================================================================
# INSTRUCTOR FEATURES (Section 3.3)
# ============================================================================

async def list_quizzes_with_filters(
    instructor_id: str,
    course_id: Optional[str] = None,
    class_id: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    skip: int = 0,
    limit: int = 20
) -> Dict:
    """
    3.3.2: List quizzes với filters cho instructor
    
    Business logic:
    - Filter by instructor (created_by), course_id, class_id
    - Search by title
    - Sort by created_at, title, question_count, pass_rate
    - Calculate stats for each quiz
    
    Args:
        instructor_id: ID của instructor
        course_id: Filter by course (optional)
        class_id: Filter by class (optional)
        search: Search trong title/description
        sort_by: Field sort
        sort_order: asc hoặc desc
        skip: Pagination skip
        limit: Pagination limit
        
    Returns:
        Dict với data (list QuizListItem), total, skip, limit, has_next
    """
    # Build query
    query_conditions = [Quiz.created_by == instructor_id]
    
    if course_id:
        query_conditions.append(Quiz.course_id == course_id)
    
    if search:
        # MongoDB text search - cần tạo text index trước
        # Tạm thời filter sau khi query
        pass
    
    # Get quizzes
    query = Quiz.find(*query_conditions)
    
    # Sort
    if sort_order == "desc":
        query = query.sort(f"-{sort_by}")
    else:
        query = query.sort(f"+{sort_by}")
    
    # Count total trước khi skip/limit
    total = await query.count()
    
    # Pagination
    quizzes = await query.skip(skip).limit(limit).to_list()
    
    # Search filter sau query (nếu có)
    if search:
        search_lower = search.lower()
        quizzes = [
            q for q in quizzes
            if search_lower in q.title.lower() or
            (q.description and search_lower in q.description.lower())
        ]
        total = len(quizzes)
    
    # Build response với stats
    quiz_items = []
    
    for quiz in quizzes:
        # Lấy lesson info
        lesson = await Lesson.get(quiz.lesson_id) if quiz.lesson_id else None
        lesson_title = lesson.title if lesson else "N/A"
        
        # Lấy course info
        course = await Course.get(quiz.course_id) if quiz.course_id else None
        course_title = course.title if course else "N/A"
        
        # Class info (nếu class_id filter)
        class_name = None
        if class_id:
            class_obj = await Class.get(class_id)
            class_name = class_obj.name if class_obj else None
        
        # Tính stats
        attempts = await QuizAttempt.find(
            QuizAttempt.quiz_id == str(quiz.id),
            QuizAttempt.submitted_at != None
        ).to_list()
        
        total_students = len(set(a.user_id for a in attempts))
        completed_count = len(attempts)
        pass_count = sum(1 for a in attempts if a.passed)
        pass_rate = (pass_count / completed_count * 100) if completed_count > 0 else 0
        avg_score = (sum(a.score for a in attempts) / completed_count) if completed_count > 0 else 0
        
        # Determine status
        status = "active"
        
        quiz_items.append({
            "quiz_id": str(quiz.id),
            "title": quiz.title,
            "description": quiz.description,
            "lesson_id": quiz.lesson_id,
            "lesson_title": lesson_title,
            "course_id": quiz.course_id,
            "course_title": course_title,
            "class_id": class_id,
            "class_name": class_name,
            "status": status,
            "question_count": len(quiz.questions),
            "time_limit": quiz.time_limit_minutes or 0,
            "pass_threshold": int(quiz.passing_score),
            "total_students": total_students,
            "completed_count": completed_count,
            "pass_count": pass_count,
            "pass_rate": round(pass_rate, 2),
            "average_score": round(avg_score, 2),
            "created_at": quiz.created_at,
            "updated_at": quiz.updated_at
        })
    
    has_next = (skip + limit) < total
    
    return {
        "data": quiz_items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_next": has_next
    }


async def check_quiz_attempts_count(quiz_id: str) -> int:
    """
    Kiểm tra số lượng attempts cho quiz
    
    Args:
        quiz_id: ID của quiz
        
    Returns:
        Số lượng attempts
    """
    attempts = await QuizAttempt.find(
        QuizAttempt.quiz_id == quiz_id
    ).to_list()
    
    return len(attempts)


async def update_quiz_instructor(
    quiz_id: str,
    instructor_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    time_limit_minutes: Optional[int] = None,
    passing_score: Optional[float] = None,
    max_attempts: Optional[int] = None,
    questions: Optional[List[Dict]] = None
) -> Dict:
    """
    3.3.3: Update quiz (instructor only)
    
    Business logic:
    - Check quiz ownership (created_by)
    - Count attempts - if > 0, add warning
    - Allow update but warn frontend to suggest new version
    - Update all provided fields
    
    Args:
        quiz_id: ID của quiz
        instructor_id: ID của instructor (verify ownership)
        title, description, time_limit_minutes, passing_score, max_attempts, questions: Fields to update
        
    Returns:
        Dict với quiz_id, title, question_count, has_attempts, attempts_count, warning, updated_at
    """
    quiz = await get_quiz_by_id(quiz_id)
    
    if not quiz:
        return None
    
    # Verify ownership
    if quiz.created_by != instructor_id:
        raise Exception("Unauthorized: Not the creator of this quiz")
    
    # Count attempts
    attempts_count = await check_quiz_attempts_count(quiz_id)
    has_attempts = attempts_count > 0
    
    warning = None
    if has_attempts:
        warning = f"Cảnh báo: {attempts_count} học viên đã làm quiz này. Khuyến nghị tạo phiên bản mới thay vì sửa."
    
    # Update fields
    if title is not None:
        quiz.title = title
    
    if description is not None:
        quiz.description = description
    
    if time_limit_minutes is not None:
        quiz.time_limit_minutes = time_limit_minutes
    
    if passing_score is not None:
        quiz.passing_score = passing_score
    
    if max_attempts is not None:
        quiz.max_attempts = max_attempts
    
    if questions is not None:
        quiz.questions = questions
    
    quiz.updated_at = datetime.utcnow()
    await quiz.save()
    
    return {
        "quiz_id": str(quiz.id),
        "title": quiz.title,
        "question_count": len(quiz.questions),
        "total_points": sum(q.get("points", 0) for q in quiz.questions),
        "has_attempts": has_attempts,
        "attempts_count": attempts_count,
        "warning": warning,
        "updated_at": quiz.updated_at,
        "message": "Quiz đã được cập nhật thành công"
    }


async def delete_quiz_instructor(quiz_id: str, instructor_id: str) -> Dict:
    """
    3.3.4: Delete quiz (instructor only)
    
    Business logic:
    - Check quiz ownership
    - Count attempts - if > 0, REJECT delete
    - Only allow delete if no attempts
    
    Args:
        quiz_id: ID của quiz
        instructor_id: ID của instructor
        
    Returns:
        Dict với quiz_id, message
        
    Raises:
        Exception: Nếu có attempts hoặc không phải owner
    """
    quiz = await get_quiz_by_id(quiz_id)
    
    if not quiz:
        raise Exception("Quiz không tồn tại")
    
    # Verify ownership
    if quiz.created_by != instructor_id:
        raise Exception("Unauthorized: Not the creator of this quiz")
    
    # Count attempts
    attempts_count = await check_quiz_attempts_count(quiz_id)
    
    if attempts_count > 0:
        raise Exception(
            f"Không thể xóa quiz: {attempts_count} học viên đã làm quiz này"
        )
    
    # Delete quiz
    await quiz.delete()
    
    return {
        "quiz_id": str(quiz_id),
        "message": "Quiz đã được xóa thành công"
    }


async def get_class_quiz_results(quiz_id: str, class_id: str) -> Dict:
    """
    3.3.5: Get quiz results for entire class
    
    Business logic:
    - Get all students in class (from enrollments)
    - Get all quiz attempts from those students
    - Calculate statistics: avg, median, highest, lowest, pass rate
    - Build histogram (score distribution)
    - Rank students by score
    - Find difficult questions (lowest correct rate)
    
    Args:
        quiz_id: ID của quiz
        class_id: ID của class
        
    Returns:
        Dict với statistics, score_distribution, student_ranking, difficult_questions
    """
    quiz = await get_quiz_by_id(quiz_id)
    
    if not quiz:
        raise Exception("Quiz không tồn tại")
    
    # Get students in class (enrolled in course with class_id)
    enrollments = await Enrollment.find(
        Enrollment.course_id == quiz.course_id,
        Enrollment.status == "active"
    ).to_list()
    
    student_ids = [e.user_id for e in enrollments]
    
    # Get quiz attempts from these students
    attempts = await QuizAttempt.find(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.submitted_at != None
    ).to_list()
    
    # Filter only students in class
    class_attempts = [a for a in attempts if a.user_id in student_ids]
    
    # Statistics
    total_students = len(student_ids)
    completed_count = len(class_attempts)
    completion_rate = (completed_count / total_students * 100) if total_students > 0 else 0
    
    pass_count = sum(1 for a in class_attempts if a.passed)
    fail_count = completed_count - pass_count
    pass_rate = (pass_count / completed_count * 100) if completed_count > 0 else 0
    
    scores = [a.score for a in class_attempts]
    avg_score = sum(scores) / len(scores) if scores else 0
    median_score = sorted(scores)[len(scores) // 2] if scores else 0
    highest_score = max(scores) if scores else 0
    lowest_score = min(scores) if scores else 0
    
    times = [a.time_spent_seconds / 60 for a in class_attempts]  # Convert to minutes
    avg_time = sum(times) / len(times) if times else 0
    
    statistics = {
        "total_students": total_students,
        "completed_count": completed_count,
        "completion_rate": round(completion_rate, 2),
        "pass_count": pass_count,
        "fail_count": fail_count,
        "pass_rate": round(pass_rate, 2),
        "average_score": round(avg_score, 2),
        "median_score": round(median_score, 2),
        "highest_score": round(highest_score, 2),
        "lowest_score": round(lowest_score, 2),
        "average_time": int(avg_time)
    }
    
    # Score distribution (histogram)
    # Ranges: 0-10, 11-20, ..., 91-100
    score_distribution = []
    ranges = [(i, i + 10) for i in range(0, 100, 10)]
    
    for start, end in ranges:
        count = sum(1 for s in scores if start <= s < end)
        percentage = (count / len(scores) * 100) if scores else 0
        
        score_distribution.append({
            "range": f"{start}-{end-1}" if end < 100 else f"{start}-100",
            "count": count,
            "percentage": round(percentage, 2)
        })
    
    # Student ranking
    # Get best attempt per student
    student_best_attempts = {}
    for attempt in class_attempts:
        uid = attempt.user_id
        if uid not in student_best_attempts or attempt.score > student_best_attempts[uid].score:
            student_best_attempts[uid] = attempt
    
    # Sort by score descending
    ranked_attempts = sorted(
        student_best_attempts.values(),
        key=lambda a: (-a.score, a.time_spent_seconds)
    )
    
    student_ranking = []
    for rank, attempt in enumerate(ranked_attempts[:20], start=1):  # Top 20
        user = await User.get(attempt.user_id)
        
        # Count attempts
        user_attempts = [a for a in class_attempts if a.user_id == attempt.user_id]
        
        student_ranking.append({
            "rank": rank,
            "user_id": attempt.user_id,
            "full_name": user.full_name if user else "Unknown",
            "avatar": user.avatar_url if user else None,
            "score": round(attempt.score, 2),
            "time_spent": int(attempt.time_spent_seconds / 60),
            "attempt_count": len(user_attempts),
            "status": "pass" if attempt.passed else "fail",
            "completed_at": attempt.submitted_at
        })
    
    # Difficult questions (lowest correct rate)
    # Analyze answers across all attempts
    question_stats = {}
    
    for attempt in class_attempts:
        answer_map = {ans["question_id"]: ans["answer"] for ans in attempt.answers}
        
        for question in quiz.questions:
            q_id = question.get("question_id") or question.get("id") or question.get("order")
            
            if q_id not in question_stats:
                question_stats[q_id] = {
                    "question_text": question.get("question_text", ""),
                    "correct_count": 0,
                    "total_count": 0
                }
            
            user_answer = answer_map.get(q_id)
            correct_answer = question.get("correct_answer")
            
            question_stats[q_id]["total_count"] += 1
            if user_answer == correct_answer:
                question_stats[q_id]["correct_count"] += 1
    
    # Calculate correct rate and find hardest questions
    difficult_questions = []
    
    for q_id, stats in question_stats.items():
        total = stats["total_count"]
        correct = stats["correct_count"]
        correct_rate = (correct / total * 100) if total > 0 else 0
        
        difficult_questions.append({
            "question_id": q_id,
            "question_text": stats["question_text"],
            "correct_rate": round(correct_rate, 2),
            "total_answers": total
        })
    
    # Sort by correct_rate ascending (hardest first)
    difficult_questions.sort(key=lambda q: q["correct_rate"])
    difficult_questions = difficult_questions[:3]  # Top 3 hardest
    
    # Get class name
    class_obj = await Class.get(class_id)
    class_name = class_obj.name if class_obj else f"Class {class_id}"
    
    return {
        "quiz_id": quiz_id,
        "quiz_title": quiz.title,
        "class_id": class_id,
        "class_name": class_name,
        "statistics": statistics,
        "score_distribution": score_distribution,
        "student_ranking": student_ranking,
        "difficult_questions": difficult_questions
    }


async def create_new_attempt(user_id: str, quiz_id: str) -> QuizAttempt:
    """Tạo attempt mới cho retake quiz"""
    existing_attempts = await get_user_quiz_attempts(user_id, quiz_id)
    attempt_number = len(existing_attempts) + 1
    
    new_attempt = QuizAttempt(
        quiz_id=quiz_id,
        user_id=user_id,
        attempt_number=attempt_number,
        answers=[],
        score=0.0,
        status="in_progress"
    )
    await new_attempt.insert()
    return new_attempt

