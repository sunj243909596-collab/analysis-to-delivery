---
name: setup-analysis-delivery
description: 首次为新项目接 analysis-to-delivery 工作流 — 生成 4 个项目级 *-path.md 配置文件。Use when starting a new project or adding this skill to an existing project.
disable-model-invocation: true
version: 3.0.1

---

# Setup Analysis-Delivery — 项目配置初始化

## 适用场景

- 拿到一个新项目,需要接 analysis-to-delivery 工作流
- 给现有项目补这套工作流的配置

## 流程步骤

### 1. 检测项目根

- 必须在 git 仓库根执行(`git rev-parse --show-toplevel`)
- 项目根不存在 `.git` → 提示用户先 `git init`

### 2. 检测项目类型

读项目根文件,推断技术栈:
- `pom.xml` / `build.gradle` → Java/Maven/Gradle
- `package.json` → Node/前端
- `pyproject.toml` / `requirements.txt` → Python
- `go.mod` → Go

### 3. 生成 4 个项目级配置

在项目根生成以下 4 个空模板(用户填写后提交到 git):

| 文件 | 作用 | 模板 |
|---|---|---|
| `knowledge-path.md` | 列项目涉及的外部知识库(领域表结构、合规法规等)路径 | `templates/project-config/knowledge-path.md` |
| `compliance-path.md` | 列项目适用的合规规则文件路径 + 启用开关 | `templates/project-config/compliance-path.md` |
| `tech-stack-path.md` | 列后端/前端/数据库/中间件 + 团队规范路径 | `templates/project-config/tech-stack-path.md` |
| `doc-naming.md` | 文档编号、命名前缀、存放目录 | `templates/project-config/doc-naming.md` |

### 4. 验证

- 4 个文件存在且非空(允许只有注释)
- 跑 `python3 scripts/field-alignment-check.py --help` 确认脚本可用

## 调用的 discipline

- `disciplines/context-pointer` — 三层配置加载规则

## 结束条件

- [ ] 4 个 `*-path.md` 全部生成在项目根
- [ ] 用户已填写真实内容(knowledge-path 必须至少 1 个真实路径)
- [ ] 已提交到 git(可选,但建议)
