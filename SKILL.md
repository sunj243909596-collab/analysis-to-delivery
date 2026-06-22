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
PRD 生成 → 文档委派 → 开发设计(V1→V2) → QA 审计 → 代码交接
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
| 8 | 开发设计 | V1（存储过程）→ V2（代码实现） | 中等+ |
| 9 | QA 审计 | 审计报告 + 修复 patch | 强制 |
| 10 | 代码交接 | `HANDOVER.md` | 强制 |

详细每阶段产物见 [SPEC.md §3.2](SPEC.md#32-阶段详细定义)。

## 配置加载机制（核心）

**理念**：通用工作流骨架 + 可插拔领域配置。不同行业/技术栈只需加载不同 `config/` 文件。

### 加载触发

Claude 在阶段 1（需求澄清）时询问用户：

```
"本项目属于哪个领域？后端/前端/数据库各用什么技术栈？是否有强制合规要求？"
```

### 加载规则

根据用户回答，加载对应 config：

| 用户回答 | 加载的 config |
|---|---|
| 医药物流 / WMS | `config/compliance/gsp.md` + `config/tech-stack/java-spring.md` |
| 医疗健康 | `config/compliance/hipaa.md` + `config/tech-stack/{用户指定}` |
| 金融支付 | `config/compliance/sox.md` + `config/tech-stack/{用户指定}` |
| SaaS 后台 | `config/compliance/none.md` + `config/tech-stack/{用户指定}` |
| 移动 App | `config/compliance/none.md` + `config/tech-stack/{用户指定}` |
| 未说明 / 不确定 | 不加载任何 config，走默认通用流程 |

### config 缺失处理

如果用户行业/技术栈不在 `config/` 中：
- 用 `config/compliance/template.md` 或 `config/tech-stack/template.md` 让用户复制改
- 或选近似配置参考
- **严禁 Claude 自行编造合规规则或技术规范**

config 编写方法见 [SPEC.md §6](SPEC.md#6-配置接口契约)。

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
| **00201 | 严重 | 追溯完整性 | ... | FSD §3 | ✅ |

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

## 阶段 8：开发设计（V1 → V2）

### 8.1 V1（存储过程 / 详细设计版）

**适用**：复杂业务逻辑、需精准 SQL 设计、性能敏感场景。

**产物**：
- PL/SQL 包清单
- 包规范 + 包体
- 核心 SQL
- 错误码定义
- tXML 接口
- 部署清单

**输出**：`02-功能规格说明书 FSD.md` + `03-数据模型设计.md`

### 8.2 V2（代码实现版）

**触发**：用户确认 V1 后。

**产物**：
- 后端分层（Controller / Service / Repository / Entity）
- Service 实现
- Mapper XML
- DTO / VO
- REST API
- 事务异常处理
- **前端组件**（PC + APP，按需）
- 联调说明
- Mock 数据
- Checklist

**输出**：`06-开发设计说明书.md`

**⚠️ 关键纪律**：
- 严禁一次生成两个版本（V1 → 用户确认 → V2）
- V2 严禁降级（遇错重试，不跳过）
- V2 文档必须含前端 + 联调，仅有后端视为不完整

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
| 02 | 功能规格说明书 FSD.md | 8 (V1) |
| 03 | 数据模型设计.md | 8 (V1) |
| 04 | 合规评审.md | 3 |
| 05 | 产品需求文档 PRD.md | 6 |
| 06 | 开发设计说明书.md | 8 (V2) |
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
| V1/V2 双版本 | [references/v1-v2-versioning.md](references/v1-v2-versioning.md) |
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
