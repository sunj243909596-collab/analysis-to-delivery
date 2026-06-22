# 本示例使用的 config 清单

> 这个示例在执行 analysis-to-delivery 工作流时，加载了以下 config 文件。

## 合规配置

| 文件 | 用途 | 加载阶段 |
|---|---|---|
| `config/compliance/gsp.md` | 医药 GSP 合规规则 | 阶段 3（合规评审） |

**为什么选这个**：
- 业务场景是医药物流收货，GSP 是国家强制要求
- 涉及药品追溯、效期锁定、质量状态控制等必须满足的条款

## 技术栈配置

| 文件 | 用途 | 加载阶段 |
|---|---|---|
| `config/tech-stack/java-spring.md` | Java + Spring Boot + MyBatis-Plus + Oracle 规范 | 阶段 1（确认技术栈）至 阶段 8（开发设计） |
| `config/tech-stack/frontend-vue.md` | Vue 3 + Element Plus + Vite + TS 规范 | 阶段 4（系统方案）至 阶段 8（V2 前端） |

**为什么选这个**：
- 后端是 WMS 既有架构（Java + Spring + Oracle）
- 前端 PC 端用 Vue 3 + Element Plus（团队统一栈）

## 领域知识库配置

| 文件 | 用途 | 加载阶段 |
|---|---|---|
| `config/domain-knowledge/wms.md` | WMOS 表结构、字段映射、状态码、PIX 事务代码 | 阶段 1.3（字段对齐）至 阶段 8（开发设计） |

**为什么需要这个**：
- 涉及 WMOS 原生表（ASN/ASN_DETAIL/LPN/INVENTORY）的字段使用
- 必须严格对齐 WMOS 表结构定义，严禁自行发明字段

## 文档命名配置

| 文件 | 用途 | 加载阶段 |
|---|---|---|
| （使用默认） | 沿用 skill 的 `0X-` 编号规范 | - |

**为什么没自定义**：
- 团队沿用 skill 默认的 01-07 编号
- 无需额外的命名前缀

## config 加载效果

加载上述 config 后，Claude 在每个阶段会自动应用相应规则。例如：

**阶段 1.3 字段对齐时**：
- 加载 `wms.md` 中的 WMOS 表结构
- 加载 `gsp.md` 中的 00201 追溯要求
- 加载 `java-spring.md` 中的命名规范

**阶段 2 业务流程时**：
- 应用 GSP 强制流程节点（批次关联、效期校验、质量锁定）
- 应用 Java 分层架构约束（在 BRD 中标注"巴枪→Controller→Service→Repository"链路）

**阶段 3 合规评审时**：
- 加载 GSP 7 项核心条款
- 按缺陷等级评估
- 输出 `04-合规评审.md`

**阶段 8 开发设计时**：
- 加载 Java 命名规范、审计字段五件套、SEQUENCE 主键策略
- 加载 Vue 组件规范、Element Plus 用法
- 加载 WMOS 表字段引用（不能瞎写）

## 如何替换成你自己的 config

如果你的项目不是 WMS，可以这样选：

| 你的场景 | 替换为 |
|---|---|
| 金融支付 | `config/compliance/sox.md` + `config/tech-stack/java-spring.md` |
| SaaS 后台 | `config/compliance/none.md` + `config/tech-stack/node-nestjs.md` |
| 移动 App | `config/compliance/none.md` + `config/tech-stack/frontend-vue.md` |

如果你的 config 不在示例中，复制 `config/compliance/template.md` 改即可。
