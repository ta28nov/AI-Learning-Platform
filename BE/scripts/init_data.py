"""
init_data.py - Rebuilt seed pipeline (x4 profile, full reset)
==============================================================
- Seed quy mo lon, day du quan he va field quan trong theo models/schemas.
- Chay theo stage ro rang + deterministic randomness.
- Co validation integrity sau khi seed.
"""

import asyncio
import random
import sys
import os
import uuid
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple, Any, TypedDict

from faker import Faker
from passlib.context import CryptContext

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import get_settings
from app.database import init_database
from models.models import (
    User,
    RefreshToken,
    PasswordResetTokenDocument,
    Course,
    Module,
    Lesson,
    EmbeddedModule,
    EmbeddedLesson,
    Enrollment,
    Progress,
    LessonProgressItem,
    Quiz,
    QuizAttempt,
    AssessmentSession,
    Conversation,
    Class,
    Recommendation,
)


from scripts.curriculum_content import (
    get_course_blueprint,
    get_course_learning_outcomes,
    get_course_preview_url,
    get_course_prerequisites,
    get_course_thumbnail,
    get_lesson_video_url,
    get_module_learning_outcomes,
    pick_lesson,
    pick_module,
)

fake = Faker("vi_VN")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# =============================================================================
# DEMO DATA POOLS — ảnh & video thật, tài liệu công khai, câu quiz có nghĩa
# =============================================================================

REAL_AVATARS: List[str] = [
    "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop",
    "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=400&fit=crop",
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop",
    "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=400&fit=crop",
    "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=400&fit=crop",
    "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&h=400&fit=crop",
    "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400&h=400&fit=crop",
    "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=400&h=400&fit=crop",
    "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=400&h=400&fit=crop",
    "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&h=400&fit=crop",
]

REAL_THUMBNAILS: List[str] = [
    "https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=1200&h=675&fit=crop",
    "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=1200&h=675&fit=crop",
    "https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=1200&h=675&fit=crop",
    "https://images.unsplash.com/photo-1542831371-29b0f74f9713?w=1200&h=675&fit=crop",
    "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=1200&h=675&fit=crop",
    "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=1200&h=675&fit=crop",
    "https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=1200&h=675&fit=crop",
    "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200&h=675&fit=crop",
]

# Mã video YouTube thật (tutorial / tech) — có thể embed trên frontend
REAL_YOUTUBE_VIDEO_IDS: List[str] = [
    "rfscVS0vtbw",
    "YYXdXT2l-Gg",
    "_uQrJ0TkZlc",
    "W6NZfCO5SIk",
    "Ke90Tje7VS0",
    "hdI2bqOjy3c",
    "lhWGzTFEcko",
    "8aGhZQkoFbQ",
    "eWRfhZUzrAc",
    "SqcY0GlATPk",
]


class _ResourceSeed(TypedDict):
    title: str
    type: str
    url: str
    size_mb: float
    description: str


REAL_RESOURCE_POOL: List[_ResourceSeed] = [
    {
        "title": "W3C — Ghi chú trong PDF (WCAG mẫu)",
        "type": "pdf",
        "url": "https://www.w3.org/WAI/WCAG21/working-examples/pdf-note/note.pdf",
        "size_mb": 0.05,
        "description": "Tệp PDF ví dụ do W3C/WAI công bố, phù hợp test mở/tải trong demo.",
    },
    {
        "title": "WHATWG — HTML Living Standard",
        "type": "link",
        "url": "https://html.spec.whatwg.org/multipage/",
        "size_mb": 0.0,
        "description": "Chuẩn HTML hiện đại, nguồn mở, truy cập công khai.",
    },
    {
        "title": "Python Documentation — Tutorial",
        "type": "link",
        "url": "https://docs.python.org/3/tutorial/",
        "size_mb": 0.0,
        "description": "Hướng dẫn Python chính thống từ python.org.",
    },
    {
        "title": "MDN — JavaScript học tập",
        "type": "link",
        "url": "https://developer.mozilla.org/en-US/docs/Learn/JavaScript",
        "size_mb": 0.0,
        "description": "Tài liệu học JavaScript từ Mozilla MDN.",
    },
    {
        "title": "ECMA-262 (ECMAScript) — PDF chính thức",
        "type": "pdf",
        "url": "https://www.ecma-international.org/wp-content/uploads/ECMA-262_13th_edition_june_2022.pdf",
        "size_mb": 8.0,
        "description": "Đặc tả ngôn ngữ ECMAScript (bản công khai).",
    },
    {
        "title": "React — Documentation",
        "type": "link",
        "url": "https://react.dev/learn",
        "size_mb": 0.0,
        "description": "Tài liệu học React chính thức (react.dev).",
    },
    {
        "title": "FastAPI — User Guide",
        "type": "link",
        "url": "https://fastapi.tiangolo.com/tutorial/",
        "size_mb": 0.0,
        "description": "Tutorial FastAPI công khai.",
    },
    {
        "title": "CPython — README (mã nguồn)",
        "type": "code",
        "url": "https://raw.githubusercontent.com/python/cpython/main/README.rst",
        "size_mb": 0.02,
        "description": "README CPython trên GitHub (raw), dùng làm tài nguyên dạng code/text.",
    },
    {
        "title": "PostgreSQL — Documentation",
        "type": "link",
        "url": "https://www.postgresql.org/docs/current/tutorial.html",
        "size_mb": 0.0,
        "description": "Tutorial PostgreSQL chính thức.",
    },
    {
        "title": "Git — Reference",
        "type": "link",
        "url": "https://git-scm.com/doc",
        "size_mb": 0.0,
        "description": "Tài liệu Git chính thức.",
    },
    {
        "title": "Rust Book",
        "type": "link",
        "url": "https://doc.rust-lang.org/book/",
        "size_mb": 0.0,
        "description": "Sách học Rust công khai.",
    },
    {
        "title": "IEEE 802.3 — Overview (IEEE)",
        "type": "link",
        "url": "https://standards.ieee.org/standard/802_3.html",
        "size_mb": 0.0,
        "description": "Trang tiêu chuẩn Ethernet IEEE (tham chiếu networking).",
    },
]


class _McqPoolItem(TypedDict):
    question_text: str
    options: List[str]
    correct_index: int
    explanation: str


QUIZ_MCQ_POOL: List[_McqPoolItem] = [
    {
        "question_text": "Trong Python 3, kiểu `str` lưu trữ chuỗi ký tự theo dạng nào?",
        "options": ["Byte thuần không mã hóa", "Unicode (text)", "Chỉ ASCII 7-bit", "Cặp key-value"],
        "correct_index": 1,
        "explanation": "Kiểu `str` trong Python 3 là text Unicode; byte dùng kiểu `bytes`.",
    },
    {
        "question_text": "Toán tử `is` trong Python so sánh điều gì?",
        "options": ["Giá trị bằng nhau (==)", "Cùng đối tượng trong bộ nhớ (identity)", "Kiểu dữ liệu", "Độ dài chuỗi"],
        "correct_index": 1,
        "explanation": "`is` kiểm tra hai tham chiếu có trỏ cùng một object hay không.",
    },
    {
        "question_text": "HTTP status code 404 nghĩa là gì?",
        "options": ["Thành công", "Không tìm thấy tài nguyên", "Lỗi máy chủ", "Cần xác thực"],
        "correct_index": 1,
        "explanation": "404 Not Found: URL hoặc resource không tồn tại trên server.",
    },
    {
        "question_text": "Phương thức HTTP nào thường dùng để tạo tài nguyên mới trong REST API?",
        "options": ["GET", "POST", "DELETE", "HEAD"],
        "correct_index": 1,
        "explanation": "POST thường dùng để tạo mới (còn PUT/PATCH có thể cập nhật tuỳ thiết kế).",
    },
    {
        "question_text": "Trong JavaScript, `const` khai báo biến có đặc điểm gì?",
        "options": [
            "Gán lại được và hosting như `var`",
            "Không thể gán lại binding, phạm vi block",
            "Chỉ dùng trong vòng lặp for",
            "Luôn immutable sâu cho object",
        ],
        "correct_index": 1,
        "explanation": "`const` không cho gán lại binding; object bên trong vẫn có thể mutate trừ khi freeze.",
    },
    {
        "question_text": "`async/await` trong JavaScript chủ yếu dùng để làm gì?",
        "options": [
            "Tăng tốc DOM render",
            "Viết mã bất đồng bộ dễ đọc hơn Promise chain",
            "Thay thế hoàn toàn Web Worker",
            "Bắt buộc single-thread",
        ],
        "correct_index": 1,
        "explanation": "async/await là cú pháp đường đi trên Promise, giúp code async gọn hơn.",
    },
    {
        "question_text": "Trong React, Hook `useEffect` thường dùng để:",
        "options": [
            "Khai báo state",
            "Side effect (fetch, subscription) theo lifecycle/dependencies",
            "Thay Router",
            "Memo hóa giá trị tính toán",
        ],
        "correct_index": 1,
        "explanation": "useEffect nhóm side effects; cleanup trả về từ effect khi unmount/dep đổi.",
    },
    {
        "question_text": "SQL: `PRIMARY KEY` của bảng đảm bảo điều gì?",
        "options": ["Null nhiều lần", "Duy nhất và không null (thường)", "Luôn là UUID", "Tự động mã hóa"],
        "correct_index": 1,
        "explanation": "Primary key định danh mỗi hàng, thường NOT NULL + UNIQUE.",
    },
    {
        "question_text": "`git merge` so với `git rebase` (nhánh feature), phát biểu nào thường đúng?",
        "options": [
            "Merge tạo merge commit; rebase viết lại lịch sử commit",
            "Chúng giống hệt nhau",
            "Rebase không bao giờ gây conflict",
            "Merge xóa branch tự động",
        ],
        "correct_index": 0,
        "explanation": "Merge giữ lịch sử phân nhánh; rebase đặt commit lên đỉnh branch khác.",
    },
    {
        "question_text": "Trong mô hình OSI, HTTP thường được xem ở lớp nào (quy ước thông dụng)?",
        "options": ["Vật lý", "Tầng ứng dụng (Application)", "Tầng liên kết", "Tầng giao vận đơn thuần"],
        "correct_index": 1,
        "explanation": "HTTP là giao thức lớp application; TCP nằm ở transport.",
    },
    {
        "question_text": "JSON là viết tắt của?",
        "options": [
            "JavaScript Object Notation",
            "Java Structured Object Network",
            "Joint Open Network",
            "Jira Object Notation",
        ],
        "correct_index": 0,
        "explanation": "JSON: JavaScript Object Notation — định dạng trao đổi dữ liệu nhẹ.",
    },
    {
        "question_text": "Tránh SQL injection, biện pháp nào được coi là best practice?",
        "options": [
            "Nối chuỗi SQL trực tiếp từ input người dùng",
            "Tham số hóa / prepared statements + validate input",
            "Chỉ dùng POST",
            "Tắt log database",
        ],
        "correct_index": 1,
        "explanation": "Binding tham số + ORM an toàn giúp ngăn nhúng mã SQL độc hại.",
    },
    {
        "question_text": "Trong Linux, lệnh `chmod +x script.sh` làm gì?",
        "options": [
            "Xóa file",
            "Thêm quyền thực thi cho file",
            "Đổi owner sang root",
            "Nén file",
        ],
        "correct_index": 1,
        "explanation": "`+x` thêm executable bit để có thể chạy script (nếu shebang/perms phù hợp).",
    },
    {
        "question_text": "JWT (JSON Web Token) gồm phần nào theo định dạng tiêu chuẩn?",
        "options": [
            "Chỉ payload",
            "Header.Payload.Signature (chuỗi base64url, chấm nối)",
            "CSV ba cột",
            "XML SOAP envelope",
        ],
        "correct_index": 1,
        "explanation": "JWT thường là ba phần nối bằng dấu chấm và ký để xác minh integrity.",
    },
    {
        "question_text": "RESTful API ‘idempotent’ với PUT thường có nghĩa gì?",
        "options": [
            "Lần gọi đầu lỗi thì không gọi lại",
            "Gọi nhiều lần với cùng payload cho kết quả giống như một lần",
            "Luôn tạo bản ghi mới",
            "Chỉ đọc dữ liệu",
        ],
        "correct_index": 1,
        "explanation": "PUT idempotent trong thiết kế chuẩn: không tạo thêm side-effects khi lặp lại.",
    },
    {
        "question_text": "Trong MongoDB/BSON, một document không được vượt quá kích thước bao nhiêu?",
        "options": ["1 MB", "16 MB", "256 MB", "Không giới hạn"],
        "correct_index": 1,
        "explanation": "Giới hạn document BSON mặc định trong MongoDB là 16 MB.",
    },
    {
        "question_text": "Trong Kubernetes, Deployment quản lý gì chủ đạo?",
        "options": [
            "Chỉ log",
            "Pod replicas và rollout/rollback của ứng dụng",
            "Firewall hardware",
            "DNS root zone",
        ],
        "correct_index": 1,
        "explanation": "Deployment điều khiển ReplicaSet/Pods và chiến lược rollout.",
    },
    {
        "question_text": "Độ phức tạp trung bình của tìm kiếm trên BST cân bằng có thứ tự N phần tử là?",
        "options": ["O(N)", "O(log N)", "O(1) luôn luôn", "O(N^2)"],
        "correct_index": 1,
        "explanation": "BST cân bằng cho phép insert/search/delete trung bình O(log N).",
    },
]

QUIZ_TRUE_FALSE_POOL: List[Tuple[str, str]] = [
    ("Trong IPv4, địa chỉ IP gồm 32 bit.", "True"),
    ("HTTPS sử dụng TLS để mã hóa lớp vận chuyển giữa client và server.", "True"),
    ("Python là ngôn ngữ chỉ biên dịch sang native trước khi chạy, không có interpreter.", "False"),
    ("React render commit là synchronous trong mọi trường hợp concurrent.", "False"),
    ("DNS chuyển tên miền thành địa chỉ IP.", "True"),
]

QUIZ_FILL_IN_BLANK_POOL: List[Tuple[str, str]] = [
    ("Giao thức không trạng thái của web phổ biến dùng với REST là ____.", "HTTP"),
    ("Thuật toán hashing một chiều thường dùng lưu mật khẩu trong DB có tiền tố bcrypt/PBKDF là ____ hashing.", "password"),
    ("Khóa công khai trong RSA thường dùng với chức năng ____ hóa dữ liệu cho người nhận.", "encrypt"),
    ("Trường `Content-Type` trong HTTP header chỉ báo ____ của payload.", "media"),
    ("Trong bash, `$?` chứa mã thoát của ____ vừa chạy.", "command"),
]

ASSESSMENT_SKILLS_BY_CATEGORY: Dict[str, List[str]] = {
    "Programming": ["Python cơ bản", "Cấu trúc dữ liệu", "Git & workflow", "Debug & testing"],
    "Data Science": ["Phân tích dữ liệu", "SQL truy vấn", "Machine Learning", "Trực quan hóa"],
    "Business": ["Quản lý dự án", "Giao tiếp nhóm", "OKR & KPI", "Ra quyết định"],
    "Languages": ["Đọc hiểu tài liệu", "Viết kỹ thuật", "Thuyết trình", "Từ vựng chuyên ngành"],
    "Math": ["Đại số", "Xác suất thống kê", "Giải tích", "Tư duy logic"],
}

ASSESSMENT_QUESTIONS_BY_DIFFICULTY: Dict[str, List[str]] = {
    "easy": [
        "Biến trong Python dùng để lưu trữ gì?",
        "HTTP status 200 nghĩa là gì?",
        "Git commit dùng để làm gì?",
        "Hàm `len()` trong Python trả về gì?",
    ],
    "medium": [
        "Sự khác nhau giữa list và tuple trong Python là gì?",
        "Khi nào nên dùng index trong cơ sở dữ liệu?",
        "REST API idempotent nghĩa là gì?",
        "Cross-validation trong ML dùng để làm gì?",
    ],
    "hard": [
        "Giải thích trade-off giữa consistency và availability trong CAP.",
        "Phân biệt optimistic và pessimistic locking.",
        "Khi nào chọn microservices thay vì monolith?",
        "Giải thích overfitting và cách giảm thiểu.",
    ],
}

CLASS_NAME_PREFIXES = ["Lớp", "Nhóm học", "Cohort", "Buổi"]


def pick_assessment_skill(category: str) -> str:
    pool = ASSESSMENT_SKILLS_BY_CATEGORY.get(category) or ASSESSMENT_SKILLS_BY_CATEGORY["Programming"]
    return random.choice(pool)


def mk_class_description(course_title: str) -> str:
    return (
        f"Lớp học trực tuyến gắn khóa «{course_title}». "
        "Học theo module, làm quiz và theo dõi tiến độ trên dashboard."
    )


def mk_quiz_description(lesson_title: str, lesson_description: str = "") -> str:
    base = f"Kiểm tra kiến thức bài «{lesson_title}»."
    if lesson_description and lesson_description != lesson_title:
        snippet = lesson_description[:100].strip()
        if snippet:
            return f"{base} {snippet}"
    return base


def pick_avatar_url() -> str:
    return random.choice(REAL_AVATARS)


def pick_thumbnail_url() -> str:
    return random.choice(REAL_THUMBNAILS)


def youtube_watch_from_id(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def pick_youtube_watch_url() -> str:
    return youtube_watch_from_id(random.choice(REAL_YOUTUBE_VIDEO_IDS))


@dataclass
class SeedConfig:
    seed: int = 20260507
    admins: int = 10
    instructors: int = 40
    students: int = 360
    public_courses: int = 70
    personal_courses: int = 80
    public_modules_per_course: int = 6
    public_lessons_per_module: int = 6
    personal_modules_per_course: int = 4
    personal_lessons_per_module: int = 5
    classes: int = 90


def now() -> datetime:
    return datetime.now(timezone.utc)


def past(days_min: int = 1, days_max: int = 120) -> datetime:
    return now() - timedelta(days=random.randint(days_min, days_max), hours=random.randint(0, 23))


def future(days_min: int = 1, days_max: int = 60) -> datetime:
    return now() + timedelta(days=random.randint(days_min, days_max))


def gid() -> str:
    return str(uuid.uuid4())


def hp(password: str) -> str:
    return pwd_context.hash(password)


def sample_weighted(values: List[Tuple[str, float]]) -> str:
    keys = [k for k, _ in values]
    weights = [w for _, w in values]
    return random.choices(keys, weights=weights, k=1)[0]


def mk_resource(title: str, rtype: str) -> dict:
    """Lấy URL thật (W3C / MDN / docs công khai) từ REAL_RESOURCE_POOL — giữ nguyên `rtype` theo schema UI."""
    rt = (rtype or "link").lower()
    if rt == "video":
        preferred = ("link",)
    elif rt == "slide":
        preferred = ("pdf", "link")
    elif rt == "pdf":
        preferred = ("pdf", "link")
    elif rt == "code":
        preferred = ("code", "link")
    else:
        preferred = ("link", "pdf", "code")
    candidates = [r for r in REAL_RESOURCE_POOL if r["type"] in preferred]
    pool = candidates if candidates else REAL_RESOURCE_POOL
    src = random.choice(pool)
    size_mb = src["size_mb"] if src["size_mb"] and src["size_mb"] > 0 else round(random.uniform(0.2, 12.0), 2)
    return {
        "id": gid(),
        "title": title,
        "type": rtype,
        "url": src["url"],
        "size_mb": size_mb,
        "description": src["description"],
    }


def mk_course_outcome() -> dict:
    return {
        "description": fake.sentence(nb_words=10),
        "skill_tag": fake.slug().replace("-", "_"),
    }


def mk_module_outcome() -> dict:
    return {
        "id": gid(),
        "outcome": fake.sentence(nb_words=10),
        "skill_tag": fake.slug().replace("-", "_"),
        "is_mandatory": random.choice([True, True, False]),
    }


def module_outcomes_from_curriculum(mod_tpl: dict) -> List[dict]:
    outcomes = get_module_learning_outcomes(mod_tpl)
    return [
        {
            "id": gid(),
            "outcome": item["description"],
            "skill_tag": item.get("skill_tag") or "module-outcome",
            "is_mandatory": True,
        }
        for item in outcomes
    ]


def mk_quiz_question(order: int) -> dict:
    qtype = sample_weighted([
        ("multiple_choice", 0.7),
        ("fill_in_blank", 0.2),
        ("true_false", 0.1),
    ])
    points = random.randint(1, 3)
    if qtype == "multiple_choice":
        item = random.choice(QUIZ_MCQ_POOL)
        question_text = item["question_text"]
        options = list(item["options"])
        correct = str(item["correct_index"])
        explanation = item["explanation"]
    elif qtype == "true_false":
        question_text, correct = random.choice(QUIZ_TRUE_FALSE_POOL)
        options = ["True", "False"]
        explanation = f"Phát biểu trên {'đúng' if correct == 'True' else 'sai'} theo kiến thức phổ biến về CNTT."
    else:
        question_text, correct = random.choice(QUIZ_FILL_IN_BLANK_POOL)
        options = None
        explanation = f"Ô trống đúng: «{correct}» (không phân biệt hoa thường khi chấm)."
    return {
        "id": gid(),
        "type": qtype,
        "question_text": question_text,
        "options": options,
        "correct_answer": correct,
        "explanation": explanation,
        "points": points,
        "is_mandatory": random.choice([True, False]),
        "order": order,
    }


def mk_assessment_question(difficulty: str, category: str = "Programming") -> dict:
    qtype = random.choice(["multiple_choice", "fill_in_blank", "drag_and_drop"])
    options = ["Đáp án A", "Đáp án B", "Đáp án C", "Đáp án D"] if qtype == "multiple_choice" else None
    points = {"easy": 1, "medium": 2, "hard": 3}[difficulty]
    skill_tag = pick_assessment_skill(category)
    question_pool = ASSESSMENT_QUESTIONS_BY_DIFFICULTY.get(difficulty, ASSESSMENT_QUESTIONS_BY_DIFFICULTY["medium"])
    return {
        "question_id": gid(),
        "question_text": random.choice(question_pool),
        "question_type": qtype,
        "difficulty": difficulty,
        "skill_tag": skill_tag,
        "points": points,
        "options": options,
        "correct_answer_hint": f"Ôn tập mục «{skill_tag}» trong lĩnh vực {category}.",
    }


def mk_assessment_skill_analysis_payload(
    questions: List[dict],
    correct_answers: int,
    overall_feedback: str,
) -> dict:
    """Khớp cấu trúc assessment_service.evaluate — skill_analysis là dict, không phải list."""
    by_tag: Dict[str, Dict[str, int]] = {}
    for q in questions:
        tag = q.get("skill_tag") or "general"
        by_tag.setdefault(tag, {"total": 0, "correct": 0})
        by_tag[tag]["total"] += 1

    remaining = max(0, correct_answers or 0)
    tags = list(by_tag.keys())
    skill_items = []
    for i, tag in enumerate(tags):
        total = by_tag[tag]["total"]
        if i == len(tags) - 1:
            correct = remaining
        else:
            correct = min(remaining, random.randint(0, total))
        remaining -= correct
        pct = round((correct / total) * 100, 1) if total else 0.0
        strength = "Strong" if pct >= 75 else ("Average" if pct >= 50 else "Weak")
        skill_items.append({
            "skill_tag": tag,
            "questions_count": total,
            "correct_count": correct,
            "proficiency_percentage": pct,
            "strength_level": strength,
            "detailed_feedback": f"Kỹ năng «{tag}»: {correct}/{total} câu đúng.",
        })

    breakdown = {
        d: {"correct": 0, "total": 0}
        for d in ("easy", "medium", "hard")
    }
    for q in questions:
        diff = q.get("difficulty", "medium")
        if diff in breakdown:
            breakdown[diff]["total"] += 1
    remaining = max(0, correct_answers or 0)
    for diff in ("easy", "medium", "hard"):
        total = breakdown[diff]["total"]
        if diff == "hard":
            correct = remaining
        else:
            correct = min(remaining, random.randint(0, total)) if total else 0
        breakdown[diff]["correct"] = correct
        remaining -= correct

    return {
        "skill_analysis": skill_items,
        "score_breakdown": breakdown,
        "overall_feedback": overall_feedback,
    }


def profile_header(title: str):
    print(f"\n--- {title} ---")


# Batch sizes — tránh một lệnh insert quá lớn (BSON ~16MB, RAM spike) khi nội dung lesson/progress nặng
BATCH_COURSES = 50
BATCH_MODULES = 200
BATCH_LESSONS = 200
BATCH_USERS = 250
BATCH_CLASSES = 200
BATCH_ENROLLMENTS = 400
BATCH_PROGRESS = 120
BATCH_QUIZZES = 200
BATCH_QUIZ_ATTEMPTS = 250
BATCH_ASSESSMENTS = 350
BATCH_RECOMMENDATIONS = 250
BATCH_CONVERSATIONS = 150
BATCH_TOKENS = 500


async def insert_many_batched(model: Any, docs: List[Any], batch_size: int) -> int:
    """Chunk insert_many để giảm rủi ro vượt ngưỡng bulk write / BSON."""
    if not docs:
        return 0
    inserted = 0
    for i in range(0, len(docs), batch_size):
        chunk = docs[i : i + batch_size]
        await model.insert_many(chunk)
        inserted += len(chunk)
    return inserted


async def drop_all_collections():
    profile_header("FULL RESET COLLECTIONS")
    await RefreshToken.delete_all()
    await PasswordResetTokenDocument.delete_all()
    await QuizAttempt.delete_all()
    await Quiz.delete_all()
    await Progress.delete_all()
    await Enrollment.delete_all()
    await AssessmentSession.delete_all()
    await Recommendation.delete_all()
    await Conversation.delete_all()
    await Class.delete_all()
    await Lesson.delete_all()
    await Module.delete_all()
    await Course.delete_all()
    await User.delete_all()
    print("Reset done.")


async def seed_users(cfg: SeedConfig) -> Dict[str, List[str]]:
    profile_header("SEED USERS")
    users: List[User] = []
    role_ids = {"admin": [], "instructor": [], "student": []}

    for i in range(cfg.admins):
        uid = gid()
        user = User(
            id=uid,
            full_name=f"Admin {fake.name()}",
            email=f"admin{i+1}@ailearning.vn",
            hashed_password=hp("Admin@123456"),
            role="admin",
            status=sample_weighted([("active", 0.9), ("inactive", 0.06), ("banned", 0.02), ("suspended", 0.02)]),
            avatar_url=pick_avatar_url(),
            bio=fake.text(max_nb_chars=180),
            contact_info=fake.phone_number(),
            learning_preferences=random.sample(["Programming", "Data Science", "Business", "Languages", "Math"], k=2),
            email_verified=random.random() < 0.94,
            phone_verified=random.random() < 0.82,
            created_at=past(120, 300),
            updated_at=past(5, 20),
            last_login_at=past(0, 5),
        )
        users.append(user)
        role_ids["admin"].append(uid)

    for i in range(cfg.instructors):
        uid = gid()
        user = User(
            id=uid,
            full_name=fake.name(),
            email=f"instructor{i+1}@ailearning.vn",
            hashed_password=hp("Instructor@123"),
            role="instructor",
            status=sample_weighted([("active", 0.8), ("inactive", 0.15), ("banned", 0.03), ("suspended", 0.02)]),
            avatar_url=pick_avatar_url(),
            bio=fake.text(max_nb_chars=260),
            contact_info=fake.phone_number(),
            learning_preferences=random.sample(["Programming", "Data Science", "Business", "Languages", "Math"], k=3),
            email_verified=random.random() < 0.86,
            phone_verified=random.random() < 0.74,
            created_by=random.choice(role_ids["admin"]),
            created_at=past(90, 220),
            updated_at=past(1, 20),
            last_login_at=past(0, 15),
        )
        users.append(user)
        role_ids["instructor"].append(uid)

    for i in range(cfg.students):
        uid = gid()
        user = User(
            id=uid,
            full_name=fake.name(),
            email=f"student{i+1}@gmail.com",
            hashed_password=hp("Student@123"),
            role="student",
            status=sample_weighted([("active", 0.82), ("inactive", 0.11), ("banned", 0.04), ("suspended", 0.03)]),
            avatar_url=pick_avatar_url(),
            bio=fake.text(max_nb_chars=220),
            contact_info=fake.phone_number(),
            learning_preferences=random.sample(["Programming", "Data Science", "Business", "Languages", "Math"], k=random.randint(1, 3)),
            email_verified=random.random() < 0.82,
            phone_verified=random.random() < 0.68,
            created_by=random.choice(role_ids["admin"] + role_ids["instructor"]),
            created_at=past(30, 220),
            updated_at=past(1, 20),
            last_login_at=past(0, 30),
        )
        users.append(user)
        role_ids["student"].append(uid)

    await insert_many_batched(User, users, BATCH_USERS)
    print(f"Users seeded: {len(users)}")
    return role_ids


def build_course_blueprint(idx: int, owner_type: str) -> Dict[str, str]:
    pack = get_course_blueprint(idx)
    return {
        "title": pack["title"],
        "description": pack["description"],
        "category": pack["category"],
        "level": pack["level"],
        "language": random.choice(["vi", "en"]),
        "owner_type": owner_type,
        "_curriculum": pack,
    }


async def seed_courses_modules_lessons(cfg: SeedConfig, role_ids: Dict[str, List[str]]) -> Dict[str, Any]:
    profile_header("SEED COURSES/MODULES/LESSONS")
    courses: List[Course] = []
    modules: List[Module] = []
    lessons: List[Lesson] = []
    course_map = {"public": [], "personal": []}

    # Public courses
    for i in range(cfg.public_courses):
        cid = gid()
        instructor_id = random.choice(role_ids["instructor"])
        owner_id = random.choice(role_ids["admin"] + role_ids["instructor"])
        bp = build_course_blueprint(i, "admin" if owner_id in role_ids["admin"] else "instructor")
        curriculum = bp.pop("_curriculum", {})
        module_embeds: List[EmbeddedModule] = []
        total_lessons = 0
        total_duration = 0

        for m in range(cfg.public_modules_per_course):
            mid = gid()
            mod_tpl = pick_module(m, curriculum)
            module_lessons_embed: List[EmbeddedLesson] = []
            module_duration = 0
            for l in range(cfg.public_lessons_per_module):
                lid = gid()
                lesson_tpl = pick_lesson(mod_tpl, l)
                mins = random.randint(18, 65)
                ctype = lesson_tpl.get("content_type") or "text"
                has_video = ctype in ["video", "mixed"] or bool(lesson_tpl.get("video_id"))
                lesson = Lesson(
                    id=lid,
                    module_id=mid,
                    course_id=cid,
                    title=lesson_tpl["title"],
                    description=lesson_tpl.get("description") or lesson_tpl["title"],
                    order=l + 1,
                    content=lesson_tpl["content"],
                    content_type=ctype,
                    duration_minutes=mins,
                    video_url=get_lesson_video_url(curriculum, lesson_tpl, l) if has_video else None,
                    audio_url=None,
                    learning_objectives=lesson_tpl.get("objectives")
                    or [fake.sentence(nb_words=6) for _ in range(random.randint(2, 3))],
                    resources=[
                        mk_resource("Slide pack", "slide"),
                        mk_resource("Practice code", "code"),
                        mk_resource("Reference", "link"),
                    ],
                    quiz_id=None,
                    is_published=True,
                    created_at=past(30, 180),
                    updated_at=past(1, 20),
                )
                lessons.append(lesson)
                module_duration += mins
                total_lessons += 1
                total_duration += mins
                module_lessons_embed.append(
                    EmbeddedLesson(
                        id=lid,
                        title=lesson.title,
                        description=lesson.description,
                        order=lesson.order,
                        content=lesson.content,
                        content_type=lesson.content_type,
                        duration_minutes=lesson.duration_minutes,
                        video_url=lesson.video_url,
                        audio_url=lesson.audio_url,
                        resources=lesson.resources,
                        learning_objectives=lesson.learning_objectives,
                        quiz_id=None,
                        is_published=True,
                        created_at=lesson.created_at,
                        updated_at=lesson.updated_at,
                    )
                )

            module = Module(
                id=mid,
                course_id=cid,
                title=mod_tpl.get("title") or f"Module {m+1}",
                description=mod_tpl.get("description") or fake.text(max_nb_chars=180),
                order=m + 1,
                difficulty=random.choice(["Basic", "Intermediate", "Advanced"]),
                estimated_hours=round(module_duration / 60.0, 1),
                learning_outcomes=module_outcomes_from_curriculum(mod_tpl),
                resources=[mk_resource("Module Notes", "pdf"), mk_resource("Links", "link")],
                prerequisites=[module_embeds[m - 1].id] if m > 0 else [],
                total_lessons=cfg.public_lessons_per_module,
                total_duration_minutes=module_duration,
                created_at=past(20, 120),
                updated_at=past(1, 10),
            )
            modules.append(module)
            module_embeds.append(
                EmbeddedModule(
                    id=mid,
                    title=module.title,
                    description=module.description,
                    order=module.order,
                    difficulty=module.difficulty,
                    estimated_hours=module.estimated_hours,
                    learning_outcomes=module.learning_outcomes,
                    prerequisites=module.prerequisites,
                    resources=module.resources,
                    lessons=module_lessons_embed,
                    total_lessons=module.total_lessons,
                    total_duration_minutes=module.total_duration_minutes,
                    created_at=module.created_at,
                    updated_at=module.updated_at,
                )
            )

        course = Course(
            id=cid,
            title=bp["title"],
            description=bp["description"],
            category=bp["category"],
            level=bp["level"],
            thumbnail_url=get_course_thumbnail(curriculum),
            preview_video_url=get_course_preview_url(curriculum),
            language=bp["language"],
            status=sample_weighted([("published", 0.8), ("draft", 0.15), ("archived", 0.05)]),
            owner_id=owner_id,
            owner_type=bp["owner_type"],
            instructor_id=instructor_id,
            instructor_name=f"Instructor {instructor_id[:6]}",
            instructor_avatar=pick_avatar_url(),
            instructor_bio=fake.text(max_nb_chars=200),
            course_type="public",
            learning_outcomes=get_course_learning_outcomes(curriculum) or [mk_course_outcome()],
            prerequisites=get_course_prerequisites(curriculum),
            modules=module_embeds,
            total_duration_minutes=total_duration,
            total_modules=len(module_embeds),
            total_lessons=total_lessons,
            enrollment_count=0,
            avg_rating=round(random.uniform(3.5, 5.0), 1),
            created_at=past(40, 220),
            updated_at=past(1, 20),
        )
        courses.append(course)
        course_map["public"].append(cid)

    # Personal courses
    selected_students = random.sample(role_ids["student"], k=min(cfg.personal_courses, len(role_ids["student"])))
    for i, student_id in enumerate(selected_students):
        cid = gid()
        bp = build_course_blueprint(i + 100, "student")
        curriculum = bp.pop("_curriculum", {})
        module_embeds: List[EmbeddedModule] = []
        total_lessons = 0
        total_duration = 0

        for m in range(cfg.personal_modules_per_course):
            mid = gid()
            mod_tpl = pick_module(m, curriculum)
            module_lessons_embed: List[EmbeddedLesson] = []
            module_duration = 0
            for l in range(cfg.personal_lessons_per_module):
                lid = gid()
                lesson_tpl = pick_lesson(mod_tpl, l)
                mins = random.randint(15, 45)
                ctype = lesson_tpl.get("content_type") or "text"
                has_video = ctype in ["video", "mixed"] or bool(lesson_tpl.get("video_id"))
                lesson = Lesson(
                    id=lid,
                    module_id=mid,
                    course_id=cid,
                    title=lesson_tpl["title"],
                    description=lesson_tpl.get("description") or lesson_tpl["title"],
                    order=l + 1,
                    content=lesson_tpl["content"],
                    content_type=ctype,
                    duration_minutes=mins,
                    video_url=get_lesson_video_url(curriculum, lesson_tpl, l) if has_video else None,
                    learning_objectives=lesson_tpl.get("objectives")
                    or [fake.sentence(nb_words=5) for _ in range(random.randint(1, 3))],
                    resources=[mk_resource("Personal notes", "pdf")],
                    quiz_id=None,
                    is_published=True,
                    created_at=past(20, 120),
                    updated_at=past(1, 10),
                )
                lessons.append(lesson)
                module_duration += mins
                total_lessons += 1
                total_duration += mins
                module_lessons_embed.append(
                    EmbeddedLesson(
                        id=lid,
                        title=lesson.title,
                        description=lesson.description,
                        order=lesson.order,
                        content=lesson.content,
                        content_type=lesson.content_type,
                        duration_minutes=lesson.duration_minutes,
                        video_url=lesson.video_url,
                        resources=lesson.resources,
                        learning_objectives=lesson.learning_objectives,
                        quiz_id=None,
                        is_published=True,
                        created_at=lesson.created_at,
                        updated_at=lesson.updated_at,
                    )
                )

            module = Module(
                id=mid,
                course_id=cid,
                title=mod_tpl.get("title") or f"Module {m+1}",
                description=mod_tpl.get("description") or fake.sentence(nb_words=12),
                order=m + 1,
                difficulty=random.choice(["Basic", "Intermediate", "Advanced"]),
                estimated_hours=round(module_duration / 60.0, 1),
                learning_outcomes=module_outcomes_from_curriculum(mod_tpl),
                resources=[mk_resource("Ref", "link")],
                prerequisites=[module_embeds[m - 1].id] if m > 0 else [],
                total_lessons=cfg.personal_lessons_per_module,
                total_duration_minutes=module_duration,
                created_at=past(10, 70),
                updated_at=past(1, 7),
            )
            modules.append(module)
            module_embeds.append(
                EmbeddedModule(
                    id=mid,
                    title=module.title,
                    description=module.description,
                    order=module.order,
                    difficulty=module.difficulty,
                    estimated_hours=module.estimated_hours,
                    learning_outcomes=module.learning_outcomes,
                    prerequisites=module.prerequisites,
                    resources=module.resources,
                    lessons=module_lessons_embed,
                    total_lessons=module.total_lessons,
                    total_duration_minutes=module.total_duration_minutes,
                    created_at=module.created_at,
                    updated_at=module.updated_at,
                )
            )

        course = Course(
            id=cid,
            title=f"Personal - {bp['title']}",
            description=bp["description"],
            category=bp["category"],
            level=bp["level"],
            language=bp["language"],
            thumbnail_url=get_course_thumbnail(curriculum),
            preview_video_url=get_course_preview_url(curriculum),
            status=sample_weighted([("published", 0.45), ("draft", 0.5), ("archived", 0.05)]),
            owner_id=student_id,
            owner_type="student",
            instructor_name=f"Student Owner {student_id[:6]}",
            instructor_avatar=pick_avatar_url(),
            instructor_bio=fake.sentence(nb_words=14),
            course_type="personal",
            learning_outcomes=get_course_learning_outcomes(curriculum) or [mk_course_outcome()],
            prerequisites=get_course_prerequisites(curriculum),
            modules=module_embeds,
            total_duration_minutes=total_duration,
            total_modules=len(module_embeds),
            total_lessons=total_lessons,
            enrollment_count=0,
            avg_rating=None,
            created_at=past(8, 100),
            updated_at=past(1, 6),
        )
        courses.append(course)
        course_map["personal"].append(cid)

    await insert_many_batched(Course, courses, BATCH_COURSES)
    await insert_many_batched(Module, modules, BATCH_MODULES)
    await insert_many_batched(Lesson, lessons, BATCH_LESSONS)
    print(f"Courses seeded: {len(courses)} (public={len(course_map['public'])}, personal={len(course_map['personal'])})")
    print(f"Modules seeded: {len(modules)} | Lessons seeded: {len(lessons)}")
    return {"course_map": course_map}


async def seed_classes(cfg: SeedConfig, role_ids: Dict[str, List[str]], course_map: Dict[str, List[str]]) -> List[str]:
    profile_header("SEED CLASSES")
    classes: List[Class] = []
    public_courses = course_map["public"]
    course_docs = {
        c.id: c
        for c in await Course.find({"_id": {"$in": public_courses}}).to_list()
    }
    course_counters: Dict[str, int] = {}

    for i in range(cfg.classes):
        start = past(0, 35)
        end = start + timedelta(days=random.randint(45, 120))
        course_id = random.choice(public_courses)
        course = course_docs.get(course_id)
        course_title = course.title if course else "Khóa học"
        course_counters[course_id] = course_counters.get(course_id, 0) + 1
        n = course_counters[course_id]
        prefix = CLASS_NAME_PREFIXES[i % len(CLASS_NAME_PREFIXES)]
        short_title = course_title if len(course_title) <= 48 else f"{course_title[:45]}…"
        name = f"{prefix} {short_title}" if n == 1 else f"{prefix} {short_title} #{n}"

        c = Class(
            id=gid(),
            name=name,
            description=mk_class_description(course_title),
            course_id=course_id,
            instructor_id=random.choice(role_ids["instructor"]),
            max_students=random.randint(45, 120),
            start_date=start,
            end_date=end,
            status=sample_weighted([("preparing", 0.25), ("active", 0.6), ("completed", 0.15)]),
            student_ids=[],
            created_at=past(3, 90),
            updated_at=past(1, 7),
        )
        classes.append(c)

    await insert_many_batched(Class, classes, BATCH_CLASSES)
    print(f"Classes seeded: {len(classes)}")
    return [c.id for c in classes]


async def seed_enrollments_progress(cfg: SeedConfig, role_ids: Dict[str, List[str]], course_map: Dict[str, List[str]]) -> Dict[str, Any]:
    profile_header("SEED ENROLLMENTS/PROGRESS")
    public_course_ids = course_map["public"]
    course_docs = await Course.find({"_id": {"$in": public_course_ids}}).to_list()
    modules = await Module.find({"course_id": {"$in": public_course_ids}}).to_list()
    lessons = await Lesson.find({"course_id": {"$in": public_course_ids}}).to_list()

    module_by_course: Dict[str, List[Module]] = {}
    lessons_by_module: Dict[str, List[Lesson]] = {}
    for m in modules:
        module_by_course.setdefault(m.course_id, []).append(m)
    for l in lessons:
        lessons_by_module.setdefault(l.module_id, []).append(l)

    enrollments: List[Enrollment] = []
    progresses: List[Progress] = []
    enrollment_by_course: Dict[str, List[Enrollment]] = {}
    all_enrollment_ids: List[str] = []

    for sid in role_ids["student"]:
        picked_courses = random.sample(public_course_ids, k=min(random.randint(12, 22), len(public_course_ids)))
        for cid in picked_courses:
            eid = gid()
            status = sample_weighted([("active", 0.68), ("completed", 0.22), ("cancelled", 0.10)])
            enrolled_at = past(5, 150)
            progress_percent = 0.0
            if status == "completed":
                progress_percent = 100.0
            elif status == "active":
                progress_percent = round(random.uniform(5, 95), 1)
            else:
                progress_percent = round(random.uniform(0, 70), 1)

            course_modules = sorted(module_by_course.get(cid, []), key=lambda x: x.order)
            all_lessons: List[Lesson] = []
            for m in course_modules:
                all_lessons.extend(sorted(lessons_by_module.get(m.id, []), key=lambda x: x.order))
            total_lessons_count = len(all_lessons)
            completed_count = int((progress_percent / 100.0) * total_lessons_count) if total_lessons_count else 0
            completed_lessons = [ls.id for ls in all_lessons[:completed_count]]

            completed_modules: List[str] = []
            for m in course_modules:
                m_lessons = sorted(lessons_by_module.get(m.id, []), key=lambda x: x.order)
                if m_lessons and all(ls.id in completed_lessons for ls in m_lessons):
                    completed_modules.append(m.id)

            enrollment = Enrollment(
                id=eid,
                user_id=sid,
                course_id=cid,
                status=status,
                progress_percent=progress_percent,
                completion_rate=progress_percent,
                completed_lessons=completed_lessons,
                completed_modules=completed_modules,
                avg_quiz_score=round(random.uniform(45, 98), 1) if completed_count > 0 else None,
                total_time_spent_minutes=random.randint(40, 2400) if completed_count > 0 else 0,
                enrolled_at=enrolled_at,
                last_accessed_at=past(0, 12) if status != "cancelled" else None,
                completed_at=(enrolled_at + timedelta(days=random.randint(20, 110))) if status == "completed" else None,
            )
            enrollments.append(enrollment)
            enrollment_by_course.setdefault(cid, []).append(enrollment)
            all_enrollment_ids.append(eid)

            if status in ["active", "completed"]:
                lp_items: List[LessonProgressItem] = []
                for idx, ls in enumerate(all_lessons):
                    is_done = idx < completed_count
                    lp_items.append(
                        LessonProgressItem(
                            lesson_id=ls.id,
                            module_id=ls.module_id,
                            lesson_title=ls.title,
                            status="completed" if is_done else ("in-progress" if idx == completed_count and status == "active" else "not-started"),
                            completion_date=past(1, 80) if is_done else None,
                            time_spent_minutes=random.randint(10, max(ls.duration_minutes, 15)) if is_done else 0,
                            video_progress_seconds=random.randint(60, ls.duration_minutes * 60) if is_done and ls.video_url else 0,
                        )
                    )

                progress = Progress(
                    id=gid(),
                    user_id=sid,
                    course_id=cid,
                    enrollment_id=eid,
                    overall_progress_percent=progress_percent,
                    completed_lessons_count=completed_count,
                    total_lessons_count=total_lessons_count,
                    lessons_progress=lp_items,
                    total_time_spent_minutes=enrollment.total_time_spent_minutes,
                    estimated_hours_remaining=max(0.0, round(((total_lessons_count - completed_count) * 0.75), 1)),
                    study_streak_days=random.randint(0, 42),
                    avg_quiz_score=enrollment.avg_quiz_score or 0.0,
                    last_accessed_at=enrollment.last_accessed_at,
                    created_at=enrolled_at,
                    updated_at=past(0, 7),
                )
                progresses.append(progress)

    await insert_many_batched(Enrollment, enrollments, BATCH_ENROLLMENTS)
    if progresses:
        await insert_many_batched(Progress, progresses, BATCH_PROGRESS)

    for c in course_docs:
        c.enrollment_count = len(enrollment_by_course.get(c.id, []))
        c.updated_at = now()
        await c.save()

    print(f"Enrollments seeded: {len(enrollments)}")
    print(f"Progress docs seeded: {len(progresses)}")
    return {"enrollment_by_course": enrollment_by_course, "all_enrollment_ids": all_enrollment_ids}


async def seed_quizzes_attempts(cfg: SeedConfig, role_ids: Dict[str, List[str]]) -> Dict[str, List[str]]:
    profile_header("SEED QUIZZES/ATTEMPTS")
    lessons = await Lesson.find().to_list()
    enrollments = await Enrollment.find().to_list()
    enroll_by_user_course = {(e.user_id, e.course_id): e for e in enrollments}
    quizzes: List[Quiz] = []
    attempts: List[QuizAttempt] = []
    quiz_ids: List[str] = []

    for ls in lessons:
        create_quiz = random.random() < (0.72 if ls.course_id else 0.5)
        if not create_quiz:
            continue
        qid = gid()
        question_count = random.randint(5, 10)
        qs = [mk_quiz_question(i + 1) for i in range(question_count)]
        total_points = sum(q["points"] for q in qs)
        mandatory_count = sum(1 for q in qs if q["is_mandatory"])
        quiz = Quiz(
            id=qid,
            lesson_id=ls.id,
            course_id=ls.course_id,
            module_id=ls.module_id,
            title=f"Quiz - {ls.title}",
            description=mk_quiz_description(ls.title, ls.description or ""),
            quiz_type=random.choice(["review", "practice", "final_check"]),
            time_limit_minutes=random.choice([10, 15, 20, 25, None]),
            passing_score=random.choice([60.0, 70.0, 75.0]),
            max_attempts=random.choice([2, 3, 4]),
            deadline=future(20, 90),
            is_draft=random.choice([False, False, False, True]),
            questions=qs,
            question_count=question_count,
            total_points=total_points,
            mandatory_question_count=mandatory_count,
            created_by=random.choice(role_ids["instructor"] + role_ids["admin"]),
            created_at=past(5, 120),
            updated_at=past(1, 10),
        )
        quizzes.append(quiz)
        quiz_ids.append(qid)

    if quizzes:
        await Quiz.insert_many(quizzes)

    # map lesson->quiz for lesson update
    quiz_by_lesson = {q.lesson_id: q for q in quizzes}
    for ls in lessons:
        if ls.id in quiz_by_lesson:
            ls.quiz_id = quiz_by_lesson[ls.id].id
            ls.updated_at = now()
            await ls.save()

    # Attempts
    for q in quizzes:
        eligible_user_ids = []
        for e in enrollments:
            if e.course_id == q.course_id and e.status in ["active", "completed"]:
                eligible_user_ids.append(e.user_id)
        if not eligible_user_ids:
            continue
        sampled = random.sample(eligible_user_ids, k=min(len(eligible_user_ids), random.randint(8, 24)))
        for uid in sampled:
            attempts_count = random.choice([1, 1, 2, 2, 3])
            for n in range(attempts_count):
                score = round(random.uniform(35, 100), 1)
                passed = score >= q.passing_score
                started = past(1, 90)
                submitted = started + timedelta(minutes=random.randint(4, 45))
                answers = []
                correct = 0
                mandatory_correct = 0
                for qq in q.questions:
                    is_correct = random.random() < (0.65 if n == 0 else 0.78)
                    if is_correct:
                        correct += 1
                    if qq.get("is_mandatory") and is_correct:
                        mandatory_correct += 1
                    answers.append({
                        "question_id": qq["id"],
                        "question_content": qq["question_text"],
                        "student_answer": qq.get("correct_answer") if is_correct else fake.word(),
                        "correct_answer": qq.get("correct_answer"),
                        "is_correct": is_correct,
                        "is_mandatory": qq.get("is_mandatory", False),
                        "score": qq["points"] if is_correct else 0,
                        "explanation": qq.get("explanation", ""),
                        "related_lesson_link": f"/dashboard/courses/{q.course_id}/lessons/{q.lesson_id}",
                    })

                attempt = QuizAttempt(
                    id=gid(),
                    quiz_id=q.id,
                    user_id=uid,
                    answers=answers,
                    score=score,
                    status="Pass" if passed else "Fail",
                    passed=passed,
                    attempt_number=n + 1,
                    correct_answers=correct,
                    total_questions=q.question_count,
                    mandatory_correct=mandatory_correct,
                    mandatory_total=q.mandatory_question_count,
                    mandatory_passed=mandatory_correct >= max(1, int(q.mandatory_question_count * 0.6)) if q.mandatory_question_count else True,
                    can_retake=(n + 1) < q.max_attempts,
                    started_at=started,
                    submitted_at=submitted,
                    time_spent_seconds=int((submitted - started).total_seconds()),
                )
                attempts.append(attempt)

    if attempts:
        await insert_many_batched(QuizAttempt, attempts, BATCH_QUIZ_ATTEMPTS)

    print(f"Quizzes seeded: {len(quizzes)}")
    print(f"Quiz attempts seeded: {len(attempts)}")
    return {"quiz_ids": quiz_ids}


async def seed_assessments_recommendations(role_ids: Dict[str, List[str]], course_map: Dict[str, List[str]]) -> Dict[str, str]:
    profile_header("SEED ASSESSMENTS/RECOMMENDATIONS")
    sessions: List[AssessmentSession] = []
    # user -> (session_id, created_at, proficiency_level) — phiên evaluated mới nhất theo created_at
    user_latest_evaluated: Dict[str, Tuple[str, datetime, str]] = {}
    categories = ["Programming", "Data Science", "Business", "Languages", "Math"]
    level_cfg = {
        "Beginner": (15, 15),
        "Intermediate": (25, 22),
        "Advanced": (35, 30),
    }

    for sid in role_ids["student"]:
        for _ in range(random.randint(2, 4)):
            level = random.choice(["Beginner", "Intermediate", "Advanced"])
            category = random.choice(categories)
            total_questions, time_limit = level_cfg[level]
            status = sample_weighted([("pending", 0.15), ("in_progress", 0.2), ("submitted", 0.15), ("evaluated", 0.5)])
            created = past(1, 100)
            expires = created + timedelta(minutes=60)
            questions = []
            for i in range(total_questions):
                if i < total_questions * 0.2:
                    diff = "easy"
                elif i < total_questions * 0.8:
                    diff = "medium"
                else:
                    diff = "hard"
                questions.append(mk_assessment_question(diff, category))

            answers = []
            overall = None
            proficiency = None
            correct_answers = None
            skill_analysis = None
            knowledge_gaps = []
            ai_feedback = None
            time_analysis = None
            submitted_at = None
            evaluated_at = None

            if status in ["submitted", "evaluated"]:
                submitted_at = created + timedelta(minutes=random.randint(8, time_limit))
                for q in questions:
                    is_correct = random.random() < 0.62
                    answers.append({
                        "question_id": q["question_id"],
                        "answer_content": q["correct_answer_hint"] if is_correct else fake.word(),
                        "selected_option": random.randint(0, 3) if q["question_type"] == "multiple_choice" else None,
                        "time_taken_seconds": random.randint(20, 95),
                    })

            if status == "evaluated":
                evaluated_at = submitted_at + timedelta(seconds=random.randint(8, 180))
                correct_answers = sum(1 for _ in range(total_questions) if random.random() < 0.64)
                overall = round((correct_answers / total_questions) * 100, 1)
                proficiency = "Advanced" if overall >= 80 else ("Intermediate" if overall >= 60 else "Beginner")
                ai_feedback = (
                    f"Bạn đạt {overall}% ở mức {proficiency}. "
                    f"Hãy tập trung củng cố các kỹ năng còn yếu trong lĩnh vực {category}."
                )
                skill_analysis = mk_assessment_skill_analysis_payload(
                    questions, correct_answers, ai_feedback
                )
                knowledge_gaps = [
                    {
                        "gap_area": pick_assessment_skill(category),
                        "description": f"Cần ôn thêm kiến thức {category.lower()} ở mức {level}.",
                        "importance": random.choice(["High", "Medium", "Low"]),
                        "suggested_action": "Xem lại bài học liên quan và làm bài luyện tập.",
                    } for _ in range(random.randint(1, 3))
                ]
                total_time_seconds = sum(a["time_taken_seconds"] for a in answers) if answers else random.randint(400, 1800)
                time_analysis = {
                    "total_time_seconds": total_time_seconds,
                    "average_time_per_question": round(total_time_seconds / total_questions, 2),
                    "fastest_question_time": random.randint(8, 25),
                    "slowest_question_time": random.randint(80, 150),
                }

            sid_session = gid()
            session = AssessmentSession(
                id=sid_session,
                user_id=sid,
                category=category,
                subject=random.choice(ASSESSMENT_SKILLS_BY_CATEGORY.get(category, ["Tổng quan"])),
                level=level,
                focus_areas=[fake.word() for _ in range(random.randint(1, 3))],
                total_questions=total_questions,
                time_limit_minutes=time_limit,
                questions=questions,
                status=status,
                answers=answers,
                overall_score=overall,
                proficiency_level=proficiency,
                correct_answers=correct_answers,
                skill_analysis=skill_analysis,
                knowledge_gaps=knowledge_gaps,
                ai_feedback=ai_feedback,
                time_analysis=time_analysis,
                created_at=created,
                expires_at=expires,
                submitted_at=submitted_at,
                evaluated_at=evaluated_at,
            )
            sessions.append(session)
            if status == "evaluated" and proficiency:
                prev = user_latest_evaluated.get(sid)
                if prev is None or created >= prev[1]:
                    user_latest_evaluated[sid] = (sid_session, created, proficiency)

    if sessions:
        await insert_many_batched(AssessmentSession, sessions, BATCH_ASSESSMENTS)
    print(f"Assessment sessions seeded: {len(sessions)}")

    recommendations: List[Recommendation] = []
    all_courses = await Course.find({"status": {"$in": ["published", "draft"]}}).to_list()
    for sid in role_ids["student"]:
        eval_info = user_latest_evaluated.get(sid)
        session_id = eval_info[0] if eval_info else None
        prof_from_assessment = eval_info[2] if eval_info else None
        picked = random.sample(all_courses, k=min(len(all_courses), random.randint(4, 7)))
        recs = []
        order = []
        total_est_h = 0.0
        for rank, c in enumerate(picked, start=1):
            est_days = random.randint(7, 60)
            total_est_h += round((c.total_duration_minutes or 180) / 60.0, 1)
            recs.append({
                "course_id": c.id,
                "title": c.title,
                "description": c.description,
                "category": c.category,
                "level": c.level,
                "thumbnail_url": c.thumbnail_url,
                "priority_rank": rank,
                "relevance_score": round(random.uniform(60, 98), 1),
                "reason": fake.sentence(nb_words=16),
                "addresses_gaps": [fake.word() for _ in range(random.randint(1, 3))],
                "estimated_completion_days": est_days,
            })
            order.append({
                "step": rank,
                "course_id": c.id,
                "focus_modules": [f"Module {i}" for i in range(1, random.randint(2, 4))],
                "why_this_order": fake.sentence(nb_words=14),
            })

        if session_id and prof_from_assessment:
            rec_source = "assessment"
            user_prof_level = prof_from_assessment
        else:
            rec_source = random.choice(["learning_history", "ai_suggestion"])
            user_prof_level = sample_weighted([
                ("Beginner", 0.32),
                ("Intermediate", 0.41),
                ("Advanced", 0.27),
            ])

        recommendation = Recommendation(
            id=gid(),
            user_id=sid,
            source=rec_source,
            assessment_session_id=session_id,
            user_proficiency_level=user_prof_level,
            recommended_courses=recs,
            suggested_learning_order=order,
            practice_exercises=[
                {
                    "skill_tag": fake.slug().replace("-", "_"),
                    "exercise_type": random.choice(["coding", "quiz", "project", "reading"]),
                    "description": fake.sentence(nb_words=12),
                    "difficulty": random.choice(["easy", "medium", "hard"]),
                    "estimated_time_hours": round(random.uniform(0.5, 6.0), 1),
                } for _ in range(random.randint(3, 6))
            ],
            ai_personalized_advice=fake.paragraph(nb_sentences=3),
            total_estimated_hours=round(total_est_h, 1),
            created_at=past(0, 35),
            expires_at=future(15, 120),
        )
        recommendations.append(recommendation)

    if recommendations:
        await insert_many_batched(Recommendation, recommendations, BATCH_RECOMMENDATIONS)
    print(f"Recommendations seeded: {len(recommendations)}")
    return {u: info[0] for u, info in user_latest_evaluated.items()}


async def seed_conversations_tokens(role_ids: Dict[str, List[str]], course_map: Dict[str, List[str]]):
    profile_header("SEED CONVERSATIONS/TOKENS")
    conversations: List[Conversation] = []
    refresh_tokens: List[RefreshToken] = []
    reset_tokens: List[PasswordResetTokenDocument] = []
    active_users = await User.find({"status": "active"}).to_list()
    public_courses = course_map["public"]

    for sid in role_ids["student"]:
        for _ in range(random.randint(1, 4)):
            cid = random.choice(public_courses)
            msg_count = random.randint(4, 16)
            messages = []
            for i in range(msg_count):
                role = "user" if i % 2 == 0 else "assistant"
                messages.append({
                    "id": gid(),
                    "role": role,
                    "content": fake.sentence(nb_words=18) if role == "user" else fake.paragraph(nb_sentences=2),
                    "created_at": past(0, 40),
                })
            conv = Conversation(
                id=gid(),
                user_id=sid,
                course_id=cid,
                title=f"Discussion {fake.word().title()}",
                summary=fake.sentence(nb_words=18),
                course_title=f"Course {cid[:8]}",
                messages=messages,
                total_messages=len(messages),
                last_message_at=messages[-1]["created_at"],
                created_at=past(1, 60),
                updated_at=past(0, 15),
            )
            conversations.append(conv)

    for u in active_users:
        created = past(0, 10)
        refresh_tokens.append(
            RefreshToken(
                id=gid(),
                user_id=u.id,
                token=secrets.token_urlsafe(64),
                expires_at=created + timedelta(days=7),
                created_at=created,
            )
        )

    # seed một phần password reset tokens để phủ collection
    sample_users = random.sample(active_users, k=min(len(active_users), 14))
    for u in sample_users:
        created = past(0, 20)
        reset_tokens.append(
            PasswordResetTokenDocument(
                id=gid(),
                user_id=u.id,
                token=secrets.token_urlsafe(32),
                expires_at=created + timedelta(hours=24),
                used=random.choice([False, False, True]),
                created_at=created,
            )
        )

    if conversations:
        await insert_many_batched(Conversation, conversations, BATCH_CONVERSATIONS)
    if refresh_tokens:
        await insert_many_batched(RefreshToken, refresh_tokens, BATCH_TOKENS)
    if reset_tokens:
        await insert_many_batched(PasswordResetTokenDocument, reset_tokens, BATCH_TOKENS)

    print(f"Conversations seeded: {len(conversations)}")
    print(f"Refresh tokens seeded: {len(refresh_tokens)}")
    print(f"Password reset tokens seeded: {len(reset_tokens)}")


async def sync_classes_with_enrollments(class_ids: List[str]):
    profile_header("SYNC CLASS MEMBERSHIPS")
    classes = await Class.find({"_id": {"$in": class_ids}}).to_list()
    for c in classes:
        eligible = await Enrollment.find({
            "course_id": c.course_id,
            "status": {"$in": ["active", "completed"]},
        }).to_list()
        random.shuffle(eligible)
        selected = [e.user_id for e in eligible[: min(len(eligible), random.randint(20, min(c.max_students, 95)))]]
        c.student_ids = selected
        c.updated_at = now()
        await c.save()
    print(f"Classes synced: {len(classes)}")


async def validate_integrity() -> Dict[str, int]:
    profile_header("VALIDATE INTEGRITY")
    errors = 0

    users = await User.find().to_list()
    user_ids = {u.id for u in users}
    courses = await Course.find().to_list()
    course_ids = {c.id for c in courses}
    modules = await Module.find().to_list()
    module_ids = {m.id for m in modules}
    lessons = await Lesson.find().to_list()
    lesson_ids = {l.id for l in lessons}
    enrollments = await Enrollment.find().to_list()
    enrollment_ids = {e.id for e in enrollments}
    quizzes = await Quiz.find().to_list()
    quiz_ids = {q.id for q in quizzes}

    for c in courses:
        if c.owner_id not in user_ids:
            errors += 1
        if c.instructor_id and c.instructor_id not in user_ids:
            errors += 1
        if c.total_modules != len(c.modules):
            errors += 1

    for m in modules:
        if m.course_id not in course_ids:
            errors += 1
        for p in m.prerequisites:
            if p and p not in module_ids:
                errors += 1

    for l in lessons:
        if l.module_id not in module_ids:
            errors += 1
        if l.course_id not in course_ids:
            errors += 1
        if l.quiz_id and l.quiz_id not in quiz_ids:
            errors += 1

    for e in enrollments:
        if e.user_id not in user_ids or e.course_id not in course_ids:
            errors += 1
        if not (0.0 <= e.progress_percent <= 100.0):
            errors += 1

    progresses = await Progress.find().to_list()
    for p in progresses:
        if p.user_id not in user_ids or p.course_id not in course_ids or p.enrollment_id not in enrollment_ids:
            errors += 1
        if not (0.0 <= p.overall_progress_percent <= 100.0):
            errors += 1
        for lp in p.lessons_progress:
            if lp.lesson_id not in lesson_ids:
                errors += 1
            if lp.module_id and lp.module_id not in module_ids:
                errors += 1

    classes = await Class.find().to_list()
    for c in classes:
        if c.course_id not in course_ids or c.instructor_id not in user_ids:
            errors += 1
        for sid in c.student_ids:
            if sid not in user_ids:
                errors += 1

    assessments = await AssessmentSession.find().to_list()
    assessment_by_id = {a.id: a for a in assessments}

    recommendations = await Recommendation.find().to_list()
    for r in recommendations:
        if r.user_id not in user_ids:
            errors += 1
        for rc in r.recommended_courses:
            if rc.get("course_id") not in course_ids:
                errors += 1
        aid = r.assessment_session_id
        if aid:
            sess = assessment_by_id.get(aid)
            if sess is None:
                errors += 1
            elif (
                sess.proficiency_level
                and r.user_proficiency_level
                and sess.proficiency_level != r.user_proficiency_level
            ):
                errors += 1
        if r.source == "assessment" and not aid:
            errors += 1

    summary = {
        "users": len(users),
        "courses": len(courses),
        "modules": len(modules),
        "lessons": len(lessons),
        "enrollments": len(enrollments),
        "progress": len(progresses),
        "quizzes": len(quizzes),
        "quiz_attempts": await QuizAttempt.find().count(),
        "assessments": len(assessments),
        "recommendations": len(recommendations),
        "conversations": await Conversation.find().count(),
        "classes": len(classes),
        "refresh_tokens": await RefreshToken.find().count(),
        "password_reset_tokens": await PasswordResetTokenDocument.find().count(),
        "integrity_errors": errors,
    }
    for k, v in summary.items():
        print(f"{k}: {v}")
    return summary


async def seed_report_accounts():
    print("\nDemo accounts:")
    print("  Admin: admin1@ailearning.vn / Admin@123456")
    print("  Instructor: instructor1@ailearning.vn / Instructor@123")
    print("  Student: student1@gmail.com / Student@123")


async def main():
    cfg = SeedConfig()
    random.seed(cfg.seed)
    fake.seed_instance(cfg.seed)

    print("=" * 72)
    print("AI Learning Platform - Rebuilt Seed Data (x4, Full Reset)")
    print("=" * 72)
    print(f"Seed: {cfg.seed}")

    settings = get_settings()
    await init_database()
    print(f"MongoDB: {settings.mongodb_database}")

    await drop_all_collections()
    role_ids = await seed_users(cfg)
    domain = await seed_courses_modules_lessons(cfg, role_ids)
    class_ids = await seed_classes(cfg, role_ids, domain["course_map"])
    await seed_enrollments_progress(cfg, role_ids, domain["course_map"])
    await sync_classes_with_enrollments(class_ids)
    await seed_quizzes_attempts(cfg, role_ids)
    await seed_assessments_recommendations(role_ids, domain["course_map"])
    await seed_conversations_tokens(role_ids, domain["course_map"])
    summary = await validate_integrity()
    await seed_report_accounts()

    print("\n" + "=" * 72)
    print("SEED COMPLETED")
    print("=" * 72)
    if summary["integrity_errors"] > 0:
        print(f"WARNING: integrity_errors={summary['integrity_errors']}")
    else:
        print("Integrity checks: PASS")


if __name__ == "__main__":
    asyncio.run(main())

