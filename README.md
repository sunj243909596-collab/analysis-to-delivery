# Analysis to Delivery

> 通用需求分析到开发实施工作流 — **26 个独立可组合 skill**、3 个完整行业示例、13 个 CI workflow、26 个自动化脚本、15 个 pytest 测试。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-4.0.0-blue.svg)](plan.md)
[![Skills](https://img.shields.io/badge/skills-26-green.svg)](skills/)
[![Examples](https://img.shields.io/badge/examples-3-orange.svg)](examples/)
[![CI](https://img.shields.io/badge/CI-13%20workflows-purple.svg)](.github/workflows/)
[![Scripts](https://img.shields.io/badge/scripts-26-blue.svg)](scripts/)
[![Tests](https://img.shields.io/badge/tests-15%20pytest-green.svg)](tests/)

## 它是什么

一个面向 Claude Code / Hermes / Codex / OpenCode 等 agentic coding assistants 的 **agent-neutral skill/workflow 集合**,提供从「需求澄清」到「开发实施」的标准化工作流。

- **26 个独立可组合 skill** — 拆分为 2 router + 9 动作 + 1 编排 + 7 bridge + 7 纪律,职责单一,自由组合
- **3 个完整行业示例** — 医药 WMS / SaaS 订单 / 移动 App 积分,看完即可照搬到同类项目
- **5 个 GitHub Actions CI workflow** — smoke test / SQL 方言 / 文档校验 / 字段对齐 / 全量 QA 审计
- **流程图工具链** — ASCII → Mermaid / Drawio → SVG / PNG(命令行 + VSCode 集成)

**设计原则**:小而精、可组合、不拥有流程。每个 skill < 300 行,改一个不影响其他。

任何团队拿到这个 skill 之后:

1. 告诉你的 agent 你的**领域**(医药/金融/SaaS/移动 App...)和**技术栈**(Java/Go/Python/Node...)
2. 用 `/ask-delivery` 选择对应 skill,或直接 `/analysis-delivery-workflow` 走完整流程(不支持 slash command 的 agent 可用自然语言触发)
3. 产出可直接交给开发的设计文档(BRD/FSD/数据模型/PRD/开发设计/测试用例)

**默认不包含**:实际业务代码。若用户明确启用"实施扩展模式",可走 `/using-superpowers` 串接 superpowers 5 步实施。

## 核心特性

- ✅ **26 个独立 skill** — 2 router + 9 动作 + 1 编排 + 7 bridge + 7 discipline,职责单一,自由组合
- ✅ **3 个完整行业示例** — 医药 WMS / SaaS 订单 / 移动 App 积分,各 16 文件,看完照搬
- ✅ **26 个自动化脚本** — 7 阶段门控 + 5 静态审计 + 4 元数据校验 + 3 流程图工具 + 5 基础设施 + 2 状态管理
- ✅ **13 个 GitHub Actions workflow** — smoke-test / sql-dialect / doc-validate / field-alignment / full-qa-audit + 8 个 P0/P1 增量校验
- ✅ **15 个 pytest 测试** — 每个 gate 脚本有对应测试,覆盖 CLI / 双模式 / 互斥参数 / 边界条件
- ✅ **流程图工具链** — ASCII → Mermaid/Drawio → SVG/PNG(命令行 + VSCode 集成)
- ✅ **VSCode 扩展** — 4 个命令直接桥接到 skill 脚本
- ✅ **可组合** — 不强制流程,自由调任意 skill
- ✅ **可插拔配置** — `config/` 目录放行业/技术栈/领域知识库,按需加载
- ✅ **框架层通用** — 流程骨架/门控/纪律与具体语言无关(见[覆盖范围](#覆盖范围已覆盖-vs-未覆盖))
- ✅ **社区治理** — CONTRIBUTING.md + Issue/PR 模板 + Conventional Commits

## 目录

- [它是什么](#它是什么)
- [核心特性](#核心特性)
- [覆盖范围(已覆盖 vs 未覆盖)](#覆盖范围已覆盖-vs-未覆盖)
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

## 覆盖范围(已覆盖 vs 未覆盖)

> **诚实声明**:本仓库**框架层通用**(流程骨架/门控/纪律与具体语言无关),
> 但**默认示例与 config 只覆盖 3 个领域**(医药 WMS / SaaS 后台 / 移动 App)。
> 其他行业/技术栈需用户在项目级补 `knowledge-path.md` / `tech-stack-path.md` / `compliance/`。

| 维度 | 已覆盖(开箱即用) | 未覆盖(需用户补 config) |
|---|---|---|
| **流程骨架** | 9 阶段工作流、3 层门控、白名单签字纪律、纪律清单(7 个) | — |
| **领域** | 医药物流 WMS / SaaS 后台 / 移动 App(3 个 example) | 金融 / 教育 / 医疗 HIS / 制造 MES / 物流 TMS… |
| **技术栈** | Spring Boot + Vue 3 / Node + React / Flutter + Firebase | Go / Rust / .NET / K8s 原生 / 函数计算… |
| **数据库** | Oracle 11g/19c / PostgreSQL / MySQL(注:Oracle 是默认示例) | DB2 / SQL Server / TiDB / 大数据 Hive / ClickHouse… |
| **合规体系** | 中国 GSP(药品经营质量管理规范) | GAMP 5 / ISO 13485 / HIPAA / GDPR / 等保 2.0… |
| **门控脚本** | 12 个(setup / brd / compliance / prd / dev-design-backtest…)| — |
| **VSCode 集成** | 4 个命令(mmdc / drawio / flow-export / 新建文件) | IntelliJ / Vim / Emacs 插件 |

**如何补 config**:在项目根放 3 个 `*-path.md` + 1 个 `compliance/`,详见 `/setup-analysis-delivery` skill。

## 安装

### 平台支持

安装方式按运行环境选择:

| 平台 | 推荐方式 | 说明 |
|---|---|---|
| Linux / Ubuntu / Debian / Fedora / Arch / CentOS | Bash 一键安装或 `git clone` | 需要 `bash`、`git`;一键安装还需要 `curl` |
| macOS | Bash 一键安装或 `git clone` | 建议先确认 `git --version` 可用 |
| Windows + WSL | 在 WSL 里运行 Linux 安装命令 | 推荐 Windows 用户使用,路径在 WSL 用户目录下 |
| Windows + Git Bash | 在 Git Bash 里运行 Bash 安装命令 | 适合已安装 Git for Windows 的用户 |
| Windows PowerShell / CMD | 手动 `git clone` | 不直接运行 `install.sh`;用 PowerShell 示例命令 |

### Linux / macOS / WSL / Git Bash 一键安装(推荐)

```bash
curl -fsSL https://raw.githubusercontent.com/BlueprintOS/analysis-to-delivery/main/install.sh | bash
```

指定 agent:

```bash
curl -fsSL https://raw.githubusercontent.com/BlueprintOS/analysis-to-delivery/main/install.sh | bash -s -- --agent codex
curl -fsSL https://raw.githubusercontent.com/BlueprintOS/analysis-to-delivery/main/install.sh | bash -s -- --agent claude
curl -fsSL https://raw.githubusercontent.com/BlueprintOS/analysis-to-delivery/main/install.sh | bash -s -- --agent opencode
```

### Linux / macOS / WSL / Git Bash 手动安装

```bash
# 稳定版(推荐生产用,锁定到 v4.0.0)
git clone --branch 4.0.0 --depth 1 https://github.com/BlueprintOS/analysis-to-delivery.git \
  ~/.codex/skills/analysis-to-delivery

# main 分支(尝鲜用,跟随最新提交)
git clone --depth 1 https://github.com/BlueprintOS/analysis-to-delivery.git \
  ~/.codex/skills/analysis-to-delivery
```

也可以把目标目录换成对应 agent 的 skills 目录,或用项目级 `AGENTS.md` 直接引用本仓库。

### Windows PowerShell 手动安装

PowerShell 不直接运行 `install.sh`。请用 `git clone` 安装到对应 agent 的 skills 目录:

```powershell
# Codex
git clone --branch 4.0.0 --depth 1 https://github.com/BlueprintOS/analysis-to-delivery.git "$env:USERPROFILE\.codex\skills\analysis-to-delivery"

# Claude Code
git clone --branch 4.0.0 --depth 1 https://github.com/BlueprintOS/analysis-to-delivery.git "$env:USERPROFILE\.claude\skills\analysis-to-delivery"

# Hermes
git clone --branch 4.0.0 --depth 1 https://github.com/BlueprintOS/analysis-to-delivery.git "$env:USERPROFILE\.hermes\skills\analysis-to-delivery"

# OpenCode
git clone --branch 4.0.0 --depth 1 https://github.com/BlueprintOS/analysis-to-delivery.git "$env:USERPROFILE\.opencode\skills\analysis-to-delivery"
```

如果目标目录的父目录不存在,先创建:

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills"
```

### Windows CMD 手动安装

```bat
REM Codex
git clone --branch 4.0.0 --depth 1 https://github.com/BlueprintOS/analysis-to-delivery.git "%USERPROFILE%\.codex\skills\analysis-to-delivery"

REM Claude Code
git clone --branch 4.0.0 --depth 1 https://github.com/BlueprintOS/analysis-to-delivery.git "%USERPROFILE%\.claude\skills\analysis-to-delivery"
```

### 升级

```bash
cd <SKILL_ROOT>/analysis-to-delivery && git pull origin main
```

PowerShell 升级:

```powershell
cd "$env:USERPROFILE\.codex\skills\analysis-to-delivery"
git pull origin main
```

### 安装选项

```bash
# Dry run(只检查不安装)
bash install.sh --dry-run

# 指定 agent 默认目录
bash install.sh --agent claude
bash install.sh --agent hermes
bash install.sh --agent codex
bash install.sh --agent opencode

# 指定目标目录
bash install.sh --target /path/to/install

# 指定版本
bash install.sh --version v4.0.0

# 卸载(会清理已知 agent skills 目录中的本 skill)
bash install.sh --uninstall
```

### 卸载

Linux / macOS / WSL / Git Bash:

```bash
# 在仓库目录内执行
bash install.sh --uninstall

# 或手动删除指定 agent 目录
rm -rf ~/.codex/skills/analysis-to-delivery
rm -rf ~/.claude/skills/analysis-to-delivery
rm -rf ~/.hermes/skills/analysis-to-delivery
rm -rf ~/.opencode/skills/analysis-to-delivery
```

Windows PowerShell:

```powershell
# Codex
Remove-Item -Recurse -Force "$env:USERPROFILE\.codex\skills\analysis-to-delivery"

# Claude Code
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\skills\analysis-to-delivery"

# Hermes
Remove-Item -Recurse -Force "$env:USERPROFILE\.hermes\skills\analysis-to-delivery"

# OpenCode
Remove-Item -Recurse -Force "$env:USERPROFILE\.opencode\skills\analysis-to-delivery"
```

Windows CMD:

```bat
REM Codex
rmdir /s /q "%USERPROFILE%\.codex\skills\analysis-to-delivery"

REM Claude Code
rmdir /s /q "%USERPROFILE%\.claude\skills\analysis-to-delivery"

REM Hermes
rmdir /s /q "%USERPROFILE%\.hermes\skills\analysis-to-delivery"

REM OpenCode
rmdir /s /q "%USERPROFILE%\.opencode\skills\analysis-to-delivery"
```

### 安装位置

脚本自动检测已存在的 agent 目录:
- `~/.claude/skills/`(Claude Code)
- `~/.hermes/skills/`(Hermes)
- `~/.codex/skills/` 或 `$CODEX_HOME/skills/`(Codex)
- `~/.opencode/skills/` 或 `$OPENCODE_HOME/skills/`(OpenCode,若本地采用该目录约定)

可用 `--agent` 选择默认目录,或用 `--target` 强制指定。更多说明见 `docs/adapters/`。

### Agent 兼容性

核心工作流是 agent-neutral 的 Markdown + CLI 脚本;不同 agent 只在入口、命令触发和子代理能力上有差异。

| Agent | 推荐接入 | 说明 |
|---|---|---|
| Claude Code | `--agent claude` 或 `~/.claude/skills` | 原生 skill / slash command 体验最佳 |
| Hermes | `--agent hermes` 或 `~/.hermes/skills` | 沿用 Claude 风格 skill 目录 |
| Codex | `--agent codex` 或 `$CODEX_HOME/skills` | 通过 `SKILL.md`、`AGENTS.md` 和脚本门控接入 |
| OpenCode | `--agent opencode` 或 `--target` | 优先用项目级 `AGENTS.md` + CLI 脚本接入 |

不支持 slash command 的 agent 可直接用自然语言触发,例如:"使用 analysis-to-delivery 的 `/grill-task` 流程澄清这个需求"。

## 快速通道

跳过 router,直接按目标选:

| 目标 | 命令 |
|---|---|
| 配置项目 | `/setup-analysis-delivery` |
| 跑 5 项门控全套 | `bash scripts/smoke-test.sh` |
| 看项目走到哪个阶段 | `python3 scripts/analysis-state.py status` |
| ASCII → Mermaid | `python3 scripts/flow-to-mermaid.py file.txt` |
| 校验所有 skill 是否合规 | `python3 scripts/discipline-lint.py skills/` |
| 校验 Required rules / paths 声明 | `python3 scripts/rules-path-lint.py <repo>` |
| 校验目标边界与分期 | `python3 scripts/goal-boundary-check.py <project_dir>` |

## 逆向使用

不是"需求 → 设计",而是**已有产物需要后向追溯**:

| 已有产物 | 逆向动作 |
|---|---|
| `01-BRD.md` 已写,字段不确定 | `python3 scripts/field-alignment-check.py <project>` |
| `05-PRD.md` 与 BRD 冲突 | 回到 `/grill-task` 重对齐 |
| `06-开发设计.md` 与代码不一致 | 直接 `/qa-audit` 找偏差 |
| `09-QA审计报告.md` P0 列表 | 逐项修复后重跑 `full-qa-audit.py` |
| 状态文件 `.analysis-delivery-state.json` 在 | `python3 scripts/analysis-state.py status` 看中断阶段 |

## 度量

`python3 scripts/analysis-state.py metrics [--json]` 输出 5 项:

| # | 指标 | 含义 |
|---|---|---|
| 1 | 总 gate 调用次数 | 整套流程自动化门控累计调用 |
| 2 | 总签字次数 | 用户白名单话术累计签字 |
| 3 | gate 拦截次数 | 各 gate 脚本失败次数(按脚本名) |
| 4 | 各阶段重试次数 | 哪些阶段反复回去修 |
| 5 | 阶段用时(分钟) | 已签字阶段耗时(开始 → 签字) |

**用途**:找流程瓶颈 / 门控过严过松。详见 `rules/stage-gate.md` §度量章节。

## 快速开始

### 0. 装完先跑 smoke test(v1.2+)

```bash
bash <SKILL_ROOT>/analysis-to-delivery/scripts/smoke-test.sh
```

确认文件完整后再用。✅ 全部通过即可放心;⚠️ 有警告可继续;❌ 有错误需先修复。

当前标准:**95+ ✅ / 0 ⚠️ / 0 ❌**(v3.0 后)

### 方式 1:斜杠命令(支持 slash command 的 agent)

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

Agent 会自动:
1. 加载项目级 `*-path.md` 配置(若有,详见[📚 知识库配置](#-知识库配置项目级))
2. 加载 `config/compliance/none.md`(无强合规)
3. 加载 `config/tech-stack/node-nestjs.md`(如果存在)
4. 按 9 阶段工作流推进

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
/setup-analysis-delivery → 生成项目级配置(knowledge/compliance/tech-stack/doc-naming)
/setup-analysis-delivery → 阶段 1:生成项目级配置
/grill-task              → 阶段 2:AI 反复追问澄清需求
/to-brd                  → 阶段 3:生成业务需求文档(BRD)
/compliance-review       → 阶段 4:合规评审(GSP / 等保 / GDPR / PIPL)
/test-case-design        → 阶段 5:生成测试用例
/to-prd                  → 阶段 6:生成产品需求文档(PRD)
/dev-design              → 阶段 7:开发设计(FSD + 数据模型 + 开发设计说明书)
/qa-audit                → 阶段 8:QA 审计(6 大类)
/handoff                 → 阶段 9:交付清单
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
| 01 | [wms-warehouse](examples/01-wms-warehouse/) | 医药物流 WMS | Oracle + Spring Boot + Vue 3 | 16 |
| 02 | [saas-dashboard](examples/02-saas-dashboard/) | B2B SaaS 后台 | PostgreSQL + Express 5 + React 19 | 16 |
| 03 | [mobile-app](examples/03-mobile-app/) | B2C 移动 App | Firestore + Flutter 3.24 | 16 |

### 示例 1:医药物流 WMS 收货管理

完整迷你示例,含 BRD + 字段对齐分析 + ASCII 流程图 + 4 个项目级配置 + `decisions.md` ADR 产物。

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

### 项目级配置(4 个 `paths/*.md`)

每个真实项目根目录下默认生成 `paths/` 目录,其中 4 个 canonical path 文件是项目上下文加载入口:

| 文件 | 用途 | 示例内容 |
|---|---|---|
| `paths/knowledge-path.md` | 列出真实知识库路径 | "WMOS 表结构在 `/root/WMOS 知识库/01-WMOS核心/`" |
| `paths/tech-stack-path.md` | 分端列技术栈 | "后端 Java 11 / 前端 Vue 3 / 数据库 Oracle" |
| `paths/compliance-path.md` | 启用合规 + 路径 | "启用 GSP,知识库在 `/root/WMOS 知识库/03-GSP法规/`" |
| `paths/doc-naming-path.md` | 文档编号规则 | "01-09 编号,文档存项目根" |

旧项目根目录下的 `knowledge-path.md` / `tech-stack-path.md` / `compliance-path.md` / `doc-naming.md` 仍作为 legacy 兼容入口识别,但新项目不要继续使用。

### 配置使用记录 / ADR 产物

`config-used.md` 不是配置文件,不参与配置加载,也不由 `init-project-config.sh` 生成。它是可选的交付产物,用于记录:

- 本项目实际读取了哪些 `paths/*.md` / skill fallback 配置
- 为什么选择这些路径、技术栈、合规规则
- 关键配置决策的 ADR(例如"为什么用行级多租户?")
- 后续配置变更需要同步更新哪些文档

可从 `templates/CONFIG_USED.md` 复制生成。

### 一键生成项目配置

```bash
bash scripts/init-project-config.sh /path/to/your-project
```

默认生成 `paths/*.md` 4 个空模板,用户填好后 Claude 自动识别。旧项目如需继续生成项目根 `*.md`,使用 `--legacy`。

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

看 [examples/02-saas-dashboard/decisions.md](examples/02-saas-dashboard/decisions.md):

```markdown
# 配置使用记录 / ADR

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
code --install-extension analysis-to-delivery-4.0.0.vsix
```

**配置**(`settings.json`):
```json
{
  "analysisToDelivery.skillsPath": "${userHome}/.codex/skills/analysis-to-delivery",
  "analysisToDelivery.mermaidCli": "mmdc",
  "analysisToDelivery.defaultFormat": "svg"
}
```

## GitHub Actions CI

13 个 workflow 自动验证(.github/workflows/):

| Workflow | 触发 | 检查 |
|---|---|---|
| `smoke-test.yml` | push/PR | Skill 集合结构 + 元数据(14 节自检) |
| `sql-dialect-check.yml` | push/PR | Oracle / PG / MySQL 方言校验 |
| `doc-validate.yml` | push/PR | Markdown 格式 / 表格 / 代码块 |
| `field-alignment-check.yml` | push/PR | 字段对齐 / 多租户 / 整数 |
| `full-qa-audit.yml` | push to main / release | 6 大类聚合,失败阻断 merge |
| `discipline-lint.yml` | PR | 7 个 discipline 强制加载 + requires 一致性 |
| `bridge-completeness-check.yml` | PR | 7 个 bridge 含降级方案 + 安装提示 + 纪律摘要 |
| `task-confirm-check.yml` | PR | 5 项 check + 双模式 + pytest 22 case |
| `flow-to-mermaid-ascii-strict.yml` | PR | ASCII → Mermaid strict(回流闭环 + 禁 classDef) |
| `analysis-state.yml` | PR | state 持久化脚本可运行 |
| `description-lint.yml` | PR | SKILL.md description 80-150 字符 |
| `antipattern-section-check.yml` | PR | 9 个 user-invoked 反模式清单 ≥ 3 条 |
| `filename-naming-check.yml` | PR | `config-used.md` → `decisions.md` 改名一致性 |

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
├── skills/                     # 26 个独立 skill
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
│   └── disciplines/            # 7 个 legacy 纪律兼容壳(指向 rules/*)
│       ├── no-field-guessing/    →  rules/no-field-guessing.md
│       ├── no-self-invent/       →  rules/no-self-invent.md
│       ├── ascii-flowchart/      →  rules/ascii-flowchart.md
│       ├── stage-gate/           →  rules/stage-gate.md
│       ├── sql-dialect-discipline/ → rules/sql-dialect.md
│       ├── doc-numbering/        →  rules/doc-numbering.md
│       └── context-pointer/      →  rules/context-pointer.md
├── rules/                      # 8 个跨阶段规则(canonical,v4.0.0)
├── paths/                      # 4 个项目级配置入口(canonical)
├── docs/adapters/              # Codex / OpenCode 等 agent 接入说明
├── templates/project-config/   # 兼容壳(指向 paths/*)
├── config/                     # 领域配置(skill 级 fallback)
│   ├── compliance/             # gsp / none / template
│   ├── tech-stack/             # java-spring / frontend-vue / template
│   ├── domain-knowledge/       # template
│   └── doc-naming/             # template
├── examples/                   # 3 个完整示例,各 16 文件
│   ├── 01-wms-warehouse/       # 医药物流 WMS(Oracle)
│   ├── 02-saas-dashboard/      # SaaS 订单(Node + React + PG)
│   └── 03-mobile-app/          # 移动 App(Flutter + Firebase)
├── templates/                  # 文档模板(36 个)
│   ├── *.md                    # 16 个阶段模板
│   ├── project-config/         # 4 个 *-path.md 模板
│   └── cookiecutter-analysis/  # 16 个项目骨架模板 + cookiecutter.json
├── scripts/                    # 26 个自动化脚本
│   ├── smoke-test.sh           # 14 节自检
│   ├── _gate_common.py         # 共享门控库(argparse / 退出码 / CheckResult)
│   ├── setup-check.py          # 阶段门控 1→2
│   ├── task-confirm-check.py   # 阶段门控 2→3(5 check + --strict/--loose)
│   ├── brd-check.py            # 阶段门控 3→4
│   ├── compliance-check.py     # 阶段门控 4→5
│   ├── testcase-coverage-check.py  # 阶段门控 5→6
│   ├── prd-check.py            # 阶段门控 6→7
│   ├── dev-design-backtest.py  # 阶段门控 7→8(4 大类回测)
│   ├── doc-validate.py         # 静态审计
│   ├── field-alignment-check.py
│   ├── sql-dialect-check.py
│   ├── full-qa-audit.py        # 6 大类聚合(P0 阻断)
│   ├── discipline-lint.py      # 元数据校验(legacy 兼容壳)
│   ├── description-lint.py
│   ├── antipattern-section-check.py
│   ├── bridge-completeness-check.py
│   ├── filename-naming-check.py
│   ├── rules-path-lint.py      # Required rules / paths 声明一致性
│   ├── goal-boundary-check.py  # 目标边界与分期(TASK_CONFIRM / PRD / TC / HANDOVER)
│   ├── flow-to-mermaid.py      # ASCII → Mermaid(--ascii-strict)
│   ├── flow-to-drawio.py       # ASCII → Drawio XML
│   ├── flow-export.sh          # Mermaid → SVG/PNG(包装 mmdc)
│   ├── analysis-state.py       # 9 阶段状态持久化(init/record-gate/signoff/status/metrics)
│   ├── parallel-delegate.sh    # Claude adapter: 基于 Claude CLI 并行任务
│   ├── postprocess_prd_html.py # PRD HTML 后处理
│   ├── init-project-config.sh  # 生成 4 个 *-path.md
│   └── cookiecutter-gen.sh     # 生成项目骨架
├── tests/                      # 15 个 pytest 测试(每个 gate 脚本一份)
├── .github/
│   ├── workflows/              # 13 个 CI workflow
│   │   ├── smoke-test.yml
│   │   ├── sql-dialect-check.yml
│   │   ├── doc-validate.yml
│   │   ├── field-alignment-check.yml
│   │   ├── full-qa-audit.yml
│   │   ├── discipline-lint.yml
│   │   ├── bridge-completeness-check.yml
│   │   ├── task-confirm-check.yml
│   │   ├── flow-to-mermaid-ascii-strict.yml
│   │   ├── analysis-state.yml
│   │   ├── description-lint.yml
│   │   ├── antipattern-section-check.yml
│   │   └── filename-naming-check.yml
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── PULL_REQUEST_TEMPLATE.md
└── vscode-extension/           # VSCode 扩展
    ├── package.json
    ├── src/extension.ts
    └── README.md
```

## 脚本能力表

### 阶段门控(7 个)

| 脚本 | 阶段过渡 | 能力 | 依赖 |
|---|---|---|---|
| `scripts/setup-check.py` | 1→2 | 4 个 `*-path.md` 非空 + knowledge 至少 1 个真实路径 | Python 标准库 |
| `scripts/task-confirm-check.py` | 2→3 | 5 项 check(状态 ✅ / 12 词 TBD / 5 章节 / 第八节空 / 🔴❓=0)+ `--strict`/`--loose` | Python 标准库 |
| `scripts/brd-check.py` | 3→4 | BRD 9 章节齐 + 字段映射表 + ASCII 流程图 | Python 标准库 |
| `scripts/compliance-check.py` | 4→5 | 合规条款 1:1 全覆盖,严重条款必须 ✅ | Python 标准库 |
| `scripts/testcase-coverage-check.py` | 5→6 | 5 大类齐 + TC 编号规范 + 合规条款关联 | Python 标准库 |
| `scripts/prd-check.py` | 6→7 | PRD 8 章节齐 + §七 白名单签字 + 字段映射 | Python 标准库 |
| `scripts/dev-design-backtest.py` | 7→8 | 4 大类设计回测(数据模型 / 业务规则 / 状态机 / 字段对齐) | Python 标准库 |

### 静态审计(5 个)

| 脚本 | 能力 | 依赖 |
|---|---|---|
| `scripts/doc-validate.py` | Markdown frontmatter / H1 / 章节 / 链接 / 占位符,P0/P1/P2 分级,`--template-mode` | Python 标准库 |
| `scripts/field-alignment-check.py` | Markdown 表格 + SQL DDL 字段对齐(missing / type_mismatch / nullable_mismatch) | Python 标准库 |
| `scripts/sql-dialect-check.py` | Oracle / PostgreSQL / MySQL 方言混用,`Target_DB` 注释校验 | Python 标准库 |
| `scripts/full-qa-audit.py` | 6 大类聚合(P0 阻断 merge / release) | Python 标准库 |
| `scripts/discipline-lint.py` | SKILL.md `requires:` 与 discipline 路径一致 + 无 typo(legacy 兼容壳) | Python 标准库 |
| `scripts/rules-path-lint.py` | `Required rules / paths` 声明一致性(未知 / 重复 / 缺失 / legacy 别名) | Python 标准库 |
| `scripts/goal-boundary-check.py` | 目标边界与分期: TASK_CONFIRM §二 / §三 + PRD §七 + TC §三 + HANDOVER §二 | Python 标准库 |

### 元数据校验(4 个)

| 脚本 | 能力 | 依赖 |
|---|---|---|
| `scripts/description-lint.py` | SKILL.md description 80-150 字符 + 不空泛 | Python 标准库 |
| `scripts/antipattern-section-check.py` | 9 个 user-invoked SKILL.md 含 `## 反模式` ≥ 3 条 | Python 标准库 |
| `scripts/bridge-completeness-check.py` | 7 个 bridge 含降级方案 + 安装提示 + 纪律摘要 | Python 标准库 |
| `scripts/filename-naming-check.py` | `config-used.md` → `decisions.md` 改名一致性 | Python 标准库 |

### 流程图工具链(3 个)

| 脚本 | 能力 | 依赖 |
|---|---|---|
| `scripts/flow-to-mermaid.py` | ASCII → Mermaid 源码,状态机自动检测 ▼,`--ascii-strict` 校验回流闭环 + 禁 `classDef` | Python 标准库 |
| `scripts/flow-to-drawio.py` | ASCII → Drawio XML(可在线编辑),白底蓝边 #3b82f6 | Python 标准库 |
| `scripts/flow-export.sh` | Mermaid → SVG/PNG(单文件 / `--batch` / `--all`),包装 `mmdc` | mermaid-cli |

### 流程状态 + 基础设施(7 个)

| 脚本 | 能力 | 依赖 |
|---|---|---|
| `scripts/analysis-state.py` | `.analysis-delivery-state.json` 持久化;5 子命令 `init` / `record-gate` / `signoff` / `status` / `metrics`;签字白名单 4 句 | Python 标准库 |
| `scripts/smoke-test.sh` | 14 节自检(目录 / 工具 / 文档 / 模板 / 脚本 / skills / config / examples / metadata / 编号 / 链接 / 语义 / CI / 工具链) | Bash + Python |
| `scripts/init-project-config.sh` | 一键生成项目根 4 个 `*-path.md`;支持 `--force` | Bash |
| `scripts/parallel-delegate.sh` | Claude adapter: 基于 Claude CLI 并行执行任务文件 | Bash + `claude` |
| `scripts/cookiecutter-gen.sh` | 生成 `templates/cookiecutter-analysis/` 项目骨架 | cookiecutter |
| `scripts/postprocess_prd_html.py` | PRD HTML 后处理(封面 / 目录 / 章节卡片 / 响应式) | Python 标准库 |
| `scripts/_gate_common.py` | 共享库(argparse / 退出码 / JSON / CheckResult / GateReport) | Python 标准库 |

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

每个项目目录里,`01-09` 是唯一编号文档(强制):

| 编号 | 文档 | 阶段 |
|---|---|---|
| 01 | 业务需求文档 BRD.md | 3 |
| 02 | 功能规格说明书 FSD.md | 7 |
| 03 | 数据模型设计.md | 7 |
| 04 | 合规评审.md | 4(可省略) |
| 05 | 产品需求文档 PRD.md | 6 |
| 06 | 开发设计说明书.md | 7 |
| 07 | 测试用例设计.md | 5 |
| 08 | 设计回测报告.md | 7 |
| 09 | QA 审计报告.md | 8 |

不占编号:`HANDOVER.md` / `AGENTS.md` / `REVIEW_*` / `TASK_CONFIRM_*` / `RETRO_*`。

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
| v1.0 | MVP,9 阶段工作流 + 1 个示例 | ✅ 2026-06 |
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
| 用户 | 在 [GitHub Issues](https://github.com/BlueprintOS/analysis-to-delivery/issues) 报 bug / 提需求 / 分享使用案例 |
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
**当前版本**:4.0.0(2026-07,plan §P0~P3 12 项修复完成)
**GitHub**:https://github.com/BlueprintOS/analysis-to-delivery
