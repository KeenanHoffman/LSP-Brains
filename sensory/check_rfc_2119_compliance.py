"""RFC 2119 compliance sensory tool.

Counts uppercase MUST/SHOULD/MAY usage (good) and flags lowercase
`must`/`should`/`will` occurrences (ambiguous-normative) in numbered spec
sections. Skips headings, fenced code blocks, inline code, and link text
to avoid false positives.
"""

from __future__ import annotations

import asyncio
import json
import re
import sys
from pathlib import Path
from typing import Any

_SDK_PATH = Path(r"D:/Brains/Moth-er-Br-AI-n/Moth-er-Br-AI-n-main/sdk-python")
if str(_SDK_PATH) not in sys.path:
    sys.path.insert(0, str(_SDK_PATH))

from lsp_brains import SensoryTool, Finding  # noqa: E402


UPPER_MUST_RE = re.compile(r"\bMUST\b")
UPPER_SHOULD_RE = re.compile(r"\bSHOULD\b")
UPPER_MAY_RE = re.compile(r"\bMAY\b")
LOWER_AMBIG_RE = re.compile(r"\b(will|should|must)\b")

CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`]*`")
LINK_TEXT_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")


def _strip_noise(text: str) -> str:
    """Remove fenced blocks, inline code, link URLs but keep link text."""
    text = CODE_FENCE_RE.sub(" ", text)
    text = INLINE_CODE_RE.sub(" ", text)
    # Replace `[link](url)` with just `link` so we still check the visible text.
    text = LINK_TEXT_RE.sub(lambda m: m.group(1), text)
    return text


def _collect_numbered_sections(text: str) -> list[tuple[str, str, str]]:
    """Return list of (section_id, title, body) for every `## N.` or `### N.M` section.

    We slice by heading position; body runs until the next heading of equal-or-higher depth.
    For ambiguous-normative detection we only care about numbered sections (not appendices,
    not "Conformance Language", not TOC).
    """
    heading_re = re.compile(r"^(#{2,3})\s+(\d+(?:\.\d+)?)\.?\s+(.+)$", re.MULTILINE)
    matches = list(heading_re.finditer(text))
    results: list[tuple[str, str, str]] = []
    for i, m in enumerate(matches):
        sec_id = m.group(2)
        title = m.group(3).strip()
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        # Skip body that begins with the next `## Appendix ...` — chop there if present.
        appendix_cut = re.search(r"^##\s+Appendix\s+", text[body_start:body_end], re.MULTILINE)
        if appendix_cut:
            body_end = body_start + appendix_cut.start()
        body = text[body_start:body_end]
        results.append((sec_id, title, body))
    return results


class RFC2119ComplianceTool(SensoryTool):
    name = "check-rfc-2119-compliance"
    domain = "rfc-2119-compliance"

    async def analyze(self, project_root: str) -> dict[str, Any]:
        root = Path(project_root)
        spec_path = root / "spec" / "LSP-BRAINS-SPEC.md"
        if not spec_path.exists():
            return self.build_cmdb(
                score=0,
                findings=[Finding(f"Spec not found: {spec_path}", severity="critical")],
            )

        text = spec_path.read_text(encoding="utf-8")

        # Uppercase usage across the whole (non-code) spec.
        clean_all = _strip_noise(text)
        must_count = len(UPPER_MUST_RE.findall(clean_all))
        should_count = len(UPPER_SHOULD_RE.findall(clean_all))
        may_count = len(UPPER_MAY_RE.findall(clean_all))

        # Ambiguous-normative: lowercase `will/should/must` in numbered-section bodies,
        # skipping headings, code, and link URLs. We further skip lines that begin with `|`
        # (table rows — often prose-agnostic) and blockquote lines.
        ambiguous: list[str] = []
        for (sec_id, title, body) in _collect_numbered_sections(text):
            cleaned = _strip_noise(body)
            for lineno, line in enumerate(cleaned.splitlines(), start=1):
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped.startswith("#"):
                    continue  # heading line
                # Skip markdown table rows (prone to false positives like "- should fail")
                if stripped.startswith("|"):
                    continue
                for m in LOWER_AMBIG_RE.finditer(line):
                    ambiguous.append(f"§{sec_id}: '{m.group(0)}' in: {stripped[:100]}")

        score = max(0, min(100, 100 - 1 * len(ambiguous)))

        findings: list[Finding | str] = [
            Finding(f"MUST occurrences: {must_count}"),
            Finding(f"SHOULD occurrences: {should_count}"),
            Finding(f"MAY occurrences: {may_count}"),
            Finding(f"Ambiguous-normative (lowercase will/should/must in numbered sections): {len(ambiguous)}",
                    severity="warning" if ambiguous else "info"),
        ]
        for m in ambiguous[:20]:
            findings.append(Finding(f"  {m}"))
        if len(ambiguous) > 20:
            findings.append(Finding(f"  ... {len(ambiguous) - 20} more"))

        exported = {
            "rfc2119:ambiguous_count": len(ambiguous),
            "rfc2119:must_count": must_count,
            "rfc2119:should_count": should_count,
            "rfc2119:may_count": may_count,
        }
        return self.build_cmdb(score=score, findings=findings, exported_variables=exported)


def _run_and_write(project_root: Path) -> None:
    tool = RFC2119ComplianceTool()
    envelope = asyncio.run(tool.analyze(str(project_root)))
    envelope["meta"]["source"] = (
        "scan of spec numbered sections for lowercase will/should/must vs RFC 2119 uppercase usage"
    )
    out_path = project_root / ".claude" / f"{tool.domain}-cmdb.json"
    out_path.write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}  score={envelope['score']}")


if __name__ == "__main__":
    _run_and_write(Path(__file__).resolve().parent.parent)
