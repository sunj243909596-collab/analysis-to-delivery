# Rules and Path Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` or `superpowers:executing-plans` to implement this plan task by task. Steps use checkbox syntax for tracking.

**Goal:** Refactor `analysis-to-delivery` from a Skill-heavy workflow into a thin Skill router with explicit `rules/` and `paths/` boundaries.

**Architecture:** Keep Skills as action and orchestration entrypoints. Move cross-stage invariants from `skills/disciplines/` into `rules/`. Normalize project-level configuration pointers into `paths/`. Each stage Skill declares the rules and paths it needs, and validation scripts enforce those declarations.

**Tech Stack:** Markdown Skills, Python validation scripts, Bash smoke tests, existing `pytest` suite, existing templates and examples.

---

## 1. Problem Statement

The current structure relies too heavily on Skills. This creates three problems:

- Context bloat: large Skill bodies are loaded when only a few constraints are needed.
- Blurry boundaries: routing, workflow steps, project configuration, and global rules are mixed together.
- Weak validation: stage Skills mention required disciplines in prose, but there is no machine-checkable declaration.

The target model separates responsibility:

```text
Skill = action or workflow entrypoint
rules = cross-stage invariant constraints
paths = project-owned context pointers
```

## 2. Target Directory Model

```text
analysis-to-delivery/
  SKILL.md                         # thin router only
  skills/
    ask-delivery/                  # router
    user-invoked/                  # single actions
    orchestration/                 # full workflow and implementation bridges
  rules/
    stage-gate.md
    no-field-guessing.md
    no-self-invent.md
    ascii-flowchart.md
    sql-dialect.md
    doc-numbering.md
    context-pointer.md
    goal-boundary.md
  paths/
    knowledge-path.md
    compliance-path.md
    tech-stack-path.md
    doc-naming-path.md
  templates/
  scripts/
  tests/
```

## 3. Responsibility Boundaries

| Layer | Owns | Does Not Own |
|---|---|---|
| Root `SKILL.md` | Triggering, routing, quick start, minimal architecture map | Full rules, stage procedures, large examples |
| `skills/user-invoked/*` | One user-visible action and its outputs | Global invariants or project knowledge bodies |
| `skills/orchestration/*` | Ordered workflow composition | Detailed implementation of every child Skill |
| `rules/*` | Cross-stage constraints and hard gates | Stage-specific document generation steps |
| `paths/*` | Project context pointers | Large knowledge bodies or copied source docs |
| `templates/*` | Output document skeletons | Workflow control logic |
| `scripts/*` | Deterministic validation and migration helpers | Human-only methodology prose |

## 4. Compatibility Policy

Existing folders remain available during migration:

- `skills/disciplines/*`
- `config/*`
- `templates/project-config/*`

New work should use:

- `rules/*`
- `paths/*`

Compatibility wrappers must not contain divergent rule text. They should point to the canonical rule or path file.

## 5. File Map

Create:

- `rules/stage-gate.md`
- `rules/no-field-guessing.md`
- `rules/no-self-invent.md`
- `rules/ascii-flowchart.md`
- `rules/sql-dialect.md`
- `rules/doc-numbering.md`
- `rules/context-pointer.md`
- `rules/goal-boundary.md`
- `paths/knowledge-path.md`
- `paths/compliance-path.md`
- `paths/tech-stack-path.md`
- `paths/doc-naming-path.md`
- `scripts/rules-path-lint.py`
- `tests/test_rules_path_lint.py`
- `scripts/goal-boundary-check.py`
- `tests/test_goal_boundary_check.py`

Modify:

- `SKILL.md`
- `README.md`
- `SPEC.md`
- `CHANGELOG.md`
- `skills/ask-delivery/SKILL.md`
- `skills/orchestration/analysis-delivery-workflow/SKILL.md`
- `skills/user-invoked/setup-analysis-delivery/SKILL.md`
- `skills/user-invoked/grill-task/SKILL.md`
- `skills/user-invoked/to-brd/SKILL.md`
- `skills/user-invoked/compliance-review/SKILL.md`
- `skills/user-invoked/test-case-design/SKILL.md`
- `skills/user-invoked/to-prd/SKILL.md`
- `skills/user-invoked/dev-design/SKILL.md`
- `skills/user-invoked/qa-audit/SKILL.md`
- `skills/user-invoked/handoff/SKILL.md`
- `templates/TASK_CONFIRM.md`
- `templates/REVIEW_需求确认书.md`
- `templates/PRD.md`
- `templates/TEST_CASE_DESIGN.md`
- `templates/HANDOVER.md`
- `scripts/setup-check.py`
- `scripts/init-project-config.sh`
- `scripts/smoke-test.sh`
- `scripts/discipline-lint.py`

---

## Task 1: Introduce Canonical Rules

**Files:**

- Create: `rules/*.md`
- Modify: `skills/disciplines/*/SKILL.md`

- [ ] Step 1: Copy discipline bodies into canonical rule files.

Mapping:

```text
skills/disciplines/stage-gate/SKILL.md              -> rules/stage-gate.md
skills/disciplines/no-field-guessing/SKILL.md       -> rules/no-field-guessing.md
skills/disciplines/no-self-invent/SKILL.md          -> rules/no-self-invent.md
skills/disciplines/ascii-flowchart/SKILL.md         -> rules/ascii-flowchart.md
skills/disciplines/sql-dialect-discipline/SKILL.md  -> rules/sql-dialect.md
skills/disciplines/doc-numbering/SKILL.md           -> rules/doc-numbering.md
skills/disciplines/context-pointer/SKILL.md         -> rules/context-pointer.md
```

- [ ] Step 2: Remove Skill-only metadata from `rules/*.md`.

Rules must not contain:

- YAML frontmatter delimiters (`---`)
- `name:`, `description:`, `disable-model-invocation:`, `version:`, or `requires:` metadata
- `## Contract` lines that describe Skill routing instead of the rule itself
- `Required disciplines:` declarations

- [ ] Step 3: Replace each old discipline Skill body with a compatibility wrapper:

```markdown
# Compatibility Wrapper

This Skill remains for backward compatibility. The canonical rule now lives at `rules/<rule-name>.md`.

When this Skill is invoked, read `rules/<rule-name>.md` and follow that rule as the source of truth.
```

- [ ] Step 4: Verify rules do not contain Skill frontmatter.

```bash
grep -R "^---$" rules/ && false || true
```

Expected: command exits successfully without reporting YAML delimiter lines.

- [ ] Step 5: Commit.

```bash
git add rules skills/disciplines
git commit -m "refactor: introduce canonical rules layer"
```

---

## Task 2: Normalize Project Context Pointers Into Paths

**Files:**

- Create: `paths/knowledge-path.md`
- Create: `paths/compliance-path.md`
- Create: `paths/tech-stack-path.md`
- Create: `paths/doc-naming-path.md`
- Modify: `templates/project-config/*`
- Modify: `skills/user-invoked/setup-analysis-delivery/SKILL.md`
- Modify: `scripts/setup-check.py`
- Modify: `scripts/init-project-config.sh`
- Modify: `tests/test_setup_check.py`

- [ ] Step 1: Create `paths/knowledge-path.md`.

Required content:

```markdown
# Knowledge Path

## Purpose

Point to project-owned knowledge sources used during analysis and design.

## Required Entries

| Source | Path | When To Read | Owner |
|---|---|---|---|
| Business glossary | `docs/knowledge/business-glossary.md` | Before naming fields, statuses, or user-facing concepts | Product owner |
| Data dictionary | `docs/knowledge/data-dictionary.md` | Before creating or modifying tables, fields, DTOs, or APIs | Tech lead |
| Existing process docs | `docs/knowledge/processes/` | Before writing BRD, PRD, FSD, or workflow diagrams | Business analyst |

## Rules

- Read only entries required by the current stage.
- Do not copy large knowledge bodies into this file.
- If a required source is missing, stop before inventing names or rules.
```

- [ ] Step 2: Create `paths/tech-stack-path.md`.

Required content:

```markdown
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
```

- [ ] Step 3: Create `paths/compliance-path.md`.

Required content:

```markdown
# Compliance Path

## Purpose

Point to project-owned compliance constraints and review evidence.

## Required Entries

| Rule Set | Enabled | Path | When To Read | Owner |
|---|---|---|---|---|
| General compliance | true | `docs/compliance/general.md` | Before compliance review and QA audit | Compliance owner |
| Industry rules | false | `docs/compliance/industry.md` | When the project belongs to a regulated domain | Compliance owner |
| Privacy rules | false | `docs/compliance/privacy.md` | When sensitive data is involved | Security owner |

## Rules

- Read enabled entries only.
- If compliance is disabled, record the explicit reason.
- Do not treat built-in examples as legal advice or authoritative policy.
```

- [ ] Step 4: Create `paths/doc-naming-path.md`.

Required content:

```markdown
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
```

- [ ] Step 5: Convert `templates/project-config/*` into compatibility templates that point to `paths/*`.

Compatibility templates must not contain divergent path content. Each should point to its canonical `paths/<name>.md` file and explain that `templates/project-config/*` remains only for existing setup scripts or older users.

- [ ] Step 6: Update setup Skill so stage 1 creates or validates `paths/*.md`.

Stage 1 should create or validate canonical files under `paths/`:

```text
paths/knowledge-path.md
paths/compliance-path.md
paths/tech-stack-path.md
paths/doc-naming-path.md
```

Treat old project-root files (`knowledge-path.md`, `compliance-path.md`, `tech-stack-path.md`, `doc-naming.md`) as compatibility inputs only.

- [ ] Step 7: Update setup scripts and tests for canonical paths.

Required updates:

- `scripts/setup-check.py` checks canonical `paths/*.md` first.
- `scripts/setup-check.py` may warn about legacy project-root files, but must not require them.
- `scripts/init-project-config.sh` writes `paths/*.md` by default.
- `scripts/init-project-config.sh` keeps a compatibility path or message for `templates/project-config/*`.
- `tests/test_setup_check.py` covers canonical pass, missing canonical files, and legacy compatibility behavior.

- [ ] Step 8: Verify setup checks.

```bash
pytest tests/test_setup_check.py -q
```

- [ ] Step 9: Commit.

```bash
git add paths templates/project-config skills/user-invoked/setup-analysis-delivery/SKILL.md scripts/setup-check.py scripts/init-project-config.sh tests/test_setup_check.py
git commit -m "refactor: normalize project context as paths"
```

---

## Task 3: Add Required Rules And Required Paths Declarations

**Files:**

- Modify: `skills/user-invoked/*/SKILL.md`
- Modify: `skills/orchestration/analysis-delivery-workflow/SKILL.md`

- [ ] Step 1: Add this block under each `## Contract`.

```markdown
- Required rules: `stage-gate`, `no-field-guessing`
- Required paths: `knowledge-path`, `doc-naming-path`
```

- [ ] Step 2: Use this matrix.

| Skill | Required Rules | Required Paths |
|---|---|---|
| `grill-task` | `stage-gate`, `no-field-guessing`, `context-pointer` | `knowledge-path`, `doc-naming-path` |
| `to-brd` | `stage-gate`, `no-field-guessing`, `ascii-flowchart`, `doc-numbering` | `knowledge-path`, `doc-naming-path` |
| `compliance-review` | `stage-gate`, `context-pointer` | `compliance-path`, `doc-naming-path` |
| `test-case-design` | `stage-gate`, `no-field-guessing`, `doc-numbering` | `knowledge-path`, `doc-naming-path` |
| `to-prd` | `stage-gate`, `no-field-guessing`, `doc-numbering` | `knowledge-path`, `doc-naming-path` |
| `dev-design` | `stage-gate`, `no-field-guessing`, `no-self-invent`, `sql-dialect`, `doc-numbering`, `context-pointer` | `knowledge-path`, `tech-stack-path`, `doc-naming-path` |
| `qa-audit` | `stage-gate`, `no-field-guessing`, `no-self-invent`, `sql-dialect`, `doc-numbering` | `knowledge-path`, `tech-stack-path`, `compliance-path`, `doc-naming-path` |
| `handoff` | `stage-gate`, `doc-numbering`, `context-pointer` | `knowledge-path`, `tech-stack-path`, `compliance-path`, `doc-naming-path` |
| `analysis-delivery-workflow` | `stage-gate`, `doc-numbering`, `context-pointer` | `knowledge-path`, `tech-stack-path`, `compliance-path`, `doc-naming-path` |

- [ ] Step 3: Replace duplicate prose lists with:

```markdown
See the `Required rules` and `Required paths` lines in the contract above.
```

- [ ] Step 4: Decide and document frontmatter `requires:` compatibility.

Recommended migration:

- Keep frontmatter `requires:` temporarily for old tooling compatibility.
- Treat `Required rules:` and `Required paths:` as the canonical source of truth.
- If frontmatter `requires:` stays, map old names to canonical rule names in tooling (`sql-dialect-discipline` -> `sql-dialect`).
- Do not add path dependencies to frontmatter `requires:`.

- [ ] Step 5: Verify declarations.

```bash
grep -R "Required rules:" skills/user-invoked/*/SKILL.md skills/orchestration/analysis-delivery-workflow/SKILL.md
grep -R "Required paths:" skills/user-invoked/*/SKILL.md skills/orchestration/analysis-delivery-workflow/SKILL.md
```

- [ ] Step 6: Commit.

```bash
git add skills/user-invoked skills/orchestration/analysis-delivery-workflow/SKILL.md
git commit -m "refactor: declare required rules and paths per stage"
```

---

## Task 4: Thin Root SKILL.md Into Router

**Files:**

- Modify: `SKILL.md`
- Modify: `README.md`
- Modify: `SPEC.md`

- [ ] Step 1: Rewrite root `SKILL.md` to four sections only.

Required structure:

```markdown
# Analysis to Delivery

## Contract

- Inputs: new feature or project delivery request, optional existing project paths
- Outputs: routed action Skill or full 9-stage workflow
- Rules: load only the rules declared by the selected Skill
- Paths: load only the paths declared by the selected Skill
- Next: `/ask-delivery`, `/analysis-delivery-workflow`, or a specific user-invoked Skill

## Quick Start

| Goal | Invoke |
|---|---|
| Choose the right action | `/ask-delivery` |
| Run the full 9-stage workflow | `/analysis-delivery-workflow` |
| Configure a project | `/setup-analysis-delivery` |
| Continue into implementation | `/using-superpowers` |

## Architecture

`skills/` contains actions and orchestration. `rules/` contains cross-stage invariants. `paths/` contains project-owned context pointers. `templates/` contains document skeletons. `scripts/` contains deterministic checks.

## Loading Rule

Load the selected Skill first, then load only the `Required rules` and `Required paths` declared by that Skill. Do not load all rules or all paths by default.
```

- [ ] Step 2: Move long explanation into `README.md` or `SPEC.md`.

- [ ] Step 3: Add compatibility policy to `SPEC.md`.

- [ ] Step 4: Verify root Skill size.

```bash
wc -l SKILL.md
```

Expected: fewer than 120 lines.

- [ ] Step 5: Commit.

```bash
git add SKILL.md README.md SPEC.md
git commit -m "refactor: thin root skill into router"
```

---

## Task 5: Add Rules And Paths Linter

**Files:**

- Create: `scripts/rules-path-lint.py`
- Create: `tests/test_rules_path_lint.py`
- Modify: `scripts/smoke-test.sh`

- [ ] Step 1: Implement `scripts/rules-path-lint.py`.

Required checks:

- All expected `rules/*.md` files from Task 1 exist.
- All expected `paths/*.md` files exist.
- Do not require `goal-boundary` in Task 5; Task 9 adds it and updates the known-rule set.
- Every user-invoked Skill has exactly one `Required rules:` line.
- Every user-invoked Skill has exactly one `Required paths:` line.
- `skills/orchestration/analysis-delivery-workflow/SKILL.md` has exactly one `Required rules:` line.
- `skills/orchestration/analysis-delivery-workflow/SKILL.md` has exactly one `Required paths:` line.
- Every declared rule is known.
- Every declared path is known.
- Legacy rule names are rejected in canonical declarations (`sql-dialect-discipline` must be declared as `sql-dialect`).

- [ ] Step 2: Add tests for pass, unknown rule, unknown path, missing declaration, duplicate declaration, and legacy SQL rule name.

- [ ] Step 3: Add the linter to `scripts/smoke-test.sh`.

```bash
python3 scripts/rules-path-lint.py .
```

- [ ] Step 4: Run focused verification.

```bash
pytest tests/test_rules_path_lint.py -q
python3 scripts/rules-path-lint.py .
```

- [ ] Step 5: Commit.

```bash
git add scripts/rules-path-lint.py tests/test_rules_path_lint.py scripts/smoke-test.sh
git commit -m "test: lint rules and paths declarations"
```

---

## Task 6: Update Documentation And Existing Lints

**Files:**

- Modify: `scripts/discipline-lint.py`
- Modify: `README.md`
- Modify: `SPEC.md`
- Modify: `CHANGELOG.md`

- [ ] Step 1: Rename architecture language in docs.

Use:

```text
rule
path
```

Instead of:

```text
discipline
config path
```

Exception: compatibility notes may still mention old names.

- [ ] Step 2: Keep `discipline-lint.py` working for compatibility wrappers.

`discipline-lint.py` becomes a legacy compatibility lint only:

- It should verify `skills/disciplines/*/SKILL.md` wrappers still exist.
- It should verify wrapper text points to the matching canonical `rules/*.md`.
- It should not require canonical stage Skills to use `Required disciplines:`.
- It should not be the source of truth for stage dependency declarations after Task 5.

- [ ] Step 3: Add changelog entry.

```markdown
## Unreleased - Rules and Paths Refactor

- Added canonical `rules/` layer for cross-stage invariants.
- Added canonical `paths/` layer for project-owned context pointers.
- Added per-stage `Required rules` and `Required paths` declarations.
- Added `scripts/rules-path-lint.py` to prevent undeclared or unknown context dependencies.
- Kept `skills/disciplines/*` and `templates/project-config/*` as compatibility wrappers during migration.
```

- [ ] Step 4: Verify old references.

```bash
grep -R "disciplines/" README.md SPEC.md SKILL.md skills/user-invoked skills/orchestration | head -40
python3 scripts/rules-path-lint.py .
```

Expected: remaining `disciplines/` references are compatibility notes only.

- [ ] Step 5: Commit.

```bash
git add scripts/discipline-lint.py README.md SPEC.md CHANGELOG.md
git commit -m "docs: document rules and paths architecture"
```

---

## Task 7: Migration Compatibility Check

**Files:**

- Modify: tests only if existing assertions depend on old names.

- [ ] Step 1: Run full tests.

```bash
pytest -q
```

- [ ] Step 2: Run smoke test.

```bash
bash scripts/smoke-test.sh
```

- [ ] Step 3: Inspect compatibility references.

```bash
grep -R "skills/disciplines" examples templates README.md SPEC.md SKILL.md | head -80
grep -R "templates/project-config" examples templates README.md SPEC.md SKILL.md | head -80
```

Expected: references either point to compatibility behavior or are migrated to `rules/` and `paths/`.

- [ ] Step 4: Commit final fixes.

```bash
git status --short
git add <only migration files changed by this plan>
git commit -m "chore: complete rules and paths migration checks"
```

Do not use `git add .` if unrelated local changes are present.

---


## Task 9: Add Goal Boundary Control

**Files:**

- Create: `rules/goal-boundary.md`
- Create: `scripts/goal-boundary-check.py`
- Create: `tests/test_goal_boundary_check.py`
- Modify: `templates/TASK_CONFIRM.md`
- Modify: `templates/REVIEW_需求确认书.md`
- Modify: `templates/PRD.md`
- Modify: `templates/TEST_CASE_DESIGN.md`
- Modify: `templates/HANDOVER.md`
- Modify: `skills/user-invoked/grill-task/SKILL.md`
- Modify: `skills/user-invoked/to-brd/SKILL.md`
- Modify: `skills/user-invoked/test-case-design/SKILL.md`
- Modify: `skills/user-invoked/to-prd/SKILL.md`
- Modify: `skills/user-invoked/dev-design/SKILL.md`
- Modify: `skills/user-invoked/qa-audit/SKILL.md`
- Modify: `skills/user-invoked/handoff/SKILL.md`
- Modify: `skills/orchestration/analysis-delivery-workflow/SKILL.md`
- Modify: `scripts/rules-path-lint.py`
- Modify: `scripts/smoke-test.sh`
- Modify: `README.md`
- Modify: `SPEC.md`
- Modify: `CHANGELOG.md`

**Purpose:** Make delivery goals, completion boundaries, and staged delivery explicit and machine-checkable. The workflow must not treat a requirement as ready for design or implementation until it answers: what counts as complete, whether phased delivery is allowed, and which acceptance criteria belong to each phase.

- [ ] Step 1: Create `rules/goal-boundary.md`.

Required content:

```markdown
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
```

- [ ] Step 2: Update `templates/TASK_CONFIRM.md` to capture goal boundary decisions.

Replace or extend `## 二、需求目标` with:

```markdown
## 二、需求目标与完成边界

| 问题 | 你的回答 |
|---|---|
| 最终业务目标是什么？ | [待填写] |
| 本次交付做到什么程度才算完成？ | [待填写] |
| 可量化成功指标是什么？ | [待填写] |
| 本次明确不解决哪些问题？ | [待填写] |
| 是否允许分阶段交付？ | 是 / 否 |

## 三、阶段目标

| 阶段 | 目标 | 包含范围 | 不包含范围 | 交付物 | 验收条件 | 是否阻塞上线 |
|---|---|---|---|---|---|---|
| MVP / Phase 1 | [待填写] | [待填写] | [待填写] | [待填写] | [待填写] | 是 / 否 |
| Phase 2 | [待填写] | [待填写] | [待填写] | [待填写] | [待填写] | 是 / 否 |
| Later | [待填写] | [待填写] | [待填写] | [待填写] | [待填写] | 是 / 否 |
```

Keep the existing functional scope section, but renumber later sections if needed.

- [ ] Step 3: Update review, PRD, test case, and handoff templates.

Required additions:

- `templates/REVIEW_需求确认书.md`: add a goal boundary confirmation section and a phase goal confirmation section.
- `templates/PRD.md`: add `## 九、目标边界与分期` or an equivalent section linking product requirements to phases.
- `templates/TEST_CASE_DESIGN.md`: add `关联阶段` and `关联验收条件` columns to test cases.
- `templates/HANDOVER.md`: add achieved phases, deferred phases, remaining goal gaps, and receiver acceptance checklist.

- [ ] Step 4: Update stage Skill contracts and required rules.

Add `goal-boundary` to `Required rules:` for:

```text
grill-task
to-brd
test-case-design
to-prd
dev-design
qa-audit
handoff
analysis-delivery-workflow
```

Do not add `goal-boundary` to stages that only initialize project paths unless they inspect or validate requirement goals.

- [ ] Step 5: Implement `scripts/goal-boundary-check.py`.

Required checks:

- `TASK_CONFIRM_*.md` contains a goal boundary section.
- Current delivery completion definition is non-empty.
- Explicit non-goals are non-empty.
- Staged delivery decision is present (`是` or `否`).
- If staged delivery is `是`, at least one MVP or Phase 1 row exists.
- Every active phase has a goal and acceptance criteria.
- PRD acceptance criteria reference a phase.
- Test cases reference a phase or acceptance criterion.

The script may start with template-level and document-level checks. Deep cross-document consistency can be added incrementally.

- [ ] Step 6: Add tests for goal boundary checks.

Required test cases:

- Pass: single-phase requirement with completion definition and acceptance criteria.
- Pass: staged requirement with MVP and Phase 2.
- Fail: missing completion definition.
- Fail: staged delivery enabled but no MVP or Phase 1.
- Fail: PRD acceptance criteria without phase mapping.
- Fail: test cases without phase or acceptance mapping.

- [ ] Step 7: Add goal-boundary to linters and smoke test.

Required updates:

- `scripts/rules-path-lint.py` recognizes `goal-boundary` as a known rule.
- `scripts/smoke-test.sh` runs `python3 scripts/goal-boundary-check.py --self-test`.
- Existing doc validation recognizes the new or renumbered sections.

- [ ] Step 8: Update docs.

Required updates:

- README explains that requirements are not ready for design until goal boundary decisions are complete.
- SPEC defines goal boundary as a cross-stage rule.
- CHANGELOG records the new goal boundary control.

- [ ] Step 9: Run focused verification.

```bash
python3 scripts/rules-path-lint.py .
python3 scripts/goal-boundary-check.py --self-test
pytest tests/test_goal_boundary_check.py -q
bash scripts/smoke-test.sh
```

- [ ] Step 10: Commit.

```bash
git add rules/goal-boundary.md scripts/goal-boundary-check.py tests/test_goal_boundary_check.py templates/TASK_CONFIRM.md templates/REVIEW_需求确认书.md templates/PRD.md templates/TEST_CASE_DESIGN.md templates/HANDOVER.md skills/user-invoked skills/orchestration/analysis-delivery-workflow/SKILL.md scripts/rules-path-lint.py scripts/smoke-test.sh README.md SPEC.md CHANGELOG.md
git commit -m "feat: add goal boundary control"
```

---

## Task 10: Final Verification

**Files:**

- Verify all changed files.

- [ ] Step 1: Review diff.

```bash
git diff --stat
git diff -- SKILL.md README.md SPEC.md CHANGELOG.md scripts/rules-path-lint.py tests/test_rules_path_lint.py scripts/goal-boundary-check.py tests/test_goal_boundary_check.py
```

- [ ] Step 2: Run final checks.

```bash
python3 scripts/rules-path-lint.py .
python3 scripts/goal-boundary-check.py --self-test
python3 scripts/discipline-lint.py skills/
pytest -q
bash scripts/smoke-test.sh
```

- [ ] Step 3: Confirm acceptance criteria.

```text
Root SKILL.md is under 120 lines.
Every stage Skill has one Required rules line.
Every stage Skill has one Required paths line.
The analysis-delivery workflow Skill has one Required rules line.
The analysis-delivery workflow Skill has one Required paths line.
Every declared rule maps to rules/*.md.
Every declared path maps to paths/*.md.
Compatibility wrappers remain available.
Setup tooling creates or validates canonical paths/*.md files.
All tests pass.
Smoke test passes.
Goal boundary control is declared by relevant stages and enforced before design handoff.
README and SPEC explain the loading model.
```

- [ ] Step 4: Commit verification notes if docs changed.

```bash
git add README.md CHANGELOG.md
git commit -m "docs: add rules and paths migration notes"
```

---

## Rollback Plan

If the migration breaks existing users, keep `rules/` and `paths/` files but restore previous Skill bodies from Git.

Recommended rollback for a local branch:

```bash
git log --oneline --max-count=10
git revert <first_bad_commit>^..<last_bad_commit>
```

Do not delete `rules/` or `paths/` immediately. They are additive and remain useful even if the root router rewrite is delayed.

## Acceptance Criteria

- Root `SKILL.md` acts only as router and navigation.
- Root `SKILL.md` is fewer than 120 lines.
- Every user-invoked stage Skill has exactly one `Required rules` line.
- Every user-invoked stage Skill has exactly one `Required paths` line.
- Every declared rule maps to a file in `rules/`.
- Every declared path maps to a file in `paths/`.
- `skills/disciplines/*` remain available as compatibility wrappers.
- `templates/project-config/*` remain available as compatibility templates.
- `python3 scripts/rules-path-lint.py .` passes.
- `python3 scripts/goal-boundary-check.py --self-test` passes.
- `pytest -q` passes.
- `bash scripts/smoke-test.sh` passes.
- README and SPEC explain: selected Skill first, declared rules and paths second, no bulk loading by default.
- Goal boundaries define what counts as complete, whether staged delivery is allowed, and which phase each acceptance criterion belongs to.

## Self-Review

- Coverage: this plan covers thin Skills, canonical rules, canonical paths, goal boundaries, declarations, lints, docs, compatibility, tests, rollback, and acceptance criteria.
- Placeholder scan: this document contains no unresolved `TBD` or `TODO` markers.
- Naming consistency: new canonical rule is `sql-dialect`; old compatibility Skill remains `sql-dialect-discipline`.
- Naming consistency: new canonical path is `doc-naming-path`; old compatibility template may remain `doc-naming.md`.
