# Báo cáo lỗi phát hiện qua pytest & phần chưa cover

**Ngày:** 2026-05-19 (cập nhật sau P1–P6)  
**Ngữ cảnh:** Phase 2 test coverage — chạy `pytest` với MongoDB local, mock Gemini (`TESTING=true`). **173 passed** (full suite).

**Danh sách API + flow + log coverage:** [`API_COVERAGE_LOG.md`](API_COVERAGE_LOG.md) (bảng đầy đủ ~88 operations, bug registry, luồng chưa E2E).

### Trạng thái sửa (2026-05-19)

| Nhóm | ID | Trạng thái |
|------|-----|------------|
| Admin 500 | BUG-001–002, 004–006, 009–013 | ✅ Đã sửa — `tests/admin/` assert 200/201 |
| Classes | BUG-003, 007–008, 011, 014 | ✅ Đã sửa — `tests/classes/` |
| RBAC | RBAC-R1, R3–R5 (R2 = BUG-011) | ✅ `middleware/rbac` + `tests/rbac/` (31 tests) |
| Docs/FE gap | GAP-002, GAP-005, GAP-006 | ✅ QUICKSTART `SECRET_KEY`, `StudentOrInstructorRoute`, `SEED_SCHEMA_MATRIX.md` |
| By design | GAP-004 ProgressPage | ✅ FE dùng analytics (không đổi wire `progress_router`) |
| Đã xong | KNOWN-005 / GAP-001 forgot-reset password | ✅ BE + FE + `tests/auth/test_password_reset.py` |
| P7 E2E | E2E-001–004, `run_tests.py` | ✅ `admin`, `instructor`, `route-guards`, `personal-courses` specs |

---

## 1. Lỗi backend (HTTP 500) — **đã sửa** (lưu lại để tra cứu)

### BUG-001: `GET /api/v1/admin/users/{user_id}` → 500

| Mục | Chi tiết |
|-----|----------|
| **Endpoint** | `GET /admin/users/{user_id}` |
| **Khi reproduce** | Admin JWT hợp lệ; user tồn tại (student/instructor/admin, có hoặc không enrollment) |
| **HTTP** | `500 Internal Server Error` |
| **Body** | `{"detail": "Lỗi khi lấy chi tiết người dùng: created_at"}` |
| **File** | `BE/controllers/admin_controller.py` → `admin_service.get_user_detail_admin()` |
| **Nguyên nhân gốc** | Service trả `created_at` / `last_login_at` dạng **chuỗi ISO** (`user.created_at.isoformat()`), trong khi `AdminUserDetailResponse` (`BE/schemas/admin.py`) khai báo kiểu **`datetime`**. Pydantic validation fail khi `AdminUserDetailResponse(**user_detail)`. |
| **Lỗi phụ (student có enrollment)** | `enrollment.progress` — model `Enrollment` chỉ có `progress_percent`, không có field `progress` (`BE/services/admin_service.py` ~dòng 175). Gây `AttributeError` nếu sửa xong datetime. |
| **Lỗi phụ (schema)** | Service trả thêm `enrollments`, `courses`, `recent_activity`, `statistics` không có trong `AdminUserDetailResponse` (có thể gây lỗi tùy cấu hình Pydantic). |
| **Test hiện tại** | Không assert 200; smoke CRUD user bỏ bước GET detail. |
| **Gợi ý sửa** | Trả `datetime` object; đổi `progress` → `progress_percent`; căn schema với payload hoặc dùng response model mở rộng. |

---

### BUG-002: `POST /api/v1/admin/courses` → 500

| Mục | Chi tiết |
|-----|----------|
| **Endpoint** | `POST /admin/courses` |
| **Body mẫu** | `title`, `description`, `category`, `level`, `status: draft` (đúng `AdminCourseCreateRequest`) |
| **HTTP** | `500` |
| **Body** | `Lỗi khi tạo khóa học: 1 validation error for Course\nowner_id\n  Field required` |
| **File** | `BE/services/admin_service.py` → `create_course_admin()` |
| **Nguyên nhân gốc** | Tạo `Course(...)` **không gán `owner_id`** (bắt buộc trên `BE/models/models.py` `Course.owner_id`). Chỉ set `instructor_id` từ `creator_id` / `instructor_id` trong body — request admin **không có** các field này → `instructor_id=None`. |
| **Lỗi phụ (nếu tạo DB thành công)** | Response service thiếu `course_type`, `created_by`; có `creator_name` thay vì schema `AdminCourseCreateResponse.created_by`. |
| **Gợi ý sửa** | Set `owner_id=current_admin_id`, `owner_type="admin"`; map response đúng schema. |

---

### BUG-003: `GET /api/v1/classes/{class_id}/progress` → 500

| Mục | Chi tiết |
|-----|----------|
| **Endpoint** | `GET /classes/{class_id}/progress` |
| **Khi reproduce** | Instructor owner của lớp; lớp không có học viên vẫn 500 |
| **HTTP** | `500` |
| **File** | `BE/controllers/class_controller.py` → `class_service.get_class_progress()` |
| **Nguyên nhân gốc** | **Lệch schema:** service trả `score_distribution`, `module_completion`, `most_completed_lessons`, `least_completed_lessons` (`BE/services/class_service.py` ~870–878). `ClassProgressResponse` (`BE/schemas/classes.py`) yêu cầu `average_progress`, `completion_rate`, `average_quiz_score`. `ClassProgressResponse(**result)` validation fail. |
| **Lỗi phụ** | `progress.lessons_progress` dùng `lp.get("lesson_id")` — thực tế là list `LessonProgressItem` (attribute access), có thể sai khi có dữ liệu progress. |
| **Test Phase 2** | `test_class_progress` chấp nhận `200` hoặc `500` (workaround tạm). |
| **Gợi ý sửa** | Tính và trả đúng field schema HOẶC đổi `ClassProgressResponse` khớp analytics hiện tại. |

---

## 2. Hành vi đã biết (không phải 500)

| ID | Mô tả | Ghi chú |
|----|--------|---------|
| **KNOWN-001** | `GET /recommendations/from-assessment` với session **chưa** submit/evaluate | Trả **404** (không phải 400); message: assessment chưa đánh giá. Test chấp nhận `(400, 404, 422)`. |
| **KNOWN-002** | `POST /lessons/{id}/quizzes` (instructor) | Cần document `Lesson` trong collection `lessons`, không chỉ `EmbeddedLesson` trong `Course`. Fixture test đã insert `LessonDocument`. |
| **KNOWN-003** | `POST /ai/generate-practice` với `lesson_id` embedded-only | **404** nếu không có bản ghi `lessons`. Test dùng `course_id` + `topic_prompt`. |
| **KNOWN-004** | E2E assessment / chat | Cần `GOOGLE_API_KEY` thật; spec `test.skip` nếu thiếu. |
| **KNOWN-005** | Forgot / reset / verify email | ✅ `forgot-password`, `reset-password`, `verify-email`, `resend-verification`. |
| **KNOWN-006** | OAuth Google/Facebook | **By design** — FE placeholder (`SocialAuthButtons`, toast); không có BE. |

---

## 2b. Kiểm tra RBAC (`BE/tests/rbac/`)

**Module `BE/middleware/rbac.py`:** hierarchy `admin ≥ instructor ≥ student`; `require_student_only` (exact student); factory `def` + `Depends()` (không còn coroutine shorthand lỗi).

**Router đã gắn:** `dashboard_router.py`, `analytics_router.py` (`require_student_only`, `require_instructor`).

**Controller:** `dashboard_controller`, `quiz_controller` dùng `ensure_student_only` / `ensure_minimum_role(INSTRUCTOR)`; admin vẫn `role == "admin"` trong `admin_controller`.

| Vùng | Cơ chế | Student | Instructor | Admin |
|------|--------|---------|------------|-------|
| `/admin/*` | `admin_controller` | 403 | 403 | 200 (data OK sau BUG fix) |
| `/dashboard/instructor`, `/analytics/instructor/*` | `require_instructor` + hierarchy | 403 | 200 | **200** |
| `/dashboard/student`, learning-stats, progress-chart | `require_student_only` | 200 | **403** | **403** |
| `POST/PUT/DELETE` quiz instructor | `ensure_minimum_role(INSTRUCTOR)` | 403 | 200 | **200** |
| `POST /classes` | instructor/admin only (BUG-011) | **403** | 201 | 201 |

**Test:** 31 cases — `test_rbac_module.py`, `test_admin_rbac_matrix.py`, `test_instructor_rbac_matrix.py`.

---

## 3. Ma trận coverage (pytest + E2E)

**Cập nhật:** sau P5 RBAC + admin/classes fix — **173** pytest, **74** path trong OpenAPI snapshot (`BE/tests/fixtures/openapi.json`).

| Ký hiệu | Ý nghĩa |
|---------|---------|
| ✅ | Có test gọi API; assert happy path hoặc RBAC 403 |
| ⚠️ | Đã gọi nhưng chỉ regression bug (500/404) hoặc assert lỏng `in (200, …)` |
| ❌ | Chưa có test pytest chuyên cho case đó |
| 🔶 | Chỉ E2E smoke UI (Playwright), không thay API test |

**Tóm tắt:** ~**68/74** path đã được gọi ≥1 lần trong pytest (~92%). Phần còn lại chủ yếu là **edge case / filter / luồng lỗi nghiệp vụ**, không phải route hoàn toàn bỏ quên.

---

### 3.1. Đã cover (theo nhóm router)

| Nhóm | Routes | File test chính | Ghi chú |
|------|--------|-----------------|--------|
| Auth | 4/4 | `auth/test_*.py` | register, login, refresh, logout |
| Users | 2/2 | `users/test_users.py` | GET/PATCH `/users/me` |
| Assessments | 5/5 | `assessments/`, `integration/` | generate, submit, results, history, review |
| Courses (catalog) | 4/4 | `courses/test_courses.py` | search, public, detail, enrollment-status |
| Enrollments | 4/4 | `enrollments/`, `integration/` | POST, my-courses, detail, DELETE |
| Learning | 6/6 | `learning/test_learning.py` | modules, lesson, complete, outcomes, resources, module assessment |
| Quizzes | 10/10 | `quizzes/`, `instructor/` | student + instructor CRUD, class-results, practice AI |
| Progress | 1/1 | `progress/test_progress.py` | `GET /progress/course/{id}` |
| Personal courses | 6/6 | `personal_courses/` | from-prompt, manual, list, detail, update, delete |
| Chat | 5/5 | `chat/test_chat.py` | send, history, conversation, delete |
| Recommendations | 2/2 | `recommendations/` | list, from-assessment |
| Dashboard | 3/3 | `dashboard/`, `rbac/` | student / instructor / admin |
| Analytics | 5/5 | `analytics/`, `rbac/` | student ×2, instructor ×3 |
| Search | 4/4 | `search/`, `rbac/` | universal, suggestions, history, analytics (admin) |
| Classes | 10/10 | `classes/`, `rbac/` | CRUD, join, students, progress (3 route lỗi data) |
| Admin | 17/17 | `admin/`, `rbac/` | full matrix RBAC + regression bugs |
| RBAC module | — | `rbac/test_rbac_module.py` | map quyền, hierarchy, router không import rbac |
| Health | 1 | `test_health.py` | `/health` |
| Integration flow | — | `integration/test_flow_steps.py` | assessment → recommend → enroll → lesson → quiz |

---

### 3.2. Admin & Instructor — chi tiết

**Admin (17 endpoint):** mọi route đã gọi; RBAC student/instructor → 403 (`test_admin_rbac_matrix.py`).

| Endpoint | Test |
|----------|------|
| `GET /admin/users` (+ `role`, sort) | ✅ |
| `GET /admin/users?keyword=` | ⚠️ BUG-012 |
| `GET /admin/users/{id}` | ⚠️ BUG-001 |
| `POST/PUT/DELETE /admin/users`, role, reset-password | ✅ (một số body tối thiểu) |
| `GET /admin/courses` | ✅ |
| `GET /admin/courses?keyword=` | ⚠️ BUG-010 |
| `GET/POST/PUT/DELETE /admin/courses/{id}` | ⚠️ BUG-002/004/005/009 |
| `GET /admin/classes` | ✅ |
| `GET /admin/classes?search=` | ⚠️ BUG-013 |
| `GET /admin/classes/{id}` | ✅ |
| Analytics growth / courses / system-health | ✅ / ⚠️ BUG-006 |

**Instructor:**

| Endpoint | Test |
|----------|------|
| `POST/GET/PUT/DELETE /classes`, `my-classes` | ✅ (`test_classes.py`, rbac) |
| `POST /classes` (student) | ⚠️ BUG-011 (201, không 403) |
| `POST /classes/join` | ✅ (assert lỏng 200/201) |
| `GET/DELETE …/students/{id}` | ⚠️ BUG-007 / BUG-008 |
| `GET …/progress` | ⚠️ BUG-003 |
| Quiz instructor CRUD + filters | ✅ |
| Instructor dashboard + analytics | ✅ + rbac (admin bị 403 — gap thiết kế) |

---

### 3.3. Chưa test hoặc còn mỏng (ưu tiên bổ sung)

#### Pytest — hành vi / edge case (`tests/*_filters.py`, `*_edge.py`, `test_quiz_limits.py`)

| # | Mục | Trạng thái | File test |
|---|-----|------------|-----------|
| 1 | Filter enrollment `status=` | ✅ | `enrollments/test_enrollments_filters.py` |
| 2 | `GET /courses/search` category/level/guest | ✅ | `courses/test_courses_filters.py` |
| 3 | `GET /search` guest + filters | ✅ | `search/test_search_extended.py` |
| 4 | Join mã sai / đã join / lớp đầy | ✅ | `classes/test_classes_edge.py` |
| 5 | Join lớp `preparing` | ⚠️ **BUG-014** | `test_join_class_preparing_status_rejected` |
| 6 | Xóa lớp có HV | ✅ 400 | `test_delete_class_with_students_rejected` |
| 7 | Quiz max attempts | ✅ 403 | `quizzes/test_quiz_limits.py` |
| 8 | Admin tạo student không password | ✅ 422 (schema bắt buộc password) | `admin/test_admin_edge.py` |
| 9 | Admin list `status=active` | ✅ | `admin/test_admin_edge.py` |
| 10 | Admin happy 200 sau sửa bug | ❌ chờ fix BUG-001–006 | |
| 11 | Ownership quiz instructor khác | ✅ có sẵn | `rbac/`, `instructor_coverage` |
| 12 | `GET /quizzes` admin | ✅ có sẵn | `rbac/test_instructor_rbac_matrix.py` |

#### RBAC / bảo mật (đã phát hiện, chưa sửa BE)

| # | Mục | Hiện trạng |
|---|-----|------------|
| R1 | `middleware/rbac.py` | Không gắn router; shorthand `require_*` broken |
| R2 | Student tạo lớp | BUG-011 |
| R3 | Instructor vào student dashboard/analytics | 200 (không check role) — `test_instructor_rbac_matrix` |
| R4 | Admin vào instructor dashboard | 403 (lệch hierarchy rbac.py) |
| R5 | Admin mutate quiz | 403 (exact `instructor` string) |

#### E2E Playwright (`e2e/tests/`)

| Spec | Cover | Chưa cover |
|------|-------|------------|
| `auth.spec.js` | login | register, logout |
| `student-flow.spec.js` | luồng HV | — |
| `enrollment-lesson.spec.js` | enroll + lesson | — |
| `quiz.spec.js` | quiz | — |
| `assessment-flow.spec.js` | generate (skip nếu không API key) | submit + results |
| `chat.spec.js` | skip nếu không API key | — |
| `recommendations.spec.js` | smoke | — |
| `admin.spec.js` 🔶 | 1 màn users tab | courses, classes, analytics UI |
| `instructor.spec.js` 🔶 | dashboard + classes list | tạo lớp, quiz UI, analytics chart |

**E2E guards:** `e2e/tests/route-guards.spec.js`. **Smoke tay:** `BE/scripts/smoke_test.py` (health + login, không thay pytest). **Auth reset:** forgot/reset password đã có BE+FE; verify-email chưa.

---

### 3.4. Lệnh kiểm tra coverage nhanh

```powershell
cd BE
pytest --collect-only -q          # đếm case (171)
pytest tests/rbac -v              # ma trận RBAC
pytest -q                         # full suite
```

So khớp route ↔ test: tìm path trong `tests/` và đối chiếu `BE/tests/fixtures/openapi.json`.

---

### BUG-004: `GET /api/v1/admin/courses/{course_id}` → 500

| Mục | Chi tiết |
|-----|----------|
| **HTTP** | `500` |
| **Body** | `Lỗi khi lấy chi tiết khóa học: module 'services.course_service' has no attribute 'get_course_detail'` |
| **File** | `BE/controllers/admin_controller.py` → `handle_get_course_detail_admin()` |
| **Nguyên nhân** | Gọi `course_service.get_course_detail(...)` — hàm **không tồn tại**. Đúng ra phải gọi `course_service.get_course_detail_admin(course_id)` (`BE/services/course_service.py` có định nghĩa). |

---

### BUG-005: `PUT /api/v1/admin/courses/{course_id}` → 500 (response)

| Mục | Chi tiết |
|-----|----------|
| **HTTP** | `500` (có thể đã ghi DB) |
| **Body** | `2 validation errors for AdminCourseUpdateResponse` — thiếu `title`, `status` |
| **File** | `BE/services/admin_service.py` → `update_course_admin()` |
| **Nguyên nhân** | Service chỉ trả `{course_id, message, updated_at}`; schema `AdminCourseUpdateResponse` bắt buộc `title` + `status`. |

---

### BUG-006: `GET /api/v1/admin/analytics/system-health` → 500

| Mục | Chi tiết |
|-----|----------|
| **HTTP** | `500` |
| **Body** | `Lỗi khi lấy system health: created_at` |
| **Nguyên nhân** | Cùng nhóm lỗi **datetime vs chuỗi ISO** trong payload analytics (tương tự BUG-001). |

**Lưu ý:** `GET /admin/analytics/users-growth` và `/admin/analytics/courses` trả **200** trong pytest.

---

### BUG-007: `GET /api/v1/classes/{class_id}/students/{student_id}` → 500

| Mục | Chi tiết |
|-----|----------|
| **HTTP** | `500` |
| **Body** | `Lỗi khi lấy thông tin học viên: course_id` |
| **File** | `BE/services/class_service.py` → `get_student_detail()` |
| **Nguyên nhân** | Query `QuizAttempt.find(..., QuizAttempt.course_id == cls.course_id)` — model `QuizAttempt` **không có field `course_id`** (chỉ `quiz_id`, `user_id`, …). |
| **Lỗi phụ** | `EmbeddedModule` không có `default_quiz_id`; `progress.lessons_progress` dùng `.get()` trên `LessonProgressItem` object. |

---

### BUG-009: `DELETE /api/v1/admin/courses/{course_id}` → 500

| Mục | Chi tiết |
|-----|----------|
| **Body** | `Lỗi khi xóa khóa học: 'ExpressionField' object is not callable` |
| **File** | `BE/services/admin_service.py` (truy vấn Beanie khi xóa / kiểm tra dependency) |

---

### BUG-010: `GET /api/v1/admin/courses?keyword=...` → 500

| Mục | Chi tiết |
|-----|----------|
| **Ghi chú** | `GET /admin/courses` **không** filter → **200**; thêm `keyword` → **500** |
| **Body** | `'ExpressionField' object is not callable` |

---

### BUG-011: `POST /api/v1/classes` — student được tạo lớp

| Mục | Chi tiết |
|-----|----------|
| **HTTP** | **201** (mong đợi **403**) |
| **File** | `BE/controllers/class_controller.py` → `handle_create_class()` |
| **Nguyên nhân** | Không kiểm `current_user.role == "instructor"`; mọi user đăng nhập đều gọi `create_class(instructor_id=user_id)`. |

---

### BUG-012: `GET /api/v1/admin/users?keyword=...` → 500

| Mục | Chi tiết |
|-----|----------|
| **Ghi chú** | `GET /admin/users?role=student` → **200**; thêm `keyword` → **500** |
| **Body** | `'ExpressionField' object is not callable` |

---

### BUG-013: `GET /api/v1/admin/classes?search=...` → 500

| Mục | Chi tiết |
|-----|----------|
| **Ghi chú** | `GET /admin/classes?page=1` → **200**; thêm `search` → **500** |
| **Body** | `'ExpressionField' object is not callable` |

---

### BUG-014: `POST /classes` → `preparing`; `POST /classes/join` cần `active`

| Mục | Chi tiết |
|-----|----------|
| **HTTP** | Join ngay sau tạo lớp → **400** `Lớp học không ở trạng thái active` |
| **Nguyên nhân** | `create_class()` set `status="preparing"`; `join_class_with_code()` chỉ cho `active`. `ClassUpdateRequest` **không** có field `status` → không kích hoạt lớp qua API. |
| **File** | `BE/services/class_service.py`, `BE/schemas/classes.py` |
| **Test** | `tests/classes/test_classes_edge.py::test_join_class_preparing_status_rejected` |
| **Gợi ý sửa** | Tạo lớp với `status=active` khi `start_date <= now`, hoặc thêm `status` vào `ClassUpdateRequest` / auto-activate. |

---

### BUG-008: `DELETE /api/v1/classes/{class_id}/students/{student_id}` → 404 (sau join)

| Mục | Chi tiết |
|-----|----------|
| **HTTP** | `404` sau `POST /classes/join` thành công |
| **Nguyên nhân có thể** | `student_id` từ JWT/`user` object không khớp id trong `class.student_ids`, hoặc join không ghi student (cần kiểm tra thêm). Test regression ghi nhận 404. |

---

## 4. Việc đã làm (tích lũy)

- Báo cáo này + ma trận §3 (coverage + gap).
- Phase 2: integration, E2E, admin/instructor coverage.
- `BE/tests/rbac/` — unit rbac + ma trận Admin/Instructor.
- Edge §3.3: `test_enrollments_filters`, `test_courses_filters`, `test_search_extended`, `test_classes_edge`, `test_quiz_limits`, `test_admin_edge`.
- Regression BUG-001 → BUG-014 (xem §1 và bảng §3.2–3.3).

---

## 5. Ưu tiên test tiếp theo (gợi ý)

1. **Sửa BUG-001–013** rồi đổi test regression sang assert `200`/`201`.
2. **Edge classes** (join lỗi, xóa lớp có học viên) + **enrollment/search filters**.
3. **Wire `middleware/rbac`** lên router → cập nhật `tests/rbac` theo hierarchy thống nhất.
4. **E2E admin/instructor** — thêm 2–3 flow UI (tạo user, tạo lớp) nếu cần demo.

---

## 6. Lệnh tái hiện nhanh

```powershell
cd BE
# BUG-001
pytest tests/admin/test_admin_extended.py::test_admin_get_user_detail_known_bug -v

# BUG-002
pytest tests/admin/test_admin_extended.py::test_admin_create_course_known_bug -v

# BUG-003
pytest tests/classes/test_classes.py::test_class_progress -v

pytest -q
```
