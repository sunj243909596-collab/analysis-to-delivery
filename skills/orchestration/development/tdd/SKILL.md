---
name: tdd
description: 测试驱动开发(红绿循环)— 来自 superpowers 体系。本 skill 是桥接层,完整纪律见 ~/.claude/skills/tdd/。
version: 3.0.1

---

# TDD(桥接到 superpowers)

## Contract

- Inputs: executable task from writing plan, test target, acceptance criteria
- Outputs: RED test, GREEN implementation, refactor notes
- Gates: RED observed before implementation; GREEN observed after implementation
- Required disciplines: `stage-gate`
- Next: `/executing-plans`

> **本仓库不维护此 skill 的内容**。完整纪律请读:
> `~/.claude/skills/tdd/SKILL.md`

## 何时调

- writing-plans 之后
- 每个子任务开始时(红绿循环)

## 衔接点

- **产出**:RED 测试 + GREEN 实现 + REFACTOR
- **下一步**:`/executing-plans`(commit + 下一任务)
- **门控**:`disciplines/stage-gate` 第 3 层(RED 必须确认失败才能写实现)
