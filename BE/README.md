# Backend — AI Learning Platform

API server bằng **FastAPI** chạy trên **Uvicorn** (ASGI), dùng **MongoDB + Beanie ODM** và tích hợp **Google Gemini** cho assessment / quiz / AI tutor. Đăng ký **90 endpoint** (1 `/health` + 89 dưới `/api/v1`) cho 3 role: `student / instructor / admin`.

> Tài liệu này tập trung vào **Backend**. Setup nhanh có sẵn ở [`QUICKSTART.md`](QUICKSTART.md). API reference chi tiết: [`../docs/API.md`](../docs/API.md). Toàn cảnh hệ thống: [`../README.md`](../README.md).

---

## 1. Tech stack

| Lớp | Thư viện | Phiên bản |
|------|---------|-----------|
| Framework | `fastapi`, `uvicorn[standard]` | 0.116.2 / 0.35.0 |
| Validation / Settings | `pydantic`, `pydantic-settings`, `email-validator` | 2.11.1 / 2.10.1 / 2.0.0 |
| Database (async) | `motor`, `pymongo`, `dnspython`, `beanie` (ODM) | 3.6.0 / 4.9.1 / 2.7.0 / 1.27.0 |
| Auth | `python-jose[cryptography]` (JWT), `passlib[bcrypt]`, `bcrypt` (pin) | 3.3.0 / 1.7.4 / 3.2.2 |
| File / Upload | `python-multipart`, `aiofiles`, `python-magic`, `python-magic-bin` (Win) | 0.0.20 / 24.1.0 / 0.4.27 |
| AI | `google-generativeai`, `google-auth` | 0.8.3 / 2.40.3 |
| HTTP / Env | `httpx`, `python-dotenv` | 0.28.1 / 1.0.0 |
| Test / Dev | `pytest`, `pytest-asyncio`, `coverage`, `Faker` | 8.4.2 / 0.24.0 / 7.6.4 / 25.9.1 |

Nguồn: [`requirements.txt`](requirements.txt). Python 3.11+.

---

## 2. Yêu cầu môi trường

- **Python**: 3.11+.
- **MongoDB**: 6 hoặc 7 (local, Atlas, hoặc docker-compose kèm theo).
- **Google Gemini API key**: lấy ở https://aistudio.google.com/app/apikey.
- **Tùy chọn**: Redis (cho cache/session — hiện chưa wire vào code), SendGrid/SMTP (cho email — feature flag).

---

## 3. Setup nhanh

Đã có hướng dẫn từng bước ở [`QUICKSTART.md`](QUICKSTART.md). Tóm tắt:

```powershell
cd BE
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

copy .env.example .env
# sua SECRET_KEY, MONGODB_URL, GOOGLE_API_KEY trong .env

uvicorn app.main:app --reload
# hoac: python -m uvicorn app.main:app --reload
```

Mở `http://localhost:8000/docs` để xem Swagger UI và thử endpoint.

> Lưu ý so với `QUICKSTART.md`: biến môi trường JWT thực tế là **`SECRET_KEY`** (không phải `JWT_SECRET_KEY`) — xem `config/config.py`. Trong `.env`, set `SECRET_KEY=...`.

---

## 4. Biến môi trường (`BE/.env`)

Tất cả được Pydantic Settings đọc trong [`config/config.py`](config/config.py).

| Nhóm | Key | Bắt buộc | Mặc định |
|------|-----|----------|----------|
| App | `APP_NAME` | – | `AI Learning Platform API` |
| App | `ENVIRONMENT` | – | `development` |
| App | `DEBUG`, `TESTING` | – | `false / false` |
| **JWT** | **`SECRET_KEY`** | **Có** | – (Field bắt buộc — app sẽ throw nếu thiếu) |
| JWT | `ALGORITHM` | – | `HS256` |
| JWT | `ACCESS_TOKEN_EXPIRE_MINUTES` | – | `15` |
| JWT | `REFRESH_TOKEN_EXPIRE_DAYS` | – | `7` |
| DB | `MONGODB_URL` | – | `mongodb://localhost:27017` |
| DB | `MONGODB_DATABASE` | – | `ai_learning_app` |
| **AI** | **`GOOGLE_API_KEY`** | **Có** | – (Field bắt buộc) |
| AI | `GEMINI_MODEL` | – | `gemini-1.5-pro` (code) — `gemini-2.5-flash` (`.env.example`) |
| Cache | `REDIS_URL` | – | `redis://localhost:6379/0` |
| CORS | `ALLOWED_ORIGINS` | – | `["http://localhost:3000", "http://localhost:5173"]` |
| Email | `SENDGRID_API_KEY`, `FROM_EMAIL`, `SMTP_HOST/PORT/USER/PASSWORD` | – | – / `noreply@ailearning.com` |
| File | `STORAGE_TYPE`, `UPLOAD_DIR`, `MAX_UPLOAD_SIZE_MB`, `S3_*` | – | `local / ./uploads / 50 / –` |
| Security | `RATE_LIMIT_PER_MINUTE`, `BCRYPT_ROUNDS` | – | `100 / 12` |
| Log | `LOG_LEVEL`, `SENTRY_DSN` | – | `INFO / –` |
| Feature | `ENABLE_AI_CHAT`, `ENABLE_EMAIL_NOTIFICATIONS`, `ENABLE_VECTOR_SEARCH` | – | `true / true / false` |

`SECRET_KEY` và `GOOGLE_API_KEY` được khai báo `Field(..., alias=...)` → nếu thiếu, app sẽ raise ngay khi load Settings (xem mục **Troubleshooting**).

---

## 5. Chạy ứng dụng

### 5.1 Local (dev)

```powershell
uvicorn app.main:app --reload
# hoac
python -m uvicorn app.main:app --reload --port 8000
```

- `--reload` bật auto-reload khi sửa code (không khuyến nghị production).
- Mặc định bind `0.0.0.0:8000`.
- Swagger UI: `/docs`. ReDoc: `/redoc`. Health: `/health`.

### 5.2 Docker Compose

File [`docker-compose.yml`](docker-compose.yml) cấp 2 service:

| Service | Image | Ports | Ghi chú |
|---------|-------|-------|---------|
| `api` | build từ `BE/Dockerfile` (nếu có) | `8000:8000` | đọc `BE/.env`, depends on mongodb |
| `mongodb` | `mongo:7.0` | `27017:27017` | volume `mongo_data`, root user `admin / admin123` |

```powershell
cd BE
docker compose up --build
```

> Chú ý: image MongoDB compose dùng auth `admin/admin123`, **`MONGODB_URL`** trong `.env` cần dạng `mongodb://admin:admin123@mongodb:27017/?authSource=admin` khi chạy trong docker network.

---

## 6. Cấu trúc thư mục

```
BE/
├── app/
│   ├── main.py              # FastAPI app, lifespan, CORS, include router
│   ├── database.py          # init_beanie + Motor client lifecycle
│   └── __init__.py
├── controllers/             # Business orchestration cho HTTP handler
├── routers/                 # FastAPI APIRouter + Swagger metadata
│   └── routers.py           # registry tap hop 15 router
├── services/                # Logic nghiep vu + AI prompts
│   └── ai_service.py        # Wrapper Gemini cho assessment/quiz/chat
├── models/                  # Beanie Document (Mongo collections)
├── schemas/                 # Pydantic request/response DTO
├── middleware/
│   ├── auth.py              # JWT Bearer, get_current_user / get_optional_user
│   └── rbac.py              # Role hierarchy + permission helpers (chua gan router)
├── utils/                   # security (hash/jwt), helpers
├── config/
│   ├── config.py            # Pydantic Settings
│   └── logging_config.py    # log handlers, file logs/app.log
├── docs/reports/            # SEED_SCHEMA_MATRIX.md
├── modules/                 # (rong) - placeholder
├── logs/                    # app.log generated runtime
├── docker-compose.yml
├── Dockerfile               # (neu co)
├── QUICKSTART.md
├── requirements.txt
└── README.md                # tai lieu nay
```

| Folder | Mục đích |
|--------|---------|
| `routers/` | Mỗi domain 1 file (`auth_router`, `users_router`, …). `routers.py` mount tất cả vào `api_router` prefix `/api/v1`. |
| `controllers/` | Nhận DTO + `current_user`, gọi service tương ứng, trả về Response DTO. **Hiện đang chứa cả check role bằng so chuỗi.** |
| `services/` | Truy vấn DB (qua Beanie), tính toán nghiệp vụ, gọi AI. |
| `models/models.py` | 14 collection Mongo (Beanie `Document`). |
| `schemas/` | Pydantic v2 model phục vụ request/response, validate input. |

---

## 7. Lifecycle

`app/main.py` định nghĩa `lifespan` (FastAPI `asynccontextmanager`):

1. `setup_logging()` — cấu hình logger ra console + file `BE/logs/app.log`.
2. `init_database()` — tạo `AsyncIOMotorClient`, gọi `init_beanie(database=..., document_models=[...])`.
3. **yield** — app phục vụ request.
4. `close_database()` — đóng Motor client khi shutdown.

CORS middleware cho phép `settings.allowed_origins` (mặc định `http://localhost:3000`, `http://localhost:5173`).

---

## 8. Models / collections (MongoDB)

Định nghĩa trong [`models/models.py`](models/models.py). Mỗi class kế thừa `beanie.Document` và khai báo `class Settings: name = "..."` để map sang collection name.

| Class | Collection | Mục đích |
|-------|-----------|---------|
| `User` | `users` | Hồ sơ + auth. Field chính: `email`, `hashed_password`, `role`, `status`, `avatar_url`, `bio`. |
| `RefreshToken` | `refresh_tokens` | JWT refresh tokens active của user (hỗ trợ multi-device logout). |
| `PasswordResetTokenDocument` | `password_reset_tokens` | Token reset password (chưa được dùng — chưa có route forgot password). |
| `Course` | `courses` | Khóa học (public hoặc personal — phân biệt qua `course_type`). Chứa metadata + nested modules/lessons. |
| `Module` | `modules` | Module dùng standalone (nếu không nhúng trong Course). |
| `Lesson` | `lessons` | Lesson dùng standalone. |
| `Enrollment` | `enrollments` | Liên kết user ↔ course, status, tiến độ tổng. |
| `AssessmentSession` | `assessment_sessions` | Phiên đánh giá năng lực (questions + answers + AI analysis). |
| `Quiz` | `quizzes` | Quiz gắn vào lesson (do AI sinh hoặc instructor tạo). |
| `QuizAttempt` | `quiz_attempts` | Mỗi lần làm quiz của student. |
| `Progress` | `progress` | Tiến độ chi tiết per-course (lessons_progress, time_spent, streak). |
| `Conversation` | `conversations` | Lịch sử chat AI Tutor theo course. |
| `Class` | `classes` | Lớp học do instructor tạo từ course, có `invite_code`. |
| `Recommendation` | `recommendations` | Lộ trình AI sinh ra (từ assessment hoặc tổng quan). |

`app/database.py` import các class `*Document` — trong [`models/models.py`](models/models.py) (cuối file) có **alias** `UserDocument = User`, `ChatDocument = Conversation`, `AssessmentDocument = AssessmentSession`, … nên `init_beanie` khớp với danh sách document đã đăng ký.

---

## 9. Auth & RBAC

### 9.1 JWT flow

```mermaid
sequenceDiagram
    autonumber
    participant FE as Frontend
    participant BE as FastAPI
    participant DB as MongoDB

    FE->>BE: POST /auth/login {email, password}
    BE->>DB: find user, verify bcrypt
    BE->>BE: create access (15m) + refresh (7d) JWT
    BE->>DB: insert refresh_tokens
    BE-->>FE: {access_token, refresh_token, user}

    FE->>BE: GET ... (Authorization: Bearer <access>)
    BE->>BE: decode_token (utils.security)
    BE-->>FE: 200 OK / 401 if invalid

    Note over FE,BE: Access hết hạn 401
    FE->>BE: POST /auth/refresh {refresh_token}
    BE->>DB: validate refresh_tokens collection
    BE->>BE: issue new access JWT
    BE-->>FE: {access_token}
```

- Payload JWT: `{ sub: user_id, email, role, type: "access" | "refresh", exp }`.
- `get_current_user` (xem `middleware/auth.py`) chỉ chấp nhận token `type == "access"`. Trả về `dict {user_id, email, role}` để controller dùng.
- Mã hash password: `passlib[bcrypt]` với `bcrypt_rounds=12` mặc định.

### 9.2 RBAC trong codebase

`middleware/rbac.py` định nghĩa sẵn:

- `Role.STUDENT / INSTRUCTOR / ADMIN` với hierarchy `admin > instructor > student`.
- Bảng `ROLE_PERMISSIONS` map đầy đủ permission cho 84 chức năng (Section 2–5 theo CHUCNANG.md).
- Dependency factories: `require_role`, `require_permission`, `require_any_role`, `require_ownership_or_admin`.
- Shorthand `require_student / require_instructor / require_admin`, `require_instructor_or_admin`.

**Đã gắn `Depends` trên một số router** (hierarchy `admin ≥ instructor ≥ student`; student-only dùng `require_student_only`):

| Router | Dependency |
|--------|------------|
| [`routers/dashboard_router.py`](routers/dashboard_router.py) | `require_student_only` → `/dashboard/student`; `require_instructor` → `/dashboard/instructor` |
| [`routers/analytics_router.py`](routers/analytics_router.py) | `require_student_only` → learning-stats, progress-chart; `require_instructor` → `/analytics/instructor/*` |

**Vẫn check chuỗi trong controller** (chưa refactor sang `Depends`):

| File | Pattern check |
|------|----------------|
| [`controllers/admin_controller.py`](controllers/admin_controller.py) | `role != "admin"` → 403 |
| [`controllers/dashboard_controller.py`](controllers/dashboard_controller.py) | `ensure_student_only` / `ensure_minimum_role(INSTRUCTOR)` + admin dashboard |
| [`controllers/quiz_controller.py`](controllers/quiz_controller.py) | `ensure_minimum_role(INSTRUCTOR)` cho mutate quiz; student list riêng |
| [`controllers/search_controller.py`](controllers/search_controller.py) | `GET /search/analytics` chỉ admin |
| [`controllers/class_controller.py`](controllers/class_controller.py) | Tạo lớp: instructor/admin; ownership trong service |

Khi mở rộng router mới, ưu tiên `Depends(require_role(...))` / `require_student_only` thay vì so chuỗi lặp lại.

---

## 10. AI integration (Google Gemini)

File: [`services/ai_service.py`](services/ai_service.py). Thư viện `google-generativeai==0.8.3`.

Các use case AI:

- **Assessment generate** — `POST /assessments/generate`: prompt Gemini sinh bộ câu hỏi (15/25/35 câu theo `beginner/intermediate/advanced`) bám sát content course có sẵn, kèm phân bổ easy/medium/hard.
- **Assessment scoring** — `POST /assessments/{id}/submit`: chấm điểm có trọng số + Gemini phân tích skill strengths / weaknesses / knowledge gaps.
- **Recommendations** — `GET /recommendations/from-assessment`, `GET /recommendations`: AI suy ra course ưu tiên + thứ tự.
- **AI Tutor chat** — `POST /chat/course/{course_id}`: chat context theo course (lưu vào `conversations`).
- **AI practice / module quiz** — `POST /ai/generate-practice`, `POST /courses/{id}/modules/{mid}/assessments/generate`: AI sinh quiz theo chủ đề / module.
- **Personal course from prompt** — `POST /courses/from-prompt`: sinh khung modules + lessons từ mô tả natural language.

Vì Gemini có thể mất 20–120 giây/request, FE đã set 2 timeout dài hơn (`AI_TIMEOUT=120s`, `ASSESSMENT_SUBMIT_TIMEOUT=180s`).

---

## 11. API surface — tóm tắt 90 endpoints

Reference đầy đủ: [`../docs/API.md`](../docs/API.md).

| Router | Prefix | Số endpoint | Vai trò chính |
|--------|--------|-------------|----------------|
| System | `/health` | 1 | Public health probe |
| Auth | `/api/v1/auth` | 4 | register/login/logout/refresh |
| Users | `/api/v1/users` | 2 | GET/PATCH `/users/me` |
| Assessments | `/api/v1/assessments` | 5 | Student – generate, history, submit, results, review |
| Personal Courses | `/api/v1/courses` (sub-paths) | 6 | Student – CRUD course cá nhân + AI prompt |
| Courses (public) | `/api/v1/courses` | 4 | Public – search, list, detail, enrollment-status |
| Enrollments | `/api/v1/enrollments` | 4 | Student – enroll / my-courses / detail / cancel |
| Learning | `/api/v1/courses` (modules/lessons) | 7 | Student – module/lesson + AI module quiz |
| Quiz | `/api/v1/quizzes`, `/lessons/.../quizzes`, `/ai/generate-practice` | 10 | Student (5) + Instructor (5) |
| Progress | `/api/v1/progress` | 1 | Student – course progress |
| Chat | `/api/v1/chat` | 5 | Student – AI tutor |
| Recommendations | `/api/v1/recommendations` | 2 | Student – AI roadmap |
| Dashboard | `/api/v1/dashboard` | 3 | per-role dashboard |
| Analytics | `/api/v1/analytics` | 5 | Student (2) + Instructor (3) |
| Classes | `/api/v1/classes` | 10 | Instructor (8) + Student join (1) + class progress |
| Search | `/api/v1/search` | 4 | Public/auth – global search |
| Admin | `/api/v1/admin` | 17 | Admin – users (7), courses (5), classes (2), analytics (3) |

**Tổng = 1 + 4 + 2 + 5 + 6 + 4 + 4 + 7 + 10 + 1 + 5 + 2 + 3 + 5 + 10 + 4 + 17 = 90.**

---

## 12. Seed & tests

- **Seed**: [`scripts/init_data.py`](scripts/init_data.py) — chạy `cd BE && python -m scripts.init_data` (full reset collections + seed lớn: users, courses, enrollments, quizzes, classes, …). Cuối script in **demo accounts** (ví dụ `admin1@ailearning.vn / Admin@123456`). Tham khảo thêm [`docs/reports/SEED_SCHEMA_MATRIX.md`](docs/reports/SEED_SCHEMA_MATRIX.md).
  - Nếu không muốn reset toàn DB: chỉ dùng Swagger `POST /auth/register` rồi `PUT /admin/users/{id}/role` khi cần role đặc biệt.
- **Tests**: Thư mục [`tests/`](tests/) — **173** pytest cases; báo cáo lỗi: [`docs/reports/TEST_ISSUES_AND_GAPS.md`](../docs/reports/TEST_ISSUES_AND_GAPS.md) (integration, mock Gemini), database `ai_learning_test`. Modules: auth, assessments, recommendations, courses, enrollments, learning, quizzes, dashboard, chat, users, progress, search, analytics, classes, personal_courses, admin, instructor, **rbac** (`tests/rbac/` — ma trận Admin/Instructor + unit `middleware/rbac.py`), `integration/test_flow_steps.py`. Chạy: `pytest -q`. Export OpenAPI: `python scripts/export_openapi.py`; Postman: `python scripts/generate_postman.py`.

---

## 13. Logging & errors

- Cấu hình logger ở [`config/logging_config.py`](config/logging_config.py), `setup_logging()` được gọi trong `lifespan`.
- Output: console (DEBUG/INFO theo `LOG_LEVEL`) + file `BE/logs/app.log` (rotation theo cấu hình trong file).
- Errors thường gặp:
  - **`pydantic.ValidationError`** → FastAPI tự trả 422 với `detail` là array (FE handle ở `handleApiError`).
  - **`HTTPException`** trong controller → status code tùy chỗ (401, 403, 404, 400).
  - Custom error message bằng tiếng Việt được dùng nhiều, ví dụ `"Email đã tồn tại"`, `"Yêu cầu quyền admin..."`.

---

## 14. Known gaps & lưu ý

- **`PasswordResetTokenDocument`** có collection nhưng không router nào dùng (chưa có endpoint forgot/reset password). FE có page nhưng service báo lỗi 501.
- **`SECRET_KEY` vs `JWT_SECRET_KEY`** — đã sửa [`QUICKSTART.md`](QUICKSTART.md); dùng `SECRET_KEY` trong `.env`.
- **RBAC** — dashboard/analytics đã dùng `middleware/rbac` trên router; admin/classes/search vẫn check trong controller (mục 9.2).
- **`ProgressPage` (FE)** — dùng `/analytics/learning-stats` + `/analytics/progress-chart`, không gọi `GET /progress/course/{id}` (theo thiết kế FE; xem `docs/API.md`).
- **`GEMINI_MODEL` không nhất quán** — code default `gemini-1.5-pro`, `.env.example` ghi `gemini-2.5-flash`.

---

## 15. Troubleshooting

| Triệu chứng | Nguyên nhân | Cách xử lý |
|-------------|-------------|------------|
| `pydantic.ValidationError: SECRET_KEY field required` | `.env` thiếu `SECRET_KEY` | Thêm `SECRET_KEY=<random>` (gen: `python -c "import secrets; print(secrets.token_hex(32))"`) |
| `pydantic.ValidationError: GOOGLE_API_KEY field required` | Thiếu key Gemini | Lấy ở https://aistudio.google.com/app/apikey, set vào `.env` |
| `pymongo.errors.ServerSelectionTimeoutError` lúc khởi động | MongoDB chưa chạy hoặc URL sai | `mongod` local hoặc `docker compose up mongodb`; check `MONGODB_URL` |
| `ImportError: cannot import name 'UserDocument'` | Thiếu alias trong `models/models.py` hoặc import sai trong `app/database.py` | Đảm bảo cuối `models/models.py` có `UserDocument = User`, … và `database.py` import đúng tên |
| `401 Token type không hợp lệ` khi gọi `/auth/refresh` | FE gửi access token thay vì refresh token | Đảm bảo body `{refresh_token: <refresh>}` |
| `403 Yêu cầu quyền admin` mà user đã đổi role trong DB | Token cũ còn cache role cũ trong claim | Logout + login lại để claim mới |
| CORS error trên FE | `ALLOWED_ORIGINS` chưa chứa origin FE | Sửa `.env` (note: format JSON list nếu để trong quote) |
| Gemini timeout / 429 | Limit của free tier | Đổi model nhỏ (`gemini-2.5-flash`), retry, hoặc cache prompt |
