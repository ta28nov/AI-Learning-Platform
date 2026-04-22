"""
Enrollment Schemas
Định nghĩa request/response schemas cho enrollment endpoints
Bao gồm: enroll, list my courses, detail, cancel
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class EnrollmentCreateRequest(BaseModel):
    course_id: str = Field(..., description="UUID of course to enroll")


class EnrollmentCreateResponse(BaseModel):
    id: str = Field(..., description="UUID of created enrollment")
    user_id: str = Field(..., description="UUID of student")
    course_id: str = Field(..., description="UUID of course")
    course_title: str
    status: str = Field(..., description="active")
    enrolled_at: datetime
    progress_percent: float = Field(..., description="0 on creation")
    message: str = Field(..., description="Success message")


class NextLessonInfo(BaseModel):
    lesson_id: Optional[str] = Field(None, description="UUID of next lesson, null if completed")
    lesson_title: Optional[str] = None
    module_title: Optional[str] = None


class EnrollmentListItem(BaseModel):
    id: str = Field(..., description="UUID of enrollment")
    course_id: str
    course_title: str
    course_description: str = Field(..., description="Short description")
    course_thumbnail: Optional[str] = Field(None, description="Thumbnail URL")
    course_level: str = Field(..., description="Beginner|Intermediate|Advanced")
    instructor_name: str
    status: str = Field(..., description="in-progress|completed|cancelled")
    progress_percent: float = Field(..., description="0-100")
    enrolled_at: datetime
    last_accessed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    avg_quiz_score: Optional[float] = Field(None, description="0-100")
    total_time_spent_minutes: int
    next_lesson: Optional[NextLessonInfo] = Field(None, description="Next lesson info if available")


class EnrollmentSummary(BaseModel):
    total_enrollments: int
    in_progress: int
    completed: int
    cancelled: int


class EnrollmentListResponse(BaseModel):
    enrollments: List[EnrollmentListItem]
    summary: EnrollmentSummary
    skip: int
    limit: int


class EnrollmentDetailResponse(BaseModel):
    id: str = Field(..., description="UUID of enrollment")
    user_id: str = Field(..., description="UUID of student")
    course_id: str
    course_title: str
    course_description: str
    course_thumbnail: Optional[str] = Field(None, description="URL")
    instructor_name: str
    status: str = Field(..., description="active|completed|cancelled")
    enrolled_at: datetime
    completed_at: Optional[datetime] = None
    progress_percent: float = Field(..., description="0-100")
    avg_quiz_score: Optional[float] = Field(None, description="0-100")
    total_modules: int
    completed_modules: int
    total_lessons: int
    completed_lessons: int


class EnrollmentCancelResponse(BaseModel):
    message: str = Field(..., description="Success message")
    note: str = Field(..., description="Data preservation notice")
