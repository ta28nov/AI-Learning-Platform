from pathlib import Path

from setuptools import find_packages, setup

BASE_DIR = Path(__file__).parent
README = (BASE_DIR / "README.md").read_text(encoding="utf-8")


def load_requirements() -> list[str]:
    requirements_path = BASE_DIR / "requirements.txt"
    raw_lines = requirements_path.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in raw_lines if line.strip() and not line.strip().startswith("#")]

setup(
    name="belearningai",
    version="0.1.0",
    description="Skeleton backend FastAPI ",
    long_description=README,
    long_description_content_type="text/markdown",
    author="AI Agent",
    python_requires=">=3.11",
    packages=find_packages(exclude=("tests", "tests.*")),
    include_package_data=True,
    install_requires=load_requirements(),
    extras_require={
        "dev": ["pytest", "pytest-asyncio", "coverage", "black", "isort", "mypy"],
    },
)
