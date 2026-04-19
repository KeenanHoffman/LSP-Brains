# Dual Brain Architecture — Detailed Design

**Version:** 1.1
**Date:** 2026-04-17 (hybrid MCP + A2A update)
**Status:** Design (implementation tracked in Stage 6 "Dual Brain via A2A")
**Depends on:** LSP Brains Specification v2.1, Sections 10 + 13, Appendix G

---

## Purpose

This document expands LSP Brains Specification Section 10 into a detailed, implementable
design for the dual brain architecture. A developer reading only this document and the
spec MUST be able to build an external brain that cooperates with the existing local brain.

**Design constraint:** The local brain (NeuroGrim) MUST NOT require code changes
to support the dual brain architecture. All new behavior is additive — new files, new
triggers, new event routing — never modifications to existing scoring or governance logic.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Local Brain Responsibilities](#2-local-brain-responsibilities)
3. [External Brain Responsibilities](#3-external-brain-responsibilities)
4. [Trigger Model](#4-trigger-model)
5. [Event Protocol](#5-event-protocol)
6. [Shared State Protocol](#6-shared-state-protocol)
7. [Metadata Proximity Rules](#7-metadata-proximity-rules)
8. [Sync Protocol](#8-sync-protocol)
9. [Implementation Patterns](#9-implementation-patterns)
10. [Migration Path](#10-migration-path)
11. [Security Model](#11-security-model)
12. [Failure Modes](#12-failure-modes)

---

## 1. Architecture Overview

> **Diagram:** See `diagrams/dual-brain.mmd`
> **Diagram:** See `diagrams/dual-brain-detailed.mmd`

The dual brain architecture splits project health scoring between two cooperating
instances that share state files and communicate via a lightweight event protocol.

```
┌──────────────────────┐      ┌────────────────────┐      ┌──────────────────────┐
│    Local Brain       │      │   Shared State     │      │   External Brain     │
│  (developer terminal)│◄────►│  (file system or   │◄────►│  (cloud / CI)        │
│                      │      │   object store)    │      │                      │
│  Triggers:           │      │  brain-registry    │      │  Triggers:           │
│  - file save         │      │  test-gates        │      │  - webhook           │
│  - git commit        │      │  score-history     │      │  - cron schedule     │
│  - manual invocation │      │  proposal-ledger   │      │  - CI pipeline event │
│  - hook              │      │  incident-ledger   │      │  - queue message     │
│                      │      │                    │      │  - manual API call   │
│  Sensory:            │  ┌──►│  event-log.jsonl   │◄──┐  │  Sensory:            │
│  - git status        │  │   │  (append-only)     │   │  │  - cloud APIs        │
│  - lint output       │  │   └────────────────────┘   │  │  - CI results        │
│  - test results      │  │                            │  │  - issue tracker     │
│  - file system       │  │   ┌────────────────────┐   │  │  - SCA databases     │
│                      │──┘   │   Event Router     │   └──│  - monitoring        │
│  Output:             │◄────►│  (optional)        │◄────►│                      │
│  agent-output.json   │      │  file / queue /    │      │  Output:             │
│                      │      │  pub-sub           │      │  agent-output.json   │
└──────────────────────┘      └────────────────────┘      └──────────────────────┘
```

**Key invariants:**
- Both brains produce `agent-output-schema.json` compliant output
- Both brains read the same `brain-registry.json` structure
- Both brains contribute to the same score history
- Neither brain modifies the other's domain scores directly
- Shared state is the ONLY communication channel (plus optional events)

---

## 2. Local Brain Responsibilities

The local brain runs on the developer's machine. It is the v1 product
(NeuroGrim as currently implemented).

### 2.1 Performance Envelope

| Metric | Requirement | Rationale |
|--------|-------------|-----------|
| Score latency | < 5 seconds | Interactive developer workflow |
| Agent mode latency | < 10 seconds | Hook/automation acceptable |
| Ecosystem mode | < 30 seconds | Cross-project aggregation |
| Memory | < 200 MB | Developer machine constraint |
| Network | None required | Offline-capable |

### 2.2 Owned Domains

The local brain MUST own domains that require file system access:

- Code quality (lint configs, source file analysis)
- Test health (test file enumeration, test result parsing)
- Deploy readiness (git status, config file checks)
- Gate state (test-gates.json)
- Any domain whose sensory tool reads the local file system

### 2.3 Trigger Points

| Trigger | Mechanism | Typical Latency |
|---------|-----------|----------------|
| File save | Editor hook or file watcher | < 2s |
| Git commit | Pre-commit / post-commit hook | < 5s |
| Manual invocation | CLI command | < 5s |
| Claude Code hook | PostToolUse / PreToolUse | < 5s |
| Periodic refresh | Cron or scheduled task | N/A |

### 2.4 Outputs

The local brain writes:
- Agent output JSON (stdout or file)
- Score history snapshots (append to `score-history.json`)
- Proposal ledger entries (append to `proposal-ledger.json`)
- Event log entries (append to `event-log.jsonl`)
- CMDB files (sensory tool outputs)

---

## 3. External Brain Responsibilities

The external brain runs in a cloud environment (CI runner, Cloud Function, container,
or any server with network access).

### 3.1 Performance Envelope

| Metric | Requirement | Rationale |
|--------|-------------|-----------|
| Score latency | < 5 minutes | Background job, not interactive |
| Ecosystem aggregation | < 10 minutes | Cross-project, many children |
| API rate limits | Respect provider limits | Cloud API quotas |
| Execution frequency | Configurable (1/hr typical) | Balance freshness vs. cost |

### 3.2 Owned Domains

The external brain MUST own domains that require network/API access:

- CI/CD pipeline results (GitHub Actions, Jenkins, etc.)
- Issue tracker state (Jira, GitHub Issues, Linear)
- Software composition analysis (vulnerability databases)
- Production monitoring (uptime, error rates, latency)
- Dependency freshness (npm, pip, crate updates)
- Container image state (registry freshness, CVE scans)

### 3.3 Trigger Points

| Trigger | Mechanism | Source | Typical Latency |
|---------|-----------|-------|----------------|
| CI pipeline complete | Webhook | CI provider | < 30s after event |
| Issue state change | Webhook | Issue tracker | < 60s after event |
| Scheduled sweep | Cron / Cloud Scheduler | Timer | Exact schedule |
| Manual API call | HTTP POST | Operator | Immediate |
| Dependency alert | Webhook | Registry / Dependabot | < 5m after alert |
| Score request | Queue message | Parent brain or UI | < 30s after message |

### 3.4 Outputs

The external brain writes:
- Agent output JSON (to shared state or API response)
- Score history snapshots (append to `score-history.json`)
- CMDB files for owned domains (to shared state)
- Event log entries (append to `event-log.jsonl`)
- Incident ledger entries when cross-project patterns fire

---

## 4. Trigger Model

### 4.1 Trigger Types

A conformant dual brain implementation MUST support at least 6 trigger types:

| # | Trigger Type | Direction | Payload |
|---|-------------|-----------|---------|
| 1 | `file.changed` | Local | `{ "paths": ["src/main.ts"], "action": "save" }` |
| 2 | `git.committed` | Local | `{ "sha": "abc123", "message": "...", "files_changed": 5 }` |
| 3 | `manual.invoked` | Either | `{ "mode": "agent", "hat": "operator", "persona": "executive" }` |
| 4 | `ci.completed` | External | `{ "pipeline": "deploy-dev", "status": "success", "duration_s": 120 }` |
| 5 | `webhook.received` | External | `{ "source": "jira", "event": "issue.updated", "key": "PROJ-123" }` |
| 6 | `schedule.fired` | External | `{ "schedule_id": "hourly-sweep", "last_run": "2026-04-11T10:00:00Z" }` |
| 7 | `event.received` | Either | `{ "event_type": "score.updated", "brain_id": "local", "score": 74 }` |
| 8 | `snapshot.requested` | External→Local | `{ "requested_by": "external", "domains": ["code-quality"] }` |

### 4.2 Trigger Routing

Each trigger MUST specify which brain(s) should respond:

```json
{
  "trigger_routing": {
    "file.changed":       { "target": "local" },
    "git.committed":      { "target": "local" },
    "manual.invoked":     { "target": "specified" },
    "ci.completed":       { "target": "external" },
    "webhook.received":   { "target": "external" },
    "schedule.fired":     { "target": "external" },
    "event.received":     { "target": "specified" },
    "snapshot.requested": { "target": "local" }
  }
}
```

`"specified"` means the trigger payload includes a `target_brain` field.

### 4.3 Trigger Debouncing

Local brain triggers SHOULD be debounced to avoid redundant scoring:

| Trigger | Debounce Window | Strategy |
|---------|----------------|----------|
| `file.changed` | 2 seconds | Trailing edge (wait for burst to finish) |
| `git.committed` | None | Always score (commits are intentional) |
| `schedule.fired` | N/A | Timer handles cadence |

---

## 5. A2A Message Vocabulary

**v2.1 update:** This section was originally titled "Event Protocol." It is now recast
as the A2A message vocabulary. The 10 message types below are the normative vocabulary;
A2A (spec §13, Appendix G) is the normative transport. The legacy shared-file transport
(`event-log.jsonl`) is retained as a degraded-mode fallback for air-gapped environments
only.

### 5.1 Envelope Format

Messages are structured JSON objects conforming to `a2a-envelope-v1.schema.json`:

```json
{
  "schema_version": "1",
  "message_id": "msg_20260417T100000_abc123",
  "task_id": "task_20260417T100000_xyz789",
  "timestamp": "2026-04-17T10:00:00Z",
  "brain_id": "local",
  "message_type": "score.updated",
  "reply_to": null,
  "payload": {},
  "metadata": {}
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `schema_version` | string | MUST | Envelope schema version (currently "1") |
| `message_id` | string | MUST | Unique message identifier; used as idempotency key |
| `task_id` | string | OPTIONAL | Correlation ID for multi-message tasks |
| `timestamp` | string (ISO 8601) | MUST | When the message was produced |
| `brain_id` | string | MUST | Originating Brain id (matches Agent Card) |
| `message_type` | string | MUST | One of the 10 types defined in §5.2 |
| `reply_to` | string | OPTIONAL | For request/response: the `message_id` being answered |
| `payload` | object | MUST | Message-type-specific (see Appendix G.5 for shapes) |
| `metadata` | object | OPTIONAL | Transport/routing hints, trace IDs |

### 5.2 Message Type Vocabulary

| message_type | Producer | Consumer | Payload Summary |
|--------------|----------|----------|-----------------|
| `score.updated` | Either | Either | Interface Contract output (spec §6) |
| `gate.changed` | Either | Either | `gate_key`, `old_status`, `new_status`, `blocks`, `run_command` |
| `incident.detected` | Either | Either | `pattern_id`, `severity`, `hypothesis`, `domain_variables`, `recurrence_count` |
| `incident.resolved` | Either | Either | `pattern_id`, `resolved_at`, `resolved_by` |
| `ecosystem.scored` | External | Local | Interface Contract output with `children[]` populated (spec §9) |
| `config.changed` | Either | Either | `registry_path`, `changed_sections`, `committed_at` |
| `snapshot.requested` | External | Local | `scope`, optional `domain_filter` |
| `snapshot.delivered` | Local | External | Payload depends on scope; envelope `reply_to` matches request's `message_id` |
| `proposal.created` | Either | Either | Proposal object from learning ledger (spec §12) |
| `proposal.resolved` | Either | Either | `proposal_id`, `pre_score`, `post_score`, `action_types` |

See spec Appendix G.5 for canonical payload shapes.

### 5.3 Delivery Guarantees

A2A uses **at-least-once** delivery semantics:

- Messages MUST include a `message_id` for deduplication (idempotency key)
- Consumers MUST be idempotent — processing the same `message_id` twice MUST be a no-op
  that returns the cached response
- Messages MAY arrive out of order; consumers MUST use `timestamp` for ordering
- Failed deliveries SHOULD retry with exponential backoff (client side)
- Server responses for duplicated `message_id`s MUST return the cached response (not an error)

### 5.4 Transport

**Normative transport (v2.1+):** A2A (see spec §13 and Appendix G).
- HTTP + Server-Sent Events — RECOMMENDED
- JSON-RPC over HTTP — permitted

**Degraded-mode fallback:** shared file `event-log.jsonl`. Reserved for air-gapped
environments or bootstrap scenarios where an A2A server is not yet reachable. When used,
it MUST still encode envelopes that validate against `a2a-envelope-v1.schema.json` — the
schema is transport-independent. Consumers track their read position and dedupe by
`message_id`.

| Transport | Status | Latency | Suitable For |
|-----------|--------|---------|--------------|
| **A2A (HTTP+SSE)** | RECOMMENDED | Milliseconds | Cross-machine, streaming tasks |
| **A2A (JSON-RPC)** | Permitted | Milliseconds | Simple request/response peers |
| **Shared file** (degraded) | Fallback | Seconds (polling) | Air-gapped, bootstrap |

Message queues (SQS, Pub/Sub), webhooks, and git-based transports are deprecated at the
spec level — they are implementation choices beneath A2A, not alternatives to A2A.

---

## 6. Shared State Protocol

### 6.1 Shared State Files

| File | Truth Layer | Writers | Merge Strategy |
|------|-------------|---------|---------------|
| `brain-registry.json` | Source | Human (manual) | Not auto-merged (source truth) |
| `test-gates.json` | Runtime | Local (primarily) | Last-writer-wins by `updated_at` |
| `score-history.json` | Runtime | Both | Append-only, deduplicate by `scored_at` |
| `proposal-ledger.json` | Runtime | Both | Append-only, deduplicate by `timestamp` |
| `incident-ledger.json` | Runtime | Both | Append-only, deduplicate by `detected_at` |
| `event-log.jsonl` | Runtime | Both | Append-only (no merge needed) |
| `*-cmdb.json` | Runtime | Domain owner | Last-writer-wins by `meta.updated_at` |

### 6.2 Ownership Rules

Each shared state file has a primary owner:

- **Source truth files** (registry): Human-owned, never auto-modified by either brain
- **Runtime truth files** (CMDBs): Owned by the brain whose sensory tools produce them
- **Append-only files** (history, ledgers, events): Both brains append; no ownership conflict
- **Gate state**: Primarily local-owned (gates cleared by local test runs)

### 6.3 Concurrency Rules

Both brains MAY write to shared state simultaneously. Implementations MUST follow:

1. **Append-only files** (history, ledger, events): Append atomically (write to temp file,
   rename). No locking needed since appends don't conflict.
2. **Last-writer-wins files** (CMDBs, gates): Use `updated_at` / `meta.updated_at` timestamp.
   A write with an older timestamp MUST NOT overwrite a newer one.
3. **Source truth files** (registry): Never written by either brain automatically.

### 6.4 File Locking (Single Machine)

When both brains run on the same machine (e.g., external brain as a local daemon):

```
# Advisory lock pattern (cross-platform)
lock_file = "<state_file>.lock"

1. Create lock file with PID and timestamp
2. If lock file exists and PID is alive, wait with backoff
3. If lock file exists and PID is dead, remove stale lock
4. Write state file
5. Remove lock file
```

Maximum lock hold time: 5 seconds. Lock attempts timeout after 30 seconds.

### 6.5 External State Store (Distributed)

When brains run on different machines, shared state MUST be stored in an external
location both can access:

| Option | Mechanism | Consistency |
|--------|-----------|-------------|
| Cloud storage (GCS, S3) | Object versioning + conditional writes | Strong (with conditions) |
| Git repository | Commit + push/pull | Eventual (merge on pull) |
| Database | Transactions | Strong |

The recommended pattern for cloud storage:

```
1. Read current version (note generation/etag)
2. Compute new state
3. Write with precondition (if-generation-match)
4. If precondition fails, re-read and retry (optimistic concurrency)
```

---

## 7. Metadata Proximity Rules

### 7.1 The Core Rule

**Each brain SHOULD own domains whose sensory data is "near" it.**

"Near" means the data source is directly accessible without crossing a network
boundary (for local) or is only accessible via network (for external).

### 7.2 Classification Matrix

| Data Source | Proximity | Brain | Rationale |
|-------------|-----------|-------|-----------|
| Git working tree | File system | Local | `git status` requires local checkout |
| Lint/format configs | File system | Local | Config files on disk |
| Test results | File system / process | Local | Test runner is local |
| File counts / structure | File system | Local | Directory traversal |
| CI/CD pipeline results | API | External | CI provider webhooks |
| Issue tracker (Jira, GH Issues) | API | External | REST API required |
| SCA vulnerability data | API + DB | External | Vuln database network access |
| Production monitoring | API | External | Observability platform APIs |
| Container registry state | API | External | Docker registry API |
| Dependency update status | API | External | Package registry APIs |
| Score history | File / object store | Shared | Both brains read and write |
| Gate state | File / object store | Shared | Local writes, external reads |
| Proposal ledger | File / object store | Shared | Both brains append |

### 7.3 Boundary Cases

Some data sources span both proximities:

| Data Source | Resolution |
|-------------|-----------|
| Test results (local run vs. CI run) | Local brain owns local results; external brain owns CI results. Use different CMDB paths. |
| Git status (local vs. remote) | Local brain owns working tree state. External brain owns remote branch comparison. |
| Dependency lock files | Local brain reads the file. External brain queries the registry for update availability. |

When a data source spans proximities, each brain writes its own CMDB file with a distinct
path. The scoring engine treats them as separate domains or merges via correlation.

---

## 8. Sync Protocol

> **Diagram:** See `diagrams/sync-protocol.mmd` for the shared-state sync patterns
> (append-merge, last-writer-wins, event append) summarized below.

### 8.1 Score History Sync

Score history is the most critical shared state. Both brains append snapshots.

**Append-merge algorithm:**

```
1. Read local score-history.json
2. Read remote score-history.json (from shared store)
3. Merge: union of both, deduplicated by scored_at timestamp
4. Sort by scored_at ascending
5. Apply retention pruning (retention_days from registry)
6. Write merged result to shared store
```

**Deduplication key:** `scored_at` timestamp (ISO 8601, UTC).
If two entries have identical `scored_at`, keep the one with the higher `score`
(tie-break: alphabetical `brain_id`).

### 8.2 Incident Ledger Sync

Same append-merge pattern as score history.
**Deduplication key:** `detected_at` + `pattern_id`.

### 8.3 Proposal Ledger Sync

Same append-merge pattern.
**Deduplication key:** `timestamp` + first proposal `id`.

### 8.4 Gate State Sync

Gate state is a replace-merge (not append):

```
1. Read local test-gates.json
2. Read remote test-gates.json
3. For each gate key present in both:
   a. Compare updated_at timestamps
   b. Keep the entry with the more recent timestamp
4. Gates present in only one source: include in merged result
5. Write merged result
```

### 8.5 CMDB Sync

CMDB files are single-owner. The owning brain writes; the other brain reads.
No merge needed — but the reader MUST check `meta.updated_at` to detect staleness.

### 8.6 Sync Frequency

| Sync Target | Recommended Frequency | Acceptable Staleness |
|-------------|----------------------|---------------------|
| Score history | After each brain run | Minutes |
| Incident ledger | After each brain run | Minutes |
| Proposal ledger | After each brain run | Minutes |
| Gate state | After each gate change | Seconds (local), minutes (external) |
| CMDBs | After each sensory tool run | Hours (depends on domain) |
| Event log | Continuous (append) | None (append-only) |

---

## 9. Implementation Patterns

### 9.1 GitHub Actions External Brain

The simplest external brain: a GitHub Actions workflow triggered by events.

```yaml
# .github/workflows/external-brain.yml
name: External Brain
on:
  schedule:
    - cron: '0 * * * *'     # Hourly
  workflow_dispatch:          # Manual trigger
  workflow_run:
    workflows: [deploy-dev]   # After CI pipeline
    types: [completed]

jobs:
  score:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install PowerShell
        uses: PowerShell/setup-powershell@v1
      - name: Run external sensory tools
        run: |
          pwsh -File scripts/external/check-ci-health.ps1
          pwsh -File scripts/external/check-dependency-freshness.ps1
      - name: Score
        run: pwsh -File scripts/dev/Find-Brain.ps1 -Mode agent -Plain > agent-output.json
      - name: Sync state
        run: |
          # Push updated CMDBs and score history back to shared store
          git add .claude/brain/score-history.json .claude/*-cmdb.json
          git commit -m "chore: external brain score update" || true
          git push
```

### 9.2 Cloud Function External Brain

For event-driven architectures (GCP Cloud Functions, AWS Lambda):

```
Webhook → Cloud Function → Run sensory tools → Score → Write to shared store → Emit event
```

The function reads `brain-registry.json` from the shared store, runs its owned sensory
tools, computes scores, and writes results back.

### 9.3 Daemon External Brain

For continuous monitoring (systemd service, Docker container):

```
Timer loop:
  1. Read shared state
  2. Check trigger conditions (schedule, webhook queue)
  3. Run sensory tools for owned domains
  4. Score
  5. Sync state
  6. Emit events
  7. Sleep until next interval
```

### 9.4 Local Brain as External Brain

For development and testing, the local brain CAN act as both brains by running
two invocations with different domain configurations:

```powershell
# Local domains
Find-Brain.ps1 -Mode agent -Domains "code-quality,test-health" -Plain

# External domains (simulated locally)
Find-Brain.ps1 -Mode agent -Domains "ci-health,dependency-freshness" -Plain
```

This pattern is useful for testing the sync protocol before deploying a real
external brain.

---

## 10. Migration Path

> **Diagram:** See `diagrams/migration-path.mmd` for a visual overview of the five
> phases below (Phase 0 Local-Only → Phase 4 Events), including the zero-code-change
> transitions between Phases 0→1→2→3.

### 10.1 Phase 0: Local Only (Current State)

Single local brain. All domains scored locally. No external triggers.
Score history, gates, ledgers all local files.

### 10.2 Phase 1: Shared State

Move shared state files to an accessible location (cloud storage bucket or
shared git repository). Local brain reads/writes via the shared store.

**Changes required:** Configure state file paths in registry. Add sync script.
**Local brain code changes:** Zero (paths are already configurable).

### 10.3 Phase 2: External Sensory Tools

Add external sensory tools that write CMDBs to the shared store. These run
outside the local brain (CI jobs, cron scripts, webhooks).

**Changes required:** New sensory tool scripts. New CMDB paths in registry.
New domain definitions for external domains.
**Local brain code changes:** Zero (CMDB scoring is already generic).

### 10.4 Phase 3: External Brain

Deploy the external brain. It reads the same registry, runs its owned sensory
tools, scores its domains, and writes to the shared store.

**Changes required:** External brain deployment. Trigger configuration.
**Local brain code changes:** Zero.

### 10.5 Phase 4: Event Protocol

Enable event-based communication between brains. Events trigger cross-brain
actions (e.g., external brain detects CI failure → local brain notifies developer).

**Changes required:** Event log file or message queue. Event consumer in local brain.
**Local brain code changes:** Minimal (optional event consumer hook).

### 10.6 Phase 5: Ecosystem Integration

External brain handles ecosystem aggregation. Multiple projects' external brains
report to a parent external brain.

**Changes required:** Ecosystem registry for external brain. Parent brain deployment.
**Local brain code changes:** Zero.

---

## 11. Security Model

### 11.1 Authentication

| Channel | Authentication | Mechanism |
|---------|---------------|-----------|
| Shared state (cloud storage) | Service account | IAM role binding |
| Shared state (git) | SSH key or token | Deploy key / PAT |
| Webhooks (inbound) | Signature verification | HMAC-SHA256 |
| Webhooks (outbound) | Bearer token | API key in secret manager |
| Event queue | Service account | IAM role binding |

### 11.2 Authorization

Each brain SHOULD have minimum required permissions:

| Brain | Read | Write |
|-------|------|-------|
| Local | All shared state | Own CMDBs, append-only files, own events |
| External | All shared state | Own CMDBs, append-only files, own events |
| Neither | — | `brain-registry.json` (source truth, human-only) |

### 11.3 Secrets

Sensory tools that access external APIs MUST read credentials from environment
variables or a secret manager, never from committed files.

---

## 12. Failure Modes

### 12.1 External Brain Unreachable

**Impact:** External domains go stale. Confidence decays naturally via age-based
confidence scoring (Section 4.4 of the spec).

**Recovery:** Local brain continues to function. External domain CMDBs decay in
confidence. Score history shows the gap. When external brain recovers, it resumes
writing and confidence restores.

### 12.2 Shared State Unavailable

**Impact:** Neither brain can sync. Both continue scoring locally.

**Recovery:** When shared state is restored, sync protocol merges diverged state.
Append-only files merge cleanly. Last-writer-wins files use timestamps.

### 12.3 Event Delivery Failure

**Impact:** Cross-brain notifications delayed. No data loss (events are optional;
shared state is the source of truth).

**Recovery:** At-least-once delivery with retry. Consumers are idempotent.

### 12.4 Clock Skew

**Impact:** Timestamp-based deduplication and last-writer-wins may produce incorrect
results if clocks are significantly skewed.

**Mitigation:** All timestamps MUST be UTC. Implementations SHOULD use NTP.
Deduplication windows SHOULD tolerate up to 5 seconds of skew.

### 12.5 Conflicting Domain Ownership

**Impact:** If both brains claim the same domain, they may overwrite each other's
CMDB files.

**Prevention:** Domain ownership MUST be explicit in the registry:

```json
{
  "domain_definitions": {
    "code-quality": {
      "scoring_source": { "type": "cmdb", "path": "...", "owner": "local" },
    },
    "ci-health": {
      "scoring_source": { "type": "cmdb", "path": "...", "owner": "external" },
    }
  }
}
```

The `owner` field is OPTIONAL in v1 (backward compatible). When present, the
non-owning brain MUST NOT write to that domain's CMDB.

---

## Appendix A: Agent Output Extensions

The dual brain architecture adds OPTIONAL fields to the agent output:

```json
{
  "brain_id": "local",
  "brain_type": "local",
  "trigger": {
    "type": "git.committed",
    "payload": { "sha": "abc123" }
  }
}
```

These fields are OPTIONAL and do not break the existing schema (additionalProperties
is false in the current schema, so these would require a schema version bump to v2
when implemented).

## Appendix B: Event Log Format

The event log file (`event-log.jsonl`) uses JSON Lines format (one JSON object per line):

```jsonl
{"event_id":"evt_001","event_type":"score.updated","timestamp":"2026-04-11T10:00:00Z","brain_id":"local","version":"1","payload":{"score":74}}
{"event_id":"evt_002","event_type":"gate.changed","timestamp":"2026-04-11T10:01:00Z","brain_id":"local","version":"1","payload":{"gate_key":"lint-check","old_status":"dirty","new_status":"clean"}}
{"event_id":"evt_003","event_type":"ci.completed","timestamp":"2026-04-11T11:00:00Z","brain_id":"external","version":"1","payload":{"pipeline":"deploy-dev","status":"success"}}
```

The event log SHOULD be rotated when it exceeds 10,000 lines or 10 MB.
Old event logs MAY be archived or deleted.

## Appendix C: Registry Extensions for Dual Brain

The `brain-registry.json` MAY include a `dual_brain` section for future configuration:

```json
{
  "config": {
    "dual_brain": {
      "enabled": false,
      "local_brain_id": "local",
      "external_brain_id": "external",
      "shared_state": {
        "type": "file",
        "path": ".claude/brain/"
      },
      "event_transport": {
        "type": "file",
        "path": ".claude/brain/event-log.jsonl"
      },
      "sync": {
        "auto_sync": false,
        "sync_interval_seconds": 300
      }
    }
  }
}
```

This section is OPTIONAL and ignored by the current local brain implementation.
It exists as a configuration placeholder for Stage 6 implementation.
