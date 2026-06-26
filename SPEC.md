# SPEC — Analysis to Delivery

> 功能规格说明书。读者：想自己改/扩展这个 skill 的开发者、想用它的人。
> 项目计划看 [plan.md](plan.md)，用户使用看 [README.md](README.md)。

## 1. 范围与定位

### 1.1 是什么
一个 Claude Code / Hermes 的 skill，提供**从需求澄清到开发设计**的 9 阶段标准化工作流。

### 1.2 不是什么
- **不是** 编码 skill（不写实际业务代码）—— 那是 `wms-code-implementation` 类 skill 的事
- **不是** 单一行业 skill（医药/金融/SaaS/移动 App 都适用）
- **不是** 单一技术栈 skill（Java/Go/Python/Node 全支持）

### 1.3 用户与场景
| 用户类型 | 典型使用场景 |
|---|---|
| 产品经理 | 收到一个模糊需求 → 跑工作流 → 产出可执行的 PRD |
| 架构师 | 设计新系统功能模块 → 产出 BRD/FSD/数据模型 |
| 高级开发 | 接到复杂功能开发任务 → 按 FSD 直接写代码 |
| AI 助手使用者 | 把工作流内化进自己的 AI 流程 |

## 2. 核心概念

### 2.1 三个角色
```
┌─────────────────────────────────────────────────┐
│  Skill (this)                                    │
│  提供 9 阶段工作流骨架 + 配置加载机制           │
└─────────────────┬───────────────────────────────┘
                  │ 由 Claude Code / Hermes 加载
                  ▼
┌─────────────────────────────────────────────────┐
│  AI 助手（执行者）                                │
│  按 SKILL.md 指引走流程，调用 config/ 加载领域   │
└─────────────────┬───────────────────────────────┘
                  │ 与用户协作
                  ▼
┌─────────────────────────────────────────────────┐
│  用户（项目方）                                   │
│  提供需求 + 行业上下文 + 确认各阶段产物           │
└─────────────────────────────────────────────────┘
```

### 2.2 关键术语
| 术语 | 含义 |
|---|---|
| **阶段 (Stage)** | 9 阶段工作流中的某一阶段（需求澄清、业务流程设计…） |
| **产物 (Deliverable)** | 某阶段产出的文档（如 BRD、FSD、PRD） |
| **配置 (Config)** | `config/` 目录下描述特定领域/技术栈的 markdown 文件 |
| **示例 (Example)** | `examples/` 目录下某个迷你项目的完整产物样例 |
| **模板 (Template)** | `templates/` 目录下空白的文档模板，用户可复制使用 |
| **参考 (Reference)** | `references/` 目录下方法论文档（流程图规范、字段对齐规范等） |

### 2.3 配置加载机制（v1.1 起以项目级为优先）

```
Claude 进入项目
        ↓
扫描项目根是否存在 *-path.md（项目级）
        ↓ Yes                    ↓ No
读取项目级                扫描 skill 自带 config/（skill 级）
        ↓                         ↓
注入到工作流相应阶段       项目级 + skill 级都缺？
        ↓                         ↓
按 9 阶段推进            主动问用户（默认）
```

**三层优先级**：

| 层级 | 位置 | 作用 | 优先级 |
|------|------|------|--------|
| **Level 1 项目级** | 项目根 `knowledge-path.md` 等 4 个文件 | 项目方自己填的真实配置（最准） | 最高 |
| **Level 2 skill 级** | `~/.claude/skills/analysis-to-delivery/config/` | skill 自带的示例 + fallback | 中 |
| **Level 3 默认** | Claude 询问用户 | 主动澄清，不擅自编造 | 兜底 |

**加载示例**：
- 项目根有 `tech-stack-path.md` 指向 Java 规范 → Claude 直接用项目级，不读 skill 级
- 项目根为空 + 用户说"这是医药物流项目" → Claude 加载 `config/compliance/{对应行业}.md` 作为参考（标注来源）
- 项目根为空 + 用户也未说明 → Claude **主动问用户**，禁止编造

## 3. 工作流定义

### 3.1 9 阶段总览

| # | 阶段 | 调用的 skill | 关键产物 | 是否可跳过 |
|---|---|---|---|---|
| 1 | 项目配置 | `/setup-analysis-delivery` | 4 个 `*-path.md` + 可选 `config-used.md` ADR | 新项目强制 |
| 2 | 需求澄清 | `/grill-task` | `TASK_CONFIRM_{项目}.md` + `REVIEW_需求确认书.md` + `REVIEW_字段对齐分析.md` | 否 |
| 3 | BRD | `/to-brd` | `01-业务需求文档 BRD.md` + ASCII 流程图 | 否 |
| 4 | 合规评审 | `/compliance-review` | `04-合规评审.md` | 无强合规可跳过 |
| 5 | 测试用例 | `/test-case-design` | `07-测试用例设计.md` | 否 |
| 6 | PRD | `/to-prd` | `05-产品需求文档 PRD.md`（可选 HTML/DOCX） | 否 |
| 7 | 开发设计 | `/dev-design` | `AGENTS.md` + FSD + 数据模型 + 开发设计 + 回测报告 | 中等及以上需求 |
| 8 | QA 审计 | `/qa-audit` | `09-QA审计报告.md` | 否 |
| 9 | 交接 | `/handoff` | `HANDOVER.md` | 否 |

### 3.2 阶段详细定义

#### 阶段 1：项目配置
**目标**：为真实项目建立配置指针，避免 skill 仓库内的示例配置污染项目事实。

**产物**：
- `knowledge-path.md`
- `compliance-path.md`
- `tech-stack-path.md`
- `doc-naming.md`
- `config-used.md`(可选;配置使用记录 / ADR,不参与配置加载)

#### 阶段 2：需求澄清
**目标**：用结构化文档把模糊需求转化为明确规格。

**流程**：
1. Claude 生成 `TASK_CONFIRM_{项目}.md`（参考 `templates/TASK_CONFIRM.md`）
2. 用户填写后告知 Claude
3. AI 助手读取并生成 `REVIEW_需求确认书.md` 和 `REVIEW_字段对齐分析.md`
4. `scripts/task-confirm-check.py --strict` 通过
5. 用户白名单话术签字 → 进入阶段 3

**关键纪律**：
- 严禁跳过确认书直接进入设计
- 字段对齐分析必须在确认后、设计前完成

#### 阶段 3：BRD
**目标**：把业务流画清楚，各方对流程达成一致。

**产物**：
- ASCII 流程图（状态流转图、业务流程图、泳道图）
- `01-业务需求文档 BRD.md`
- `业务流程图.drawio`（可选，用于可视化）

**关键纪律**：
- 禁用 Mermaid 作为交付源，终端优先使用 ASCII
- 字段映射表必须与知识库定义一致

#### 阶段 4：合规评审
**目标**：检查设计是否满足行业合规要求。

**流程**：
1. 加载 `compliance-path.md` 指向的合规条款
2. 按条款逐项评估设计
3. 输出 `04-合规评审.md`

#### 阶段 5：测试用例
**目标**：在开发前明确“什么算成功”。

**产物**：
- `07-测试用例设计.md`（参考 `templates/TEST_CASE_DESIGN.md`）

**关键纪律**：
- 必须覆盖正常路径、边界条件、异常路径、合规校验
- 强制阶段，不可跳过

#### 阶段 6：PRD
**目标**：把 BRD、合规评审和测试用例整合为产品需求文档。

**产物**：
- `05-产品需求文档 PRD.md`
- `05-PRD.html`（可选）
- `05-PRD.docx`（可选）

**关键纪律**：
- 字段名必须与知识库定义一致
- 业务同义不同名需在注释中显式标注

#### 阶段 7：开发设计
**目标**：把 PRD 翻译为可执行的技术实现方案。默认只产出设计交接文档；用户明确启用实施扩展时，才继续编排 TDD / execute / commit。

**产物**：
- `AGENTS.md`
- `02-功能规格说明书 FSD.md`
- `03-数据模型设计.md`
- `06-开发设计说明书.md`
- `08-设计回测报告.md`

**关键纪律**：
- 严禁只写后端，必须含前端 + 联调 + Mock
- 严禁降级为伪代码 / TODO
- 设计回测不通过禁止进入阶段 8

#### 阶段 8：QA 审计
**目标**：在交付前发现所有遗留问题。

**审计维度**：
1. 文档格式
2. 文档编号
3. 核心文档完整性
4. SQL 方言
5. 字段映射
6. 删除/修改精度

**产物**：
- `09-QA审计报告.md`
- 修复记录
- 一致性验证结果

#### 阶段 9：交接
**目标**：把设计文档移交给编码 skill 或开发团队。

**产物**：
- `HANDOVER.md`
- 待办事项清单
- 已知风险与限制

**触发**：转编码 skill，或直接进入开发冲刺。

## 4. 文档编号规范

**强制**：每个项目目录中，编号前缀只允许一个文件存在。

| 编号 | 文档 | 对应阶段 |
|---|---|---|
| 01 | 业务需求文档 BRD.md | 阶段 3 |
| 02 | 功能规格说明书 FSD.md | 阶段 7 |
| 03 | 数据模型设计.md | 阶段 7 |
| 04 | 合规评审.md | 阶段 4 |
| 05 | 产品需求文档 PRD.md | 阶段 6 |
| 06 | 开发设计说明书.md | 阶段 7 |
| 07 | 测试用例设计.md | 阶段 5 |
| 08 | 设计回测报告.md | 阶段 7 |
| 09 | QA 审计报告.md | 阶段 8 |

非编号文档(不占编号):

| 文档 | 对应阶段 |
|---|---|
| AGENTS.md | 阶段 7 |
| TASK_CONFIRM_*.md | 阶段 2 |
| REVIEW_*.md | 阶段 2 |
| RETRO_*.md | 阶段 7 / 实施扩展 |
| HANDOVER.md | 阶段 9 |

**冲突处理**：发现编号冲突 → 立即 `mv` 重命名，文档内部标题同步修正。

## 5. 文件命名规范

| 文件类型 | 命名格式 | 示例 |
|---|---|---|
| 需求确认表 | `TASK_CONFIRM_{项目名}.md` | `TASK_CONFIRM_收货管理.md` |
| 需求确认书 | `REVIEW_需求确认书.md` | `REVIEW_需求确认书.md` |
| 字段对齐分析 | `REVIEW_字段对齐分析.md` | `REVIEW_字段对齐分析.md` |
| 主文档 | `0X-{名称}.md` | `01-业务需求文档 BRD.md` |
| 配置 | `{类别}/{领域}.md` | `compliance/gsp.md` |
| 示例 | `examples/{编号}-{名称}/` | `examples/01-wms-warehouse/` |
| 模板 | `{文档名}.md` | `BRD.md` |
| 参考 | `{主题}.md` | `flow-chart-ascii.md` |

## 6. 配置接口契约

### 6.1 合规配置（`config/compliance/{行业}.md`）

**最小结构**：
```markdown
# {行业} 合规规则

## 适用范围
（哪些业务场景必须遵循此规则）

## 核心条款清单
| 条款编号 | 条款名称 | 缺陷等级 | 检查要点 |
|---|---|---|---|

## 评估方法
（按缺陷等级计算符合率）

## 判定标准
- ❌ 不符合：...
- ⚠️ 基本符合：...
- ✅ 符合：...
```

**MVP 提供的示例**：
- `gsp.md`（医药物流 GSP）
- `none.md`（无强合规要求场景）

### 6.2 技术栈配置（`config/tech-stack/{技术栈}.md`）

**最小结构**：
```markdown
# {技术栈} 规范

## 技术栈
- 后端：...
- 前端：...
- 数据库：...
- 中间件：...

## 分层架构
...

## 命名规范
- 表命名：...
- 字段命名：...
- 状态码：...

## 审计字段
（五件套）

## 关键约束
- ...
```

**MVP 提供的示例**：
- `java-spring.md`（Java + Spring Boot + MyBatis-Plus + Oracle）
- `frontend-vue.md`（Vue 3 + TS + Element Plus + Vite）

### 6.3 领域知识库配置（`config/domain-knowledge/{领域}.md`）

**最小结构**：
```markdown
# {领域} 知识库引用

## 必读文档
（项目相关的知识库文件路径列表）

## 字段映射表
（如有强制的字段映射）

## 状态码字典
（如有固定的状态码规范）

## 术语表
（领域特定术语解释）
```

### 6.4 文档命名配置（`config/doc-naming/{团队}.md`）

**最小结构**：
```markdown
# {团队} 文档命名规范

## 文档编号
（覆盖默认的 01-09 编号）

## 命名前缀
（如 P0 / Sprint-1 / ...）

## 存放路径
（如 docs/requirements/ vs 直接根目录）
```

### 6.5 项目级配置（canonical paths）

> v3.2.0-dev 起,新项目应在项目根目录的 `paths/` 下放 4 个 `*-path.md` 文件。Claude 优先读取项目级 `paths/*.md`,再 fallback 到 skill 级。
> `config-used.md` 是配置使用记录 / ADR 产物,不是配置文件,不参与配置加载。

#### 6.5.1 4 个文件一览

| 文件 | 项目级路径 | 模板 | 加载阶段 |
|------|-----------|------|----------|
| 知识库 | `paths/knowledge-path.md` | `paths/knowledge-path.md` | 2 / 7 |
| 合规 | `paths/compliance-path.md` | `paths/compliance-path.md` | 4 |
| 技术栈 | `paths/tech-stack-path.md` | `paths/tech-stack-path.md` | 1 / 7 |
| 文档命名 | `paths/doc-naming-path.md` | `paths/doc-naming-path.md` | 2-9 全部 |

`templates/project-config/*` 仅作为 legacy 兼容 wrapper 保留。旧项目根目录下的 `knowledge-path.md` / `compliance-path.md` / `tech-stack-path.md` / `doc-naming.md` 可被 `setup-check.py` 识别并产生迁移 warning。

#### 6.5.1a 非配置产物:`config-used.md`

`config-used.md` 可从 `templates/CONFIG_USED.md` 复制生成。它只记录"读取了哪些配置、为什么这么选、有哪些 ADR",不作为 Level 1 配置输入。

#### 6.5.2 加载优先级（强制）

```
项目级 paths/*.md（Level 1，最准）
    ↓ 未提供
skill 级 config/*.md（Level 2，示例库 + fallback）
    ↓ 仍未匹配
Claude 主动询问用户（Level 3，兜底；严禁编造）
```

#### 6.5.3 路径格式契约

| 项 | 规范 |
|---|---|
| 默认接受 | 本地**绝对路径**（Unix: `/path/...` 或 Windows: `D:\path\...`） |
| 也接受 | 相对项目根的相对路径（Claude 自动解析为绝对路径） |
| 谨慎接受 | HTTP/HTTPS URL — 必须加 ` # remote` 后缀明确授权 |
| 严禁 | 执行路径下任何代码 — 仅作 Markdown 文本读取 |

#### 6.5.4 文件最小结构

每个 `*-path.md` 文件最小结构（详见各自模板）：

```markdown
# {文件名}：项目级 {类型} 配置

## 路径列表
| 标签 | 路径 | 用途 | 必读？ |

## 加载规则
（明确 fallback 行为）

## 安全约束
（路径白名单 / 远程标注）
```

#### 6.5.5 一键初始化

```bash
# 在新项目根跑：
bash ~/.claude/skills/analysis-to-delivery/scripts/init-project-config.sh /path/to/project

# 会生成：
#   /path/to/project/knowledge-path.md
#   /path/to/project/compliance-path.md
#   /path/to/project/tech-stack-path.md
#   /path/to/project/doc-naming.md
# 全部带示例注释，用户填写真实内容。
```

#### 6.5.6 与 skill 级 config 的关系

| 维度 | 项目级（v1.1+） | skill 级（v1.0 中心化） |
|------|----------------|------------------------|
| 位置 | 项目根 | `~/.claude/skills/.../config/` |
| 优先级 | **最高** | 项目级未填时的 fallback |
| 维护者 | 项目方 | skill 维护者 |
| 适用场景 | 真实项目交付 | skill 内置示例 / 临时试用 |
| 版本控制 | 跟项目一起 commit | 跟 skill 一起发布 |

## 7. 脚本接口契约

### 7.1 `scripts/sql-dialect-check.py`

**功能**：检查 Markdown/SQL 文档中是否混用 Oracle / PostgreSQL / MySQL 方言。

**输入**：文件、目录或 glob；可选 `--dialect auto|oracle|postgres|mysql`；可选 `--json`。

**输出**：退出码 0 表示通过，1 表示发现方言问题，2 表示参数或路径错误。

### 7.2 `scripts/full-qa-audit.py`

**功能**：聚合文档校验、内部链接、编号冲突、核心文档完整性、SQL 方言、字段对齐。

**输入**：项目目录或单个 Markdown 文件；可选 `--json`。

**输出**：按 P0/P1/P2 分级的审计报告；P0 存在时退出码 1。

### 7.3 `scripts/field-alignment-check.py`

**功能**：检查文档引用字段是否在知识库中定义，并在双方都有定义时比较类型和可空性。

**输入**：文档路径 + 知识库文件路径；知识库支持 Markdown 表格和 SQL DDL；可选 `--json`。

**输出**：missing / type_mismatch / nullable_mismatch；任一不一致退出码 1。

### 7.4 `scripts/parallel-delegate.sh`

**功能**：基于本机 Claude CLI 并行执行多个任务文件。

**输入**：任务文件列表；可选 `--jobs`、`--out-dir`、`--timeout`、`--dry-run`。

**输出**：每个任务一份日志，全部成功退出码 0，有任务失败退出码 1，依赖缺失或参数错误退出码 2。

### 7.5 `scripts/postprocess_prd_html.py`

**功能**：将 pandoc 或普通 HTML 重组为带封面、目录、章节卡片、响应式和打印样式的 PRD HTML。

**输入**：`<input.html> <output.html>`。

**输出**：可直接浏览和打印的 HTML 文件。

## 8. 错误处理

### 8.1 找不到 config
**场景**：用户告知行业，但 `config/compliance/{行业}.md` 不存在。
**行为**：Claude 应提示用户用 `config/compliance/template.md` 自己创建，或选择近似行业配置。

### 8.2 字段不在知识库
**场景**：设计时引用的字段在知识库中未定义。
**行为**：Claude 应**严禁自行发明字段**，必须停下来问用户。详见 `references/field-alignment.md`。

### 8.3 流程图渲染问题
**场景**：ASCII 流程图在某终端下显示错乱。
**行为**：使用等宽字体（`Courier New` / `Consolas` / `Monaco`）。如果仍错乱，转用 `业务流程图.drawio`。

## 9. 版本兼容性

- **v1.x**：配置加载机制 + 9 阶段工作流保持兼容
- **v2.0**：可能引入 cookiecutter 模板引擎（破坏性变更，会升级主版本）
- **v3.0**：可能引入外部依赖（drawio CLI、mermaid CLI）

## 10. 安全与边界

### 10.1 严禁执行的操作
- ❌ 任何 DDL/DML 写操作（`CREATE`/`DROP`/`INSERT`/`UPDATE`/`DELETE`）
- ❌ 任何对外发起的 HTTP 请求（除用户明确授权外）
- ❌ 任何破坏性 git 操作（`push --force`、`reset --hard` 等）

### 10.2 允许的操作
- ✅ SELECT 查询（只读）
- ✅ 读存储过程/函数源码（只读）
- ✅ 文件读写（仅限 `~/.claude/skills/analysis-to-delivery/` 下的文件）
- ✅ 本地 git 操作（仅限 skill 自己的目录）

### 10.3 数据保护
- 不收集用户数据
- 不上传任何信息
- 所有产物保留在用户本地

## 11. 验收标准（MVP 1.0）

| # | 验收项 | 通过条件 |
|---|---|---|
| A1 | `install.sh` 可执行 | 装到 `~/.claude/skills/` 成功，SKILL.md 存在 |
| A2 | 目录结构完整 | `config/` `examples/` `references/` `templates/` `scripts/` 都有内容 |
| A3 | SKILL.md 可读 | 9 阶段工作流定义清晰，无 WMS 领域特定内容 |
| A4 | 1 个示例完整 | `examples/01-wms-warehouse` 含 BRD + 配置使用清单 |
| A5 | 4 个脚本可运行 | 跑 `--help` 不报错 |
| A6 | README 完整 | 用户能 5 分钟内完成安装和使用 |
| A7 | 文档自洽 | plan.md / SPEC.md / README.md 互相引用一致 |

## 12. 开放问题（MVP 期间需用户决策）

1. 是否需要 i18n？（v1.0 仅中文）
2. 是否支持 git submodule 安装方式？（v1.0 仅 curl 一键 + git clone）
3. 是否需要 Docker 镜像？（v1.0 不提供）

## 13. Rules and Paths 加载模型（v3.2.0-dev）

> 这是 `docs/plans/2026-06-25-rules-path-refactor.md` 的实现细节。

### 13.1 三层职责

```text
Skill = action or workflow entrypoint
rules = cross-stage invariant constraints
paths = project-owned context pointers
```

| 层 | 拥有 | 不拥有 |
|---|---|---|
| 根 `SKILL.md` | 触发、路由、快速开始、最小架构图 | 完整规则、阶段流程、大段示例 |
| `skills/user-invoked/*` | 一个用户可见动作及其产出 | 全局不变式或项目知识库 |
| `skills/orchestration/*` | 有序工作流编排 | 每个子 Skill 的细节实现 |
| `rules/*` | 跨阶段约束与硬门控 | 阶段级文档生成步骤 |
| `paths/*` | 项目级上下文指针 | 大段知识库或源码拷贝 |
| `templates/*` | 输出文档骨架 | 工作流控制逻辑 |
| `scripts/*` | 确定性校验与迁移助手 | 纯人工方法论文档 |

### 13.2 加载规则

```text
1. 加载被选中的 Skill（user-invoked 或 orchestration）
2. 读取该 Skill 的 Required rules / Required paths 声明
3. 仅按声明加载对应的 rules/*.md 与 paths/*.md
4. 禁止一次性全量加载所有 rules/* 与 paths/*
```

### 13.3 兼容策略

迁移期间，旧的位置仍然保留作为兼容壳：

| 旧位置 | 新位置 | 兼容方式 |
|---|---|---|
| `skills/disciplines/*/SKILL.md` | `rules/*.md` | 旧 Skill 是新规则的薄包装，仅指向 canonical |
| 项目根 `knowledge-path.md` 等 | `paths/*.md` | `setup-check.py` 优先 `paths/`,项目根文件接受并产生 warning |
| `templates/project-config/*` | `paths/*.md` | 旧模板变为兼容 wrapper，`init-project-config.sh --legacy` 仍可用 |
| frontmatter `requires:` | Contract 段 `Required rules:` / `Required paths:` | 两者并存；新代码以 Contract 段为准 |

兼容壳不得携带与 canonical 不同的规则文本。如发现分歧,以 canonical 为准。

## 14. Goal-Boundary Control（v3.2.0-dev）

> 配合 `rules/goal-boundary.md` 与 `scripts/goal-boundary-check.py`。

### 14.1 为什么需要

- 用户在第 2/3 阶段最常踩的坑是「本次到底要交付什么？做到什么程度？」模糊。
- 不显式区分「最终目标 / 本次边界 / 明确不解决」,后续 PRD / TC / HANDOVER 全部会跟着模糊。

### 14.2 校验对象

| 文档 | 校验点 | 严重度 |
|---|---|---|
| `TASK_CONFIRM_*.md` §二 | 含「做到什么程度」「不解决哪些」「是否分阶段」3 个必填问题 | error |
| `TASK_CONFIRM_*.md` §三 | 若分阶段是,至少 1 行 MVP / Phase 1,每行有 goal + acceptance | error |
| `05-PRD.md` §七 | 每条 AC 关联到阶段 | error |
| `07-测试用例设计.md` §三 | 每条 TC 关联到阶段 + 至少 1 个 AC | error / warning |
| `HANDOVER.md` §二 | 已达成 / 延后 / 剩余差距 三表填写 | warning |

### 14.3 与 PRD §九 / 模板的对应

- `templates/TASK_CONFIRM.md` §二 阶段目标
- `templates/REVIEW_需求确认书.md` §八 / §九 目标边界 + 阶段目标
- `templates/PRD.md` §九.1 完成边界 / §九.2 阶段映射
- `templates/TEST_CASE_DESIGN.md` §五 阶段覆盖检查
- `templates/HANDOVER.md` §二 阶段达成与剩余目标

---

**最后更新**：2026-06-26
**维护者**：Jason sun
**协议**：MIT
