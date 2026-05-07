"""
init_data.py - Rebuilt seed pipeline (x4 profile, full reset)
==============================================================
- Seed quy mo lon, day du quan he va field quan trong theo models/schemas.
- Chay theo stage ro rang + deterministic randomness.
- Co validation integrity sau khi seed.
"""

import asyncio
import random
import sys
import os
import uuid
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple, Any

from faker import Faker
from passlib.context import CryptContext

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import get_settings
from app.database import init_database
from models.models import (
    User,
    RefreshToken,
    PasswordResetTokenDocument,
    Course,
    Module,
    Lesson,
    EmbeddedModule,
    EmbeddedLesson,
    Enrollment,
    Progress,
    LessonProgressItem,
    Quiz,
    QuizAttempt,
    AssessmentSession,
    Conversation,
    Class,
    Recommendation,
)


fake = Faker("vi_VN")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@dataclass
class SeedConfig:
    seed: int = 20260507
    admins: int = 10
    instructors: int = 40
    students: int = 360
    public_courses: int = 70
    personal_courses: int = 80
    public_modules_per_course: int = 6
    public_lessons_per_module: int = 6
    personal_modules_per_course: int = 4
    personal_lessons_per_module: int = 5
    classes: int = 90


def now() -> datetime:
    return datetime.now(timezone.utc)


def past(days_min: int = 1, days_max: int = 120) -> datetime:
    return now() - timedelta(days=random.randint(days_min, days_max), hours=random.randint(0, 23))


def future(days_min: int = 1, days_max: int = 60) -> datetime:
    return now() + timedelta(days=random.randint(days_min, days_max))


def gid() -> str:
    return str(uuid.uuid4())


def hp(password: str) -> str:
    return pwd_context.hash(password)


def sample_weighted(values: List[Tuple[str, float]]) -> str:
    keys = [k for k, _ in values]
    weights = [w for _, w in values]
    return random.choices(keys, weights=weights, k=1)[0]


def mk_resource(title: str, rtype: str) -> dict:
    return {
        "id": gid(),
        "title": title,
        "type": rtype,
        "url": f"https://example.com/resources/{gid()}",
        "size_mb": round(random.uniform(0.2, 25.0), 2),
        "description": fake.sentence(nb_words=12),
    }


def mk_course_outcome() -> dict:
    return {
        "description": fake.sentence(nb_words=10),
        "skill_tag": fake.slug().replace("-", "_"),
    }


def mk_module_outcome() -> dict:
    return {
        "id": gid(),
        "outcome": fake.sentence(nb_words=10),
        "skill_tag": fake.slug().replace("-", "_"),
        "is_mandatory": random.choice([True, True, False]),
    }


def mk_quiz_question(order: int) -> dict:
    qtype = sample_weighted([
        ("multiple_choice", 0.7),
        ("fill_in_blank", 0.2),
        ("true_false", 0.1),
    ])
    if qtype == "multiple_choice":
        options = [fake.sentence(nb_words=4) for _ in range(4)]
        correct = str(random.randint(0, 3))
    elif qtype == "true_false":
        options = ["True", "False"]
        correct = random.choice(["True", "False"])
    else:
        options = None
        correct = fake.word()
    points = random.randint(1, 3)
    return {
        "id": gid(),
        "type": qtype,
        "question_text": fake.sentence(nb_words=15),
        "options": options,
        "correct_answer": correct,
        "explanation": fake.sentence(nb_words=14),
        "points": points,
        "is_mandatory": random.choice([True, False]),
        "order": order,
    }


def mk_assessment_question(difficulty: str) -> dict:
    qtype = random.choice(["multiple_choice", "fill_in_blank", "drag_and_drop"])
    options = [fake.word() for _ in range(4)] if qtype == "multiple_choice" else None
    points = {"easy": 1, "medium": 2, "hard": 3}[difficulty]
    return {
        "question_id": gid(),
        "question_text": fake.sentence(nb_words=14),
        "question_type": qtype,
        "difficulty": difficulty,
        "skill_tag": fake.slug().replace("-", "_"),
        "points": points,
        "options": options,
        "correct_answer_hint": fake.sentence(nb_words=6),
    }


def profile_header(title: str):
    print(f"\n--- {title} ---")


async def drop_all_collections():
    profile_header("FULL RESET COLLECTIONS")
    await RefreshToken.delete_all()
    await PasswordResetTokenDocument.delete_all()
    await QuizAttempt.delete_all()
    await Quiz.delete_all()
    await Progress.delete_all()
    await Enrollment.delete_all()
    await AssessmentSession.delete_all()
    await Recommendation.delete_all()
    await Conversation.delete_all()
    await Class.delete_all()
    await Lesson.delete_all()
    await Module.delete_all()
    await Course.delete_all()
    await User.delete_all()
    print("Reset done.")


async def seed_users(cfg: SeedConfig) -> Dict[str, List[str]]:
    profile_header("SEED USERS")
    users: List[User] = []
    role_ids = {"admin": [], "instructor": [], "student": []}

    for i in range(cfg.admins):
        uid = gid()
        user = User(
            id=uid,
            full_name=f"Admin {fake.name()}",
            email=f"admin{i+1}@ailearning.vn",
            hashed_password=hp("Admin@123456"),
            role="admin",
            status=random.choice(["active", "active", "inactive"]),
            avatar_url=fake.image_url(),
            bio=fake.text(max_nb_chars=180),
            contact_info=fake.phone_number(),
            learning_preferences=random.sample(["Programming", "Data Science", "Business", "Languages", "Math"], k=2),
            email_verified=True,
            phone_verified=random.choice([True, False]),
            created_at=past(120, 300),
            updated_at=past(5, 20),
            last_login_at=past(0, 5),
        )
        users.append(user)
        role_ids["admin"].append(uid)

    for i in range(cfg.instructors):
        uid = gid()
        user = User(
            id=uid,
            full_name=fake.name(),
            email=f"instructor{i+1}@ailearning.vn",
            hashed_password=hp("Instructor@123"),
            role="instructor",
            status=sample_weighted([("active", 0.8), ("inactive", 0.15), ("banned", 0.03), ("suspended", 0.02)]),
            avatar_url=fake.image_url(),
            bio=fake.text(max_nb_chars=260),
            contact_info=fake.phone_number(),
            learning_preferences=random.sample(["Programming", "Data Science", "Business", "Languages", "Math"], k=3),
            email_verified=random.choice([True, True, False]),
            phone_verified=random.choice([True, False]),
            created_by=random.choice(role_ids["admin"]),
            created_at=past(90, 220),
            updated_at=past(1, 20),
            last_login_at=past(0, 15),
        )
        users.append(user)
        role_ids["instructor"].append(uid)

    for i in range(cfg.students):
        uid = gid()
        user = User(
            id=uid,
            full_name=fake.name(),
            email=f"student{i+1}@gmail.com",
            hashed_password=hp("Student@123"),
            role="student",
            status=sample_weighted([("active", 0.82), ("inactive", 0.11), ("banned", 0.04), ("suspended", 0.03)]),
            avatar_url=fake.image_url(),
            bio=fake.text(max_nb_chars=220),
            contact_info=fake.phone_number(),
            learning_preferences=random.sample(["Programming", "Data Science", "Business", "Languages", "Math"], k=random.randint(1, 3)),
            email_verified=random.choice([True, True, False]),
            phone_verified=random.choice([True, False]),
            created_by=random.choice(role_ids["admin"] + role_ids["instructor"]),
            created_at=past(30, 220),
            updated_at=past(1, 20),
            last_login_at=past(0, 30),
        )
        users.append(user)
        role_ids["student"].append(uid)

    await User.insert_many(users)
    print(f"Users seeded: {len(users)}")
    return role_ids


def build_course_blueprint(idx: int, owner_type: str) -> Dict[str, str]:
    categories = ["Programming", "Data Science", "Business", "Languages", "Math", "Marketing", "Engineering"]
    levels = ["Beginner", "Intermediate", "Advanced"]
    return {
        "title": f"{random.choice(['Master', 'Complete', 'Bootcamp', 'Foundations'])} {random.choice(categories)} {idx+1}",
        "description": fake.text(max_nb_chars=420),
        "category": random.choice(categories),
        "level": random.choice(levels),
        "language": random.choice(["vi", "en"]),
        "owner_type": owner_type,
    }


async def seed_courses_modules_lessons(cfg: SeedConfig, role_ids: Dict[str, List[str]]) -> Dict[str, Any]:
    profile_header("SEED COURSES/MODULES/LESSONS")
    courses: List[Course] = []
    modules: List[Module] = []
    lessons: List[Lesson] = []
    course_map = {"public": [], "personal": []}

    # Public courses
    for i in range(cfg.public_courses):
        cid = gid()
        instructor_id = random.choice(role_ids["instructor"])
        owner_id = random.choice(role_ids["admin"] + role_ids["instructor"])
        bp = build_course_blueprint(i, "admin" if owner_id in role_ids["admin"] else "instructor")
        module_embeds: List[EmbeddedModule] = []
        total_lessons = 0
        total_duration = 0

        for m in range(cfg.public_modules_per_course):
            mid = gid()
            module_lessons_embed: List[EmbeddedLesson] = []
            module_duration = 0
            for l in range(cfg.public_lessons_per_module):
                lid = gid()
                mins = random.randint(18, 65)
                ctype = random.choice(["text", "video", "mixed", "code"])
                has_video = ctype in ["video", "mixed"]
                lesson = Lesson(
                    id=lid,
                    module_id=mid,
                    course_id=cid,
                    title=f"Lesson {m+1}.{l+1} - {fake.sentence(nb_words=5)}",
                    description=fake.sentence(nb_words=14),
                    order=l + 1,
                    content=f"<h2>{fake.sentence(nb_words=6)}</h2><p>{fake.paragraph(nb_sentences=4)}</p>",
                    content_type=ctype,
                    duration_minutes=mins,
                    video_url=f"https://youtube.com/watch?v={gid()[:11]}" if has_video else None,
                    audio_url=f"https://cdn.example.com/audio/{gid()}.mp3" if ctype == "audio" else None,
                    learning_objectives=[fake.sentence(nb_words=6) for _ in range(random.randint(2, 4))],
                    resources=[
                        mk_resource("Slide pack", "slide"),
                        mk_resource("Practice code", "code"),
                        mk_resource("Reference", "link"),
                    ],
                    quiz_id=None,
                    is_published=True,
                    created_at=past(30, 180),
                    updated_at=past(1, 20),
                )
                lessons.append(lesson)
                module_duration += mins
                total_lessons += 1
                total_duration += mins
                module_lessons_embed.append(
                    EmbeddedLesson(
                        id=lid,
                        title=lesson.title,
                        description=lesson.description,
                        order=lesson.order,
                        content=lesson.content,
                        content_type=lesson.content_type,
                        duration_minutes=lesson.duration_minutes,
                        video_url=lesson.video_url,
                        audio_url=lesson.audio_url,
                        resources=lesson.resources,
                        learning_objectives=lesson.learning_objectives,
                        quiz_id=None,
                        is_published=True,
                        created_at=lesson.created_at,
                        updated_at=lesson.updated_at,
                    )
                )

            module = Module(
                id=mid,
                course_id=cid,
                title=f"Module {m+1} - {fake.sentence(nb_words=4)}",
                description=fake.text(max_nb_chars=180),
                order=m + 1,
                difficulty=random.choice(["Basic", "Intermediate", "Advanced"]),
                estimated_hours=round(module_duration / 60.0, 1),
                learning_outcomes=[mk_module_outcome() for _ in range(random.randint(3, 5))],
                resources=[mk_resource("Module Notes", "pdf"), mk_resource("Links", "link")],
                prerequisites=[module_embeds[m - 1].id] if m > 0 else [],
                total_lessons=cfg.public_lessons_per_module,
                total_duration_minutes=module_duration,
                created_at=past(20, 120),
                updated_at=past(1, 10),
            )
            modules.append(module)
            module_embeds.append(
                EmbeddedModule(
                    id=mid,
                    title=module.title,
                    description=module.description,
                    order=module.order,
                    difficulty=module.difficulty,
                    estimated_hours=module.estimated_hours,
                    learning_outcomes=module.learning_outcomes,
                    prerequisites=module.prerequisites,
                    resources=module.resources,
                    lessons=module_lessons_embed,
                    total_lessons=module.total_lessons,
                    total_duration_minutes=module.total_duration_minutes,
                    created_at=module.created_at,
                    updated_at=module.updated_at,
                )
            )

        course = Course(
            id=cid,
            title=bp["title"],
            description=bp["description"],
            category=bp["category"],
            level=bp["level"],
            thumbnail_url=fake.image_url(),
            preview_video_url=f"https://youtube.com/watch?v={gid()[:11]}",
            language=bp["language"],
            status=sample_weighted([("published", 0.8), ("draft", 0.15), ("archived", 0.05)]),
            owner_id=owner_id,
            owner_type=bp["owner_type"],
            instructor_id=instructor_id,
            instructor_name=f"Instructor {instructor_id[:6]}",
            instructor_avatar=fake.image_url(),
            instructor_bio=fake.text(max_nb_chars=200),
            course_type="public",
            learning_outcomes=[mk_course_outcome() for _ in range(random.randint(4, 7))],
            prerequisites=[fake.sentence(nb_words=4) for _ in range(random.randint(0, 3))],
            modules=module_embeds,
            total_duration_minutes=total_duration,
            total_modules=len(module_embeds),
            total_lessons=total_lessons,
            enrollment_count=0,
            avg_rating=round(random.uniform(3.5, 5.0), 1),
            created_at=past(40, 220),
            updated_at=past(1, 20),
        )
        courses.append(course)
        course_map["public"].append(cid)

    # Personal courses
    selected_students = random.sample(role_ids["student"], k=min(cfg.personal_courses, len(role_ids["student"])))
    for i, student_id in enumerate(selected_students):
        cid = gid()
        bp = build_course_blueprint(i, "student")
        module_embeds: List[EmbeddedModule] = []
        total_lessons = 0
        total_duration = 0

        for m in range(cfg.personal_modules_per_course):
            mid = gid()
            module_lessons_embed: List[EmbeddedLesson] = []
            module_duration = 0
            for l in range(cfg.personal_lessons_per_module):
                lid = gid()
                mins = random.randint(15, 45)
                ctype = random.choice(["text", "video", "mixed"])
                lesson = Lesson(
                    id=lid,
                    module_id=mid,
                    course_id=cid,
                    title=f"Personal Lesson {m+1}.{l+1} - {fake.word()}",
                    description=fake.sentence(nb_words=10),
                    order=l + 1,
                    content=f"<h3>{fake.word().title()}</h3><p>{fake.paragraph(nb_sentences=3)}</p>",
                    content_type=ctype,
                    duration_minutes=mins,
                    video_url=f"https://youtube.com/watch?v={gid()[:11]}" if ctype in ["video", "mixed"] else None,
                    learning_objectives=[fake.sentence(nb_words=5) for _ in range(random.randint(1, 3))],
                    resources=[mk_resource("Personal notes", "pdf")],
                    quiz_id=None,
                    is_published=True,
                    created_at=past(20, 120),
                    updated_at=past(1, 10),
                )
                lessons.append(lesson)
                module_duration += mins
                total_lessons += 1
                total_duration += mins
                module_lessons_embed.append(
                    EmbeddedLesson(
                        id=lid,
                        title=lesson.title,
                        description=lesson.description,
                        order=lesson.order,
                        content=lesson.content,
                        content_type=lesson.content_type,
                        duration_minutes=lesson.duration_minutes,
                        video_url=lesson.video_url,
                        resources=lesson.resources,
                        learning_objectives=lesson.learning_objectives,
                        quiz_id=None,
                        is_published=True,
                        created_at=lesson.created_at,
                        updated_at=lesson.updated_at,
                    )
                )

            module = Module(
                id=mid,
                course_id=cid,
                title=f"Personal Module {m+1}",
                description=fake.sentence(nb_words=12),
                order=m + 1,
                difficulty=random.choice(["Basic", "Intermediate", "Advanced"]),
                estimated_hours=round(module_duration / 60.0, 1),
                learning_outcomes=[mk_module_outcome() for _ in range(3)],
                resources=[mk_resource("Ref", "link")],
                prerequisites=[module_embeds[m - 1].id] if m > 0 else [],
                total_lessons=cfg.personal_lessons_per_module,
                total_duration_minutes=module_duration,
                created_at=past(10, 70),
                updated_at=past(1, 7),
            )
            modules.append(module)
            module_embeds.append(
                EmbeddedModule(
                    id=mid,
                    title=module.title,
                    description=module.description,
                    order=module.order,
                    difficulty=module.difficulty,
                    estimated_hours=module.estimated_hours,
                    learning_outcomes=module.learning_outcomes,
                    prerequisites=module.prerequisites,
                    resources=module.resources,
                    lessons=module_lessons_embed,
                    total_lessons=module.total_lessons,
                    total_duration_minutes=module.total_duration_minutes,
                    created_at=module.created_at,
                    updated_at=module.updated_at,
                )
            )

        course = Course(
            id=cid,
            title=f"Personal - {bp['title']}",
            description=bp["description"],
            category=bp["category"],
            level=bp["level"],
            language=bp["language"],
            status=sample_weighted([("published", 0.45), ("draft", 0.5), ("archived", 0.05)]),
            owner_id=student_id,
            owner_type="student",
            instructor_name=f"Student Owner {student_id[:6]}",
            instructor_avatar=fake.image_url(),
            instructor_bio=fake.sentence(nb_words=14),
            course_type="personal",
            learning_outcomes=[mk_course_outcome() for _ in range(3)],
            prerequisites=[],
            modules=module_embeds,
            total_duration_minutes=total_duration,
            total_modules=len(module_embeds),
            total_lessons=total_lessons,
            enrollment_count=0,
            avg_rating=None,
            created_at=past(8, 100),
            updated_at=past(1, 6),
        )
        courses.append(course)
        course_map["personal"].append(cid)

    await Course.insert_many(courses)
    await Module.insert_many(modules)
    await Lesson.insert_many(lessons)
    print(f"Courses seeded: {len(courses)} (public={len(course_map['public'])}, personal={len(course_map['personal'])})")
    print(f"Modules seeded: {len(modules)} | Lessons seeded: {len(lessons)}")
    return {"course_map": course_map}


async def seed_classes(cfg: SeedConfig, role_ids: Dict[str, List[str]], course_map: Dict[str, List[str]]) -> List[str]:
    profile_header("SEED CLASSES")
    classes: List[Class] = []
    public_courses = course_map["public"]
    for i in range(cfg.classes):
        start = past(0, 35)
        end = start + timedelta(days=random.randint(45, 120))
        c = Class(
            id=gid(),
            name=f"Class {i+1} - {fake.word().title()}",
            description=fake.text(max_nb_chars=180),
            course_id=random.choice(public_courses),
            instructor_id=random.choice(role_ids["instructor"]),
            max_students=random.randint(45, 120),
            start_date=start,
            end_date=end,
            status=sample_weighted([("preparing", 0.25), ("active", 0.6), ("completed", 0.15)]),
            student_ids=[],
            created_at=past(3, 90),
            updated_at=past(1, 7),
        )
        classes.append(c)

    await Class.insert_many(classes)
    print(f"Classes seeded: {len(classes)}")
    return [c.id for c in classes]


async def seed_enrollments_progress(cfg: SeedConfig, role_ids: Dict[str, List[str]], course_map: Dict[str, List[str]]) -> Dict[str, Any]:
    profile_header("SEED ENROLLMENTS/PROGRESS")
    public_course_ids = course_map["public"]
    course_docs = await Course.find({"_id": {"$in": public_course_ids}}).to_list()
    modules = await Module.find({"course_id": {"$in": public_course_ids}}).to_list()
    lessons = await Lesson.find({"course_id": {"$in": public_course_ids}}).to_list()

    module_by_course: Dict[str, List[Module]] = {}
    lessons_by_module: Dict[str, List[Lesson]] = {}
    for m in modules:
        module_by_course.setdefault(m.course_id, []).append(m)
    for l in lessons:
        lessons_by_module.setdefault(l.module_id, []).append(l)

    enrollments: List[Enrollment] = []
    progresses: List[Progress] = []
    enrollment_by_course: Dict[str, List[Enrollment]] = {}
    all_enrollment_ids: List[str] = []

    for sid in role_ids["student"]:
        picked_courses = random.sample(public_course_ids, k=min(random.randint(12, 22), len(public_course_ids)))
        for cid in picked_courses:
            eid = gid()
            status = sample_weighted([("active", 0.68), ("completed", 0.22), ("cancelled", 0.10)])
            enrolled_at = past(5, 150)
            progress_percent = 0.0
            if status == "completed":
                progress_percent = 100.0
            elif status == "active":
                progress_percent = round(random.uniform(5, 95), 1)
            else:
                progress_percent = round(random.uniform(0, 70), 1)

            course_modules = sorted(module_by_course.get(cid, []), key=lambda x: x.order)
            all_lessons: List[Lesson] = []
            for m in course_modules:
                all_lessons.extend(sorted(lessons_by_module.get(m.id, []), key=lambda x: x.order))
            total_lessons_count = len(all_lessons)
            completed_count = int((progress_percent / 100.0) * total_lessons_count) if total_lessons_count else 0
            completed_lessons = [ls.id for ls in all_lessons[:completed_count]]

            completed_modules: List[str] = []
            for m in course_modules:
                m_lessons = sorted(lessons_by_module.get(m.id, []), key=lambda x: x.order)
                if m_lessons and all(ls.id in completed_lessons for ls in m_lessons):
                    completed_modules.append(m.id)

            enrollment = Enrollment(
                id=eid,
                user_id=sid,
                course_id=cid,
                status=status,
                progress_percent=progress_percent,
                completion_rate=progress_percent,
                completed_lessons=completed_lessons,
                completed_modules=completed_modules,
                avg_quiz_score=round(random.uniform(45, 98), 1) if completed_count > 0 else None,
                total_time_spent_minutes=random.randint(40, 2400) if completed_count > 0 else 0,
                enrolled_at=enrolled_at,
                last_accessed_at=past(0, 12) if status != "cancelled" else None,
                completed_at=(enrolled_at + timedelta(days=random.randint(20, 110))) if status == "completed" else None,
            )
            enrollments.append(enrollment)
            enrollment_by_course.setdefault(cid, []).append(enrollment)
            all_enrollment_ids.append(eid)

            if status in ["active", "completed"]:
                lp_items: List[LessonProgressItem] = []
                for idx, ls in enumerate(all_lessons):
                    is_done = idx < completed_count
                    lp_items.append(
                        LessonProgressItem(
                            lesson_id=ls.id,
                            module_id=ls.module_id,
                            lesson_title=ls.title,
                            status="completed" if is_done else ("in-progress" if idx == completed_count and status == "active" else "not-started"),
                            completion_date=past(1, 80) if is_done else None,
                            time_spent_minutes=random.randint(10, max(ls.duration_minutes, 15)) if is_done else 0,
                            video_progress_seconds=random.randint(60, ls.duration_minutes * 60) if is_done and ls.video_url else 0,
                        )
                    )

                progress = Progress(
                    id=gid(),
                    user_id=sid,
                    course_id=cid,
                    enrollment_id=eid,
                    overall_progress_percent=progress_percent,
                    completed_lessons_count=completed_count,
                    total_lessons_count=total_lessons_count,
                    lessons_progress=lp_items,
                    total_time_spent_minutes=enrollment.total_time_spent_minutes,
                    estimated_hours_remaining=max(0.0, round(((total_lessons_count - completed_count) * 0.75), 1)),
                    study_streak_days=random.randint(0, 42),
                    avg_quiz_score=enrollment.avg_quiz_score or 0.0,
                    last_accessed_at=enrollment.last_accessed_at,
                    created_at=enrolled_at,
                    updated_at=past(0, 7),
                )
                progresses.append(progress)

    await Enrollment.insert_many(enrollments)
    if progresses:
        await Progress.insert_many(progresses)

    for c in course_docs:
        c.enrollment_count = len(enrollment_by_course.get(c.id, []))
        c.updated_at = now()
        await c.save()

    print(f"Enrollments seeded: {len(enrollments)}")
    print(f"Progress docs seeded: {len(progresses)}")
    return {"enrollment_by_course": enrollment_by_course, "all_enrollment_ids": all_enrollment_ids}


async def seed_quizzes_attempts(cfg: SeedConfig, role_ids: Dict[str, List[str]]) -> Dict[str, List[str]]:
    profile_header("SEED QUIZZES/ATTEMPTS")
    lessons = await Lesson.find().to_list()
    enrollments = await Enrollment.find().to_list()
    enroll_by_user_course = {(e.user_id, e.course_id): e for e in enrollments}
    quizzes: List[Quiz] = []
    attempts: List[QuizAttempt] = []
    quiz_ids: List[str] = []

    for ls in lessons:
        create_quiz = random.random() < (0.72 if ls.course_id else 0.5)
        if not create_quiz:
            continue
        qid = gid()
        question_count = random.randint(5, 10)
        qs = [mk_quiz_question(i + 1) for i in range(question_count)]
        total_points = sum(q["points"] for q in qs)
        mandatory_count = sum(1 for q in qs if q["is_mandatory"])
        quiz = Quiz(
            id=qid,
            lesson_id=ls.id,
            course_id=ls.course_id,
            module_id=ls.module_id,
            title=f"Quiz - {ls.title}",
            description=fake.sentence(nb_words=18),
            quiz_type=random.choice(["review", "practice", "final_check"]),
            time_limit_minutes=random.choice([10, 15, 20, 25, None]),
            passing_score=random.choice([60.0, 70.0, 75.0]),
            max_attempts=random.choice([2, 3, 4]),
            deadline=future(20, 90),
            is_draft=random.choice([False, False, False, True]),
            questions=qs,
            question_count=question_count,
            total_points=total_points,
            mandatory_question_count=mandatory_count,
            created_by=random.choice(role_ids["instructor"] + role_ids["admin"]),
            created_at=past(5, 120),
            updated_at=past(1, 10),
        )
        quizzes.append(quiz)
        quiz_ids.append(qid)

    if quizzes:
        await Quiz.insert_many(quizzes)

    # map lesson->quiz for lesson update
    quiz_by_lesson = {q.lesson_id: q for q in quizzes}
    for ls in lessons:
        if ls.id in quiz_by_lesson:
            ls.quiz_id = quiz_by_lesson[ls.id].id
            ls.updated_at = now()
            await ls.save()

    # Attempts
    for q in quizzes:
        eligible_user_ids = []
        for e in enrollments:
            if e.course_id == q.course_id and e.status in ["active", "completed"]:
                eligible_user_ids.append(e.user_id)
        if not eligible_user_ids:
            continue
        sampled = random.sample(eligible_user_ids, k=min(len(eligible_user_ids), random.randint(8, 24)))
        for uid in sampled:
            attempts_count = random.choice([1, 1, 2, 2, 3])
            for n in range(attempts_count):
                score = round(random.uniform(35, 100), 1)
                passed = score >= q.passing_score
                started = past(1, 90)
                submitted = started + timedelta(minutes=random.randint(4, 45))
                answers = []
                correct = 0
                mandatory_correct = 0
                for qq in q.questions:
                    is_correct = random.random() < (0.65 if n == 0 else 0.78)
                    if is_correct:
                        correct += 1
                    if qq.get("is_mandatory") and is_correct:
                        mandatory_correct += 1
                    answers.append({
                        "question_id": qq["id"],
                        "question_content": qq["question_text"],
                        "student_answer": qq.get("correct_answer") if is_correct else fake.word(),
                        "correct_answer": qq.get("correct_answer"),
                        "is_correct": is_correct,
                        "is_mandatory": qq.get("is_mandatory", False),
                        "score": qq["points"] if is_correct else 0,
                        "explanation": qq.get("explanation", ""),
                        "related_lesson_link": f"/dashboard/courses/{q.course_id}/lessons/{q.lesson_id}",
                    })

                attempt = QuizAttempt(
                    id=gid(),
                    quiz_id=q.id,
                    user_id=uid,
                    answers=answers,
                    score=score,
                    status="Pass" if passed else "Fail",
                    passed=passed,
                    attempt_number=n + 1,
                    correct_answers=correct,
                    total_questions=q.question_count,
                    mandatory_correct=mandatory_correct,
                    mandatory_total=q.mandatory_question_count,
                    mandatory_passed=mandatory_correct >= max(1, int(q.mandatory_question_count * 0.6)) if q.mandatory_question_count else True,
                    can_retake=(n + 1) < q.max_attempts,
                    started_at=started,
                    submitted_at=submitted,
                    time_spent_seconds=int((submitted - started).total_seconds()),
                )
                attempts.append(attempt)

    if attempts:
        await QuizAttempt.insert_many(attempts)

    print(f"Quizzes seeded: {len(quizzes)}")
    print(f"Quiz attempts seeded: {len(attempts)}")
    return {"quiz_ids": quiz_ids}


async def seed_assessments_recommendations(role_ids: Dict[str, List[str]], course_map: Dict[str, List[str]]) -> Dict[str, str]:
    profile_header("SEED ASSESSMENTS/RECOMMENDATIONS")
    sessions: List[AssessmentSession] = []
    latest_eval_session_by_user: Dict[str, str] = {}
    categories = ["Programming", "Data Science", "Business", "Languages", "Math"]
    level_cfg = {
        "Beginner": (15, 15),
        "Intermediate": (25, 22),
        "Advanced": (35, 30),
    }

    for sid in role_ids["student"]:
        for _ in range(random.randint(2, 4)):
            level = random.choice(["Beginner", "Intermediate", "Advanced"])
            total_questions, time_limit = level_cfg[level]
            status = sample_weighted([("pending", 0.15), ("in_progress", 0.2), ("submitted", 0.15), ("evaluated", 0.5)])
            created = past(1, 100)
            expires = created + timedelta(minutes=60)
            questions = []
            for i in range(total_questions):
                if i < total_questions * 0.2:
                    diff = "easy"
                elif i < total_questions * 0.8:
                    diff = "medium"
                else:
                    diff = "hard"
                questions.append(mk_assessment_question(diff))

            answers = []
            overall = None
            proficiency = None
            correct_answers = None
            skill_analysis = None
            knowledge_gaps = []
            ai_feedback = None
            time_analysis = None
            submitted_at = None
            evaluated_at = None

            if status in ["submitted", "evaluated"]:
                submitted_at = created + timedelta(minutes=random.randint(8, time_limit))
                for q in questions:
                    is_correct = random.random() < 0.62
                    answers.append({
                        "question_id": q["question_id"],
                        "answer_content": q["correct_answer_hint"] if is_correct else fake.word(),
                        "selected_option": random.randint(0, 3) if q["question_type"] == "multiple_choice" else None,
                        "time_taken_seconds": random.randint(20, 95),
                    })

            if status == "evaluated":
                evaluated_at = submitted_at + timedelta(seconds=random.randint(8, 180))
                correct_answers = sum(1 for _ in range(total_questions) if random.random() < 0.64)
                overall = round((correct_answers / total_questions) * 100, 1)
                proficiency = "Advanced" if overall >= 80 else ("Intermediate" if overall >= 60 else "Beginner")
                skill_analysis = [
                    {
                        "skill_tag": f"skill_{i+1}",
                        "questions_count": random.randint(3, 8),
                        "correct_count": random.randint(1, 6),
                        "proficiency_percentage": round(random.uniform(30, 95), 1),
                        "strength_level": random.choice(["Strong", "Average", "Weak"]),
                        "detailed_feedback": fake.sentence(nb_words=18),
                    } for i in range(random.randint(3, 6))
                ]
                knowledge_gaps = [
                    {
                        "gap_area": fake.word(),
                        "description": fake.sentence(nb_words=16),
                        "importance": random.choice(["High", "Medium", "Low"]),
                        "suggested_action": fake.sentence(nb_words=14),
                    } for _ in range(random.randint(1, 4))
                ]
                ai_feedback = fake.paragraph(nb_sentences=3)
                total_time_seconds = sum(a["time_taken_seconds"] for a in answers) if answers else random.randint(400, 1800)
                time_analysis = {
                    "total_time_seconds": total_time_seconds,
                    "average_time_per_question": round(total_time_seconds / total_questions, 2),
                    "fastest_question_time": random.randint(8, 25),
                    "slowest_question_time": random.randint(80, 150),
                }

            session = AssessmentSession(
                id=gid(),
                user_id=sid,
                category=random.choice(categories),
                subject=fake.word().title(),
                level=level,
                focus_areas=[fake.word() for _ in range(random.randint(1, 3))],
                total_questions=total_questions,
                time_limit_minutes=time_limit,
                questions=questions,
                status=status,
                answers=answers,
                overall_score=overall,
                proficiency_level=proficiency,
                correct_answers=correct_answers,
                skill_analysis=skill_analysis,
                knowledge_gaps=knowledge_gaps,
                ai_feedback=ai_feedback,
                time_analysis=time_analysis,
                created_at=created,
                expires_at=expires,
                submitted_at=submitted_at,
                evaluated_at=evaluated_at,
            )
            sessions.append(session)
            if status == "evaluated":
                latest_eval_session_by_user[sid] = session.id

    if sessions:
        await AssessmentSession.insert_many(sessions)
    print(f"Assessment sessions seeded: {len(sessions)}")

    recommendations: List[Recommendation] = []
    all_courses = await Course.find({"status": {"$in": ["published", "draft"]}}).to_list()
    for sid in role_ids["student"]:
        session_id = latest_eval_session_by_user.get(sid)
        picked = random.sample(all_courses, k=min(len(all_courses), random.randint(4, 7)))
        recs = []
        order = []
        total_est_h = 0.0
        for rank, c in enumerate(picked, start=1):
            est_days = random.randint(7, 60)
            total_est_h += round((c.total_duration_minutes or 180) / 60.0, 1)
            recs.append({
                "course_id": c.id,
                "title": c.title,
                "description": c.description,
                "category": c.category,
                "level": c.level,
                "thumbnail_url": c.thumbnail_url,
                "priority_rank": rank,
                "relevance_score": round(random.uniform(60, 98), 1),
                "reason": fake.sentence(nb_words=16),
                "addresses_gaps": [fake.word() for _ in range(random.randint(1, 3))],
                "estimated_completion_days": est_days,
            })
            order.append({
                "step": rank,
                "course_id": c.id,
                "focus_modules": [f"Module {i}" for i in range(1, random.randint(2, 4))],
                "why_this_order": fake.sentence(nb_words=14),
            })

        recommendation = Recommendation(
            id=gid(),
            user_id=sid,
            source="assessment" if session_id else random.choice(["learning_history", "ai_suggestion"]),
            assessment_session_id=session_id,
            user_proficiency_level=random.choice(["Beginner", "Intermediate", "Advanced"]),
            recommended_courses=recs,
            suggested_learning_order=order,
            practice_exercises=[
                {
                    "skill_tag": fake.slug().replace("-", "_"),
                    "exercise_type": random.choice(["coding", "quiz", "project", "reading"]),
                    "description": fake.sentence(nb_words=12),
                    "difficulty": random.choice(["easy", "medium", "hard"]),
                    "estimated_time_hours": round(random.uniform(0.5, 6.0), 1),
                } for _ in range(random.randint(3, 6))
            ],
            ai_personalized_advice=fake.paragraph(nb_sentences=3),
            total_estimated_hours=round(total_est_h, 1),
            created_at=past(0, 35),
            expires_at=future(15, 120),
        )
        recommendations.append(recommendation)

    if recommendations:
        await Recommendation.insert_many(recommendations)
    print(f"Recommendations seeded: {len(recommendations)}")
    return latest_eval_session_by_user


async def seed_conversations_tokens(role_ids: Dict[str, List[str]], course_map: Dict[str, List[str]]):
    profile_header("SEED CONVERSATIONS/TOKENS")
    conversations: List[Conversation] = []
    refresh_tokens: List[RefreshToken] = []
    reset_tokens: List[PasswordResetTokenDocument] = []
    active_users = await User.find({"status": "active"}).to_list()
    public_courses = course_map["public"]

    for sid in role_ids["student"]:
        for _ in range(random.randint(1, 4)):
            cid = random.choice(public_courses)
            msg_count = random.randint(4, 16)
            messages = []
            for i in range(msg_count):
                role = "user" if i % 2 == 0 else "assistant"
                messages.append({
                    "id": gid(),
                    "role": role,
                    "content": fake.sentence(nb_words=18) if role == "user" else fake.paragraph(nb_sentences=2),
                    "created_at": past(0, 40),
                })
            conv = Conversation(
                id=gid(),
                user_id=sid,
                course_id=cid,
                title=f"Discussion {fake.word().title()}",
                summary=fake.sentence(nb_words=18),
                course_title=f"Course {cid[:8]}",
                messages=messages,
                total_messages=len(messages),
                last_message_at=messages[-1]["created_at"],
                created_at=past(1, 60),
                updated_at=past(0, 15),
            )
            conversations.append(conv)

    for u in active_users:
        created = past(0, 10)
        refresh_tokens.append(
            RefreshToken(
                id=gid(),
                user_id=u.id,
                token=secrets.token_urlsafe(64),
                expires_at=created + timedelta(days=7),
                created_at=created,
            )
        )

    # seed một phần password reset tokens để phủ collection
    sample_users = random.sample(active_users, k=min(len(active_users), 14))
    for u in sample_users:
        created = past(0, 20)
        reset_tokens.append(
            PasswordResetTokenDocument(
                id=gid(),
                user_id=u.id,
                token=secrets.token_urlsafe(32),
                expires_at=created + timedelta(hours=24),
                used=random.choice([False, False, True]),
                created_at=created,
            )
        )

    if conversations:
        await Conversation.insert_many(conversations)
    if refresh_tokens:
        await RefreshToken.insert_many(refresh_tokens)
    if reset_tokens:
        await PasswordResetTokenDocument.insert_many(reset_tokens)

    print(f"Conversations seeded: {len(conversations)}")
    print(f"Refresh tokens seeded: {len(refresh_tokens)}")
    print(f"Password reset tokens seeded: {len(reset_tokens)}")


async def sync_classes_with_enrollments(class_ids: List[str]):
    profile_header("SYNC CLASS MEMBERSHIPS")
    classes = await Class.find({"_id": {"$in": class_ids}}).to_list()
    for c in classes:
        eligible = await Enrollment.find({
            "course_id": c.course_id,
            "status": {"$in": ["active", "completed"]},
        }).to_list()
        random.shuffle(eligible)
        selected = [e.user_id for e in eligible[: min(len(eligible), random.randint(20, min(c.max_students, 95)))]]
        c.student_ids = selected
        c.updated_at = now()
        await c.save()
    print(f"Classes synced: {len(classes)}")


async def validate_integrity() -> Dict[str, int]:
    profile_header("VALIDATE INTEGRITY")
    errors = 0

    users = await User.find().to_list()
    user_ids = {u.id for u in users}
    courses = await Course.find().to_list()
    course_ids = {c.id for c in courses}
    modules = await Module.find().to_list()
    module_ids = {m.id for m in modules}
    lessons = await Lesson.find().to_list()
    lesson_ids = {l.id for l in lessons}
    enrollments = await Enrollment.find().to_list()
    enrollment_ids = {e.id for e in enrollments}
    quizzes = await Quiz.find().to_list()
    quiz_ids = {q.id for q in quizzes}

    for c in courses:
        if c.owner_id not in user_ids:
            errors += 1
        if c.instructor_id and c.instructor_id not in user_ids:
            errors += 1
        if c.total_modules != len(c.modules):
            errors += 1

    for m in modules:
        if m.course_id not in course_ids:
            errors += 1
        for p in m.prerequisites:
            if p and p not in module_ids:
                errors += 1

    for l in lessons:
        if l.module_id not in module_ids:
            errors += 1
        if l.course_id not in course_ids:
            errors += 1
        if l.quiz_id and l.quiz_id not in quiz_ids:
            errors += 1

    for e in enrollments:
        if e.user_id not in user_ids or e.course_id not in course_ids:
            errors += 1
        if not (0.0 <= e.progress_percent <= 100.0):
            errors += 1

    progresses = await Progress.find().to_list()
    for p in progresses:
        if p.user_id not in user_ids or p.course_id not in course_ids or p.enrollment_id not in enrollment_ids:
            errors += 1
        if not (0.0 <= p.overall_progress_percent <= 100.0):
            errors += 1
        for lp in p.lessons_progress:
            if lp.lesson_id not in lesson_ids:
                errors += 1
            if lp.module_id and lp.module_id not in module_ids:
                errors += 1

    classes = await Class.find().to_list()
    for c in classes:
        if c.course_id not in course_ids or c.instructor_id not in user_ids:
            errors += 1
        for sid in c.student_ids:
            if sid not in user_ids:
                errors += 1

    recommendations = await Recommendation.find().to_list()
    for r in recommendations:
        if r.user_id not in user_ids:
            errors += 1
        for rc in r.recommended_courses:
            if rc.get("course_id") not in course_ids:
                errors += 1

    summary = {
        "users": len(users),
        "courses": len(courses),
        "modules": len(modules),
        "lessons": len(lessons),
        "enrollments": len(enrollments),
        "progress": len(progresses),
        "quizzes": len(quizzes),
        "quiz_attempts": await QuizAttempt.find().count(),
        "assessments": await AssessmentSession.find().count(),
        "recommendations": len(recommendations),
        "conversations": await Conversation.find().count(),
        "classes": len(classes),
        "refresh_tokens": await RefreshToken.find().count(),
        "password_reset_tokens": await PasswordResetTokenDocument.find().count(),
        "integrity_errors": errors,
    }
    for k, v in summary.items():
        print(f"{k}: {v}")
    return summary


async def seed_report_accounts():
    print("\nDemo accounts:")
    print("  Admin: admin1@ailearning.vn / Admin@123456")
    print("  Instructor: instructor1@ailearning.vn / Instructor@123")
    print("  Student: student1@gmail.com / Student@123")


async def main():
    cfg = SeedConfig()
    random.seed(cfg.seed)
    fake.seed_instance(cfg.seed)

    print("=" * 72)
    print("AI Learning Platform - Rebuilt Seed Data (x4, Full Reset)")
    print("=" * 72)
    print(f"Seed: {cfg.seed}")

    settings = get_settings()
    await init_database()
    print(f"MongoDB: {settings.mongodb_database}")

    await drop_all_collections()
    role_ids = await seed_users(cfg)
    domain = await seed_courses_modules_lessons(cfg, role_ids)
    class_ids = await seed_classes(cfg, role_ids, domain["course_map"])
    await seed_enrollments_progress(cfg, role_ids, domain["course_map"])
    await sync_classes_with_enrollments(class_ids)
    await seed_quizzes_attempts(cfg, role_ids)
    await seed_assessments_recommendations(role_ids, domain["course_map"])
    await seed_conversations_tokens(role_ids, domain["course_map"])
    summary = await validate_integrity()
    await seed_report_accounts()

    print("\n" + "=" * 72)
    print("SEED COMPLETED")
    print("=" * 72)
    if summary["integrity_errors"] > 0:
        print(f"WARNING: integrity_errors={summary['integrity_errors']}")
    else:
        print("Integrity checks: PASS")


if __name__ == "__main__":
    asyncio.run(main())

