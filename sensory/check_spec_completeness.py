"""Spec completeness sensory tool.

Measures whether every Table-of-Contents entry in the LSP Brains spec has a
body, and whether normative sections (those containing MUST/SHOULD/MAY) are
free of TBD/TODO/FIXME markers. Honest scoring — unknown is not good.
"""

from __future__ import annotations

import asyncio
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# SDK import — prefer installed `lsp_brains`; fall back to sibling layout.
try:
    from lsp_brains import SensoryTool, Finding  # noqa: E402
except ImportError:
    _SIBLING_SDK = Path(__file__).resolve().parents[2] / "Moth-er-Br-AI-n" / "sdk-python"
    if (_SIBLING_SDK / "lsp_brains" / "__init__.py").is_file():
        sys.path.insert(0, str(_SIBLING_SDK))
    from lsp_brains import SensoryTool, Finding  # noqa: E402


TOC_RE = re.compile(r"^\s*(\d+)\.\s+\[([^\]]+)\]\(#([^)]+)\)\s*$", re.MULTILINE)
NORMATIVE_TOKEN_RE = re.compile(r"\b(?:MUST|SHOULD|MAY|REQUIRED|SHALL|RECOMMENDED|OPTIONAL)\b")
TBD_RE = re.compile(r"\b(?:TBD|TODO|FIXME)\b")


class SpecCompletenessTool(SensoryTool):
    name = "check-spec-completeness"
    domain = "spec-completeness"

    async def analyze(self, project_root: str) -> dict[str, Any]:
        root = Path(project_root)
        spec_path = root / "spec" / "LSP-BRAINS-SPEC.md"
        if not spec_path.exists():
            return self.build_cmdb(
                score=0,
                findings=[Finding(f"Spec not found: {spec_path}", severity="critical")],
            )

        text = spec_path.read_text(encoding="utf-8")

        # Extract TOC entries (only numbered top-level entries: `N. [Title](#anchor)`)
        toc_entries = TOC_RE.findall(text)  # list of (num, title, anchor)

        # Extract all `## N. Title` bodies
        section_re = re.compile(r"^##\s+(\d+)\.\s+(.+)$", re.MULTILINE)
        headings = [(m.group(1), m.group(2).strip(), m.start(), m.end())
                    for m in section_re.finditer(text)]

        # Build body spans: from end of heading line to start of next `##` heading.
        next_heading_re = re.compile(r"^##\s", re.MULTILINE)
        missing_bodies: list[str] = []
        tbd_in_normative = 0
        tbd_details: list[str] = []

        for i, (num, title, _start, end) in enumerate(headings):
            # find next `##` heading
            m = next_heading_re.search(text, pos=end)
            body_end = m.start() if m else len(text)
            body = text[end:body_end]
            # Strip leading whitespace and check for prose presence
            stripped = body.strip()
            # A body must have prose beyond whitespace; require >40 non-whitespace chars.
            if len(re.sub(r"\s+", " ", stripped)) < 40:
                missing_bodies.append(f"Section {num}. {title}")
            # Check for TBD in normative-context sections
            if NORMATIVE_TOKEN_RE.search(body):
                for tbd in TBD_RE.finditer(body):
                    tbd_in_normative += 1
                    tbd_details.append(f"{num}. {title}: '{tbd.group(0)}'")

        # Cross-check: every TOC entry has a matching heading
        heading_nums = {num for (num, _, _, _) in headings}
        missing_from_headings: list[str] = []
        for (num, title, _anchor) in toc_entries:
            if num not in heading_nums:
                missing_from_headings.append(f"TOC entry {num}. {title} has no matching `## {num}.` heading")

        # Score
        score = 100
        score -= 5 * (len(missing_bodies) + len(missing_from_headings))
        score -= 10 * tbd_in_normative
        score = max(0, min(100, score))

        findings: list[Finding | str] = [
            Finding(f"TOC entries: {len(toc_entries)}"),
            Finding(f"Section headings found: {len(headings)}"),
            Finding(
                f"Missing bodies: {len(missing_bodies)}",
                severity="warning" if missing_bodies else "info",
            ),
            Finding(
                f"TBD/TODO/FIXME in normative context: {tbd_in_normative}",
                severity="warning" if tbd_in_normative else "info",
            ),
        ]
        for m in missing_bodies:
            findings.append(Finding(f"  missing body: {m}", severity="warning"))
        for m in missing_from_headings:
            findings.append(Finding(f"  {m}", severity="warning"))
        for d in tbd_details[:10]:
            findings.append(Finding(f"  {d}", severity="warning"))

        exported = {
            "spec:toc_entries": len(toc_entries),
            "spec:missing_bodies": len(missing_bodies) + len(missing_from_headings),
            "spec:tbd_count": tbd_in_normative,
        }
        return self.build_cmdb(score=score, findings=findings, exported_variables=exported)


def _run_and_write(project_root: Path) -> None:
    tool = SpecCompletenessTool()
    envelope = asyncio.run(tool.analyze(str(project_root)))
    # Stamp the source for traceability
    envelope["meta"]["source"] = (
        "scan of spec/LSP-BRAINS-SPEC.md: TOC entries vs section bodies, TBD markers in normative sections"
    )
    out_path = project_root / ".claude" / f"{tool.domain}-cmdb.json"
    out_path.write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}  score={envelope['score']}")


if __name__ == "__main__":
    _run_and_write(Path(__file__).resolve().parent.parent)
