# Analysis to Delivery

> 通用需求分析到开发实施工作流 — 26 个独立可组合 skill,跨行业、跨技术栈。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.4.0--dev-blue.svg)](plan.md)

## 它是什么

一个 Claude Code / Hermes 的 **skill 集合**(v1.4 重大重构),提供从「需求澄清」到「开发实施」的标准化工作流。

参考 [mattpocock/skills](https://github.com/mattpocock/skills) 风格:**小而精、可组合、不拥有流程**。

任何团队拿到这个 skill 之后:
1. 告诉 Claude 你的**领域**(医药/金融/SaaS/移动 App...)和**技术栈**(Java/Go/Python/Node...)
2. 用 `/ask-delivery` 选择对应 skill,或直接 `/analysis-delivery-workflow` 走完整流程
3. 产出可直接交给开发的设计文档(BRD/FSD/数据模型/PRD/开发设计/测试用例)

**默认不包含**:实际业务代码。若用户明确启用"实施扩展模式",可走 `/using-superpowers` 串接 superpowers 5 步实施。

## 核心特性

- ✅ **26 个独立 skill**(v1.4 拆分):2 router + 9 动作 + 1 编排 + 7 bridge + 7 discipline
- ✅ **可组合**:不强制流程,自由调任意 skill
- ✅ **可插拔配置**:`config/` 目录放行业/技术栈/领域知识库,按需加载
- ✅ **跨行业**:医药/金融/SaaS/移动 App 通用
- ✅ **跨技术栈**:Java/Go/Python/Node/Rust/.NET 全支持
- ✅ **示例驱动**:内置 1 个完整示例(医药 WMS 收货管理),其他行业示例规划中
- ✅ **自动化脚本**:smoke test、文档校验、字段对齐、SQL 方言检查、QA 审计、并行委派、PRD HTML 后处理、项目初始化、cookiecutter 生成
- ✅ **12 个文档模板**:从需求确认表到开发设计说明书

## 安装

### 一键安装（推荐）

```bash
curl -fsSL https://raw.githubusercontent.com/sunj243909596-collab/analysis-to-delivery/main/install.sh | bash
```

### 手动安装

```bash
git clone https://github.com/sunj243909596-collab/analysis-to-delivery.git \
  ~/.claude/skills/analysis-to-delivery
```

### 安装选项

```bash
# Dry run（只检查不安装）
bash install.sh --dry-run

# 指定目标目录
bash install.sh --target /path/to/install

# 指定版本
bash install.sh --version v1.0.0

# 卸载
bash install.sh --uninstall
```

### 安装位置

脚本自动检测：
- 优先 `~/.claude/skills/`（Claude Code 用户）
- 回退 `~/.hermes/skills/`（Hermes 用户）

可用 `--target` 强制指定。

## 使用

### 0. 装完先跑 smoke test（v1.2+）

```bash
bash ~/.claude/skills/analysis-to-delivery/scripts/smoke-test.sh
```

确认文件完整后再用。✅ 全部通过即可放心；⚠️ 有警告可继续；❌ 有错误需先修复。

### 方式 1：斜杠命令（Claude Code）

```
/analysis-to-delivery
```

### 方式 2：自然语言

```
"使用 analysis-to-delivery 分析入库收货需求"
```

### 方式 3：项目启动

```
"我要做一个 SaaS CRM 系统，用 Node + React + PostgreSQL，请用 analysis-to-delivery 帮我走完需求到设计"
```

Claude 会自动：
1. 加载 `config/compliance/none.md`（无强合规）
2. 加载 `config/tech-stack/node-nestjs.md`（如果存在）
3. 按 10 阶段工作流推进

## 包含什么

```
analysis-to-delivery/
├── SKILL.md                    # 顶层入口(指向 skills/ 下)
├── install.sh                  # 一键安装
├── README.md                   # 本文件
├── plan.md                     # 项目路线图
├── SPEC.md                     # 功能规格
├── CHANGELOG.md                # 版本历史
├── LICENSE                     # MIT
├── skills/                     # 26 个独立 skill(v1.4 拆分)
│   ├── ask-delivery/           # Router 1
│   ├── using-superpowers/      # Router 2
│   ├── user-invoked/           # 9 个动作
│   │   ├── setup-analysis-delivery/
│   │   ├── grill-task/
│   │   ├── to-brd/
│   │   ├── compliance-review/
│   │   ├── test-case-design/
│   │   ├── to-prd/
│   │   ├── dev-design/
│   │   ├── qa-audit/
│   │   └── handoff/
│   ├── orchestration/          # 1 编排 + 7 bridge
│   │   ├── analysis-delivery-workflow/
│   │   └── development/        # 7 个 superpowers bridge
│   │       ├── brainstorming/
│   │       ├── design-an-interface/
│   │       ├── domain-modeling/
│   │       ├── writing-plans/
│   │       ├── tdd/
│   │       ├── executing-plans/
│   │       └── verification-before-completion/
│   └── disciplines/            # 7 个纪律(model-invoked)
│       ├── no-field-guessing/
│       ├── no-self-invent/
│       ├── ascii-flowchart/
│       ├── stage-gate/
│       ├── sql-dialect-discipline/
│       ├── doc-numbering/
│       └── context-pointer/
├── config/                     # 领域配置(skill 级 fallback)
│   ├── compliance/
│   ├── tech-stack/
│   ├── domain-knowledge/
│   └── doc-naming/
├── examples/                   # 完整示例
│   └── 01-wms-warehouse/
├── templates/                  # 文档模板(12 个)
│   └── ...
└── scripts/                    # 自动化脚本(8 个)
    └── ...
    ├── doc-validate.py         # v1.2+ 文档格式校验
    ├── sql-dialect-check.py    # SQL 方言混用检查
    ├── full-qa-audit.py        # 6 大类全量 QA 审计
    ├── field-alignment-check.py # 字段对齐验证
    ├── parallel-delegate.sh    # 并行委派 Claude
    └── postprocess_prd_html.py # PRD HTML 后处理
```

## 脚本能力表

| 脚本 | 阶段 | 能力 | 依赖 |
|---|---|---|---|
| `scripts/smoke-test.sh` | 安装后 / CI | 文件完整性、链接、版本一致性、脚本 help 自检 | Bash + Python |
| `scripts/doc-validate.py` | 全阶段 | frontmatter、H1、章节、链接、代码块、占位符；支持模板模式 | Python 标准库 |
| `scripts/field-alignment-check.py` | 阶段 1/6/8/9 | Markdown 表格 + SQL DDL 字段对齐，支持 JSON | Python 标准库 |
| `scripts/sql-dialect-check.py` | 阶段 8/9 | Oracle / PostgreSQL / MySQL 方言混用检查 | Python 标准库 |
| `scripts/full-qa-audit.py` | 阶段 9 | 聚合文档校验、SQL、字段、编号、核心文档检查 | Python 标准库 |
| `scripts/parallel-delegate.sh` | 阶段 7 / 实施扩展 | 基于 Claude CLI 的任务文件并行委派，支持 dry-run | Bash + `claude` |
| `scripts/postprocess_prd_html.py` | 阶段 6 | PRD HTML 封面、目录、章节容器、响应式/打印样式 | Python 标准库 |
| `scripts/init-project-config.sh` | 项目启动 | 生成 4 个项目级配置文件 | Bash |
| `scripts/cookiecutter-gen.sh` | 项目启动 | 生成编号文档骨架 | cookiecutter |

## 工作流总览

```
9 阶段(分析-设计)            +    5 步实施(superpowers)
需求澄清 → BRD → 合规 →     →  brainstorming → design-an-interface
测试用例 → PRD → 开发设计    →  domain-modeling → writing-plans
→ QA → 交接                 →  tdd → executing-plans → verification
```

**走完整流程**:`/analysis-delivery-workflow`(9 阶段)+ `/using-superpowers`(5 步实施)
**做单件事**:直接 `/to-brd` `/to-prd` `/dev-design` 等任意 9 动作

详细见 [SKILL.md](SKILL.md) 或 [SPEC.md](SPEC.md#3-工作流定义)。

## 文档编号

每个项目目录里，按以下编号组织文档（强制）：

| 编号 | 文档 | 阶段 |
|---|---|---|
| 01 | 业务需求文档 BRD.md | 2 |
| 02 | 功能规格说明书 FSD.md | 8 |
| 03 | 数据模型设计.md | 8 |
| 04 | 合规评审.md | 3 |
| 05 | 产品需求文档 PRD.md | 6 |
| 06 | 开发设计说明书.md | 8 |
| 07 | 测试用例设计.md | 5 |
| 08 | 业务流程图.drawio | 2 |

## 示例

### 示例 1：医药物流 WMS 收货管理
完整迷你示例，含 BRD + 字段对齐分析 + ASCII 流程图。
详见 [examples/01-wms-warehouse/](examples/01-wms-warehouse/)

### 计划中的示例
- 示例 2：SaaS 后台（Node + React + PostgreSQL）— v2.0
- 示例 3：移动 App（Flutter + Firebase）— v2.0

## 依赖

- Python 3.8+
- Bash 4+
- Git
- pandoc（生成 DOCX/HTML，可选）
- drawio desktop（生成 PNG，可选）

## 路线图

| 版本 | 内容 | 计划时间 |
|---|---|---|
| v1.4.0-dev | **当前开发版**：拆分为 26 个独立 skill (mattpocock 风格) | 2026-06 |
| v1.1 | 项目级配置体系 + 阶段 8 简化 | 2026-06 |
| v1.2 | skill 自检 + 模板引擎化 | 2026-06 |
| v2.0 | 2 个新示例 + GitHub Actions + CONTRIBUTING | 2026-Q4 |
| v3.0 | drawio CLI + mermaid CLI + VSCode 扩展 | 2027 |

详见 [plan.md](plan.md)

## 贡献

| 角色 | 方式 |
|---|---|
| 用户 | 在 GitHub Issues 报 bug / 提需求 / 分享使用案例 |
| 贡献者 | Fork → 修改 → PR |

**优先欢迎的贡献**：
- 新的 `config/compliance/*.md`（你所在行业的合规规则）
- 新的 `config/tech-stack/*.md`（你熟悉的技术栈）
- 新的 `examples/*`（你做过的真实项目蒸馏版）
- 新的 `templates/*`（你团队在用的文档模板）
- 脚本 bug 修复

## 安全

- ❌ 严禁 DDL/DML 写操作（建表/改字段/插入/删除）
- ❌ 严禁对外 HTTP 请求（除用户明确授权外）
- ❌ 严禁破坏性 git 操作
- ✅ 仅允许 SELECT 查询 + 文件读写（仅限工作目录）

## 协议

MIT — 详见 [LICENSE](LICENSE)

## 相关链接

- [plan.md](plan.md) — 项目路线图
- [SPEC.md](SPEC.md) — 功能规格
- [CHANGELOG.md](CHANGELOG.md) — 版本历史
- [examples/01-wms-warehouse/](examples/01-wms-warehouse/) — 完整示例

---

**维护者**：Jason sun
**当前版本**：1.4.0-dev（2026-06-22）
