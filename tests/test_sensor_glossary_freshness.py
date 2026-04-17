"""Integration test for the glossary-freshness sensor."""

from __future__ import annotations

import asyncio

import jsonschema

from sensory.check_glossary_freshness import GlossaryFreshnessTool


def test_glossary_freshness_runs_and_is_schema_valid(repo_root, cmdb_schema):
    tool = GlossaryFreshnessTool()
    env = asyncio.run(tool.analyze(str(repo_root)))
    jsonschema.validate(env, cmdb_schema)
    assert 0 <= env["score"] <= 100


def test_glossary_freshness_exports_declared_variables(repo_root):
    tool = GlossaryFreshnessTool()
    env = asyncio.run(tool.analyze(str(repo_root)))
    for key in ("glossary:missing_count", "glossary:orphan_count"):
        assert key in env["exported_variables"], f"missing {key}"


def test_glossary_freshness_regression_guard(repo_root):
    # Today: 100. If this drops, either a `**bolded**` term is missing from
    # Appendix E (add a glossary row), or a glossary row has been added that
    # the spec body never references anywhere (remove the row or reference it).
    tool = GlossaryFreshnessTool()
    env = asyncio.run(tool.analyze(str(repo_root)))
    assert env["score"] >= 100, f"glossary-freshness regressed — findings: {env['findings']}"
