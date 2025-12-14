"""
Quiz Schemas
Định nghĩa request/response schemas cho quiz endpoints
Bao gồm: get detail, attempt, results, retake, create, update, delete, practice, list, class results
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class QuizDetailResponse(BaseModel):
    id: str = Field(..., description="UUID quiz")
    title: str
    description: str
    question_count: int
    time_limit: int = Field(..., description="Minutes")
    pass_threshold: int = Field(..., description="Percentage")
    mandatory_question_count: int
    user_attempts: int
    best_score: Optional[float] = Field(None, description="0-100")
    last_attempt_at: Optional[datetime] = None


class AnswerItem(BaseModel):
    question_id: str = Field(..., description="UUID")
    selected_option: str = Field(..., description="A|B|C|D or fill-in text")


class QuizAttemptRequest(BaseModel):
    answers: List[AnswerItem]
    time_spent_minutes: Optional[int] = Field(None, description="Time spent on quiz in minutes")


class QuizAttemptResponse(BaseModel):
    attempt_id: str = Field(..., description="UUID")
    quiz_id: str = Field(..., description="UUID")
    score: float = Field(..., description="0-100")
    passed: bool = Field(..., description="Đã đạt yêu cầu pass hay chưa")
    total_questions: int = Field(..., description="Tổng số câu hỏi")
    correct_answers: int = Field(..., description="Số câu trả lời đúng")
    time_spent_minutes: int = Field(..., description="Thời gian làm bài (phút)")
    attempt_number: int = Field(..., description="Lần thử thứ mấy")
    submitted_at: datetime
    message: str


class QuestionResult(BaseModel):
    question_id: str = Field(..., description="UUID")
    question_content: str
    student_answer: str
    correct_answer: str
    is_correct: bool
    is_mandatory: bool
    score: float
    explanation: str
    related_lesson_link: Optional[str] = None


class QuizResultsResponse(BaseModel):
    attempt_id: str = Field(..., description="UUID")
    quiz_id: str = Field(..., description="UUID")
    total_score: float = Field(..., description="0-100")
    status: str = Field(..., description="Pass|Fail")
    pass_threshold: float
    results: List[QuestionResult]
    mandatory_passed: bool
    can_retake: bool


class RetakeQuestion(BaseModel):
    id: str = Field(..., description="UUID of new question")
    content: str
    options: List[str]


class QuizRetakeResponse(BaseModel):
    new_attempt_id: str = Field(..., description="UUID")
    quiz_id: str = Field(..., description="UUID")
    message: str
    questions: List[RetakeQuestion]


class QuestionCreate(BaseModel):
    type: str = Field(..., description="multiple_choice|fill_in_blank|true_false")
    question_text: str
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: Optional[str] = None
    points: int = Field(..., ge=1)
    is_mandatory: bool = False
    order: int


class QuizCreateRequest(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    time_limit: int = Field(..., ge=1, le=180)
    pass_threshold: int = Field(70, ge=0, le=100)
    max_attempts: Optional[int] = Field(None, ge=1)
    deadline: Optional[datetime] = None
    is_draft: bool = False
    questions: List[QuestionCreate] = Field(..., min_items=1, max_items=50)


class QuizCreateResponse(BaseModel):
    quiz_id: str = Field(..., description="UUID")
    lesson_id: str = Field(..., description="UUID")
    title: str
    description: Optional[str] = None
    time_limit: int
    pass_threshold: int
    max_attempts: Optional[int] = None
    deadline: Optional[datetime] = None
    is_draft: bool
    question_count: int
    total_points: int
    mandatory_count: int
    created_at: datetime
    preview_url: str
    message: str


class QuestionUpdate(BaseModel):
    question_id: Optional[str] = Field(None, description="UUID, null if new")
    type: str = Field(..., description="multiple_choice|fill_in_blank|true_false")
    question_text: str
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: Optional[str] = None
    points: int
    is_mandatory: bool
    order: int
    action: str = Field(..., description="add|update|delete")


class QuizUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    time_limit: Optional[int] = None
    pass_threshold: Optional[int] = None
    max_attempts: Optional[int] = None
    deadline: Optional[datetime] = None
    is_draft: Optional[bool] = None
    questions: Optional[List[QuestionUpdate]] = None


class QuizUpdateResponse(BaseModel):
    quiz_id: str = Field(..., description="UUID")
    title: str
    question_count: int
    total_points: int
    has_attempts: bool
    attempts_count: int
    warning: Optional[str] = None
    updated_at: datetime
    message: str


class QuizDeleteResponse(BaseModel):
    quiz_id: str = Field(..., description="UUID")
    message: str


class SourceInfo(BaseModel):
    lesson_id: Optional[str] = None
    course_id: Optional[str] = None
    topic_prompt: Optional[str] = None


class Exercise(BaseModel):
    id: str = Field(..., description="UUID")
    type: str = Field(..., description="theory|coding|problem-solving")
    question: str
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: str
    difficulty: str = Field(..., description="Easy|Medium|Hard")
    related_skill: str
    points: int


class PracticeExercisesGenerateRequest(BaseModel):
    lesson_id: Optional[str] = None
    course_id: Optional[str] = None
    topic_prompt: Optional[str] = None
    difficulty: str = Field("medium", description="easy|medium|hard")
    question_count: int = Field(5, ge=1, le=20)
    practice_type: str = Field("multiple_choice", description="multiple_choice|short_answer|mixed")
    focus_skills: Optional[List[str]] = None


class PracticeExercisesGenerateResponse(BaseModel):
    practice_id: str = Field(..., description="UUID")
    source: SourceInfo
    difficulty: str
    exercises: List[Exercise]
    total_questions: int
    estimated_time: int = Field(..., description="Minutes")
    created_at: datetime
    message: str


class QuizListItem(BaseModel):
    quiz_id: str = Field(..., description="UUID")
    title: str
    description: Optional[str] = None
    lesson_id: str = Field(..., description="UUID")
    lesson_title: str
    course_id: str = Field(..., description="UUID")
    course_title: str
    class_id: Optional[str] = None
    class_name: Optional[str] = None
    status: str = Field(..., description="active|draft|archived")
    question_count: int
    time_limit: int
    pass_threshold: int
    total_students: int
    completed_count: int
    pass_count: int
    pass_rate: float = Field(..., description="0-100")
    average_score: float = Field(..., description="0-100")
    created_at: datetime
    updated_at: datetime


class QuizListResponse(BaseModel):
    data: List[QuizListItem]
    total: int
    skip: int
    limit: int
    has_next: bool


class ScoreDistribution(BaseModel):
    range: str = Field(..., description="0-10, 11-20, etc")
    count: int
    percentage: float = Field(..., description="0-100")


class StudentRank(BaseModel):
    rank: int
    user_id: str = Field(..., description="UUID")
    full_name: str
    avatar: Optional[str] = None
    score: float = Field(..., description="0-100")
    time_spent: int = Field(..., description="Minutes")
    attempt_count: int
    status: str = Field(..., description="pass|fail")
    completed_at: datetime


class DifficultQuestion(BaseModel):
    question_id: str = Field(..., description="UUID")
    question_text: str
    correct_rate: float = Field(..., description="0-100")
    total_answers: int


class ClassResultStatistics(BaseModel):
    total_students: int
    completed_count: int
    completion_rate: float = Field(..., description="0-100")
    pass_count: int
    fail_count: int
    pass_rate: float = Field(..., description="0-100")
    average_score: float = Field(..., description="0-100")
    median_score: float = Field(..., description="0-100")
    highest_score: float = Field(..., description="0-100")
    lowest_score: float = Field(..., description="0-100")
    average_time: int = Field(..., description="Minutes")


class QuizClassResultsResponse(BaseModel):
    quiz_id: str = Field(..., description="UUID")
    quiz_title: str
    class_id: str = Field(..., description="UUID")
    class_name: str
    statistics: ClassResultStatistics
    score_distribution: List[ScoreDistribution]
    student_ranking: List[StudentRank]
    difficult_questions: List[DifficultQuestion]
# - QuizListResponse (GET /api/v1/quizzes)
# - QuizClassResultsResponse (GET /api/v1/quizzes/{id}/class-results)
