"""
Patch hiển thị seed — sửa tên lớp, mô tả quiz, module trùng tên, skill assessment
mà không cần reseed toàn bộ DB. Chạy: python -m scripts.patch_seed_display
"""

import asyncio
import os
import re
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_database
from models.models import AssessmentSession, Class, Course, Lesson, Module, Quiz

from scripts.init_data import (
    ASSESSMENT_SKILLS_BY_CATEGORY,
    CLASS_NAME_PREFIXES,
    mk_class_description,
    mk_quiz_description,
    pick_assessment_skill,
)


def _dedupe_module_titles(modules: list) -> bool:
    changed = False
    seen: dict[str, int] = {}
    for mod in modules:
        title = getattr(mod, "title", None) or (mod.get("title") if isinstance(mod, dict) else "")
        if not title:
            continue
        if title in seen:
            seen[title] += 1
            new_title = f"{title} — Phần {seen[title]}"
            if hasattr(mod, "title"):
                mod.title = new_title
            elif isinstance(mod, dict):
                mod["title"] = new_title
            changed = True
        else:
            seen[title] = 1
    return changed


async def patch_classes() -> int:
    count = 0
    classes = await Class.find_all().to_list()
    course_ids = {c.course_id for c in classes}
    courses = {c.id: c for c in await Course.find({"_id": {"$in": list(course_ids)}}).to_list()}
    counters: dict[str, int] = {}

    for idx, cls in enumerate(classes):
        course = courses.get(cls.course_id)
        if not course:
            continue
        counters[cls.course_id] = counters.get(cls.course_id, 0) + 1
        n = counters[cls.course_id]
        prefix = CLASS_NAME_PREFIXES[idx % len(CLASS_NAME_PREFIXES)]
        short = course.title if len(course.title) <= 48 else f"{course.title[:45]}…"
        new_name = f"{prefix} {short}" if n == 1 else f"{prefix} {short} #{n}"
        new_desc = mk_class_description(course.title)
        if cls.name != new_name or cls.description != new_desc:
            cls.name = new_name
            cls.description = new_desc
            await cls.save()
            count += 1
    return count


async def patch_modules() -> int:
    count = 0
    courses = await Course.find_all().to_list()
    for course in courses:
        if _dedupe_module_titles(course.modules):
            await course.save()
            count += 1

    modules = await Module.find_all().to_list()
    by_course: dict[str, list] = {}
    for mod in modules:
        by_course.setdefault(mod.course_id, []).append(mod)
    for mods in by_course.values():
        mods.sort(key=lambda m: m.order)
        seen: dict[str, int] = {}
        for mod in mods:
            if mod.title in seen:
                seen[mod.title] += 1
                mod.title = f"{mod.title} — Phần {seen[mod.title]}"
                await mod.save()
                count += 1
            else:
                seen[mod.title] = 1
    return count


async def patch_quizzes() -> int:
    count = 0
    quizzes = await Quiz.find_all().to_list()
    lesson_ids = {q.lesson_id for q in quizzes if q.lesson_id}
    lessons = {l.id: l for l in await Lesson.find({"_id": {"$in": list(lesson_ids)}}).to_list()}

    latin_re = re.compile(r"\b(volutpat|voluptat|lorem|ipsum|facere|nobis)\b", re.I)
    for quiz in quizzes:
        lesson = lessons.get(quiz.lesson_id)
        title = lesson.title if lesson else quiz.title.replace("Quiz - ", "")
        desc = mk_quiz_description(title, (lesson.description if lesson else "") or "")
        if quiz.description != desc or (quiz.description and latin_re.search(quiz.description)):
            quiz.description = desc
            await quiz.save()
            count += 1
    return count


async def patch_assessments() -> int:
    count = 0
    sessions = await AssessmentSession.find({"status": "evaluated"}).to_list()
    for session in sessions:
        changed = False
        category = session.category or "Programming"
        for q in session.questions or []:
            tag = q.get("skill_tag") or ""
            if "_" in tag or len(tag) < 4 or tag.isascii() and tag.islower():
                q["skill_tag"] = pick_assessment_skill(category)
                changed = True
            if not q.get("question_text") or len(q.get("question_text", "")) < 8:
                q["question_text"] = f"Câu hỏi đánh giá {category} — {q.get('skill_tag', 'Tổng quan')}"
                changed = True

        sa = session.skill_analysis
        if isinstance(sa, dict):
            items = sa.get("skill_analysis") or sa.get("skills") or []
            if isinstance(items, list):
                for item in items:
                    tag = item.get("skill_tag") or ""
                    if "_" in tag:
                        item["skill_tag"] = pick_assessment_skill(category)
                        item["detailed_feedback"] = f"Kỹ năng «{item['skill_tag']}»: {item.get('correct_count', 0)}/{item.get('questions_count', 0)} câu đúng."
                        changed = True

        for gap in session.knowledge_gaps or []:
            if gap.get("gap_area") and "_" in str(gap.get("gap_area")):
                gap["gap_area"] = pick_assessment_skill(category)
                gap["description"] = f"Cần ôn thêm kiến thức {category.lower()}."
                gap["suggested_action"] = "Xem lại bài học liên quan và làm bài luyện tập."
                changed = True

        if session.subject and "_" in str(session.subject):
            session.subject = pick_assessment_skill(category)
            changed = True

        if changed:
            await session.save()
            count += 1
    return count


async def main():
    await init_database()
    c1 = await patch_classes()
    c2 = await patch_modules()
    c3 = await patch_quizzes()
    c4 = await patch_assessments()
    print(f"Patched classes: {c1}")
    print(f"Patched courses/modules: {c2}")
    print(f"Patched quizzes: {c3}")
    print(f"Patched assessments: {c4}")


if __name__ == "__main__":
    asyncio.run(main())
