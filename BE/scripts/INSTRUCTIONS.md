# HƯỚNG DẪN QUY TRÌNH PATCH NỘI DUNG GIÁO TRÌNH (RUNBOOK)

Tài liệu này hướng dẫn chi tiết quy trình cập nhật nội dung bài học từ các placeholder (`[CONTENT_PLACEHOLDER]`) thành nội dung học thuật HTML thực tế, giúp lập trình viên hoặc các tác nhân AI ở các phiên làm việc tiếp theo thực hiện chính xác và không gặp lỗi.

---

## 1. Mục Tiêu & Công Cụ Duy Nhất
*   **Mục tiêu**: Thay thế toàn bộ trường `content` của các bài học có dạng `"[CONTENT_PLACEHOLDER]"` trong tệp `BE/scripts/courses_import.json` bằng nội dung HTML học thuật phong phú, có kèm code mẫu.
*   **Công cụ**: Tệp kịch bản [patch_courses_content.py](file:///c:/Users/Admin/Downloads/AI-Learning-Platform/BE/scripts/patch_courses_content.py) là nơi duy nhất quản lý dữ liệu hardcoded và áp dụng các bản vá (patch) vào JSON. **Không tạo thêm các file script mới lẻ tẻ** để giữ thư mục gọn gàng.

---

## 2. Quy Trình Thực Hiện Từng Bước

### Bước 1: Soạn thảo nội dung học thuật cho Khóa học mới
1. Mở tệp [patch_courses_content.py](file:///c:/Users/Admin/Downloads/AI-Learning-Platform/BE/scripts/patch_courses_content.py).
2. Tạo một từ điển Python mới dạng `course_X_lessons_content = { ... }` (với `X` là số thứ tự khóa học).
3. Định nghĩa nội dung bài học dạng chuỗi đa dòng HTML:
   ```python
   course_5_lessons_content = {
       "Tên Bài Học Đầu Tiên": """
   <h2>Tiêu đề Lớn</h2>
   <p>Nội dung lý thuyết học thuật chi tiết bằng tiếng Việt...</p>
   <h3>Tiêu đề phụ</h3>
   <pre><code>// Code mẫu minh họa
   void main() {
       print("Hello World");
   }
   </code></pre>
   """,
   }
   ```

### Bước 2: Tích hợp vào hàm patch chính
Di chuyển xuống cuối file [patch_courses_content.py](file:///c:/Users/Admin/Downloads/AI-Learning-Platform/BE/scripts/patch_courses_content.py) tại hàm `patch_courses_import()` và thêm logic cho khóa học mới:
```python
    # X. Patch Course X
    course_x = courses[index_của_khóa_học_trong_json] # Ví dụ: index 4 cho khóa học thứ 5
    print(f"Patching Course X: {course_x['title']}")
    patched_cx = 0
    for module in course_x.get("modules", []):
        for lesson in module.get("lessons", []):
            title = lesson["title"]
            if title in course_x_lessons_content:
                lesson["content"] = course_x_lessons_content[title]
                patched_cx += 1
            else:
                print(f"Warning: No content defined for lesson '{title}' in Course X")
```
Đồng thời, cập nhật dòng in tóm tắt ở cuối hàm để theo dõi:
```python
    print(f"Summary: Patched {patched_c1} lessons for Course 1, ..., {patched_cx} lessons for Course X.")
```

### Bước 3: Chạy script cập nhật dữ liệu
*   **Trên môi trường Windows**: Luôn chạy command với cờ `-Xutf8` để ép kiểu đọc/ghi file UTF-8, tránh hoàn toàn lỗi `UnicodeDecodeError` do bảng mã hệ thống mặc định (CP1252):
    ```bash
    python -Xutf8 scripts/patch_courses_content.py
    ```
*   **Trên Linux/macOS**:
    ```bash
    python scripts/patch_courses_content.py
    ```

---

## 3. Các Lỗi Thường Gặp & Cách Khắc Phục (CRITICAL)

### Lỗi 1: `SyntaxError: invalid syntax` do xung đột nháy kép `"""`
*   **Nguyên nhân**: Khi viết các khối code ví dụ trong nội dung bài học (nhất là code Python hoặc Dart chứa docstring dạng `"""Docstring"""`), trình thông dịch Python sẽ hiểu nhầm dấu nháy kép `"""` đó là điểm kết thúc chuỗi của bài học.
*   **Cách khắc phục**:
    *   **Phương án 1 (Khuyên dùng)**: Thay thế toàn bộ dấu ba nháy kép `"""` bên trong code ví dụ thành ba nháy đơn `'''`. Cú pháp docstring trong code mẫu vẫn hoàn toàn hợp lệ và không làm hỏng cấu trúc chuỗi ngoài.
    *   **Phương án 2**: Sử dụng thực thể HTML mã hóa tương ứng `&quot;&quot;&quot;` cho dấu nháy kép để trình duyệt tự động render ra ký tự `"""` mà không gây lỗi cú pháp script.

### Lỗi 2: `UnicodeDecodeError: 'charmap' codec can't decode byte...`
*   **Nguyên nhân**: Chạy Python trên Windows mà không chỉ định rõ mã hóa UTF-8 khi đọc/ghi các tệp JSON và script chứa tiếng Việt có dấu.
*   **Cách khắc phục**: Luôn chạy file script Python bằng lệnh `python -Xutf8 <path_to_script>`. Ngoài ra, trong code Python mở file, luôn thêm tham số `encoding="utf-8"`:
    ```python
    with open(json_path, "r", encoding="utf-8") as f:
    ```

### Lỗi 3: Dữ liệu biến mất sau khi chạy seed
*   **Nguyên nhân**: Chạy kịch bản khởi tạo lại cơ sở dữ liệu `init_data.py` mà quên mất chưa patch nội dung mới vào `courses_import.json`.
*   **Cách khắc phục**: Luôn đảm bảo chạy cập nhật nội dung bài học trước khi khởi chạy lệnh seeding. Tuyệt đối không cần thiết phải chạy `init_data.py` sau mỗi lần patch một khóa học riêng lẻ để tiết kiệm thời gian và tài nguyên.
