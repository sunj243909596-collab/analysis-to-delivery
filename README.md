# Analysis to Delivery

> 通用需求分析到开发实施工作流 — **26 个独立可组合 skill**、3 个完整行业示例、5 个 CI workflow。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-3.0.1-blue.svg)](plan.md)
[![Skills](https://img.shields.io/badge/skills-26-green.svg)](skills/)
[![Examples](https://img.shields.io/badge/examples-3-orange.svg)](examples/)
[![CI](https://img.shields.io/badge/CI-5%20workflows-purple.svg)](.github/workflows/)

## 它是什么

一个 Claude Code / Hermes 的 **skill 集合**,提供从「需求澄清」到「开发实施」的标准化工作流。

- **26 个独立可组合 skill** — 拆分为 2 router + 9 动作 + 1 编排 + 7 bridge + 7 纪律,职责单一,自由组合
- **3 个完整行业示例** — 医药 WMS / SaaS 订单 / 移动 App 积分,看完即可照搬到同类项目
- **5 个 GitHub Actions CI workflow** — smoke test / SQL 方言 / 文档校验 / 字段对齐 / 全量 QA 审计
- **流程图工具链** — ASCII → Mermaid / Drawio → SVG / PNG(命令行 + VSCode 集成)

**设计原则**:小而精、可组合、不拥有流程。每个 skill < 300 行,改一个不影响其他。

任何团队拿到这个 skill 之后:

1. 告诉 Claude 你的**领域**(医药/金融/SaaS/移动 App...)和**技术栈**(Java/Go/Python/Node...)
2. 用 `/ask-delivery` 选择对应 skill,或直接 `/analysis-delivery-workflow` 走完整流程
3. 产出可直接交给开发的设计文档(BRD/FSD/数据模型/PRD/开发设计/测试用例)

**默认不包含**:实际业务代码。若用户明确启用"实施扩展模式",可走 `/using-superpowers` 串接 superpowers 5 步实施。

## 核心特性

- ✅ **26 个独立 skill**(v1.4 拆分):2 router + 9 动作 + 1 编排 + 7 bridge + 7 discipline
- ✅ **3 个完整行业示例**(v2.0):医药 WMS / SaaS 订单 / 移动 App 积分
- ✅ **5 个 GitHub Actions workflow**(v2.0):smoke-test / sql-dialect / doc-validate / field-alignment / full-qa-audit
- ✅ **流程图工具链**(v3.0):ASCII → Mermaid/Drawio → SVG/PNG(命令行 + VSCode 集成)
- ✅ **VSCode 扩展**(v3.0):4 个命令直接桥接到 skill 脚本
- ✅ **可组合**:不强制流程,自由调任意 skill
- ✅ **可插拔配置**:`config/` 目录放行业/技术栈/领域知识库,按需加载
- ✅ **跨行业**:医药/金融/SaaS/移动 App 通用
- ✅ **跨技术栈**:Java/Go/Python/Node/Rust/.NET 全支持
- ✅ **社区治理**:CONTRIBUTING.md + Issue/PR 模板 + Conventional Commits

## 目录

- [它是什么](#它是什么)
- [核心特性](#核心特性)
- [安装](#安装)
- [快速开始](#快速开始)
- [26 个 skill 速查](#26-个-skill-速查)
- [3 个示例](#3-个示例)
- [📚 知识库配置(项目级)](#-知识库配置项目级)
- [🔧 工具链](#-工具链)
- [GitHub Actions CI](#github-actions-ci)
- [包含什么](#包含什么)
- [脚本能力表](#脚本能力表)
- [工作流总览](#工作流总览)
- [文档编号](#文档编号)
- [依赖](#依赖)
- [路线图](#路线图)
- [贡献](#贡献)
- [安全](#安全)
- [协议](#协议)

## 安装

### 一键安装(推荐)

```bash
curl -fsSL https://raw.githubusercontent.com/sunj243909596-collab/analysis-to-delivery/main/install.sh | bash
```

### 手动安装

```bash
# 稳定版(推荐生产用,锁定到 v3.0.0)
git clone --branch 3.0.0 --depth 1 https://github.com/sunj243909596-collab/analysis-to-delivery.git \
  ~/.claude/skills/analysis-to-delivery

# main 分支(尝鲜用,跟随最新提交)
git clone --depth 1 https://github.com/sunj243909596-collab/analysis-to-delivery.git \
  ~/.claude/skills/analysis-to-delivery
```

### 升级

```bash
cd ~/.claude/skills/analysis-to-delivery && git pull origin 3.0.0
```

### 安装选项

```bash
# Dry run(只检查不安装)
bash install.sh --dry-run

# 指定目标目录
bash install.sh --target /path/to/install

# 指定版本
bash install.sh --version v3.0.0

# 卸载
bash install.sh --uninstall
```

### 安装位置

脚本自动检测:
- 优先 `~/.claude/skills/`(Claude Code 用户)
- 回退 `~/.hermes/skills/`(Hermes 用户)

可用 `--target` 强制指定。

## 快速开始

### 0. 装完先跑 smoke test(v1.2+)

```bash
bash ~/.claude/skills/analysis-to-delivery/scripts/smoke-test.sh
```

确认文件完整后再用。✅ 全部通过即可放心;⚠️ 有警告可继续;❌ 有错误需先修复。

当前标准:**95+ ✅ / 0 ⚠️ / 0 ❌**(v3.0 后)

### 方式 1:斜杠命令(Claude Code)

```
/analysis-to-delivery
```

### 方式 2:自然语言

```
"使用 analysis-to-delivery 分析入库收货需求"
```

### 方式 3:项目启动

```
"我要做一个 SaaS CRM 系统,用 Node + React + PostgreSQL,请用 analysis-to-delivery 帮我走完需求到设计"
```

Claude 会自动:
1. 加载项目级 `*-path.md` 配置(若有,详见[📚 知识库配置](#-知识库配置项目级))
2. 加载 `config/compliance/none.md`(无强合规)
3. 加载 `config/tech-stack/node-nestjs.md`(如果存在)
4. 按 10 阶段工作流推进

## 26 个 skill 速查

| 类别 | 数量 | 触发方式 | 说明 |
|---|---|---|---|
| **Router** | 2 | 用户 `/<name>` | 入口路由 |
| **User-invoked 动作** | 9 | 用户 `/<name>` | 单步动作 |
| **Orchestration 编排** | 1 + 7 | 用户 + AI | 9 阶段流程 + 7 superpowers bridge |
| **Discipline 纪律** | 7 | AI 自动 | 模型自动调用,保证质量 |

### Router(2 个)

```
/ask-delivery            → 选择 skill 走流程
/using-superpowers       → 启用实施扩展模式(7 个 superpowers bridge)
```

### User-invoked 动作(9 个)— 单步

```
/setup-analysis-delivery → 生成项目级配置(knowledge/compliance/tech-stack/doc-naming/config-used)
/grill-task              → 阶段 1:AI 反复追问澄清需求
/to-brd                  → 阶段 2:生成业务需求文档(BRD)
/compliance-review       → 阶段 3:合规评审(GSP / 等保 / GDPR / PIPL)
/test-case-design        → 阶段 3.5:生成测试用例
/to-prd                  → 阶段 4:生成产品需求文档(PRD)
/dev-design              → 阶段 5-8:开发设计(FSD + 数据模型 + 开发设计说明书)
/qa-audit                → 阶段 9:QA 审计(6 大类)
/handoff                 → 阶段 10:交付清单
```

### Orchestration(1 个)— 走完整流程

```
/analysis-delivery-workflow  → 9 阶段分析设计 + 衔接 superpowers 实施
```

### 需求澄清门控(v3.x 新增)

`grill-task` 阶段新增 `scripts/task-confirm-check.py` 硬门控脚本：

- **5 项检查**：状态字段、12 词 TBD 扫描、5 章节完整、REVIEW 第八节为空、字段对齐 🔴/❓=0
- **12 词 TBD 红线**：`TBD` / `TODO` / `待定` / `稍后` / `下次` / `N/A` / `待确认` / `暂定` / `未定` / `待补充` / `⬜` / `❓`
- **白名单话术**：用户必须用以下 4 句之一才能进入下一阶段：
  - `我已全部确认，可以进入下一步`
  - `确认通过，进入 BRD`
  - `全部完成，继续`
  - `approved, proceed to next stage`
- **TASK_CONFIRM 模板状态字段**：硬约束为二态（⬜ / ✅），删除 🟡 中间态
- **双模式**：
  - `--strict`（默认）：5 项检查全部 BLOCK,任一失败 exit 1
  - `--loose`：Check 1(状态字段) / Check 2(TBD) 仍 BLOCK;Check 3/4/5 降级为 warning,exit 0
  - `--strict` 与 `--loose` 互斥（argparse 强制）

### Bridge(7 个)— 实施扩展

```
/brainstorming             /design-an-interface
/domain-modeling           /writing-plans
/tdd                       /executing-plans
/verification-before-completion
```

### Discipline(7 个)— AI 自动调用

```
no-field-guessing        no-self-invent          ascii-flowchart
stage-gate               sql-dialect-discipline  doc-numbering
context-pointer
```

## 3 个示例

| # | 名称 | 行业 | 技术栈 | 文件数 |
|---|---|---|---|---|
| 01 | [wms-warehouse](examples/01-wms-warehouse/) | 医药物流 WMS | Oracle + Spring Boot + Vue 3 | 12 |
| 02 | [saas-dashboard](examples/02-saas-dashboard/) | B2B SaaS 后台 | PostgreSQL + Express 5 + React 19 | 12 |
| 03 | [mobile-app](examples/03-mobile-app/) | B2C 移动 App | Firestore + Flutter 3.24 | 12 |

### 示例 1:医药物流 WMS 收货管理

完整迷你示例,含 BRD + 字段对齐分析 + ASCII 流程图 + 配置 5 件套。

```bash
cd examples/01-wms-warehouse
cat 01-业务需求文档\ BRD.md   # 业务需求
cat REVIEW_字段对齐分析.md    # Oracle 字段对齐
cat 业务流程图-状态流转.txt  # 状态机
```

**重点演示**:GSP 合规 / 2 位数字状态码 / Oracle 方言 / 巴枪扫码场景。

### 示例 2:SaaS 后台 — 客户订单管理

Node 22 + Express 5 + React 19 + PostgreSQL 16。

```bash
cd examples/02-saas-dashboard
cat 01-业务需求文档\ BRD.md   # 业务需求
cat REVIEW_字段对齐分析.md    # PG 字段对齐
cat 业务流程图-订单状态流转.txt  # 9 状态状态机
```

**重点演示**:多租户行级隔离 / PG 方言(NVL→COALESCE / ROWNUM→LIMIT)/ 字符串状态枚举 / 支付集成。

### 示例 3:移动 App — 会员积分管理

Flutter 3.24 + Cloud Firestore + Cloud Functions。

```bash
cd examples/03-mobile-app
cat 01-业务需求文档\ BRD.md   # 业务需求
cat REVIEW_字段对齐分析.md    # Firestore 字段对齐
cat 业务流程图-积分状态流转.txt  # 双状态机
```

**重点演示**:FIFO 批次消耗积分 / FCM 推送 / 离线优先架构 / PIPL 轻合规 / Riverpod 状态管理。

### 跨示例对比

| 维度 | 01-wms | 02-saas | 03-mobile |
|---|---|---|---|
| 数据库 | Oracle 19c | PostgreSQL 16 | Cloud Firestore |
| 后端 | Spring Boot 3 | Express 5 | Cloud Functions |
| 前端 | Vue 3 PC | React 19 Web | Flutter(iOS+Android)|
| 合规 | GSP 医药 | None(商业)| PIPL(C 端)|
| 多租户 | 单租户 | 行级多租户 | 用户维度 |
| 实时性 | 异步队列 | T+1 | 实时 listener |
| 离线 | 不涉及 | 不涉及 | 必备 |
| 推送 | 不涉及 | 不涉及 | FCM |

## 📚 知识库配置(项目级)

> **痛点回顾**:v1.0 把所有 config 放在 skill 内 `config/`,真实项目交付时配置不准、难维护。
> **v1.1 调整**:**项目级优先 + skill 级 fallback**。

### 三层优先级

```
项目级配置  >  Skill 级 config/  >  全局默认值
(本项目根)    (skill 内部)         (运行时推断)
```

Claude 启动时按这个顺序找配置,找到即用。

### 项目级配置(5 件套)

每个真实项目根目录下生成这 5 个文件:

| 文件 | 用途 | 示例内容 |
|---|---|---|
| `knowledge-path.md` | 列出真实知识库路径 | "WMOS 表结构在 `/root/WMOS 知识库/01-WMOS核心/`" |
| `tech-stack-path.md` | 分端列技术栈 | "后端 Java 11 / 前端 Vue 3 / 数据库 Oracle" |
| `compliance-path.md` | 启用合规 + 路径 | "启用 GSP,知识库在 `/root/WMOS 知识库/03-GSP法规/`" |
| `doc-naming.md` | 文档编号规则 | "01-08 编号,文档存项目根" |
| `config-used.md` | 配置汇总 + ADR | "为什么用行级多租户?" |

### 一键生成项目配置

```bash
bash scripts/init-project-config.sh /path/to/your-project
```

生成 4 个空模板,用户填好后 Claude 自动识别。

### Skill 级 fallback(`config/`)

skill 自带少量 fallback,仅作"格式参考样例",**不追求覆盖广度**:

```
config/
├── compliance/
│   ├── gsp.md        # 医药 GSP 示例
│   ├── none.md       # 无强合规默认
│   └── template.md   # 新增合规的模板
├── tech-stack/
│   ├── java-spring.md  # Java + Spring Boot
│   └── template.md     # 新增技术栈的模板
├── domain-knowledge/
└── doc-naming/
```

### 实战示例

看 [examples/02-saas-dashboard/config-used.md](examples/02-saas-dashboard/config-used.md):

```markdown
# 配置使用说明

## 一、配置清单
| 配置项 | 路径 | 用途 |
|---|---|---|
| 合规 | config/compliance/none.md | 无强合规 |
| 知识库 | knowledge-path.md | PostgreSQL + Node + React |
| 技术栈 | tech-stack-path.md | Node 22 + Express 5 + React 19 + PG 16 |
| ... | | |

## 二、与全局默认的差异
| 配置项 | 全局默认 | 本项目 | 差异 |
|---|---|---|---|
| 数据库方言 | Oracle | PostgreSQL | NVL→COALESCE |
| 状态码 | 2 位数字 | 字符串枚举 | draft/submitted/paid |
| 多租户 | 单租户 | 多租户(行级)| 架构差异 |
| ... | | | |
```

这样每个真实项目都能"配置自描述",skill 升级不影响项目。

## 🔧 工具链

### 流程图渲染(v3.0)

将 examples/ 中的 ASCII 流程图转为可视化图形 — 支持两条路径(Mermaid 或 Drawio):

**路径 1:Mermaid → SVG/PNG**(适合网页嵌入 / GitHub README)

```bash
# 单文件
bash scripts/flow-export.sh examples/02-saas-dashboard/业务流程图-订单状态流转.txt

# 批量(整个目录)
bash scripts/flow-export.sh --batch examples/02-saas-dashboard/ png ./diagrams

# 只转换,不渲染(生成 .mmd 源码)
python3 scripts/flow-to-mermaid.py --batch examples/02-saas-dashboard/
```

**路径 2:Drawio XML**(适合在线编辑 / 精细布局)

```bash
# 单文件
python3 scripts/flow-to-drawio.py examples/02-saas-dashboard/业务流程图-订单状态流转.txt
# → 生成 业务流程图-订单状态流转.drawio(可用 https://app.diagrams.net/ 打开)

# 批量(整个目录)
python3 scripts/flow-to-drawio.py --batch examples/02-saas-dashboard/
```

**前置依赖**:
- Mermaid 路径:`npm install -g @mermaid-js/mermaid-cli`
- Drawio 路径:仅 Python 3.8+,**无外部依赖**(drawio desktop 可选,用于打开编辑)

**支持图类型**:状态机(自动检测 ▼ 垂直箭头)/ 简单连接图。
**限制**:复杂泳道图(swimlane)需手动整理。

**两条路径对比**:

| 维度 | Mermaid | Drawio |
|---|---|---|
| 输出 | SVG / PNG / 源码 | XML(可编辑) |
| 编辑 | 需改 ASCII 重转 | drawio 桌面/网页直接拖拽 |
| 嵌入 | GitHub README 直接渲染 | 需截图或嵌入 .drawio 文件 |
| 精细布局 | 一般 | 强(自由拖拽) |
| 依赖 | mmdc(Node) | 仅 Python |

### VSCode 扩展(v3.0)

提供 4 个 IDE 内命令:[vscode-extension/](vscode-extension/)

| 命令 | 说明 |
|---|---|
| `Analysis to Delivery: Apply Skill` | 选择 + 打开 skill |
| `Analysis to Delivery: Run Smoke Test` | 跑 smoke-test.sh |
| `Analysis to Delivery: Render Flow Chart` | 右键 → ASCII → SVG |
| `Analysis to Delivery: Open Documentation` | 快速打开 README 等 |

**安装**:
```bash
cd vscode-extension
npm install
npm run compile
# F5 启动 Extension Development Host
# 或打包 .vsix:
npm run package
code --install-extension analysis-to-delivery-0.1.0.vsix
```

**配置**(`settings.json`):
```json
{
  "analysisToDelivery.skillsPath": "${userHome}/.claude/skills/analysis-to-delivery",
  "analysisToDelivery.mermaidCli": "mmdc",
  "analysisToDelivery.defaultFormat": "svg"
}
```

## GitHub Actions CI

5 个 workflow 自动验证(.github/workflows/):

| Workflow | 触发 | 检查 |
|---|---|---|
| `smoke-test.yml` | push/PR | Skill 集合结构 + 元数据 |
| `sql-dialect-check.yml` | push/PR | Oracle / PG 双方言校验 |
| `doc-validate.yml` | push/PR | Markdown 格式 / 表格 / 代码块 |
| `field-alignment-check.yml` | push/PR | 字段对齐 / 多租户 / 整数 |
| `full-qa-audit.yml` | push to main / release | 4 项聚合,失败阻断 merge |

详见 [.github/workflows/](.github/workflows/) 和 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 包含什么

```
analysis-to-delivery/
├── SKILL.md                    # 顶层入口(指向 skills/ 下)
├── install.sh                  # 一键安装
├── README.md                   # 本文件
├── plan.md                     # 项目路线图
├── SPEC.md                     # 功能规格
├── CHANGELOG.md                # 版本历史
├── CONTRIBUTING.md             # 贡献者指南
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
├── examples/                   # 3 个完整示例(v2.0)
│   ├── 01-wms-warehouse/       # 医药物流 WMS(Oracle)
│   ├── 02-saas-dashboard/      # SaaS 订单(Node + React + PG)
│   └── 03-mobile-app/          # 移动 App(Flutter + Firebase)
├── templates/                  # 文档模板(12 个)
├── scripts/                    # 自动化脚本(v2.0+ 共 10 个)
│   ├── smoke-test.sh
│   ├── doc-validate.py
│   ├── sql-dialect-check.py
│   ├── full-qa-audit.py
│   ├── field-alignment-check.py
│   ├── parallel-delegate.sh
│   ├── postprocess_prd_html.py
│   ├── init-project-config.sh
│   ├── cookiecutter-gen.sh
│   ├── flow-to-mermaid.py      # v3.0:ASCII → Mermaid
│   ├── flow-to-drawio.py       # v3.0:ASCII → Drawio XML
│   └── flow-export.sh          # v3.0:Mermaid → SVG/PNG
├── .github/
│   ├── workflows/              # 5 个 CI(v2.0)
│   │   ├── smoke-test.yml
│   │   ├── sql-dialect-check.yml
│   │   ├── doc-validate.yml
│   │   ├── field-alignment-check.yml
│   │   └── full-qa-audit.yml
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── PULL_REQUEST_TEMPLATE.md
└── vscode-extension/           # VSCode 扩展(v3.0)
    ├── package.json
    ├── src/extension.ts
    └── README.md
```

## 脚本能力表

| 脚本 | 阶段 | 能力 | 依赖 |
|---|---|---|---|
| `scripts/smoke-test.sh` | 安装后 / CI | 文件完整性、链接、版本一致性、脚本 help 自检 | Bash + Python |
| `scripts/doc-validate.py` | 全阶段 | frontmatter、H1、章节、链接、代码块、占位符 | Python 标准库 |
| `scripts/field-alignment-check.py` | 阶段 1/6/8/9 | Markdown 表格 + SQL DDL 字段对齐 | Python 标准库 |
| `scripts/sql-dialect-check.py` | 阶段 8/9 | Oracle / PostgreSQL / MySQL 方言混用检查 | Python 标准库 |
| `scripts/full-qa-audit.py` | 阶段 9 | 聚合文档校验、SQL、字段、编号、核心文档检查 | Python 标准库 |
| `scripts/parallel-delegate.sh` | 阶段 7 / 实施扩展 | 基于 Claude CLI 的任务文件并行委派 | Bash + `claude` |
| `scripts/postprocess_prd_html.py` | 阶段 6 | PRD HTML 封面、目录、章节容器 | Python 标准库 |
| `scripts/init-project-config.sh` | 项目启动 | 生成 4 个项目级配置文件 | Bash |
| `scripts/cookiecutter-gen.sh` | 项目启动 | 生成编号文档骨架 | cookiecutter |
| `scripts/flow-to-mermaid.py` | v3.0 | ASCII 流程图 → Mermaid 源码 | Python 标准库 |
| `scripts/flow-to-drawio.py` | v3.0 | ASCII 流程图 → Drawio XML(可在线编辑) | Python 标准库 |
| `scripts/flow-export.sh` | v3.0 | Mermaid → SVG/PNG(批量 / 单文件) | mermaid-cli |

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

每个项目目录里,按以下编号组织文档(强制):

| 编号 | 文档 | 阶段 |
|---|---|---|
| 01 | 业务需求文档 BRD.md | 2 |
| 02 | 功能规格说明书 FSD.md | 8(可省略)|
| 03 | 数据模型设计.md | 8 |
| 04 | 合规评审.md | 3(可省略)|
| 05 | 产品需求文档 PRD.md | 4 |
| 06 | 开发设计说明书.md | 8 |
| 07 | 测试用例设计.md | 3 |
| 08 | 业务流程图.drawio | 2 |

## 依赖

| 依赖 | 版本 | 必需 | 用途 |
|---|---|---|---|
| Python | 3.8+ | ✅ | 验证脚本 |
| Bash | 4+ | ✅ | 多个 shell 脚本 |
| Git | 2+ | ✅ | 安装 / 升级 |
| Node.js | 20+ | ⚠️ 可选 | VSCode 扩展构建 + mermaid-cli |
| mermaid-cli | latest | ⚠️ 可选 | 流程图渲染(`flow-export.sh`) |
| pandoc | latest | ⚠️ 可选 | 生成 DOCX/HTML |
| cookiecutter | latest | ⚠️ 可选 | 项目骨架生成 |

## 路线图

| 版本 | 内容 | 状态 |
|---|---|---|
| v1.0 | MVP,10 阶段工作流 + 1 个示例 | ✅ 2026-06 |
| v1.1 | 项目级配置体系 + 阶段 8 简化 | ✅ 2026-06 |
| v1.2 | skill 自检 + 模板引擎化 | ✅ 2026-06 |
| v1.3 | 双模式 + 阶段门控 + 设计回测 + 任务复盘 | ✅ 2026-06 |
| v1.4 | 拆分为 26 个独立 skill(mattpocock 风格)| ✅ 2026-06 |
| v2.0 | **当前**:2 个新示例 + GitHub Actions + CONTRIBUTING | ✅ 2026-06 |
| v3.0 | drawio/mermaid CLI + VSCode 扩展 | ✅ 2026-06 |
| v4.0 | 国际化 + 团队协作(计划) | ⬜ 待开始 |

详见 [plan.md](plan.md)。

## 贡献

| 角色 | 方式 |
|---|---|
| 用户 | 在 [GitHub Issues](https://github.com/sunj243909596-collab/analysis-to-delivery/issues) 报 bug / 提需求 / 分享使用案例 |
| 贡献者 | Fork → 修改 → PR(详见 [CONTRIBUTING.md](CONTRIBUTING.md))|

**优先欢迎的贡献**:
- 新的 `config/compliance/*.md`(你所在行业的合规规则)
- 新的 `config/tech-stack/*.md`(你熟悉的技术栈)
- 新的 `examples/*`(你做过的真实项目蒸馏版)
- 新的 `templates/*`(你团队在用的文档模板)
- 脚本 bug 修复
- VSCode 扩展功能(贡献到 `vscode-extension/`)

## 安全

- ❌ 严禁 DDL/DML 写操作(建表/改字段/插入/删除)
- ❌ 严禁对外 HTTP 请求(除用户明确授权外)
- ❌ 严禁破坏性 git 操作
- ✅ 仅允许 SELECT 查询 + 文件读写(仅限工作目录)

## 协议

MIT — 详见 [LICENSE](LICENSE)

## 相关链接

- [plan.md](plan.md) — 项目路线图
- [SPEC.md](SPEC.md) — 功能规格
- [CHANGELOG.md](CHANGELOG.md) — 版本历史
- [CONTRIBUTING.md](CONTRIBUTING.md) — 贡献者指南
- [SKILL.md](SKILL.md) — 顶层 skill 入口
- [examples/](examples/) — 3 个完整示例
- [.github/workflows/](.github/workflows/) — 5 个 CI workflow

---

**维护者**:Jason SUN (`sunj243909596@gmail.com`)
**当前版本**:3.0.0-dev(2026-06-22)
**GitHub**:https://github.com/sunj243909596-collab/analysis-to-delivery