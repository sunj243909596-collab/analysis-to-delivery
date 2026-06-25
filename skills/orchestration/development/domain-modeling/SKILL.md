---
name: domain-modeling
description: 梳理领域模型 — 来自 superpowers 体系。本 skill 是桥接层,完整纪律见 ~/.claude/skills/domain-modeling/。
version: 3.0.1

---

# Domain-Modeling(桥接到 superpowers)

## Contract

- Inputs: design spec, terminology, entities, business rules
- Outputs: domain model diagram and entity list
- Gates: user agrees canonical terms and relationships
- Required disciplines: `stage-gate`
- Next: `/writing-plans`

> **本仓库不维护此 skill 的内容**。完整纪律请读:
> `~/.claude/skills/domain-modeling/SKILL.md`

## 何时调

- brainstorming / design-an-interface 之后
- 需要定义实体、值对象、聚合根

## 衔接点

- **产出**:领域模型图 + 实体清单
- **下一步**:`/writing-plans`
- **门控**:`disciplines/stage-gate` 第 2 层
