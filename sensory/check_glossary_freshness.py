"""Glossary freshness sensory tool.

Extracts bold-quoted terms (`**Term**`) in the spec outside Appendix E,
compares against glossary entries in Appendix E, and surfaces both
introduced-but-undefined terms and orphan glossary entries.

Glossary entries are recognized as leading-cell `**Term**` inside the
Appendix E markdown table.
"""

from __future__ import annotations

import asyncio
import json
import re
import sys
from pathlib import Path
from typing import Any

_SDK_PATH = Path(r"D:/Brains/Moth-er-Br-AI-n/sdk-python")
if str(_SDK_PATH) not in sys.path:
    sys.path.insert(0, str(_SDK_PATH))

from lsp_brains import SensoryTool, Finding  # noqa: E402


BOLD_RE = re.compile(r"\*\*([^*\n]+?)\*\*")
CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`]*`")
GLOSSARY_ROW_RE = re.compile(r"^\|\s*\*\*([^*|]+?)\*\*\s*\|", re.MULTILINE)
# Numbered-list-item label pattern: lines like `1. **Label**` or `- **Label**` followed by
# a dash or em-dash definition. These are structural sub-labels, not glossary-worthy terms.
LIST_ITEM_LABEL_RE = re.compile(
    r"^\s*(?:\d+\.|-)\s+\*\*([^*\n]+?)\*\*\s*(?:—|-|\()",
    re.MULTILINE,
)

# Terms to ignore: bold labels that aren't glossary-worthy (section markers, form labels).
IGNORE_TERMS = {
    "Version", "Date", "Status", "Purpose", "Context", "Tool Name", "Diagram",
    "Diagrams", "Tool name", "Input schema", "Output", "Output schema", "Example",
    "Required", "Optional", "Returns", "Parameters", "Default", "Note",
    "Canonical location", "Protocol boundary (v2.1+)", "Why this matters",
    "Problem", "Why two protocols", "Decision", "Rationale", "Scope",
    "Rule:", "Pattern", "Transport", "Severity", "Severity hint",
    "Fix priority", "Discovery flow", "Flow", "Usage", "Format",
    "Implementations", "Changelog",
    # Transport/config table-cell bolds — descriptive labels, not defined terms.
    "File-level locking", "Last-writer-wins with timestamps",
    "HTTP + Server-Sent Events (SSE)", "JSON-RPC over HTTP",
    "Gate tier weights",
    # Emphasis bolds in prose — describing things, not naming them.
    "agent nervous systems", "correlation engine", "continuous exponential decay",
    "raw scores", "human-comms", "identical", "invariants", "task",
}

# Story-ID pattern: `S6-DB-7`, `S5-TP-9`, etc. Never glossary terms.
STORY_ID_RE = re.compile(r"^S\d+-[A-Z]+-\d+$")


def _strip_code(text: str) -> str:
    text = CODE_FENCE_RE.sub(" ", text)
    text = INLINE_CODE_RE.sub(" ", text)
    return text


def _split_at_appendix_e(text: str) -> tuple[str, str]:
    """Return (before_glossary, glossary_onwards). Glossary begins at `## Appendix E`."""
    m = re.search(r"^## Appendix E\b", text, re.MULTILINE)
    if not m:
        return text, ""
    return text[: m.start()], text[m.start():]


def _normalize(term: str) -> str:
    return re.sub(r"\s+", " ", term).strip()


class GlossaryFreshnessTool(SensoryTool):
    name = "check-glossary-freshness"
    domain = "glossary-freshness"

    async def analyze(self, project_root: str) -> dict[str, Any]:
        root = Path(project_root)
        spec_path = root / "spec" / "LSP-BRAINS-SPEC.md"
        if not spec_path.exists():
            return self.build_cmdb(
                score=0,
                findings=[Finding(f"Spec not found: {spec_path}", severity="critical")],
            )

        text = spec_path.read_text(encoding="utf-8")
        before, glossary_block = _split_at_appendix_e(text)

        # Terms introduced in the body (exclude code blocks and inline code).
        prose_before = _strip_code(before)
        # Suppress numbered-list-item labels like `2. **Acceptance** — ...` which are
        # structural sub-labels, not glossary-worthy terms.
        list_item_labels = {_normalize(m.group(1)) for m in LIST_ITEM_LABEL_RE.finditer(prose_before)}
        introduced_raw = {_normalize(m.group(1)) for m in BOLD_RE.finditer(prose_before)}
        introduced_raw -= list_item_labels
        # Filter: keep terms of <= 6 words, alphabetical-leading, not ignored.
        introduced: set[str] = set()
        for term in introduced_raw:
            if not term:
                continue
            if term in IGNORE_TERMS:
                continue
            if term.endswith(":"):
                continue
            if len(term.split()) > 6:
                continue
            if not re.match(r"^[A-Z(]", term):
                # Lowercase-first bolds are emphasis, not term introductions.
                continue
            if STORY_ID_RE.match(term):
                # Story identifiers like `S6-DB-7` are roadmap markers, not terms.
                continue
            introduced.add(term)

        # Glossary terms from Appendix E rows
        glossary_terms = {_normalize(m.group(1)) for m in GLOSSARY_ROW_RE.finditer(glossary_block)}

        # Case-insensitive mapping for comparison
        gloss_lower = {t.lower() for t in glossary_terms}
        introduced_lower = {t.lower() for t in introduced}

        missing = sorted(t for t in introduced if t.lower() not in gloss_lower)
        orphans = sorted(t for t in glossary_terms if t.lower() not in introduced_lower)

        score = 100 - 5 * len(missing) - 2 * len(orphans)
        score = max(0, min(100, score))

        findings: list[Finding | str] = [
            Finding(f"Bold terms introduced in body: {len(introduced)}"),
            Finding(f"Glossary entries in Appendix E: {len(glossary_terms)}"),
            Finding(f"Introduced but undefined: {len(missing)}",
                    severity="warning" if missing else "info"),
            Finding(f"Orphan glossary entries (not referenced in body): {len(orphans)}",
                    severity="info"),
        ]
        for t in missing[:15]:
            findings.append(Finding(f"  missing: **{t}**", severity="warning"))
        for t in orphans[:15]:
            findings.append(Finding(f"  orphan: **{t}**"))

        exported = {
            "glossary:missing_count": len(missing),
            "glossary:orphan_count": len(orphans),
        }
        return self.build_cmdb(score=score, findings=findings, exported_variables=exported)


def _run_and_write(project_root: Path) -> None:
    tool = GlossaryFreshnessTool()
    envelope = asyncio.run(tool.analyze(str(project_root)))
    envelope["meta"]["source"] = (
        "scan of spec prose for **bold** terms vs Appendix E glossary rows"
    )
    out_path = project_root / ".claude" / f"{tool.domain}-cmdb.json"
    out_path.write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}  score={envelope['score']}")


if __name__ == "__main__":
    _run_and_write(Path(__file__).resolve().parent.parent)
