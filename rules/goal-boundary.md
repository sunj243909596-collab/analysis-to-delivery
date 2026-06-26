# Goal Boundary Rule

## Purpose

Define what counts as complete for a requirement before analysis, design, implementation, QA, and handoff proceed.

## Required Decisions

Every requirement must state:

- Final business goal.
- Current delivery completion definition.
- Measurable success indicators.
- Explicit non-goals.
- Whether staged delivery is allowed.
- Phase goals when staged delivery is allowed.

## Phase Rules

If staged delivery is allowed, each phase must define:

| Field | Required Meaning |
|---|---|
| Phase | MVP, Phase 1, Phase 2, Later, or a project-owned name |
| Goal | The outcome this phase must achieve |
| Included scope | Capabilities included in this phase |
| Excluded scope | Capabilities intentionally deferred or rejected |
| Deliverables | Documents, code, configuration, data, migration, or tests expected |
| Acceptance criteria | Observable conditions that prove this phase is complete |
| Release blocker | Whether this phase blocks launch or can be deferred |

## Hard Gates

- Do not enter BRD if the current delivery completion definition is missing.
- Do not enter PRD if acceptance criteria are not mapped to a phase.
- Do not enter dev-design if Phase 1 or MVP acceptance criteria are untestable.
- Do not mark handoff complete without listing achieved phases, deferred phases, and remaining goal gaps.
