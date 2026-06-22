---
name: grill-task
description: 需求澄清 + 字段对齐分析 — 反复提问拉齐用户意图,生成 TASK_CONFIRM 和字段对齐分析。Use when starting a new feature, clarifying requirements, or aligning field names with existing tables.
disable-model-invocation: true
---

# Grill-Task — 需求澄清 + 字段对齐

## 适用场景

- 用户提出新需求时
- 需求涉及现有表查询/维护类功能
- 团队对需求理解不一致时

## 流程步骤

### 1. 生成《需求确认表》

- 加载 `templates/TASK_CONFIRM.md`
- 替换项目名、日期,生成 `TASK_CONFIRM_{项目名}.md` 到工作目录
- 告知用户填写并保存

### 2. 用户填写后,生成《需求确认书》

- 读取用户填写的 `TASK_CONFIRM_*.md`
- 加载 `templates/REVIEW_需求确认书.md`
- 逐项标注 AI 助手的理解,列出待确认的设计假设
- 输出 `REVIEW_需求确认书.md`

### 3. 字段对齐分析(涉及现有表时强制)

- 提取需求中提到的所有表名和字段名
- 与 `knowledge-path.md` 引用的知识库核对
- 输出 `REVIEW_字段对齐分析.md`,分类标注:
  - ✅ 已对齐
  - ⚠️ 需 JOIN
  - ❓ 待确认(业务同义不同名)
  - 🔴 缺失
- 跑 `python3 scripts/field-alignment-check.py` 自动验证

## 关键纪律

- 用户填写完 TASK_CONFIRM 后,**严禁直接跳进设计**
- 必须先出确认书让用户审阅
- 用户确认通过 → 进入 `/to-brd`
- 字段对齐有 🔴 缺失项 → 严禁进入下一步

## 调用的 discipline

- `disciplines/no-field-guessing` — 严禁猜测字段名
- `disciplines/no-self-invent` — 严禁自创字段
- `disciplines/context-pointer` — 三层知识库加载

## 结束条件

- [ ] TASK_CONFIRM 4 个必备章节填完
- [ ] REVIEW_需求确认书已签字
- [ ] REVIEW_字段对齐分析无 🔴 缺失项
- [ ] `field-alignment-check.py` 通过
