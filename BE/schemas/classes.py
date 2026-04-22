"""
Classes Schemas
Định nghĩa request/response schemas cho classes endpoints (Instructor)
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class ClassCreateRequest(BaseModel):
    name: str
    description: str
    course_id: str = Field(..., description="UUID")
    start_date: datetime
    end_date: datetime
    max_students: int


class ClassCreateResponse(BaseModel):
    class_id: str = Field(..., description="UUID")
    name: str
    invite_code: str = Field(..., description="6-8 characters")
    course_title: str
    student_count: int = Field(..., description="Số học viên hiện tại")
    created_at: datetime
    message: str


class ClassListItem(BaseModel):
    id: str = Field(..., description="UUID")
    name: str
    course_title: str
    student_count: str = Field(..., description="e.g. 25/30")
    status: str = Field(..., description="preparing|active|completed")
    start_date: datetime
    end_date: datetime
    progress: float = Field(..., description="0-100")


class ClassListResponse(BaseModel):
    classes: List[ClassListItem]
    total: int


class StudentInfo(BaseModel):
    id: str = Field(..., description="UUID")
    name: str
    email: str
    avatar_url: Optional[str] = None
    progress: float = Field(..., description="0-100")
    joined_at: datetime


class CourseInfo(BaseModel):
    id: str = Field(..., description="UUID")
    title: str
    module_count: int


class ClassStats(BaseModel):
    total_students: int
    lessons_completed: int
    avg_quiz_score: float


class ClassDetailResponse(BaseModel):
    id: str = Field(..., description="UUID")
    name: str
    description: str
    course: CourseInfo
    invite_code: str
    max_students: int
    student_count: int
    start_date: datetime
    end_date: datetime
    status: str
    recent_students: List[StudentInfo]
    class_stats: ClassStats


class ClassUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    max_students: Optional[int] = None
    end_date: Optional[datetime] = None


class ClassUpdateResponse(BaseModel):
    class_id: str = Field(..., description="UUID")
    message: str
    updated_at: datetime


class ClassDeleteResponse(BaseModel):
    message: str


class ClassJoinRequest(BaseModel):
    invite_code: str = Field(..., description="6-8 characters")


class ClassJoinResponse(BaseModel):
    message: str
    class_id: str = Field(..., description="UUID")
    class_name: str
    course_title: str
    course_id: str = Field(..., description="UUID")
    instructor_name: str
    enrollment_id: str = Field(..., description="UUID")
    student_count: int
    max_students: int


class ClassStudent(BaseModel):
    student_id: str = Field(..., description="UUID")
    student_name: str
    email: str
    join_date: datetime
    progress: float = Field(..., description="0-100")
    completed_modules: int
    total_modules: int
    last_activity: datetime
    quiz_average: float = Field(..., description="0-100")


class ClassStudentListResponse(BaseModel):
    class_id: str = Field(..., description="UUID")
    class_name: str
    data: List[ClassStudent]
    total: int
    skip: int
    limit: int


class QuizScore(BaseModel):
    quiz_id: str = Field(..., description="UUID")
    quiz_title: str
    score: float = Field(..., description="0-100")
    attempt_date: datetime


class ModuleDetail(BaseModel):
    module_id: str = Field(..., description="UUID")
    module_title: str
    progress: float = Field(..., description="0-100")
    completed_lessons: int
    quiz_scores: List[QuizScore]


class StudentProgress(BaseModel):
    overall_progress: float = Field(..., description="0-100")
    completed_modules: int
    total_modules: int
    study_streak_days: int
    total_study_time: float = Field(..., description="Hours")


class ClassStudentInfo(BaseModel):
    student_id: str = Field(..., description="UUID")
    student_name: str
    email: str
    join_date: datetime


class ClassStudentDetailResponse(BaseModel):
    student_id: str = Field(..., description="UUID")
    student_name: str
    email: str
    avatar_url: Optional[str] = None
    quiz_scores: List[QuizScore]
    modules_detail: List[ModuleDetail]
    progress: StudentProgress


class ClassProgressResponse(BaseModel):
    class_id: str = Field(..., description="UUID")
    class_name: str
    total_students: int
    average_progress: float = Field(..., description="0-100")
    completion_rate: float = Field(..., description="0-100")
    average_quiz_score: float = Field(..., description="0-100")
