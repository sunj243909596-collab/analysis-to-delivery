---
name: executing-plans
description: 逐步按计划执行 + 复盘 — 来自 superpowers 体系。本 skill 是桥接层,完整纪律见 ~/.claude/skills/executing-plans/。
version: 3.0.1

---

# Executing-Plans(桥接到 superpowers)

## Contract

- Inputs: writing plan, passing task tests, implementation diff
- Outputs: commit history and 5-question retrospective / knowledge updates
- Gates: tests pass; verification command recorded; commit or explicit handoff state exists
- Required disciplines: `stage-gate`
- Next: next `/tdd` task or `/verification-before-completion`

> **本仓库不维护此 skill 的内容**。完整纪律请读:
> `~/.claude/skills/executing-plans/SKILL.md`

## 何时调

- tdd 通过后,逐步 commit
- 每个 writing-plans 子任务 GREEN 后

## 衔接点

- **产出**:commit history + 5 问复盘(沉淀到知识库)
- **下一步**:下一任务(回到 `/tdd`)或 `/verification-before-completion`
- **门控**:`disciplines/stage-gate` 第 3 层(commit + 复盘 + 沉淀三件套)
