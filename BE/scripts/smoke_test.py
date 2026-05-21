#!/usr/bin/env python3
"""Smoke HTTP checks — BE đang chạy tại http://127.0.0.1:8000 (không thay pytest)."""

import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8000"
TIMEOUT = 15


def _get(path: str) -> tuple[int, dict]:
    req = urllib.request.Request(f"{BASE}{path}", method="GET")
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.status, json.loads(resp.read().decode())


def _post(path: str, body: dict) -> tuple[int, dict]:
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.status, json.loads(resp.read().decode())


def main() -> int:
    errors = []
    try:
        code, _ = _get("/health")
        if code != 200:
            errors.append(f"health -> {code}")
    except urllib.error.URLError as e:
        print(f"FAIL: không kết nối {BASE} — {e}")
        print("Chạy: cd BE && python -m uvicorn app.main:app --reload")
        return 1

    try:
        code, body = _post(
            "/api/v1/auth/login",
            {"email": "student1@gmail.com", "password": "Student@123"},
        )
        if code != 200:
            errors.append(f"login -> {code}")
        else:
            token = body.get("access_token")
            if not token:
                errors.append("login thiếu access_token")
            else:
                req = urllib.request.Request(
                    f"{BASE}/api/v1/users/me",
                    headers={"Authorization": f"Bearer {token}"},
                )
                with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                    if resp.status != 200:
                        errors.append(f"users/me -> {resp.status}")
    except urllib.error.HTTPError as e:
        errors.append(f"auth chain -> HTTP {e.code}")
    except Exception as e:
        errors.append(str(e))

    if errors:
        print("SMOKE FAIL:", "; ".join(errors))
        return 1
    print("SMOKE OK: health + login + /users/me")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
