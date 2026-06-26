---
name: analysis-to-delivery
description: 通用需求分析到开发设计工作流 — thin Skill router,加载规则与路径按声明。Use when starting any new feature requiring structured analysis-to-delivery workflow.
category: software-development
version: 3.2.0-dev
created: 2026-06-22
updated: "2026-06-26: v3.2.0-dev rules-and-paths refactor — thin root router, rules/ + paths/ layers"
---

# Analysis to Delivery

> 26 个独立 skill 自由组合 — 走流程用 orchestration,做单件事用 action,纪律由 rules 自动加载。

## Contract

- Inputs: 新功能 / 项目交付请求,领域,技术栈,可选的 `paths/*.md` 配置
- Outputs: 推荐路由的 user-invoked skill,或走完整 9 阶段工作流
- Gates: 走流程用 `/analysis-delivery-workflow`;每阶段由子 skill 的 stage-gate 把关
- Required rules: 子 skill 各自声明(`context-pointer` / `stage-gate` / `doc-numbering` / `no-field-guessing` 等)
- Required paths: 子 skill 各自声明(`knowledge-path` / `tech-stack-path` / `compliance-path` / `doc-naming-path`)
- Next: `/ask-delivery`、`/analysis-delivery-workflow`,或直接调某个 user-invoked skill

## 快速开始

- **不知道用哪个?** → `/ask-delivery`(router)
- **走完整 9 阶段** → `/analysis-delivery-workflow`
- **进入开发实施** → `/using-superpowers`(router)

## 快速通道

跳过 router,直接按目标选:

| 你想要 | 直接调 |
|---|---|
| 配置项目(知识库/技术栈/合规/命名) | `/setup-analysis-delivery` |
| 跑 5 项门控全套 | `bash scripts/smoke-test.sh` |
| 看项目走到哪个阶段 | `python3 scripts/analysis-state.py status` |
| 把 ASCII 流程图转成 Mermaid | `python3 scripts/flow-to-mermaid.py file.txt` |
| 校验所有 skill 是否合规 | `python3 scripts/discipline-lint.py skills/` |
| 校验 Required rules / paths 声明 | `python3 scripts/rules-path-lint.py <repo>` |
| 校验目标边界与分期 | `python3 scripts/goal-boundary-check.py <project_dir>` |

## 逆向使用

不是从需求 → 设计,而是**已有产物需要后向追溯 / 修复**:

| 已有产物 | 逆向动作 |
|---|---|
| 有 `01-BRD.md`,但不确定字段是否对 | `python3 scripts/field-alignment-check.py <project>` |
| 有 `05-PRD.md`,但发现 PRD 与 BRD 冲突 | 回到 `/grill-task` 重对齐 |
| 有 `06-开发设计.md`,但代码已写完 | 直接进 `/qa-audit` 找设计偏差 |
| 有 `09-QA审计报告.md` P0 列表 | 逐项修复后重跑 `python3 scripts/full-qa-audit.py` |
| 状态文件还在(`.analysis-delivery-state.json`) | `python3 scripts/analysis-state.py status` 看中断在哪个阶段 |

## 度量

`scripts/analysis-state.py metrics [--json]` 输出 5 项指标(项目级,持久化到 `.analysis-delivery-state.json`):

| # | 指标 | 含义 |
|---|---|---|
| 1 | 总 gate 调用次数 | 整套流程跑了多少次自动化门控 |
| 2 | 总签字次数 | 用户白名单话术累计签字次数 |
| 3 | gate 拦截次数 | 每个 gate 脚本失败的次数(按脚本名分) |
| 4 | 各阶段重试次数 | 哪些阶段需要反复回去修 |
| 5 | 阶段用时(分钟) | 已签字阶段的耗时(开始 → 签字) |

**用途**:发现流程瓶颈(哪阶段重试最多)、门控过严/过松(gate 拦截频率)。详见 `rules/stage-gate.md` §度量章节。

## 加载规则

> v3.2.0-dev:rules + paths 显式声明,只按需加载。

1. 加载被选中的 Skill(user-invoked 或 orchestration)
2. 读取该 Skill 的 `Required rules` / `Required paths` 声明
3. 仅按声明加载对应的 `rules/*.md` 与 `paths/*.md`
4. **禁止一次性全量加载**所有 `rules/*` 与 `paths/*`

## 详细文档

- [README.md](README.md) — 完整使用说明
- [plan.md](plan.md) — 路线图
- [CHANGELOG.md](CHANGELOG.md) — 版本历史
- [SPEC.md §13](SPEC.md) — Rules and Paths 加载模型
