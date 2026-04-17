"""Changelog hygiene sensory tool.

Parses the `### Changelog` block in the spec header, checks each version
entry cites a `METHODOLOGY-EVOLUTION.md §N` section, and cross-checks that
every numbered `## N.` section in METHODOLOGY-EVOLUTION.md is cited by at
least one changelog entry.
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


# A version entry in the changelog, possibly spanning multiple lines until the next `- **vX.Y`.
VERSION_ENTRY_RE = re.compile(
    r"-\s+\*\*v(\d+\.\d+)\s*\(([^)]*)\):\*\*\s*(.*?)(?=\n-\s+\*\*v|\n---|\n##|\Z)",
    re.DOTALL,
)
METH_CITE_RE = re.compile(r"METHODOLOGY-EVOLUTION(?:\.md)?\s*§?\s*(\d+)", re.IGNORECASE)
# Also count `§N` references within changelog description that follow `METHODOLOGY-EVOLUTION`
METH_PLAIN_SECTION_RE = re.compile(r"§\s*(\d+)")
METH_HEADING_RE = re.compile(r"^##\s+(\d+)\.\s+", re.MULTILINE)


def _find_changelog_block(text: str) -> str:
    """Return the text of the `### Changelog` block, up to the next `---` or `##` heading."""
    m = re.search(r"^### Changelog\s*$", text, re.MULTILINE)
    if not m:
        return ""
    start = m.end()
    tail = text[start:]
    stop = re.search(r"^(?:---|##\s)", tail, re.MULTILINE)
    return tail[: stop.start()] if stop else tail


class ChangelogHygieneTool(SensoryTool):
    name = "check-changelog-hygiene"
    domain = "changelog-hygiene"

    async def analyze(self, project_root: str) -> dict[str, Any]:
        root = Path(project_root)
        spec_path = root / "spec" / "LSP-BRAINS-SPEC.md"
        meth_path = root / "spec" / "METHODOLOGY-EVOLUTION.md"
        if not spec_path.exists():
            return self.build_cmdb(
                score=0,
                findings=[Finding(f"Spec not found: {spec_path}", severity="critical")],
            )

        text = spec_path.read_text(encoding="utf-8")
        changelog = _find_changelog_block(text)

        entries = VERSION_ENTRY_RE.findall(changelog)  # list[(version, date, body)]
        uncited_entries: list[str] = []
        cited_meth_sections: set[str] = set()
        for (version, date, body) in entries:
            body_full = body.strip()
            # look for METHODOLOGY-EVOLUTION citation
            meth_hits = set(METH_CITE_RE.findall(body_full))
            # Also accept §N references that appear after a METHODOLOGY-EVOLUTION mention
            # within the same entry.
            if "METHODOLOGY-EVOLUTION" in body_full:
                for m in METH_PLAIN_SECTION_RE.finditer(body_full):
                    meth_hits.add(m.group(1))
            if not meth_hits and "METHODOLOGY-EVOLUTION" not in body_full:
                # v2.0 "Original release" shouldn't need a cite; only fault entries that
                # describe material change without citation. Heuristic: 2+ sentences.
                if re.search(r"[.!?].+?[.!?]", body_full):
                    uncited_entries.append(f"v{version} ({date}): missing METHODOLOGY-EVOLUTION cite")
            cited_meth_sections.update(meth_hits)

        # Cross-check METHODOLOGY-EVOLUTION sections
        meth_sections: set[str] = set()
        if meth_path.exists():
            meth_text = meth_path.read_text(encoding="utf-8")
            meth_sections = set(METH_HEADING_RE.findall(meth_text))

        uncited_meth = sorted(meth_sections - cited_meth_sections, key=lambda s: int(s))

        score = 100 - 15 * len(uncited_entries) - 5 * len(uncited_meth)
        score = max(0, min(100, score))

        findings: list[Finding | str] = [
            Finding(f"Changelog entries parsed: {len(entries)}"),
            Finding(f"METHODOLOGY-EVOLUTION sections present: {len(meth_sections)}"),
            Finding(f"Entries missing METHODOLOGY-EVOLUTION cite: {len(uncited_entries)}",
                    severity="warning" if uncited_entries else "info"),
            Finding(f"METH-EV sections with no changelog citation: {len(uncited_meth)}",
                    severity="warning" if uncited_meth else "info"),
        ]
        for e in uncited_entries:
            findings.append(Finding(f"  {e}", severity="warning"))
        for s in uncited_meth:
            findings.append(Finding(f"  uncited METH-EV §{s}"))

        exported = {
            "changelog:entries": len(entries),
            "changelog:uncited_meth_ev": len(uncited_meth),
        }
        return self.build_cmdb(score=score, findings=findings, exported_variables=exported)


def _run_and_write(project_root: Path) -> None:
    tool = ChangelogHygieneTool()
    envelope = asyncio.run(tool.analyze(str(project_root)))
    envelope["meta"]["source"] = (
        "scan of spec ### Changelog block for METHODOLOGY-EVOLUTION.md §N citations; "
        "cross-check against METHODOLOGY-EVOLUTION ## N. headings"
    )
    out_path = project_root / ".claude" / f"{tool.domain}-cmdb.json"
    out_path.write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}  score={envelope['score']}")


if __name__ == "__main__":
    _run_and_write(Path(__file__).resolve().parent.parent)
