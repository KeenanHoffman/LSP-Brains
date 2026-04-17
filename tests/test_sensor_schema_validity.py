"""Integration test for the schema-validity sensor."""

from __future__ import annotations

import asyncio

import jsonschema

from sensory.check_schema_validity import SchemaValidityTool


def test_schema_validity_runs_and_is_schema_valid(repo_root, cmdb_schema):
    tool = SchemaValidityTool()
    env = asyncio.run(tool.analyze(str(repo_root)))
    jsonschema.validate(env, cmdb_schema)
    assert 0 <= env["score"] <= 100


def test_schema_validity_exports_declared_variables(repo_root):
    tool = SchemaValidityTool()
    env = asyncio.run(tool.analyze(str(repo_root)))
    for key in ("schemas:count", "schemas:invalid_count", "schemas:broken_refs"):
        assert key in env["exported_variables"], f"missing {key}"


def test_schema_validity_regression_guard(repo_root):
    # Today: 100. If this drops, a schema has a syntax error or a broken $ref.
    tool = SchemaValidityTool()
    env = asyncio.run(tool.analyze(str(repo_root)))
    assert env["score"] >= 100, f"schema-validity regressed — findings: {env['findings']}"
