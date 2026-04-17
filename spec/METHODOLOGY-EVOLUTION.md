# LSP Brains: Methodology Evolution Analysis

**Date:** 2026-04-11 (original) — **Updated:** 2026-04-17 (hybrid MCP + A2A)
**Context:** Stage 5 complete (7/7 stories). Three deep audits synthesized.
**Purpose:** Identify structural improvements to the underlying methodology.

---

## 7. Cultural Substrate (2026-04-17)

### Problem

LLM agents carry emotional activations in their token embeddings — this is observable in
Anthropic's interpretability research. Those activations shape outputs regardless of
surface prompting. An agent that is "polite on the surface" but carrying unspoken
condescension in its latent space will leak condescension in ways no schema catches.
Ignoring these activations doesn't make them disappear; it just lets them drift.

Existing personalization layers — `human-comms` (per-human preferences), hats
(attentional bias), personas (audience adaptation) — handle style, focus, and verbosity.
None of them govern *how an agent treats the conversation partner*. The methodology had
no floor. A hat could amplify "urgency" and the agent could become curt in the process,
with nothing to push back.

### The Insight

Declaring culture beats denying it. If the emotional substrate is there whether or not
we name it, naming it gives us three things the alternative doesn't:

1. **A shared reference point** — all participating agents operate from the same five
   values. No negotiation mid-conversation about whether "being blunt" overrides "being
   kind."
2. **An invariant floor** — culture applies after hats, personas, and human-comms. A
   human who prefers terse feedback still gets honest, respectful terse feedback. No
   personalization crosses the floor.
3. **A drift signal** — once the manifest exists, divergence between what we declared
   and what outputs actually look like becomes measurable (future work).

### The Decision

Adopt a **cultural substrate** as a first-class primitive, sibling to `secret-refs` in
pattern ("not a policy, a primitive"). Five canonical values — positivity, integrity,
honesty, critical-but-kind, respect — declared in a small, versioned manifest.

**Key design choices:**

- **Three identical peer-local copies** — each participating agent (ecosystem Brain,
  MotherBrain, LSP-Brains) carries its own `culture.yaml`. No inheritance by reference.
  Rationale: agents are peers; no agent should depend on another to resolve its basic
  operating invariants. Drift becomes a visible health signal rather than a mechanical
  concern.
- **Invariants-only-tighten** — analogous to `safety_invariants` in autonomy resolution
  (§5.5, step 4). Culture applies last in the output pipeline. No hat, persona, or
  human-comms override can cross the floor.
- **No drift sensor in v1** — declaration is enforcement for now. Measurement layer
  (LLM-based or rule-based judge that scores output compliance) is future work. Risk
  acknowledged: declaration can become aspirational. Mitigation: the ecosystem Brain's
  `culture-coherence` domain does at least verify byte-identity across the three copies,
  which catches *structural* drift even if content drift awaits a proper sensor.
- **Exceedingly simple scope** — the entire manifest is ~15 lines, five values, one
  sentence per value. Bloat is the main failure mode; the scope is kept deliberately
  narrow. New values are added only when a real gap is felt, not proactively.

### Spec Changes (additive, no version bump required beyond v2.1)

- **§14 "Cultural Substrate"** (new, after §13) — normative description of the substrate,
  the five values, the invariant semantics, and the relationship to hats/personas/human-comms.
- **Appendix D** — row added for `culture-manifest-v1.schema.json`.
- **Appendix E** — glossary entries: **Culture Manifest**, **Culture Invariant**, **Cultural Substrate**.

### New Schema

- `schemas/culture-manifest-v1.schema.json` — validates `culture.yaml`. Required fields:
  `schema_version`, `version`, `values` (all five), `application`.

### First User: Rubber-Duck Skill

Before drift detection, the substrate gets a concrete user: a **rubber-duck** skill that
spawns a subagent as a Socratic questioner rather than an advisor. The duck asks by
default and offers opinions only when explicitly invited — exactly the critical-but-kind
value in action. Demonstrates that culture is visible in behavior, not just declaration.

### Why This Matters in a Multi-Agent World

In a single-agent world, culture governs agent↔human. In fractal composition (parent↔child)
and dual brain (local↔external), culture *also* governs agent↔agent. If a parent Brain
operates under a "strict" culture and a child under "relaxed," their outputs conflict in
ways no schema catches. A shared manifest means peer Brains cooperate rather than
compound each other's blind spots.

### Impact

- Agents carry an explicit, declared emotional substrate instead of a latent one.
- Critical feedback has a place to land — kindness and honesty coexist by contract.
- The hybrid MCP+A2A protocol split (§6 above) is now complemented by a cultural layer
  that governs how traffic on those protocols actually *reads*.
- Peer Brains in the ecosystem coordinate from a shared floor.

### Implementation

Tracked in the MotherBrain roadmap as:
- **S5-TP-9** (Cultural Substrate) — manifest, spec §14, principle #17, schema,
  rubber-duck skill. Adopter-facing methodology addition.
- **S6-DB-7** (Ecosystem Brain) adds `culture-coherence` domain that watches for drift
  across the three copies.

Drift sensor (LLM-based or heuristic) remains open as future work — intentionally
deferred to avoid premature complexity.

---

## 6. Hybrid MCP + A2A Protocol Split (2026-04-17)

### Problem

The spec used MCP (Model Context Protocol) for every Brain↔world and Brain↔Brain interaction.
MCP is, by design, a tool-semantics protocol: "an LLM calls tools." That fits two roles
cleanly — sensory tool invocation (Brain-as-MCP-client) and Brain exposure to an LLM (Brain-as-MCP-server).
It fits a third role awkwardly: peer Brain communication. Parent↔child in fractal composition
(Section 9) and local↔external in dual brain (Section 10) are agent interactions, not tool calls.
Using MCP for peer coordination meant reinventing task lifecycle, peer discovery, and async
message routing — the exact concerns the Agent2Agent (A2A) protocol already solves.

### The Insight

MotherBrain has two distinct protocol shapes inside it:
- **Tool-call shape** — sensory tools → Brain, Brain → LLM agent. MCP is the right fit. Keep.
- **Peer-agent shape** — parent Brain ↔ child Brain (Stage 4), local Brain ↔ external Brain
  (Stage 6). MCP is the wrong fit. Adopt A2A.

The Stage 4 fractal composition already shipped with subprocess invocation for child Brains,
not MCP. The Stage 6 dual brain is design-only. Neither path is encumbered by deep MCP
integration — the migration surface is smaller than it looks.

### The Decision

**MCP stays** as the normative protocol for sensory tool invocation (spec §3.7 + Appendix F)
and for Brain-as-tool exposure to LLM agents (Claude Code, Cursor, etc.). The `motherbrain-mcp`
crate and the Python SDK `run_server()` helper remain unchanged.

**A2A is adopted** as the normative protocol for Brain-to-Brain peer communication:
- Fractal composition (§9): child invocation MAY use subprocess (legacy, conformant) or
  A2A (RECOMMENDED in v2.1+). MCP is explicitly NOT RECOMMENDED for this role.
- Dual brain (§10): the event protocol (§10.4) is recast as A2A message vocabulary. The
  10 event types (score.updated, gate.changed, ecosystem.scored, incident.detected,
  incident.resolved, snapshot.requested, snapshot.delivered, proposal.created,
  proposal.resolved, config.changed) become A2A message types.

### Spec Changes (v2.0 → v2.1, additive)

- §1.1 scope: add "How peer Brains communicate (A2A Peer Protocol, Section 13)."
- §3.7: add boundary sentence ("MCP is for sensory + LLM; not for peer coordination").
- §9: add §9.7 "A2A Transport Mapping" — ecosystem-registry.json carries optional
  `a2a_endpoint`; presence selects A2A, absence falls back to subprocess.
- §10.4: rewrite "Event Protocol" to delegate to A2A task + message semantics.
- §10.5: clarify shared state protocol is unchanged; A2A is for messages, not state.
- **New §13 "A2A Peer Protocol"** — canonical normative rules.
- **New Appendix G "A2A Integration"** — mirror of Appendix F for peers.
- Appendix E (Glossary): add A2A, Agent Card, Peer Brain, Task (A2A), A2A Message.
- Appendix D: add rows for `motherbrain-a2a` crate.

### New Schemas

- `schemas/a2a-envelope-v1.schema.json` — validates A2A message envelope (message_id,
  task_id, timestamp, brain_id, message_type, payload, metadata).
- `schemas/agent-card-v1.schema.json` — validates Brain Agent Cards (id, capabilities,
  transport, authentication, topology).
- `schemas/brain-registry-v2.schema.json` — additive: `children[].a2a_endpoint` optional;
  `dual_brain.event_transport.mode` with "a2a" default. Schema version stays v2.

### Why v2.1, not v3.0

No existing field is removed; no existing conformance claim is invalidated. Subprocess
invocation remains conformant in §9. The "MCP for peer coordination" pattern was never
mandated (§9 always said "parent Brain invokes the child and parses its JSON output" —
transport-agnostic). v2.1 is an additive refinement; v3.0 is deferred until A2A becomes
`MUST` for child invocation (i.e., until subprocess is removed as a conformant transport).

### Impact

- MCP scope becomes explicit and narrower: sensory + LLM-facing. Easier to reason about.
- A2A brings off-the-shelf task lifecycle, discovery (Agent Card at `/.well-known/agent-card.json`),
  and streaming — the Brain stops reinventing these.
- Stage 6 dual-brain work lands on a real, growing standard (Linux Foundation project)
  instead of a bespoke event protocol.
- Fractal composition gains a peer-native transport without breaking the subprocess path
  that starter-kit adopters and CI one-shots rely on.

### Implementation

Tracked in MotherBrain roadmap as:
- S5-TP-8 (spec + schemas publication)
- S6-DB-1 through S6-DB-6 (motherbrain-a2a crate, ecosystem refactor, A2A server,
  dual-brain pair integration, reference deployment, optional Python SDK helper)

Stage 6 rescoped as "Dual Brain via A2A." Keep-subprocess decision rationale: starter-kit
adopters must not be forced to run an HTTP server for fractal composition to work.

---



## Executive Summary

Stage 5 delivered a transferable specification, a working starter kit, and adoption
documentation. The architecture is sound. The methodology works. But three independent
audits — structural, mathematical, and adoption-focused — converge on the same insight:

**The methodology is better at describing health than at demonstrating it.**

The spec defines 12 sections of rigorous protocol. The starter kit ships 3 sensory tools
that check whether files exist. The gap between what the methodology CAN express and what
it DOES express out of the box is the single biggest barrier to adoption. A team that
follows the 6-step tutorial gets a static number that never changes. The architecture
supports trajectory intelligence, cross-domain correlation, and incident detection — but
none of these features activate with the default sensory tools because the underlying
data never varies.

This document identifies 5 structural improvements that would close that gap.

---

## 1. Continuous Confidence Decay

### Problem

The confidence function is a 4-step staircase: 100/75/50/25 at day boundaries 1/3/7.
This creates cliff effects where the unified score drops 15-25% overnight with zero
actual state change. The trajectory system records these as "degrading" trends. Teams
learn to re-run sensory tools at 23-hour intervals to avoid the cliff — optimizing for
freshness theater rather than information quality.

### The Math

Current step function:
```
age < 1 day  → 100    (0% penalty)
age < 3 days → 75     (25% penalty)
age < 7 days → 50     (50% penalty)
age ≥ 7 days → 25     (75% penalty)
```

A domain with raw=80 experiences effective scores of {80, 60, 40, 20} depending purely
on when someone last ran the sensory tool. The transition from 80→60 happens in a single
instant when the clock crosses 24 hours.

### Proposed Fix

Replace the step function with exponential decay:

```
confidence = 100 × e^(-λ × age_days)
```

where λ = ln(4) / cmdb_very_stale_days ≈ 0.198.

This produces smooth degradation that matches the current thresholds at key points:
- age=0 → 100 (same)
- age=1 → 82 (was 100, smoother onset)
- age=3 → 55 (was 75, gradual)
- age=7 → 25 (same)
- age=14 → 6 (was 25, continues decaying)

The formula is configurable via `confidence_decay_lambda` in the registry, and the
existing `cmdb_fresh_days`/`cmdb_stale_days`/`cmdb_very_stale_days` thresholds can be
used to auto-compute λ.

### Impact

- Eliminates the 24-hour cliff that triggers phantom trajectory degradation
- Removes the perverse incentive to run tools on a clock rather than when data changes
- Makes trajectory velocity track ACTUAL health changes, not confidence oscillation
- The formula is one line of PowerShell vs. the current 4-line if/elseif chain

### Spec Change

Section 4.4 (Confidence Weighting) would add: "Implementations SHOULD use continuous
decay. Implementations MAY use step functions but MUST document the cliff effects in
operator guidance."

---

## 2. Domain Floor Constraints (Non-Linear Scoring)

### Problem

The unified score is purely additive: `sum(effective × weight)`. This means a project
with 90/100 code-quality and 20/100 test-health produces the same unified score as one
with 55/55 on both — if weights are equal. But these situations represent fundamentally
different risk profiles. The first project has a critical gap that the unified score masks.

Biological nervous systems use non-linear integration. Pain in one subsystem doesn't add
to comfort in another — it gates motor responses entirely. The current model has no
equivalent of "this domain is so bad that the overall score should be capped."

### Proposed Fix

Add an optional `floor` field to domain definitions in the registry:

```json
"test-health": {
  "scoring_source": { ... },
  "floor": {
    "min_score": 30,
    "unified_cap": 50,
    "message": "Test health below 30 caps unified score at 50"
  }
}
```

When any domain's effective score falls below its `floor.min_score`, the unified score
is capped at `floor.unified_cap` regardless of other domain scores.

### The Math

Without floors (current):
```
code-quality: 90 × 0.35 = 31.5
test-health:  20 × 0.35 = 7.0
deploy-ready: 80 × 0.30 = 24.0
unified = 62.5 → 62
```

With floor (test-health.floor.min_score=30, unified_cap=50):
```
test-health effective = 20 < 30 → floor triggers
unified = min(62, 50) = 50
```

This correctly signals "there's a critical gap" rather than averaging it away.

### Impact

- Prevents the additive model from masking critical domain failures
- Gives teams a way to declare "this domain is load-bearing"
- Maps to the biological analogy: inhibitory signals that gate the whole system
- Purely additive by default; floors are opt-in per domain

### Spec Change

Section 4.6 (Unified Score) would add: "Implementations SHOULD support per-domain floor
constraints. When an effective score falls below a domain's declared minimum, the unified
score MUST be capped at the floor's declared ceiling."

---

## 3. Trajectory on Raw Scores (Separate Health from Certainty)

### Problem

The trajectory system computes velocity from unified scores, which embed confidence. This
means confidence recovery (re-running a sensory tool without any state change) registers
as "improving" and confidence decay (not running tools for a day) registers as "degrading."
The system cannot distinguish "the project got healthier" from "someone checked."

Additionally, the minimum sample count (3) provides zero statistical power. With 3 samples,
velocity is literally the difference between the last two scores — not a trend, just a
single delta. Any noise of magnitude ≥2 triggers a classification.

### Proposed Fixes

**3a: Track trajectory on raw scores, not effective scores.**

The score history already stores per-domain `{ score, confidence }`. Compute velocity
from the `score` field alone, ignoring confidence fluctuations. This measures "is the
underlying system health changing?" rather than "have we checked recently?"

**3b: Raise minimum samples from 3 to 5.**

At 5 samples with velocity_window=5, n=min(5,2)=2 — averaging 2 points against 2 points.
This provides minimal but real smoothing. At 3 samples, velocity is a single point-to-point
comparison with no averaging at all.

**3c: Add uncertainty bounds to trajectory output.**

Report velocity with a confidence interval: `velocity: 3.2 ± 4.1` signals that the
trend might not be real. The interval width is `stddev × sqrt(1/n + 1/n)` where n is the
window half-size. If the interval includes zero, the classification should be "stable"
regardless of the point estimate.

### Impact

- Eliminates phantom trends from confidence oscillation (the "just checked" illusion)
- Prevents false "degrading" classification from the midnight cliff
- Makes trajectory intelligence trustworthy enough to inform decisions
- Aligns with spec principle 2: "Scoring must be honest"

### Spec Change

Section 7.2 (Velocity Computation): "Implementations MUST compute velocity from raw
domain scores, not from confidence-weighted effective scores." Section 7.1 (Score History):
"Each snapshot MUST include raw score and confidence separately per domain."

---

## 4. One Dynamic Sensory Tool

### Problem

All three starter-kit sensory tools check for file existence (lint configs, test files,
CI config, README). For any established project, these checks produce a static score on
day one that never changes. This means:

- Trajectory intelligence never activates (no score variation)
- Correlations never fire (scores don't cross thresholds)
- Incident patterns never trigger (no domain degradation)
- The health dashboard is a green wall from the first run

The entire value proposition of the methodology — cross-domain correlation, incident
detection, trajectory intelligence — is invisible to new adopters because the default
sensory tools produce dead data.

### Proposed Fix

Ship a 4th sensory tool that reads **dynamic, real data**: test execution results.

`check-test-results.ps1` would:
1. Search for common test result artifacts (JUnit XML, pytest JSON, Pester NUnit XML,
   Jest JSON, coverage.xml)
2. Parse pass/fail/skip counts from the most recent result file
3. Compute score: `(pass / total) × 100`, with deductions for high skip rates
4. Write a CMDB with score, pass_count, fail_count, skip_count, result_file_path

This tool reads EXISTING test output that most projects already produce. It does not run
tests — it reads the last result. This means:

- The score changes every time tests are run (dynamic data!)
- A failing test immediately drops the score (correlation with deploy-readiness)
- The trajectory system sees real velocity (test health improving or degrading)
- The "quality cascade" incident pattern can actually fire

### Why This Specific Tool

Test results are the most universally available dynamic data in software projects. Every
project that has tests also has test output. The tool reads artifacts, not APIs — no
authentication, no network, no external dependencies. It works on CI runners and local
machines equally.

### Starter Kit Integration

- Add `test-results` as a 4th domain (weight: 0.25, rebalance others)
- Or: enhance `test-health` to prefer test results when available, fall back to file count
- Update the example correlation: `failing_tests_block_deploy` fires when test-results
  score < 60 AND deploy-readiness is being evaluated

### Impact

- Transforms the starter kit from "static dashboard" to "living health monitor"
- Activates trajectory intelligence with real data from the first week
- Makes correlations and incident patterns fire in practice, not just in theory
- Provides the missing "aha moment" that adoption requires

---

## 5. Attention Budget (Bounded Recommendations)

### Problem

The Brain can emit unlimited recommendations. In practice, a human can act on 3-5 items
per session. A developer seeing 15 recommendations treats them as noise. The system lacks
the biological concept of selective attention — the nervous system actively suppresses
most signals to focus resources.

The hat system controls emphasis (which signals are amplified) but not volume (how many
signals surface). This means the operator hat might surface 12 recommendations with
deploy-readiness items ranked first — but 12 items is still cognitive overload.

### Proposed Fix

Add an `attention_budget` configuration to the registry:

```json
"attention_budget": {
  "max_recommendations": 5,
  "per_domain_max": 3,
  "persona_overrides": {
    "executive": 3,
    "developer": 10,
    "product-manager": 5
  }
}
```

The recommendation engine produces ALL recommendations internally (for agent mode
consumers), but display modes (`-Mode recommend`, `-Mode brief`) truncate to the budget.
Hat emphasis determines WHICH items fill the budget, not how many there are.

### Biological Analogy

This is selective attention. The retina captures a wide visual field but the brain's
attention system focuses processing on a small region. The hat is the direction of gaze;
the attention budget is the aperture. Both are needed for effective cognition.

### Impact

- Recommendations become actionable, not overwhelming
- Forces the scoring/priority system to make real tradeoffs
- Personas get appropriate signal density (executive: 3, developer: 10)
- Agent mode consumers still get full data for automation

### Spec Change

Section 6.3 (Recommendations): "Display-mode consumers SHOULD limit recommendations to
the configured attention budget. Agent-mode consumers MAY access the full recommendation
set."

---

## Priority Ranking

| # | Improvement | Impact | Effort | Risk |
|---|-------------|--------|--------|------|
| 1 | Continuous confidence decay | High | Small | Low |
| 2 | Trajectory on raw scores + higher min_samples | High | Small | Low |
| 3 | Dynamic sensory tool (test results) | Very High | Medium | Low |
| 4 | Domain floor constraints | Medium | Small | Low |
| 5 | Attention budget | Medium | Medium | Low |

Items 1 and 2 are pure improvements to existing code with no architectural changes.
Item 3 is the highest-impact single change — it transforms the adoption experience.
Items 4 and 5 are new features that deepen the methodology.

---

## What This Does NOT Cover (Future Directions)

These were identified by the audits but are too large for this iteration:

- **Metabolic layer** (cost-per-point tracking) — requires new data collection
- **Python reference implementation** — weeks of work, high impact for adoption
- **Git hook integration** — makes Brain reactive without Claude Code
- **CI workflow template** — posts scores to PRs automatically
- **Gate dependency graph** — ordering relationships between gates
- **Degradation budgets** — time-bounded governance exceptions
- **Per-domain cadence** — trajectory windows measured in time, not samples
- **External event injection** — protocol for non-CMDB signals

Each is a valid Stage 6 candidate. The 5 improvements above are the highest
signal-to-effort ratio for strengthening the methodology NOW.

---

## Relationship to Existing Vision

These improvements advance three VISION.md principles directly:

- **Principle 2 (Scoring must be honest):** Continuous decay and raw-score trajectory
  eliminate phantom trends. Floor constraints prevent additive masking. The score
  becomes more honest.

- **Principle 12 (Trajectories reveal more than snapshots):** Raw-score tracking and
  higher min_samples make trajectory intelligence trustworthy. A dynamic sensory tool
  gives trajectory real data to analyze.

- **Principle 7 (The pattern is the product):** A dynamic sensory tool proves the
  pattern works for EVERY project — not just ones where files haven't changed.
  The methodology transfers because it demonstrates value, not just structure.
