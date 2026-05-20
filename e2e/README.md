# E2E (Playwright)

## Chạy nhanh (không cần Google API)

Sau `cd BE && python -m scripts.init_data`:

```powershell
cd e2e
npx playwright test instructor roadmap-epics admin route-guards personal-courses student-join-class auth
```

## Tạm ngưng — cần `GOOGLE_API_KEY`

Các spec sau **tự skip** khi không có key (hoặc `fake-key-not-used-in-tests`):

| File | Lý do |
|------|--------|
| `assessment-flow.spec.js` | Live assessment generation |
| `student-flow.spec.js` | Live assessment |
| `chat.spec.js` | Live Gemini chat |
| `personal-courses.spec.js` | `POST /courses/from-prompt` (describe «Personal course from-prompt») |

Không chạy nhóm này trong CI/local trừ khi đã cấu hình API key thật.

## Web servers

Playwright tự khởi động BE `:8000` + FE `:3000` (xem `playwright.config.js`). Có thể tái sử dụng server đang chạy khi không ở CI.
