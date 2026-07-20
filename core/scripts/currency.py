#!/usr/bin/env python3
"""Baseline/lock/report transaction helpers for the currency watchers
(KTD-6). Pure stdlib; imported by tests and invoked by the watcher skills'
full mode (report-only runs are read-plus-report and never call the
mutating helpers).

Design contract:
- Baselines are schema-versioned JSON advanced by temp-file-plus-rename on
  the same filesystem, strictly AFTER the wave's commit lands. The only
  crash window (after commit, before rename) re-surfaces already-adopted
  candidates on the next run — self-correcting against the ledger, never a
  baseline ahead of committed work.
- The lock lives INSIDE knowledge/currency/ (a report-only run must be able
  to create and reclaim it under the restricted profile). Stale = dead PID
  or age beyond a generous bound; reclaim is logged, delete-to-recover is
  the documented manual escape.
- Reports count as completed only under their final name AND with the
  completion trailer — a crashed run's partial file is never surfaced.
- CE_FAULT_POINT is a test-only seam making the transaction kill-points
  deterministic (Verification Contract: baseline transaction drill).

Self-test home: core/scripts/tests/test_currency.py.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCHEMA_VERSION = 1
LOCK_MAX_AGE_HOURS = 2
REPORT_TRAILER_PREFIX = "<!-- report-complete:"
_REPORT_NAME = re.compile(r"^(\d{4})-(\d{2})-(\d{2})\.md$")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _fault(point: str) -> None:
    if os.environ.get("CE_FAULT_POINT") == point:
        print(f"CE_FAULT_POINT={point}: aborting for drill", file=sys.stderr)
        sys.exit(3)


# ── Baseline ─────────────────────────────────────────────────────────────────
def load_baseline(path: Path | str):
    """Return (data, status). status: ok | absent | corrupt | older-schema.
    Older-known schemas keep their data (migrate-or-rescan with notice —
    never silently discarded); corrupt/absent mean full rescan."""
    path = Path(path)
    if not path.exists():
        return None, "absent"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None, "corrupt"
    if not isinstance(data, dict) or "schema_version" not in data:
        return None, "corrupt"
    if data["schema_version"] != SCHEMA_VERSION:
        return data, "older-schema"
    return data, "ok"


def write_baseline_atomic(path: Path | str, data: dict) -> None:
    """Advance a baseline atomically: write a temp file in the SAME
    directory, then rename. Call only after the wave's commit landed."""
    path = Path(path)
    payload = dict(data)
    payload["schema_version"] = SCHEMA_VERSION
    payload["updated"] = _now().strftime("%Y-%m-%dT%H:%M:%SZ")
    tmp = path.with_name(path.name + f".tmp{os.getpid()}")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    _fault("before-rename")
    os.replace(tmp, path)


# ── Lock ─────────────────────────────────────────────────────────────────────
def _pid_alive(pid) -> bool:
    try:
        os.kill(int(pid), 0)
        return True
    except (ProcessLookupError, ValueError, TypeError):
        return False
    except PermissionError:
        return True  # exists, owned by someone else


def acquire_lock(path: Path | str, mode: str):
    """Return (status, notice). status: acquired | active | reclaimed.
    A live, young lock means another run is active. Dead-PID or over-age
    locks are reclaimed with a logged notice (KTD-6)."""
    path = Path(path)
    notice = ""
    if path.exists():
        stale_reason = None
        try:
            held = json.loads(path.read_text(encoding="utf-8"))
            started = datetime.strptime(
                held.get("started", ""), "%Y-%m-%dT%H:%M:%SZ"
            ).replace(tzinfo=timezone.utc)
            age = _now() - started
            pid = held.get("pid")
            if pid is not None and not _pid_alive(pid):
                stale_reason = f"pid {pid} is dead"
            elif age > timedelta(hours=LOCK_MAX_AGE_HOURS):
                stale_reason = f"age {age} exceeds {LOCK_MAX_AGE_HOURS}h bound"
        except Exception:
            stale_reason = "unreadable lock content"
        if stale_reason is None:
            return "active", "another run holds a live lock; not proceeding"
        notice = (f"reclaimed stale lock ({stale_reason}); if this recurs, "
                  f"delete {path} to recover")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "pid": os.getpid(),
        "started": _now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "mode": mode,
    }, indent=2) + "\n", encoding="utf-8")
    return ("reclaimed", notice) if notice else ("acquired", "")


def release_lock(path: Path | str) -> None:
    Path(path).unlink(missing_ok=True)


# ── Reports ──────────────────────────────────────────────────────────────────
def prune_reports(reports_dir: Path | str, keep_days: int):
    """Delete reports older than keep_days, judged by FILENAME date, inside
    a currency reports directory only (path-asserted — deletion is
    code-level safety; refuse anything outside the currency tree)."""
    reports_dir = Path(reports_dir).resolve()
    parts = "/".join(reports_dir.parts)
    if "knowledge/currency/reports" not in parts.replace("\\", "/"):
        raise ValueError(
            f"refusing to prune outside knowledge/currency/reports: {reports_dir}")
    cutoff = _now() - timedelta(days=keep_days)
    removed = []
    for p in sorted(reports_dir.iterdir()):
        m = _REPORT_NAME.match(p.name)
        if not m:
            continue
        file_date = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)),
                             tzinfo=timezone.utc)
        if file_date < cutoff:
            p.unlink()
            removed.append(p)
    return removed


def completed_reports(reports_dir: Path | str):
    """Reports that finished: final name (YYYY-MM-DD.md) AND completion
    trailer present. Sorted oldest→newest; a crashed run's partial report
    never qualifies."""
    reports_dir = Path(reports_dir)
    if not reports_dir.is_dir():
        return []
    done = []
    for p in sorted(reports_dir.iterdir()):
        if not _REPORT_NAME.match(p.name):
            continue
        try:
            if REPORT_TRAILER_PREFIX in p.read_text(encoding="utf-8"):
                done.append(p)
        except UnicodeDecodeError:
            continue
    return done


# ── Watcher status aggregate (KTD-3: structured fields only) ─────────────────
def watcher_status(base_dir: Path | str) -> dict:
    """Read-only currency aggregate for get_watcher_status and the file
    fallback in /morning. Values are counts, dates, and filenames only —
    no fetched report text passes through. Only completed reports count."""
    base_dir = Path(base_dir)
    today = _now().date()
    out: dict = {"watchers": {}, "generated": today.isoformat()}
    for watcher in ("cli", "repo"):
        reports_dir = base_dir / "knowledge" / "currency" / "reports" / watcher
        done = completed_reports(reports_dir)
        entry = {"last_run": None, "days_since": None, "undecided_candidates": 0}
        if done:
            newest = done[-1]
            run_date = datetime.strptime(newest.name[:10], "%Y-%m-%d").date()
            undecided = sum(
                1 for line in newest.read_text(encoding="utf-8").splitlines()
                if line.lstrip().startswith("- [ ] adopt"))
            entry = {"last_run": run_date.isoformat(),
                     "days_since": (today - run_date).days,
                     "undecided_candidates": undecided}
        out["watchers"][watcher] = entry

    registry_size = None
    live_path = base_dir / "knowledge" / "currency" / "repo-registry.json"
    seed_path = base_dir / "core" / "watchers" / "registry.seed.json"
    if live_path.exists():
        try:
            live = json.loads(live_path.read_text(encoding="utf-8"))
            if not validate_registry(live):
                registry_size = sum(
                    1 for e in live.get("repos", {}).values()
                    if not (isinstance(e, dict) and e.get("watch") is False))
            else:
                out["registry_error"] = "live registry failed schema validation"
        except Exception as e:
            out["registry_error"] = f"unreadable live registry: {type(e).__name__}"
    else:
        try:
            seed = json.loads(seed_path.read_text(encoding="utf-8"))
            registry_size = len(seed.get("repos", {}))
            out["registry_note"] = "no live registry yet — size from shipped seed"
        except Exception:
            registry_size = None
    out["registry_size"] = registry_size
    return out


# ── Registry (KTD-2: tracked immutable seed / gitignored live state) ─────────
_SLUG = re.compile(r"^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$")
_SHA = re.compile(r"^[0-9a-f]{40}$")


def validate_registry(data) -> list[str]:
    """Schema-validate a hand-editable live registry. Returns named errors
    (empty = valid) — a malformed registry is a named failure at run start,
    never a crash mid-run."""
    errs: list[str] = []
    if not isinstance(data, dict):
        return ["registry: not a JSON object"]
    if data.get("schema_version") != SCHEMA_VERSION:
        errs.append(f"registry: schema_version must be {SCHEMA_VERSION}")
    repos = data.get("repos")
    if not isinstance(repos, dict):
        return errs + ["registry: `repos` must be an object"]
    for slug, entry in repos.items():
        if not _SLUG.match(slug):
            errs.append(f"registry: invalid repo slug '{slug}' (want owner/name)")
        if not isinstance(entry, dict):
            errs.append(f"registry: entry for '{slug}' must be an object")
            continue
        for field in ("cursor_sha", "retired_at_sha"):
            v = entry.get(field)
            if v is not None and not _SHA.match(str(v)):
                errs.append(f"registry: '{slug}'.{field} is not a 40-char sha")
        if "watch" in entry and not isinstance(entry["watch"], bool):
            errs.append(f"registry: '{slug}'.watch must be true/false")
    return errs


def effective_watchlist(seed: dict, live: dict) -> dict:
    """Merge seed + live into {slug: cursor_sha} of repos to watch.
    Live wins; retired (watch: false) repos are excluded; adopter-added
    repos (live-only) are included — their names never enter tracked files."""
    out: dict[str, str] = {}
    live_repos = (live or {}).get("repos", {}) or {}
    seed_repos = (seed or {}).get("repos", {}) or {}
    for slug, entry in seed_repos.items():
        lv = live_repos.get(slug, {})
        if isinstance(lv, dict) and lv.get("watch") is False:
            continue
        cursor = (lv.get("cursor_sha") if isinstance(lv, dict) else None) \
            or entry.get("seed_sha")
        if cursor:
            out[slug] = cursor
    for slug, entry in live_repos.items():
        if slug in seed_repos or not isinstance(entry, dict):
            continue
        if entry.get("watch") is False:
            continue
        if entry.get("cursor_sha"):
            out[slug] = entry["cursor_sha"]
    return out


def resume_cursor(seed: dict, live: dict, slug: str):
    """Cursor to resume a repo from: tombstone (`retired_at_sha`) wins, then
    the live cursor, then the frozen seed SHA (provenance fallback)."""
    entry = ((live or {}).get("repos", {}) or {}).get(slug, {})
    if isinstance(entry, dict):
        if entry.get("retired_at_sha"):
            return entry["retired_at_sha"]
        if entry.get("cursor_sha"):
            return entry["cursor_sha"]
    return (((seed or {}).get("repos", {}) or {}).get(slug, {}) or {}).get("seed_sha")


if __name__ == "__main__":
    print(__doc__)
