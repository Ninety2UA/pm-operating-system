#!/usr/bin/env python3
"""Workspace loader and MCP result builders for the manager-ai server.

`core/mcp/server.py` imports the `mcp` package at module load and creates
directories at import time, and the documented test command
(`uv run --with pytest --with pyyaml pytest core/scripts/tests/`) installs
neither. Every rule a test has to reach therefore lives here, and the server
keeps only its tool declarations, its dispatch chain, and one-line branches.

Two sections, one import direction (server → builders → filesystem):

- Filesystem: `Workspace` names the four directories; `parse_frontmatter`
  classifies a file into one of the reasons below; `load_tasks`/`load_projects`
  return `(rows, unreadable)`; `plan_prune`/`apply_prune` take `now` so the
  date-suffixed collision name is testable.
- Builders: `tool_<name>(ws, args)` returns the exact result dict the server
  hands back, so the result-shape invariants are proven without an MCP runtime.

Two invariants the builders enforce:

- A file that exists but cannot be used is never reported as absent. Every
  result that reads `tasks/` or `projects/` carries `unreadable`, a list of
  `{path, reason}` with `reason` from the closed set `no-frontmatter`,
  `unterminated`, `unparseable`, `io-error`, `missing`. `reason` is a token and
  `path` is workspace-relative, so no fragment of a private file can ride into
  a result the owner may paste elsewhere. `unreadable` ignores the tool's
  filters and never counts toward `count`.
- Every row says whether its body was clipped (`body_truncated`), and the two
  list results state the cut (`body_limit`).

Self-test home: core/scripts/tests/test_workspace.py.
"""
from __future__ import annotations

import logging
import re
import shutil
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Optional

import yaml

logger = logging.getLogger(__name__)

BODY_LIMIT = 500
EXCLUDED_FILENAMES = frozenset({"README.md", ".gitkeep"})
PRUNE_BASIS = "mtime"

# The closed reason set (KTD5). The read-error reason is `io-error`, never
# `unreadable`, so the list name and a reason value can never collide.
REASON_OK = "ok"
REASON_NO_FRONTMATTER = "no-frontmatter"
REASON_UNTERMINATED = "unterminated"
REASON_UNPARSEABLE = "unparseable"
REASON_IO_ERROR = "io-error"
REASON_MISSING = "missing"
UNREADABLE_REASONS = frozenset({
    REASON_NO_FRONTMATTER, REASON_UNTERMINATED, REASON_UNPARSEABLE,
    REASON_IO_ERROR, REASON_MISSING,
})
SKIP_REASONS = frozenset({"vanished", "collision", "unreadable"})

PIPELINE_STAGES = ["idea", "evaluating", "ready", "active", "paused", "archived"]

PROJECT_ARTIFACTS = [
    ("idea", "idea.md"),
    ("prd", "prd.md"),
    ("lean_canvas", "lean-canvas.md"),
    ("gtm_plan", "gtm-plan.md"),
    ("pre_mortem", "pre-mortem.md"),
    ("user_stories", "user-stories.md"),
]

KNOWLEDGE_ARTIFACTS = [
    ("validation_brief", "knowledge/research/projects/{project}.md"),
    ("competitor_analysis", "knowledge/research/projects/{project}-competitors.md"),
]

DEDUP_CONFIG = {
    "similarity_threshold": 0.6,
    "check_categories": True,
}


# ─── Filesystem section ─────────────────────────────────────────────

@dataclass(frozen=True)
class Workspace:
    """The four directories every reader needs, resolved once."""
    base: Path
    tasks: Path
    projects: Path
    archive: Path

    @classmethod
    def from_base(cls, path: Any) -> "Workspace":
        base = Path(path)
        tasks = base / "tasks"
        return cls(base=base, tasks=tasks, projects=base / "projects", archive=tasks / "archive")


@dataclass(frozen=True)
class Parsed:
    """One file's frontmatter, body, and why it could not be used."""
    meta: dict
    body: str
    reason: str


def _rel(ws: Workspace, path: Path) -> str:
    """Workspace-relative POSIX path — the two merged results need it to
    disambiguate a task from a project."""
    try:
        return path.relative_to(ws.base).as_posix()
    except ValueError:
        return path.name


def parse_frontmatter(text: str) -> Parsed:
    """Classify markdown into (meta, body, reason) per the reason table.

    A fence is a *line* equal to `---`, never the substring: a `---` inside a
    YAML scalar or in the body no longer cuts the file. Trade-off accepted
    here and not upstream: `tasks/*.md` and `idea.md` carry frontmatter by
    contract, so a missing closing fence is reported without a heuristic that
    tries to tell prose from frontmatter.
    """
    if text.startswith("﻿"):
        text = text[1:]
    lines = text.split("\n")
    if not lines or lines[0].rstrip("\r") != "---":
        return Parsed({}, text, REASON_NO_FRONTMATTER)
    close = next((i for i in range(1, len(lines)) if lines[i].rstrip("\r") == "---"), None)
    if close is None:
        return Parsed({}, text, REASON_UNTERMINATED)
    body = "\n".join(lines[close + 1:])
    try:
        meta = yaml.safe_load("\n".join(lines[1:close]))
    except Exception:
        # The exception text can quote the offending line, so it never travels.
        return Parsed({}, text, REASON_UNPARSEABLE)
    if meta is None:
        return Parsed({}, body, REASON_OK)
    if not isinstance(meta, dict):
        return Parsed({}, text, REASON_UNPARSEABLE)
    return Parsed(meta, body, REASON_OK)


def read_markdown(path: Path) -> Parsed:
    """Read a file as UTF-8 (BOM tolerated) and parse it."""
    try:
        raw = path.read_bytes()
    except OSError:
        return Parsed({}, "", REASON_IO_ERROR)
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return Parsed({}, "", REASON_IO_ERROR)
    return parse_frontmatter(text)


def _row(meta: dict, body: str, body_limit: int, key: str, value: str) -> dict:
    row = dict(meta)
    row[key] = value
    body = body or ""
    row["body_content"] = body[:body_limit]
    row["body_truncated"] = len(body) > body_limit
    return row


def load_tasks(ws: Workspace, body_limit: int = BODY_LIMIT) -> tuple[list[dict], list[dict]]:
    """Return (rows, unreadable) for `tasks/*.md`. Rows are gated on the
    reason, never on truthiness, so a file whose frontmatter is an empty
    mapping is a row with only its filename and body."""
    rows: list[dict] = []
    unreadable: list[dict] = []
    if not ws.tasks.is_dir():
        return rows, unreadable
    for task_file in sorted(ws.tasks.glob("*.md")):
        if task_file.name in EXCLUDED_FILENAMES:
            continue
        parsed = read_markdown(task_file)
        if parsed.reason != REASON_OK:
            unreadable.append({"path": _rel(ws, task_file), "reason": parsed.reason})
            continue
        rows.append(_row(parsed.meta, parsed.body, body_limit, "filename", task_file.name))
    return rows, unreadable


def load_projects(ws: Workspace, body_limit: int = BODY_LIMIT) -> tuple[list[dict], list[dict]]:
    """Return (rows, unreadable) for `projects/*/idea.md`. A non-dot folder
    without an `idea.md` is reported `missing`, not ignored."""
    rows: list[dict] = []
    unreadable: list[dict] = []
    if not ws.projects.is_dir():
        return rows, unreadable
    for folder in sorted(ws.projects.iterdir()):
        if not folder.is_dir() or folder.name.startswith("."):
            continue
        idea_file = folder / "idea.md"
        if not idea_file.is_file():
            unreadable.append({"path": _rel(ws, idea_file), "reason": REASON_MISSING})
            continue
        parsed = read_markdown(idea_file)
        if parsed.reason != REASON_OK:
            unreadable.append({"path": _rel(ws, idea_file), "reason": parsed.reason})
            continue
        rows.append(_row(parsed.meta, parsed.body, body_limit, "folder_name", folder.name))
    return rows, unreadable


def update_frontmatter(filepath: Path, updates: dict) -> bool:
    """Merge `updates` into a file's frontmatter and rewrite it.

    Refuses a file whose frontmatter did not parse: rewriting it would replace
    a corrupt-but-recoverable file with the update alone. Returns False and
    logs instead.
    """
    parsed = read_markdown(filepath)
    if parsed.reason != REASON_OK:
        logger.error("Refusing to rewrite %s: frontmatter %s", filepath.name, parsed.reason)
        return False
    meta = dict(parsed.meta)
    meta.update(updates)
    try:
        yaml_str = yaml.dump(meta, default_flow_style=False, sort_keys=False)
        filepath.write_text(f"---\n{yaml_str}---\n{parsed.body}", encoding="utf-8")
    except Exception as exc:
        logger.error("Error updating %s: %s", filepath.name, exc)
        return False
    return True


def _iso(value: Any) -> Any:
    return value.isoformat() if isinstance(value, (datetime, date)) else value


def _dated_name(filename: str, when: datetime) -> str:
    stem, _, suffix = filename.rpartition(".")
    return f"{stem}_{when.strftime('%Y-%m-%d')}.{suffix}" if stem else filename


def plan_prune(ws: Workspace, days: int, now: datetime) -> dict:
    """What `prune_completed_tasks` would move, and why it could not read the rest.

    Built on `load_tasks`, so the `unreadable` list is identical to the one
    `list_tasks` returns — a corrupt done task is never silently left behind.
    Only candidate rows are stat-ed. The cutoff is measured on file mtime, not
    on any completion date in the frontmatter.
    """
    rows, unreadable = load_tasks(ws)
    cutoff = now - timedelta(days=days)
    would: list[dict] = []
    for row in rows:
        if row.get("status") != "d":
            continue
        task_file = ws.tasks / row["filename"]
        try:
            mtime = datetime.fromtimestamp(task_file.stat().st_mtime)
        except OSError:
            continue  # gone between the read and the stat; nothing to move
        if mtime >= cutoff:
            continue
        dest_name = row["filename"]
        if (ws.archive / dest_name).exists():
            dest_name = _dated_name(dest_name, now)
        would.append({
            "filename": row["filename"],
            "mtime_date": mtime.date().isoformat(),
            "created_date": _iso(row.get("created_date")),
            "due_date": _iso(row.get("due_date")),
            "status": row.get("status"),
            "destination": _rel(ws, ws.archive / dest_name),
        })
    return {
        "days": days,
        "basis": PRUNE_BASIS,
        "cutoff": cutoff.isoformat(timespec="seconds"),
        "would_archive": would,
        "unreadable": unreadable,
    }


def apply_prune(ws: Workspace, plan: dict, now: datetime) -> dict:
    """Move exactly what the plan listed. Never overwrites: when both the
    plain and the dated destination exist the file stays where it is and is
    reported as `collision`."""
    candidates = plan.get("would_archive", [])
    archived: list[str] = []
    skipped: list[dict] = []
    if candidates:
        ws.archive.mkdir(parents=True, exist_ok=True)
    for row in candidates:
        source = ws.tasks / row["filename"]
        if not source.is_file():
            skipped.append({"path": _rel(ws, source), "reason": "vanished"})
            continue
        dest = ws.archive / row["filename"]
        if dest.exists():
            dest = ws.archive / _dated_name(row["filename"], now)
            if dest.exists():
                skipped.append({"path": _rel(ws, source), "reason": "collision"})
                continue
        try:
            shutil.move(str(source), str(dest))
        except OSError:
            skipped.append({"path": _rel(ws, source), "reason": "unreadable"})
            continue
        archived.append(row["filename"])
    return {
        "success": True,
        "dry_run": False,
        "days": plan.get("days"),
        "basis": plan.get("basis", PRUNE_BASIS),
        "cutoff": plan.get("cutoff"),
        "archived_count": len(archived),
        "archived_files": archived,
        "skipped": skipped,
        "unreadable": plan.get("unreadable", []),
        "message": (
            f"Archived {len(archived)} done task(s) older than {plan.get('days')} days "
            f"to tasks/archive/; {len(skipped)} skipped."
        ),
    }


def project_artifact_status(ws: Workspace, project_name: str) -> dict:
    """Which pipeline artifacts exist for a project (no frontmatter is read)."""
    project_dir = ws.projects / project_name
    result = {key: (project_dir / filename).exists() for key, filename in PROJECT_ARTIFACTS}
    for key, path_template in KNOWLEDGE_ARTIFACTS:
        result[key] = (ws.base / path_template.format(project=project_name)).exists()
    return result


def determine_next_skill(artifacts: dict) -> Optional[str]:
    """The next required skill given artifact state.

    Pipeline sequence: validate → lean-canvas → gtm-plan → pre-mortem →
    user-stories. `/competitive-analysis` is optional and not a gate.
    """
    if not artifacts.get("idea"):
        return None
    if not artifacts.get("validation_brief"):
        return "/validate-project"
    if not artifacts.get("lean_canvas"):
        return "/lean-canvas"
    if not artifacts.get("gtm_plan"):
        return "/gtm-plan"
    if not artifacts.get("pre_mortem"):
        return "/pre-mortem"
    if not artifacts.get("user_stories"):
        return "/user-stories"
    return None  # Pipeline complete


# ─── Dedup helpers ──────────────────────────────────────────────────

def calculate_similarity(text1: str, text2: str) -> float:
    """Similarity between two strings (0-1 score)"""
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


def extract_keywords(text: str) -> set:
    """Meaningful keywords from text"""
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
                  'for', 'with', 'from', 'up', 'out', 'is', 'it', 'of', 'my'}
    words = re.findall(r'\b\w+\b', text.lower())
    return {w for w in words if w not in stop_words and len(w) > 2}


def find_similar_items(item: str, existing: list, title_key: str = 'title',
                       source_label: str = 'tasks/', config: dict = DEDUP_CONFIG) -> list:
    """Find items similar to the given text"""
    similar = []
    item_keywords = extract_keywords(item)

    for entry in existing:
        if entry.get('status') == 'd':
            continue
        title = entry.get(title_key, '')
        title_similarity = calculate_similarity(item, title)
        task_keywords = extract_keywords(title)
        if item_keywords and task_keywords:
            keyword_overlap = len(item_keywords & task_keywords) / len(item_keywords | task_keywords)
        else:
            keyword_overlap = 0

        similarity_score = (title_similarity * 0.7) + (keyword_overlap * 0.3)

        if similarity_score >= config['similarity_threshold']:
            similar.append({
                'title': title,
                'source': source_label,
                'filename': entry.get('filename', entry.get('folder_name', '')),
                'category': entry.get('category', ''),
                'status': entry.get('status', entry.get('project_status', '')),
                'similarity_score': round(similarity_score, 2)
            })

    similar.sort(key=lambda x: x['similarity_score'], reverse=True)
    return similar[:3]


def is_ambiguous(item: str) -> bool:
    """Whether an item is too vague to create from"""
    vague_patterns = [
        r'^(fix|update|improve|check|review|look at|work on)\s+(the|a|an)?\s*\w+$',
        r'^\w+\s+(stuff|thing|issue|problem)$',
        r'^(follow up|reach out|contact|email)$',
        r'^(investigate|research|explore)\s*\w{0,20}$',
    ]
    item_lower = item.lower().strip()
    if len(item_lower.split()) <= 2:
        return True
    for pattern in vague_patterns:
        if re.match(pattern, item_lower):
            return True
    return False


def generate_clarification_questions(item: str) -> list:
    """Clarification questions for an ambiguous item"""
    questions = []
    item_lower = item.lower()
    if any(w in item_lower for w in ['fix', 'bug', 'error', 'issue']):
        questions.append("Which specific bug or error? Can you provide more details?")
    if any(w in item_lower for w in ['update', 'improve', 'refactor']):
        questions.append("What specific aspects need updating/improvement?")
    if any(w in item_lower for w in ['email', 'contact', 'reach out', 'follow up']):
        questions.append("Who should be contacted and what's the purpose?")
    if any(w in item_lower for w in ['research', 'investigate', 'explore']):
        questions.append("What specific questions need to be answered?")
    if not questions:
        questions.append("Can you provide more specific details about what needs to be done?")
    return questions


# ─── Builder section ────────────────────────────────────────────────

def consent_given(value: Any) -> bool:
    """True only for the JSON boolean `true`. A host that flattens the flag to
    the string "true" or to 1 has not carried consent, so nothing moves."""
    return value is True


def _echo_confirm(value: Any) -> Any:
    """What the tool received for `confirm`, JSON-safe, so a caller can see
    why it got a preview instead of retrying forever."""
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return value[:20]
    return type(value).__name__


def validate_days(value: Any) -> tuple[Optional[int], Optional[dict]]:
    """Return (days, None) or (None, preview-shaped error) — a bad `days`
    never becomes a transport error and never reaches the filesystem."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None, {
            "dry_run": True,
            "error": "invalid-days",
            "days": None,
            "basis": PRUNE_BASIS,
            "cutoff": None,
            "confirm_received": None,
            "would_archive": [],
            "unreadable": [],
            "message": ("`days` must be a non-negative JSON integer (30, not \"30\"). "
                        "Nothing was read and nothing moved."),
        }
    return value, None


def tool_list_tasks(ws: Workspace, args: dict) -> dict:
    tasks, unreadable = load_tasks(ws)
    if not args.get('include_done', False):
        tasks = [t for t in tasks if t.get('status') != 'd']
    if args.get('category'):
        cats = [c.strip() for c in args['category'].split(',')]
        tasks = [t for t in tasks if t.get('category') in cats]
    if args.get('priority'):
        pris = [p.strip() for p in args['priority'].split(',')]
        tasks = [t for t in tasks if t.get('priority') in pris]
    if args.get('status'):
        stats = [s.strip() for s in args['status'].split(',')]
        tasks = [t for t in tasks if t.get('status') in stats]
    return {
        "tasks": tasks,
        "count": len(tasks),
        "body_limit": BODY_LIMIT,
        "unreadable": unreadable,
        "filters_applied": args,
    }


def tool_get_task_summary(ws: Workspace, args: dict) -> dict:
    tasks, unreadable = load_tasks(ws)
    active = [t for t in tasks if t.get('status') != 'd']
    by_priority = Counter(t.get('priority', 'P2') for t in active)
    by_category = Counter(t.get('category', 'other') for t in active)
    by_status = Counter(t.get('status', 'n') for t in tasks)

    time_by_priority = {}
    for p in ['P0', 'P1', 'P2', 'P3']:
        mins = sum(t.get('estimated_time', 30) for t in active if t.get('priority') == p)
        time_by_priority[p] = {"total_minutes": mins, "total_hours": round(mins / 60, 1)}

    return {
        "total_tasks": len(tasks),
        "active_tasks": len(active),
        "by_priority": dict(by_priority),
        "by_category": dict(by_category),
        "by_status": dict(by_status),
        "time_by_priority": time_by_priority,
        "unreadable": unreadable,
    }


def tool_check_priority_limits(ws: Workspace, args: dict) -> dict:
    rows, unreadable = load_tasks(ws)
    tasks = [t for t in rows if t.get('status') != 'd']
    by_priority = Counter(t.get('priority', 'P2') for t in tasks)
    thresholds = {'P0': 3, 'P1': 7}
    alerts = []
    for p, limit in thresholds.items():
        count = by_priority.get(p, 0)
        if count > limit:
            alerts.append(f"{p} has {count} tasks (limit: {limit})")
    return {
        "priority_counts": dict(by_priority),
        "alerts": alerts,
        "balanced": len(alerts) == 0,
        "unreadable": unreadable,
    }


def tool_prune_completed_tasks(ws: Workspace, args: dict) -> dict:
    """Preview by default; move only on the JSON boolean `confirm: true`.

    Two gates: the declared schema rejects a non-boolean `confirm` before the
    handler runs, and `consent_given` rejects it again here for direct callers
    and for any runtime with schema validation off.
    """
    confirm = args.get('confirm')
    days, error = validate_days(args.get('days', 30))
    if error is not None:
        error["confirm_received"] = _echo_confirm(confirm)
        return error
    now = datetime.now()
    plan = plan_prune(ws, days, now)
    if consent_given(confirm):
        result = apply_prune(ws, plan, now)
        result["confirm_received"] = True
        return result
    why = "absent" if confirm is None else "not the JSON boolean true"
    return {
        "dry_run": True,
        "days": days,
        "basis": PRUNE_BASIS,
        "cutoff": plan["cutoff"],
        "confirm_received": _echo_confirm(confirm),
        "would_archive": plan["would_archive"],
        "unreadable": plan["unreadable"],
        "message": (
            f"Preview only — nothing moved, and tasks/archive/ was not created: `confirm` was {why}. "
            f"{len(plan['would_archive'])} done task(s) older than {days} days (measured on file "
            "modification time) would move. Show this list to the owner and call again with "
            "confirm: true only after they say yes."
        ),
    }


def tool_list_projects(ws: Workspace, args: dict) -> dict:
    projects, unreadable = load_projects(ws)
    if args.get('project_status'):
        statuses = [s.strip() for s in args['project_status'].split(',')]
        projects = [p for p in projects if p.get('project_status') in statuses]
    if args.get('priority'):
        pris = [p.strip() for p in args['priority'].split(',')]
        projects = [p for p in projects if p.get('priority') in pris]
    if args.get('category'):
        cats = [c.strip() for c in args['category'].split(',')]
        projects = [p for p in projects if p.get('category') in cats]
    return {
        "projects": projects,
        "count": len(projects),
        "body_limit": BODY_LIMIT,
        "unreadable": unreadable,
        "filters_applied": args,
    }


def tool_get_pipeline_status(ws: Workspace, args: dict) -> dict:
    projects, unreadable = load_projects(ws)
    by_stage = Counter(p.get('project_status', 'idea') for p in projects)
    ordered = {stage: by_stage.get(stage, 0) for stage in PIPELINE_STAGES}
    return {
        "pipeline": ordered,
        "total": len(projects),
        "active_pipeline": sum(ordered.get(s, 0) for s in ['evaluating', 'ready', 'active']),
        "unreadable": unreadable,
    }


def tool_get_project_summary(ws: Workspace, args: dict) -> dict:
    projects, unreadable = load_projects(ws)
    by_status = Counter(p.get('project_status', 'idea') for p in projects)
    by_category = Counter(p.get('category', 'other') for p in projects)
    by_priority = Counter(p.get('priority', 'P2') for p in projects)

    artifact_counts = Counter()
    for p in projects:
        folder = p.get('folder_name', '')
        if folder:
            for key, exists in project_artifact_status(ws, folder).items():
                if exists:
                    artifact_counts[key] += 1

    return {
        "total": len(projects),
        "by_status": dict(by_status),
        "by_category": dict(by_category),
        "by_priority": dict(by_priority),
        "artifact_coverage": dict(artifact_counts),
        "unreadable": unreadable,
    }


def tool_get_system_status(ws: Workspace, args: dict) -> dict:
    all_tasks, task_unreadable = load_tasks(ws)
    active_tasks = [t for t in all_tasks if t.get('status') != 'd']
    all_projects, project_unreadable = load_projects(ws)

    priority_counts = Counter(t['priority'] for t in active_tasks if 'priority' in t)
    task_status_counts = Counter(t['status'] for t in active_tasks if 'status' in t)
    project_status_counts = Counter(p.get('project_status', 'idea') for p in all_projects)

    backlog_items = 0
    backlog_file = ws.base / 'BACKLOG.md'
    if backlog_file.exists():
        content = backlog_file.read_text(encoding='utf-8', errors='replace').strip()
        if content and content != 'all done!':
            backlog_items = len([l for l in content.split('\n') if l.strip().startswith('-')])

    hour = datetime.now().hour
    time_insights = []
    if 9 <= hour < 12:
        time_insights.append("Morning — ideal for outreach and communication tasks")
    elif 14 <= hour < 17:
        time_insights.append("Afternoon — good for deep work (building, writing, analysis)")
    elif hour >= 17:
        time_insights.append("End of day — quick admin tasks or planning tomorrow")

    return {
        "tasks": {"total": len(all_tasks), "active": len(active_tasks),
                  "by_priority": dict(priority_counts), "by_status": dict(task_status_counts)},
        "projects": {"total": len(all_projects), "by_status": dict(project_status_counts)},
        "backlog_items": backlog_items,
        "time_insights": time_insights,
        "unreadable": task_unreadable + project_unreadable,
        "timestamp": datetime.now().isoformat(),
    }


def tool_process_backlog_with_dedup(ws: Workspace, args: dict) -> dict:
    existing_tasks, task_unreadable = load_tasks(ws)
    existing_projects, project_unreadable = load_projects(ws)
    unreadable = task_unreadable + project_unreadable

    items = args.get('items', [])
    if not items:
        return {"error": "No items provided to process", "unreadable": unreadable}

    result = {
        "new_tasks": [],
        "potential_duplicates": [],
        "needs_clarification": [],
        "unreadable": unreadable,
        "summary": {},
    }

    for item in items:
        # Check against BOTH tasks and projects
        similar_tasks = find_similar_items(item, existing_tasks, 'title', 'tasks/')
        similar_projects = find_similar_items(item, existing_projects, 'title', 'projects/')
        all_similar = sorted(similar_tasks + similar_projects,
                             key=lambda x: x['similarity_score'], reverse=True)[:3]

        if all_similar:
            result["potential_duplicates"].append({
                "item": item,
                "similar": all_similar,
                "recommended_action": "merge" if all_similar[0]['similarity_score'] > 0.8 else "review"
            })
        elif is_ambiguous(item):
            result["needs_clarification"].append({
                "item": item,
                "questions": generate_clarification_questions(item),
            })
        else:
            result["new_tasks"].append({
                "item": item,
                "ready_to_create": True
            })

    result["summary"] = {
        "total_items": len(items),
        "new_tasks": len(result["new_tasks"]),
        "duplicates_found": len(result["potential_duplicates"]),
        "needs_clarification": len(result["needs_clarification"]),
    }
    return result
