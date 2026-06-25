---
name: decisions
description: 项目级 ADR / 决策记录模板。汇总本项目引用的全部配置路径(4 个 *-path.md 的使用记录)和关键技术决策。
type: deliverable
stage: 1
replaces: config-used.md
version: 3.1.0
---

# Decisions（ADR / 决策记录）：{项目名}

> 文件身份：**ADR / 决策记录**，不参与配置加载
> 加载阶段：阶段 1 项目配置 / 持续维护
> 替代：`config-used.md`（v3.1.0 起改名为 decisions.md，旧名保留为别名）
> 注意：配置加载只读 4 个 `*-path.md`，本文件是"配置的使用记录 + 决策日志"

## 一、配置加载清单

| 配置类型 | 实际文件 | 加载结果 | 说明 |
|---|---|---|---|
| 知识库 | `knowledge-path.md` | ⬜ 待确认 | |
| 合规 | `compliance-path.md` | ⬜ 待确认 | |
| 技术栈 | `tech-stack-path.md` | ⬜ 待确认 | |
| 文档命名 | `doc-naming.md` | ⬜ 待确认 | |

## 二、Fallback 使用情况

| 配置类型 | 是否使用 skill fallback | fallback 文件 | 原因 |
|---|---|---|---|
| 知识库 | 否 | | |
| 合规 | 否 | | |
| 技术栈 | 否 | | |
| 文档命名 | 否 | | |

## 三、ADR 记录（决策日志）

| ADR | 日期 | 决策 | 原因 | 影响范围 |
|---|---|---|---|---|
| ADR-001 | YYYY-MM-DD | 例:Target_DB 选 Oracle 19c | 客户已有 Oracle 许可 + DBA 团队熟悉 | 数据模型/FSD/开发设计/PIX |
| ADR-002 | | | | |

## 四、版本演进

| 版本 | 日期 | 变更 |
|---|---|---|
| v1.0 | YYYY-MM-DD | 项目立项，初版配置 |
| v3.1.0 | YYYY-MM-DD | 改名 `config-used.md` → `decisions.md`(更准确反映 ADR 性质) |

## 五、后续维护规则

- 修改任一 `*-path.md` 后,同步更新本文件的 §一 加载清单。
- 新增关键技术/合规/命名决策后,追加 §三 ADR 记录(编号递增)。
- 本文件不得替代 `knowledge-path.md` / `compliance-path.md` / `tech-stack-path.md` / `doc-naming.md`。

---

> 改名历史：v3.1.0 起 `config-used.md` 改名 `decisions.md`，原因：原名容易被误以为是配置文件（实际是 ADR），改名后更准确反映文件性质。旧文件名保留作为别名（向后兼容）。