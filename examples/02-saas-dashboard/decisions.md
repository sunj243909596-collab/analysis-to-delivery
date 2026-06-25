# Decisions（ADR / 决策记录）— SaaS 后台 客户订单管理(v3.1.0)

> 项目:SaaS 后台 — 客户订单管理
> 版本:v3.1.0(2026-07,阶段 4-7 文档补齐;v3.1.0 起从 `config-used.md` 改名为 decisions.md)
> 文件身份:ADR / 决策记录,由 `/setup-analysis-delivery` 阶段 1 可选生成
> 注意:本文件不参与配置加载,配置加载只读取 4 个 `*-path.md`
> 用途:汇总本项目引用的全部配置路径 + 关键技术决策,便于审计与回溯

## 一、配置清单

| 配置项 | 路径 | 用途 |
|---|---|---|
| 合规 | `config/compliance/none.md` | 无强合规 |
| 知识库 | `knowledge-path.md`(本目录)| PostgreSQL + Node + React |
| 技术栈 | `tech-stack-path.md`(本目录)| Node 22 + Express 5 + React 19 + PG 16 |
| 合规 | `compliance-path.md`(本目录)| 软合规清单 |
| 文档命名 | `doc-naming.md`(本目录)| 01-09 编号 |
| 配置使用记录 / ADR | `decisions.md`(本文件)| 不参与配置加载 |

## 二、与全局默认的差异

| 配置项 | 全局默认 | 本项目 | 差异 |
|---|---|---|---|
| 合规等级 | none | none | **一致** |
| 数据库方言 | Oracle | PostgreSQL | **差异**:`NVL→COALESCE`,`ROWNUM→LIMIT`,`SYSDATE→NOW()` |
| 状态码 | 2 位数字 | 字符串枚举 | **差异**:`draft`/`submitted`/`paid` |
| 前端框架 | Vue 3 + Element Plus | React 19 + shadcn/ui | **差异** |
| 后端框架 | Spring Boot + MyBatis-Plus | Express 5 + Prisma | **差异** |
| 主键策略 | SEQUENCE | `BIGSERIAL` / UUID | **差异** |
| 多租户 | 单租户 | 多租户(行级 `tenant_id`)| **差异** |
| 字符分隔 | `\|\|` | `\|\|` | **一致** |
| 整数除法 | `1.0/3` | `1.0/3` | **一致** |
| 审计字段 | 五件套 | 五件套(`created_at`/`created_by`/`updated_at`/`updated_by`/`version`)| **一致** |
| 文档编号 | 01-09 | 01-09(省略 02/04/08/09)| **一致**(本项目按 SaaS 场景裁剪) |

## 三、关键决策记录

### 3.1 为什么选 PostgreSQL?

**背景**:B2B SaaS 需要 JSON 字段存订单扩展属性,UUID 做主键,物化视图加速数据看板。

**选项**:
- ✅ **PostgreSQL 16**(本项目选)
- ❌ MySQL 8:JSON 支持弱,无物化视图
- ❌ Oracle:授权费高,部署复杂
- ❌ SQL Server:Windows 授权,生态受限

**理由**:
- ✅ JSON 字段原生支持 + JSONB 索引
- ✅ UUID 原生支持(`gen_random_uuid()` 免扩展)
- ✅ 物化视图(数据看板 T+1 友好)
- ✅ 开源,无授权费
- ✅ 团队熟悉度高

### 3.2 为什么选 Prisma?

**选项**:
- ✅ **Prisma 5.10+**(本项目选)
- ❌ TypeORM:复杂关系时心智负担重,迁移工具弱
- ❌ Drizzle:生态较新,生产案例少
- ❌ 裸 SQL:失去类型安全

**理由**:
- ✅ TypeScript 类型安全最佳
- ✅ 迁移工具完善(`prisma migrate`)
- ✅ 与 PostgreSQL 集成好
- ✅ Studio 可视化调试
- ✅ 社区活跃

### 3.3 为什么行级多租户?

**选项**:
- ✅ **行级 `tenant_id` 隔离**(本项目选)
- ❌ Schema 级:运维成本高,跨租户统计复杂
- ❌ DB 级:资源利用率低,运维爆炸

**理由**:
- ✅ 运维成本低(单库)
- ✅ 跨租户统计方便(数据看板)
- ✅ 资源利用率高
- ❌ 风险:代码漏带 `tenant_id` 致命

**缓解措施**:
- 应用层中间件强制检查
- Prisma 中间件自动注入 `tenant_id`
- lint 规则禁止裸 `findMany`
- 代码审查重点项
- 跨租户访问告警
- 定期跨租户泄露扫描脚本

### 3.4 为什么 T+1 数据看板?

**选项**:
- ✅ **T+1 离线数仓 + 定时任务**(本项目选)
- ❌ 实时数仓(Kafka + Flink):复杂度高
- ❌ 直接 OLTP 查询:性能差

**理由**:
- ✅ 简单(夜间批处理)
- ✅ 性能压力小
- ✅ 历史数据可回溯
- ✅ 物化视图自动刷新

**风险与缓解**:
- ❌ 实时性差(隔天才能看)
- 缓解:v2 可加实时数仓(Kafka + Flink)
- 当前业务可接受(销售次日开早会看报表)

### 3.5 为什么走第三方支付?

**选项**:
- ✅ **支付宝 / 微信 / Stripe**(本项目选)
- ❌ 自建支付通道:需 PCI-DSS 合规

**理由**:
- ✅ 避免 PCI-DSS 合规
- ✅ 集成工作由支付服务商承担
- ✅ 风控由支付服务商承担
- ✅ 覆盖国内 + 国际市场

**影响**:`payments` 表只存 `transaction_id`,不存卡号

### 3.6 为什么字符串枚举状态?

**选项**:
- ✅ **字符串枚举**(本项目选):`draft`/`submitted`/`paid`
- ❌ 2 位数字码(10/20/30):与 WMS 一致

**理由**:
- ✅ 可读性强
- ✅ 国际化友好
- ✅ TypeScript enum 类型安全
- ❌ 数字码:不友好,需查表

**影响**:`orders.status` 类型 `VARCHAR(20)`,Prisma `enum` 定义

## 四、配置继承关系

```
全局默认(config/)
├── compliance/
│   ├── gsp.md
│   └── none.md ←【本项目使用】
├── db-dialect/
│   ├── oracle.md
│   └── postgresql.md ←【本项目使用】
└── ...

项目级(本目录)
├── compliance-path.md ← 引用 none.md
├── knowledge-path.md ← 引用 PG 16 + Node + React 文档
├── tech-stack-path.md ← 引用 PG 16 + Node + React
├── doc-naming.md ← 引用全局 01-09 规则
└── decisions.md ←【ADR 记录,不参与配置加载】
```

## 五、回溯与审计

| 场景 | 查阅路径 |
|---|---|
| 为什么用 PostgreSQL? | `tech-stack-path.md` §2.3 + `decisions.md` §3.1 |
| 为什么多租户行级? | `tech-stack-path.md` §七 ADR-003 + `decisions.md` §3.3 |
| 合规要求? | `compliance-path.md` §一-五 |
| 状态机定义? | `01-业务需求文档 BRD.md` §3.2 + `业务流程图-订单状态流转.txt` |
| 字段映射? | `REVIEW_字段对齐分析.md` |
| 文档编号规则? | `doc-naming.md` §一 |
| 状态码为什么字符串? | `decisions.md` §3.6 + `tech-stack-path.md` ADR-004 |
| 支付通道? | `tech-stack-path.md` §2.2 + `decisions.md` §3.5 |

## 六、与 WMS 示例的配置差异(对比)

| 维度 | WMS(01-wms-warehouse)| SaaS(02-saas-dashboard)| 备注 |
|---|---|---|---|
| 合规 | GSP(医药)| None | 本项目无 GSP |
| 数据库 | Oracle 19c | PostgreSQL 16 | 方言差异 |
| 后端 | Spring Boot 3 | Express 5 | 范式差异 |
| 前端 PC | Vue 3 + Element Plus | React 19 + shadcn/ui | 框架差异 |
| 移动端 | uni-app 巴枪 | 无(响应式 Web)| 范围差异 |
| 状态码 | 2 位数字 | 字符串枚举 | 可读性差异 |
| 多租户 | 单租户 | 多租户 | 架构差异 |
| 审计字段 | 五件套 | 五件套 | 一致 |
| 文档编号 | 01-09(全 9 份)| 01-09(省 02/04/08/09)| 裁剪差异 |
| 字符分隔 | `\|\|` | `\|\|` | 一致 |
| 整数除法 | `1.0/3` | `1.0/3` | 一致 |
| 序列 | `SEQ.NEXTVAL` | `NEXTVAL('seq')` / UUID | 差异 |

## 七、配置变更流程

1. **小变更**(版本号、依赖升级)
   - 直接修改 `*.path.md` 文件
   - 在 `## 变更记录` 中追加
   - 提交 Git,无需审批

2. **中变更**(技术选型调整)
   - 评估影响范围
   - 更新 `*-path.md`,并在 `decisions.md` 追加 ADR
   - 提交 Git,需团队 review

3. **大变更**(合规、数据库切换)
   - 走 `/grill-task` 重新审视
   - 更新所有相关 `*.path.md` + BRD
   - 走 `/dev-design` 重新设计
   - 必须团队 review + 业务方确认

## 八、变更记录

| 日期 | 变更 | 原因 |
|---|---|---|
| 2026-06-22 | 初版配置 | 项目立项,确定 SaaS 技术栈 |
| 2026-07-02 | v3.1.0 升级:新增 04/05/07 三文档 + GDPR/PIPL 合规清单 | 跟随 skill v3.1.0 阶段 4-7 补齐;实际业务涉及欧盟客户,需补 GDPR |

## v3.1.0 升级说明

本示例从 v3.0.1 升级到 v3.1.0,新增/升级了以下产物：

### 新增产物

| 文件 | 对应 skill | 阶段 | 说明 |
|---|---|---|---|
| [`04-合规评审.md`](./04-合规评审.md) | `/compliance-review` | 4 | GDPR/PIPL 10 条款合规性分析（严重 3 + 主要 5 + 一般 2）|
| [`05-产品需求文档 PRD.md`](./05-产品需求文档 PRD.md) | `/to-prd` | 6 | 8 节齐全 + §七 验收标准白名单签字 |
| [`07-测试用例设计.md`](./07-测试用例设计.md) | `/test-case-design` | 5 | 5 大类用例 31 条 + GDPR/PIPL 合规校验 + 多租户隔离 |

### 配套验证脚本

```bash
# 阶段 3→4 门控
python3 scripts/brd-check.py --strict examples/02-saas-dashboard/

# 阶段 4→5 门控
python3 scripts/compliance-check.py --strict examples/02-saas-dashboard/

# 阶段 5→6 门控
python3 scripts/testcase-coverage-check.py --strict examples/02-saas-dashboard/

# 阶段 6→7 门控
python3 scripts/prd-check.py --strict examples/02-saas-dashboard/
```

### 与 v3.0.1 的差异

| 维度 | v3.0.1 | v3.1.0 |
|---|---|---|
| 覆盖阶段 | 1-3 | 1-9（含 4-7） |
| 文档数 | 7 | 10（+3） |
| 合规评审 | ❌ 无 | ✅ GDPR/PIPL 10 条款全过 |
| PRD | ❌ 无 | ✅ 8 节齐 + §七 签字 |
| 测试用例 | ❌ 无 | ✅ 5 大类 31 条 |
| 自动化门控 | 2 个（setup + task-confirm） | 6 个（+brd/compliance/testcase/prd） |

### 已知未补全

- 阶段 7-8（`/dev-design` 6 大文档：FSD/数据模型/开发设计/回测/复盘/交接）— 留待后续升级
- 阶段 9（`/qa-audit` 全量 QA 审计）— 留待后续升级
