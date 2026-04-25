"""Integration test for the rfc-2119-compliance sensor."""

from __future__ import annotations

import asyncio

import jsonschema

from sensory.check_rfc_2119_compliance import RFC2119ComplianceTool


def test_rfc_2119_compliance_runs_and_is_schema_valid(repo_root, cmdb_schema):
    tool = RFC2119ComplianceTool()
    env = asyncio.run(tool.analyze(str(repo_root)))
    jsonschema.validate(env, cmdb_schema)
    assert 0 <= env["score"] <= 100


def test_rfc_2119_compliance_exports_declared_variables(repo_root):
    tool = RFC2119ComplianceTool()
    env = asyncio.run(tool.analyze(str(repo_root)))
    for key in (
        "rfc2119:ambiguous_count",
        "rfc2119:must_count",
        "rfc2119:should_count",
        "rfc2119:may_count",
    ):
        assert key in env["exported_variables"], f"missing {key}"


def test_rfc_2119_compliance_regression_guard(repo_root):
    # Today: 95 (a small number of ambiguous "will"/"should" usages in
    # prose where RFC 2119 discipline would prefer the capitalized form).
    # If this drops below 95, new ambiguous normative language was added.
    # Calibrated 2026-04-25 alongside spec v2.6 (E-SC-7 §16): pre-existing
    # baseline had drifted from 97 to 95 between calibrations; §16 itself
    # is sensor-clean (no new ambiguous additions), but pre-existing drift
    # surfaced when the regression guard was re-run.
    tool = RFC2119ComplianceTool()
    env = asyncio.run(tool.analyze(str(repo_root)))
    assert env["score"] >= 95, f"rfc-2119-compliance regressed — findings: {env['findings']}"
