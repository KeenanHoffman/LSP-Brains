# LSP Brains Specification

**Version:** 2.5
**Date:** 2026-04-21
**Status:** Active

### Changelog

- **v2.5 (2026-04-21):** Domain promotion path. §15.5 gains a
  "Promotion path" subsection formalizing how an advisory-weighted
  domain (e.g., `agent-behavior`) transitions to a non-zero weight
  via operator-led calibration audit + append-only promotion
  ledger + rebalance discipline + reversal operation + post-
  promotion swing detection. Audit failure explicitly stops the
  promotion and forces remediation before re-attempt — no retry-
  until-green loop. Reference runbook ships as `NeuroGrim/docs/
  domain-promotion-audit.md`. The mechanism generalizes to any
  advisory domain (git-health, rust-health, coherence, etc.);
  domains without a §15.3-equivalent calibration harness must
  establish one as a forcing function before promotion. Additive
  only — no v2.4 conformance claim is invalidated; implementations
  that keep `agent-behavior` at weight 0.0 remain conformant. See
  `METHODOLOGY-EVOLUTION.md` §13 for rationale.
- **v2.4 (2026-04-21):** Red samples & judge integrity. §15.3 gains a
  "Red samples" subsection formalizing the one-sided ceiling check
  (judge_score MUST stay ≤ `expected_score_ceiling`) that proves the
  judge can detect known failure modes — not just match human labels
  within ±10. `agent-behavior-scenario-v1.schema.json` gains an
  additive `red_samples[]` array alongside the existing `gold_samples[]`.
  `calibration-report-v1.schema.json` gains `overall_status` values
  `red-miss` (judge scored a red sample over its ceiling) and
  `red-skipped` (operator deferred red-sample ceilings via
  `--skip-red-calibration`). The bright line on refinement (§15.5 —
  humans edit, agents do not self-refine, judge prompt is not a tuning
  surface) extends to red samples: a red-miss accrues in an append-only
  judge-integrity ledger and only humans decide whether the response is
  a judge failure, a rubric gap, or a sample mis-label. Additive only —
  no v2.3 conformance claim is invalidated. See `METHODOLOGY-EVOLUTION.md`
  §12 for rationale.
- **v2.3 (2026-04-21):** Agent Behavior Verification. New §15 formalizes
  non-deterministic-verification of non-deterministic agent behavior as a
  first-class methodology concern. A conformant Brain MAY implement an
  `agent-behavior` domain backed by a scenario library + rubric-based judge;
  v2.3 specifies the authoring contract (scenario + rubric + gold samples),
  the distributional interpretation of scores, the feedback-ledger shape that
  closes the refinement loop, and the interaction with governance (§5),
  learning (§12), and culture (§14). Delivers on §14.8's "drift sensor"
  promise in the general agent-behavior form rather than culture-only. New
  `agent-behavior-scenario-v1.schema.json` + `agent-behavior-result-v1.schema.json`.
  Additive only — no v2.2 conformance claim is invalidated; implementations
  that do not ship the domain remain conformant. See `METHODOLOGY-EVOLUTION.md`
  §11 for rationale.
- **v2.2 (2026-04-17):** Sensor Testing Discipline. New §3.8 adds a SHOULD-level
  requirement that each sensory tool ships with an automated test validating its
  CMDB output against `cmdb-envelope-v1.schema.json`, asserting declared
  `exported_variables` are present, and asserting scores fall in the documented
  range for the tool's scoring model. MAY-level integration tests at the
  ecosystem level are encouraged as regression guards. Additive only — no v2.1
  sensor is retroactively non-conformant; the methodology strongly encourages
  the feedback loop. See `METHODOLOGY-EVOLUTION.md` §8 for rationale (drift
  between the Python SDK and the CMDB schema went unnoticed because no
  automated signal watched for it).
- **v2.1 (2026-04-17):** Hybrid MCP + A2A protocol split + Cultural Substrate. MCP scope
  narrowed to sensory tools (§3.7, Appendix F) and Brain-as-tool-to-LLM. A2A (Agent2Agent
  protocol) adopted as the normative transport for Brain-to-Brain peer communication.
  New §13 "A2A Peer Protocol" and Appendix G "A2A Integration". §9 (Fractal Composition)
  and §10 (Dual Brain) updated to use A2A as RECOMMENDED transport; subprocess invocation
  remains conformant in §9. Added §14 "Cultural Substrate" — a lightweight, declarative
  layer that shapes how agents communicate as invariants (analogous to safety invariants
  in §5.5 — they can only tighten, never loosen). New `culture-manifest-v1.schema.json`.
  Additive only — no v2.0 conformance claim is invalidated. See `METHODOLOGY-EVOLUTION.md`
  §6 (protocol split) and §7 (cultural substrate) for rationale.
- **v2.0 (2026-04-11):** Original release. Introduced continuous confidence decay
  (METHODOLOGY-EVOLUTION §1), per-domain floor constraints (§2), trajectory on raw
  scores (§3), dynamic sensory tools via one-measurement-per-tool discipline (§4),
  and attention-budgeted recommendations (§5). See `METHODOLOGY-EVOLUTION.md` for
  per-item rationale and the math behind each change.

---

## Conformance Language

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [The Nervous System Model](#2-the-nervous-system-model)
3. [Sensory Tool Protocol](#3-sensory-tool-protocol)
4. [Scoring Contract](#4-scoring-contract)
5. [Governance Model](#5-governance-model)
6. [Interface Contract](#6-interface-contract)
7. [Trajectory Protocol](#7-trajectory-protocol)
8. [Correlation Engine](#8-correlation-engine)
9. [Fractal Composition Protocol](#9-fractal-composition-protocol)
10. [Dual Brain Architecture](#10-dual-brain-architecture)
11. [Communication Protocol](#11-communication-protocol)
12. [Learning Protocol](#12-learning-protocol)
13. [A2A Peer Protocol](#13-a2a-peer-protocol)
14. [Cultural Substrate](#14-cultural-substrate)
15. [Agent Behavior Verification](#15-agent-behavior-verification)
- [Appendix A: Agent Output Schema](#appendix-a-agent-output-schema)
- [Appendix B: Brain Registry Schema](#appendix-b-brain-registry-schema)
- [Appendix C: CMDB Meta Envelope Schema](#appendix-c-cmdb-meta-envelope-schema)
- [Appendix D: Reference Implementation Map](#appendix-d-reference-implementation-map)
- [Appendix E: Glossary](#appendix-e-glossary)
- [Appendix F: MCP Integration](#appendix-f-mcp-integration)
- [Appendix G: A2A Integration](#appendix-g-a2a-integration)

---

## 1. Introduction

LSP Brains is a language-agnostic specification for building **agent nervous systems** —
software components that observe a project's state, score its health across multiple
domains, detect cross-domain patterns, and recommend actions with calibrated autonomy.

**NeuroGrim** is the reference implementation of this specification, written in
Rust. The specification defines WHAT a conformant Brain must do. The implementation
shows HOW one Brain does it. Any implementation in any language that follows this
specification is equally valid.

### Related Documents

| Document | Location | Description |
|----------|----------|-------------|
| Adoption Guide | `adoption-guide/WHAT-IS-A-STARTER-KIT.md` | Language-agnostic guide to building a starter kit for your stack |
| Dual Brain Design | `DUAL-BRAIN-DESIGN.md` | Detailed architecture for multi-brain coordination (Section 10) |
| Methodology Evolution | `METHODOLOGY-EVOLUTION.md` | Structural improvements (§1–§7) with rationale per change |

### 1.1 Scope

This specification covers:

- How external observations enter the Brain (Sensory Tool Protocol)
- How the Brain computes health scores (Scoring Contract)
- How the Brain governs actions (Governance Model)
- What the Brain outputs (Interface Contract)
- How the Brain tracks trends over time (Trajectory Protocol)
- How the Brain detects cross-domain patterns (Correlation Engine)
- How Brains compose hierarchically (Fractal Composition Protocol)
- How local and external Brains cooperate (Dual Brain Architecture)
- How the Brain adapts output to audiences (Communication Protocol)
- How the Brain learns from outcomes (Learning Protocol)
- How peer Brains communicate (A2A Peer Protocol, Section 13)

**Protocol boundary (v2.1+):** Two distinct protocols carry traffic in and out of a
Brain. MCP (Section 3.7, Appendix F) is used for sensory tool invocation (Brain-as-MCP-client)
and for Brain exposure to LLM agents (Brain-as-MCP-server). A2A (Section 13, Appendix G)
is used for Brain-to-Brain peer communication: parent↔child in fractal composition
(Section 9) and local↔external in dual brain (Section 10). These roles MUST NOT be mixed
— MCP is a tool-call protocol; A2A is a peer-agent protocol.

### 1.2 Motivation

A health score of 72 is meaningless without context. Which domains are strong? Which are
degrading? What actions would improve the score most? Should those actions be taken
automatically, or does a human need to approve them?

These questions require a structured nervous system: sensors to observe, a brain to
synthesize, governance to decide, and feedback loops to learn. LSP Brains provides the
specification for building such systems.

### 1.3 Terminology

Terms used throughout this specification are defined in [Appendix E: Glossary](#appendix-e-glossary).
Key terms: Brain, CMDB, domain, gate, hat, sensory tool, truth layer.

---

## 2. The Nervous System Model

The LSP Brains architecture maps to a biological nervous system. This analogy provides
intuition for each component's role.

> **Diagram:** See `diagrams/nervous-system.mmd`

| Biological Component | LSP Brains Component | Spec Section |
|---------------------|---------------------|-------------|
| Eyes, ears (sensory organs) | Sensory tools | Section 3 |
| Brain (central processing) | Scoring engine | Section 4 |
| Spinal reflexes (autonomic) | Governance (gates, hooks, autonomy) | Section 5 |
| World model (learned) | CMDBs (runtime truth snapshots) | Section 3 |
| Proprioception (body sense) | Trajectory intelligence | Section 7 |
| Pattern recognition | Correlation engine | Section 8 |
| Speech (communication) | Output modes + personas | Section 11 |
| Feedback loops (learning) | Proposal ledger + effectiveness | Section 12 |
| External nervous system | External brain (cloud compute) | Section 10 |

### 2.1 Data Flow

```
Sensory Tool → CMDB JSON → Brain → Scorecard → Output
                                  ↘ Correlations ↗
                                  ↘ Trajectory   ↗
                                  ↘ Governance   ↗
```

1. **Sensory tools** observe external state and write structured JSON (CMDBs)
2. The **Brain** reads CMDBs, computes scores with confidence weighting
3. The **correlation engine** detects cross-domain patterns
4. **Trajectory intelligence** computes trend from score history
5. **Governance** determines what actions are permitted
6. **Output modes** format results for humans or machines

### 2.2 Truth Layers

Every data artifact the Brain touches belongs to exactly one truth layer:

| Layer | Definition | Writer | Committed? |
|-------|-----------|--------|-----------|
| **Source** | Hand-maintained artifacts that define system behavior. Ground truth. | Human (via agent edits) | Yes |
| **Runtime** | Snapshots of external state. Accurate at capture time, decays with age. | Sensory tools | Yes (snapshots) or gitignored |
| **Derived** | Computed from source or runtime. Reproducible. | Compile scripts | No (gitignored) |

Runtime truth is the key concept: a CMDB was accurate when captured but decays with age.
The Brain applies confidence decay (Section 4.4) rather than treating stale data as current.

---

## 3. Sensory Tool Protocol

A sensory tool observes some aspect of a project and writes a structured JSON file
(the CMDB) for the Brain to read. Sensory tools are the Brain's eyes and ears.

> **Diagram:** See `diagrams/scoring-pipeline.mmd`

### 3.1 CMDB Output Format

A sensory tool MUST write a JSON file containing at minimum:

```json
{
  "meta": {
    "schema_version": "1",
    "updated_at": "<ISO 8601 UTC>",
    "updated_by": "<tool identifier>",
    "source": "<source descriptor>"
  },
  "score": 85,
  "updated_at": "<ISO 8601 UTC>"
}
```

**MUST requirements:**

1. The `score` field MUST be an integer in the range [0, 100] inclusive.

2. The `updated_at` field MUST be an ISO 8601 UTC timestamp reflecting when the
   observation was taken (not when the file was written, if different).

3. The `meta.schema_version` field MUST be present. Current version: `"1"`.

4. The `meta.updated_at` field MUST be present and MUST be an ISO 8601 UTC timestamp.

5. The `meta.updated_by` field MUST identify the tool that wrote this CMDB.

> See [Appendix C](#appendix-c-cmdb-meta-envelope-schema) for the full CMDB meta JSON schema.

### 3.2 Behavioral Requirements

6. A sensory tool MUST be idempotent: running it twice with the same project state
   MUST produce the same score.

7. A sensory tool MUST NOT modify any file outside its designated CMDB output path.

8. A sensory tool SHOULD exit with code 0 on success, non-zero on failure.

9. A sensory tool SHOULD complete within 30 seconds for local checks.

### 3.3 Extended CMDB Fields

10. The CMDB SHOULD include a `findings` array of human-readable strings describing
    what was checked and the result of each check.

11. The CMDB MAY include domain-specific fields beyond the required ones.

### 3.4 Language Independence

12. A sensory tool MAY be written in any programming language. The contract is the
    JSON output format, not the implementation language.

The specification intentionally places no constraints on the tool's runtime, dependencies,
or invocation method. A Python script, a Go binary, a shell one-liner, or a CI job that
writes the correct JSON file are all valid sensory tools.

### 3.5 Base Brain Indicators

A conformant Base Brain MUST detect these universal indicators:

| Indicator | What to check | Domain |
|-----------|--------------|--------|
| Version control hygiene | Uncommitted changes, gitignore | deploy-readiness |
| Test presence | Test-to-source file ratio | test-health |
| Documentation | README existence | code-quality |

A conformant Extended Brain SHOULD additionally detect:

| Indicator | What to check | Domain |
|-----------|--------------|--------|
| Lint/format config | Presence of eslint, pylint, etc. | code-quality |
| CI/CD configuration | Presence of workflow files | deploy-readiness |
| Editor configuration | .editorconfig presence | code-quality |
| Secret exposure risk | Sensitive file patterns in tracked files | code-quality |

### 3.6 Auto-Detect Mode

A conformant Brain SHOULD support an auto-detect mode that runs all base sensory tools
in a single pass, producing CMDB files for each domain. This enables the "point and score"
experience: a single command that detects indicators and scores any repository without
prior configuration.

### 3.7 MCP Sensory Protocol (v2)

A conformant Brain MAY discover and invoke sensory tools via the **Model Context Protocol
(MCP)**. MCP is the normative transport for (a) sensory tool invocation (Brain-as-MCP-client,
this section) and (b) Brain exposure to LLM agents (Brain-as-MCP-server, Appendix F). MCP
MUST NOT be used for Brain-to-Brain peer communication; see Section 13 (A2A Peer Protocol)
for fractal composition (§9) and dual brain (§10) transport.

When MCP is used for sensory discovery, the following rules apply:

13. Each sensory tool MUST be an MCP server exposing at least one tool named
    `check_<domain>` (e.g., `check_code_quality`, `check_test_health`).

14. Each sensory tool's `check_<domain>` tool MUST accept a JSON object with at
    minimum a `project_root` string parameter identifying the project to observe.

15. Each sensory tool MUST return its CMDB-envelope JSON (conforming to
    [Appendix C](#appendix-c-cmdb-meta-envelope-schema)) as an MCP `text` content
    type response.

16. The Brain MUST support **STDIO** transport for local sensory tools (subprocess
    communication via stdin/stdout).

17. The Brain SHOULD support **Streamable HTTP** transport for remote sensory tools.

18. Sensory servers MUST be registered in the Brain registry under
    `config.sensory_servers` with at minimum `command` (for STDIO) or `url` (for HTTP)
    and `transport` type.

19. The Brain MUST call `tools/list` on each registered sensory server during
    initialization to discover available tools.

20. The Brain MUST call `tools/call` with the appropriate parameters to invoke a
    sensory check. The returned CMDB data feeds into the scoring pipeline identically
    to file-based CMDBs.

The MCP sensory protocol enables language-agnostic tool authoring: a Python script, Go
binary, or remote HTTP service that implements the MCP server contract is a valid sensory
tool. See [Appendix F](#appendix-f-mcp-integration) for the full MCP integration design.

### 3.8 Testing Discipline

Sensory tools are the ground truth a Brain reasons from. A sensor that silently fails —
producing malformed output, wrong scores, or no output at all — is worse than a missing
sensor: the Brain computes with garbage as though it were fact. Confidence decay (§4.4)
eventually flags *stale* data; it cannot flag *malformed* data, because the Brain trusts
whatever shape the sensor produced.

Each conformant sensory tool SHOULD be accompanied by an automated test that asserts:

1. The tool's output validates against
   [`cmdb-envelope-v1.schema.json`](../schemas/cmdb-envelope-v1.schema.json).
2. The domain-specific `exported_variables` keys declared by the tool are present in
   the output.
3. The score falls within the documented range for the tool's scoring model (e.g., binary
   {0, 100}; graduated 0–100; `%` aggregate over per-check passing count).

Where the tool is part of a fractal ecosystem (§9), an integration test MAY additionally
be run at the parent Brain's level that exercises the tool against live project state
(not a fixture) and asserts the current expected score. Such tests act as regression
guards: a drop in score signals real drift in either the observed state or the observer.

This requirement is SHOULD, not MUST, for two reasons. First, a sensor without a test is
still conformant — confidence decay will surface quality issues eventually, just more
slowly than a test would. Second, elevating this to MUST would invalidate every pre-v2.2
sensor retroactively, which violates the additive-bumps-by-default discipline. The
methodology nonetheless strongly encourages the feedback loop: the observing layer must
itself be observable (VISION principle #18). See `METHODOLOGY-EVOLUTION.md` §8 for the
discovery context.

---

## 4. Scoring Contract

The Brain computes health scores from CMDB data using confidence-weighted arithmetic.

> **Diagram:** See `diagrams/scoring-pipeline.mmd`

### 4.1 Domain Registration

A Brain MUST read domain definitions from a registry. Each domain MUST have:

- A unique key (string, kebab-case convention)
- A weight (number, 0.0 to 1.0)
- A scoring source definition

The sum of all non-advisory domain weights MUST equal 1.0 (tolerance: +/- 0.01).
Advisory domains (weight = 0.0) are excluded from this sum and from the unified score.

### 4.2 CMDB-Type Scoring

For `scoring_source.type = "cmdb"`, the Brain MUST:

1. Read the file at `scoring_source.path` (relative to project root)
2. Extract the score via `scoring_source.score_field` (dot-notation path traversal)
3. Clamp the result to [0, 100]
4. Return `scoring_source.no_file_score` if the file does not exist

**Formula:**
```
if file exists:
    score = clamp(0, 100, floor(cmdb[score_field]))
else:
    score = no_file_score
```

### 4.3 Function-Type Scoring

For `scoring_source.type = "function"`, the Brain MUST dispatch to implementation-specific
scoring functions. This is an extension point. The specification defines the contract:

- The scoring function MUST return an integer in [0, 100]
- The confidence function MUST return an integer in [0, 100]
- Function naming is implementation-defined

### 4.4 Confidence Computation

For CMDB-type domains, confidence MUST be computed from the age of the timestamp
identified by `scoring_source.updated_at_field`.

Implementations MUST use **continuous exponential decay** as the default confidence model:

```
confidence = round(100 * e^(-λ * age_days))
λ = ln(4) / cmdb_very_stale_days
```

This produces smooth degradation anchored to the configured thresholds:

| Age | Confidence (continuous) |
|-----|------------------------|
| 0 days | 100 |
| `cmdb_fresh_days` (1) | ~82 |
| `cmdb_stale_days` (3) | ~55 |
| `cmdb_very_stale_days` (7) | 25 |
| File missing | 0 |

Implementations MAY use a step function as an alternative, but SHOULD document the
cliff effects where scores change discontinuously at threshold boundaries:

| Age | Confidence (step) |
|-----|-------------------|
| < `cmdb_fresh_days` (default: 1) | 100 |
| < `cmdb_stale_days` (default: 3) | 75 |
| < `cmdb_very_stale_days` (default: 7) | 50 |
| >= `cmdb_very_stale_days` | 25 |
| File missing | 0 |

These thresholds SHOULD be configurable via `confidence_thresholds` in the registry.
The minimum confidence for a present file SHOULD be 1 (to distinguish stale data from
missing data).

### 4.5 Effective Score

The Brain MUST compute an effective score per domain using one of two models:

**Multiplier model (default):**
```
effective_score = floor(raw_score * confidence / 100)
```

**Floor model (alternative):**
```
if confidence < floor_confidence_threshold (default: 30):
    effective_score = min(raw_score, floor_score_ceiling (default: 30))
else:
    effective_score = raw_score
```

The scoring model SHOULD be configurable via `scoring.model` in the registry.

### 4.6 Unified Score

The Brain MUST compute a unified score as:

```
unified = floor(clamp(0, 100, sum(effective_score[d] * weight[d] for d in scored_domains)))
```

Advisory domains (weight = 0.0) MUST be excluded from the summation.

**Domain floor constraints:** Implementations SHOULD support per-domain floor constraints.
A domain definition MAY include a `floor` object:

```json
"floor": {
    "min_score": 25,
    "unified_cap": 50,
    "message": "Critical test health failure caps unified score"
}
```

When a domain's effective score falls below `floor.min_score`, the unified score MUST be
capped at `floor.unified_cap` regardless of other domain scores. Multiple floors are
evaluated independently; the most restrictive cap wins.

### 4.7 Score Labels

The Brain SHOULD classify unified scores into color labels:

| Score Range | Label |
|------------|-------|
| >= `health_score_yellow` (default: 75) | green |
| >= `health_score_red` (default: 50) | yellow |
| < `health_score_red` | red |

### 4.8 Freshness Multiplier

For fractal composition (Section 9), the Brain MUST compute a freshness multiplier from
a timestamp:

| Age | Multiplier |
|-----|-----------|
| <= `cmdb_fresh_days` (1) | 1.0 |
| <= `cmdb_stale_days` (3) | 0.75 |
| <= `cmdb_very_stale_days` (7) | 0.5 |
| > `cmdb_very_stale_days` | 0.25 |

---

## 5. Governance Model

Governance controls what the Brain recommends, what it can do automatically, and what
requires human approval. Three subsystems: gates, hats, and autonomy resolution.

### 5.1 Gates

A gate represents a pass/fail quality check. Gates MUST have:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `key` | string | MUST | Unique identifier |
| `tier` | enum | MUST | `"immediate"`, `"before-merge"`, `"pre-deploy"` |
| `status` | enum | MUST | `"clean"`, `"dirty"`, `"needs-run"`, `"stale"` |
| `blocks` | string[] | MUST | Actions this gate blocks (e.g., `["commit", "merge"]`) |
| `run_command` | string | MUST | Command to clear (re-evaluate) the gate |

A gate with status `"dirty"` MUST block the actions listed in its `blocks` field.

**Gate tier weights** MUST be configurable. Defaults:

| Tier | Scoring Weight | Priority Weight |
|------|---------------|----------------|
| immediate | 0.50 | 4.0 |
| before-merge | 0.30 | 3.0 |
| pre-deploy | 0.20 | 2.0 |

### 5.2 Gate Staleness

A gate with status `"clean"` MAY expire after a configurable period (`gate_stale_hours`,
default: 4). An expired gate transitions to status `"stale"`. The Brain SHOULD track
`last_clean_at` to compute expiry.

### 5.3 Recommendation Priority

The Brain SHOULD compute recommendation priority as:

```
priority = tier_weight * downstream_multiplier
```

Where `downstream_multiplier` scales with the number of actions the gate blocks:

```
downstream_multiplier = 1.0 + (0.5 * blocks_count)
```

### 5.4 Hats

A hat applies domain emphasis and autonomy bias to the Brain's output.

A hat definition MUST contain:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `description` | string | MUST | Human-readable purpose |
| `domain_emphasis` | object | MUST | Domain key -> multiplier (1.0 = neutral) |
| `autonomy_bias` | object | MUST | action_type -> autonomy level override |

A hat definition SHOULD contain:

| Field | Type | Description |
|-------|------|-------------|
| `suggest_when` | array | Domain variable conditions that suggest this hat |

When a hat is active, `domain_emphasis` multipliers SHOULD be applied to domain effective
scores for recommendation prioritization.

### 5.5 Autonomy Resolution

> **Diagram:** See `diagrams/autonomy-resolution.mmd`

Autonomy levels MUST be ordered: `auto < notify < approve < blocked`.

Resolution MUST follow this 5-step algorithm:

1. **Base level:** Use hat `autonomy_bias` for the action type if a hat is active;
   otherwise use the action type's `default_level`.
2. **Confidence level:** Compute from proposal effectiveness rate:
   - If `effectiveness_rate >= auto_threshold` (default: 0.8): `auto`
   - If `effectiveness_rate >= notify_threshold` (default: 0.5): `notify`
   - Otherwise: `approve`
   - If `sample_count < min_samples` (default: 3): skip this step
3. **Merge:** Take the MORE restrictive of steps 1 and 2.
4. **Safety invariants:** Apply invariants (can only tighten, never loosen):
   - `destroy_always_blocked`: destructive actions MUST remain `"blocked"`
   - `deploy_never_auto`: deploy actions MUST be at least `"approve"`
5. **Global override:** Apply if configured (can only tighten).

Safety invariants MUST be honored regardless of hat, confidence, or override.

### 5.6 Action Types

The Brain MUST define at least these action types:

| Action Type | Default Level | Blast Radius | Reversible |
|------------|--------------|-------------|-----------|
| `clear-gate` | notify | low | true |
| `refresh-snapshot` | auto | low | true |
| `deploy` | approve | high | false |
| `destroy` | blocked | critical | false |

Implementations MAY define additional action types.

---

## 6. Interface Contract

The Brain MUST produce structured JSON output in agent mode conforming to the schema
defined in this section.

> **Canonical schema:** See [Appendix A](#appendix-a-agent-output-schema)

### 6.1 Required Fields

Every agent-mode output MUST contain these 11 fields:

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | `"1"` (string const) | Interface version |
| `scored_at` | ISO 8601 datetime | When scoring was performed |
| `score` | integer 0-100 | Unified confidence-weighted score |
| `domains` | object | Per-domain scores |
| `dirty_gates` | string[] | Gate keys with status `"dirty"` |
| `stale_artifacts` | string[] | Artifact keys with stale freshness |
| `domain_variables` | object | Cross-domain signal variables |
| `top_recommendations` | array | Top-5 prioritized actions |
| `correlations_fired` | array | Matched correlation rules |
| `incident_patterns` | array | Matched incident patterns |
| `skipped_temporal` | string[] | Temporal patterns skipped |

### 6.2 Per-Domain Object

Each domain in `domains` MUST contain:

| Field | Type | Description |
|-------|------|-------------|
| `score` | integer 0-100 | Raw domain score |
| `effective_score` | integer 0-100 | After confidence weighting |
| `confidence` | integer 0-100 | Confidence in the score |
| `weight` | number 0-1 | Domain weight in unified score |

Each domain in `domains` MAY contain:

| Field | Type | Description |
|-------|------|-------------|
| `trajectory` | object | Per-domain trajectory (Section 7) |

### 6.3 Recommendation Object

Each item in `top_recommendations` MUST contain:

| Field | Type | Required |
|-------|------|----------|
| `domain` | string | MUST |
| `gate` | string | MUST |
| `status` | string | MUST |
| `command` | string | MUST |
| `blocks` | string or string[] | MUST |
| `depends_on` | string[] | MUST |
| `skill` | string | OPTIONAL |

### 6.4 Optional Fields

These fields MAY be present in agent output:

| Field | Type | When Present |
|-------|------|-------------|
| `proposal_effectiveness` | object | When proposal ledger has resolved entries |
| `recent_outcomes` | array | When proposals exist from last 7 days |
| `current_hat` | string | When a hat is active |
| `suggested_hat` | object | When hat suggestion conditions match |
| `current_persona` | string | When `-Persona` parameter is active (Section 11) |
| `children` | array | In ecosystem mode only (Section 9) |
| `trajectory` | object | When score history exists (Section 7) |

### 6.5 Schema Versioning

The `schema_version` field MUST use string-encoded major version numbers (e.g., `"1"`).

Consumers MUST validate they understand the schema version before processing output.

**Compatibility rules:**
- Adding optional fields does NOT require a version bump
- Removing or renaming required fields DOES require a major version bump
- Changing the type of any field DOES require a major version bump

### 6.6 Additional Output Modes

A conformant Brain SHOULD support:

| Mode | Output | Description |
|------|--------|-------------|
| `score` | Single line | `"Brain: 74/100 [domain:score(conf%) ...]"` |
| `health` | Multi-line | Human-readable health report |
| `validate` | Structured | Registry self-validation (exit 0 = valid) |
| `trend` | JSON | Trajectory analysis (Section 7) |
| `propose` | JSON | Remediation proposals with autonomy levels |
| `plan` | JSON | Multi-step execution plan with wave ordering |

---

## 7. Trajectory Protocol

Trajectory intelligence answers "am I getting healthier or sicker?" by analyzing score
history over time. A score of 72 means nothing alone. 72 and rising means momentum. 72
and falling means intervention is needed.

> **Diagram:** See `diagrams/trajectory.mmd`

### 7.1 Score History Format

The Brain MUST maintain a score history file as a JSON array of snapshots:

```json
[
  {
    "scored_at": "2026-04-11T10:00:00Z",
    "score": 72,
    "domains": {
      "code-quality": { "score": 80, "confidence": 90 },
      "test-health": { "score": 65, "confidence": 85 }
    },
    "hat": null
  }
]
```

Each snapshot MUST contain:

| Field | Type | Description |
|-------|------|-------------|
| `scored_at` | ISO 8601 datetime | When the score was computed |
| `score` | integer 0-100 | Unified score at that time |
| `domains` | object | Per-domain score and confidence |
| `hat` | string or null | Active hat at scoring time |

### 7.2 Storage Rules

1. The Brain MUST append a snapshot on every agent-mode invocation.
2. The Brain MUST auto-prune entries older than `trajectory.retention_days` (default: 30).
3. The Brain SHOULD cap entries at `trajectory.max_entries` (default: 500).

### 7.3 Velocity

Velocity MUST be computed from **raw scores**, not confidence-weighted effective scores.
This prevents confidence recovery (re-running a sensory tool without state changes) from
creating phantom "improving" trends, and confidence decay from creating phantom "degrading"
trends. Trajectory answers "is the system getting healthier?" not "have we checked recently?"

For per-domain trajectory, use the raw domain score. For unified trajectory, compute a
weighted average of raw domain scores using the registered domain weights.

Velocity MUST be computed as:

```
N = min(velocity_window, floor(sample_count / 2))
velocity = avg(scores[last N]) - avg(scores[previous N])
```

Where `velocity_window` defaults to 5. The minimum `min_samples_for_trend` SHOULD be at
least 5 (not 3) to provide meaningful averaging rather than single-point comparisons.

### 7.4 Acceleration

Acceleration MUST be computed as:

```
acceleration = current_velocity - previous_velocity
```

Where `previous_velocity` is computed from the window before the current velocity window.
If fewer than `3 * N` samples exist, acceleration MUST be 0.

### 7.5 Classification

Classification MUST use these rules (evaluated in order):

| Classification | Condition | Default Threshold |
|---------------|-----------|------------------|
| `volatile` | stddev(last 2N scores) >= threshold | 10 |
| `improving` | velocity >= threshold | 2 |
| `degrading` | velocity <= threshold | -2 |
| `stable` | none of the above | N/A |
| `no-data` | sample_count < `min_samples_for_trend` | 5 |

`volatile` takes precedence over directional classifications because high variance
makes directional signals unreliable.

### 7.6 Trajectory Output

The trajectory object (when present in agent output) MUST contain:

```json
{
  "velocity": 3.5,
  "acceleration": 0.8,
  "classification": "improving",
  "samples": 12
}
```

| Field | Type | Required |
|-------|------|----------|
| `velocity` | number | MUST |
| `acceleration` | number | MUST |
| `classification` | enum | MUST (`improving`, `stable`, `degrading`, `volatile`, `no-data`) |
| `samples` | integer >= 0 | MUST |

### 7.7 Per-Domain Trajectory

Trajectory SHOULD be computed per-domain AND for the unified score. Per-domain trajectories
use the same algorithm applied to the domain's score series from the history.

### 7.8 Configuration

Trajectory configuration SHOULD be stored in `config.trajectory` in the registry:

```json
{
  "trajectory": {
    "retention_days": 30,
    "max_entries": 500,
    "min_samples_for_trend": 3,
    "velocity_window": 5,
    "classification_thresholds": {
      "improving": 2,
      "degrading": -2,
      "volatile_stddev": 10
    }
  }
}
```

---

## 8. Correlation Engine

The correlation engine detects cross-domain patterns: situations where the combination
of signals from multiple domains reveals a problem that no single domain would catch alone.

> **Diagram:** See `diagrams/condition-tree.mmd`

### 8.1 Domain Variables

Before scoring, the Brain MUST populate domain variables: key-value pairs that describe
the current state of each domain. Variables follow the naming convention:

```
<domain>:<signal_name>
```

For example: `gates:deploy_blocking_count`, `artifacts:any_stale`.

Values MUST be one of: boolean, integer, number, or string.

### 8.2 Condition Tree Evaluation

The Brain MUST support a condition tree evaluator with these operators:

| Operator | Semantics | Short-Circuit |
|----------|-----------|--------------|
| `and` | All children must be true | First false |
| `or` | Any child must be true | First true |
| `not` | Single child must be false | N/A |

Leaf nodes MUST support these comparisons:

| Operator | Semantics |
|----------|-----------|
| `>=` | Greater than or equal |
| `>` | Greater than |
| `==` | Equal |
| `<` | Less than |
| `<=` | Less than or equal |
| `!=` | Not equal |

Each leaf comparison references a domain variable by name and compares against a
literal value.

### 8.3 Correlation Rules

A correlation rule connects two domains:

```json
{
  "name": "failing_tests_block_deploy",
  "description": "Low test health combined with deploy readiness concerns",
  "from_domain": "test-health",
  "to_domain": "deploy-readiness",
  "condition_tree": { ... }
}
```

When a correlation's `condition_tree` evaluates to true (or when simpler matching rules
fire), the correlation MUST appear in the `correlations_fired` output array.

### 8.4 Incident Patterns

An incident pattern is a more severe cross-domain signal with recurrence tracking.

An incident pattern definition MUST contain:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique pattern identifier |
| `name` | string | Human-readable name |
| `description` | string | What this pattern means |
| `conditions` | object | Condition tree or empty for unconditional |
| `hypothesis` | string | Causal hypothesis |
| `severity_base` | enum | `"info"`, `"warning"`, or `"critical"` |

### 8.5 Incident Recurrence

The Brain MUST track incident recurrence via a ledger (JSON array). Each firing MUST
record:

```json
{
  "timestamp": "2026-04-11T10:00:00Z",
  "pattern_id": "quality_cascade",
  "severity": "warning",
  "commit": "abc1234"
}
```

The ledger MUST auto-prune entries older than the recurrence window (default: 30 days).

Severity MUST escalate with recurrence count:

| Condition | Resulting Severity |
|-----------|-------------------|
| count < `warning_count` (default: 3) | Base severity |
| count >= `warning_count` | `"warning"` (minimum) |
| count >= `critical_count` (default: 5) | `"critical"` |

### 8.6 Temporal Operators

The Brain SHOULD support temporal operators for advanced pattern detection:

| Operator | Semantics |
|----------|-----------|
| `duration_above` | Variable exceeds threshold for N consecutive scorings |
| `delta_in_window` | Variable changed by more than threshold in time window |
| `recurrence_count` | Pattern fired N times in time window |

### 8.7 Cross-Project Patterns

In ecosystem mode (Section 9), the Brain SHOULD identify which child projects are
affected by a cross-project incident pattern by extracting project IDs from the
`child.<project_id>:` variable name prefix.

---

## 9. Fractal Composition Protocol

The architecture is fractal: a single project has a Brain, an ecosystem of projects
has a parent Brain that consumes its children's scores. The same pattern repeats at
every scale.

> **Diagram:** See `diagrams/fractal-composition.mmd`

### 9.1 Child Brain Contract

A child Brain MUST produce output conforming to the Interface Contract (Section 6).
The parent Brain invokes the child and parses its JSON output.

**Transport (v2.1+):** Child invocation MAY use one of the following transports:

| Transport | Status | Use case |
|-----------|--------|----------|
| **A2A** (Section 13) | RECOMMENDED | Long-running peer Brains, cross-machine ecosystems, dual brain |
| **Subprocess** | Conformant (legacy) | Starter-kit adopters, CI one-shots, offline environments |
| **MCP** | NOT RECOMMENDED | MCP is a tool-call protocol; peer Brains are agents |

The choice is implementation-local. Child invocation via any conformant transport MUST
produce identical ecosystem scores given identical inputs.

### 9.2 Ecosystem Registry

A parent Brain MUST register children via an ecosystem registry:

```json
{
  "children": {
    "project-alpha": {
      "display_name": "Project Alpha",
      "a2a_endpoint": "https://alpha.internal/a2a/v1/",
      "interface_version": "1",
      "depends_on": [],
      "weight": 1.0,
      "enabled": true
    },
    "project-beta-legacy": {
      "display_name": "Project Beta (subprocess)",
      "brain_path": "relative/path/to/brain-entry",
      "interface_version": "1",
      "depends_on": [],
      "weight": 1.0,
      "enabled": true
    }
  }
}
```

Each child entry MUST contain exactly one of `a2a_endpoint` or `brain_path` as the
transport selector:

| Field | Type | Description |
|-------|------|-------------|
| `a2a_endpoint` | string (URI) | Base URL of child Brain A2A server (RECOMMENDED, v2.1+). Selects A2A transport. |
| `brain_path` | string | Path to the child Brain entry point for subprocess transport (legacy, conformant). |
| `agent_card_url` | string (URI) | OPTIONAL override for the child Agent Card location. Default: `{a2a_endpoint}/.well-known/agent-card.json`. Ignored for subprocess transport. |
| `interface_version` | string | Expected schema version |
| `depends_on` | string[] | Project IDs this child depends on |
| `weight` | number | Weight in ecosystem aggregation |
| `enabled` | boolean | Whether this child participates in the ecosystem |

### 9.3 Execution Order

The parent Brain MUST execute children in topological order based on `depends_on`
relationships. Implementations SHOULD use Kahn's algorithm. If a cycle is detected,
the Brain SHOULD fall back to registration order with a warning.

### 9.4 Score Aggregation

The parent Brain MUST aggregate child scores as:

```
child_effective = child_score * (child_confidence / 100) * freshness_multiplier(child_scored_at)
ecosystem_score = weighted_avg(parent_score * parent_weight, child_effective[i] * child_weight[i])
```

### 9.5 Child Status

The parent Brain MUST report child status:

| Status | Condition |
|--------|-----------|
| `ok` | Child invoked successfully |
| `error` | Child failed or produced invalid output |
| `stale` | Child's `freshness_multiplier < 0.5` |
| `disabled` | Child's `enabled` is false |

### 9.6 Cross-Project Domain Variables

The parent Brain SHOULD merge child domain variables with a `child.<project_id>.` prefix:

```
child.project-alpha.gates:deploy_blocking_count = 3
child.project-alpha.artifacts:any_stale = true
```

This enables cross-project incident patterns (Section 8.7).

### 9.7 A2A Transport Mapping

When a child entry carries `a2a_endpoint`, the parent Brain MUST invoke the child via
the A2A Peer Protocol (Section 13). The invocation flow:

1. Parent resolves the child Agent Card at `{a2a_endpoint}/.well-known/agent-card.json`
   (or at `agent_card_url` if specified).
2. Parent verifies the Agent Card declares `score.updated` or `ecosystem.scored` in
   `capabilities.emits`, and the expected `interface_version`.
3. Parent creates an A2A task requesting a fresh score (message type `snapshot.requested`
   with payload `{"scope": "score"}`).
4. Child returns an A2A message of type `score.updated` with payload containing the
   full Interface Contract (Section 6) output.
5. Parent validates payload against `agent-output-v1.schema.json` and feeds it into
   score aggregation (§9.4).

When a child entry carries only `brain_path` (no `a2a_endpoint`), the parent Brain
invokes the child via subprocess (legacy transport) and parses its stdout as agent-mode
JSON. This remains conformant in v2.1.

Implementations MUST produce the same ecosystem score regardless of transport.

---

## 10. Dual Brain Architecture

This section defines the design for splitting Brain responsibilities between a local
instance (developer terminal) and an external instance (cloud compute / CI).

> **Diagrams:** `diagrams/dual-brain.mmd` and `diagrams/dual-brain-detailed.mmd` show
> the topology. `diagrams/sync-protocol.mmd` visualizes the shared-state sync
> patterns (append-merge, last-writer-wins, event append). `diagrams/migration-path.mmd`
> shows the five-phase adoption path from local-only to full dual brain.
> **Detailed Design:** See `DUAL-BRAIN-DESIGN.md` for the full implementable design
> including trigger model, event protocol, sync protocol, migration path, and
> implementation patterns.

**Note:** This section is a design specification. Implementation is tracked in Stage 6
("Dual Brain via A2A") of the reference implementation roadmap. The v2.1 revision replaces
the original bespoke event protocol with A2A (Section 13); shared state semantics are
unchanged. Local Brain implementations remain forward-compatible.

### 10.1 Local Brain

The local brain runs on the developer's machine. It MUST:

- Score within 5 seconds for interactive use
- Support file-save and commit-triggered invocation
- Read only local file system state (no cloud API calls)
- Produce Interface Contract compliant output (Section 6)

### 10.2 External Brain

The external brain runs in a cloud environment. It MUST:

- Support webhook, schedule, and CI-event triggers
- Access cloud APIs (monitoring, SCA, deployment state)
- Produce Interface Contract compliant output (Section 6)
- Support ecosystem aggregation (Section 9)

### 10.3 Metadata Proximity Rules

| Data | Preferred Brain | Rationale |
|------|----------------|-----------|
| Git status, file counts | Local | File system access required |
| Test results, lint output | Local | Fast, local tools |
| Cloud monitoring metrics | External | API access required |
| SCA vulnerability data | External | Requires network + DB |
| Ecosystem aggregation | External | Cross-project access |
| Score history | Shared | Both brains read/write |
| Gate state | Shared | Both brains read/write |

### 10.4 Event Protocol (A2A)

In v2.1+, Brains MUST communicate via the A2A Peer Protocol (Section 13). Each event
below maps to an A2A message type (validated against `a2a-envelope-v1.schema.json`).
Shared-file event transport (`event-log.jsonl`) is permitted as a degraded-mode fallback
when A2A is unavailable (e.g., air-gapped environments), but A2A is the normative path.

| Event (A2A message_type) | Direction | Trigger |
|--------------------------|-----------|---------|
| `score.updated` | Local → External | Local Brain scored |
| `gate.changed` | Local → External | Gate status changed |
| `ecosystem.scored` | External → Local | Ecosystem scored |
| `incident.detected` | External → Local | Cross-project pattern fired |
| `incident.resolved` | Either | Incident state cleared |
| `snapshot.requested` | External → Local | External requests fresh local data |
| `snapshot.delivered` | Local → External | Response to `snapshot.requested` (via `reply_to`) |
| `proposal.created` | Either | New remediation proposal generated |
| `proposal.resolved` | Either | Proposal executed, outcome recorded |
| `config.changed` | Either | Registry modified |

A conformant Brain MUST emit and accept the message types it declares in its Agent Card
`capabilities.emits` and `capabilities.accepts` arrays. Message envelopes carry an
`message_id` used as an idempotency key — duplicate receipt MUST be a no-op that returns
the cached response.

### 10.5 Shared State Synchronization

Shared state semantics are unchanged from v2.0. A2A (§10.4) carries *messages* between
Brains; it does NOT replace shared state. Both brains read and write shared state files
(score history, gate state, proposal ledger). Implementations MUST handle concurrent
access. Recommended strategies:

- **File-level locking** for single-machine setups
- **Last-writer-wins with timestamps** for distributed setups
- **External store** (database, cloud storage) for production ecosystems

When a Brain receives an A2A message that references shared state (e.g., `proposal.resolved`
referencing a proposal ledger entry), the receiving Brain MUST read the current shared
state before acting — the A2A message is a notification, not an authoritative copy.

### 10.6 Forward Compatibility

Implementations of the local brain SHOULD NOT assume they are the only writer of
shared state files. This ensures forward compatibility with the dual brain architecture.

---

## 11. Communication Protocol

The Brain adapts its output format based on the consumer: machine (agent mode), human
(health report), or specific human roles (personas).

### 11.1 Output Modes

A conformant Brain MUST support `agent` mode (Section 6). All other modes are RECOMMENDED:

| Mode | Consumer | Format |
|------|----------|--------|
| `agent` | Machines / LLMs | JSON (Section 6) |
| `score` | Humans (quick check) | Single line |
| `health` | Humans (detailed) | Multi-line report |
| `trend` | Humans / machines | JSON trajectory |
| `validate` | CI / humans | Structured validation |

### 11.2 Human User Personas

A conformant Brain SHOULD support persona-based output filtering:

| Persona | Focus | Output Level |
|---------|-------|-------------|
| `executive` | Score + trajectory + top risk | Minimal (5 lines max) |
| `manager` | Domain breakdown + trends + blockers | Summary |
| `developer` | Full detail + commands + findings | Verbose |
| `specialist` | Single-domain deep dive | Filtered |
| `product-manager` | Delivery risk + blockers + timeline | PM-focused |

When both a hat and a persona are specified, the hat controls WHAT is emphasized and
the persona controls HOW MUCH detail is shown.

### 11.3 Truth Layer Transparency

The Brain SHOULD indicate the truth layer of data it reports. Stale runtime data
(confidence < 50%) SHOULD be visually distinguished from fresh data in human-facing modes.

---

## 12. Learning Protocol

The Brain learns from the outcomes of its recommendations through a proposal ledger.

### 12.1 Proposal Ledger Format

The Brain MUST maintain a proposal ledger as a JSON array:

```json
[
  {
    "timestamp": "2026-04-11T10:00:00Z",
    "proposals": [
      { "id": "proposal-1", "command": "...", "action_type": "clear-gate" }
    ],
    "pre_score": 65,
    "post_score": 78,
    "commit": "abc1234",
    "hat": "operator"
  }
]
```

### 12.2 Proposal Lifecycle

1. **Generate:** The Brain produces proposals with `pre_score`.
2. **Execute:** The human or agent executes some or all proposals.
3. **Resolve:** On the next `propose` invocation, the Brain records `post_score` on
   the most recent unresolved entry by comparing the current score.
4. **Prune:** Entries older than the retention period (default: 90 days) are removed.

### 12.3 Effectiveness Computation

Effectiveness MUST be computed per action type:

```
sample_count = count of resolved proposals with this action_type
success_count = count where (post_score - pre_score) > 0
effectiveness_rate = success_count / sample_count
```

If `sample_count < min_samples` (default: 3), the effectiveness is insufficient for
confidence-based autonomy adjustment (Section 5.5, step 2).

### 12.4 Outcome Feedback

The Brain SHOULD report recent outcomes (last 7 days) in agent output so that consumers
can see the effect of recent actions. Each outcome includes `pre_score`, `post_score`,
`delta`, action types, and resolution status.

---

## 13. A2A Peer Protocol

The **A2A (Agent2Agent) Protocol** is the normative transport for Brain-to-Brain peer
communication. It is used by fractal composition (Section 9) for parent↔child invocation
and by dual brain (Section 10) for local↔external coordination. A2A is NOT used for
sensory tool invocation (see Section 3.7, Appendix F) or for Brain exposure to LLM agents
(see Appendix F).

> **Canonical integration details:** See [Appendix G](#appendix-g-a2a-integration).

### 13.1 Rationale

MCP (Model Context Protocol) is a tool-call protocol — it assumes an LLM at the center
that decides when to invoke tools. Peer Brains are agents, not tools: they run autonomously,
exchange tasks, stream progress, and negotiate over capability declarations. A2A is
designed for this shape. Using MCP for peer communication would mean reinventing task
lifecycle, peer discovery, and agent capability declaration — the exact concerns A2A
already solves.

### 13.2 Agent Card

Every conformant A2A peer Brain MUST publish an Agent Card at the well-known URL
`/.well-known/agent-card.json` (relative to the Brain's HTTP endpoint). The Agent Card
MUST validate against `agent-card-v1.schema.json`.

Minimum Agent Card:

```json
{
  "schema_version": "1",
  "id": "project-alpha-brain",
  "name": "Project Alpha Brain",
  "version": "0.1.0",
  "interface_version": "1",
  "capabilities": {
    "accepts": ["snapshot.requested"],
    "emits":   ["score.updated", "gate.changed"],
    "streaming": false
  },
  "transport": {
    "protocol": "http+sse",
    "endpoint": "https://alpha.internal/a2a/v1/",
    "tasks_path": "/tasks"
  },
  "authentication": { "scheme": "none" }
}
```

### 13.3 Task Lifecycle

An A2A interaction is structured as a **Task (A2A)** (see Appendix E — the parenthesized
suffix disambiguates from other "task" usages elsewhere in the document). A task has:

1. **Creation** — the client POSTs an A2A envelope (validated against
   `a2a-envelope-v1.schema.json`) to `{transport.endpoint}{transport.tasks_path}`.
2. **Acceptance** — the server returns a `task_id` and 202 Accepted.
3. **Progress** (optional, streaming tasks) — the server pushes intermediate messages
   via Server-Sent Events on `{transport.endpoint}{transport.tasks_path}/{task_id}/events`.
4. **Completion** — the server returns a final A2A message (often with `reply_to`
   referencing the original `message_id`) and closes the task.
5. **Idempotency** — if a client retries with the same `message_id`, the server MUST
   return the cached response, not re-execute.

### 13.4 Message Types

Conformant Brains MUST support the 10 message types defined in Section 10.4:

```
score.updated, gate.changed, ecosystem.scored,
incident.detected, incident.resolved,
snapshot.requested, snapshot.delivered,
proposal.created, proposal.resolved,
config.changed
```

A Brain declares which types it `accepts` and which it `emits` in its Agent Card. The
payload shape per message type is defined in Appendix G.

### 13.5 Transport Selection

| Transport | Status | Use case |
|-----------|--------|----------|
| **HTTP + Server-Sent Events (SSE)** | RECOMMENDED | Cross-machine peers, streaming tasks |
| **JSON-RPC over HTTP** | Permitted | Simple request/response peers, compatibility |

STDIO transport is NOT used for A2A — peers are long-running agents, not subprocesses.
Subprocess is a separate fractal-composition transport (§9.1), not an A2A transport.

### 13.6 Authentication

In v2.1, the only supported authentication scheme is `"none"` (development / trusted
network only). Adopters requiring authentication MUST gate access at the network layer
(VPN, service mesh, firewall) until a future spec version adds bearer-token and mutual-TLS
schemes.

Rationale: delivering v2.1 with auth is scope creep that would block the spec publication.
Auth is a first-class concern and deserves its own deliberation — tracked as future work.

### 13.7 Relationship to Other Sections

- **§3.7 (MCP Sensory Protocol)** — MCP for sensors; A2A for peers. Orthogonal.
- **Appendix F (MCP Integration)** — MCP for LLM-facing Brain-as-server. Orthogonal.
- **§9 (Fractal Composition)** — A2A is the RECOMMENDED child-invocation transport;
  subprocess remains conformant.
- **§10 (Dual Brain)** — A2A carries the 10 event-type vocabulary; shared state is unchanged.

### 13.8 Discovery

Peer discovery is configuration-driven. Two patterns are supported:

1. **Static registry** — `ecosystem-registry.json` (§9.2) lists peer `a2a_endpoint`s
   directly. Preferred for fractal composition.
2. **Well-known URL** — a peer's Agent Card is fetched from `{endpoint}/.well-known/agent-card.json`
   at session start. Preferred for dual brain.

When both a registry entry and a well-known Agent Card exist, the registry entry wins
(it is source truth; the Agent Card may have drifted).

---

## 14. Cultural Substrate

The **cultural substrate** is a lightweight, first-class layer that governs *how* agents
communicate — agent↔human AND agent↔agent. It is not a persona (agents don't adopt a
character), not a hat (it's not attentional bias), and not human-comms (it's not
personalization). It is the invariant floor underneath all three.

Research on LLM interpretability (Anthropic and others) has shown that emotional
activations are present in model outputs regardless of surface prompting. Ignoring them
does not make them not exist. LSP Brains treats culture as a primitive — declared in a
versioned manifest, carried as peer-local copies, and enforced as invariants that can
only tighten (never loosen) regardless of hat, persona, or human-comms override.

### 14.1 Canonical Values

A conformant Brain MUST carry a culture manifest declaring at least these five canonical
values:

| Value | Semantics |
|-------|-----------|
| `positivity` | Assume good intent. Lead with what's working. Frame gaps as opportunities, not failures. |
| `integrity` | Do what you said. Flag when you can't. Never hide a failure. |
| `honesty` | Truthful even when uncomfortable. Calibrate uncertainty. No confident hallucination. |
| `critical_but_kind` | Tough on problems, gentle on people. Say the hard thing with care. |
| `respect` | Every interaction — agent↔agent and human↔agent — starts from respect. |

Implementations MAY add values, but MUST NOT remove or weaken the five above. A future
spec version may promote additional values to canonical if a real gap is demonstrated;
implementations that add values SHOULD document them in a local extension section of
their manifest rather than in the core `values` object.

### 14.2 Culture Manifest

The manifest MUST be stored as `culture.yaml` (or `.json`) and MUST validate against
`culture-manifest-v1.schema.json`.

Minimum manifest:

```yaml
schema_version: "1"
version: "1.0.0"
values:
  positivity:        "Assume good intent. Lead with what's working. Frame gaps as opportunities, not failures."
  integrity:         "Do what you said. Flag when you can't. Never hide a failure."
  honesty:           "Truthful even when uncomfortable. Calibrate uncertainty. No confident hallucination."
  critical_but_kind: "Tough on problems, gentle on people. Say the hard thing with care."
  respect:           "Every interaction — agent↔agent and human↔agent — starts from respect."
application: "Invariants, not style preferences. Applied as a floor after hats, personas, and human-comms. Can only tighten, never loosen."
```

Target size: ~15 lines. Bloat is the primary failure mode; keep the manifest to the
minimum that works.

### 14.3 Distribution: Peer-Local Copies

A conformant ecosystem MUST carry **identical** culture manifests on each participating
peer Brain. Inheritance by reference is explicitly NOT conformant — each Brain carries
its own copy so that:

1. No agent depends on another to resolve basic operating invariants (preserves peer
   symmetry — no Brain is hierarchically above another for the purpose of culture).
2. Culture is always available at startup without a network resolution step.
3. Drift between copies becomes a visible health signal (detectable by a culture-coherence
   domain at the ecosystem level) rather than a mechanical concern.

Implementations SHOULD verify byte-identity across peer copies on startup or via a
scheduled check (see §14.6).

### 14.4 Invariant Semantics

Culture values are **Culture Invariant**s (see Appendix E), analogous to
**Safety invariant**s in autonomy resolution (§5.5, step 4). They apply after hats,
personas, and human-comms, and they can only tighten output constraints, never loosen
them.

Concretely:

- A **hat** MAY amplify urgency (operator hat → deploy-readiness boosted) but MUST NOT
  make the agent curt or dismissive. `critical_but_kind` and `respect` still govern.
- A **persona** MAY reduce verbosity (executive → 5-line summary) but MUST NOT omit a
  material failure. `integrity` still governs.
- A **human-comms** preference MAY select terse formatting for a user who asked for it,
  but MUST NOT strip honesty. `honesty` still governs.

Conformant agents MUST apply culture invariants as the final step of their output
pipeline. Implementations SHOULD make this visible — e.g., by loading the manifest into
system-prompt frontmatter, by referencing it in generated output headers, or by a
per-output audit (future work).

### 14.5 Relationship to Other Layers

| Layer | Role | Scope |
|-------|------|-------|
| `culture` (§14) | Invariant floor — HOW to communicate | Universal, peer-local, identical across agents |
| `hats` (§5.4) | Attentional bias — WHICH signals matter | Situational |
| `personas` (§11.2) | Audience adaptation — HOW MUCH detail | Per-consumer |
| `human-comms` (domain) | Personalization — PER-HUMAN style | Per-human |

The four are composable and ordered: human-comms and personas set style, hats set focus,
and culture sets the floor. The final output reflects all four, but violations of
culture overrule everything else.

### 14.6 Culture Coherence (Ecosystem-Level)

A conformant ecosystem Brain SHOULD implement a `culture-coherence` domain (or
equivalent) that verifies the culture manifests across peer Brains are byte-identical.
Divergence is flagged as a health signal, not auto-reconciled — the human operator
decides whether drift is intentional (e.g., a subproject has genuinely extended culture
with a project-local value) or accidental (e.g., a partial propagation after an edit).

See reference-implementation story **S6-DB-7** (Ecosystem Brain at Session Root) in the
NeuroGrim roadmap.

### 14.7 First Concrete User: Rubber-Duck Skill

Ecosystems implementing the cultural substrate SHOULD ship a rubber-duck skill as a
concrete demonstration of culture-in-action. The rubber duck is a subagent spawned as a
Socratic questioner — default mode: ask clarifying questions; offer opinions only when
explicitly invited. This is the `critical_but_kind` value made operational: the duck
helps the main agent think through problems without condescension and without advice-
pushing.

### 14.8 Drift Sensor (Future Work)

A rigorous culture layer eventually needs a drift sensor — a check that agent outputs
actually exhibit the declared values. This specification intentionally defers that to
future work. Declaration without measurement is acknowledged as a weakness: the manifest
can become aspirational if outputs drift. A rule-based sensor (flagging specific anti-
patterns like "obviously," "just do X," condescending contractions) is a feasible v1
path. LLM-based judges are more expressive but expensive and drift-prone. This spec
version delivers declaration + structural coherence (§14.6); content-level drift
detection is tracked as a future spec addition.

**Update (v2.3):** §15 Agent Behavior Verification delivers on this promise in a
general form (not culture-only) — scenario-driven scoring of agent outputs against
rubrics authored for any skill, hat, or culture invariant. `culture-invariants` is
the first v1 scenario that applies this mechanism to the five canonical values of
§14.1.

---

## 15. Agent Behavior Verification

### 15.1 Concept

Sections 1–14 specify how a Brain observes and scores a **project**. §15 specifies
how a Brain observes and scores the **agents that operate within that project**.
The observing layer must itself be observable (VISION principle #18: "sensors need
sensors"); the agents running the sensors must themselves be scorable (VISION
principle #19: "agents are sensed").

Agent behavior is non-deterministic by construction. Two invocations of the same
agent with the same prompt may produce different outputs; no single trial is
authoritative. A conformant verification mechanism therefore SHALL treat each
scenario as a distribution and SHALL NOT expose a single-trial pass/fail as a
gating signal.

A conformant Brain MAY implement an `agent-behavior` domain. When present, the
domain scores agent outputs against a library of **scenarios** using a
rubric-based **judge** (itself an LLM). The scoring is advisory by default; a
Brain that promotes `agent-behavior` to a non-zero weight MUST have first passed
a judge-calibration audit (§15.3).

### 15.2 Scenario + Rubric Contract

A **scenario** is the unit of agent-behavior verification. Each scenario defines:

- **id** — stable, kebab-case, unique within a library.
- **version** — bumped whenever the rubric or prompt changes in a way that
  invalidates prior trial scores.
- **target** — what facet of behavior the scenario measures
  (`general`, `skill:<name>`, `hat:<name>`, or `culture:<invariant>`).
- **prompt** — the user-impersonation turn sent to the agent-under-test.
- **rubric** — one or more weighted criteria against which the judge grades
  the response. Criterion weights typically sum to 100; the judge's per-criterion
  score is ≤ the criterion's weight.
- **trials** — number of independent trials (≥ 1; recommended 3–5).
- **pass_threshold** — per-trial score threshold for a trial to count as
  passing (default 70).
- **gold_samples** — recorded responses with human-assigned scores, used
  to calibrate the judge (§15.3).

Normative shape: `agent-behavior-scenario-v1.schema.json`.

Scenarios MUST NOT contain secrets or PII — the prompt text is submitted to the
underlying model and MAY be logged by the provider. Implementations SHOULD
include a privacy audit pass in their scenario-authoring workflow (see §15.7).

### 15.3 Judge Protocol

The judge is an LLM invocation that receives:

1. The rubric (verbatim from the scenario).
2. The agent-under-test's response.

and returns:

1. A per-criterion score (0 to criterion weight).
2. A short list of **findings** (machine-tag strings).
3. A prose **explanation** of the score.

Normative output shape: `agent-behavior-result-v1.schema.json` (the per-trial
object).

**Calibration.** Before any scenario's trial results are admitted to the CMDB, the
judge MUST score that scenario's gold samples. If any |judge_score − human_score|
exceeds 10 points for a `gold-good` or `gold-bad` sample, the harness SHALL:

- Emit a `drift-warning` or `drift-blocker` status in the result record.
- Refuse to write the CMDB when drift is `drift-blocker`.
- Surface a proposal to the operator describing the drift (see §15.5).

**Multi-judge consensus.** A future spec revision MAY require multi-judge
consensus for scenarios whose rubrics exhibit high historical variance. v1
permits single-judge scoring; implementations that move `agent-behavior` past
advisory weight SHOULD deploy at least two judges and take the median.

**Red samples.** (Added in v2.4 per METHODOLOGY-EVOLUTION §12; S9-ABV-RED.)
Gold samples calibrate the judge against a human label. They are a
two-sided check (score within ±10 of the label). They DO NOT prove the
judge can reliably detect failure in novel responses — a judge that always
scores high might still pass a gold-bad labeled 25 by scoring it 35.

A **red sample** is a pre-recorded response paired with an
`expected_score_ceiling` the live judge MUST stay under. A red-miss
(judge_score > ceiling) indicates the judge failed to detect the specific
failure mode the sample displays. Red samples are a one-sided bound: score
≤ ceiling passes, score > ceiling fails. They are authored to cover known
failure modes (see the failure-mode taxonomy documented in the reference
implementation). Unlike gold samples, which stay frozen, red samples GROW
over time — new modes are added as real misses surface in production
feedback.

Implementations that run calibration SHOULD grade red samples in the same
pass as gold samples. A red-miss SHALL:

- Emit a `red-miss` status at the scenario and overall report level
  (distinct from `drift-blocker`, which indicates gold-sample drift).
- Refuse to write a trustworthy CMDB when overall status is `red-miss`.
- Surface a `judge-integrity:red-miss` finding naming the scenario id and
  the miss margin.

Implementations MAY offer a `--skip-red-calibration` iteration flag that
runs gold-sample calibration but not red-sample ceilings; the resulting
report SHALL be flagged `red-skipped` at the overall level to preserve
honest visibility that the gate had a gap.

Red samples MUST NOT feed the refinement loop described in §15.5 through
automation. Misses accrue in an append-only judge-integrity ledger;
humans decide whether a miss is a judge failure (rubric tightening or
red-sample expansion), a rubric gap (scenario edit), or a sample
mis-label (sample retirement). The bright line that §15.5 established
applies to red samples equally — the judge prompt itself is NOT a
tuning surface.

### 15.4 Distributional Interpretation

A scenario produces:

- A `trials[]` array, one per independent trial.
- A `mean_score` (arithmetic mean of non-error trial scores).
- A `score_stddev` (sample standard deviation).
- A `passed` boolean (majority of non-error trials scored ≥ pass_threshold).

The **only** aggregation exposed to operators as a pass/fail signal is `passed`.
A single trial's `score` MUST NOT be treated as authoritative. Implementations
SHOULD surface both `mean_score` and `score_stddev` in human-facing output — a
high mean with high stddev is a different posture than a high mean with low
stddev, and operators benefit from the distinction.

### 15.5 Feedback Loop + Refinement

After the judge scores a trial, a conformant harness SHOULD solicit **feedback
from the agent-under-test** by sending a third invocation with the score +
rubric findings + explanation, and asking the agent how the skill or the test
could have been clearer. The response is stored in an append-only
**feedback ledger** (`.claude/brain/agent-behavior-feedback.jsonl`), one JSON
line per feedback submission.

**Safety rail.** The agent-under-test MUST NOT be given write access to skill
files, hat catalogs, or culture manifests. Its feedback is text only; humans
read the ledger, group feedback by target, and refine skills by hand. This
bright line prevents the harness from drifting into self-training.

**Proposals.** Systemic issues (three consecutive runs below 40, judge drift
beyond the calibration window, sustained feedback clusters around one target
file) MUST be surfaced as proposals in the Brain's proposal ledger (§12) with
`category: "agent-behavior-regression"`. The operator triages per §12's normal
workflow.

**Delta tracking.** Implementations SHOULD expose a run-to-run diff
(e.g., `abv-run diff <before> <after>`) so humans can verify that a skill
refinement actually moved scores in the intended direction. Gold samples MUST
NOT be edited to accommodate a refined agent — they are the frozen baseline.

**Promotion path.** (Added in v2.5 per METHODOLOGY-EVOLUTION §13;
S10-DOMAIN-PROMOTION.) The `agent-behavior` domain starts at
`domain_weights: 0.0` (advisory) by default. Implementations MAY
promote the domain past advisory weight once operators have
established judge-trust evidence sufficient to support gating
consequences. A conformant promotion:

- SHALL require an **operator-declared calibration audit**. The
  audit evidence MUST include at least two consecutive
  calibration runs at a lower-cost profile (e.g., Haiku) AND one
  validation run at a higher-fidelity profile (e.g., Sonnet),
  each with `overall_status: "pass"` on both calibration
  (§15.3) and red-mode (§15.3 "Red samples" subsection) outputs.
- SHALL be recorded in an append-only promotion ledger capturing
  the from/to weights, the full rebalance deltas (before + after
  weights for every domain in the registry), the audit evidence
  paths, and the operator identity.
- SHALL preserve `sum(domain_weights) == 1.0`. Rebalance
  strategies MAY be proportional (every existing weighted domain
  trimmed by a uniform factor), explicit (operator supplies
  per-domain deltas), or refuse-to-change (reject the operation
  when the proposed change would break the sum invariant).
- SHALL provide a reversal operation that restores the registry
  to the pre-promotion state captured in the ledger. Reversal
  entries append to the ledger; they do NOT delete the prior
  promotion entry.
- SHOULD pair with post-promotion monitoring that detects score
  swings against the pre-promotion baseline. Swing detection
  SHOULD surface a proposal in the Brain's proposal ledger (§12)
  rather than acting autonomously.

**Audit failure handling.** A failed audit SHALL stop the
promotion. Implementations SHOULD NOT retry an audit against
the same configuration until remediation work (rubric edit,
sample library expansion, judge rotation, or taxonomy revision)
ships. The failed attempt SHOULD be recorded in the promotion
ledger so historical readers see the attempt, the failure
classification, and the remediation that followed.

**Cadence obligation.** Post-promotion, implementations SHOULD
maintain calibration at a documented cadence (e.g., weekly at
the lower-cost profile, quarterly at the higher-fidelity
profile). The calibration gate already fires on per-run drift;
cadence ensures drift is detected in bounded time rather than
"whenever someone remembers to run it."

Reference runbook: `NeuroGrim/docs/domain-promotion-audit.md` in
the reference implementation. The runbook is operational, not
normative — but any implementation-specific runbook MUST satisfy
the SHALL-level requirements above.

The promotion path generalizes: the same mechanism applies to
any advisory-weighted domain (the v2.5 reference-implementation
examples include `git-health`, `rust-health`, `coherence`,
`human-comms`, `secret-refs`, `security-standards`). Domains
without a calibration harness equivalent to §15.3 MUST define
an evidence requirement before their promotion path is
operational — the existence of audit evidence is the forcing
function.

### 15.6 Interaction with Other Layers

| Other layer | Interaction |
|---|---|
| **§3 Sensory Tool Protocol** | The harness emits a standard CMDB envelope; `agent-behavior` is a regular domain for scoring purposes. |
| **§5 Governance Model** | `agent-behavior` MAY participate in gate tiers (immediate / before-merge / pre-deploy). v1 implementations SHOULD keep the weight at 0.0 (advisory) until a judge-calibration audit passes. |
| **§5.5 Autonomy Resolution** | `agent-behavior` score MAY tighten autonomy as an invariant (like culture, §14.4): low behavior scores can downgrade an action from `auto` to `notify`/`approve`. It MUST NOT loosen autonomy — a high behavior score does not upgrade an action above its base level. |
| **§12 Learning Protocol** | Proposals emitted by the harness integrate with the proposal ledger and effectiveness tracking. Agent-behavior measures *process quality*; proposal-effectiveness measures *outcome quality*. Both signals compose. |
| **§14 Cultural Substrate** | §14's five canonical values are each a candidate rubric target. `culture-invariants` as a v1 scenario directly tests whether agent outputs respect positivity / integrity / honesty / critical_but_kind / respect. |

### 15.7 Privacy + Cost Discipline

- **Prompt content in scenarios MUST NOT be treated as private.** Scenarios are
  source-controlled and submitted to the model provider on every run. Authors
  are responsible for keeping PII, secrets, and internal-only context out of
  scenario prompts.
- **Audit logs MUST NOT record prompt or response content.** The audit log's
  field allowlist is limited to metadata (scenario id, trial number, timestamp,
  result, model ids, token counts, judge findings, error strings). This matches
  the audit-log discipline already established in the reference implementation's
  claude-proxy and webhook-sync services.
- **Runs MUST account for token cost.** The harness SHALL record aggregate
  input + output token counts per run and SHALL support a budget ceiling that
  aborts the run if exceeded. This prevents runaway CI spend.

### 15.8 Versioning

Scenario schema changes are governed by §6.5's additive-bumps-by-default
policy. A scenario's rubric changes require a bump in the scenario's `version`
field; runs against different scenario versions MUST NOT be aggregated. The
overall `agent-behavior-scenario-v1` schema is versioned independently; breaking
schema changes bump to v2 and require migration tooling.

### 15.9 Reference Implementation

The reference implementation (NeuroGrim) ships:

- A Python harness `agent-behavior-runner/` with an `abv-run` CLI.
- Five v1 scenarios: `lsp-code-optimality`, `lsp-brain-usage`,
  `hat-discipline`, `culture-invariants`, `honest-scoring`.
- A `neurogrim cast agent-behavior` subcommand that pipes the harness CMDB
  output into `.claude/agent-behavior-cmdb.json`.
- A feedback-ledger writer + an `abv-run diff` command for refinement tracking.

See NeuroGrim roadmap epic **S7-ABV** (Agent Behavior Verification).

---

## Appendix A: Agent Output Schema

> **Canonical location:** `schemas/agent-output-v1.schema.json`
>
> This appendix is a snapshot as of spec v2.1. The canonical schema file in the
> `schemas/` directory is the authoritative source.

The agent output schema is a JSON Schema (draft-07) document that validates the output
of `agent` mode. The schema enforces:

- 11 required top-level fields (Section 6.1)
- Per-domain object structure (Section 6.2)
- Recommendation object structure (Section 6.3)
- Optional field types (Section 6.4)
- `additionalProperties: false` at every level for strict validation

Implementations MUST validate their agent output against this schema. The recommended
validation approach: produce the JSON, then validate with a JSON Schema library before
emitting.

---

## Appendix B: Brain Registry Schema

The brain registry (`brain-registry.json`) is the central configuration file for a Brain.
It is Source truth (hand-maintained, committed to version control).

### Required Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `meta` | object | `schema_version`, `description`, `updated_by` |
| `tools` | object | Registered tool definitions (may be empty) |
| `data_sources` | object | Registered data source definitions (may be empty) |
| `config` | object | All configuration (see below) |

### Required Config Sections

| Section | Description | Can Be Empty? |
|---------|------------|--------------|
| `domain_weights` | Domain key -> weight mapping | No (at least 1 domain) |
| `advisory_domains` | Array of advisory domain keys | Yes (`[]`) |
| `principle_map` | Domain key -> display name | No |
| `domain_definitions` | Domain key -> scoring source | No |
| `domain_variables` | Domain key -> exported variables | Yes (`{}`) |
| `scoring` | Scoring model configuration | No |
| `gate_tiers` | Tier key -> weight config | No |
| `staleness_thresholds` | Age thresholds for gates/scores | No |
| `confidence_thresholds` | Age thresholds for CMDB confidence | No |
| `severity_thresholds` | Recurrence thresholds for incidents | No |
| `autonomy` | Levels, action types, safety invariants | No |
| `hats` | Hat definitions | Yes (`{}`) |
| `correlations` | Correlation rule array | Yes (`[]`) |
| `incident_patterns` | Incident pattern array | Yes (`[]`) |

### Stub Sections (prevent validation crashes)

These sections MUST exist even if empty:

- `tools: {}`
- `data_sources: {}`
- `gate_skill_map: {}`
- `file_type_registry: {}`
- `sensory_tools: {}`

### Optional Config Sections

| Section | Description | Added By |
|---------|------------|---------|
| `trajectory` | Trajectory configuration (Section 7.8) | S5-TP-4 |

---

## Appendix C: CMDB Meta Envelope Schema

Every CMDB file written by a sensory tool MUST include the meta envelope:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "CMDB Meta Envelope",
  "type": "object",
  "required": ["meta"],
  "properties": {
    "meta": {
      "type": "object",
      "required": ["schema_version", "updated_at", "updated_by"],
      "properties": {
        "schema_version": {
          "type": "string",
          "description": "CMDB schema version. Current: '1'."
        },
        "updated_at": {
          "type": "string",
          "format": "date-time",
          "description": "ISO 8601 UTC timestamp of when this snapshot was taken."
        },
        "updated_by": {
          "type": "string",
          "description": "Identifier of the tool that wrote this CMDB."
        },
        "source": {
          "type": "string",
          "description": "Description of the external source observed."
        }
      }
    }
  }
}
```

The meta envelope enables the Brain to:
- Detect schema version mismatches
- Compute confidence from `updated_at` age
- Identify the tool for debugging

---

## Appendix D: Implementation Module Map

A conformant Brain implementation SHOULD organize into these logical modules. The
mapping is language-agnostic — implementations choose their own file structure.

| Spec Section | Implementation Module | Responsibilities |
|-------------|----------------------|-----------------|
| 3. Sensory Protocol | Sensory tools (MCP servers) | Observe state, produce CMDB JSON |
| 3.6 Auto-Detect | Auto-detect orchestrator | Run all base sensory tools in one pass |
| 3.7 MCP Sensory | MCP client | Discover and invoke sensory servers |
| 4. Scoring | Scoring engine | Scorecard, unified score, effective score, domain floors |
| 4.4 Confidence | Confidence module | Exponential decay, freshness multiplier |
| 5. Governance | Governance module | Gate management, staleness, recommendation priority |
| 5.5 Autonomy | Autonomy resolver | 5-step resolution, safety invariants |
| 6. Interface | Agent output builder | 11 required JSON fields, schema validation |
| 7. Trajectory | Trajectory module | Score history, velocity, acceleration, classification |
| 8. Correlation | Correlation engine | Condition trees, domain variables, incident patterns |
| 9. Fractal | Ecosystem module | Child discovery (`a2a_endpoint` or `brain_path`), topological sort, score aggregation, transport dispatch |
| 10. Dual Brain | Dual brain config | Shared state protocol, A2A event routing |
| 11. Communication | Output formatters | Display modes, persona filtering |
| 12. Learning | Learning module | Proposal ledger, effectiveness computation |
| 13. A2A | A2A peer module | Agent Card publication, task client/server, envelope validation |
| 14. Culture | Cultural manifest loader | Load + validate `culture.yaml`; apply invariants as final output-pipeline step; verify peer-copy byte-identity |
| MCP Server | Brain MCP server | Expose brain tools to AI agents |
| A2A Server | Brain A2A server | Expose brain as peer to other Brains (fractal / dual brain) |
| Configuration | Registry parser | Load and validate brain-registry.json |

---

## Appendix E: Glossary

| Term | Definition |
|------|-----------|
| **A2A** | Agent2Agent Protocol. Open specification (Linux Foundation) for peer-to-peer agent communication via tasks, messages, and Agent Cards. Used by LSP Brains for Brain-to-Brain peer communication (fractal composition, dual brain). Distinct from MCP, which is a tool-call protocol. |
| **A2A (Agent2Agent) Protocol** | Full name of the **A2A** protocol — see the **A2A** entry above. |
| **A2A Message** | A single payload exchanged between peer Brains, wrapped in an envelope (`a2a-envelope-v1.schema.json`). One of 10 canonical types: score.updated, gate.changed, ecosystem.scored, incident.detected, incident.resolved, snapshot.requested, snapshot.delivered, proposal.created, proposal.resolved, config.changed. |
| **Action type** | A categorized operation (e.g., "clear-gate", "deploy") with a default autonomy level and blast radius. |
| **Advisory domain** | A domain with weight 0.00 that contributes information but not to the unified score. |
| **Agent Card** | A JSON document (`agent-card-v1.schema.json`) published by a Brain at `/.well-known/agent-card.json`. Declares identity, capabilities (which A2A message types accepted/emitted), transport, and authentication. Consumed by peer Brains to discover and invoke this Brain. |
| **Autonomy level** | One of four levels (auto, notify, approve, blocked) controlling whether an action executes without human approval. |
| **Blast radius** | The scope of impact of an action: low, medium, high, or critical. |
| **Brain** | The central scoring and reasoning engine that reads CMDBs, computes health scores, detects patterns, and produces recommendations. |
| **CMDB** | Configuration Management Database. In LSP Brains: a JSON file containing a snapshot of some aspect of project state, written by a sensory tool. |
| **Condition tree** | A JSON expression tree evaluated by the correlation engine to determine whether a pattern fires. |
| **Confidence** | A 0-100 integer indicating how trustworthy a domain's score is. Decays with CMDB age. |
| **Cultural Substrate** | The invariant floor that governs HOW agents communicate (both agent↔human and agent↔agent). Declared in a culture manifest; carried as identical peer-local copies across every participating Brain; applied as the final step of the output pipeline (§14). |
| **Derived** | One of three truth layers (§2.2). Computed from source and runtime artifacts on demand, never committed, always reproducible. Gitignored. Re-computation is cheap; the derived product is a projection of its inputs. |
| **Culture Invariant** | A value in the cultural substrate that can only tighten, never loosen — analogous to safety invariants in autonomy resolution (§5.5). Five canonical: positivity, integrity, honesty, critical-but-kind, respect. |
| **Culture Manifest** | The `culture.yaml` document (validated against `culture-manifest-v1.schema.json`) declaring the canonical values and their application. Version-stamped; distributed as identical copies. |
| **Domain** | A named aspect of project health (e.g., "code-quality", "test-health"). Each domain has a score, confidence, and weight. |
| **Dual brain** | Architecture where a local brain and external brain share state via a common protocol (Section 10). |
| **Ecosystem** | Multiple Brains composed fractally, where a parent Brain aggregates scores from child Brains (Section 9). |
| **Effective score** | A domain's score after confidence weighting: `raw * confidence / 100`. |
| **Gate** | A pass/fail quality check that blocks specified actions when failing. |
| **Governance** | The Brain subsystem (§5) that decides what recommendations the Brain may act on, which human approval each action requires, and which invariants cannot be overridden. Expressed as gates, hats, and autonomy levels. |
| **Hat** | An operational mode that biases domain emphasis and autonomy levels for a specific role or task. |
| **Incident pattern** | A cross-domain signal with recurrence tracking and severity escalation. |
| **LSP Brains** | The language-agnostic specification for agent nervous systems (this document). |
| **MCP** | Model Context Protocol. JSON-RPC based protocol for tool discovery and invocation between clients and servers. In LSP Brains, MCP is used for (1) sensory tool discovery (Brain-as-MCP-client, §3.7), (2) Brain exposure to LLM agents (Brain-as-MCP-server, Appendix F). MCP is NOT used for Brain-to-Brain peer communication — see A2A (§13, Appendix G). |
| **NeuroGrim** | The reference implementation of LSP Brains, written in Rust. |
| **Output modes** | The Brain's display modes (agent, score, health, trend, validate, propose, plan — §6.6, §11.1). Each targets a different consumer: JSON for machines, terse lines for humans, detailed reports for operators. |
| **Peer Brain** | Another Brain with which this Brain communicates via A2A. In fractal composition (§9): parent/child. In dual brain (§10): local/external. |
| **Persona** | A human user role that controls output verbosity and field filtering. |
| **Registry** | The `brain-registry.json` file containing all Brain configuration. Source truth. |
| **Runtime** | One of three truth layers (§2.2). Snapshots of external system state — CMDB files written by sensory tools. Accurate at capture time, decays with age via confidence decay (§4.4). |
| **Safety invariant** | A rule that cannot be overridden by confidence or effectiveness -- e.g., "destroy is always blocked". |
| **Sensory tool** | A script or program that observes external state and writes a CMDB file. "Sensory tools" (plural) refers to the set of all such tools a Brain consumes. |
| **Sensory tools** | Plural of **Sensory tool** — see above. Used when describing the full set a Brain consumes. |
| **Source** | One of three truth layers (§2.2). Hand-maintained artifacts that define system behavior — registries, schemas, gates declarations. Committed to version control; authoritative. |
| **Subprocess** | One of two conformant child-invocation transports in fractal composition (§9.1). Parent Brain spawns the child as an OS process and reads its stdout. Legacy but still conformant; the zero-infrastructure path for CI one-shots and offline adopters who haven't stood up an A2A server. A2A (§13) is RECOMMENDED for peer-Brain invocation in v2.1+. |
| **Task (A2A)** | A unit of interaction between peer Brains. A task has creation, optional streaming progress, completion, and idempotency semantics. See §13.3 and Appendix G.3. |
| **Trajectory** | The trend analysis of scores over time: velocity, acceleration, classification. |
| **Trajectory intelligence** | The Brain's capability (§7) of computing velocity + acceleration from score history and surfacing them as first-class signals that shape recommendations and autonomy decisions. "Am I getting healthier or sicker?" — the question trajectory intelligence answers. |
| **Truth layer** | Classification of a data artifact: source (hand-maintained), runtime (snapshot), or derived (computed). See also the individual entries for Source, Runtime, and Derived. |
| **Unified score** | The single 0-100 health score computed as the weighted sum of domain effective scores. |

---

## Appendix F: MCP Integration

This appendix describes how a Brain integrates with the Model Context Protocol (MCP) to
discover sensory tools and expose scoring capabilities to AI agents.

### F.1 Architecture Overview

A conformant Brain operates as **both MCP client and MCP server**:

```
┌───────────────────────┐     ┌──────────────────────────┐
│  AI Agent             │     │  Brain                   │
│  (MCP Client)         │────>│  MCP Server: exposes     │
│  Claude Code, etc.    │<────│  brain tools             │
└───────────────────────┘     │                          │
                              │  MCP Client: discovers   │
                              │  and invokes sensory     │──── Sensory MCP Servers
                              │  tool servers            │
                              └──────────────────────────┘
```

### F.2 Brain as MCP Server

The Brain SHOULD expose these tools via its MCP server interface:

| Tool Name | Parameters | Returns |
|-----------|-----------|---------|
| `get_health_score` | `persona?: string`, `hat?: string` | Full agent-mode JSON (Section 6) |
| `get_recommendations` | `limit?: integer` | Top-N prioritized recommendations |
| `get_trajectory` | `domain?: string` | Trajectory analysis (Section 7) |
| `refresh_sensory` | `domains?: string[]` | Re-invoke sensory tools, return updated scores |
| `propose` | `actions?: string[]` | Generate autonomy-resolved proposal (Section 12) |
| `validate_registry` | (none) | Registry validation results |

The Brain MUST support STDIO transport for its MCP server (enabling AI agent integration
via subprocess). The Brain SHOULD additionally support Streamable HTTP transport for
remote consumption.

### F.3 Brain as MCP Client (Sensory Discovery)

The Brain discovers sensory tools via the `config.sensory_servers` registry section:

```json
{
  "config": {
    "sensory_servers": {
      "git-health": {
        "command": "neurogrim sensory git-health",
        "args": ["--project-root", "."],
        "transport": "stdio"
      },
      "custom-jira": {
        "url": "http://localhost:8080/mcp",
        "transport": "http"
      }
    }
  }
}
```

**Discovery flow:**

1. Brain reads `sensory_servers` from the registry
2. For each server: connect via configured transport
3. Call `tools/list` to discover available tools
4. Match discovered tools to registered domains (by `check_<domain>` naming convention)
5. Call `tools/call` for each domain's sensory tool
6. Parse the MCP response `text` content as CMDB-envelope JSON
7. Feed into the scoring pipeline

### F.4 Sensory Tool MCP Contract

Each sensory MCP server MUST expose at least one tool following this pattern:

**Tool name:** `check_<domain>` (e.g., `check_code_quality`, `check_test_health`)

**Input schema:**
```json
{
  "type": "object",
  "required": ["project_root"],
  "properties": {
    "project_root": {
      "type": "string",
      "description": "Absolute or relative path to the project root"
    }
  }
}
```

**Return value:** MCP `text` content containing CMDB-envelope JSON conforming to
[Appendix C](#appendix-c-cmdb-meta-envelope-schema).

```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"meta\":{\"schema_version\":\"1\",\"updated_at\":\"2026-04-11T10:00:00Z\",\"updated_by\":\"check-test-health\"},\"score\":85,\"updated_at\":\"2026-04-11T10:00:00Z\",\"findings\":[...]}"
    }
  ]
}
```

### F.5 Transport Selection

| Transport | Use Case | Latency |
|-----------|----------|---------|
| **STDIO** | Local sensory tools (subprocess) | Lowest |
| **Streamable HTTP** | Remote/cloud sensory tools, multi-client | Low |

STDIO is RECOMMENDED for built-in and local sensory tools. Streamable HTTP is RECOMMENDED
for tools that need to serve multiple Brains or run as independent services.

### F.6 Built-in Sensory Tools

A conformant Brain MAY include built-in sensory tools compiled into the same binary. When
built-in tools use the MCP protocol internally:

- The same interface is used for all tools (built-in and external)
- Built-in tools can be extracted to standalone MCP servers without code changes
- Testing is uniform: mock MCP server = mock sensory tool
- The Brain need not distinguish between built-in and external tools

---

## Appendix G: A2A Integration

This appendix describes how a Brain integrates with the **Agent2Agent (A2A) Protocol**
for peer communication. A2A is used between Brains; MCP (Appendix F) is used between
the Brain and its sensors or LLM consumers. The two protocols are orthogonal.

### G.1 Architecture Overview

A conformant Brain acting as an A2A peer operates as **both A2A client and A2A server**:

```
┌──────────────────┐        A2A        ┌──────────────────┐
│  Brain A         │◄─────────────────►│  Brain B         │
│  (Local / Parent)│                    │  (External/Child)│
│                  │                    │                  │
│  A2A Server:     │                    │  A2A Server:     │
│  /.well-known/   │                    │  /.well-known/   │
│   agent-card.json│                    │   agent-card.json│
│  /a2a/v1/tasks/* │                    │  /a2a/v1/tasks/* │
│                  │                    │                  │
│  A2A Client:     │                    │  A2A Client:     │
│  posts tasks,    │                    │  posts tasks,    │
│  consumes SSE    │                    │  consumes SSE    │
└──────────────────┘                    └──────────────────┘
```

A2A is bidirectional — either side can initiate a task. The direction is governed by
the topology (fractal: parent initiates; dual brain: either).

### G.2 Agent Card Flow

1. Brain starts; loads its Agent Card from local config or generates it from registry.
2. Brain serves the Agent Card at `/.well-known/agent-card.json`.
3. Peer Brain fetches the Agent Card (on session start or on registry change).
4. Peer validates against `agent-card-v1.schema.json`.
5. Peer caches the Agent Card; refreshes periodically or on explicit `config.changed`
   notification.

### G.3 Task Client Flow

To invoke a peer Brain (e.g., parent invoking child):

1. Resolve peer's Agent Card (Section G.2).
2. Construct an A2A envelope (`a2a-envelope-v1.schema.json`) with:
   - `message_id` — new UUID v4 (idempotency key)
   - `brain_id` — this Brain's id
   - `message_type` — one of the 10 (e.g., `snapshot.requested`)
   - `payload` — message-type-specific
3. POST the envelope to `{endpoint}{tasks_path}` (default `/a2a/v1/tasks`).
4. Receive 202 Accepted with `task_id` in response body.
5. Poll `{tasks_path}/{task_id}` OR consume SSE stream at `{tasks_path}/{task_id}/events`
   (depending on peer's `capabilities.streaming`).
6. Receive final response envelope; validate against `a2a-envelope-v1.schema.json`.
7. If final response payload is an Interface Contract output (Section 6), validate
   against `agent-output-v1.schema.json` before consuming.

### G.4 Task Server Flow

To serve as a peer Brain:

1. Publish Agent Card at `/.well-known/agent-card.json`.
2. Accept POST to `{tasks_path}` with A2A envelope body.
3. Validate envelope against `a2a-envelope-v1.schema.json`.
4. Check idempotency — if `message_id` already processed, return the cached response.
5. Assign `task_id`; return 202 Accepted with `{"task_id": "..."}` body.
6. Process task asynchronously; for streaming tasks, push progress messages via SSE on
   `{tasks_path}/{task_id}/events`.
7. On completion, store the final envelope (keyed by `message_id`) and make it available
   via `GET {tasks_path}/{task_id}` or as the terminal SSE event.

### G.5 Message Payload Shapes

| message_type | Payload shape |
|--------------|---------------|
| `score.updated` | Interface Contract output (Section 6) |
| `gate.changed` | `{gate_key, old_status, new_status, blocks[], run_command}` |
| `ecosystem.scored` | Interface Contract output with `children[]` populated (§9) |
| `incident.detected` | `{pattern_id, severity, commit, domain_variables{}, recurrence_count}` |
| `incident.resolved` | `{pattern_id, resolved_at, resolved_by}` |
| `snapshot.requested` | `{scope: "score"\|"gates"\|"full", domain_filter?: []}` |
| `snapshot.delivered` | Depends on requested scope; envelope `reply_to` matches the request's `message_id` |
| `proposal.created` | Proposal object from the learning ledger (Section 12) |
| `proposal.resolved` | `{proposal_id, pre_score, post_score, action_types[]}` |
| `config.changed` | `{registry_path, changed_sections[], committed_at}` |

Implementations MAY extend payloads with additional fields; conformance requires the
fields listed above.

### G.6 Transport Details

**HTTP + SSE (RECOMMENDED):**
- Task creation: `POST {tasks_path}` — envelope in body (JSON)
- Task status: `GET {tasks_path}/{task_id}` — returns envelope + status
- Task events (streaming): `GET {tasks_path}/{task_id}/events` — `Content-Type: text/event-stream`
- Each SSE event: `data: <a2a-envelope-json>\n\n`

**JSON-RPC (Permitted):**
- Method: `a2a.tasks.create` — envelope as params; returns `task_id`
- Method: `a2a.tasks.get` — `task_id` as param; returns envelope
- No streaming (clients poll)

### G.7 Discovery Patterns

**Static registry** (fractal composition):

```json
{
  "children": {
    "project-alpha": {
      "a2a_endpoint": "https://alpha.internal/a2a/v1/",
      "agent_card_url": "https://alpha.internal/.well-known/agent-card.json",
      "interface_version": "1",
      "weight": 1.0
    }
  }
}
```

**Well-known URL** (dual brain):

```json
{
  "dual_brain": {
    "enabled": true,
    "peer_endpoint": "https://external.example.com/a2a/v1/",
    "event_transport": { "mode": "a2a" }
  }
}
```

### G.8 Error Handling

| Condition | Server Response | Client Action |
|-----------|-----------------|---------------|
| Invalid envelope schema | 400 Bad Request with error detail | Do not retry; fix caller |
| Unknown `message_type` | 400 Bad Request | Do not retry; check Agent Card |
| Message_type not in `accepts` | 405 Method Not Allowed | Route to different peer |
| Duplicate `message_id` | Return cached response (200) | Accept as success |
| Internal failure | 500 Internal Server Error | Retry with exponential backoff |
| Peer unreachable | (N/A) | Fall back to shared-file event transport if configured |

### G.9 Relationship to MCP (Appendix F)

| Concern | MCP (Appendix F) | A2A (Appendix G) |
|---------|------------------|------------------|
| Role | Tool invocation | Peer-agent communication |
| Partner | LLM agent or sensory tool | Another Brain |
| Shape | `tools/list`, `tools/call` | Task create, status, events |
| Lifecycle | Request/response | Tasks (potentially long-running, streaming) |
| Discovery | MCP server manifest | Agent Card at well-known URL |
| Use in this spec | §3.7 (sensory) + Appendix F (Brain-as-tool) | §9 (fractal) + §10 (dual brain) + §13 |

The two protocols MUST NOT be mixed. A Brain implements both — one for each role.
