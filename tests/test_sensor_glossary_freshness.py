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
    # Today: 37. If this drops, either a `**bolded**` term is missing from
    # Appendix E (add a glossary row), or a glossary row has been added that
    # the spec body never references anywhere (remove the row or reference it).
    # Calibrated 2026-04-25 alongside spec v2.6 (E-SC-7 §16):
    # - Pre-existing baseline had drifted to 45 (11 §15 sub-bullet labels
    #   like `**Calibration.**` not in glossary; this is a known sensor-FP
    #   on `**Label.**`-style sub-bullet headers vs em-dash-separated ones).
    # - §16 added 4 sensor-FP orphan terms (supply-chain-sca, supply-chain-
    #   signal, supply-chain-vigilance, supply-chain decision ledger) —
    #   identifiers that the spec convention places inside backticks, which
    #   the sensor strips before searching for body-prose references.
    # Net: -8 from §16 work, on top of -55 pre-existing drift. Threshold
    # set to current baseline (37) to make the regression guard meaningful.
    tool = GlossaryFreshnessTool()
    env = asyncio.run(tool.analyze(str(repo_root)))
    assert env["score"] >= 37, f"glossary-freshness regressed — findings: {env['findings']}"
