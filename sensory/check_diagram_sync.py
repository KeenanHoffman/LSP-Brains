"""Diagram-sync sensory tool.

Scans `spec/LSP-BRAINS-SPEC.md` for `diagrams/*.mmd` references, confirms
each referenced file exists under `spec/diagrams/`, and flags orphan
diagram files that sit in `spec/diagrams/` without any prose referencing
them.
"""

from __future__ import annotations

import asyncio
import json
import re
import sys
from pathlib import Path
from typing import Any

# SDK import — prefer installed `lsp_brains`; fall back to sibling layout.
try:
    from lsp_brains import SensoryTool, Finding  # noqa: E402
except ImportError:
    _SIBLING_SDK = Path(__file__).resolve().parents[2] / "NeuroGrim" / "sdk-python"
    if (_SIBLING_SDK / "lsp_brains" / "__init__.py").is_file():
        sys.path.insert(0, str(_SIBLING_SDK))
    from lsp_brains import SensoryTool, Finding  # noqa: E402


# Matches `diagrams/<name>.mmd` anywhere in the spec (prose, backticks, or blockquotes).
DIAGRAM_REF_RE = re.compile(r"diagrams/([A-Za-z0-9_\-]+\.mmd)")


class DiagramSyncTool(SensoryTool):
    name = "check-diagram-sync"
    domain = "diagram-sync"

    async def analyze(self, project_root: str) -> dict[str, Any]:
        root = Path(project_root)
        spec_path = root / "spec" / "LSP-BRAINS-SPEC.md"
        diagrams_dir = root / "spec" / "diagrams"

        if not spec_path.exists():
            return self.build_cmdb(
                score=0,
                findings=[Finding(f"Spec not found: {spec_path}", severity="critical")],
            )

        text = spec_path.read_text(encoding="utf-8")
        referenced = {m.group(1) for m in DIAGRAM_REF_RE.finditer(text)}

        present: set[str] = set()
        if diagrams_dir.is_dir():
            present = {p.name for p in diagrams_dir.glob("*.mmd")}

        missing = sorted(referenced - present)          # referenced but file missing
        orphans = sorted(present - referenced)          # file present but not referenced

        score = 100 - 10 * len(missing) - 3 * len(orphans)
        score = max(0, min(100, score))

        findings: list[Finding | str] = [
            Finding(f"Diagrams referenced in spec: {len(referenced)}"),
            Finding(f"Diagrams present on disk: {len(present)}"),
            Finding(f"Referenced but missing: {len(missing)}",
                    severity="critical" if missing else "info"),
            Finding(f"Orphan diagrams (unreferenced): {len(orphans)}",
                    severity="warning" if orphans else "info"),
        ]
        for m in missing:
            findings.append(Finding(f"  missing file: diagrams/{m}", severity="critical"))
        for o in orphans:
            findings.append(Finding(f"  orphan: diagrams/{o}"))

        exported = {
            "diagrams:referenced": len(referenced),
            "diagrams:present": len(present),
            "diagrams:missing": len(missing),
        }
        return self.build_cmdb(score=score, findings=findings, exported_variables=exported)


def _run_and_write(project_root: Path) -> None:
    tool = DiagramSyncTool()
    envelope = asyncio.run(tool.analyze(str(project_root)))
    envelope["meta"]["source"] = (
        "scan of spec for diagrams/*.mmd references vs files under spec/diagrams/"
    )
    out_path = project_root / ".claude" / f"{tool.domain}-cmdb.json"
    out_path.write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}  score={envelope['score']}")


if __name__ == "__main__":
    _run_and_write(Path(__file__).resolve().parent.parent)
