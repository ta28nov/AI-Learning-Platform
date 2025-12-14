"""
Course Service - Xử lý logic liên quan đến Course
Sử dụng: Beanie ODM, MongoDB
Tuân thủ: CHUCNANG.md Section 2.3, 2.5, 3.1
"""

from datetime import datetime
from typing import Optional, List
from models.models import Course, Module, Lesson, Enrollment, EmbeddedModule, EmbeddedLesson
from beanie.operators import In, RegEx, Or


# ============================================================================
# COURSE CRUD
# ============================================================================

async def create_course(
    title: str,
    description: str,
    category: str,
    level: str,
    owner_id: str,
    owner_type: str = "admin"
) -> Course:
    """
    Tạo khóa học mới
    
    Args:
        title: Tiêu đề khóa học
        description: Mô tả
        category: Danh mục
        level: Mức độ
        owner_id: ID của người tạo
        owner_type: Loại owner (admin, instructor, student)
        
    Returns:
        Course document đã tạo
    """
    course = Course(
        title=title,
        description=description,
        category=category,
        level=level,
        owner_id=owner_id,
        owner_type=owner_type,
        status="draft"
    )
    
    await course.insert()
    return course


async def get_course_by_id(course_id: str) -> Optional[Course]:
    """
    Lấy course theo ID
    
    Args:
        course_id: ID của course
        
    Returns:
        Course document hoặc None
    """
    try:
        course = await Course.get(course_id)
        return course
    except Exception:
        return None


async def get_courses_list(
    category: Optional[str] = None,
    level: Optional[str] = None,
    status: Optional[str] = None,
    owner_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
) -> List[Course]:
    """
    Lấy danh sách courses với filter
    
    Args:
        category: Filter theo category
        level: Filter theo level
        status: Filter theo status
        owner_id: Filter theo owner
        skip: Pagination skip
        limit: Pagination limit
        
    Returns:
        List Course documents
    """
    query = Course.find()
    
    if category:
        query = query.find(Course.category == category)
    
    if level:
        query = query.find(Course.level == level)
    
    if status:
        query = query.find(Course.status == status)
    
    if owner_id:
        query = query.find(Course.owner_id == owner_id)
    
    courses = await query.skip(skip).limit(limit).to_list()
    return courses


async def update_course(
    course_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    category: Optional[str] = None,
    level: Optional[str] = None,
    thumbnail_url: Optional[str] = None,
    status: Optional[str] = None
) -> Optional[Course]:
    """
    Cập nhật thông tin course
    
    Args:
        course_id: ID của course
        title, description, category, level, thumbnail_url, status: Fields cần update
        
    Returns:
        Course document đã update hoặc None
    """
    course = await get_course_by_id(course_id)
    
    if not course:
        return None
    
    if title is not None:
        course.title = title
    
    if description is not None:
        course.description = description
    
    if category is not None:
        course.category = category
    
    if level is not None:
        course.level = level
    
    if thumbnail_url is not None:
        course.thumbnail_url = thumbnail_url
    
    if status is not None:
        course.status = status
    
    course.updated_at = datetime.utcnow()
    
    await course.save()
    return course


async def delete_course(course_id: str) -> bool:
    """
    Xóa course
    
    Args:
        course_id: ID của course
        
    Returns:
        True nếu xóa thành công, False nếu không tìm thấy
    """
    course = await get_course_by_id(course_id)
    
    if not course:
        return False
    
    await course.delete()
    return True


# ============================================================================
# MODULE MANAGEMENT (Section 2.5.1-2.5.2)
# ============================================================================

async def add_module_to_course(
    course_id: str,
    title: str,
    description: str,
    order: int,
    difficulty: str = "Basic"
) -> Optional[Course]:
    """
    Thêm module vào course
    
    Args:
        course_id: ID của course
        title: Tiêu đề module
        description: Mô tả module
        order: Thứ tự module
        difficulty: Độ khó
        
    Returns:
        Course document đã update hoặc None
    """
    course = await get_course_by_id(course_id)
    
    if not course:
        return None
    
    # Initialize modules list if not exists
    if not hasattr(course, 'modules'):
        course.modules = []
    
    new_module = EmbeddedModule(
        title=title,
        description=description,
        order=order,
        difficulty=difficulty
    )
    
    course.modules.append(new_module)
    course.updated_at = datetime.utcnow()
    
    await course.save()
    return course


async def update_module_in_course(
    course_id: str,
    module_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    order: Optional[int] = None
) -> Optional[Course]:
    """
    Cập nhật module trong course
    
    Args:
        course_id: ID của course
        module_id: ID của module
        title, description, order: Fields cần update
        
    Returns:
        Course document đã update hoặc None
    """
    course = await get_course_by_id(course_id)
    
    if not course:
        return None
    
    # Check if course has modules
    if not hasattr(course, 'modules') or not course.modules:
        return None
    
    # Tìm module
    for module in course.modules:
        if module.id == module_id:
            if title is not None:
                module.title = title
            if description is not None:
                module.description = description
            if order is not None:
                module.order = order
            break
    
    course.updated_at = datetime.utcnow()
    await course.save()
    return course


async def delete_module_from_course(course_id: str, module_id: str) -> Optional[Course]:
    """
    Xóa module khỏi course
    
    Args:
        course_id: ID của course
        module_id: ID của module
        
    Returns:
        Course document đã update hoặc None
    """
    course = await get_course_by_id(course_id)
    
    if not course:
        return None
    
    # Lọc bỏ module
    course.modules = [m for m in course.modules if m.id != module_id]
    course.updated_at = datetime.utcnow()
    
    await course.save()
    return course


# ============================================================================
# LESSON MANAGEMENT (Section 2.5.3-2.5.6)
# ============================================================================

async def add_lesson_to_module(
    course_id: str,
    module_id: str,
    title: str,
    order: int,
    content: str = "",
    content_type: str = "text",
    duration_minutes: int = 0
) -> Optional[Course]:
    """
    Thêm lesson vào module
    
    Args:
        course_id: ID của course
        module_id: ID của module
        title: Tiêu đề lesson
        order: Thứ tự lesson
        content: Nội dung
        content_type: Loại nội dung
        duration_minutes: Thời lượng
        
    Returns:
        Course document đã update hoặc None
    """
    course = await get_course_by_id(course_id)
    
    if not course:
        return None
    
    # Check if course has modules
    if not hasattr(course, 'modules') or not course.modules:
        return None
    
    # Tìm module
    for module in course.modules:
        if module.id == module_id:
            # Initialize lessons list if not exists
            if not hasattr(module, 'lessons'):
                module.lessons = []
            
            new_lesson = EmbeddedLesson(
                title=title,
                order=order,
                content=content,
                content_type=content_type,
                duration_minutes=duration_minutes
            )
            module.lessons.append(new_lesson)
            break
    
    course.updated_at = datetime.utcnow()
    await course.save()
    return course


async def update_lesson_in_module(
    course_id: str,
    module_id: str,
    lesson_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    video_url: Optional[str] = None
) -> Optional[Course]:
    """
    Cập nhật lesson trong module
    
    Args:
        course_id: ID của course
        module_id: ID của module
        lesson_id: ID của lesson
        title, content, video_url: Fields cần update
        
    Returns:
        Course document đã update hoặc None
    """
    course = await get_course_by_id(course_id)
    
    if not course:
        return None
    
    # Check if course has modules
    if not hasattr(course, 'modules') or not course.modules:
        return None
    
    # Tìm module và lesson
    for module in course.modules:
        if module.id == module_id:
            if not hasattr(module, 'lessons') or not module.lessons:
                continue
            
            for lesson in module.lessons:
                if lesson.id == lesson_id:
                    if title is not None:
                        lesson.title = title
                    if content is not None:
                        lesson.content = content
                    if video_url is not None:
                        lesson.video_url = video_url
                    break
    
    course.updated_at = datetime.utcnow()
    await course.save()
    return course


async def delete_lesson_from_module(
    course_id: str,
    module_id: str,
    lesson_id: str
) -> Optional[Course]:
    """
    Xóa lesson khỏi module
    
    Args:
        course_id: ID của course
        module_id: ID của module
        lesson_id: ID của lesson
        
    Returns:
        Course document đã update hoặc None
    """
    course = await get_course_by_id(course_id)
    
    if not course:
        return None
    
    # Check if course has modules
    if not hasattr(course, 'modules') or not course.modules:
        return None
    
    # Tìm module và xóa lesson
    for module in course.modules:
        if module.id == module_id:
            if hasattr(module, 'lessons') and module.lessons:
                module.lessons = [l for l in module.lessons if l.id != lesson_id]
            break
    
    course.updated_at = datetime.utcnow()
    await course.save()
    return course


# ============================================================================
# SEARCH & FILTER
# ============================================================================

async def count_courses(
    category: Optional[str] = None,
    level: Optional[str] = None,
    status: Optional[str] = None,
    owner_id: Optional[str] = None,
    search_term: Optional[str] = None
) -> int:
    """
    Đếm số lượng courses matching filters (không load documents)
    
    Args:
        category: Filter theo category
        level: Filter theo level
        status: Filter theo status
        owner_id: Filter theo owner
        search_term: Tìm kiếm trong title và description (regex)
        
    Returns:
        Số lượng courses matching
    """
    conditions = []
    
    # Nếu có search_term, tìm trong title HOẶC description
    if search_term:
        search_conditions = Or(
            RegEx(Course.title, search_term, "i"),
            RegEx(Course.description, search_term, "i")
        )
        conditions.append(search_conditions)
    
    if category:
        conditions.append(Course.category == category)
    
    if level:
        conditions.append(Course.level == level)
    
    if status:
        conditions.append(Course.status == status)
    
    if owner_id:
        conditions.append(Course.owner_id == owner_id)
    
    # Gọi find() với tất cả điều kiện cùng lúc
    if conditions:
        query = Course.find(*conditions)
    else:
        query = Course.find()
    
    count = await query.count()
    return count


async def search_courses(
    search_term: str,
    category: Optional[str] = None,
    level: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
) -> List[Course]:
    """
    Tìm kiếm courses theo từ khóa
    
    Args:
        search_term: Từ khóa tìm kiếm (tìm trong title, description)
        category: Filter category
        level: Filter level
        skip: Pagination skip
        limit: Pagination limit
        
    Returns:
        List Course documents matching search (chỉ published courses)
    """
    # Xây dựng điều kiện tìm kiếm: title HOẶC description chứa search_term (không phân biệt hoa thường)
    search_conditions = Or(
        RegEx(Course.title, search_term, "i"),
        RegEx(Course.description, search_term, "i")
    )
    
    # Kết hợp với điều kiện status = published
    query = Course.find(
        search_conditions,
        Course.status == "published"
    )
    
    # Thêm filter nếu có
    if category:
        query = query.find(Course.category == category)
    
    if level:
        query = query.find(Course.level == level)
    
    courses = await query.skip(skip).limit(limit).to_list()
    return courses


async def get_published_courses(
    skip: int = 0,
    limit: int = 50
) -> List[Course]:
    """
    Lấy danh sách courses đã publish
    
    Args:
        skip: Pagination skip
        limit: Pagination limit
        
    Returns:
        List Course documents với status=published
    """
    courses = await Course.find(
        Course.status == "published"
    ).skip(skip).limit(limit).to_list()
    
    return courses


async def get_user_created_courses(
    owner_id: str,
    skip: int = 0,
    limit: int = 50
) -> List[Course]:
    """
    Lấy các courses do user tạo (instructor/student personal courses)
    
    Args:
        owner_id: ID của owner
        skip: Pagination skip
        limit: Pagination limit
        
    Returns:
        List Course documents
    """
    courses = await Course.find(
        Course.owner_id == owner_id
    ).skip(skip).limit(limit).to_list()
    
    return courses


# ============================================================================
# ADMIN COURSE MANAGEMENT (Section 4.2)
# ============================================================================

async def list_all_courses_admin(
    author_id: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    course_type: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    skip: int = 0,
    limit: int = 50
) -> dict:
    """
    4.2.1: Xem tất cả khóa học (Admin)
    
    Business logic:
    - List tất cả courses (public + personal)
    - Filter: author, status, category, type
    - Search: tên khóa học
    - Sort: theo columns
    - Show: tên, tác giả, type, enrollment_count, status, created_at
    
    Args:
        author_id: Filter theo author (owner_id)
        status: draft|published|archived
        category: Filter theo category
        course_type: public|personal
        search: Search text (title)
        sort_by: Field sort
        sort_order: asc|desc
        skip: Pagination skip
        limit: Pagination limit
        
    Returns:
        Dict với data, total, skip, limit, has_next
    """
    from models.models import User
    
    # Build query
    query_conditions = []
    
    if author_id:
        query_conditions.append(Course.owner_id == author_id)
    
    if status:
        query_conditions.append(Course.status == status)
    
    if category:
        query_conditions.append(Course.category == category)
    
    if course_type:
        if course_type == "public":
            query_conditions.append(Course.owner_type == "admin")
        else:  # personal
            query_conditions.append(Course.owner_type != "admin")
    
    # Get courses
    if query_conditions:
        query = Course.find(*query_conditions)
    else:
        query = Course.find()
    
    # Sort
    if sort_order == "desc":
        query = query.sort(f"-{sort_by}")
    else:
        query = query.sort(f"+{sort_by}")
    
    # Count total
    total = await query.count()
    
    # Pagination
    courses = await query.skip(skip).limit(limit).to_list()
    
    # Search filter
    if search:
        search_lower = search.lower()
        courses = [c for c in courses if search_lower in c.title.lower()]
        total = len(courses)
    
    # Build response
    course_items = []
    
    for course in courses:
        # Get author info
        author = await User.get(course.owner_id)
        
        author_info = {
            "user_id": course.owner_id,
            "full_name": author.full_name if author else "Unknown",
            "email": author.email if author else "unknown@email.com",
            "role": author.role if author else "unknown"
        }
        
        # Determine course type
        c_type = "public" if course.owner_type == "admin" else "personal"
        
        course_items.append({
            "course_id": str(course.id),
            "title": course.title,
            "thumbnail_url": course.thumbnail_url,
            "author": author_info,
            "course_type": c_type,
            "enrollment_count": course.enrollment_count,
            "status": course.status,
            "category": course.category,
            "level": course.level,
            "created_at": course.created_at,
            "updated_at": course.updated_at
        })
    
    has_next = (skip + limit) < total
    
    return {
        "data": course_items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_next": has_next
    }


async def get_course_detail_admin(course_id: str) -> dict:
    """
    4.2.2: Xem chi tiết khóa học (Admin)
    
    Business logic:
    - Xem thông tin đầy đủ course
    - Metadata, cấu trúc modules/lessons
    - Analytics: enrollment_count, completion_rate
    - Preview course như student
    
    Args:
        course_id: ID của course
        
    Returns:
        Dict với course info, modules, analytics
        
    Raises:
        Exception: Nếu course không tồn tại
    """
    from models.models import User
    
    course = await get_course_by_id(course_id)
    
    if not course:
        raise Exception("Khóa học không tồn tại")
    
    # Get author
    author = await User.get(course.owner_id)
    
    author_info = {
        "user_id": course.owner_id,
        "full_name": author.full_name if author else "Unknown",
        "email": author.email if author else "unknown@email.com",
        "role": author.role if author else "unknown"
    }
    
    # Build modules summary
    modules_summary = []
    for module in course.modules:
        modules_summary.append({
            "module_id": module.id,
            "title": module.title,
            "order": module.order,
            "lesson_count": len(module.lessons),
            "estimated_hours": module.estimated_hours
        })
    
    # Get analytics
    enrollments = await Enrollment.find(
        Enrollment.course_id == course_id
    ).to_list()
    
    total_enrollments = len(enrollments)
    completed_enrollments = sum(1 for e in enrollments if e.status == "completed")
    completion_rate = (completed_enrollments / total_enrollments * 100) if total_enrollments > 0 else 0
    active_students = sum(1 for e in enrollments if e.status == "active")
    
    analytics = {
        "enrollment_count": total_enrollments,
        "completion_rate": round(completion_rate, 2),
        "avg_rating": course.avg_rating,
        "total_students_active": active_students
    }
    
    # Determine course type
    c_type = "public" if course.owner_type == "admin" else "personal"
    
    return {
        "course_id": str(course.id),
        "title": course.title,
        "description": course.description,
        "thumbnail_url": course.thumbnail_url,
        "preview_video_url": course.preview_video_url,
        "category": course.category,
        "level": course.level,
        "language": course.language,
        "status": course.status,
        "course_type": c_type,
        "author": author_info,
        "modules": modules_summary,
        "total_duration_minutes": course.total_duration_minutes,
        "prerequisites": course.prerequisites,
        "learning_outcomes": course.learning_outcomes,
        "analytics": analytics,
        "created_at": course.created_at,
        "updated_at": course.updated_at
    }


async def create_course_admin(
    admin_id: str,
    title: str,
    description: str,
    category: str,
    level: str,
    language: str = "vi",
    thumbnail_url: Optional[str] = None,
    preview_video_url: Optional[str] = None,
    prerequisites: List[str] = None,
    learning_outcomes: List[dict] = None,
    status: str = "draft"
) -> dict:
    """
    4.2.3: Tạo khóa học chính thức (Admin)
    
    Business logic:
    - Admin tạo official course (public)
    - owner_type = "admin"
    - Có thể thiết kế modules/lessons
    - Có thể publish ngay
    
    Args:
        admin_id: ID của admin tạo
        title, description, category, level: Course metadata
        language: Ngôn ngữ (default vi)
        thumbnail_url, preview_video_url: Media URLs
        prerequisites: List yêu cầu kiến thức
        learning_outcomes: List mục tiêu học tập
        status: draft|published
        
    Returns:
        Dict với course_id, title, status, created_by, message
    """
    course = Course(
        title=title,
        description=description,
        category=category,
        level=level,
        language=language,
        owner_id=admin_id,
        owner_type="admin",
        thumbnail_url=thumbnail_url,
        preview_video_url=preview_video_url,
        prerequisites=prerequisites or [],
        learning_outcomes=learning_outcomes or [],
        status=status
    )
    
    await course.insert()
    
    return {
        "course_id": str(course.id),
        "title": course.title,
        "status": course.status,
        "course_type": "public",
        "created_by": admin_id,
        "created_at": course.created_at,
        "message": "Khóa học chính thức đã được tạo thành công"
    }


async def update_course_admin(
    course_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    category: Optional[str] = None,
    level: Optional[str] = None,
    language: Optional[str] = None,
    thumbnail_url: Optional[str] = None,
    preview_video_url: Optional[str] = None,
    prerequisites: Optional[List[str]] = None,
    learning_outcomes: Optional[List[dict]] = None,
    status: Optional[str] = None
) -> dict:
    """
    4.2.4: Chỉnh sửa bất kỳ khóa học nào (Admin)
    
    Business logic:
    - Admin có quyền sửa BẤT KỲ course nào
    - Bao gồm personal courses của user
    - Có thể sửa nội dung, cấu trúc, metadata
    - Kiểm duyệt chất lượng
    
    Args:
        course_id: ID của course
        title, description, etc: Fields cần update
        
    Returns:
        Dict với course_id, title, status, updated_at, message
        
    Raises:
        Exception: Nếu course không tồn tại
    """
    course = await get_course_by_id(course_id)
    
    if not course:
        raise Exception("Khóa học không tồn tại")
    
    # Update fields
    if title:
        course.title = title
    
    if description:
        course.description = description
    
    if category:
        course.category = category
    
    if level:
        course.level = level
    
    if language:
        course.language = language
    
    if thumbnail_url is not None:
        course.thumbnail_url = thumbnail_url
    
    if preview_video_url is not None:
        course.preview_video_url = preview_video_url
    
    if prerequisites is not None:
        course.prerequisites = prerequisites
    
    if learning_outcomes is not None:
        course.learning_outcomes = learning_outcomes
    
    if status:
        course.status = status
    
    course.updated_at = datetime.utcnow()
    await course.save()
    
    return {
        "course_id": str(course.id),
        "title": course.title,
        "status": course.status,
        "updated_at": course.updated_at,
        "message": "Khóa học đã được cập nhật thành công"
    }


async def delete_course_admin(course_id: str) -> dict:
    """
    4.2.5: Xóa khóa học (Admin)
    
    Business logic:
    - Kiểm tra impact:
      * Số học viên đang học
      * Số lớp đang sử dụng course
    - Cảnh báo chi tiết impact
    - Xóa vĩnh viễn (không thể khôi phục)
    
    Args:
        course_id: ID của course
        
    Returns:
        Dict với course_id, title, impact, message
        
    Raises:
        Exception: Nếu có blocking dependencies
    """
    from models.models import Class
    
    course = await get_course_by_id(course_id)
    
    if not course:
        raise Exception("Khóa học không tồn tại")
    
    # Check impact
    # 1. Enrollments
    enrollments = await Enrollment.find(
        Enrollment.course_id == course_id
    ).to_list()
    
    enrolled_students = len(enrollments)
    active_enrollments = sum(1 for e in enrollments if e.status == "active")
    
    # 2. Classes using this course
    classes_using = await Class.find(
        Class.course_id == course_id
    ).to_list()
    
    active_classes = sum(1 for c in classes_using if c.status == "active")
    
    # 3. Personal courses derived from this
    personal_courses = await Course.find(
        Course.owner_type != "admin"
    ).count()
    
    # Build impact analysis
    impact = {
        "enrolled_students": enrolled_students,
        "active_classes": len(classes_using),
        "personal_courses_derived": 0,
        "warning": ""
    }
    
    if active_enrollments > 0:
        impact["warning"] += f"{active_enrollments} học viên đang học khóa này. "
    
    if active_classes > 0:
        impact["warning"] += f"{active_classes} lớp học đang sử dụng khóa học này. "
    
    if active_enrollments > 0 or active_classes > 0:
        raise Exception(
            f"Không thể xóa khóa học: {impact['warning']}"
            "Vui lòng hoàn thành hoặc hủy các enrollment/class trước."
        )
    
    # Delete course
    await course.delete()
    
    return {
        "course_id": str(course_id),
        "title": course.title,
        "impact": impact,
        "message": "Khóa học đã được xóa vĩnh viễn khỏi hệ thống"
    }

