"""One-off runner: load GOOGLE_API_KEY from BE/.env and run Gemini E2E specs."""
import os
import subprocess
import sys
from pathlib import Path

try:
    from dotenv import dotenv_values
except ImportError:
    print("ERROR: python-dotenv required", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
d = dotenv_values(ROOT / "BE" / ".env")
env = os.environ.copy()
env["E2E_SKIP_WEB_SERVER"] = "1"
key = (d.get("GOOGLE_API_KEY") or "").strip().strip('"')
if key:
    env["GOOGLE_API_KEY"] = key
else:
    print("WARN: GOOGLE_API_KEY missing in BE/.env — tests may skip", file=sys.stderr)

e2e = ROOT / "e2e"
log_path = e2e / "_phase4_playwright_last.log"
cmd = (
    "npx playwright test tests/assessment-flow.spec.js tests/chat.spec.js "
    "tests/personal-courses.spec.js tests/student-flow.spec.js --reporter=list"
)
with open(log_path, "w", encoding="utf-8") as logf:
    r = subprocess.run(cmd, cwd=e2e, env=env, shell=True, stdout=logf, stderr=subprocess.STDOUT)
print("Wrote log:", log_path, "exit:", r.returncode)
sys.exit(r.returncode)
