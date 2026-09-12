"""Tests for the import-light workspace loader (core/scripts/workspace.py).

These never import the `mcp` package: the loader and the nine result builders
live outside `core/mcp/server.py` precisely so the documented test command
(`uv run --with pytest --with pyyaml pytest`) can reach them (KTD4).
"""
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

import pytest

import workspace as ws


VALID_TASK = "---\ntitle: Valid\nstatus: n\npriority: P1\ncategory: technical\n---\nBody text\n"
VALID_PROJECT = "---\ntitle: Valid\nproject_status: idea\npriority: P1\ncategory: technical\n---\nScope\n"


def _mkws(tmp_path):
    (tmp_path / "tasks").mkdir()
    (tmp_path / "projects").mkdir()
    return ws.Workspace.from_base(tmp_path)


def _task(w, name, text, days_old=None):
    p = w.tasks / name
    if isinstance(text, bytes):
        p.write_bytes(text)
    else:
        p.write_text(text, encoding="utf-8")
    if days_old is not None:
        stamp = (datetime.now() - timedelta(days=days_old)).timestamp()
        os.utime(p, (stamp, stamp))
    return p


def _project(w, name, text=None):
    d = w.projects / name
    d.mkdir(parents=True)
    if text is not None:
        (d / "idea.md").write_text(text, encoding="utf-8")
    return d


def _snapshot(root):
    """Every path under root with its bytes and mtime — a byte-identical proof."""
    out = {}
    for p in sorted(Path(root).rglob("*")):
        rel = p.relative_to(root).as_posix()
        out[rel] = ("dir", None) if p.is_dir() else ("file", p.read_bytes(), p.stat().st_mtime_ns)
    return out


# ─── parse_frontmatter: the reason table ────────────────────────────

def test_parse_frontmatter_classifies_each_input_shape():
    assert ws.parse_frontmatter(VALID_TASK).reason == "ok"
    assert ws.parse_frontmatter(VALID_TASK).meta["title"] == "Valid"
    assert ws.parse_frontmatter(VALID_TASK).body == "Body text\n"
    assert ws.parse_frontmatter("# just prose\n").reason == "no-frontmatter"
    assert ws.parse_frontmatter("---\ntitle: x\nbody with no closing fence\n").reason == "unterminated"
    assert ws.parse_frontmatter("---\n- a\n- b\n---\nbody\n").reason == "unparseable"
    assert ws.parse_frontmatter("---\ntitle: [unclosed\n---\nbody\n").reason == "unparseable"


def test_parse_frontmatter_keeps_empty_mapping_as_a_row():
    parsed = ws.parse_frontmatter("---\n---\nbody\n")
    assert parsed.reason == "ok"
    assert parsed.meta == {}


def test_parse_frontmatter_fence_is_a_whole_line_not_a_substring():
    # A `---` inside a YAML scalar and a `---` line in the body must not cut.
    parsed = ws.parse_frontmatter('---\ntitle: "a --- b"\n---\n# T\n\n---\n\nmore\n')
    assert parsed.reason == "ok"
    assert parsed.meta["title"] == "a --- b"
    assert parsed.body == "# T\n\n---\n\nmore\n"


def test_parse_frontmatter_tolerates_a_byte_order_mark():
    parsed = ws.parse_frontmatter("﻿" + VALID_TASK)
    assert parsed.reason == "ok"
    assert parsed.meta["title"] == "Valid"


# ─── load_tasks / load_projects ─────────────────────────────────────

def test_load_tasks_returns_rows_plus_a_reason_for_every_unreadable_file(tmp_path):
    w = _mkws(tmp_path)
    _task(w, "valid.md", VALID_TASK)
    _task(w, "list-fm.md", "---\n- a\n- b\n---\nbody\n")
    _task(w, "unterminated.md", "---\ntitle: x\nstill going\n")
    _task(w, "no-fence.md", "# prose only\n")
    _task(w, "bad-bytes.md", b"---\ntitle: caf\xe9\n---\nbody\n")
    _task(w, "empty-fm.md", "---\n---\nbody\n")
    _task(w, "bom.md", "﻿" + VALID_TASK)
    _task(w, "body-fence.md", "---\ntitle: T\n---\nintro\n---\ntail\n")
    _task(w, "README.md", "# readme\n")
    (w.tasks / ".gitkeep").write_text("", encoding="utf-8")

    rows, unreadable = ws.load_tasks(w)

    assert sorted(r["filename"] for r in rows) == ["body-fence.md", "bom.md", "empty-fm.md", "valid.md"]
    assert sorted((u["path"], u["reason"]) for u in unreadable) == [
        ("tasks/bad-bytes.md", "io-error"),
        ("tasks/list-fm.md", "unparseable"),
        ("tasks/no-fence.md", "no-frontmatter"),
        ("tasks/unterminated.md", "unterminated"),
    ]
    empty = next(r for r in rows if r["filename"] == "empty-fm.md")
    assert set(empty) == {"filename", "body_content", "body_truncated"}
    body_fence = next(r for r in rows if r["filename"] == "body-fence.md")
    assert body_fence["body_content"] == "intro\n---\ntail\n"


def test_load_tasks_reason_never_carries_file_content(tmp_path):
    w = _mkws(tmp_path)
    _task(w, "leaky.md", "---\ntitle: [SECRET-TOKEN-VALUE\n---\nbody\n")
    rows, unreadable = ws.load_tasks(w)
    assert rows == []
    assert unreadable == [{"path": "tasks/leaky.md", "reason": "unparseable"}]
    assert "SECRET-TOKEN-VALUE" not in repr(unreadable)


def test_load_projects_reports_a_folder_without_idea_md_as_missing(tmp_path):
    w = _mkws(tmp_path)
    _project(w, "good", VALID_PROJECT)
    _project(w, "broken", "---\n- a\n---\nbody\n")
    _project(w, "empty-folder")
    _project(w, ".hidden", VALID_PROJECT)
    (w.projects / "README.md").write_text("# projects\n", encoding="utf-8")

    rows, unreadable = ws.load_projects(w)

    assert [r["folder_name"] for r in rows] == ["good"]
    assert sorted((u["path"], u["reason"]) for u in unreadable) == [
        ("projects/broken/idea.md", "unparseable"),
        ("projects/empty-folder/idea.md", "missing"),
    ]


def test_body_truncation_flag_marks_only_bodies_over_the_limit(tmp_path):
    w = _mkws(tmp_path)
    for n in (499, 500, 501):
        _task(w, f"b{n}.md", "---\ntitle: T\n---\n" + ("x" * n))
    rows = {r["filename"]: r for r in ws.load_tasks(w)[0]}
    assert rows["b499.md"]["body_truncated"] is False
    assert rows["b500.md"]["body_truncated"] is False
    assert rows["b501.md"]["body_truncated"] is True
    assert all(len(r["body_content"]) <= 500 for r in rows.values())


# ─── consent and argument gates ─────────────────────────────────────

@pytest.mark.parametrize("value", ["true", "True", 1, 0, None, [], {}, "yes"])
def test_consent_given_is_false_for_everything_but_the_json_boolean(value):
    assert ws.consent_given(value) is False


def test_consent_given_is_true_only_for_boolean_true():
    assert ws.consent_given(True) is True
    assert ws.consent_given(False) is False


@pytest.mark.parametrize("value", ["30", -1, None, 3.5, True])
def test_validate_days_refuses_a_non_integer_with_a_preview_shaped_error(value):
    days, error = ws.validate_days(value)
    assert days is None
    assert error["dry_run"] is True
    assert error["would_archive"] == []
    assert error["error"] == "invalid-days"


def test_validate_days_accepts_a_non_negative_integer():
    assert ws.validate_days(30) == (30, None)
    assert ws.validate_days(0) == (0, None)


# ─── prune: plan ────────────────────────────────────────────────────

def test_plan_prune_lists_only_done_tasks_older_than_the_cutoff(tmp_path):
    w = _mkws(tmp_path)
    _task(w, "done-old.md", "---\ntitle: Old\nstatus: d\ncreated_date: 2026-01-02\n---\nb\n", days_old=60)
    _task(w, "done-new.md", "---\ntitle: New\nstatus: d\n---\nb\n", days_old=1)
    _task(w, "open-old.md", "---\ntitle: Open\nstatus: n\n---\nb\n", days_old=60)
    _task(w, "broken-done.md", "---\n- status: d\n---\nb\n", days_old=60)

    now = datetime.now()
    plan = ws.plan_prune(w, 30, now)

    assert [r["filename"] for r in plan["would_archive"]] == ["done-old.md"]
    row = plan["would_archive"][0]
    assert row["mtime_date"] == (now - timedelta(days=60)).date().isoformat()
    assert row["destination"] == "tasks/archive/done-old.md"
    assert row["created_date"] == "2026-01-02"
    assert row["status"] == "d"
    assert plan["basis"] == "mtime"
    assert plan["unreadable"] == [{"path": "tasks/broken-done.md", "reason": "unparseable"}]


def test_plan_prune_suffixes_a_destination_that_already_exists(tmp_path):
    w = _mkws(tmp_path)
    _task(w, "done-old.md", "---\ntitle: Old\nstatus: d\n---\nb\n", days_old=60)
    w.archive.mkdir(parents=True)
    (w.archive / "done-old.md").write_text("older copy\n", encoding="utf-8")

    now = datetime(2026, 9, 12, 10, 0, 0)
    plan = ws.plan_prune(w, 30, now)
    assert plan["would_archive"][0]["destination"] == "tasks/archive/done-old_2026-09-12.md"


# ─── prune: apply ───────────────────────────────────────────────────

def test_apply_prune_moves_exactly_the_planned_files(tmp_path):
    w = _mkws(tmp_path)
    _task(w, "done-old.md", "---\ntitle: Old\nstatus: d\n---\nb\n", days_old=60)
    _task(w, "open-old.md", "---\ntitle: Open\nstatus: n\n---\nb\n", days_old=60)

    now = datetime.now()
    result = ws.apply_prune(w, ws.plan_prune(w, 30, now), now)

    assert result["archived_files"] == ["done-old.md"]
    assert result["skipped"] == []
    assert not (w.tasks / "done-old.md").exists()
    assert (w.archive / "done-old.md").exists()
    assert (w.tasks / "open-old.md").exists()


def test_apply_prune_reports_a_file_that_vanished_between_plan_and_apply(tmp_path):
    w = _mkws(tmp_path)
    _task(w, "done-old.md", "---\ntitle: Old\nstatus: d\n---\nb\n", days_old=60)
    now = datetime.now()
    plan = ws.plan_prune(w, 30, now)
    (w.tasks / "done-old.md").unlink()

    result = ws.apply_prune(w, plan, now)
    assert result["archived_files"] == []
    assert result["skipped"] == [{"path": "tasks/done-old.md", "reason": "vanished"}]


def test_apply_prune_uses_the_dated_name_when_the_plain_destination_exists(tmp_path):
    w = _mkws(tmp_path)
    _task(w, "done-old.md", "---\ntitle: Old\nstatus: d\n---\nnew\n", days_old=60)
    w.archive.mkdir(parents=True)
    (w.archive / "done-old.md").write_text("older copy\n", encoding="utf-8")

    now = datetime(2026, 9, 12, 10, 0, 0)
    result = ws.apply_prune(w, ws.plan_prune(w, 30, now), now)

    assert result["archived_files"] == ["done-old.md"]
    assert (w.archive / "done-old.md").read_text(encoding="utf-8") == "older copy\n"
    assert (w.archive / "done-old_2026-09-12.md").read_text(encoding="utf-8").endswith("new\n")


def test_apply_prune_never_overwrites_when_both_destinations_exist(tmp_path):
    w = _mkws(tmp_path)
    _task(w, "done-old.md", "---\ntitle: Old\nstatus: d\n---\nnew\n", days_old=60)
    w.archive.mkdir(parents=True)
    (w.archive / "done-old.md").write_text("older copy\n", encoding="utf-8")
    (w.archive / "done-old_2026-09-12.md").write_text("dated copy\n", encoding="utf-8")

    now = datetime(2026, 9, 12, 10, 0, 0)
    before = _snapshot(tmp_path)
    result = ws.apply_prune(w, ws.plan_prune(w, 30, now), now)

    assert result["archived_files"] == []
    assert result["skipped"] == [{"path": "tasks/done-old.md", "reason": "collision"}]
    assert _snapshot(tmp_path) == before


# ─── prune builder: the consent gate ────────────────────────────────

def test_prune_builder_previews_and_leaves_the_tree_byte_identical(tmp_path):
    w = _mkws(tmp_path)
    _task(w, "done-old.md", "---\ntitle: Old\nstatus: d\n---\nb\n", days_old=60)
    before = _snapshot(tmp_path)

    result = ws.tool_prune_completed_tasks(w, {"days": 30})

    assert result["dry_run"] is True
    assert [r["filename"] for r in result["would_archive"]] == ["done-old.md"]
    assert result["basis"] == "mtime"
    assert result["cutoff"]
    assert result["confirm_received"] is None
    assert "archived_count" not in result
    assert not w.archive.exists()
    assert _snapshot(tmp_path) == before


@pytest.mark.parametrize("confirm", ["true", 1, None, False])
def test_prune_builder_previews_for_any_confirm_that_is_not_boolean_true(tmp_path, confirm):
    w = _mkws(tmp_path)
    _task(w, "done-old.md", "---\ntitle: Old\nstatus: d\n---\nb\n", days_old=60)
    args = {"days": 30} if confirm is None else {"days": 30, "confirm": confirm}

    result = ws.tool_prune_completed_tasks(w, args)

    assert result["dry_run"] is True
    assert result["confirm_received"] == (confirm if confirm is not None else None)
    assert (w.tasks / "done-old.md").exists()
    assert not w.archive.exists()


def test_prune_builder_moves_only_on_the_json_boolean_true(tmp_path):
    w = _mkws(tmp_path)
    _task(w, "done-old.md", "---\ntitle: Old\nstatus: d\n---\nb\n", days_old=60)

    result = ws.tool_prune_completed_tasks(w, {"days": 30, "confirm": True})

    assert result["dry_run"] is False
    assert result["archived_files"] == ["done-old.md"]
    assert result["confirm_received"] is True
    assert (w.archive / "done-old.md").exists()


def test_prune_builder_refuses_a_bad_days_value_without_touching_the_tree(tmp_path):
    w = _mkws(tmp_path)
    _task(w, "done-old.md", "---\ntitle: Old\nstatus: d\n---\nb\n", days_old=60)
    before = _snapshot(tmp_path)

    result = ws.tool_prune_completed_tasks(w, {"days": "30", "confirm": True})

    assert result["error"] == "invalid-days"
    assert result["dry_run"] is True
    assert _snapshot(tmp_path) == before


# ─── result-shape invariants across the nine builders ───────────────

READS_TASKS = ["list_tasks", "get_task_summary", "check_priority_limits",
               "prune_completed_tasks", "get_system_status", "process_backlog_with_dedup"]
READS_PROJECTS = ["list_projects", "get_pipeline_status", "get_project_summary",
                  "get_system_status", "process_backlog_with_dedup"]
BUILDER_ARGS = {"process_backlog_with_dedup": {"items": ["a brand new unrelated thing"]}}


def _parity_ws(tmp_path):
    w = _mkws(tmp_path)
    _task(w, "valid.md", VALID_TASK)
    _task(w, "broken.md", "---\n- a\n- b\n---\nbody\n")
    _project(w, "good", VALID_PROJECT)
    _project(w, "broken", "---\n- a\n- b\n---\nbody\n")
    return w


@pytest.mark.parametrize("tool", sorted(set(READS_TASKS) | set(READS_PROJECTS)))
def test_every_builder_reports_what_it_could_not_read(tmp_path, tool):
    w = _parity_ws(tmp_path)
    result = getattr(ws, f"tool_{tool}")(w, BUILDER_ARGS.get(tool, {}))

    expected = []
    if tool in READS_TASKS:
        expected.append({"path": "tasks/broken.md", "reason": "unparseable"})
    if tool in READS_PROJECTS:
        expected.append({"path": "projects/broken/idea.md", "reason": "unparseable"})
    assert sorted(result["unreadable"], key=lambda u: u["path"]) == sorted(expected, key=lambda u: u["path"])


def test_the_two_summary_tools_carry_the_same_unreadable_list_as_the_list_tools(tmp_path):
    w = _parity_ws(tmp_path)
    assert ws.tool_get_task_summary(w, {})["unreadable"] == ws.tool_list_tasks(w, {})["unreadable"]
    assert ws.tool_get_project_summary(w, {})["unreadable"] == ws.tool_list_projects(w, {})["unreadable"]


def test_unreadable_ignores_the_tools_filters_and_is_excluded_from_count(tmp_path):
    w = _parity_ws(tmp_path)
    result = ws.tool_list_tasks(w, {"priority": "P3"})
    assert result["count"] == 0
    assert result["tasks"] == []
    assert result["unreadable"] == [{"path": "tasks/broken.md", "reason": "unparseable"}]


def test_the_two_list_results_state_the_body_limit(tmp_path):
    w = _parity_ws(tmp_path)
    assert ws.tool_list_tasks(w, {})["body_limit"] == 500
    assert ws.tool_list_projects(w, {})["body_limit"] == 500
    assert ws.tool_list_tasks(w, {})["tasks"][0]["body_truncated"] is False


def test_valid_rows_survive_beside_the_broken_ones(tmp_path):
    w = _parity_ws(tmp_path)
    assert [t["filename"] for t in ws.tool_list_tasks(w, {})["tasks"]] == ["valid.md"]
    assert [p["folder_name"] for p in ws.tool_list_projects(w, {})["projects"]] == ["good"]
    assert ws.tool_get_pipeline_status(w, {})["pipeline"]["idea"] == 1


# ─── the frontmatter updater refuses corrupt files ──────────────────

def test_update_frontmatter_refuses_a_file_whose_frontmatter_did_not_parse(tmp_path):
    w = _mkws(tmp_path)
    path = _task(w, "broken.md", "---\n- a\n- b\n---\nbody\n")
    before = path.read_bytes()

    assert ws.update_frontmatter(path, {"status": "d"}) is False
    assert path.read_bytes() == before


def test_update_frontmatter_writes_when_the_frontmatter_parsed(tmp_path):
    w = _mkws(tmp_path)
    path = _task(w, "valid.md", VALID_TASK)

    assert ws.update_frontmatter(path, {"status": "d"}) is True
    assert ws.parse_frontmatter(path.read_text(encoding="utf-8")).meta["status"] == "d"


def test_reason_tokens_come_from_the_closed_sets(tmp_path):
    """The reason vocabulary is a contract consumers switch on (KTD5, KTD6):
    every `unreadable` reason the loader emits and every `skipped` reason the
    prune apply emits must be a member of the exported closed set."""
    w = _mkws(tmp_path)
    _task(w, "bad.md", "---\n- a list, not a mapping\n---\nb\n")
    _task(w, "done-old.md", "---\ntitle: Old\nstatus: d\n---\nb\n", days_old=60)
    _, unreadable = ws.load_tasks(w)
    assert unreadable and {e["reason"] for e in unreadable} <= ws.UNREADABLE_REASONS
    now = datetime.now()
    plan = ws.plan_prune(w, 30, now)
    (w.tasks / "done-old.md").unlink()
    result = ws.apply_prune(w, plan, now)
    assert result["skipped"] and {e["reason"] for e in result["skipped"]} <= ws.SKIP_REASONS
