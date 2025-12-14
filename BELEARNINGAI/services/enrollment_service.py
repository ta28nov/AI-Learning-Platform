"""
Enrollment Service - Xử lý đăng ký và theo dõi tiến độ khóa học
Sử dụng: Beanie ODM, MongoDB
Tuân thủ: CHUCNANG.md Section 2.3.4-2.3.8, 2.4
"""

from datetime import datetime
from typing import Optional, List
from beanie.operators import In
from models.models import Enrollment, Progress, Course


# ============================================================================
# ENROLLMENT CRUD
# ============================================================================

async def create_enrollment(user_id: str, course_id: str) -> Enrollment:
    """
    Tạo enrollment mới (đăng ký khóa học)
    
    Args:
        user_id: ID của user
        course_id: ID của course
        
    Returns:
        Enrollment document đã tạo
        
    Raises:
        ValueError: Nếu user đã đăng ký course này rồi (và chưa hủy)
    """
    # Kiểm tra đã đăng ký chưa (chỉ check status active/completed, không check cancelled)
    existing = await Enrollment.find_one(
        Enrollment.user_id == user_id,
        Enrollment.course_id == course_id,
        In(Enrollment.status, ["active", "completed"])
    )
    
    if existing:
        raise ValueError("Bạn đã đăng ký khóa học này rồi")
    
    # Kiểm tra có enrollment bị cancelled không - nếu có thì tái kích hoạt
    cancelled_enrollment = await Enrollment.find_one(
        Enrollment.user_id == user_id,
        Enrollment.course_id == course_id,
        Enrollment.status == "cancelled"
    )
    
    if cancelled_enrollment:
        # Tái kích hoạt enrollment cũ
        cancelled_enrollment.status = "active"
        cancelled_enrollment.enrolled_at = datetime.utcnow()
        # Reset progress về 0 cho enrollment mới
        cancelled_enrollment.progress_percent = 0.0
        cancelled_enrollment.completed_lessons = []
        cancelled_enrollment.completed_modules = []
        cancelled_enrollment.last_accessed_at = datetime.utcnow()
        await cancelled_enrollment.save()
        
        # Tăng enrollment_count của course
        course = await Course.get(course_id)
        if course:
            course.enrollment_count += 1
            await course.save()
        
        return cancelled_enrollment
    
    # Tạo enrollment mới
    enrollment = Enrollment(
        user_id=user_id,
        course_id=course_id,
        status="active"
    )
    
    await enrollment.insert()
    
    # Tăng enrollment_count của course
    course = await Course.get(course_id)
    if course:
        course.enrollment_count += 1
        await course.save()
    
    return enrollment


async def get_enrollment_by_id(enrollment_id: str) -> Optional[Enrollment]:
    """
    Lấy enrollment theo ID
    
    Args:
        enrollment_id: ID của enrollment
        
    Returns:
        Enrollment document hoặc None
    """
    try:
        enrollment = await Enrollment.get(enrollment_id)
        return enrollment
    except Exception:
        return None


async def get_user_enrollment(user_id: str, course_id: str) -> Optional[Enrollment]:
    """
    Lấy enrollment của user cho một course cụ thể
    
    Args:
        user_id: ID của user
        course_id: ID của course
        
    Returns:
        Enrollment document hoặc None
    """
    enrollment = await Enrollment.find_one(
        Enrollment.user_id == user_id,
        Enrollment.course_id == course_id
    )
    
    return enrollment


async def get_user_enrollments(
    user_id: str,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
) -> List[Enrollment]:
    """
    Lấy tất cả enrollments của user
    
    Args:
        user_id: ID của user
        status: Filter theo status (active, completed, cancelled)
        skip: Pagination skip
        limit: Pagination limit
        
    Returns:
        List Enrollment documents
    """
    query = Enrollment.find(Enrollment.user_id == user_id)
    
    if status:
        query = query.find(Enrollment.status == status)
    
    enrollments = await query.skip(skip).limit(limit).to_list()
    return enrollments


async def get_course_enrollments(
    course_id: str,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
) -> List[Enrollment]:
    """
    Lấy tất cả enrollments của một course
    
    Args:
        course_id: ID của course
        status: Filter theo status
        skip: Pagination skip
        limit: Pagination limit
        
    Returns:
        List Enrollment documents
    """
    query = Enrollment.find(Enrollment.course_id == course_id)
    
    if status:
        query = query.find(Enrollment.status == status)
    
    enrollments = await query.skip(skip).limit(limit).to_list()
    return enrollments


# ============================================================================
# ENROLLMENT UPDATE (Section 2.3.4-2.3.8)
# ============================================================================

async def update_enrollment_progress(
    enrollment_id: str,
    progress_percent: Optional[float] = None,
    completed_lessons: Optional[List[str]] = None,
    completed_modules: Optional[List[str]] = None
) -> Optional[Enrollment]:
    """
    Cập nhật tiến độ enrollment
    
    Args:
        enrollment_id: ID của enrollment
        progress_percent: % tiến độ
        completed_lessons: List lesson IDs đã hoàn thành
        completed_modules: List module IDs đã hoàn thành
        
    Returns:
        Enrollment document đã update hoặc None
    """
    enrollment = await get_enrollment_by_id(enrollment_id)
    
    if not enrollment:
        return None
    
    if progress_percent is not None:
        enrollment.progress_percent = progress_percent
    
    if completed_lessons is not None:
        enrollment.completed_lessons = completed_lessons
    
    if completed_modules is not None:
        enrollment.completed_modules = completed_modules
    
    enrollment.last_accessed_at = datetime.utcnow()
    
    # Kiểm tra nếu hoàn thành 100%
    if enrollment.progress_percent >= 100:
        enrollment.status = "completed"
        enrollment.completed_at = datetime.utcnow()
    
    await enrollment.save()
    return enrollment


async def mark_lesson_completed(
    user_id: str,
    course_id: str,
    lesson_id: str
) -> Optional[Enrollment]:
    """
    Đánh dấu lesson đã hoàn thành và tính lại progress
    
    Args:
        user_id: ID của user
        course_id: ID của course
        lesson_id: ID của lesson
        
    Returns:
        Enrollment document đã update hoặc None
    """
    enrollment = await get_user_enrollment(user_id, course_id)
    
    if not enrollment:
        return None
    
    # Thêm lesson_id nếu chưa có
    if lesson_id not in enrollment.completed_lessons:
        enrollment.completed_lessons.append(lesson_id)
    
    # Tính lại progress
    course = await Course.get(course_id)
    if course and hasattr(course, 'modules') and course.modules:
        total_lessons = sum(len(module.lessons) for module in course.modules)
        if total_lessons > 0:
            enrollment.progress_percent = (
                len(enrollment.completed_lessons) / total_lessons * 100
            )
    
    enrollment.last_accessed_at = datetime.utcnow()
    
    # Kiểm tra hoàn thành
    if enrollment.progress_percent >= 100:
        enrollment.status = "completed"
        enrollment.completed_at = datetime.utcnow()
    
    await enrollment.save()
    return enrollment


async def cancel_enrollment(enrollment_id: str) -> Optional[Enrollment]:
    """
    Hủy enrollment
    
    Args:
        enrollment_id: ID của enrollment
        
    Returns:
        Enrollment document đã update hoặc None
    """
    enrollment = await get_enrollment_by_id(enrollment_id)
    
    if not enrollment:
        return None
    
    enrollment.status = "cancelled"
    await enrollment.save()
    
    # Giảm enrollment_count của course
    course = await Course.get(enrollment.course_id)
    if course and course.enrollment_count > 0:
        course.enrollment_count -= 1
        await course.save()
    
    return enrollment


# ============================================================================
# PROGRESS TRACKING (Section 2.4.9)
# ============================================================================

async def get_or_create_progress(
    user_id: str,
    course_id: str,
    enrollment_id: str
) -> Progress:
    """
    Lấy hoặc tạo Progress document
    
    Args:
        user_id: ID của user
        course_id: ID của course
        enrollment_id: ID của enrollment
        
    Returns:
        Progress document
    """
    # Tìm progress hiện tại
    progress = await Progress.find_one(
        Progress.user_id == user_id,
        Progress.course_id == course_id
    )
    
    if progress:
        return progress
    
    # Tạo progress mới
    course = await Course.get(course_id)
    total_lessons = 0
    if course and hasattr(course, 'modules') and course.modules:
        total_lessons = sum(len(module.lessons) for module in course.modules)
    
    progress = Progress(
        user_id=user_id,
        course_id=course_id,
        enrollment_id=enrollment_id,
        total_lessons_count=total_lessons
    )
    
    await progress.insert()
    return progress


async def update_lesson_progress(
    user_id: str,
    course_id: str,
    lesson_id: str,
    status: str,
    time_spent_seconds: int = 0
) -> Optional[Progress]:
    """
    Cập nhật tiến độ cho một lesson cụ thể
    
    Args:
        user_id: ID của user
        course_id: ID của course
        lesson_id: ID của lesson
        status: Status của lesson (not_started, in_progress, completed)
        time_spent_seconds: Thời gian đã học (giây)
        
    Returns:
        Progress document đã update hoặc None
    """
    # Lấy enrollment
    enrollment = await get_user_enrollment(user_id, course_id)
    if not enrollment:
        return None
    
    # Lấy hoặc tạo progress
    progress = await get_or_create_progress(user_id, course_id, enrollment.id)
    
    # Tìm lesson progress entry
    lesson_entry = None
    for entry in progress.lessons_progress:
        if entry.get("lesson_id") == lesson_id:
            lesson_entry = entry
            break
    
    if lesson_entry:
        # Update existing
        lesson_entry["status"] = status
        lesson_entry["time_spent_seconds"] += time_spent_seconds
        lesson_entry["last_accessed_at"] = datetime.utcnow()
    else:
        # Add new
        progress.lessons_progress.append({
            "lesson_id": lesson_id,
            "status": status,
            "time_spent_seconds": time_spent_seconds,
            "last_accessed_at": datetime.utcnow()
        })
    
    # Đếm số lessons completed
    completed = sum(
        1 for entry in progress.lessons_progress 
        if entry.get("status") == "completed"
    )
    progress.completed_lessons_count = completed
    
    # Tính progress percent
    if progress.total_lessons_count > 0:
        progress.overall_progress_percent = (
            completed / progress.total_lessons_count * 100
        )
    
    # Tính tổng thời gian
    progress.total_time_spent_minutes = sum(
        entry.get("time_spent_seconds", 0) for entry in progress.lessons_progress
    ) // 60
    
    progress.last_accessed_at = datetime.utcnow()
    progress.updated_at = datetime.utcnow()
    
    await progress.save()
    
    # Đồng bộ với enrollment
    await update_enrollment_progress(
        enrollment.id,
        progress_percent=progress.overall_progress_percent,
        completed_lessons=[
            e["lesson_id"] for e in progress.lessons_progress 
            if e.get("status") == "completed"
        ]
    )
    
    return progress


async def get_user_progress(user_id: str, course_id: str) -> Optional[Progress]:
    """
    Lấy progress của user cho course
    
    Args:
        user_id: ID của user
        course_id: ID của course
        
    Returns:
        Progress document hoặc None
    """
    progress = await Progress.find_one(
        Progress.user_id == user_id,
        Progress.course_id == course_id
    )
    
    return progress


# ============================================================================
# STATISTICS
# ============================================================================

async def get_enrollment_stats(course_id: str) -> dict:
    """
    Lấy thống kê enrollments cho course
    
    Args:
        course_id: ID của course
        
    Returns:
        Dict chứa thống kê
    """
    total = await Enrollment.find(
        Enrollment.course_id == course_id
    ).count()
    
    active = await Enrollment.find(
        Enrollment.course_id == course_id,
        Enrollment.status == "active"
    ).count()
    
    completed = await Enrollment.find(
        Enrollment.course_id == course_id,
        Enrollment.status == "completed"
    ).count()
    
    return {
        "total_enrollments": total,
        "active_enrollments": active,
        "completed_enrollments": completed,
        "completion_rate": (completed / total * 100) if total > 0 else 0
    }
