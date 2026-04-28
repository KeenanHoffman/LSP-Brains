# LSP Brains Specification

> **A declared overlay of project-shaped commitments on a general-purpose statistical
> engine.** The LLM provides cognition; the Brain provides what to be cognizant of.
> This specification defines the language-agnostic primitives — sensory tools, scoring
> contracts, governance gates, trajectory intelligence, and peer-Brain coordination.
> NeuroGrim is the Rust reference implementation.

**Version:** 3.0
**Date:** 2026-04-27
**Status:** Stable v3.0

### Changelog

- **v3.0 (2026-04-27):** Stability-marker release. Closes the Brains-2.0
  self-observability campaign (E-B2-1..E-B2-7) by promoting v2.7→v2.12 to a
  stable consolidated v3.0 baseline. **No section-content changes.** All seven
  Brains-2.0 primitives (confidence as first-class envelope §3.8, self-coherence
  + domain-calibration ledgers §17, hat-as-formal-contract §5.4.1, trust-budget
  §16.8, METHODOLOGY-EVOLUTION §16 multi-round assessment, operator-calibration §17.12,
  federated patterns A2A §16.6.1) ship advisory (weight 0.0) across all four
  Brains in the ecosystem. v3.0 is **additive over v2.x**; deprecation track
  deferred to v4.0 (no symbols are deprecated, removed, or withdrawn at this
  release). Calibration windows (≥30-day self-coherence, ≥50 operator-calibration
  records) per the Charter Amendment 2026-04-27 are post-publish observation
  windows feeding a v3.1 calibration-report gate. See
  `audit/BRAINS-2-0-RETROSPECTIVE-2026-04-27.md` for the campaign retrospective
  and METHODOLOGY-EVOLUTION §16 multi-round assessment cadence applied to the Brains-2.0
  campaign close.

- **v2.12 (2026-04-27):** Federated patterns A2A primitive (Brains-2.0
  E-B2-7) — the first cross-Brain primitive in the campaign.

  New §16.6.1 (Federated Pattern Sharing) extends §16.6 (A2A Signal
  Sharing) with a parallel-construction `federated-pattern` A2A message
  type carrying anonymized pattern features between peer Brains under
  the same bidirectional opt-in posture as the v2.6 supply-chain-signal
  precedent. New schema `a2a-federated-pattern-v1.schema.json` formalizes
  the wire format; new schema `pattern-aggregation-ledger-v1.schema.json`
  formalizes the per-Brain `pattern-aggregation-ledger.jsonl` which
  records both received and emitted federated-patterns with `oneOf`
  row-kind discrimination.

  RFC 2119: implementations SHOULD ship the federated-pattern surface;
  Brains lacking it remain conformant — federation is opt-in via Agent
  Card capabilities (mirrors §16.6 supply-chain-signal posture).

  **Closed-set `pattern_kind` vocabulary at v1: `vigilance-pattern`
  (single value).** Future kinds (operator-calibration-pattern,
  hat-contract-pattern, trust-budget-pattern) require additive spec
  change. Same closed-set discipline as §5.4.1 hat-contract tool
  names + §16.8 trust-budget enums + §17.12 disposition kinds.

  **Privacy under composition (Q1+Q8 lock).** `feature_vector` is
  closed-set numeric-only at v1: `numeric_count`, `severity_class`
  (closed-set enum), `observation_window_days`. NO strings, NO file
  paths, NO FQDNs, NO operator handles, NO per-skill names. Bounded
  numeric features cannot exfiltrate operator-specific patterns the
  way free-text could. Schema's `additionalProperties: false` on the
  payload AND on FeatureVector enforces this structurally.

  **BR-6 signal-flooding mitigation (Q6 lock).** Two-layer rate limit:
  sender-side `tokio::sync::Semaphore` (max 10 federated-pattern
  messages per peer per minute) + receiver-side sliding-window
  drop-and-log past threshold. Drops captured as
  `entry_kind=received, dropped_reason=rate-limit-exceeded` rows in
  the pattern-aggregation-ledger. Mirrors R2-2 pattern from
  supply-chain-vigilance.

  **Recursion guard (Q9 lock — MUST).** Two-layer mitigation. Wire-
  level: every federated-pattern carries `origin_set[]` array of
  opaque brain-id hashes (sender + relayers); receiver MUST validate
  `origin_set[]` does not contain its own opaque hash, dropping with
  `dropped_reason=recursion-guard` if so. Source-level: the
  federated-patterns aggregator sensor's own findings (kind prefix
  `federated_patterns:*`) MUST NOT be transmittable as
  federated-patterns. Closed-loop by construction.

  **Topology (Q16 lock — LOCAL).** v1 federation flows EXCLUSIVELY
  parent↔child within the existing fractal-composition tree
  (`brain-registry.json:children`). Sibling federation and cross-tree
  federation are v2 candidates per BACKLOG B-23.

  **No reputation decay at v1 (Q7 lock).** v1 ships flat trust + flat
  rate-limit + drop-and-log; the data captured in the
  pattern-aggregation-ledger is the substrate for v3 reputation
  calibration per BACKLOG B-23. Federation is observability-only at v1
  — no findings to gate on.

  **Operator-explicit emission at v1 (Q2 lock).** No automatic
  emission on score-update. The reference CLI `neurogrim
  federated-pattern emit` is operator-invoked. Auto-emission is a v2
  candidate per BACKLOG B-23 — same discipline as E-B2-6 explicit-only
  disposition CLI.

  Out of scope at v1: per-skill aggregation, real-time correlation
  feedback, hard gates, transitive federation auto-relay, cross-Brain
  reputation sharing. All BACKLOG B-23.

  Additive only — no v2.11 conformance claim invalidated. Reference
  implementation: NeuroGrim crates `neurogrim-a2a::federated_pattern`
  + `neurogrim-sensory::federated_patterns` + CLI
  `neurogrim federated-pattern`. Per-epic Layer-2 plan in
  `~/.claude/plans/brains-2-0-e-b2-7-layer-2.md`. See
  `METHODOLOGY-EVOLUTION.md` §15 for rationale (federated patterns
  extend the §16.6 supply-chain A2A signal-sharing precedent under
  the same bidirectional opt-in posture).

- **v2.11 (2026-04-27):** Operator-calibration primitive (Brains-2.0
  E-B2-6).

  Per-Brain operator-calibration captures the operator's judgment of
  agent skill invocations as append-only disposition records on the
  existing invocation-ledger (additive; NOT a new ledger). New
  schema `invocation-ledger-v1.schema.json` formalizes the existing
  skill-record shape AND introduces a sibling DispositionEntry row
  kind discriminated via `oneOf`. Closed-set 4-entry vocabulary:
  `accepted`, `rejected`, `modified`, `superseded` — same additive
  promotion path as §5.4.1 hat-contract tool names + §16.8
  trust-budget enums.

  RFC 2119: `neurogrim disposition record` CLI is RECOMMENDED
  (SHOULD), not MUST. Brains lacking the disposition CLI remain
  conformant; the operator-calibration sensor reports
  `low_confidence` until N_MIN=20 dispositions accrue. Hard-gate
  elevation deferred to v2 per BACKLOG B-23 — gated on calibration
  data + §15.5 evidence-bundle review (NOT automated promotion).

  **Privacy contract reaffirmed (BR-5).** Disposition records
  preserve the invocation-ledger's v1 privacy invariant: closed-set
  `disposition_kind` + ts + invocation_id + human_operator ONLY.
  Implementations MUST NOT capture free-text justification on
  disposition records at v1 (the schema's `additionalProperties:
  false` on DispositionEntry enforces this structurally). v2 may
  reopen with strict prose-only-no-paths discipline + dedicated
  opt-in.

  **Recursion guard (MUST).** The operator-calibration sensor's own
  findings (kind prefix `operator_calibration:*`) MUST NOT be valid
  disposition targets. Implementations MUST verify (e.g., the CLI
  rejects matching `--invocation-id` references at parse time).

  **Aggregation-only export (MUST).** The operator-calibration
  sensor's CMDB output MUST emit aggregate totals only — no
  per-invocation rows, no per-skill breakdowns at v1.

  **Sample-size disclosure (MUST).** The sensor MUST report
  `dispositioned_count` AND `total_invocations` as exported
  variables alongside any score. Score MAY be `null` when
  `dispositioned_count < N_MIN`.

  **Per-Brain scope (LOCAL).** Implementations MUST NOT auto-share
  disposition entries via A2A in conformant v1 deployments
  (mirrors §17.8). Cross-Brain `operator-calibration-signal` is a
  v2 candidate per BACKLOG B-23.

  Out of scope at v1: auto-inference from session traces (requires
  invocation-ledger schema bump deferred to B-23, parallel to
  E-B2-3 v2 runtime hat-enforcement and E-B2-4 v2 runtime shell-out
  tracking); per-skill calibration breakdown; hat-scoped
  disposition; A2A signal type; per-operator score breakdown for
  multi-operator topologies.

  Additive only — no v2.10 conformance claim invalidated.
  Reference implementation: NeuroGrim crate
  `neurogrim-sensory::operator_calibration` + CLI
  `neurogrim disposition record`. Per-epic Layer-2 plan in
  `~/.claude/plans/brains-2-0-e-b2-6-layer-2.md`. See
  `METHODOLOGY-EVOLUTION.md` §13 for rationale (operator-calibration
  is the first-class evidence input for governance-via-evidence
  domain promotion).

- **v2.10 (2026-04-27):** Trust budget primitive (Brains-2.0 E-B2-4).

  Per-Brain `trust-budget.toml` (committed at repo root) declares the
  third-party crate / shell-out / external-service surface as a
  schema-typed contract conforming to `trust-budget-v1.schema.json`.
  Closed-set vocabulary: 4-entry `ecosystem` enum (cargo, pypi, npm,
  system); 4-entry `trust_posture` enum (api_only, official_registry,
  operator_audited, vendor_attested) — same additive discipline as
  §5.4.1 hat-contract tool names.

  RFC 2119: `trust-budget.toml` is RECOMMENDED (SHOULD), not MUST.
  Brains lacking the file remain conformant; sensor flags absence as
  advisory finding only. Hard-gate elevation deferred to v2 per
  BACKLOG B-23 — gated on calibration data, mirroring the §16.4
  v1→v2 advisory-before-strict discipline.

  Composes with §5.4.1 hat contracts: trust-budget reads
  `forbidden_tools[]` + `network_targets.allowed[]` to surface per-hat
  composition findings. v1 is static-only — runtime tool tracking
  parallels §5.4.1 v2 runtime enforcement (also B-23).

  Drift findings emit two distinct kinds:
  `trust_budget:undeclared:*` (actual surface not in declaration)
  and `trust_budget:overdeclared:*` (declaration not in actual
  surface). Both advisory weight 0.0.

  Out of scope at v1: transitive crate budgets (BR-3 mitigation —
  flagging on Cargo.lock's 369 transitive deltas would saturate
  signal-to-noise); `max_growth_per_release` prescriptive thresholds
  (release-boundary semantics deferred); A2A trust-budget signal
  types (parallel to E-B2-3's deferred hat-contract-signal). All
  BACKLOG B-23.

  Additive only — no v2.9 conformance claim invalidated. Reference
  implementation: NeuroGrim crate `neurogrim-sensory::trust_budget`
  (lands in E-B2-4 C3). Per-epic Layer-2 plan in
  `~/.claude/plans/brains-2-0-e-b2-4-layer-2.md`. See
  `METHODOLOGY-EVOLUTION.md` §15 for rationale (trust-budget is
  a supply-chain primitive declaring third-party trust surface as
  schema-typed contract).

- **v2.9 (2026-04-27):** Two coordinated additions (Brains-2.0
  E-B2-3 + E-B2-5).

  **(1) Hat persona contracts (E-B2-3, §5.4.1 NEW).** Promotes
  the persona-hat anti-capability prose at
  `.claude/skills/hats/<hat>.md` into a schema-typed declaration
  (`hat-contract-v1.schema.json`). Closed-set tool vocabulary —
  8 initial entries: `Bash`, `Write`, `Edit`, `WebFetch`,
  `WebSearch`, `network_egress`, `mcp:*`, `package_install`.
  Optional `network_targets: { allowed[], forbidden[] }` for
  per-hat egress restrictions (E-B2-4 trust-budget reuses this).
  Validated statically by NeuroGrim's `capability_hygiene` sensor;
  v1 advisory weight 0.0; runtime enforcement deferred to v2 per
  BACKLOG B-23.

  **Two-layer model (Q5 = 5c, operator-confirmed 2026-04-27).**
  Registry hats (§5.4 — `brain-registry.json:config.hats.*` for
  scoring biases) and persona hats (§5.4.1 — `.claude/skills/hats/`
  for operational lenses + tool-boundary contracts) are
  permanently distinct concepts. Appendix E gains 3 disambiguating
  glossary entries: registry hat, persona hat, hat contract.
  RFC 2119: contract frontmatter is RECOMMENDED (SHOULD), not
  MUST — hats lacking frontmatter remain conformant; the sensor
  flags absence as advisory finding only.

  **(2) Multi-round pre-release assessment (E-B2-5, METHODOLOGY-EVOLUTION §16
  NEW).** Codifies the strict-bar → surgical-bar →
  diminishing-returns + Phase 1.5 escape-hatch retrospective
  pattern observed in the 2026-04-26 supply-chain pre-release
  campaign (Rounds 1, 2, 3) as a documented methodology
  evolution. RECOMMENDED, not MUST — cadence observed in a
  single campaign (N=1) and §16 explicitly framed as "patterns
  observed in pre-release context" pending validation by a
  second campaign (earliest candidate: E-B2-8). Plan-critic
  skill updated with §16 cross-reference for pre-release
  contexts; routine plan review remains single-pass.

  Additive only — no v2.8 conformance claim is invalidated;
  implementations that don't ship hat-contract or §16 cadence
  remain conformant. Reference implementation: NeuroGrim crate
  `neurogrim-sensory` (hat-contract validator lands in
  E-B2-3 Component 5; schema + fixtures + conformance test
  shipped in E-B2-3 Components 1+3). Per-epic Layer-2 plans in
  `~/.claude/plans/parallel-hugging-eich.md` § E-B2-3 + § E-B2-5.
  See `METHODOLOGY-EVOLUTION.md` §16 for rationale (multi-round
  pre-release assessment cadence — the second of the two coordinated
  additions in this version).

- **v2.8 (2026-04-27):** Domain calibration ledgers (Brains-2.0
  E-B2-2). New §17 formalizes the per-domain calibration ledger
  as a first-class methodology concern — generalizing the 2-phase
  Pending → Triaged append-only pattern that already shipped as
  three separate instances (judge-integrity-ledger v2.4,
  domain-promotion-ledger v2.5, supply-chain-decision-ledger v2.6)
  into a unified schema for new domains adopting the pattern. The
  three existing ledger instances are intentionally NOT migrated;
  each retains its own schema and on-disk file. New domains adopt
  the unified `domain-calibration-ledger-v1` schema.

  Triggers are a discriminated union (Layer-2 design pivot from
  the original `expected_score_range` primitive after adversarial
  review — that primitive over-fired on legitimate signal
  collapses): `OutOfExpectedRange { min, max }` for threshold-
  driven domains; `SignalClassFired { signal_kinds }` for
  event-driven domains (matches supply-chain's existing trigger
  shape); `Manual` for operator-only entries (the safe default
  for new domains). `TrajectorySwing` is a v2 candidate.

  Triage decision is a coarse 4-class enum
  (confirmed/mislabeled/gap/no-action); finer categorization
  belongs in `human_notes` (verbatim, auditable). Operator
  identity from `NEUROGRIM_OPERATOR` env var or `--operator`
  CLI flag — same shape as supply-chain's existing convention.

  Rotation policy: `*-calibration-ledger-{year}.jsonl` annual
  archives; sensor reader globs `*-calibration-ledger*.jsonl`
  so rotation is transparent.

  No A2A cross-Brain aggregation in v1 — calibration ledgers
  stay LOCAL to each Brain. (v2 candidate: bidirectional opt-in
  matching v2.6 supply-chain-signal posture.)

  Naming note: the Brains-2.0 master plan called this concept
  "self-coherence", but the Layer-2 review surfaced a collision
  with the existing `coherence` domain (cross-domain correlation
  health, see §8). Renamed to `domain-calibration` at the
  Layer-2 pass — the schema, the sensor file, and the CLI all
  use the new name. Spec §17's title mirrors.

  Additive only — no v2.7 conformance claim is invalidated;
  implementations that don't ship the calibration domain remain
  conformant. Reference implementation: NeuroGrim crate
  `neurogrim-core::calibration_ledger` (lands in E-B2-2 C3).
  Per-epic Layer-2 plan in
  `~/.claude/plans/parallel-hugging-eich.md` § E-B2-2. See
  `METHODOLOGY-EVOLUTION.md` §13 for rationale (domain-calibration
  ledgers feed governance-via-evidence; calibration-ledger pattern
  generalizes the 2-phase Pending → Triaged shape).

- **v2.7 (2026-04-27):** Confidence as a first-class envelope field
  (Brains-2.0 E-B2-1). Three coordinated additions across the
  CMDB envelope, the agent-output interface contract, and the A2A
  `score.updated` payload:
  - **§3.1 / Appendix C:** `cmdb-envelope-v1.schema.json` gains an
    optional root-level `confidence` integer in [0, 100]. When a
    sensor has its own freshness signal (e.g., cache-age,
    registry-fetch staleness), it MAY emit `confidence` directly;
    when absent, the Brain falls back to the existing age-decay
    model on `meta.updated_at` (§4.4). Schema relax-friendly:
    pre-v2.7 envelopes still validate.
  - **§6.1 / §6.7 (new):** `agent-output-v1` gains
    `unified_confidence` as a peer of `score`. Formula:
    `round(sum(d.confidence * d.weight) / sum(d.weight))` over
    scored (non-advisory) domains. Receivers SHOULD use this for
    peer-to-peer trust decisions ("score=85 / unified_confidence=20
    is a low-quality signal"). The schema's root
    `additionalProperties` was relaxed from `false` to `true` as a
    deliberate one-time forward-compat enabler — future spec
    changes still require explicit property additions; the
    relaxation is not a posture for ongoing sloppiness.
  - **§13.4:** `score.updated` payload (= AgentOutput) now carries
    `unified_confidence`. Consumers MUST tolerate absence from v2.6
    peers (treat as 0); v2.7+ producers MUST emit it.
  - **Appendix E (Glossary):** Three confidence concepts
    disambiguated — envelope.confidence (sensor-supplied freshness,
    optional), unified_confidence (Brain-aggregate, weighted-mean),
    children[].confidence (ecosystem-aggregate of a child Brain,
    weighted-mean for parity). The supply-chain-signal payload's
    `cross_brain_count` field is explicitly NOT a confidence — it
    is a peer count, distinct concept.

  Additive only — no v2.6 conformance claim is invalidated;
  v2.6 implementations that emit AgentOutput without
  unified_confidence remain conformant-to-v2.6 (and v2.7
  consumers tolerate them via the schema's
  `additionalProperties: true` and `#[serde(default)]`-style
  defaults). Reference implementation: NeuroGrim crates
  `neurogrim-core`, `neurogrim-sensory`, `neurogrim-cli`.
  See per-epic Layer-2 plan in
  `~/.claude/plans/parallel-hugging-eich.md` § E-B2-1. See
  `METHODOLOGY-EVOLUTION.md` §13 for rationale (confidence as
  first-class envelope field is the evidence-input primitive that
  governance-via-evidence domain promotion depends on).

- **v2.6 (2026-04-25):** Supply-chain awareness. New §16 formalizes
  supply-chain awareness as a first-class Brain concern, structured
  as three composing layers — Layer 1 mechanical SCA (lockfile +
  vulnerability-database query), Layer 2 vigilance (deep-signal
  publishing-behavior heuristics), Layer 3 agent-assisted human
  review (read-only static analysis + decision ledger). Conforming
  Brains MUST NOT shell out to external scanner binaries in their
  primary scoring path — the LiteLLM 2026-04-23 incident
  established scanner-chain compromise as a real attack class, and
  the methodology's structural mitigation is to query a
  vulnerability database (OSV.dev RECOMMENDED) directly. Layer 3
  MUST run agent review in read-only static-analysis mode (no
  package code execution); decisions MUST be recorded in an
  append-only `supply-chain-decision-ledger.jsonl` matching the new
  `supply-chain-decision-ledger-v1.schema.json`. A new A2A message
  type, `supply-chain-signal`, carries findings between peer
  Brains under a **bidirectional opt-in** consent model — both
  peers MUST declare the type in their Agent Card before signals
  flow, a tighter posture than other A2A messages owing to the
  legal-exposure profile of supply-chain findings. Two new schemas
  (`supply-chain-decision-ledger-v1.schema.json`,
  `a2a-supply-chain-signal-v1.schema.json`) and additive enum
  extensions to `a2a-envelope-v1.schema.json` and
  `agent-card-v1.schema.json` (new `supply-chain-signal` value).
  Additive only — no v2.5 conformance claim is invalidated;
  implementations that do not ship any of the three layers remain
  conformant. This is the FIRST methodology evolution where the
  reference implementation shipped a normative protocol-shape
  feature ahead of the spec — see `METHODOLOGY-EVOLUTION.md` §15
  for rationale (security-urgency exception with bounded
  conditions; not a general license for spec-impl-alignment
  drift).
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
16. [Supply-chain Awareness](#16-supply-chain-awareness)
17. [Domain Calibration](#17-domain-calibration)
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
Rust. The specification defines WHAT a conformant Brain is required to do. The
implementation shows HOW one Brain does it. Any implementation in any language that follows this
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
  "updated_at": "<ISO 8601 UTC>",
  "confidence": 90
}
```

**MUST requirements:**

1. The `score` field MUST be an integer in the range [0, 100] inclusive.

2. The `updated_at` field MUST be an ISO 8601 UTC timestamp reflecting when the
   observation was taken (not when the file was written, if different).

3. The `meta.schema_version` field MUST be present. Current version: `"1"`.

4. The `meta.updated_at` field MUST be present and MUST be an ISO 8601 UTC timestamp.

5. The `meta.updated_by` field MUST identify the tool that wrote this CMDB.

**MAY requirements:**

6. The `confidence` field MAY be present (added in v2.7). When present, it MUST
   be an integer in [0, 100] expressing the sensor's own freshness signal —
   e.g., a cache-age decay, a registry-fetch staleness, or a domain-specific
   notion of how trustworthy this snapshot is. When present, the Brain MUST
   prefer it over the age-decay model (§4.4) — sensors with their own
   freshness signal know better than the aggregator's clock-based estimate.
   When absent, the Brain MUST fall back to age-decay of `meta.updated_at`
   per §4.4. Most sensors SHOULD omit this field; opt-in is intended for
   sensors whose freshness signal is independent of clock-skew (e.g.,
   `supply-chain-vigilance` with cache-age data, `supply-chain-sca` with
   OSV cache age).

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
still conformant — confidence decay surfaces quality issues eventually, just more
slowly than a test would. Second, elevating this to MUST would invalidate every pre-v2.2
sensor retroactively, which violates the additive-bumps-by-default discipline. The
methodology nonetheless strongly encourages the feedback loop: the observing layer is
itself observable (VISION principle #18). See `METHODOLOGY-EVOLUTION.md` §8 for the
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

For CMDB-type domains, confidence is resolved in two steps:

1. **Envelope-supplied confidence (v2.7+).** If the CMDB envelope contains
   a top-level `confidence` integer in [0, 100] (§3.1), the Brain MUST use
   that value. Sensors with their own freshness signal — independent of
   the operator's machine clock — know more about the snapshot's
   trustworthiness than an age-decay heuristic can express.

2. **Age-decay fallback.** If the envelope omits `confidence`, the Brain
   MUST compute confidence from the age of the timestamp identified by
   `scoring_source.updated_at_field` using the default model below.

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

**Confidence counterpart (v2.7+).** The unified score has a peer
field `unified_confidence` in agent output (§6.7) that aggregates
confidence with the same weight-and-advisory semantics as
`unified_score` — filtering out advisory domains, weighting by
domain weight. The shape difference is just normalization: where
`unified_score` is a weighted *contribution* (sums weighted
effective scores), `unified_confidence` is a weighted *mean*
(divides by total weight). Receivers SHOULD use the pair
`(unified_score, unified_confidence)` for trust decisions on
peer-supplied scores.

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

### 5.4.1 Hat Persona Contracts

> **NORMATIVE NOTE — Two distinct hat concepts (v2.9+).** §5.4
> defines the **registry hat** (a Brain-scoring concept declared
> in `brain-registry.json:config.hats.*` for domain emphasis and
> autonomy bias). §5.4.1 defines the **persona hat** (an
> operational lens declared at `.claude/skills/hats/<hat>.md` for
> agent behavior — tone, briefing style, tool-boundary contract).
> The two are intentionally separate. See Appendix E entries for
> "registry hat", "persona hat", and "hat contract" for the
> disambiguated definitions. The bare term "hat" remains
> acceptable when context makes the scope unambiguous.

A persona hat is a subagent-facing operational lens — adversary,
architect, supply-chain-auditor, source-reader, incident-commander,
rubber-duck, security-auditor, visionary — catalogued at
`.claude/skills/hats/SKILL.md` and used to calibrate subagent
briefings. Persona hats live as per-hat markdown files under
`.claude/skills/hats/<hat>.md`, optionally carrying YAML
frontmatter conforming to `hat-contract-v1.schema.json`.

A persona hat's frontmatter SHOULD declare a tool-boundary contract:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | MUST | Hat identifier (e.g., "supply-chain-auditor") |
| `description` | string | MUST | One-line summary of the lens |
| `briefing` | string | SHOULD | One-line subagent calibration text |
| `allowed_tools` | array | MAY | Closed-set tool names the hat is permitted to invoke |
| `forbidden_tools` | array | MAY | Closed-set tool names the hat MUST NOT invoke |
| `network_targets` | object | MAY | Per-hat egress restriction with `allowed[]` and `forbidden[]` FQDN arrays |

**Closed-set vocabulary (v1 — additive promotion path).** The
`allowed_tools` and `forbidden_tools` items use a closed enum of
exactly 8 entries: `Bash`, `Write`, `Edit`, `WebFetch`,
`WebSearch`, `network_egress`, `mcp:*` (wildcard for any
MCP-namespaced tool), and `package_install` (semantic alias for
the `npm install` / `pip install` / `cargo build` set). New
vocabulary terms require a spec change with explicit
METHODOLOGY-EVOLUTION entry — same discipline as the culture
manifest (§14). Implementations MUST reject unknown vocabulary
terms.

**Backward compatibility.** A persona hat without frontmatter is
a conformant v1 hat. The validator MUST treat a missing contract
as advisory-only — equivalent to
`{forbidden_tools: [], allowed_tools: ["*"]}` with an advisory
finding flagging the absence. This matches the v1 RECOMMENDED
posture; v2 may MANDATE per BACKLOG B-23.

**Static validation v1.** The v1 validator (NeuroGrim's
`capability_hygiene` sensor) performs three static checks:
(a) frontmatter parses and validates against
`hat-contract-v1.schema.json`; (b) every declared tool name is
in the closed-set; (c) the catalog inventory is internally
consistent. **Runtime enforcement** — observing actual tool
invocations and cross-referencing against declared
`forbidden_tools` — is OUT OF SCOPE for v1. The v1
invocation-ledger captures only `Skill` tool invocations, not
`Bash` / `Write` / `Edit`; runtime enforcement requires a ledger
schema bump deferred to v2 per BACKLOG B-23.

**Recursion guard (MUST).** The hat-contract validator itself
MUST NOT wear a persona hat with declared `forbidden_tools`. The
validator is plain code, not a hat — self-loop is closed by
construction. Implementations MUST verify (e.g., via unit test)
that the validator's source contains no shell-out invocations
when reading hat-contract files.

**Per-Brain scope (v1).** Persona hats are LOCAL to each Brain's
`.claude/skills/hats/`. There is NO A2A propagation in v1. When
a Brain authors a new persona hat, it does NOT automatically
appear in peer Brains. Cross-Brain hat-contract sharing
(`hat-contract-signal` A2A message type with bidirectional
opt-in) is a v2 candidate per BACKLOG B-23.

**Trust-budget composition (v2.8+).** The `network_targets` field
exists to give the trust-budget primitive (E-B2-4 / §16.8) a
per-hat egress restriction surface. Trust-budget reads BOTH
`forbidden_tools` AND `network_targets.allowed` from the
hat-contract; budget enforcement is implementation-defined within
`trust-budget` and orthogonal to this contract.

**Findings shape.** Implementations SHOULD surface validator
output via the `capability-hygiene` CMDB findings stream, with
finding kinds:
- `hat_contract:declaration:<name>` — hat lacks frontmatter
  (neutral, advisory).
- `hat_contract:vocabulary:<name>:<term>` — frontmatter declares
  an unknown vocabulary term (error, advisory).
- `hat_contract:violation:<hat>:<observed_tool>` — DEFERRED to v2
  (requires runtime signal per BACKLOG B-23).

All v1 findings carry advisory weight (0.0).

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

Every agent-mode output MUST contain these 12 fields (was 11 pre-v2.7;
`unified_confidence` added in v2.7):

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | `"1"` (string const) | Interface version |
| `scored_at` | ISO 8601 datetime | When scoring was performed |
| `score` | integer 0-100 | Unified confidence-weighted score |
| `unified_confidence` | integer 0-100 | Brain-aggregate confidence (v2.7+; see §6.7) |
| `domains` | object | Per-domain scores |
| `dirty_gates` | string[] | Gate keys with status `"dirty"` |
| `stale_artifacts` | string[] | Artifact keys with stale freshness |
| `domain_variables` | object | Cross-domain signal variables |
| `top_recommendations` | array | Top-5 prioritized actions |
| `correlations_fired` | array | Matched correlation rules |
| `incident_patterns` | array | Matched incident patterns |
| `skipped_temporal` | string[] | Temporal patterns skipped |

**Backward compatibility (v2.6 producers):** v2.7 consumers MUST
tolerate the absence of `unified_confidence` from peers conforming
to v2.6 or earlier (treat as 0 = unknown). The schema reflects this
by listing `unified_confidence` in `properties` but NOT in
`required[]` — see §6.7 for the producer/consumer contract details.

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

**v2.7 schema-evolution note:** The v2.7 spec relaxed the
agent-output-v1 schema's root `additionalProperties` from `false`
to `true` as a deliberate one-time forward-compat enabler. Pre-v2.7
the schema rejected any unknown root field; v2.7 onward, future
spec changes can add optional fields without reissuing the schema.
This is NOT a license for ongoing additionalProperties sloppiness —
future spec changes still require explicit `properties` additions.
The relaxation just unblocks the additive-evolution discipline so
that adding `unified_confidence` (and similarly-shaped future
fields) doesn't require coordinated lockstep upgrades across all
peers in the four-Brain ecosystem.

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

### 6.7 Unified Confidence

Added in v2.7 (Brains-2.0 E-B2-1). `unified_confidence` is a peer
of `score` in the agent output: where `score` is the weighted-mean
of per-domain *effective scores*, `unified_confidence` is the
weighted-mean of per-domain *confidence*.

**Formula:**

```
unified_confidence = round(
    sum(d.confidence * d.weight) / sum(d.weight)
    over scored (non-advisory) domains
)
```

The aggregation matches `unified_score`'s semantics — both filter
out advisory-weight (0.0) domains; both weight by domain weight.
The shape difference is the normalization-by-weight-sum: `score`
is a weighted *contribution* (sums to ≤100 only if weights sum to
1.0); `unified_confidence` is a weighted *mean* (always in [0, 100]
regardless of weight sum). When the scored set is empty OR total
weight is 0, `unified_confidence` MUST be 0 — matching
`unified_score`'s "no signal" semantics.

**Producer obligation (v2.7+ Brains):**
- v2.7+ producers MUST emit `unified_confidence` in every agent-
  mode output.

**Consumer obligation (all Brains):**
- v2.7+ consumers MUST tolerate the absence of `unified_confidence`
  from peers conforming to v2.6 or earlier. Absence is interpreted
  as 0 (unknown, no signal).
- Consumers receiving `unified_confidence` SHOULD use it for
  peer-to-peer trust decisions: a peer with `score=85` and
  `unified_confidence=20` is a low-quality signal regardless of
  the score itself, and SHOULD be discounted in cross-Brain
  aggregation (§9.4).

**Rendering:**
- Operator-visible output SHOULD surface `unified_confidence`
  alongside `score` when it is below 100 (the steady-state for
  fresh data — suppressing the 100 case avoids noise). When
  `unified_confidence == 0`, output MUST surface it explicitly so
  the operator distinguishes "v2.6 peer" or "all-advisory Brain"
  from missing data.

**Why a separate field rather than overloading `score`:**
- `score` and `confidence` answer different questions: "how
  healthy?" vs. "how trustworthy is the answer?". A peer reporting
  `score=85 / confidence=100` differs meaningfully from `score=85 /
  confidence=10` — the former is actionable; the latter SHOULD
  prompt re-fetch or operator review.
- The distinction was implicit per-domain since v2.0 (per-domain
  `confidence` exists in §6.2). v2.7 surfaces the aggregate so
  receivers don't have to recompute it from per-domain values
  embedded in the payload.

> See [Appendix E](#appendix-e-glossary) for the disambiguation of
> the three confidence concepts (envelope, unified, children[]).

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

(v2.6 additionally defined the `supply-chain-signal` message type
with bidirectional opt-in — see §16.6.)

A Brain declares which types it `accepts` and which it `emits` in its Agent Card. The
payload shape per message type is defined in Appendix G.

**v2.7 payload note (`score.updated`):** The `score.updated`
payload IS the AgentOutput per §6 — including `unified_confidence`
as of v2.7. Receivers SHOULD use the peer's `unified_confidence`
for trust decisions when aggregating across peers (§9.4): a peer
with high score but low `unified_confidence` is a low-quality
signal regardless of the score itself. v2.7+ consumers MUST
tolerate the absence of `unified_confidence` from peers conforming
to v2.6 or earlier (treat as 0; see §6.7).

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
The observing layer MUST itself be observable (VISION principle #18: "sensors need
sensors"); the agents running the sensors MUST themselves be scorable (VISION
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

## 16. Supply-chain Awareness

### 16.1 Concept

Sections 1–15 specify how a Brain observes a project, scores it,
correlates findings, learns from outcomes, and verifies the agents
operating on it. §16 specifies how a Brain observes the **supply
chain that the project depends on** — the dependency graph
(declared and transitive), the publishers behind each dep, the
behavior of those publishers over time, and the patterns that
distinguish a safe-to-build-on package from one that has gone or
is going bad.

The motivating observation is that supply-chain attacks are now a
first-class threat-class against the projects a Brain observes. A
project may be internally healthy — its tests pass, its code is
clean, its agents behave well — and still ship a critical
vulnerability to its users because a transitive dependency was
compromised. Existing domains do not measure this surface; §16
gives it normative shape.

A second motivating observation is that **the security tooling
itself can be the attack vector**. A Brain whose primary scoring
path shells out to an external scanner binary inherits that
scanner's trust. The 2026-04-23 LiteLLM incident (METHODOLOGY-
EVOLUTION §15) established this attack class concretely. §16's
normative posture is that conforming Brains MUST NOT shell out to
external scanner binaries in their primary scoring path; they
MUST query a vulnerability database directly (OSV.dev RECOMMENDED)
and MAY supplement with pinned local advisory sources.

Supply-chain awareness is structured as **three composing layers**:

1. **Layer 1 — Mechanical SCA** — Lockfile parsing + vulnerability-
   database query. Deterministic, exact-match.
2. **Layer 2 — Vigilance** — Deep-signal heuristics on
   publish-cadence, maintainer delta, signature gaps, binary
   reproducibility, typosquat proximity, transitive surface delta,
   exfil indicators. Probabilistic, advisory.
3. **Layer 3 — Agent-assisted human review** — Read-only static
   analysis by an LLM-judge agent on flagged deps; humans triage;
   decisions accrue in a normative append-only ledger.

The three layers compose. Layer 1 catches the known-bad with high
precision. Layer 2 surfaces the "this looks suspicious" signal that
a zero-day eventually triggers. Layer 3 puts a human in the loop
when neither machine answer is conclusive. **No layer auto-blocks
or auto-rolls-back deps in v1 — humans gate, machines advise.**

Conforming Brains MAY implement any subset of the three layers;
SHOULD implement Layer 1 (it is the lowest-cost, highest-precision
contribution); MUST honor the contracts of any layer they do
implement. A Brain that implements no layers is conformant but
silent on the supply-chain surface; the spec does not require
opt-in.

### 16.2 Layer 1 — Mechanical SCA

Layer 1 produces deterministic findings by:

1. Parsing the project's lockfile(s) to enumerate the resolved
   dependency graph (direct + transitive).
2. Querying a vulnerability database for advisories matching each
   `(name, version, ecosystem)` tuple.
3. Filtering findings against an operator-curated accepted-
   advisories file.
4. Emitting CMDB findings + a score.

Normative requirements for a Layer 1 implementation:

- **Direct vulnerability-database query** — Conforming Brains MUST
  query a vulnerability database directly over a network protocol
  (HTTPS RECOMMENDED). OSV.dev is RECOMMENDED as the primary
  source; implementations MAY use ecosystem-native databases
  (RustSec for Rust, PyPA for Python, GHSA for npm) as supplements
  or fallbacks. The data source MUST be documented in the
  implementation's operator guide.
- **No external scanner binaries in the primary scoring path** — Conforming Brains MUST NOT shell out to `cargo audit` /
  `pip-audit` / `npm audit` / `trivy` / `grype` / `osv-scanner` /
  any equivalent external scanner binary as the primary source of
  Layer 1 findings. Implementations MAY accept output from such
  tools as an opt-in cross-check; the cross-check MUST NOT be the
  source of truth. Rationale: the LiteLLM 2026-04-23 incident
  (METHODOLOGY-EVOLUTION §15) demonstrated that scanner binaries
  themselves are a viable attack vector ("scanner-chain
  compromise"); narrowing the trust surface to the Brain itself +
  its pinned libraries + its vulnerability-database HTTPS endpoint
  is a structural mitigation.
- **CMDB envelope conformance** — Layer 1 output MUST be a CMDB
  envelope conforming to `cmdb-envelope-v1.schema.json`. Each
  advisory SHOULD appear as one entry in `findings[]`. Domain
  name SHOULD include `supply-chain-sca` (kebab-case; ecosystem-
  agnostic naming RECOMMENDED).
- **Response cache** — Implementations SHOULD support a local
  response cache for vulnerability-database queries with a
  documented TTL (24 hours RECOMMENDED) and an operator-controlled
  bypass mechanism (e.g., environment variable).
- **Accepted-advisories file with hygiene lever** — Implementations
  SHOULD support an operator-curated file of accepted advisories
  (path implementation-defined; `.claude/supply-chain-accepted-
  advisories.toml` RECOMMENDED). Each accepted entry MUST require
  a non-empty `note` field documenting why the advisory has been
  accepted; entries without a `note` MUST be silently skipped (the
  hygiene lever — silent acceptance is the failure mode the file
  is intended to prevent).
- **Graceful degradation** — Implementations MUST NOT panic when
  the vulnerability database is unreachable. The expected
  degradation path is: serve from cache + pinned local advisory
  source if present, surface the degradation in the CMDB extras
  (e.g., `osv_reachable: false`), and emit a `lockfile_unreadable`
  or equivalent sensor_status when the lockfile itself is missing.
- **Score model** — The scoring rubric is implementation-defined.
  v1 implementations SHOULD use a count-based rubric (e.g., 0
  unaccepted advisories → 100; 4+ → 0) until severity coverage
  improves across vulnerability databases. Severity-weighted
  rubrics MAY be opt-in alternatives.
- **Domain weight default** — The `supply-chain-sca` domain SHOULD
  default to weight 0.0 (advisory) for v1; promotion past advisory
  follows §15.5 governance discipline.

### 16.3 Layer 2 — Vigilance

Layer 2 produces probabilistic findings by analyzing **publishing
behavior** of the dependencies in the graph:

1. **Publish cadence** — Step-function changes in release frequency
   (e.g., a package that hadn't shipped in 18 months suddenly
   ships three releases in a week).
2. **Maintainer delta** — New maintainers added within a configured
   window before a release.
3. **Signature gaps** — Sigstore / GPG / trusted-publishing presence
   versus last-known-good for the same package.
4. **Binary reproducibility** — Registry-tarball hash versus
   source-tag hash, when both are available.
5. **Typosquat proximity** — Levenshtein distance ≤ 1 to popular
   packages on the same registry.
6. **Transitive surface delta** — Dep-count change between
   adjacent versions of the same package (e.g., a patch release
   that suddenly pulls in 40 new transitive deps).
7. **Exfil indicators** — Static-analysis heuristics for base64
   strings, dynamic `eval`/`exec`, `subprocess` invocations,
   network-endpoint additions in recent versions.

Normative requirements for a Layer 2 implementation:

- **Advisory weight only in v1** — The `supply-chain-vigilance`
  domain (or equivalent) MUST default to `domain_weights: 0.0`
  in v1. Promotion past advisory weight requires a calibration
  audit equivalent in spirit to §15.3 (operator-declared evidence
  of acceptable false-positive rate against a fixture library).
  See §15.5's governance pattern for the promotion path.
- **Findings format** — Each Layer 2 finding SHOULD include the
  signal kind (one of the seven above or an
  implementation-defined extension), the package + version,
  recent observation history sufficient to reproduce the signal,
  and a confidence score in [0, 1].
- **No primary gating in v1** — Layer 2 findings MUST NOT be the
  sole basis for blocking a publish or a merge in v1. They MAY be
  the basis for surfacing a Layer 3 review ticket (§16.4).
- **CMDB envelope conformance** — Layer 2 output MUST conform to
  `cmdb-envelope-v1.schema.json`.

### 16.4 Layer 3 — Agent-assisted Human Review

Layer 3 puts a human reviewer in the loop, structured by an LLM
agent that produces read-only static-analysis findings to inform
the human decision.

Normative requirements for a Layer 3 implementation:

- **Read-only static analysis** — The agent reviewing a flagged
  dependency MUST NOT execute package code as part of the review.
  This is a security-critical constraint: an agent that executes
  potentially-malicious package code in its review pipeline is
  potentially executing the very attack it is reviewing. The
  constraint applies to the **automated** review path; a human
  operator who chooses to run package code in a separately-
  isolated environment as part of manual triage is not bound by
  §16.4 — but that path MUST be documented in the
  implementation's operator guide as a manual escalation, not an
  automated review step.
- **Prompt-injection isolation** — The agent reviewer SHOULD be
  fed only specific file excerpts (e.g., the diff and the
  changed files), not the full package context. README files,
  long-form documentation, and other free-text artifacts in the
  package are common prompt-injection vectors and SHOULD be
  excluded from the agent's input or sanitized before inclusion.
  Container-isolated agent execution is RECOMMENDED for
  implementations where the threat model warrants it.
- **Decision ledger** — Every Layer 3 outcome MUST be recorded in
  an append-only `supply-chain-decision-ledger.jsonl` conforming
  to `supply-chain-decision-ledger-v1.schema.json` (§16.7). The
  ledger captures the package, the triggering signals from
  Layer 1 + Layer 2, the agent's findings, the human operator's
  identity, the human's notes, and the decision (accept / reject /
  pin-to-last-good / review-pending / review-triaged).
- **Human decision is the gate** — The agent reviewer MUST NOT
  auto-accept, auto-reject, or auto-pin findings in v1. Every
  decision MUST have a human operator's identity recorded in the
  ledger entry. Implementations MAY surface agent-recommended
  decisions to the operator; they MUST NOT skip the human-
  decision step.
- **Append-only discipline** — Ledger entries MUST NOT be edited
  in place. Triage corrections are recorded as new
  `review-triaged` entries that supersede a prior
  `review-pending` (the new entry's `supersedes_ts` references the
  superseded entry's `ts`). This is the same append-only pattern
  established by `domain-promotion-ledger-v1` (§15.5) and
  `agent-behavior-feedback.jsonl` (§15.5).
- **Output language discipline** — Findings published outside the
  Brain (e.g., shared via §16.6 A2A signal) MUST use non-
  attributive language. "This package's release pattern…" is
  acceptable; "Maintainer X introduced a malicious payload…" is
  not. Rationale: supply-chain findings about specific maintainers
  carry legal-exposure risk (defamation, tortious interference);
  conservative language is the default. The
  `a2a-supply-chain-signal-v1.schema.json` carries an operator-
  visible `legal_disclaimer` field as a forcing function.

### 16.5 The supply-chain-auditor Hat

A conforming Brain that ships any of Layers 1–3 MUST expose a
**supply-chain-auditor hat** — a scoped agent persona that handles
package-level review. Per §5.4, hat content is implementation-
defined; the spec normatively requires the hat exist with the
following operational scope:

- **Provenance verification** — The hat checks that a package's
  declared provenance (Sigstore attestation, PyPI trusted
  publisher, npm signed publish, etc.) matches the registry's
  records.
- **Unreviewed-dep audit** — The hat enumerates dependencies
  introduced or upgraded since the last review checkpoint and
  surfaces them for triage.
- **Remediation gate** — The hat is the agent persona that gates
  the publish-day runbook. A human operator wearing this hat is
  the final gate; the hat does not auto-decide.

Hat content MAY be authored as a `.claude/skills/hats/SKILL.md`
catalog entry (the reference implementation's pattern). Other
implementations MAY use other hat-discovery mechanisms; the
contract is the operational scope above.

### 16.6 A2A Signal Sharing

Conforming Brains MAY share supply-chain findings with peer
Brains via the A2A protocol (§13). A new A2A message type,
`supply-chain-signal`, carries the finding payload defined in
`a2a-supply-chain-signal-v1.schema.json` (§16.7).

The consent model is **bidirectional opt-in**:

- A Brain MUST declare `supply-chain-signal` in its Agent Card
  (`agent-card-v1.schema.json`) `capabilities.accepts[]` to
  receive supply-chain signals.
- A Brain MUST declare `supply-chain-signal` in its Agent Card
  `capabilities.emits[]` to send supply-chain signals.
- A Brain MUST NOT send a `supply-chain-signal` to a peer whose
  Agent Card does not declare `supply-chain-signal` in
  `accepts[]`.
- Implementations SHOULD additionally require operator
  acknowledgement that both peers are trusted as supply-chain-
  signal correspondents before signals flow. The exact
  mechanism is implementation-defined.

This is a **tighter** consent model than the existing one-
direction-by-Agent-Card-declaration default for other A2A message
types. Rationale:

1. **Legal exposure** — Supply-chain findings name specific
   packages and frequently specific maintainer behavior.
   Auto-broadcasting findings to peers creates defamation and
   tortious-interference risk that one-direction consent does not
   adequately mitigate.
2. **False-positive multiplication** — A single false-positive
   that auto-propagates to peer Brains becomes a multiplied false
   positive. Bidirectional opt-in keeps the false-positive blast
   radius bounded.
3. **Conservative posture** — v2.6 takes the conservative
   position. v2.7+ MAY relax to one-direction consent if real
   demand surfaces and the risk profile is shown to be
   manageable.

A Brain receiving a `supply-chain-signal` from a peer MUST treat
it as advisory input. Implementations SHOULD aggregate signals
across peers (e.g., "two independent peers flagged this package")
to produce a `cross_brain_count` field; aggregation rules are
implementation-defined in v2.6 and a candidate for normative
specification in v2.7+.

#### 16.6.1 Federated Pattern Sharing (v2.12+)

Brains-2.0 E-B2-7 introduces a **second** A2A message type for
cross-Brain communication: `federated-pattern`. Where
`supply-chain-signal` is supply-chain-specific, `federated-pattern`
is a general primitive for sharing **anonymized pattern features**
between peer Brains. The wire format is governed by
`a2a-federated-pattern-v1.schema.json`; the local persistence layer
is the per-Brain `pattern-aggregation-ledger.jsonl` governed by
`pattern-aggregation-ledger-v1.schema.json`.

Both schemas land at v2.12. The federated-pattern message type is
the v1 first-customer of a federation primitive that v2/v3 may
extend to additional pattern kinds (operator-calibration drift,
hat-contract violations, trust-budget growth) per BACKLOG B-23. The
v1 closed-set vocabulary contains a single `pattern_kind` value:
`vigilance-pattern` — Brains share supply-chain-vigilance correlation
findings with their peers when the operator chooses to do so.

**Conformance.** A Brain MAY ship without the federated-pattern
surface and remain conformant — federation is opt-in via Agent Card
`capabilities.accepts[]` and `capabilities.emits[]` advertisement,
mirroring the §16.6 supply-chain-signal precedent. Brains lacking
the advertisement neither send nor receive federated-pattern
messages.

**Bidirectional opt-in (reuse §16.6 precedent).** Both peers MUST
declare `federated-pattern` in their Agent Card capabilities before
federation flows. The reference implementation provides a
parallel-construction `federated_pattern_opt_in_satisfied(local,
peer) -> bool` helper mirroring `bidirectional_opt_in_satisfied`
from supply-chain-signal. Operator-acknowledgement-of-trust SHOULD
also apply, mirroring §16.6 paragraph 4.

**Privacy under composition (MUST).** The `feature_vector` field is
closed-set numeric-only at v1: `numeric_count` (integer ≥ 0),
`severity_class` (closed-set enum), `observation_window_days`
(integer ≥ 1). Implementations MUST NOT introduce string fields, FQDNs,
operator handles, file paths, per-skill names, or any free-text into
the federated-pattern payload at v1. The schema's
`additionalProperties: false` on both the payload AND the
FeatureVector sub-object enforces this structurally. The optional
`metadata` field carries `additionalProperties: true` as an
operator-extension escape hatch BUT spec MUST language forbids
placing PII / paths / operator handles in `metadata` — the schema
cannot enforce this; implementations MUST audit emitted patterns to
verify the discipline (Q12 sender-side ledger entries provide the
audit trail).

**Recursion guard (MUST).** Federated patterns flow A → B → C → A
unless mitigated. Implementations MUST mitigate at TWO layers:

1. **Wire-level.** Every federated-pattern message carries an
   `origin_set[]` array of opaque brain-id hashes — entries for the
   original sender and any relayer that has previously handled this
   message. The receiver MUST validate that `origin_set[]` does not
   contain its own opaque hash before processing; if it does, the
   message is dropped with `dropped_reason=recursion-guard` recorded
   in the pattern-aggregation-ledger. The schema enforces
   `origin_set` maxItems 4 (Q15 hop-limit lock — sender plus three
   relayers).

2. **Source-level.** The federated-patterns aggregator sensor's own
   findings (kind prefix `federated_patterns:*`) MUST NOT be valid
   sources for emitted federated-pattern messages. Implementations
   MUST verify (e.g., the emit CLI rejects `--pattern-kind` values
   prefixed `federated_patterns:` at parse time) — closes the
   meta-finding feedback loop by construction.

Mirrors the §17.9 `Manual` calibration trigger discipline (E-B2-2)
and the §17.12.5 operator-calibration recursion guard (E-B2-6),
extended to cross-Brain message flow.

**Signal flooding mitigation (BR-6, MUST).** Two-layer rate limit.

- **Sender-side.** Implementations MUST gate federated-pattern
  emission with a per-peer concurrency limit. The reference
  implementation uses `tokio::sync::Semaphore` with two permits and
  a 6-second per-permit interval (effective ~10 messages per peer
  per minute), mirroring the R2-2 pattern from
  `supply_chain_vigilance/registry.rs`.
- **Receiver-side.** Implementations MUST gate federated-pattern
  receipt with a sliding-window counter per `peer_brain_id` —
  drop-and-log if a peer exceeds 10 federated-pattern receipts per
  60-second window. Drops MUST be recorded as
  `entry_kind=received, dropped_reason=rate-limit-exceeded` rows in
  the pattern-aggregation-ledger.

Two-layer enforcement is BR-6 defense-in-depth: a misconfigured
sender that bypasses its own semaphore is still constrained by
receiver-side drop. The 10-per-minute threshold is a v1 starting
point; v2/v3 candidates include per-peer-reputation-based dynamic
thresholds (BACKLOG B-23). Default-conservative: tighten thresholds
first; relax based on calibration data.

**Topology (MUST — LOCAL).** v1 federation flows EXCLUSIVELY between
parent and child in the existing fractal-composition tree
(`brain-registry.json:children`). Implementations MUST NOT propagate
federated-patterns to peers outside this declared tree at v1.
Sibling federation and cross-tree federation are v2 candidates per
BACKLOG B-23.

**Operator-explicit emission (Q2).** v1 emission is RECOMMENDED to
be operator-invoked rather than automatic. The reference
implementation provides `neurogrim federated-pattern emit
--pattern-kind <kind> [--peer <peer-id>] [--operator <handle>]`
which constructs the payload from local correlation findings and
sends to declared peers under the rate-limit semaphore.
Auto-emission on every score-update is OUT OF SCOPE for v1
(BR-6 amplification risk) and is a v2 candidate per BACKLOG B-23 —
same discipline as the §17.12 explicit-only disposition CLI.

**Sender-side audit trail (Q12).** Every emitted federated-pattern
MUST be recorded in the SENDER's own pattern-aggregation-ledger as
an `entry_kind=emitted` row. Operator MAY review what their Brain
has shared by reading the ledger. NEUROGRIM_OPERATOR identity is
NOT captured — federation is project-level, not operator-level.

**Cross-version compatibility (Q11).** v1 receivers tolerate unknown
future `pattern_kind` values via graceful degradation: the schema
validates structural fields but pattern_kind enum enforcement happens
at the sensor level (where forgiveness is appropriate). Unknown
values are silently logged as
`entry_kind=received, dropped_reason=unknown-pattern-kind` rows.
Forward-compat additive surface lands via the per-entry `extensions`
block (E4-7 pattern from trust-budget schema).

**The federated-patterns sensor.** The reference implementation
provides `neurogrim-sensory::federated_patterns` which reads the
pattern-aggregation-ledger and emits aggregate observability data.
Score is advisory floor 100 (federation is INFORMATION, not health).
Findings: `federated_patterns:no_active_peers`,
`federated_patterns:peer_inactive_30d`,
`federated_patterns:high_drop_rate`, `federated_patterns:low_confidence`,
`federated_patterns:cross_peer_co_occurrence`.
All advisory weight 0.0 at v1; per Q13 + Q17 lock, no automated
promotion to gating.

`federated_patterns:cross_peer_co_occurrence` (added v3.1) fires when
≥2 distinct anonymized origins emit `vigilance-pattern` findings
sharing a feature_vector signature (`severity_class` +
`observation_window_days`) within the rolling 7-day window. Multiple
peers independently flagging similar concerns is the operator-
actionable signal that federation-as-intelligence is meant to
surface. Detail field is aggregate-only (peer count + severity +
window) — no per-peer hashes, no per-row data. Closed-set additivity
per Q17 lock; same aggregation-only export discipline as the other
four findings.

**v1→v2 promotion.** No automated promotion to hard gates.
Federated patterns are observability-only at v1. v2 candidates per
BACKLOG B-23 are scope expansions: more pattern_kind values,
per-skill aggregation, real-time correlation feedback. v3
candidates: cross-Brain reputation decay, sibling federation,
cryptographic origin proofs (B-25 cryptographic naming).

### 16.7 Schemas

Two new normative schemas land with v2.6:

- **`supply-chain-decision-ledger-v1.schema.json`** — Append-only
  JSONL ledger for Layer 3 decisions. Five entry kinds (`accept`,
  `reject`, `pin-to-last-good`, `review-pending`,
  `review-triaged`). Discriminated by `entry_kind`. Mirrors the
  shape established by `domain-promotion-ledger-v1.schema.json`
  (§15.5). `additionalProperties: false` at every level.
- **`a2a-supply-chain-signal-v1.schema.json`** — Payload shape for
  the new `supply-chain-signal` A2A message type (§16.6).
  Required fields: `package` (an object with required `name`,
  `ecosystem`, and `version` sub-fields), `severity_class`,
  `discovery_source`, `peer_brain_id`, `schema_version`.
  Optional fields: `advisory_id` (present for Layer 1 mechanical-
  SCA signals carrying a registry advisory id; absent for
  vigilance/agent-review signals that did not produce a
  registry-tracked advisory), `cross_brain_count`,
  `legal_disclaimer`, `discovered_at`, `advisory_uri`,
  `summary`, `recommended_action`, `metadata`.
  `additionalProperties: false` at the top level; the `metadata`
  field is the operator-extension escape hatch.

The existing `a2a-envelope-v1.schema.json` and
`agent-card-v1.schema.json` schemas extend their `message_type` /
`capabilities.accepts[]` / `capabilities.emits[]` enums to include
`supply-chain-signal` as an additive change. These extensions are
non-breaking — peers that do not understand the new value continue
to validate their other messages correctly.

### 16.8 Trust Budget

A Brain's trust surface — the set of declared third-party code,
scripts, and external services it relies on — is a first-class
supply-chain concern. The trust budget primitive (v2.10+) makes that
surface auditable as a versioned, schema-typed declaration,
complementing the runtime SCA findings of §16.2 with operator-stated
intent.

A `trust-budget.toml` file SHOULD be placed at each Brain's repo
root (committed and code-reviewable, NOT under `.claude/` runtime
state). The file conforms to `trust-budget-v1.schema.json` and
declares three orthogonal surface types:

- **`declared_crates[]`** — third-party packages the Brain
  consumes. Direct dependencies only at v1; transitive
  dependencies are out of scope (the workspace's transitive
  closure alone exceeds 360 entries on the NeuroGrim reference
  implementation; transitive expansion to that surface was
  deferred to v2 per BACKLOG B-23 to avoid saturating advisory
  signal-to-noise).
- **`declared_shell_outs[]`** — script-invoked commands. Operator
  declares the catalog by command name plus optional `script_paths[]`
  for traceability.
- **`declared_external_services[]`** — outbound network endpoints
  by FQDN, with `purpose` prose and a `trust_posture` enum
  classifying HOW the operator trusts the service.

Each entry MAY carry a `seeded` boolean indicating the entry was
operator-acknowledged at trust-budget bootstrap; sensors SHOULD use
this to suppress first-run findings on operator-known surface.

**Closed-set vocabulary.** The schema enforces two enums whose
extensibility is governed by the same discipline as §5.4.1
hat-contract tool names — additive only via spec change. v2.10
vocabulary:

- `ecosystem` ∈ {`cargo`, `pypi`, `npm`, `system`}. The first
  three match the §16.2 SCA ecosystems; `system` covers OS-provided
  binaries (e.g., `git`, `curl`) outside any package registry.
- `trust_posture` ∈ {`api_only`, `official_registry`,
  `operator_audited`, `vendor_attested`}. Discriminates trust
  derivation: read-only API surface; default-trust-of-the-package-
  registry; operator-audited code path; vendor-signed attestation.

**Conformance.** A Brain MAY ship without a `trust-budget.toml` and
remain conformant; the trust-budget sensor MUST treat absence as a
permissive default and emit an advisory finding flagging the gap. A
Brain that ships `trust-budget.toml` MUST validate against
`trust-budget-v1.schema.json`; trust-budget findings MUST carry
advisory weight (0.0) at v1. Hard-gate elevation is deferred to v2
per BACKLOG B-23 — gated on calibration data demonstrating that
operators acted on findings before the gate fires (mirrors the §16.4
Layer-3 advisory-before-strict posture).

**Composition with §5.4.1 hat contracts.** Each persona-hat contract
optionally declares `forbidden_tools[]` and `network_targets:
{ allowed[], forbidden[] }`. The trust-budget sensor SHOULD
cross-reference both fields against `declared_shell_outs[]` and
`declared_external_services[]` respectively, surfacing per-hat
composition findings (e.g., "hat `supply-chain-auditor` declares
`network_targets.allowed: [osv.dev]`; workspace declares no
`osv.dev` external service" — drift in either direction is an
advisory finding). Per-hat runtime enforcement requires observed
tool invocations, deferred to v2 in tandem with hat-contract
runtime enforcement (BACKLOG B-23, §5.4.1).

**Drift semantics.** The sensor reports two distinct finding kinds:
`trust_budget:undeclared:*` (actual surface item not in the
operator-declared set — operator-action: add to `trust-budget.toml`
OR remove the surface) and `trust_budget:overdeclared:*` (declared
item not in the actual surface — operator-action: remove from
`trust-budget.toml` OR re-introduce the surface intentionally). Both
finding kinds carry advisory weight (0.0); they preserve
operator-intent visibility regardless of the direction of drift.

**Out-of-scope at v1.** Transitive crate budgets, runtime shell-out
observation, `max_growth_per_release` prescriptive thresholds, A2A
trust-budget signal types, and an auto-regenerate CLI — all deferred
to v2 per BACKLOG B-23 with explicit calibration-data gates where
applicable.

### 16.9 Versioning + Extensibility

The new schemas use `additionalProperties: false` per the
ecosystem's existing pattern (§6.5). Additive changes (e.g., a
new `entry_kind` for the decision ledger, a new
`severity_class` value) bump the schema version (v1 → v2) and
require migration tooling. Implementations MUST validate
incoming ledger entries against the declared `schema_version`
field; entries with unknown schema versions MUST be rejected with
a recoverable error (not silently ignored).

The v2.6 schemas are intentionally narrow. They cover the v1
implementation experience captured in METHODOLOGY-EVOLUTION §15.
Future additive changes — severity-weighted scoring (§16.2),
cross-Brain aggregation rules (§16.6), execution-isolated agent
review (§16.4) — are candidate v2.7+ work.

### 16.10 Reference Implementation

The reference implementation (NeuroGrim) ships:

- **Layer 1** — A native-Rust SCA sensor at
  `neurogrim-sensory/src/supply_chain_sca/`. Three ecosystems as
  of 2026-04-25: Rust (`Cargo.lock`), Python (`uv.lock` +
  `requirements*.txt`), Node (`package-lock.json` v2/v3 +
  `yarn.lock` Classic + Berry + `pnpm-lock.yaml` v6/v9). Direct
  OSV.dev queries with file-backed 24h cache; pinned RustSec
  advisory-db submodule for OSV-miss coverage and offline
  capability; operator-curated accepted-advisories TOML with
  required-`note` hygiene lever; count-based scoring rubric
  (0/1/2/3/4+ unaccepted → 100/75/50/25/0). Operator guide:
  `NeuroGrim/docs/supply-chain-sca.md`.
- **Layers 2 + 3** — Reference implementation tracked as
  NeuroGrim epic E-SC-5 (vigilance) and E-SC-6 (agent-assisted
  review). The §16 contract is normative now; reference-
  implementation work proceeds via those epics.
- **Operational scaffolding** — `audit/ROLLBACK-PLAYBOOK.md`
  (sensor-specific recovery procedures, populated epic-by-epic);
  `audit/TOOL-TRUST-NOTES.md` (running record of trust
  observations); `BEFORE-PUBLIC-RELEASE.md § Gate 11` (master
  publish gate forbidding `cargo publish` until Layer 1 is green
  on NeuroGrim's own dependency graph).

See METHODOLOGY-EVOLUTION §15 for the broader rationale, the
LiteLLM 2026-04-23 motivating incident, and the spec-impl-alignment
observation that surfaced during this epic (the first time the
reference implementation shipped a normative protocol-shape
feature ahead of the spec, and the bounded conditions under which
that ordering is acceptable).

---

## 17. Domain Calibration

A Brain's score for a domain is a model of the truth, not the
truth itself. When a human disagrees with the score — judges that
the Brain over-rated `test-health` because the green tests are
flaky, or that `code-quality` is artificially low because the
linter is mis-configured — that disagreement is **calibration
data**. §17 formalizes how Brains record those disagreements as
first-class artifacts, so that:

1. The decision becomes auditable 18 months later when the
   operator who made it has rotated off the project.
2. Cross-domain analysis can detect when calibration burden is
   shifting (a domain with persistent triage backlog is asking
   for attention).
3. The Brain can later compute a *self-observation* score — does
   our scoring model agree with humans? — without re-deriving the
   pattern from scratch in each domain.

§17 introduces a **unified ledger schema** for calibration entries
in domains that don't already have a ledger of their own. Three
existing ledger instances — judge-integrity-ledger (§15.3),
domain-promotion-ledger (§15.5), supply-chain-decision-ledger
(§16.4) — are **intentionally NOT migrated**. They predate the
unified schema, and their per-family fields (red samples; promotion
audits; package references) are richer than the unified schema
captures. The unified schema is for **new domains** adopting the
calibration pattern.

> **Diagram:** A flow diagram for the unified calibration ledger
> (Pending → Triaged transitions, trigger-discriminated entry shapes)
> is planned for a future spec revision; the reference implementation
> tracks `domain-calibration-ledger-v1.schema.json` directly.

### 17.1 Concept

The word "calibration" is used in four distinct senses across this
spec. Operators reading §17 in isolation encounter all four;
this glossary disambiguates them up front:

| Concept | Sense | Spec Reference |
|---------|-------|----------------|
| **Adversarial audit** (red-mode) | Running a calibrator against red samples to verify the judge can detect known failure modes (one-sided ceiling check) | §15.3 |
| **Promotion audit** | The evidence-bundle review that promotes an advisory-weight domain to non-zero weight | §15.5 |
| **Judge-integrity audit** | The append-only ledger of red-misses + operator triage of those misses | §15.3 + §15.4 |
| **Domain calibration** (§§17.1–17.11) | The append-only per-domain ledger of automated-vs-human-decision disagreement | §17 |
| **Operator calibration** (§17.12, v2.11+) | The append-only ledger of operator dispositions of agent skill invocations (sibling family of domain calibration; per-invocation rather than per-domain) | §17.12 |

When this section says "calibration" without qualification, it
refers to the §17 domain-calibration sense (§§17.1–17.11). The
operator-calibration sense (§17.12) is the sibling family
introduced in v2.11.

### 17.2 The 2-phase Ledger Pattern

Calibration ledgers are append-only JSONL files conforming to
`domain-calibration-ledger-v1.schema.json`. Each ledger records
two entry kinds:

- **Pending** — an automated trigger fired and produced an
  observation awaiting human triage. Snapshot of the score that
  triggered it + the trigger reason.
- **Triaged** — an operator reviewed the pending entry and
  recorded a decision. Supersedes the pending via `supersedes_ts`.

This is the same shape that `judge-integrity-ledger`,
`domain-promotion-ledger`, and `supply-chain-decision-ledger`
already use. §17's contribution is the unified schema for new
adopters, plus the formal trigger-discriminated-union (§17.3) and
the per-family extension scaffold (§17.4).

A conformant Brain implementing §17 MUST:

1. Write entries via append-only `O_APPEND` semantics (atomic
   temp+rename for cross-process safety).
2. Reject in-place edits — corrections are new entries
   superseding old ones.
3. Validate every entry against the schema before writing.
4. Reject pending entries whose `domain` is unknown to the
   registry (the registry is the authoritative domain enum).
5. Reject triaged entries whose `supersedes_ts` doesn't match an
   existing pending entry's `ts` in the same ledger.
6. Validate operator identity at write time — see §17.6.

Readers reconstruct ledger state by folding the stream
chronologically. An entry is **open** if it is pending and no
later triaged entry references its `ts` via `supersedes_ts`.

### 17.3 Calibration Triggers

A domain opts into calibration via a `calibration_trigger`
discriminated union in its `brain-registry.json`
`domain_definitions` block. The four variants:

```
CalibrationTrigger:
  - OutOfExpectedRange { min: u8, max: u8 }
  - SignalClassFired { signal_kinds: [string] }
  - Manual
  - TrajectorySwing { window_days, magnitude }   # v2 candidate; deferred
```

**`OutOfExpectedRange { min, max }`** — the Brain appends a
`pending` entry whenever the domain's effective_score is `< min`
OR `> max`. Threshold-driven; matches the judge-integrity-ledger
pattern (red-miss when `judge_score > expected_ceiling`). Operators
SHOULD only configure this trigger AFTER observing the domain's
actual score distribution for at least one calibration period
(otherwise the trigger fires on legitimate signal collapses, and
the operator burns triage cycles labeling them all `confirmed →
no-action`).

**`SignalClassFired { signal_kinds: [string] }`** — the Brain
appends a `pending` entry when the domain emits a CMDB finding
whose name matches one of the listed signal_kinds, or when an
extras field key matches. Event-driven; matches the
supply-chain-decision-ledger pattern (`auto_create_from_vigilance`
fires on Layer 2 finding kinds). Operators configure this when
the domain's score-volatility is too high for threshold-based
triggers but specific signal classes warrant calibration review.

**`Manual`** — the Brain emits NO automated entries against this
domain; entries are operator-created via the
`neurogrim domain-calibration triage --manual` CLI. **Default for
new domains.** The safe-by-default posture: a domain that has not
yet been observed long enough to know its score distribution OR
its signal taxonomy starts in `Manual` mode. Promotion to
threshold/signal-based requires observed-distribution evidence.

**`TrajectorySwing`** — DEFERRED to v2. Triggers on Δ-from-rolling-
baseline (§7 trajectory primitive integration). Avoids the
static-prior problem of `OutOfExpectedRange` by self-tuning to the
domain's actual distribution; v2 candidate once §7 + the trigger
plumbing are integrated.

A conformant Brain MUST default a domain's `calibration_trigger`
to `Manual` when:

- The field is absent from the registry, AND
- The Brain's `enable_calibration_writes` config is `true`.

A conformant Brain MUST NOT auto-fire entries when
`enable_calibration_writes` is `false` (the global gate) OR when
the domain's `calibration_trigger` is `Manual`.

### 17.4 Per-family Extension

The unified schema's `domain_family` field is an enum. Initial v1
value: `domain-calibration`. Future families add an enum value
AND a per-family `definitions` block dispatched via JSON Schema
`if/then/else` keyed on `domain_family`. Each per-family
definition uses `additionalProperties: false` on its own slice.
**New families add a definition; they do not relax the schema.**

For v1, the `domain-calibration` family has no per-family fields
beyond the shared core. The dispatch machinery is reserved for
when a second family adopts the unified schema (e.g., a future
governance-calibration family that needs to record gate-override
metadata; or a cultural-substrate-calibration family that needs
to record value-violation context).

### 17.5 Schema

Canonical: `schemas/domain-calibration-ledger-v1.schema.json`.

Required fields on every entry: `ts`, `schema_version` (const
"1"), `entry_kind` (`pending` | `triaged`), `domain` (string,
minLength 1, registry-validated by writer), `domain_family`
(enum).

Pending entries additionally require `trigger_signal_kind` and
`actual_score`. Optional: `expected_score_lower`,
`expected_score_upper`, `context_notes`, `context_artifacts[]`.

Triaged entries additionally require `supersedes_ts`,
`triage_decision` (enum: `confirmed` | `mislabeled` | `gap` |
`no-action`), `human_operator` (minLength 1), `human_notes`
(minLength 1). Optional: `audit_artifacts[]`.

The four-class `triage_decision` enum is intentionally coarse —
finer categorization belongs in `human_notes` (verbatim,
auditable):

- **`confirmed`** — the signal is real and actionable; operator
  intends to act on the underlying problem.
- **`mislabeled`** — the signal is false; sensor was wrong;
  calibration adjustment may be warranted.
- **`gap`** — the signal is real but no domain/rubric mechanism
  exists to act on it. Registers a follow-on need (e.g., "the
  domain is missing a sub-sensor that would catch this class").
- **`no-action`** — operator reviewed and concluded no action is
  warranted at this time. (Distinct from `mislabeled` in that
  the signal was *correct* but the situation doesn't require a
  response.)

### 17.6 Operator Identity

Triaged entries MUST carry `human_operator: string, minLength 1`.
The reference implementation discovers operator identity from:

1. `--operator <handle>` CLI flag (highest precedence), OR
2. `NEUROGRIM_OPERATOR` environment variable, OR
3. Reject the write — operator identity is REQUIRED on triaged
   entries.

The `NEUROGRIM_OPERATOR` convention matches the existing
supply-chain-decision-ledger writer (§16.4's reference impl).
Note that judge-integrity uses `ABV_OPERATOR` and the existing
ledgers retain their existing env vars. A future spec-promotion
candidate is unifying all three under `BRAIN_OPERATOR` — out of
scope for §17.

Pending entries SHOULD set `human_operator: "auto"` when the
trigger fired automatically; this matches the
`auto_create_from_vigilance` convention in the existing
supply-chain ledger (the 2026-04-26 PRE-RELEASE B10 fix tightened
this from optional to required on the pending side too — operator
identity discipline applies to every entry kind).

### 17.7 Storage + Rotation

Calibration ledgers live at:

```
.claude/brain/<domain>-calibration-ledger.jsonl
```

One ledger per domain (NOT per Brain — a Brain may have many
domains and thus many ledgers). Empirically, healthy domains
produce 0 entries — the storage cost is bounded by triage need.
A domain with 50 triage events per year + ~1 KB per entry yields
~50 KB/year/domain. A 4-Brain × 10-domain ecosystem accumulates
~2 MB/year before rotation.

A conformant implementation SHOULD rotate ledger files annually
to `<domain>-calibration-ledger-{year}.jsonl`. Rotation is an
implementation choice, not a normative requirement.

The reference reader globs `<domain>-calibration-ledger*.jsonl`
so rotation is transparent — readers concatenate the streams
chronologically and fold as if they were one ledger.

### 17.8 Cross-Brain Aggregation

**v1 posture: NO cross-Brain calibration aggregation.**

Calibration ledgers stay LOCAL to each Brain. The ecosystem Brain
does NOT aggregate calibration health from children. Operators
asking "are my children's calibration ledgers fresh?" address
that question by inspecting the children's domain-calibration
domain scores via the existing fractal-composition pipeline (§9).

The high-trust nature of calibration data — operator handles,
verbatim rationale prose, references to internal tooling —
matches the §16.6 supply-chain-signal posture. A future v2
A2A `domain-calibration-signal` message type with bidirectional
opt-in is a candidate; explicitly out of scope for v1.

Implementations MUST NOT auto-share calibration entries via
A2A in conformant v1 deployments.

### 17.9 The domain-calibration Sensor

A Brain implementing §17 SHOULD ship a `domain-calibration`
sensor that:

1. Reads all `*-calibration-ledger*.jsonl` files under
   `.claude/brain/`.
2. Computes per-domain calibration health (open count vs
   triaged count vs ledger freshness).
3. Aggregates into a single `domain-calibration` CMDB envelope.
4. Emits envelope-supplied confidence based on a tuple-aware
   ledger-state signal (§3.1, v2.7+): `(has_ever_fired,
   last_triage_age)`. Rationale: a domain with zero entries
   ("no signal yet") and a domain with a recently-triaged entry
   ("signal exists and is current") look identical to a
   freshness-only metric. The tuple distinguishes them.

The `domain-calibration` sensor's own calibration trigger MUST
be hard-coded to `Manual` — automated triggers against the
sensor's own ledger create a bootstrap-loop class of failure.
The sensor calibrates other domains; humans calibrate it.

A conformant Brain MUST default the `domain-calibration` domain
to weight 0.0 (advisory) at v1. Promotion to non-zero weight
requires §15.5-equivalent calibration evidence.

### 17.10 Carve-out: Existing Ledgers

The following ledger instances predate v2.8 and are intentionally
NOT migrated to `domain-calibration-ledger-v1`:

- **`judge-integrity-ledger-v1`** (§15.3) — agent-behavior judge
  red-miss tracking. Per-family fields (scenario_id, red_sample_id,
  failure_mode, judge_models, per_judge_scores, judge_findings,
  judge_explanation) are richer than the unified schema captures.
- **`domain-promotion-ledger-v1`** (§15.5) — domain promotion
  audit decisions. Per-family fields (evidence_bundle reference,
  audit_status, rebalance details) are richer than the unified
  schema captures.
- **`supply-chain-decision-ledger-v1`** (§16.4) — Layer 3
  supply-chain review decisions. Per-family fields (PackageRef,
  triggering_signals[], agent_findings[], remediation_action,
  expires_at) are richer than the unified schema captures.

Each of these retains its own schema, its own on-disk file, its
own writer convention, and its own §-section governance. The
unified schema's existence does NOT obligate migration — the
carve-out is normative.

Future spec evolution MAY consolidate any of the three under
`domain-calibration-ledger-v2` (or later), but such a
consolidation requires its own METHODOLOGY-EVOLUTION entry and
explicit migration guidance. This section's stance: additivity is
the discipline; convergence is a future option, not an
obligation.

### 17.11 Reference Implementation

Reference Rust implementation: NeuroGrim crates
`neurogrim-core::calibration_ledger` (writer + reader),
`neurogrim-sensory::domain_calibration` (the meta-observer
sensor), and `neurogrim-cli::commands::domain_calibration` (the
operator triage CLI). Per-Brain registries declare the
`domain-calibration` domain at advisory weight 0.0 in v1.

Reference operator workflow:

```
$ NEUROGRIM_OPERATOR=alice neurogrim domain-calibration list \
    --project-root . --open-only
# … shows pending entries awaiting triage …

$ NEUROGRIM_OPERATOR=alice neurogrim domain-calibration triage \
    --domain test-health \
    --pending-ts 1777310000.0 \
    --decision no-action \
    --notes "Score drop was a deliberate test-suite restructure; recalibrate next sprint."
```

See METHODOLOGY-EVOLUTION (planned: §16) for the broader
rationale: §17 generalizes a pattern that emerged across three
independent epics (judge-integrity, domain-promotion,
supply-chain-decision) and formalizes it as a methodology piece.
The rename from "self-coherence" (master plan) to
"domain-calibration" (this section) was driven by the §8
correlation-coherence collision surfaced during the Layer-2
review.

### 17.12 Operator-calibration ledger family (v2.11+)

§§17.1–17.11 govern **domain calibration** — how does the operator's
evaluation relate to a domain's automated score? **Operator
calibration** (this section) is the sibling family that asks the
inverse question: how does the operator's evaluation relate to an
agent skill's invocation? Both families share the storage convention
(`.claude/brain/`-prefixed JSONL), the operator-identity discipline
(NEUROGRIM_OPERATOR per §17.6), advisory weight 0.0 default, and the
v1→v2 calibration-gated promotion path (§15.5 evidence-bundle).

The two families are structurally distinct:

- **Domain calibration** (§§17.1–17.11): per-domain, file-per-domain
  at `.claude/brain/<domain>-calibration-ledger.jsonl`. Per-domain
  calibration triggers + 2-phase Pending/Triaged supersedes pattern.
- **Operator calibration** (this subsection, §17.12): per-skill-
  invocation, single-file at `.claude/brain/invocation-ledger.jsonl`
  (the existing high-frequency append-only ledger that already
  records skill invocations per Axis 4 v1, 2026-04-22). Single-row-
  kind disposition records linked back to skill records via
  `invocation_id`.

#### 17.12.1 Schema

The invocation ledger conforms to `invocation-ledger-v1.schema.json`
(NEW v2.11+). The schema's top-level `oneOf` discriminates two
entry kinds:

- **`SkillEntry`** — the existing skill-invocation record (written
  by the PostToolUse hook per the Axis 4 v1 documentation in
  `NeuroGrim/docs/invocation-ledger.md`). Required: `schema_version`,
  `ts`, `type` (const `"skill"`), `name`, `session_id`,
  `invocation_id`. Optional: `disposition` (forward-compat for
  writers that capture the disposition at invocation time).
- **`DispositionEntry`** — NEW. Required: `schema_version`, `ts`,
  `entry_kind` (const `"disposition"`), `invocation_id` (references
  a SkillEntry's `invocation_id`), `disposition_kind`,
  `human_operator`. Both row kinds enforce `additionalProperties:
  false` — extensions land in a per-entry `extensions` object
  rather than ad-hoc top-level fields.

#### 17.12.2 Closed-set disposition vocabulary

Implementations MUST validate `disposition_kind` against the
following closed set (4 entries, additive promotion path same as
§5.4.1 hat-contract tool names):

| Value | Meaning |
|-------|---------|
| `accepted` | Operator took the suggestion as-is. |
| `rejected` | Operator did not take the suggestion. |
| `modified` | Operator took the suggestion with changes. |
| `superseded` | Operator chose a different path that addressed the same underlying need. |

New vocabulary terms require a spec change with explicit
METHODOLOGY-EVOLUTION entry; implementations MUST reject unknown
vocabulary terms.

#### 17.12.3 Privacy contract (BR-5)

Disposition records preserve the v1 invocation-ledger privacy
invariant declared in `NeuroGrim/docs/invocation-ledger.md`:
**closed-set vocabulary + ts + invocation_id + operator handle
ONLY.** Implementations MUST NOT capture free-text justification on
disposition records at v1; the schema's `additionalProperties:
false` on DispositionEntry enforces this structurally. v2 may
re-open with strict prose-only-no-paths discipline + dedicated
opt-in flag (BACKLOG B-23).

#### 17.12.4 Capture mechanism

Disposition records MUST be captured via explicit operator action
at v1 (no auto-inference from session traces). The reference
implementation provides a CLI subcommand:

```
$ NEUROGRIM_OPERATOR=alice neurogrim disposition record \
    --invocation-id <id> \
    --kind <accepted|rejected|modified|superseded> \
    --project-root .
```

Auto-inference of disposition from observed follow-up actions
(operator immediately invoked another skill, edited a file, etc.)
is OUT OF SCOPE for v1 and is a v2 candidate per BACKLOG B-23.
v1's explicit-only posture is structural: the existing PostToolUse
hook is `Skill`-only, so the substrate to observe follow-up
Bash/Edit/Write actions does not yet exist.

#### 17.12.5 Recursion guard (MUST)

The operator-calibration sensor's own findings MUST NOT be valid
disposition targets. Concretely: implementations MUST reject
`--invocation-id` references whose source `name` matches the
sensor's finding-kind prefix (`operator_calibration:*`).
Recursion-loop closure mirrors the §17.9 `Manual` calibration
trigger discipline for the domain-calibration sensor's own family.

#### 17.12.6 Aggregation-only export (MUST)

The operator-calibration sensor's CMDB output MUST emit aggregate
totals only — no per-invocation rows, no per-skill breakdowns at
v1. Per-skill calibration breakdown is a v2 candidate per BACKLOG
B-23. Aggregation discipline is the BR-5 privacy mitigation that
keeps disposition data from flowing beyond the per-Brain CMDB.

#### 17.12.7 Sample-size disclosure (MUST)

The sensor MUST report `dispositioned_count` AND `total_invocations`
as exported variables alongside any score. The score MAY be `null`
when `dispositioned_count < N_MIN` (reference value: N_MIN=20,
mirroring `LOW_CONFIDENCE_TOTAL_INVOCATIONS` in
`capability-hygiene`'s ledger reader). Below N_MIN, the sensor
MUST emit an `operator_calibration:low_confidence` advisory finding
to surface the small-sample state explicitly. Selection bias
(operators disposition rare events; routine accept-all use is
invisible) is the dominant interpretive risk; the sample-size
disclosure surface is the structural mitigation.

#### 17.12.8 Per-Brain scope (LOCAL)

Operator-calibration data is LOCAL to each Brain. Implementations
MUST NOT auto-share disposition entries via A2A in conformant v1
deployments (mirrors §17.8 lock for domain-calibration). A
cross-Brain `operator-calibration-signal` A2A message type is a v2
candidate per BACKLOG B-23, parallel to the deferred
`hat-contract-signal` (§5.4.1), `trust-budget-signal` (§16.8), and
`domain-calibration-signal` (§17.8) types.

#### 17.12.9 The operator-calibration sensor

The reference implementation provides a sensor at
`neurogrim-sensory::operator_calibration` that reads the same
`.claude/brain/invocation-ledger.jsonl` file consumed by
`capability-hygiene`'s `read_invocation_ledger()` reader. The two
sensors have separation-of-concerns by construction: the existing
reader silently skips DispositionEntry rows (no `name` field at
the skill level); the new sensor recognizes both row kinds and
groups disposition rows by `disposition_kind`.

The score model:

```
dispositioned_count = count of DispositionEntry rows
total_invocations = count of SkillEntry rows
accepted_count = count of dispositioned rows where disposition_kind == "accepted"

If dispositioned_count < N_MIN (20):
    score = null
    findings += operator_calibration:low_confidence (advisory)
Else:
    score = round(100 * accepted_count / dispositioned_count)
```

Non-dispositioned skill invocations are NOT in the denominator —
they are "not yet judged," not "neutral." This is the structural
fix for selection bias.

#### 17.12.10 v1→v2 promotion

Promotion of operator-calibration's advisory weight 0.0 to non-zero
weight requires §15.5-equivalent calibration evidence: a ≥30-day
collection window AND ≥50 dispositions across a representative
session population, reviewed via the §15.5 promotion-evidence-
bundle pattern. Automated promotion is explicitly out of scope —
the sensor's own data informs whether to elevate the sensor's
findings to gating power, which creates a circular accountability
that human review MUST resolve.

---

## Appendix A: Agent Output Schema

> **Canonical location:** `schemas/agent-output-v1.schema.json`
>
> This appendix is a snapshot as of spec v2.1. The canonical schema file in the
> `schemas/` directory is the authoritative source.

The agent output schema is a JSON Schema (draft-07) document that validates the output
of `agent` mode. The schema enforces:

- 12 required top-level fields (Section 6.1; was 11 pre-v2.7 — `unified_confidence` added in v2.7)
- Per-domain object structure (Section 6.2)
- Recommendation object structure (Section 6.3)
- Optional field types (Section 6.4)
- `additionalProperties: false` at every nested level for strict validation; the root
  `additionalProperties` was relaxed to `true` in v2.7 as a deliberate one-time
  forward-compat enabler (§6.5 — does not loosen nested structures)

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
    },
    "confidence": {
      "type": "integer",
      "minimum": 0,
      "maximum": 100,
      "description": "Optional sensor-supplied confidence in [0, 100] (added in v2.7). When absent, the Brain falls back to age-decay of meta.updated_at per §4.4. When present, the envelope value takes precedence — sensors with their own freshness signal (cache-age, registry-fetch staleness) MAY emit this directly. See §3.1."
    }
  }
}
```

The meta envelope enables the Brain to:
- Detect schema version mismatches
- Compute confidence from `updated_at` age (or use sensor-supplied
  `confidence` when present, v2.7+)
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
| 6. Interface | Agent output builder | 12 required JSON fields (v2.7+), schema validation |
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
| **A2A Message** | A single payload exchanged between peer Brains, wrapped in an envelope (`a2a-envelope-v1.schema.json`). Canonical types as of v2.6: score.updated, gate.changed, ecosystem.scored, incident.detected, incident.resolved, snapshot.requested, snapshot.delivered, proposal.created, proposal.resolved, config.changed, supply-chain-signal (v2.6, bidirectional opt-in — §16.6). |
| **Accepted-advisories file** | Operator-curated list (e.g., `.claude/supply-chain-accepted-advisories.toml`) recording supply-chain advisories accepted as not-currently-actionable. Each entry MUST have a non-empty `note` field documenting WHY (the hygiene lever; silent acceptance is the failure mode the file exists to prevent). See §16.2. |
| **Bidirectional opt-in** | Tighter consent model used for `supply-chain-signal` (v2.6). Both peers MUST declare the message type in their Agent Card `accepts[]` before signals flow — a stronger requirement than the one-direction-by-declaration default of other A2A types. Motivated by legal-exposure and false-positive-multiplication concerns. See §16.6. |
| **Action type** | A categorized operation (e.g., "clear-gate", "deploy") with a default autonomy level and blast radius. |
| **Adversarial audit** | (Red-mode.) Running a calibrator against red samples to verify the judge can detect known failure modes (one-sided ceiling check, §15.3). Distinct from **Promotion audit** (evidence-bundle review that flips a domain's weight) and **Judge-integrity audit** (append-only ledger of red-misses + operator triage). The §17.1 disambiguation table is the canonical sense-distinction. See §15.3. |
| **Advisory domain** | A domain with weight 0.00 that contributes information but not to the unified score. |
| **Agent Card** | A JSON document (`agent-card-v1.schema.json`) published by a Brain at `/.well-known/agent-card.json`. Declares identity, capabilities (which A2A message types accepted/emitted), transport, and authentication. Consumed by peer Brains to discover and invoke this Brain. |
| **Audit failure handling.** | A failed `agent-behavior` domain promotion audit (§15.5) MUST stop the promotion. Implementations SHOULD record the failed attempt in the promotion ledger and SHOULD NOT retry until remediation work (rubric edit, sample library expansion, judge rotation, or taxonomy revision) ships. See §15.5. |
| **Autonomy level** | One of four levels (auto, notify, approve, blocked) controlling whether an action executes without human approval. |
| **Blast radius** | The scope of impact of an action: low, medium, high, or critical. |
| **Brain** | The central scoring and reasoning engine that reads CMDBs, computes health scores, detects patterns, and produces recommendations. |
| **Cadence obligation.** | Post-promotion (§15.5), implementations SHOULD maintain calibration at a documented cadence (e.g., weekly at the lower-cost profile, quarterly at the higher-fidelity profile). Ensures drift detection in bounded time rather than ad-hoc. See §15.5. |
| **Calibration.** | Judge calibration (§15.3): before any scenario's trial results are admitted to the CMDB, the judge MUST score that scenario's gold samples. If any `\|judge_score − human_score\|` exceeds 10 points for a `gold-good` or `gold-bad` sample, the harness emits `drift-warning` or `drift-blocker`. Distinct from **Operator calibration** (§17.12) and the **domain-calibration ledger** (§17). See §15.3. |
| **CMDB** | Configuration Management Database. In LSP Brains: a JSON file containing a snapshot of some aspect of project state, written by a sensory tool. |
| **Condition tree** | A JSON expression tree evaluated by the correlation engine to determine whether a pattern fires. |
| **Confidence** | A 0-100 integer indicating how trustworthy a score is. The spec uses the term in three distinct scopes — see **envelope confidence**, **per-domain confidence**, **unified confidence**, and **children[] confidence** for the disambiguated definitions. The bare term "confidence" is acceptable when context makes the scope unambiguous. |
| **envelope confidence** | The optional `confidence` field at the root of a CMDB envelope (`cmdb-envelope-v1.schema.json`, v2.7+). Sensor-supplied freshness signal in [0, 100]. When present, takes precedence over the Brain's age-decay computation; when absent, the Brain falls back to age-decay of `meta.updated_at`. See §3.1 + §4.4. Distinct from **per-domain confidence** (downstream of envelope confidence) and **unified confidence** (aggregate across domains). |
| **per-domain confidence** | The `confidence` field on each entry in the `domains` map of an agent-output (§6.2). Computed from envelope confidence (when supplied) or via age-decay of `meta.updated_at` (§4.4). The value used in effective-score computation (§4.5). |
| **unified confidence** | The `unified_confidence` field at the root of agent-output (v2.7+). Weighted-mean of per-domain confidence over scored (non-advisory) domains: `round(sum(d.confidence * d.weight) / sum(d.weight))`. Receivers SHOULD use this for peer-to-peer trust decisions (§6.7). Distinct from per-domain confidence (one Brain has many of these, one of those). |
| **children[] confidence** | The `confidence` field on each entry in the `children[]` array of an ecosystem-mode agent-output (§9.4). Aggregate confidence across the child Brain's scored domains, computed with the same weighted-mean formula as **unified confidence** for parity. The two share semantics; the only difference is scope (root = this Brain; children[] = an aggregated child Brain). |
| **Cultural Substrate** | The invariant floor that governs HOW agents communicate (both agent↔human and agent↔agent). Declared in a culture manifest; carried as identical peer-local copies across every participating Brain; applied as the final step of the output pipeline (§14). |
| **Declared crate** | An entry in `trust-budget.toml`'s `declared_crates[]` array (v2.10+) — `name`, `ecosystem` (cargo / pypi / npm / system), optional `notes` and `seeded` fields. Direct dependencies only at v1; transitive crates deferred to v2 per BACKLOG B-23. See §16.8. |
| **Delta tracking.** | §15.5 requirement that implementations SHOULD expose a run-to-run diff (e.g., `abv-run diff <before> <after>`) so humans can verify a skill refinement actually moved scores in the intended direction. Gold samples MUST NOT be edited to accommodate a refined agent — they are the frozen baseline. See §15.5. |
| **Derived** | One of three truth layers (§2.2). Computed from source and runtime artifacts on demand, never committed, always reproducible. Gitignored. Re-computation is cheap; the derived product is a projection of its inputs. |
| **Culture Invariant** | A value in the cultural substrate that can only tighten, never loosen — analogous to safety invariants in autonomy resolution (§5.5). Five canonical: positivity, integrity, honesty, critical-but-kind, respect. |
| **Culture Manifest** | The `culture.yaml` document (validated against `culture-manifest-v1.schema.json`) declaring the canonical values and their application. Version-stamped; distributed as identical copies. |
| **Disposition kind** | One of four closed-set values (`accepted`, `rejected`, `modified`, `superseded`) that an operator may assign to an agent skill invocation (v2.11+). Vocabulary additivity follows the same discipline as §5.4.1 hat-contract tool names — new terms require a spec change. See §17.12.2. |
| **Disposition record** | An append-only entry on the invocation-ledger (kind `DispositionEntry` per `invocation-ledger-v1.schema.json`, v2.11+) recording the operator's judgment of a specific agent skill invocation. Required fields: `schema_version`, `ts`, `entry_kind`, `invocation_id`, `disposition_kind`, `human_operator`. Free-text justification is FORBIDDEN at v1 (BR-5 privacy contract). See §17.12.1 + §17.12.3. |
| **Domain** | A named aspect of project health (e.g., "code-quality", "test-health"). Each domain has a score, confidence, and weight. |
| **Dual brain** | Architecture where a local brain and external brain share state via a common protocol (Section 10). |
| **Ecosystem** | Multiple Brains composed fractally, where a parent Brain aggregates scores from child Brains (Section 9). |
| **Effective score** | A domain's score after confidence weighting: `raw * confidence / 100`. |
| **Federated pattern** | An A2A message type (v2.12+, kind `federated-pattern`) carrying anonymized pattern features between peer Brains under bidirectional opt-in. Closed-set `pattern_kind` vocabulary at v1: `vigilance-pattern`. `feature_vector` is closed-set numeric-only (privacy under composition lock). Recursion guard via `origin_set[]` array of opaque brain-id hashes (max 4 hops). Two-layer rate limit (sender + receiver) per BR-6. v1 federation flows parent↔child within the fractal-composition tree only; sibling federation is a v2 candidate. See §16.6.1. |
| **Pattern-aggregation ledger** | Per-Brain append-only `.claude/brain/pattern-aggregation-ledger.jsonl` (v2.12+) recording received and emitted federated-pattern messages. `oneOf` row-kind discrimination: `ReceivedEntry` (with optional `dropped_reason` for rate-limit / recursion-guard / schema-validation drops) vs `EmittedEntry` (sender-side audit trail per Q12 lock). Validates against `pattern-aggregation-ledger-v1.schema.json`. Read by the `federated-patterns` aggregator sensor; observability-only at v1. See §16.6.1. |
| **Gate** | A pass/fail quality check that blocks specified actions when failing. |
| **Governance** | The Brain subsystem (§5) that decides what recommendations the Brain may act on, which human approval each action requires, and which invariants cannot be overridden. Expressed as gates, hats, and autonomy levels. |
| **Hat** | An operational mode in LSP Brains. The spec uses the term in two distinct scopes (v2.9+) — see **registry hat** (§5.4) and **persona hat** (§5.4.1) for the disambiguated definitions. The bare term "hat" is acceptable when context makes the scope unambiguous. |
| **Hat contract** | The schema-typed tool-boundary declaration optionally attached to a **persona hat** as YAML frontmatter, conforming to `hat-contract-v1.schema.json` (v2.9+). Declares `allowed_tools[]`, `forbidden_tools[]` (closed-set vocabulary of 8 tool names), and optional `network_targets`. Validated statically by the `capability_hygiene` sensor; runtime enforcement deferred to v2 per BACKLOG B-23. See §5.4.1. |
| **Incident pattern** | A cross-domain signal with recurrence tracking and severity escalation. |
| **LSP Brains** | The language-agnostic specification for agent nervous systems (this document). |
| **MCP** | Model Context Protocol. JSON-RPC based protocol for tool discovery and invocation between clients and servers. In LSP Brains, MCP is used for (1) sensory tool discovery (Brain-as-MCP-client, §3.7), (2) Brain exposure to LLM agents (Brain-as-MCP-server, Appendix F). MCP is NOT used for Brain-to-Brain peer communication — see A2A (§13, Appendix G). |
| **Multi-judge consensus.** | A future spec revision MAY require multi-judge consensus for scenarios whose rubrics exhibit high historical variance. v1 permits single-judge scoring; implementations promoting `agent-behavior` past advisory weight SHOULD deploy at least two judges and take the median. See §15.3. |
| **NeuroGrim** | The reference implementation of LSP Brains, written in Rust. |
| **Operator calibration** | A first-class observability primitive (v2.11+) that captures the operator's judgment of agent skill invocations as append-only **disposition records** on the existing invocation-ledger. Sibling family of **domain calibration** (§17): both share storage convention + operator-identity discipline + advisory weight 0.0 default; different observation surface (per-skill-invocation vs per-domain). v1 explicit-only via `neurogrim disposition record` CLI; auto-inference deferred to v2 per BACKLOG B-23. See §17.12. |
| **Output modes** | The Brain's display modes (agent, score, health, trend, validate, propose, plan — §6.6, §11.1). Each targets a different consumer: JSON for machines, terse lines for humans, detailed reports for operators. |
| **Peer Brain** | Another Brain with which this Brain communicates via A2A. In fractal composition (§9): parent/child. In dual brain (§10): local/external. |
| **Persona** | A human user role that controls output verbosity and field filtering. Distinct from **persona hat** (the agent-facing operational lens — §5.4.1). |
| **Persona hat** | An agent-facing operational lens (e.g., adversary, supply-chain-auditor, source-reader) declared at `.claude/skills/hats/<hat>.md` and used to calibrate subagent briefings (v2.9+). A persona hat MAY carry a **hat contract** (§5.4.1 — schema-typed tool-boundary declaration). Contrast with **registry hat** (§5.4 — Brain-scoring concept) and **Persona** (the human user role for output formatting). See §5.4.1. |
| **Promotion audit** | The evidence-bundle review that promotes an advisory-weight domain to non-zero weight (§15.5). Per the §15.5 promotion-path discipline: requires operator-declared calibration audit, append-only promotion ledger entry, `sum(domain_weights) == 1.0` preservation, and a reversal operation. Distinct from **Adversarial audit** (red-mode judge run) and **Judge-integrity audit** (red-miss ledger). The §17.1 disambiguation table is the canonical sense-distinction. See §15.5. |
| **Promotion path.** | (Added v2.5; METHODOLOGY-EVOLUTION §13; S10-DOMAIN-PROMOTION.) The mechanism by which `agent-behavior` and similar advisory-weighted domains may be promoted past `domain_weights: 0.0`. Requires operator-declared calibration audit, append-only promotion ledger, `sum(domain_weights) == 1.0` preservation, and a reversal operation. Generalizes to any advisory-weighted domain with a calibration-harness equivalent. See §15.5. |
| **Proposals.** | Systemic agent-behavior issues (three consecutive runs below 40, judge drift beyond the calibration window, sustained feedback clusters around one target file) MUST be surfaced as proposals in the Brain's proposal ledger (§12) with `category: "agent-behavior-regression"`. The operator triages per §12's normal workflow. See §15.5. |
| **Red samples.** | (Added v2.4; METHODOLOGY-EVOLUTION §12; S9-ABV-RED.) Pre-recorded responses paired with an `expected_score_ceiling` the live judge MUST stay under. A red-miss (judge_score > ceiling) indicates the judge failed to detect a specific failure mode. Red samples are one-sided bounds (gold samples are two-sided), GROW over time as failure modes surface in production feedback, and MUST NOT feed the refinement loop through automation. See §15.3. |
| **Registry** | The `brain-registry.json` file containing all Brain configuration. Source truth. |
| **Registry hat** | A hat declaration in `brain-registry.json:config.hats.*` (§5.4) carrying `description`, `domain_emphasis`, `autonomy_bias`, and optionally `suggest_when`. Affects Brain scoring (domain-emphasis multipliers) and gate autonomy resolution. Contrast with **persona hat** (§5.4.1 — operational lens declared at `.claude/skills/hats/`). The two are intentionally distinct concepts (v2.9+). See §5.4. |
| **Scanner-chain compromise** | Attack class where the security scanner binary itself is the attack vector (e.g., the LiteLLM 2026-04-23 incident, where a trojanized Trivy release exfiltrated CI tokens). The structural mitigation in v2.6+ is the §16.2 prohibition on shelling out to external scanner binaries in the primary scoring path. See METHODOLOGY-EVOLUTION §15. |
| **Supply-chain awareness** | First-class Brain concern (v2.6). Three composing layers: Layer 1 mechanical SCA, Layer 2 deep-signal vigilance, Layer 3 agent-assisted human review. See §16. |
| **supply-chain-auditor hat** | A **persona hat** (§5.4.1) for package-level review (provenance verification, unreviewed-dep audit, remediation gate). Required by §16.5; content is implementation-defined per §5.4.1. v2.9+ recommends authoring its frontmatter with `forbidden_tools: [package_install, Bash]` and `network_targets.allowed: [osv.dev]` to make the read-only / OSV-only constraints machine-checkable. |
| **supply-chain-sca** | Layer 1 mechanical-SCA domain (§16.2). Lockfile parsing + vulnerability-database query; default weight 0.0 in v1 (advisory). Reference implementation is NeuroGrim's `supply_chain_sca/` module. |
| **supply-chain-signal** | A2A message type (v2.6) carrying supply-chain findings between peer Brains under bidirectional opt-in consent. Payload conforms to `a2a-supply-chain-signal-v1.schema.json`. See §16.6. |
| **supply-chain-vigilance** | Layer 2 deep-signal-vigilance domain (§16.3). Probabilistic findings on publishing behavior; default weight 0.0 in v1 (advisory). |
| **supply-chain decision ledger** | Append-only `supply-chain-decision-ledger.jsonl` matching `supply-chain-decision-ledger-v1.schema.json`. Records Layer 3 review decisions (accept / reject / pin-to-last-good / review-pending / review-triaged) with operator identity + rationale. See §16.4 + §16.7. One of three pre-v2.8 ledger instances of the 2-phase Pending → Triaged pattern (alongside **judge-integrity ledger** + **promotion ledger**); carved out from the v2.8 unified schema per §17.10. |
| **domain-calibration ledger** | Append-only `<domain>-calibration-ledger.jsonl` files matching `domain-calibration-ledger-v1.schema.json`. Records per-domain automated-vs-human-decision disagreement entries (pending) and operator triage decisions (triaged). v2.8+. Triggers via discriminated `CalibrationTrigger` union (OutOfExpectedRange / SignalClassFired / Manual). 4-class triage_decision enum (confirmed/mislabeled/gap/no-action). One ledger per domain (NOT per Brain). LOCAL to each Brain — no A2A aggregation in v1. See §17 (entire). |
| **domain-calibration sensor** | The CMDB sensor that reads `*-calibration-ledger*.jsonl` files and reports per-domain calibration health (open vs triaged counts; ledger freshness; tuple-aware (has_ever_fired, last_triage_age) confidence). Emits envelope-supplied confidence per spec §3.1 v2.7+. Hard-coded `Manual` calibration trigger to close the bootstrap-loop class of failure. Default weight 0.0 (advisory) in v1. See §17.9. |
| **Judge-integrity audit** | The append-only ledger of red-misses (judge_score > red sample's `expected_score_ceiling`) plus operator triage of those misses (§15.3 + §15.4). Per §15.5: red-misses MUST NOT be auto-resolved; humans decide whether each is a judge failure (rubric tightening or red-sample expansion), a rubric gap (scenario edit), or a sample mis-label (sample retirement). Distinct from **Adversarial audit** (the calibration run that produces misses) and **Promotion audit** (the domain-weight promotion gate). See §15.3 + §15.4. |
| **judge-integrity ledger** | Pre-v2.8 instance of the 2-phase Pending → Triaged ledger pattern (matches `judge-integrity-ledger-v1.schema.json`). Records judge red-misses + operator triage. Per-family fields: scenario_id, red_sample_id, failure_mode, judge_models, judge_findings, judge_explanation. Carved out from the v2.8 unified schema per §17.10. See §15.3 + §15.4. |
| **promotion ledger** | Pre-v2.8 instance of the 2-phase Pending → Triaged ledger pattern (matches `domain-promotion-ledger-v1.schema.json`). Records domain promotion audit decisions. Per-family fields: evidence_bundle reference, audit_status, rebalance details. Carved out from the v2.8 unified schema per §17.10. See §15.5. |
| **Runs MUST account for token cost.** | Imperative §15.7 requirement: the agent-behavior harness SHALL record aggregate input + output token counts per run and SHALL support a budget ceiling that aborts the run when exceeded. Prevents runaway CI spend. See §15.7. |
| **Runtime** | One of three truth layers (§2.2). Snapshots of external system state — CMDB files written by sensory tools. Accurate at capture time, decays with age via confidence decay (§4.4). |
| **Runtime enforcement** | Observing actual tool invocations at runtime and cross-referencing against a hat contract's declared `forbidden_tools[]` / `network_targets.allowed[]` (§5.4.1) or a trust-budget's `declared_shell_outs[]` / `declared_external_services[]` (§16.8). Contrast with static validation — checking catalog inventories at scoring time without observing live execution. Per §5.4.1 + §16.8: v1 is static-validation-only; runtime enforcement is deferred to v2 per BACKLOG B-23. See §5.4.1. |
| **S7-ABV** | Agent Behavior Verification — the reference-implementation campaign in NeuroGrim's roadmap that materializes spec §15 (Agent Behavior Verification Protocol). See `NeuroGrim/roadmap/` epic catalog. |
| **Safety invariant** | A rule that cannot be overridden by confidence or effectiveness -- e.g., "destroy is always blocked". |
| **Safety rail.** | The §15.5 boundary: the agent-under-test MUST NOT be given write access to skill files, hat catalogs, or culture manifests. Its feedback is text only — humans read the ledger, group feedback by target, and refine skills by hand. Prevents the harness from drifting into self-training. See §15.5. |
| **Sensory tool** | A script or program that observes external state and writes a CMDB file. "Sensory tools" (plural) refers to the set of all such tools a Brain consumes. |
| **Sensory tools** | Plural of **Sensory tool** — see above. Used when describing the full set a Brain consumes. |
| **Source** | One of three truth layers (§2.2). Hand-maintained artifacts that define system behavior — registries, schemas, gates declarations. Committed to version control; authoritative. |
| **Subprocess** | One of two conformant child-invocation transports in fractal composition (§9.1). Parent Brain spawns the child as an OS process and reads its stdout. Legacy but still conformant; the zero-infrastructure path for CI one-shots and offline adopters who haven't stood up an A2A server. A2A (§13) is RECOMMENDED for peer-Brain invocation in v2.1+. |
| **Task (A2A)** | A unit of interaction between peer Brains. A task has creation, optional streaming progress, completion, and idempotency semantics. See §13.3 and Appendix G.3. |
| **Trajectory** | The trend analysis of scores over time: velocity, acceleration, classification. |
| **Trajectory intelligence** | The Brain's capability (§7) of computing velocity + acceleration from score history and surfacing them as first-class signals that shape recommendations and autonomy decisions. "Am I getting healthier or sicker?" — the question trajectory intelligence answers. |
| **Trust budget** | A first-class supply-chain primitive (v2.10+) declaring a Brain's trust surface — third-party crates, shell-out scripts, external services — as a schema-typed contract. Conforms to `trust-budget-v1.schema.json`. Sensor cross-references declared vs actual; emits `trust_budget:undeclared:*` and `trust_budget:overdeclared:*` advisory findings (drift in either direction). Composes with §5.4.1 hat-contract `forbidden_tools` + `network_targets.allowed` for per-hat trust composition. v1 advisory only; v2 hard gates per BACKLOG B-23. See §16.8. |
| **trust-budget.toml** | The operator-authored TOML file at each Brain's repo root (committed, NOT under `.claude/`) declaring `declared_crates[]`, `declared_shell_outs[]`, `declared_external_services[]` (v2.10+). Each entry MAY carry a `seeded` boolean to suppress first-run findings on operator-acknowledged surface. Validates against `trust-budget-v1.schema.json`. See §16.8. |
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
| `supply-chain-signal` | Payload conforms to `a2a-supply-chain-signal-v1.schema.json` (§16.6, §16.7). Bidirectional opt-in: both peers MUST declare the type in their Agent Card `accepts[]` before signals flow. |

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
