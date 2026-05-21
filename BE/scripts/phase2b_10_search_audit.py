"""Phase 2b.10 — API audit for search (4 ops)."""
import asyncio
import json
import sys

import httpx

sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:8000/api/v1"
STUDENT = ("student1@gmail.com", "Student@123")
ADMIN = ("admin1@ailearning.vn", "Admin@123456")
KEYWORD = "math"


async def login(client: httpx.AsyncClient, creds):
    r = await client.post(f"{BASE}/auth/login", json={"email": creds[0], "password": creds[1]})
    r.raise_for_status()
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


async def main():
    results = []

    async with httpx.AsyncClient(timeout=60) as c:
        sh = await login(c, STUDENT)
        ah = await login(c, ADMIN)

        r = await c.get(f"{BASE}/search", params={"q": KEYWORD, "limit": 10}, headers=sh)
        body = r.json() if r.status_code == 200 else {}
        total = body.get("total_results")
        groups = len(body.get("results_by_category") or [])
        results.append(
            (
                "GET /search",
                r.status_code,
                f"total={total} groups={groups} err={r.text[:80] if r.status_code != 200 else ''}",
            )
        )

        r = await c.get(f"{BASE}/search/suggestions", params={"q": "ma"}, headers=sh)
        sug_body = r.json() if r.status_code == 200 else {}
        sug_count = len(sug_body.get("suggestions") or sug_body if isinstance(sug_body, list) else [])
        if isinstance(sug_body, dict):
            sug_count = len(sug_body.get("suggestions") or [])
        results.append(
            (
                "GET /search/suggestions",
                r.status_code,
                f"count={sug_count}",
            )
        )

        r = await c.get(f"{BASE}/search/history", headers=sh)
        hist = r.json() if r.status_code == 200 else {}
        hist_count = len(hist.get("search_history") or [])
        results.append(
            (
                "GET /search/history",
                r.status_code,
                f"count={hist_count}",
            )
        )

        r = await c.get(f"{BASE}/search/analytics", headers=sh)
        results.append(
            (
                "GET /search/analytics (student)",
                r.status_code,
                "403 expected" if r.status_code == 403 else r.text[:60],
            )
        )

        r = await c.get(f"{BASE}/search/analytics", headers=ah)
        analytics = r.json() if r.status_code == 200 else {}
        total_searches = analytics.get("total_searches")
        results.append(
            (
                "GET /search/analytics (admin)",
                r.status_code,
                f"total_searches={total_searches}",
            )
        )

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
