"""Shared pytest fixtures for the LSP-Brains spec-quality sensor tests.

Per spec §3.8 "Testing Discipline": every sensory tool should ship with a test
that validates its output against `cmdb-envelope-v1.schema.json`, asserts its
declared `exported_variables` are present, and asserts the score falls in the
tool's documented range.

These are project-level integration tests for the seven spec-quality sensors
that score the LSP Brains specification itself (the "ideas as code" Brain).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# The tests directory sits at the LSP-Brains repo root.
_REPO_ROOT = Path(__file__).resolve().parents[1]

# Make `import sensory.check_*` work from any pytest invocation directory.
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


@pytest.fixture
def repo_root() -> Path:
    """Absolute path to the LSP-Brains repo root."""
    return _REPO_ROOT


@pytest.fixture
def cmdb_schema(repo_root: Path) -> dict:
    """The canonical cmdb-envelope-v1 schema (lives in this repo)."""
    schema_path = repo_root / "schemas" / "cmdb-envelope-v1.schema.json"
    return json.loads(schema_path.read_text(encoding="utf-8"))


@pytest.fixture
def cmdb_dir(repo_root: Path) -> Path:
    """This Brain's CMDB directory (`.claude/`)."""
    return repo_root / ".claude"
