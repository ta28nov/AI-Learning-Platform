# API Coverage Log

**Ngày cập nhật:** 2026-05-19 (P7)  
**Nguồn route:** `BE/tests/fixtures/openapi.json` (snapshot OpenAPI)  
**Pytest:** **173** cases (`python tests/run_tests.py` hoặc `pytest -q`)  
**Chi tiết bug / trạng thái:** [`TEST_ISSUES_AND_GAPS.md`](TEST_ISSUES_AND_GAPS.md)

---

## 1. Tổng quan

| Metric | Số lượng |
|--------|----------|
| Path OpenAPI (`/api/v1/...` + `/health`) | **74** path |
| HTTP operations (method × path) | **~88** |
| Operations đã gọi trong pytest | **~86** (smoke / regression / RBAC) |
| Operations chưa có test riêng | **~2** (không tồn tại BE) |
| Bug BUG-001 → BUG-014 | **Đã sửa** (pytest assert 200/201/403) |
| Luồng E2E Playwright | **12** spec (`admin`, `instructor`, `route-guards`, `personal-courses`, …) |

**Chú thích cột Test**

| Ký hiệu | Ý nghĩa |
|---------|---------|
| ✅ | Có pytest; thường assert 200/201 hoặc 403 RBAC |
| ⚠️ | Đã gọi; regression bug (500/404) hoặc assert lỏng |
| 🔶 | Chỉ E2E UI smoke |
| ❌ | Chưa có pytest / không có API BE |

---

## 2. Danh sách API đầy đủ

Prefix: `/api/v1` (trừ `/health`).

### 2.1 Auth (4)

| Method | Path | Test | Ghi chú |
|--------|------|------|---------|
| POST | `/auth/register` | ✅ | `tests/auth/test_register.py` |
| POST | `/auth/login` | ✅ | `tests/auth/test_login.py`, helpers |
| POST | `/auth/logout` | ✅ | `tests/auth/test_logout.py` |
| POST | `/auth/refresh` | ✅ | `tests/auth/test_refresh.py` |

**Không có BE:** forgot / reset / verify password (FE có page, không router).

---

### 2.2 Users (2)

| Method | Path | Test | Ghi chú |
|--------|------|------|---------|
| GET | `/users/me` | ✅ | `tests/users/test_users.py` |
| PATCH | `/users/me` | ✅ | validation bio |

---

### 2.3 Assessments (5)

| Method | Path | Test | Ghi chú |
|--------|------|------|---------|
| POST | `/assessments/generate` | ✅ | mock AI |
| GET | `/assessments/history` | ✅ | |
| POST | `/assessments/{session_id}/submit` | ✅ | |
| GET | `/assessments/{session_id}/results` | ✅ | |
| GET | `/assessments/{session_id}/review` | ✅ | |

---

### 2.4 Personal courses (6)

| Method | Path | Test | Ghi chú |
|--------|------|------|---------|
| POST | `/courses/from-prompt` | ✅ | mock AI |
| POST | `/courses/personal` | ✅ | |
| GET | `/courses/personal/{course_id}` | ✅ | |
| PUT | `/courses/personal/{course_id}` | ✅ | |
| DELETE | `/courses/personal/{course_id}` | ✅ | |
| GET | `/courses/my-personal` | ✅ | |

---

### 2.5 Courses catalog (4)

| Method | Path | Test | Ghi chú |
|--------|------|------|---------|
| GET | `/courses/search` | ✅ | keyword, category, level, guest |
| GET | `/courses/public` | ✅ | pagination |
| GET | `/courses/{course_id}` | ✅ | |
| GET | `/courses/{course_id}/enrollment-status` | ✅ | enrolled / not |

---

### 2.6 Enrollments (4)

| Method | Path | Test | Ghi chú |
|--------|------|------|---------|
| POST | `/enrollments` | ✅ | integration + unit |
| GET | `/enrollments/my-courses` | ✅ | filter `active` / `cancelled` / `completed` |
| GET | `/enrollments/{enrollment_id}` | ✅ | |
| DELETE | `/enrollments/{enrollment_id}` | ✅ | cancel |

---

### 2.7 Learning (6)

| Method | Path | Test | Ghi chú |
|--------|------|------|---------|
| GET | `/courses/{course_id}/modules` | ✅ | |
| GET | `/courses/{course_id}/modules/{module_id}` | ✅ | |
| GET | `/courses/{course_id}/lessons/{lesson_id}` | ✅ | integration |
| POST | `/courses/{course_id}/lessons/{lesson_id}/complete` | ✅ | integration |
| GET | `/courses/{course_id}/modules/{module_id}/outcomes` | ✅ | |
| GET | `/courses/{course_id}/modules/{module_id}/resources` | ✅ | |
| POST | `/courses/{course_id}/modules/{module_id}/assessments/generate` | ✅ | mock AI |

---

### 2.8 Quizzes (10)

| Method | Path | Test | Ghi chú |
|--------|------|------|---------|
| GET | `/quizzes` | ✅ | student + instructor filters |
| GET | `/quizzes/{quiz_id}` | ✅ | |
| POST | `/quizzes/{quiz_id}/attempt` | ✅ | max attempts → 403 |
| GET | `/quizzes/{quiz_id}/results` | ✅ | |
| POST | `/quizzes/{quiz_id}/retake` | ✅ | |
| POST | `/ai/generate-practice` | ✅ | mock AI |
| POST | `/lessons/{lesson_id}/quizzes` | ✅ | cần `LessonDocument` trong DB |
| PUT | `/quizzes/{quiz_id}` | ✅ | instructor |
| DELETE | `/quizzes/{quiz_id}` | ✅ | instructor |
| GET | `/quizzes/{quiz_id}/class-results` | ✅ | |

---

### 2.9 Progress (1)

| Method | Path | Test | Ghi chú |
|--------|------|------|---------|
| GET | `/progress/course/{course_id}` | ✅ | FE `CourseDetailPage` (đã ghi danh) + pytest; `ProgressPage` dùng analytics |

---

### 2.10 Chat (5)

| Method | Path | Test | Ghi chú |
|--------|------|------|---------|
| POST | `/chat/course/{course_id}` | ✅ | mock AI |
| GET | `/chat/history` | ✅ | |
| GET | `/chat/conversations/{conversation_id}` | ✅ | |
| DELETE | `/chat/conversations` | ✅ | |
| DELETE | `/chat/history/{conversation_id}` | ✅ | |

---

### 2.11 Recommendations (2)

| Method | Path | Test | Ghi chú |
|--------|------|------|---------|
| GET | `/recommendations/from-assessment` | ✅ | session chưa evaluate → 404 (KNOWN-001) |
| GET | `/recommendations` | ✅ | |

---

### 2.12 Dashboard (3)

| Method | Path | Test | Ghi chú |
|--------|------|------|---------|
| GET | `/dashboard/student` | ✅ | RBAC: instructor/admin cũng 200 (gap) |
| GET | `/dashboard/instructor` | ✅ | student 403; admin 403 (exact role) |
| GET | `/dashboard/admin` | ✅ | RBAC 403 non-admin |

---

### 2.13 Analytics (5)

| Method | Path | Test | Ghi chú |
|--------|------|------|---------|
| GET | `/analytics/learning-stats` | ✅ | |
| GET | `/analytics/progress-chart` | ✅ | |
| GET | `/analytics/instructor/classes` | ✅ | |
| GET | `/analytics/instructor/progress-chart` | ✅ | |
| GET | `/analytics/instructor/quiz-performance` | ✅ | |

---

### 2.14 Classes — Instructor (10)

| Method | Path | Test | Ghi chú |
|--------|------|------|---------|
| POST | `/classes` | ✅ | student → 403 (BUG-011 đã sửa) |
| GET | `/classes/my-classes` | ✅ | **E1:** role-aware — student query `student_ids`, instructor `instructor_id` |
| GET | `/classes/{class_id}` | ✅ | instructor owner; student trong `student_ids` (read-only, no `invite_code`) |
| PUT | `/classes/{class_id}` | ✅ | không có field `status` trong schema |
| DELETE | `/classes/{class_id}` | ✅ | lớp có HV → 400; lớp trống → xóa OK |
| POST | `/classes/join` | ✅ | lớp `active` join OK; `preparing` → 400 |
| GET | `/classes/{class_id}/students` | ✅ | |
| GET | `/classes/{class_id}/students/{student_id}` | ✅ | BUG-007 đã sửa |
| DELETE | `/classes/{class_id}/students/{student_id}` | ✅ | BUG-008 đã sửa |
| GET | `/classes/{class_id}/progress` | ✅ | BUG-003 đã sửa |

---

### 2.15 Search (4)

| Method | Path | Test | Ghi chú |
|--------|------|------|---------|
| GET | `/search` | ✅ | guest + filters |
| GET | `/search/suggestions` | ✅ | |
| GET | `/search/history` | ✅ | |
| GET | `/search/analytics` | ✅ | admin only |

**Mỏng:** `rating`, `instructor` filter — chưa assert sâu từng kết quả.

---

### 2.16 Admin (17)

| Method | Path | Test | Ghi chú |
|--------|------|------|---------|
| GET | `/admin/users` | ✅ | role, sort, keyword search |
| POST | `/admin/users` | ✅ | student cần password (422 nếu thiếu) |
| GET | `/admin/users/{user_id}` | ✅ | đã sửa BUG-001 |
| PUT | `/admin/users/{user_id}` | ✅ | |
| DELETE | `/admin/users/{user_id}` | ✅ | |
| PUT | `/admin/users/{user_id}/role` | ✅ | RBAC matrix |
| POST | `/admin/users/{user_id}/reset-password` | ✅ | |
| GET | `/admin/courses` | ✅ | keyword search |
| POST | `/admin/courses` | ✅ | BUG-002 đã sửa |
| GET | `/admin/courses/{course_id}` | ✅ | BUG-004 đã sửa |
| PUT | `/admin/courses/{course_id}` | ✅ | BUG-005 đã sửa |
| DELETE | `/admin/courses/{course_id}` | ✅ | BUG-009 đã sửa |
| GET | `/admin/classes` | ✅ | search filter |
| GET | `/admin/classes/{class_id}` | ✅ | |
| GET | `/admin/analytics/users-growth` | ✅ | time_range |
| GET | `/admin/analytics/courses` | ✅ | |
| GET | `/admin/analytics/system-health` | ✅ | BUG-006 đã sửa |

---

### 2.17 System (1)

| Method | Path | Test | Ghi chú |
|--------|------|------|---------|
| GET | `/health` | ✅ | `tests/test_health.py` |

---

## 3. Luồng nghiệp vụ (flow)

| # | Luồng | API liên quan | Pytest | E2E | Ghi chú |
|---|--------|---------------|--------|-----|---------|
| F1 | Đăng ký → đăng nhập → refresh → logout | auth/* | ✅ | 🔶 auth.spec | |
| F2 | Assessment AI: generate → submit → results → review | assessments/* | ✅ | 🔶 assessment-flow (submit cần API key) | mock Gemini trong pytest |
| F3 | Gợi ý khóa học sau assessment | recommendations/from-assessment | ✅ | 🔶 recommendations | |
| F4 | Khám phá → enroll → my-courses | courses/*, enrollments/* | ✅ | 🔶 enrollment-lesson | |
| F5 | Học bài: modules → lesson → complete | learning/* | ✅ | 🔶 enrollment-lesson | |
| F6 | Quiz: detail → attempt → results → retake | quizzes/* | ✅ | 🔶 quiz.spec | |
| F7 | Personal course: prompt → CRUD | courses/from-prompt, personal/* | ✅ | 🔶 personal-courses.spec | |
| F8 | Chat theo course | chat/* | ✅ | 🔶 chat.spec (skip không key) | |
| F9 | Dashboard + analytics student | dashboard/student, analytics/* | ✅ | 🔶 student-flow | RBAC student-only |
| F10 | Instructor: tạo lớp → mời → quản lý HV | classes/* | ✅ | 🔶 instructor.spec | E2E tạo lớp + invite code |
| F11 | Instructor: tạo quiz → kết quả lớp | lessons/.../quizzes, class-results | ✅ | ❌ | |
| F12 | Instructor dashboard + analytics | dashboard/instructor, analytics/instructor/* | ✅ | 🔶 instructor.spec | |
| F13 | Admin: users / courses / classes / analytics | admin/* | ✅ | 🔶 admin.spec | 4 tabs E2E |
| F14 | Integration happy path HV | F2→F3→F4→F5→F6 (rút gọn) | ✅ | — | `integration/test_flow_steps.py` |
| F15 | Universal search | search/* | ✅ | ❌ | |
| F16 | RBAC ma trận admin/instructor | admin/*, dashboard, classes, quiz | ✅ | 🔶 route-guards.spec | `tests/rbac/` |

---

## 4. Chưa test / còn mỏng (không tạo test mới trong đợt này)

### 4.1 API — đã gọi nhưng thiếu happy path 200

Tất cả admin/instructor/class routes có bug trong §5 — pytest chỉ regression 500/404, chưa assert dữ liệu đúng sau khi sửa BE.

### 4.2 API / tính năng không tồn tại BE

| Mục | Lý do |
|-----|--------|
| Forgot / reset / verify password | Không có trong `auth_router` |
| Kích hoạt lớp `preparing` → `active` qua PUT | `ClassUpdateRequest` không có `status` (**BUG-014**) |

### 4.3 Hành vi / filter chưa assert sâu

| Mục | Route |
|-----|--------|
| Search `rating`, `instructor` | `GET /search` |
| Admin `GET /admin/users?status=inactive` | chỉ smoke `active` |
| Public courses filter category/level kết quả cụ thể | `GET /courses/public` |
| Quiz retake sinh AI đầy đủ | `POST /quizzes/{id}/retake` |
| Xóa lớp `status=completed` khi còn HV | `DELETE /classes/{id}` (rule chưa test) |

### 4.4 E2E & FE (ngoài pytest)

| Mục | Trạng thái |
|-----|------------|
| Admin UI: courses, classes, analytics | 🔶 chưa |
| Instructor: tạo lớp trên UI | ✅ `instructor.spec.js` (invite code) |
| Admin: courses/classes/analytics tabs | ✅ `admin.spec.js` |
| Personal courses FE | ✅ `personal-courses.spec.js` |
| FE route guards | ✅ `route-guards.spec.js` |
| Assessment + chat E2E với Gemini thật | skip không `GOOGLE_API_KEY` |
| Student join lớp trên UI | ❌ route chỉ `InstructorRoute` — join modal chưa có path student |

### 4.5 RBAC — đã sửa (pytest `tests/rbac/`)

| Mục | Trạng thái |
|-----|------------|
| `dashboard_router`, `analytics_router` | `Depends(require_student_only \| require_instructor)` |
| BUG-011 / RBAC-R2 | Student `POST /classes` → **403** |
| `/dashboard/student`, learning-stats | Instructor/admin → **403** |
| `/dashboard/instructor`, quiz mutate | Admin → **200** (hierarchy) |
| E2E route guards | `e2e/tests/route-guards.spec.js` |

---

## 5. Bug registry (lịch sử — đã xử lý P1–P5)

| ID | Trạng thái | Ghi chú ngắn |
|----|------------|--------------|
| BUG-001–006, 009–013 | ✅ | Admin + Beanie search/delete |
| BUG-003, 007–008, 011, 014 | ✅ | Classes progress, quiz, role, status dates |
| BUG-004 | ✅ | `get_course_detail_admin` |
| BUG-010 | ✅ | (cùng nhóm search regex) |
| BUG-014 | ✅ | `start_date` tương lai → `preparing`; join khi `active` |

**Known (không phải 500):** KNOWN-001 recommendations chưa evaluate → 404; KNOWN-002 lesson document; KNOWN-003 practice lesson_id; KNOWN-004 E2E cần API key. **Auth:** forgot/reset password covered in `tests/auth/test_password_reset.py`.

---

## 6. Lệnh tham chiếu

```powershell
cd BE
python tests/run_tests.py
python tests/run_tests.py -v tests/rbac/
pytest --collect-only -q
```

Cập nhật snapshot OpenAPI sau đổi router:

```powershell
python scripts/export_openapi.py
```

---

## 7. Lịch sử log

| Ngày | Thay đổi |
|------|----------|
| 2026-05-19 | Tạo log: 88 operations, ma trận test/RBAC, 14 bug, 16 flow, mục chưa cover |
| 2026-05-19 | INFRA-002: export OpenAPI (79 paths), Postman regen; roadmap E1–E9 chốt |
