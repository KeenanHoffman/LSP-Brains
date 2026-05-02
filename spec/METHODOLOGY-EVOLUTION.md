# LSP Brains: Methodology Evolution Analysis

**Date:** 2026-04-11 (original) — **Updated:** 2026-04-27 (Multi-round pre-release assessment — patterns observed in a single campaign)
**Context:** Stages 5-6 complete; Stage 7 shipped agent-behavior measurement; Stage 8 made it trustworthy; Stage 9 proved it can detect failure. Stage 10 delivers the governance-via-evidence path from trustworthy-advisory to trustworthy-load-bearing. 2026-04-22/23 produced the first rigorous brain-vs-control measurements (three-arm comparison: no Brain, static context, live tool), which surfaced a pattern this log absorbs as §14. 2026-04-23/24/25 saw a PyPI supply-chain incident force the methodology to grow a normative supply-chain awareness layer (§15) — the first time the reference implementation shipped a normative protocol-shape feature ahead of the spec. 2026-04-26 closed the supply-chain pre-release campaign with a three-round retrospective whose strict-bar → surgical-bar → diminishing-returns shape this log absorbs as §16 — observational, scoped to pre-release, and explicitly bounded by single-campaign evidence.
**Purpose:** Identify structural improvements to the underlying methodology.

---

## 16. Multi-round pre-release assessment — patterns observed in a single campaign (2026-04-27)

### Problem

Through v2.8 the methodology had a robust answer for adversarial review at *plan time* — the
`plan-critic` skill (single-pass, structured, hat-driven) — but no documented cadence for
the assessment work that happens **after** an epic closes and **before** a public release.
The 2026-04-23/24/25/26 supply-chain pre-release campaign organically converged on a
three-round shape (strict bar → surgical bar → tighter surgical + escape hatch) that
nobody designed in advance. Each round had to be invented; the convergence pattern was
visible only in retrospect.

The gap was real even though it surfaced quietly: pre-release verification rounds are
high-stakes (the next thing to happen after them is `cargo publish`), they are
expensive (a substantial campaign consumes 2–3 person-days of focused work), and
their outcomes are not symmetric (a missed defect ships to crates.io / PyPI; a
spurious finding burns operator time). A methodology that names *plan-time* adversarial
review explicitly and leaves *pre-release* assessment to be reinvented every campaign
is silent on the harder, more consequential half.

This section absorbs what the supply-chain campaign retrospective surfaced as the
shape of pre-release work — strict-then-surgical-then-escape-hatch — without committing
the spec to that shape as universal. It is **observational**, in the deliberate sense
of §14: it documents a pattern, identifies the gates that would promote it to
normative status in a future spec version, and identifies the gates that would kill
it. The evidence base is N=1 (one campaign); the methodology stance is
proportional to that evidence.

### The Insight

Three insights surfaced in the campaign retrospective. They are listed in the order
the campaign produced them, not in order of importance — the third is the most
load-bearing structurally.

**1. Strict-bar Round 1 surfaces nearly all real defects.** Round 1 of the
supply-chain campaign produced 70 catalog findings, of which 23 majors were
fix-now. Round 2 produced 28 findings (5 majors fix-now); Round 3 produced 7
findings (4 picks fix-now). The first round catches the bulk of real defects;
later rounds tighten an already-mostly-clean surface. This pattern matches
intuition about adversarial review economics — broad-net-cheap first pass,
expensive narrow refinement after — but the campaign produced concrete numbers
that future campaigns can compare against.

**2. Surgical bar prevents Round 2+ from becoming Round 1 again.** Without a
tighter bar in Round 2, the campaign would have re-litigated Round 1's deferred
minors through the same lens — a treadmill that produces motion without
progress. The campaign's Round 2 explicitly adopted a "top 5–7 highest-leverage"
bar (and Round 3 tightened it further to 3–5 picks). This forces leverage
discipline, not exhaustion discipline: the question stops being "is there a
finding here" and becomes "is this finding worth fixing relative to the
remaining BACKLOG."

**3. Phase 1.5 escape hatch closes the series honestly.** The campaign's most
structurally important convention is the "Phase 1.5" evaluation that runs
between catalog and pick: when the catalog surfaces fewer than the round's
surgical-bar minimum of high-leverage findings, the operator SHOULD close the
assessment series rather than dropping the bar to find work to do. The
campaign's Round 3 nearly fired the escape hatch (catalog produced 1
strict-letter high-leverage finding; the operator chose Path C — Surgical-4 —
over the strict-close path on affirmative leverage grounds). The pattern is
that the escape hatch exists to be used; not invoking it requires affirmative
justification, recorded in the round's artifact. Without this convention,
multi-round assessment becomes ritual: a fourth round runs because there is a
fourth round on the calendar, not because there is a fourth round of work to
do.

### The Fix

§16 codifies the cadence as RECOMMENDED (not MUST) for **pre-release / epic-close-out
contexts only**. Routine plan review remains single-pass via `plan-critic`; that
boundary is load-bearing (see §16's "What this section does NOT commit the spec to"
subsection below). The cadence has four named phases:

- **Round 1 — Strict bar.** All blockers + majors fix-now; minors deferred to
  BACKLOG unless trivially close to a fix-now item. Cadence: ~2 days for a
  substantial campaign. Yield expectation: a substantial fraction of catalog
  becomes fix-now.
- **Round 2 — Surgical bar (top 5–7).** Re-evaluate Round 1's deferred minors
  through a focused dimension lens (DRY, waste, gaps, inefficiency, etc.).
  Cadence: ~½–1 day. Yield expectation: a smaller number of high-leverage picks
  with deferral becoming the default disposition.
- **Round 3 — Tighter surgical (3–5 picks) + Phase 1.5 escape hatch.** If the
  catalog produces fewer than 3 high-leverage candidates, the operator SHOULD
  close the series. If the catalog produces 3 or more, the operator picks the
  surgical set. Cadence: ~3 hours. Yield expectation: very small absolute
  count; high relative leverage on what is fixed.
- **Round 4+ — Default to closure.** A fourth round faces severe diminishing
  returns; the escape hatch RECOMMENDED-fires decisively at this point. The
  remaining BACKLOG items are picked off opportunistically as code in those
  areas is touched, NOT as the deliverable of a dedicated round.

Each round SHOULD include a phase-specific verification gate (e.g., `cargo test
--workspace --all-targets` green; the project's prepublish-check green) before
the round is declared complete. Each round SHOULD produce a written artifact
(catalog + pick + Phase 1.5 evaluation + retrospective) so the next campaign
can compare against the previous one's shape.

The retrospective produced by the supply-chain campaign — quoted verbatim below
from `audit/PRE-RELEASE-ASSESSMENT-2026-04-26.md` lines 671–697 — is the
canonical worked example. The diminishing-returns table MUST be quoted with
the R3 caveat paragraph attached; the table read in isolation tells a
misleading "yields are climbing" story that is the opposite of the methodology's
actual claim. (This is a methodology-hygiene rule, not a cadence claim — see
§16's RFC 2119 discipline note in the Implementation notes subsection.)

> **Diminishing-returns retrospective**
>
> | Round | Findings | Fixed | Yield rate | Time |
> |---|---|---|---|---|
> | Round 1 | 70 | 23 majors | 33% | ~2 days |
> | Round 2 | 28 | 5 majors + 1 doc | 21% | ~¾ day |
> | Round 3 | 7 | 4 picks | 57% | ~3 hr |
>
> **The Round 3 yield rate (57%) is artificially high because the Phase 1.5
> escape hatch + tighter surgical bar combined with the agent's conservative
> labeling pre-filtered the candidate pool.** What this actually says: the
> agent correctly identified ~7 things worth fixing; we picked 4 of them
> (deferring 3 low-leverage); the discipline worked.
>
> **Recommendation for any future Round 4:** the assessment series has now
> produced 32 fix-now items across 3 rounds. A fourth round would face severe
> diminishing returns; the Phase 1.5 escape hatch would likely fire decisively.
> The plan-critic position: **close the assessment series here** unless a
> specific concrete concern emerges (e.g., a new incident, a calibration
> regression, a sensor that develops a real performance pain). The remaining
> BACKLOG B-22 items (now ~22 from R1 + R2 + R3 deferrals) should be picked
> off opportunistically as code in those areas is touched, not as the
> deliverable of a dedicated assessment round.
> — `audit/PRE-RELEASE-ASSESSMENT-2026-04-26.md` lines 671–697 (verbatim)

The R3 caveat is part of the methodology, not a footnote: a pre-release campaign
that produces yield rates climbing toward Round N would be evidence the cadence
is *not* converging — the opposite reading of the table-without-caveat.

### What this section does NOT commit the spec to

This subsection mirrors §14's epistemic posture explicitly. §16 is observational
and bounded; it imposes no normative requirements on conforming Brains. Three
explicit non-commitments:

**1. Not normative MUST anywhere in cadence claims.** The cadence is RECOMMENDED.
Round counts (3) are observed-not-prescribed — a campaign converging in 2 or 4
rounds is not a §16 violation. Yield rates (33% / 21% / 57%) are descriptive,
not predictive; no future campaign is expected to reproduce these numbers, and
no scoring system computes against them. The Phase 1.5 escape hatch is
RECOMMENDED rather than MUST — when a round catalog surfaces fewer than the
round's surgical-bar minimum of high-leverage findings, the operator SHOULD
close the series rather than drop the bar; an operator who continues anyway
records affirmative justification but does not violate any spec invariant.

**2. Not a substitute for `plan-critic`.** The `plan-critic` skill remains the
single-pass adversarial review for plans. §16 is a **separate**, post-execution
cadence for pre-release verification rounds. The two are complementary, not
overlapping: plan-critic operates on a plan file before implementation; §16
operates on a closed epic before publish. A plan reviewer running §16's
multi-round shape on a routine plan would be applying pre-release methodology
to plan-time work, which is the BR-7 trap §16 is explicitly avoiding.

**3. Bounded to pre-release contexts.** §16 does NOT apply to routine plan
review, BACKLOG triage, in-flight epic feedback, post-publish maintenance
review, or any other context outside "this is the assessment work between an
epic closing and a public release." The carve-out is structural: applying
§16's cadence beyond pre-release would re-introduce the problem Insight #2
addresses (every plan review becoming a 3-round campaign), and the evidence
base does not support generalization. Future spec versions may re-evaluate
this boundary after a non-release campaign produces evidence; for v2.9 the
scope is narrow.

### Rationale

- **Strict-then-surgical is honest about marginal cost.** Round 1 is
  wide-net-cheap — an Explore agent runs the catalog in well under a day. The
  marginal cost of widening Round 2 to "all minors from the Round 1 catalog"
  is high relative to the marginal yield (Round 2 produced 28 findings against
  Round 1's 70; the deferred-minor pool is large and mostly low-leverage).
  Surgical bar matches the cost-to-yield curve — it spends Round 2's review
  budget on candidates likely to clear a leverage bar, not on exhaustively
  re-evaluating Round 1's deferrals.
- **Phase 1.5 is the structural mitigation against treadmill rounds.** A round
  whose catalog produces fewer than the surgical-bar minimum of high-leverage
  candidates is signal that the campaign has converged. Continuing the round
  by lowering the bar produces motion (work performed) without progress (defects
  closed that mattered). Naming Phase 1.5 as a deliverable phase — not a
  silent "go / don't-go" check — forces the question into the artifact: every
  campaign's round-N artifact contains a Phase 1.5 section that says either
  "fired, closing series" or "did not fire because [specific affirmative
  justification]." The artifact is what makes the methodology auditable in 18
  months.
- **N=1 generalization is honest about evidence.** §16 does NOT claim the
  round counts (3), the escape-hatch threshold (<3 high-leverage candidates),
  or the yield rates (33% / 21% / 57%) are universal. The supply-chain
  campaign happened to converge in 3 rounds; another campaign may converge in
  2 or 4. The pattern §16 codifies is the **shape** (strict → surgical → tighter
  surgical + escape hatch), not the **counts**. A future campaign that converges
  differently is evidence that strengthens or refines §16, not evidence that
  refutes it — provided the shape (broader-then-narrower-then-honest-closure)
  holds.

### Implementation notes

- **Reference case study.** The canonical campaign artifact is
  `D:/Brains/audit/PRE-RELEASE-ASSESSMENT-2026-04-26.md`. It contains the
  full Round 1, Round 2, and Round 3 catalogs + picks, the Phase 1.5
  evaluation that nearly fired the escape hatch in Round 3, and the
  diminishing-returns retrospective quoted above. Future campaigns SHOULD
  produce a comparable artifact — same section structure, same Phase 1.5
  named phase, same retrospective table at close — so cross-campaign
  comparison is mechanically possible.
- **Skill integration.** The `plan-critic` skill at
  `D:/Brains/.claude/skills/plan-critic/SKILL.md` (and its NeuroGrim copy at
  `D:/Brains/NeuroGrim/.claude/skills/plan-critic/SKILL.md`) carries a
  `See Also` link to this section and a one-paragraph note in its "When to
  Run the Critic" section pointing pre-release / epic-close-out contexts to
  §16. The `plan-critic` skill protocol is unchanged — it remains
  single-pass — and the cross-reference is minimal-link, not substantive
  rewrite. This preserves the boundary the second non-commitment in this
  section names.
- **Cross-reference to METH-EV §15.** §15 is the precedent for a
  spec-impl-alignment exception driven by security urgency. §16 explicitly
  does **NOT** invoke §15's exception: pre-release verification has no
  security urgency that mandates implementation-first, and §16 is being
  documented at v2.9 in the absence of any conformance pressure to ship the
  cadence as a sensor. The cadence is a methodology pattern, not a protocol
  shape. If a future spec version absorbs §16's cadence into a normative
  sensor (e.g., a "pre-release-readiness" Brain domain), that absorption
  follows the conventional spec-first ordering, not §15's exception.
- **Cross-reference to METH-EV §14.** §14 is the precedent for bounded-evidence
  observational framing with explicit non-commitments. §16 follows §14's
  template structurally: it documents what a single experimental observation
  appears to suggest, names the gates that would promote it to normative
  status, and names the gates that would kill it. §14 uses access-pattern
  polymorphism as its observation; §16 uses the strict-then-surgical-then-escape
  cadence as its observation. The "What this section does NOT commit the spec
  to" subsection in both is the load-bearing BR-7 mitigation.
- **RFC 2119 discipline.** §16 deliberately uses no MUST in any cadence claim.
  The single MUST in this section is the methodology-hygiene rule that the
  diminishing-returns table MUST be quoted with the R3 caveat (because the
  table read in isolation actively misleads, which is a hygiene failure
  rather than a cadence failure). All cadence claims use SHOULD or
  RECOMMENDED, matching the evidence base (N=1 campaign).

### Deferred

- **Promotion of cadence-RECOMMENDED to cadence-MUST.** Requires a second
  campaign to validate the shape. Earliest candidate: the post-Brains-2.0
  v3.0 release campaign (E-B2-8 will itself be a pre-release campaign and
  will be its own §16 case study). If E-B2-8 converges in roughly the same
  shape — strict-then-surgical-then-escape — a future METH-EV revision MAY
  promote specific elements (likely the Phase 1.5 escape-hatch convention
  first) from RECOMMENDED to MUST.
- **Round-count generalization beyond 3.** §16 v1 names 3 rounds because the
  supply-chain campaign converged in 3; future campaigns may converge in 2
  or 4. The escape hatch is the structural answer, not a count — a v3+ spec
  may parameterize cadence by campaign size (small: 2; medium: 3; large: 4)
  if cross-campaign evidence supports it.
- **Application to non-release contexts.** Routine plan review, BACKLOG
  triage, in-flight feedback. §16 v1 carves these out per the third
  non-commitment; future spec versions may re-evaluate after a campaign
  produces evidence that a non-release context organically adopted a
  multi-round cadence. Until then, applying §16 outside pre-release is out
  of scope.
- **Cross-Brain assessment cadence.** A2A peer Brains running coordinated
  multi-round campaigns (e.g., the ecosystem Brain orchestrating Round 1
  catalogs across NeuroGrim and LSP-Brains in parallel) is a v3+ candidate.
  Orthogonal to §16 v1, which scopes to a single project's pre-release.
- **§16 sensor.** A future Brain domain could measure "is this campaign on a
  §16 cadence?" by reading audit-folder artifacts (presence of Round-N
  catalogs, Phase 1.5 evaluations, retrospective tables). Speculative;
  defer until at least 3 campaigns produce comparable artifacts.

### Update 2026-04-27 — first §16 case study (Brains-2.0 campaign close)

The Brains-2.0 self-observability campaign (E-B2-0..E-B2-8) closed
2026-04-27 and was the first campaign to apply §16 to its own pre-
release retrospective. Outcome:

- **Strict bar (Round 1) honored.** Each of the 9 epics ran a Layer-2
  plan-critic pass before execution. Plan-critic surfaced 18 open
  questions for E-B2-8 alone (Q1–Q18); 17 locked at Layer-2; only
  Q1+Q2 needed explicit operator authorization (charter amendment
  for the calibration-window reframe). Plan-critic surfaced 2 🔴
  blockers for E-B2-8 that would have shipped without an adversary
  pass — confirming Round 1's value proposition.
- **Surgical bar (Round 2) NOT invoked.** Round 1 + diminishing-
  returns signaling was sufficient at this campaign close. v3.1
  calibration-report gate may invoke Round 2 when promotion-readiness
  data lands (post-publish 30-day window).
- **Diminishing-returns signal fired.** Q-decisions in Round 1
  trended toward "lock the recommendation as-is" by Q-band C onward.
  The campaign converged on "ship the structural surface; defer
  empirical validation to v3.1." Convergence shape: strict-then-
  diminishing-returns with no surgical bar required, because the
  prior 7 epics had already locked the relevant primitives.
- **Phase 1.5 escape hatch NOT invoked.** No URGENCY trigger. The
  charter amendment was an explicit Layer-2 mechanism, not an
  escape-hatch firing.
- **Retrospective lands at** `audit/BRAINS-2-0-RETROSPECTIVE-2026-04-27.md`.
- **Charter amendment lands at** `audit/BRAINS-2-0-CHARTER.md` §
  Charter Amendment 2026-04-27.

**N=2 case-study count after Brains-2.0:** Brains-2.0 (this update)
joins the supply-chain campaign (`audit/PRE-RELEASE-ASSESSMENT-2026-
04-26.md`) as the second §16 case study. The two campaigns converged
in different shapes — supply-chain in 3 rounds (strict + surgical +
diminishing-returns), Brains-2.0 in essentially 1+½ rounds (strict +
diminishing-returns, no surgical bar). This bears out §16's
"round-count generalization" Deferred item: future campaigns may
converge in 2 or 4 rounds, and the structural answer is the escape
hatch + signaling, not a count.

**RFC 2119 status remains unchanged.** §16 cadence claims remain
SHOULD / RECOMMENDED. The N=2 evidence base is not yet sufficient
to promote any cadence element to MUST. A third campaign at v3.1+
(when the calibration-report gate fires) is the earliest candidate
for cadence-MUST promotion of the Phase-1.5 escape-hatch convention
(per the original Deferred item).

---

## 15. Supply-chain awareness as first-class Brain concern (2026-04-25)

### Problem

On 2026-04-23 a PyPI supply-chain incident surfaced involving
LiteLLM 1.82.7/1.82.8. The attack vector was second-order:
attackers compromised a security scanner binary (a malicious Trivy
release) which then ran in CI/CD with credentials, exfiltrated
tokens, and used those tokens to publish base64-payload-laden
versions of an otherwise-legitimate package that executed a
fork-bomb on `import`. The class of attack — **the scanner itself
becomes the attack vector** — has a name: scanner-chain
compromise.

Through v2.5 the spec said nothing about supply-chain awareness as
a Brain concern. Domains scored test health, code quality,
deployment readiness, agent behavior, but no domain measured
*"are the dependencies we're building on actually safe to build
on?"* Conforming Brains were silent on the supply chain — operators
were free to bolt on `cargo audit` / `pip-audit` / `npm audit` /
`trivy` themselves outside the Brain's scoring loop, but the
methodology gave no normative shape for doing so. Every adopter
solved the problem ad-hoc, with no shared contract for how findings
should be represented, accepted, scored, or shared between peer
Brains.

The incident also made a sharper point: **any SCA solution that
shells out to an external scanner binary inherits that binary's
trust.** A Brain that depends on `cargo audit` / `pip-audit` /
`trivy` to score its supply-chain health is one trojanized release
of those tools away from being the attack surface itself. The
LiteLLM incident IS that scenario, and the methodology had no
posture against it.

### The Insight

Supply-chain awareness is a first-class Brain concern, not a
bolt-on. It deserves a normative section in the spec the way agent
behavior (§15, v2.3) deserved one — because adopters need a shared
contract, because the failure modes are too important to leave
ad-hoc, and because the protocol shape (CMDB findings, advisory
weights, A2A peer signals, ledger-recorded human decisions) is the
same shape the rest of the methodology already uses.

The architectural insight from the LiteLLM incident is that
supply-chain awareness needs **three layers** that compose, not one
monolithic SCA scan:

1. **Layer 1 — Mechanical SCA.** Lockfile parsing + vulnerability-
   database query. Deterministic, exact-match, low false-positive
   rate. Answers: "is this dep+version on a known-bad list?"
2. **Layer 2 — Vigilance.** Deep-signal heuristics on
   publish-cadence, maintainer delta, signature gaps, binary
   reproducibility, typosquat proximity, exfil indicators.
   Probabilistic, advisory, harder to calibrate. Answers: "does
   this dep look like it might be turning bad?"
3. **Layer 3 — Agent-assisted human review.** Read-only static
   analysis by an LLM-judge agent on flagged deps; humans triage
   findings; decisions accrue in an append-only ledger. Answers:
   "we found something worth a human eye — what did the human
   decide and why?"

The three layers compose: Layer 1 catches the known-bad with high
precision; Layer 2 surfaces the "this smells off" signal that a
zero-day eventually triggers; Layer 3 puts a human in the loop
when neither mechanical answer is conclusive. None of the layers
auto-blocks or auto-rolls-back deps in v1 — humans gate, machines
advise.

The other architectural insight is **trust-surface minimization**.
The Brain's primary scoring path MUST NOT shell out to external
scanner binaries, because doing so inherits scanner trust. Native-
language SCA implementations (the reference implementation is
native Rust) query OSV.dev directly over HTTPS, supplemented with
a pinned local advisory database (RustSec for Rust; OSV's
PyPA/GHSA mirrors for Python/npm). External-scanner output is
permitted only as opt-in cross-check, never as the source of
truth. This narrows the trust surface from "every scanner binary
on the operator's CI runner" to "the Brain itself + a small set of
pinned libraries + OSV.dev's HTTPS endpoint."

### The Fix

New spec chapter §16 "Supply-chain awareness" (v2.6) formalizes
the three-layer contract:

- **§16.1 Concept** — supply-chain awareness as a cumulative
  property; three-layer framing; immune-system metaphor.
- **§16.2 Layer 1 — Mechanical SCA** — normative requirements:
  conforming Brains MUST query a vulnerability database; MUST NOT
  shell out to external scanner binaries in their primary scoring
  path; MUST emit findings in the CMDB envelope; SHOULD support
  response cache + accepted-advisories file with hygiene-lever
  semantics (a `note` is required for every accepted entry — no
  silent acceptance).
- **§16.3 Layer 2 — Vigilance** — normative shape for deep-signal
  scoring; MUST be advisory weight in v1; SHOULD pass calibration
  before any gating consequence.
- **§16.4 Layer 3 — Agent-assisted review** — Brains MUST run
  agent review in **read-only static analysis only** (no package
  code execution in automated pipelines) and MUST emit decisions
  to a `supply-chain-decision-ledger.jsonl` matching the v1
  schema; the **human decision MUST be the gate**, not the agent.
- **§16.5 The supply-chain-auditor hat** — conforming Brains MUST
  expose a hat for scoped human review. Hat content is
  implementation-defined per §5.4; the spec normatively requires
  the hat exists.
- **§16.6 A2A signal sharing** — bidirectional-opt-in consent
  model. New `supply-chain-signal` A2A message type. Both peers
  MUST declare the type in their Agent Card `accepts[]` for
  signals to flow.
- **§16.7 Schemas** — references the new `supply-chain-decision-
  ledger-v1.schema.json` and `a2a-supply-chain-signal-v1.schema.json`.
- **§16.8 Versioning + extensibility** — schemas closed but
  additive; new entry kinds bump schema version.
- **§16.9 Reference implementation** — pointer to NeuroGrim
  `neurogrim-sensory/src/supply_chain_sca/` and its operator guide
  `docs/supply-chain-sca.md`.

### Spec-impl-alignment observation

This is the **first time in the ecosystem's history** where the
implementation has shipped a normative protocol-shape feature
**before** the spec documented it. The pattern through v2.5 was
always "spec moves first; implementation follows" — that's how
agent behavior (§15) and A2A (§13) and cultural substrate (§14)
landed. E-SC-2 inverted that: the LiteLLM incident created
genuine urgency for self-protection (NeuroGrim's own dependency
graph needed to be green before its first crates.io publish), and
the spec section had to follow the sensor's behavior rather than
predict it.

This entry treats that ordering inversion as a methodology
evolution in its own right. The spec-impl-alignment domain in the
ecosystem Brain flags general drift between specification and
implementation; this acknowledges one acceptable case where the
ordering MAY invert. The conditions are bounded:

1. **Security urgency.** A live exploit class motivating
   self-protection in bounded time (days, not weeks).
2. **Spec-writers have implementation experience as input.** The
   spec section is written *after* the sensor has shipped — the
   author observes real behavior, real edge cases, real
   degradation modes, and writes the contract that captures what
   the sensor demonstrably does.

When BOTH conditions hold, implementation-first is acceptable.
When either is missing — the urgency is manufactured, or the
spec is being written without impl experience — the conventional
"spec first, implementation follows" ordering applies. This
discipline is not a license; it is a narrow exception with
explicit gates.

### Rationale

- **Three-layer separation matches the real attack-class taxonomy.**
  Mechanical SCA catches known-bad with low FP. Deep-signal
  vigilance catches the still-being-published-but-suspicious cases
  (LiteLLM's payload was visible in source diffs hours before the
  attack was confirmed). Agent-assisted review puts a human in
  the loop with structured agent help when the first two layers
  produce an ambiguous signal. Collapsing these into one layer
  would either over-block (every deep-signal alert blocks the
  build) or under-detect (only known-bad gets caught).
- **Trust-surface minimization is the structural answer to
  scanner-chain compromise.** Native-language SCA + direct
  OSV.dev + pinned local advisory submodule + opt-in external
  cross-check makes the Brain's own dependency on security
  tooling auditable line-by-line. This is the methodology's
  answer to "the scanner itself can be the attack vector": don't
  ship one.
- **Bidirectional-opt-in A2A consent is the conservative
  posture.** Supply-chain findings name specific packages and
  often specific maintainer behavior. Auto-broadcasting a finding
  to peer Brains creates legal exposure (defamation,
  tortious-interference) and also creates a multiplier on
  potential false-positives. Bidirectional opt-in (both peers
  declare `supply-chain-signal` in their Agent Card `accepts[]`)
  is tighter than the existing one-direction model and was a
  conscious choice. v2.7 may relax if real demand surfaces.
- **Read-only static analysis as MUST, not SHOULD.** A Brain that
  executes package code in its automated review pipeline is
  potentially executing the very attack it is reviewing. The
  bright line is "no execution"; this is a security-critical
  constraint, not a quality recommendation.
- **Count-based scoring rubric.** OSV batch responses don't carry
  per-advisory severity for many ecosystems; many RustSec
  advisories (especially `informational = "unmaintained"`) have no
  severity. A count-based rubric (0/1/2/3/4+ unaccepted →
  100/75/50/25/0) is honest about what the sensor can measure
  reliably. Severity-weighted scoring is a calibration candidate
  for v2.7+.
- **Accepted-advisories hygiene lever.** An advisory accepted
  silently is the failure mode the file is supposed to prevent.
  Requiring a non-empty `note` field on every accepted entry
  forces the operator to write down WHY — which is what makes the
  acceptance auditable in 18 months when the operator who made the
  decision has rotated off the project.

### Implementation notes

Reference implementation lives at
`D:/Brains/NeuroGrim/neurogrim/crates/neurogrim-sensory/src/supply_chain_sca/`:

- `lockfile/cargo.rs` + `python.rs` + `npm.rs` + `pnpm.rs` +
  `yarn.rs` — native parsers covering `Cargo.lock`, `uv.lock` +
  `requirements*.txt`, `package-lock.json` v2/v3, `pnpm-lock.yaml`
  v6/v9, `yarn.lock` (Classic + Berry).
- `osv.rs` — direct OSV.dev `/v1/querybatch` client over `reqwest`
  with file-backed 24h cache.
- `rustsec.rs` — local advisory-db submodule pinned to a specific
  commit; OSV-miss coverage + offline capability.
- `accepted.rs` — operator triage file
  (`.claude/supply-chain-accepted-advisories.toml`) with required
  `note` hygiene lever.
- `scoring.rs` — count-based rubric (E-SC-8 calibration candidate
  for severity-weighted upgrade).

The CMDB shape extends `cmdb-envelope-v1.schema.json` via
`additionalProperties` (no breaking change to the envelope). Two
new schemas land in this evolution: `supply-chain-decision-
ledger-v1.schema.json` (mirrors the `domain-promotion-ledger-v1`
pattern; five entry kinds — accept / reject / pin-to-last-good /
review-pending / review-triaged) and `a2a-supply-chain-signal-v1.schema.json`
(payload shape for the new A2A message type).

Operational scaffolding lives outside the Rust code:
- `audit/ROLLBACK-PLAYBOOK.md` (ecosystem repo) — sensor-specific
  recovery procedures populated epic-by-epic.
- `audit/TOOL-TRUST-NOTES.md` (ecosystem repo) — running record of
  tool-trust observations as ideas surface.
- `BEFORE-PUBLIC-RELEASE.md § Gate 11` — master gate forbidding
  `cargo publish` until Layer 1 is green and the sensor's own
  CMDB shows score 100.

### Deferred

- **Layer 2 (vigilance).** §16.3 names the seven sub-sensors
  (publish-cadence, maintainer-delta, signature gap, binary
  reproducibility, typosquat proximity, transitive surface delta,
  exfil indicator) but the reference implementation's E-SC-5 epic
  is the body of work. v2.6 establishes the contract; v2.7+ may
  tighten it once calibration evidence accrues.
- **Layer 3 (agent review).** §16.4 names the read-only static
  constraint, the ledger schema, and the human-decision gate. The
  reference implementation's E-SC-6 epic ships the
  supply-chain-auditor hat content + the LLM-as-judge invocation
  flow. The protocol shape is normative now; the specific
  implementation is post-v2.6.
- **Severity-weighted scoring.** Count-based scoring is honest
  about v1's data quality. As OSV severity coverage improves and
  RustSec adds severity to historically-unscored advisories, v2.7
  may add severity weighting as an opt-in scoring mode.
- **Cross-Brain finding aggregation.** §16.6 specifies the A2A
  signal envelope but does not specify aggregation semantics
  (e.g., "two independent peers flagging the same package
  bumps the finding to higher confidence"). That is a calibration
  candidate for v2.7+ once enough peer Brains exist for the
  pattern to be observable.
- **Active blocking / auto-rollback.** v1 is advisory + operator-
  gated. The publish-day runbook is the gate; the sensor proposes
  but the human disposes. Auto-rollback is a candidate for v3+
  once human-agreement rates on Layer 3 findings demonstrate the
  agent can be trusted with a tighter loop.
- **Severity-aware A2A signal aggregation.** The `severity_class`
  field in `a2a-supply-chain-signal-v1` allows downstream
  aggregation but does not define aggregation rules. Operators
  configuring multi-Brain topologies define their own rules in v1.

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

### Update 2026-04-23 — one-shot scope + held-out contradiction

Two subsequent pieces of evidence deserve absorption into this
observational entry:

**First**, a held-out back-test (22 tasks, 440 trials, Sonnet,
`reframe/factual-augmentation` branch) directly **contradicted**
the specific one-sentence dispatch rule derived from the original
12-task benchmark. Direct agreement with oracle dropped to 40.9%
(below the pre-registered 50% kill threshold). L1 won 18 of 22
held-out tasks — broader than the "factual-augmentation service"
framing suggested. The branch was abandoned per pre-registration.
Full post-mortem at `NeuroGrim/.claude/experiments/brain-vs-
control/reports/reframe-post-mortem.md`.

**Second**, and more fundamentally: the single-turn experimental
apparatus this discovery log rests on is a **bounded instrument**.
It measures how static-context-injection affects single-response
quality on a blind-judge rubric. It does NOT measure — and
structurally cannot measure in one-shot form — the longitudinal
value the Brain's infrastructure is organized around: consistency
across sessions, cumulative project awareness, culture-floor
persistence, gated-governance decision history, capability
hygiene over time, invocation-ledger self-observability. The
vast majority of the Brain's existing architecture is longitudinal
by design and is out of scope for these experiments.

§14's access-pattern-polymorphism observation stands, bounded by
that scope. The methodology's primary value hypothesis remains the
longitudinal one (persistent awareness across a project's
lifecycle); the single-turn experimental data is a secondary
instrument useful for specific sub-questions (context-injection
efficiency, agent self-routing on tools, content-freshness
failure modes). Future normative changes to the spec — in §14's
direction or any other — require evidence beyond single-turn
benchmarks.

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
2. **Rust types** — `ScoringSourceConfig` carries the `endpoint` string
   *(this struct was named `ScoringSource` when Session 3 landed; it
   was renamed to `ScoringSourceConfig` in NeuroGrim v5.0.0 / V5-MOD-1
   when the unqualified name `ScoringSource` was reclaimed for the
   pluggable trait)*
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
- `neurogrim-core/src/registry.rs` — `ScoringSourceConfig` gains
  `endpoint: Option<String>` + `interface_version: Option<String>`.
  *(Was named `ScoringSource` at Session 3 landing; renamed in
  NeuroGrim v5.0.0 / V5-MOD-1 when the trait of that name landed.)*
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
