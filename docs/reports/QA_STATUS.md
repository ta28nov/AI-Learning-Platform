# QA snapshot

**Ngày:** 2026-05-19 (cập nhật GV deep QA: 2026-05-21)  
**Môi trường:** MongoDB local, `TESTING=true`, mock Gemini trong pytest.

## Kết quả chạy test

| Suite | Lệnh | Kỳ vọng |
|-------|------|---------|
| BE pytest | `cd BE && python tests/run_tests.py -q` | **184 passed** (E7 verify-email +3) |
| BE RBAC | `python tests/run_tests.py tests/rbac/ -q` | 31 passed |
| E2E (P7) | `cd e2e && npx playwright test admin instructor route-guards personal-courses` | **12 passed** (cần `init_data` trước) |
| E2E (P11–P16) | `cd e2e && npx playwright test instructor roadmap-epics` | **10 passed** (thêm E7 verify UI) |
| E2E Gemini | `assessment-flow`, `student-flow`, `chat`, `personal-courses` (from-prompt) | **Tạm ngưng** — xem `e2e/README.md` |
| Smoke tay | `cd BE && python -m scripts.smoke_test` | health + login (BE phải đang chạy) |

## Phase đã xong

- P1–P4: BUG-001–014  
- P5: RBAC dashboard/analytics  
- P6: SECRET_KEY doc, personal-courses guard, SEED_SCHEMA_MATRIX  
- P7: E2E mở rộng, `run_tests.py`, fix `ClassCreatePage` (`courses` + `limit=50`)

## P8 (mới)

- Route `/dashboard/classes` (student + instructor join)  
- E2E `student-join-class.spec.js`  
- KNOWN-004: `student-flow` skip khi thiếu `GOOGLE_API_KEY`  
- COV: `test_admin_list_users_by_status_inactive`, search `rating`+`instructor`

## P9 (xong)

- GAP-001 / KNOWN-005: `POST /auth/forgot-password`, `POST /auth/reset-password`, FE pages, `tests/auth/test_password_reset.py`

## P10 — Epic E1 Lớp học (2026-05-19)

- **BE:** `list_my_classes(user_id, role)`, `get_class_detail` cho student đã join; index `student_ids` trên `Class`
- **FE:** `/dashboard/classes/:classId`, `ClassDetailPage` role-aware (student read-only + vào khóa học; instructor edit/delete/progress tab)
- **Test:** `tests/classes/` 18 passed; FE `npm run build` OK
- **E2E:** `student-join-class` — assert `my-classes` ≥1 sau join (API)

## P11–P16 — Roadmap FE/BE (2026-05-19) ✅

| Epic | Nội dung | Verify |
|------|----------|--------|
| **E2** | Quiz GV: routes, form, kết quả lớp, `LessonPage` panel | BE `tests/quizzes/test_quiz_instructor.py`; E2E `instructor.spec.js` |
| **E3** | `/dashboard/instructor/analytics` | E2E analytics load; fix `student_answer` trong `dashboard_service` |
| **E4** | Admin modal tạo user/khóa học (`Input`, validation) | E2E `roadmap-epics.spec.js` |
| **E6** | Xóa khóa cá nhân `CourseEditorPage` | UI + `DELETE /courses/personal/{id}` (smoke tay) |
| **E8** | `/terms`, `/privacy` | E2E `roadmap-epics.spec.js` |
| **E9** | Panel search analytics (admin) | E2E `roadmap-epics.spec.js` |
| **E5** | Progress | `CourseDetailPage` wire `GET /progress/course/{id}` khi đã ghi danh; `ProgressPage` vẫn dùng analytics |
| **E7** | verify-email | ✅ `POST /auth/verify-email`, `resend-verification`, `VerifyEmailPage`; OAuth vẫn UI+toast |

## P17 — Epic E7 verify-email (2026-05-19)

- **BE:** `EmailVerificationTokenDocument`, token khi đăng ký (`TESTING` trả `verification_token`)
- **FE:** `VerifyEmailPage` — auto verify `?token=`, resend form, loading/success/error
- **Test:** `tests/auth/test_email_verification.py`
- **E2E:** `roadmap-epics` — form verify (không cần Gemini)

## Tiến độ so với plan (`fe-be-db_sync_process`)

| Bước plan | Epic | UI/UX | BE | E2E (không Gemini) |
|-----------|------|-------|-----|-------------------|
| 1 | Template | ✅ | — | — |
| 2 | E1 Lớp học | ✅ | ✅ | ✅ join |
| 3 | E2 Quiz GV | ✅ | ✅ | ✅ |
| 4 | E4 Admin | ✅ | ✅ | ✅ modal |
| 5 | E3 Analytics | ✅ | ✅ | ✅ |
| 6 | E6, E8, E9 | ✅ | ✅ | ✅ |
| 7 | E7 verify-email | ✅ | ✅ | ✅ form |
| — | E7 OAuth | ✅ placeholder FE | — (by design) | — |
| 8 | E5 progress wire | ✅ `CourseDetailPage` | ✅ | smoke tay |
| **UI/UX Plan Phase 5 (pre-deploy)** | — | PRE-001→007 | seed, assessment goals, AI rate limit, GV quiz/class/stats | xem `UI_UX_MANUAL_TEST_REPORT.md` §Phase 5 |

**E2E (sau `init_data`, không Gemini):**
```powershell
cd e2e && npx playwright test instructor roadmap-epics admin route-guards personal-courses student-join-class auth
```

## P18 — Epic E5 progress trên CourseDetail (2026-05-19)

- **FE:** `progressService.getCourseProgress` trên `CourseDetailPage` khi `is_enrolled`; stats + breakdown module/bài
- **FE:** `RegisterPage` → `/auth/verify-email?email=…` (token khi BE trả về, ví dụ `TESTING`)
- **Verify:** `npm run build` OK

## P19 — Plan closure + INFRA-002 (2026-05-19)

- **INFRA:** `BE/scripts/export_openapi.py`, `generate_postman.py` — snapshot 79 paths
- **OAuth:** Giữ placeholder FE (`SocialAuthButtons`, toast); **không** triển khai BE
- **Doc:** [`ROADMAP_CLOSURE.md`](ROADMAP_CLOSURE.md), [`PLAN_STATUS.md`](PLAN_STATUS.md)

## Backlog tùy chọn

- E2E assessment/chat/from-prompt (cần `GOOGLE_API_KEY`)

## P20 — UI/UX manual QA (đang chạy)

- Plan: [`.cursor/plans/ui_ux_editorial_refactor_plan_e17edc9e.plan.md`](../.cursor/plans/ui_ux_editorial_refactor_plan_e17edc9e.plan.md)
- Báo cáo: [`UI_UX_MANUAL_TEST_REPORT.md`](UI_UX_MANUAL_TEST_REPORT.md)
- **2026-05-21:** Fix **UIUX-032** (GV 403 lesson content khi tạo quiz) + retest deep luồng instructor — §Phase 7 báo cáo; pytest `test_instructor_lesson_content_without_enrollment` pass
- **2026-05-21:** Retest browser luồng **học viên** `/dashboard/classes` — §7.9 báo cáo (list/detail/tabs/resume/guard PASS; UIUX-033 CSS OK cho HV)
- **2026-05-21:** Deep retest **toàn bộ UI/luồng HV** — §7.10 (17/18 trang PASS; UIUX-HV-05 module detail fail trên 1 module)
- **2026-05-21:** Fix **UIUX-HV-05/HV-03/GV-02/030/031** + deep retest §7.11 — module detail PASS; quiz titles class progress PASS; profile save PASS; personal course modals PASS
- **2026-05-21:** Seed/polish **HV-01/02/04/06/07, GV-01/03/06** — `init_data`, `curriculum_content`, `patch_seed_display.py`, mobile sidebar CSS; deep retest HV §7.12 (enrollment, join mã `B8BBA609`, quiz/assessment/class copy PASS)
- **2026-05-21:** Deep retest luồng HV còn lại §7.13 — chat AI PASS, quiz results PASS, lesson→quiz PASS; assessment resume in-progress **FAIL** (UIUX-HV-08)

Chi tiết: `ROADMAP_CLOSURE.md` · bug cũ: `TEST_ISSUES_AND_GAPS.md` · API: `API_COVERAGE_LOG.md`
