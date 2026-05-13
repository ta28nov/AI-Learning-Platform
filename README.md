# AI Learning Platform

Nền tảng học tập **cá nhân hóa bằng AI** (assessment → lộ trình → bài học → ôn tập) gồm:

- **Frontend (FE)**: SPA React 18 + Vite, single landing + dashboard cho 3 role.
- **Backend (BE)**: FastAPI + MongoDB (Beanie ODM), tích hợp **Google Gemini** cho assessment / AI tutor / sinh quiz.
- **Tài liệu**: README cấp phân hệ (FE, BE), API reference (`docs/API.md`), QUICKSTART đã có sẵn cho BE.

> Đây là tài liệu **gốc** mô tả toàn cảnh hệ thống. Setup chi tiết xem [`FE/README.md`](FE/README.md) và [`BE/README.md`](BE/README.md). API reference đầy đủ xem [`docs/API.md`](docs/API.md).

---

## 1. Kiến trúc tổng quan

```mermaid
flowchart LR
    Browser[Trinh duyet nguoi dung]
    FE["React 18 + Vite SPA<br/>port 3000<br/>FE/src"]
    BE["FastAPI + Uvicorn<br/>port 8000<br/>prefix /api/v1"]
    Mongo[("MongoDB<br/>collections: users, courses, ...")]
    Gemini["Google Gemini API<br/>google-generativeai"]

    Browser -->|"HTML / JS bundle"| FE
    FE -->|"axios + JWT Bearer"| BE
    BE -->|"Beanie ODM (Motor async)"| Mongo
    BE -->|"prompts / generate"| Gemini
    BE -->|"JWT access + refresh"| FE
```

- **Auth**: JWT access token (15 phút mặc định) + refresh token 7 ngày, refresh tự động qua axios interceptor (`FE/src/services/api.js`).
- **CORS**: BE cho phép `http://localhost:3000` và `http://localhost:5173` mặc định (`BE/config/config.py`).

---

## 2. Tech stack ngắn gọn

| Lớp | Công nghệ chính | Dùng để làm gì |
|------|-----------------|----------------|
| **Frontend** | React 18.2 + Vite 7.1 + JSX, Zustand 4 (persist), axios 1.4, react-router-dom 6, framer-motion 10, recharts 2, react-hook-form 7, react-hot-toast | SPA, routing, state, gọi API, animation, biểu đồ tiến độ |
| **Backend** | FastAPI + Uvicorn, Pydantic v2, Beanie ODM (Motor + PyMongo), python-jose (JWT), passlib/bcrypt, google-generativeai | REST API, validation, JWT auth, hash password, gọi Gemini |
| **Database** | MongoDB 7.0 (document store) | Collections: `users`, `courses`, `modules`, `lessons`, `enrollments`, `assessment_sessions`, `quizzes`, `quiz_attempts`, `progress`, `conversations`, `classes`, `recommendations`, `refresh_tokens`, `password_reset_tokens` |
| **AI** | Google Gemini (qua `BE/services/ai_service.py`) | Sinh đề assessment, sinh quiz / practice, AI Tutor chat, đề xuất khóa |
| **Infra** | Docker Compose (`BE/docker-compose.yml`), file log `BE/logs/app.log` | Chạy BE + MongoDB ở môi trường dev/staging |

---

## 3. Ba vai trò (role)

Tên role lấy chính xác từ model `User` (`BE/models/models.py`) và RBAC (`BE/middleware/rbac.py`): **`student | instructor | admin`** (mặc định khi đăng ký là `student`).

| Role | Mô tả | Page chính | Nhóm endpoint chính |
|------|------|------------|---------------------|
| **`student`** | Người học. Đăng ký công khai, làm assessment, học theo lộ trình AI, chat AI tutor, làm quiz, theo dõi tiến độ. | `/dashboard`, `/dashboard/assessment`, `/dashboard/courses`, `/dashboard/my-courses`, `/dashboard/chat`, `/dashboard/quiz`, `/dashboard/recommendations`, `/dashboard/personal-courses` | `assessments`, `enrollments`, `learning`, `chat`, `quiz`, `recommendations`, `personal-courses`, `progress`, `analytics/learning-stats` |
| **`instructor`** | Giảng viên. Quản lý lớp (`classes`), theo dõi học viên, tạo / sửa quiz, xem analytics lớp. | `/dashboard/instructor`, `/dashboard/instructor/classes` | `dashboard/instructor`, `analytics/instructor/*`, `classes/*`, `quizzes` (CRUD), `lessons/{id}/quizzes` |
| **`admin`** | Quản trị viên. CRUD user (đổi role, reset password), CRUD khóa học toàn cục, giám sát lớp, analytics hệ thống. | `/dashboard/admin/{users,courses,classes,analytics}` | `admin/*`, `dashboard/admin`, `search/analytics` |

Phân quyền hiện được kiểm trong **controller** (so sánh chuỗi `current_user["role"]`), chưa gắn qua `Depends` của `BE/middleware/rbac.py`. Chi tiết: [`BE/README.md`](BE/README.md).

---

## 4. FLOW_STEPS — quy trình học tập cốt lõi

Bốn bước marketing trên landing (`FE/src/pages/landing/LandingPage.jsx`) **map 1‑1** với luồng code thực tế:

```mermaid
flowchart LR
    A["1. Danh gia<br/>POST /assessments/generate<br/>POST /assessments/{id}/submit"]
    B["2. Lo trinh<br/>GET /recommendations/from-assessment"]
    C["3. Bai hoc<br/>GET /courses/{id}/modules<br/>POST /lessons/{id}/complete"]
    D["4. On tap<br/>POST /quizzes/{id}/attempt<br/>POST /ai/generate-practice"]

    A --> B --> C --> D
    D -->|"adaptive feedback"| C
```

| Bước | Mục tiêu | Page FE | Endpoint chính | Collection thay đổi |
|------|----------|---------|----------------|---------------------|
| **1. Đánh giá** | Xác định năng lực hiện tại | `AssessmentSetupPage` → `AssessmentQuizPage` → `AssessmentResultsPage` | `POST /assessments/generate`, `POST /assessments/{id}/submit`, `GET /assessments/{id}/results` | `assessment_sessions` |
| **2. Lộ trình** | Sinh kế hoạch học cá nhân từ kết quả assessment | `RecommendationsPage` | `GET /recommendations/from-assessment?session_id=…`, `GET /recommendations` | `recommendations` |
| **3. Bài học** | Học theo module/lesson, đánh dấu hoàn thành | `CourseDetailPage` → `ModuleListPage` → `ModuleDetailPage` → `LessonPage` | `GET /courses/{id}/modules`, `GET /courses/{id}/lessons/{lessonId}`, `POST /courses/{id}/lessons/{lessonId}/complete` | `courses`, `modules`, `lessons`, `enrollments`, `progress` |
| **4. Ôn tập** | Củng cố đúng điểm yếu | `QuizPage` → `QuizAttemptPage` → `QuizResultsPage`; AI practice tự sinh | `POST /quizzes/{id}/attempt`, `POST /quizzes/{id}/retake`, `POST /ai/generate-practice`, `POST /courses/{id}/modules/{moduleId}/assessments/generate` | `quizzes`, `quiz_attempts`, `progress` |

---

## 5. End-to-end flows theo role

### 5.1 Student — luồng đầy đủ

```mermaid
sequenceDiagram
    autonumber
    participant U as Student
    participant FE as React SPA
    participant BE as FastAPI
    participant DB as MongoDB
    participant AI as Gemini

    U->>FE: Mo /auth/register
    FE->>BE: POST /auth/register
    BE->>DB: insert users (role=student)
    BE-->>FE: 201 + UserInfo

    U->>FE: Login
    FE->>BE: POST /auth/login
    BE-->>FE: access + refresh JWT
    FE->>FE: localStorage.setItem(tokens)

    U->>FE: /dashboard
    FE->>BE: GET /dashboard/student
    BE->>DB: query enrollments, progress
    BE-->>FE: dashboard payload

    U->>FE: /dashboard/assessment
    FE->>BE: POST /assessments/generate
    BE->>AI: prompt generate questions
    AI-->>BE: questions
    BE->>DB: insert assessment_sessions
    FE->>BE: POST /assessments/{id}/submit
    BE->>AI: prompt analyze skill
    BE->>DB: update session + skill_analysis
    BE-->>FE: results

    U->>FE: /dashboard/recommendations
    FE->>BE: GET /recommendations/from-assessment
    BE->>AI: prompt suggest courses
    BE-->>FE: list recommended courses

    U->>FE: Click enroll
    FE->>BE: POST /enrollments
    BE->>DB: insert enrollments, init progress

    U->>FE: Mo lesson
    FE->>BE: GET /courses/{id}/lessons/{lid}
    FE->>BE: POST /chat/course/{id} (AI Tutor)
    BE->>AI: chat completion
    FE->>BE: POST .../lessons/{lid}/complete
    BE->>DB: update progress.lessons_progress

    U->>FE: Lam quiz on tap
    FE->>BE: POST /quizzes/{id}/attempt
    BE->>DB: insert quiz_attempts, update progress
```

### 5.2 Instructor — luồng đầy đủ

```mermaid
sequenceDiagram
    autonumber
    participant I as Instructor
    participant FE as React SPA
    participant BE as FastAPI
    participant DB as MongoDB

    I->>FE: Login (POST /auth/login)
    FE-->>I: JWT (role=instructor)

    I->>FE: /dashboard/instructor
    FE->>BE: GET /dashboard/instructor
    BE->>DB: classes, enrollments, quiz stats
    BE-->>FE: dashboard payload

    I->>FE: /dashboard/instructor/classes/create
    FE->>BE: POST /classes
    BE->>DB: insert classes (invite_code)

    I->>FE: /dashboard/instructor/classes/{id}
    FE->>BE: GET /classes/{id}/students
    FE->>BE: GET /classes/{id}/progress

    I->>FE: Tao quiz cho lesson
    FE->>BE: POST /lessons/{lessonId}/quizzes
    BE->>DB: insert quizzes (role check: instructor)

    I->>FE: Xem analytics lop
    FE->>BE: GET /analytics/instructor/classes
    FE->>BE: GET /analytics/instructor/quiz-performance
    BE-->>FE: charts data

    I->>FE: Xem ket qua quiz cua lop
    FE->>BE: GET /quizzes/{quizId}/class-results
```

### 5.3 Admin — luồng đầy đủ

```mermaid
sequenceDiagram
    autonumber
    participant A as Admin
    participant FE as React SPA
    participant BE as FastAPI
    participant DB as MongoDB

    A->>FE: Login
    FE-->>A: JWT (role=admin)

    A->>FE: /dashboard
    FE->>BE: GET /dashboard/admin
    BE-->>FE: tong quan he thong

    A->>FE: /dashboard/admin/users
    FE->>BE: GET /admin/users
    FE->>BE: PUT /admin/users/{id}/role
    FE->>BE: POST /admin/users/{id}/reset-password
    FE->>BE: DELETE /admin/users/{id}
    BE->>DB: cap nhat users

    A->>FE: /dashboard/admin/courses
    FE->>BE: GET /admin/courses
    FE->>BE: POST /admin/courses (tao course chinh thuc)
    FE->>BE: PUT /admin/courses/{id}
    FE->>BE: DELETE /admin/courses/{id}

    A->>FE: /dashboard/admin/classes
    FE->>BE: GET /admin/classes
    FE->>BE: GET /admin/classes/{id}

    A->>FE: /dashboard/admin/analytics
    FE->>BE: GET /admin/analytics/users-growth
    FE->>BE: GET /admin/analytics/courses
    FE->>BE: GET /admin/analytics/system-health
    FE->>BE: GET /search/analytics
```

---

## 6. Cấu trúc workspace

```
AI-Learning-Platform/
├── README.md                       # tai lieu nay
├── BE/                             # backend FastAPI
│   ├── README.md                   # huong dan BE (stack + setup + RBAC)
│   ├── QUICKSTART.md               # setup nhanh BE (da co tu truoc)
│   ├── app/                        # entry point + db init
│   ├── controllers/                # HTTP handlers
│   ├── routers/                    # khai bao FastAPI Router
│   ├── services/                   # nghiep vu + AI
│   ├── models/                     # Beanie Document
│   ├── schemas/                    # Pydantic request/response
│   ├── middleware/                 # auth (JWT) + rbac helpers
│   ├── utils/                      # security, helpers
│   ├── config/                     # Settings, logging
│   ├── docs/reports/               # bao cao schema seed
│   ├── docker-compose.yml          # MongoDB + BE container
│   └── requirements.txt
├── FE/                             # frontend React + Vite
│   ├── README.md                   # huong dan FE (stack + setup + routing)
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx, App.jsx, AppRouter.jsx
│       ├── pages/                  # landing, auth, dashboard, ...
│       ├── components/             # layout, ui, ...
│       ├── services/               # axios + API per domain
│       ├── stores/                 # Zustand
│       ├── hooks/, contexts/, styles/, utils/
└── docs/
    └── API.md                      # API reference day du
```

---

## 7. Quick start (3 phút)

> Yêu cầu: **Node 18+**, **Python 3.11+**, **MongoDB** đang chạy (local hoặc Atlas), **Google Gemini API key**.

```powershell
# 1) Backend (xem BE/README.md de biet chi tiet)
cd BE
python -m venv venv ; venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # sua SECRET_KEY, MONGODB_URL, GOOGLE_API_KEY
uvicorn app.main:app --reload      # http://localhost:8000

# 2) Frontend (mo terminal moi - xem FE/README.md de biet chi tiet)
cd FE
npm install
copy .env.example .env             # VITE_API_BASE_URL=http://localhost:8000/api/v1
npm run dev                        # http://localhost:3000
```

Sau đó:

1. Truy cập `http://localhost:3000` → đăng ký tài khoản (role mặc định **`student`**).
2. Để tạo `instructor` / `admin`: dùng Swagger `http://localhost:8000/docs` đăng nhập bằng tài khoản admin, gọi `PUT /admin/users/{id}/role` để đổi role.

---

## 8. Tài liệu liên quan

| Tài liệu | Mục đích |
|----------|----------|
| [`FE/README.md`](FE/README.md) | Setup, scripts, routing, state, design system của Frontend |
| [`BE/README.md`](BE/README.md) | Setup, biến môi trường, RBAC, AI integration của Backend |
| [`BE/QUICKSTART.md`](BE/QUICKSTART.md) | Setup nhanh BE (đã có sẵn) |
| [`BE/docs/reports/SEED_SCHEMA_MATRIX.md`](BE/docs/reports/SEED_SCHEMA_MATRIX.md) | Ma trận seed schema cho mọi collection |
| [`docs/API.md`](docs/API.md) | Reference đầy đủ **90 endpoints** + curl mẫu |

---

## 9. Trạng thái tính năng và known gaps

Mục này tổng hợp những điểm code thực tế **lệch** với tài liệu cũ hoặc **chưa hoàn thiện**, để dev mới khỏi mất thời gian đoán:

- [ ] **Forgot / reset / verify password** — page tồn tại (`FE/src/pages/auth/{ForgotPassword,ResetPassword,VerifyEmail}Page.jsx`) nhưng service throw vì BE chưa có endpoint (`FE/src/services/authService.js`). `auth_router.py` chỉ có `register / login / logout / refresh`.
- [x] **Seed script** — có sẵn [`BE/scripts/init_data.py`](BE/scripts/init_data.py): `cd BE && python -m scripts.init_data` (full reset DB + seed lớn). Sau khi chạy, script in demo accounts (ví dụ `admin1@ailearning.vn / Admin@123456`, `instructor1@ailearning.vn / Instructor@123`, `student1@gmail.com / Student@123`). Có thể dùng kèm smoke test [`BE/scripts/smoke_test.py`](BE/scripts/smoke_test.py).
- [ ] **Tests** — `pytest` có trong `BE/requirements.txt` và `vitest` có trong `FE/package.json`, nhưng **không có file test thực tế** trong cả 2 phân hệ.
- [ ] **`SECRET_KEY` vs `JWT_SECRET_KEY`** — `BE/QUICKSTART.md` viết `JWT_SECRET_KEY`, nhưng `BE/config/config.py` đọc biến tên **`SECRET_KEY`**. Dùng `SECRET_KEY` trong `.env`.
- [ ] **RBAC helpers chưa gắn router** — `BE/middleware/rbac.py` có `require_admin / require_instructor / require_student`, hierarchy đầy đủ, nhưng các router hiện kiểm `role` bằng cách so chuỗi trong controller (xem `BE/controllers/{admin,dashboard,quiz,search}_controller.py`).
- [ ] **Progress page chưa wire BE** — `BE/routers/progress_router.py` expose `GET /progress/course/{id}` và `FE/src/services/progressService.js` đã có hàm gọi, nhưng **không page nào import**. `ProgressPage` đang dùng `analyticsService` (`/analytics/learning-stats`, `/analytics/progress-chart`).
- [ ] **Instructor bị chặn personal-courses** — `FE/src/AppRouter.jsx` bọc `/dashboard/personal-courses*` trong `<StudentRoute>` ⇒ role `instructor` sẽ rơi vào `/unauthorized`. Nếu muốn instructor cũng dùng course editor, cần đổi guard.

---

## 10. License & liên hệ

> Placeholder — bổ sung khi xác định license và thông tin team.
