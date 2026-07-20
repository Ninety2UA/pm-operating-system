"""Shared fixtures for the core/scripts test harness.

Run the suite with:
    uv run --with pytest --with pyyaml pytest core/scripts/tests/

(pyyaml is build_adapters' runtime dependency; uv's ephemeral env needs it
declared explicitly because pytest is the entry point here, not a script
with inline metadata.)
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = REPO_ROOT / "core" / "scripts"
sys.path.insert(0, str(SCRIPTS))
