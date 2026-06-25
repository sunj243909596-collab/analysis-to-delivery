---
name: test-case-design
description: 测试用例设计 — 覆盖正常路径/边界条件/异常路径/合规校验/性能安全。Use when defining acceptance criteria before development.
disable-model-invocation: true
version: 3.0.1

---

# Test-Case-Design — 测试用例设计

## Contract

- Inputs: signed BRD, optional `04-合规评审.md`, business rules and acceptance criteria
- Outputs: `07-测试用例设计.md`
- Gates: BRD functions covered; normal/boundary/exception/compliance cases present; user signoff
- Required disciplines: `stage-gate`, `doc-numbering`
- Next: `/to-prd`

## 适用场景

- BRD 通过,需要明确"什么算成功"
- 开发前需要验收标准
- 测试团队需要用例输入

## 流程步骤

### 1. 加载模板

- `templates/TEST_CASE_DESIGN.md`

### 2. 覆盖范围

按以下 5 大类逐项设计:

| 类别 | 内容 | 占比建议 |
|---|---|---|
| 正常路径 | 主流程 happy path | 30% |
| 边界条件 | 极值、空值、最大/最小 | 20% |
| 异常路径 | 错误输入、超时、外部依赖失败 | 30% |
| 合规校验 | 数据授权、审计、效期锁定 | 10% |
| 性能/安全 | 并发、SQL 注入、XSS | 10% |

### 3. 用例结构

每条用例至少包含:

| 字段 | 说明 |
|---|---|
| 用例编号 | TC-{模块}-{序号} |
| 关联需求 | BRD §{章节} |
| 前置条件 | 初始数据/状态 |
| 输入 | 测试数据 |
| 操作步骤 | 步骤化 |
| 预期结果 | 精确、可验证 |
| 实际结果 | 测试执行时填 |
| 通过条件 | PASS/FAIL 判定标准 |

### 4. 业务规则回测(从 BRD §四 提取)

对每条业务规则设计至少 1 个用例:
- 正向:触发条件满足 → 期望行为
- 反向:触发条件不满足 → 期望拦截
- 边界:临界值

## 输出

- `07-测试用例设计.md`

## 调用的 discipline

- `disciplines/stage-gate` — 阶段 5 门控

## 结束条件

- [ ] 用例覆盖 BRD §四 全部功能点
- [ ] 异常路径 100%(每条主流程至少 1 个异常用例)
- [ ] 业务规则正向 + 反向 + 边界 三类齐
- [ ] 合规校验用例关联到合规评审条款
- [ ] 用户签字进入 `/to-prd`
