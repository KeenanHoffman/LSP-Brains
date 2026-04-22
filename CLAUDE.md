# LSP-Brains — Agent Guide

LSP-Brains is the **specification** for building agent nervous systems. It is the
methodology; `NeuroGrim` is the reference implementation. This repo has its own
Brain that scores **specification quality** — the first Brain in the ecosystem that
scores a methodology rather than a codebase. Ideas as code.

## Repository Structure

| Directory | Contents |
|-----------|----------|
| `spec/` | The LSP Brains Specification — `LSP-BRAINS-SPEC.md` (14 sections + appendices A–G), `DUAL-BRAIN-DESIGN.md`, `METHODOLOGY-EVOLUTION.md`, `diagrams/` |
| `schemas/` | Normative JSON Schemas — agent output, CMDB envelope, brain registry v2, A2A envelope v1, agent card v1, culture manifest v1 |
| `adoption-guide/` | Language-agnostic guide for building a starter kit |
| `.claude/` | This repo's Brain — `brain-registry.json`, seven spec-quality CMDB stubs, `culture.yaml`, `skills/` |

## The Brain at `.claude/`

This repo's Brain declares seven advisory domains (all weight 0.0 for v1 — sensory tools
are future work):

| Domain | What it measures |
|--------|------------------|
| `spec-completeness`    | All TOC entries have bodies; no "TBD" in normative sections |
| `schema-validity`      | All `*.schema.json` parse as draft-07; `$ref`s resolve |
| `link-integrity`       | Internal `§`-references resolve; METHODOLOGY-EVOLUTION back-references are valid |
| `glossary-freshness`   | Terms introduced in recent sections appear in Appendix E; no orphan entries |
| `diagram-sync`         | Diagrams referenced in spec prose exist under `spec/diagrams/` |
| `rfc-2119-compliance`  | MUST/SHOULD/MAY used consistently; no ambiguous "will"/"should" in normative contexts |
| `changelog-hygiene`    | Spec version bumps carry changelog entries citing METHODOLOGY-EVOLUTION |

CMDB stubs currently score 0 — that's the honest state until sensory tools land
(per spec principle #2). Building these sensory tools is a good follow-on project; they
are natural Python-SDK examples (small, single-purpose, operate on text files).

## Working in a Spec Repo

A spec repo is not a codebase, and the workflow has sharper edges:

1. **RFC 2119 discipline.** The spec uses MUST/SHOULD/MAY deliberately. Don't add
   normative language ("will", "should", "must") without the RFC 2119 context. Read spec
   §Conformance Language before editing normative sections.
2. **Additive version bumps by default.** v2.1 is additive to v2.0 — no field removed,
   no existing conformance claim invalidated. A breaking change earns v3.0 and requires
   a changelog entry.
3. **Schema-first for normative contracts.** If you change data that crosses a trust
   boundary (sensory tool output, agent output, A2A envelope, culture manifest, brain
   registry), change the schema first, then the prose.
4. **Changelog discipline.** Version bumps in the spec header require a changelog entry;
   the entry should cite the `METHODOLOGY-EVOLUTION.md` section that motivated it.
5. **Diagrams live under `spec/diagrams/`.** If you reference a diagram in the spec text,
   it must exist as a `.mmd` file. The `diagram-sync` domain will eventually enforce this.

## Skills

| Task | Skill |
|------|-------|
| Talk through a stuck problem with a Socratic subagent | `.claude/skills/rubber-duck/SKILL.md` |

The skill inventory is intentionally small. This is a spec repo; most work is prose and
schema editing, and the Brain is more advisory than operational.

## Cultural Substrate

The file `.claude/culture.yaml` is this repo's copy of the ecosystem-wide cultural
substrate (spec §14). It is byte-identical to the copies at `D:\Brains\.claude\` and
`D:\Brains\NeuroGrim\.claude\`. Agents working in this repo
honor the five values — positivity, integrity, honesty, critical-but-kind, respect —
as invariants that apply after hats, personas, and human-comms.

Drift between the three copies is flagged by the ecosystem Brain's `culture-coherence`
domain.

## Relationship to the Ecosystem

This repo is one of two children of the ecosystem Brain at `D:\Brains\.claude\`. The
ecosystem Brain will (eventually) query this Brain via A2A (spec §13 + Appendix G) when
the A2A server crate (`neurogrim-a2a`, Stage 6) ships. For now, this Brain is stand-
alone and observable via direct file reads.

## Spec Edits Workflow

For routine edits:
1. Make the spec change (and schema change if applicable)
2. Bump the spec version if the change is material (vX.Y+1 for additive, vX+1.0 for breaking)
3. Add a changelog entry to the spec header citing the METHODOLOGY-EVOLUTION section
4. Add or update a METHODOLOGY-EVOLUTION section if the change is a new structural idea
5. Update glossary and TOC if new terms or sections are introduced
6. Commit

The seven spec-quality domains exist to catch misses in steps 3–5 automatically when
their sensory tools land.
