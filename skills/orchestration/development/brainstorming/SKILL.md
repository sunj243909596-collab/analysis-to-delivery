---
name: brainstorming
description: 反复提问澄清需求,产出设计稿 — 来自 superpowers 体系(obra/superpowers)。本 skill 是桥接层,完整纪律见 ~/.claude/skills/brainstorming/。
version: 3.0.1

---

# Brainstorming(桥接到 superpowers)

> **本仓库不维护此 skill 的内容**。完整纪律请读:
> `~/.claude/skills/brainstorming/SKILL.md`

## 何时调

- 拿到新需求/新功能,需要先与用户对齐
- 在 `analysis-delivery-workflow` 阶段 2(grill-task)之后
- 在 `dev-design` 阶段 7 之前

## 如何调

```bash
# 方式 1:直接调 superpowers 官方
/brainstorming
```

## 衔接点

- **产出**:`docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`
- **下一步**:`/writing-plans`(拆任务)
- **门控**:`disciplines/stage-gate` 第 2 层

> 🚧 **桥接层不重复 superpowers 内容**,保持单一权威源。
