"""
Personal Courses Service
Business logic cho personal courses (khóa học cá nhân)
Section 2.5.1-2.5.5
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from models.models import Course, EmbeddedModule, EmbeddedLesson, generate_uuid
from services.ai_service import generate_course_from_prompt


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _normalize_course_level(level: Optional[str], fallback: str = "Beginner") -> str:
    """Map AI / loose strings to API-allowed course levels."""
    allowed = {"Beginner", "Intermediate", "Advanced"}
    if level in allowed:
        return level
    low = _safe_str(level).lower()
    if "intermediate" in low or "trung cấp" in low or "trung bình" in low:
        return "Intermediate"
    if "advanced" in low or "nâng cao" in low:
        return "Advanced"
    if "beginner" in low or "cơ bản" in low or "nhập môn" in low:
        return "Beginner"
    return fallback if fallback in allowed else "Beginner"


def _normalize_module_learning_outcomes(raw: Any) -> List[Dict[str, str]]:
    """
    Coerce AI output to list of {description, skill_tag} for module + CourseFromPromptResponse.
    Gemini often omits skill_tag or returns plain strings.
    """
    out: List[Dict[str, str]] = []
    if not raw or not isinstance(raw, list):
        return [
            {"description": "Hoàn thành nội dung module", "skill_tag": "module-complete"}
        ]
    for idx, item in enumerate(raw):
        if isinstance(item, str):
            out.append(
                {
                    "description": item.strip() or f"Mục tiêu {idx + 1}",
                    "skill_tag": f"outcome-{idx + 1}",
                }
            )
            continue
        if isinstance(item, dict):
            desc = (
                item.get("description")
                or item.get("title")
                or item.get("text")
                or item.get("outcome")
                or item.get("objective")
            )
            tag = (
                item.get("skill_tag")
                or item.get("skill")
                or item.get("tag")
                or item.get("id")
                or f"skill-{idx + 1}"
            )
            desc_s = _safe_str(desc, f"Mục tiêu {idx + 1}")
            tag_s = _safe_str(tag, f"skill-{idx + 1}")[:120]
            out.append({"description": desc_s, "skill_tag": tag_s})
    if not out:
        out.append(
            {"description": "Hoàn thành nội dung module", "skill_tag": "module-complete"}
        )
    return out


def _normalize_course_learning_outcomes_stored(raw: Any) -> List[Dict[str, str]]:
    """Course document stores List[dict]; empty AI field → []."""
    if not raw or not isinstance(raw, list):
        return []
    out: List[Dict[str, str]] = []
    for idx, item in enumerate(raw):
        if isinstance(item, str):
            out.append(
                {"description": item.strip() or f"Mục tiêu {idx + 1}", "skill_tag": f"course-{idx + 1}"}
            )
            continue
        if isinstance(item, dict):
            desc = (
                item.get("description")
                or item.get("title")
                or item.get("text")
                or item.get("outcome")
                or item.get("objective")
            )
            tag = (
                item.get("skill_tag")
                or item.get("skill")
                or item.get("tag")
                or item.get("id")
                or f"course-{idx + 1}"
            )
            desc_s = _safe_str(desc, f"Mục tiêu {idx + 1}")
            tag_s = _safe_str(tag, f"course-{idx + 1}")[:120]
            out.append({"description": desc_s, "skill_tag": tag_s})
    return out


def _course_learning_outcomes_to_strings(stored: Any) -> List[str]:
    """PersonalCourseDetailResponse expects learning_outcomes: List[str]."""
    result: List[str] = []
    if not stored:
        return result
    for item in stored:
        if isinstance(item, str):
            if item.strip():
                result.append(item.strip())
        elif isinstance(item, dict):
            desc = item.get("description") or item.get("title") or item.get("text")
            if desc and str(desc).strip():
                result.append(str(desc).strip())
    return result


# ============================================================================
# Section 2.5.1: TẠO KHÓA HỌC TỪ AI PROMPT
# ============================================================================

async def create_course_from_ai_prompt(
    user_id: str,
    prompt: str,
    level: Optional[str] = "Beginner",
    estimated_duration_weeks: Optional[int] = 4,
    language: Optional[str] = "vi"
) -> Dict:
    """
    Tạo khóa học từ AI prompt
    
    Flow:
    1. Gửi prompt đến AI (Google Gemini)
    2. AI sinh ra: title, description, modules, lessons, learning outcomes
    3. Lưu vào DB với status="draft"
    4. Return course data
    
    Args:
        user_id: ID học viên
        prompt: Mô tả bằng ngôn ngữ tự nhiên
        level: Cấp độ (Beginner, Intermediate, Advanced)
        estimated_duration_weeks: Thời lượng học tập ước tính
        language: Ngôn ngữ khóa học
        
    Returns:
        Dict chứa course data và modules
    """
    # Gọi AI service để sinh course structure
    # Chú ý: ai_service.generate_course_from_prompt expects difficulty, not level
    ai_result = await generate_course_from_prompt(
        prompt=prompt,
        user_preferences=None,
        difficulty=level  # Map level to difficulty parameter
    )

    resolved_level = _normalize_course_level(
        ai_result.get("level") or level, fallback=level or "Beginner"
    )
    course_title = _safe_str(ai_result.get("title"), "Khóa học mới")
    course_description = _safe_str(
        ai_result.get("description"),
        "Khóa học được tạo từ mô tả của bạn.",
    )
    course_category = _safe_str(ai_result.get("category"), "General")
    course_learning_outcomes = _normalize_course_learning_outcomes_stored(
        ai_result.get("learning_outcomes")
    )
    
    # Tạo modules từ AI result
    modules = []
    total_lessons = 0
    
    for idx, module_data in enumerate(ai_result.get("modules", [])):
        if not isinstance(module_data, dict):
            continue
        # Tạo lessons cho module
        lessons = []
        for lesson_idx, lesson_data in enumerate(module_data.get("lessons", []) or []):
            if not isinstance(lesson_data, dict):
                continue
            lesson_title = _safe_str(lesson_data.get("title"), f"Bài {lesson_idx + 1}")
            lesson_order = _safe_int(lesson_data.get("order"), lesson_idx + 1)
            lesson = EmbeddedLesson(
                id=generate_uuid(),
                title=lesson_title,
                order=lesson_order,
                content=_safe_str(lesson_data.get("content"), ""),
                content_type=_safe_str(lesson_data.get("content_type"), "text") or "text",
                video_url=lesson_data.get("video_url"),
                duration_minutes=_safe_int(lesson_data.get("duration_minutes"), 0),
                resources=(
                    lesson_data.get("resources")
                    if isinstance(lesson_data.get("resources"), list)
                    else []
                ),
            )
            lessons.append(lesson)
            total_lessons += 1

        if not lessons:
            lessons.append(
                EmbeddedLesson(
                    id=generate_uuid(),
                    title="Bài 1",
                    order=1,
                    content="",
                    content_type="text",
                    duration_minutes=0,
                    resources=[],
                )
            )
            total_lessons += 1
        
        # Tạo module
        module_title = _safe_str(module_data.get("title"), f"Module {idx + 1}")
        module_order = _safe_int(module_data.get("order"), idx + 1)
        mod_learning_outcomes = _normalize_module_learning_outcomes(
            module_data.get("learning_outcomes")
        )
        module = EmbeddedModule(
            id=generate_uuid(),
            title=module_title,
            description=_safe_str(module_data.get("description"), ""),
            order=module_order,
            difficulty=_safe_str(module_data.get("difficulty"), "Basic") or "Basic",
            estimated_hours=float(module_data.get("estimated_hours") or 0),
            learning_outcomes=mod_learning_outcomes,
            lessons=lessons,
            total_lessons=len(lessons),
            total_duration_minutes=sum(l.duration_minutes for l in lessons)
        )
        modules.append(module)

    if not modules:
        raise ValueError(
            "AI không trả về module hợp lệ; thử lại với mô tả chi tiết hơn."
        )
    
    # Tạo Course document
    course = Course(
        id=generate_uuid(),
        title=course_title,
        description=course_description,
        category=course_category,
        level=resolved_level,
        status="draft",
        owner_id=user_id,
        owner_type="student",  # Personal course
        modules=modules,
        learning_outcomes=course_learning_outcomes,
        total_duration_minutes=sum(m.total_duration_minutes for m in modules),
        total_modules=len(modules),
        total_lessons=total_lessons,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Lưu vào DB
    await course.insert()
    
    # Return response data matching schema
    return {
        "id": course.id,  # Changed from course_id to id
        "title": course.title,
        "description": course.description,
        "category": course.category,
        "level": course.level,
        "status": course.status,
        "owner_id": course.owner_id,
        "owner_type": course.owner_type,
        "modules": [
            {
                "id": m.id,
                "title": m.title,
                "description": m.description,
                "order": m.order,
                "difficulty": m.difficulty,
                "learning_outcomes": _normalize_module_learning_outcomes(m.learning_outcomes),
                "lessons": [
                    {
                        "id": lesson.id,
                        "title": lesson.title,
                        "order": lesson.order,
                        "content_outline": lesson.content[:200] if lesson.content else ""  # First 200 chars as outline
                    }
                    for lesson in m.lessons
                ]
            }
            for m in modules
        ],
        "created_at": course.created_at
    }


# ============================================================================
# Section 2.5.2: TẠO KHÓA HỌC THỦ CÔNG
# ============================================================================

async def create_personal_course_manual(
    user_id: str,
    title: str,
    description: str,
    category: str,
    level: str,
    thumbnail_url: Optional[str] = None,
    language: str = "vi"
) -> Dict:
    """
    Tạo khóa học thủ công (empty course)
    
    Flow:
    1. Tạo course document với thông tin cơ bản
    2. Modules và lessons = empty (user sẽ tự thêm sau)
    3. Status = "draft"
    4. Lưu vào DB
    
    Args:
        user_id: ID học viên
        title: Tên khóa học
        description: Mô tả
        category: Danh mục
        level: Cấp độ
        thumbnail_url: URL hình ảnh
        language: Ngôn ngữ
        
    Returns:
        Dict chứa course data
    """
    course = Course(
        id=generate_uuid(),
        title=title,
        description=description,
        category=category,
        level=level,
        thumbnail_url=thumbnail_url,
        language=language,
        status="draft",
        owner_id=user_id,
        owner_type="student",  # Personal course
        modules=[],  # Empty - user sẽ thêm sau
        learning_outcomes=[],
        prerequisites=[],
        total_duration_minutes=0,
        enrollment_count=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Lưu vào DB
    await course.insert()
    
    return {
        "course_id": course.id,
        "title": course.title,
        "description": course.description,
        "category": course.category,
        "level": course.level,
        "status": course.status,
        "created_at": course.created_at
    }


# ============================================================================
# Section 2.5.3: XEM DANH SÁCH KHÓA HỌC CÁ NHÂN
# ============================================================================

async def list_my_personal_courses(
    user_id: str,
    status_filter: Optional[str] = None,
    search_query: Optional[str] = None
) -> Dict:
    """
    Lấy danh sách khóa học cá nhân của user
    
    Flow:
    1. Query courses với owner_id = user_id và owner_type = "student"
    2. Apply filters (status, search)
    3. Tính statistics (draft/published/archived count)
    4. Return list
    
    Args:
        user_id: ID học viên
        status_filter: Filter theo status (draft|published|archived)
        search_query: Tìm kiếm theo tên
        
    Returns:
        Dict chứa danh sách courses và statistics
    """
    # Build query
    query_conditions = {
        "owner_id": user_id,
        "owner_type": "student"
    }
    
    if status_filter:
        query_conditions["status"] = status_filter
    
    # Query courses
    if search_query:
        courses = await Course.find(
            query_conditions,
            Course.title.contains(search_query, case_insensitive=True)
        ).sort("-created_at").to_list()
    else:
        courses = await Course.find(query_conditions).sort("-created_at").to_list()
    
    # Tính statistics
    all_courses = await Course.find({
        "owner_id": user_id,
        "owner_type": "student"
    }).to_list()
    
    draft_count = sum(1 for c in all_courses if c.status == "draft")
    published_count = sum(1 for c in all_courses if c.status == "published")
    archived_count = sum(1 for c in all_courses if c.status == "archived")
    
    # Build response
    courses_data = []
    for course in courses:
        modules_count = len(course.modules) if course.modules else 0
        lessons_count = sum(len(m.lessons) for m in course.modules) if course.modules else 0
        
        courses_data.append({
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "thumbnail_url": course.thumbnail_url,
            "category": course.category,
            "level": course.level,
            "status": course.status,
            "modules_count": modules_count,
            "lessons_count": lessons_count,
            "total_duration_minutes": course.total_duration_minutes,
            "created_at": course.created_at,
            "updated_at": course.updated_at
        })
    
    return {
        "courses": courses_data,
        "total": len(courses_data),
        "draft_count": draft_count,
        "published_count": published_count,
        "archived_count": archived_count
    }


async def get_personal_course_detail(user_id: str, course_id: str) -> Optional[Dict]:
    """Lấy full detail khóa học cá nhân để chỉnh sửa (bao gồm lesson.content)."""
    course = await Course.find_one(
        Course.id == course_id,
        Course.owner_id == user_id,
        Course.owner_type == "student",
    )
    if not course:
        return None

    modules_data = []
    for m in course.modules or []:
        modules_data.append(
            {
                "id": m.id,
                "title": m.title,
                "description": m.description,
                "order": m.order,
                "difficulty": m.difficulty,
                "estimated_hours": m.estimated_hours,
                "learning_outcomes": m.learning_outcomes or [],
                "lessons": [
                    {
                        "id": l.id,
                        "title": l.title,
                        "description": l.description,
                        "order": l.order,
                        "content": l.content or "",
                        "content_type": l.content_type or "text",
                        "duration_minutes": l.duration_minutes or 0,
                        "video_url": l.video_url,
                    }
                    for l in (m.lessons or [])
                ],
            }
        )

    return {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "category": course.category,
        "level": course.level,
        "status": course.status,
        "language": course.language or "vi",
        "thumbnail_url": course.thumbnail_url,
        "learning_outcomes": _course_learning_outcomes_to_strings(course.learning_outcomes or []),
        "prerequisites": course.prerequisites or [],
        "modules": modules_data,
        "created_at": course.created_at,
        "updated_at": course.updated_at,
    }


# ============================================================================
# Section 2.5.4: CHỈNH SỬA KHÓA HỌC CÁ NHÂN
# ============================================================================

async def update_personal_course(
    user_id: str,
    course_id: str,
    update_data: Dict
) -> Optional[Dict]:
    """
    Cập nhật khóa học cá nhân
    
    Flow:
    1. Kiểm tra ownership (chỉ owner mới được update)
    2. Cập nhật các fields được cung cấp
    3. Nếu có modules data → rebuild modules list
    4. Cập nhật updated_at
    5. Save và return
    
    Args:
        user_id: ID học viên
        course_id: ID khóa học
        update_data: Dict chứa fields cần update
        
    Returns:
        Dict chứa course data sau khi update, None nếu không tìm thấy
    """
    # Query course
    course = await Course.find_one(
        Course.id == course_id,
        Course.owner_id == user_id,
        Course.owner_type == "student"
    )
    
    if not course:
        return None
    
    # Update basic fields
    if "title" in update_data and update_data["title"]:
        course.title = update_data["title"]
    
    if "description" in update_data and update_data["description"]:
        course.description = update_data["description"]
    
    if "category" in update_data and update_data["category"]:
        course.category = update_data["category"]
    
    if "level" in update_data and update_data["level"]:
        course.level = update_data["level"]
    
    if "thumbnail_url" in update_data:
        course.thumbnail_url = update_data["thumbnail_url"]
    
    if "status" in update_data and update_data["status"]:
        course.status = update_data["status"]
    
    if "learning_outcomes" in update_data:
        course.learning_outcomes = update_data["learning_outcomes"]
    
    if "prerequisites" in update_data:
        course.prerequisites = update_data["prerequisites"]
    
    # Update modules nếu có
    if "modules" in update_data and update_data["modules"] is not None:
        modules = []
        total_duration = 0
        
        for module_data in update_data["modules"]:
            # Tạo lessons
            lessons = []
            for lesson_data in module_data.get("lessons", []):
                lesson = EmbeddedLesson(
                    id=lesson_data.get("id") or generate_uuid(),
                    title=lesson_data["title"],
                    order=lesson_data["order"],
                    description=lesson_data.get("description"),
                    content=lesson_data.get("content", ""),
                    content_type=lesson_data.get("content_type", "text"),
                    video_url=lesson_data.get("video_url"),
                    duration_minutes=lesson_data.get("duration_minutes", 0),
                    resources=lesson_data.get("resources", [])
                )
                lessons.append(lesson)
            
            # Tạo module
            module = EmbeddedModule(
                id=module_data.get("id") or generate_uuid(),
                title=module_data["title"],
                description=module_data.get("description", ""),
                order=module_data["order"],
                difficulty=module_data.get("difficulty", "Basic"),
                estimated_hours=module_data.get("estimated_hours", 0),
                learning_outcomes=module_data.get("learning_outcomes", []),
                lessons=lessons,
                total_lessons=len(lessons),
                total_duration_minutes=sum((l.duration_minutes or 0) for l in lessons)
            )
            modules.append(module)
            total_duration += module.total_duration_minutes
        
        course.modules = modules
        course.total_duration_minutes = total_duration
    
    # Update timestamp
    course.updated_at = datetime.utcnow()
    
    # Save
    await course.save()
    
    # Return response
    modules_count = len(course.modules) if course.modules else 0
    lessons_count = sum(len(m.lessons) for m in course.modules) if course.modules else 0
    
    return {
        "course_id": course.id,
        "title": course.title,
        "status": course.status,
        "modules_count": modules_count,
        "lessons_count": lessons_count,
        "updated_at": course.updated_at
    }


# ============================================================================
# Section 2.5.5: XÓA KHÓA HỌC CÁ NHÂN
# ============================================================================

async def delete_personal_course(
    user_id: str,
    course_id: str
) -> Optional[Dict]:
    """
    Xóa khóa học cá nhân
    
    Flow:
    1. Kiểm tra ownership (chỉ owner mới được xóa)
    2. Xóa vĩnh viễn khỏi DB
    3. Return confirmation
    
    Args:
        user_id: ID học viên
        course_id: ID khóa học
        
    Returns:
        Dict chứa thông tin khóa học đã xóa, None nếu không tìm thấy
    """
    # Query course
    course = await Course.find_one(
        Course.id == course_id,
        Course.owner_id == user_id,
        Course.owner_type == "student"
    )
    
    if not course:
        return None
    
    # Lưu info trước khi xóa
    course_title = course.title
    
    # Xóa course
    await course.delete()
    
    return {
        "course_id": course_id,
        "course_title": course_title,
        "deleted_at": datetime.utcnow()
    }
