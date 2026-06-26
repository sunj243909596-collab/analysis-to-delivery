# Doc Naming Path — 文档命名路径

## 目的

定义项目自有的文档名、编号、输出目录;9 阶段产物全部按本表命名。

## 必填条目

| 文档 | 默认文件名 | 输出目录 | 阶段 |
|---|---|---|---|
| 任务确认表 | `TASK_CONFIRM.md` | `docs/analysis/` | 2 |
| 业务需求文档 BRD | `01-BRD.md` | `docs/analysis/` | 3 |
| 功能规格说明书 FSD | `02-FSD.md` | `docs/design/` | 7 |
| 数据模型设计 | `03-DATA-MODEL.md` | `docs/design/` | 7 |
| 合规评审 | `04-COMPLIANCE.md` | `docs/analysis/` | 4 |
| 产品需求文档 PRD | `05-PRD.md` | `docs/analysis/` | 6 |
| 开发设计说明书 | `06-DEV-DESIGN.md` | `docs/design/` | 7 |
| 测试用例设计 | `07-TEST-CASES.md` | `docs/test/` | 5 |
| 设计回测报告 | `08-DESIGN-BACKTEST.md` | `docs/design/` | 7 |
| QA 审计报告 | `09-QA-AUDIT.md` | `docs/qa/` | 8 |
| 交接清单 | `HANDOVER.md` | `docs/handoff/` | 9 |

## 规则

1. **编号 01-09 严格对应表内编号文档**,同项目目录不允许重号
2. 签字后的文档**严禁重新编号**(下游引用全部失效)
3. 项目覆盖默认文件名时,后续阶段**统一**用新名(`setup-check.py` 不强制默认名,只校验文件存在)
4. 非编号文档(`HANDOVER.md` / `AGENTS.md` / `REVIEW_*` / `TASK_CONFIRM_*` / `RETRO_*`)**不占**编号
5. 输出目录按需调整;但同一项目内**必须一致**(避免文档散落)
