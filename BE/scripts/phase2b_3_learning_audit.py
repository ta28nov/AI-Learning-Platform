"""Phase 2b.3 — API audit for learning (modules, lessons, complete)."""
import asyncio
import json
import sys

import httpx

sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:8000/api/v1"
COURSE_ID = "6cec7c81-6ff4-425e-84c8-de3238e0b5a2"
STUDENT = ("student1@gmail.com", "Student@123")


async def login(client: httpx.AsyncClient, creds):
    r = await client.post(f"{BASE}/auth/login", json={"email": creds[0], "password": creds[1]})
    r.raise_for_status()
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


async def main():
    results = []
    async with httpx.AsyncClient(timeout=45) as c:
        sh = await login(c, STUDENT)
        cid = COURSE_ID

        r = await c.get(f"{BASE}/courses/{cid}/modules", headers=sh)
        modules = r.json().get("modules", r.json() if isinstance(r.json(), list) else [])
        if isinstance(r.json(), dict) and "modules" not in r.json():
            modules = r.json().get("data", []) or []
        results.append(("GET /courses/{id}/modules", r.status_code, len(modules) if isinstance(modules, list) else "?"))

        mid = None
        if modules:
            mid = modules[0].get("id") or modules[0].get("module_id")
            if len(modules) > 3:
                mid4 = modules[3].get("id") or modules[3].get("module_id")
            else:
                mid4 = mid
        else:
            mid4 = None

        if mid:
            r = await c.get(f"{BASE}/courses/{cid}/modules/{mid}", headers=sh)
            body = r.json()
            lo = body.get("learning_outcomes", [])
            res = body.get("resources", [])
            pre = body.get("prerequisites", [])
            results.append(
                (
                    "GET /courses/{id}/modules/{mid}",
                    r.status_code,
                    f"outcomes={len(lo)} resources={len(res)} prereq_sample={pre[:1]}",
                )
            )

            r = await c.get(f"{BASE}/courses/{cid}/modules/{mid}/outcomes", headers=sh)
            results.append(("GET .../outcomes", r.status_code, len(r.json().get("learning_outcomes", []))))

            r = await c.get(f"{BASE}/courses/{cid}/modules/{mid}/resources", headers=sh)
            results.append(("GET .../resources", r.status_code, len(r.json().get("resources", []))))

        if mid4 and mid4 != mid:
            r = await c.get(f"{BASE}/courses/{cid}/modules/{mid4}", headers=sh)
            results.append(("GET module[4]", r.status_code, r.json().get("title", "")[:50]))

        # lesson from module detail
        lid = None
        if mid:
            det = await c.get(f"{BASE}/courses/{cid}/modules/{mid4 or mid}", headers=sh)
            lessons = det.json().get("lessons", [])
            for les in lessons:
                if not les.get("is_completed"):
                    lid = les.get("id") or les.get("lesson_id")
                    break
            if not lid and lessons:
                lid = lessons[0].get("id") or lessons[0].get("lesson_id")

        if lid:
            r = await c.get(f"{BASE}/courses/{cid}/lessons/{lid}", headers=sh)
            results.append(("GET /courses/{id}/lessons/{lid}", r.status_code, r.json().get("title", "")[:40]))

            r = await c.post(f"{BASE}/courses/{cid}/lessons/{lid}/complete", headers=sh, json={})
            results.append(("POST .../complete", r.status_code, r.text[:80]))

        if mid4 or mid:
            m = mid4 or mid
            for qc in (3, 5, 10):
                r = await c.post(
                    f"{BASE}/courses/{cid}/modules/{m}/assessments/generate",
                    headers=sh,
                    json={"question_count": qc},
                )
                if r.status_code == 200:
                    results.append(("POST .../assessments/generate", r.status_code, f"question_count={qc}"))
                    break
                if qc == 10:
                    results.append(("POST .../assessments/generate", r.status_code, r.text[:120]))

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
