"""Canned AI responses for integration tests (no Gemini calls)."""

import uuid
from typing import Any, Dict, List, Optional


def mock_assessment_questions(
    category: str,
    subject: str,
    level: str,
    count: int = 15,
    focus_areas: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    n = 15 if level == "Beginner" else (25 if level == "Intermediate" else min(count, 35))
    questions = []
    for i in range(n):
        diff = "easy" if i < 3 else ("hard" if i >= n - 4 else "medium")
        points = 1 if diff == "easy" else (3 if diff == "hard" else 2)
        questions.append(
            {
                "question_id": f"q{i + 1}",
                "question_text": f"Test question {i + 1} about {subject}?",
                "question_type": "multiple_choice",
                "difficulty": diff,
                "skill_tag": f"{subject.lower()}-basics",
                "points": points,
                "options": ["A", "B", "C", "D"],
                "correct_answer_hint": "A",
            }
        )
    return questions


def mock_evaluate_assessment_answers(
    questions: List[Dict],
    answers: List[Dict],
    category: str,
    subject: str,
) -> Dict[str, Any]:
    per_question = []
    for q in questions:
        per_question.append(
            {
                "question_id": q["question_id"],
                "is_correct": True,
                "points_earned": q.get("points", 1),
                "feedback": "Correct (mock)",
            }
        )
    return {
        "overall_score": 85.0,
        "proficiency_level": "Advanced",
        "skill_analysis": [
            {
                "skill_tag": f"{subject.lower()}-basics",
                "questions_count": len(questions),
                "correct_count": len(questions),
                "proficiency_percentage": 100.0,
                "strength_level": "Strong",
                "detailed_feedback": "Mock analysis",
            }
        ],
        "knowledge_gaps": [],
        "overall_feedback": "Mock evaluation completed successfully.",
        "score_breakdown": {
            "easy": {"correct": 3, "total": 3},
            "medium": {"correct": 8, "total": 8},
            "hard": {"correct": 4, "total": 4},
        },
        "per_question_results": per_question,
    }


def mock_chat_response(
    course_id: str,
    question: str,
    conversation_history: Optional[List[Dict]] = None,
) -> str:
    return f"Mock AI tutor reply for course {course_id}: understood your question."


def mock_course_recommendations(*args, **kwargs) -> List[Dict[str, Any]]:
    return [{"course_id": str(uuid.uuid4()), "title": "Mock Recommended Course", "match_score": 90}]


def mock_ai_recommendation_reasons(
    assessment_results: Dict,
    selected_courses: List[Any],
) -> Dict[str, Any]:
    reasons = {}
    for course in selected_courses:
        cid = str(getattr(course, "id", course))
        reasons[cid] = f"Mock reason for course {getattr(course, 'title', cid)}"
    return {"course_reasons": reasons, "general_advice": "Mock personalized advice."}


def mock_practice_exercises(*args, **kwargs) -> Dict[str, Any]:
    return {
        "exercises": [
            {
                "id": "ex1",
                "type": "multiple_choice",
                "question_text": "Practice question?",
                "options": ["A", "B"],
                "correct_answer": "A",
            }
        ]
    }


def mock_generate_course_from_prompt(
    prompt: str,
    user_preferences: Optional[List[str]] = None,
    difficulty: str = "Beginner",
) -> Dict[str, Any]:
    mid = str(uuid.uuid4())
    lid = str(uuid.uuid4())
    return {
        "title": "Mock AI Course",
        "description": "Generated for tests",
        "category": "Programming",
        "level": difficulty,
        "estimated_duration": 30,
        "modules": [
            {
                "title": "Module 1",
                "description": "Intro",
                "order": 1,
                "difficulty": "Basic",
                "estimated_hours": 2,
                "learning_outcomes": [
                    {"description": "Learn basics", "skill_tag": "python-basics"}
                ],
                "lessons": [
                    {
                        "title": "Lesson 1",
                        "description": "First lesson",
                        "content": "Content",
                        "duration_minutes": 15,
                        "order": 1,
                    }
                ],
            }
        ],
    }


def mock_generate_module_quiz(
    module_title: str,
    learning_outcomes: List[Dict],
    module_description: Optional[str] = None,
    question_count: int = 10,
    difficulty: str = "medium",
    focus_outcomes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    outcome_id = learning_outcomes[0].get("id", "out1") if learning_outcomes else "out1"
    questions = []
    for i in range(min(question_count, 5)):
        questions.append(
            {
                "question": f"Module quiz Q{i + 1}?",
                "type": "multiple_choice",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A",
                "explanation": "Mock",
                "points": 2,
                "is_mandatory": i == 0,
                "order": i + 1,
                "outcome_id": outcome_id,
            }
        )
    return {
        "questions": questions,
        "total_points": len(questions) * 2,
        "mandatory_count": 1,
        "estimated_time_minutes": 15,
    }
