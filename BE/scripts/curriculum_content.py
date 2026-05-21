"""
Catalog khóa học kiểu Coursera — nội dung thật, media cố định (Unsplash + YouTube URL).
Không upload storage: mọi thumbnail/preview/lesson video đều trỏ URL công khai ổn định.
"""

from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Media registry — ảnh & video theo danh mục (cố định, có nghĩa với chủ đề)
# ---------------------------------------------------------------------------

CATEGORY_MEDIA: Dict[str, Dict[str, Any]] = {
    "Programming": {
        "thumbnail": "https://images.unsplash.com/photo-1542831371-29b0f74f9713?w=1200&h=675&fit=crop&q=80",
        "preview_video_id": "rfscVS0vtbw",
        "lesson_video_ids": ["rfscVS0vtbw", "YYXdXT2l-GG", "_uQrJ0TkZlc", "W6NZfCO5SIk", "Ke90Tje7VS0"],
    },
    "Data Science": {
        "thumbnail": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&h=675&fit=crop&q=80",
        "preview_video_id": "YYXdXT2l-GG",
        "lesson_video_ids": ["YYXdXT2l-GG", "ua-CiDNNj0", "r-uOLxNrNk8", "aircAruvnKk"],
    },
    "Math": {
        "thumbnail": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=1200&h=675&fit=crop&q=80",
        "preview_video_id": "WUvTyaaNkzM",
        "lesson_video_ids": ["WUvTyaaNkzM", "fNk_zzaMoSs", "zIbNJdmW72k"],
    },
    "Business": {
        "thumbnail": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1200&h=675&fit=crop&q=80",
        "preview_video_id": "6sQDTgOu1-w",
        "lesson_video_ids": ["6sQDTgOu1-w", "6DXEPJB6XNE", "6sQDTgOu1-w"],
    },
    "Languages": {
        "thumbnail": "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=1200&h=675&fit=crop&q=80",
        "preview_video_id": "HAnw168huqA",
        "lesson_video_ids": ["HAnw168huqA", "k85mRPqvMbM", "z9Iwi8IfiX4"],
    },
    "Marketing": {
        "thumbnail": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1200&h=675&fit=crop&q=80",
        "preview_video_id": "9noqY5926nY",
        "lesson_video_ids": ["9noqY5926nY", "7CCh_bCpw0U", "GxwEyXIGkwk"],
    },
    "Engineering": {
        "thumbnail": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200&h=675&fit=crop&q=80",
        "preview_video_id": "SqcY0GlATPk",
        "lesson_video_ids": ["SqcY0GlATPk", "3c-iBn73dDE", "pTFZFxd4hOI", "RqTek2enlXo"],
    },
}

DEFAULT_PREREQUISITES: Dict[str, List[str]] = {
    "Beginner": [],
    "Intermediate": ["Hoàn thành khóa nền tảng cùng lĩnh vực hoặc tương đương 6 tháng thực hành"],
    "Advanced": [
        "Nắm vững kiến thức trung cấp",
        "Đã hoàn thành ít nhất một dự án thực tế trong lĩnh vực",
    ],
}


def youtube_watch(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def _lesson(
    title: str,
    content: str,
    objectives: List[str],
    content_type: str = "text",
    video_id: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "title": title,
        "description": objectives[0] if objectives else title,
        "content": content,
        "content_type": content_type,
        "objectives": objectives,
        "video_id": video_id,
    }


def _mod(title: str, description: str, lessons: List[Dict[str, Any]], outcomes: Optional[List[str]] = None) -> Dict[str, Any]:
    lo = [{"description": o, "skill_tag": o.lower().replace(" ", "-")[:40]} for o in (outcomes or [])]
    return {"title": title, "description": description, "lessons": lessons, "learning_outcomes": lo}


def _course(
    title: str,
    description: str,
    category: str,
    level: str,
    modules: List[Dict[str, Any]],
    outcomes: List[str],
    thumbnail: Optional[str] = None,
    preview_video_id: Optional[str] = None,
    prerequisites: Optional[List[str]] = None,
) -> Dict[str, Any]:
    media = CATEGORY_MEDIA.get(category, CATEGORY_MEDIA["Programming"])
    return {
        "title": title,
        "description": description,
        "category": category,
        "level": level,
        "modules": modules,
        "learning_outcomes": [{"description": o, "skill_tag": o.lower().replace(" ", "-")[:40]} for o in outcomes],
        "prerequisites": prerequisites if prerequisites is not None else DEFAULT_PREREQUISITES.get(level, []),
        "thumbnail_url": thumbnail or media["thumbnail"],
        "preview_video_id": preview_video_id or media["preview_video_id"],
    }


# ---------------------------------------------------------------------------
# Catalog — mỗi entry là một khóa học độc lập (tiêu đề + giáo trình thật)
# ---------------------------------------------------------------------------

COURSE_CATALOG: List[Dict[str, Any]] = [
    _course(
        "Python cho mọi người",
        "Học Python 3 từ con số 0: biến, hàm, cấu trúc dữ liệu, file và gọi API. Có bài tập mini sau mỗi module.",
        "Programming", "Beginner",
        [
            _mod("Tuần 1 — Cú pháp Python", "Biến, kiểu, toán tử, input/output.", [
                _lesson("Giới thiệu & cài đặt", "<h2>Bắt đầu</h2><p>Cài Python 3.11+, VS Code, chạy <code>print('Hello')</code>.</p>", ["Cài môi trường", "Chạy script đầu tiên"], "mixed", "rfscVS0vtbw"),
                _lesson("Biến và kiểu dữ liệu", "<h2>int, float, str, bool</h2><pre><code>price = 19.99\nname = 'An'</code></pre>", ["Khai báo biến", "Dùng f-string"]),
                _lesson("List và vòng lặp for", "<h2>Collection</h2><p>Duyệt list, sum, min, max.</p>", ["Dùng for", "List comprehension cơ bản"], "code"),
            ], ["Hiểu cú pháp Python cơ bản", "Viết script đơn giản"]),
            _mod("Tuần 2 — Hàm & module", "Tách code, import, xử lý lỗi.", [
                _lesson("Định nghĩa hàm", "<h2>def / return</h2><p>Tham số, default, docstring.</p>", ["Viết hàm tái sử dụng"]),
                _lesson("Module & pip", "<h2>import json, requests</h2><p>Cài package, virtualenv.</p>", ["Import chuẩn", "pip install"]),
                _lesson("try/except", "<h2>Xử lý lỗi</h2><p>Không nuốt exception.</p>", ["Bắt lỗi hợp lý"], "code"),
            ], ["Tổ chức code thành hàm"]),
            _mod("Tuần 3 — OOP & dự án", "Class, JSON, REST API nhỏ.", [
                _lesson("Class cơ bản", "<h2>OOP</h2><p>Class Task, method, attribute.</p>", ["Tạo class"]),
                _lesson("Đọc/ghi JSON", "<h2>json module</h2><p>Lưu cấu hình UTF-8.</p>", ["Serialize JSON"]),
                _lesson("Gọi REST API", "<h2>requests.get</h2><p>Public API, status_code.</p>", ["HTTP GET"], "mixed", "_uQrJ0TkZlc"),
            ], ["Hoàn thành mini project quản lý task"]),
        ],
        ["Viết chương trình Python độc lập", "Đọc tài liệu chính thức python.org", "Gọi API REST cơ bản"],
    ),
    _course(
        "JavaScript hiện đại (ES6+)",
        "Biến let/const, arrow function, promise/async-await, DOM và fetch API — nền tảng cho React.",
        "Programming", "Beginner",
        [
            _mod("Nền tảng JS", "Cú pháp ES6.", [
                _lesson("Biến & kiểu", "<h2>let, const</h2><p>Khác var, block scope.</p>", ["Dùng let/const"]),
                _lesson("Hàm & arrow", "<h2>=&gt;</h2><p>Callback, higher-order function.</p>", ["Arrow function"], "code"),
                _lesson("Array methods", "<h2>map, filter, reduce</h2>", ["Transform mảng"], "mixed", "W6NZfCO5SIk"),
            ], ["Viết JS ES6"]),
            _mod("Bất đồng bộ", "Promise, async/await.", [
                _lesson("Promise", "<h2>.then/.catch</h2>", ["Hiểu Promise"]),
                _lesson("async/await", "<h2>try/catch async</h2>", ["Viết async function"]),
                _lesson("fetch API", "<h2>GET JSON</h2>", ["Gọi REST từ browser"], "mixed"),
            ], ["Xử lý async"]),
        ],
        ["Viết JavaScript ES6+", "Gọi API từ trình duyệt"],
    ),
    _course(
        "React.js — Xây giao diện web",
        "Component, props, state, hooks (useState, useEffect), routing và gọi API trong ứng dụng SPA.",
        "Programming", "Intermediate",
        [
            _mod("React core", "JSX, component, props.", [
                _lesson("JSX & component", "<h2>Function component</h2>", ["Tạo component"]),
                _lesson("State với useState", "<h2>Counter app</h2>", ["Quản lý state"]),
                _lesson("useEffect", "<h2>Side effect</h2><p>Fetch khi mount.</p>", ["Lifecycle hooks"], "mixed", "Ke90Tje7VS0"),
            ], ["Xây UI bằng React"]),
            _mod("Routing & data", "React Router, loading state.", [
                _lesson("React Router", "<h2>Route, Link</h2>", ["Điều hướng SPA"]),
                _lesson("Form controlled", "<h2>Input + state</h2>", ["Form trong React"]),
                _lesson("Project structure", "<h2>pages, components</h2>", ["Tổ chức thư mục"], "code"),
            ], ["SPA routing"]),
        ],
        ["Xây SPA với React", "Tích hợp REST API"],
        prerequisites=["Biết HTML/CSS và JavaScript cơ bản"],
    ),
    _course(
        "Node.js & REST API với Express",
        "Xây backend REST: routing, middleware, validation, MongoDB cơ bản và deploy.",
        "Programming", "Intermediate",
        [
            _mod("Express fundamentals", "Route, middleware, JSON.", [
                _lesson("Hello Express", "<h2>app.get/post</h2>", ["Tạo server"]),
                _lesson("Middleware", "<h2>auth, logger</h2>", ["Pipeline request"]),
                _lesson("Validation", "<h2>Joi/Zod</h2>", ["Validate body"], "code"),
            ], ["API REST cơ bản"]),
            _mod("Database & auth", "MongoDB, JWT.", [
                _lesson("MongoDB CRUD", "<h2>Mongoose</h2>", ["Model & schema"]),
                _lesson("JWT auth", "<h2>Bearer token</h2>", ["Bảo vệ route"]),
                _lesson("Error handling", "<h2>Global handler</h2>", ["HTTP status đúng"], "mixed"),
            ], ["Persist data"]),
        ],
        ["Xây REST API production-ready", "JWT authentication"],
    ),
    _course(
        "Phân tích dữ liệu với Pandas",
        "Đọc CSV, làm sạch, groupby, merge và xuất báo cáo insight cho business.",
        "Data Science", "Beginner",
        [
            _mod("Pandas cơ bản", "DataFrame, Series.", [
                _lesson("read_csv & explore", "<h2>head, info, describe</h2>", ["Khám phá dataset"], "mixed", "YYXdXT2l-GG"),
                _lesson("Filter & sort", "<h2>Boolean index</h2>", ["Lọc dữ liệu"]),
                _lesson("groupby", "<h2>aggregate</h2>", ["Báo cáo theo nhóm"], "code"),
            ], ["Thao tác DataFrame"]),
            _mod("Làm sạch dữ liệu", "Missing, duplicate, types.", [
                _lesson("Missing values", "<h2>fillna/dropna</h2>", ["Chiến lược impute"]),
                _lesson("Chuẩn hóa cột", "<h2>rename, astype</h2>", ["Schema sạch"]),
                _lesson("merge tables", "<h2>inner/left join</h2>", ["Join 2 nguồn"]),
            ], ["Data cleaning"]),
        ],
        ["Phân tích CSV với Pandas", "Trình bày insight"],
    ),
    _course(
        "Machine Learning cơ bản",
        "Supervised learning: regression, classification, train/test split, metrics và overfitting.",
        "Data Science", "Intermediate",
        [
            _mod("ML workflow", "Pipeline sklearn.", [
                _lesson("Train/test split", "<h2>80/20</h2>", ["Tránh leak"]),
                _lesson("Linear regression", "<h2>MSE, R²</h2>", ["Regression"]),
                _lesson("Classification", "<h2>accuracy, F1</h2>", ["Phân loại"], "mixed", "aircAruvnKk"),
            ], ["Workflow ML"]),
            _mod("Tuning", "Cross-validation, overfitting.", [
                _lesson("Cross-validation", "<h2>k-fold</h2>", ["Đánh giá ổn định"]),
                _lesson("Regularization", "<h2>L1/L2</h2>", ["Giảm overfit"]),
                _lesson("Feature scaling", "<h2>StandardScaler</h2>", ["Chuẩn hóa feature"], "code"),
            ], ["Tối ưu model"]),
        ],
        ["Xây pipeline ML với scikit-learn", "Đánh giá model đúng cách"],
        prerequisites=["Python cơ bản", "Pandas cơ bản"],
    ),
    _course(
        "SQL cho Data Analyst",
        "SELECT, JOIN, GROUP BY, window functions và tối ưu truy vấn trên PostgreSQL.",
        "Data Science", "Beginner",
        [
            _mod("SQL cơ bản", "SELECT, WHERE, ORDER BY.", [
                _lesson("SELECT & filter", "<h2>WHERE, LIKE</h2>", ["Truy vấn cơ bản"]),
                _lesson("JOIN", "<h2>INNER/LEFT</h2>", ["Nối bảng"]),
                _lesson("GROUP BY", "<h2>HAVING</h2>", ["Tổng hợp"], "code"),
            ], ["Viết SQL"]),
            _mod("Nâng cao", "Window, CTE.", [
                _lesson("Window functions", "<h2>ROW_NUMBER</h2>", ["Ranking"]),
                _lesson("CTE", "<h2>WITH</h2>", ["Query dễ đọc"]),
                _lesson("Index basics", "<h2>EXPLAIN</h2>", ["Hiểu performance"], "mixed"),
            ], ["SQL nâng cao"]),
        ],
        ["Truy vấn SQL phức tạp", "Đọc execution plan cơ bản"],
    ),
    _course(
        "Đại số & phương trình",
        "Phương trình bậc nhất, bậc hai, hệ phương trình và bất phương trình — nền tảng toán THPT/đại học.",
        "Math", "Beginner",
        [
            _mod("Phương trình", "Một ẩn và hai ẩn.", [
                _lesson("Bậc nhất", "<h2>ax+b=0</h2>", ["Giải và kiểm tra"]),
                _lesson("Bậc hai", "<h2>Delta</h2>", ["Nghiệm parabol"], "mixed", "WUvTyaaNkzM"),
                _lesson("Hệ PT", "<h2>Thế, cộng</h2>", ["2 ẩn"]),
            ], ["Giải phương trình"]),
        ],
        ["Giải phương trình bậc nhất và bậc hai", "Giải hệ phương trình 2 ẩn"],
    ),
    _course(
        "Giải tích 1 — Đạo hàm",
        "Giới hạn, đạo hàm, quy tắc tính và ứng dụng cực trị.",
        "Math", "Intermediate",
        [
            _mod("Đạo hàm", "Definition & rules.", [
                _lesson("Giới hạn", "<h2>lim</h2>", ["Hiểu giới hạn"]),
                _lesson("Quy tắc đạo hàm", "<h2>product, chain</h2>", ["Tính đạo hàm"]),
                _lesson("Cực trị", "<h2>f'=0</h2>", ["Tối ưu"], "mixed"),
            ], ["Tính đạo hàm"]),
        ],
        ["Áp dụng đạo hàm tìm cực trị"],
        prerequisites=["Đại số cơ bản"],
    ),
    _course(
        "Quản trị dự án Agile",
        "Scrum, sprint planning, daily standup, retrospective và Jira workflow.",
        "Business", "Intermediate",
        [
            _mod("Scrum", "Roles, events, artifacts.", [
                _lesson("Scrum overview", "<h2>PO, SM, Dev</h2>", ["Hiểu vai trò"]),
                _lesson("Sprint planning", "<h2>Story point</h2>", ["Lập sprint"], "mixed", "6sQDTgOu1-w"),
                _lesson("Retro", "<h2>Start/Stop/Continue</h2>", ["Cải tiến team"]),
            ], ["Chạy sprint Scrum"]),
        ],
        ["Điều phối sprint Agile", "Facilitate retrospective"],
    ),
    _course(
        "OKR & KPI cho team",
        "Viết Objective/Key Result, tracking hàng tuần và dashboard cho lãnh đạo.",
        "Business", "Beginner",
        [
            _mod("OKR", "Framework.", [
                _lesson("Objective vs KR", "<h2>Measurable KR</h2>", ["Viết OKR"]),
                _lesson("Check-in", "<h2>Confidence</h2>", ["Theo dõi tiến độ"]),
            ], ["Triển khai OKR"]),
        ],
        ["Thiết kế OKR quý", "Báo cáo tiến độ KPI"],
    ),
    _course(
        "English for Developers",
        "Từ vựng kỹ thuật, đọc tài liệu API, viết commit message và thuyết trình ngắn.",
        "Languages", "Beginner",
        [
            _mod("Tech English", "Reading & writing.", [
                _lesson("API docs", "<h2>Skim README</h2>", ["Đọc docs nhanh"], "video", "HAnw168huqA"),
                _lesson("Commit messages", "<h2>Conventional commits</h2>", ["Viết commit rõ"]),
                _lesson("Stand-up", "<h2>Yesterday/Today</h2>", ["Nói 60 giây"], "video"),
            ], ["Giao tiếp công sở IT"]),
        ],
        ["Đọc tài liệu kỹ thuật tiếng Anh", "Thuyết trình stand-up"],
    ),
    _course(
        "Digital Marketing căn bản",
        "Funnel AIDA, persona, kênh owned/earned/paid và đo lường conversion.",
        "Marketing", "Beginner",
        [
            _mod("Marketing core", "Funnel & metrics.", [
                _lesson("AIDA funnel", "<h2>Awareness→Action</h2>", ["Hiểu funnel"]),
                _lesson("Persona", "<h2>JTBD</h2>", ["Xác định khách hàng"]),
                _lesson("KPI marketing", "<h2>CTR, CPA</h2>", ["Đo hiệu quả"], "mixed", "9noqY5926nY"),
            ], ["Digital marketing basics"]),
        ],
        ["Thiết kế chiến dịch digital", "Đọc metric cơ bản"],
    ),
    _course(
        "SEO & Content Strategy",
        "On-page SEO, keyword research, meta tags và content calendar.",
        "Marketing", "Intermediate",
        [
            _mod("SEO", "Technical & content.", [
                _lesson("Keyword research", "<h2>Intent</h2>", ["Chọn từ khóa"]),
                _lesson("On-page SEO", "<h2>title, h1, meta</h2>", ["Tối ưu trang"]),
                _lesson("Content calendar", "<h2>Editorial plan</h2>", ["Lên lịch content"], "code"),
            ], ["SEO on-page"]),
        ],
        ["Lập kế hoạch content SEO", "Tối ưu meta tags"],
    ),
    _course(
        "System Design cơ bản",
        "Scalability, load balancer, cache, database sharding và trade-off CAP.",
        "Engineering", "Advanced",
        [
            _mod("Scalability", "Horizontal vs vertical.", [
                _lesson("Load balancer", "<h2>Round robin</h2>", ["Phân tải"]),
                _lesson("Caching", "<h2>Redis</h2>", ["Giảm latency"], "mixed", "SqcY0GlATPk"),
                _lesson("Database scale", "<h2>Replication</h2>", ["Read replica"]),
            ], ["Thiết kế scalable"]),
            _mod("Reliability & CAP", "Consistency, availability, partition tolerance.", [
                _lesson("CAP theorem", "<h2>Trade-off</h2>", ["Hiểu CAP"]),
                _lesson("Failover", "<h2>Active-passive</h2>", ["High availability"]),
                _lesson("Monitoring", "<h2>SLI/SLO</h2>", ["Đo độ tin cậy"], "mixed"),
            ], ["Đánh đổi CAP"]),
            _mod("Storage & sharding", "Partition key, hot spots.", [
                _lesson("Sharding strategies", "<h2>Hash/range</h2>", ["Chia dữ liệu"]),
                _lesson("Hot partition", "<h2>Rebalance</h2>", ["Tránh hotspot"]),
                _lesson("Object storage", "<h2>S3 pattern</h2>", ["Blob & CDN"], "code"),
            ], ["Thiết kế lưu trữ phân tán"]),
            _mod("Messaging & async", "Queue, pub/sub, idempotency.", [
                _lesson("Message queue", "<h2>Kafka/RabbitMQ</h2>", ["Async workflow"]),
                _lesson("Event-driven", "<h2>Pub/sub</h2>", ["Loose coupling"]),
                _lesson("Idempotency", "<h2>Retry safe</h2>", ["Xử lý trùng lặp"]),
            ], ["Kiến trúc bất đồng bộ"]),
            _mod("API & gateway", "Rate limit, BFF, versioning.", [
                _lesson("API gateway", "<h2>Auth, routing</h2>", ["Cổng vào hệ thống"]),
                _lesson("Rate limiting", "<h2>Token bucket</h2>", ["Bảo vệ backend"]),
                _lesson("Versioning", "<h2>v1/v2</h2>", ["Evolve API"], "mixed"),
            ], ["Thiết kế API scale"]),
            _mod("Case study", "Thiết kế URL shortener / feed.", [
                _lesson("URL shortener", "<h2>Hash, redirect</h2>", ["Thiết kế end-to-end"]),
                _lesson("News feed", "<h2>Fan-out</h2>", ["Timeline design"]),
                _lesson("Review checklist", "<h2>Capacity</h2>", ["Ước lượng QPS"], "code"),
            ], ["Áp dụng system design"]),
        ],
        ["Thiết kế hệ thống phân tán cơ bản", "Đánh đổi consistency/availability"],
        prerequisites=["Kinh nghiệm backend 1+ năm"],
    ),
    _course(
        "Docker & Container",
        "Image, Dockerfile, docker-compose và deploy container local.",
        "Engineering", "Intermediate",
        [
            _mod("Docker", "Images & containers.", [
                _lesson("Dockerfile", "<h2>FROM, RUN, CMD</h2>", ["Build image"]),
                _lesson("docker-compose", "<h2>multi-service</h2>", ["Orchestrate local"]),
                _lesson("Volume & network", "<h2>Persistence</h2>", ["Data trong container"], "mixed", "3c-iBn73dDE"),
            ], ["Container hóa app"]),
        ],
        ["Đóng gói app với Docker", "Chạy stack bằng compose"],
    ),
    _course(
        "Git & GitHub Workflow",
        "Branch, merge, pull request, code review và resolve conflict.",
        "Engineering", "Beginner",
        [
            _mod("Git", "Version control.", [
                _lesson("commit & branch", "<h2>git checkout -b</h2>", ["Branch workflow"]),
                _lesson("Pull request", "<h2>Review</h2>", ["Collaborate trên GitHub"]),
                _lesson("Merge conflict", "<h2>resolve</h2>", ["Xử lý conflict"], "code"),
            ], ["Git collaboration"]),
        ],
        ["Làm việc nhóm với Git", "Tạo và review PR"],
    ),
    _course(
        "TypeScript cho dự án React",
        "Kiểu dữ liệu, interface, generic và type-safe props trong React.",
        "Programming", "Intermediate",
        [
            _mod("TypeScript", "Types & interfaces.", [
                _lesson("Basic types", "<h2>string, union</h2>", ["Annotate types"]),
                _lesson("Interface", "<h2>Props typing</h2>", ["Type React props"]),
                _lesson("Generic", "<h2>ApiResponse&lt;T&gt;</h2>", ["Generic cơ bản"], "code"),
            ], ["TypeScript in React"]),
        ],
        ["Viết React type-safe", "Thiết kế interface API"],
        prerequisites=["JavaScript ES6+", "React cơ bản"],
    ),
    _course(
        "Trực quan hóa dữ liệu",
        "Matplotlib, seaborn và storytelling với biểu đồ cho báo cáo business.",
        "Data Science", "Beginner",
        [
            _mod("Visualization", "Charts.", [
                _lesson("Line & bar chart", "<h2>matplotlib</h2>", ["Biểu đồ cơ bản"]),
                _lesson("Distribution", "<h2>histogram, box</h2>", ["Phân phối"]),
                _lesson("Storytelling", "<h2>chart junk</h2>", ["Biểu đồ rõ ràng"], "mixed"),
            ], ["Data viz"]),
        ],
        ["Chọn biểu đồ phù hợp", "Trình bày insight trực quan"],
    ),
    _course(
        "Xác suất thống kê",
        "Xác suất, phân phối, kiểm định giả thuyết và confidence interval.",
        "Math", "Intermediate",
        [
            _mod("Statistics", "Probability.", [
                _lesson("Xác suất cơ bản", "<h2>P(A∩B)</h2>", ["Quy tắc xác suất"]),
                _lesson("Phân phối", "<h2>Normal, Binomial</h2>", ["Distribution"]),
                _lesson("Hypothesis test", "<h2>p-value</h2>", ["Kiểm định"], "mixed"),
            ], ["Thống kê suy luận"]),
        ],
        ["Áp dụng kiểm định giả thuyết", "Hiểu p-value"],
    ),
    _course(
        "Tài chính doanh nghiệp",
        "Báo cáo tài chính, dòng tiền, ROI và đọc balance sheet.",
        "Business", "Beginner",
        [
            _mod("Financial statements", "3 báo cáo.", [
                _lesson("Balance sheet", "<h2>Assets = L + E</h2>", ["Đọc B/S"]),
                _lesson("Income statement", "<h2>Revenue, margin</h2>", ["P&L"]),
                _lesson("Cash flow", "<h2>Operating CF</h2>", ["Dòng tiền"]),
            ], ["Đọc báo cáo TC"]),
        ],
        ["Phân tích báo cáo tài chính cơ bản"],
    ),
    _course(
        "Performance Marketing",
        "Facebook/Google Ads, pixel, conversion tracking và A/B test creative.",
        "Marketing", "Advanced",
        [
            _mod("Paid ads", "Campaign structure.", [
                _lesson("Campaign setup", "<h2>Objective, budget</h2>", ["Tạo campaign"]),
                _lesson("Pixel & events", "<h2>Conversion API</h2>", ["Tracking"]),
                _lesson("A/B creative", "<h2>CTR, CPA</h2>", ["Tối ưu creative"], "mixed"),
            ], ["Paid media"]),
        ],
        ["Chạy campaign performance", "Đo conversion"],
        prerequisites=["Digital Marketing căn bản"],
    ),
    _course(
        "AWS Cloud Practitioner",
        "EC2, S3, IAM, VPC overview và mô hình pricing AWS.",
        "Engineering", "Beginner",
        [
            _mod("AWS core", "Services.", [
                _lesson("IAM", "<h2>User, role, policy</h2>", ["Least privilege"]),
                _lesson("EC2 & S3", "<h2>Compute & storage</h2>", ["Core services"], "mixed", "pTFZFxd4hOI"),
                _lesson("VPC basics", "<h2>Subnet, SG</h2>", ["Networking intro"]),
            ], ["AWS fundamentals"]),
        ],
        ["Hiểu dịch vụ AWS core", "Thiết kế IAM an toàn"],
    ),
    _course(
        "Linear Algebra cho Machine Learning",
        "Vector, matrix, dot product, eigenvalues — nền tảng cho ML/deep learning.",
        "Math", "Advanced",
        [
            _mod("Linear algebra", "Vectors & matrices.", [
                _lesson("Vectors", "<h2>dot product</h2>", ["Vector ops"]),
                _lesson("Matrix multiply", "<h2>dim check</h2>", ["Matrix algebra"]),
                _lesson("Eigenvalues intro", "<h2>PCA link</h2>", ["Dimensionality"], "code"),
            ], ["LA for ML"]),
        ],
        ["Thao tác ma trận cho ML"],
        prerequisites=["Đại số cơ bản", "Giải tích cơ bản"],
    ),
    _course(
        "DevOps CI/CD",
        "GitHub Actions, pipeline test/build/deploy và blue-green deploy.",
        "Engineering", "Intermediate",
        [
            _mod("CI/CD", "Pipeline.", [
                _lesson("GitHub Actions", "<h2>workflow yaml</h2>", ["CI pipeline"]),
                _lesson("Test stage", "<h2>pytest/jest</h2>", ["Quality gate"]),
                _lesson("Deploy", "<h2>staging→prod</h2>", ["CD basics"], "mixed", "RqTek2enlXo"),
            ], ["Automate delivery"]),
        ],
        ["Thiết lập pipeline CI/CD", "Deploy tự động"],
        prerequisites=["Git", "Docker cơ bản"],
    ),
    _course(
        "Business English — Email & Meetings",
        "Viết email chuyên nghiệp, agenda họp và follow-up minutes.",
        "Languages", "Intermediate",
        [
            _mod("Professional English", "Writing.", [
                _lesson("Email structure", "<h2>Subject, ask, deadline</h2>", ["Professional email"], "video"),
                _lesson("Meeting agenda", "<h2>timebox</h2>", ["Facilitate meeting"]),
                _lesson("Minutes", "<h2>action items</h2>", ["Ghi biên bản"]),
            ], ["Business communication"]),
        ],
        ["Viết email và tài liệu họp bằng tiếng Anh"],
    ),
    _course(
        "Java OOP & Design Patterns",
        "Class hierarchy, interface, Singleton, Factory và SOLID principles.",
        "Programming", "Advanced",
        [
            _mod("OOP Java", "Classes.", [
                _lesson("Class & inheritance", "<h2>extends</h2>", ["OOP Java"]),
                _lesson("Interface", "<h2>implements</h2>", ["Abstraction"]),
                _lesson("SOLID intro", "<h2>SRP, DIP</h2>", ["Clean design"], "code"),
            ], ["OOP patterns"]),
            _mod("Design patterns", "Creational & structural.", [
                _lesson("Singleton/Factory", "<h2>when to use</h2>", ["Creational"]),
                _lesson("Observer", "<h2>event-driven</h2>", ["Behavioral"]),
                _lesson("Refactoring", "<h2>code smell</h2>", ["Maintain code"], "mixed"),
            ], ["Design patterns"]),
        ],
        ["Áp dụng design pattern", "Viết Java OOP sạch"],
        prerequisites=["Lập trình hướng đối tượng cơ bản"],
    ),
    _course(
        "Deep Learning giới thiệu",
        "Neural network, backprop, CNN intro và transfer learning với PyTorch/TensorFlow overview.",
        "Data Science", "Advanced",
        [
            _mod("Neural nets", "Basics.", [
                _lesson("Perceptron → MLP", "<h2>layers</h2>", ["NN architecture"]),
                _lesson("Backprop intuition", "<h2>gradient</h2>", ["Training loop"]),
                _lesson("CNN intro", "<h2>conv, pool</h2>", ["Image models"], "mixed"),
            ], ["Deep learning basics"]),
        ],
        ["Hiểu kiến trúc neural network", "Transfer learning cơ bản"],
        prerequisites=["Machine Learning cơ bản", "Linear Algebra"],
    ),
    _course(
        "Leadership cho Team Lead",
        "1-on-1, feedback, delegation và xử lý xung đột trong team kỹ thuật.",
        "Business", "Advanced",
        [
            _mod("Leadership", "People skills.", [
                _lesson("1-on-1", "<h2>coaching questions</h2>", ["Effective 1:1"]),
                _lesson("Feedback", "<h2>SBI model</h2>", ["Constructive feedback"]),
                _lesson("Delegation", "<h2>ownership</h2>", ["Scale team"], "mixed"),
            ], ["Tech leadership"]),
        ],
        ["Dẫn dắt team kỹ thuật", "Feedback hiệu quả"],
        prerequisites=["2+ năm kinh nghiệm làm việc nhóm"],
    ),
    _course(
        "C++ cơ bản cho lập trình viên",
        "Con trỏ, reference, STL vector/map và quản lý bộ nhơ — nền tảng cho hệ thống và game.",
        "Programming", "Intermediate",
        [
            _mod("C++ core", "Syntax & memory.", [
                _lesson("Pointer & reference", "<h2>* và &</h2><p>Stack vs heap, tránh dangling pointer.</p>", ["Hiểu pointer"]),
                _lesson("STL containers", "<h2>vector, map</h2><p>Iterator, auto keyword.</p>", ["Dùng STL"]),
                _lesson("RAII", "<h2>smart pointer</h2><p>unique_ptr, shared_ptr.</p>", ["Quản lý memory"], "code"),
            ], ["C++ fundamentals"]),
        ],
        ["Viết chương trình C++ an toàn bộ nhớ", "Dùng STL hiệu quả"],
        prerequisites=["Biết ít nhất một ngôn ngữ lập trình"],
    ),
    _course(
        "Go (Golang) — Backend hiệu năng cao",
        "Goroutine, channel, HTTP server và cấu trúc project Go chuẩn cho microservice.",
        "Programming", "Intermediate",
        [
            _mod("Go basics", "Concurrency.", [
                _lesson("Syntax & struct", "<h2>package main</h2>", ["Go syntax"]),
                _lesson("Goroutine & channel", "<h2>go func()</h2>", ["Concurrency Go"]),
                _lesson("HTTP server", "<h2>net/http</h2>", ["REST nhỏ với Go"], "mixed", "YS4e4qUKX90"),
            ], ["Go backend"]),
        ],
        ["Xây API Go concurrent", "Thiết kế goroutine an toàn"],
    ),
    _course(
        "Flutter & Dart — Mobile đa nền tảng",
        "Widget tree, stateful/stateless, layout và gọi API trong app iOS/Android từ một codebase.",
        "Programming", "Intermediate",
        [
            _mod("Flutter UI", "Widgets.", [
                _lesson("Widget tree", "<h2>StatelessWidget</h2>", ["Cấu trúc UI Flutter"]),
                _lesson("State management", "<h2>setState, Provider</h2>", ["Quản lý state"]),
                _lesson("Navigation & API", "<h2>Navigator, http</h2>", ["App hoàn chỉnh"], "mixed"),
            ], ["Flutter mobile"]),
        ],
        ["Xây app Flutter đa nền tảng", "Tích hợp REST API"],
        prerequisites=["OOP và Dart/JavaScript cơ bản"],
    ),
    _course(
        "Vue.js 3 — Progressive Framework",
        "Composition API, reactivity, Vue Router và Pinia store cho SPA quy mô vừa.",
        "Programming", "Intermediate",
        [
            _mod("Vue 3", "Composition API.", [
                _lesson("ref & reactive", "<h2>setup()</h2>", ["Reactivity Vue 3"]),
                _lesson("Components & props", "<h2>emit, slots</h2>", ["Component design"]),
                _lesson("Pinia store", "<h2>state/actions</h2>", ["Global state"], "code"),
            ], ["Vue SPA"]),
        ],
        ["Xây SPA với Vue 3", "Quản lý state bằng Pinia"],
        prerequisites=["HTML, CSS, JavaScript ES6+"],
    ),
    _course(
        "MongoDB & NoSQL cơ bản",
        "Document model, CRUD, aggregation pipeline và schema design cho ứng dụng web.",
        "Programming", "Beginner",
        [
            _mod("MongoDB", "Documents.", [
                _lesson("Document model", "<h2>JSON/BSON</h2>", ["NoSQL vs SQL"]),
                _lesson("CRUD & index", "<h2>find, insert</h2>", ["Truy vấn MongoDB"]),
                _lesson("Aggregation", "<h2>$match, $group</h2>", ["Pipeline báo cáo"], "code"),
            ], ["MongoDB basics"]),
        ],
        ["Thiết kế schema MongoDB", "Viết aggregation pipeline"],
    ),
    _course(
        "NLP cơ bản với Python",
        "Tokenization, TF-IDF, sentiment analysis và giới thiệu transformer cho text classification.",
        "Data Science", "Intermediate",
        [
            _mod("Text processing", "NLP pipeline.", [
                _lesson("Tokenization", "<h2>NLTK/spaCy</h2>", ["Chuẩn hóa text"]),
                _lesson("TF-IDF & BoW", "<h2>Vector hóa</h2>", ["Feature text"]),
                _lesson("Sentiment", "<h2>classifier</h2>", ["Phân loại cảm xúc"], "mixed"),
            ], ["NLP workflow"]),
        ],
        ["Xử lý văn bản với Python", "Xây classifier sentiment cơ bản"],
        prerequisites=["Python cơ bản", "Pandas cơ bản"],
    ),
    _course(
        "Apache Spark cho Big Data",
        "RDD, DataFrame, Spark SQL và xử lý batch trên dataset lớn với PySpark.",
        "Data Science", "Advanced",
        [
            _mod("PySpark", "Distributed compute.", [
                _lesson("Spark architecture", "<h2>driver, executor</h2>", ["Hiểu Spark"]),
                _lesson("DataFrame API", "<h2>select, filter</h2>", ["PySpark DataFrame"]),
                _lesson("Spark SQL", "<h2>temp view</h2>", ["Query phân tán"], "code"),
            ], ["Big data processing"]),
        ],
        ["Xử lý dữ liệu lớn với Spark", "Viết job PySpark"],
        prerequisites=["Python", "SQL cơ bản"],
    ),
    _course(
        "Power BI cho Business Analyst",
        "Import data, DAX measure, visualization và publish dashboard cho stakeholder.",
        "Data Science", "Beginner",
        [
            _mod("Power BI", "Dashboards.", [
                _lesson("Get data", "<h2>Power Query</h2>", ["Import & transform"]),
                _lesson("DAX basics", "<h2>CALCULATE, SUM</h2>", ["Measure & column"]),
                _lesson("Publish report", "<h2>share, refresh</h2>", ["Dashboard business"], "mixed"),
            ], ["BI reporting"]),
        ],
        ["Tạo dashboard Power BI", "Viết DAX measure cơ bản"],
    ),
    _course(
        "Giải tích 2 — Tích phân & chuỗi",
        "Tích phân xác định/bất định, ứng dụng diện tích thể tích và chuỗi số.",
        "Math", "Intermediate",
        [
            _mod("Calculus II", "Integration.", [
                _lesson("Tích phân bất định", "<h2>u-substitution</h2>", ["Nguyên hàm"]),
                _lesson("Tích phân xác định", "<h2>FTC</h2>", ["Diện tích dưới đường cong"]),
                _lesson("Chuỗi số", "<h2>convergence</h2>", ["Chuỗi hội tụ"], "mixed"),
            ], ["Calculus applications"]),
        ],
        ["Tính tích phân và ứng dụng", "Phân tích chuỗi số"],
        prerequisites=["Giải tích 1 — Đạo hàm"],
    ),
    _course(
        "Toán rời rạc cho CNTT",
        "Logic, tập hợp, đồ thị, cây và thuật toán đếm — nền tảng CS và phỏng vấn.",
        "Math", "Beginner",
        [
            _mod("Discrete math", "Logic & graphs.", [
                _lesson("Logic & proof", "<h2>∀, ∃, contrapositive</h2>", ["Chứng minh cơ bản"]),
                _lesson("Set & combinatorics", "<h2>C(n,k), pigeonhole</h2>", ["Đếm tổ hợp"]),
                _lesson("Graph basics", "<h2>BFS, DFS</h2>", ["Đồ thị trong CS"], "code"),
            ], ["Discrete foundations"]),
        ],
        ["Áp dụng logic và đồ thị", "Giải bài toán đếm"],
    ),
    _course(
        "Product Management căn bản",
        "Discovery, user story, roadmap, prioritization (RICE) và làm việc với design/engineering.",
        "Business", "Beginner",
        [
            _mod("Product discovery", "Problem-solution.", [
                _lesson("Problem interview", "<h2>Jobs to be done</h2>", ["Validate problem"]),
                _lesson("User story & AC", "<h2>As a user...</h2>", ["Viết story rõ"]),
                _lesson("Roadmap & RICE", "<h2>score, timeline</h2>", ["Ưu tiên feature"], "mixed"),
            ], ["PM workflow"]),
        ],
        ["Viết user story chất lượng", "Lập roadmap sản phẩm"],
    ),
    _course(
        "Lean Startup & MVP",
        "Build-Measure-Learn, MVP, pivot và metric pirate (AARRR) cho startup/sản phẩm mới.",
        "Business", "Intermediate",
        [
            _mod("Lean startup", "Experiment.", [
                _lesson("MVP types", "<h2>concierge, smoke test</h2>", ["Thiết kế MVP"]),
                _lesson("Build-Measure-Learn", "<h2>hypothesis</h2>", ["Vòng lặp học"]),
                _lesson("AARRR metrics", "<h2>acquisition→revenue</h2>", ["Growth metrics"]),
            ], ["Lean methodology"]),
        ],
        ["Thiết kế MVP có thể đo lường", "Ra quyết định pivot dựa trên data"],
    ),
    _course(
        "IELTS Speaking cơ bản",
        "Part 1/2/3 structure, fluency, vocabulary topic và practice cue card có feedback.",
        "Languages", "Beginner",
        [
            _mod("IELTS Speaking", "3 parts.", [
                _lesson("Part 1 — familiar topics", "<h2>extend answer</h2>", ["Trả lời 2-3 câu"], "video", "z9Iwi8IfiX4"),
                _lesson("Part 2 — cue card", "<h2>1 min prep</h2>", ["Structure 2 phút"], "video"),
                _lesson("Part 3 — discussion", "<h2>opinion + example</h2>", ["Thảo luận sâu"]),
            ], ["IELTS speaking"]),
        ],
        ["Trình bày cue card IELTS", "Mở rộng câu trả lời Part 1"],
    ),
    _course(
        "Tiếng Nhật N5 — Hiragana & cơ bản",
        "Bảng Hiragana/Katakana, chào hỏi, số đếm và cấu trúc câu は・を cơ bản.",
        "Languages", "Beginner",
        [
            _mod("N5 basics", "Scripts & grammar.", [
                _lesson("Hiragana", "<h2>46 ký tự</h2>", ["Đọc Hiragana"]),
                _lesson("Katakana intro", "<h2>loan words</h2>", ["Đọc Katakana"]),
                _lesson("Grammar は・を", "<h2>わたしは...です</h2>", ["Câu cơ bản"], "video"),
            ], ["Japanese N5"]),
        ],
        ["Đọc Hiragana/Katakana", "Tạo câu N5 cơ bản"],
    ),
    _course(
        "Social Media Marketing",
        "Chiến lược nội dung Facebook/LinkedIn/TikTok, lịch đăng và community management.",
        "Marketing", "Intermediate",
        [
            _mod("Social channels", "Content plan.", [
                _lesson("Platform fit", "<h2>B2B vs B2C</h2>", ["Chọn kênh"]),
                _lesson("Content calendar", "<h2>hook, CTA</h2>", ["Lên lịch đăng"]),
                _lesson("Community mgmt", "<h2>reply, crisis</h2>", ["Engagement"], "mixed", "7CCh_bCpw0U"),
            ], ["Social marketing"]),
        ],
        ["Lập kế hoạch social media", "Đo engagement cơ bản"],
        prerequisites=["Digital Marketing căn bản"],
    ),
    _course(
        "Brand Strategy & Positioning",
        "Brand pyramid, positioning statement, tone of voice và brand guideline cho team marketing.",
        "Marketing", "Advanced",
        [
            _mod("Brand building", "Strategy.", [
                _lesson("Positioning", "<h2>for X who Y</h2>", ["Positioning statement"]),
                _lesson("Tone of voice", "<h2>do/don't</h2>", ["Brand voice"]),
                _lesson("Brand guideline", "<h2>logo, color</h2>", ["Tài liệu brand"], "mixed"),
            ], ["Brand strategy"]),
        ],
        ["Xây positioning rõ ràng", "Soạn brand guideline ngắn"],
    ),
    _course(
        "Kubernetes cơ bản",
        "Pod, Deployment, Service, ConfigMap và kubectl — chạy app container trên cluster.",
        "Engineering", "Advanced",
        [
            _mod("K8s core", "Orchestration.", [
                _lesson("Pod & Deployment", "<h2>replicas</h2>", ["Deploy workload"]),
                _lesson("Service & Ingress", "<h2>ClusterIP, LB</h2>", ["Expose app"]),
                _lesson("ConfigMap/Secret", "<h2>env inject</h2>", ["Cấu hình app"], "mixed"),
            ], ["Kubernetes ops"]),
        ],
        ["Triển khai app lên Kubernetes", "Debug pod/service cơ bản"],
        prerequisites=["Docker & Container"],
    ),
    _course(
        "Bảo mật Web — OWASP Top 10",
        "XSS, SQL injection, CSRF, auth flaws và checklist hardening cho ứng dụng web.",
        "Engineering", "Intermediate",
        [
            _mod("Web security", "OWASP.", [
                _lesson("Injection", "<h2>SQLi, parameterized</h2>", ["Phòng injection"]),
                _lesson("XSS & CSRF", "<h2>CSP, token</h2>", ["Client-side attacks"]),
                _lesson("Auth & session", "<h2>JWT pitfalls</h2>", ["Secure auth"], "code"),
            ], ["Secure web apps"]),
        ],
        ["Nhận diện OWASP Top 10", "Áp dụng biện pháp phòng thủ"],
        prerequisites=["Web development cơ bản"],
    ),
    _course(
        "Microservices Architecture",
        "Service boundary, API gateway, event-driven, saga pattern và trade-off monolith vs micro.",
        "Engineering", "Advanced",
        [
            _mod("Microservices", "Design.", [
                _lesson("Service boundary", "<h2>DDD bounded context</h2>", ["Chia service"]),
                _lesson("API gateway", "<h2>routing, auth</h2>", ["Edge layer"]),
                _lesson("Saga & events", "<h2>async, eventual</h2>", ["Distributed transactions"], "mixed"),
            ], ["Microservices design"]),
        ],
        ["Thiết kế kiến trúc microservices", "Chọn pattern phù hợp"],
        prerequisites=["REST API", "System Design cơ bản"],
    ),
]


def get_course_blueprint(index: int) -> Dict[str, Any]:
    """Chọn khóa từ catalog; lặp có nhãn cohort khi index vượt số khóa unique."""
    cat_size = len(COURSE_CATALOG)
    base = COURSE_CATALOG[index % cat_size]
    cohort = (index // cat_size) + 1
    title = base["title"]
    if cohort > 1:
        title = f"{title} (Cohort {cohort})"
    return {
        **base,
        "title": title,
        "modules": base["modules"],
    }


def pick_module(index: int, pack: Dict[str, Any]) -> Dict[str, Any]:
    modules = pack.get("modules") or []
    if not modules:
        return {"title": "Module 1", "description": "", "lessons": [], "learning_outcomes": []}
    base = modules[index % len(modules)]
    cycle = index // len(modules)
    if cycle == 0:
        return base
    mod = dict(base)
    mod["title"] = f"{base.get('title', 'Module')} — Phần {cycle + 1}"
    return mod


def pick_lesson(module: Dict[str, Any], lesson_index: int) -> Dict[str, Any]:
    lessons = module.get("lessons") or []
    if not lessons:
        return {
            "title": f"Bài {lesson_index + 1}",
            "description": "Nội dung bài học",
            "content": "<p>Nội dung bài học.</p>",
            "content_type": "text",
            "objectives": ["Hoàn thành bài học"],
            "video_id": None,
        }
    return lessons[lesson_index % len(lessons)]


def get_course_thumbnail(pack: Dict[str, Any]) -> str:
    return pack.get("thumbnail_url") or CATEGORY_MEDIA.get(pack.get("category", "Programming"), {})["thumbnail"]


def get_course_preview_url(pack: Dict[str, Any]) -> str:
    vid = pack.get("preview_video_id") or CATEGORY_MEDIA.get(pack.get("category", "Programming"), {})["preview_video_id"]
    return youtube_watch(vid)


def get_lesson_video_url(pack: Dict[str, Any], lesson_tpl: Dict[str, Any], lesson_index: int) -> Optional[str]:
    if lesson_tpl.get("video_id"):
        return youtube_watch(lesson_tpl["video_id"])
    cat = pack.get("category", "Programming")
    ids = CATEGORY_MEDIA.get(cat, CATEGORY_MEDIA["Programming"]).get("lesson_video_ids", [])
    if not ids:
        return None
    return youtube_watch(ids[lesson_index % len(ids)])


def get_course_learning_outcomes(pack: Dict[str, Any]) -> List[dict]:
    return list(pack.get("learning_outcomes") or [])


def get_course_prerequisites(pack: Dict[str, Any]) -> List[str]:
    return list(pack.get("prerequisites") or [])


def get_module_learning_outcomes(mod_tpl: Dict[str, Any]) -> List[dict]:
    raw = mod_tpl.get("learning_outcomes") or []
    result = []
    for item in raw:
        if isinstance(item, dict):
            result.append({
                "description": item.get("description") or item.get("outcome") or "Hoàn thành module",
                "skill_tag": item.get("skill_tag") or "module-outcome",
            })
        elif isinstance(item, str):
            result.append({"description": item, "skill_tag": item.lower().replace(" ", "-")[:40]})
    return result or [{"description": mod_tpl.get("title") or "Hoàn thành module", "skill_tag": "module-complete"}]
