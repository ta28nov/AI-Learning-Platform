# Implementation Plan Template

Copy file này cho mỗi epic/task trước khi code. Plan epic lưu tại `.cursor/plans/<epic>_<id>.plan.md`.

## 1. Phân tích yêu cầu

- **User story:**
- **Role:** student | instructor | admin
- **Acceptance criteria:**
  - Given …
  - When …
  - Then …
- **Out of scope:**

## 2. Flow & matrix đồng bộ

| Layer | File / endpoint | Thay đổi |
|-------|-----------------|----------|
| DB | | |
| BE schema | | |
| BE service | | |
| BE router + auth | | |
| FE service | | |
| FE page/component | | |
| State | | |

## 3. Task breakdown

### FE Tasks
- [ ]

### BE Tasks
- [ ]

### DB Tasks
- [ ]

### AI Tasks (nếu có)
- [ ]

### Testing Tasks
- [ ]

### Refactor Tasks
- [ ]

## 4. UI/UX

- Tokens: `FE/src/styles/tokens.css`
- Components: `StateView`, `Modal`, `Button`, `AILoadingState`
- States: loading / empty / error / validation (tiếng Việt)

## 5. API contract

```json
// Request
// Response
```

HTTP: 200 | 201 | 400 | 403 | 404

## 6. Auth / permission

- BE: `middleware/rbac.py`, ownership
- FE: `AppRouter.jsx` guards

## 7. Logging & debug

| Triệu chứng | Kiểm tra |
|-------------|----------|
| UI trống | Network tab, JWT role, response body |
| 403 | RBAC + route guard |
| 500 | pytest reproduce |

## 8. Test plan

```powershell
cd BE && python tests/run_tests.py tests/<module>/ -q
cd e2e && npx playwright test <spec>
```

## Definition of Done

- [ ] Pytest pass
- [ ] E2E liên quan (hoặc skip có lý do)
- [ ] `docs/reports/API_COVERAGE_LOG.md` cập nhật
- [ ] `docs/reports/QA_STATUS.md` cập nhật
