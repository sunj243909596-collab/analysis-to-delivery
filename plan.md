# Plan — Analysis to Delivery

> **当前版本**:v2.0.0-dev(2026-06-22)
> 路线图详见下方各版本节。最新进度看 [README.md](README.md)，详细规格看 [SPEC.md](SPEC.md)。

## 愿景

把"需求 → 设计 → 开发"这条链路沉淀为一个**可复用、可配置、跨行业**的 AI 工作流框架。

任何团队拿到这个 skill 之后：
1. 告诉 Claude 自己的**领域**和**技术栈**
2. Claude 自动加载对应配置，按 10 阶段工作流推进
3. 产出可直接交给开发的设计文档（BRD/FSD/数据模型/PRD/开发设计/测试用例）

**目标用户**：3-10 人的小型软件团队的 AI 助手使用者（产品经理 + 架构师 + 高级开发）。

## 核心原则

| 原则 | 说明 |
|---|---|
| **大道至简** | 主文档只讲"怎么做"，领域细节全部放 config |
| **可插拔** | 用户只加载自己用得到的配置 |
| **跨行业** | 医药/金融/SaaS/移动 App 都用同一套骨架 |
| **跨技术栈** | Java/Go/Python/Node 全支持 |
| **可审计** | 所有产物可追溯：每段文档对应哪个阶段、哪条配置 |
| **不重复造轮子** | 借用社区成熟工具（pandoc、drawio、Python），不重新发明 |

## 版本路线图

### v1.0（MVP，当前）— 最小可用
**目标**：跑通"通用工作流 + 1 个领域示例"，让用户能装能用。

**范围**：
- ✅ 通用 10 阶段工作流（SKILL.md 骨架）
- ✅ 1 个配置目录（compliance/tech-stack/domain-knowledge/doc-naming 各 1-2 个示例）
- ✅ 1 个完整示例（`examples/01-wms-warehouse`，医药物流收货管理蒸馏版）
- ✅ 文档模板（BRD/FSD/PRD/数据模型/开发设计/测试用例）
- ✅ 4 个核心脚本（sql-dialect-check / full-qa-audit / field-alignment-check / parallel-delegate）
- ✅ install.sh 一键安装
- ❌ **不包含**：完整配置库（待 v1.1+ 补）、2 个其他行业示例（待 v2.0）、自动化 CI

**用户承诺**：
- 装上后能跑完一个简单项目（如 1-2 周工作量）的需求到设计流程
- 文档结构清晰，示例可直接对照使用
- 脚本能跑（即使功能不完整）

### v1.1（计划 2026-Q3）— **项目级配置体系**（核心方向调整）

> 痛点回顾：v1.0 把所有 config 放在 skill 内 `config/`，真实项目交付时配置不准、难维护。
> 调整方向：**项目级优先 + skill 级 fallback**。

**核心变更**：
- ✅ 新增 4 个项目级 config 模板（`templates/project-config/` 下）
  - `knowledge-path.md`（项目根，列真实知识库路径）
  - `compliance-path.md`（项目根，启用开关 + 路径）
  - `tech-stack-path.md`（项目根，分端列后端/前端/数据库/中间件）
  - `doc-naming.md`（项目根，文档编号/前缀/存放目录）
- ✅ 新增 `scripts/init-project-config.sh`（一键在项目根生成 4 个空模板）
- ✅ SKILL.md / SPEC.md 重写"配置加载机制"章节，明确三层优先级（项目级 > skill 级 > 默认）
- ✅ 示例 `examples/01-wms-warehouse/config-used.md` 改写为项目级演示
- ✅ 阶段 8 简化：去掉 V1/V2 双版本（FSD / 数据模型 / 开发设计三件套）
- ✅ templates 通用化 + WMS 痕迹清理

**用户承诺（v1.1）**：
- 拿到一个真实项目后，跑一行 `init-project-config.sh` 就能开工
- 项目的合规规则、技术栈、知识库路径**全部跟着项目走**，不污染 skill
- skill 级示例仅作 fallback 参考；其他行业的 config 让用户用 LLM 按 `templates/` 自己生成

**明确不做的**（v1.2+ 也不会做）：
- ❌ skill 维护方**不**预置 N 个合规规则 / N 个技术栈的内置 fallback
- 原因：LLM 时代，用户用 `templates/` 自己生成 config 更快、更贴场景；skill 维护方写一堆 fallback 是低价值重复劳动
- skill 自带的 `config/compliance/gsp.md` / `config/tech-stack/java-spring.md` 仅作"格式参考样例"，不追求覆盖广度

### v1.2（计划 2026-Q3）— 测试增强
- 集成 v1.0 skill 的自检脚本（skill 装完后自动跑 smoke test）
- 文档产物模板添加"自动校验"按钮
- 模板引擎化（用 cookiecutter / copier 替代手写）

### v1.3.0-dev（开发中，2026-Q3）— 双模式 + 开发实施纪律
> 痛点回顾：阶段 8 写完即进 QA，缺过程纪律 → 设计漏洞 / 知识无法沉淀 / 跑偏无法发现。
> 调整方向：**默认设计交接 + 可选实施扩展 + 3 层门控 + 设计回测 + 任务复盘**。

**核心变更**：
- ✅ 新增 3 个方法论参考文档（`references/`）：
  - `stage-gate.md` — 3 层门控（工作流 / 子流程 / 子任务）
  - `design-backtest.md` — 设计回测 4 大类（数据 / 业务 / 状态机 / 字段）
  - `task-retrospective.md` — 5 问复盘 + 知识库沉淀
- ✅ SKILL.md 阶段 8 扩展为 8.0-8.6 七个子节
  - §8.0 开发实施子流程（brainstorming → spec → plan → TDD → execute）
  - §8.1-8.3 FSD / 数据模型 / 开发设计说明书
  - §8.4 设计回测（HARD GATE：不通过禁入阶段 9）
  - §8.5 任务复盘（5 问 + 沉淀）
  - §8.6 阶段门控（3 层签字）
- ✅ `templates/开发设计说明书.md` 加 §5 设计回测 / §6 子流程门控 / §7 任务复盘汇总
- ✅ cookiecutter 模板同步

**用户承诺（v1.3）**：
- 阶段 8 有明确的"开始 / 暂停 / 继续"信号
- 设计回测能在 QA 前发现 80%+ 的字段 / 状态机 / 业务规则漏洞
- 任务复盘把"个人经验"沉淀为"团队知识"
- 跨项目经验回流到 `references/`，skill 自我进化

**明确不做的**（v1.4+ 也不会做）：
- ❌ 不写自动回测脚本（设计回测需要人判断哪些样本有意义，自动化反而不准）
- ❌ 不做强制 IDE 插件（门控在文档 / commit message 层就够）

### v2.0（计划 2026-Q4）— 多领域示例 + CI
- 补充 2 个完整示例：
  - `examples/02-saas-dashboard`（SaaS 后台，Node + React + PostgreSQL）
  - `examples/03-mobile-app`（移动 App，Flutter + Firebase）
- 接入 GitHub Actions（自动跑 SQL 方言检查 + 文档 QA 审计）
- Issue 模板 + PR 模板
- 贡献者指南（CONTRIBUTING.md）

### v3.0（计划 2027）— 工具链集成
- 集成 drawio CLI（自动生成流程图 PNG）
- 集成 mermaid CLI（备选）
- 可选：集成 docx 模板（python-docx-template）支持更精细排版
- 可选：VSCode 扩展（右键项目 → 应用 skill）

## 已识别的限制（MVP 阶段需告知用户）

| 限制 | 影响 | 缓解 |
|---|---|---|
| 配置库不完整 | 用户行业不在示例中时需自己写 config | v1.1 补齐 |
| 仅有 1 个领域示例 | 用户需参照示例自己改 | v2.0 补 2 个 |
| 无自动化测试 | skill 自身的 bug 需手动发现 | v1.2 加 smoke test |
| 文档以中文为主 | 英文用户阅读有门槛 | v2.0 考虑 i18n |
| 假设 Python 3.8+ | 老环境跑不了 | README 明确标注依赖 |

## 贡献方式

| 角色 | 怎么参与 |
|---|---|
| **用户** | 在 GitHub Issues 报 bug / 提需求 / 分享使用案例 |
| **贡献者** | Fork → 修改 → PR（详见 v2.0 的 CONTRIBUTING.md） |
| **维护者** | 审 PR / 发版 / 维护 issue |

### 优先欢迎的贡献
- 新的 `config/compliance/*.md`（你所在行业的合规规则）
- 新的 `config/tech-stack/*.md`（你熟悉的技术栈）
- 新的 `examples/*`（你做过的真实项目蒸馏版）
- 新的 `templates/*`（你团队在用的文档模板）
- 脚本 bug 修复

## 决策记录

### 为什么 v1.0 选 wms-warehouse 作为唯一示例？
- 蒸馏来源是已验证的 wms-requirement-analysis skill（实战检验）
- 医药行业合规复杂，能体现 config 机制的威力
- 收货管理是大多数 B 端系统都有的通用模块，用户易理解

### 为什么 config 而不是更细粒度的插件机制？
- 配置简单：用户复制 config/ 下文件改即可
- 不引入外部依赖（不用 Python entry_points、npm plugin 等）
- 维护成本低：v1.x 都是声明式 markdown，v2.0 再考虑动态加载

### 为什么不用 cookiecutter 模板？
- v1.0 用户群体小，引入额外工具会抬高上手成本
- v1.2 再引入也不晚，渐进式披露

## 进度看板

### v1.0 MVP — 全部完成 ✅
| Phase | 状态 | Commit | 备注 |
|---|---|---|---|
| 建目录骨架 | ✅ 已完成 | 129dea6 | 2026-06-22 |
| 写 plan.md / SPEC.md / SKILL.md | ✅ 已完成 | 129dea6 | 2026-06-22 |
| 写 install.sh | ✅ 已完成 | 129dea6 | 含 --dry-run / --target / --uninstall / --version |
| 蒸馏 examples/01-wms-warehouse | ✅ 已完成 | 129dea6 | 8 个文件（BRD / 流程图 / 配置） |
| 写 README/LICENSE/CHANGELOG | ✅ 已完成 | 129dea6 | |
| 本地验证 | ✅ 已完成 | 129dea6 | 脚本 --help 全跑通 |
| git init + 推送 GitHub | ✅ 已完成 | b35d53e | sunj243909596-collab/analysis-to-delivery |

### v1.1 — 全部完成 ✅（不含 fallback 库）
| Phase | 状态 | Commit | 备注 |
|---|---|---|---|
| 项目级 config 体系（4 个 *-path.md + init 脚本） | ✅ 已完成 | 09bb58d | 核心方向调整 |
| 阶段 8 去掉 V1/V2 双版本 | ✅ 已完成 | fb8db83 | 用户反馈"存储过程不需要" |
| templates 通用化 | ✅ 已完成 | 511009f | 移除 WMS 特定内容 |
| references / SKILL / SPEC WMS 痕迹清理 | ✅ 已完成 | 8a6c585 | 实战教训段保留（按方案 B） |
| plan.md 进度看板同步 | ✅ 已完成 | e224917 | |
| ~~skill 级配置库补充~~ | ❌ 取消 | - | LLM 时代用户自己生成更快 |
| **CHANGELOG 升 [1.1.0] tag** | ⬜ 待开始 | | v1.1 已发到 main，未打 tag |

### v1.2 — 全部完成 ✅
| Phase | 状态 | Commit | 备注 |
|---|---|---|---|
| skill 自检 smoke test | ✅ 已完成 | 6fae30f | `scripts/smoke-test.sh`（11 节 / 37 项检查） |
| 文档产物自动校验 | ✅ 已完成 | 0330181 | `scripts/doc-validate.py`（P0/P1/P2 分级，CI 可集成） |
| 模板引擎化（cookiecutter） | ✅ 已完成 | ed8cc29 | `templates/cookiecutter-analysis/` + `scripts/cookiecutter-gen.sh` |
| 文档同步 | ✅ 已完成 | b5e8de0 | README / SKILL / plan / CHANGELOG |

### v1.3.0-dev — 已完成 ✅
| Phase | 状态 | 备注 |
|---|---|---|
| 阶段门控（stage-gate.md） | ✅ 已完成 | 3 层门控（工作流 / 子流程 / 子任务） |
| 设计回测（design-backtest.md） | ✅ 已完成 | 4 大类：数据 / 业务 / 状态机 / 字段 |
| 任务复盘（task-retrospective.md） | ✅ 已完成 | 5 问 + 知识库沉淀 |
| SKILL.md 集成双模式 §8.0-8.6 | ✅ 已完成 | 默认设计交接；实施扩展可选 |
| 脚本补实现 | ✅ 已完成 | 字段对齐、QA、SQL、HTML、并行委派、语义 smoke test |
| 模板与文档同步 | ✅ 已完成 | dev 设计模板 + cookiecutter 链接修正 |

### v1.4.0-dev — 开发中 🚧
| Phase | 状态 | 备注 |
|---|---|---|
| 26 个 skill 目录骨架 | ✅ 已完成 | 2 router + 9 动作 + 1 编排 + 7 bridge + 7 discipline |
| 9 个 user-invoked 动作 | ✅ 已完成 | grill-task / to-brd / to-prd / dev-design / qa-audit / handoff 等 |
| 2 个 router | ✅ 已完成 | ask-delivery / using-superpowers |
| 1 个 orchestration | ✅ 已完成 | analysis-delivery-workflow(9 阶段 + superpowers 衔接) |
| 7 个 superpowers bridge | ✅ 已完成 | brainstorming / writing-plans / tdd / 等(桥接层,内容指向官方) |
| 7 个 discipline | ✅ 已完成 | no-field-guessing / no-self-invent / stage-gate 等 |
| 删除 references/ | ✅ 已完成 | 13 篇已迁移到对应 skill |
| smoke test 适配 | ✅ 已完成 | 检查 26 个 skill + 各类目数量 |
| README / CHANGELOG 同步 | ✅ 已完成 | 加 v1.4.0-dev 条目 + 新结构说明 |
| **CHANGELOG 升 [1.3.0] tag** | ⬜ 待开始 | v1.3 稳定后发布正式版 |

### v2.0 — 全部完成 ✅
| Phase | 状态 | 备注 |
|---|---|---|
| examples/02-saas-dashboard(Node + React + PostgreSQL)| ✅ 已完成 | 12 个文件(BRD / 流程图 / 配置 / 状态机)|
| examples/03-mobile-app(Flutter + Firebase)| ✅ 已完成 | 12 个文件(含 PIPL 轻合规 / Firestore 字段 / FIFO 批次)|
| GitHub Actions(5 个 workflow)| ✅ 已完成 | smoke-test / sql-dialect-check / doc-validate / field-alignment-check / full-qa-audit |
| Issue / PR 模板 | ✅ 已完成 | bug_report.md / feature_request.md / PULL_REQUEST_TEMPLATE.md |
| CONTRIBUTING.md | ✅ 已完成 | 行为准则 + 开发流程 + 验证脚本 + 目录约定 |

### v3.0 — 部分完成 🚧
| Phase | 状态 | 备注 |
|---|---|---|
| ASCII 流程图 → Mermaid 转换器 | ✅ 已完成 | `scripts/flow-to-mermaid.py` |
| mermaid CLI → SVG/PNG 渲染 | ✅ 已完成 | `scripts/flow-export.sh`(mmdc 包装)|
| VSCode 扩展 scaffold | ✅ 已完成 | `vscode-extension/`(4 命令 + 配置)|
| drawio CLI 集成 | ⬜ 待开始 | 与 mermaid 互为补充 |
| docx 模板 | ⬜ 待开始 | python-docx-template(可选) |

---

**维护者**：Jason sun
**反馈渠道**：GitHub Issues（仓库地址待发布后补）
**协议**：MIT
