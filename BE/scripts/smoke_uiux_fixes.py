"""Quick smoke test for UIUX-007/003 fixes."""
import asyncio
import httpx


async def main():
    base = "http://127.0.0.1:8000/api/v1"
    async with httpx.AsyncClient(timeout=30) as client:
        login = await client.post(
            f"{base}/auth/login",
            json={"email": "student1@gmail.com", "password": "Student@123"},
        )
        login.raise_for_status()
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        cid = "6cec7c81-6ff4-425e-84c8-de3238e0b5a2"
        lid = "44d94937-6bfa-49f1-aa4d-a2fbc4e4727b"

        lesson = await client.get(f"{base}/courses/{cid}/lessons/{lid}", headers=headers)
        print("lesson", lesson.status_code, lesson.json().get("title", lesson.text[:120]))

        classes = await client.get(f"{base}/classes/my-classes", headers=headers)
        print("classes", classes.status_code, len(classes.json().get("classes", [])))

        course = await client.get(f"{base}/courses/{cid}", headers=headers)
        stats = course.json().get("course_statistics", {})
        print("avg_rating", stats.get("avg_rating"))


if __name__ == "__main__":
    asyncio.run(main())
