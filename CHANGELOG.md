# Changelog

所有本项目的显著变更都会记录在此文件。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

## [v3.1.0] - 2026-07-02

> **P0-P3 共 12 项修复**:门控脚本补齐 + discipline lint + bridge 降级 + flow strict + 状态持久化 + 数字统一 + README 降级 + 快速通道 + 3 example 升级 + description 精简 + 反模式 + 改名 decisions。

### P0 架构必修(2 项)

- 🆕 **6 个门控脚本 + 6 个 workflow**(plan §1)
  - `scripts/setup-check.py`(1→2)/`brd-check.py`(3→4)/`compliance-check.py`(4→5)/`testcase-coverage-check.py`(5→6)/`prd-check.py`(6→7)/`dev-design-backtest.py`(7→8)
  - 每个脚本统一接口:`--strict` / `--loose` / `--self-test` / `--json`,通过共享 `_gate_common.py`
  - 6 个对应 `.github/workflows/<name>-check.yml` + 6 个 `tests/test_<name>_check.py`
- 🆕 **discipline 强制加载机制**(plan §2)
  - 9 个 user-invoked SKILL.md frontmatter 增 `requires: [...]`
  - `scripts/discipline-lint.py` 校验 4 条(frontmatter 存在 / Contract 一致 / discipline 路径存在 / 无 typo)
  - `.github/workflows/discipline-lint.yml` PR 触发

### P1 关键工程问题(4 项)

- 🆕 **bridge skill 实质化**(plan §3)
  - 7 个 `skills/orchestration/development/*/SKILL.md` 补 `## 降级方案(superpowers 未装时)` 章节
  - `scripts/bridge-completeness-check.py` 校验含降级章节 + 安装提示 + 纪律摘要
- 🆕 **`flow-to-mermaid.py --ascii-strict`**(plan §4)
  - 检测输入 ASCII 是否缺回流闭环
  - 检测输出 mermaid 是否含 `classDef`(违反简洁性)
- 🆕 **`.analysis-delivery-state.json` 状态持久化**(plan §5)
  - `scripts/analysis-state.py` 5 子命令:`init` / `record-gate` / `signoff` / `status` / `metrics`
  - 仓库根 + `.gitignore`,提供 9 阶段流程的"中断/恢复"
- 🛠️ **数字打架修复**(plan §6)
  - 3 个 example config-used.md 升 v3.0.1
  - README install --version → v3.1.0
  - 后续随 P3-1 改造 description 后复核"26 个 skill"数字

### P2 质量问题(3 项)

- 🛠️ **README 跨行业/跨技术栈话术降级**(plan §7)
  - "Java/Go/Python 全支持" → "框架层通用;具体行业/领域需用户补 config"
  - 新增"已覆盖 vs 未覆盖"对照表
- 🆕 **缺失能力补齐:快速通道 / 逆向使用 / 度量**(plan §8)
  - SKILL.md / README.md 各增 3 章节
  - `analysis-state.py` 扩 `metrics` 子命令
- 🆕 **3 个 example 升级到 v3.0.1**(plan §9)
  - 01-wms-warehouse / 02-saas-dashboard / 03-mobile-app 各补 04-合规评审 / 05-PRD / 07-测试用例 三文档
  - config-used.md 标题升 v3.0.1 + 新增 `## v3.1.0 升级说明` 节

### P3 易用性(3 项)

- 🆕 **description 字段精简到 80-150 字符**(plan §10)
  - 26 个 SKILL.md 全部压到合理范围
  - `scripts/description-lint.py` 校验长度 + 不空泛 + 必存在
- 🆕 **9 个 user-invoked SKILL.md 补反模式清单**(plan §11)
  - 每个 SKILL.md 增 `## 反模式` 章节,3-7 条 `❌` 开头
  - `scripts/antipattern-section-check.py` 校验存在性 + 条数 ≥ 3
- 🆕 **`config-used.md` → `decisions.md` 改名**(plan §12)
  - 名称更准确反映 ADR 性质(非配置文件)
  - `templates/decisions.md` 新 ADR 模板
  - `templates/CONFIG_USED.md` 改 deprecation stub
  - `scripts/filename-naming-check.py` 校验

### 工程改进

- 🆕 共享 `scripts/_gate_common.py`(统一 argparse / 退出码 / JSON 序列化 / CheckResult / GateReport)
- 🆕 26 个 SKILL.md `requires:` 前置纪律声明
- 🛠️ smoke-test.sh 列表同步(12 个脚本 + 12 个 workflow + 实际 help 检查)
- 🛠️ .gitignore 增 `.analysis-delivery-state.json`

### 已知遗留 / 留给后续版本

- 阶段 7-8 `/dev-design` 6 大文档(FSD/数据模型/开发设计/回测/复盘/交接)留待后续
- 阶段 9 `/qa-audit` 全量审计报告留待后续
- 2 个 example 流程图(WMS 状态流转 / SaaS 订单流转)在 `--ascii-strict` 下报"缺回流闭环",默认 mode 不影响

## [v3.0.1] - 2026-06-24

> **grill-task 门控加固**:从需求澄清到 BRD 的硬门控,避免 LLM 在用户未完成确认时自动推进。

### 新增

- 🆕 **`scripts/task-confirm-check.py` v1.1.0** — TASK_CONFIRM 门控验证器(5 项 check + 双模式)
  - **Check 1**:状态字段必须 = `✅`(硬约束 `⬜/✅` 二态,删 🟡)
  - **Check 2**:12 词 TBD 红线扫描(`TBD`/`TODO`/`待定`/`稍后`/`下次`/`N/A`/`待确认`/`暂定`/`未定`/`待补充`/`⬜`/`❓`)+ `\b` 整词匹配(ID_TODO_FIELD 不误报)
  - **Check 3**:TASK_CONFIRM 必须含 5 个章节(一~五)
  - **Check 4**:REVIEW_需求确认书 第八节"待明确事项"必须为空(无 T-XX 残留)
  - **Check 5**:REVIEW_字段对齐分析 对齐结论表 `🔴=0` 且 `❓=0`(BLOCK 规则)
  - **双模式**:`--strict`(默认,5 项全 BLOCK)/ `--loose`(Check 1/2 仍 BLOCK,Check 3/4/5 降级为 warning)
  - argparse 互斥组:`--strict --loose` 同时传 → rc=2
  - 模板文件例外:`templates/TASK_CONFIRM.md` 自动跳过 Check 2/3(自指占位符)
  - 退出码:0 = pass(strict)/ 仅 warning(loose);1 = fail;2 = 参数错误
- 🆕 **`.github/workflows/task-confirm-check.yml`** — PR 时自动跑 self-test + pytest + 集成 + 模板拒绝
- 🆕 **`tests/test_task_confirm_check.py`** — 22 个 pytest case(覆盖 5 check + CLI + 双模式 + 互斥)

### 修复

- `grill-task` SKILL 结束条件从模糊"已签字"改为 7 条硬门控
- `stage-gate` 2→3 门控从 1 条拆为 3 条独立门
- `field-alignment-check.py` docstring 显式声明不接 TASK_CONFIRM(仅校验 PRD/FSD 字段引用)
- `analysis-delivery-workflow` 加"严禁自动推进"规则 + 2→3 门控交叉引用 `task-confirm-check.py`

### 模板硬约束

- `templates/TASK_CONFIRM.md`:状态字段 `⬜/✅` 二态(删 🟡);trigger 4 句白名单话术;12 词红线引用脚本
- `templates/REVIEW_需求确认书.md`:第七节"AI 助手补充确认项"(设计假设)+ 第八节"待明确事项"空表;用户操作改为"进入阶段 3(BRD)" + HARD BLOCK
- `templates/REVIEW_字段对齐分析.md`:状态字段扩 4 态(`✅/⚠️/❓/🔴`)+ BLOCK 规则 + 阶段号 2→3

### 示例同步

- `examples/01-wms-warehouse/`:TASK_CONFIRM 重写为 v3.0.1 5 章节格式;REVIEW 文档加 4 态状态字段 + 对齐结论表 + 第七/八节
- `examples/02-saas-dashboard/`:同上
- `examples/03-mobile-app/`:同上
- 3 套示例在 `--strict` 与 `--loose` 模式下均 5/5 check 通过

### 留痕

- `docs/superpowers/specs/2026-06-24-grill-task-bugfix-design.md` — 设计 spec
- `docs/plans/2026-06-24-grill-task-bugfix.md` — 18 Task 实施计划
- `logs/STEP-P0-review.md` / `STEP-P1-review.md` / `STEP-P2-review.md` / `STEP-P3-review.md` — B+C 留痕 + 用户签字

### Breaking Changes (v3.x)

- **TASK_CONFIRM 模板状态字段**：从三态 `⬜/🟡/✅` 改为二态 `⬜/✅`。现有 🟡 文档需手动改为 ⬜ 或 ✅
- **触发话术**：用户必须用白名单话术（`我已全部确认，可以进入下一步` / `确认通过，进入 BRD` / `全部完成，继续` / `approved, proceed to next stage`）才能进入下一阶段。仅说"已填写"不再有效
- **新增门控脚本**：`scripts/task-confirm-check.py`（5 项检查），替代 `field-alignment-check.py` 在 grill-task 中的引用
- **grill-task 章节数**：从"4 章节"改为"5 章节"（一~五），SKILL 文档同步

### 新增
- 🆕 **`scripts/task-confirm-check.py`**（v1.0.0）— TASK_CONFIRM 门控验证器
  - 5 项检查：状态字段 / 12 词 TBD / 5 章节完整 / REVIEW 第八节为空 / 字段对齐 🔴❓ 计数
  - CLI：`python3 task-confirm-check.py <TASK_CONFIRM.md> <REVIEW_需求确认书.md> <REVIEW_字段对齐分析.md>`
  - 退出码：0 = pass / 1 = fail / 2 = 参数错误
  - 模板文件 `templates/TASK_CONFIRM.md` 自动跳过 Check 2/3（含自指占位符）
- 🆕 **`.github/workflows/task-confirm-check.yml`** — PR 时自动跑 task-confirm-check.py

### 修复
- `field-alignment-check.py` docstring 显式声明不接 TASK_CONFIRM（仅校验 PRD/FSD 字段引用）
- `grill-task` SKILL 结束条件从模糊"已签字"改为 7 条硬门控
- `stage-gate` 2→3 门控从 1 条拆为 3 条独立门

### 增强
- **`scripts/task-confirm-check.py` 升至 v1.1.0** — 新增 `--strict` / `--loose` 双模式
  - `--strict`（默认）：5 项检查全部 BLOCK
  - `--loose`：Check 1/2 仍 BLOCK,Check 3/4/5 降级为 warning(⚠️)
  - argparse 互斥组,`--strict --loose` 同时传会 exit 2
- **examples 三套 REVIEW 文档**全部对齐 v3.x 格式(4 态状态字段 + 对齐结论表 + 第七/八节),`--strict` 模式 5/5 check 通过

### 新增
- 🆕 **v3.0-dev 工具链 + VSCode 集成**(开发中)
  - **`scripts/flow-to-mermaid.py`** — ASCII 流程图 → Mermaid 源码转换器
    - 支持状态机自动检测(▼ 垂直箭头)
    - 自动清理 box label 中的 │ 分隔符
    - 批量模式 + JSON 输出
    - 启发式边检测,失败时输出节点 + 边注释模板
  - **`scripts/flow-export.sh`** — Mermaid → SVG/PNG 渲染器
    - 包装 `mmdc`(mermaid-cli)
    - 支持单文件 + `--batch` 批量 + `--all` 递归
    - 自动创建 rendered/ 输出目录
    - 依赖检查 + 友好错误提示
  - **`scripts/flow-to-drawio.py`** — ASCII 流程图 → drawio XML 转换器(与 mermaid 互为补充)
    - 输出标准 mxGraphModel 格式,可直接在 https://app.diagrams.net/ 打开
    - 简单垂直布局(120x60 节点,80px 间距,白底蓝边 #3b82f6)
    - 启发式垂直边检测(▼ 箭头)
    - 支持 `--batch` 批量转换
    - 适用场景:团队偏好 drawio 在线编辑 / 需要更精细布局控制时
  - **`vscode-extension/`** — VSCode 扩展 scaffold(v0.1.0)
    - 4 个命令:`applySkill` / `runSmokeTest` / `renderFlowChart` / `openDocumentation`
    - 配置项:`skillsPath` / `mermaidCli` / `defaultFormat` / `disabled`
    - 上下文菜单集成(.txt 业务流程图自动出现)
    - 自动激活(workspace 包含 BRD / TASK_CONFIRM 时)
    - 自定义 SVG 图标(蓝色流程图风格)
    - TypeScript + ESLint + .vscodeignore 完整工程
    - README 详述开发 / 调试 / 打包 / 发布流程
  - **`README.md` 全面重写**
    - 添加目录导航(11 节)
    - 添加 "26 个 skill 速查" 表
    - 添加 "📚 知识库配置(项目级)" 完整章节(痛点 + 三层优先级 + 4 个 `*-path.md` + config-used ADR + init 脚本 + 实战)
    - 添加 "🔧 工具链" 章节(flow-export + VSCode 扩展用法)
    - 添加 "GitHub Actions CI" 章节
    - 更新依赖表(Node.js / mermaid-cli / cookiecutter)
    - 更新路线图(v2.0 完成 + v3.0 进行中 + v4.0 计划)

## [Unreleased 历史]

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
  - **架构重构**:从"1 个大 SKILL + 9 阶段强流程"拆为 26 个独立可组合 skill
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
- 9 阶段通用工作流（SKILL.md，16KB）
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
