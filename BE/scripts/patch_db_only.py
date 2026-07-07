# -*- coding: utf-8 -*-
"""
patch_db_only.py
================
- Đọc file BE/scripts/courses_import.json
- Kết nối vào Database MongoDB (qua cấu hình trong .env)
- Thực hiện cập nhật/chèn mới (Upsert) chỉ cho các collection: courses, modules, lessons
- KHÔNG xóa/drop các collection khác (Users, Enrollments, Progress,...) để tránh mất mát dữ liệu thực tế.
- Giữ nguyên ID (_id) của các Course, Module, Lesson cũ nếu trùng khớp tiêu đề để bảo toàn liên kết dữ liệu tiến độ của học viên.
"""

import asyncio
import json
import sys
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import get_settings
from app.database import init_database
from models.models import (
    Course,
    Module,
    Lesson,
    EmbeddedModule,
    EmbeddedLesson
)

def gid() -> str:
    return uuid.uuid4().hex

async def patch_database_courses():
    # 1. Khởi tạo kết nối Database từ cấu hình trong .env
    print("[INIT] Khởi tạo kết nối database...")
    await init_database()
    print("[SUCCESS] Đã kết nối cơ sở dữ liệu thành công.")

    # 2. Đọc file JSON danh mục khóa học
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "courses_import.json")
    if not os.path.exists(json_path):
        print(f"[ERROR] Không tìm thấy file dữ liệu import tại: {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        courses_data = json.load(f)
    print(f"[INFO] Đọc thành công {len(courses_data)} khóa học từ file JSON.")

    # 3. Tiến hành Upsert từng khóa học
    for idx, c_data in enumerate(courses_data):
        title = c_data["title"]
        print(f"\n[{idx+1}/{len(courses_data)}] Đang xử lý khóa học: {title}")

        # Tìm xem khóa học đã tồn tại trong DB chưa
        db_course = await Course.find_one({"title": title})
        if db_course:
            cid = db_course.id
            print(f"  -> Tìm thấy Khóa học cũ (ID: {cid}). Tiến hành cập nhật.")
            db_course.description = c_data.get("description", db_course.description)
            db_course.category = c_data.get("category", db_course.category)
            db_course.level = c_data.get("level", db_course.level)
            db_course.thumbnail_url = c_data.get("thumbnail_url", db_course.thumbnail_url)
            db_course.preview_video_url = c_data.get("preview_video_url", db_course.preview_video_url)
            db_course.learning_outcomes = c_data.get("learning_outcomes", db_course.learning_outcomes)
            db_course.prerequisites = c_data.get("prerequisites", db_course.prerequisites)
            db_course.updated_at = datetime.utcnow()
        else:
            cid = gid()
            print(f"  -> Không tìm thấy Khóa học. Tiến hành chèn mới (ID: {cid}).")
            # Thiết lập các thông số mặc định cho khóa học mới
            db_course = Course(
                id=cid,
                title=title,
                description=c_data.get("description", ""),
                category=c_data.get("category", "Programming"),
                level=c_data.get("level", "Beginner"),
                thumbnail_url=c_data.get("thumbnail_url", None),
                preview_video_url=c_data.get("preview_video_url", None),
                language="vi",
                status="published",
                owner_id="admin_system", # Gán owner mặc định là quản trị viên hệ thống
                owner_type="admin",
                course_type="public",
                learning_outcomes=c_data.get("learning_outcomes", []),
                prerequisites=c_data.get("prerequisites", []),
                modules=[],
                total_duration_minutes=0,
                total_modules=0,
                total_lessons=0,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

        # Xử lý các modules và lessons của khóa học
        module_embeds = []
        total_duration_course = 0
        total_lessons_course = 0

        modules_list = c_data.get("modules", [])
        for m_idx, m_data in enumerate(modules_list):
            m_title = m_data["title"]
            # Tìm xem module đã tồn tại trong DB chưa
            db_module = await Module.find_one({"course_id": cid, "title": m_title})
            if db_module:
                mid = db_module.id
                db_module.description = m_data.get("description", db_module.description)
                db_module.order = m_idx + 1
                db_module.difficulty = m_data.get("difficulty", db_module.difficulty)
                db_module.estimated_hours = m_data.get("estimated_hours", db_module.estimated_hours)
                db_module.learning_outcomes = m_data.get("learning_outcomes", db_module.learning_outcomes)
                db_module.resources = m_data.get("resources", db_module.resources)
                db_module.prerequisites = m_data.get("prerequisites", db_module.prerequisites)
                db_module.updated_at = datetime.utcnow()
            else:
                mid = gid()
                db_module = Module(
                    id=mid,
                    course_id=cid,
                    title=m_title,
                    description=m_data.get("description", m_title),
                    order=m_idx + 1,
                    difficulty=m_data.get("difficulty", "Basic"),
                    estimated_hours=m_data.get("estimated_hours", 2.0),
                    learning_outcomes=m_data.get("learning_outcomes", []),
                    resources=m_data.get("resources", []),
                    prerequisites=m_data.get("prerequisites", []),
                    total_lessons=0,
                    total_duration_minutes=0,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )

            # Xử lý các lessons của module này
            lesson_embeds = []
            total_duration_module = 0
            lessons_list = m_data.get("lessons", [])

            for l_idx, l_data in enumerate(lessons_list):
                l_title = l_data["title"]
                # Tìm xem bài học đã có trong DB chưa
                db_lesson = await Lesson.find_one({"course_id": cid, "module_id": mid, "title": l_title})
                
                # Tính thời lượng bài học mặc định
                mins = l_data.get("duration_minutes") or 30
                ctype = l_data.get("content_type") or "text"

                if db_lesson:
                    lid = db_lesson.id
                    db_lesson.description = l_data.get("description", db_lesson.description)
                    db_lesson.order = l_idx + 1
                    db_lesson.content = l_data.get("content", db_lesson.content)
                    db_lesson.content_type = ctype
                    db_lesson.duration_minutes = mins
                    db_lesson.video_url = l_data.get("video_url", db_lesson.video_url)
                    db_lesson.learning_objectives = l_data.get("learning_objectives", db_lesson.learning_objectives)
                    db_lesson.resources = l_data.get("resources", db_lesson.resources)
                    db_lesson.updated_at = datetime.utcnow()
                else:
                    lid = gid()
                    db_lesson = Lesson(
                        id=lid,
                        module_id=mid,
                        course_id=cid,
                        title=l_title,
                        description=l_data.get("description", l_title),
                        order=l_idx + 1,
                        content=l_data.get("content", ""),
                        content_type=ctype,
                        duration_minutes=mins,
                        video_url=l_data.get("video_url", None),
                        learning_objectives=l_data.get("learning_objectives", []),
                        resources=l_data.get("resources", []),
                        is_published=True,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )

                await db_lesson.save()
                total_duration_module += mins
                total_lessons_course += 1

                # Thêm vào danh sách nhúng để lưu trong Course
                lesson_embeds.append(
                    EmbeddedLesson(
                        id=lid,
                        title=l_title,
                        description=db_lesson.description,
                        order=db_lesson.order,
                        content=db_lesson.content,
                        content_type=ctype,
                        duration_minutes=mins,
                        video_url=db_lesson.video_url,
                        audio_url=db_lesson.audio_url,
                        resources=db_lesson.resources,
                        learning_objectives=db_lesson.learning_objectives,
                        quiz_id=db_lesson.quiz_id,
                        is_published=db_lesson.is_published,
                        created_at=db_lesson.created_at,
                        updated_at=db_lesson.updated_at
                    )
                )

            # Cập nhật thông số tính toán của Module và lưu
            db_module.total_lessons = len(lesson_embeds)
            db_module.total_duration_minutes = total_duration_module
            await db_module.save()

            total_duration_course += total_duration_module

            # Thêm vào danh sách nhúng để lưu trong Course
            module_embeds.append(
                EmbeddedModule(
                    id=mid,
                    title=m_title,
                    description=db_module.description,
                    order=db_module.order,
                    difficulty=db_module.difficulty,
                    estimated_hours=db_module.estimated_hours,
                    learning_outcomes=db_module.learning_outcomes,
                    prerequisites=db_module.prerequisites,
                    resources=db_module.resources,
                    lessons=lesson_embeds,
                    total_lessons=db_module.total_lessons,
                    total_duration_minutes=db_module.total_duration_minutes,
                    created_at=db_module.created_at,
                    updated_at=db_module.updated_at
                )
            )

        # Cập nhật thông số tính toán của Course và lưu
        db_course.modules = module_embeds
        db_course.total_modules = len(module_embeds)
        db_course.total_lessons = total_lessons_course
        db_course.total_duration_minutes = total_duration_course
        await db_course.save()

        print(f"  -> Cập nhật hoàn tất: {len(module_embeds)} modules, {total_lessons_course} lessons.")

    print("\n[SUCCESS] Hoàn thành cập nhật toàn bộ cơ sở dữ liệu khóa học!")

if __name__ == "__main__":
    asyncio.run(patch_database_courses())
