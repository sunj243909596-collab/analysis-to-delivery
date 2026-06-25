---
name: writing-plans
description: 把 spec 拆成可执行计划(每个 ≤ 2h)— 来自 superpowers 体系。本 skill 是桥接层,完整纪律见 ~/.claude/skills/writing-plans/。
version: 3.0.1

---

# Writing-Plans(桥接到 superpowers)

## Contract

- Inputs: signed design spec, interface/domain model as available
- Outputs: `docs/superpowers/plans/YYYY-MM-DD-<topic>-plan.md`
- Gates: tasks are independently executable and each is no larger than 2 hours
- Required disciplines: `stage-gate`
- Next: `/tdd`

> **本仓库不维护此 skill 的内容**。完整纪律请读:
> `~/.claude/skills/writing-plans/SKILL.md`

## 何时调

- brainstorming / design-an-interface / domain-modeling 之后
- 需要把 spec 拆成可逐步执行的计划

## 衔接点

- **产出**:`docs/superpowers/plans/YYYY-MM-DD-<topic>-plan.md`(含 ≤ 2h 子任务列表)
- **下一步**:`/tdd`(开始红绿循环)
- **门控**:`disciplines/stage-gate` 第 2 层 + 第 3 层(每个子任务)
