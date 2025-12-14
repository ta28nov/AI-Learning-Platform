# AI Learning Platform - Backend API

> Hệ thống học tập thông minh sử dụng AI để cá nhân hóa trải nghiệm học tập

**Phiên bản**: 1.0.0  
**Ngày cập nhật**: 14/12/2025  
**Tác giả**: Nguyễn Ngọc Tuấn Anh

---

## Mục lục

1. [Tổng quan](#tổng-quan)
2. [Tính năng chính](#tính-năng-chính)
3. [Công nghệ sử dụng](#công-nghệ-sử-dụng)
4. [Kiến trúc hệ thống](#kiến-trúc-hệ-thống)
5. [Cài đặt](#cài-đặt)
6. [Cấu hình](#cấu-hình)
7. [Chạy ứng dụng](#chạy-ứng-dụng)
8. [API Documentation](#api-documentation)
9. [Cấu trúc dự án](#cấu-trúc-dự-án)
10. [Testing](#testing)
11. [Deployment](#deployment)

---

## Tổng quan

**AI Learning Platform** là một hệ thống quản lý học tập (LMS) thông minh, sử dụng Google Gemini AI để:

- **Đánh giá năng lực tự động**: Sinh câu hỏi đánh giá động dựa trên AI, phân tích điểm mạnh/yếu của học viên
- **Cá nhân hóa lộ trình học tập**: Đề xuất khóa học và bài tập phù hợp với từng cá nhân
- **Tạo khóa học từ AI**: Học viên chỉ cần mô tả mục tiêu, AI tự động tạo khóa học hoàn chỉnh
- **Chatbot hỗ trợ học tập**: Trợ lý AI trả lời câu hỏi theo ngữ cảnh khóa học
- **Quản lý lớp học**: Giảng viên tạo lớp, quản lý học viên và theo dõi tiến độ

Hệ thống hỗ trợ 3 vai trò chính:
- **Student (Học viên)**: Học tập, làm quiz, chat với AI
- **Instructor (Giảng viên)**: Tạo lớp học, quản lý học viên, tạo quiz
- **Admin (Quản trị viên)**: Quản lý toàn bộ hệ thống

---

## Tính năng chính

### 1. Xác thực và Quản lý Tài khoản
- Đăng ký/Đăng nhập với JWT Authentication
- Quản lý hồ sơ cá nhân
- Phân quyền theo vai trò (Role-Based Access Control)

### 2. Đánh giá Năng lực AI (AI Dynamic Assessment)
- AI tự động sinh câu hỏi đánh giá theo chủ đề và cấp độ
- Phân bổ câu hỏi thông minh: 20% dễ, 50% trung bình, 30% khó
- Chấm điểm tự động với thuật toán có trọng số
- Phân tích chi tiết: điểm mạnh, điểm yếu, lỗ hổng kiến thức
- Đề xuất lộ trình học tập cá nhân hóa

### 3. Khám phá và Đăng ký Khóa học
- Tìm kiếm khóa học nâng cao với filter đa dạng
- Xem chi tiết khóa học: modules, lessons, learning outcomes
- Đăng ký/Hủy đăng ký khóa học
- Theo dõi tiến độ học tập

### 4. Học tập và Theo dõi Tiến độ
- Xem nội dung bài học: text, video, tài liệu
- Làm quiz với nhiều dạng câu hỏi: trắc nghiệm, điền khuyết, kéo thả
- Câu hỏi "điểm liệt": bắt buộc trả lời đúng mới pass
- Làm lại quiz không giới hạn với câu hỏi mới do AI sinh
- Tracking thời gian học và tiến độ chi tiết

### 5. Khóa học Cá nhân (Personal Course)
- **Tạo từ AI Prompt**: Mô tả mục tiêu học tập, AI tạo khóa học hoàn chỉnh
- **Tạo thủ công**: Tự thiết kế modules và lessons
- Chỉnh sửa và quản lý khóa học cá nhân
- Chỉ người tạo và Admin có quyền truy cập

### 6. Chatbot Hỗ trợ AI
- Chat với AI về nội dung khóa học
- AI hiểu ngữ cảnh: modules, lessons, learning outcomes
- Lưu lịch sử hội thoại
- Tiếp tục chat từ conversation cũ

### 7. Dashboard và Phân tích
- **Student Dashboard**: Khóa học đang học, quiz cần làm, thống kê tiến độ
- **Instructor Dashboard**: Quản lý lớp học, học viên, phân tích quiz
- **Admin Dashboard**: Tổng quan hệ thống, analytics toàn diện

### 8. Quản lý Lớp học (Instructor)
- Tạo lớp học từ khóa học có sẵn
- Mã mời tự động để học viên tham gia
- Quản lý danh sách học viên
- Theo dõi tiến độ từng học viên
- Tạo và quản lý quiz tùy chỉnh

### 9. Quản trị Hệ thống (Admin)
- Quản lý người dùng: tạo, sửa, xóa, đổi role
- Quản lý khóa học: duyệt, chỉnh sửa, xóa
- Giám sát lớp học
- Analytics và báo cáo chi tiết

---

## Công nghệ sử dụng

### Core Framework
- **Python 3.11+**: Ngôn ngữ lập trình chính
- **FastAPI 0.116.2**: Web framework hiện đại, async, hiệu suất cao
- **Uvicorn 0.35.0**: ASGI server với WebSocket support

### Database
- **MongoDB**: NoSQL database linh hoạt
- **Motor 3.6.0**: Async MongoDB driver
- **Beanie 1.27.0**: Async ODM (Object Document Mapper)

### AI Integration
- **Google Gemini API**: Sinh câu hỏi, phân tích, chatbot
- **google-generativeai 0.8.3**: SDK chính thức

### Authentication & Security
- **JWT (JSON Web Tokens)**: Xác thực stateless
- **python-jose 3.3.0**: JWT handling
- **passlib + bcrypt**: Mã hóa mật khẩu

### Data Validation
- **Pydantic 2.11.1**: Validation và serialization
- **email-validator 2.0.0**: Kiểm tra email hợp lệ

### Development Tools
- **pytest 8.4.2**: Testing framework
- **pytest-asyncio 0.24.0**: Async test support
- **Faker 25.9.1**: Tạo dữ liệu mẫu

---

## Kiến trúc hệ thống

### Kiến trúc tổng quan

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                          │
│  (Frontend - React/Vue/Mobile App)                          │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/HTTPS (REST API)
                         │ WebSocket (Real-time)
┌────────────────────────▼────────────────────────────────────┐
│                     API GATEWAY LAYER                        │
│  FastAPI Application (app/main.py)                          │
│  - CORS Middleware                                          │
│  - Authentication Middleware                                │
│  - Rate Limiting                                            │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐  ┌──────▼──────┐  ┌─────▼──────┐
│   ROUTERS    │  │ MIDDLEWARE  │  │  SCHEMAS   │
│ (16 routers) │  │ - Auth      │  │ (Pydantic) │
│ - auth       │  │ - CORS      │  │ - Request  │
│ - courses    │  │ - Logging   │  │ - Response │
│ - quiz       │  └─────────────┘  └────────────┘
│ - chat       │
│ - admin      │
│ ...          │
└───────┬──────┘
        │
┌───────▼──────────────────────────────────────────────────┐
│                   CONTROLLER LAYER                        │
│  Business Logic (controllers/)                           │
│  - handle_register, handle_login                         │
│  - handle_create_course, handle_enroll                   │
│  - handle_generate_assessment                            │
└───────┬──────────────────────────────────────────────────┘
        │
        ├─────────────────┬─────────────────┬──────────────┐
        │                 │                 │              │
┌───────▼──────┐  ┌───────▼──────┐  ┌──────▼──────┐  ┌────▼────┐
│   SERVICES   │  │    MODELS    │  │   MODULES   │  │  UTILS  │
│ (services/)  │  │  (models/)   │  │ (modules/)  │  │ (utils/)│
│ - auth_svc   │  │ - User       │  │ - ai_svc    │  │ - jwt   │
│ - course_svc │  │ - Course     │  │ - gemini    │  │ - hash  │
│ - quiz_svc   │  │ - Quiz       │  │             │  │         │
│ - ai_svc     │  │ - Progress   │  │             │  │         │
└───────┬──────┘  └───────┬──────┘  └──────┬──────┘  └─────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
┌─────────────────────────▼─────────────────────────────────┐
│                   DATABASE LAYER                          │
│  MongoDB (via Motor + Beanie)                            │
│  Collections:                                            │
│  - users, courses, modules, lessons                      │
│  - quizzes, assessments, enrollments                     │
│  - classes, chat_conversations, progress                 │
└───────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────┐
│                  EXTERNAL SERVICES                        │
│  - Google Gemini AI API (AI generation)                  │
│  - Email Service (optional - notifications)              │
└───────────────────────────────────────────────────────────┘
```

### Luồng xử lý Request

```
1. Client gửi HTTP Request
   ↓
2. API Gateway (FastAPI) nhận request
   ↓
3. Middleware xử lý (Auth, CORS, Logging)
   ↓
4. Router phân tích endpoint và method
   ↓
5. Schema validation (Pydantic)
   ↓
6. Controller xử lý business logic
   ↓
7. Service layer tương tác với Database/AI
   ↓
8. Model (Beanie ODM) query MongoDB
   ↓
9. Response trả về qua các layer ngược lại
   ↓
10. Client nhận JSON response
```

---

## Cài đặt

### Yêu cầu hệ thống

- **Python**: 3.11 trở lên
- **MongoDB**: 4.4 trở lên (local hoặc MongoDB Atlas)
- **RAM**: Tối thiểu 2GB
- **Disk**: 500MB trống

### Bước 1: Clone repository

```bash
git clone 
cd 
```

### Bước 2: Tạo môi trường ảo

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Bước 3: Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Bước 4: Cài đặt MongoDB

**Option 1: MongoDB Local**
- Tải và cài đặt MongoDB Community Server từ [mongodb.com](https://www.mongodb.com/try/download/community)
- Khởi động MongoDB service

**Option 2: MongoDB Atlas (Cloud)**
- Tạo tài khoản miễn phí tại [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
- Tạo cluster và lấy connection string

---

## Cấu hình

### Tạo file .env

Copy file `.env.example` thành `.env`:

```bash
cp .env.example .env
```

### Cấu hình các biến môi trường

Mở file `.env` và cập nhật các giá trị:

```env
# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
MONGODB_URL=mongodb://localhost:27017
# Hoặc dùng MongoDB Atlas:
# MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority

MONGODB_DATABASE=belearning_db

# ============================================================================
# SECURITY & AUTHENTICATION
# ============================================================================
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# ============================================================================
# GOOGLE AI (GEMINI) CONFIGURATION
# ============================================================================
GOOGLE_API_KEY=your-google-gemini-api-key-here
# Lấy API key tại: https://aistudio.google.com/app/apikey

# ============================================================================
# APPLICATION SETTINGS
# ============================================================================
APP_NAME=AI Learning Platform
APP_VERSION=1.0.0
DEBUG=True
ENVIRONMENT=development

# ============================================================================
# CORS SETTINGS
# ============================================================================
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
# Thêm domain frontend của bạn vào đây

# ============================================================================
# FILE UPLOAD (Optional)
# ============================================================================
MAX_UPLOAD_SIZE_MB=10
ALLOWED_FILE_TYPES=pdf,docx,pptx,jpg,png,mp4

# ============================================================================
# LOGGING
# ============================================================================
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### Lấy Google Gemini API Key

1. Truy cập: https://aistudio.google.com/app/apikey
2. Đăng nhập bằng Google Account
3. Click **"Create API Key"**
4. Copy API key và paste vào file `.env`

---

## Chạy ứng dụng

### Khởi tạo dữ liệu mẫu

Chạy script để tạo dữ liệu mẫu (users, courses, quizzes):

```bash
python -m scripts.init_data
```

Script sẽ tạo:
- 1 Admin account
- 3 Instructor accounts
- 10 Student accounts
- 5 Courses với modules và lessons
- Quiz cho mỗi lesson

### Khởi động server

**Development mode (với auto-reload):**

```bash
uvicorn app.main:app --reload
```

**Production mode:**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Kiểm tra server

Mở trình duyệt và truy cập:

- **Health Check**: http://localhost:8000/health
- **API Documentation (Swagger UI)**: http://localhost:8000/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc

Nếu thấy trang Swagger UI, server đã chạy thành công!

---

## API Documentation

### Tổng quan API

Hệ thống có **84 API endpoints** được tổ chức thành **16 routers**:

| Router | Endpoints | Mô tả |
|--------|-----------|-------|
| `auth_router` | 3 | Đăng ký, đăng nhập, đăng xuất |
| `users_router` | 2 | Quản lý hồ sơ cá nhân |
| `courses_router` | 4 | Tìm kiếm, xem khóa học |
| `enrollments_router` | 4 | Đăng ký, quản lý enrollment |
| `learning_router` | 6 | Xem modules, lessons |
| `quiz_router` | 10 | Làm quiz, xem kết quả |
| `assessments_router` | 3 | Đánh giá năng lực AI |
| `personal_courses_router` | 5 | Tạo khóa học cá nhân |
| `chat_router` | 5 | Chatbot AI |
| `classes_router` | 10 | Quản lý lớp học (Instructor) |
| `progress_router` | 1 | Theo dõi tiến độ |
| `recommendation_router` | 2 | Đề xuất khóa học |
| `analytics_router` | 5 | Thống kê, phân tích |
| `dashboard_router` | 3 | Dashboard theo role |
| `admin_router` | 17 | Quản trị hệ thống |
| `search_router` | 1 | Tìm kiếm toàn hệ thống |

### Sử dụng Swagger UI

1. Truy cập: http://localhost:8000/docs
2. Đăng nhập để lấy token:
   - Click **POST /api/v1/auth/login**
   - Click **Try it out**
   - Nhập:
     ```json
     {
       "email": "admin.super@ailab.com.vn",
       "password": "Admin@12345",
       "remember_me": true
     }
     ```
   - Click **Execute**
   - Copy `access_token` từ response

3. Authorize:
   - Click nút **Authorize** (ở đầu trang)
   - Nhập: `Bearer <your_access_token>`
   - Click **Authorize**

4. Bây giờ có thể test các API protected!

### Tài khoản test có sẵn

**Admin:**
```
Email: admin.super@ailab.com.vn
Password: Admin@12345
```

**Instructor:**
```
Email: tuananh.nguyen@ailab.edu.vn
Password: Giangvien@123
```

**Student:**
```
Email: student1@example.com
Password: Hocvien@123
```

### Ví dụ API Calls

**1. Đăng ký tài khoản mới:**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Nguyen Van Test",
    "email": "test@example.com",
    "password": "Test@12345"
  }'
```

**2. Tìm kiếm khóa học:**

```bash
curl -X GET "http://localhost:8000/api/v1/courses/search?keyword=Python&level=Beginner"
```

**3. Tạo khóa học từ AI (cần token):**

```bash
curl -X POST "http://localhost:8000/api/v1/courses/from-prompt" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Tôi muốn học Python từ cơ bản đến nâng cao",
    "category": "Programming",
    "level": "Beginner"
  }'
```

**4. Chat với AI về khóa học:**

```bash
curl -X POST "http://localhost:8000/api/v1/chat/course/{course_id}" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Exception trong Python là gì?"
  }'
```

---

## Cấu trúc dự án

```
BELEARNINGAI/
│
├── app/                          # Application core
│   ├── __init__.py
│   ├── main.py                   # FastAPI app entry point
│   └── database.py               # MongoDB connection setup
│
├── routers/                      # API Routes (16 routers)
│   ├── auth_router.py            # Authentication endpoints
│   ├── users_router.py           # User management
│   ├── courses_router.py         # Course discovery
│   ├── enrollments_router.py     # Course enrollment
│   ├── learning_router.py        # Learning content
│   ├── quiz_router.py            # Quiz system
│   ├── assessments_router.py     # AI assessment
│   ├── personal_courses_router.py # Personal courses
│   ├── chat_router.py            # AI chatbot
│   ├── classes_router.py         # Class management
│   ├── progress_router.py        # Progress tracking
│   ├── recommendation_router.py  # Recommendations
│   ├── analytics_router.py       # Analytics
│   ├── dashboard_router.py       # Dashboards
│   ├── admin_router.py           # Admin features
│   └── search_router.py          # Global search
│
├── controllers/                  # Business logic handlers
│   ├── auth_controller.py
│   ├── course_controller.py
│   ├── quiz_controller.py
│   └── ...
│
├── services/                     # Service layer
│   ├── auth_service.py           # Authentication logic
│   ├── course_service.py         # Course operations
│   ├── quiz_service.py           # Quiz logic
│   ├── ai_service.py             # AI integration
│   └── ...
│
├── models/                       # Database models (Beanie ODM)
│   ├── user.py                   # User model
│   ├── course.py                 # Course, Module, Lesson
│   ├── quiz.py                   # Quiz, Question
│   ├── assessment.py             # Assessment session
│   ├── enrollment.py             # Enrollment
│   ├── class_model.py            # Class
│   ├── chat.py                   # Chat conversation
│   └── progress.py               # Progress tracking
│
├── schemas/                      # Pydantic schemas
│   ├── auth_schema.py            # Auth request/response
│   ├── course_schema.py          # Course schemas
│   ├── quiz_schema.py            # Quiz schemas
│   └── ...
│
├── modules/                      # AI modules
│   ├── ai_service.py             # Google Gemini integration
│   ├── assessment_generator.py  # Generate assessment questions
│   ├── course_generator.py      # Generate courses from prompt
│   └── chatbot.py                # AI chatbot logic
│
├── middleware/                   # Custom middleware
│   ├── auth_middleware.py        # JWT verification
│   ├── cors_middleware.py        # CORS handling
│   └── logging_middleware.py     # Request logging
│
├── utils/                        # Utility functions
│   ├── jwt_utils.py              # JWT encode/decode
│   ├── password_utils.py         # Password hashing
│   ├── validators.py             # Custom validators
│   └── helpers.py                # Helper functions
│
├── config/                       # Configuration
│   ├── settings.py               # App settings (from .env)
│   └── constants.py              # Constants
│
├── scripts/                      # Utility scripts
│   └── init_data.py              # Initialize sample data
│
├── tests/                        # Test suite
│   ├── test_auth.py
│   ├── test_courses.py
│   ├── test_quiz.py
│   └── ...
│
├── logs/                         # Application logs
│   └── app.log
│
├── .env                          # Environment variables (create from .env.example)
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── setup.py                      # Package setup
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Docker Compose
├── QUICKSTART.md                 # Quick start guide
└── README.md                     # This file
```

---

## Testing

### Chạy tất cả tests

```bash
pytest
```

### Chạy tests với coverage

```bash
pytest --cov=app --cov-report=html
```

Xem báo cáo coverage tại `htmlcov/index.html`

### Chạy tests cho module cụ thể

```bash
# Test authentication
pytest tests/test_auth.py -v

# Test courses
pytest tests/test_courses.py -v

# Test quiz
pytest tests/test_quiz.py -v
```

### Test API bằng Swagger UI

1. Truy cập http://localhost:8000/docs
2. Đăng nhập và authorize
3. Test từng endpoint bằng giao diện trực quan

### Test API bằng Postman

Import collection từ file `postman_collection.json` (nếu có)

---

## Deployment

### Sử dụng Docker

**Build image:**

```bash
docker build -t ai-learning-backend .
```

**Run container:**

```bash
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name ai-learning-api \
  ai-learning-backend
```

### Sử dụng Docker Compose

```bash
# Start all services (API + MongoDB)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Deploy lên Cloud

**Heroku:**

```bash
# Login
heroku login

# Create app
heroku create ai-learning-platform

# Set environment variables
heroku config:set MONGODB_URL=your_mongodb_atlas_url
heroku config:set GOOGLE_API_KEY=your_google_api_key
heroku config:set JWT_SECRET_KEY=your_secret_key

# Deploy
git push heroku main
```

**Railway / Render:**

1. Connect GitHub repository
2. Set environment variables trong dashboard
3. Deploy tự động khi push code

**AWS / GCP / Azure:**

Sử dụng Docker image và deploy lên:
- AWS ECS / Fargate
- Google Cloud Run
- Azure Container Instances

---

## Tài liệu tham khảo

### Tài liệu dự án

- **CHUCNANG.md**: Mô tả chi tiết tất cả chức năng theo vai trò
- **API_SCHEMA.md**: Định nghĩa đầy đủ API schemas
- **ENDPOINTS.md**: Mapping endpoints với routers
- **API_TEST_GUIDE.md**: Hướng dẫn test API chi tiết
- **QUICKSTART.md**: Hướng dẫn khởi động nhanh

### Tài liệu công nghệ

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MongoDB Manual](https://www.mongodb.com/docs/manual/)
- [Beanie ODM](https://beanie-odm.dev/)
- [Google Gemini API](https://ai.google.dev/docs)
- [Pydantic](https://docs.pydantic.dev/)

---

## Troubleshooting

### Lỗi kết nối MongoDB

**Lỗi**: `ServerSelectionTimeoutError`

**Giải pháp**:
- Kiểm tra MongoDB đã chạy: `mongod --version`
- Kiểm tra connection string trong `.env`
- Nếu dùng Atlas, kiểm tra IP whitelist

### Lỗi Google API Key

**Lỗi**: `Invalid API key`

**Giải pháp**:
- Kiểm tra API key trong `.env`
- Tạo key mới tại https://aistudio.google.com/app/apikey
- Đảm bảo không có khoảng trắng thừa

### Lỗi Import Module

**Lỗi**: `ModuleNotFoundError`

**Giải pháp**:
```bash
# Cài lại dependencies
pip install -r requirements.txt

# Hoặc cài package cụ thể
pip install beanie motor fastapi
```

### Lỗi Port đã được sử dụng

**Lỗi**: `Address already in use`

**Giải pháp**:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

---


## Liên hệ

**Tác giả**: Nguyễn Ngọc Tuấn Anh

**Email**: tiphong05@gmail.com

**GitHub**: https://github.com/ta28nov

---

**Cảm ơn bạn đã sử dụng AI Learning Platform!**
