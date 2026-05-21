"""Phase 2b.13–14 — grep audit for orphan APIs + route smoke notes."""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
FE = ROOT / "FE" / "src"
PAGES = FE / "pages"
HOOKS = FE / "hooks"
SERVICES = FE / "services"

# (label, service_method_pattern, pages_hooks_pattern or None)
GAP_CHECKS = [
    (
        "GET /courses/{id}/enrollment-status",
        r"getEnrollmentStatus",
        r"getEnrollmentStatus",
    ),
    (
        "GET .../outcomes (standalone)",
        r"getOutcomes|/outcomes",
        r"getOutcomes|learning_outcomes",
    ),
    (
        "GET .../resources (standalone)",
        r"getResources|/resources",
        r"getResources|module\.resources",
    ),
    (
        "POST .../modules/{mid}/assessments/generate",
        r"generateModuleAssessment",
        r"generateModuleAssessment",
    ),
    (
        "POST /ai/generate-practice",
        r"generatePractice|generate-practice",
        r"generatePractice|generate-practice",
    ),
    (
        "PUT /quizzes/{id}",
        r"updateQuiz",
        r"updateQuiz",
    ),
    (
        "GET /classes/.../students/{sid}",
        r"getStudentDetail",
        r"getStudentDetail",
    ),
    (
        "adminService.updateCourse",
        r"adminService.*updateCourse|updateCourse",
        r"adminService|updateCourse",
    ),
    (
        "adminService.getUserDetail / updateUser",
        r"getUserDetail|updateUser",
        r"getUserDetail|updateUser",
    ),
]


def grep_dir(base: Path, pattern: str) -> list[str]:
    if not base.exists():
        return []
    hits = []
    rx = re.compile(pattern)
    for p in base.rglob("*"):
        if p.suffix not in {".js", ".jsx", ".ts", ".tsx"}:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        if rx.search(text):
            hits.append(str(p.relative_to(ROOT)).replace("\\", "/"))
    return hits


def classify(label: str, svc_hits: list, ui_hits: list) -> dict:
    ui_only = [h for h in ui_hits if "/services/" not in h]
    if label.startswith("GET /classes"):
        gap = "—" if ui_only else "API_NO_UI"
        note = "Wired ClassDetailPage modal (UIUX-022)" if ui_only else "orphan"
    elif "outcomes" in label or "resources" in label:
        gap = "—" if any("ModuleDetailPage" in h for h in ui_only) else "API_NO_UI"
        note = "Embedded in module detail payload" if ui_only else "orphan"
    elif "enrollment-status" in label:
        gap = "API_NO_UI"
        note = "CourseDetail uses enrollment_info from GET /courses/{id}"
    elif "adminService.updateCourse" in label:
        ui_admin = [h for h in ui_only if "/admin/" in h]
        gap = "API_NO_UI" if not ui_admin else "—"
        note = "personalCourseService.updateCourse wired in CourseEditorPage"
    elif "adminService.getUserDetail" in label:
        ui_admin = [h for h in ui_only if "/admin/" in h]
        gap = "API_NO_UI" if not ui_admin else "—"
        note = "Admin list actions only"
    else:
        gap = "API_NO_UI" if not ui_only else "—"
        note = "by design" if gap == "API_NO_UI" else "wired"
    return {
        "check": label,
        "service_hits": len(svc_hits),
        "ui_hits": ui_hits[:5],
        "gap": gap,
        "note": note,
    }


def main():
    results = []
    for label, svc_pat, ui_pat in GAP_CHECKS:
        svc_hits = grep_dir(SERVICES, svc_pat)
        ui_hits = grep_dir(PAGES, ui_pat) + grep_dir(HOOKS, ui_pat)
        results.append(classify(label, svc_hits, ui_hits))

    print(json.dumps(results, ensure_ascii=False, indent=2))
    api_no_ui = sum(1 for r in results if r["gap"] == "API_NO_UI")
    wired = sum(1 for r in results if r["gap"] == "—")
    print(f"\nSummary: {wired} wired/embedded, {api_no_ui} API_NO_UI (by design)")


if __name__ == "__main__":
    main()
