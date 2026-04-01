#!/usr/bin/env python3
"""
MCP Server for Personal OS — Task & Project Management

Tools:
  Tasks:    list_tasks, get_task_summary, check_priority_limits, prune_completed_tasks
  Projects: list_projects, get_pipeline_status, get_project_artifacts, get_project_summary
  System:   get_system_status, process_backlog_with_dedup
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, date
from collections import Counter

import yaml
import re
from difflib import SequenceMatcher
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles date/datetime objects"""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)


# Configuration
BASE_DIR = Path(os.environ.get('MANAGER_AI_BASE_DIR', Path.cwd()))
TASKS_DIR = BASE_DIR / 'Tasks'
PROJECTS_DIR = BASE_DIR / 'Projects'
KNOWLEDGE_DIR = BASE_DIR / 'Knowledge'

# Ensure directories exist
TASKS_DIR.mkdir(exist_ok=True, parents=True)
PROJECTS_DIR.mkdir(exist_ok=True, parents=True)

# Duplicate detection configuration
DEDUP_CONFIG = {
    "similarity_threshold": 0.6,
    "check_categories": True,
}

# Pipeline artifact files to check per project
PROJECT_ARTIFACTS = [
    ("idea", "idea.md"),
    ("prd", "prd.md"),
    ("lean_canvas", "lean-canvas.md"),
    ("gtm_plan", "gtm-plan.md"),
    ("pre_mortem", "pre-mortem.md"),
    ("user_stories", "user-stories.md"),
]

# Knowledge-based artifacts (stored outside project folder)
KNOWLEDGE_ARTIFACTS = [
    ("validation_brief", "Knowledge/research/projects/{project}.md"),
    ("competitor_analysis", "Knowledge/research/projects/{project}-competitors.md"),
]

# Pipeline stage definitions
PIPELINE_STAGES = ["idea", "evaluating", "ready", "active", "paused", "archived"]


# ─── File parsing helpers ───────────────────────────────────────────

def parse_yaml_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown content"""
    if not content.startswith('---'):
        return {}, content
    try:
        parts = content.split('---', 2)[1:]
        if len(parts) >= 1:
            metadata = yaml.safe_load(parts[0])
            body = parts[1] if len(parts) > 1 else ''
            return metadata or {}, body
    except Exception as e:
        logger.error(f"Error parsing YAML: {e}")
    return {}, content


def update_file_frontmatter(filepath: Path, updates: dict) -> bool:
    """Update YAML frontmatter in a file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        metadata, body = parse_yaml_frontmatter(content)
        metadata.update(updates)
        yaml_str = yaml.dump(metadata, default_flow_style=False, sort_keys=False)
        new_content = f"---\n{yaml_str}---\n{body}"
        with open(filepath, 'w') as f:
            f.write(new_content)
        return True
    except Exception as e:
        logger.error(f"Error updating {filepath}: {e}")
        return False


# ─── Task helpers ───────────────────────────────────────────────────

def get_all_tasks() -> List[Dict[str, Any]]:
    """Get all tasks from the Tasks directory"""
    tasks = []
    if not TASKS_DIR.exists():
        return tasks
    for task_file in TASKS_DIR.glob('*.md'):
        if task_file.name in ('README.md', '.gitkeep'):
            continue
        try:
            with open(task_file, 'r') as f:
                content = f.read()
            metadata, body = parse_yaml_frontmatter(content)
            if metadata:
                metadata['filename'] = task_file.name
                metadata['body_content'] = body[:500] if body else ''
                tasks.append(metadata)
        except Exception as e:
            logger.error(f"Error reading {task_file}: {e}")
    return tasks


# ─── Project helpers ────────────────────────────────────────────────

def get_all_projects() -> List[Dict[str, Any]]:
    """Get all projects from the Projects directory"""
    projects = []
    if not PROJECTS_DIR.exists():
        return projects
    for idea_file in PROJECTS_DIR.glob('*/idea.md'):
        try:
            with open(idea_file, 'r') as f:
                content = f.read()
            metadata, body = parse_yaml_frontmatter(content)
            if metadata:
                metadata['folder_name'] = idea_file.parent.name
                metadata['body_content'] = body[:500] if body else ''
                projects.append(metadata)
        except Exception as e:
            logger.error(f"Error reading {idea_file}: {e}")
    return projects


def get_project_artifact_status(project_name: str) -> Dict[str, bool]:
    """Check which artifacts exist for a project"""
    project_dir = PROJECTS_DIR / project_name
    result = {}

    # Check project-folder artifacts
    for key, filename in PROJECT_ARTIFACTS:
        result[key] = (project_dir / filename).exists()

    # Check knowledge-based artifacts
    for key, path_template in KNOWLEDGE_ARTIFACTS:
        path = BASE_DIR / path_template.format(project=project_name)
        result[key] = path.exists()

    return result


def determine_next_skill(artifacts: Dict[str, bool], status: str) -> Optional[str]:
    """Determine the next required skill to run based on artifact state.

    Pipeline sequence: validate → lean-canvas → gtm-plan → pre-mortem → user-stories.
    Note: /competitive-analysis is optional and not included in the required sequence.
    It can be run at any point during evaluation but is not a gate.
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
    """Calculate similarity between two strings (0-1 score)"""
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


def extract_keywords(text: str) -> set:
    """Extract meaningful keywords from text"""
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
                  'for', 'with', 'from', 'up', 'out', 'is', 'it', 'of', 'my'}
    words = re.findall(r'\b\w+\b', text.lower())
    return {w for w in words if w not in stop_words and len(w) > 2}


def find_similar_items(item: str, existing: List[Dict[str, Any]],
                       title_key: str = 'title', source_label: str = 'Tasks/',
                       config: dict = DEDUP_CONFIG) -> List[Dict[str, Any]]:
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
    """Check if an item is too vague or ambiguous"""
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


def generate_clarification_questions(item: str) -> List[str]:
    """Generate clarification questions for ambiguous items"""
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


# ─── MCP Server ─────────────────────────────────────────────────────

app = Server("manager-ai-mcp")


@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List all available tools"""
    return [
        # ── Task tools ──
        types.Tool(
            name="list_tasks",
            description="List tasks with optional filters (category, priority, status)",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Filter by category (comma-separated)"},
                    "priority": {"type": "string", "description": "Filter by priority (comma-separated, e.g., P0,P1)"},
                    "status": {"type": "string", "description": "Filter by status (n,s,b,d,r)"},
                    "include_done": {"type": "boolean", "description": "Include completed tasks", "default": False}
                }
            }
        ),
        types.Tool(
            name="get_task_summary",
            description="Get summary statistics for all tasks",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="check_priority_limits",
            description="Check if priority limits are exceeded (P0 max 3, P1 max 7)",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="prune_completed_tasks",
            description="Delete completed tasks older than specified days",
            inputSchema={
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "Days old before pruning", "default": 30}
                }
            }
        ),

        # ── Project tools ──
        types.Tool(
            name="list_projects",
            description="List projects with optional filters (project_status, priority, category)",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_status": {"type": "string", "description": "Filter by status (comma-separated: idea,evaluating,ready,active,paused,archived)"},
                    "priority": {"type": "string", "description": "Filter by priority (comma-separated)"},
                    "category": {"type": "string", "description": "Filter by category (comma-separated)"}
                }
            }
        ),
        types.Tool(
            name="get_pipeline_status",
            description="Get count of projects at each pipeline stage",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="get_project_artifacts",
            description="Check which artifacts exist for a project and determine next skill to run",
            inputSchema={
                "type": "object",
                "properties": {
                    "project": {"type": "string", "description": "Project folder name"}
                },
                "required": ["project"]
            }
        ),
        types.Tool(
            name="get_project_summary",
            description="Get aggregate project statistics — by status, category, artifact coverage",
            inputSchema={"type": "object", "properties": {}}
        ),

        # ── System tools ──
        types.Tool(
            name="get_system_status",
            description="Get comprehensive system status — tasks, projects, backlog, time insights",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="process_backlog_with_dedup",
            description="Process backlog items with duplicate detection against both Tasks/ and Projects/",
            inputSchema={
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of backlog items to process"
                    },
                    "auto_create": {
                        "type": "boolean",
                        "description": "Automatically create non-duplicate tasks",
                        "default": False
                    }
                },
                "required": ["items"]
            }
        ),
    ]


@app.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls"""
    args = arguments or {}

    # ── list_tasks ──────────────────────────────────────────────
    if name == "list_tasks":
        tasks = get_all_tasks()
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

        result = {"tasks": tasks, "count": len(tasks), "filters_applied": args}

    # ── get_task_summary ────────────────────────────────────────
    elif name == "get_task_summary":
        tasks = get_all_tasks()
        active = [t for t in tasks if t.get('status') != 'd']
        by_priority = Counter(t.get('priority', 'P2') for t in active)
        by_category = Counter(t.get('category', 'other') for t in active)
        by_status = Counter(t.get('status', 'n') for t in tasks)

        time_by_priority = {}
        for p in ['P0', 'P1', 'P2', 'P3']:
            mins = sum(t.get('estimated_time', 30) for t in active if t.get('priority') == p)
            time_by_priority[p] = {"total_minutes": mins, "total_hours": round(mins / 60, 1)}

        result = {
            "total_tasks": len(tasks),
            "active_tasks": len(active),
            "by_priority": dict(by_priority),
            "by_category": dict(by_category),
            "by_status": dict(by_status),
            "time_by_priority": time_by_priority
        }

    # ── check_priority_limits ───────────────────────────────────
    elif name == "check_priority_limits":
        tasks = [t for t in get_all_tasks() if t.get('status') != 'd']
        by_priority = Counter(t.get('priority', 'P2') for t in tasks)
        thresholds = {'P0': 3, 'P1': 7, 'P2': 15}
        alerts = []
        for p, limit in thresholds.items():
            count = by_priority.get(p, 0)
            if count > limit:
                alerts.append(f"{p} has {count} tasks (limit: {limit})")
        result = {
            "priority_counts": dict(by_priority),
            "alerts": alerts,
            "balanced": len(alerts) == 0
        }

    # ── prune_completed_tasks ───────────────────────────────────
    elif name == "prune_completed_tasks":
        days = args.get('days', 30)
        cutoff = datetime.now() - timedelta(days=days)
        deleted = []
        for task_file in TASKS_DIR.glob('*.md'):
            if task_file.name in ('README.md', '.gitkeep'):
                continue
            try:
                mtime = datetime.fromtimestamp(task_file.stat().st_mtime)
                if mtime < cutoff:
                    with open(task_file, 'r') as f:
                        metadata, _ = parse_yaml_frontmatter(f.read())
                    if metadata.get('status') == 'd':
                        task_file.unlink()
                        deleted.append(task_file.name)
            except Exception as e:
                logger.error(f"Error processing {task_file}: {e}")
        result = {
            "success": True,
            "deleted_count": len(deleted),
            "deleted_files": deleted,
            "message": f"Deleted {len(deleted)} done tasks older than {days} days"
        }

    # ── list_projects ───────────────────────────────────────────
    elif name == "list_projects":
        projects = get_all_projects()
        if args.get('project_status'):
            statuses = [s.strip() for s in args['project_status'].split(',')]
            projects = [p for p in projects if p.get('project_status') in statuses]
        if args.get('priority'):
            pris = [p.strip() for p in args['priority'].split(',')]
            projects = [p for p in projects if p.get('priority') in pris]
        if args.get('category'):
            cats = [c.strip() for c in args['category'].split(',')]
            projects = [p for p in projects if p.get('category') in cats]
        result = {"projects": projects, "count": len(projects), "filters_applied": args}

    # ── get_pipeline_status ─────────────────────────────────────
    elif name == "get_pipeline_status":
        projects = get_all_projects()
        by_stage = Counter(p.get('project_status', 'idea') for p in projects)
        ordered = {stage: by_stage.get(stage, 0) for stage in PIPELINE_STAGES}
        result = {
            "pipeline": ordered,
            "total": len(projects),
            "active_pipeline": sum(ordered.get(s, 0) for s in ['evaluating', 'ready', 'active'])
        }

    # ── get_project_artifacts ───────────────────────────────────
    elif name == "get_project_artifacts":
        project = args['project']
        project_dir = PROJECTS_DIR / project
        if not project_dir.exists():
            result = {"success": False, "error": f"Project not found: {project}"}
        else:
            artifacts = get_project_artifact_status(project)
            next_skill = determine_next_skill(artifacts, "")
            result = {
                "project": project,
                "artifacts": artifacts,
                "next_skill": f"{next_skill} {project}" if next_skill else None,
                "pipeline_complete": next_skill is None
            }

    # ── get_project_summary ─────────────────────────────────────
    elif name == "get_project_summary":
        projects = get_all_projects()
        by_status = Counter(p.get('project_status', 'idea') for p in projects)
        by_category = Counter(p.get('category', 'other') for p in projects)
        by_priority = Counter(p.get('priority', 'P2') for p in projects)

        # Count artifact coverage
        artifact_counts = Counter()
        for p in projects:
            folder = p.get('folder_name', '')
            if folder:
                artifacts = get_project_artifact_status(folder)
                for key, exists in artifacts.items():
                    if exists:
                        artifact_counts[key] += 1

        result = {
            "total": len(projects),
            "by_status": dict(by_status),
            "by_category": dict(by_category),
            "by_priority": dict(by_priority),
            "artifact_coverage": dict(artifact_counts)
        }

    # ── get_system_status ───────────────────────────────────────
    elif name == "get_system_status":
        all_tasks = get_all_tasks()
        active_tasks = [t for t in all_tasks if t.get('status') != 'd']
        all_projects = get_all_projects()

        priority_counts = Counter(t['priority'] for t in active_tasks if 'priority' in t)
        task_status_counts = Counter(t['status'] for t in active_tasks if 'status' in t)
        project_status_counts = Counter(p.get('project_status', 'idea') for p in all_projects)

        # Check backlog
        backlog_items = 0
        backlog_file = BASE_DIR / 'BACKLOG.md'
        if backlog_file.exists():
            with open(backlog_file, 'r') as f:
                content = f.read().strip()
            if content and content != 'all done!':
                backlog_items = len([l for l in content.split('\n') if l.strip().startswith('-')])

        # Time insights
        hour = datetime.now().hour
        time_insights = []
        if 9 <= hour < 12:
            time_insights.append("Morning — ideal for outreach and communication tasks")
        elif 14 <= hour < 17:
            time_insights.append("Afternoon — good for deep work (building, writing, analysis)")
        elif hour >= 17:
            time_insights.append("End of day — quick admin tasks or planning tomorrow")

        result = {
            "tasks": {"total": len(all_tasks), "active": len(active_tasks),
                      "by_priority": dict(priority_counts), "by_status": dict(task_status_counts)},
            "projects": {"total": len(all_projects), "by_status": dict(project_status_counts)},
            "backlog_items": backlog_items,
            "time_insights": time_insights,
            "timestamp": datetime.now().isoformat()
        }

    # ── process_backlog_with_dedup ──────────────────────────────
    elif name == "process_backlog_with_dedup":
        items = args.get('items', [])
        if not items:
            result = {"error": "No items provided to process"}
        else:
            existing_tasks = get_all_tasks()
            existing_projects = get_all_projects()

            result = {
                "new_tasks": [],
                "potential_duplicates": [],
                "needs_clarification": [],
                "summary": {}
            }

            for item in items:
                # Check against BOTH tasks and projects
                similar_tasks = find_similar_items(item, existing_tasks, 'title', 'Tasks/')
                similar_projects = find_similar_items(item, existing_projects, 'title', 'Projects/')
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

    else:
        result = {"error": f"Unknown tool: {name}"}

    return [types.TextContent(type="text", text=json.dumps(result, indent=2, cls=DateTimeEncoder))]


async def main():
    """Main entry point for the MCP server"""
    logger.info(f"Starting Personal OS MCP Server")
    logger.info(f"Base directory: {BASE_DIR}")
    logger.info(f"Tasks: {TASKS_DIR} | Projects: {PROJECTS_DIR}")

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="personal-os-mcp",
                server_version="2.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
