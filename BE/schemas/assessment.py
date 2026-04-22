"""
Assessment Schemas
Định nghĩa request/response schemas cho assessment endpoints (2.2.1-2.2.4)
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import List, Optional
from enum import Enum


class LevelEnum(str, Enum):
    """Enum cho mức độ đánh giá"""
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class QuestionTypeEnum(str, Enum):
    """Enum cho loại câu hỏi"""
    MULTIPLE_CHOICE = "multiple_choice"
    FILL_IN_BLANK = "fill_in_blank"
    DRAG_AND_DROP = "drag_and_drop"


class DifficultyEnum(str, Enum):
    """Enum cho độ khó câu hỏi"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


# ===== GENERATE ASSESSMENT (2.2.1) =====

class AssessmentGenerateRequest(BaseModel):
    """Schema request để sinh bộ câu hỏi đánh giá - POST /api/v1/assessments/generate"""
    category: str = Field(..., description="Lĩnh vực: Programming, Math, Business, Languages...")
    subject: str = Field(..., description="Chủ đề: Python, JavaScript, Algebra, English...")
    level: LevelEnum = Field(..., description="Mức độ: Beginner|Intermediate|Advanced")
    focus_areas: Optional[List[str]] = Field(default=None, description="Các chủ đề con cụ thể (tùy chọn)")


class AssessmentQuestion(BaseModel):
    """Schema cho một câu hỏi trong assessment"""
    question_id: str = Field(..., description="UUID câu hỏi")
    question_text: str = Field(..., description="Đề bài câu hỏi")
    question_type: QuestionTypeEnum
    difficulty: DifficultyEnum
    skill_tag: str = Field(..., description="Kỹ năng được kiểm tra (python-syntax, algorithm-complexity...)")
    points: int = Field(..., description="Điểm: easy=1, medium=2, hard=3")
    options: Optional[List[str]] = Field(None, description="Các lựa chọn (null nếu không phải multiple_choice)")
    correct_answer_hint: str = Field(..., description="Gợi ý ngắn về đáp án")


class AssessmentGenerateResponse(BaseModel):
    """Schema response sau khi sinh bộ câu hỏi - 201 Created"""
    session_id: str = Field(..., description="UUID phiên đánh giá")
    category: str
    subject: str
    level: str
    question_count: int = Field(..., description="Số lượng câu hỏi được sinh")
    time_limit_minutes: int = Field(..., description="Thời gian làm bài (phút)")
    questions: List[AssessmentQuestion]
    created_at: datetime
    expires_at: datetime = Field(..., description="Hết hạn sau 60 phút")
    message: str = Field(default="Bộ câu hỏi đánh giá đã được tạo thành công")


# ===== SUBMIT ASSESSMENT (2.2.2) =====

class AssessmentAnswer(BaseModel):
    """Schema cho một câu trả lời"""
    question_id: str = Field(..., description="UUID câu hỏi")
    answer_content: str = Field(..., description="Đáp án của học viên")
    selected_option: Optional[int] = Field(None, description="Chỉ số đáp án cho multiple_choice: 0,1,2,3")
    time_taken_seconds: int = Field(..., description="Thời gian làm câu này (giây)")


class AssessmentSubmitRequest(BaseModel):
    """Schema request để nộp bài đánh giá - POST /api/v1/assessments/{session_id}/submit"""
    answers: List[AssessmentAnswer] = Field(..., min_length=1)
    total_time_seconds: int = Field(..., description="Tổng thời gian làm bài")
    submitted_at: datetime = Field(..., description="Thời gian nộp bài")


class AssessmentSubmitResponse(BaseModel):
    """Schema response sau khi nộp bài - 200 OK"""
    session_id: str
    submitted_at: datetime
    total_questions: int
    time_taken_minutes: float
    status: str = Field(default="submitted", description="submitted - chờ chấm điểm")
    message: str = Field(default="Bài làm đã được nộp thành công. Kết quả sẽ có sau vài giây.")


# ===== GET RESULTS (2.2.3) =====

class ScoreBreakdownCategory(BaseModel):
    """Schema cho phân tích điểm theo từng mức độ"""
    total: int
    correct: int
    score_percentage: float


class ScoreBreakdown(BaseModel):
    """Schema cho phân tích chi tiết điểm số"""
    easy_questions: ScoreBreakdownCategory
    medium_questions: ScoreBreakdownCategory
    hard_questions: ScoreBreakdownCategory


class SkillAnalysis(BaseModel):
    """Schema cho phân tích kỹ năng"""
    skill_tag: str = Field(..., description="python-syntax, algorithm-complexity...")
    questions_count: int = Field(..., description="Số câu hỏi về skill này")
    correct_count: int = Field(..., description="Số câu trả lời đúng")
    proficiency_percentage: float = Field(..., description="0-100")
    strength_level: str = Field(..., description="Strong|Average|Weak")
    detailed_feedback: str = Field(..., description="Nhận xét chi tiết về skill này")


class KnowledgeGap(BaseModel):
    """Schema cho lỗ hổng kiến thức"""
    gap_area: str = Field(..., description="Lĩnh vực thiếu kiến thức")
    description: str = Field(..., description="Mô tả chi tiết lỗ hổng")
    importance: str = Field(..., description="High|Medium|Low")
    suggested_action: str = Field(..., description="Hành động được đề xuất")


class TimeAnalysis(BaseModel):
    """Schema cho phân tích thời gian"""
    total_time_seconds: int
    average_time_per_question: float
    fastest_question_time: int
    slowest_question_time: int


class AssessmentInfo(BaseModel):
    """Schema cho thông tin assessment"""
    category: str
    subject: str
    level: str
    completed_at: datetime


class AssessmentResultsResponse(BaseModel):
    """Schema response cho kết quả đánh giá - GET /api/v1/assessments/{session_id}/results"""
    session_id: str
    assessment_info: AssessmentInfo
    overall_score: float = Field(..., description="0-100, điểm tổng thể")
    proficiency_level: str = Field(..., description="Beginner|Intermediate|Advanced, trình độ thực tế")
    total_questions: int
    correct_answers: int
    score_breakdown: ScoreBreakdown
    skill_analysis: List[SkillAnalysis]
    knowledge_gaps: List[KnowledgeGap]
    time_analysis: TimeAnalysis
    ai_feedback: str = Field(..., description="Nhận xét tổng quan và chi tiết từ AI")
