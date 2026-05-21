"""Phase 2b.6 — API audit for progress, dashboard, analytics."""
import asyncio
import json
import sys

import httpx

sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:8000/api/v1"
COURSE_ID = "6cec7c81-6ff4-425e-84c8-de3238e0b5a2"
STUDENT = ("student1@gmail.com", "Student@123")
INSTRUCTOR = ("instructor1@ailearning.vn", "Instructor@123")
ADMIN = ("admin1@ailearning.vn", "Admin@123456")


async def login(client: httpx.AsyncClient, creds):
    r = await client.post(f"{BASE}/auth/login", json={"email": creds[0], "password": creds[1]})
    r.raise_for_status()
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


async def main():
    results = []
    async with httpx.AsyncClient(timeout=60) as c:
        sh = await login(c, STUDENT)
        ih = await login(c, INSTRUCTOR)
        ah = await login(c, ADMIN)

        r = await c.get(f"{BASE}/progress/course/{COURSE_ID}", headers=sh)
        body = r.json() if r.status_code == 200 else {}
        results.append(("GET /progress/course/{id}", r.status_code, f"progress={body.get('progress_percent', body.get('overall_progress', 'n/a'))}"))

        r = await c.get(f"{BASE}/dashboard/student", headers=sh)
        sd = r.json() if r.status_code == 200 else {}
        results.append(("GET /dashboard/student", r.status_code, f"courses={len(sd.get('recent_courses', []))} recs={len(sd.get('recommendations', []))}"))

        r = await c.get(f"{BASE}/dashboard/instructor", headers=ih)
        idb = r.json() if r.status_code == 200 else {}
        active = idb.get("active_classes_count", len(idb.get("recent_classes", [])))
        students = idb.get("total_students", "n/a")
        results.append(("GET /dashboard/instructor", r.status_code, f"active_classes={active} students={students}"))

        r = await c.get(f"{BASE}/dashboard/admin", headers=ah)
        adb = r.json() if r.status_code == 200 else {}
        results.append(("GET /dashboard/admin", r.status_code, list(adb.keys())[:6] if adb else r.text[:80]))

        r = await c.get(f"{BASE}/analytics/learning-stats", headers=sh)
        ls = r.json() if r.status_code == 200 else {}
        results.append(("GET /analytics/learning-stats", r.status_code, f"keys={list(ls.keys())[:5]}"))

        r = await c.get(f"{BASE}/analytics/progress-chart", headers=sh, params={"time_range": "week"})
        pc = r.json() if r.status_code == 200 else {}
        pts = pc.get("chart_data") or pc.get("data_points") or pc.get("points") or []
        results.append(("GET /analytics/progress-chart", r.status_code, f"points={len(pts) if isinstance(pts, list) else 'n/a'}"))

        r = await c.get(f"{BASE}/analytics/instructor/classes", headers=ih)
        ic = r.json() if r.status_code == 200 else {}
        results.append(("GET /analytics/instructor/classes", r.status_code, f"classes={len(ic.get('classes', ic.get('data', [])))}"))

        r = await c.get(f"{BASE}/analytics/instructor/progress-chart", headers=ih, params={"time_range": "week"})
        ipc = r.json() if r.status_code == 200 else {}
        ip_pts = ipc.get("chart_data") or ipc.get("data_points") or ipc.get("points") or []
        results.append(("GET /analytics/instructor/progress-chart", r.status_code, f"points={len(ip_pts) if isinstance(ip_pts, list) else 'n/a'}"))

        r = await c.get(f"{BASE}/analytics/instructor/quiz-performance", headers=ih)
        iqp = r.json() if r.status_code == 200 else {}
        results.append(("GET /analytics/instructor/quiz-performance", r.status_code, f"keys={list(iqp.keys())[:5]}"))

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
