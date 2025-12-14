# Dockerfile triển khai FastAPI theo yêu cầu tài liệu HE_THONG.md
FROM python:3.11-slim AS base

# Thiết lập biến môi trường cơ bản
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app

WORKDIR ${APP_HOME}

# Cài đặt gói hệ thống cần thiết
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Sao chép file requirements và cài đặt dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Sao chép toàn bộ mã nguồn vào container
COPY . .

# Expose port và câu lệnh chạy uvicorn
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
