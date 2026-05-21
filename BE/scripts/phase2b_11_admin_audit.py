"""Phase 2b.11 — API audit for admin (17 ops per plan)."""
import asyncio
import json
import sys
import uuid

import httpx

sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:8000/api/v1"
ADMIN = ("admin1@ailearning.vn", "Admin@123456")


async def login(client: httpx.AsyncClient, creds):
    r = await client.post(f"{BASE}/auth/login", json={"email": creds[0], "password": creds[1]})
    r.raise_for_status()
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


async def main():
    results = []
    created_user_id = None
    created_course_id = None
    sample_user_id = None
    sample_course_id = None
    sample_class_id = None

    async with httpx.AsyncClient(timeout=120) as c:
        ah = await login(c, ADMIN)

        r = await c.get(f"{BASE}/admin/users", headers=ah, params={"limit": 5})
        users = r.json().get("data") or r.json().get("users") or [] if r.status_code == 200 else []
        if users:
            sample_user_id = users[0].get("user_id") or users[0].get("id")
        results.append(("GET /admin/users", r.status_code, f"count={len(users)}"))

        email = f"audit.{uuid.uuid4().hex[:8]}@gmail.com"
        r = await c.post(
            f"{BASE}/admin/users",
            headers=ah,
            json={
                "full_name": "Audit Test User",
                "email": email,
                "role": "student",
                "password": "AuditTest123",
            },
        )
        if r.status_code in (200, 201):
            created_user_id = r.json().get("id") or r.json().get("user_id")
        results.append(
            (
                "POST /admin/users",
                r.status_code,
                f"id={created_user_id}" if created_user_id else r.text[:80],
            )
        )

        target_user = created_user_id or sample_user_id
        if target_user:
            r = await c.get(f"{BASE}/admin/users/{target_user}", headers=ah)
            results.append(("GET /admin/users/{id}", r.status_code, "ok" if r.status_code == 200 else r.text[:60]))

            r = await c.put(
                f"{BASE}/admin/users/{target_user}",
                headers=ah,
                json={"full_name": "Audit Test User Updated"},
            )
            results.append(("PUT /admin/users/{id}", r.status_code, "ok" if r.status_code == 200 else r.text[:60]))

            r = await c.put(
                f"{BASE}/admin/users/{target_user}/role",
                headers=ah,
                json={"new_role": "student", "impact": "audit role check"},
            )
            results.append(("PUT /admin/users/{id}/role", r.status_code, "ok" if r.status_code == 200 else r.text[:60]))

            r = await c.post(
                f"{BASE}/admin/users/{target_user}/reset-password",
                headers=ah,
                json={"new_password": "AuditReset123"},
            )
            results.append(
                (
                    "POST /admin/users/{id}/reset-password",
                    r.status_code,
                    "ok" if r.status_code == 200 else r.text[:60],
                )
            )
        else:
            for op in [
                "GET /admin/users/{id}",
                "PUT /admin/users/{id}",
                "PUT /admin/users/{id}/role",
                "POST /admin/users/{id}/reset-password",
            ]:
                results.append((op, 0, "skipped-no-user"))

        r = await c.get(f"{BASE}/admin/courses", headers=ah, params={"limit": 5})
        courses = r.json().get("data") or r.json().get("courses") or [] if r.status_code == 200 else []
        if courses:
            sample_course_id = courses[0].get("course_id") or courses[0].get("id")
        results.append(("GET /admin/courses", r.status_code, f"count={len(courses)}"))

        r = await c.post(
            f"{BASE}/admin/courses",
            headers=ah,
            json={
                "title": f"Audit Course {uuid.uuid4().hex[:6]}",
                "description": "Course created by phase2b_11 audit script.",
                "category": "Programming",
                "level": "Beginner",
            },
        )
        if r.status_code in (200, 201):
            created_course_id = r.json().get("id") or r.json().get("course_id")
        results.append(
            (
                "POST /admin/courses",
                r.status_code,
                f"id={created_course_id}" if created_course_id else r.text[:80],
            )
        )

        target_course = created_course_id or sample_course_id
        if target_course:
            r = await c.get(f"{BASE}/admin/courses/{target_course}", headers=ah)
            results.append(("GET /admin/courses/{id}", r.status_code, "ok" if r.status_code == 200 else r.text[:60]))

            r = await c.put(
                f"{BASE}/admin/courses/{target_course}",
                headers=ah,
                json={"title": "Audit Course Updated"},
            )
            results.append(("PUT /admin/courses/{id}", r.status_code, "ok" if r.status_code == 200 else r.text[:60]))
        else:
            results.append(("GET /admin/courses/{id}", 0, "skipped-no-course"))
            results.append(("PUT /admin/courses/{id}", 0, "skipped-no-course"))

        r = await c.get(f"{BASE}/admin/classes", headers=ah, params={"limit": 5})
        classes = r.json().get("data") or r.json().get("classes") or [] if r.status_code == 200 else []
        if classes:
            sample_class_id = classes[0].get("class_id") or classes[0].get("id")
        results.append(("GET /admin/classes", r.status_code, f"count={len(classes)}"))

        if sample_class_id:
            r = await c.get(f"{BASE}/admin/classes/{sample_class_id}", headers=ah)
            results.append(("GET /admin/classes/{id}", r.status_code, "ok" if r.status_code == 200 else r.text[:60]))
        else:
            results.append(("GET /admin/classes/{id}", 0, "skipped-no-class"))

        r = await c.get(f"{BASE}/admin/analytics/users-growth", headers=ah, params={"time_range": "30d"})
        results.append(("GET /admin/analytics/users-growth", r.status_code, "ok" if r.status_code == 200 else r.text[:60]))

        r = await c.get(f"{BASE}/admin/analytics/courses", headers=ah)
        results.append(("GET /admin/analytics/courses", r.status_code, "ok" if r.status_code == 200 else r.text[:60]))

        r = await c.get(f"{BASE}/admin/analytics/system-health", headers=ah)
        results.append(("GET /admin/analytics/system-health", r.status_code, "ok" if r.status_code == 200 else r.text[:60]))

        if created_course_id:
            r = await c.delete(f"{BASE}/admin/courses/{created_course_id}", headers=ah)
            results.append(("DELETE /admin/courses/{id}", r.status_code, "ok" if r.status_code == 200 else r.text[:60]))
        elif sample_course_id:
            results.append(("DELETE /admin/courses/{id}", 0, "skipped-keep-sample"))
        else:
            results.append(("DELETE /admin/courses/{id}", 0, "skipped-no-course"))

        delete_user_id = created_user_id
        if delete_user_id:
            r = await c.delete(f"{BASE}/admin/users/{delete_user_id}", headers=ah)
            results.append(("DELETE /admin/users/{id}", r.status_code, "ok" if r.status_code == 200 else r.text[:60]))
        else:
            results.append(("DELETE /admin/users/{id}", 0, "skipped-no-user"))

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
