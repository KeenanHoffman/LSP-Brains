"""Integration test for the changelog-hygiene sensor."""

from __future__ import annotations

import asyncio

import jsonschema

from sensory.check_changelog_hygiene import ChangelogHygieneTool


def test_changelog_hygiene_runs_and_is_schema_valid(repo_root, cmdb_schema):
    tool = ChangelogHygieneTool()
    env = asyncio.run(tool.analyze(str(repo_root)))
    jsonschema.validate(env, cmdb_schema)
    assert 0 <= env["score"] <= 100


def test_changelog_hygiene_exports_declared_variables(repo_root):
    tool = ChangelogHygieneTool()
    env = asyncio.run(tool.analyze(str(repo_root)))
    for key in ("changelog:entries", "changelog:uncited_meth_ev"):
        assert key in env["exported_variables"], f"missing {key}"


def test_changelog_hygiene_regression_guard(repo_root):
    # Today: 100. If this drops, a spec version bump landed without a
    # changelog entry or without citing METHODOLOGY-EVOLUTION.
    tool = ChangelogHygieneTool()
    env = asyncio.run(tool.analyze(str(repo_root)))
    assert env["score"] >= 100, f"changelog-hygiene regressed — findings: {env['findings']}"
