"""Phase 2b.2 — API audit for courses catalog & enrollments."""
import asyncio
import json
import sys

import httpx

sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:8000/api/v1"
STUDENT = ("student1@gmail.com", "Student@123")
INSTRUCTOR = ("instructor1@ailearning.vn", "Instructor@123")


async def login(client: httpx.AsyncClient, creds):
    r = await client.post(f"{BASE}/auth/login", json={"email": creds[0], "password": creds[1]})
    r.raise_for_status()
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


async def main():
    results = []
    async with httpx.AsyncClient(timeout=45) as c:
        sh = await login(c, STUDENT)
        ih = await login(c, INSTRUCTOR)

        # 1 search
        r = await c.get(f"{BASE}/courses/search", headers=sh, params={"limit": 5, "keyword": "Math"})
        results.append(("GET /courses/search", r.status_code, len(r.json().get("courses", []))))

        # 2 public
        r = await c.get(f"{BASE}/courses/public", headers=sh, params={"limit": 5})
        results.append(("GET /courses/public", r.status_code, len(r.json().get("courses", []))))

        courses = r.json().get("courses", [])
        if not courses:
            r2 = await c.get(f"{BASE}/courses/search", headers=sh, params={"limit": 3})
            courses = r2.json().get("courses", [])

        cid = courses[0]["id"] if courses else None

        # 3 detail
        if cid:
            r = await c.get(f"{BASE}/courses/{cid}", headers=sh)
            d = r.json()
            results.append(
                (
                    "GET /courses/{id}",
                    r.status_code,
                    f"enrolled={d.get('enrollment_info', {}).get('is_enrolled')} rating={d.get('course_statistics', {}).get('avg_rating')}",
                )
            )

            # 4 enrollment-status
            r = await c.get(f"{BASE}/courses/{cid}/enrollment-status", headers=sh)
            results.append(("GET /courses/{id}/enrollment-status", r.status_code, r.text[:80]))

        # 5 my-courses
        r = await c.get(f"{BASE}/enrollments/my-courses", headers=sh, params={"limit": 5})
        enrollments = r.json().get("enrollments", [])
        results.append(("GET /enrollments/my-courses", r.status_code, len(enrollments)))

        eid = None
        if enrollments:
            eid = enrollments[0].get("id") or enrollments[0].get("enrollment_id")

        # 6 enrollment detail
        if eid:
            r = await c.get(f"{BASE}/enrollments/{eid}", headers=sh)
            results.append(("GET /enrollments/{id}", r.status_code, r.json().get("course_title", "")[:40]))

        # Find unenrolled course for enroll test
        unenrolled_cid = None
        r = await c.get(f"{BASE}/courses/search", headers=sh, params={"limit": 20})
        for course in r.json().get("courses", []):
            cid2 = course["id"]
            det = await c.get(f"{BASE}/courses/{cid2}", headers=sh)
            if det.status_code == 200 and not det.json().get("enrollment_info", {}).get("is_enrolled"):
                unenrolled_cid = cid2
                break

        # 7 POST enroll (then cancel if success)
        if unenrolled_cid:
            r = await c.post(f"{BASE}/enrollments", headers=sh, json={"course_id": unenrolled_cid})
            results.append(("POST /enrollments", r.status_code, r.json().get("id", r.text[:60])))
            new_eid = r.json().get("id") if r.status_code in (200, 201) else None
            if new_eid:
                dr = await c.delete(f"{BASE}/enrollments/{new_eid}", headers=sh)
                results.append(("DELETE /enrollments/{id} (cleanup)", dr.status_code, ""))
        else:
            results.append(("POST /enrollments", "SKIP", "no unenrolled course found"))
            if eid:
                # dry-run: only verify endpoint exists with HEAD-like GET already done
                results.append(("DELETE /enrollments/{id}", "SKIP", "no test enroll; use manual"))

        # instructor public
        r = await c.get(f"{BASE}/courses/public", headers=ih, params={"limit": 3})
        results.append(("GET /courses/public (instructor)", r.status_code, len(r.json().get("courses", []))))

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
