"""Integration test for the diagram-sync sensor."""

from __future__ import annotations

import asyncio

import jsonschema

from sensory.check_diagram_sync import DiagramSyncTool


def test_diagram_sync_runs_and_is_schema_valid(repo_root, cmdb_schema):
    tool = DiagramSyncTool()
    env = asyncio.run(tool.analyze(str(repo_root)))
    jsonschema.validate(env, cmdb_schema)
    assert 0 <= env["score"] <= 100


def test_diagram_sync_exports_declared_variables(repo_root):
    tool = DiagramSyncTool()
    env = asyncio.run(tool.analyze(str(repo_root)))
    for key in ("diagrams:referenced", "diagrams:present", "diagrams:missing"):
        assert key in env["exported_variables"], f"missing {key}"


def test_diagram_sync_regression_guard(repo_root):
    # Today: 100. If this drops, a diagram referenced in the spec is missing
    # from `spec/diagrams/`.
    tool = DiagramSyncTool()
    env = asyncio.run(tool.analyze(str(repo_root)))
    assert env["score"] >= 100, f"diagram-sync regressed — findings: {env['findings']}"
