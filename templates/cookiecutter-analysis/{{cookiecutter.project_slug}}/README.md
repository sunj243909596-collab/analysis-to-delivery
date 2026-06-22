# {{ cookiecutter.project_name }}

> 项目代号：{{ cookiecutter.project_code }}
> 版本：{{ cookiecutter.version }}
> 负责人：{{ cookiecutter.owner }}
> 启动日期：{{ cookiecutter.date }}

## 项目结构

本目录由 `analysis-to-delivery` skill 通过 `cookiecutter-gen.sh` 自动生成。

| 编号 | 文档 | 阶段 | 状态 |
|---|---|---|---|
| 01 | [业务需求文档 BRD.md](01-业务需求文档%20BRD.md) | 2 | ⬜ 待填写 |
| 02 | [功能规格说明书 FSD.md](02-功能规格说明书%20FSD.md) | 8 | ⬜ 待填写 |
| 03 | [数据模型设计.md](03-数据模型设计.md) | 8 | ⬜ 待填写 |
| 04 | [合规评审.md](04-合规评审.md) | 3 | ⬜ 待填写 |
| 05 | [产品需求文档 PRD.md](05-产品需求文档%20PRD.md) | 6 | ⬜ 待填写 |
| 06 | [开发设计说明书.md](06-开发设计说明书.md) | 8 | ⬜ 待填写 |
| 07 | [测试用例设计.md](07-测试用例设计.md) | 5 | ⬜ 待填写 |
| -   | [TASK_CONFIRM.md](TASK_CONFIRM.md) | 1 | ⬜ 待填写 |
| -   | [REVIEW_需求确认书.md](REVIEW_需求确认书.md) | 1 | ⬜ 待填写 |
| -   | [REVIEW_字段对齐分析.md](REVIEW_字段对齐分析.md) | 1 | ⬜ 待填写 |
| -   | [AGENTS.md](AGENTS.md) | 7 | ⬜ 待填写 |
| -   | [HANDOVER.md](HANDOVER.md) | 10 | ⬜ 待填写 |

## 快速开始

1. 填写 `TASK_CONFIRM.md`（阶段 1：需求确认）
2. 按编号顺序填充文档
3. 文档写完后跑格式校验：

```bash
python3 ~/.claude/skills/analysis-to-delivery/scripts/doc-validate.py . --level P1
```

## 详细工作流

参见 `~/.claude/skills/analysis-to-delivery/SKILL.md` 的 10 阶段工作流。
