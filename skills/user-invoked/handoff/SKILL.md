---
name: handoff
description: 代码交接文档 — 整理已完成文档、待办事项、已知风险、后续工作建议。Use when ending design phase and handing over to implementation.
disable-model-invocation: true
version: 3.0.1

---

# Handoff — 代码交接

## 适用场景

- QA 审计通过(P0=0)
- 准备把设计交付给编码 skill(如 `wms-code-implementation`)或开发冲刺

## 流程步骤

### 1. 整理已完成文档

列出本项目已交付的设计文档:

```markdown
## 已完成文档

| 编号 | 文档 | 路径 | 状态 |
|---|---|---|---|
| 01 | 业务需求文档 BRD | `01-业务需求文档 BRD.md` | ✅ |
| 02 | 功能规格说明书 FSD | `02-功能规格说明书 FSD.md` | ✅ |
| 03 | 数据模型设计 | `03-数据模型设计.md` | ✅ |
| 04 | 合规评审 | `04-合规评审.md` | ✅ |
| 05 | 产品需求文档 PRD | `05-PRD.md` | ✅ |
| 06 | 开发设计说明书 | `06-开发设计说明书.md` | ✅ |
| 07 | 测试用例设计 | `07-测试用例设计.md` | ✅ |
| 08 | 设计回测报告 | `08-设计回测报告.md` | ✅ |
| 09 | QA 审计报告 | `09-QA审计报告.md` | ✅ |
| - | AGENTS.md | `AGENTS.md` | ✅ |
```

### 2. 整理待办事项

按 P0/P1/P2 列出:

```markdown
## 待办事项

### P0(必须后续处理)
- [ ] ...

### P1(建议后续处理)
- [ ] ...

### P2(可选)
- [ ] ...
```

### 3. 整理已知风险与限制

```markdown
## 已知风险与限制

| 风险 | 影响 | 缓解 | 责任方 |
|---|---|---|---|
| ... | ... | ... | ... |
```

### 4. 后续工作建议

- **进入实施**:推荐 `/using-superpowers` 走 5 步实施子流程
- **或转交编码 skill**:如 `wms-code-implementation`
- **或直接进入开发冲刺**:按 PRD §九 上线计划推进

### 5. 触发

- 转交编码 skill → 在项目根放 `HANDOVER.md`
- 或直接进入开发冲刺 → 把 HANDOVER.md 链接发到团队群

## 输出

- `HANDOVER.md`

## 调用的 discipline

- `disciplines/stage-gate` — 阶段 10 门控
- `disciplines/doc-numbering` — HANDOVER 不受编号约束

## 结束条件

- [ ] HANDOVER.md 含 4 节(已完成/待办/风险/后续)
- [ ] 接收方(编码 skill / 开发团队)已确认收到
