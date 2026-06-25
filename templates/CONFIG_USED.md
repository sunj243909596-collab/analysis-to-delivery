# 配置使用记录 / ADR：{项目名}

> 生成阶段：阶段 1 项目配置
> 文件身份：交付产物 / ADR 记录
> 注意：本文件不是配置文件，不参与配置加载。配置加载只读取 4 个 `*-path.md`。

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

## 三、ADR 记录

| ADR | 决策 | 原因 | 影响文档 |
|---|---|---|---|
| ADR-001 | | | |

## 四、后续维护规则

- 修改任一 `*-path.md` 后,同步更新本文件的加载清单。
- 新增关键技术/合规/命名决策后,追加 ADR 记录。
- 本文件不得替代 `knowledge-path.md` / `compliance-path.md` / `tech-stack-path.md` / `doc-naming.md`。
