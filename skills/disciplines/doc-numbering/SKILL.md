---
name: doc-numbering
description: 文档编号 01-08 严格对应阶段,同项目目录不允许重号,Figma 文档不受编号约束。Use when creating or organizing any design document.
---

# Doc-Numbering — 文档编号规范

## 编号映射(强制)

| 编号 | 文档 | 阶段 |
|---|---|---|
| 01 | 业务需求文档 BRD | 2 |
| 02 | 功能规格说明书 FSD | 7 |
| 03 | 数据模型设计 | 7 |
| 04 | 合规评审 | 3 |
| 05 | 产品需求文档 PRD | 6 |
| 06 | 开发设计说明书 | 7 |
| 07 | 测试用例设计 | 5 |
| 08 | 业务流程图.drawio / 设计回测报告 | 2 / 7 |
| 09 | QA 审计报告 | 8 |
| - | AGENTS.md | 7 |
| - | TASK_CONFIRM_*.md | 1 |
| - | REVIEW_*.md | 1 |
| - | HANDOVER.md | 9 |
| - | Figma设计文档_{功能名}_{端}.md | 4(可选) |

## 规则

1. **同一项目目录**,每个编号**只允许一个 `0X-` 开头的文件**
2. Figma 文档不受编号约束(命名为 `Figma设计文档_{功能名}_{端}.md`)
3. 编号冲突时 `full-qa-audit.py` 会报 P0 错误
4. AGENTS.md / TASK_CONFIRM / REVIEW / HANDOVER 不占编号

## 反例

```bash
# ❌ 错误:同一目录有 2 个 01- 开头的文件
01-业务需求文档 BRD.md
01-业务需求文档 BRD-v2.md  # ❌ 编号冲突

# ✅ 正确:v2 用日期后缀
01-业务需求文档 BRD.md
01-业务需求文档 BRD-2026-06-22-v2.md  # 或归档到 history/
```

## 自动检查

`scripts/full-qa-audit.py` 会自动检查编号冲突。

## 引用

- 详细规范:原 `references/doc-numbering.md`
