"""Phase 2b.4 — API audit for quizzes & AI practice."""
import asyncio
import json
import sys

import httpx

sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:8000/api/v1"
COURSE_ID = "6cec7c81-6ff4-425e-84c8-de3238e0b5a2"
LESSON_WITH_QUIZ = "fc027579-aff5-412f-aa22-587284117067"
STUDENT = ("student1@gmail.com", "Student@123")
INSTRUCTOR = ("instructor1@ailearning.vn", "Instructor@123")


async def login(client: httpx.AsyncClient, creds):
    r = await client.post(f"{BASE}/auth/login", json={"email": creds[0], "password": creds[1]})
    r.raise_for_status()
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


async def main():
    results = []
    async with httpx.AsyncClient(timeout=90) as c:
        sh = await login(c, STUDENT)
        ih = await login(c, INSTRUCTOR)

        # 1 GET /quizzes — student list
        r = await c.get(f"{BASE}/quizzes", headers=sh, params={"limit": 10})
        quizzes = r.json().get("data", []) if r.status_code == 200 else []
        results.append(("GET /quizzes (student)", r.status_code, len(quizzes)))

        # 2 GET /quizzes — instructor list
        r = await c.get(f"{BASE}/quizzes", headers=ih, params={"limit": 10})
        inst_quizzes = r.json().get("data", []) if r.status_code == 200 else []
        results.append(("GET /quizzes (instructor)", r.status_code, len(inst_quizzes)))

        quiz_id = None
        if quizzes:
            quiz_id = quizzes[0].get("quiz_id") or quizzes[0].get("id")

        # quiz from lesson
        if not quiz_id:
            lr = await c.get(
                f"{BASE}/courses/{COURSE_ID}/lessons/{LESSON_WITH_QUIZ}",
                headers=sh,
            )
            if lr.status_code == 200:
                qi = lr.json().get("quiz_info") or {}
                quiz_id = qi.get("quiz_id")

        if not quiz_id and inst_quizzes:
            quiz_id = inst_quizzes[0].get("quiz_id") or inst_quizzes[0].get("id")

        if quiz_id:
            # 3 GET detail
            r = await c.get(f"{BASE}/quizzes/{quiz_id}", headers=sh)
            detail = r.json() if r.status_code == 200 else {}
            qcount = len(detail.get("questions", []))
            results.append(("GET /quizzes/{id}", r.status_code, f"questions={qcount} title={str(detail.get('title',''))[:40]}"))

            # 4 POST attempt
            answers = []
            for q in detail.get("questions", []):
                qid = q.get("question_id") or q.get("id")
                opts = q.get("options") or []
                answers.append({"question_id": qid, "selected_option": "A" if opts else "test"})

            if answers:
                r = await c.post(
                    f"{BASE}/quizzes/{quiz_id}/attempt",
                    headers=sh,
                    json={"answers": answers, "time_spent_minutes": 3},
                )
                results.append(("POST /quizzes/{id}/attempt", r.status_code, r.text[:100]))

            # 5 GET results
            r = await c.get(f"{BASE}/quizzes/{quiz_id}/results", headers=sh)
            res_body = r.json() if r.status_code == 200 else {}
            results.append(
                (
                    "GET /quizzes/{id}/results",
                    r.status_code,
                    f"score={res_body.get('score')} can_retake={res_body.get('can_retake')}",
                )
            )

            # 6 POST retake (may need AI / fail if passed)
            r = await c.post(f"{BASE}/quizzes/{quiz_id}/retake", headers=sh)
            results.append(("POST /quizzes/{id}/retake", r.status_code, r.text[:80]))

            # 9 GET class-results (instructor) — requires class_id
            classes = (await c.get(f"{BASE}/classes/my-classes", headers=ih)).json().get("classes", [])
            class_id = (classes[0].get("id") or classes[0].get("class_id")) if classes else None
            if class_id:
                r = await c.get(
                    f"{BASE}/quizzes/{quiz_id}/class-results",
                    headers=ih,
                    params={"class_id": class_id},
                )
                results.append(("GET /quizzes/{id}/class-results", r.status_code, r.text[:80]))
            else:
                results.append(("GET /quizzes/{id}/class-results", "SKIP", "no class"))

            # 8 DELETE — skip destructive; verify OPTIONS only
            results.append(("DELETE /quizzes/{id}", "SKIP", "no destructive test in audit"))
        else:
            results.append(("quiz flow", "SKIP", "no quiz_id found"))

        # 7 POST /lessons/{lid}/quizzes — dry validation only
        r = await c.post(
            f"{BASE}/lessons/{LESSON_WITH_QUIZ}/quizzes",
            headers=ih,
            json={},
        )
        results.append(("POST /lessons/{lid}/quizzes (empty body)", r.status_code, r.text[:80]))

        # 10 POST generate-practice
        r = await c.post(
            f"{BASE}/ai/generate-practice",
            headers=sh,
            json={"lesson_id": LESSON_WITH_QUIZ, "question_count": 3, "difficulty": "medium"},
        )
        results.append(("POST /ai/generate-practice", r.status_code, r.text[:80]))

        # PUT — API_NO_UI smoke
        if quiz_id:
            r = await c.put(f"{BASE}/quizzes/{quiz_id}", headers=ih, json={"title": "audit"})
            results.append(("PUT /quizzes/{id}", r.status_code, r.text[:60]))

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
