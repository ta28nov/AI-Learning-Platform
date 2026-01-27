# BELEARNINGAI Quickstart Guide
 **Updated: 2025-10-16**

## Prerequisites

- Python 3.11+
- MongoDB running (local hoặc Atlas)
- Google AI API key

---

## Step 1: Clone & Setup 
```powershell
# Clone repo
cd BELEARNINGAI

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

---

## Step 2: Configuration

```powershell
# Copy environment file
copy .env.example .env

# Edit .env với text editor
notepad .env  # Windows
# nano .env   # Linux
```

**Minimum required:**
```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=belearning_db
GOOGLE_API_KEY=your-google-ai-api-key-here
JWT_SECRET_KEY=any-random-string-for-development
```

**Get Google AI API Key:**
1. Visit: https://aistudio.google.com/app/apikey
2. Create new key
3. Copy vào `.env`

---

## Step 4: Initialize Database (1 phút)

```powershell
# Create initial data
python scripts/init_data.py  -- python -m scripts.init_data


```

---

## Step 5: Start Server (30 giây)

```powershell
uvicorn app.main:app --reload
```
python -m uvicorn app.main:app --reload

**Server running at:**
- **API**: http://localhost:8000       //đường dẫn cho API chính, nơi FE gọi 

- **Swagger UI**: http://localhost:8000/docs ⭐   //đường dẫn cho tài liệu API tương tác ,Mô tả rõ từng endpoint: method (GET, POST, PUT…), params, response schema, status code. Nơi FE đọc để biết endpoint nào cần gọi, input/output ra sao.

- **ReDoc**: http://localhost:8000/redoc       //Giao diện documentation chỉ đọc

- **Health**: http://localhost:8000/health     //Kiểm tra nhanh trạng thái server.

---

---

### Using Swagger UI

1. Open http://localhost:8000/docs
2. Click "Authorize" button
3. Register user via `/auth/register`
4. Login via `/auth/login` → copy token
5. Paste token in "Authorize" dialog
6. Now can test protected endpoints!


---

