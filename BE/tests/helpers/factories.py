"""Test data factories using Faker."""

from faker import Faker

fake = Faker()


def register_payload(
    email: str | None = None,
    password: str = "TestPass1!",
    full_name: str = "Nguyen Van Test",
) -> dict:
    return {
        "full_name": full_name,
        "email": email or fake.unique.email(),
        "password": password,
    }


def login_payload(email: str, password: str = "TestPass1!", remember_me: bool = False) -> dict:
    return {"email": email, "password": password, "remember_me": remember_me}


def assessment_generate_payload() -> dict:
    return {
        "category": "Programming",
        "subject": "Python",
        "level": "Beginner",
        "focus_areas": ["syntax"],
    }
