"""
Class Service - Xử lý quản lý lớp học cho Instructor
Sử dụng: Beanie ODM
Tuân thủ: CHUCNANG.md Section 3.1, 3.2
"""

from datetime import datetime
from typing import List, Dict, Optional
import random
import string
from models.models import Class, User, Course, Enrollment, Progress, QuizAttempt


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
    
    # Create class
    new_class = Class(
        name=name,
        description=description,
        course_id=course_id,
        instructor_id=instructor_id,
        invite_code=invite_code,
        max_students=max_students,
        start_date=start_date,
        end_date=end_date,
        status="preparing",
        student_ids=[]
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
    instructor_id: str,
    status_filter: Optional[str] = None
) -> Dict:
    """
    3.1.2: Xem danh sách lớp học của instructor
    
    Business Logic:
    1. Query Class với instructor_id
    2. Optional filter theo status
    3. Lấy course_title cho mỗi lớp
    4. Tính student_count và overall progress
    5. Sort theo created_at DESC
    
    Args:
        instructor_id: ID giảng viên
        status_filter: Optional filter (preparing/active/completed)
        
    Returns:
        Dict chứa classes list và total
    """
    # Build query
    query = {"instructor_id": instructor_id}
    if status_filter:
        query["status"] = status_filter
    
    classes = await Class.find(query).sort(-Class.created_at).to_list()
    
    # Format response
    classes_list = []
    for cls in classes:
        # Get course
        course = await Course.get(cls.course_id)
        
        # Calculate student count
        student_count = len(cls.student_ids)
        
        # Calculate overall progress
        if student_count > 0:
            # Query Progress for students in class
            progress_list = await Progress.find(
                Progress.user_id.in_(cls.student_ids),
                Progress.course_id == cls.course_id
            ).to_list()
            
            if progress_list:
                avg_progress = sum(p.overall_progress_percent for p in progress_list) / len(progress_list)
            else:
                avg_progress = 0.0
        else:
            avg_progress = 0.0
        
        classes_list.append({
            "id": cls.id,
            "name": cls.name,
            "course_title": course.title if course else "Unknown",
            "student_count": f"{student_count}/{cls.max_students}",
            "status": cls.status,
            "start_date": cls.start_date,
            "end_date": cls.end_date,
            "progress": round(avg_progress, 2)
        })
    
    return {
        "classes": classes_list,
        "total": len(classes_list)
    }


async def get_class_detail(class_id: str, instructor_id: str) -> Dict:
    """
    3.1.3: Xem chi tiết lớp học
    
    Business Logic:
    1. Tìm Class theo class_id và instructor_id (ownership check)
    2. Lấy course information
    3. Query students info với progress
    4. Tính statistics: lessons completed, avg quiz score
    5. Return full detail
    
    Args:
        class_id: ID lớp học
        instructor_id: ID giảng viên (ownership)
        
    Returns:
        Dict chứa class detail, students, stats
        
    Raises:
        ValueError: Nếu class không tồn tại hoặc không phải owner
    """
    # Find class with ownership check
    cls = await Class.find_one(
        Class.id == class_id,
        Class.instructor_id == instructor_id
    )
    
    if not cls:
        raise ValueError("Lớp học không tồn tại hoặc bạn không có quyền truy cập")
    
    # Get course
    course = await Course.get(cls.course_id)
    
    # Count modules
    module_count = len(course.modules) if course else 0
    
    # Get students info
    students_info = []
    total_lessons_completed = 0
    total_quiz_score = 0.0
    quiz_count = 0
    
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
            "joined_at": enrollment.created_at if enrollment else cls.created_at
        })
        
        # Accumulate stats
        if progress:
            total_lessons_completed += progress.completed_lessons_count
        
        # Get quiz scores
        quiz_attempts = await QuizAttempt.find(
            QuizAttempt.user_id == student_id,
            QuizAttempt.course_id == cls.course_id
        ).to_list()
        
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
            "module_count": module_count
        },
        "invite_code": cls.invite_code,
        "max_students": cls.max_students,
        "student_count": len(cls.student_ids),
        "start_date": cls.start_date,
        "end_date": cls.end_date,
        "status": cls.status,
        "recent_students": students_info,
        "class_stats": stats
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
    
    # Check if already joined
    if user_id in cls.student_ids:
        raise ValueError("Bạn đã tham gia lớp học này")
    
    # Add student to class
    cls.student_ids.append(user_id)
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
        
        # Get quiz attempts
        quiz_attempts = await QuizAttempt.find(
            QuizAttempt.user_id == student_id,
            QuizAttempt.course_id == cls.course_id
        ).to_list()
        
        # Calculate quiz average
        if quiz_attempts:
            quiz_avg = sum(a.score for a in quiz_attempts) / len(quiz_attempts)
        else:
            quiz_avg = 0.0
        
        # Calculate completed modules
        if progress:
            completed_modules = sum(
                1 for lp in progress.lessons_progress
                if lp.get("status") == "completed"
            )
        else:
            completed_modules = 0
        
        students_list.append({
            "student_id": user.id,
            "student_name": user.full_name,
            "email": user.email,
            "join_date": enrollment.created_at if enrollment else cls.created_at,
            "progress": progress.overall_progress_percent if progress else 0.0,
            "completed_modules": completed_modules,
            "total_modules": total_modules,
            "last_activity": progress.last_accessed_at if progress and progress.last_accessed_at else enrollment.updated_at if enrollment else cls.created_at,
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
    
    if student_id not in cls.student_ids:
        raise ValueError("Học viên không thuộc lớp này")
    
    # Get user
    user = await User.get(student_id)
    
    # Get progress
    progress = await Progress.find_one(
        Progress.user_id == student_id,
        Progress.course_id == cls.course_id
    )
    
    # Get quiz attempts
    quiz_attempts = await QuizAttempt.find(
        QuizAttempt.user_id == student_id,
        QuizAttempt.course_id == cls.course_id
    ).sort(-QuizAttempt.created_at).to_list()
    
    # Get course
    course = await Course.get(cls.course_id)
    
    # Format quiz scores
    quiz_scores = []
    for attempt in quiz_attempts:
        # Get quiz info from modules
        quiz_title = f"Quiz {attempt.quiz_id[:8]}"
        if course:
            for module in course.modules:
                if module.default_quiz_id == attempt.quiz_id:
                    quiz_title = f"Quiz {module.title}"
                    break
        
        quiz_scores.append({
            "quiz_id": attempt.quiz_id,
            "quiz_title": quiz_title,
            "score": attempt.score,
            "attempt_date": attempt.created_at
        })
    
    # Format modules detail
    modules_detail = []
    if course and progress:
        for module in course.modules:
            # Count completed lessons in this module
            module_lessons = [l.id for l in module.lessons]
            completed_in_module = sum(
                1 for lp in progress.lessons_progress
                if lp.get("lesson_id") in module_lessons and lp.get("status") == "completed"
            )
            
            module_progress = (completed_in_module / len(module.lessons) * 100) if len(module.lessons) > 0 else 0.0
            
            # Get quiz scores for this module
            module_quiz_scores = [
                qs for qs in quiz_scores
                if module.default_quiz_id and module.default_quiz_id == qs["quiz_id"]
            ]
            
            modules_detail.append({
                "module_id": module.id,
                "module_title": module.title,
                "progress": round(module_progress, 2),
                "completed_lessons": completed_in_module,
                "quiz_scores": module_quiz_scores
            })
    
    # Student progress summary
    progress_summary = {
        "overall_progress": progress.overall_progress_percent if progress else 0.0,
        "completed_modules": sum(1 for m in modules_detail if m["progress"] == 100.0),
        "total_modules": len(modules_detail),
        "study_streak_days": progress.study_streak_days if progress else 0,
        "total_study_time": progress.total_time_spent_minutes / 60.0 if progress else 0.0
    }
    
    return {
        "student_id": user.id,
        "student_name": user.full_name,
        "email": user.email,
        "avatar_url": user.avatar_url if hasattr(user, 'avatar_url') else None,
        "quiz_scores": quiz_scores,
        "modules_detail": modules_detail,
        "progress": progress_summary
    }


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
    
    if student_id not in cls.student_ids:
        raise ValueError("Học viên không thuộc lớp này")
    
    # Remove from class
    cls.student_ids.remove(student_id)
    cls.updated_at = datetime.utcnow()
    await cls.save()
    
    # Update enrollment status (keep data)
    enrollment = await Enrollment.find_one(
        Enrollment.user_id == student_id,
        Enrollment.course_id == cls.course_id
    )
    
    if enrollment:
        enrollment.status = "removed"
        enrollment.updated_at = datetime.utcnow()
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
    
    # Get course
    course = await Course.get(cls.course_id)
    
    # Query all students' progress
    progress_list = await Progress.find(
        Progress.user_id.in_(cls.student_ids),
        Progress.course_id == cls.course_id
    ).to_list()
    
    # Query all quiz attempts
    quiz_attempts = await QuizAttempt.find(
        QuizAttempt.user_id.in_(cls.student_ids),
        QuizAttempt.course_id == cls.course_id
    ).to_list()
    
    # Score histogram (group by score ranges)
    score_ranges = {
        "0-20": 0,
        "21-40": 0,
        "41-60": 0,
        "61-80": 0,
        "81-100": 0
    }
    
    for attempt in quiz_attempts:
        score = attempt.score
        if score <= 20:
            score_ranges["0-20"] += 1
        elif score <= 40:
            score_ranges["21-40"] += 1
        elif score <= 60:
            score_ranges["41-60"] += 1
        elif score <= 80:
            score_ranges["61-80"] += 1
        else:
            score_ranges["81-100"] += 1
    
    # Module completion rates
    module_completion = []
    if course:
        for module in course.modules:
            module_lessons = [l.id for l in module.lessons]
            
            # Count students who completed this module
            completed_students = 0
            for progress in progress_list:
                completed_in_module = sum(
                    1 for lp in progress.lessons_progress
                    if lp.get("lesson_id") in module_lessons and lp.get("status") == "completed"
                )
                if completed_in_module == len(module_lessons):
                    completed_students += 1
            
            module_completion.append({
                "module_id": module.id,
                "module_title": module.title,
                "completed_students": completed_students,
                "total_students": len(cls.student_ids),
                "completion_rate": round(completed_students / len(cls.student_ids) * 100, 2) if len(cls.student_ids) > 0 else 0.0
            })
    
    # Lessons completion stats
    lesson_stats = {}
    for progress in progress_list:
        for lp in progress.lessons_progress:
            lesson_id = lp.get("lesson_id")
            if lesson_id:
                if lesson_id not in lesson_stats:
                    lesson_stats[lesson_id] = 0
                if lp.get("status") == "completed":
                    lesson_stats[lesson_id] += 1
    
    # Sort to find most/least completed
    sorted_lessons = sorted(lesson_stats.items(), key=lambda x: x[1], reverse=True)
    
    most_completed = sorted_lessons[:3] if sorted_lessons else []
    least_completed = sorted_lessons[-3:] if sorted_lessons else []
    
    return {
        "class_id": cls.id,
        "class_name": cls.name,
        "total_students": len(cls.student_ids),
        "score_distribution": score_ranges,
        "module_completion": module_completion,
        "most_completed_lessons": most_completed,
        "least_completed_lessons": least_completed
    }
