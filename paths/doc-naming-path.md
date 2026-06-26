# Document Naming Path

## Purpose

Define project-owned document names, sequence numbers, and output directories.

## Required Entries

| Document | Default Name | Output Directory | Required Stage |
|---|---|---|---|
| Task confirmation | `TASK_CONFIRM.md` | `docs/analysis/` | 2 |
| BRD | `01-BRD.md` | `docs/analysis/` | 3 |
| FSD | `02-FSD.md` | `docs/design/` | 7 |
| Data model | `03-DATA-MODEL.md` | `docs/design/` | 7 |
| Compliance review | `04-COMPLIANCE.md` | `docs/analysis/` | 4 |
| PRD | `05-PRD.md` | `docs/analysis/` | 6 |
| Development design | `06-DEV-DESIGN.md` | `docs/design/` | 7 |
| Test cases | `07-TEST-CASES.md` | `docs/test/` | 5 |
| Backtest report | `08-DESIGN-BACKTEST.md` | `docs/design/` | 7 |
| QA audit | `09-QA-AUDIT.md` | `docs/qa/` | 8 |
| Handoff | `HANDOVER.md` | `docs/handoff/` | 9 |

## Rules

- Keep numbering stable across the project.
- Do not renumber existing documents after signoff.
- If a project overrides a name, use that name consistently in later stages.
