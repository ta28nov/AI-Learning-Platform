"""
Progress Schemas
Định nghĩa request/response schemas cho progress endpoints
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class LessonProgress(BaseModel):
    id: str = Field(..., description="UUID")
    title: str
    status: str = Field(..., description="completed|in-progress|not-started")
    completion_date: Optional[datetime] = None


class ModuleProgress(BaseModel):
    id: str = Field(..., description="UUID")
    title: str
    progress: float = Field(..., description="0-100")
    lessons: List[LessonProgress]


class ProgressCourseResponse(BaseModel):
    course_id: str = Field(..., description="UUID")
    course_title: str
    overall_progress: float = Field(..., description="0-100")
    modules: List[ModuleProgress]
    estimated_hours_remaining: float
    study_streak_days: int
    avg_quiz_score: float = Field(..., description="0-100")
    total_hours_spent: float
