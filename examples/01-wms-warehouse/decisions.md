# Decisions（ADR / 决策记录）— 医药物流 WMS 收货管理（v3.1.0）

> v3.1.0 起，本文件从 `config-used.md` 改名为 `decisions.md`（更准确反映 ADR 性质）。
> 每个项目根目录放自己的 4 个 `*-path.md` 文件，Claude 优先读项目级的。
> 本目录（`examples/01-wms-warehouse/`）模拟一个完整迷你项目的根，演示项目级配置长什么样。
> 本文件是 ADR / 决策记录，不是配置文件，不参与配置加载。

## 项目级 config 文件（v3.1.0 推荐方式）

本示例的"项目根"下放了 4 个 `*-path.md`，都是真实的项目级配置：

| 文件 | 加载阶段 | 关联模板 |
|------|---------|---------|
| [`knowledge-path.md`](./knowledge-path.md) | 2 / 7 | [templates/project-config/knowledge-path.md](../../templates/project-config/knowledge-path.md) |
| [`compliance-path.md`](./compliance-path.md) | 4 | [templates/project-config/compliance-path.md](../../templates/project-config/compliance-path.md) |
| [`tech-stack-path.md`](./tech-stack-path.md) | 1 / 7 | [templates/project-config/tech-stack-path.md](../../templates/project-config/tech-stack-path.md) |
| [`doc-naming.md`](./doc-naming.md) | 2-9 全部 | [templates/project-config/doc-naming.md](../../templates/project-config/doc-naming.md) |

## 加载效果

Claude 进入 `examples/01-wms-warehouse/` 时：

1. **先扫项目根** → 发现 4 个 `*-path.md` → 按 Level 1 加载
2. **不再 fallback 到 skill 级**（项目级已填）
3. 按 4 个文件中的真实路径，去读 `/root/WMOS 知识库/` 等

### 阶段 2 字段对齐时

- 加载 `knowledge-path.md` → `wms-core` → WMOS 表结构（`TC_ASN_ID`、`ASN_DTL_ID`、`TC_LPN_ID`、`BATCH_NBR` 等）
- 加载 `compliance-path.md` → `mode=gsp` → 00201/05805 等追溯条款
- 加载 `tech-stack-path.md` → 后端 Java + Oracle + 5 件套审计字段

### 阶段 2 业务流程时

- 应用 GSP 强制流程节点（批次关联、效期校验、质量锁定）
- 应用 Java 分层架构约束（巴枪→Controller→Service→Repository 链路）
- 按 `doc-naming.md` 默认规范生成 `01-业务需求文档 BRD.md`

### 阶段 4 合规评审时

- 读 `compliance-path.md` 中列出的 `gsp-rules` 真实路径
- 按缺陷等级评估
- 输出 `04-合规评审.md`（本示例未生成）

### 阶段 7 开发设计时

- 加载 Java 命名规范、5 件套审计字段、SEQUENCE 主键策略
- 加载 Vue 3 组件规范、Element Plus 用法
- 加载 WMOS 表字段引用（**严禁 Claude 瞎写**）

## 如何替换成你自己的配置

### 场景 1：开新项目

```bash
# 一键初始化（在你的项目根跑）
bash ~/.claude/skills/analysis-to-delivery/scripts/init-project-config.sh /path/to/your-project

# 然后编辑 4 个 *-path.md，填你项目的真实路径
```

### 场景 2：现有项目想用本 skill

把 4 个 `*-path.md` 复制到项目根，按下面的对照表填：

| 你的项目类型 | knowledge-path.md 路径示例 | compliance mode | tech-stack 后端 | tech-stack 前端 |
|-------------|--------------------------|----------------|----------------|----------------|
| **金融支付** | `/公司内网/wiki/pay-rules/` | `sox` | `java-spring` | `frontend-vue` |
| **SaaS 后台** | `/公司内网/wiki/saas/` | `none` | `node-nestjs` | `frontend-react` |
| **移动 App** | `/公司内网/wiki/mobile/` | `none` | `python-django` (后端) | `frontend-react-native` |
| **医疗信息化** | `/公司内网/wiki/medical/` | `hipaa` | `dotnet-core` | `frontend-vue` |

### 场景 3：项目级为空（fallback 到 skill 级）

如果你的项目根**没有** `*-path.md`：

1. Claude 扫不到项目级 → 进入 Level 2（skill 级 fallback）
2. 加载 `config/compliance/gsp.md` / `config/tech-stack/java-spring.md` 等作为参考
3. Claude 会在工作流中标注"来源：skill 内置"——提醒用户尽快补项目级配置

### 场景 4：项目级 + skill 级都没有

Claude **必须主动询问**用户：
- "你的项目用 Java 还是 Go？"
- "你的项目是否需要 GSP 合规评审？"

**严禁 Claude 自行猜测或编造**。

## 与 v1.0 skill 级 config 的关系

| 维度 | v1.1 项目级（推荐） | v1.0 skill 级（fallback） |
|------|---------------------|--------------------------|
| 位置 | 项目根目录 | `~/.claude/skills/.../config/` |
| 优先级 | **最高** | 项目级为空时 |
| 维护者 | 项目方（跟着项目走） | skill 维护者（跟着 skill 走） |
| 适用场景 | 真实项目交付 | 临时试用 / 不知道写什么时参考 |

> 简言之：**项目级是"真"，skill 级是"参考"**。

## v3.1.0 升级说明

本示例从 v3.0.1 升级到 v3.1.0，新增/升级了以下产物：

### 新增产物

| 文件 | 对应 skill | 阶段 | 说明 |
|---|---|---|---|
| [`04-合规评审.md`](./04-合规评审.md) | `/compliance-review` | 4 | GSP 9 条款合规性分析（严重/主要/一般） |
| [`05-产品需求文档 PRD.md`](./05-产品需求文档 PRD.md) | `/to-prd` | 6 | 8 节齐全 + §七 验收标准白名单签字 |
| [`07-测试用例设计.md`](./07-测试用例设计.md) | `/test-case-design` | 5 | 5 大类用例各 ≥1 条 + GSP 合规校验覆盖 |

### 配套验证脚本

```bash
# 阶段 3→4 门控
python3 scripts/brd-check.py --strict examples/01-wms-warehouse/

# 阶段 4→5 门控
python3 scripts/compliance-check.py --strict examples/01-wms-warehouse/

# 阶段 5→6 门控
python3 scripts/testcase-coverage-check.py --strict examples/01-wms-warehouse/

# 阶段 6→7 门控
python3 scripts/prd-check.py --strict examples/01-wms-warehouse/
```

### 与 v3.0.1 的差异

| 维度 | v3.0.1 | v3.1.0 |
|---|---|---|
| 覆盖阶段 | 1-3 | 1-9（含 4-7） |
| 文档数 | 7 | 10（+3） |
| 合规评审 | ❌ 无 | ✅ GSP 9 条款全过 |
| PRD | ❌ 无 | ✅ 8 节齐 + §七 签字 |
| 测试用例 | ❌ 无 | ✅ 5 大类 26 条 |
| 自动化门控 | 2 个（setup + task-confirm） | 6 个（+brd/compliance/testcase/prd） |

### 已知未补全

- 阶段 7-8（`/dev-design` 6 大文档：FSD/数据模型/开发设计/回测/复盘/交接）— 留待后续升级
- 阶段 9（`/qa-audit` 全量 QA 审计）— 留待后续升级

---

**最后更新**：2026-06-22
**维护者**：Jason sun
