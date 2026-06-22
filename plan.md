# Plan — Analysis to Delivery

> 项目路线图。最新进度看 [README.md](README.md)，详细规格看 [SPEC.md](SPEC.md)。

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

### v1.1（计划 2026-Q3）— 配置库完善
- 补充 5-8 个常用合规规则（HIPAA / SOX / 等保 2.0 / GDPR / PCI-DSS / 工业互联网安全）
- 补充 6-8 个常用技术栈（Java+Spring+MySQL / Python+Django / Go+Gin / Node+NestJS / .NET Core / Rust+Actix）
- 补充 3-5 个常用领域知识库引用模板

### v1.2（计划 2026-Q3）— 测试增强
- 集成 v1.0 skill 的自检脚本（skill 装完后自动跑 smoke test）
- 文档产物模板添加"自动校验"按钮
- 模板引擎化（用 cookiecutter / copier 替代手写）

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

| Phase | 状态 | 备注 |
|---|---|---|
| 建目录骨架 | ✅ 已完成 | 2026-06-22 |
| 写 plan.md | ✅ 已完成 | 2026-06-22 |
| 写 SPEC.md | ⏳ 进行中 | |
| 写 SKILL.md | ⬜ 待开始 | |
| 写 install.sh | ⬜ 待开始 | |
| 蒸馏 examples/01-wms-warehouse | ⬜ 待开始 | |
| 写 README/LICENSE/CHANGELOG | ⬜ 待开始 | |
| 本地验证 | ⬜ 待开始 | |
| git init | ⬜ 待开始 | 等待 GitHub 仓库地址 |
| 推送 GitHub | ⬜ 待开始 | 等待用户授权 |

---

**维护者**：Jason sun
**反馈渠道**：GitHub Issues（仓库地址待发布后补）
**协议**：MIT
