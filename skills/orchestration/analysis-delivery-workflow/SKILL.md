---
name: analysis-delivery-workflow
description: 严守 9 阶段流程(分析-设计)— 适合新手/复杂项目,按顺序自动调 9 个 user-invoked skill。Use when you want the full structured workflow without making decisions per step.
disable-model-invocation: true
version: 3.0.1

---

# Analysis to Delivery Workflow — 9 阶段流程编排

## 适用场景

- 复杂项目(中等+)
- 新手第一次用
- 严守流程纪律,避免跳步

## 9 阶段(按顺序触发)

| # | 阶段 | 调用的 skill | 产出 |
|---|---|---|---|
| 1 | 项目配置 | `/setup-analysis-delivery` | 4 个 `*-path.md` |
| 2 | 需求澄清 | `/grill-task` | TASK_CONFIRM + 字段对齐 |
| 3 | BRD | `/to-brd` | 01-BRD + 流程图 |
| 4 | 合规评审 | `/compliance-review` | 04-合规评审 |
| 5 | 测试用例 | `/test-case-design` | 07-测试用例 |
| 6 | PRD | `/to-prd` | 05-PRD(三格式) |
| 7 | 开发设计 | `/dev-design` | AGENTS + FSD + 数据模型 + 开发设计 + 回测 + 复盘 |
| 8 | QA 审计 | `/qa-audit` | 09-QA 审计报告 |
| 9 | 交接 | `/handoff` | HANDOVER.md |

## 衔接 superpowers 实施(阶段 9 之后)

**设计交接完成后,推荐进入 `/using-superpowers` 走 5 步实施**:

```
brainstorming → design-an-interface → domain-modeling → writing-plans → tdd → executing-plans → verification-before-completion
```

| 实施步骤 | 产出 |
|---|---|
| brainstorming | 设计稿 |
| design-an-interface | 接口契约 |
| domain-modeling | 领域模型 |
| writing-plans | ≤ 2h 子任务列表 |
| tdd | RED → GREEN → REFACTOR |
| executing-plans | 逐步开发 + commit |
| verification-before-completion | 完成前验证 |

## 门控(贯穿)

每阶段必签字才能进入下一阶段。详细见 `disciplines/stage-gate` 3 层门控:

- **第 1 层**:9 阶段之间 → 用户签字
- **第 2 层**:实施子流程之间 → 用户 + Claude 双向
- **第 3 层**:每个 writing-plans 子任务 → 测试 + 用户抽查

## 关键纪律

- **严禁自动推进**：本编排"按顺序触发"9 个 skill，但每阶段产物必须经用户显式签字（白名单话术）后才能进入下一阶段。LLM 不得自行解释"OK""继续""好"等模糊回复为签字。
- 严禁跳阶段(从 1 跳 3 / 从 5 跳 7)
- 每阶段产物必须签字
- HARD GATE:阶段 7 设计回测 ❌ 禁入阶段 8
- HARD GATE:阶段 8 QA 审计 P0>0 禁入阶段 9

## 2→3 门控（2026-06-24 强化）

阶段 2 → 阶段 3 之间，必须同时满足：

1. TASK_CONFIRM 状态 = ✅
2. REVIEW 文档中 ❓=0 且 🔴=0
3. 用户白名单话术签字（详见 `skills/disciplines/stage-gate/SKILL.md`）

详见 `scripts/task-confirm-check.py` 自动化校验。

## 调用的 discipline

- `disciplines/stage-gate` — 3 层门控
- `disciplines/no-field-guessing` — 字段名
- `disciplines/doc-numbering` — 文档编号

## 结束条件

- [ ] 9 阶段全部签字
- [ ] HANDOVER.md 已生成
- [ ] 已交接给编码 skill 或开发团队
