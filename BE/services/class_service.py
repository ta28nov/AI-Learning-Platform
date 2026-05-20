"""
Class Service - Xử lý quản lý lớp học cho Instructor
Sử dụng: Beanie ODM
Tuân thủ: CHUCNANG.md Section 3.1, 3.2
"""

from datetime import datetime
from typing import List, Dict, Optional, Any
import random
import string
from beanie.operators import In
from models.models import Class, User, Course, Enrollment, Progress, QuizAttempt, Quiz


def _lesson_progress_id(lp: Any) -> Optional[str]:
    if hasattr(lp, "lesson_id"):
        return lp.lesson_id
    if isinstance(lp, dict):
        return lp.get("lesson_id")
    return None


def _lesson_progress_status(lp: Any) -> Optional[str]:
    if hasattr(lp, "status"):
        return lp.status
    if isinstance(lp, dict):
        return lp.get("status")
    return None


async def _quiz_attempts_for_course(student_ids: List[str], course_id: str) -> List[QuizAttempt]:
    if not student_ids:
        return []
    quizzes = await Quiz.find(Quiz.course_id == course_id).to_list()
    quiz_ids = [q.id for q in quizzes]
    if not quiz_ids:
        return []
    return await QuizAttempt.find(
        In(QuizAttempt.quiz_id, quiz_ids),
        In(QuizAttempt.user_id, [str(s) for s in student_ids]),
    ).to_list()


async def _find_next_lesson(user_id: str, course_id: str) -> Optional[Dict]:
    """Bài học đầu tiên chưa hoàn thành — cùng logic enrollment/my-courses."""
    enrollment = await Enrollment.find_one(
        Enrollment.user_id == user_id,
        Enrollment.course_id == course_id,
    )
    if not enrollment or enrollment.status == "cancelled":
        return None

    course = await Course.get(course_id)
    if not course or not getattr(course, "modules", None):
        return None

    completed = {str(lid) for lid in (enrollment.completed_lessons or [])}
    for module in course.modules:
        for lesson in module.lessons:
            if str(lesson.id) not in completed:
                return {
                    "lesson_id": str(lesson.id),
                    "lesson_title": lesson.title,
                    "module_title": module.title,
                }
    return None


async def _build_student_class_profile(cls: Class, student_id: str) -> Dict:
    """Hồ sơ tiến độ HV trong lớp — dùng cho instructor drill-down và student my-progress."""
    student_id = str(student_id)
    user = await User.get(student_id)
    if not user:
        raise ValueError("Học viên không tồn tại")

    progress = await Progress.find_one(
        Progress.user_id == student_id,
        Progress.course_id == cls.course_id,
    )

    quiz_attempts = await _quiz_attempts_for_course([student_id], cls.course_id)
    quiz_attempts.sort(key=lambda a: a.started_at or datetime.utcnow(), reverse=True)

    course = await Course.get(cls.course_id)

    quiz_scores = []
    for attempt in quiz_attempts:
        quiz_title = f"Quiz {attempt.quiz_id[:8]}"
        if course:
            for module in course.modules:
                module_quiz_id = getattr(module, "default_quiz_id", None)
                if not module_quiz_id:
                    for lesson in module.lessons:
                        if getattr(lesson, "quiz_id", None):
                            module_quiz_id = lesson.quiz_id
                            break
                if module_quiz_id == attempt.quiz_id:
                    quiz_title = f"Quiz {module.title}"
                    break

        quiz_scores.append({
            "quiz_id": attempt.quiz_id,
            "quiz_title": quiz_title,
            "score": attempt.score,
            "attempt_date": attempt.started_at,
        })

    modules_detail = []
    if course and progress:
        for module in course.modules:
            module_lessons = [l.id for l in module.lessons]
            completed_in_module = sum(
                1
                for lp in progress.lessons_progress
                if _lesson_progress_id(lp) in module_lessons
                and _lesson_progress_status(lp) == "completed"
            )
            module_progress = (
                (completed_in_module / len(module.lessons) * 100) if module.lessons else 0.0
            )

            module_quiz_id = getattr(module, "default_quiz_id", None)
            if not module_quiz_id and module.lessons:
                for lesson in module.lessons:
                    if getattr(lesson, "quiz_id", None):
                        module_quiz_id = lesson.quiz_id
                        break

            module_quiz_scores = [
                qs for qs in quiz_scores
                if module_quiz_id and module_quiz_id == qs["quiz_id"]
            ]

            modules_detail.append({
                "module_id": module.id,
                "module_title": module.title,
                "progress": round(module_progress, 2),
                "completed_lessons": completed_in_module,
                "quiz_scores": module_quiz_scores,
            })

    progress_summary = {
        "overall_progress": progress.overall_progress_percent if progress else 0.0,
        "completed_modules": sum(1 for m in modules_detail if m["progress"] == 100.0),
        "total_modules": len(modules_detail),
        "study_streak_days": progress.study_streak_days if progress else 0,
        "total_study_time": progress.total_time_spent_minutes / 60.0 if progress else 0.0,
    }

    return {
        "student_id": user.id,
        "student_name": user.full_name,
        "email": user.email,
        "avatar_url": user.avatar_url if hasattr(user, "avatar_url") else None,
        "quiz_scores": quiz_scores,
        "modules_detail": modules_detail,
        "progress": progress_summary,
    }


async def get_my_class_progress(class_id: str, user_id: str) -> Dict:
    """Tiến độ cá nhân của HV trong lớp (student self-service)."""
    cls = await Class.get(class_id)
    if not cls:
        raise ValueError("Lớp học không tồn tại hoặc bạn không có quyền truy cập")

    user_id = str(user_id)
    student_ids = [str(s) for s in cls.student_ids]
    if user_id not in student_ids:
        raise ValueError("Lớp học không tồn tại hoặc bạn không có quyền truy cập")

    return await _build_student_class_profile(cls, user_id)


# ============================================================================
# Section 3.1: QUẢN LÝ LỚP HỌC
# ============================================================================

async def create_class(
    instructor_id: str,
    name: str,
    description: str,
    course_id: str,
    start_date: datetime,
    end_date: datetime,
    max_students: int
) -> Dict:
    """
    3.1.1: Tạo lớp học mới
    
    Business Logic:
    1. Validate course_id tồn tại
    2. Generate invite_code (6-8 ký tự unique)
    3. Tạo Class document với status="preparing"
    4. Return class_id và invite_code
    
    Args:
        instructor_id: ID giảng viên
        name: Tên lớp học
        description: Mô tả lớp học
        course_id: ID khóa học làm nền tảng
        start_date: Ngày bắt đầu
        end_date: Ngày kết thúc
        max_students: Số học viên tối đa
        
    Returns:
        Dict chứa class_id, invite_code, status
        
    Raises:
        ValueError: Nếu course_id không tồn tại
    """
    # Validate course exists
    course = await Course.get(course_id)
    if not course:
        raise ValueError("Khóa học không tồn tại")
    
    # Generate unique invite code
    invite_code = await generate_unique_invite_code()
    
    now = datetime.utcnow()
    start_cmp = start_date.replace(tzinfo=None) if start_date.tzinfo else start_date
    initial_status = "active" if start_cmp <= now else "preparing"

    new_class = Class(
        name=name,
        description=description,
        course_id=course_id,
        instructor_id=instructor_id,
        invite_code=invite_code,
        max_students=max_students,
        start_date=start_date,
        end_date=end_date,
        status=initial_status,
        student_ids=[],
    )
    
    await new_class.insert()
    
    return {
        "class_id": new_class.id,
        "name": new_class.name,
        "invite_code": new_class.invite_code,
        "course_title": course.title,
        "student_count": 0,
        "created_at": new_class.created_at,
        "message": "Tạo lớp học thành công"
    }


async def generate_unique_invite_code() -> str:
    """
    Generate mã mời unique (6-8 ký tự)
    
    Returns:
        Invite code duy nhất
    """
    max_attempts = 10
    for _ in range(max_attempts):
        # Generate 8 ký tự random
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # Check uniqueness
        existing = await Class.find_one(Class.invite_code == code)
        if not existing:
            return code
    
    # Fallback: UUID-based
    import uuid
    return str(uuid.uuid4())[:8].upper()


async def list_my_classes(
    user_id: str,
    role: str,
    status_filter: Optional[str] = None,
) -> Dict:
    """
    3.1.2: Danh sách lớp theo vai trò JWT.

    - instructor/admin: lớp do instructor tạo (instructor_id)
    - student: lớp đã tham gia (student_ids)
    """
    if role == "student":
        query: dict = {"student_ids": user_id}
    else:
        query = {"instructor_id": user_id}

    if status_filter:
        query["status"] = status_filter

    classes = await Class.find(query).sort("-created_at").to_list()

    classes_list = []
    for cls in classes:
        course = await Course.get(cls.course_id)
        student_count = len(cls.student_ids)

        if role == "student":
            progress_doc = await Progress.find_one(
                Progress.user_id == user_id,
                Progress.course_id == cls.course_id,
            )
            progress_value = (
                progress_doc.overall_progress_percent if progress_doc else 0.0
            )
            student_count_label = str(student_count)
        else:
            if student_count > 0:
                progress_list = await Progress.find(
                    In(Progress.user_id, [str(s) for s in cls.student_ids]),
                    Progress.course_id == cls.course_id,
                ).to_list()
                progress_value = (
                    sum(p.overall_progress_percent for p in progress_list)
                    / len(progress_list)
                    if progress_list
                    else 0.0
                )
            else:
                progress_value = 0.0
            student_count_label = f"{student_count}/{cls.max_students}"

        instructor = await User.get(cls.instructor_id)
        item = {
            "id": cls.id,
            "name": cls.name,
            "course_id": cls.course_id,
            "course_title": course.title if course else "Unknown",
            "instructor_name": instructor.full_name if instructor else "Giảng viên",
            "student_count": student_count_label,
            "status": cls.status,
            "start_date": cls.start_date,
            "end_date": cls.end_date,
            "progress": round(progress_value, 2),
        }
        if role == "student":
            item["next_lesson"] = await _find_next_lesson(user_id, cls.course_id)
        classes_list.append(item)

    return {
        "classes": classes_list,
        "total": len(classes_list),
    }


async def get_class_detail(class_id: str, user_id: str, role: str) -> Dict:
    """
    3.1.3: Chi tiết lớp — instructor (owner) hoặc student (đã join).

    Student: không trả invite_code; không trả recent_students.
    """
    cls = await Class.get(class_id)
    if not cls:
        raise ValueError("Lớp học không tồn tại hoặc bạn không có quyền truy cập")

    is_student_view = role == "student"
    if is_student_view:
        if user_id not in cls.student_ids:
            raise ValueError("Lớp học không tồn tại hoặc bạn không có quyền truy cập")
    elif role == "admin":
        pass
    elif cls.instructor_id != user_id:
        raise ValueError("Lớp học không tồn tại hoặc bạn không có quyền truy cập")
    
    # Get course
    course = await Course.get(cls.course_id)
    
    # Count modules
    module_count = len(course.modules) if course else 0
    
    instructor = await User.get(cls.instructor_id)
    instructor_name = instructor.full_name if instructor else "Giảng viên"

    students_info = []
    total_lessons_completed = 0
    total_quiz_score = 0.0
    quiz_count = 0

    if is_student_view:
        progress = await Progress.find_one(
            Progress.user_id == user_id,
            Progress.course_id == cls.course_id,
        )
        my_progress = progress.overall_progress_percent if progress else 0.0
        next_lesson = await _find_next_lesson(user_id, cls.course_id)
        stats = {
            "total_students": len(cls.student_ids),
            "lessons_completed": progress.completed_lessons_count if progress else 0,
            "avg_quiz_score": 0.0,
        }
        return {
            "id": cls.id,
            "name": cls.name,
            "description": cls.description,
            "course": {
                "id": cls.course_id,
                "title": course.title if course else "Unknown",
                "module_count": module_count,
            },
            "invite_code": None,
            "instructor_name": instructor_name,
            "max_students": cls.max_students,
            "student_count": len(cls.student_ids),
            "start_date": cls.start_date,
            "end_date": cls.end_date,
            "status": cls.status,
            "my_progress": round(my_progress, 2),
            "next_lesson": next_lesson,
            "recent_students": [],
            "class_stats": stats,
        }

    for student_id in cls.student_ids:
        user = await User.get(student_id)
        if not user:
            continue
        
        # Get progress
        progress = await Progress.find_one(
            Progress.user_id == student_id,
            Progress.course_id == cls.course_id
        )
        
        # Get enrollment to find joined_at
        enrollment = await Enrollment.find_one(
            Enrollment.user_id == student_id,
            Enrollment.course_id == cls.course_id
        )
        
        students_info.append({
            "id": user.id,
            "name": user.full_name,
            "email": user.email,
            "avatar_url": user.avatar_url if hasattr(user, 'avatar_url') else None,
            "progress": progress.overall_progress_percent if progress else 0.0,
            "joined_at": enrollment.enrolled_at if enrollment else cls.created_at
        })
        
        # Accumulate stats
        if progress:
            total_lessons_completed += progress.completed_lessons_count
        
        # Get quiz scores (QuizAttempt has no course_id — join via Quiz)
        quiz_attempts = [
            a for a in await _quiz_attempts_for_course([student_id], cls.course_id)
            if str(a.user_id) == str(student_id)
        ]
        
        for attempt in quiz_attempts:
            total_quiz_score += attempt.score
            quiz_count += 1
    
    # Calculate stats
    stats = {
        "total_students": len(cls.student_ids),
        "lessons_completed": total_lessons_completed,
        "avg_quiz_score": round(total_quiz_score / quiz_count, 2) if quiz_count > 0 else 0.0
    }
    
    return {
        "id": cls.id,
        "name": cls.name,
        "description": cls.description,
        "course": {
            "id": cls.course_id,
            "title": course.title if course else "Unknown",
            "module_count": module_count,
        },
        "invite_code": cls.invite_code,
        "instructor_name": instructor_name,
        "max_students": cls.max_students,
        "student_count": len(cls.student_ids),
        "start_date": cls.start_date,
        "end_date": cls.end_date,
        "status": cls.status,
        "recent_students": students_info,
        "class_stats": stats,
    }


async def update_class(
    class_id: str,
    instructor_id: str,
    update_data: Dict
) -> Dict:
    """
    3.1.4: Chỉnh sửa thông tin lớp
    
    Business Logic:
    1. Find class với ownership check
    2. Validate updates:
       - Không giảm max_students dưới current students
       - Không thay đổi start_date nếu đã bắt đầu
    3. Update allowed fields
    4. Return updated info
    
    Args:
        class_id: ID lớp học
        instructor_id: ID giảng viên
        update_data: Dict chứa fields cần update
        
    Returns:
        Dict với class_id, message, updated_at
        
    Raises:
        ValueError: Nếu validation fails
    """
    # Find class
    cls = await Class.find_one(
        Class.id == class_id,
        Class.instructor_id == instructor_id
    )
    
    if not cls:
        raise ValueError("Lớp học không tồn tại hoặc bạn không có quyền chỉnh sửa")
    
    # Validate max_students
    if "max_students" in update_data:
        new_max = update_data["max_students"]
        current_students = len(cls.student_ids)
        if new_max < current_students:
            raise ValueError(f"Không thể giảm số học viên tối đa xuống dưới {current_students}")
    
    # Validate start_date changes (only if not started)
    if "start_date" in update_data:
        if datetime.utcnow() >= cls.start_date:
            raise ValueError("Không thể thay đổi ngày bắt đầu khi lớp đã bắt đầu")
    
    # Update allowed fields
    if "name" in update_data:
        cls.name = update_data["name"]
    if "description" in update_data:
        cls.description = update_data["description"]
    if "max_students" in update_data:
        cls.max_students = update_data["max_students"]
    if "end_date" in update_data:
        cls.end_date = update_data["end_date"]
    if "status" in update_data:
        cls.status = update_data["status"]
    
    cls.updated_at = datetime.utcnow()
    await cls.save()
    
    return {
        "class_id": cls.id,
        "message": "Cập nhật lớp học thành công",
        "updated_at": cls.updated_at
    }


async def delete_class(class_id: str, instructor_id: str) -> Dict:
    """
    3.1.5: Xóa lớp học
    
    Business Logic:
    1. Find class với ownership check
    2. Validate deletion:
       - Chỉ xóa nếu: no students HOẶC status="completed"
    3. Delete class document
    4. Return confirmation
    
    Args:
        class_id: ID lớp học
        instructor_id: ID giảng viên
        
    Returns:
        Dict với message
        
    Raises:
        ValueError: Nếu không đủ điều kiện xóa
    """
    # Find class
    cls = await Class.find_one(
        Class.id == class_id,
        Class.instructor_id == instructor_id
    )
    
    if not cls:
        raise ValueError("Lớp học không tồn tại hoặc bạn không có quyền xóa")
    
    # Validate deletion conditions
    student_count = len(cls.student_ids)
    if student_count > 0 and cls.status != "completed":
        raise ValueError(f"Không thể xóa lớp đang có {student_count} học viên. Chỉ xóa được khi lớp chưa có học viên hoặc đã hoàn thành.")
    
    # Delete class
    await cls.delete()
    
    return {
        "message": "Đã xóa lớp học thành công"
    }


# ============================================================================
# Section 3.2: QUẢN LÝ HỌC VIÊN TRONG LỚP
# ============================================================================

async def join_class_with_code(user_id: str, invite_code: str) -> Dict:
    """
    3.2.1: Student tham gia lớp bằng mã mời
    
    Business Logic:
    1. Tìm Class theo invite_code
    2. Validate:
       - Class status="active"
       - Chưa đầy (student_count < max_students)
       - User chưa join lớp này
    3. Add user_id vào class.student_ids
    4. Create Enrollment cho user với course
    5. Return class info và enrollment_id
    
    Args:
        user_id: ID học viên
        invite_code: Mã mời
        
    Returns:
        Dict với class info, course_id, enrollment_id
        
    Raises:
        ValueError: Nếu mã mời invalid hoặc lớp đầy
    """
    # Find class by invite code
    cls = await Class.find_one(Class.invite_code == invite_code)
    
    if not cls:
        raise ValueError("Mã mời không hợp lệ")
    
    # Validate class status
    if cls.status != "active":
        raise ValueError("Lớp học không ở trạng thái active")
    
    # Check if full
    if len(cls.student_ids) >= cls.max_students:
        raise ValueError("Lớp học đã đầy")
    
    user_id = str(user_id)
    student_ids = [str(s) for s in cls.student_ids]

    if user_id in student_ids:
        raise ValueError("Bạn đã tham gia lớp học này")

    student_ids.append(user_id)
    cls.student_ids = student_ids
    cls.updated_at = datetime.utcnow()
    await cls.save()
    
    # Create enrollment if not exists
    existing_enrollment = await Enrollment.find_one(
        Enrollment.user_id == user_id,
        Enrollment.course_id == cls.course_id
    )
    
    if not existing_enrollment:
        enrollment = Enrollment(
            user_id=user_id,
            course_id=cls.course_id,
            status="active",
            progress_percent=0.0
        )
        await enrollment.insert()
        enrollment_id = enrollment.id
    else:
        enrollment_id = existing_enrollment.id
    
    # Get course and instructor info
    course = await Course.get(cls.course_id)
    instructor = await User.get(cls.instructor_id)
    
    return {
        "message": "Tham gia lớp học thành công",
        "class_id": cls.id,
        "class_name": cls.name,
        "course_title": course.title if course else "Unknown",
        "course_id": cls.course_id,
        "instructor_name": instructor.full_name if instructor else "Unknown",
        "enrollment_id": enrollment_id,
        "student_count": len(cls.student_ids),
        "max_students": cls.max_students
    }


async def get_class_students(
    class_id: str,
    instructor_id: str,
    skip: int = 0,
    limit: int = 50
) -> Dict:
    """
    3.2.2: Xem danh sách học viên trong lớp
    
    Business Logic:
    1. Find class với ownership check
    2. Query User info cho student_ids
    3. Lấy Progress và QuizAttempt cho mỗi student
    4. Calculate metrics: progress, quiz_average, last_activity
    5. Return paginated list
    
    Args:
        class_id: ID lớp học
        instructor_id: ID giảng viên
        skip: Pagination skip
        limit: Pagination limit
        
    Returns:
        Dict với students list, total, pagination info
    """
    # Find class
    cls = await Class.find_one(
        Class.id == class_id,
        Class.instructor_id == instructor_id
    )
    
    if not cls:
        raise ValueError("Lớp học không tồn tại hoặc bạn không có quyền truy cập")
    
    # Get course
    course = await Course.get(cls.course_id)
    total_modules = len(course.modules) if course else 0
    
    # Paginate student_ids
    paginated_ids = cls.student_ids[skip:skip+limit]
    
    # Get students info
    students_list = []
    for student_id in paginated_ids:
        user = await User.get(student_id)
        if not user:
            continue
        
        # Get enrollment
        enrollment = await Enrollment.find_one(
            Enrollment.user_id == student_id,
            Enrollment.course_id == cls.course_id
        )
        
        # Get progress
        progress = await Progress.find_one(
            Progress.user_id == student_id,
            Progress.course_id == cls.course_id
        )
        
        # Get quiz attempts (QuizAttempt has no course_id — join via Quiz)
        quiz_attempts = [
            a for a in await _quiz_attempts_for_course([student_id], cls.course_id)
            if str(a.user_id) == str(student_id)
        ]
        
        # Calculate quiz average
        if quiz_attempts:
            quiz_avg = sum(a.score for a in quiz_attempts) / len(quiz_attempts)
        else:
            quiz_avg = 0.0
        
        completed_lesson_ids: set[str] = set()
        if enrollment and enrollment.completed_lessons:
            completed_lesson_ids = {str(lid) for lid in enrollment.completed_lessons}
        elif progress:
            completed_lesson_ids = {
                str(_lesson_progress_id(lp))
                for lp in (progress.lessons_progress or [])
                if _lesson_progress_status(lp) == "completed" and _lesson_progress_id(lp)
            }

        completed_modules = 0
        if course and getattr(course, "modules", None):
            for module in course.modules:
                module_lesson_ids = {str(lesson.id) for lesson in module.lessons}
                if module_lesson_ids and module_lesson_ids.issubset(completed_lesson_ids):
                    completed_modules += 1
        
        students_list.append({
            "student_id": user.id,
            "student_name": user.full_name,
            "email": user.email,
            "join_date": enrollment.enrolled_at if enrollment else cls.created_at,
            "progress": progress.overall_progress_percent if progress else 0.0,
            "completed_modules": completed_modules,
            "total_modules": total_modules,
            "last_activity": (
                progress.last_accessed_at
                if progress and progress.last_accessed_at
                else enrollment.last_accessed_at if enrollment and enrollment.last_accessed_at
                else enrollment.enrolled_at if enrollment
                else cls.created_at
            ),
            "quiz_average": round(quiz_avg, 2)
        })
    
    return {
        "class_id": cls.id,
        "class_name": cls.name,
        "data": students_list,
        "total": len(cls.student_ids),
        "skip": skip,
        "limit": limit
    }


async def get_student_detail(
    class_id: str,
    student_id: str,
    instructor_id: str
) -> Dict:
    """
    3.2.3: Xem hồ sơ học viên chi tiết
    
    Business Logic:
    1. Find class với ownership check
    2. Validate student_id in class.student_ids
    3. Get user profile
    4. Get quiz scores detail
    5. Get progress detail per module
    6. Return full student profile
    
    Args:
        class_id: ID lớp học
        student_id: ID học viên
        instructor_id: ID giảng viên
        
    Returns:
        Dict với student profile, quiz scores, progress
    """
    # Find class
    cls = await Class.find_one(
        Class.id == class_id,
        Class.instructor_id == instructor_id
    )
    
    if not cls:
        raise ValueError("Lớp học không tồn tại")

    student_id = str(student_id)
    cls.student_ids = [str(s) for s in cls.student_ids]

    if student_id not in cls.student_ids:
        raise ValueError("Học viên không thuộc lớp này")

    return await _build_student_class_profile(cls, student_id)


async def remove_student(
    class_id: str,
    student_id: str,
    instructor_id: str
) -> Dict:
    """
    3.2.4: Xóa học viên khỏi lớp
    
    Business Logic:
    1. Find class với ownership check
    2. Validate student_id in class.student_ids
    3. Remove student_id from list
    4. Update enrollment status="removed" (KEEP progress data)
    5. Return confirmation
    
    Args:
        class_id: ID lớp học
        student_id: ID học viên
        instructor_id: ID giảng viên
        
    Returns:
        Dict với message
    """
    # Find class
    cls = await Class.find_one(
        Class.id == class_id,
        Class.instructor_id == instructor_id
    )
    
    if not cls:
        raise ValueError("Lớp học không tồn tại")
    
    student_id = str(student_id)
    cls.student_ids = [str(s) for s in cls.student_ids]

    if student_id not in cls.student_ids:
        raise ValueError("Học viên không thuộc lớp này")

    cls.student_ids.remove(student_id)
    cls.updated_at = datetime.utcnow()
    await cls.save()
    
    # Update enrollment status (keep data)
    enrollment = await Enrollment.find_one(
        Enrollment.user_id == student_id,
        Enrollment.course_id == cls.course_id
    )
    
    if enrollment:
        enrollment.status = "cancelled"
        await enrollment.save()
    
    return {
        "message": "Đã xóa học viên khỏi lớp"
    }


async def get_class_progress(class_id: str, instructor_id: str) -> Dict:
    """
    3.2.5: Xem tiến độ tổng thể của lớp
    
    Business Logic:
    1. Find class với ownership check
    2. Query Progress cho tất cả students
    3. Calculate distribution metrics:
       - Score histogram (phân bố điểm)
       - Module completion rates
       - Most/least completed lessons
    4. Return analytics data
    
    Args:
        class_id: ID lớp học
        instructor_id: ID giảng viên
        
    Returns:
        Dict với progress analytics
    """
    # Find class
    cls = await Class.find_one(
        Class.id == class_id,
        Class.instructor_id == instructor_id
    )
    
    if not cls:
        raise ValueError("Lớp học không tồn tại")

    student_ids = [str(s) for s in cls.student_ids]
    total_students = len(student_ids)

    if student_ids:
        progress_list = await Progress.find(
            In(Progress.user_id, student_ids),
            Progress.course_id == cls.course_id,
        ).to_list()
    else:
        progress_list = []

    quiz_attempts = await _quiz_attempts_for_course(student_ids, cls.course_id)

    if progress_list:
        average_progress = sum(p.overall_progress_percent for p in progress_list) / len(progress_list)
        completed_count = sum(1 for p in progress_list if p.overall_progress_percent >= 100)
        completion_rate = (completed_count / total_students * 100) if total_students else 0.0
    else:
        average_progress = 0.0
        completion_rate = 0.0

    if quiz_attempts:
        average_quiz_score = sum(a.score for a in quiz_attempts) / len(quiz_attempts)
    else:
        average_quiz_score = 0.0

    return {
        "class_id": cls.id,
        "class_name": cls.name,
        "total_students": total_students,
        "average_progress": round(average_progress, 2),
        "completion_rate": round(completion_rate, 2),
        "average_quiz_score": round(average_quiz_score, 2),
    }
