"""Phase 2b.7 — API audit for classes (10 ops)."""
import asyncio
import json
import sys
from datetime import datetime, timedelta, timezone

import httpx

sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:8000/api/v1"
COURSE_ID = "6cec7c81-6ff4-425e-84c8-de3238e0b5a2"
STUDENT = ("student1@gmail.com", "Student@123")
INSTRUCTOR = ("instructor1@ailearning.vn", "Instructor@123")


async def login(client: httpx.AsyncClient, creds):
    r = await client.post(f"{BASE}/auth/login", json={"email": creds[0], "password": creds[1]})
    r.raise_for_status()
    body = r.json()
    return {"Authorization": f"Bearer {body['access_token']}"}, body.get("user", {})


async def main():
    results = []
    temp_class_id = None

    async with httpx.AsyncClient(timeout=90) as c:
        sh, student_user = await login(c, STUDENT)
        ih, _ = await login(c, INSTRUCTOR)
        student_id = student_user.get("id") or student_user.get("user_id")

        # Existing class with students (read-only probes)
        r = await c.get(f"{BASE}/classes/my-classes", headers=ih)
        inst_classes = r.json().get("classes", []) if r.status_code == 200 else []
        sample_id = inst_classes[0]["id"] if inst_classes else None
        results.append(
            ("GET /classes/my-classes (instructor)", r.status_code, f"count={len(inst_classes)}")
        )

        r = await c.get(f"{BASE}/classes/my-classes", headers=sh)
        stud_classes = r.json().get("classes", []) if r.status_code == 200 else []
        results.append(
            ("GET /classes/my-classes (student)", r.status_code, f"count={len(stud_classes)}")
        )

        if sample_id:
            r = await c.get(f"{BASE}/classes/{sample_id}", headers=ih)
            detail = r.json() if r.status_code == 200 else {}
            results.append(
                ("GET /classes/{id} (instructor)", r.status_code, f"name={detail.get('name', '')[:30]}")
            )

            r = await c.get(f"{BASE}/classes/{sample_id}/students", headers=ih)
            stu_body = r.json() if r.status_code == 200 else {}
            stu_rows = stu_body.get("data", [])
            results.append(
                ("GET /classes/{id}/students", r.status_code, f"students={len(stu_rows)} total={stu_body.get('total')}")
            )

            if stu_rows:
                sid = stu_rows[0].get("student_id")
                r = await c.get(f"{BASE}/classes/{sample_id}/students/{sid}", headers=ih)
                sd = r.json() if r.status_code == 200 else {}
                results.append(
                    (
                        "GET /classes/{id}/students/{sid}",
                        r.status_code,
                        f"student={sd.get('student_name', 'n/a')[:20]} modules={len(sd.get('modules_detail', []))}",
                    )
                )
            else:
                results.append(("GET /classes/{id}/students/{sid}", "SKIP", "no students in sample class"))

            r = await c.get(f"{BASE}/classes/{sample_id}/progress", headers=ih)
            prog = r.json() if r.status_code == 200 else {}
            results.append(
                (
                    "GET /classes/{id}/progress",
                    r.status_code,
                    f"avg={prog.get('average_progress')} completion={prog.get('completion_rate')}",
                )
            )

        # Mutating flow: create → join → update → remove → delete
        now = datetime.now(timezone.utc)
        create_payload = {
            "name": f"2b7 Audit {now.strftime('%H%M%S')}",
            "description": "Temporary class for phase 2b.7 audit",
            "course_id": COURSE_ID,
            "start_date": now.isoformat(),
            "end_date": (now + timedelta(days=90)).isoformat(),
            "max_students": 30,
        }
        r = await c.post(f"{BASE}/classes", headers=ih, json=create_payload)
        created = r.json() if r.status_code in (200, 201) else {}
        temp_class_id = created.get("class_id") or created.get("id")
        invite = created.get("invite_code")
        results.append(
            ("POST /classes", r.status_code, f"class_id={temp_class_id} invite={invite}")
        )

        if temp_class_id:
            r = await c.put(
                f"{BASE}/classes/{temp_class_id}",
                headers=ih,
                json={"name": create_payload["name"] + " (updated)"},
            )
            results.append(("PUT /classes/{id}", r.status_code, r.text[:80] if r.status_code != 200 else "ok"))

        if invite:
            r = await c.post(f"{BASE}/classes/join", headers=sh, json={"invite_code": invite})
            join = r.json() if r.status_code in (200, 201) else {}
            results.append(
                ("POST /classes/join", r.status_code, f"class={join.get('class_name', '')[:24]} err={r.text[:60] if r.status_code not in (200, 201) else ''}")
            )

            if temp_class_id and student_id and r.status_code in (200, 201):
                r = await c.get(f"{BASE}/classes/{temp_class_id}/students/{student_id}", headers=ih)
                sd = r.json() if r.status_code == 200 else {}
                results.append(
                    (
                        "GET /classes/{id}/students/{sid}",
                        r.status_code,
                        f"student={sd.get('student_name', 'n/a')[:20]} modules={len(sd.get('modules_detail', []))}",
                    )
                )

                r = await c.get(f"{BASE}/classes/{temp_class_id}", headers=sh)
                sd = r.json() if r.status_code == 200 else {}
                results.append(
                    ("GET /classes/{id} (student joined)", r.status_code, f"my_progress={sd.get('my_progress')}")
                )

                r = await c.delete(f"{BASE}/classes/{temp_class_id}/students/{student_id}", headers=ih)
                results.append(
                    ("DELETE /classes/{id}/students/{sid}", r.status_code, r.text[:60] if r.status_code not in (200, 204) else "ok")
                )

            if temp_class_id:
                r = await c.delete(f"{BASE}/classes/{temp_class_id}", headers=ih)
                results.append(
                    ("DELETE /classes/{id}", r.status_code, r.text[:60] if r.status_code not in (200, 204) else "ok")
                )
                temp_class_id = None

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
