"""Full sweep — runs every LSP-Brains spec-quality sensor + validates every
CMDB file on disk against the schema.
"""

from __future__ import annotations

import asyncio
import json

import jsonschema
import pytest

from sensory.check_changelog_hygiene import ChangelogHygieneTool
from sensory.check_diagram_sync import DiagramSyncTool
from sensory.check_glossary_freshness import GlossaryFreshnessTool
from sensory.check_link_integrity import LinkIntegrityTool
from sensory.check_rfc_2119_compliance import RFC2119ComplianceTool
from sensory.check_schema_validity import SchemaValidityTool
from sensory.check_spec_completeness import SpecCompletenessTool


SENSORS = [
    ("spec-completeness", SpecCompletenessTool),
    ("schema-validity", SchemaValidityTool),
    ("link-integrity", LinkIntegrityTool),
    ("diagram-sync", DiagramSyncTool),
    ("changelog-hygiene", ChangelogHygieneTool),
    ("rfc-2119-compliance", RFC2119ComplianceTool),
    ("glossary-freshness", GlossaryFreshnessTool),
]

EXPECTED_CMDB_FILES = [f"{name}-cmdb.json" for name, _ in SENSORS]


@pytest.mark.parametrize("name,tool_cls", SENSORS, ids=[n for n, _ in SENSORS])
def test_every_sensor_output_is_schema_valid(name, tool_cls, repo_root, cmdb_schema):
    tool = tool_cls()
    env = asyncio.run(tool.analyze(str(repo_root)))
    jsonschema.validate(env, cmdb_schema)
    assert 0 <= env["score"] <= 100


def test_every_cmdb_file_on_disk_exists(cmdb_dir):
    for fname in EXPECTED_CMDB_FILES:
        assert (cmdb_dir / fname).is_file(), f"missing CMDB: {cmdb_dir / fname}"


def test_every_cmdb_file_on_disk_is_schema_valid(cmdb_dir, cmdb_schema):
    for fname in EXPECTED_CMDB_FILES:
        p = cmdb_dir / fname
        doc = json.loads(p.read_text(encoding="utf-8"))
        jsonschema.validate(doc, cmdb_schema)
