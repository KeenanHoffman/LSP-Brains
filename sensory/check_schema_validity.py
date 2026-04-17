"""Schema validity sensory tool.

Parses every `schemas/*.schema.json`, verifies `$schema` is draft-07, and
resolves every internal `#/...` `$ref` within the same document. No external
schema libraries used — a minimal JSON Pointer walk is sufficient.
"""

from __future__ import annotations

import asyncio
import json
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


DRAFT_07 = "http://json-schema.org/draft-07/schema#"


def _resolve_pointer(doc: Any, pointer: str) -> bool:
    """Resolve a JSON pointer of the form '#/a/b/c' against `doc`. Return True if resolvable."""
    if not pointer.startswith("#"):
        return False  # external refs are not our concern here
    frag = pointer[1:]
    if not frag:
        return True
    if not frag.startswith("/"):
        return False
    cur: Any = doc
    for raw in frag.split("/")[1:]:
        key = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(cur, dict):
            if key not in cur:
                return False
            cur = cur[key]
        elif isinstance(cur, list):
            try:
                idx = int(key)
            except ValueError:
                return False
            if idx < 0 or idx >= len(cur):
                return False
            cur = cur[idx]
        else:
            return False
    return True


def _collect_refs(node: Any, out: list[str]) -> None:
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "$ref" and isinstance(v, str):
                out.append(v)
            else:
                _collect_refs(v, out)
    elif isinstance(node, list):
        for v in node:
            _collect_refs(v, out)


class SchemaValidityTool(SensoryTool):
    name = "check-schema-validity"
    domain = "schema-validity"

    async def analyze(self, project_root: str) -> dict[str, Any]:
        root = Path(project_root)
        schemas_dir = root / "schemas"
        if not schemas_dir.is_dir():
            return self.build_cmdb(
                score=0,
                findings=[Finding(f"schemas/ directory not found at {schemas_dir}", severity="critical")],
            )

        files = sorted(schemas_dir.glob("*.schema.json"))
        invalid: list[str] = []
        wrong_draft: list[str] = []
        broken_refs: list[str] = []
        total_refs = 0

        for f in files:
            try:
                doc = json.loads(f.read_text(encoding="utf-8"))
            except Exception as exc:
                invalid.append(f"{f.name}: JSON parse error: {exc}")
                continue
            dollar = doc.get("$schema")
            if dollar != DRAFT_07:
                wrong_draft.append(f"{f.name}: $schema={dollar!r} (expected draft-07)")
            refs: list[str] = []
            _collect_refs(doc, refs)
            total_refs += len(refs)
            for ref in refs:
                if ref.startswith("#"):
                    if not _resolve_pointer(doc, ref):
                        broken_refs.append(f"{f.name}: unresolved $ref {ref}")
                # external refs (e.g. http://...) are skipped (not our invariant)

        score = 100 - 20 * (len(invalid) + len(wrong_draft)) - 5 * len(broken_refs)
        score = max(0, min(100, score))

        findings: list[Finding | str] = [
            Finding(f"Schemas scanned: {len(files)}"),
            Finding(f"Invalid JSON schemas: {len(invalid)}",
                    severity="critical" if invalid else "info"),
            Finding(f"Non-draft-07 schemas: {len(wrong_draft)}",
                    severity="warning" if wrong_draft else "info"),
            Finding(f"$ref occurrences: {total_refs}"),
            Finding(f"Broken internal $refs: {len(broken_refs)}",
                    severity="warning" if broken_refs else "info"),
        ]
        for m in invalid + wrong_draft + broken_refs:
            findings.append(Finding(f"  {m}", severity="warning"))

        exported = {
            "schemas:count": len(files),
            "schemas:invalid_count": len(invalid) + len(wrong_draft),
            "schemas:broken_refs": len(broken_refs),
        }
        return self.build_cmdb(score=score, findings=findings, exported_variables=exported)


def _run_and_write(project_root: Path) -> None:
    tool = SchemaValidityTool()
    envelope = asyncio.run(tool.analyze(str(project_root)))
    envelope["meta"]["source"] = (
        "parse of schemas/*.schema.json: draft-07 conformance, internal $ref resolution"
    )
    out_path = project_root / ".claude" / f"{tool.domain}-cmdb.json"
    out_path.write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}  score={envelope['score']}")


if __name__ == "__main__":
    _run_and_write(Path(__file__).resolve().parent.parent)
