# Roadmap closure — FE/BE/DB sync plan

**Ngày chốt:** 2026-05-19  
**Plan gốc:** `.cursor/plans/fe-be-db_sync_process_a8a9c6d1.plan.md`

## Epics đã hoàn thành

| Epic | Mô tả | Ghi chú |
|------|--------|---------|
| E1 | Lớp học role-aware | `my-classes`, student detail, E2E join |
| E2 | Quiz giảng viên | CRUD, class results, lesson panel |
| E3 | Analytics giảng viên | `InstructorAnalyticsPage` |
| E4 | Admin CRUD UI | Modal user/course |
| E5 | Progress | `CourseDetailPage` + `GET /progress/course/{id}` |
| E6 | Xóa khóa cá nhân | `CourseEditorPage` |
| E7 | verify-email | BE + FE + pytest + E2E form |
| E8 | Terms / Privacy | `LegalPage` |
| E9 | Search analytics | Admin panel trên search |

## Cố ý không triển khai (theo product)

| Hạng mục | Trạng thái | Lý do |
|----------|------------|--------|
| **OAuth (Google/Facebook)** | FE placeholder only | `SocialAuthButtons` — toast “sắp có”; **không có BE** |
| **E2E Gemini** | Tạm ngưng | `assessment-flow`, `student-flow`, `chat`, from-prompt — cần `GOOGLE_API_KEY` |
| **GAP-004 ProgressPage** | By design | Trang tổng quan vẫn dùng `/analytics/*`; chi tiết khóa dùng progress API |

## INFRA

| ID | Nội dung | Trạng thái |
|----|----------|------------|
| INFRA-002 | Export OpenAPI + Postman | ✅ `BE/scripts/export_openapi.py`, `generate_postman.py` |

```powershell
cd BE
python scripts/export_openapi.py
python scripts/generate_postman.py
```

Snapshot: `BE/tests/fixtures/openapi.json` (79 paths sau chốt). Postman: `docs/postman/AI-Learning-Platform.postman_collection.json`.

## Verify cuối

| Kiểm tra | Lệnh | Kỳ vọng |
|----------|------|---------|
| BE | `python tests/run_tests.py -q` | 184 passed |
| FE build | `cd FE && npm run build` | OK |
| E2E (không Gemini) | `cd e2e && npx playwright test instructor roadmap-epics admin route-guards personal-courses student-join-class auth` | sau `init_data` |

Báo cáo chi tiết: [`QA_STATUS.md`](QA_STATUS.md) · API: [`API_COVERAGE_LOG.md`](API_COVERAGE_LOG.md).
