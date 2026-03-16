1/ 
routes C:\Users\Admin\Downloads\AI-Learning-Platform\BELEARNINGAI\routers\recommendation_router.py
Chưa hoàn thành service cho api này 
todo AI đề xuất khóa học dựa trên lịch sử học tập và sở thích :
get_recommendations_api_v1_recommendations_get
2/ Chưa viết logic cho api này :
Có routers, nhưng chưa có service để xử lý logic :
Analytics


GET
/api/v1/analytics/learning-stats
Thống kê học tập chi tiết



GET
/api/v1/analytics/progress-chart
Biểu đồ tiến độ theo thời gian



GET
/api/v1/analytics/instructor/classes
Thống kê các lớp học của giảng viên



GET
/api/v1/analytics/instructor/progress-chart
Biểu đồ tiến độ lớp học theo thời gian



GET
/api/v1/analytics/instructor/quiz-performance
Analytics hiệu quả quiz của giảng viên

3/ Ghi chú:
Routers: định nghĩa các endpoint, nhận request, trả về response
Services: xử lý logic nghiệp vụ, tương tác với database, gọi các hàm khác nếu cần
Schemas: định nghĩa các kiểu dữ liệu, request body, response body, validation (tức là service trả ra cái gì thì schema sẽ định nghĩa kiểu dữ liệu đó trả về cho client)
Models: định nghĩa các đối tượng trong database, tương tác trực tiếp với database (ví dụ User, Course, Enrollment,...)
middlewares: xử lý các tác vụ chung như xác thực, logging, xử lý lỗi,... trước khi request đến routers hoặc sau khi response được tạo ra từ routers
controllers chỉ đơn giản là tách biệt logic ra khỏi routers
(Hiện đang viết cả logic vào trong này, hơi rắc rối, có thể tách ra thành service riêng nếu cần)

4/ Check point lại 4 api trong admin/v1/courses:
Hiện tại từ đầu tới cuối đang sai lệch logic, trường dữ liệu so với mô tả.
Schema file thiếu rất nhiều, khi so sánh với models ở database, thiếu rất nhiều trường dữ liệu, thiếu rất nhiều mô tả, thiếu rất nhiều validation..
