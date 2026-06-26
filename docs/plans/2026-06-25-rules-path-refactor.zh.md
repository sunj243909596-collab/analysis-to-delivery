# Rules 与 Paths 重构实施计划

> **给 agentic workers：** 必须使用子技能：用 `superpowers:subagent-driven-development` 或 `superpowers:executing-plans` 按任务逐项实施本计划。步骤使用 checkbox 语法跟踪进度。

**目标：** 将 `analysis-to-delivery` 从 Skill 偏重的工作流，重构为一个薄 Skill 路由器，并建立明确的 `rules/` 与 `paths/` 边界。

**架构：** 保留 Skills 作为动作与编排入口。将跨阶段不变量从 `skills/disciplines/` 移到 `rules/`。将项目级配置指针规范化到 `paths/`。每个阶段 Skill 声明自己需要的 rules 与 paths，并由验证脚本强制检查这些声明。

**技术栈：** Markdown Skills、Python 验证脚本、Bash smoke tests、现有 `pytest` 测试套件、现有 templates 与 examples。

---

## 1. 问题陈述

当前结构过度依赖 Skills。这带来三个问题：

- 上下文膨胀：只需要少量约束时，也会加载很大的 Skill 内容。
- 边界模糊：路由、工作流步骤、项目配置、全局规则混在一起。
- 验证薄弱：阶段 Skills 在 prose 中提到所需 disciplines，但没有机器可检查的声明。

目标模型拆分责任：

```text
Skill = action or workflow entrypoint
rules = cross-stage invariant constraints
paths = project-owned context pointers
```

## 2. 目标目录模型

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

## 3. 责任边界

| Layer | Owns | Does Not Own |
|---|---|---|
| 根 `SKILL.md` | 触发、路由、快速开始、最小架构图 | 完整规则、阶段流程、大型示例 |
| `skills/user-invoked/*` | 一个用户可见动作及其输出 | 全局不变量或项目知识正文 |
| `skills/orchestration/*` | 有序工作流组合 | 每个子 Skill 的详细实现 |
| `rules/*` | 跨阶段约束与硬门控 | 阶段特定文档生成步骤 |
| `paths/*` | 项目上下文指针 | 大型知识正文或复制的源文档 |
| `templates/*` | 输出文档骨架 | 工作流控制逻辑 |
| `scripts/*` | 确定性验证与迁移辅助 | 仅供人读的方法论 prose |

## 4. 兼容策略

迁移期间保留既有目录：

- `skills/disciplines/*`
- `config/*`
- `templates/project-config/*`

新工作应使用：

- `rules/*`
- `paths/*`

兼容 wrapper 不能包含发散的规则文本。它们应该指向 canonical rule 或 path 文件。

## 5. 文件地图

创建：

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

修改：

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

## Task 1：引入 Canonical Rules

**文件：**

- 创建：`rules/*.md`
- 修改：`skills/disciplines/*/SKILL.md`

- [ ] Step 1：将 discipline 正文复制到 canonical rule 文件。

映射：

```text
skills/disciplines/stage-gate/SKILL.md              -> rules/stage-gate.md
skills/disciplines/no-field-guessing/SKILL.md       -> rules/no-field-guessing.md
skills/disciplines/no-self-invent/SKILL.md          -> rules/no-self-invent.md
skills/disciplines/ascii-flowchart/SKILL.md         -> rules/ascii-flowchart.md
skills/disciplines/sql-dialect-discipline/SKILL.md  -> rules/sql-dialect.md
skills/disciplines/doc-numbering/SKILL.md           -> rules/doc-numbering.md
skills/disciplines/context-pointer/SKILL.md         -> rules/context-pointer.md
```

- [ ] Step 2：从 `rules/*.md` 中移除仅属于 Skill 的元数据。

Rules 不得包含：

- YAML frontmatter 分隔符（`---`）
- `name:`、`description:`、`disable-model-invocation:`、`version:` 或 `requires:` 元数据
- 描述 Skill 路由而不是 rule 本身的 `## Contract` 行
- `Required disciplines:` 声明

- [ ] Step 3：将每个旧 discipline Skill 正文替换为兼容 wrapper：

```markdown
# Compatibility Wrapper

This Skill remains for backward compatibility. The canonical rule now lives at `rules/<rule-name>.md`.

When this Skill is invoked, read `rules/<rule-name>.md` and follow that rule as the source of truth.
```

- [ ] Step 4：验证 rules 不包含 Skill frontmatter。

```bash
grep -R "^---$" rules/ && false || true
```

预期：命令成功退出，且不报告 YAML delimiter 行。

- [ ] Step 5：提交。

```bash
git add rules skills/disciplines
git commit -m "refactor: introduce canonical rules layer"
```

---

## Task 2：将项目上下文指针规范化为 Paths

**文件：**

- 创建：`paths/knowledge-path.md`
- 创建：`paths/compliance-path.md`
- 创建：`paths/tech-stack-path.md`
- 创建：`paths/doc-naming-path.md`
- 修改：`templates/project-config/*`
- 修改：`skills/user-invoked/setup-analysis-delivery/SKILL.md`
- 修改：`scripts/setup-check.py`
- 修改：`scripts/init-project-config.sh`
- 修改：`tests/test_setup_check.py`

- [ ] Step 1：创建 `paths/knowledge-path.md`。

必需内容：

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

- [ ] Step 2：创建 `paths/tech-stack-path.md`。

必需内容：

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

- [ ] Step 3：创建 `paths/compliance-path.md`。

必需内容：

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

- [ ] Step 4：创建 `paths/doc-naming-path.md`。

必需内容：

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

- [ ] Step 5：将 `templates/project-config/*` 转换为指向 `paths/*` 的兼容模板。

兼容模板不能包含发散的 path 内容。每个模板都应指向其 canonical `paths/<name>.md` 文件，并说明 `templates/project-config/*` 仅为既有 setup scripts 或旧用户保留。

- [ ] Step 6：更新 setup Skill，使阶段 1 创建或验证 `paths/*.md`。

阶段 1 应在 `paths/` 下创建或验证 canonical 文件：

```text
paths/knowledge-path.md
paths/compliance-path.md
paths/tech-stack-path.md
paths/doc-naming-path.md
```

将旧 project-root 文件（`knowledge-path.md`、`compliance-path.md`、`tech-stack-path.md`、`doc-naming.md`）仅视为兼容输入。

- [ ] Step 7：更新 setup scripts 与 tests，使其使用 canonical paths。

必需更新：

- `scripts/setup-check.py` 优先检查 canonical `paths/*.md`。
- `scripts/setup-check.py` 可以对 legacy project-root 文件给出 warning，但不能要求它们存在。
- `scripts/init-project-config.sh` 默认写入 `paths/*.md`。
- `scripts/init-project-config.sh` 为 `templates/project-config/*` 保留兼容路径或提示信息。
- `tests/test_setup_check.py` 覆盖 canonical pass、canonical 文件缺失，以及 legacy 兼容行为。

- [ ] Step 8：验证 setup checks。

```bash
pytest tests/test_setup_check.py -q
```

- [ ] Step 9：提交。

```bash
git add paths templates/project-config skills/user-invoked/setup-analysis-delivery/SKILL.md scripts/setup-check.py scripts/init-project-config.sh tests/test_setup_check.py
git commit -m "refactor: normalize project context as paths"
```

---

## Task 3：添加 Required Rules 与 Required Paths 声明

**文件：**

- 修改：`skills/user-invoked/*/SKILL.md`
- 修改：`skills/orchestration/analysis-delivery-workflow/SKILL.md`

- [ ] Step 1：在每个 `## Contract` 下添加这个块。

```markdown
- Required rules: `stage-gate`, `no-field-guessing`
- Required paths: `knowledge-path`, `doc-naming-path`
```

- [ ] Step 2：使用这个矩阵。

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

- [ ] Step 3：将重复的 prose 列表替换为：

```markdown
See the `Required rules` and `Required paths` lines in the contract above.
```

- [ ] Step 4：决定并记录 frontmatter `requires:` 的兼容策略。

推荐迁移方式：

- 暂时保留 frontmatter `requires:`，用于兼容旧工具。
- 将 `Required rules:` 与 `Required paths:` 作为 canonical source of truth。
- 如果保留 frontmatter `requires:`，在 tooling 中将旧名称映射到 canonical rule 名称（`sql-dialect-discipline` -> `sql-dialect`）。
- 不要将 path 依赖加入 frontmatter `requires:`。

- [ ] Step 5：验证声明。

```bash
grep -R "Required rules:" skills/user-invoked/*/SKILL.md skills/orchestration/analysis-delivery-workflow/SKILL.md
grep -R "Required paths:" skills/user-invoked/*/SKILL.md skills/orchestration/analysis-delivery-workflow/SKILL.md
```

- [ ] Step 6：提交。

```bash
git add skills/user-invoked skills/orchestration/analysis-delivery-workflow/SKILL.md
git commit -m "refactor: declare required rules and paths per stage"
```

---

## Task 4：将根 SKILL.md 精简为 Router

**文件：**

- 修改：`SKILL.md`
- 修改：`README.md`
- 修改：`SPEC.md`

- [ ] Step 1：将根 `SKILL.md` 重写为仅包含四个 section。

必需结构：

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

- [ ] Step 2：将长解释移动到 `README.md` 或 `SPEC.md`。

- [ ] Step 3：将兼容策略加入 `SPEC.md`。

- [ ] Step 4：验证根 Skill 大小。

```bash
wc -l SKILL.md
```

预期：少于 120 行。

- [ ] Step 5：提交。

```bash
git add SKILL.md README.md SPEC.md
git commit -m "refactor: thin root skill into router"
```

---

## Task 5：添加 Rules 与 Paths Linter

**文件：**

- 创建：`scripts/rules-path-lint.py`
- 创建：`tests/test_rules_path_lint.py`
- 修改：`scripts/smoke-test.sh`

- [ ] Step 1：实现 `scripts/rules-path-lint.py`。

必需检查：

- Task 1 中预期的 `rules/*.md` 文件都存在。
- 所有预期的 `paths/*.md` 文件都存在。
- Task 5 不要求 `goal-boundary`；Task 9 会添加它并更新 known-rule set。
- 每个 user-invoked Skill 恰好有一行 `Required rules:`。
- 每个 user-invoked Skill 恰好有一行 `Required paths:`。
- `skills/orchestration/analysis-delivery-workflow/SKILL.md` 恰好有一行 `Required rules:`。
- `skills/orchestration/analysis-delivery-workflow/SKILL.md` 恰好有一行 `Required paths:`。
- 每个声明的 rule 都是已知 rule。
- 每个声明的 path 都是已知 path。
- canonical declarations 中拒绝 legacy rule 名称（`sql-dialect-discipline` 必须声明为 `sql-dialect`）。

- [ ] Step 2：为 pass、unknown rule、unknown path、missing declaration、duplicate declaration、legacy SQL rule name 添加测试。

- [ ] Step 3：将 linter 加入 `scripts/smoke-test.sh`。

```bash
python3 scripts/rules-path-lint.py .
```

- [ ] Step 4：运行聚焦验证。

```bash
pytest tests/test_rules_path_lint.py -q
python3 scripts/rules-path-lint.py .
```

- [ ] Step 5：提交。

```bash
git add scripts/rules-path-lint.py tests/test_rules_path_lint.py scripts/smoke-test.sh
git commit -m "test: lint rules and paths declarations"
```

---

## Task 6：更新文档与现有 Lints

**文件：**

- 修改：`scripts/discipline-lint.py`
- 修改：`README.md`
- 修改：`SPEC.md`
- 修改：`CHANGELOG.md`

- [ ] Step 1：在文档中重命名架构术语。

使用：

```text
rule
path
```

替代：

```text
discipline
config path
```

例外：兼容说明中仍可提及旧名称。

- [ ] Step 2：保持 `discipline-lint.py` 可用于兼容 wrappers。

`discipline-lint.py` 降级为 legacy compatibility lint：

- 它应验证 `skills/disciplines/*/SKILL.md` wrappers 仍然存在。
- 它应验证 wrapper 文本指向匹配的 canonical `rules/*.md`。
- 它不应要求 canonical stage Skills 使用 `Required disciplines:`。
- Task 5 之后，它不再是阶段依赖声明的 source of truth。

- [ ] Step 3：添加 changelog 条目。

```markdown
## Unreleased - Rules and Paths Refactor

- Added canonical `rules/` layer for cross-stage invariants.
- Added canonical `paths/` layer for project-owned context pointers.
- Added per-stage `Required rules` and `Required paths` declarations.
- Added `scripts/rules-path-lint.py` to prevent undeclared or unknown context dependencies.
- Kept `skills/disciplines/*` and `templates/project-config/*` as compatibility wrappers during migration.
```

- [ ] Step 4：验证旧引用。

```bash
grep -R "disciplines/" README.md SPEC.md SKILL.md skills/user-invoked skills/orchestration | head -40
python3 scripts/rules-path-lint.py .
```

预期：剩余的 `disciplines/` 引用仅为兼容说明。

- [ ] Step 5：提交。

```bash
git add scripts/discipline-lint.py README.md SPEC.md CHANGELOG.md
git commit -m "docs: document rules and paths architecture"
```

---

## Task 7：迁移兼容性检查

**文件：**

- 仅当现有 assertions 依赖旧名称时，才修改 tests。

- [ ] Step 1：运行完整测试。

```bash
pytest -q
```

- [ ] Step 2：运行 smoke test。

```bash
bash scripts/smoke-test.sh
```

- [ ] Step 3：检查兼容引用。

```bash
grep -R "skills/disciplines" examples templates README.md SPEC.md SKILL.md | head -80
grep -R "templates/project-config" examples templates README.md SPEC.md SKILL.md | head -80
```

预期：引用要么指向兼容行为，要么已迁移到 `rules/` 与 `paths/`。

- [ ] Step 4：提交最终修复。

```bash
git status --short
git add <only migration files changed by this plan>
git commit -m "chore: complete rules and paths migration checks"
```

如果存在无关本地修改，不要使用 `git add .`。

---

## Task 9：添加目标边界管控

**文件：**

- 创建：`rules/goal-boundary.md`
- 创建：`scripts/goal-boundary-check.py`
- 创建：`tests/test_goal_boundary_check.py`
- 修改：`templates/TASK_CONFIRM.md`
- 修改：`templates/REVIEW_需求确认书.md`
- 修改：`templates/PRD.md`
- 修改：`templates/TEST_CASE_DESIGN.md`
- 修改：`templates/HANDOVER.md`
- 修改：`skills/user-invoked/grill-task/SKILL.md`
- 修改：`skills/user-invoked/to-brd/SKILL.md`
- 修改：`skills/user-invoked/test-case-design/SKILL.md`
- 修改：`skills/user-invoked/to-prd/SKILL.md`
- 修改：`skills/user-invoked/dev-design/SKILL.md`
- 修改：`skills/user-invoked/qa-audit/SKILL.md`
- 修改：`skills/user-invoked/handoff/SKILL.md`
- 修改：`skills/orchestration/analysis-delivery-workflow/SKILL.md`
- 修改：`scripts/rules-path-lint.py`
- 修改：`scripts/smoke-test.sh`
- 修改：`README.md`
- 修改：`SPEC.md`
- 修改：`CHANGELOG.md`

**目的：** 将交付目标、完成边界、分阶段交付显式化并可机器检查。工作流不能只因为“需求已确认”就进入设计或实现，必须先回答：做到什么程度才算完成、是否允许分阶段交付、每条验收标准属于哪个阶段。

- [ ] Step 1：创建 `rules/goal-boundary.md`。

必需内容：

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

- [ ] Step 2：更新 `templates/TASK_CONFIRM.md`，捕获目标边界决策。

将 `## 二、需求目标` 替换或扩展为：

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

保留原有功能范围章节；如有需要，顺延后续章节编号。

- [ ] Step 3：更新需求确认书、PRD、测试用例与交接模板。

必需新增：

- `templates/REVIEW_需求确认书.md`：新增目标边界确认章节和阶段目标确认章节。
- `templates/PRD.md`：新增 `## 九、目标边界与分期` 或等价章节，将产品需求映射到阶段。
- `templates/TEST_CASE_DESIGN.md`：测试用例增加 `关联阶段` 与 `关联验收条件` 列。
- `templates/HANDOVER.md`：新增已达成阶段、延期阶段、剩余目标差距、接收方验收 checklist。

- [ ] Step 4：更新阶段 Skill contracts 与 required rules。

为以下 Skill 的 `Required rules:` 增加 `goal-boundary`：

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

除非 setup 阶段会检查或验证需求目标，否则不要给只初始化项目 paths 的阶段增加 `goal-boundary`。

- [ ] Step 5：实现 `scripts/goal-boundary-check.py`。

必需检查：

- `TASK_CONFIRM_*.md` 包含目标边界章节。
- 当前交付完成定义非空。
- 明确不做项非空。
- 存在分阶段交付决策（`是` 或 `否`）。
- 如果分阶段交付为 `是`，至少存在一个 MVP 或 Phase 1 行。
- 每个 active phase 都有目标和验收条件。
- PRD 验收标准引用阶段。
- 测试用例引用阶段或验收条件。

脚本可以先从模板级和单文档级检查开始。跨文档深度一致性可以后续增量补强。

- [ ] Step 6：为目标边界检查添加测试。

必需测试用例：

- 通过：单阶段需求，包含完成定义和验收条件。
- 通过：分阶段需求，包含 MVP 和 Phase 2。
- 失败：缺少完成定义。
- 失败：启用分阶段交付但没有 MVP 或 Phase 1。
- 失败：PRD 验收标准没有阶段映射。
- 失败：测试用例没有阶段或验收映射。

- [ ] Step 7：将 goal-boundary 加入 linters 与 smoke test。

必需更新：

- `scripts/rules-path-lint.py` 将 `goal-boundary` 识别为已知 rule。
- `scripts/smoke-test.sh` 运行 `python3 scripts/goal-boundary-check.py --self-test`。
- 现有 doc validation 能识别新增或重新编号的章节。

- [ ] Step 8：更新文档。

必需更新：

- README 说明：目标边界决策完整之前，需求不能进入设计。
- SPEC 将 goal boundary 定义为跨阶段 rule。
- CHANGELOG 记录新的目标边界管控。

- [ ] Step 9：运行聚焦验证。

```bash
python3 scripts/rules-path-lint.py .
python3 scripts/goal-boundary-check.py --self-test
pytest tests/test_goal_boundary_check.py -q
bash scripts/smoke-test.sh
```

- [ ] Step 10：提交。

```bash
git add rules/goal-boundary.md scripts/goal-boundary-check.py tests/test_goal_boundary_check.py templates/TASK_CONFIRM.md templates/REVIEW_需求确认书.md templates/PRD.md templates/TEST_CASE_DESIGN.md templates/HANDOVER.md skills/user-invoked skills/orchestration/analysis-delivery-workflow/SKILL.md scripts/rules-path-lint.py scripts/smoke-test.sh README.md SPEC.md CHANGELOG.md
git commit -m "feat: add goal boundary control"
```

---

## Task 10：最终验证

**文件：**

- 验证所有已修改文件。

- [ ] Step 1：检查 diff。

```bash
git diff --stat
git diff -- SKILL.md README.md SPEC.md CHANGELOG.md scripts/rules-path-lint.py tests/test_rules_path_lint.py scripts/goal-boundary-check.py tests/test_goal_boundary_check.py
```

- [ ] Step 2：运行最终检查。

```bash
python3 scripts/rules-path-lint.py .
python3 scripts/goal-boundary-check.py --self-test
python3 scripts/discipline-lint.py skills/
pytest -q
bash scripts/smoke-test.sh
```

- [ ] Step 3：确认验收标准。

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

- [ ] Step 4：如果文档有变化，提交验证说明。

```bash
git add README.md CHANGELOG.md
git commit -m "docs: add rules and paths migration notes"
```

---

## 回滚计划

如果迁移破坏了现有用户，保留 `rules/` 与 `paths/` 文件，但从 Git 恢复之前的 Skill 正文。

本地分支推荐回滚方式：

```bash
git log --oneline --max-count=10
git revert <first_bad_commit>^..<last_bad_commit>
```

不要立即删除 `rules/` 或 `paths/`。它们是 additive 的，即使 root router rewrite 被延迟，也仍然有用。

## 验收标准

- 根 `SKILL.md` 仅作为 router 与导航。
- 根 `SKILL.md` 少于 120 行。
- 每个 user-invoked 阶段 Skill 恰好有一行 `Required rules`。
- 每个 user-invoked 阶段 Skill 恰好有一行 `Required paths`。
- 每个声明的 rule 都映射到 `rules/` 中的文件。
- 每个声明的 path 都映射到 `paths/` 中的文件。
- `skills/disciplines/*` 仍作为兼容 wrappers 可用。
- `templates/project-config/*` 仍作为兼容 templates 可用。
- `python3 scripts/rules-path-lint.py .` 通过。
- `python3 scripts/goal-boundary-check.py --self-test` 通过。
- `pytest -q` 通过。
- `bash scripts/smoke-test.sh` 通过。
- README 与 SPEC 解释加载模型：先加载 selected Skill，再加载 declared rules 与 paths，默认不 bulk loading。
- 目标边界定义什么算完成、是否允许分阶段交付，以及每条验收标准属于哪个阶段。

## 自审

- 覆盖范围：本计划覆盖 thin Skills、canonical rules、canonical paths、goal boundaries、declarations、lints、docs、compatibility、tests、rollback 与 acceptance criteria。
- 占位符扫描：本文档不含未解决的 `TBD` 或 `TODO` 标记。
- 命名一致性：新的 canonical rule 是 `sql-dialect`；旧兼容 Skill 仍为 `sql-dialect-discipline`。
- 命名一致性：新的 canonical path 是 `doc-naming-path`；旧兼容 template 可保留 `doc-naming.md`。
