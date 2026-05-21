"""
Export OpenAPI schema to tests/fixtures/openapi.json (INFRA-002).

Does not require MongoDB — builds the same in-process app as pytest.
Run from BE/:  python scripts/export_openapi.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

BE_ROOT = Path(__file__).resolve().parents[1]
if str(BE_ROOT) not in sys.path:
    sys.path.insert(0, str(BE_ROOT))

os.environ.setdefault("TESTING", "true")
os.environ.setdefault("MONGODB_DATABASE", "ai_learning_test")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-ci-only-min-32-chars")
os.environ.setdefault("GOOGLE_API_KEY", "fake-key-not-used-in-export")
os.environ.setdefault("ENVIRONMENT", "test")

from config.config import get_settings  # noqa: E402

get_settings.cache_clear()

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from routers.routers import api_router  # noqa: E402


def build_app() -> FastAPI:
    settings = get_settings()
    export_app = FastAPI(
        title=settings.app_name,
        description="API nền tảng học tập AI",
        version="0.1.0",
    )
    export_app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    export_app.include_router(api_router, prefix="/api/v1")

    @export_app.get("/health", tags=["system"], summary="Kiểm tra sức khỏe hệ thống")
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return export_app


def main() -> None:
    schema = build_app().openapi()
    out = BE_ROOT / "tests" / "fixtures" / "openapi.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(schema, ensure_ascii=False, indent=2) + "\n"
    out.write_text(text, encoding="utf-8")
    path_count = len(schema.get("paths", {}))
    print(f"Wrote {out.relative_to(BE_ROOT)} ({path_count} paths)")


if __name__ == "__main__":
    main()
