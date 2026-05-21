"""Phase 2b.5 — API audit for assessments & recommendations."""
import asyncio
import json
import sys
from datetime import datetime, timezone

import httpx

sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:8000/api/v1"
STUDENT = ("student1@gmail.com", "Student@123")
GENERATE_PAYLOAD = {
    "category": "Programming",
    "subject": "Python",
    "level": "Beginner",
    "focus_areas": ["Variables", "Functions"],
}


async def login(client: httpx.AsyncClient, creds):
    r = await client.post(f"{BASE}/auth/login", json={"email": creds[0], "password": creds[1]})
    r.raise_for_status()
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def build_answers(questions):
    answers = []
    for q in questions:
        opts = q.get("options") or []
        answers.append(
            {
                "question_id": q["question_id"],
                "answer_content": opts[0] if opts else "test answer",
                "selected_option": 0 if opts else None,
                "time_taken_seconds": 25,
            }
        )
    return answers


async def main():
    results = []
    session_id = None
    evaluated_session_id = None

    async with httpx.AsyncClient(timeout=180) as c:
        sh = await login(c, STUDENT)

        # 1 GET history (before generate)
        r = await c.get(f"{BASE}/assessments/history", headers=sh, params={"limit": 10})
        hist_before = r.json() if r.status_code == 200 else {}
        sessions_before = hist_before.get("sessions", [])
        results.append(
            (
                "GET /assessments/history",
                r.status_code,
                f"sessions={len(sessions_before)}",
            )
        )
        for s in sessions_before:
            if s.get("status") == "evaluated":
                evaluated_session_id = s.get("session_id")
                break

        # 2 POST generate (AI — may take time)
        r = await c.post(f"{BASE}/assessments/generate", headers=sh, json=GENERATE_PAYLOAD)
        gen = r.json() if r.status_code in (200, 201) else {}
        session_id = gen.get("session_id")
        qcount = len(gen.get("questions", []))
        results.append(
            (
                "POST /assessments/generate",
                r.status_code,
                f"session={session_id} questions={qcount} err={r.text[:80] if r.status_code not in (200, 201) else ''}",
            )
        )

        if session_id and gen.get("questions"):
            answers = build_answers(gen["questions"])
            # 3 POST submit
            r = await c.post(
                f"{BASE}/assessments/{session_id}/submit",
                headers=sh,
                json={
                    "answers": answers,
                    "total_time_seconds": 300,
                    "submitted_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            results.append(
                (
                    "POST /assessments/{sid}/submit",
                    r.status_code,
                    r.text[:120],
                )
            )

            # 4 GET results (may need brief wait for AI grading)
            for attempt in range(3):
                r = await c.get(f"{BASE}/assessments/{session_id}/results", headers=sh)
                if r.status_code == 200:
                    body = r.json()
                    score = body.get("overall_score") or body.get("score") or "ok"
                    results.append(
                        (
                            "GET /assessments/{sid}/results",
                            r.status_code,
                            f"score={score}",
                        )
                    )
                    evaluated_session_id = session_id
                    break
                await asyncio.sleep(2)
            else:
                results.append(
                    (
                        "GET /assessments/{sid}/results",
                        r.status_code,
                        r.text[:120],
                    )
                )

            # 5 GET review
            r = await c.get(f"{BASE}/assessments/{session_id}/review", headers=sh)
            rev = r.json() if r.status_code == 200 else {}
            results.append(
                (
                    "GET /assessments/{sid}/review",
                    r.status_code,
                    f"questions={len(rev.get('questions', rev.get('review', [])))} err={r.text[:60] if r.status_code != 200 else ''}",
                )
            )

        # 6 GET history (after)
        r = await c.get(f"{BASE}/assessments/history", headers=sh, params={"limit": 10})
        hist_after = r.json() if r.status_code == 200 else {}
        results.append(
            (
                "GET /assessments/history (after)",
                r.status_code,
                f"sessions={len(hist_after.get('sessions', []))}",
            )
        )

        rec_sid = evaluated_session_id or session_id
        if rec_sid:
            # 7 GET recommendations from assessment
            r = await c.get(
                f"{BASE}/recommendations/from-assessment",
                headers=sh,
                params={"session_id": rec_sid},
            )
            rec = r.json() if r.status_code == 200 else {}
            courses = rec.get("recommended_courses") or rec.get("courses") or rec.get("recommendations") or []
            results.append(
                (
                    "GET /recommendations/from-assessment",
                    r.status_code,
                    f"courses={len(courses) if isinstance(courses, list) else 'n/a'} err={r.text[:80] if r.status_code != 200 else ''}",
                )
            )
        else:
            results.append(
                (
                    "GET /recommendations/from-assessment",
                    "SKIP",
                    "no evaluated session",
                )
            )

        # 8 GET recommendations list
        r = await c.get(f"{BASE}/recommendations", headers=sh)
        rec_list = r.json() if r.status_code == 200 else {}
        items = rec_list.get("recommendations") or rec_list.get("courses") or rec_list.get("data") or []
        results.append(
            (
                "GET /recommendations",
                r.status_code,
                f"items={len(items) if isinstance(items, list) else 'n/a'}",
            )
        )

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
