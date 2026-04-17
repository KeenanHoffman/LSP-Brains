"""LSP-Brains spec-quality sensory tools.

Seven tools that observe the LSP-Brains specification and emit CMDB envelopes
for the seven advisory domains declared in `.claude/brain-registry.json`:

    check_spec_completeness   - TOC entries have bodies; no TBD in normative sections
    check_schema_validity     - `schemas/*.schema.json` parse as draft-07; `$ref`s resolve
    check_link_integrity      - `Section N` / `Appendix X` references in prose resolve
    check_glossary_freshness  - bold-quoted terms appear in Appendix E glossary
    check_diagram_sync        - spec diagram references match files under `spec/diagrams/`
    check_rfc_2119_compliance - lowercase "must/should/will" in normative sections flagged
    check_changelog_hygiene   - version entries cite METHODOLOGY-EVOLUTION sections

The tools observe; they do not edit. Each is runnable as a script
(`py -3 sensory/check_<x>.py`) and writes to `.claude/<domain>-cmdb.json`.
"""
