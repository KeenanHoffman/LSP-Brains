# LSP Brains Specification

A language-agnostic specification for giving AI agents continuous project health awareness
through sensory tools, scoring contracts, trajectory intelligence, and gated governance.

**New here?** Read [INTRO.md](INTRO.md) first — a five-page, problem-first introduction
to the pattern before the spec's normative detail.

## What is LSP Brains?

LSP Brains defines a pattern — not a tool — for building an agent nervous system:

1. **Sensory tools** observe project state and write structured health snapshots (CMDB files)
2. **A Brain** reads those snapshots, computes confidence-weighted scores, and detects cross-domain patterns
3. **Governance gates** control what the agent can do autonomously vs. what requires human approval
4. **Trajectory intelligence** tracks velocity and acceleration of health scores over time
5. **Hats** provide attentional bias — same data, different emphasis depending on context

The architecture is fractal: a single project has a Brain, an ecosystem has a parent Brain
consuming child scores. The same pattern repeats at every scale.

## Repository Contents

```
spec/
  LSP-BRAINS-SPEC.md           The specification (14 sections + appendices A-G)
  METHODOLOGY-EVOLUTION.md     7 structural improvements (§6 = hybrid MCP+A2A, §7 = cultural substrate)
  DUAL-BRAIN-DESIGN.md         Local + external brain coordination design (v1.1: A2A-based)
  diagrams/                    10 Mermaid diagrams

schemas/
  agent-output-v1.schema.json      JSON Schema for Brain agent-mode output
  cmdb-envelope-v1.schema.json     JSON Schema for sensory tool CMDB output
  brain-registry-v2.schema.json    JSON Schema for Brain configuration
  a2a-envelope-v1.schema.json      JSON Schema for A2A peer-Brain messages
  agent-card-v1.schema.json        JSON Schema for Brain Agent Cards
  culture-manifest-v1.schema.json  JSON Schema for the cultural substrate manifest (§14)

adoption-guide/
  WHAT-IS-A-STARTER-KIT.md    Language-agnostic guide to building a starter kit
```

## Implementations

| Implementation | Language | Repository |
|---------------|----------|------------|
| Moth(er):Br+AI+n | Rust | [KeenanHoffman/Moth-er-Br-AI-n](https://github.com/KeenanHoffman/Moth-er-Br-AI-n) |

## Ecosystem Context

This repo is one of three in the [Brains-ecosystem](https://github.com/KeenanHoffman/Brains-ecosystem):

- **LSP-Brains** (this repo) — the methodology (spec + schemas + sensory tools scoring the spec itself)
- **Moth-er-Br-AI-n** — the Rust reference implementation
- **Brains-ecosystem** — coordination layer (ecosystem Brain that measures spec↔impl alignment, culture coherence, etc.)

To clone the whole ecosystem at once: `git clone --recursive git@github.com:KeenanHoffman/Brains-ecosystem.git`.
To clone just this spec (no impl, no ecosystem Brain): `git clone git@github.com:KeenanHoffman/LSP-Brains.git`.

### Running the spec-quality sensory tools

The 7 Python sensory tools under `sensory/` (spec-completeness, schema-validity, link-integrity,
glossary-freshness, diagram-sync, rfc-2119-compliance, changelog-hygiene) currently depend on the
`lsp_brains` Python package shipped in `Moth-er-Br-AI-n/sdk-python/`. They import via a
hardcoded `sys.path` shim assuming the monorepo layout (sibling directories under `D:\Brains\`).

If you cloned this repo standalone (without the ecosystem), the tools won't import. Two options:

1. **Recommended — clone the full ecosystem** via `--recursive` on `Brains-ecosystem`. The tools
   then find the SDK at their expected sibling path.
2. **Install the SDK from source** — `pip install -e <path-to>/Moth-er-Br-AI-n/sdk-python/` and then
   edit the `_SDK_PATH` shim at the top of each `sensory/check_*.py` to be a no-op (remove the
   `sys.path.insert`). PyPI publication of the SDK is not yet in place.

The sensor tools score the spec itself — they're the "ideas as code" proof-of-concept and shouldn't
be treated as blocking for adopters who just want to read the spec.

## Design Principles

1. Declarations over dashboards — agents read files, not UIs
2. Scoring must be honest — unknown is not good; confidence weights matter
3. Observation has intrinsic value — just looking increases self-knowledge
4. Hats are how agents think — context-dependent emphasis, not personas
5. Fractal by design — works at project AND ecosystem scale
6. Pattern is the product — specific domains are implementation details
7. Trajectories reveal more than snapshots — velocity and acceleration are first-class
8. Right protocol for the role — MCP for tool invocation, A2A for peer-Brain coordination (see spec §13, Appendix G)

## Protocols

Two protocols carry traffic in and out of a conformant Brain. They are orthogonal.

| Protocol | Role | Spec section |
|----------|------|--------------|
| **MCP** (Model Context Protocol) | Sensory tool invocation (Brain-as-MCP-client) + Brain exposure to LLM agents (Brain-as-MCP-server) | §3.7, Appendix F |
| **A2A** (Agent2Agent Protocol) | Brain-to-Brain peer communication: fractal composition (parent↔child) and dual brain (local↔external) | §9, §10, §13, Appendix G |

MCP is a tool-call protocol; A2A is a peer-agent protocol. Using MCP for peer Brain
coordination or A2A for sensory/LLM-facing work is explicitly discouraged. See
`METHODOLOGY-EVOLUTION.md` §6 for the rationale.

## Quick Reference

**Sensory Tool Contract (MCP):** Write JSON with `score` (0-100), `updated_at` (ISO 8601), and
`meta` envelope. Validate against `schemas/cmdb-envelope-v1.schema.json`. Serve via MCP
`check_<domain>` tool (spec §3.7).

**Brain Output Contract:** Produce JSON with 11 required fields (score, domains, gates,
recommendations, correlations, etc.). Validate against `schemas/agent-output-v1.schema.json`.

**Configuration:** Hand-maintain a `brain-registry.json` defining domains, weights, governance,
intelligence rules, and peer topology. Validate against `schemas/brain-registry-v2.schema.json`.

**Peer Brain Contract (A2A):** Publish an Agent Card at `/.well-known/agent-card.json`
validating against `schemas/agent-card-v1.schema.json`. Exchange A2A messages (10 canonical
types) validating against `schemas/a2a-envelope-v1.schema.json`. See spec §13 + Appendix G.

## License

MIT
