# Changelog

所有本项目的显著变更都会记录在此文件。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 新增
- 🆕 **v2.0 多领域示例 + CI + 社区治理**
  - **`examples/02-saas-dashboard/`**(Node 22 + Express 5 + React 19 + PostgreSQL 16)
    - 12 个文件:README / TASK_CONFIRM_订单管理 / REVIEW_需求确认书 / REVIEW_字段对齐分析 / 01-BRD / 业务流程图(订单创建 + 状态流转)/ knowledge-path / tech-stack-path / compliance-path / doc-naming / config-used
    - 演示:SaaS 客户订单管理 / 多租户行级隔离 / 字符串状态枚举 / PostgreSQL 方言(NVL→COALESCE / ROWNUM→LIMIT / SERIAL / TIMESTAMPTZ)/ 9 状态状态机 / 支付集成(支付宝/微信/Stripe)/ 物流(顺丰)
  - **`examples/03-mobile-app/`**(Flutter 3.24 + Cloud Firestore + Cloud Functions)
    - 12 个文件:README / TASK_CONFIRM_会员积分 / REVIEW_需求确认书 / REVIEW_字段对齐分析 / 01-BRD / 业务流程图(积分获取 + 状态流转)/ knowledge-path / tech-stack-path / compliance-path / doc-naming / config-used
    - 演示:会员积分管理(B2C 移动 App)/ 跨平台 iOS+Android / Firestore NoSQL / FIFO 批次消耗积分 / FCM 推送 / 离线优先 / PIPL 轻合规 / Riverpod 状态管理
  - **`.github/workflows/`**(5 个 GitHub Actions)
    - `smoke-test.yml` — Skill 集合结构冒烟测试
    - `sql-dialect-check.yml` — SQL 方言校验(Oracle / PostgreSQL 双跑)
    - `doc-validate.yml` — 文档格式校验(Markdown / 表格 / 代码块 / 章节)
    - `field-alignment-check.yml` — 字段对齐审计(知识库对照 / 多租户必带 / 整数积分)
    - `full-qa-audit.yml` — 全量 QA 审计(综合 4 项 + 阻断 merge / release)
  - **`CONTRIBUTING.md`** — 贡献者指南
    - 行为准则 / 贡献类型 / 开发流程(Fork & Clone & 分支命名)/ 提交规范(Conventional Commits)/ 本地验证 / examples & skills & scripts 目录约定 / SemVer 发布流程
  - **`.github/ISSUE_TEMPLATE/`**
    - `bug_report.md` — Bug 报告模板(8 节 + 检查清单)
    - `feature_request.md` — 功能请求模板(优先级 / 验收标准 / 工作量)
  - **`.github/PULL_REQUEST_TEMPLATE.md`** — PR 模板(改动类型 / 测试 / 文档同步 / 兼容性 / 检查清单)
  - **`scripts/smoke-test.sh` v2.0 扩展**
    - 新增第 13 节:examples ≥ 3 个 + 每例 ≥ 10 个文件 + 5 个 workflow + CONTRIBUTING + Issue/PR 模板

### 跨项目差异对比(全 3 例)
| 维度 | 01-wms-warehouse | 02-saas-dashboard | 03-mobile-app |
|---|---|---|---|
| 数据库 | Oracle 19c | PostgreSQL 16 | Cloud Firestore |
| 后端 | Spring Boot 3 | Express 5 | Cloud Functions |
| 前端 | Vue 3 PC | React 19 Web | Flutter 3.24(iOS+Android)|
| 合规 | GSP 医药 | None(商业)| PIPL(C 端个人信息)|
| 多租户 | 单租户 | 行级多租户 | 用户维度 |
| 实时性 | 异步队列 | T+1 | 实时 Firestore listener |
| 离线 | 不涉及 | 不涉及 | 必备(Offline-first)|
| 推送 | 不涉及 | 不涉及 | FCM |

## [Unreleased 历史]

### 新增
- 🆕 **v1.4.0-dev 拆分为 26 个独立 skill（mattpocock 风格）**
  - **架构重构**:从"1 个大 SKILL + 10 阶段强流程"拆为 26 个独立可组合 skill
  - **2 个 router**(`disable-model-invocation: true`,零 context load):
    - `ask-delivery` — 路由 9 动作 + 1 编排
    - `using-superpowers` — 路由 7 个 superpowers 实施 skill
  - **9 个 user-invoked 动作**:setup-analysis-delivery / grill-task / to-brd / compliance-review / test-case-design / to-prd / dev-design / qa-audit / handoff
  - **1 个 orchestration 编排**:analysis-delivery-workflow(9 阶段)
  - **7 个 superpowers bridge**(桥接层,不复制内容):brainstorming / design-an-interface / domain-modeling / writing-plans / tdd / executing-plans / verification-before-completion
  - **7 个 discipline**(model-invoked,自动调用):no-field-guessing / no-self-invent / ascii-flowchart / stage-gate / sql-dialect-discipline / doc-numbering / context-pointer
  - 删除 `references/`(13 篇已迁移到对应 skill)
  - 删除 `examples/01-wms-warehouse/REVIEW_*.md` 等(已合并到 user-invoked skill)
  - 顶层 `SKILL.md` 改为简短入口(指向 `skills/` 下)
  - `smoke-test.sh` 适配新结构,检查 26 个 skill + 各类目数量
  - 总规模:26 SKILL.md,平均 < 200 行,职责单一
- 🆕 **v1.3.0-dev 双模式 + 脚本补实现 + 开发实施纪律**

## [1.2.0] - 2026-06-22

### 新增
- 🆕 **v1.2 skill 自检 + 文档校验 + 模板引擎化**
  - `scripts/smoke-test.sh` — Skill 装完自检（11 节 / 37 项检查），支持 `--verbose` / `--json`
  - `scripts/doc-validate.py` — 单文档格式校验（P0/P1/P2 分级），支持 `--type` / `--json` / `--level`
  - `templates/cookiecutter-analysis/` — Cookiecutter 项目骨架模板（13 个文件 + cookiecutter.json）
  - `scripts/cookiecutter-gen.sh` — 一键生成项目骨架（支持 `--name` / `--slug` / `--code` / `--version` / `--owner` 等参数）
  - README.md / SKILL.md / plan.md 同步更新

## [1.1.0] - 2026-06-22

### 变更
- 🎯 **阶段 8 简化**：去掉 V1（存储过程版）/ V2（代码实现版）双版本概念，统一为单一代码版工作流
  - FSD（功能规格）从"V1 配套产物"独立为阶段 8.1 通用产物，模板完全重写
  - 数据模型设计、开发设计说明书保持，归属从 `(V1)` `(V2)` 改为通用
  - `references/v1-v2-versioning.md` 重命名为 `references/dev-design-spec.md` 并重写
  - SKILL.md / SPEC.md 阶段 8 整段同步重写

### 新增
- 🆕 **项目级 config 体系**（v1.1 核心）
  - 4 个 `*-path.md` 模板（`templates/project-config/`）：knowledge / compliance / tech-stack / doc-naming
  - `scripts/init-project-config.sh`：一键在项目根生成 4 个空模板
  - SKILL.md 配置加载机制重写为三层优先级（项目级 > skill 级 > 默认）
  - SPEC.md §6.5 项目级配置契约
  - 示例 `examples/01-wms-warehouse/` 下加 4 个 `*-path.md` 演示

## [1.0.0-mvp] - 2026-06-22

### 新增
- 🎉 MVP 首发版本
- 10 阶段通用工作流（SKILL.md，16KB）
- install.sh 一键安装脚本（支持 dry-run、target、uninstall、version 参数）
- 配置目录（`config/`）：
  - 合规规则：gsp.md（医药示例）、none.md、template.md
  - 技术栈：java-spring.md、frontend-vue.md、template.md
  - 领域知识、文档命名：template.md
- 完整示例（`examples/01-wms-warehouse/`）：
  - 医药物流 WMS 收货管理迷你示例
  - 含 config-used.md / TASK_CONFIRM / REVIEW_需求确认书 / REVIEW_字段对齐分析 / BRD / 状态流转图 / 业务流程图
- 12 个文档模板（`templates/`）
- 10 个方法论文档（`references/`）占位
- 5 个自动化脚本（`scripts/`）占位
- 完整文档：README.md / plan.md / SPEC.md / LICENSE

### 已知限制
- 仅有 1 个领域示例（医药 WMS）
- 配置库不完整（仅有 2 个合规 + 2 个技术栈示例）
- 模板和脚本为占位（待 v1.1 完善）
- 无 GitHub Actions CI（待 v2.0）

### 计划
- v1.1：补 5-8 个合规规则 + 6-8 个技术栈
- v1.2：补完整模板和脚本 + skill 自检
- v2.0：补 2 个新示例 + GitHub Actions + CONTRIBUTING.md

---

## 版本说明

- **1.0.0-mvp**：MVP 首发。功能完整但配置库/模板/脚本不全，**生产环境慎用**
- **1.1.0**（2026-06-22）：项目级 config 体系 + 阶段 8 简化
- **1.2.0**（2026-06-22）：skill 自检 + 文档校验 + cookiecutter 引擎化
- **1.3.0-dev**：双模式 + 阶段门控 + 设计回测 + 任务复盘 + 脚本补实现
- **1.4.0-dev**：拆分为 26 个独立 skill（mattpocock 风格）
- **2.0.0-dev**（2026-06-22）：多领域示例(SaaS + 移动 App)+ GitHub Actions(5 个 workflow)+ CONTRIBUTING + Issue/PR 模板
- **1.x.x**：配置库完善阶段，向完全可用演进
- **2.x.x**：多领域示例 + CI 阶段（当前）
- **3.x.x**：工具链集成 + 可视化阶段
