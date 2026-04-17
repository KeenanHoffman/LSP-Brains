"""Link-integrity sensory tool.

Scans the spec and METHODOLOGY-EVOLUTION.md for `§N`, `Section N`, and
`Appendix X` references in prose, then verifies each one resolves to an
actual `## N.` or `## Appendix X` heading. Lightweight — no markdown
parser needed, just regex and a skip-list for code fences.
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


SECTION_HEADING_RE = re.compile(r"^##\s+(\d+)\.\s+", re.MULTILINE)
SUBSECTION_HEADING_RE = re.compile(r"^###\s+(\d+\.\d+)\s+", re.MULTILINE)
APPENDIX_HEADING_RE = re.compile(r"^##\s+Appendix\s+([A-Z])\b", re.MULTILINE)

# Reference patterns in prose
SECTION_REF_RE = re.compile(r"(?:§|\bSection\s+)(\d+(?:\.\d+)?)")
APPENDIX_REF_RE = re.compile(r"\bAppendix\s+([A-Z])\b")

CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`]*`")


def _strip_code(text: str) -> str:
    text = CODE_FENCE_RE.sub(" ", text)
    text = INLINE_CODE_RE.sub(" ", text)
    return text


def _collect_headings(text: str) -> tuple[set[str], set[str], set[str]]:
    sections = set(SECTION_HEADING_RE.findall(text))
    subsections = set(SUBSECTION_HEADING_RE.findall(text))
    appendices = set(APPENDIX_HEADING_RE.findall(text))
    return sections, subsections, appendices


class LinkIntegrityTool(SensoryTool):
    name = "check-link-integrity"
    domain = "link-integrity"

    async def analyze(self, project_root: str) -> dict[str, Any]:
        root = Path(project_root)
        spec_path = root / "spec" / "LSP-BRAINS-SPEC.md"
        meth_path = root / "spec" / "METHODOLOGY-EVOLUTION.md"
        if not spec_path.exists():
            return self.build_cmdb(
                score=0,
                findings=[Finding(f"Spec not found: {spec_path}", severity="critical")],
            )

        spec_text = spec_path.read_text(encoding="utf-8")
        meth_text = meth_path.read_text(encoding="utf-8") if meth_path.exists() else ""

        spec_sections, spec_subs, spec_apps = _collect_headings(spec_text)

        total = 0
        broken: list[str] = []

        # Scan spec prose (strip code blocks and inline code)
        spec_prose = _strip_code(spec_text)
        for m in SECTION_REF_RE.finditer(spec_prose):
            ref = m.group(1)
            total += 1
            if "." in ref:
                top = ref.split(".")[0]
                # accept if subsection exists, or if its top-level section exists
                if ref not in spec_subs and top not in spec_sections:
                    broken.append(f"spec §{ref}: not found")
            else:
                if ref not in spec_sections:
                    broken.append(f"spec §{ref}: not found")
        for m in APPENDIX_REF_RE.finditer(spec_prose):
            letter = m.group(1)
            total += 1
            if letter not in spec_apps:
                broken.append(f"spec Appendix {letter}: not found")

        # Scan METHODOLOGY-EVOLUTION prose for spec references
        if meth_text:
            meth_prose = _strip_code(meth_text)
            for m in SECTION_REF_RE.finditer(meth_prose):
                ref = m.group(1)
                total += 1
                if "." in ref:
                    top = ref.split(".")[0]
                    if ref not in spec_subs and top not in spec_sections:
                        broken.append(f"METHODOLOGY-EVOLUTION §{ref}: not found in spec")
                else:
                    if ref not in spec_sections:
                        # METHODOLOGY-EVOLUTION also uses §N for its OWN sections.
                        # We check if it refers to a METHODOLOGY-EVOLUTION section first.
                        meth_sections = set(SECTION_HEADING_RE.findall(meth_text))
                        if ref not in meth_sections:
                            broken.append(f"METHODOLOGY-EVOLUTION §{ref}: not found in spec or self")
            for m in APPENDIX_REF_RE.finditer(meth_prose):
                letter = m.group(1)
                total += 1
                if letter not in spec_apps:
                    broken.append(f"METHODOLOGY-EVOLUTION Appendix {letter}: not found in spec")

        score = max(0, min(100, 100 - 3 * len(broken)))

        findings: list[Finding | str] = [
            Finding(f"References scanned: {total}"),
            Finding(f"Broken references: {len(broken)}",
                    severity="warning" if broken else "info"),
        ]
        # Collapse duplicates and report top 20
        seen: set[str] = set()
        for m in broken:
            if m in seen:
                continue
            seen.add(m)
            findings.append(Finding(f"  {m}", severity="warning"))
            if len(seen) >= 20:
                findings.append(Finding(f"  ... {len(broken) - 20} more"))
                break

        exported = {
            "links:total": total,
            "links:broken": len(broken),
        }
        return self.build_cmdb(score=score, findings=findings, exported_variables=exported)


def _run_and_write(project_root: Path) -> None:
    tool = LinkIntegrityTool()
    envelope = asyncio.run(tool.analyze(str(project_root)))
    envelope["meta"]["source"] = (
        "scan of spec prose for §N / Section N / Appendix X references vs actual headings"
    )
    out_path = project_root / ".claude" / f"{tool.domain}-cmdb.json"
    out_path.write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}  score={envelope['score']}")


if __name__ == "__main__":
    _run_and_write(Path(__file__).resolve().parent.parent)
