---
name: to-brd
description: 生成业务需求文档(BRD)— 含业务流程图、角色职责、功能模块、字段映射。Use when business requirements need to be documented formally.
disable-model-invocation: true
---

# To-BRD — 业务需求文档生成

## 适用场景

- TASK_CONFIRM 和字段对齐分析已通过
- 需要把业务需求整理成 BRD 交给团队评审
- 需要画业务流程图 / 状态流转图

## 流程步骤

### 1. 加载模板

- `templates/BRD.md`(9 节必备章节)

### 2. 填充内容

按 BRD 模板逐节生成:

| 章节 | 内容来源 |
|---|---|
| 一、项目概述 | TASK_CONFIRM §1-3 |
| 二、角色与职责 | 业务调研 |
| 三、业务流程 | ASCII 流程图 / drawio |
| 四、功能模块 | TASK_CONFIRM §功能描述 |
| 五、数据要求 | 字段对齐分析 + 知识库 |
| 六、合规要点 | 预留,阶段 3 填 |
| 七、非功能需求 | 性能/可靠性/安全/可维护性 |
| 八、风险与约束 | 团队约束 + 外部依赖 |
| 九、上线计划 | 团队节奏 |

### 3. 画流程图

- 状态流转图:**ASCII**(参考 `disciplines/ascii-flowchart`)
- 业务流程图:简单用 ASCII,复杂用 drawio
- 泳道图:ASCII(角色分工清晰)

### 4. 字段映射表

把字段对齐分析里的 ✅ 项固化到 BRD §五.3:

| 业务概念 | 字段 | 备注 |
|---|---|---|
| ASN 单号 | `ASN.TC_ASN_ID` | ❌ 严禁用 ASN_NBR |

### 5. DB 验证(如涉及)

- 仅允许 `SELECT` 查询
- 用 `desc table_name` 验证字段定义
- **严禁** 任何 DDL/DML 写操作

## 输出

- `01-业务需求文档 BRD.md`
- `业务流程图-状态流转.txt`(ASCII)
- `业务流程图-收货流程.txt`(如需要,泳道图)
- `业务流程图.drawio`(可选,用于可视化)

## 调用的 discipline

- `disciplines/ascii-flowchart` — 流程图规范
- `disciplines/no-field-guessing` — 字段名必须查知识库
- `disciplines/doc-numbering` — 文档编号 01

## 结束条件

- [ ] BRD 9 个必备章节齐
- [ ] ASCII 流程图 + 状态流转图
- [ ] 字段映射表通过 `field-alignment-check.py`
- [ ] 用户签字进入阶段 3
