"""Validator characterization: the sequential script stays green on the real
repo, and the harness itself is visible to git (regression against the
global test_*.py gitignore trap). Fixture-driven tests for individual check
helpers land alongside the checks themselves (U9/U14, test-first).
"""
import subprocess
import sys

from conftest import REPO_ROOT


def test_validator_green_on_real_repo():
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / "core/scripts/validate.py")],
        capture_output=True, text=True, cwd=REPO_ROOT, timeout=300,
    )
    assert proc.returncode == 0, f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    assert "ALL CHECKS PASS" in proc.stdout


def test_harness_is_visible_to_git():
    """core/scripts/tests/ must escape the global test_*.py ignore rule —
    without the U6 negation this whole suite would be invisible to git."""
    proc = subprocess.run(
        ["git", "check-ignore", "core/scripts/tests/test_validate.py"],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )
    assert proc.returncode == 1, (
        "test files are gitignored — the U6 negation rule is missing or broken"
    )
