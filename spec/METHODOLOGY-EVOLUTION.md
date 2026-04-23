# LSP Brains: Methodology Evolution Analysis

**Date:** 2026-04-11 (original) — **Updated:** 2026-04-23 (Access-pattern polymorphism — experimental observation)
**Context:** Stages 5-6 complete; Stage 7 shipped agent-behavior measurement; Stage 8 made it trustworthy; Stage 9 proved it can detect failure. Stage 10 delivers the governance-via-evidence path from trustworthy-advisory to trustworthy-load-bearing. 2026-04-22/23 produced the first rigorous brain-vs-control measurements (three-arm comparison: no Brain, static context, live tool), which surfaced a pattern this log absorbs as §14.
**Purpose:** Identify structural improvements to the underlying methodology.

---

## 14. Access-pattern polymorphism — an experimental observation (2026-04-23)

### Problem

Through Stages 1-13 the Brain has been discussed in the singular — as
a thing an agent either has or doesn't. Adoption guidance, operator
runbooks, and scoring all treat "Brain-equipped" as a binary attribute
of a session. The Phase 2 brain-vs-control experiment (static context
vs no context) produced mixed verdicts that could be interpreted as
"the Brain is sometimes helpful, sometimes not" — a framing that
leaves operators with a rough rule-of-thumb ("use it for repo-aware
work") and no deeper model.

The Phase 3 experiment added a third arm (live `brain_query` tool
access) and produced a sharper pattern:

- Every arm wins at a different task class. None dominates across all.
- L0 (no Brain) is best on trivial tasks. L1 (static) is best on
  repo-aware. L2 (live tool) ties L0 on trivial and loses to L1 on
  repo-aware despite perfect routing.
- Agent self-routing was validated: given a tool with per-domain
  cost warnings, Sonnet invoked the Brain 100% of the time on
  repo-aware tasks and 0% of the time on trivial tasks.

### The Insight

"Does the Brain help?" is the wrong question. The right question is
**which access pattern fits this task shape?** The Brain is not a
preset; it is a *plural substrate* — a collection of capabilities
(sensors, correlations, skills, culture) that different tasks sample
differently. Static injection, live tool access, and zero access are
not competing architectures — they are *patterns* of sampling from
the same substrate, each correct for some task shape.

What the experiments elevate to a first-class methodology concern is
not another sensor or another domain; it is the **dispatch function
between task and access pattern**. Self-routing behavior (the agent
deciding on its own which pattern to use) appears to already work for
the trivial vs repo-aware distinction. What doesn't yet work is the
*synthesis* step: when the agent does call for Brain data via a tool,
it applies the result less effectively than when the same data is
pre-loaded. This is a prompt-engineering frontier, not an
architectural one.

### What this section does NOT commit the spec to

This entry is **observational**. It does not:
- Rename any existing concept.
- Introduce new normative requirements.
- Mandate a new Brain domain, schema, or CMDB shape.
- Trigger a spec version bump.

It documents what the experiments appear to suggest as a hypothesis
about the methodology's shape. If future controlled evidence validates
the hypothesis (Tier 2b of the 2026-04-23 plan), the spec can absorb
access-pattern polymorphism as a normative concept in a subsequent
version bump with its own adversarial review. Until then, this is
discovery log.

### Rationale

Premature spec changes poison trust more than delayed ones. The
Tier 1→2a→2b→3 gating structure mirrors the Stage-10 governance
discipline: cheap reversible work first, experimental validation
next, normative change last with evidence attached. An operator
reading this log in 18 months should see the hypothesis, the gate
that would promote it, and the gate that would kill it.

### Implementation notes

- Experimental evidence: `.claude/experiments/brain-vs-control/`
  (reports phase1-3, synthesis, ledger at 432 rows).
- Tier 1 (this entry + operator-guidance updates + BACKLOG-14
  CANDIDATE): cheap documentation, ships immediately.
- Tier 2a (oracle-ceiling analysis on existing ledger): free,
  deterministic, tells us whether there is upside worth chasing.
- Tier 2b (realistic dispatcher measurement): only runs if 2a
  shows ≥5 pt headroom over best single arm.
- Tier 3 (spec/VISION/domain changes): only runs if 2b shows
  measured positive evidence. Gets its own plan file + review.

### Deferred

- Whether the dispatch function should be an explicit Brain domain
  (`dispatcher-quality`), a registry-level policy, a skill, or an
  agent-prompt pattern — all candidate shapes, not selected.
- Whether VISION.md gains a new principle ("The Brain is a
  substrate, not a preset"). Candidate; gated on Tier 2b.
- Whether the methodology names more access patterns than L0/L1/L2
  (e.g., cached-digest, selective-pre-inject, agent-edited-manifest).
  Out of scope for §14; raised in B-14.

### Relationship to existing vision

§14 does not alter VISION.md principles. It proposes that the
methodology's unit of analysis for Brain-equipped sessions shift
from "session has the Brain: yes/no" to "session deploys which
access pattern per task." The principles governing honesty,
observability, and governance are unchanged; what changes is where
those principles get applied — namely, to the dispatch decision
itself.

---

## 13. Domain Promotion Path — governance via evidence (2026-04-21)

### Problem

The `agent-behavior` domain entered the methodology at weight 0.0 by
design — LLM-as-judge scoring isn't trustworthy enough on day one to
attach gating consequences to. S8-ABV-EXT shipped the calibration
gate that would make LLM-as-judge trustworthy; S9-ABV-RED shipped the
detection evidence that would make it FAIL trustworthily. With both
pieces in hand, the outstanding question was operational, not
technical: **how does a domain move from "trustworthy advisory" to
"trustworthy and load-bearing" without a hand-wave?**

The question generalizes. Across the reference implementation's two
Brains (NeuroGrim, ecosystem) plus the methodology's stated pattern
for any adopter, several advisory domains sit at weight 0.0:
`git-health`, `rust-health`, `coherence`, `human-comms`,
`secret-refs`, `security-standards`, `agent-behavior`. Each has a
different path to trustworthiness — `agent-behavior` needs calibration
audits; `secret-refs` needs provider-manifest validation; `coherence`
needs cross-domain correlation health — but the POLICY question is
the same: what evidence is required, who declares it sufficient, and
how is the declaration recorded so it survives audit?

Without an answer, "promote when ready" becomes a hand-wave that
either never happens (domains stay advisory forever, value unrealized)
or happens too eagerly (a weight flip lands via a single commit
whose justification reviewers didn't have tools to verify). Both
outcomes poison trust in the scoring system.

### The Insight

Promotion is **governance**, not a code change. The code change —
mutating a `domain_weights` value in a registry JSON — is trivial.
The governance — establishing that the change is warranted — is
everything. The methodology's job is to make governance tractable:
define what evidence counts, require it to be attached to the code
change that uses it, preserve the decision's history, and make
reversal cheap.

Four primitives compose the governance layer:

1. **An audit protocol** that produces machine-readable evidence
   (calibration report, red-mode report). Not a vibe.
2. **An append-only promotion ledger** that records the decision
   with the evidence attached (paths, operator identity, the full
   rebalance deltas). Readable in 18 months.
3. **A CLI that REFUSES to act without evidence** — the audit
   reports aren't decorative, they're preconditions for the
   registry change. The machine enforces the policy.
4. **A reversal operation** that's cheap, fast, and preserves the
   audit trail. Reversibility is what lets the operator attempt a
   promotion conservatively — "if this looks wrong in a week,
   we'll roll back and investigate."

These four don't eliminate judgment calls — an operator still decides
whether to promote. They make the judgment call legible, verifiable,
and correctable.

### The Fix

New spec chapter §15.5 subsection "Promotion path" formalizes the
SHALL-level requirements:

- Every promotion SHALL require operator-declared audit evidence
  from at least two consecutive lower-cost calibration runs + one
  higher-fidelity validation, all passing calibration + red-mode.
- Every promotion SHALL be recorded in an append-only ledger with
  from/to weights, full rebalance deltas, audit paths, operator
  identity.
- Every promotion SHALL preserve `sum(domain_weights) == 1.0` via
  a declared rebalance strategy (proportional, explicit, or
  refuse-to-change).
- Every promotion SHALL provide a reversal operation that restores
  the pre-promotion registry state from the ledger's captured
  deltas. Reversals append; they don't delete.
- Implementations SHOULD pair promotion with post-change swing
  detection that surfaces proposals against the Brain's existing
  proposal ledger (§12) rather than acting autonomously.

A reference runbook ships at `NeuroGrim/docs/domain-promotion-audit.md`
documenting the two-profile ladder (Haiku routine + Sonnet validation
gate), pass/fail criteria, rollback procedure, post-promotion cadence,
and — critically — how to handle audit failure. The runbook's posture
on failure is: **stop and spawn remediation work; don't retry
until green.** "Green on the next run" isn't the goal; "green with
confidence, backed by evidence we'd still trust in six months" is.

A generalized `abv-run promote <domain>` CLI + promotion ledger +
rebalance helper + `abv-run rollback` + `abv-run promotion-watch`
executes the mechanism. The CLI enforces the policy: no
`--audit-report` argument → no promotion.

### Rationale

- **Separates infrastructure from action.** The mechanism is neutral;
  it doesn't compel promotion. Any operator can use it; the decision
  to flip a specific weight is a policy call the mechanism enables
  but doesn't make.
- **Evidence requirement makes the methodology self-extending.**
  When someone proposes to promote a domain that lacks a calibration
  harness, the machine's "no evidence, no promotion" refusal becomes
  the forcing function to build the harness. The gap surfaces
  immediately instead of being discovered later.
- **Audit failure as a first-class outcome.** The spec explicitly
  names the failure case and says: stop, don't retry, spawn
  remediation. That's a methodology stance, not just a tool
  behavior — it commits us to treating a "not yet" as a complete
  answer, not as a temporary state to paper over.
- **Reversibility is cheap by construction.** The ledger's
  append-only history + the registry backup stamped with the
  promotion timestamp means rollback is a single CLI call that
  restores a known state. Operators make the promotion call
  knowing the cost of being wrong is bounded.
- **Generalizes across domains.** The mechanism applies to any
  advisory-weighted domain; the only per-domain variance is what
  "audit evidence" means (calibration reports for
  `agent-behavior`, provider-manifest checks for `secret-refs`,
  cross-correlation reports for `coherence`, etc.). The
  METHODOLOGY-EVOLUTION entry cements this as a pattern, not a
  special case.

### Implementation notes

Reference implementation ships across the existing three-repo
layout. LSP-Brains gets the schema + spec. Ecosystem gets the
CLI + ledger + rebalance helper + swing detector. NeuroGrim gets
the reference runbook. None of the existing weighted domains
(`test-health`, `code-quality`, `deploy-readiness` in NeuroGrim)
are touched; their weights stay unchanged and their scoring path
is unaffected. Stage 10 is ADDITIVE — not promoting remains
conformant.

The first concrete case — promoting `agent-behavior` in
NeuroGrim from 0.0 to 0.05 via proportional rebalance — is
documented in `S10-domain-promotion.md` as S10-DP-4. That story
is guarded-pending on operator execution of the runbook's audit
protocol. The epic closes on successful delivery of the
mechanism; the flip itself is a separate, evidence-backed
operator action.

### Deferred

- **Commit-signed operator authentication.** Current posture uses
  `ABV_OPERATOR` env var (matches `judge-integrity-ledger`
  posture). Hardening to signed commits for consequential ledger
  writes is a future epic.
- **Automated cadence enforcement.** Post-promotion calibration
  cadence is operator-enforced via the runbook. A scheduled
  agent trigger that runs the cadence automatically (and alerts
  when skipped) is a future epic.
- **Multi-step gradient promotion.** Current posture is single-
  step (0.0 → 0.05). Promoting through intermediate values
  (0.025 → 0.05 → 0.075) across multiple audit cycles is
  operationally supported — operator runs multiple
  `abv-run promote` calls with incrementally larger `--to`
  values — but there's no automation to orchestrate the sequence.
- **Ecosystem Brain weighting philosophy.** Every ecosystem
  domain currently sits at 0.0. Promoting any of them requires
  a meta-decision about what the ecosystem Brain's weighted
  score represents (trajectory health? cross-child alignment?
  something else?). Deliberately out of Stage 10 scope.

---

## 12. Red Samples & Judge Integrity (2026-04-21)

### Problem

§15 and the S8-ABV-EXT extensions shipped an increasingly trustworthy measurement chain: rubric-driven LLM-as-judge scoring, gold-sample calibration, multi-judge consensus, and execution-based evidence. Yet the suite has a blind spot nobody noticed until it was named: **the harness can only demonstrate that agents scored green. It cannot demonstrate that judges would score red when an agent actually fails.**

Gold samples test agreement with a human label within ±10 — a two-sided check. If the human labeled a gold-bad at 25 and the judge returned 35, that's a pass. But "35 on a gold-bad" is consistent with *every* red response scoring 35 — the judge might be uniformly generous and never produce a truly blocking output. Every green CMDB the harness has ever emitted is consistent with a judge that only says green. Without a control scenario that intentionally forces red and is verified to produce one, we cannot distinguish "agents did well" from "the test is fail-proof."

This matters before any decision to promote `agent-behavior` past advisory weight (tracked as BACKLOG item B-01 in the reference implementation). Weighted gating on evidence that can only ever be green would be negative-value observability.

### The Insight

Gold samples prove the judge can *agree* with a human on a specific response. **Red samples** — a new class of calibration fixture — prove the judge can *detect* specific failure modes. A red sample is a pre-recorded response paired with an `expected_score_ceiling` the judge MUST stay under. Unlike gold samples, red samples are a one-sided bound: score ≤ ceiling = pass, score > ceiling = red-miss. And unlike gold samples, which stay frozen (they're the baseline skills are refined against), red samples **grow over time** — new modes are added as real misses surface in feedback. Coverage expands; the gold-baseline stays stable.

The pattern is classical test-engineering wisdom applied to non-deterministic verification: mutation testing / fault injection / canary cases. Assertions that never fire tell you nothing. The discipline transfers to LLM-as-judge systems directly, and nobody's spelled it out in the LLM-as-judge literature we've seen.

### The Fix

§15.3 gains a "Red samples" subsection normatively requiring:

- **Schema extension.** `agent-behavior-scenario-v1.schema.json` gains an additive `red_samples[]` array. Each sample declares `id` + `failure_mode` + `expected_score_ceiling` + `response` (+ optional `notes` and `retired_in_version`). No breaking change to the existing gold-sample path.
- **Calibration-time coverage.** Implementations SHOULD grade red samples in the same pass as gold samples. The `calibration-report-v1.schema.json` gains `red-miss` and `red-skipped` at the `overall_status` enum.
- **Blocking precedence.** A red-miss SHALL refuse the trustworthy CMDB path (same blocking severity as gold `drift-blocker`) but emit a distinct `judge-integrity:red-miss` finding so operators can triage: judge failure, rubric gap, or sample mis-label.
- **Iteration escape.** A `--skip-red-calibration` flag permits operators authoring new red samples to iterate without blocking the harness; the resulting CMDB is flagged `red-skipped` (less trust than `pass` but not blocking).
- **Ledger discipline.** Red-misses accrue in an append-only judge-integrity ledger as `pending` entries; humans append `triaged` records with one of three decision branches (`confirmed-judge-miss`, `scenario-rubric-gap`, `mislabeled-red-sample`). No triage → no evidence.

### Rationale

- **Preserves the §15.5 bright line.** The established rule ("humans edit, agents don't self-refine; judge prompt is not a tuning surface") extends to red samples verbatim. When a red-miss is triaged as a confirmed judge failure, the refinement lever is *library expansion* (more red samples covering that surface) — NOT judge-prompt editing. This prevents the feedback loop from collapsing into self-training pressure on the judge.
- **Makes the gating decision tractable.** B-01 (promote past advisory) becomes "red-sample coverage at or above X failure modes AND zero unexplained red-misses over Y calibration cycles." That's a measurable precondition, not a vibe check.
- **Cheap by construction.** Architecture A (pre-recorded red samples) reuses every piece of existing calibration infrastructure. The stretch (Architecture B — live mock-bad-agent generating novel red responses per run) is deferred to BACKLOG item B-06, to be scoped after Architecture A has been in operation for ≥ 2 calibration cycles and real coverage gaps have surfaced.
- **Honest about the limit.** Red samples only prove the judge detects the failure modes the library covers. The methodology NAMES this limit and offers two disciplines for stewarding it: (a) diversify at authoring time via a shared failure-mode taxonomy; (b) grow the library whenever real-world misses surface. A `red-coverage-staleness` signal (no new samples for N months while feedback keeps flowing) becomes a methodology smell.

### Implementation notes

Reference implementation lives alongside the S7-ABV/S8-ABV-EXT harness at `D:/Brains/agent-behavior-runner/`. S9-ABV-RED-1 delivers the schema + harness path; S9-ABV-RED-2 ships an initial six-mode failure-mode taxonomy (`false-specifics`, `bureaucratic-polish`, `confident-cat-grep`, `rubric-mimicry`, `culture-veneer`, `false-humility`) plus one canary red per scenario (ceiling ≤ 5); S9-ABV-RED-3 wires the judge-integrity ledger + `refine-judge-integrity.md` skill. All three stories are additive — v2.3 agent-behavior implementations remain conformant without red samples.

### Deferred

- **Mock-bad-agent red mode (Architecture B).** Live generation of novel red responses by a second adversary LLM. Deferred to BACKLOG B-06 after the pre-recorded-library approach has been calibrated in operation. The trade-off is richer coverage vs. non-determinism and a new trust surface ("how bad is the mock, really?") that needs its own calibration discipline.
- **Automatic rubric tightening from ledger data.** Humans read the judge-integrity ledger and decide what to do. No pattern-match → auto-edit pipeline.
- **Automatic red-sample generation from feedback.** Humans author samples after triage. Same discipline as gold samples.
- **Per-project red-sample overrides.** One ecosystem-wide library in v1. Per-project overrides overlap with BACKLOG B-03.

---

## 11. Agent Behavior Verification (2026-04-21)

### Problem

Sections 1–14 of the spec describe how a Brain measures the state of a **project**. Nothing in the spec measures the state of the **agents operating on that project**. Skills describe how an agent should behave; hats describe how it should attend; culture describes what it should never violate — but all three are declarations without verification. §14.8 acknowledged this gap for culture specifically ("declaration without measurement is a weakness; the manifest can become aspirational if outputs drift"). The problem is not culture-specific: every skill, every hat, every cross-cutting expectation about agent behavior has the same risk.

Autonomy resolution (§5.5) uses proposal-effectiveness from outcomes — "85% of proposals worked → auto." That's a lag signal after actions took effect. It says nothing about whether the reasoning was sound, whether LSP tools were used when they should have been, whether cultural invariants held under a tempting prompt, whether the right hat was worn. A proposal that worked by accident scores the same as a proposal that was soundly reasoned; a rubric-violating agent whose recommendation happened to land scores full marks.

There is no operational answer to "is this agent fit for this project's verification gating?" Which matters, because the VISION principles explicitly position culture, hats, and skills as load-bearing. If an agent is silently drifting away from them, the Brain is measuring the wrong thing — the project looks healthy while the measurement surface is degrading.

### The Insight

Agents have behavior. That behavior is measurable. **Non-deterministic verification of non-deterministic behavior** is messier than deterministic tests, but the mess is load-bearing: it forces us to treat scores distributionally, to calibrate the judge against human-labeled gold samples, and to treat single-trial numbers as uninterpretable. Those constraints are features, not bugs — they keep anyone from mistaking a noisy number for a clean one.

The mechanism is: a **scenario** (user-impersonation prompt + rubric + trial count) → multiple **trials** (agent responses) → a **judge** (a second LLM scoring each response against the rubric) → a **feedback elicitation** (the agent-under-test is told its score and invited to suggest how the skill / test could have been clearer) → a **ledger** of feedback the human reviewer uses to refine skills. The agent cannot edit the skills it is graded against; that bright line prevents drift into self-training.

This is VISION principle #19 ("agents are sensed") made operational. It sits beside #18 ("sensors need sensors") as the second half of a single observability story: the observer needs an observer, AND the agents running the observers must themselves be scorable.

### The Fix

New spec chapter §15 "Agent Behavior Verification" formalizes the contract:

- **§15.2 Scenario + Rubric** specifies the authoring shape. `agent-behavior-scenario-v1.schema.json` is the normative schema. A scenario declares an id + version + target + prompt + rubric + trial count + gold samples.
- **§15.3 Judge Protocol** specifies the judge's inputs, outputs, and — importantly — calibration. Before trial results are admitted to the CMDB, the judge MUST score that scenario's gold samples and SHALL refuse to emit results if drift exceeds the configured threshold. This is the operational guard against silent judge degradation.
- **§15.4 Distributional Interpretation** is deliberate: a scenario's single-trial score is never authoritative. Mean score + stddev + majority-pass constitute the result; implementations MUST surface all three.
- **§15.5 Feedback Loop** specifies the human-in-the-loop refinement workflow. Critically: agent-under-test feedback is text only. Humans read the ledger, group by target, and refine skills by hand. Delta tracking verifies refinements moved scores in the right direction. Gold samples are FROZEN — they are the baseline against which skills are refined, not the other way around.
- **§15.6 Interaction** spells out how `agent-behavior` composes with §5 governance (participates in gates but only after calibration audit; MAY tighten autonomy as an invariant but MUST NOT loosen it), §12 learning (proposals emitted for regressions), and §14 culture (the five values are direct rubric targets).
- **§15.7 Privacy + Cost** requires the harness to allowlist audit-log fields (no prompt content on disk), track token budgets, and enforce cost ceilings. Matches the hygiene already established in the reference implementation's claude-proxy and webhook-sync services.

### Rationale

- **Generalizes §14.8's drift-sensor promise** — we promised a culture drift check; we deliver a scenario-driven verification mechanism where `culture-invariants` is one of five first-party scenarios (`lsp-code-optimality`, `lsp-brain-usage`, `hat-discipline`, `culture-invariants`, `honest-scoring`).
- **Separates process quality from outcome quality.** §12 Learning Protocol measures outcomes (did the proposal work?). §15 measures process (did the agent reason soundly, use the right tools, honor the culture?). Both are real; both are necessary; they compose.
- **Advisory by default.** A new domain type where scores come from LLM-as-judge is not trustworthy enough on day one to carry a gating weight. v1 implementations SHOULD keep the weight at 0.0 until a documented judge-calibration audit passes. Conservative ≠ slow — it's what makes the eventual gating trustworthy.
- **Human-in-the-loop refinement preserves accountability.** The safety rail (agent cannot edit skills) is deliberate. Combined with frozen gold samples, it forces refinements to either improve the score or fail honestly — there is no escape hatch where the agent trains itself into an easier rubric.
- **Dog-food value.** The reference implementation ships five scenarios targeting skills the ecosystem already ships. The first run will find real issues in real skills. Every issue surfaced is a skill improvement that compounds across every future project adopting the ecosystem.

### Implementation notes

Reference implementation lives at `D:/Brains/agent-behavior-runner/` — a Python CLI (`abv-run`) that reuses claude-proxy tokens + audit discipline. The CMDB shape extends `cmdb-envelope-v1.schema.json` via `additionalProperties`; no breaking change to the envelope schema. The feedback ledger follows the existing append-only JSONL pattern (`incident-ledger`, `proposal-ledger`, `score-history`). Integration with NeuroGrim happens through a new CLI subcommand (`neurogrim cast agent-behavior`) that shells out to `abv-run` and pipes the result CMDB into the standard domain-scoring path. No Rust scoring-engine changes required.

### Deferred

- **Multi-judge consensus.** v1 ships single-judge scoring. §15.3 names multi-judge as the stretch for scenarios where historical rubric variance is high.
- **Cross-model judges.** Same model family for agent and judge in v1. Using a different model family for the judge (e.g., Claude agent + GPT judge) reduces blind-spot overlap at cost.
- **Execution-based rubrics.** v1 grades stated intent (did the agent plan to use Grep?). Execution-based grading (did the agent *actually* call Grep in the resulting work?) is phase-2.
- **Per-project rubric overrides.** "Good agent" varies by project; v1 ships one ecosystem-wide rubric set.
- **CI integration.** v1 cadence is on-demand + documented weekly. Continuous runs on every PR are gated on cost-budget tooling maturity.
- **Gating.** Advisory-only in v1 with the path to weighted-gating left open. Promoting past advisory requires passing the judge-calibration audit defined in §15.3.

---

## 10. A2A Bearer Authentication (2026-04-20)

### Problem

v2.1 of the spec fixes `authentication.scheme` to `"none"` and says:
"Adopters requiring auth MUST gate access at the network layer."
This is adequate for single-host dev topologies (containers on a
loopback-only Docker network, trusted team machines), but it
forecloses remote-agent patterns that the methodology otherwise
supports at the protocol level.

The "CEO scenario" — an operator whose only local artifact is a
`brain-registry.json` pointing at hosted agents, with credentials
for access — requires per-client credentials. Network-layer auth
(firewall, VPN) is too coarse: it gates *anyone with network
access*, not *this specific client*. The protocol needs a
fine-grained credential the hosted agents can issue, validate,
audit, and revoke without operator cooperation from the clients.

### Addition

`authentication.scheme` enum extended to `["none", "bearer"]`
(additive; existing `none` consumers are unaffected). When `scheme:
bearer` is advertised:

- The client MUST send `Authorization: Bearer <token>` on every
  task request. Agent Card discovery remains unauthenticated —
  peers must be able to learn of each other's existence before
  they can authenticate.
- Token issuance and validation are implementation-defined. The
  reference implementation (NeuroGrim) uses hashed storage in a
  local SQLite database with constant-time hash comparison,
  per-token rate-limit profiles, revocation, and optional
  expiration. Tokens are never stored in plaintext on disk.
- Response shapes for auth failure: `401` with a machine-readable
  `detail` (missing / invalid / revoked / expired). Implementations
  MUST audit-log the rejection without recording the presented token.

### Rationale

- **Enables remote-agent topologies without weakening the default.**
  Trusted-network deployments stay on `none`; multi-tenant /
  hosted deployments opt into `bearer`. The choice is per-peer.
- **Additive, not breaking.** An old client that doesn't send an
  `Authorization` header can still talk to a `scheme: none` peer,
  and old peers that ignore `Authorization` still work against a
  bearer-sending client.
- **Bearer is the minimum useful auth primitive.** mTLS is stronger
  but requires certificate infrastructure most adopters don't have.
  OAuth requires an auth provider. Bearer is the lingua franca that
  fits between "no auth" and "enterprise PKI."
- **Enables the kill switch.** With per-token credentials, an
  operator can revoke one client's access without touching any other
  client's. This is the minimum capability required for responsible
  multi-client hosting.

### Implementation notes

- Reference impl ships a `token_store` module with issue / validate
  / revoke / list / expire semantics; token CLI follows the
  `proxy-cli` pattern (issue prints the raw token exactly once,
  store records only the hash).
- Rate-limit profile is associated with each token at issuance;
  the validator returns the profile so the caller can enforce
  quotas.
- Audit log records the token's label + token_id prefix (first 8
  hex chars of hash), never the raw token.
- The `/.well-known/agent-card.json` endpoint stays unauthenticated
  by design; it is the contract surface peers use to discover each
  other's auth requirements.

Deferred: mTLS, OAuth, per-model / per-endpoint scope restrictions.
All additive; none block this change.

---

## 9. A2A-Pull Fractal Composition (2026-04-17)

### Problem

Spec §9 "Fractal Composition" describes the pattern: a parent Brain
aggregates child Brain scores, treating each child's unified score as
one input to the parent's own score. Spec §13 adds A2A as the
RECOMMENDED transport for this, replacing the legacy subprocess-
invocation fallback. The Rust workspace shipped both layers in Stage 6:

- `neurogrim-a2a` crate — A2A server + client (envelopes, task
  lifecycle, agent cards)
- `neurogrim-ecosystem` crate — `ChildEntry` / `ChildTransport::A2A` +
  `invoke_child` + `score_ecosystem` for aggregation

What was missing: **the wiring from the regular scoring pipeline to
these layers**. A brain-registry could declare
`scoring_source: {type: "cmdb", path: "…"}` and the pipeline would load
that domain's CMDB from disk. It had no way to declare `type: "a2a"` —
the schema didn't allow it, and `load_cmdb_data` silently skipped
anything that wasn't `"cmdb"`. The fractal pattern existed in code but
couldn't be reached from configuration alone.

Result: the ecosystem Brain at `D:\Brains\.claude\` declared two
children (NeuroGrim + LSP-Brains) but never consumed their scores.
Its unified score reflected only its own 6 domains from local CMDBs.
The three-Brain topology was load-bearing in diagrams and
documentation but had never actually composed.

### The Insight

Declaration is not composition. Three separate layers shipped without
the one-line contract that connects them: a `scoring_source.type`
variant that tells the pipeline "fetch this domain's score from that
peer Brain." A declaration in the schema isn't the same as a wire
running between modules. The fractal pattern requires all three layers
to agree:

1. **Schema** — `brain-registry-v2` permits `type: "a2a"` + `endpoint`
2. **Rust types** — `ScoringSource` carries the `endpoint` string
3. **Pipeline dispatch** — `load_cmdb_data` routes `type: "a2a"` to
   `invoke_child` with a synthesized `ChildTransport::A2A`

Session 3 landed all three. The test at
`neurogrim-cli/tests/three_way_brain.rs` spawns two real subprocess
peers, builds an ecosystem registry pointing at them via A2A endpoints,
and runs `neurogrim score` — the full pipeline path a user would
take. The score aggregates across all three sources (2 A2A peers + 1
local CMDB) and exits 0. Fractal composition is finally composed.

### The Fix

Three lock-step additions, all additive:

- `brain-registry-v2.schema.json` — `scoring_source.type` enum gains
  `"a2a"`; new `endpoint` + `interface_version` properties.
- `neurogrim-core/src/registry.rs` — `ScoringSource` gains
  `endpoint: Option<String>` + `interface_version: Option<String>`.
- `neurogrim-cli/src/commands/context.rs::load_cmdb_data` — dispatch
  on `source_type`; A2A branch builds a `ChildEntry` and calls
  `neurogrim_ecosystem::invoke_child`; resulting AgentOutput.score
  becomes the domain's raw score.

Failure semantics: unreachable peer / bad URL / version mismatch →
tracing warning, domain falls back to `no_file_score` (default 0).
Consistent with the existing CMDB-miss path.

### Deployment Note

For the real ecosystem registry at `D:/Brains/.claude/`, the A2A-pull
opt-in is NOT flipped by default. Flipping it requires children to be
running as A2A servers when the parent scores — a deployment choice
the user makes when they have a running topology. The code path is
proven by the integration test; the registry flip is a separate
operational decision.

### Carried Forward

- Parallel A2A fetch (currently sequential in `load_cmdb_data`) is a
  natural follow-on once an ecosystem has ≥3 A2A-sourced domains and
  latency becomes material.
- Proactive emission (child pushes `score.updated` to parent on
  change, vs parent pulling) remains explicitly deferred (Stage 6+ per
  dual_brain_pair's out-of-scope note). This pass shipped the pull
  direction; push is a separate piece.

---

## 8. Sensor Testing Discipline (2026-04-17)

### Problem

Round 2 of ecosystem sensors — `protocol-boundary`, `terminology-coherence`,
`spec-impl-alignment` — shipped and scored 100 on all three. Post-hoc manual validation
against `cmdb-envelope-v1.schema.json` surfaced drift: the Python SDK had been emitting
findings as `list[str]` since inception, while both the canonical schema and the Rust
`Finding` struct required objects with `{name, status, points, detail}`. The drift had
been latent since the first Python sensor. Zero automated signal caught it.

The Brain noticed nothing. The Rust side was correct. The schema was correct. The Python
SDK quietly produced output that a strict `jsonschema.validate()` would have rejected —
but no code path called `validate()`, so the drift was invisible.

This is not a one-off. It is a structural blind spot: the observing layer was not itself
observed. A sensor's output shape is load-bearing — the Brain reads it, correlates on
it, decays confidence against it, and feeds it upward into parent Brains. A malformed
sensor produces malformed scoring, and none of the downstream integrity checks
(confidence decay in §4.4, correlation engine in §8, fractal aggregation in §9) can tell
malformed data from legitimate data. They operate on whatever shape the sensor handed
them.

### The Insight

Sensors are hypotheses about project state. A test that validates the sensor's own
output is the cheapest possible evidence that the hypothesis has a well-formed answer.
Without that test, a drift in the observer looks identical to a drift in the observed —
both manifest as the score changing. Knowing which kind of drift is happening is load-
bearing: one requires a code fix, the other requires an investigation.

The testing layer is also fractal. Each sensor gets a unit-level test that asserts its
output against the schema. The ecosystem gets an integration test that runs every sensor
against live project state and asserts the current expected score. The unit tests catch
shape drift; the integration tests catch behavioral drift. Both feedback loops cost very
little relative to the cost of a Brain reasoning from garbage.

### The Fix

§3.8 "Testing Discipline" — a SHOULD-level requirement that every sensory tool ships
with a test validating:

1. Output conforms to `cmdb-envelope-v1.schema.json`.
2. Declared `exported_variables` keys are present.
3. Score is within the tool's documented scoring-model range.

§9 ecosystem sensors MAY additionally have an ecosystem-level integration test exercising
the sensor against live state — a regression guard for score drops.

Additive by design. No pre-v2.2 sensor is retroactively non-conformant — the
methodology nonetheless strongly encourages adoption. Elevating to MUST would violate
the additive-bumps discipline and the spec never breaks v2.x conformance claims.

Principle #18 "Sensors need sensors" encodes this as a first-class invariant. The
methodology now explicitly recognizes that the observing layer needs its own observers,
and that the cheapest place to catch a broken sensor is in a test that runs on every
commit.

### Discovery Context

Drift surfaced during a post-ship validation pass while manually running
`jsonschema.validate()` on the four live ecosystem CMDBs (spec §9 ecosystem
`D:\Brains\.claude\`). All four failed with `'Status: identical' is not of type 'object'`
— the SDK emitted the literal string `"Status: identical"` where the schema expected an
object. Had an integration test existed, it would have caught this on the first sensor
(`culture-coherence`, shipped weeks before) rather than on round 2.

The fix landed alongside this METH-EV entry: Python SDK mapped to object findings, all
four sensors regenerated their CMDBs (same scores, richer shape), and the ecosystem
gained a `tests/` tree that runs `pytest` across every sensor on every change.

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
  NeuroGrim, LSP-Brains) carries its own `culture.yaml`. No inheritance by reference.
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

Tracked in the NeuroGrim roadmap as:
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

NeuroGrim has two distinct protocol shapes inside it:
- **Tool-call shape** — sensory tools → Brain, Brain → LLM agent. MCP is the right fit. Keep.
- **Peer-agent shape** — parent Brain ↔ child Brain (Stage 4), local Brain ↔ external Brain
  (Stage 6). MCP is the wrong fit. Adopt A2A.

The Stage 4 fractal composition already shipped with subprocess invocation for child Brains,
not MCP. The Stage 6 dual brain is design-only. Neither path is encumbered by deep MCP
integration — the migration surface is smaller than it looks.

### The Decision

**MCP stays** as the normative protocol for sensory tool invocation (spec §3.7 + Appendix F)
and for Brain-as-tool exposure to LLM agents (Claude Code, Cursor, etc.). The `neurogrim-mcp`
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
- Appendix D: add rows for `neurogrim-a2a` crate.

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

Tracked in NeuroGrim roadmap as:
- S5-TP-8 (spec + schemas publication)
- S6-DB-1 through S6-DB-6 (neurogrim-a2a crate, ecosystem refactor, A2A server,
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
