"""
Learning Service - Xử lý module & lesson content
Sử dụng: Beanie ODM, MongoDB
Tuân thủ: CHUCNANG.md Section 2.4.1-2.4.2, ENDPOINTS.md learning_router
"""

from datetime import datetime
from typing import Optional, List, Dict
from models.models import Course, Module, Lesson, Enrollment, Progress, Quiz


# ============================================================================
# MODULE OPERATIONS
# ============================================================================

async def get_module_detail(
    course_id: str,
    module_id: str,
    user_id: Optional[str] = None
) -> Optional[Dict]:
    """
    Lấy thông tin chi tiết module
    Section 2.4.1
    
    Args:
        course_id: ID của course
        module_id: ID của module
        user_id: ID của user hiện tại (để tính progress)
        
    Returns:
        Dict chứa module detail hoặc None
    """
    # Lấy course
    course = await Course.get(course_id)
    if not course:
        return None
    
    # Check if course has modules
    if not hasattr(course, 'modules') or not course.modules:
        return None
    
    # Tìm module trong course
    module = None
    for m in course.modules:
        if str(m.id) == module_id:
            module = m
            break
    
    if not module:
        return None
    
    # Tính progress của user (nếu có)
    completion_status = "not-started"
    completed_lessons_count = 0
    progress_percent = 0.0
    is_locked = False  # Khởi tạo is_locked
    
    if user_id:
        # Lấy enrollment và progress
        from services.enrollment_service import get_user_enrollment
        enrollment = await get_user_enrollment(user_id, course_id)
        
        if enrollment:
            # Đếm số lessons đã hoàn thành trong module này
            completed_in_module = [
                lesson_id for lesson_id in enrollment.completed_lessons
                if any(str(lesson.id) == lesson_id for lesson in module.lessons)
            ]
            completed_lessons_count = len(completed_in_module)
            
            total_lessons = len(module.lessons)
            if total_lessons > 0:
                progress_percent = (completed_lessons_count / total_lessons * 100)
            
            # Xác định completion_status
            if progress_percent == 100:
                completion_status = "completed"
            elif progress_percent > 0:
                completion_status = "in-progress"
    
    # Transform learning outcomes to match schema format
    transformed_outcomes = []
    for i, outcome in enumerate(module.learning_outcomes):
        transformed_outcome = {
            "id": str(i + 1),  # Generate sequential ID
            "outcome": outcome.get("description", ""),  # Map description to outcome
            "skill_tag": outcome.get("skill_tag", ""),
            "is_mandatory": True  # Default to mandatory
        }
        transformed_outcomes.append(transformed_outcome)
    
    # Build response
    result = {
        "id": str(module.id),
        "title": module.title,
        "description": getattr(module, 'description', '') or '',
        "difficulty": getattr(module, 'difficulty', 'Basic'),
        "order": module.order,
        "lessons": [],
        "learning_outcomes": transformed_outcomes,
        "estimated_hours": getattr(module, 'estimated_hours', 0.0),
        "resources": module.resources if hasattr(module, 'resources') else [],  # Resources từ module schema
        "completion_status": completion_status,
        "completed_lessons": completed_lessons_count,
        "total_lessons": len(module.lessons),
        "progress_percent": progress_percent,
        "is_accessible": not is_locked,
        "prerequisites": module.prerequisites if hasattr(module, 'prerequisites') else []  # Prerequisites từ module schema
    }
    
    # Build lessons list với completion status
    for lesson in module.lessons:
        is_completed = False
        is_locked = False
        
        if user_id:
            from services.enrollment_service import get_user_enrollment
            enrollment = await get_user_enrollment(user_id, course_id)
            if enrollment:
                is_completed = str(lesson.id) in enrollment.completed_lessons
                
                # Check if locked (previous lesson not completed)
                if lesson.order > 1:
                    prev_lesson = next(
                        (l for l in module.lessons if l.order == lesson.order - 1),
                        None
                    )
                    if prev_lesson and str(prev_lesson.id) not in enrollment.completed_lessons:
                        is_locked = True
        
        result["lessons"].append({
            "id": str(lesson.id),
            "title": getattr(lesson, 'title', ''),
            "order": getattr(lesson, 'order', 0),
            "duration_minutes": getattr(lesson, 'duration_minutes', 0),
            "content_type": getattr(lesson, 'content_type', 'text'),
            "has_quiz": lesson.quiz_id is not None if hasattr(lesson, 'quiz_id') else False,
            "is_completed": is_completed,
            "is_locked": is_locked
        })
    
    return result


async def get_lesson_content(
    course_id: str,
    lesson_id: str,
    user_id: Optional[str] = None
) -> Optional[Dict]:
    """
    Lấy nội dung chi tiết của lesson
    Section 2.4.2
    
    Args:
        course_id: ID của course
        lesson_id: ID của lesson
        user_id: ID của user hiện tại
        
    Returns:
        Dict chứa lesson content hoặc None
    """
    # Lấy course
    course = await Course.get(course_id)
    if not course:
        return None
    
    # Tìm lesson và module chứa lesson
    lesson = None
    module = None
    
    # First try to find in embedded modules
    if hasattr(course, 'modules') and course.modules:
        for m in course.modules:
            if m.lessons:
                for l in m.lessons:
                    if str(l.id) == str(lesson_id):
                        lesson = l
                        module = m
                        break
            if lesson:
                break
    
    # If not found, try to find standalone Lesson document
    if not lesson:
        from models.models import Lesson as LessonModel, Module as ModuleModel
        standalone_lesson = await LessonModel.get(lesson_id)
        if standalone_lesson and str(standalone_lesson.course_id) == str(course_id):
            lesson = standalone_lesson
            # Get the module for this lesson
            if standalone_lesson.module_id:
                module = await ModuleModel.get(standalone_lesson.module_id)
    
    if not lesson:
        return None
    
    # Tìm lesson trước và sau
    previous_lesson_id = None
    next_lesson_id = None
    
    # Handle navigation for embedded lessons
    if module and hasattr(module, 'lessons') and module.lessons:
        lessons_in_module = sorted(module.lessons, key=lambda x: x.order)
        for i, l in enumerate(lessons_in_module):
            if str(l.id) == str(lesson_id):
                if i > 0:
                    previous_lesson_id = str(lessons_in_module[i-1].id)
                if i < len(lessons_in_module) - 1:
                    next_lesson_id = str(lessons_in_module[i+1].id)
                break
    # Handle navigation for standalone lessons
    elif module:
        from models.models import Lesson as LessonModel
        module_lessons = await LessonModel.find(
            LessonModel.module_id == str(module.id),
            LessonModel.course_id == course_id
        ).sort("order").to_list()
        
        for i, l in enumerate(module_lessons):
            if str(l.id) == str(lesson_id):
                if i > 0:
                    previous_lesson_id = str(module_lessons[i-1].id)
                if i < len(module_lessons) - 1:
                    next_lesson_id = str(module_lessons[i+1].id)
                break
    
    # Tracking info của user
    is_completed = False
    last_accessed_at = None
    time_spent_seconds = 0
    video_progress_seconds = 0
    quiz_passed = False
    is_next_locked = False
    
    if user_id:
        # Lấy enrollment và progress
        from services.enrollment_service import get_user_enrollment
        enrollment = await get_user_enrollment(user_id, course_id)
        
        if enrollment:
            is_completed = str(lesson_id) in [str(lid) for lid in enrollment.completed_lessons]
            last_accessed_at = enrollment.last_accessed_at
            
            # Lấy progress detail
            progress = await Progress.find_one(
                Progress.user_id == user_id,
                Progress.course_id == course_id
            )
            
            if progress:
                # Tìm lesson progress
                for lp in progress.lessons_progress:
                    if str(lp.get("lesson_id")) == str(lesson_id):
                        time_spent_seconds = lp.get("time_spent_seconds", 0)
                        video_progress_seconds = lp.get("video_progress_seconds", 0)
                        break
            
            # Check quiz status
            quiz = await Quiz.find_one(Quiz.lesson_id == str(lesson_id))
            if quiz:
                from services.quiz_service import get_user_quiz_attempts
                attempts = await get_user_quiz_attempts(user_id, str(quiz.id))
                if attempts:
                    # Check if passed any attempt
                    quiz_passed = any(attempt.passed for attempt in attempts)
            
            # Check if next lesson is locked
            if next_lesson_id:
                next_completed = str(next_lesson_id) in [str(lid) for lid in enrollment.completed_lessons]
                # Next lesson locked if current not completed
                is_next_locked = not is_completed
    
    # Parse attachments từ resources
    attachments = []
    lesson_resources_raw = getattr(lesson, 'resources', []) or []
    for resource in lesson_resources_raw:
        if isinstance(resource, dict):
            attachments.append({
                "id": resource.get("id", "") or "",
                "filename": resource.get("filename", resource.get("title", "")) or "Untitled",
                "file_type": resource.get("type", "other") or "other",
                "url": resource.get("url", "") or "",
                "size_mb": float(resource.get("size_mb", 0) or 0)
            })
    
    # Parse video info
    video_info = None
    video_url = getattr(lesson, 'video_url', None)
    if video_url:
        video_info = {
            "url": video_url,
            "duration_seconds": getattr(lesson, 'duration_minutes', 0) * 60,
            "thumbnail_url": None,  # Can be added later
            "quality": ["360p", "720p", "1080p"]
        }
    
    # Lấy quiz info chi tiết
    quiz = await Quiz.find_one(Quiz.lesson_id == str(lesson_id))
    has_quiz = quiz is not None
    quiz_info = {
        "quiz_id": str(quiz.id) if quiz else None,
        "question_count": len(quiz.questions) if quiz else None,
        "is_mandatory": True if quiz else None  # Default mandatory
    }
    
    # Tính video_progress_percent nếu có video
    video_progress_percent = None
    if video_info and video_info["duration_seconds"] > 0:
        video_progress_percent = (video_progress_seconds / video_info["duration_seconds"] * 100)
    
    # Build navigation object theo API_SCHEMA.md
    # Get previous lesson title
    previous_lesson_title = None
    if previous_lesson_id and module:
        if hasattr(module, 'lessons'):
            prev_lesson = next((l for l in module.lessons if str(l.id) == previous_lesson_id), None)
            if prev_lesson:
                previous_lesson_title = prev_lesson.title
        else:
            from models.models import Lesson as LessonModel
            prev_lesson_doc = await LessonModel.get(previous_lesson_id)
            if prev_lesson_doc:
                previous_lesson_title = prev_lesson_doc.title
    
    # Get next lesson title
    next_lesson_title = None
    if next_lesson_id and module:
        if hasattr(module, 'lessons'):
            nxt_lesson = next((l for l in module.lessons if str(l.id) == next_lesson_id), None)
            if nxt_lesson:
                next_lesson_title = nxt_lesson.title
        else:
            from models.models import Lesson as LessonModel
            nxt_lesson_doc = await LessonModel.get(next_lesson_id)
            if nxt_lesson_doc:
                next_lesson_title = nxt_lesson_doc.title
    
    navigation = {
        "previous_lesson": {
            "id": previous_lesson_id,
            "title": previous_lesson_title
        },
        "next_lesson": {
            "id": next_lesson_id,
            "title": next_lesson_title,
            "is_locked": is_next_locked
        }
    }
    
    # Build completion_status object
    completion_date = None
    # Get completion_date from Progress.lessons_progress
    if user_id and is_completed:
        progress = await Progress.find_one(
            Progress.user_id == user_id,
            Progress.course_id == course_id
        )
        if progress and progress.lessons_progress:
            lesson_progress = next(
                (lp for lp in progress.lessons_progress if str(lp.lesson_id) == str(lesson_id)),
                None
            )
            if lesson_progress:
                completion_date = lesson_progress.completion_date
    
    completion_status = {
        "is_completed": is_completed,
        "completion_date": completion_date,
        "time_spent_minutes": time_spent_seconds // 60,
        "video_progress_percent": video_progress_percent
    }
    
    # Get learning objectives từ lesson (nếu có trong model)
    learning_objectives = getattr(lesson, 'learning_objectives', [])
    
    # Get resources từ lesson
    resources = []
    lesson_resources = getattr(lesson, 'resources', []) or []
    for res in lesson_resources:
        if isinstance(res, dict):
            resources.append({
                "id": res.get("id", "") or "",
                "title": res.get("title", res.get("filename", "")) or "Untitled",
                "type": res.get("type", "other") or "other",
                "url": res.get("url", "") or "",
                "size_mb": float(res.get("size_mb", 0) or 0),
                "description": res.get("description", "") or ""
            })
    
    # Build final result theo LessonContentResponse schema mới
    result = {
        "id": str(lesson.id),
        "course_id": course_id,
        "title": getattr(lesson, 'title', ''),
        "module_id": str(module.id) if module else None,
        "module_title": getattr(module, 'title', '') if module else None,
        "order": getattr(lesson, 'order', 0),
        "duration_minutes": getattr(lesson, 'duration_minutes', 0),
        "content_type": getattr(lesson, 'content_type', 'text'),
        "text_content": getattr(lesson, 'content', ''),
        "video_info": video_info,
        "attachments": attachments,
        "learning_objectives": learning_objectives,
        "resources": resources,
        "navigation": navigation,
        "has_quiz": has_quiz,
        "quiz_info": quiz_info,
        "completion_status": completion_status,
        "created_at": getattr(lesson, 'created_at', datetime.utcnow()),
        "updated_at": getattr(lesson, 'updated_at', datetime.utcnow())
    }
    
    # Update last_accessed_at
    if user_id:
        from services.enrollment_service import get_user_enrollment
        enrollment = await get_user_enrollment(user_id, course_id)
        if enrollment:
            enrollment.last_accessed_at = datetime.utcnow()
            await enrollment.save()
    
    return result


async def get_course_modules_list(
    course_id: str,
    user_id: Optional[str] = None
) -> Optional[Dict]:
    """
    Lấy danh sách tất cả modules trong course
    
    Args:
        course_id: ID của course
        user_id: ID của user hiện tại
        
    Returns:
        Dict chứa modules list
    """
    course = await Course.get(course_id)
    if not course:
        return None
    
    # Check if course has modules
    if not hasattr(course, 'modules') or not course.modules:
        return {
            "course_id": course.id,
            "course_title": course.title,
            "modules": [],
            "total_modules": 0,
            "completed_modules": 0
        }
    
    # Get enrollment nếu có user
    enrollment = None
    if user_id:
        from services.enrollment_service import get_user_enrollment
        enrollment = await get_user_enrollment(user_id, course_id)
    
    modules_list = []
    completed_modules = 0
    
    for module in course.modules:
        # Tính progress cho module
        progress_percent = 0.0
        is_locked = False
        completed_in_module = []
        
        if enrollment:
            # Đếm lessons completed trong module
            module_lesson_ids = {str(lesson.id) for lesson in module.lessons}
            completed_in_module = [
                lesson_id for lesson_id in enrollment.completed_lessons
                if lesson_id in module_lesson_ids
            ]
            
            total_lessons = len(module.lessons)
            if total_lessons > 0:
                progress_percent = (len(completed_in_module) / total_lessons * 100)
            
            if progress_percent == 100:
                completed_modules += 1
            
            # Check if locked (previous module not completed)
            if module.order > 1:
                prev_module = next(
                    (m for m in course.modules if m.order == module.order - 1),
                    None
                )
                if prev_module:
                    # Check if prev module completed
                    prev_lesson_ids = {str(lesson.id) for lesson in prev_module.lessons}
                    prev_completed = [
                        lesson_id for lesson_id in enrollment.completed_lessons
                        if lesson_id in prev_lesson_ids
                    ]
                    if len(prev_completed) < len(prev_module.lessons):
                        is_locked = True
        
        modules_list.append({
            "id": str(module.id),
            "title": module.title,
            "description": getattr(module, 'description', ''),
            "difficulty": getattr(module, 'difficulty', 'Basic'),
            "order": module.order,
            "estimated_hours": getattr(module, 'estimated_hours', 0.0),
            "lesson_count": len(module.lessons),
            "total_lessons": len(module.lessons),
            "completed_lessons": len(completed_in_module),
            "progress_percent": progress_percent,
            "is_accessible": not is_locked,
            "is_locked": is_locked,
            "status": "completed" if progress_percent >= 100 else "in-progress" if progress_percent > 0 else "not-started"
        })
    
    return {
        "course_id": str(course.id),
        "course_title": course.title,
        "modules": modules_list,
        "total_modules": len(course.modules),
        "completed_modules": completed_modules
    }


async def get_module_outcomes(
    course_id: str,
    module_id: str,
    user_id: Optional[str] = None
) -> Optional[Dict]:
    """
    Lấy learning outcomes của module với trạng thái achieved
    
    Args:
        course_id: ID của course
        module_id: ID của module
        user_id: ID của user
        
    Returns:
        Dict chứa outcomes với achieved status
    """
    import logging
    from models.models import Progress
    
    logger = logging.getLogger(__name__)
    
    course = await Course.get(course_id)
    if not course:
        return None
    
    # Check if course has modules
    if not hasattr(course, 'modules') or not course.modules:
        return None
    
    module = None
    for m in course.modules:
        if m.id == module_id:
            module = m
            break
    
    if not module:
        return None
    
    # Tính achieved outcomes từ Progress
    achieved_outcomes_count = 0
    completion_status = "not-started"
    overall_score = 0.0
    
    if user_id:
        # Lấy Progress của user cho course này
        progress = await Progress.find_one(
            Progress.user_id == user_id,
            Progress.course_id == course_id
        )
        
        if progress and progress.lessons_progress:
            # Đếm số lessons completed trong module này
            module_lesson_ids = {str(lesson.id) for lesson in module.lessons}
            completed_in_module = [
                lp for lp in progress.lessons_progress
                if str(lp.lesson_id) in module_lesson_ids and lp.status == "completed"
            ]
            
            # Nếu hoàn thành đủ lessons, coi như đạt được outcomes
            total_lessons = len(module.lessons)
            if total_lessons > 0:
                completion_percent = (len(completed_in_module) / total_lessons) * 100
                overall_score = completion_percent
                
                # Tính achieved outcomes dựa trên completion
                if completion_percent >= 100:
                    achieved_outcomes_count = len(module.learning_outcomes)
                    completion_status = "completed"
                elif completion_percent >= 70:
                    # 70-99%: đạt được hầu hết outcomes
                    achieved_outcomes_count = int(len(module.learning_outcomes) * 0.8)
                    completion_status = "in-progress"
                elif completion_percent > 0:
                    # 1-69%: đạt được một số outcomes
                    achieved_outcomes_count = int(len(module.learning_outcomes) * (completion_percent / 100))
                    completion_status = "in-progress"
    
    # Transform learning outcomes to match schema
    transformed_outcomes = []
    skills_acquired = []
    areas_for_improvement = []
    
    for i, outcome in enumerate(module.learning_outcomes):
        skill_tag = outcome.get("skill_tag", "")
        transformed_outcomes.append({
            "id": outcome.get("id", str(i + 1)),
            "outcome": outcome.get("description", outcome.get("outcome", "")),
            "skill_tag": skill_tag,
            "is_mandatory": outcome.get("is_mandatory", True)
        })
        
        # Phân loại skills
        if i < achieved_outcomes_count:
            skills_acquired.append(skill_tag)
        else:
            areas_for_improvement.append(skill_tag)
    
    return {
        "module_id": str(module.id),
        "module_title": module.title,
        "learning_outcomes": transformed_outcomes,
        "total_outcomes": len(module.learning_outcomes),
        "achieved_outcomes": achieved_outcomes_count,
        "completion_status": completion_status,
        "overall_score": overall_score,
        "skills_acquired": skills_acquired,
        "areas_for_improvement": areas_for_improvement
    }


async def get_module_resources(
    course_id: str,
    module_id: str
) -> Optional[Dict]:
    """
    Lấy tài nguyên học tập của module
    
    Args:
        course_id: ID của course
        module_id: ID của module
        
    Returns:
        Dict chứa resources
    """
    course = await Course.get(course_id)
    if not course:
        return None
    
    # Check if course has modules
    if not hasattr(course, 'modules') or not course.modules:
        return None
    
    module = None
    for m in course.modules:
        if m.id == module_id:
            module = m
            break
    
    if not module:
        return None
    
    # Collect resources từ tất cả lessons trong module
    resources = []
    resources_by_type = {}
    mandatory_count = 0
    
    for lesson in module.lessons:
        # Check if lesson has resources
        lesson_resources = getattr(lesson, 'resources', None) or []
        
        if not lesson_resources:
            continue
            
        for resource in lesson_resources:
            if not isinstance(resource, dict):
                continue
                
            resource_type = resource.get("type", "other")
            
            # Build clean resource object
            clean_resource = {
                "id": resource.get("id", "") or "",
                "title": resource.get("title", resource.get("filename", "Untitled")) or "Untitled",
                "type": resource_type or "other",
                "url": resource.get("url", "") or "",
                "size_mb": float(resource.get("size_mb", 0) or 0),
                "description": resource.get("description", "") or ""
            }
            
            resources.append(clean_resource)
            resources_by_type[resource_type] = resources_by_type.get(resource_type, 0) + 1
            
            # Count mandatory resources
            if resource.get("is_mandatory", False):
                mandatory_count += 1
    
    return {
        "module_id": str(module.id),
        "module_title": module.title,
        "resources": resources,
        "total_resources": len(resources),
        "mandatory_resources": mandatory_count,
        "resource_categories": list(resources_by_type.keys()),
        "resources_by_type": resources_by_type
    }
