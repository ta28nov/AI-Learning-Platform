"""
Generate Postman collection from tests/fixtures/openapi.json.

Run from BE/:
  python scripts/export_openapi.py
  python scripts/generate_postman.py
"""

from __future__ import annotations

import json
from pathlib import Path

BE_ROOT = Path(__file__).resolve().parents[1]
OPENAPI_PATH = BE_ROOT / "tests" / "fixtures" / "openapi.json"
OUT_PATH = BE_ROOT.parent / "docs" / "postman" / "AI-Learning-Platform.postman_collection.json"

HTTP_METHODS = frozenset({"get", "post", "put", "patch", "delete", "head", "options"})
API_PREFIX = "/api/v1"


def _path_to_url(openapi_path: str) -> str:
    if openapi_path.startswith(API_PREFIX):
        suffix = openapi_path[len(API_PREFIX) :]
        return "{{base_url}}" + (suffix or "")
    return "{{base_url}}" + openapi_path


def _request_body(op: dict) -> dict | None:
    content = (op.get("requestBody") or {}).get("content") or {}
    if "application/json" not in content:
        return None
    return {
        "mode": "raw",
        "raw": "{}",
        "options": {"raw": {"language": "json"}},
    }


def _build_request(path: str, method: str, op: dict) -> dict:
    url_path = _path_to_url(path)
    return {
        "name": op.get("summary") or f"{method.upper()} {path}",
        "request": {
            "method": method.upper(),
            "header": [{"key": "Content-Type", "value": "application/json"}],
            "body": _request_body(op),
            "url": url_path,
            "description": op.get("description") or "",
        },
    }


def main() -> None:
    if not OPENAPI_PATH.is_file():
        raise SystemExit(f"Missing {OPENAPI_PATH}. Run: python scripts/export_openapi.py")

    schema = json.loads(OPENAPI_PATH.read_text(encoding="utf-8"))
    by_tag: dict[str, list] = {}

    for path, path_item in schema.get("paths", {}).items():
        for method, op in path_item.items():
            if method not in HTTP_METHODS:
                continue
            tag = (op.get("tags") or ["Other"])[0]
            by_tag.setdefault(tag, []).append(_build_request(path, method, op))

    collection = {
        "info": {
            "name": schema.get("info", {}).get("title", "AI Learning Platform API"),
            "description": "Auto-generated from OpenAPI. Regenerate with BE/scripts/generate_postman.py.",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "auth": {
            "type": "bearer",
            "bearer": [{"key": "token", "value": "{{access_token}}", "type": "string"}],
        },
        "item": [
            {"name": tag, "item": sorted(requests, key=lambda r: r["name"])}
            for tag, requests in sorted(by_tag.items(), key=lambda x: x[0].lower())
        ],
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(collection, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    req_count = sum(len(v) for v in by_tag.values())
    print(f"Wrote {OUT_PATH} ({req_count} requests in {len(by_tag)} folders)")


if __name__ == "__main__":
    main()
