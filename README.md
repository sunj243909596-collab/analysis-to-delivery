# Analysis to Delivery

> 通用需求分析到开发设计工作流 — 跨行业、跨技术栈的 10 阶段标准化流程。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0--mvp-blue.svg)](plan.md)

## 它是什么

一个 Claude Code / Hermes 的 skill，提供从「需求澄清」到「开发设计」的标准化工作流。

任何团队拿到这个 skill 之后：
1. 告诉 Claude 你的**领域**（医药/金融/SaaS/移动 App...）和**技术栈**（Java/Go/Python/Node...）
2. Claude 自动加载对应配置，按 10 阶段工作流推进
3. 产出可直接交给开发的设计文档（BRD/FSD/数据模型/PRD/开发设计/测试用例）

**不包含**：实际业务代码（用 `wms-code-implementation` 等编码 skill）。

## 核心特性

- ✅ **10 阶段工作流**：需求澄清 → 业务流程 → 合规评审 → 系统方案 → 测试用例 → PRD → 委派 → 开发设计 → QA → 交接
- ✅ **可插拔配置**：`config/` 目录放行业/技术栈/领域知识库，按需加载
- ✅ **跨行业**：医药/金融/SaaS/移动 App 通用
- ✅ **跨技术栈**：Java/Go/Python/Node/Rust/.NET 全支持
- ✅ **3 个示例**：内置 1 个完整示例（医药 WMS 收货管理），其他行业 2 个规划中
- ✅ **6 个自动化脚本**：SQL 方言检查、字段对齐、QA 审计、并行委派、HTML 后处理
- ✅ **12 个文档模板**：从需求确认表到开发设计说明书
- ✅ **10+ 个方法论文档**：流程图规范、字段对齐、Draw.io 生成等

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
├── SKILL.md                    # 主文档（10 阶段工作流）
├── install.sh                  # 一键安装
├── README.md                   # 本文件
├── plan.md                     # 项目路线图
├── SPEC.md                     # 功能规格
├── CHANGELOG.md                # 版本历史
├── LICENSE                     # MIT
├── config/                     # 领域配置（按需加载）
│   ├── compliance/             # 合规规则（gsp / none / template）
│   ├── tech-stack/             # 技术栈规范（java-spring / frontend-vue / template）
│   ├── domain-knowledge/       # 领域知识库引用（template）
│   └── doc-naming/             # 文档命名规范（template）
├── examples/                   # 完整示例
│   └── 01-wms-warehouse/       # 医药物流 WMS 收货管理（完整迷你示例）
├── references/                 # 方法论文档
│   ├── workflow-discipline.md
│   ├── field-alignment.md
│   ├── flow-chart-ascii.md
│   ├── figma-design-doc.md
│   ├── prd-output.md
│   ├── v1-v2-versioning.md
│   ├── qa-audit-checklist.md
│   ├── safe-bulk-editing.md
│   ├── drawio-guide.md
│   └── doc-numbering.md
├── templates/                  # 文档模板（占位）
│   ├── TASK_CONFIRM.md         # 阶段 1
│   ├── REVIEW_需求确认书.md     # 阶段 1
│   ├── REVIEW_字段对齐分析.md   # 阶段 1
│   ├── AGENTS.md               # 阶段 7
│   ├── BRD.md                  # 阶段 2
│   ├── FSD.md                  # 阶段 8 (V1)
│   ├── 数据模型设计.md           # 阶段 8 (V1)
│   ├── 合规评审.md              # 阶段 3
│   ├── PRD.md                  # 阶段 6
│   ├── 开发设计说明书.md         # 阶段 8 (V2)
│   └── TEST_CASE_DESIGN.md     # 阶段 5
└── scripts/                    # 自动化脚本
    ├── install.sh
    ├── sql-dialect-check.py    # SQL 方言混用检查
    ├── full-qa-audit.py        # 6 大类全量 QA 审计
    ├── field-alignment-check.py # 字段对齐验证
    ├── parallel-delegate.sh    # 并行委派 Claude
    └── postprocess_prd_html.py # PRD HTML 后处理
```

## 工作流总览

```
需求澄清 → 业务流程 → 合规评审 → 系统方案 → 测试用例
    ↓
PRD 生成 → 文档委派 → 开发设计(V1→V2) → QA 审计 → 代码交接
```

详细每个阶段见 [SKILL.md](SKILL.md) 或 [SPEC.md](SPEC.md#3-工作流定义)。

## 文档编号

每个项目目录里，按以下编号组织文档（强制）：

| 编号 | 文档 | 阶段 |
|---|---|---|
| 01 | 业务需求文档 BRD.md | 2 |
| 02 | 功能规格说明书 FSD.md | 8 (V1) |
| 03 | 数据模型设计.md | 8 (V1) |
| 04 | 合规评审.md | 3 |
| 05 | 产品需求文档 PRD.md | 6 |
| 06 | 开发设计说明书.md | 8 (V2) |
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
| v1.0 MVP | 当前版本 | 2026-06 |
| v1.1 | 配置库完善（5-8 个合规、6-8 个技术栈） | 2026-Q3 |
| v1.2 | skill 自检 + 模板引擎化 | 2026-Q3 |
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
**当前版本**：1.0.0-mvp（2026-06-22）
