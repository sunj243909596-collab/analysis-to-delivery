# 本示例使用的 config 清单（v1.1：项目级配置演示）

> v1.1 起，**每个项目根目录**放自己的 4 个 `*-path.md` 文件，Claude 优先读项目级的。
> 本目录（`examples/01-wms-warehouse/`）模拟一个完整迷你项目的根，演示项目级配置长什么样。

## 项目级 config 文件（v1.1 推荐方式）

本示例的"项目根"下放了 4 个 `*-path.md`，都是真实的项目级配置：

| 文件 | 加载阶段 | 关联模板 |
|------|---------|---------|
| [`knowledge-path.md`](./knowledge-path.md) | 1.3 / 8 | [templates/project-config/knowledge-path.md](../../templates/project-config/knowledge-path.md) |
| [`compliance-path.md`](./compliance-path.md) | 3 | [templates/project-config/compliance-path.md](../../templates/project-config/compliance-path.md) |
| [`tech-stack-path.md`](./tech-stack-path.md) | 1 / 4 / 8 | [templates/project-config/tech-stack-path.md](../../templates/project-config/tech-stack-path.md) |
| [`doc-naming.md`](./doc-naming.md) | 2-10 全部 | [templates/project-config/doc-naming.md](../../templates/project-config/doc-naming.md) |

## 加载效果

Claude 进入 `examples/01-wms-warehouse/` 时：

1. **先扫项目根** → 发现 4 个 `*-path.md` → 按 Level 1 加载
2. **不再 fallback 到 skill 级**（项目级已填）
3. 按 4 个文件中的真实路径，去读 `/root/WMOS 知识库/` 等

### 阶段 1.3 字段对齐时

- 加载 `knowledge-path.md` → `wms-core` → WMOS 表结构（`TC_ASN_ID`、`ASN_DTL_ID`、`TC_LPN_ID`、`BATCH_NBR` 等）
- 加载 `compliance-path.md` → `mode=gsp` → 00201/05805 等追溯条款
- 加载 `tech-stack-path.md` → 后端 Java + Oracle + 5 件套审计字段

### 阶段 2 业务流程时

- 应用 GSP 强制流程节点（批次关联、效期校验、质量锁定）
- 应用 Java 分层架构约束（巴枪→Controller→Service→Repository 链路）
- 按 `doc-naming.md` 默认规范生成 `01-业务需求文档 BRD.md`

### 阶段 3 合规评审时

- 读 `compliance-path.md` 中列出的 `gsp-rules` 真实路径
- 按缺陷等级评估
- 输出 `04-合规评审.md`（本示例未生成）

### 阶段 8 开发设计时

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

---

**最后更新**：2026-06-22
**维护者**：Jason sun
