#!/usr/bin/env python3
"""Phase 2 data audit: compare MongoDB fields vs API responses for QA report."""
from __future__ import annotations

import json
import sys
from typing import Any

import requests
from pymongo import MongoClient

BASE = "http://127.0.0.1:8000/api/v1"
DB = MongoClient("mongodb://localhost:27017")["ai_learning_app"]

ACCOUNTS = {
    "student": ("student1@gmail.com", "Student@123"),
    "instructor": ("instructor1@ailearning.vn", "Instructor@123"),
    "admin": ("admin1@ailearning.vn", "Admin@123456"),
}


def login(role: str) -> str:
    email, password = ACCOUNTS[role]
    r = requests.post(f"{BASE}/auth/login", json={"email": email, "password": password}, timeout=30)
    r.raise_for_status()
    body = r.json()
    data = body.get("data") or body
    return data["access_token"]


def api_get(path: str, token: str) -> dict[str, Any]:
    r = requests.get(f"{BASE}{path}", headers={"Authorization": f"Bearer {token}"}, timeout=30)
    return {"status": r.status_code, "body": r.json() if r.content else {}}


def unwrap(body: dict) -> Any:
    if isinstance(body, dict) and "data" in body:
        return body["data"]
    return body


def field_matrix(label: str, db: dict, api: dict, keys: list[str]) -> list[dict]:
    rows = []
    for k in keys:
        dv = db.get(k) if db else None
        av = api.get(k) if isinstance(api, dict) else None
        if dv is not None and av is None:
            status = "API_MISSING"
        elif dv is None and av is not None:
            status = "DB_NULL_OK"
        elif dv == av or (dv is not None and av is not None):
            status = "OK"
        elif dv is not None and av is not None:
            status = "MISMATCH"
        else:
            status = "BOTH_NULL"
        rows.append({"entity": label, "field": k, "db": dv, "api": av, "status": status})
    return rows


def main() -> int:
    report: dict[str, Any] = {"samples": {}, "matrices": [], "gaps": []}

    student_tok = login("student")
    inst_tok = login("instructor")
    admin_tok = login("admin")

    # --- Course (enrolled sample) ---
    course = DB.courses.find_one({"title": "Bootcamp Business 3"})
    if not course:
        course = DB.courses.find_one()
    cid = course.get("id") or str(course.get("_id", ""))
    detail = unwrap(api_get(f"/courses/{cid}", student_tok)["body"])
    list_resp = unwrap(api_get("/courses?page=1&limit=20", student_tok)["body"])
    list_items = list_resp.get("items") or list_resp.get("courses") or (
        list_resp if isinstance(list_resp, list) else []
    )
    list_item = next((x for x in list_items if x.get("id") == cid or x.get("course_id") == cid), list_items[0] if list_items else {})

    course_keys = [
        "title",
        "description",
        "level",
        "category",
        "thumbnail_url",
        "preview_video_url",
        "avg_rating",
        "status",
        "language",
    ]
    report["samples"]["course_id"] = cid
    report["samples"]["course_title"] = course.get("title")
    report["matrices"].extend(field_matrix("course_detail", course, detail or {}, course_keys))
    report["matrices"].extend(
        field_matrix("course_list_card", course, list_item or {}, course_keys + ["enrollment_count", "instructor_name", "total_modules", "total_lessons"])
    )
    if course.get("avg_rating") and not (detail or {}).get("avg_rating"):
        report["gaps"].append("UIUX-002: avg_rating in DB but missing in GET /courses/{id}")
    if course.get("avg_rating") and not (list_item or {}).get("avg_rating"):
        report["gaps"].append("avg_rating missing in GET /courses list response")

    # --- Unenrolled course (catalog only) ---
    stu = DB.users.find_one({"email": "student1@gmail.com"})
    stu_id = (stu or {}).get("id") or str((stu or {}).get("_id", ""))
    enrolled_ids = [
        e.get("course_id")
        for e in DB.enrollments.find({"user_id": stu_id}, {"course_id": 1}).limit(500)
        if e.get("course_id")
    ]
    unenrolled = DB.courses.find_one({"id": {"$nin": enrolled_ids}}) if stu_id else None
    if unenrolled:
        uid = unenrolled.get("id")
        ud = unwrap(api_get(f"/courses/{uid}", student_tok)["body"])
        report["samples"]["unenrolled_course"] = unenrolled.get("title")
        ei = (ud or {}).get("enrollment_info") or {}
        report["matrices"].append(
            {
                "entity": "unenrolled_course",
                "field": "enrollment_info.is_enrolled",
                "db": "not enrolled",
                "api": ei.get("is_enrolled"),
                "status": "OK" if ei.get("is_enrolled") is False else "CHECK",
            }
        )

    # --- Class (instructor) ---
    inst_user = DB.users.find_one({"email": "instructor1@ailearning.vn"})
    inst_id = (inst_user or {}).get("id") or str((inst_user or {}).get("_id", ""))
    cls = DB.classes.find_one({"instructor_id": inst_id}) if inst_id else DB.classes.find_one()
    if cls:
        class_id = cls.get("id") or str(cls.get("_id", ""))
        cd = unwrap(api_get(f"/classes/{class_id}", inst_tok)["body"])
        class_keys = ["name", "description", "invite_code", "max_students", "start_date", "end_date", "status", "course_id"]
        report["samples"]["class_id"] = class_id
        report["samples"]["class_name"] = cls.get("name")
        report["matrices"].extend(field_matrix("class_detail", cls, cd or {}, class_keys))
        students = unwrap(api_get(f"/classes/{class_id}/students", inst_tok)["body"])
        st_list = students if isinstance(students, list) else (students or {}).get("items") or (students or {}).get("data") or []
        report["samples"]["class_student_count_api"] = len(st_list) if isinstance(st_list, list) else st_list
        report["samples"]["class_student_count_db"] = len(cls.get("student_ids") or [])

    # --- Student my-classes ---
    my_cls = unwrap(api_get("/classes/my-classes", student_tok)["body"])
    mc_list = my_cls if isinstance(my_cls, list) else (my_cls or {}).get("items") or (my_cls or {}).get("classes") or []
    report["samples"]["student_my_classes_count"] = len(mc_list) if isinstance(mc_list, list) else 0

    # --- Quiz ---
    quiz = DB.quizzes.find_one({"status": "published"}) or DB.quizzes.find_one()
    if quiz:
        qid = quiz.get("id") or str(quiz.get("_id", ""))
        qd = unwrap(api_get(f"/quizzes/{qid}", student_tok)["body"])
        quiz_keys = ["title", "description", "time_limit_minutes", "passing_score", "questions", "course_id", "lesson_id"]
        report["samples"]["quiz_id"] = qid
        report["matrices"].extend(field_matrix("quiz_detail", quiz, qd or {}, quiz_keys))

    # --- Admin users list ---
    users = unwrap(api_get("/admin/users?page=1&limit=5", admin_tok)["body"])
    u_items = users.get("items") if isinstance(users, dict) else users
    if u_items:
        u0 = u_items[0]
        db_u = DB.users.find_one({"id": u0.get("id") or u0.get("user_id")}) or {}
        admin_user_keys = ["full_name", "email", "role", "status", "avatar_url"]
        report["matrices"].extend(field_matrix("admin_user_row", db_u, u0, admin_user_keys))

    # --- Admin courses list ---
    courses = unwrap(api_get("/admin/courses?page=1&limit=5", admin_tok)["body"])
    c_items = courses.get("items") if isinstance(courses, dict) else courses
    if c_items:
        c0 = c_items[0]
        db_c = DB.courses.find_one({"id": c0.get("course_id") or c0.get("id")}) or {}
        admin_course_keys = ["title", "category", "level", "status", "course_type", "enrollment_count"]
        report["matrices"].extend(field_matrix("admin_course_row", db_c, c0, admin_course_keys))

    # --- Dashboard payloads ---
    for role, path in [
        ("student", "/dashboard/student"),
        ("instructor", "/dashboard/instructor"),
        ("admin", "/dashboard/admin"),
    ]:
        tok = {"student": student_tok, "instructor": inst_tok, "admin": admin_tok}[role]
        dash = unwrap(api_get(path, tok)["body"])
        report["samples"][f"dashboard_{role}_keys"] = sorted(dash.keys()) if isinstance(dash, dict) else str(type(dash))

    # --- Search analytics (admin) ---
    sa = api_get("/search/analytics", admin_tok)
    report["samples"]["search_analytics_status"] = sa["status"]

    # Print summary
    issues = [m for m in report["matrices"] if m["status"] in ("API_MISSING", "MISMATCH")]
    print(json.dumps({"issue_count": len(issues), "gaps": report["gaps"], "issues": issues[:30], "samples": report["samples"]}, indent=2, default=str))
    return 0 if not issues else 0


if __name__ == "__main__":
    sys.exit(main())
