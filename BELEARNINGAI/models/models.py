"""
Models MongoDB sử dụng Beanie ODM
Tuân thủ: CHUCNANG.md, API_SCHEMA.md
Naming: snake_case theo Python convention
"""

from datetime import datetime
from typing import Optional, List
from beanie import Document, Indexed
from pydantic import Field, EmailStr, BaseModel
import uuid


def generate_uuid() -> str:
    """Tạo UUID mới cho document"""
    return str(uuid.uuid4())


# ============================================================================
# PROGRESS TRACKING MODELS
# ============================================================================

class LessonProgressItem(BaseModel):
    """
    Chi tiết tiến độ của một lesson
    Sử dụng trong Progress.lessons_progress array
    Tuân thủ: dashboard_service.py logic (parse by completion_date)
    """
    lesson_id: str = Field(..., description="UUID của lesson")
    lesson_title: str = Field(..., description="Tên lesson")
    status: str = Field(..., description="completed|in-progress|not-started")
    completion_date: Optional[datetime] = Field(None, description="Ngày hoàn thành (null nếu chưa xong)")
    time_spent_minutes: int = Field(default=0, description="Thời gian học lesson này (phút)")
    video_progress_seconds: int = Field(default=0, description="Tiến độ xem video (giây)")


# ============================================================================
# EMBEDDED MODELS FOR COURSE (Lesson & Module nested in Course)
# ============================================================================

class EmbeddedLesson(BaseModel):
    """Lesson embedded trong Module"""
    id: str = Field(default_factory=generate_uuid)
    title: str
    description: Optional[str] = None
    order: int
    content: str = ""
    content_type: str = "text"  # text|video|audio|code|mixed
    duration_minutes: int = 0
    video_url: Optional[str] = None
    audio_url: Optional[str] = None  # URL audio file (mp3, wav, ogg)
    resources: List[dict] = Field(default_factory=list)
    learning_objectives: List[str] = Field(default_factory=list, description="Mục tiêu học tập của lesson")
    quiz_id: Optional[str] = None
    is_published: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class EmbeddedModule(BaseModel):
    """Module embedded trong Course"""
    id: str = Field(default_factory=generate_uuid)
    title: str
    description: str
    order: int
    difficulty: str = "Basic"
    estimated_hours: float = 0
    learning_outcomes: List[dict] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list, description="Module IDs tiên quyết")
    resources: List[dict] = Field(default_factory=list, description="Tài liệu module-level")
    lessons: List[EmbeddedLesson] = Field(default_factory=list)
    total_lessons: int = 0
    total_duration_minutes: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# USER MODEL (Section 2.1)
# ============================================================================

class User(Document):
    """
    Model người dùng cho hệ thống
    Collection: users
    Tuân thủ: API_SCHEMA.md (1.1-1.5), user.py schema
    """
    id: str = Field(default_factory=generate_uuid, alias="_id")
    full_name: str = Field(..., min_length=2, max_length=100, description="Tên đầy đủ (tối thiểu 2 từ)")
    email: EmailStr = Field(..., description="Email unique trong hệ thống")
    hashed_password: str = Field(..., description="Mật khẩu đã hash")
    role: str = Field(default="student", description="student|instructor|admin")
    status: str = Field(default="active", description="active|inactive|suspended")
    
    # Thông tin tùy chọn - theo UserProfileResponse schema
    avatar_url: Optional[str] = Field(None, description="URL ảnh đại diện, có thể null")
    bio: Optional[str] = Field(None, max_length=500, description="Mô tả bản thân (tối đa 500 ký tự), có thể null")
    contact_info: Optional[str] = Field(None, max_length=200, description="Thông tin liên hệ, có thể null")
    learning_preferences: List[str] = Field(
        default_factory=list, 
        description="Danh sách sở thích học tập: Programming, Math, Business, Languages..."
    )
    
    # Authentication tracking - theo API schema
    last_login_at: Optional[datetime] = Field(None, description="Lần đăng nhập cuối")
    email_verified: bool = Field(default=False, description="Email đã xác thực chưa")
    phone_verified: bool = Field(default=False, description="Số điện thoại đã xác thực chưa")
    
    # Admin fields - cho chức năng admin tạo user
    created_by: Optional[str] = Field(None, description="Admin ID who created this user")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Ngày tạo tài khoản")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Lần cập nhật cuối")
    
    class Settings:
        name = "users"
        indexes = [
            [("email", 1)],  # Unique email
            "role",
            "status",
            "created_at",
            "last_login_at"
        ]


# ============================================================================
# REFRESH TOKEN MODEL
# ============================================================================

class RefreshToken(Document):
    """
    Lưu trữ refresh tokens để quản lý phiên đăng nhập
    Collection: refresh_tokens
    """
    id: str = Field(default_factory=generate_uuid, alias="_id")
    user_id: str
    token: str = Field(..., unique=True)
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "refresh_tokens"
        indexes = [
            "user_id",
            "token",
            "expires_at"
        ]


# ============================================================================
# LESSON MODEL  
# ============================================================================

class Lesson(Document):
    """
    Bài học trong module
    Collection: lessons
    Tuân thủ: LessonSummary schema
    """
    id: str = Field(default_factory=generate_uuid, alias="_id")
    module_id: str = Field(..., description="UUID module chứa lesson này")
    course_id: str = Field(..., description="UUID khóa học (denormalized)")
    
    title: str = Field(..., description="Tên lesson")
    description: Optional[str] = Field(None, description="Mô tả lesson")
    order: int = Field(..., description="Thứ tự lesson trong module")
    
    # Nội dung - theo LessonSummary schema
    content: str = Field(default="", description="Nội dung HTML hoặc markdown")
    content_type: str = Field(default="text", description="Loại nội dung: text|video|audio|code|mixed")
    duration_minutes: int = Field(default=0, description="Thời lượng lesson (phút)")
    video_url: Optional[str] = Field(None, description="URL video bài học")
    audio_url: Optional[str] = Field(None, description="URL audio bài giảng (mp3, wav, ogg)")
    
    # Learning objectives - ADDED theo API_SCHEMA.md Section 4.2
    learning_objectives: List[str] = Field(default_factory=list, description="Mục tiêu học tập cụ thể của bài học")
    
    # Resources theo schema structure
    resources: List[dict] = Field(default_factory=list, description="Tài liệu kèm theo")
    # Resource structure: {
    #   "id": "uuid",
    #   "title": "Resource name",
    #   "type": "pdf|slide|code|video|audio|link", 
    #   "url": "download/view link",
    #   "size_mb": float,
    #   "audio_format": "mp3|wav|ogg" (optional, for audio type),
    #   "duration_seconds": int (optional, for video/audio),
    #   "description": "optional"
    # }
    
    # Quiz liên kết
    quiz_id: Optional[str] = Field(None, description="Quiz kèm theo lesson này")
    
    # Trạng thái
    is_published: bool = Field(default=True, description="Đã xuất bản chưa")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "lessons"
        indexes = [
            "module_id",
            "course_id",
            "quiz_id",
            [("module_id", 1), ("order", 1)],
            [("course_id", 1), ("is_published", 1)]
        ]


class Module(Document):
    """
    Module trong khóa học
    Collection: modules
    Tuân thủ: ModuleSummary schema
    """
    id: str = Field(default_factory=generate_uuid, alias="_id")
    course_id: str = Field(..., description="UUID khóa học chứa module này")
    
    title: str = Field(..., description="Tên module")
    description: str = Field(..., description="Mô tả module")
    order: int = Field(..., description="Thứ tự module trong khóa học")
    difficulty: str = Field(default="Basic", description="Độ khó: Basic|Intermediate|Advanced")
    estimated_hours: float = Field(default=0, description="Thời gian học ước tính (giờ)")
    
    # Learning outcomes cho module - theo LearningOutcome schema
    learning_outcomes: List[dict] = Field(default_factory=list, description="Mục tiêu học tập của module")
    # Learning outcome structure từ learning.py LearningOutcome: {
    #   "id": "uuid",
    #   "outcome": "Mô tả mục tiêu cụ thể",
    #   "skill_tag": "python-functions", 
    #   "is_mandatory": boolean
    # }
    
    # Module statistics
    total_lessons: int = Field(default=0, description="Số lượng lessons trong module")
    total_duration_minutes: int = Field(default=0, description="Tổng thời lượng của module (phút)")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "modules"
        indexes = [
            "course_id",
            [("course_id", 1), ("order", 1)]
        ]


class Course(Document):
    """
    Model khóa học
    Collection: courses
    Tuân thủ: API_SCHEMA.md (2.3), course.py schema
    """
    id: str = Field(default_factory=generate_uuid, alias="_id")
    title: str = Field(..., description="Tên khóa học")
    description: str = Field(..., description="Mô tả chi tiết đầy đủ khóa học")
    category: str = Field(..., description="Danh mục: Programming|Math|Business|Languages")
    level: str = Field(..., description="Cấp độ: Beginner|Intermediate|Advanced")
    
    # Metadata theo CourseDetailResponse
    thumbnail_url: Optional[str] = Field(None, description="URL ảnh đại diện")
    preview_video_url: Optional[str] = Field(None, description="URL video preview")
    language: str = Field(default="vi", description="Ngôn ngữ: vi|en")
    status: str = Field(default="draft", description="Trạng thái: draft|published|archived")
    
    # Owner & Instructor info - theo OwnerInfo schema
    owner_id: str = Field(..., description="User ID của người tạo")
    owner_type: str = Field(default="admin", description="admin|instructor|student")
    instructor_id: Optional[str] = Field(None, description="Instructor assigned to teach this course")
    instructor_name: Optional[str] = Field(None, description="Tên giảng viên (denormalized for performance)")
    instructor_avatar: Optional[str] = Field(None, description="Avatar giảng viên (denormalized for performance)")
    instructor_bio: Optional[str] = Field(None, description="Bio giảng viên (denormalized for performance)")
    
    # Nội dung học tập - theo LearningOutcome schema từ course.py
    learning_outcomes: List[dict] = Field(default_factory=list, description="Mục tiêu học tập")
    # Learning outcome structure từ course.py: {
    #   "id": "uuid",
    #   "description": "Mục tiêu cụ thể, đo lường được",
    #   "skill_tag": "Kỹ năng liên quan"
    # }
    
    prerequisites: List[str] = Field(default_factory=list, description="Yêu cầu kiến thức đầu vào")
    
    # Nội dung khóa học - embedded modules và lessons
    modules: List[EmbeddedModule] = Field(default_factory=list, description="Danh sách modules trong course")
    
    # Thống kê - theo CourseStatistics schema
    total_duration_minutes: int = Field(default=0, description="Tổng thời lượng khóa học (phút)")
    total_modules: int = Field(default=0, description="Tổng số modules")
    total_lessons: int = Field(default=0, description="Tổng số lessons")
    enrollment_count: int = Field(default=0, description="Số học viên đã đăng ký")
    avg_rating: Optional[float] = Field(None, description="Điểm đánh giá trung bình 0-5")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Ngày tạo")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Ngày cập nhật cuối")
    
    class Settings:
        name = "courses"
        indexes = [
            "owner_id",
            "instructor_id", 
            "category",
            "level",
            "status",
            "created_at",
            [("category", 1), ("level", 1)],
            [("status", 1), ("created_at", -1)],
            [("category", 1), ("status", 1)],
            [("instructor_id", 1), ("status", 1)]
        ]


# ============================================================================
# ENROLLMENT MODEL (Section 2.3.4-2.3.8)
# ============================================================================

class Enrollment(Document):
    """
    Model đăng ký khóa học
    Collection: enrollments
    Tuân thủ: EnrollmentCreateResponse, EnrollmentListItem, EnrollmentDetailResponse schemas
    """
    id: str = Field(default_factory=generate_uuid, alias="_id")
    user_id: str = Field(..., description="UUID student")
    course_id: str = Field(..., description="UUID khóa học")
    
    # Trạng thái - theo schemas
    status: str = Field(default="active", description="active|completed|cancelled")
    progress_percent: float = Field(default=0.0, description="Tiến độ 0-100")
    # Alias for API compatibility - completion_rate same as progress_percent
    completion_rate: float = Field(default=0.0, description="Alias của progress_percent cho API compatibility")
    
    # Thống kê - theo EnrollmentDetailResponse
    completed_lessons: List[str] = Field(default_factory=list, description="Danh sách UUID lessons đã hoàn thành")
    completed_modules: List[str] = Field(default_factory=list, description="Danh sách UUID modules đã hoàn thành")
    avg_quiz_score: Optional[float] = Field(None, description="Điểm quiz trung bình 0-100")
    total_time_spent_minutes: int = Field(default=0, description="Tổng thời gian học (phút)")
    
    # Timestamps
    enrolled_at: datetime = Field(default_factory=datetime.utcnow, description="Thời gian đăng ký")
    last_accessed_at: Optional[datetime] = Field(None, description="Lần truy cập cuối")
    completed_at: Optional[datetime] = Field(None, description="Thời gian hoàn thành khóa học")
    
    class Settings:
        name = "enrollments"
        indexes = [
            "user_id",
            "course_id",
            "status",
            "enrolled_at",
            "last_accessed_at",
            [("user_id", 1), ("course_id", 1)],  # Compound index
            [("user_id", 1), ("status", 1)],
            [("course_id", 1), ("status", 1)]
        ]


# ============================================================================
# ASSESSMENT MODEL (Section 2.2)
# ============================================================================

class AssessmentSession(Document):
    """
    Phiên đánh giá năng lực AI
    Collection: assessment_sessions
    Tuân thủ: API_SCHEMA.md (2.2.1-2.2.4), assessment.py schema
    """
    id: str = Field(default_factory=generate_uuid, alias="_id")
    user_id: str = Field(..., description="UUID user thực hiện đánh giá")
    
    # Cấu hình đánh giá - theo AssessmentGenerateRequest
    category: str = Field(..., description="Lĩnh vực: Programming, Math, Business, Languages...")
    subject: str = Field(..., description="Chủ đề: Python, JavaScript, Algebra, English...")
    level: str = Field(..., description="Mức độ: Beginner|Intermediate|Advanced")
    focus_areas: List[str] = Field(default_factory=list, description="Các chủ đề con cụ thể")
    total_questions: int = Field(..., description="Số lượng câu hỏi được sinh")
    time_limit_minutes: int = Field(..., description="Thời gian làm bài (phút)")
    
    # Câu hỏi - theo AssessmentQuestion schema
    questions: List[dict] = Field(default_factory=list, description="Danh sách câu hỏi")
    # Question structure từ assessment.py AssessmentQuestion: {
    #   "question_id": "uuid",
    #   "question_text": "đề bài câu hỏi",
    #   "question_type": "multiple_choice|fill_in_blank|drag_and_drop",
    #   "difficulty": "easy|medium|hard",
    #   "skill_tag": "python-syntax, algorithm-complexity...",
    #   "points": int,  # easy=1, medium=2, hard=3
    #   "options": ["A", "B", "C", "D"] or null,
    #   "correct_answer_hint": "gợi ý ngắn về đáp án"
    # }
    
    # Trạng thái
    status: str = Field(default="pending", description="pending|in_progress|submitted|evaluated")
    
    # Kết quả (sau khi submit) - theo AssessmentAnswer schema
    answers: List[dict] = Field(default_factory=list, description="Danh sách câu trả lời")
    # Answer structure từ assessment.py AssessmentAnswer: {
    #   "question_id": "uuid",
    #   "answer_content": "đáp án của học viên",
    #   "selected_option": int or null,  # 0,1,2,3 cho multiple_choice
    #   "time_taken_seconds": int
    # }
    
    # Phân tích kết quả - theo AssessmentResultsResponse
    overall_score: Optional[float] = Field(None, description="0-100, điểm tổng thể")
    proficiency_level: Optional[str] = Field(None, description="Beginner|Intermediate|Advanced dựa trên kết quả thực tế")
    
    # Phân tích chi tiết - theo SkillAnalysis schema
    skill_analysis: Optional[dict] = Field(None, description="Phân tích từng kỹ năng")
    # Skill analysis structure từ assessment.py SkillAnalysis: {
    #   "skill_tag": "python-syntax",
    #   "questions_count": 5,
    #   "correct_count": 3,
    #   "proficiency_percentage": 60.0,
    #   "strength_level": "Strong|Average|Weak",
    #   "detailed_feedback": "Nhận xét chi tiết về skill này"
    # }
    
    # Lỗ hổng kiến thức - theo KnowledgeGap schema
    knowledge_gaps: List[dict] = Field(default_factory=list, description="Các lỗ hổng kiến thức được phát hiện")
    # Knowledge gap structure từ assessment.py KnowledgeGap: {
    #   "gap_area": "Lĩnh vực thiếu kiến thức",
    #   "description": "Mô tả chi tiết lỗ hổng",
    #   "importance": "High|Medium|Low",
    #   "suggested_action": "Hành động được đề xuất"
    # }
    
    # Phân tích thời gian - theo TimeAnalysis schema
    time_analysis: Optional[dict] = Field(None, description="Phân tích thời gian làm bài")
    # Time analysis structure từ assessment.py TimeAnalysis: {
    #   "total_time_seconds": int,
    #   "average_time_per_question": float,
    #   "fastest_question_time": int,
    #   "slowest_question_time": int
    # }
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Thời gian tạo assessment")
    expires_at: datetime = Field(..., description="Hết hạn sau 60 phút kể từ khi tạo")
    submitted_at: Optional[datetime] = Field(None, description="Thời gian nộp bài")
    evaluated_at: Optional[datetime] = Field(None, description="Thời gian AI chấm xong và phân tích")
    
    class Settings:
        name = "assessment_sessions"
        indexes = [
            "user_id",
            "status",
            "category",
            "subject", 
            "level",
            "created_at",
            "expires_at",
            [("user_id", 1), ("created_at", -1)]
        ]


# ============================================================================
# QUIZ MODEL (Section 2.4.3-2.4.7)
# ============================================================================

class Quiz(Document):
    """
    Model quiz/bài kiểm tra
    Collection: quizzes
    Tuân thủ: API_SCHEMA.md, quiz.py schema
    """
    id: str = Field(default_factory=generate_uuid, alias="_id")
    lesson_id: str = Field(..., description="UUID lesson chứa quiz này")
    course_id: str = Field(..., description="UUID khóa học (denormalized)")
    module_id: Optional[str] = Field(None, description="UUID module (for module-level assessments)")
    
    title: str = Field(..., description="Tên quiz")
    description: str = Field(..., description="Mô tả quiz")
    quiz_type: Optional[str] = Field(None, description="review|practice|final_check (for module assessments)")
    
    # Cấu hình - theo QuizDetailResponse và QuizCreateRequest
    time_limit_minutes: Optional[int] = Field(None, description="Thời gian làm bài (phút), null = không giới hạn")
    passing_score: float = Field(default=70.0, description="Điểm đạt (%), 0-100")
    max_attempts: int = Field(default=3, description="Số lần làm tối đa")
    deadline: Optional[datetime] = Field(None, description="Hạn chót nộp bài")
    is_draft: bool = Field(default=False, description="Có phải bản nháp không")
    
    # Câu hỏi - theo QuestionCreate schema từ quiz.py
    questions: List[dict] = Field(default_factory=list, description="Danh sách câu hỏi")
    # Question structure từ quiz.py QuestionCreate: {
    #   "id": "uuid",
    #   "type": "multiple_choice|fill_in_blank|true_false",
    #   "question_text": "nội dung câu hỏi", 
    #   "options": ["A", "B", "C", "D"] or null,  # null nếu không phải multiple_choice
    #   "correct_answer": "đáp án đúng",
    #   "explanation": "giải thích tại sao đáp án này đúng" or null,
    #   "points": int,  # điểm cho câu hỏi này (>=1)
    #   "is_mandatory": boolean,  # câu bắt buộc phải đúng
    #   "order": int  # thứ tự câu hỏi trong quiz
    # }
    
    # Thống kê quiz - cho QuizDetailResponse
    question_count: int = Field(default=0, description="Tổng số câu hỏi")
    total_points: int = Field(default=0, description="Tổng điểm của quiz")
    mandatory_question_count: int = Field(default=0, description="Số câu bắt buộc")
    
    # Metadata
    created_by: str = Field(..., description="User ID của người tạo quiz")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "quizzes"
        indexes = [
            "lesson_id",
            "course_id",
            "module_id",  # For module-level assessments
            "created_by",
            "is_draft",
            "quiz_type",  # For filtering by assessment type
            "created_at",
            [("course_id", 1), ("is_draft", 1)],
            [("lesson_id", 1), ("is_draft", 1)],
            [("module_id", 1), ("quiz_type", 1)]  # For module assessments
        ]


class QuizAttempt(Document):
    """
    Lần thử làm quiz
    Collection: quiz_attempts
    Tuân thủ: QuizAttemptRequest, QuizResultsResponse schemas
    """
    id: str = Field(default_factory=generate_uuid, alias="_id")
    quiz_id: str = Field(..., description="UUID quiz được làm")
    user_id: str = Field(..., description="UUID user làm quiz")
    
    # Kết quả - lưu trữ theo QuestionResult schema từ quiz.py
    answers: List[dict] = Field(default_factory=list, description="Danh sách câu trả lời")
    # Answer structure từ quiz.py QuestionResult: {
    #   "question_id": "uuid",
    #   "question_content": "nội dung câu hỏi",
    #   "student_answer": "đáp án học viên chọn",
    #   "correct_answer": "đáp án đúng",
    #   "is_correct": boolean,
    #   "is_mandatory": boolean,
    #   "score": float,  # điểm cho câu này
    #   "explanation": "giải thích đáp án",
    #   "related_lesson_link": "URL lesson liên quan" or null
    # }
    
    score: float = Field(default=0.0, description="Điểm tổng (0-100)")
    status: str = Field(default="Pass", description="Pass|Fail")
    passed: bool = Field(default=False, description="Có đạt điểm đậu không")
    attempt_number: int = Field(default=1, description="Lần thứ mấy làm quiz này")
    
    # Chi tiết kết quả - theo QuizResultsResponse
    correct_answers: int = Field(default=0, description="Số câu trả lời đúng")
    total_questions: int = Field(default=0, description="Tổng số câu hỏi")
    mandatory_correct: int = Field(default=0, description="Số câu bắt buộc đúng")
    mandatory_total: int = Field(default=0, description="Tổng số câu bắt buộc")
    mandatory_passed: bool = Field(default=True, description="Có đạt yêu cầu câu bắt buộc không")
    can_retake: bool = Field(default=True, description="Có thể làm lại không")
    
    # Thời gian
    started_at: datetime = Field(default_factory=datetime.utcnow, description="Thời gian bắt đầu")
    submitted_at: Optional[datetime] = Field(None, description="Thời gian nộp bài")
    time_spent_seconds: int = Field(default=0, description="Thời gian làm bài (giây)")
    
    class Settings:
        name = "quiz_attempts"
        indexes = [
            "quiz_id",
            "user_id",
            "started_at",
            "submitted_at",
            "status",
            [("user_id", 1), ("quiz_id", 1)],
            [("user_id", 1), ("quiz_id", 1), ("attempt_number", 1)],
            [("quiz_id", 1), ("submitted_at", -1)]
        ]


# ============================================================================
# PROGRESS MODEL (Section 2.4.9)
# ============================================================================

class Progress(Document):
    """
    Model theo dõi tiến độ học tập
    Collection: progress
    Tuân thủ: ProgressCourseResponse, LessonProgress schemas
    """
    id: str = Field(default_factory=generate_uuid, alias="_id")
    user_id: str = Field(..., description="UUID user")
    course_id: str = Field(..., description="UUID khóa học")
    enrollment_id: str = Field(..., description="UUID enrollment")
    
    # Tiến độ tổng quan - theo ProgressCourseResponse
    overall_progress_percent: float = Field(default=0.0, description="Tiến độ tổng thể (0-100)")
    completed_lessons_count: int = Field(default=0, description="Số lessons đã hoàn thành")
    total_lessons_count: int = Field(default=0, description="Tổng số lessons trong khóa học")
    
    # Chi tiết từng lesson - FIXED: Sử dụng LessonProgressItem schema
    lessons_progress: List[LessonProgressItem] = Field(
        default_factory=list, 
        description="Tiến độ chi tiết từng lesson với validated structure"
    )
    
    # Thống kê học tập - theo ProgressCourseResponse
    total_time_spent_minutes: int = Field(default=0, description="Tổng thời gian học (phút)")
    estimated_hours_remaining: float = Field(default=0.0, description="Thời gian ước tính còn lại (giờ)")
    study_streak_days: int = Field(default=0, description="Số ngày học liên tiếp")
    avg_quiz_score: float = Field(default=0.0, description="Điểm quiz trung bình (0-100)")
    last_accessed_at: Optional[datetime] = Field(None, description="Lần truy cập cuối")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "progress"
        indexes = [
            "user_id",
            "course_id",
            "enrollment_id",
            [("user_id", 1), ("course_id", 1)]
        ]


# ============================================================================
# CHAT MODEL (Section 2.6)
# ============================================================================

class Conversation(Document):
    """
    Model conversation chat với AI
    Collection: conversations
    Tuân thủ: ChatMessageResponse, ConversationDetailResponse, Message schemas
    """
    id: str = Field(default_factory=generate_uuid, alias="_id")
    user_id: str = Field(..., description="UUID user")
    course_id: str = Field(..., description="UUID khóa học")
    
    # Thông tin conversation - theo ConversationDetailResponse
    title: str = Field(default="New Conversation", description="Tiêu đề conversation")
    summary: str = Field(default="", description="AI summary of topic")
    course_title: str = Field(default="", description="Tên khóa học (denormalized)")
    
    # Messages - theo Message schema structure
    messages: List[dict] = Field(default_factory=list, description="Danh sách tin nhắn")
    # Message structure theo Message schema: {
    #   "id": "uuid",
    #   "role": "user|assistant",
    #   "content": "message text",
    #   "created_at": datetime
    # }
    
    # Conversation metadata - theo ConversationDetailResponse
    total_messages: int = Field(default=0, description="Tổng số tin nhắn")
    last_message_at: datetime = Field(default_factory=datetime.utcnow, description="Thời gian tin nhắn cuối")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Lần cập nhật cuối")
    
    class Settings:
        name = "conversations"
        indexes = [
            "user_id",
            "course_id",
            "created_at",
            "last_message_at",
            [("user_id", 1), ("course_id", 1)],
            [("user_id", 1), ("last_message_at", -1)]
        ]


# ============================================================================
# CLASS MODEL (Section 3.1-3.2)
# ============================================================================

class Class(Document):
    """
    Model lớp học do giảng viên tạo
    Collection: classes
    Tuân thủ: ClassCreateRequest, ClassCreateResponse, ClassDetailResponse schemas
    """
    id: str = Field(default_factory=generate_uuid, alias="_id")
    name: str = Field(..., description="Tên lớp học")
    description: str = Field(..., description="Mô tả lớp học")
    
    # Liên kết
    course_id: str = Field(..., description="UUID khóa học")
    instructor_id: str = Field(..., description="UUID giảng viên")
    
    # Mã mời - theo ClassCreateResponse
    invite_code: str = Field(default_factory=lambda: str(uuid.uuid4())[:8].upper(), description="Mã mời 6-8 ký tự")
    
    # Cấu hình - theo ClassCreateRequest và ClassDetailResponse
    max_students: int = Field(..., description="Số học viên tối đa")
    start_date: datetime = Field(..., description="Ngày bắt đầu")
    end_date: datetime = Field(..., description="Ngày kết thúc")
    status: str = Field(default="preparing", description="preparing|active|completed")
    
    # Danh sách học viên
    student_ids: List[str] = Field(default_factory=list, description="Danh sách UUID học viên")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "classes"
        indexes = [
            "instructor_id",
            "course_id",
            "invite_code",
            "status"
        ]


# ============================================================================
# RECOMMENDATION MODEL (Section 2.2.4, 2.7.4)
# ============================================================================

class Recommendation(Document):
    """
    Đề xuất khóa học cho học viên
    Collection: recommendations
    Tuân thủ: AssessmentRecommendationResponse, RecommendationResponse schemas
    """
    id: str = Field(default_factory=generate_uuid, alias="_id")
    user_id: str = Field(..., description="UUID user")
    
    # Nguồn gốc đề xuất
    source: str = Field(..., description="assessment|learning_history|ai_suggestion")
    assessment_session_id: Optional[str] = Field(None, description="UUID assessment session nếu từ đánh giá")
    
    # User proficiency level - theo AssessmentRecommendationResponse
    user_proficiency_level: Optional[str] = Field(None, description="Beginner|Intermediate|Advanced")
    
    # Danh sách khóa học đề xuất - theo RecommendedCourseItem schema
    recommended_courses: List[dict] = Field(default_factory=list, description="Danh sách khóa học đề xuất")
    # Recommended course structure: {
    #   "course_id": "uuid",
    #   "title": "tên khóa học",
    #   "description": "mô tả",
    #   "category": "danh mục",
    #   "level": "cấp độ",
    #   "thumbnail_url": "url or null",
    #   "priority_rank": int,  # 1=highest priority
    #   "relevance_score": float,  # 0-100
    #   "reason": "lý do đề xuất",
    #   "addresses_gaps": ["gap1", "gap2"],  # các lỗ hổng kiến thức được giải quyết
    #   "estimated_completion_days": int
    # }
    
    # Lộ trình học tập - theo LearningStep schema
    suggested_learning_order: List[dict] = Field(default_factory=list, description="Thứ tự học tập được đề xuất")
    # Learning step structure: {
    #   "step": int,
    #   "course_id": "uuid", 
    #   "focus_modules": ["module1", "module2"],
    #   "why_this_order": "giải thích"
    # }
    
    # Practice exercises - theo PracticeExerciseItem schema
    practice_exercises: List[dict] = Field(default_factory=list, description="Bài tập luyện tập")
    # Practice exercise structure: {
    #   "skill_tag": "kỹ năng",
    #   "exercise_type": "coding|quiz|project|reading",
    #   "description": "mô tả",
    #   "difficulty": "easy|medium|hard",
    #   "estimated_time_hours": float
    # }
    
    # AI feedback
    ai_personalized_advice: str = Field(default="", description="Lời khuyên cá nhân hóa từ AI")
    total_estimated_hours: float = Field(default=0.0, description="Tổng thời gian ước tính để hoàn thành")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Thời gian hết hạn đề xuất")
    
    class Settings:
        name = "recommendations"
        indexes = [
            "user_id",
            "assessment_session_id",
            "created_at"
        ]


# ============================================================================
# DOCUMENT ALIASES - for database.py imports
# ============================================================================

# Alias các model để match với import trong database.py
UserDocument = User
RefreshTokenDocument = RefreshToken
CourseDocument = Course
ModuleDocument = Module
LessonDocument = Lesson
EnrollmentDocument = Enrollment
AssessmentDocument = AssessmentSession  # AssessmentSession được alias thành AssessmentDocument
QuizDocument = Quiz
QuizAttemptDocument = QuizAttempt
ProgressDocument = Progress
ChatDocument = Conversation  # Conversation được alias thành ChatDocument
ClassDocument = Class
RecommendationDocument = Recommendation

# Document cho Admin reset password chức năng


class PasswordResetTokenDocument(Document):
    """Document cho Password Reset Token - Admin reset password chức năng 4.1.7"""
    id: str = Field(default_factory=generate_uuid, alias="_id")
    user_id: str
    token: str
    expires_at: datetime
    used: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "password_reset_tokens"
