"""
Personal Courses Service
Business logic cho personal courses (khóa học cá nhân)
Section 2.5.1-2.5.5
"""

from typing import Dict, List, Optional
from datetime import datetime

from models.models import Course, EmbeddedModule, EmbeddedLesson, generate_uuid
from services.ai_service import generate_course_from_prompt


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
    
    # Tạo modules từ AI result
    modules = []
    total_lessons = 0
    
    for idx, module_data in enumerate(ai_result.get("modules", [])):
        # Tạo lessons cho module
        lessons = []
        for lesson_idx, lesson_data in enumerate(module_data.get("lessons", [])):
            lesson = EmbeddedLesson(
                id=generate_uuid(),
                title=lesson_data.get("title"),
                order=lesson_idx + 1,
                content=lesson_data.get("content", ""),
                content_type=lesson_data.get("content_type", "text"),
                video_url=lesson_data.get("video_url"),
                duration_minutes=lesson_data.get("duration_minutes", 0),
                resources=lesson_data.get("resources", [])
            )
            lessons.append(lesson)
            total_lessons += 1
        
        # Tạo module
        module = EmbeddedModule(
            id=generate_uuid(),
            title=module_data.get("title"),
            description=module_data.get("description", ""),
            order=idx + 1,
            difficulty=module_data.get("difficulty", "Basic"),
            estimated_hours=module_data.get("estimated_hours", 0),
            learning_outcomes=module_data.get("learning_outcomes", []),
            lessons=lessons,
            total_lessons=len(lessons),
            total_duration_minutes=sum(l.duration_minutes for l in lessons)
        )
        modules.append(module)
    
    # Tạo Course document
    course = Course(
        id=generate_uuid(),
        title=ai_result.get("title"),
        description=ai_result.get("description"),
        category=ai_result.get("category", "General"),
        level=ai_result.get("level", level),  # Use AI level or fallback to param level
        status="draft",
        owner_id=user_id,
        owner_type="student",  # Personal course
        modules=modules,
        learning_outcomes=ai_result.get("learning_outcomes", []),
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
                "learning_outcomes": m.learning_outcomes,
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
                lesson = Lesson(
                    id=lesson_data.get("id") or generate_uuid(),
                    title=lesson_data["title"],
                    order=lesson_data["order"],
                    content=lesson_data["content"],
                    content_type=lesson_data.get("content_type", "text"),
                    video_url=lesson_data.get("video_url"),
                    duration_minutes=lesson_data.get("duration_minutes", 0),
                    resources=lesson_data.get("resources", [])
                )
                lessons.append(lesson)
            
            # Tạo module
            module = Module(
                id=module_data.get("id") or generate_uuid(),
                title=module_data["title"],
                description=module_data["description"],
                order=module_data["order"],
                difficulty=module_data.get("difficulty", "Basic"),
                estimated_hours=module_data.get("estimated_hours", 0),
                learning_outcomes=module_data.get("learning_outcomes", []),
                lessons=lessons
            )
            modules.append(module)
            total_duration += int(module.estimated_hours * 60)
        
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
