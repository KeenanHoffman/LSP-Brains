# LSP-Brains spec-quality sensor tests

Seven spec-quality sensors live in `sensory/` — they score the spec itself.
These tests are the project-level §9 regression guards per spec §3.8
"Testing Discipline".

## Run

```
cd D:\Brains\LSP-Brains
py -3 -m pip install -r tests/requirements-dev.txt
py -3 -m pytest tests/ -v
```

## What each test asserts

Every per-sensor test validates (1) CMDB is schema-valid, (2) the tool's
declared `exported_variables` keys are present, (3) score is within the
tool's documented range. Regression guards are set to the current score so
any drop surfaces as a test failure.

| Sensor | Current score | Regression guard |
|---|---|---|
| `spec-completeness` | 100 | score >= 100 |
| `schema-validity` | 100 | score >= 100 |
| `link-integrity` | 100 | score >= 100 |
| `diagram-sync` | 100 | score >= 100 |
| `changelog-hygiene` | 100 | score >= 100 |
| `rfc-2119-compliance` | 97 | score >= 97 |
| `glossary-freshness` | 42 | score >= 42 |

The two below-100 sensors are not bugs in the sensors — they're honest
measurements of real state. Raising their scores is legitimate future work
(glossary-freshness in particular — there are terms to add to Appendix E).
The regression guard captures today's state so we don't silently regress
while working on other things.

## Relationship to spec §3.8

`tests/` is the concrete implementation of what §3.8 now normatively
describes. The existence of this test tree makes the LSP-Brains Brain
conformant to its own "Testing Discipline" subsection.
