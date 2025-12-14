"""
AI Service - Tích hợp Google Gemini API
Sử dụng: google-generativeai library
Tuân thủ: CHUCNANG.md Section 2.2 (Assessment), 2.6 (Chatbot)
"""

import json
from typing import List, Dict, Optional
import google.generativeai as genai
from config.config import get_settings
from models.models import Course, Lesson


# ============================================================================
# GEMINI API CONFIGURATION
# ============================================================================

settings = get_settings()
genai.configure(api_key=settings.google_api_key)
model = genai.GenerativeModel(settings.gemini_model)


# ============================================================================
# ASSESSMENT QUESTION GENERATION (Section 2.2.1-2.2.2)
# ============================================================================

async def generate_assessment_questions(
    category: str,
    subject: str,
    level: str,
    count: int = 10,
    focus_areas: Optional[List[str]] = None
) -> List[Dict]:
    """
    Tạo câu hỏi đánh giá năng lực sử dụng Google Gemini
    Tuân thủ CHUCNANG.md Section 2.2.1-2.2.2
    
    Phân bổ độ khó theo mức độ:
    - Beginner (15 câu): 3 Easy (20%) + 8 Medium (53%) + 4 Hard (27%)
    - Intermediate (25 câu): 5 Easy (20%) + 13 Medium (52%) + 7 Hard (28%)
    - Advanced (35 câu): 7 Easy (20%) + 18 Medium (51%) + 10 Hard (29%)
    
    Args:
        category: Danh mục (Programming, Math, Business, Languages)
        subject: Chủ đề cụ thể (Python, Calculus, Marketing, etc.)
        level: Mức độ (Beginner, Intermediate, Advanced)
        count: Số lượng câu hỏi (mặc định 10, thực tế theo level)
        focus_areas: Các chủ đề con cần tập trung (optional)
        
    Returns:
        List các câu hỏi với cấu trúc đầy đủ theo CHUCNANG.md
    """
    # Xác định số câu và phân bổ độ khó theo mức độ
    if level == "Beginner":
        total_questions = 15
        easy_count = 3
        medium_count = 8
        hard_count = 4
    elif level == "Intermediate":
        total_questions = 25
        easy_count = 5
        medium_count = 13
        hard_count = 7
    elif level == "Advanced":
        total_questions = 35
        easy_count = 7
        medium_count = 18
        hard_count = 10
    else:
        total_questions = count
        easy_count = int(count * 0.2)
        medium_count = int(count * 0.5)
        hard_count = count - easy_count - medium_count
    
    focus_areas_str = f"\n- Tập trung vào: {', '.join(focus_areas)}" if focus_areas else ""
    
    prompt = f"""
Tạo {total_questions} câu hỏi đánh giá năng lực cho:
- Danh mục: {category}
- Chủ đề: {subject}
- Mức độ: {level}{focus_areas_str}

Phân bổ độ khó CHÍNH XÁC:
- {easy_count} câu EASY (20%): Kiến thức nền tảng cơ bản
- {medium_count} câu MEDIUM (50-53%): Áp dụng kiến thức thực tế
- {hard_count} câu HARD (27-30%): Tư duy phản biện và giải quyết vấn đề phức tạp

Yêu cầu format JSON chính xác (sắp xếp từ dễ đến khó):
[
    {{
        "question_id": "q1",
        "question_text": "Câu hỏi rõ ràng, súc tích với ngữ cảnh thực tế...",
        "question_type": "multiple_choice",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct_answer_hint": "Gợi ý ngắn về đáp án đúng (không nói trực tiếp)",
        "difficulty": "easy",
        "skill_tag": "python-syntax",
        "points": 1
    }},
    {{
        "question_id": "q2",
        "question_text": "Câu hỏi...",
        "question_type": "fill_in_blank",
        "options": null,
        "correct_answer_hint": "Gợi ý ngắn...",
        "difficulty": "medium",
        "skill_tag": "algorithm-basics",
        "points": 2
    }}
]

Lưu ý:
- Sắp xếp câu hỏi từ DỄ → KHÓ
- question_type: multiple_choice, fill_in_blank, drag_and_drop
- difficulty: easy, medium, hard
- points: easy=1, medium=2, hard=3
- skill_tag: Gắn nhãn kỹ năng cụ thể (ví dụ: python-syntax, data-structures-array)
- options: null nếu không phải multiple_choice
- PHẢI trả về JSON array hợp lệ, không thêm text khác
"""
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Loại bỏ markdown code blocks nếu có
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Parse JSON
        questions = json.loads(response_text)
        
        return questions
    
    except json.JSONDecodeError as e:
        # Fallback: tạo câu hỏi mẫu nếu parse JSON thất bại
        print(f"JSON parse error: {str(e)}")
        if level == "Beginner":
            return _generate_fallback_questions(category, subject, level, 15)
        elif level == "Intermediate":
            return _generate_fallback_questions(category, subject, level, 25)
        elif level == "Advanced":
            return _generate_fallback_questions(category, subject, level, 35)
        return _generate_fallback_questions(category, subject, level, count)
    
    except Exception as e:
        # Log error và trả về fallback
        print(f"Error generating questions: {str(e)}")
        if level == "Beginner":
            return _generate_fallback_questions(category, subject, level, 15)
        elif level == "Intermediate":
            return _generate_fallback_questions(category, subject, level, 25)
        elif level == "Advanced":
            return _generate_fallback_questions(category, subject, level, 35)
        return _generate_fallback_questions(category, subject, level, count)


def _generate_fallback_questions(
    category: str,
    subject: str,
    level: str,
    count: int
) -> List[Dict]:
    """
    Tạo câu hỏi fallback khi Gemini API thất bại
    Tuân thủ phân bổ độ khó theo CHUCNANG.md
    
    Returns:
        List câu hỏi mẫu với phân bổ đúng easy/medium/hard
    """
    # Phân bổ độ khó
    if count == 15:  # Beginner
        easy_count, medium_count, hard_count = 3, 8, 4
    elif count == 25:  # Intermediate
        easy_count, medium_count, hard_count = 5, 13, 7
    elif count == 35:  # Advanced
        easy_count, medium_count, hard_count = 7, 18, 10
    else:
        easy_count = int(count * 0.2)
        medium_count = int(count * 0.5)
        hard_count = count - easy_count - medium_count
    
    questions = []
    question_num = 1
    
    # Tạo câu dễ
    for i in range(easy_count):
        questions.append({
            "question_id": f"q{question_num}",
            "question_text": f"[Fallback] Câu hỏi cơ bản về {subject} - câu {question_num}",
            "question_type": "multiple_choice",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer_hint": f"Gợi ý: Xem xét kiến thức cơ bản về {subject}",
            "difficulty": "easy",
            "skill_tag": f"{subject.lower()}-basics",
            "points": 1
        })
        question_num += 1
    
    # Tạo câu trung bình
    for i in range(medium_count):
        questions.append({
            "question_id": f"q{question_num}",
            "question_text": f"[Fallback] Câu hỏi áp dụng về {subject} - câu {question_num}",
            "question_type": "multiple_choice",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer_hint": f"Gợi ý: Áp dụng kiến thức {subject} vào thực tế",
            "difficulty": "medium",
            "skill_tag": f"{subject.lower()}-application",
            "points": 2
        })
        question_num += 1
    
    # Tạo câu khó
    for i in range(hard_count):
        questions.append({
            "question_id": f"q{question_num}",
            "question_text": f"[Fallback] Câu hỏi phức tạp về {subject} - câu {question_num}",
            "question_type": "multiple_choice",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer_hint": f"Gợi ý: Cần tư duy phản biện về {subject}",
            "difficulty": "hard",
            "skill_tag": f"{subject.lower()}-advanced",
            "points": 3
        })
        question_num += 1
    
    return questions


# ============================================================================
# ASSESSMENT EVALUATION (Section 2.2.3)
# ============================================================================

async def evaluate_assessment_answers(
    questions: List[Dict],
    answers: List[Dict],
    category: str,
    subject: str
) -> Dict:
    """
    Đánh giá kết quả assessment và phân tích năng lực
    Tuân thủ CHUCNANG.md Section 2.2.3
    
    Tính điểm có trọng số: easy=1, medium=2, hard=3
    Phân tích theo 4 khía cạnh:
    1. Điểm tổng thể (0-100)
    2. Phân loại trình độ (Beginner < 60, Intermediate 60-80, Advanced > 80)
    3. Điểm mạnh/yếu theo skill tag
    4. Lỗ hổng kiến thức cần khắc phục
    
    Args:
        questions: List câu hỏi
        answers: List câu trả lời của user
        category: Danh mục
        subject: Chủ đề
        
    Returns:
        Dict chứa kết quả phân tích đầy đủ
    """
    # Tính điểm có trọng số
    total_weighted_score = 0
    max_weighted_score = 0
    correct_count = 0
    total_count = len(questions)
    
    # Phân tích theo độ khó
    easy_correct = easy_total = 0
    medium_correct = medium_total = 0
    hard_correct = hard_total = 0
    
    # Phân tích theo skill tag
    skill_stats = {}
    
    answer_map = {ans.get("question_id"): ans.get("answer_content", ans.get("answer", "")) for ans in answers}
    
    # Sử dụng AI để đánh giá từng câu (vì chỉ có correct_answer_hint, không có đáp án thực)
    evaluation_pairs = []
    for question in questions:
        q_id = question["question_id"]
        user_answer = answer_map.get(q_id, "")
        evaluation_pairs.append({
            "question_id": q_id,
            "question_text": question.get("question_text", ""),
            "question_type": question.get("question_type", ""),
            "options": question.get("options"),
            "correct_answer_hint": question.get("correct_answer_hint", ""),
            "user_answer": user_answer,
            "difficulty": question.get("difficulty", "medium"),
            "skill_tag": question.get("skill_tag", "general"),
            "points": question.get("points", 2)
        })
    
    # IMPORTANT FIX: Batch evaluation để tránh timeout với nhiều câu hỏi
    grading_map = {}
    batch_size = 10  # Evaluate 10 questions at a time
    
    for batch_start in range(0, len(evaluation_pairs), batch_size):
        batch_end = min(batch_start + batch_size, len(evaluation_pairs))
        batch_pairs = evaluation_pairs[batch_start:batch_end]
        
        grading_prompt = f"""
Chấm điểm các câu trả lời sau (trả về JSON array):

{json.dumps(batch_pairs, ensure_ascii=False, indent=2)}

Hãy trả về JSON array với format:
[
    {{
        "question_id": "q1",
        "is_correct": true,
        "explanation": "Đáp án đúng vì..."
    }},
    ...
]

Lưu ý:
- is_correct: true/false dựa trên so sánh user_answer với correct_answer_hint
- Với multiple_choice: kiểm tra user_answer có khớp với đáp án gợi ý
- PHẢI trả về JSON array hợp lệ
"""
        
        try:
            grading_response = model.generate_content(grading_prompt)
            grading_text = grading_response.text.strip()
            
            # Clean markdown
            if grading_text.startswith("```json"):
                grading_text = grading_text[7:]
            if grading_text.startswith("```"):
                grading_text = grading_text[3:]
            if grading_text.endswith("```"):
                grading_text = grading_text[:-3]
            grading_text = grading_text.strip()
            
            batch_results = json.loads(grading_text)
            for r in batch_results:
                grading_map[r["question_id"]] = r["is_correct"]
        
        except Exception as e:
            print(f"AI grading error for batch {batch_start}-{batch_end}: {e}. Using fallback.")
            # Fallback: chấm đơn giản bằng keyword matching với hint
            for pair in batch_pairs:
                hint = pair["correct_answer_hint"].lower()
                answer = pair["user_answer"].lower()
                # Simple heuristic: nếu answer chứa từ khóa trong hint
                grading_map[pair["question_id"]] = (hint in answer or answer in hint)
    
    # Tính điểm dựa trên kết quả AI grading
    for question in questions:
        q_id = question["question_id"]
        difficulty = question.get("difficulty", "medium").lower()
        skill_tag = question.get("skill_tag", "general")
        points = question.get("points", 2)
        
        # Cập nhật max score
        max_weighted_score += points
        
        # Kiểm tra đáp án từ AI
        is_correct = grading_map.get(q_id, False)
        if is_correct:
            correct_count += 1
            total_weighted_score += points
        
        # Thống kê theo độ khó
        if difficulty == "easy":
            easy_total += 1
            if is_correct:
                easy_correct += 1
        elif difficulty == "hard":
            hard_total += 1
            if is_correct:
                hard_correct += 1
        else:  # medium
            medium_total += 1
            if is_correct:
                medium_correct += 1
        
        # Thống kê theo skill tag
        if skill_tag not in skill_stats:
            skill_stats[skill_tag] = {"total": 0, "correct": 0}
        skill_stats[skill_tag]["total"] += 1
        if is_correct:
            skill_stats[skill_tag]["correct"] += 1
    
    # Tính điểm tổng thể (0-100)
    overall_score = (total_weighted_score / max_weighted_score * 100) if max_weighted_score > 0 else 0
    
    # Xác định proficiency level theo ngưỡng
    if overall_score >= 80:
        proficiency_level = "Advanced"
    elif overall_score >= 60:
        proficiency_level = "Intermediate"
    else:
        proficiency_level = "Beginner"
    
    # Chuẩn bị dữ liệu cho Gemini phân tích
    skill_summary = []
    for skill, stats in skill_stats.items():
        percentage = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
        skill_summary.append({
            "skill": skill,
            "correct": stats["correct"],
            "total": stats["total"],
            "percentage": percentage
        })
    
    # Sử dụng Gemini để phân tích chi tiết
    analysis_prompt = f"""
Phân tích kết quả assessment chi tiết:
- Danh mục: {category}
- Chủ đề: {subject}
- Điểm số: {overall_score:.1f}/100 (có trọng số)
- Số câu đúng: {correct_count}/{total_count}
- Phân loại: {proficiency_level}

Phân tích theo độ khó:
- Easy: {easy_correct}/{easy_total} đúng ({easy_correct/easy_total*100 if easy_total > 0 else 0:.1f}%)
- Medium: {medium_correct}/{medium_total} đúng ({medium_correct/medium_total*100 if medium_total > 0 else 0:.1f}%)
- Hard: {hard_correct}/{hard_total} đúng ({hard_correct/hard_total*100 if hard_total > 0 else 0:.1f}%)

Phân tích theo skill tag:
{json.dumps(skill_summary, indent=2, ensure_ascii=False)}

Hãy trả về JSON với format (theo CHUCNANG.md Section 2.2.3):
{{
    "skill_analysis": [
        {{
            "skill_tag": "python-syntax",
            "questions_count": 5,
            "correct_count": 4,
            "proficiency_percentage": 80.0,
            "strength_level": "Strong",
            "detailed_feedback": "Bạn nắm vững cú pháp Python cơ bản..."
        }}
    ],
    "knowledge_gaps": [
        {{
            "gap_area": "Algorithm Complexity",
            "description": "Chưa hiểu rõ về độ phức tạp thuật toán O(n), O(log n)",
            "importance": "High",
            "suggested_action": "Học lại Big O notation và phân tích thuật toán"
        }}
    ],
    "overall_feedback": "Nhận xét tổng quan chi tiết về năng lực..."
}}

Lưu ý:
- strength_level: Strong (>80%), Average (60-80%), Weak (<60%)
- importance: High, Medium, Low
- PHẢI trả về JSON hợp lệ, không thêm text khác
"""
    
    try:
        response = model.generate_content(analysis_prompt)
        response_text = response.text.strip()
        
        # Loại bỏ markdown
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        analysis = json.loads(response_text)
        
        # Return structure matching what assessment_service expects
        return {
            "overall_score": round(overall_score, 1),
            "proficiency_level": proficiency_level,
            "skill_analysis": analysis.get("skill_analysis", []),  # List[SkillAnalysis]
            "knowledge_gaps": analysis.get("knowledge_gaps", []),   # List[KnowledgeGap]
            "overall_feedback": analysis.get("overall_feedback", ""),  # String
            "score_breakdown": {
                "easy": {"correct": easy_correct, "total": easy_total},
                "medium": {"correct": medium_correct, "total": medium_total},
                "hard": {"correct": hard_correct, "total": hard_total}
            }
        }
    
    except Exception as e:
        print(f"Error in AI analysis: {str(e)}")
        # Fallback analysis với logic đơn giản
        skill_analysis_list = []
        knowledge_gaps_list = []
        
        for skill, stats in skill_stats.items():
            percentage = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
            
            if percentage >= 80:
                strength_level = "Strong"
            elif percentage >= 60:
                strength_level = "Average"
            else:
                strength_level = "Weak"
                # Nếu yếu, thêm vào knowledge gaps
                knowledge_gaps_list.append({
                    "gap_area": skill,
                    "description": f"Chỉ đạt {percentage:.1f}% ở kỹ năng {skill}",
                    "importance": "High" if percentage < 40 else "Medium",
                    "suggested_action": f"Cần ôn luyện thêm về {skill}"
                })
            
            skill_analysis_list.append({
                "skill_tag": skill,
                "questions_count": stats["total"],
                "correct_count": stats["correct"],
                "proficiency_percentage": round(percentage, 1),
                "strength_level": strength_level,
                "detailed_feedback": f"Bạn đạt {percentage:.1f}% ở kỹ năng {skill}"
            })
        
        # Fallback return structure (same format as AI analysis)
        return {
            "overall_score": round(overall_score, 1),
            "proficiency_level": proficiency_level,
            "skill_analysis": skill_analysis_list,
            "knowledge_gaps": knowledge_gaps_list,
            "overall_feedback": f"Bạn đạt {overall_score:.1f}% - mức {proficiency_level}. Tổng {correct_count}/{total_count} câu đúng.",
            "score_breakdown": {
                "easy": {"correct": easy_correct, "total": easy_total},
                "medium": {"correct": medium_correct, "total": medium_total},
                "hard": {"correct": hard_correct, "total": hard_total}
            }
        }


# ============================================================================
# CHATBOT với Course Context (Section 2.6)
# ============================================================================

async def chat_with_course_context(
    course_id: str,
    question: str,
    conversation_history: Optional[List[Dict]] = None
) -> str:
    """
    Chatbot trả lời câu hỏi dựa trên context của khóa học
    
    Args:
        course_id: ID của khóa học
        question: Câu hỏi từ user
        conversation_history: Lịch sử chat trước đó (optional)
        
    Returns:
        Câu trả lời từ AI
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Lấy thông tin khóa học từ database
        course = await Course.get(course_id)
        
        if not course:
            logger.warning(f"Course not found: {course_id}")
            return "Không tìm thấy thông tin khóa học."
        
        # Tạo context từ khóa học (tóm gọn)
        course_context = _build_course_context(course)
        
        # Tạo conversation context (5 messages gần nhất - đủ cho AI free)
        history_text = ""
        if conversation_history and len(conversation_history) > 0:
            for msg in conversation_history[-5:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                history_text += f"{role}: {content}\n"
        
        # Tạo prompt
        prompt = f"""
Bạn là trợ lý AI hỗ trợ học tập cho khóa học sau:

THÔNG TIN KHÓA HỌC:
{course_context}

LỊCH SỬ HỘI THOẠI:
{history_text}

CÂU HỎI MỚI TỪ HỌC VIÊN:
{question}

Hãy trả lời câu hỏi dựa trên thông tin khóa học. Trả lời bằng tiếng Việt, ngắn gọn và dễ hiểu.
Nếu câu hỏi không liên quan đến khóa học, hãy lịch sự nhắc nhở học viên tập trung vào nội dung khóa học.
"""
        
        response = model.generate_content(prompt)
        return response.text.strip()
    
    except Exception as e:
        logger.error(f"Error in chat_with_course_context: {str(e)}", exc_info=True)
        return "Xin lỗi, tôi không thể trả lời câu hỏi này lúc này. Vui lòng thử lại sau."


def _build_course_context(course: Course) -> str:
    """
    Tạo text context từ Course document (tóm gọn cho AI free)
    Chỉ lấy thông tin cơ bản: title, description, modules/lessons structure
    
    Args:
        course: Course document
        
    Returns:
        String chứa thông tin khóa học (tối ưu cho token limit)
    """
    context = f"""
Tên khóa học: {course.title}
Mô tả: {course.description}
Danh mục: {course.category}
Mức độ: {course.level}

Kết quả học tập:
"""
    
    # Chỉ lấy tối đa 5 learning outcomes đầu tiên
    for i, outcome in enumerate(course.learning_outcomes[:5]):
        context += f"- {outcome.get('description', '')}\n"
        if i >= 4:  # Giới hạn 5 outcomes
            break
    
    context += "\nNội dung khóa học:\n"
    
    # Chỉ liệt kê cấu trúc modules và lessons (không thêm description chi tiết)
    for idx, module in enumerate(course.modules[:10]):  # Giới hạn 10 modules
        context += f"\n## Module {idx + 1}: {module.title}\n"
        
        # Chỉ list tên lessons, không thêm description
        for lesson in module.lessons[:8]:  # Giới hạn 8 lessons/module
            context += f"  - Bài {lesson.order}: {lesson.title}\n"
    
    return context


# ============================================================================
# COURSE RECOMMENDATION (Section 2.7.4)
# ============================================================================

async def generate_course_recommendations(
    user_learning_history: List[Dict],
    assessment_results: Optional[Dict] = None,
    available_courses: Optional[List[Course]] = None
) -> Dict:
    """
    Tạo đề xuất khóa học dựa trên lịch sử học tập và kết quả assessment
    
    Args:
        user_learning_history: Lịch sử học tập của user
        assessment_results: Kết quả assessment (optional)
        available_courses: Danh sách khóa học có sẵn (optional)
        
    Returns:
        Dict chứa:
        {
            "recommended_courses": [
                {
                    "course_id": "...",
                    "title": "...",
                    "reason": "...",
                    "priority": 1
                }
            ],
            "learning_path": [...],
            "ai_advice": "..."
        }
    """
    # Build available courses context
    courses_context = "Không có thông tin khóa học"
    if available_courses:
        courses_list = []
        for idx, course in enumerate(available_courses[:15], 1):  # Limit to 15 courses to avoid token overflow
            outcomes = ", ".join([o.get('description', '')[:50] for o in course.learning_outcomes[:3]])
            courses_list.append(
                f"{idx}. [{course.id}] {course.title}\n"
                f"   - Level: {course.level} | Category: {course.category}\n"
                f"   - Mô tả: {course.description[:150]}...\n"
                f"   - Học được: {outcomes}"
            )
        courses_context = "\n\n".join(courses_list)
    
    # Extract knowledge gaps for better context
    knowledge_gaps_str = ""
    if assessment_results and assessment_results.get("knowledge_gaps"):
        gaps = [f"- {gap.get('gap_area', gap.get('topic', 'Unknown'))}: {gap.get('description', '')}" 
                for gap in assessment_results["knowledge_gaps"][:5]]
        knowledge_gaps_str = "\n".join(gaps)
    
    # Tạo prompt cho Gemini với available courses
    prompt = f"""
Dựa trên thông tin học viên:

LỊCH SỬ HỌC TẬP:
{json.dumps(user_learning_history, indent=2, ensure_ascii=False)}

KẾT QUẢ ASSESSMENT:
{json.dumps(assessment_results, indent=2, ensure_ascii=False) if assessment_results else "Chưa có"}

LỖ HỔNG KIẾN THỨC CẦN KHẮC PHỤC:
{knowledge_gaps_str if knowledge_gaps_str else "Chưa xác định"}

CÁC KHÓA HỌC CÓ SẴN TRONG HỆ THỐNG:
{courses_context}

Nhiệm vụ: Dựa trên lỗ hổng kiến thức và khóa học có sẵn, hãy đề xuất:
1. Các course_id CỤ THỂ từ danh sách trên (chọn 3-5 khóa phù hợp nhất)
2. Lộ trình học (thứ tự nên học các khóa)
3. Lời khuyên cá nhân hóa

Trả về JSON format (QUAN TRỌNG - chỉ dùng course_id từ danh sách trên):
{{
    "recommended_course_ids": [
        {{
            "course_id": "abc-123-xyz",
            "reason": "Khóa này giúp khắc phục lỗ hổng về...",
            "priority": 1
        }}
    ],
    "learning_sequence": [
        {{
            "course_id": "abc-123-xyz",
            "focus_modules": ["Module về X", "Module về Y"],
            "why_this_order": "Học trước vì là nền tảng"
        }}
    ],
    "ai_advice": "Lời khuyên chi tiết cho học viên..."
}}

Lưu ý: course_id PHẢI lấy từ danh sách [id] ở trên, KHÔNG tự nghĩ ra.
PHẢI trả về JSON hợp lệ.
"""
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Loại bỏ markdown
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        recommendations = json.loads(response_text)
        
        # Validate and extract recommended courses
        recommended_course_ids = recommendations.get("recommended_course_ids", [])
        
        return {
            "recommended_courses": recommended_course_ids,  # Now contains course_id + reason
            "learning_path": recommendations.get("learning_sequence", []),
            "ai_advice": recommendations.get("ai_advice", "")
        }
    
    except Exception as e:
        print(f"Error in generate_course_recommendations: {str(e)}")
        return {
            "recommended_courses": [],
            "learning_path": [],
            "ai_advice": "Hãy tiếp tục học tập và hoàn thành các khóa học hiện tại."
        }


# ============================================================================
# PERSONAL COURSE GENERATION
# ============================================================================

async def generate_course_from_prompt(
    prompt: str,
    user_preferences: Optional[List[str]] = None,
    difficulty: str = "Beginner"
) -> Dict[str, any]:
    """
    Generate a complete course structure from a text prompt using AI.
    
    Args:
        prompt: User's description of desired course
        user_preferences: User's learning preferences
        difficulty: Course difficulty level
        
    Returns:
        Dict containing course structure (title, description, modules, lessons)
    """
    try:
        # Build prompt for AI
        system_prompt = f"""Bạn là một chuyên gia thiết kế khóa học. 
Nhiệm vụ: Tạo cấu trúc khóa học hoàn chỉnh dựa trên yêu cầu của người dùng.
Cấp độ: {difficulty}
Sở thích người dùng: {', '.join(user_preferences) if user_preferences else 'Không có'}

Trả về JSON với cấu trúc (CHỈ JSON THUẦN TÚY, KHÔNG CÓ TEXT KHÁC):
{{
    "title": "Tên khóa học ngắn gọn",
    "description": "Mô tả ngắn (max 200 chars)",
    "category": "Programming|Data Science|Business",
    "level": "{difficulty}",
    "estimated_duration": 30,
    "modules": [
        {{
            "title": "Tên module",
            "description": "Mô tả ngắn",
            "order": 1,
            "difficulty": "Basic|Intermediate|Advanced",
            "estimated_hours": 2,
            "learning_outcomes": [
                {{
                    "description": "Mục tiêu ngắn gọn",
                    "skill_tag": "tag-kỹ-năng"
                }}
            ],
            "lessons": [
                {{
                    "title": "Tên bài",
                    "description": "Mô tả ngắn",
                    "content": "Nội dung ngắn gọn",
                    "duration_minutes": 15,
                    "order": 1
                }}
            ]
        }}
    ]
}}

LƯU Ý:
- CHỈ trả về JSON, KHÔNG có markdown hay text thừa
- Mô tả ngắn gọn, tránh quá dài
- Mỗi module 2-3 learning outcomes
- Mỗi module 2-3 lessons
- Max 3-4 modules
"""

        user_prompt = f"Tạo khóa học: {prompt[:200]}"  # Giới hạn prompt
        
        # Generate course structure
        print(f"🤖 Calling Gemini API for course generation...", flush=True)
        response = model.generate_content(
            [system_prompt, user_prompt],
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=8000  # Tăng lên 8000
            )
        )
        
        print(f"✅ Gemini API responded", flush=True)
        
        # Parse response
        response_text = response.text.strip()
        print(f"📄 Response length: {len(response_text)} characters", flush=True)
        
        # Extract JSON - IMPROVED LOGIC
        json_str = None
        
        # Method 1: Check for ```json specifically
        if "```json" in response_text:
            print(f"📋 Found ```json block", flush=True)
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            if json_end > json_start:
                json_str = response_text[json_start:json_end].strip()
                print(f"📋 Method 1 extracted {len(json_str)} chars", flush=True)
            else:
                print(f"📋 Method 1 failed: json_end ({json_end}) <= json_start ({json_start})", flush=True)
        
        # Method 2: Look for JSON object directly (starts with {)
        if not json_str:
            print(f"📋 Method 1 didn't work, trying Method 2...", flush=True)
            # Find first { and last }
            first_brace = response_text.find("{")
            last_brace = response_text.rfind("}")
            
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                print(f"📋 Found JSON object at position {first_brace}-{last_brace}", flush=True)
                json_str = response_text[first_brace:last_brace+1]
            else:
                print(f"❌ No JSON object found in response", flush=True)
                raise ValueError("No valid JSON found in AI response")
        else:
            print(f"📋 Using Method 1 result", flush=True)
        
        print(f"📋 Extracted JSON length: {len(json_str)} chars", flush=True)
        print(f"📋 JSON preview: {json_str[:300]}...", flush=True)
        
        course_data = json.loads(json_str)
        
        # IMPORTANT FIX: Validate required fields để tránh crash
        required_fields = ["title", "description", "category", "level", "modules"]
        for field in required_fields:
            if field not in course_data:
                raise ValueError(f"AI response missing required field: {field}")
        
        # Validate modules structure
        if not isinstance(course_data.get("modules"), list) or len(course_data["modules"]) == 0:
            raise ValueError("AI response has invalid or empty modules")
        
        # Validate each module has required fields
        for idx, module in enumerate(course_data["modules"]):
            if not isinstance(module, dict):
                raise ValueError(f"Module {idx} is not a dict")
            if "title" not in module or "lessons" not in module:
                raise ValueError(f"Module {idx} missing title or lessons")
            if not isinstance(module["lessons"], list) or len(module["lessons"]) == 0:
                raise ValueError(f"Module {idx} has invalid or empty lessons")
        
        return course_data
        
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        print(f"❌ AI course generation error: {type(e).__name__}: {str(e)}", flush=True)
        print(f"📝 JSON preview: {json_str[:500] if 'json_str' in locals() else 'N/A'}", flush=True)
        print(f"🔄 Returning fallback structure...", flush=True)
        # Fallback structure với learning_outcomes đúng format
        return {
            "title": f"Khóa học về {prompt[:50]}",
            "description": f"Khóa học được tạo tự động dựa trên yêu cầu: {prompt}",
            "category": "General",
            "level": difficulty,
            "learning_outcomes": [
                {
                    "id": "lo1",
                    "description": f"Hiểu được khái niệm cơ bản về {prompt[:30]}",
                    "skill_tag": "basic-understanding"
                },
                {
                    "id": "lo2",
                    "description": "Áp dụng được kiến thức vào thực tế",
                    "skill_tag": "practical-application"
                }
            ],
            "modules": [
                {
                    "title": "Module 1: Giới thiệu",
                    "description": "Module giới thiệu khóa học",
                    "order": 1,
                    "difficulty": "Basic",
                    "estimated_hours": 2,
                    "learning_outcomes": [
                        {
                            "description": "Nắm được tổng quan về khóa học",
                            "skill_tag": "overview"
                        },
                        {
                            "description": "Chuẩn bị kiến thức nền tảng",
                            "skill_tag": "foundation"
                        }
                    ],
                    "lessons": [
                        {
                            "title": "Bài 1: Tổng quan",
                            "description": "Giới thiệu tổng quan về khóa học",
                            "content": f"Nội dung về {prompt}",
                            "duration_minutes": 20,
                            "order": 1
                        }
                    ]
                }
            ]
        }
    except Exception as e:
        print(f"❌ Unexpected error in course generation: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"📍 Traceback: {traceback.format_exc()}")
        print(f"🔄 Returning fallback structure...")
        # Same fallback structure với learning_outcomes đúng format
        return {
            "title": f"Khóa học về {prompt[:50]}",
            "description": f"Khóa học được tạo tự động dựa trên yêu cầu: {prompt}",
            "category": "General",
            "level": difficulty,
            "learning_outcomes": [
                {
                    "id": "lo1",
                    "description": f"Hiểu được khái niệm cơ bản về {prompt[:30]}",
                    "skill_tag": "basic-understanding"
                },
                {
                    "id": "lo2",
                    "description": "Áp dụng được kiến thức vào thực tế",
                    "skill_tag": "practical-application"
                }
            ],
            "modules": [
                {
                    "title": "Module 1: Giới thiệu",
                    "description": "Module giới thiệu khóa học",
                    "order": 1,
                    "difficulty": "Basic",
                    "estimated_hours": 2,
                    "learning_outcomes": [
                        {
                            "description": "Nắm được tổng quan về khóa học",
                            "skill_tag": "overview"
                        },
                        {
                            "description": "Chuẩn bị kiến thức nền tảng",
                            "skill_tag": "foundation"
                        }
                    ],
                    "lessons": [
                        {
                            "title": "Bài 1: Tổng quan",
                            "description": "Giới thiệu tổng quan về khóa học",
                            "content": f"Nội dung về {prompt}",
                            "duration_minutes": 20,
                            "order": 1
                        }
                    ]
                }
            ]
        }


async def generate_module_quiz(
    module_title: str,
    learning_outcomes: List[Dict],
    module_description: Optional[str] = None,
    question_count: int = 10,
    difficulty: str = "medium",
    focus_outcomes: Optional[List[str]] = None
) -> Dict:
    """
    Generate quiz questions from module learning outcomes using Gemini AI.
    
    Args:
        module_title: Title of the module
        learning_outcomes: List of learning outcomes with structure:
            [{"id": str, "outcome": str, "skill_tag": str, "is_mandatory": bool}]
        module_description: Optional description of the module for context
        question_count: Number of questions to generate (5-30)
        difficulty: Difficulty level (easy|medium|hard)
        focus_outcomes: Optional list of outcome IDs to focus on
        
    Returns:
        Dict with structure matching Quiz model schema:
        {
            "questions": [
                {
                    "question": str,
                    "type": "multiple_choice" | "fill_in_blank" | "true_false",
                    "options": List[str],  # Empty for fill_in_blank
                    "correct_answer": str,
                    "explanation": str,
                    "points": int,
                    "is_mandatory": bool,
                    "order": int,
                    "outcome_id": str  # Link to learning outcome
                }
            ],
            "total_points": int,
            "mandatory_count": int,
            "estimated_time_minutes": int
        }
    """
    try:
        # Validate inputs
        if not learning_outcomes or len(learning_outcomes) == 0:
            raise ValueError("Learning outcomes cannot be empty")
        
        if question_count < 5 or question_count > 30:
            raise ValueError("Question count must be between 5 and 30")
        
        if difficulty not in ["easy", "medium", "hard"]:
            difficulty = "medium"
        
        # Limit outcomes to avoid token overflow (max 10)
        # If focus_outcomes specified, prioritize those
        if focus_outcomes and len(focus_outcomes) > 0:
            # Filter to focus outcomes
            focused = [o for o in learning_outcomes if o.get("id") in focus_outcomes]
            if focused:
                outcomes_subset = focused[:10]
            else:
                outcomes_subset = learning_outcomes[:10]
        else:
            outcomes_subset = learning_outcomes[:10]
        
        # Build outcomes context
        outcomes_text = "\n".join([
            f"{i+1}. {outcome.get('outcome', '')} (ID: {outcome.get('id', '')}, Bắt buộc: {outcome.get('is_mandatory', False)})"
            for i, outcome in enumerate(outcomes_subset)
        ])
        
        # Add module description if available
        context_text = ""
        if module_description:
            context_text = f"\nMô tả module: {module_description}\n"
        
        # Build prompt with strict JSON structure matching Quiz schema
        prompt = f"""Bạn là chuyên gia giáo dục, hãy tạo {question_count} câu hỏi trắc nghiệm cho module "{module_title}".

THÔNG TIN MODULE:
{outcomes_text}
{context_text}

YÊU CẦU:
1. Tạo chính xác {question_count} câu hỏi
2. Độ khó: {difficulty}
3. Phân bổ đều các loại câu hỏi:
   - 60% multiple_choice (4 lựa chọn)
   - 25% fill_in_blank (câu trả lời ngắn)
   - 15% true_false (đúng/sai)
4. Câu hỏi cho outcome bắt buộc (is_mandatory=True) phải đánh dấu is_mandatory=True
5. Điểm mỗi câu: 5-15 points tùy độ khó
6. Phải có explanation chi tiết cho mỗi câu

ĐỊNH DẠNG JSON (QUAN TRỌNG - PHẢI TUÂN THỦ):
{{
  "questions": [
    {{
      "question": "Nội dung câu hỏi chi tiết",
      "type": "multiple_choice",
      "options": ["A. Đáp án 1", "B. Đáp án 2", "C. Đáp án 3", "D. Đáp án 4"],
      "correct_answer": "A. Đáp án 1",
      "explanation": "Giải thích chi tiết tại sao đây là đáp án đúng",
      "points": 10,
      "is_mandatory": false,
      "order": 1
    }}
  ]
}}

CHÚ Ý:
- Với câu fill_in_blank: options = []
- Với câu true_false: options = ["Đúng", "Sai"]
- correct_answer phải khớp chính xác với 1 trong các options
- order bắt đầu từ 1 và tăng dần

Chỉ trả về JSON thuần túy, không có markdown code block hay text thừa."""

        # Call Gemini AI (use model from settings, not hardcoded)
        quiz_model = genai.GenerativeModel(settings.gemini_model)
        response = quiz_model.generate_content(prompt)
        
        if not response or not response.text:
            raise ValueError("AI did not return any response")
        
        # Extract JSON from response
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Parse JSON
        quiz_data = json.loads(response_text)
        
        # Validate response structure
        if "questions" not in quiz_data or not isinstance(quiz_data["questions"], list):
            raise ValueError("Invalid AI response: missing 'questions' array")
        
        questions = quiz_data["questions"]
        
        if len(questions) == 0:
            raise ValueError("AI generated 0 questions")
        
        # Validate and fix each question
        validated_questions = []
        total_points = 0
        mandatory_count = 0
        
        for idx, q in enumerate(questions):
            # Ensure required fields
            if "question" not in q or not q["question"]:
                continue
            
            # Default type
            if "type" not in q or q["type"] not in ["multiple_choice", "fill_in_blank", "true_false"]:
                q["type"] = "multiple_choice"
            
            # Validate options based on type
            if q["type"] == "fill_in_blank":
                q["options"] = []
            elif q["type"] == "true_false":
                q["options"] = ["Đúng", "Sai"]
            else:  # multiple_choice
                if "options" not in q or not isinstance(q["options"], list) or len(q["options"]) < 2:
                    continue  # Skip invalid question
            
            # Validate correct_answer
            if "correct_answer" not in q or not q["correct_answer"]:
                continue
            
            # For multiple choice and true/false, correct_answer must be in options
            if q["type"] in ["multiple_choice", "true_false"]:
                if q["correct_answer"] not in q["options"]:
                    # Try to match
                    matched = False
                    for opt in q["options"]:
                        if q["correct_answer"].lower() in opt.lower() or opt.lower() in q["correct_answer"].lower():
                            q["correct_answer"] = opt
                            matched = True
                            break
                    if not matched:
                        continue  # Skip invalid question
            
            # Default explanation
            if "explanation" not in q or not q["explanation"]:
                q["explanation"] = f"Đáp án đúng là: {q['correct_answer']}"
            
            # Default points (5-15 based on difficulty)
            if "points" not in q or not isinstance(q["points"], int) or q["points"] < 1:
                if difficulty == "easy":
                    q["points"] = 5
                elif difficulty == "hard":
                    q["points"] = 15
                else:
                    q["points"] = 10
            
            # is_mandatory
            if "is_mandatory" not in q:
                q["is_mandatory"] = False
            
            if q["is_mandatory"]:
                mandatory_count += 1
            
            # order
            q["order"] = idx + 1
            
            # Map field names to Quiz model schema
            # AI uses "question", Quiz model uses "question_text"
            if "question" in q and "question_text" not in q:
                q["question_text"] = q["question"]
                del q["question"]
            
            total_points += q["points"]
            validated_questions.append(q)
        
        # Ensure we have at least 3 questions
        if len(validated_questions) < 3:
            raise ValueError(f"AI generated only {len(validated_questions)} valid questions, minimum is 3")
        
        # Estimate time: 1-2 minutes per question
        estimated_time = len(validated_questions) * 2
        
        return {
            "questions": validated_questions,
            "total_points": total_points,
            "mandatory_count": mandatory_count,
            "estimated_time_minutes": estimated_time
        }
    
    except json.JSONDecodeError as e:
        print(f"Failed to parse AI response as JSON: {str(e)}")
        print(f"Response text: {response_text[:500]}")
        print(f"Returning fallback questions for module: {module_title}")
        return _generate_module_quiz_fallback(
            module_title=module_title,
            learning_outcomes=outcomes_subset,
            question_count=question_count,
            difficulty=difficulty
        )
    
    except Exception as e:
        print(f"Error in generate_module_quiz: {str(e)}")
        print(f"Returning fallback questions for module: {module_title}")
        return _generate_module_quiz_fallback(
            module_title=module_title,
            learning_outcomes=outcomes_subset,
            question_count=question_count,
            difficulty=difficulty
        )


def _generate_module_quiz_fallback(
    module_title: str,
    learning_outcomes: List[Dict],
    question_count: int,
    difficulty: str
) -> Dict:
    """
    Generate fallback quiz questions when AI is unavailable.
    
    Args:
        module_title: Title of the module
        learning_outcomes: List of learning outcomes
        question_count: Number of questions to generate
        difficulty: Difficulty level
        
    Returns:
        Dict with quiz structure matching Quiz model schema
    """
    questions = []
    total_points = 0
    mandatory_count = 0
    
    # Calculate distribution based on question count
    mc_count = int(question_count * 0.6)  # 60% multiple choice
    fb_count = int(question_count * 0.25)  # 25% fill in blank
    tf_count = question_count - mc_count - fb_count  # remaining true/false
    
    # Ensure at least 1 of each type if possible
    if question_count >= 3:
        if mc_count == 0:
            mc_count = 1
        if fb_count == 0 and question_count > 3:
            fb_count = 1
        if tf_count == 0 and question_count > 4:
            tf_count = 1
        # Recalculate to ensure sum equals question_count
        total = mc_count + fb_count + tf_count
        if total > question_count:
            tf_count = question_count - mc_count - fb_count
    
    # Set points based on difficulty
    if difficulty == "easy":
        base_points = 5
    elif difficulty == "hard":
        base_points = 15
    else:
        base_points = 10
    
    order = 1
    
    # Generate multiple choice questions
    for i in range(mc_count):
        # Cycle through outcomes
        outcome = learning_outcomes[i % len(learning_outcomes)]
        outcome_text = outcome.get("outcome", "knowledge")
        outcome_id = outcome.get("id", "")
        is_mandatory = outcome.get("is_mandatory", False)
        
        question = {
            "question_text": f"[Fallback] Câu hỏi trắc nghiệm về: {outcome_text}",
            "type": "multiple_choice",
            "options": [
                "A. Đáp án mẫu A",
                "B. Đáp án mẫu B", 
                "C. Đáp án mẫu C",
                "D. Đáp án mẫu D"
            ],
            "correct_answer": "A. Đáp án mẫu A",
            "explanation": f"Giải thích mẫu cho câu hỏi về {outcome_text}",
            "points": base_points,
            "is_mandatory": is_mandatory,
            "order": order,
            "outcome_id": outcome_id
        }
        
        if is_mandatory:
            mandatory_count += 1
        
        total_points += base_points
        questions.append(question)
        order += 1
    
    # Generate fill in blank questions
    for i in range(fb_count):
        outcome = learning_outcomes[(mc_count + i) % len(learning_outcomes)]
        outcome_text = outcome.get("outcome", "knowledge")
        outcome_id = outcome.get("id", "")
        is_mandatory = outcome.get("is_mandatory", False)
        
        question = {
            "question_text": f"[Fallback] Điền vào chỗ trống liên quan đến: {outcome_text}",
            "type": "fill_in_blank",
            "options": [],
            "correct_answer": "đáp án mẫu",
            "explanation": f"Giải thích mẫu cho câu điền chỗ trống về {outcome_text}",
            "points": base_points,
            "is_mandatory": is_mandatory,
            "order": order,
            "outcome_id": outcome_id
        }
        
        if is_mandatory:
            mandatory_count += 1
        
        total_points += base_points
        questions.append(question)
        order += 1
    
    # Generate true/false questions
    for i in range(tf_count):
        outcome = learning_outcomes[(mc_count + fb_count + i) % len(learning_outcomes)]
        outcome_text = outcome.get("outcome", "knowledge")
        outcome_id = outcome.get("id", "")
        is_mandatory = outcome.get("is_mandatory", False)
        
        question = {
            "question_text": f"[Fallback] Đúng hay sai: {outcome_text}",
            "type": "true_false",
            "options": ["Đúng", "Sai"],
            "correct_answer": "Đúng",
            "explanation": f"Giải thích mẫu cho câu đúng/sai về {outcome_text}",
            "points": base_points,
            "is_mandatory": is_mandatory,
            "order": order,
            "outcome_id": outcome_id
        }
        
        if is_mandatory:
            mandatory_count += 1
        
        total_points += base_points
        questions.append(question)
        order += 1
    
    # Estimate time: 1.5 minutes per question
    estimated_time = int(question_count * 1.5)
    
    return {
        "questions": questions,
        "total_points": total_points,
        "mandatory_count": mandatory_count,
        "estimated_time_minutes": estimated_time
    }


async def generate_practice_exercises(
    topic: str,
    difficulty: str = "medium",
    question_count: int = 5,
    practice_type: str = "multiple_choice",
    focus_skills: Optional[List[str]] = None,
    learning_outcomes: Optional[List[Dict]] = None,
    content_summary: str = ""
) -> Dict:
    """
    Sinh bài tập luyện tập bằng AI với context đầy đủ
    
    Args:
        topic: Chủ đề cần luyện tập
        difficulty: easy|medium|hard
        question_count: Số câu hỏi (1-20)
        practice_type: multiple_choice|short_answer|mixed
        focus_skills: Danh sách skill tags cần tập trung (optional)
        learning_outcomes: Learning outcomes từ course/lesson (optional)
        content_summary: Tóm tắt nội dung từ course/lesson (optional)
        
    Returns:
        Dict with exercises array
    """
    try:
        import sys
        print(f"\n🤖 AI Service: generate_practice_exercises", flush=True)
        print(f"  Topic: {topic}", flush=True)
        print(f"  Difficulty: {difficulty}", flush=True)
        print(f"  Count: {question_count}", flush=True)
        print(f"  Has learning outcomes: {len(learning_outcomes) if learning_outcomes else 0}", flush=True)
        print(f"  Has content summary: {len(content_summary)}", flush=True)
        
        # Map difficulty
        diff_map = {
            "easy": "dễ",
            "medium": "trung bình",
            "hard": "khó"
        }
        diff_vn = diff_map.get(difficulty, "trung bình")
        
        # Build prompt with context (giảm context để tránh quá dài)
        prompt = f"""Bạn là chuyên gia giáo dục, hãy tạo {question_count} câu hỏi luyện tập chất lượng cao.

CHỦ ĐỀ: {topic}

"""
        
        # Add content summary if available (giới hạn 200 chars)
        if content_summary:
            summary_short = content_summary[:200]
            prompt += f"""NỘI DUNG THAM KHẢO:
{summary_short}

"""
        
        # Add learning outcomes if available (max 3 outcomes)
        if learning_outcomes and len(learning_outcomes) > 0:
            prompt += "MỤC TIÊU HỌC TẬP:\n"
            for i, outcome in enumerate(learning_outcomes[:3], 1):  # Max 3 outcomes
                desc = outcome.get("description", "")
                skill = outcome.get("skill_tag", "")
                if desc:
                    # Giới hạn description 100 chars
                    desc_short = desc[:100]
                    prompt += f"{i}. {desc_short}"
                    if skill:
                        prompt += f" (Kỹ năng: {skill})"
                    prompt += "\n"
            prompt += "\n"
        
        # Add requirements
        prompt += f"""YÊU CẦU:
1. Độ khó: {diff_vn}
2. Số câu hỏi: {question_count}
3. Loại câu hỏi: {practice_type}
"""
        
        if focus_skills:
            prompt += f"4. Tập trung vào các kỹ năng: {', '.join(focus_skills[:3])}\n"  # Max 3 skills
        
        prompt += """
QUAN TRỌNG - ĐỊNH DẠNG JSON:
Chỉ trả về JSON thuần túy, KHÔNG có markdown, KHÔNG có code block, KHÔNG có text thừa.

{
  "exercises": [
    {
      "id": "uuid-here",
      "type": "theory",
      "question": "Nội dung câu hỏi",
      "options": ["A. Đáp án 1", "B. Đáp án 2", "C. Đáp án 3", "D. Đáp án 4"],
      "correct_answer": "A. Đáp án 1",
      "explanation": "Giải thích ngắn gọn",
      "difficulty": "Medium",
      "related_skill": "skill-tag",
      "points": 10
    }
  ]
}

LƯU Ý:
- CHỈ JSON, KHÔNG có ```json hoặc ``` hay markdown
- Với short_answer: options = null
- type: theory, coding, hoặc problem-solving
- Câu hỏi ngắn gọn, rõ ràng
"""

        print(f"  Calling Gemini API...", flush=True)
        
        # Call Gemini AI
        model = genai.GenerativeModel(settings.gemini_model)
        response = model.generate_content(prompt)
        
        response_text = response.text.strip()
        
        print(f"  Response length: {len(response_text)} chars", flush=True)
        print(f"  Response preview: {response_text[:200]}...", flush=True)
        
        # Extract JSON - IMPROVED LOGIC
        json_str = None
        
        # Method 1: Check for ```json specifically
        if "```json" in response_text:
            print(f"  Found ```json block", flush=True)
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            if json_end > json_start:
                json_str = response_text[json_start:json_end].strip()
        
        # Method 2: Look for JSON object directly (starts with {)
        if not json_str:
            # Find first { and last }
            first_brace = response_text.find("{")
            last_brace = response_text.rfind("}")
            
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                print(f"  Found JSON object at position {first_brace}-{last_brace}", flush=True)
                json_str = response_text[first_brace:last_brace+1]
            else:
                print(f"  No JSON object found in response", flush=True)
                raise ValueError("No valid JSON found in AI response")
        
        print(f"  Extracted JSON length: {len(json_str)} chars", flush=True)
        print(f"  JSON preview: {json_str[:300]}...", flush=True)
        
        # Parse JSON
        print(f"  Parsing JSON...", flush=True)
        data = json.loads(json_str)
        
        # Validate
        if "exercises" not in data or not isinstance(data["exercises"], list):
            raise ValueError("Invalid response structure - missing exercises array")
        
        print(f"  ✅ Parsed successfully! Found {len(data['exercises'])} exercises", flush=True)
        
        # Add UUIDs if missing
        for ex in data["exercises"]:
            if "id" not in ex or not ex["id"] or ex["id"] == "uuid-here":
                ex["id"] = str(generate_uuid())
        
        return data
        
    except json.JSONDecodeError as e:
        print(f"\n❌ JSON Parse Error!", flush=True)
        print(f"  Error: {str(e)}", flush=True)
        print(f"  Position: line {e.lineno}, col {e.colno}", flush=True)
        if 'json_str' in locals():
            print(f"  Problematic JSON:", flush=True)
            lines = json_str.split('\n')
            for i, line in enumerate(lines[:20], 1):  # Show first 20 lines
                print(f"    {i}: {line}", flush=True)
        # Fallback: Return empty
        return {"exercises": []}
        
    except Exception as e:
        print(f"\n❌ AI generate_practice_exercises failed!", flush=True)
        print(f"  Error type: {type(e).__name__}", flush=True)
        print(f"  Error: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        # Fallback: Return empty
        return {"exercises": []}
