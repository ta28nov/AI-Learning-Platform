"""
Search Service - Xử lý universal search và filtering
Sử dụng: Beanie ODM, MongoDB text search
Tuân thủ: CHUCNANG.md Section 5.1
"""

import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from fastapi import HTTPException, status
from models.models import Course, User, Class, Module, Lesson
from utils.utils import normalize_search_query, calculate_relevance_score


# ============================================================================
# Section 5.1: UNIVERSAL SEARCH & ADVANCED FILTERING
# ============================================================================

async def universal_search(
    query: str,
    current_user: Dict,
    category_filter: Optional[str] = None,
    level_filter: Optional[str] = None,
    instructor_filter: Optional[str] = None,
    rating_filter: Optional[float] = None,
    page: int = 1,
    limit: int = 20
) -> Dict:
    """
    Universal search box - tìm kiếm thông minh với filter nâng cao
    
    Business Logic:
    1. Full-text search across multiple collections (courses, users, classes, modules, lessons)
    2. Apply filters: category, level, instructor, rating
    3. Calculate relevance score for each result
    4. Group results by category
    5. Generate search suggestions (autocomplete, typo correction)
    6. Save search history for logged-in users
    
    Args:
        query: Từ khóa tìm kiếm
        current_user: User context (role, permissions)
        category_filter: Programming/Math/Business...
        level_filter: Beginner/Intermediate/Advanced
        instructor_filter: Lọc theo giảng viên
        rating_filter: Đánh giá tối thiểu
        page: Trang hiện tại
        limit: Số kết quả per page
        
    Returns:
        Dict chứa kết quả search grouped by category với suggestions
    """
    start_time = time.time()
    
    # Normalize search query
    normalized_query = normalize_search_query(query)
    search_regex = re.compile(normalized_query, re.IGNORECASE)
    
    # Initialize results storage
    results_by_category = []
    total_results = 0
    
    # 1. Search Courses
    course_results = await _search_courses(
        search_regex, current_user, category_filter, 
        level_filter, instructor_filter, rating_filter
    )
    if course_results['items']:
        results_by_category.append(course_results)
        total_results += course_results['count']
    
    # 2. Search Users (if has permission)
    if _can_search_users(current_user):
        user_results = await _search_users(search_regex, current_user)
        if user_results['items']:
            results_by_category.append(user_results)
            total_results += user_results['count']
    
    # 3. Search Classes  
    class_results = await _search_classes(search_regex, current_user)
    if class_results['items']:
        results_by_category.append(class_results)
        total_results += class_results['count']
    
    # 4. Search Modules
    module_results = await _search_modules(search_regex, current_user)
    if module_results['items']:
        results_by_category.append(module_results)
        total_results += module_results['count']
    
    # 5. Search Lessons
    lesson_results = await _search_lessons(search_regex, current_user)
    if lesson_results['items']:
        results_by_category.append(lesson_results)
        total_results += lesson_results['count']
    
    # Apply pagination across all categories
    paginated_results = _apply_pagination(results_by_category, page, limit)
    
    # Generate search suggestions
    suggestions = await _generate_suggestions(query, normalized_query)
    
    # Save search history for logged-in users
    if current_user.get("user_id"):
        await _save_search_history(
            current_user["user_id"], query, total_results
        )
    
    # Calculate search time
    search_time_ms = int((time.time() - start_time) * 1000)
    
    return {
        "query": query,
        "total_results": total_results,
        "results_by_category": paginated_results,
        "suggestions": suggestions,
        "search_time_ms": search_time_ms,
        "filters_applied": {
            "category": category_filter,
            "level": level_filter,
            "instructor": instructor_filter,
            "rating": rating_filter
        }
    }


async def _search_courses(
    search_regex: re.Pattern,
    current_user: Dict,
    category_filter: Optional[str],
    level_filter: Optional[str], 
    instructor_filter: Optional[str],
    rating_filter: Optional[float]
) -> Dict:
    """
    Tìm kiếm khóa học với filters
    
    Business Logic:
    1. Search trong title, description, instructor_name
    2. Apply category, level, instructor, rating filters
    3. Calculate relevance score based on match quality
    4. Return only published courses for students
    """
    # Build query conditions
    query_conditions = []
    
    # Text search conditions
    text_conditions = [
        Course.title.regex(search_regex),
        Course.description.regex(search_regex),
        Course.instructor_name.regex(search_regex)
    ]
    from beanie.operators import Or
    query_conditions.append(Or(*text_conditions))
    
    # Status filter - students only see published courses
    if current_user.get("role") == "student":
        query_conditions.append(Course.status == "published")
    elif current_user.get("role") in ["instructor", "admin"]:
        # Instructors and admins can see draft/published
        query_conditions.append(Course.status.in_(["draft", "published"]))
    
    # Apply filters
    if category_filter:
        query_conditions.append(Course.category == category_filter)
    
    if level_filter:
        query_conditions.append(Course.level == level_filter)
    
    if instructor_filter:
        query_conditions.append(Course.instructor_id == instructor_filter)
    
    if rating_filter:
        query_conditions.append(Course.rating >= rating_filter)
    
    # Execute search
    from beanie.operators import And
    if query_conditions:
        courses = await Course.find(And(*query_conditions)).to_list()
    else:
        courses = []
    
    # Format results with relevance scoring
    course_items = []
    for course in courses:
        relevance_score = calculate_relevance_score(
            search_regex.pattern, 
            [course.title, course.description, course.instructor_name]
        )
        
        # Build metadata
        metadata = {
            "instructor_name": course.instructor_name,
            "category": course.category,
            "level": course.level,
            "rating": course.rating,
            "enrollment_count": getattr(course, 'enrollment_count', 0),
            "duration_hours": getattr(course, 'duration_hours', 0)
        }
        
        course_items.append({
            "id": str(course.id),
            "type": "course",
            "title": course.title,
            "description": course.description[:200] + "..." if len(course.description) > 200 else course.description,
            "relevance_score": relevance_score,
            "url": f"/courses/{course.id}",
            "metadata": metadata
        })
    
    # Sort by relevance score
    course_items.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    return {
        "category": "courses",
        "count": len(course_items),
        "items": course_items
    }


async def _search_users(search_regex: re.Pattern, current_user: Dict) -> Dict:
    """
    Tìm kiếm users (chỉ admin và instructor có quyền)
    
    Business Logic:
    1. Only admin can search all users
    2. Instructors can search students only
    3. Search in full_name, email
    4. Exclude inactive/deleted users
    """
    # Permission check
    user_role = current_user.get("role")
    if user_role not in ["admin", "instructor"]:
        return {"category": "users", "count": 0, "items": []}
    
    # Build query
    query_conditions = [
        User.status == "active"  # Only active users
    ]
    
    # Text search
    text_conditions = [
        User.full_name.regex(search_regex),
        User.email.regex(search_regex)
    ]
    from beanie.operators import Or, And
    query_conditions.append(Or(*text_conditions))
    
    # Role restrictions
    if user_role == "instructor":
        # Instructors can only search students
        query_conditions.append(User.role == "student")
    elif user_role == "admin":
        # Admins can search all roles
        pass
    
    # Execute search
    users = await User.find(And(*query_conditions)).to_list()
    
    # Format results
    user_items = []
    for user in users:
        relevance_score = calculate_relevance_score(
            search_regex.pattern,
            [user.full_name, user.email]
        )
        
        metadata = {
            "role": user.role,
            "email": user.email,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None
        }
        
        user_items.append({
            "id": str(user.id),
            "type": "user",
            "title": user.full_name,
            "description": f"{user.role.title()} • {user.email}",
            "relevance_score": relevance_score,
            "url": f"/users/{user.id}",
            "metadata": metadata
        })
    
    # Sort by relevance
    user_items.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    return {
        "category": "users",
        "count": len(user_items),
        "items": user_items
    }


async def _search_classes(search_regex: re.Pattern, current_user: Dict) -> Dict:
    """
    Tìm kiếm lớp học
    
    Business Logic:
    1. Students see classes they're enrolled in
    2. Instructors see their own classes + classes they can view
    3. Admins see all classes
    4. Search in class_name, description
    """
    user_role = current_user.get("role")
    user_id = current_user.get("user_id")
    
    query_conditions = []
    
    # Text search
    text_conditions = [
        Class.class_name.regex(search_regex),
        Class.description.regex(search_regex)
    ]
    from beanie.operators import Or, And
    query_conditions.append(Or(*text_conditions))
    
    # Role-based filtering
    if user_role == "student":
        # Students see classes they're enrolled in
        query_conditions.append(Class.students.in_([user_id]))
    elif user_role == "instructor":
        # Instructors see their classes + public classes
        instructor_classes = Class.instructor_id == user_id
        public_classes = Class.visibility == "public"
        query_conditions.append(Or(instructor_classes, public_classes))
    elif user_role == "admin":
        # Admins see all classes
        pass
    
    # Execute search
    classes = await Class.find(And(*query_conditions) if query_conditions else {}).to_list()
    
    # Format results
    class_items = []
    for class_obj in classes:
        relevance_score = calculate_relevance_score(
            search_regex.pattern,
            [class_obj.class_name, class_obj.description]
        )
        
        # Get instructor info
        instructor = await User.get(class_obj.instructor_id)
        instructor_name = instructor.full_name if instructor else "Unknown"
        
        metadata = {
            "instructor_name": instructor_name,
            "student_count": len(class_obj.students),
            "status": class_obj.status,
            "start_date": class_obj.start_date.isoformat() if class_obj.start_date else None
        }
        
        class_items.append({
            "id": str(class_obj.id),
            "type": "class",
            "title": class_obj.class_name,
            "description": class_obj.description[:200] + "..." if len(class_obj.description) > 200 else class_obj.description,
            "relevance_score": relevance_score,
            "url": f"/classes/{class_obj.id}",
            "metadata": metadata
        })
    
    # Sort by relevance
    class_items.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    return {
        "category": "classes", 
        "count": len(class_items),
        "items": class_items
    }


async def _search_modules(search_regex: re.Pattern, current_user: Dict) -> Dict:
    """
    Tìm kiếm modules trong courses
    
    Business Logic:
    1. Search trong module title, description
    2. Only return modules from accessible courses
    3. Include course context in results
    """
    # Get accessible courses for user
    accessible_course_ids = await _get_accessible_course_ids(current_user)
    
    if not accessible_course_ids:
        return {"category": "modules", "count": 0, "items": []}
    
    # Search modules
    query_conditions = [
        Module.course_id.in_(accessible_course_ids)
    ]
    
    # Text search
    text_conditions = [
        Module.title.regex(search_regex),
        Module.description.regex(search_regex)
    ]
    from beanie.operators import Or, And
    query_conditions.append(Or(*text_conditions))
    
    modules = await Module.find(And(*query_conditions)).to_list()
    
    # Format results
    module_items = []
    for module in modules:
        relevance_score = calculate_relevance_score(
            search_regex.pattern,
            [module.title, module.description]
        )
        
        # Get course info
        course = await Course.get(module.course_id)
        course_title = course.title if course else "Unknown Course"
        
        metadata = {
            "course_id": str(module.course_id),
            "course_title": course_title,
            "lesson_count": len(module.lessons) if hasattr(module, 'lessons') else 0,
            "order": module.order
        }
        
        module_items.append({
            "id": str(module.id),
            "type": "module",
            "title": module.title,
            "description": f"Trong khóa: {course_title} • {module.description[:150]}",
            "relevance_score": relevance_score,
            "url": f"/courses/{module.course_id}/modules/{module.id}",
            "metadata": metadata
        })
    
    # Sort by relevance
    module_items.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    return {
        "category": "modules",
        "count": len(module_items),
        "items": module_items
    }


async def _search_lessons(search_regex: re.Pattern, current_user: Dict) -> Dict:
    """
    Tìm kiếm lessons trong modules
    
    Business Logic:
    1. Search trong lesson title, content
    2. Only return lessons from accessible courses
    3. Include module/course context
    """
    # Get accessible courses for user
    accessible_course_ids = await _get_accessible_course_ids(current_user)
    
    if not accessible_course_ids:
        return {"category": "lessons", "count": 0, "items": []}
    
    # Get modules from accessible courses
    accessible_modules = await Module.find(
        Module.course_id.in_(accessible_course_ids)
    ).to_list()
    accessible_module_ids = [str(mod.id) for mod in accessible_modules]
    
    if not accessible_module_ids:
        return {"category": "lessons", "count": 0, "items": []}
    
    # Search lessons
    query_conditions = [
        Lesson.module_id.in_(accessible_module_ids)
    ]
    
    # Text search
    text_conditions = [
        Lesson.title.regex(search_regex),
        Lesson.content.regex(search_regex)
    ]
    from beanie.operators import Or, And
    query_conditions.append(Or(*text_conditions))
    
    lessons = await Lesson.find(And(*query_conditions)).to_list()
    
    # Format results
    lesson_items = []
    for lesson in lessons:
        relevance_score = calculate_relevance_score(
            search_regex.pattern,
            [lesson.title, lesson.content]
        )
        
        # Get module and course info
        module = next((m for m in accessible_modules if str(m.id) == lesson.module_id), None)
        if module:
            course = await Course.get(module.course_id)
            course_title = course.title if course else "Unknown Course"
            module_title = module.title
        else:
            course_title = "Unknown Course"
            module_title = "Unknown Module"
        
        metadata = {
            "module_id": lesson.module_id,
            "module_title": module_title,
            "course_title": course_title,
            "lesson_type": lesson.type,
            "duration_minutes": getattr(lesson, 'duration_minutes', 0)
        }
        
        lesson_items.append({
            "id": str(lesson.id),
            "type": "lesson",
            "title": lesson.title,
            "description": f"Trong: {course_title} → {module_title} • {lesson.content[:150]}...",
            "relevance_score": relevance_score,
            "url": f"/courses/{module.course_id}/modules/{lesson.module_id}/lessons/{lesson.id}",
            "metadata": metadata
        })
    
    # Sort by relevance
    lesson_items.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    return {
        "category": "lessons",
        "count": len(lesson_items),
        "items": lesson_items
    }


async def _get_accessible_course_ids(current_user: Dict) -> List[str]:
    """
    Lấy danh sách course IDs mà user có quyền truy cập
    """
    user_role = current_user.get("role")
    user_id = current_user.get("user_id")
    
    if user_role == "admin":
        # Admin có quyền truy cập tất cả courses
        courses = await Course.find().to_list()
        return [str(course.id) for course in courses]
    
    elif user_role == "instructor":
        # Instructor truy cập courses họ tạo + published courses
        instructor_courses = await Course.find(Course.instructor_id == user_id).to_list()
        published_courses = await Course.find(Course.status == "published").to_list()
        
        all_courses = instructor_courses + published_courses
        # Remove duplicates
        unique_course_ids = list(set(str(course.id) for course in all_courses))
        return unique_course_ids
    
    elif user_role == "student":
        # Student chỉ truy cập published courses và enrolled courses
        from models.models import Enrollment
        
        # Get enrolled courses
        enrollments = await Enrollment.find(Enrollment.user_id == user_id).to_list()
        enrolled_course_ids = [enrollment.course_id for enrollment in enrollments]
        
        # Get published courses
        published_courses = await Course.find(Course.status == "published").to_list()
        published_course_ids = [str(course.id) for course in published_courses]
        
        # Combine and remove duplicates
        all_course_ids = list(set(enrolled_course_ids + published_course_ids))
        return all_course_ids
    
    else:
        # Guest users - only published courses
        published_courses = await Course.find(Course.status == "published").to_list()
        return [str(course.id) for course in published_courses]


def _can_search_users(current_user: Dict) -> bool:
    """
    Kiểm tra user có quyền search users không
    """
    user_role = current_user.get("role")
    return user_role in ["admin", "instructor"]


async def _generate_suggestions(original_query: str, normalized_query: str) -> List[Dict]:
    """
    Generate search suggestions: autocomplete, typo correction, popular searches
    """
    suggestions = []
    
    # 1. Autocomplete suggestions từ course titles
    autocomplete_courses = await Course.find(
        Course.title.regex(re.compile(f"^{re.escape(normalized_query)}", re.IGNORECASE))
    ).limit(3).to_list()
    
    for course in autocomplete_courses:
        suggestions.append({
            "query": course.title,
            "type": "autocomplete",
            "score": 90.0
        })
    
    # 2. Typo correction suggestions (simplified)
    if len(original_query) > 3:
        # Basic typo suggestions - trong production có thể dùng library như difflib
        common_terms = ["python", "javascript", "react", "nodejs", "database", "api", "frontend", "backend"]
        for term in common_terms:
            if _similar_strings(original_query.lower(), term, threshold=0.7):
                suggestions.append({
                    "query": term,
                    "type": "typo_correction",
                    "score": 80.0
                })
    
    # 3. Popular searches (mock data - trong production lấy từ analytics)
    popular_searches = ["Python cơ bản", "React JS", "Database design", "API development", "Frontend basics"]
    for popular in popular_searches[:2]:  # Chỉ lấy 2 cái
        if normalized_query.lower() in popular.lower():
            suggestions.append({
                "query": popular,
                "type": "popular",
                "score": 70.0
            })
    
    # Sort by score và remove duplicates
    seen_queries = set()
    unique_suggestions = []
    for suggestion in sorted(suggestions, key=lambda x: x["score"], reverse=True):
        if suggestion["query"].lower() not in seen_queries:
            seen_queries.add(suggestion["query"].lower())
            unique_suggestions.append(suggestion)
    
    return unique_suggestions[:5]  # Limit 5 suggestions


def _similar_strings(s1: str, s2: str, threshold: float = 0.7) -> bool:
    """
    Kiểm tra 2 strings có similar không (simplified similarity check)
    """
    if len(s1) == 0 or len(s2) == 0:
        return False
    
    # Simple character-based similarity
    common_chars = len(set(s1.lower()) & set(s2.lower()))
    total_chars = len(set(s1.lower()) | set(s2.lower()))
    
    similarity = common_chars / total_chars if total_chars > 0 else 0
    return similarity >= threshold


def _apply_pagination(results_by_category: List[Dict], page: int, limit: int) -> List[Dict]:
    """
    Apply pagination across all categories
    """
    # Flatten all results với category info
    all_results = []
    for category_group in results_by_category:
        for item in category_group["items"]:
            item["category"] = category_group["category"]
            all_results.append(item)
    
    # Sort by relevance score across all categories
    all_results.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    # Apply pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_items = all_results[start_idx:end_idx]
    
    # Group back by category
    paginated_by_category = {}
    for item in paginated_items:
        category = item.pop("category")  # Remove category from item
        if category not in paginated_by_category:
            paginated_by_category[category] = {
                "category": category,
                "count": 0,
                "items": []
            }
        paginated_by_category[category]["items"].append(item)
        paginated_by_category[category]["count"] += 1
    
    return list(paginated_by_category.values())


async def _save_search_history(user_id: str, query: str, results_count: int) -> None:
    """
    Lưu lịch sử tìm kiếm của user (simplified - có thể dùng separate collection)
    """
    try:
        # Trong production, có thể tạo separate SearchHistory collection
        # Ở đây simplified bằng cách update user document
        user = await User.get(user_id)
        if user:
            # Initialize search_history if not exists
            if not hasattr(user, 'search_history'):
                user.search_history = []
            
            # Add new search to history
            search_entry = {
                "query": query,
                "timestamp": datetime.utcnow(),
                "results_count": results_count
            }
            
            # Keep only last 50 searches
            user.search_history.append(search_entry)
            if len(user.search_history) > 50:
                user.search_history = user.search_history[-50:]
            
            await user.save()
    except Exception as e:
        # Log error nhưng không fail search request
        print(f"Error saving search history: {e}")


async def get_search_history(user_id: str) -> Dict:
    """
    Lấy lịch sử tìm kiếm của user
    """
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User không tồn tại"
        )
    
    search_history = getattr(user, 'search_history', [])
    
    # Get popular searches (mock - trong production từ analytics)
    popular_searches = [
        "Python programming", "Web development", "Data science", 
        "Machine learning", "JavaScript basics"
    ]
    
    return {
        "user_id": user_id,
        "search_history": search_history[-20:],  # Last 20 searches
        "popular_searches": popular_searches
    }


async def get_search_analytics() -> Dict:
    """
    Lấy search analytics cho admin (simplified)
    """
    # Trong production, tính toán từ dedicated analytics collection
    # Ở đây return mock data structure
    
    return {
        "total_searches": 1500,
        "avg_results_per_search": 8.5,
        "popular_categories": [
            {"category": "courses", "count": 800},
            {"category": "modules", "count": 450},
            {"category": "lessons", "count": 200},
            {"category": "users", "count": 50}
        ],
        "no_results_queries": [
            "advanced quantum computing",
            "deep space programming",
            "alien technology basics"
        ],
        "avg_search_time_ms": 125.5
    }