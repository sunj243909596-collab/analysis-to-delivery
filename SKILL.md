---
name: analysis-to-delivery
description: 通用需求分析到开发设计工作流 — thin Skill router,加载规则与路径按声明。Use when starting any new feature requiring structured analysis-to-delivery workflow.
category: software-development
version: 3.2.0-dev
created: 2026-06-22
updated: "2026-06-26: v3.2.0-dev rules-and-paths refactor — thin root router, rules/ + paths/ layers"
---

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
