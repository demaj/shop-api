import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
UNREACHABLE = "postgresql+asyncpg://shop:shop@127.0.0.1:1/shop_test"


def run_integration_suite(require_db: str | None) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "DATABASE_URI": UNREACHABLE}
    env.pop("TESTS_REQUIRE_DB", None)
    if require_db is not None:
        env["TESTS_REQUIRE_DB"] = require_db
    return subprocess.run(
        [sys.executable, "-m", "pytest", "tests/integration", "-p", "no:cacheprovider", "--color=no"],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_unreachable_database_skips_by_default() -> None:
    result = run_integration_suite(require_db=None)
    assert result.returncode == pytest.ExitCode.OK, result.stdout
    assert "skipped" in result.stdout
    assert "passed" not in result.stdout


def test_unreachable_database_fails_when_required() -> None:
    result = run_integration_suite(require_db="1")
    assert result.returncode == pytest.ExitCode.TESTS_FAILED, result.stdout
    assert "PostgreSQL not reachable" in result.stdout
    assert "skipped" not in result.stdout
