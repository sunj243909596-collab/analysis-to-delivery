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

## 关键纪律（2026-06-24 更新）

- ❌ 删除"4 章节"表述——实际为 5 章节（一~五）
- ❌ 删除 `field-alignment-check.py` 作为门控脚本的引用——该脚本只校验 PRD/FSD 字段引用，不接 TASK_CONFIRM
- ✅ 新增 `scripts/task-confirm-check.py` 作为唯一门控脚本
- 🟡 删除：状态字段不再有 🟡 中间态，仅 ⬜/✅ 二态
- 🔒 HARD GATE：用户必须用白名单话术之一明确签字，LLM 不接受隐式同意

## 结束条件

- [ ] TASK_CONFIRM 状态字段 = ✅ 已确认（二态，无 🟡）
- [ ] TASK_CONFIRM 5 个必备章节（一~五）填完
- [ ] TASK_CONFIRM 无 12 词 TBD（见 `scripts/task-confirm-check.py` TBD_KEYWORDS）
- [ ] REVIEW_需求确认书 第八节"待明确事项"为空
- [ ] REVIEW_字段对齐分析 对齐结论表中 ❓=0 且 🔴=0（⚠️ 可保留，状态字段可为 ✅ 或 ⚠️）
- [ ] `scripts/task-confirm-check.py` exit 0
- [ ] 用户白名单话术签字（详见 `templates/TASK_CONFIRM.md` L48-55）
- [ ] ~~`field-alignment-check.py` 通过~~（已废弃此引用；该脚本不接 TASK_CONFIRM，仅校验 PRD/FSD 字段引用）
