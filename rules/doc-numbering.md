# Doc-Numbering — 文档编号规范

> 规范来源:`skills/disciplines/doc-numbering`(已迁移至此)。旧的 `skills/disciplines/doc-numbering/SKILL.md` 是本文件的兼容壳。

## 目的

文档编号 01-09 严格对应编号文档,同项目目录不允许重号;HANDOVER/AGENTS/REVIEW/TASK_CONFIRM/RETRO 不占编号。

## 编号映射(强制)

| 编号 | 编号文档 | 阶段 |
|---|---|---|
| 01 | 业务需求文档 BRD | 3 |
| 02 | 功能规格说明书 FSD | 7 |
| 03 | 数据模型设计 | 7 |
| 04 | 合规评审 | 4 |
| 05 | 产品需求文档 PRD | 6 |
| 06 | 开发设计说明书 | 7 |
| 07 | 测试用例设计 | 5 |
| 08 | 设计回测报告 | 7 |
| 09 | QA 审计报告 | 8 |

## 非编号文档(不占编号)

| 文档 | 阶段 | 说明 |
|---|---|---|
| AGENTS.md | 7 | 项目级 AI 助手配置 |
| TASK_CONFIRM_*.md | 2 | 需求确认表 |
| REVIEW_*.md | 2 | 需求确认书 / 字段对齐分析 |
| RETRO_*.md | 7 / 实施扩展 | 任务复盘 / 复盘汇总 |
| HANDOVER.md | 9 | 交接清单 |
| Figma设计文档_{功能名}_{端}.md | 6(可选) | 设计稿说明 |

## 规则

1. **同一项目目录**,每个编号**只允许一个 `0X-` 开头的文件**。
2. 只有 `01-` 到 `09-` 是编号文档;`00-` 不属于默认编号体系。
3. `HANDOVER.md` / `AGENTS.md` / `REVIEW_*` / `TASK_CONFIRM_*` / `RETRO_*` 不占编号。
4. Figma 文档不受编号约束,命名为 `Figma设计文档_{功能名}_{端}.md`。
5. 编号冲突时 `full-qa-audit.py` 会报 P0 错误。

## 反例

```bash
# ❌ 错误:同一目录有 2 个 01- 开头的文件
01-业务需求文档 BRD.md
01-业务需求文档 BRD-v2.md  # 编号冲突

# ✅ 正确:v2 不占用新编号,归档到 history/
01-业务需求文档 BRD.md
history/01-业务需求文档 BRD-2026-06-22-v2.md

# ✅ 正确:复盘不占 07 编号
RETRO_任务复盘汇总.md
```

## 自动检查

`scripts/full-qa-audit.py` 会自动检查编号冲突。

## 引用

- 详细规范:原 `references/doc-numbering.md`
