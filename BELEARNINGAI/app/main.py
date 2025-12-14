"""Điểm khởi động FastAPI, đăng ký router và cấu hình chung."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import close_database, init_database
from config.config import get_settings
from config.logging_config import setup_logging
from routers.routers import api_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Quản lý vòng đời ứng dụng: logging, database."""

    setup_logging()
    await init_database()
    yield
    await close_database()


app = FastAPI(
    title=settings.app_name,
    description="API nền tảng học tập AI",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["system"], summary="Kiểm tra sức khỏe hệ thống")
async def health_check() -> dict[str, str]:
    """Endpoint kiểm tra tình trạng API cho công cụ giám sát."""

    return {"status": "ok"}
