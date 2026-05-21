# Ma trận seed — `scripts/init_data.py`

**Nguồn:** đọc trực tiếp từ [`BE/scripts/init_data.py`](../../scripts/init_data.py) (`SeedConfig`, `main()`, `validate_integrity()`).  
**Chạy:** `cd BE && python -m scripts.init_data` (full reset collections rồi seed).

---

## 1. Cấu hình mặc định (`SeedConfig`)

| Tham số | Giá trị mặc định | Ý nghĩa |
|---------|------------------|---------|
| `seed` | `20260507` | Random seed (deterministic) |
| `admins` | 10 | Số user role `admin` |
| `instructors` | 40 | Số user role `instructor` |
| `students` | 360 | Số user role `student` |
| `public_courses` | 70 | Khóa public (catalog) |
| `personal_courses` | 80 | Khóa cá nhân (`course_type` personal) |
| `public_modules_per_course` | 6 | Module / khóa public |
| `public_lessons_per_module` | 6 | Lesson / module public |
| `personal_modules_per_course` | 4 | Module / khóa personal |
| `personal_lessons_per_module` | 5 | Lesson / module personal |
| `classes` | 90 | Lớp học (`classes` collection) |

---

## 2. Collections MongoDB (Beanie `Settings.name`)

| Collection | Model | Ghi chú seed |
|------------|-------|----------------|
| `users` | `User` | Admins, instructors, students + demo accounts |
| `refresh_tokens` | `RefreshToken` | Một phần user có token demo |
| `password_reset_tokens` | `PasswordResetTokenDocument` | Có thể có bản ghi; **không có API forgot password** |
| `courses` | `Course` | Public + personal; embedded modules/lessons trên document |
| `modules` | `Module` | Bản ghi tách cho public courses |
| `lessons` | `Lesson` | Bản ghi tách; quiz có thể gắn `quiz_id` |
| `enrollments` | `Enrollment` | Student ↔ course |
| `progress` | `Progress` | `lessons_progress`, `overall_progress_percent` |
| `quizzes` | `Quiz` | Gắn lesson/course |
| `quiz_attempts` | `QuizAttempt` | Attempts có `started_at` |
| `assessment_sessions` | `AssessmentSession` | Một số đã submit để test recommendations |
| `recommendations` | `Recommendation` | Có `source=assessment` khi có session |
| `conversations` | `Conversation` | Chat AI theo course |
| `classes` | `Class` | `instructor_id`, `student_ids`, `course_id` |

**Không seed riêng:** router-only aggregates; dữ liệu nhúng trong `Course.modules` / `EmbeddedLesson`.

---

## 3. Pipeline stages (`main()`)

1. `drop_all_collections()` — xóa toàn bộ collections đã đăng ký Beanie  
2. `seed_users(cfg)` → role IDs  
3. `seed_courses_modules_lessons(cfg, role_ids)` → `course_map`  
4. `seed_classes(cfg, role_ids, course_map)`  
5. `seed_enrollments_progress(cfg, role_ids, course_map)`  
6. `sync_classes_with_enrollments(class_ids)`  
7. `seed_quizzes_attempts(cfg, role_ids)`  
8. `seed_assessments_recommendations(role_ids, course_map)`  
9. `seed_conversations_tokens(role_ids, course_map)`  
10. `validate_integrity()` — in counts + `integrity_errors`  
11. `seed_report_accounts()` — in demo passwords  

---

## 4. Tài khoản demo (cuối script)

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin1@ailearning.vn` | `Admin@123456` |
| Instructor | `instructor1@ailearning.vn` | `Instructor@123` |
| Student | `student1@gmail.com` | `Student@123` |

---

## 5. Integrity (`validate_integrity`)

Script kiểm tra tham chiếu chéo: `owner_id` / `instructor_id` ∈ users, `course_id` ∈ courses, `module_id` / `lesson_id` hợp lệ, `progress_percent` ∈ [0, 100], class `student_ids` ∈ users, recommendation `course_id` và `assessment_session_id` nhất quán.

In summary counts (ví dụ): `users`, `courses`, `modules`, `lessons`, `enrollments`, `progress`, `quizzes`, `quiz_attempts`, `assessments`, `recommendations`, `conversations`, `classes`, `refresh_tokens`, `password_reset_tokens`, `integrity_errors`.

**PASS:** `integrity_errors == 0`.
