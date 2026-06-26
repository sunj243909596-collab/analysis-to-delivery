# Tech Stack Path

## Purpose

Point to project-owned technology constraints for implementation-facing design.

## Required Entries

| Area | Path | When To Read | Owner |
|---|---|---|---|
| Backend | `docs/tech/backend.md` | Before API, service, transaction, or persistence design | Backend lead |
| Frontend | `docs/tech/frontend.md` | Before page, component, state, or interaction design | Frontend lead |
| Database | `docs/tech/database.md` | Before SQL, schema, index, sequence, or migration design | DBA or backend lead |
| Integration | `docs/tech/integration.md` | Before external API, message, job, or callback design | Architect |

## Rules

- Load only the area needed by the current stage.
- Prefer project paths over built-in examples.
- Treat missing database dialect as a blocking issue for SQL design.
