# An Introduction to LSP Brains

*For engineers new to this project. Read this before the spec.*

---

## 1. The problem

Modern software projects drift in ways no single person sees.

A dependency gets pinned to an old version to unblock a release, and the
pin is still there eighteen months later. A test was green when it was
written, and no one notices that it now asserts nothing because a mock
changed upstream. A CI job got quieter after a flaky check was disabled
"temporarily." A secret was committed, rotated out of the code, and left
in the git history. Three team members independently forget the same
constraint in the same month.

Each of these is a small, local decision made by someone who meant well.
None of them are bugs. They do not trip tests. They do not break builds.
They accumulate, silently, in the gaps between the things anyone is
paid to watch.

We have instruments for the loud failures: alerts, stack traces, red
CI checks. We do not have good instruments for the quiet ones — the
slow loss of coherence between how the project *actually* works and how
everyone on the team *believes* it works. The gap between those two is
where projects go stale, where onboarding gets slower every quarter,
where the production incident that finally happens always traces back
to something nobody remembered was still there.

Observability tools watch the software. Linters watch the syntax. Tests
watch behavior. Nothing watches the project itself — its direction, its
coherence, its relationship to the decisions that were made a year ago
and the standards it claimed to follow.

You feel the drift as a sinking sense, periodically, that you don't
quite know the state of your own project anymore. You sit down with
fresh eyes on a Monday morning and it takes an hour to reacquaint
yourself. The hour is the symptom. The underlying problem is that
*nothing is maintaining the project's self-knowledge on your behalf
between Mondays.*

LSP Brains is a pattern for fixing that.

## 2. The pattern

The pattern is borrowed, quite directly, from biology.

A nervous system has three layers. **Sensory receptors** turn external
events into standardized signals. **Integrative neurons** combine those
signals into aggregate pictures of state. A **central brain** reads
those pictures, notices correlations, and decides where attention is
warranted.

LSP Brains translates this into software, one layer at a time.

**Sensory tools** are small programs — anything that can read a file,
run a command, or call an API — that observe some specific aspect of
the project and write their findings to a well-formed JSON document.
Not a dashboard. Not a metric in a time-series database. A *file*, in
the repo, with a schema, that other processes can read. One sensory
tool watches test health. Another watches dependency freshness.
Another watches secret hygiene, or documentation coverage, or
compliance evidence, or whatever the team cares about. Each one is
narrow, self-contained, replaceable.

**Domains** are the categories that group sensory readings into
meaningful pictures. "Test health" is a domain. "Security posture" is
a domain. A domain has a score between 0 and 100, and the score is
computed mechanically from its sensory tools' output. A domain is what
a human thinks in — "is our security posture okay?" — rendered as a
number the agent can compare against yesterday's.

**A Brain** reads the domains, computes a confidence-weighted
aggregate score, and — this is the part most scoring systems miss —
looks across domains for correlated patterns. A drop in test health
alongside a spike in dependency churn is a different story than
either one alone. The Brain sees the story. It decides which story is
worth surfacing.

Something you may notice about this pattern: **observation has
intrinsic value.** Most of what the Brain does, most of the time, is
quiet. It notices. It records. It builds context. The rare moment
when a recommendation surfaces is the tip of a long iceberg of
continuous attention underneath. The attention itself is the product.

A short, imagined output — what a Brain score looks like:

```
  Overall: 78 / 100  (was 81 yesterday)
  
  Test health            92   stable
  Security posture       71   declining  — one advisory unpatched
  Docs coverage          64   stable
  Human communication    88   stable
  
  Correlation: security-docs drift in the same week three times.
               Suggests docs tooling is out of date with current deps.
```

One aggregate number. A small collection of domain readings, each a
single integer. A trajectory arrow. And a sentence — the correlation
— that no single sensor could have produced alone, because it lives
at the intersection.

## 3. What changes when you have it

Concretely, three things.

**Before:** "Is the project healthy?" takes half a day to answer with
any confidence, and the answer depends on who you ask. Someone
remembers the flaky test. Someone else remembers the pinned dep.
Nobody remembers the expired certificate.

**After:** The same question returns a single number and a short
narrative, at any moment, without anyone being interrupted to
produce it. Disagreements about project health become disagreements
about what the sensors *should* be measuring, which is a much more
productive argument.

---

**Before:** An AI agent opens the project fresh and asks questions that
a ten-year veteran would never ask, because the veteran carries context
the agent does not have. Every session starts from scratch. The agent's
recommendations are shallow because they are based on a shallow reading.

**After:** The agent's first action is to read the Brain's current
score and the recent trajectory. Before writing a line of code, it
knows what's slipping and what's healthy, where the project has been
this week, what recent recommendations were taken and what were not.
It acts on a foundation that is closer to the veteran's — not the
same, but materially richer than a cold read.

---

**Before:** An incident happens. The post-mortem asks what signal could
have warned us earlier. Usually the honest answer is: the signal was
there, distributed across three dashboards, and nobody happened to be
looking at all three on the same day.

**After:** The signal is already aggregated. The correlation between
"test flakiness in the auth module" and "dependency churn in the token
library" was visible in the Brain's output before the incident. It
didn't page anyone, because it wasn't an emergency. But it was
available, to anyone — human or agent — who glanced at the score on
the day they sat down to touch auth code.

None of this prevents incidents. It makes the conditions that produce
them legible earlier.

## 4. Who this is for

LSP Brains is designed for teams with **at least three people** and
**at least two moving parts.**

"Three people" is where collective memory starts to fray. Two people
keep each other honest by accident; three people drift. "Two moving
parts" is where cross-domain correlation starts to matter — a project
that is only code, or only infrastructure, rarely has patterns worth
correlating across domains.

It is overkill for a solo project or a one-week prototype. It is
probably the wrong fit for a team whose main problem is velocity
under fire; the pattern rewards sustained attention, not firefighting.
It is a strong fit for:

- Teams where institutional memory keeps getting re-derived from git
  history.
- Projects that have been alive long enough for the original context
  to have partly evaporated.
- Teams collaborating heavily with AI agents, where the agent's
  quality of contribution is rate-limited by the quality of its
  situational awareness.
- Codebases or ecosystems where parts of the project answer to
  different concerns — security, compliance, cost, reliability — and
  a single monolithic dashboard does not serve any of them well.

The pattern is **fractal**. One project has a Brain; an ecosystem of
projects can have a parent Brain that reads its children's Brains and
notices ecosystem-level patterns that no single project could see. The
same mechanism repeats at every scale.

## 5. Next steps

If the problem resonates, the spec is the next thing to read.
It is in this repo at `spec/LSP-BRAINS-SPEC.md`. It is long — fourteen
sections, seven appendices — because the contracts between sensory
tools, Brains, and peers need to be precise. But each section is
self-contained, and the appendices are reference material you can
consult as needed, not required reading cover-to-cover.

If you want to see the pattern in living code, a reference
implementation exists in Rust as a sibling repo in this ecosystem.
It dogfoods its own spec — its Brain scores its own codebase on
the same domains the spec describes, and the results are published
in the repo. That is the honest way to publish a scoring methodology:
with a worked example that does not hide its own weaknesses.

If you want to contribute, the smallest useful thing to do is write a
sensory tool. The tool-writing contract is short (see spec §3.7), the
output schema is in `schemas/cmdb-envelope-v1.schema.json`, and new
tools are additive — they do not disturb existing ones. The Python SDK
in the reference implementation's `sdk-python/` directory has examples.

---

## A note on the name

This document refers to the reference implementation by its stylized
form, "Moth(er):Br+AI+n," but the plain-text name is currently under
trademark review. The public name may differ from drafts in this
repository. The methodology — "LSP Brains" — is the stable, long-term
name. The implementation's name is contingent.

## A note on confidence

This document was written early. The pattern is real; the
implementation work is ongoing. The conformance suite that will make
"LSP Brains-compliant" a third-party-verifiable claim is not complete.
The Python SDK is not yet on PyPI. The public release of the Rust
reference is gated on security and legal review. Principle #2 of this
project is that scoring must be honest, and that applies to the
project itself: it is a small, focused effort with working parts and
unfinished parts, and the unfinished parts are catalogued openly.

If that is the shape of project you want to work with, welcome.
