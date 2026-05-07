"""
Search Service - Universal search with model-aligned fields.
"""

import re
import time
from datetime import datetime
from typing import Dict, List, Optional

from beanie.operators import And, Or

from models.models import Class, Course, Enrollment, Lesson, Module, User
from utils.utils import calculate_relevance_score, normalize_search_query


async def universal_search(
    query: str,
    current_user: Dict,
    category_filter: Optional[str] = None,
    level_filter: Optional[str] = None,
    instructor_filter: Optional[str] = None,
    rating_filter: Optional[float] = None,
    page: int = 1,
    limit: int = 20,
) -> Dict:
    start_time = time.time()
    normalized_query = normalize_search_query(query)
    search_regex = re.compile(normalized_query, re.IGNORECASE)

    groups = [
        await _search_courses(search_regex, current_user, category_filter, level_filter, instructor_filter, rating_filter),
        await _search_users(search_regex, current_user),
        await _search_classes(search_regex, current_user),
        await _search_modules(search_regex, current_user),
        await _search_lessons(search_regex, current_user),
    ]

    non_empty_groups = [g for g in groups if g["items"]]
    total_results = sum(g["count"] for g in non_empty_groups)
    paginated_results = _apply_pagination(non_empty_groups, page, limit)
    suggestions = await _generate_suggestions(query, normalized_query)

    return {
        "query": query,
        "total_results": total_results,
        "results_by_category": paginated_results,
        "suggestions": suggestions,
        "search_time_ms": int((time.time() - start_time) * 1000),
        "filters_applied": {
            "category": category_filter,
            "level": level_filter,
            "instructor": instructor_filter,
            "rating": rating_filter,
        },
    }


async def _search_courses(search_regex, current_user, category_filter, level_filter, instructor_filter, rating_filter) -> Dict:
    conditions = [
        Or(Course.title.regex(search_regex), Course.description.regex(search_regex), Course.instructor_name.regex(search_regex))
    ]
    if current_user.get("role") == "student":
        conditions.append(Course.status == "published")
    if category_filter:
        conditions.append(Course.category == category_filter)
    if level_filter:
        conditions.append(Course.level == level_filter)
    if instructor_filter:
        conditions.append(Course.instructor_id == instructor_filter)
    if rating_filter is not None:
        conditions.append(Course.avg_rating >= rating_filter)

    courses = await Course.find(And(*conditions)).to_list()
    items = []
    for course in courses:
        items.append({
            "id": str(course.id),
            "type": "course",
            "title": course.title,
            "description": (course.description or "")[:200],
            "relevance_score": calculate_relevance_score(search_regex.pattern, [course.title, course.description or "", course.instructor_name or ""]),
            "url": f"/courses/{course.id}",
            "metadata": {
                "instructor_name": course.instructor_name,
                "category": course.category,
                "level": course.level,
                "rating": course.avg_rating,
                "enrollment_count": course.enrollment_count,
                "duration_minutes": course.total_duration_minutes,
            },
        })
    items.sort(key=lambda x: x["relevance_score"], reverse=True)
    return {"category": "courses", "count": len(items), "items": items}


async def _search_users(search_regex, current_user: Dict) -> Dict:
    role = current_user.get("role")
    if role not in ["admin", "instructor"]:
        return {"category": "users", "count": 0, "items": []}
    conditions = [User.status == "active", Or(User.full_name.regex(search_regex), User.email.regex(search_regex))]
    if role == "instructor":
        conditions.append(User.role == "student")
    users = await User.find(And(*conditions)).to_list()
    items = [{
        "id": str(user.id),
        "type": "user",
        "title": user.full_name,
        "description": f"{user.role.title()} • {user.email}",
        "relevance_score": calculate_relevance_score(search_regex.pattern, [user.full_name, user.email]),
        "url": f"/users/{user.id}",
        "metadata": {"role": user.role, "email": user.email, "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None},
    } for user in users]
    items.sort(key=lambda x: x["relevance_score"], reverse=True)
    return {"category": "users", "count": len(items), "items": items}


async def _search_classes(search_regex, current_user: Dict) -> Dict:
    role = current_user.get("role")
    user_id = current_user.get("user_id")
    conditions = [Or(Class.name.regex(search_regex), Class.description.regex(search_regex))]
    if role == "student":
        conditions.append(Class.student_ids.in_([user_id]))
    elif role == "instructor":
        conditions.append(Class.instructor_id == user_id)
    classes = await Class.find(And(*conditions)).to_list()
    items = []
    for class_obj in classes:
        instructor = await User.get(class_obj.instructor_id)
        items.append({
            "id": str(class_obj.id),
            "type": "class",
            "title": class_obj.name,
            "description": (class_obj.description or "")[:200],
            "relevance_score": calculate_relevance_score(search_regex.pattern, [class_obj.name, class_obj.description or ""]),
            "url": f"/classes/{class_obj.id}",
            "metadata": {
                "instructor_name": instructor.full_name if instructor else "Unknown",
                "student_count": len(class_obj.student_ids),
                "status": class_obj.status,
                "start_date": class_obj.start_date.isoformat() if class_obj.start_date else None,
            },
        })
    items.sort(key=lambda x: x["relevance_score"], reverse=True)
    return {"category": "classes", "count": len(items), "items": items}


async def _search_modules(search_regex, current_user: Dict) -> Dict:
    accessible_course_ids = await _get_accessible_course_ids(current_user)
    if not accessible_course_ids:
        return {"category": "modules", "count": 0, "items": []}
    modules = await Module.find(And(Module.course_id.in_(accessible_course_ids), Or(Module.title.regex(search_regex), Module.description.regex(search_regex)))).to_list()
    items = []
    for module in modules:
        course = await Course.get(module.course_id)
        items.append({
            "id": str(module.id),
            "type": "module",
            "title": module.title,
            "description": f"Trong khóa: {course.title if course else 'Unknown'} • {(module.description or '')[:150]}",
            "relevance_score": calculate_relevance_score(search_regex.pattern, [module.title, module.description or ""]),
            "url": f"/courses/{module.course_id}/modules/{module.id}",
            "metadata": {"course_id": str(module.course_id), "course_title": course.title if course else "Unknown", "order": module.order, "lesson_count": module.total_lessons},
        })
    items.sort(key=lambda x: x["relevance_score"], reverse=True)
    return {"category": "modules", "count": len(items), "items": items}


async def _search_lessons(search_regex, current_user: Dict) -> Dict:
    accessible_course_ids = await _get_accessible_course_ids(current_user)
    if not accessible_course_ids:
        return {"category": "lessons", "count": 0, "items": []}
    modules = await Module.find(Module.course_id.in_(accessible_course_ids)).to_list()
    module_map = {str(m.id): m for m in modules}
    if not module_map:
        return {"category": "lessons", "count": 0, "items": []}
    lessons = await Lesson.find(And(Lesson.module_id.in_(list(module_map.keys())), Or(Lesson.title.regex(search_regex), Lesson.content.regex(search_regex)))).to_list()
    items = []
    for lesson in lessons:
        module = module_map.get(lesson.module_id)
        course = await Course.get(module.course_id) if module else None
        items.append({
            "id": str(lesson.id),
            "type": "lesson",
            "title": lesson.title,
            "description": f"Trong: {course.title if course else 'Unknown'} -> {module.title if module else 'Unknown'}",
            "relevance_score": calculate_relevance_score(search_regex.pattern, [lesson.title, lesson.content or ""]),
            "url": f"/courses/{module.course_id if module else ''}/modules/{lesson.module_id}/lessons/{lesson.id}",
            "metadata": {
                "module_id": lesson.module_id,
                "module_title": module.title if module else "Unknown",
                "course_title": course.title if course else "Unknown",
                "lesson_type": lesson.content_type,
                "duration_minutes": lesson.duration_minutes,
            },
        })
    items.sort(key=lambda x: x["relevance_score"], reverse=True)
    return {"category": "lessons", "count": len(items), "items": items}


async def _get_accessible_course_ids(current_user: Dict) -> List[str]:
    role = current_user.get("role")
    user_id = current_user.get("user_id")
    if role == "admin":
        return [str(c.id) for c in await Course.find().to_list()]
    if role == "instructor":
        own = await Course.find(Course.instructor_id == user_id).to_list()
        published = await Course.find(Course.status == "published").to_list()
        return list({str(c.id) for c in [*own, *published]})
    if role == "student" and user_id:
        enrollments = await Enrollment.find(Enrollment.user_id == user_id).to_list()
        enrolled_ids = [e.course_id for e in enrollments]
        published = await Course.find(Course.status == "published").to_list()
        return list(set(enrolled_ids + [str(c.id) for c in published]))
    return [str(c.id) for c in await Course.find(Course.status == "published").to_list()]


async def _generate_suggestions(original_query: str, normalized_query: str) -> List[Dict]:
    suggestions: List[Dict] = []
    autocomplete_courses = await Course.find(Course.title.regex(re.compile(f"^{re.escape(normalized_query)}", re.IGNORECASE))).limit(5).to_list()
    for course in autocomplete_courses:
        suggestions.append({"query": course.title, "type": "autocomplete", "score": 90.0})
    return suggestions[:5]


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
    # No-op: history collection is not modeled yet.
    return None


async def get_search_history(user_id: str) -> Dict:
    user = await User.get(user_id)
    if not user:
        return {"user_id": user_id, "search_history": [], "popular_searches": []}
    popular_searches = [
        "Python programming",
        "Web development",
        "Data science",
        "Machine learning",
        "JavaScript basics",
    ]
    return {"user_id": user_id, "search_history": [], "popular_searches": popular_searches}


async def get_search_analytics() -> Dict:
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