#!/usr/bin/env python3
"""
Chạy pytest cho backend từ thư mục BE.

Ví dụ:
  python tests/run_tests.py
  python tests/run_tests.py -v tests/rbac/
  python tests/run_tests.py tests/admin/test_admin_extended.py -q
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    be_root = Path(__file__).resolve().parents[1]
    os.chdir(be_root)

    env = os.environ.copy()
    env.setdefault("SECRET_KEY", "test-secret-key-for-ci-only-min-32-chars")
    env.setdefault("TESTING", "true")
    env.setdefault("MONGODB_DATABASE", env.get("MONGODB_DATABASE", "ai_learning_test"))

    args = sys.argv[1:] or ["-q"]
    cmd = [sys.executable, "-m", "pytest", *args]
    return subprocess.call(cmd, env=env)


if __name__ == "__main__":
    raise SystemExit(main())
