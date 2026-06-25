---
name: compliance-review
description: 合规性评审 — 按 compliance-path.md 引用的合规规则,逐条评估设计。Use when dealing with GSP / HIPAA / SOX / GDPR / 等强合规场景。
disable-model-invocation: true
version: 3.0.1

---

# Compliance-Review — 合规评审

## Contract

- Inputs: signed `01-业务需求文档 BRD.md`, `compliance-path.md`
- Outputs: `04-合规评审.md`
- Gates: all applicable compliance clauses judged; severe gaps resolved or explicitly accepted; user/compliance signoff
- Required disciplines: `context-pointer`, `stage-gate`
- Next: `/test-case-design`

## 适用场景

| 需求类型 | 是否需要 |
|---|---|
| 涉及个人健康信息(PHI) | ✅ 必须 |
| 涉及支付/金融 | ✅ 必须 |
| 涉及个人身份信息(PII) | ✅ 必须 |
| 涉及医药追溯(GSP) | ✅ 必须 |
| 纯内部工具 | ⚠️ 按团队规范 |

## 流程步骤

### 1. 加载合规规则

- 读项目根 `compliance-path.md`
- 加载其引用的合规规则文件(`config/compliance/<行业>.md` 或 skill 级 fallback)
- 列出所有适用条款

### 2. 逐条评估 BRD

对每条合规条款,按以下格式输出:

| 条款编号 | 缺陷等级 | 检查要点 | 合规设计 | 证据位置 | 状态 |
|---|---|---|---|---|---|
| **{条款编号} | {严重/主要/一般} | {检查要点} | {合规设计摘要} | FSD §{章节号} | ✅/⚠️/🔄 |

**判定标准**:
- ✅ 符合:完全满足
- ⚠️ 不符合:存在合规缺口
- 🔄 不适用:条款不适用本功能

### 3. 写评审结论

按条款输出后,给出整体结论:
- ✅ 全部通过 → 进入下一阶段
- ⚠️ 带条件通过(列出条件)
- ❌ 不通过(回 BRD 修复)

## 输出

- `04-合规评审.md`

## 调用的 discipline

- `disciplines/context-pointer` — 三层合规规则加载(项目级 > skill 级 > 默认)
- `disciplines/stage-gate` — 阶段 4 门控

## 结束条件

- [ ] 所有适用条款已评审(无遗漏)
- [ ] 每条都有 ✅/⚠️/🔄 判定
- [ ] 整体结论签字(用户 + 合规方)
- [ ] 缺陷等级为"严重"的条款全部 ✅
