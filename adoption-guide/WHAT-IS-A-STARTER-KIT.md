# What Is a Starter Kit?

A starter kit is a template that lets a new team adopt the LSP Brains pattern in an afternoon.
It is **not** a framework to install — it is a starting configuration to customize.

## What a Starter Kit Contains

| Component | Purpose | Required? |
|-----------|---------|-----------|
| `brain-registry.json` | Central Brain configuration (domains, weights, governance) | Yes |
| 3+ sensory tools | Observe project health and write CMDB snapshots | Yes |
| 1+ gates | Quality checkpoints that block actions when dirty | Yes |
| 1+ hooks | Automated triggers (e.g., validate on file save) | Recommended |
| Agent output schema | JSON Schema for Brain output validation | Yes |
| Tutorial | Step-by-step adoption walkthrough | Recommended |

## The Three Universal Domains

Every project has health signals in these areas. A starter kit SHOULD include sensory tools
for all three:

1. **Code Quality** — lint config, formatting, documentation, source structure
2. **Test Health** — test-to-source ratio, pass/fail rates, coverage
3. **Deploy Readiness** — CI/CD config, secrets management, version control hygiene

Teams add domain-specific domains (security, compliance, performance) after the base is working.

## Adoption Ramp

The recommended adoption sequence, from least to most complex:

1. **Score** — Run the Brain, see a health score. Understand what it measures.
2. **Gates** — Add quality gates that block actions when checks fail.
3. **Hooks** — Automate gate validation on file save or commit.
4. **Sensory tools** — Customize or add sensory tools for your project's domains.
5. **Hats** — Configure attentional bias for different operational contexts.
6. **Trajectory** — Accumulate score history and watch trends emerge.

## Language Independence

A starter kit can be built in any language. The contracts are:

- **Sensory tools** produce JSON conforming to `cmdb-envelope-v1.schema.json`
- **The Brain** produces JSON conforming to `agent-output-v1.schema.json`
- **Configuration** follows `brain-registry-v2.schema.json`

The reference implementation (Moth(er):Br+AI+n) is written in Rust. Sensory tools can be
written in any language — they communicate with the Brain via MCP (Model Context Protocol).

## MCP Sensory Model

In the v2 architecture, sensory tools are MCP servers. The Brain discovers and invokes them:

```
Brain (MCP Client) ──stdio/http──> Sensory Tool (MCP Server)
                                   └── tools/list: [check_code_quality, ...]
                                   └── tools/call: check_code_quality({project_root: "."})
                                       └── returns: CMDB-envelope JSON
```

This means:
- Sensory tools can be written in any language with an MCP SDK
- The Brain discovers available tools at startup
- External teams can publish sensory tools as standalone MCP servers
- The same protocol works locally (stdio) and remotely (HTTP)

## Adding a Domain

To add a new domain to a starter kit:

1. Add the domain key and weight to `config.domain_weights` in the registry
2. Add a display name to `config.principle_map`
3. Add a `domain_definitions` entry with `scoring_source` config
4. Create a sensory tool (MCP server) that produces CMDB-envelope JSON for that domain
5. Register the sensory server in `config.sensory_servers`
6. (Optional) Add correlations that reference the new domain
7. (Optional) Add domain-specific gates
