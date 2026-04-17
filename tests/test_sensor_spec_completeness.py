"""Integration test for the spec-completeness sensor."""

from __future__ import annotations

import asyncio

import jsonschema

from sensory.check_spec_completeness import SpecCompletenessTool


def test_spec_completeness_runs_and_is_schema_valid(repo_root, cmdb_schema):
    tool = SpecCompletenessTool()
    env = asyncio.run(tool.analyze(str(repo_root)))
    jsonschema.validate(env, cmdb_schema)
    assert 0 <= env["score"] <= 100


def test_spec_completeness_exports_declared_variables(repo_root):
    tool = SpecCompletenessTool()
    env = asyncio.run(tool.analyze(str(repo_root)))
    for key in ("spec:toc_entries", "spec:missing_bodies", "spec:tbd_count"):
        assert key in env["exported_variables"], f"missing {key}"


def test_spec_completeness_regression_guard(repo_root):
    # Today: 100. If this drops, either a TOC entry has an empty body or a
    # TBD appeared in a normative section.
    tool = SpecCompletenessTool()
    env = asyncio.run(tool.analyze(str(repo_root)))
    assert env["score"] >= 100, f"spec-completeness regressed — findings: {env['findings']}"
