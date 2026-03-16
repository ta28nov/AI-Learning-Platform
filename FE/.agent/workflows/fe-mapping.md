---
description: Quy trình mapping BE → FE cho AI Learning Platform. Đọc file này mỗi khi bắt đầu phiên mới.
---

// turbo-all

# QUY TRÌNH MAPPING BE → FE

## BƯỚC 0: Đọc docs trước khi code
1. Đọc `FE/docs/BE_TO_FE_MAPPING.md` — tìm endpoint cần dùng
2. Đọc `FE/docs/FE_CODING_RULES.md` — tuân thủ quy tắc code
3. Đọc `FE/docs/FE_MAPPING_CHECKLIST.md` — xem task nào đang dang dở

## BƯỚC 1: Kiểm tra BE schema thực tế
```bash
# Đọc schema Pydantic tương ứng
cat BELEARNINGAI/schemas/<module>.py
```
⚠️ **Luôn ưu tiên code BE thực tế** hơn docs FE nếu có xung đột.

## BƯỚC 2: Viết/Sửa service
- File: `FE/src/services/<name>Service.js`
- Pattern: `import api from './api'` → `api.get/post/put/delete`
- Comment tiếng Việt không dấu
- Không cài thêm package

## BƯỚC 3: Viết/Sửa page component
- File: `FE/src/pages/<feature>/<Name>Page.jsx` + `.css`
- Pattern chuẩn trong `FE_CODING_RULES.md` section "Page Component Pattern"
- Luôn có 3 states: `data`, `loading`, `error`
- Field names **PHẢI KHỚP** BE schema (xem ⚠️ trong docs)
- Toast dùng `result.message` từ BE, không hard-code

## BƯỚC 4: Checklist trước khi hoàn thành
- [ ] Field names khớp BE schema (avatar vs avatar_url, user_id vs id...)
- [ ] Nullable fields có `?.` optional chaining
- [ ] Loading/Error states đầy đủ (skeleton + toast)
- [ ] Status values đúng format (`in-progress` hyphen, không underscore)
- [ ] Toast dùng response.message từ BE
- [ ] CSS: BEM naming, mobile-first
- [ ] Build pass: `npx vite build` → 0 errors

## BƯỚC 5: Cập nhật docs
- Đánh dấu ✅ trong `FE_MAPPING_CHECKLIST.md`
- Update checklist cuối `BE_TO_FE_MAPPING.md`

## ⚠️ CẢNH BÁO QUAN TRỌNG (đã phát hiện)
| Vấn đề | Chi tiết |
|--------|----------|
| LoginResponse | `user.avatar` (KHÔNG CÓ `_url`). Map sang `avatar_url` khi lưu store |
| RegisterRequest | KHÔNG có field `role`. Mặc định student |
| AdminUserListItem | Dùng `user_id` (không phải `id`), `avatar` (không phải `avatar_url`) |
| Admin Dashboard | `users_by_role.student` (SỐ ÍT, không phải `students`) |
| Enrollment status | `in-progress` (hyphen) không phải `in_progress` |
| ClassListItem | `student_count` là `str` format "25/30" (không phải int) |

## 📁 Docs cần đọc
- `FE/docs/BE_TO_FE_MAPPING.md` — mapping chi tiết 87 endpoints
- `FE/docs/FE_CODING_RULES.md` — quy tắc code + 11 flows UI
- `FE/docs/FE_MAPPING_CHECKLIST.md` — checklist từng page
