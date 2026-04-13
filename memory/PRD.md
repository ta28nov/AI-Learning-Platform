# PRD - AI Learning Platform - Báo cáo Kiểm tra 1-1 BE ↔ FE

## Trạng thái hệ thống
- Backend: ✅ Running (FastAPI + MongoDB + Gemini AI)
- Frontend: ✅ Running (Vite + React)
- Database: ✅ Seeded (14 users, 9 courses, modules, lessons, quizzes, enrollments)
- E2E Tests: ✅ All Passed

---

## Phase 2 (Nhóm 3): KHÁM PHÁ & ĐĂNG KÝ KHÓA HỌC — ĐÃ HOÀN THÀNH

| # | Endpoint | Trạng thái | Ghi chú |
|---|----------|-----------|---------|
| 3.1 | GET /courses/search | ✅ PASS (sau fix) | Fix category enum, level case, sort_by |
| 3.2 | GET /courses/public | ✅ PASS | Mapping chính xác |
| 3.3 | GET /courses/{id} | ✅ PASS | Nested objects đúng |
| 3.4 | POST /enrollments | ✅ PASS (sau fix) | Fix result.id vs enrollment_id |
| 3.5 | GET /enrollments/my-courses | ✅ PASS | Full response mapping |
| 3.6 | GET /enrollments/{id} | ✅ PASS | Schema fields khớp |
| 3.7 | GET /courses/{id}/enrollment-status | ✅ PASS | Mapping chính xác |
| 3.8 | DELETE /enrollments/{id} | ✅ PASS | Có confirm dialog |

## Phase 3 (Nhóm 4): HỌC TẬP & TIẾN ĐỘ — ĐÃ PHÂN TÍCH & SỬA

| # | Endpoint | Trạng thái | Ghi chú |
|---|----------|-----------|---------|
| 4.1 | GET /courses/{cid}/modules/{mid} | ✅ PASS (sau fix) | Fix lesson_count → total_lessons |
| 4.2 | GET /courses/{cid}/lessons/{lid} | ✅ PASS | All nested objects correct |
| 4.3 | GET /courses/{cid}/modules | ✅ PASS | ModuleListItem mapping đúng |
| 4.4 | GET /.../outcomes | ✅ PASS | URL đúng |
| 4.5 | GET /.../resources | ✅ PASS | URL đúng |
| 4.6 | POST /.../assessments/generate | ✅ PASS (sau fix) | Added AI_TIMEOUT |
| 4.7 | GET /quizzes/{id} | ⚠️ WARN | FE reads max_attempts/is_retakeable not in schema |
| 4.8 | POST /quizzes/{id}/attempt | ✅ PASS (sau fix) | Fix selected_option int→string "A","B" |
| 4.9 | GET /quizzes/{id}/results | ✅ PASS | All fields match |
| 4.10 | POST /quizzes/{id}/retake | ✅ PASS | No body needed |
| 4.11 | POST /ai/generate-practice | ✅ PASS (sau fix) | Added AI_TIMEOUT |
| 4.18 | GET /progress/course/{id} | ✅ PASS | URL mapping đúng |

## Phase 4 (Nhóm 2): ĐÁNH GIÁ NĂNG LỰC AI — ĐÃ PHÂN TÍCH & SỬA

| # | Endpoint | Trạng thái | Ghi chú |
|---|----------|-----------|---------|
| 2.1 | POST /assessments/generate | ✅ PASS (sau fix) | Fix categories + AI_TIMEOUT |
| 2.2 | POST /assessments/{id}/submit | ✅ PASS (sau fix) | Fix missing submitted_at |
| 2.3 | GET /assessments/{id}/results | ✅ PASS | All response fields mapped |

---

## Tổng hợp các fix đã thực hiện

### Phase 2 (5 FAIL + 3 WARN = 8 fixes):
1. Category enum values sai hoàn toàn
2. Level case sai (lowercase vs PascalCase)
3. sort_by phantom param
4. enrollment_id field name sai
5. lesson_count → total_lessons
6. AI_TIMEOUT cho module assessment
7. Level display logic
8. Category emoji mapping

### Phase 3-4 (4 FAIL + 2 WARN = 6 fixes):
1. selected_option int→string cho quiz attempt
2. submitted_at missing cho assessment submit
3. Category values sai cho assessment setup
4. AI_TIMEOUT cho assessments/generate
5. AI_TIMEOUT cho ai/generate-practice
6. Checkbox CSS pointer-events fix
