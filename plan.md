# Plan — Analysis to Delivery

> **当前版本**:v4.0.0(2026-07-02)— P0-P3 共 12 项修复(详见 [CHANGELOG.md](./CHANGELOG.md) 与本文件下方 `### v4.0.0` 节)
> 前置版本:v4.0.0(2026-06-24)— grill-task 门控加固
> 更早:v3.0.0(2026-06-22)— 工具链 + VSCode 扩展
> 路线图详见下方各版本节。最新进度看 [README.md](README.md)，详细规格看 [SPEC.md](SPEC.md)。

## 愿景

把"需求 → 设计 → 开发"这条链路沉淀为一个**可复用、可配置、跨行业**的 AI 工作流框架。

任何团队拿到这个 skill 之后：
1. 告诉 Claude 自己的**领域**和**技术栈**
2. Claude 自动加载对应配置，按 9 阶段工作流推进
3. 产出可直接交给开发的设计文档（BRD/FSD/数据模型/PRD/开发设计/测试用例）

**目标用户**：3-10 人的小型软件团队的 AI 助手使用者（产品经理 + 架构师 + 高级开发）。

## 核心原则

| 原则 | 说明 |
|---|---|
| **大道至简** | 主文档只讲"怎么做"，领域细节全部放 config |
| **可插拔** | 用户只加载自己用得到的配置 |
| **跨行业** | 框架层通用;具体行业示例默认 3 个(医药 WMS/SaaS/移动 App),其他需用户补 config |
| **跨技术栈** | 流程骨架与语言无关;具体技术栈示例默认 3 套(Spring+Vue/Node+React/Flutter+Firebase),其他需用户补 config |
| **可审计** | 所有产物可追溯：每段文档对应哪个阶段、哪条配置 |
| **不重复造轮子** | 借用社区成熟工具（pandoc、drawio、Python），不重新发明 |

## 版本路线图

### v1.0（MVP，2026-Q2 已发布）— 最小可用
**目标**：跑通"通用工作流 + 1 个领域示例"，让用户能装能用。

**范围**：
- ✅ 通用 9 阶段工作流（SKILL.md 骨架）
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

### v4.0.0（2026-07-02,当前）— P0-P3 共 12 项修复
- 🆕 **6 个门控脚本** 覆盖 1→2 / 3→4 / 4→5 / 5→6 / 6→7 / 7→8 六个过渡点(plan §1)
- 🆕 **discipline 强制加载** frontmatter `requires:` + lint(plan §2)
- 🆕 **7 个 bridge 降级方案** + **flow-to-mermaid --ascii-strict**(plan §3-4)
- 🆕 **state 持久化** `.analysis-delivery-state.json`(plan §5)
- 🆕 **3 example 升级到 v4.0.0** 新增 04/05/07 文档(plan §9)
- 🆕 **快速通道/逆向使用/度量** 三大能力(plan §8)
- 🆕 **description 精简** + **反模式清单** + **config-used → decisions 改名**(plan §10-12)
- 详细 changelog 见 [CHANGELOG.md](./CHANGELOG.md) `[v4.0.0]` 节

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

## 架构演进

> 2026-07-02 会话沉淀。状态:**待用户拍板 P0 启动**。

### 背景

v4.0.0 已将 26 个 skill 收敛为「2 router + 9 动作 + 1 编排 + 7 bridge + 7 discipline」的清晰结构,但仍然存在两个架构层问题:

1. **上下文膨胀** — 7 个 discipline 全文 569 行,user-invoked 累计 921 行;`dev-design` 一个 skill 触发时实际加载 500+ 行纪律文本
2. **边界不清晰** — discipline 之间职责重叠(如 `no-field-guessing` vs `no-self-invent` 的 description 触发条件模糊),模型可能重复加载

### 根因分析

| 现象 | 根因 | 量化数据 |
|---|---|---|
| 单个 skill 上下文占用高 | discipline 是「主题切」,不区分阶段,触发即全量注入 | `dev-design` requires 5 个 discipline ≈ 500 行 |
| discipline 重复触发 | description 模糊,模型在多个 stage 都可能拉入 | 569 行 discipline 中至少 2 对职责重叠 |
| 路径边界不显式 | 仅靠 `context-pointer` 三层降级,目录切 ≠ 规则切 | 26 个 skill 跨阶段无物理隔离 |

### 三方案对比

| 维度 | A.完全 Rules + Path | **B.混合模式(推荐)** | C.不动,只内部重构 |
|---|---|---|---|
| 核心思路 | 抛弃 SKILLS,目录级 `.claude/rules/*.md` | SKILLS 保留,discipline 拆「微规则 + path」 | discipline 内部拆文件,SKILL.md 只留摘要 |
| 上下文控制 | 强(目录切 = 上下文切) | 中(摘要化 + path 触发) | 弱(仍是 description 触发) |
| 边界清晰度 | 高(物理目录隔离) | 中(显式依赖图 + path 字段) | 低(描述仍可能重叠) |
| 可组合性 | 弱 | 强(保留自由组合) | 强 |
| 学习曲线 | 低 | 中 | 低 |
| 迁移成本 | 高(推翻 26 个 skill) | 中(增量改造) | 低 |
| 适合场景 | 重写/标准化产品 | **演进中项目(本项目现状)** | 临时止血 |

### 推荐方案 B 设计

**核心原则:把"主题分"的 discipline 改成"路径分" + "微规则"**

#### B.1 Path 概念(目录级规则)

```
stage-requirements/CLAUDE.md   →  rules: [no-field-guessing, grill-protocol, stage-gate]
stage-design/CLAUDE.md         →  rules: [ascii-flowchart, doc-numbering, stage-gate]
stage-dev-design/CLAUDE.md     →  rules: [sql-dialect, no-field-guessing, doc-numbering, stage-gate]
stage-qa/CLAUDE.md             →  rules: [doc-numbering, sql-dialect, stage-gate]
```

#### B.2 Discipline 拆分为「微规则 + 指针」

**改造前**:每个 discipline 一个 80 行 SKILL.md,内容混合「触发条件 + 规则全文」

**改造后**:

```
disciplines/no-field-guessing/
  SKILL.md          ← 5 行(摘要 + 触发条件 + 路径指针)
  RULES.md          ← 实际规则全文(按需 fetch)
  applies-to.yaml   ← 声明:在哪些 stage-path 激活
```

**SKILL.md 模板**:

```markdown
---
name: <discipline-name>
description: <一句话触发条件>
applies-to: [stage-requirements, stage-dev-design, ...]   ← 新字段
---

# <Discipline-Name>

详见 [RULES.md](./RULES.md)。

触发:<何时调用>
路径:<context-pointer 三层降级>
```

#### B.3 requires 改成依赖图(显式化)

**改造前**(扁平列表,无法区分必选/可选/条件触发):

```yaml
requires: [no-field-guessing, no-self-invent, sql-dialect-discipline, stage-gate, doc-numbering]
```

**改造后**(分层):

```yaml
requires:
  must: [stage-gate]                                      # 没有就走不下去
  should: [no-field-guessing, doc-numbering]               # 强烈建议
  may: [sql-dialect-discipline]                           # 仅在涉及 SQL 时加载
  when:
    involves_sql: [sql-dialect-discipline]
    involves_field: [no-field-guessing]
```

模型按任务特征选择性加载,**避免一次性全量注入**。

#### B.4 Path 触发器(全局 CLAUDE.md 增量)

```markdown
## Path-based Rule Loading

| 工作目录前缀 | 自动激活 rules |
|---|---|
| `*/stage-requirements/*` | no-field-guessing, grill-protocol, stage-gate |
| `*/stage-design/*` | ascii-flowchart, doc-numbering, stage-gate |
| `*/stage-dev-design/*` | sql-dialect, no-field-guessing, doc-numbering, stage-gate |
| `*/stage-qa/*` | doc-numbering, sql-dialect, stage-gate |
```

### 实施路线(P0-P3,渐进式,避免大爆炸重写)

| 阶段 | 时间 | 动作 | 风险 | 预期收益 |
|---|---|---|---|---|
| **P0 止血** | 本周 | 7 个 discipline SKILL.md 全部瘦到 5-10 行摘要 + 指向 RULES.md | 低 | 上下文占用 -40% |
| **P1 路径化** | 2 周 | 4 个核心 user-invoked 加 `applies-to.yaml` + requires 依赖图改造 | 中(改 frontmatter) | discipline 选择性加载,边界显式化 |
| **P2 目录级 CLAUDE.md** | 1 月 | 项目根创建 `stage-*/CLAUDE.md`,模型 cd 进去自动激活 rules | 中(用户接受新目录结构) | 物理边界清晰,description 不再歧义 |
| **P3 全量迁移** | 1 季 | 26 个 skill 全部迁移到新结构 + 反向兼容老 frontmatter | 高(改 SKILL.md 规范) | 完整 path 化,体系成熟 |

### 关键判断

- ✅ SKILLS 本身设计合理(主题切可组合),不必推翻
- ✅ 真正的问题是「主题切」和「路径切」混用 → 引入显式 path 字段即可解
- ✅ 渐进式改造(P0→P3)风险可控,不破坏现有 26 个 skill 的工作流
- ⏸ P0 是否启动,等用户拍板

---

## 进度看板

### v1.0 MVP（2026-Q2）— 全部完成 ✅
| Phase | 状态 | Commit | 备注 |
|---|---|---|---|
| 建目录骨架 | ✅ 已完成 | 129dea6 | 2026-06-22 |
| 写 plan.md / SPEC.md / SKILL.md | ✅ 已完成 | 129dea6 | 2026-06-22 |
| 写 install.sh | ✅ 已完成 | 129dea6 | 含 --dry-run / --target / --uninstall / --version |
| 蒸馏 examples/01-wms-warehouse | ✅ 已完成 | 129dea6 | 8 个文件（BRD / 流程图 / 配置） |
| 写 README/LICENSE/CHANGELOG | ✅ 已完成 | 129dea6 | |
| 本地验证 | ✅ 已完成 | 129dea6 | 脚本 --help 全跑通 |
| git init + 推送 GitHub | ✅ 已完成 | b35d53e | BlueprintOS/analysis-to-delivery |

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

### v1.4.0-dev — 全部完成 ✅
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

### v2.0 — 全部完成 ✅
| Phase | 状态 | 备注 |
|---|---|---|
| examples/02-saas-dashboard(Node + React + PostgreSQL)| ✅ 已完成 | 12 个文件(BRD / 流程图 / 配置 / 状态机)|
| examples/03-mobile-app(Flutter + Firebase)| ✅ 已完成 | 12 个文件(含 PIPL 轻合规 / Firestore 字段 / FIFO 批次)|
| GitHub Actions(5 个 workflow)| ✅ 已完成 | smoke-test / sql-dialect-check / doc-validate / field-alignment-check / full-qa-audit |
| Issue / PR 模板 | ✅ 已完成 | bug_report.md / feature_request.md / PULL_REQUEST_TEMPLATE.md |
| CONTRIBUTING.md | ✅ 已完成 | 行为准则 + 开发流程 + 验证脚本 + 目录约定 |

### v3.0 — 核心完成 ✅(docx 推迟到 v4.0 候选)
| Phase | 状态 | 备注 |
|---|---|---|
| ASCII 流程图 → Mermaid 转换器 | ✅ 已完成 | `scripts/flow-to-mermaid.py` |
| mermaid CLI → SVG/PNG 渲染 | ✅ 已完成 | `scripts/flow-export.sh`(mmdc 包装)|
| ASCII 流程图 → drawio XML 转换器 | ✅ 已完成 | `scripts/flow-to-drawio.py`(与 mermaid 互为补充)|
| VSCode 扩展 scaffold | ✅ 已完成 | `vscode-extension/`(4 命令 + 配置)|
| docx 模板 | ⬜ 推迟 | python-docx-template,v4.0 候选(非阻塞,用户问起再启动)|

### v4.0.0 — 全部完成 ✅(2026-07-02 发版)
| Phase | 状态 | 备注 |
|---|---|---|
| P0-1 6 个门控脚本 + 6 workflow + 6 pytest | ✅ 已完成 | `scripts/{setup-check,brd-check,compliance-check,testcase-coverage-check,prd-check,dev-design-backtest}.py` |
| P0-2 discipline lint(frontmatter `requires:`) | ✅ 已完成 | 9 个 user-invoked SKILL.md + `scripts/discipline-lint.py` |
| P1-1 7 个 bridge 降级方案 | ✅ 已完成 | `skills/orchestration/development/*/SKILL.md` |
| P1-2 `flow-to-mermaid.py --ascii-strict` | ✅ 已完成 | 检测无回流 + `classDef` |
| P1-3 `analysis-state.py` 5 子命令 | ✅ 已完成 | init/record-gate/signoff/status/metrics |
| P1-4 数字打架修复 | ✅ 已完成 | 版本号 + 26 skill 数字复核 |
| P2-1 README 跨行业话术降级 | ✅ 已完成 | "已覆盖 vs 未覆盖"对照表 |
| P2-2 快速通道/逆向使用/度量 | ✅ 已完成 | SKILL.md + README.md 各增 3 章节 |
| P2-3 3 example 升级到 v4.0.0 | ✅ 已完成 | 04/05/07 三文档 × 3 example |
| P3-1 description 精简到 80-150 字符 | ✅ 已完成 | 26 个 SKILL.md 全过 `description-lint.py` |
| P3-2 9 个 SKILL.md 补反模式清单 | ✅ 已完成 | `scripts/antipattern-section-check.py` 校验 ≥3 条 |
| P3-3 config-used.md → decisions.md 改名 | ✅ 已完成 | 3 example + templates + `filename-naming-check.py` |

### 待发布的 Git tag(发布流程,非开发任务)

| Tag | 触发条件 | 命令 |
|---|---|---|
| `[1.3.0]` | v1.3.0-dev 稳定后切 | `git tag -a 1.3.0 -m "v1.3.0: 双模式 + 设计回测 + 任务复盘"` |
| `[1.4.0]` | v1.4.0-dev 稳定后切 | `git tag -a 1.4.0 -m "v1.4.0: 拆分为 26 个独立 skill"` |
| `[2.0.0]` | v2.0 多示例 + CI 验证后切 | `git tag -a 2.0.0 -m "v2.0.0: 多领域示例 + GitHub Actions"` |
| `[3.0.0]` | v3.0 工具链验证后切 | `git tag -a 3.0.0 -m "v3.0.0: drawio/mermaid CLI + VSCode 扩展"` |
| `[4.0.0]` | v4.0.0 P0-P3 12 项修复合并后切 | `git tag -a 4.0.0 -m "v4.0.0: P0-P3 共 12 项修复(6 门控 + discipline lint + bridge + flow strict + state + 3 example + description + 反模式 + decisions)"` |

> 当前 main 已具备以上所有能力,但未打 tag — 是否切 tag 由维护者按发版节奏决定。

---

**维护者**：Jason sun
**反馈渠道**：GitHub Issues（仓库地址待发布后补）
**协议**：MIT
