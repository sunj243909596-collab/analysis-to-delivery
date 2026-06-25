---
name: verification-before-completion
description: 完成任务前验证(铁律)— 来自 superpowers 体系。本 skill 是桥接层,完整纪律见 ~/.claude/skills/verification-before-completion/。
version: 3.0.1

---

# Verification-Before-Completion(桥接到 superpowers)

## Contract

- Inputs: completion claim, verification commands, implementation/documentation outputs
- Outputs: verification report using IDENTIFY/RUN/READ/VERIFY/THEN
- Gates: full verification command succeeds and output supports the claim
- Required disciplines: `stage-gate`
- Next: commit, fix loop, or `/handoff`

> **本仓库不维护此 skill 的内容**。完整纪律请读:
> `~/.claude/skills/verification-before-completion/SKILL.md`

## 何时调

- 每个子任务结束时(在 commit 之前)
- 整个开发冲刺结束时(在 HANDOVER 之前)

## 衔接点

- **产出**:验证报告(IDENTIFY → RUN → READ → VERIFY → THEN 5 步门控)
- **下一步**:commit(通过)或修复(失败)
- **门控**:`disciplines/stage-gate` 第 3 层(失败必须重新跑)

## 5 步门控

参考完整纪律:
1. **IDENTIFY** — 什么命令能证明这个声明?
2. **RUN** — 执行完整的验证命令
3. **READ** — 读完整输出,检查退出码
4. **VERIFY** — 输出是否确认了声明?
5. **THEN** — 才能做出声明

> **铁律:跳过任何一步 = 撒谎,不是验证。**
