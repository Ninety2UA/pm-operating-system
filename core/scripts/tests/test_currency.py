"""Baseline transaction drill (U10 / KTD-6, Verification Contract row 6):
deterministic kill-points via the fault-injection seam, atomic advance,
lock reclaim semantics, corrupt/older-schema recovery, path-asserted
retention, and the completed-report filter. Test-first per KTD-4.
"""
import json
import os
import subprocess
import sys
import time

import pytest

from conftest import REPO_ROOT, SCRIPTS

import currency


def test_write_baseline_is_atomic_and_readable(tmp_path):
    p = tmp_path / "cli-baseline.json"
    currency.write_baseline_atomic(p, {"cursor": "v2.1.215"})
    data, status = currency.load_baseline(p)
    assert status == "ok"
    assert data["cursor"] == "v2.1.215"
    assert data["schema_version"] == currency.SCHEMA_VERSION
    assert not list(tmp_path.glob("*.tmp*")), "temp file must not survive"


def test_fault_seam_kill_after_commit_before_advance(tmp_path):
    """The only crash window is AFTER the wave commit, BEFORE the rename:
    the baseline must stay byte-identical, and the temp file is inert."""
    p = tmp_path / "cli-baseline.json"
    currency.write_baseline_atomic(p, {"cursor": "old"})
    before = p.read_bytes()
    proc = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0, sys.argv[1]); import currency; "
         "currency.write_baseline_atomic(sys.argv[2], {'cursor': 'new'})",
         str(SCRIPTS), str(p)],
        env={**os.environ, "CE_FAULT_POINT": "before-rename"},
        capture_output=True, text=True,
    )
    assert proc.returncode == 3, proc.stderr
    assert p.read_bytes() == before, "baseline advanced despite kill"
    data, status = currency.load_baseline(p)
    assert status == "ok" and data["cursor"] == "old"
    # Recovery: a plain re-run (no fault) completes the advance.
    currency.write_baseline_atomic(p, {"cursor": "new"})
    assert currency.load_baseline(p)[0]["cursor"] == "new"


def test_corrupt_baseline_treated_as_rescan(tmp_path):
    p = tmp_path / "b.json"
    p.write_text("{not json", encoding="utf-8")
    data, status = currency.load_baseline(p)
    assert status == "corrupt" and data is None
    assert currency.load_baseline(tmp_path / "missing.json")[1] == "absent"


def test_older_schema_flagged_never_silently_discarded(tmp_path):
    p = tmp_path / "b.json"
    p.write_text(json.dumps({"schema_version": 0, "cursor": "x"}), encoding="utf-8")
    data, status = currency.load_baseline(p)
    assert status == "older-schema"
    assert data["cursor"] == "x", "older-known data must survive for migration"


def test_lock_lifecycle_acquire_active_reclaim(tmp_path):
    lock = tmp_path / "currency.lock"
    assert currency.acquire_lock(lock, "report-only")[0] == "acquired"
    # A live, young lock blocks a second run.
    assert currency.acquire_lock(lock, "report-only")[0] == "active"
    # A dead-PID lock is reclaimed with a notice even when young.
    stale = json.loads(lock.read_text())
    stale["pid"] = 99999999
    lock.write_text(json.dumps(stale), encoding="utf-8")
    status, notice = currency.acquire_lock(lock, "report-only")
    assert status == "reclaimed" and "reclaim" in notice.lower()
    # An ancient lock is reclaimed regardless of PID liveness.
    old = json.loads(lock.read_text())
    old["started"] = "2020-01-01T00:00:00Z"
    old["pid"] = os.getpid()  # alive, but ancient
    lock.write_text(json.dumps(old), encoding="utf-8")
    assert currency.acquire_lock(lock, "report-only")[0] == "reclaimed"
    currency.release_lock(lock)
    assert not lock.exists()


def test_lock_garbage_content_is_reclaimable(tmp_path):
    lock = tmp_path / "currency.lock"
    lock.write_text("garbage", encoding="utf-8")
    assert currency.acquire_lock(lock, "report-only")[0] == "reclaimed"


def test_retention_prunes_by_filename_date_own_dir_only(tmp_path):
    reports = tmp_path / "knowledge" / "currency" / "reports" / "cli"
    reports.mkdir(parents=True)
    (reports / "2020-01-01.md").write_text("old", encoding="utf-8")
    (reports / "2099-01-01.md").write_text("new", encoding="utf-8")
    (reports / "not-a-report.txt").write_text("x", encoding="utf-8")
    removed = currency.prune_reports(reports, keep_days=90)
    assert [p.name for p in removed] == ["2020-01-01.md"]
    assert (reports / "2099-01-01.md").exists()
    assert (reports / "not-a-report.txt").exists(), "non-report names untouched"
    # Path assertion: refuses to prune outside a currency reports dir.
    outside = tmp_path / "elsewhere"
    outside.mkdir()
    (outside / "2020-01-01.md").write_text("x", encoding="utf-8")
    with pytest.raises(ValueError):
        currency.prune_reports(outside, keep_days=90)
    assert (outside / "2020-01-01.md").exists()


def test_completed_reports_require_final_name_and_trailer(tmp_path):
    d = tmp_path / "knowledge" / "currency" / "reports" / "cli"
    d.mkdir(parents=True)
    (d / "2026-07-19.md").write_text("body\n" + currency.REPORT_TRAILER_PREFIX +
                                     " 2026-07-19T10:00:00Z -->\n", encoding="utf-8")
    (d / "2026-07-20.md").write_text("crashed mid-write, no trailer",
                                     encoding="utf-8")
    (d / "2026-07-21.md.tmp").write_text("temp name", encoding="utf-8")
    done = currency.completed_reports(d)
    assert [p.name for p in done] == ["2026-07-19.md"], (
        "a crashed run's partial report must never surface as newest")
