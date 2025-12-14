"""
Recommendation Schemas
Định nghĩa request/response schemas cho recommendation endpoints
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class RecommendedCourseItem(BaseModel):
    course_id: str = Field(..., description="UUID")
    title: str
    description: str
    category: str
    level: str
    thumbnail_url: Optional[str] = None
    priority_rank: int = Field(..., description="1=highest priority")
    relevance_score: float = Field(..., description="0-100")
    reason: str
    addresses_gaps: List[str]
    estimated_completion_days: int


class LearningStep(BaseModel):
    step: int
    course_id: str = Field(..., description="UUID")
    focus_modules: List[str]
    why_this_order: str


class PracticeExerciseItem(BaseModel):
    skill_tag: str
    exercise_type: str = Field(..., description="coding|quiz|project|reading")
    description: str
    difficulty: str = Field(..., description="easy|medium|hard")
    estimated_time_hours: float


class AssessmentRecommendationResponse(BaseModel):
    assessment_session_id: str = Field(..., description="UUID")
    user_proficiency_level: str = Field(..., description="Beginner|Intermediate|Advanced")
    recommended_courses: List[RecommendedCourseItem]
    suggested_learning_order: List[LearningStep]
    practice_exercises: List[PracticeExerciseItem]
    total_estimated_hours: float
    ai_personalized_advice: str


class SimpleRecommendation(BaseModel):
    course_id: str = Field(..., description="UUID")
    title: str
    reason: str
    relevance_score: float = Field(..., description="0-100")


class RecommendationResponse(BaseModel):
    recommended_courses: List[SimpleRecommendation]
