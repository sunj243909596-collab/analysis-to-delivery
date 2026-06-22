# 配置使用说明(SaaS 后台 — 客户订单管理)

> 项目:SaaS 后台 — 客户订单管理
> 路径配置:本文档被 `/setup-analysis-delivery` 阶段 0 引用
> 用途:汇总本项目引用的全部配置路径,便于审计与回溯

## 一、配置清单

| 配置项 | 路径 | 用途 |
|---|---|---|
| 合规 | `config/compliance/none.md` | 无强合规 |
| 知识库 | `knowledge-path.md`(本目录)| PostgreSQL + Node + React |
| 技术栈 | `tech-stack-path.md`(本目录)| Node 22 + Express 5 + React 19 + PG 16 |
| 合规 | `compliance-path.md`(本目录)| 软合规清单 |
| 文档命名 | `doc-naming.md`(本目录)| 01-08 编号 |
| 配置汇总 | `config-used.md`(本文件)| 本文件 |

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
| 文档编号 | 01-08 | 01-08(省略 02/04)| **一致**(本项目按 SaaS 场景裁剪) |

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
├── doc-naming.md ← 引用全局 01-08 规则
└── config-used.md ←【本文件】
```

## 五、回溯与审计

| 场景 | 查阅路径 |
|---|---|
| 为什么用 PostgreSQL? | `tech-stack-path.md` §2.3 + `config-used.md` §3.1 |
| 为什么多租户行级? | `tech-stack-path.md` §七 ADR-003 + `config-used.md` §3.3 |
| 合规要求? | `compliance-path.md` §一-五 |
| 状态机定义? | `01-业务需求文档 BRD.md` §3.2 + `业务流程图-订单状态流转.txt` |
| 字段映射? | `REVIEW_字段对齐分析.md` |
| 文档编号规则? | `doc-naming.md` §一 |
| 状态码为什么字符串? | `config-used.md` §3.6 + `tech-stack-path.md` ADR-004 |
| 支付通道? | `tech-stack-path.md` §2.2 + `config-used.md` §3.5 |

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
| 文档编号 | 01-08(全 8 份)| 01-08(省 02/04)| 裁剪差异 |
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
   - 更新 `*.path.md` + `config-used.md` 的 ADR
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
