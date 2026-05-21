"""Phase 2b.8 — API audit for personal courses (6 ops)."""
import asyncio
import json
import sys

import httpx

sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:8000/api/v1"
STUDENT = ("student1@gmail.com", "Student@123")


async def login(client: httpx.AsyncClient, creds):
    r = await client.post(f"{BASE}/auth/login", json={"email": creds[0], "password": creds[1]})
    r.raise_for_status()
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


async def main():
    results = []
    temp_id = None

    async with httpx.AsyncClient(timeout=180) as c:
        sh = await login(c, STUDENT)

        r = await c.get(f"{BASE}/courses/my-personal", headers=sh)
        existing = r.json() if r.status_code == 200 else {}
        items = existing.get("courses") or existing.get("data") or []
        results.append(("GET /courses/my-personal", r.status_code, f"count={len(items)}"))

        manual_payload = {
            "title": "2b8 Audit Personal Course",
            "description": "Temporary course for phase 2b.8 audit",
            "category": "Programming",
            "level": "Beginner",
            "language": "vi",
        }
        r = await c.post(f"{BASE}/courses/personal", headers=sh, json=manual_payload)
        created = r.json() if r.status_code in (200, 201) else {}
        temp_id = created.get("course_id") or created.get("id")
        results.append(("POST /courses/personal", r.status_code, f"course_id={temp_id}"))

        if temp_id:
            r = await c.get(f"{BASE}/courses/personal/{temp_id}", headers=sh)
            detail = r.json() if r.status_code == 200 else {}
            results.append(
                (
                    "GET /courses/personal/{id}",
                    r.status_code,
                    f"title={str(detail.get('title', ''))[:30]} modules={len(detail.get('modules', []))}",
                )
            )

            r = await c.put(
                f"{BASE}/courses/personal/{temp_id}",
                headers=sh,
                json={"title": manual_payload["title"] + " (updated)"},
            )
            results.append(("PUT /courses/personal/{id}", r.status_code, r.text[:60] if r.status_code != 200 else "ok"))

        r = await c.post(
            f"{BASE}/courses/from-prompt",
            headers=sh,
            json={
                "prompt": "Khóa học Python cơ bản cho người mới, 4 tuần, tập trung biến và vòng lặp.",
                "level": "Beginner",
                "estimated_duration_weeks": 4,
                "language": "vi",
            },
        )
        ai_body = r.json() if r.status_code in (200, 201) else {}
        ai_id = ai_body.get("course_id") or ai_body.get("id")
        results.append(
            (
                "POST /courses/from-prompt",
                r.status_code,
                f"course_id={ai_id} err={r.text[:80] if r.status_code not in (200, 201) else ''}",
            )
        )

        if temp_id:
            r = await c.delete(f"{BASE}/courses/personal/{temp_id}", headers=sh)
            results.append(("DELETE /courses/personal/{id}", r.status_code, r.text[:60] if r.status_code not in (200, 204) else "ok"))

        if ai_id and ai_id != temp_id:
            await c.delete(f"{BASE}/courses/personal/{ai_id}", headers=sh)

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
