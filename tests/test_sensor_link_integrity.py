"""Integration test for the link-integrity sensor."""

from __future__ import annotations

import asyncio

import jsonschema

from sensory.check_link_integrity import LinkIntegrityTool


def test_link_integrity_runs_and_is_schema_valid(repo_root, cmdb_schema):
    tool = LinkIntegrityTool()
    env = asyncio.run(tool.analyze(str(repo_root)))
    jsonschema.validate(env, cmdb_schema)
    assert 0 <= env["score"] <= 100


def test_link_integrity_exports_declared_variables(repo_root):
    tool = LinkIntegrityTool()
    env = asyncio.run(tool.analyze(str(repo_root)))
    for key in ("links:total", "links:broken"):
        assert key in env["exported_variables"], f"missing {key}"


def test_link_integrity_regression_guard(repo_root):
    # Today: 100. If this drops, an internal § reference or a
    # METHODOLOGY-EVOLUTION back-reference is broken.
    tool = LinkIntegrityTool()
    env = asyncio.run(tool.analyze(str(repo_root)))
    assert env["score"] >= 100, f"link-integrity regressed — findings: {env['findings']}"
