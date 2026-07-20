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


# ── U11: registry helpers (seed/live split, tombstones, validation) ──────────

def test_registry_validation_names_errors(tmp_path):
    errs = currency.validate_registry({"schema_version": 1, "repos": {
        "owner/good": {"cursor_sha": "a" * 40, "watch": True},
        "bad slug!": {"cursor_sha": "b" * 40, "watch": True},
        "owner/short": {"cursor_sha": "abc", "watch": True},
        "owner/notdict": "x",
    }})
    joined = "\n".join(errs)
    assert "bad slug!" in joined
    assert "owner/short" in joined and "cursor_sha" in joined
    assert "owner/notdict" in joined
    assert not any("owner/good" in e for e in errs)
    assert currency.validate_registry({"repos": {}}) != []  # missing schema_version
    assert currency.validate_registry("garbage") != []


def test_registry_effective_watchlist_merges_seed_and_live():
    seed = {"repos": {"a/one": {"seed_sha": "1" * 40},
                      "a/two": {"seed_sha": "2" * 40}}}
    live = {"schema_version": 1, "repos": {
        "a/one": {"cursor_sha": "9" * 40, "watch": True},
        "a/two": {"cursor_sha": "2" * 40, "watch": False,
                   "retired_at_sha": "2" * 40},
        "adopter/private": {"cursor_sha": "3" * 40, "watch": True},
    }}
    eff = currency.effective_watchlist(seed, live)
    assert eff["a/one"] == "9" * 40
    assert "a/two" not in eff, "retired repo must not be watched"
    assert eff["adopter/private"] == "3" * 40, "adopter-added repos are watched"


def test_registry_tombstone_resume():
    """retire → delete live cursor → re-add resumes from the tombstoned SHA."""
    seed = {"repos": {"a/one": {"seed_sha": "1" * 40}}}
    live = {"schema_version": 1, "repos": {
        "a/one": {"watch": False, "retired_at_sha": "7" * 40}}}
    resumed = currency.resume_cursor(seed, live, "a/one")
    assert resumed == "7" * 40, "tombstone SHA wins over seed on re-add"
    # No tombstone and no live cursor → fall back to the frozen seed SHA.
    live2 = {"schema_version": 1, "repos": {}}
    assert currency.resume_cursor(seed, live2, "a/one") == "1" * 40


# ── U12: watcher status aggregate (KTD-3) ────────────────────────────────────

def test_watcher_status_never_ran(tmp_path):
    st = currency.watcher_status(tmp_path)
    assert st["watchers"]["cli"]["last_run"] is None
    assert st["watchers"]["repo"]["undecided_candidates"] == 0
    assert st["registry_size"] is None  # no seed in an empty base dir


def test_watcher_status_counts_only_completed_reports(tmp_path):
    d = tmp_path / "knowledge" / "currency" / "reports" / "cli"
    d.mkdir(parents=True)
    (d / "2026-07-18.md").write_text(
        "## Decision lines\n- [ ] adopt CLI-1 — x\n- [ ] adopt CLI-2 — y\n"
        "- [x] adopt CLI-0 — done\n" + currency.REPORT_TRAILER_PREFIX + " t -->\n",
        encoding="utf-8")
    (d / "2026-07-20.md").write_text("- [ ] adopt CLI-9 — crashed, no trailer",
                                     encoding="utf-8")
    st = currency.watcher_status(tmp_path)
    assert st["watchers"]["cli"]["last_run"] == "2026-07-18", (
        "trailerless newest report must be skipped in favor of the completed one")
    assert st["watchers"]["cli"]["undecided_candidates"] == 2


def test_watcher_status_registry_sizes(tmp_path):
    seed_dir = tmp_path / "core" / "watchers"
    seed_dir.mkdir(parents=True)
    (seed_dir / "registry.seed.json").write_text(
        json.dumps({"schema_version": 1, "repos": {"a/b": {}, "c/d": {}}}),
        encoding="utf-8")
    st = currency.watcher_status(tmp_path)
    assert st["registry_size"] == 2 and "seed" in st["registry_note"]
    live_dir = tmp_path / "knowledge" / "currency"
    live_dir.mkdir(parents=True)
    (live_dir / "repo-registry.json").write_text(json.dumps({
        "schema_version": 1, "repos": {
            "a/b": {"cursor_sha": "a" * 40, "watch": True},
            "c/d": {"watch": False, "retired_at_sha": "b" * 40},
            "e/f": {"cursor_sha": "c" * 40, "watch": True},
        }}), encoding="utf-8")
    st = currency.watcher_status(tmp_path)
    assert st["registry_size"] == 2, "retired repos excluded; live wins over seed"
    (live_dir / "repo-registry.json").write_text("{broken", encoding="utf-8")
    st = currency.watcher_status(tmp_path)
    assert "registry_error" in st


def test_watcher_status_real_repo_parity():
    """MCP path and file fallback read the same on-disk state: the shipped
    repo (seed present, live state variable) must yield a coherent result."""
    st = currency.watcher_status(REPO_ROOT)
    assert st["registry_size"] is not None and st["registry_size"] >= 6
    assert set(st["watchers"]) == {"cli", "repo"}
