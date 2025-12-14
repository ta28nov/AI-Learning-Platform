"""
Recommendation Service - Xử lý đề xuất khóa học
Sử dụng: Beanie ODM, Google Gemini (via ai_service)
Tuân thủ: CHUCNANG.md Section 2.2.4, 2.7.4
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict
from models.models import Recommendation, AssessmentSession, Enrollment, Course
from services.ai_service import generate_course_recommendations


# ============================================================================
# RECOMMENDATION CRUD
# ============================================================================

async def create_recommendation_from_assessment(
    user_id: str,
    assessment_session_id: str
) -> Recommendation:
    """
    Tạo đề xuất từ kết quả assessment
    
    Args:
        user_id: ID của user
        assessment_session_id: ID của assessment session
        
    Returns:
        Recommendation document đã tạo
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Creating recommendation from assessment - user: {user_id}, session: {assessment_session_id}")
    
    # Lấy assessment results
    assessment = await AssessmentSession.get(assessment_session_id)
    
    if not assessment:
        logger.error(f"Assessment session not found: {assessment_session_id}")
        raise ValueError("Assessment session không tồn tại")
    
    if assessment.status != "evaluated":
        logger.warning(f"Assessment not evaluated yet - session: {assessment_session_id}, status: {assessment.status}")
        raise ValueError("Assessment chưa được đánh giá")
    
    logger.info(f"Assessment found - category: {assessment.category}, level: {assessment.level}, score: {assessment.overall_score}")
    
    # Lấy lịch sử học tập
    enrollments = await Enrollment.find(
        Enrollment.user_id == user_id
    ).to_list()
    
    logger.info(f"Found {len(enrollments)} enrollments for user {user_id}")
    
    learning_history = [
        {
            "course_id": e.course_id,
            "progress_percent": e.progress_percent,
            "status": e.status
        }
        for e in enrollments
    ]
    
    # Lấy assessment results
    assessment_results = {
        "category": assessment.category,
        "subject": assessment.subject,
        "level": assessment.level,
        "overall_score": assessment.overall_score,
        "proficiency_level": assessment.proficiency_level,
        "knowledge_gaps": assessment.knowledge_gaps
    }
    
    # Lấy available courses từ database TRƯỚC KHI gọi AI
    try:
        logger.info(f"Fetching available courses - category: {assessment.category}")
        available_courses = await _get_available_courses(
            category=assessment.category,
            proficiency_level=assessment.proficiency_level,
            limit=15
        )
        logger.info(f"Found {len(available_courses)} available courses to send to AI")
    except Exception as e:
        logger.error(f"Failed to fetch available courses: {str(e)}", exc_info=True)
        available_courses = []
    
    # DATABASE-FIRST APPROACH: Filter enrolled courses first
    enrolled_course_ids = {e.course_id for e in enrollments}
    logger.info(f"User already enrolled in {len(enrolled_course_ids)} courses")
    
    # Filter out enrolled courses from available_courses
    unenrolled_courses = [
        course for course in available_courses 
        if str(course.id) not in enrolled_course_ids
    ]
    logger.info(f"Found {len(unenrolled_courses)} unenrolled courses to recommend")
    
    # Build recommended_courses directly from database with simple AI enhancement
    recommended_courses = []
    
    if unenrolled_courses:
        # Database-first: use actual courses, AI only for reasons
        try:
            logger.info("Getting AI reasons for selected courses...")
            ai_advice = await _get_ai_recommendation_reasons(
                assessment_results=assessment_results,
                selected_courses=unenrolled_courses[:5]  # Top 5 only
            )
            logger.info("AI reasons generated successfully")
        except Exception as e:
            logger.error(f"AI reason generation failed: {str(e)}")
            ai_advice = {"course_reasons": {}, "general_advice": "Hãy tiếp tục học tập để nâng cao kỹ năng"}
        
        # Build recommendations with guaranteed valid course_ids
        for idx, course in enumerate(unenrolled_courses[:5]):
            course_reason = ai_advice.get("course_reasons", {}).get(
                str(course.id), 
                f"Khóa học {course.title} phù hợp với kết quả đánh giá {assessment.category} {assessment.level}"
            )
            
            # Calculate relevance based on assessment gaps
            relevance_score = _calculate_course_relevance(
                course, assessment.knowledge_gaps, assessment.proficiency_level
            )
            
            recommended_courses.append({
                "course_id": course.id,
                "title": course.title,
                "category": course.category,
                "level": course.level,
                "reason": course_reason,
                "priority": idx + 1,
                "relevance_score": relevance_score,
                "addresses_gaps": _map_course_to_gaps(course, assessment.knowledge_gaps)
            })
        
        # Sort by relevance score
        recommended_courses.sort(key=lambda x: x["relevance_score"], reverse=True)
        general_ai_advice = ai_advice.get("general_advice", "")
    else:
        logger.warning("No unenrolled courses available for recommendation")
        general_ai_advice = "Bạn đã đăng ký hết các khóa học phù hợp. Hãy hoàn thành các khóa đã đăng ký hoặc thử học ở mức độ cao hơn."
    
    logger.info(f"Final recommended courses count: {len(recommended_courses)}")
    
    # Tạo recommendation với field names đúng theo model
    recommendation = Recommendation(
        user_id=user_id,
        source="assessment",
        assessment_session_id=assessment_session_id,
        user_proficiency_level=assessment.proficiency_level or "Beginner",
        recommended_courses=recommended_courses,
        suggested_learning_order=[],  # AI enhancement optional
        ai_personalized_advice=general_ai_advice,  # From database-first approach
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    
    await recommendation.insert()
    logger.info(f"Recommendation created successfully - id: {recommendation.id}")
    return recommendation


async def create_recommendation_from_history(user_id: str) -> Recommendation:
    """
    Tạo đề xuất dựa trên lịch sử học tập
    
    Args:
        user_id: ID của user
        
    Returns:
        Recommendation document đã tạo
    """
    # Lấy lịch sử học tập
    enrollments = await Enrollment.find(
        Enrollment.user_id == user_id
    ).to_list()
    
    learning_history = []
    for e in enrollments:
        course = await Course.get(e.course_id)
        if course:
            learning_history.append({
                "course_id": e.course_id,
                "course_title": course.title,
                "category": course.category,
                "level": course.level,
                "progress_percent": e.progress_percent,
                "status": e.status
            })
    
    # Lấy categories user đã học để fetch available courses
    categories = list(set(h["category"] for h in learning_history))
    primary_category = categories[0] if categories else "General"
    
    # Lấy available courses từ DB
    available_courses = await _get_available_courses(
        category=primary_category,
        proficiency_level="Intermediate",  # Default for history-based
        limit=15
    )
    
    # DATABASE-FIRST: Filter unrolled courses
    enrolled_course_ids = {h["course_id"] for h in learning_history}
    unenrolled_courses = [
        course for course in available_courses 
        if str(course.id) not in enrolled_course_ids
    ]
    
    # Build recommendations from database
    recommended_courses = []
    for idx, course in enumerate(unenrolled_courses[:10]):
        # Simple reason based on learning history patterns
        user_categories = list(set(h.get("category", "") for h in learning_history))
        if course.category in user_categories:
            reason = f"Dựa trên kinh nghiệm học {course.category}, bạn sẽ thích khóa học này"
        else:
            reason = f"Mở rộng kiến thức từ {course.category} - lĩnh vực mới thú vị"
        
        recommended_courses.append({
            "course_id": course.id,
            "title": course.title,
            "category": course.category,
            "level": course.level,
            "reason": reason,
            "priority": idx + 1,
            "relevance_score": 75.0 if course.category in user_categories else 65.0,
            "addresses_gaps": []
        })
    
    recommendation = Recommendation(
        user_id=user_id,
        source="learning_history",
        recommended_courses=recommended_courses[:10],
        suggested_learning_order=[],  # Simplified for now
        ai_personalized_advice="Dựa trên lịch sử học tập, đây là những khóa học phù hợp với bạn",
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    
    await recommendation.insert()
    return recommendation


async def get_recommendation_by_id(recommendation_id: str) -> Optional[Recommendation]:
    """
    Lấy recommendation theo ID
    
    Args:
        recommendation_id: ID của recommendation
        
    Returns:
        Recommendation document hoặc None
    """
    try:
        recommendation = await Recommendation.get(recommendation_id)
        return recommendation
    except Exception:
        return None


async def get_user_recommendations(
    user_id: str,
    skip: int = 0,
    limit: int = 50
) -> List[Recommendation]:
    """
    Lấy danh sách recommendations của user
    
    Args:
        user_id: ID của user
        skip: Pagination skip
        limit: Pagination limit
        
    Returns:
        List Recommendation documents
    """
    recommendations = await Recommendation.find(
        Recommendation.user_id == user_id
    ).skip(skip).limit(limit).to_list()
    
    return recommendations


async def get_recommendation_by_assessment(
    user_id: str,
    assessment_session_id: str
) -> Optional[Recommendation]:
    """
    Lấy recommendation theo assessment session ID
    
    Args:
        user_id: ID của user
        assessment_session_id: ID của assessment session
        
    Returns:
        Recommendation document hoặc None
    """
    recommendation = await Recommendation.find_one(
        Recommendation.user_id == user_id,
        Recommendation.assessment_session_id == assessment_session_id
    )
    
    return recommendation


async def get_latest_recommendation(user_id: str) -> Optional[Recommendation]:
    """
    Lấy recommendation mới nhất chưa expired (alias cho get_active_recommendation)
    
    Args:
        user_id: ID của user
        
    Returns:
        Recommendation document hoặc None
    """
    return await get_active_recommendation(user_id)


async def get_active_recommendation(user_id: str) -> Optional[Recommendation]:
    """
    Lấy recommendation active gần nhất (chưa expired)
    
    Args:
        user_id: ID của user
        
    Returns:
        Recommendation document hoặc None
    """
    now = datetime.utcnow()
    
    recommendation = await Recommendation.find_one(
        Recommendation.user_id == user_id,
        Recommendation.expires_at > now
    )
    
    return recommendation


async def delete_recommendation(recommendation_id: str) -> bool:
    """
    Xóa recommendation
    
    Args:
        recommendation_id: ID của recommendation
        
    Returns:
        True nếu xóa thành công, False nếu không tìm thấy
    """
    recommendation = await get_recommendation_by_id(recommendation_id)
    
    if not recommendation:
        return False
    
    await recommendation.delete()
    return True


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def _get_available_courses(
    category: str,
    proficiency_level: str,
    limit: int = 15
) -> List[Course]:
    """
    Lấy danh sách courses có sẵn để gửi cho AI
    
    Args:
        category: Danh mục
        proficiency_level: Mức độ năng lực hiện tại
        limit: Số lượng courses tối đa
        
    Returns:
        List Course documents
    """
    # Map proficiency level sang course level
    level_map = {
        "Beginner": ["Beginner", "Intermediate"],
        "Intermediate": ["Intermediate", "Advanced"],
        "Advanced": ["Advanced"]
    }
    
    target_levels = level_map.get(proficiency_level, ["Beginner"])
    
    # Tìm courses published trong category và level phù hợp
    courses = await Course.find(
        Course.category == category,
        Course.status == "published"
    ).to_list()
    
    # Filter theo level và limit
    filtered = [c for c in courses if c.level in target_levels][:limit]
    
    return filtered


async def _get_ai_recommendation_reasons(
    assessment_results: Dict,
    selected_courses: List[Course]
) -> Dict:
    """
    Lấy AI reasons cho courses đã được select từ database
    
    Args:
        assessment_results: Kết quả đánh giá 
        selected_courses: List courses đã được filter từ database
        
    Returns:
        Dict chứa reasons cho từng course và general advice
    """
    try:
        # Import here to avoid circular import
        from services.ai_service import model
        import json
        
        # Create simple context
        gaps_summary = []
        if assessment_results.get("knowledge_gaps"):
            gaps_summary = [
                gap.get("gap_area", "Unknown") 
                for gap in assessment_results["knowledge_gaps"][:3]
            ]
        
        courses_context = []
        for course in selected_courses:
            courses_context.append({
                "id": str(course.id),
                "title": course.title,
                "level": course.level,
                "description": course.description[:100] + "..."
            })
        
        prompt = f"""
Dựa trên kết quả đánh giá năng lực:
- Điểm số: {assessment_results.get('overall_score', 0)}/100
- Trình độ: {assessment_results.get('proficiency_level', 'Beginner')}
- Lỗ hổng kiến thức: {', '.join(gaps_summary)}

Hãy đưa ra lý do ngắn gọn (1-2 câu) tại sao nên học từng khóa học sau:
{json.dumps(courses_context, ensure_ascii=False, indent=2)}

Trả về JSON format:
{{
    "course_reasons": {{
        "course_id_1": "Lý do ngắn gọn...",
        "course_id_2": "Lý do ngắn gọn..."
    }},
    "general_advice": "Lời khuyên chung cho học viên dựa trên kết quả đánh giá"
}}
"""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean JSON response
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        return json.loads(response_text.strip())
        
    except Exception as e:
        # Fallback to simple reasons
        course_reasons = {}
        for course in selected_courses:
            course_reasons[str(course.id)] = f"Khóa học {course.title} phù hợp với trình độ {assessment_results.get('proficiency_level', 'Beginner')}"
        
        return {
            "course_reasons": course_reasons,
            "general_advice": f"Dựa trên kết quả đánh giá, bạn nên tập trung học các khóa học {assessment_results.get('category', 'cơ bản')} để nâng cao kỹ năng."
        }


def _calculate_course_relevance(
    course: Course,
    knowledge_gaps: List[Dict],
    proficiency_level: str
) -> float:
    """
    Tính độ phù hợp của course dựa trên knowledge gaps
    
    Returns:
        Float score từ 60-95
    """
    base_score = 70.0
    
    # Bonus for matching level
    if course.level == proficiency_level:
        base_score += 10.0
    elif course.level == "Beginner" and proficiency_level in ["Intermediate", "Advanced"]:
        base_score += 5.0  # Good for refreshing basics
    
    # Bonus for addressing knowledge gaps
    if knowledge_gaps:
        gap_keywords = []
        for gap in knowledge_gaps:
            gap_area = gap.get("gap_area", "").lower()
            gap_keywords.extend(gap_area.split())
        
        # Check if course title/description contains gap keywords  
        course_content = f"{course.title} {course.description}".lower()
        matching_keywords = sum(1 for keyword in gap_keywords if keyword in course_content)
        
        if matching_keywords > 0:
            base_score += min(15.0, matching_keywords * 3.0)  # Max 15 bonus points
    
    return min(95.0, base_score)  # Cap at 95


def _map_course_to_gaps(course: Course, knowledge_gaps: List[Dict]) -> List[str]:
    """
    Map course content to knowledge gaps it addresses
    
    Returns:
        List of gap areas this course can help with
    """
    if not knowledge_gaps:
        return []
    
    addresses_gaps = []
    course_content = f"{course.title} {course.description}".lower()
    
    for gap in knowledge_gaps:
        gap_area = gap.get("gap_area", "").lower()
        
        # Simple keyword matching
        gap_words = gap_area.split()
        if any(word in course_content for word in gap_words):
            addresses_gaps.append(gap.get("gap_area", ""))
    
    return addresses_gaps[:3]  # Limit to 3 gaps max


async def _match_courses_to_recommendations(
    category: str,
    proficiency_level: str,
    knowledge_gaps: List[Dict],
    available_courses: List[Course] = None
) -> List[Dict]:
    """
    Tìm courses phù hợp với knowledge gaps (IMPROVED matching logic)
    
    Args:
        category: Danh mục
        proficiency_level: Mức độ năng lực hiện tại
        knowledge_gaps: Các khoảng trống kiến thức
        available_courses: Courses đã fetch (optional)
        
    Returns:
        List dict chứa course recommendations
    """
    # Nếu chưa có courses, fetch lại
    if not available_courses:
        available_courses = await _get_available_courses(category, proficiency_level, 10)
    
    # IMPROVED: Match courses với knowledge gaps bằng multiple fields
    recommendations = []
    for i, course in enumerate(available_courses):
        score = 0
        matched_gaps = []
        reason_parts = []
        
        # Match với knowledge gaps
        for gap in knowledge_gaps:
            gap_area = gap.get("gap_area", gap.get("topic", "")).lower()
            gap_desc = gap.get("description", "").lower()
            
            # Check title
            if gap_area in course.title.lower():
                score += 30
                matched_gaps.append(gap_area)
            
            # Check description
            if gap_area in course.description.lower() or gap_desc in course.description.lower():
                score += 20
                if gap_area not in matched_gaps:
                    matched_gaps.append(gap_area)
            
            # Check learning outcomes
            for outcome in course.learning_outcomes:
                outcome_text = outcome.get('description', '').lower()
                if gap_area in outcome_text or gap_desc in outcome_text:
                    score += 15
                    if gap_area not in matched_gaps:
                        matched_gaps.append(gap_area)
                    break
        
        # Build reason
        if matched_gaps:
            reason_parts.append(f"Giúp khắc phục lỗ hổng: {', '.join(matched_gaps[:2])}")
        else:
            reason_parts.append("Phù hợp với trình độ hiện tại")
        
        # Bonus score for exact level match
        if course.level == proficiency_level:
            score += 10
        
        recommendations.append({
            "course_id": course.id,
            "title": course.title,
            "category": course.category,
            "level": course.level,
            "reason": ". ".join(reason_parts),
            "priority": i + 1,
            "relevance_score": min(score, 100),
            "addresses_gaps": matched_gaps[:3]
        })
    
    # Sort by relevance score
    recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    # Re-assign priority after sorting
    for i, rec in enumerate(recommendations):
        rec["priority"] = i + 1
    
    return recommendations[:10]
