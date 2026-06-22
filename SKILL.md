---
name: analysis-to-delivery
description: 通用需求分析到开发设计工作流 - 跨行业、跨技术栈的 10 阶段标准化流程，支持合规规则、技术栈、领域知识库的可插拔配置
category: software-development
version: 1.0.0-mvp
created: 2026-06-22
updated: "2026-06-22: MVP 初版"
---

# Analysis to Delivery

> 从需求澄清到开发设计的通用工作流框架。
> 项目计划：[plan.md](plan.md) · 详细规格：[SPEC.md](SPEC.md) · 项目说明：[README.md](README.md)

## 适用场景

用户提出任意业务功能需求（不限于特定行业/技术栈）时，按本工作流进行系统化分析和文档输出。

**不适用**：
- 纯编码任务（用 `wms-code-implementation` 等编码 skill）
- 极简单需求（"加个字段"级别，直接改就行）

## 工作流总览（10 阶段）

```
需求澄清 → 业务流程 → 合规评审 → 系统方案 → 测试用例
    ↓
PRD 生成 → 文档委派 → 开发设计 → QA 审计 → 代码交接
```

| # | 阶段 | 关键产物 | 强制？ |
|---|---|---|---|
| 1 | 需求澄清 | `TASK_CONFIRM_*.md` + `REVIEW_需求确认书.md` | 强制 |
| 2 | 业务流程设计 | ASCII 流程图 + `01-BRD.md` + `业务流程图.drawio` | 强制 |
| 3 | 合规性评审 | `04-合规评审.md` | 简单需求可跳 |
| 4 | 系统功能方案 | Figma 设计文档 | 按需 |
| 5 | 测试用例设计 | `07-测试用例设计.md` | 强制 |
| 6 | PRD 生成 | `05-PRD.md`（Markdown + HTML + DOCX） | 强制 |
| 7 | 文档委派 | `AGENTS.md` + 委派生成各文档 | 中等+ |
| 8 | 开发设计 | FSD + 数据模型 + 开发设计说明书 | 中等+ |
| 9 | QA 审计 | 审计报告 + 修复 patch | 强制 |
| 10 | 代码交接 | `HANDOVER.md` | 强制 |

详细每阶段产物见 [SPEC.md §3.2](SPEC.md#32-阶段详细定义)。

## 配置加载机制（核心，v1.1 起以项目级为优先）

**理念**：通用工作流骨架 + **项目级可插拔**配置。每个项目根目录放自己的 4 个 `*-path.md` 文件，Claude 优先读项目级的；项目级没填时 fallback 到 skill 自带的示例；都没有时主动问用户。

### 配置层级（从高到低）

```
┌─────────────────────────────────────────┐
│  Level 1：项目级（最高优先级）            │
│  位置：项目根目录                         │
│  文件：                                 │
│    knowledge-path.md                     │
│    compliance-path.md                    │
│    tech-stack-path.md                    │
│    doc-naming.md                         │
└──────────────┬──────────────────────────┘
               │ 项目级未填写 → fallback
               ▼
┌─────────────────────────────────────────┐
│  Level 2：skill 级（示例库 + fallback）  │
│  位置：~/.claude/skills/analysis-to-delivery/config/ │
│  文件：compliance/{gsp,none,...}.md 等    │
└──────────────┬──────────────────────────┘
               │ 仍不匹配 → fallback
               ▼
┌─────────────────────────────────────────┐
│  Level 3：默认（通用流程）                │
│  行为：Claude 主动询问用户                │
└─────────────────────────────────────────┘
```

### 加载规则

| 用户回答 / 项目状态 | 加载路径 |
|---|---|
| 项目根有 `knowledge-path.md`，列了真实路径 | **Level 1** 直接读项目填的路径 |
| 项目根没有 `*-path.md`，且命中 skill 级 fallback（如行业关键字） | **Level 2** 用 `config/compliance/{行业}.md` 或 `config/tech-stack/{栈}.md` 作为示例参考（标注来源） |
| 项目根 + skill 都没有匹配 | **Level 3** Claude 必须主动问用户，禁止编造 |

### 4 个项目级 config 文件一览

| 文件 | 作用 | 详见 |
|------|------|------|
| `knowledge-path.md` | 列项目涉及的外部知识库（领域表结构、合规法规等）的真实路径 | [templates/project-config/knowledge-path.md](templates/project-config/knowledge-path.md) |
| `compliance-path.md` | 列项目适用的合规规则文件路径 + 启用开关 | [templates/project-config/compliance-path.md](templates/project-config/compliance-path.md) |
| `tech-stack-path.md` | 列后端/前端/数据库/中间件 + 团队规范路径 | [templates/project-config/tech-stack-path.md](templates/project-config/tech-stack-path.md) |
| `doc-naming.md` | 文档编号、命名前缀、存放目录 | [templates/project-config/doc-naming.md](templates/project-config/doc-naming.md) |

### 一键初始化

在新项目里跑：

```bash
~/.claude/skills/analysis-to-delivery/scripts/init-project-config.sh /path/to/your-project
```

会自动在项目根生成 4 个空模板（带示例注释），用户填写真实内容后提交到 git。

### 配置缺失处理

如果用户行业/技术栈不在 `config/` 中：
- 用 `config/compliance/template.md` 或 `config/tech-stack/template.md` 让用户复制改
- 或选近似配置参考
- **严禁 Claude 自行编造合规规则或技术规范**

完整契约见 [SPEC.md §6.5](SPEC.md#65-项目级配置-v11)。

---

## 阶段 1：需求澄清（强制）

### 1.1 生成《需求确认表》

**触发**：用户提出新需求时。

**流程**：
1. 加载 `templates/TASK_CONFIRM.md` 模板
2. 替换项目名、日期，生成 `TASK_CONFIRM_{项目名}.md` 到工作目录
3. 告知用户填写并保存

**核心理念**：用结构化文档替代碎片化对话，避免遗漏、可追溯。

### 1.2 生成《需求确认书》

**触发**：用户告知"已填写"。

**流程**：
1. 读取用户填写的 `TASK_CONFIRM_*.md`
2. 加载 `templates/REVIEW_需求确认书.md`
3. 逐项标注 AI 助手的理解，列出待确认的设计假设
4. 输出 `REVIEW_需求确认书.md`

**⚠️ 关键纪律**：
- 用户填写完 `TASK_CONFIRM` 后，**严禁直接跳进阶段 2 设计**
- 必须先出确认书让用户审阅
- 用户确认通过 → 进入阶段 2

### 1.3 字段对齐分析（涉及现有表时强制）

**触发**：需求涉及**现有表查询/维护类功能**时。

**⚠️ 实战教训**：跳过此步直接设计 → 产出表名/字段名错误。

**流程**：
1. 提取需求中提到的所有表名和字段名
2. 与 `config/domain-knowledge/{领域}.md` 引用的知识库核对
3. 输出 `REVIEW_字段对齐分析.md`：
   - ✅ 已对齐
   - ⚠️ 需 JOIN
   - ❓ 待确认（业务同义不同名）
   - 🔴 缺失
4. 用户确认后再进入阶段 2

详细方法见 [references/field-alignment.md](references/field-alignment.md)。

---

## 阶段 2：业务流程设计

### 2.1 流程图规范（强制）

| 类型 | 工具 | 备注 |
|---|---|---|
| 状态流转图 | **ASCII 文本字符** | ⛔ **禁用 Mermaid**（用户验证：终端渲染差） |
| 业务流程图 | ASCII / Draw.io | 简单用 ASCII，复杂用 Draw.io |
| 泳道图 | ASCII | 角色分工清晰 |

**回流闭环画法**（强制）：所有回流路径箭头必须汇聚到同一目标节点并画线连回。

详细规范见 [references/flow-chart-ascii.md](references/flow-chart-ascii.md)。

### 2.2 DB 验证（如涉及现有数据库）

- 仅允许 `SELECT` 查询
- 用 `desc table_name` 验证字段定义
- **严禁** 任何 DDL/DML 写操作

### 2.3 输出

- `01-业务需求文档 BRD.md`
- `业务流程图.drawio`（可选，用于可视化）

---

## 阶段 3：合规性评审

### 3.1 触发条件

| 需求类型 | 是否需要 |
|---|---|
| 涉及个人健康信息（PHI） | ✅ 必须 |
| 涉及支付/金融 | ✅ 必须 |
| 涉及个人身份信息（PII） | ✅ 必须 |
| 纯内部工具 | ⚠️ 按团队规范 |

### 3.2 评审方法

1. 加载 `config/compliance/{行业}.md`
2. 按条款逐项评估设计
3. 输出 `04-合规评审.md`

**格式**：

| 条款编号 | 缺陷等级 | 检查要点 | 合规设计 | 证据位置 | 状态 |
|---|---|---|---|---|---|
| **{条款编号} | {严重/主要/一般} | {检查要点} | {合规设计摘要} | FSD §{章节号} | ✅ |

**判定标准**：
- ✅ 符合：完全满足
- ⚠️ 不符合：存在合规缺口
- 🔄 不适用：条款不适用本功能

详细评分方法见 [SPEC.md §3.2](SPEC.md#3-合规性评审)。

---

## 阶段 4：系统功能方案

### 4.1 触发条件

| 需求类型 | 是否需要 Figma 设计 |
|---|---|
| 简单需求（加字段/调规则） | ❌ 跳过 |
| 中等需求（新增功能/页面改造） | ✅ 需要 |
| 复杂需求（跨模块/多角色/算法介入） | ✅ 需要 |

### 4.2 输出规范

- 页面布局、组件清单、交互流程、状态标注、跳转关系
- 按目标端（PC/Pad/移动）严格遵循对应 UI 规范

详细规范见 [references/figma-design-doc.md](references/figma-design-doc.md)。

---

## 阶段 5：测试用例设计（强制）

**目的**：在开发前明确"什么算成功"。

**模板**：`templates/TEST_CASE_DESIGN.md`

**覆盖范围**：
- 正常路径
- 边界条件
- 异常路径
- 合规校验
- 性能/安全（如适用）

---

## 阶段 6：PRD 生成

### 6.1 三格式输出

| 格式 | 用途 | 生成方式 |
|---|---|---|
| Markdown | 源文件、版本管理 | 手工编写 |
| HTML | 浏览器阅读、分享 | pandoc + 后处理 |
| DOCX | Word 阅读、批注 | pandoc |

### 6.2 关键纪律

- 字段名必须与知识库定义一致
- 业务同义不同名需在 PRD 注释中**显式标注**（"业务上称为 X = 知识库定义的 Y"）
- 严禁自行发明字段

详细规范见 [references/prd-output.md](references/prd-output.md)。

---

## 阶段 7：文档委派

### 7.1 项目级 AI 助手配置

**首生成**：在项目根目录生成 `AGENTS.md`（参考 `templates/AGENTS.md`）。

**作用**：
- 列出项目约束、文档索引、分层架构规则
- Claude 后续委派时自动加载，避免每次重复说明
- 渐进式披露：地图而非手册

### 7.2 委派策略

- **并行委派**：`scripts/parallel-delegate.sh` 同时启动多个子代理
- **粒度拆分**：单次委派 ≤ 5 分钟工作量
- **完整字段清单**：委派时必须显式列出真实表名+字段清单，**不能只说"严禁猜测"**

---

## 阶段 8：开发设计

> v1.1 起去掉 V1（存储过程版）/ V2（代码实现版）双版本概念，统一为单一"代码实现版"工作流。
> 业务逻辑不再单独出 PL/SQL 包文档，直接在开发设计说明书中体现。

### 8.1 FSD（功能规格说明书）

**目的**：把 PRD 的"业务需求"翻译成"功能视角的规格"——模块怎么切、接口怎么定、状态怎么转、错误怎么返。

**产物**（参考 `templates/FSD.md`）：
- 模块清单
- 功能详述（输入 / 输出 / 业务规则 / 边界条件 / 异常路径）
- 接口契约（REST / RPC / 消息，含入参出参错误码）
- 状态机（关键业务对象的状态流转）
- 数据模型概览（哪些表、哪些字段、哪些关联）
- 业务错误码字典

**输出**：`02-功能规格说明书 FSD.md`

### 8.2 数据模型设计

**目的**：FSD 基础上定表结构、新增字段、索引、初始化数据。

**产物**（参考 `templates/数据模型设计.md`）：
- 表清单（新增 / 扩展）
- 表结构（字段、类型、可空、默认值、注释、索引）
- 序列定义
- 字段对齐验证（与知识库核对）
- 初始化数据
- 迁移脚本（如适用）

**输出**：`03-数据模型设计.md`

### 8.3 开发设计说明书（代码实现版）

**目的**：技术视角的完整实现方案，含前后端 + 联调 + Mock。

**产物**（参考 `templates/开发设计说明书.md`）：
- 架构设计（分层、关键依赖）
- 后端分层（Controller / Service / Repository / Entity / Mapper XML / DTO/VO）
- 事务与异常处理
- **前端组件**（PC + APP，按需）
- 联调说明（接口清单、步骤、Mock 数据）
- 错误码映射
- Checklist

**输出**：`06-开发设计说明书.md`

**⚠️ 关键纪律**：
- 严禁只写后端（必须含前端 + 联调 + Mock）
- 严禁降级为伪代码 / TODO 列表
- 遇错重试，不跳过
- 字段名 / 表名 / 状态码必须与 `knowledge-path.md` 引用的知识库一致
- PL/SQL 包、专有消息协议接口等不再单独成文档；如确需，**内嵌在 FSD 的接口契约或开发设计的异常处理小节**

---

## 阶段 9：QA 审计（强制）

### 9.1 审计维度

1. 公式正确性
2. SQL 方言一致性（`scripts/sql-dialect-check.py`）
3. 部署清单完整性
4. 跨文档交叉引用一致性
5. 字段映射一致性（`scripts/field-alignment-check.py`）
6. 删除/修改的精度

### 9.2 审计流程

1. 跑 `scripts/full-qa-audit.py {项目目录}`
2. 按 P0 / P1 / P2 分级输出
3. 委派 Claude 修复 P0
4. 重跑确认 P0 修复
5. 输出审计报告

---

## 阶段 10：代码交接

### 10.1 交接清单（`HANDOVER.md`）

- 已完成文档清单
- 待办事项
- 已知风险与限制
- 后续工作建议

### 10.2 触发

- 转交编码 skill（`wms-code-implementation` 等）
- 或直接进入开发冲刺

---

## 文档编号规范（强制）

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
| - | AGENTS.md | 7 |
| - | TASK_CONFIRM_*.md | 1 |
| - | REVIEW_*.md | 1 |
| - | HANDOVER.md | 10 |

**规则**：每个编号在同一项目目录中只允许一个 `0X-` 开头的文件。Figma 设计文档不受此编号约束（命名为 `Figma设计文档_{功能名}_{端}.md`）。

---

## 关键工作流纪律（实战教训 2024-2026）

### 严禁猜测
- **严禁猜测字段名** — 任何涉及数据库字段的文档，必须先到知识库核对
- **严禁猜测状态码** — 使用 config/tech-stack 中定义的常量
- **严禁猜测合规条款** — 使用 config/compliance 中定义的规则

### 严禁跳过
- 阶段 1 需求确认书（不可跳）
- 阶段 5 测试用例设计（不可跳）
- 阶段 9 QA 审计（不可跳）

### 严禁自创
- **严禁自创字段** — 用占位符 `EXT_FIELD_X`（如知识库允许）
- **严禁自创表名** — 用 `C_` 前缀（如新业务表）
- **严禁修改原生表结构** — 只新增或扩展

### 文档一致性
- 同一规则在 BRD/FSD/PRD/数据模型/开发设计中**描述必须完全一致**
- 字段名/类型/长度/可空性 4 项必须与知识库一致
- 任何修改必须**级联更新所有相关文档**（一次 patch 修完）

详细实战教训见 [references/workflow-discipline.md](references/workflow-discipline.md)。

---

## 关联参考

| 类别 | 文件 |
|---|---|
| 工作流纪律 | [references/workflow-discipline.md](references/workflow-discipline.md) |
| 字段对齐 | [references/field-alignment.md](references/field-alignment.md) |
| 流程图规范 | [references/flow-chart-ascii.md](references/flow-chart-ascii.md) |
| Figma 设计文档 | [references/figma-design-doc.md](references/figma-design-doc.md) |
| PRD 输出 | [references/prd-output.md](references/prd-output.md) |
| 开发设计规范（v1.1） | [references/dev-design-spec.md](references/dev-design-spec.md) |
| QA 审计清单 | [references/qa-audit-checklist.md](references/qa-audit-checklist.md) |
| 安全批量编辑 | [references/safe-bulk-editing.md](references/safe-bulk-editing.md) |
| Draw.io 生成 | [references/drawio-guide.md](references/drawio-guide.md) |
| 文档编号 | [references/doc-numbering.md](references/doc-numbering.md) |

## 关联模板

| 文档 | 模板 |
|---|---|
| 需求确认表 | [templates/TASK_CONFIRM.md](templates/TASK_CONFIRM.md) |
| 需求确认书 | [templates/REVIEW_需求确认书.md](templates/REVIEW_需求确认书.md) |
| 字段对齐分析 | [templates/REVIEW_字段对齐分析.md](templates/REVIEW_字段对齐分析.md) |
| AGENTS.md | [templates/AGENTS.md](templates/AGENTS.md) |
| BRD | [templates/BRD.md](templates/BRD.md) |
| FSD | [templates/FSD.md](templates/FSD.md) |
| 数据模型设计 | [templates/数据模型设计.md](templates/数据模型设计.md) |
| 合规评审 | [templates/合规评审.md](templates/合规评审.md) |
| PRD | [templates/PRD.md](templates/PRD.md) |
| 开发设计说明书 | [templates/开发设计说明书.md](templates/开发设计说明书.md) |
| 测试用例设计 | [templates/TEST_CASE_DESIGN.md](templates/TEST_CASE_DESIGN.md) |
| **项目级配置（v1.1）** | [templates/project-config/knowledge-path.md](templates/project-config/knowledge-path.md) |
| **项目级配置（v1.1）** | [templates/project-config/compliance-path.md](templates/project-config/compliance-path.md) |
| **项目级配置（v1.1）** | [templates/project-config/tech-stack-path.md](templates/project-config/tech-stack-path.md) |
| **项目级配置（v1.1）** | [templates/project-config/doc-naming.md](templates/project-config/doc-naming.md) |

## 关联示例

| 行业/场景 | 示例 |
|---|---|
| 医药物流 | [examples/01-wms-warehouse/](examples/01-wms-warehouse/) |

## 关联配置（MVP 1.0）

| 类别 | 文件 |
|---|---|
| 合规规则 | [config/compliance/gsp.md](config/compliance/gsp.md)（医药示例） |
| 合规规则 | [config/compliance/none.md](config/compliance/none.md)（无强合规） |
| 合规模板 | [config/compliance/template.md](config/compliance/template.md) |
| 技术栈 | [config/tech-stack/java-spring.md](config/tech-stack/java-spring.md) |
| 技术栈 | [config/tech-stack/frontend-vue.md](config/tech-stack/frontend-vue.md) |
| 技术栈模板 | [config/tech-stack/template.md](config/tech-stack/template.md) |
| 领域知识 | [config/domain-knowledge/template.md](config/domain-knowledge/template.md) |
| 文档命名 | [config/doc-naming/template.md](config/doc-naming/template.md) |

## 关联脚本

| 脚本 | 用途 |
|---|---|
| `scripts/install.sh` | 一键安装到 `~/.claude/skills/` |
| `scripts/init-project-config.sh` | 在项目根生成 4 个 *-path.md 空模板（v1.1+） |
| `scripts/sql-dialect-check.py` | SQL 方言混用检查 |
| `scripts/full-qa-audit.py` | 6 大类全量 QA 审计 |
| `scripts/field-alignment-check.py` | 字段对齐验证 |
| `scripts/parallel-delegate.sh` | 并行委派 Claude 子代理 |

---

## 安全边界

- ❌ **严禁** 任何 DDL/DML 写操作（建表/改字段/插入/删除）
- ❌ **严禁** 任何对外 HTTP 请求（除用户明确授权外）
- ❌ **严禁** 破坏性 git 操作
- ✅ **允许** SELECT 查询（只读）
- ✅ **允许** 文件读写（仅限工作目录）
- ✅ **允许** 本地 git 操作（仅限项目目录）

DDL/DML 操作必须由用户人工执行，Claude 标记为"待人工执行"清单。

---

**版本**：1.0.0-mvp（2026-06-22）
**维护者**：Jason sun
**协议**：MIT
