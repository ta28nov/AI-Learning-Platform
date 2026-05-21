"""Phase 2b.9 — API audit for chat (5 ops)."""
import asyncio
import json
import sys

import httpx

sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:8000/api/v1"
STUDENT = ("student1@gmail.com", "Student@123")
# Khóa HV đã enroll (Bootcamp Business 3)
COURSE_ID = "6cec7c81-6ff4-425e-84c8-de3238e0b5a2"


async def login(client: httpx.AsyncClient, creds):
    r = await client.post(f"{BASE}/auth/login", json={"email": creds[0], "password": creds[1]})
    r.raise_for_status()
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


async def resolve_course_id(client, headers):
    r = await client.get(f"{BASE}/enrollments/my-courses", headers=headers, params={"limit": 5})
    if r.status_code == 200:
        items = r.json().get("enrollments") or []
        for item in items:
            cid = item.get("course_id")
            if cid:
                return cid
    return COURSE_ID


async def main():
    results = []
    conversation_id = None

    async with httpx.AsyncClient(timeout=180) as c:
        sh = await login(c, STUDENT)
        course_id = await resolve_course_id(c, sh)

        r = await c.post(
            f"{BASE}/chat/course/{course_id}",
            headers=sh,
            json={"question": "Tóm tắt ngắn mục tiêu khóa học này?", "context_type": "general"},
        )
        body = r.json() if r.status_code in (200, 201) else {}
        conversation_id = body.get("conversation_id")
        answer_len = len(body.get("answer") or "")
        results.append(
            (
                "POST /chat/course/{id}",
                r.status_code,
                f"conv={conversation_id} answer_len={answer_len} err={r.text[:80] if r.status_code not in (200, 201) else ''}",
            )
        )

        r = await c.get(f"{BASE}/chat/history", headers=sh, params={"limit": 10})
        hist = r.json() if r.status_code == 200 else {}
        conv_count = len(hist.get("conversations") or [])
        results.append(("GET /chat/history", r.status_code, f"count={conv_count}"))

        if conversation_id:
            r = await c.get(f"{BASE}/chat/conversations/{conversation_id}", headers=sh)
            detail = r.json() if r.status_code == 200 else {}
            msg_count = len(detail.get("messages") or [])
            results.append(
                (
                    "GET /chat/conversations/{id}",
                    r.status_code,
                    f"messages={msg_count}",
                )
            )

            r = await c.delete(f"{BASE}/chat/history/{conversation_id}", headers=sh)
            results.append(
                (
                    "DELETE /chat/history/{id}",
                    r.status_code,
                    r.text[:60] if r.status_code not in (200, 204) else "ok",
                )
            )
            conversation_id = None
        else:
            results.append(("GET /chat/conversations/{id}", 0, "skipped-no-conv"))
            results.append(("DELETE /chat/history/{id}", 0, "skipped-no-conv"))

        # Tạo thêm 1 conv để test delete all
        r = await c.post(
            f"{BASE}/chat/course/{course_id}",
            headers=sh,
            json={"question": "Gợi ý thứ tự học module?", "context_type": "general"},
        )
        if r.status_code in (200, 201):
            conversation_id = r.json().get("conversation_id")

        r = await c.delete(f"{BASE}/chat/conversations", headers=sh)
        deleted = r.json().get("deleted_count") if r.status_code == 200 else None
        results.append(
            (
                "DELETE /chat/conversations",
                r.status_code,
                f"deleted={deleted}" if deleted is not None else r.text[:60],
            )
        )

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
