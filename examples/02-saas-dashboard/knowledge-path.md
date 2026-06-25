# 知识库路径(SaaS 后台 — 客户订单管理)

> 项目:SaaS 后台 — 客户订单管理
> 路径配置:本文档被 `/setup-analysis-delivery` 阶段 1 引用
> 用途:指向该项目所依赖的官方文档 / 内部知识库 / 第三方资料

## 一、PostgreSQL 16 知识库

### 1.1 官方文档(权威来源)

| 类别 | URL |
|---|---|
| 主索引 | https://www.postgresql.org/docs/16/ |
| SQL 语法 | https://www.postgresql.org/docs/16/sql.html |
| 数据类型 | https://www.postgresql.org/docs/16/datatype.html |
| 函数和操作符 | https://www.postgresql.org/docs/16/functions.html |
| 索引 | https://www.postgresql.org/docs/16/indexes.html |
| 事务隔离 | https://www.postgresql.org/docs/16/transaction-iso.html |
| 性能调优 | https://www.postgresql.org/docs/16/performance-tips.html |
| 物化视图 | https://www.postgresql.org/docs/16/rules-materializedviews.html |
| 分区表 | https://www.postgresql.org/docs/16/ddl-partitioning.html |
| JSON 类型 | https://www.postgresql.org/docs/16/datatype-json.html |

### 1.2 关键语法点(对比 Oracle)

| 概念 | Oracle | PostgreSQL | 备注 |
|---|---|---|---|
| 空值替换 | `NVL(a, b)` | `COALESCE(a, b)` | PG 标准 SQL |
| 当前时间 | `SYSDATE` | `NOW()` / `CURRENT_TIMESTAMP` | 返回 TIMESTAMPTZ |
| 行数限制 | `ROWNUM <= N` | `LIMIT N OFFSET M` | 标准 SQL |
| 序列 | `SEQ.NEXTVAL` | `NEXTVAL('seq_name')` | 函数式调用 |
| 字符串连接 | `a \|\| b` | `a \|\| b` | 一致 |
| 主键自增 | SEQUENCE + Trigger | `SERIAL` / `BIGSERIAL` / `GENERATED AS IDENTITY` | 推荐 UUID v4 |
| 数据类型 | `NUMBER(12,2)` | `NUMERIC(12,2)` | 同义 |
| 日期类型 | `DATE` / `TIMESTAMP` | `TIMESTAMPTZ`(推荐)| 时区感知 |
| 布尔 | `NUMBER(1)` 0/1 | `BOOLEAN` | 原生支持 |
| UUID 生成 | `SYS_GUID()` | `gen_random_uuid()` | 需 PG 13+ |
| 注释 | `COMMENT ON COLUMN` | `COMMENT ON COLUMN` | 一致 |
| 索引 | `CREATE INDEX` | `CREATE INDEX` | 一致 |
| 部分索引 | 不支持 | `CREATE INDEX ... WHERE` | PG 优势 |

### 1.3 推荐扩展

| 扩展 | 用途 | 启用方式 |
|---|---|---|
| `pgcrypto` | `gen_random_uuid()` / 加密函数 | `CREATE EXTENSION pgcrypto;` |
| `uuid-ossp` | UUID 生成(老版本)| `CREATE EXTENSION "uuid-ossp";` |
| `pg_trgm` | 模糊搜索 | `CREATE EXTENSION pg_trgm;` |
| `postgis` | 地理空间(物流)| 视情况 |

## 二、Node.js 22 + Express 5 知识库

### 2.1 官方文档

| 类别 | URL |
|---|---|
| Node.js 22 | https://nodejs.org/docs/latest-v22.x/api/ |
| Express 5 | https://expressjs.com/en/5x/api.html |
| Express 5 迁移指南 | https://expressjs.com/en/guide/migrating-5.html |
| TypeScript | https://www.typescriptlang.org/docs/ |

### 2.2 项目关键库

| 库 | 版本 | 用途 | 文档 |
|---|---|---|---|
| Prisma | 5.10+ | ORM | https://www.prisma.io/docs/ |
| Zod | 3.x | 数据校验 | https://zod.dev/ |
| Pino | 9.x | 日志 | https://getpino.io/ |
| jsonwebtoken | 9.x | JWT | https://github.com/auth0/node-jsonwebtoken |
| bcrypt | 5.x | 密码加密 | https://github.com/kelektiv/node.bcrypt.js |
| ioredis | 5.x | Redis 客户端 | https://github.com/redis/ioredis |
| BullMQ | 5.x | 队列 | https://docs.bullmq.io/ |
| helmet | 7.x | HTTP 安全头 | https://helmetjs.github.io/ |
| cors | 2.x | CORS | https://github.com/expressjs/cors |
| express-rate-limit | 7.x | 限流 | https://github.com/express-rate-limit/express-rate-limit |

### 2.3 Express 5 关键变化(对比 Express 4)

| 变化 | 说明 |
|---|---|
| 异步错误处理 | 路由 async 函数抛错自动到 error 中间件 |
| `req.query` | 始终是对象(不再为 `{}` when undefined) |
| 路径匹配 | 移除 `*` 通配符,改用 `*splat` |
| 性能 | 路由匹配 ~30% 提升 |

## 三、React 19 知识库

### 3.1 官方文档

| 类别 | URL |
|---|---|
| React 19 | https://react.dev/ |
| Vite 6 | https://vite.dev/guide/ |
| React Router 7 | https://reactrouter.com/ |
| TypeScript 5.4+ | https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-4.html |

### 3.2 项目关键库

| 库 | 版本 | 用途 | 文档 |
|---|---|---|---|
| TanStack Query | 5.x | 服务端状态 | https://tanstack.com/query/latest |
| Zustand | 5.x | 客户端状态 | https://zustand-demo.pmnd.rs/ |
| React Hook Form | 7.x | 表单 | https://react-hook-form.com/ |
| shadcn/ui | latest | UI 组件 | https://ui.shadcn.com/ |
| Tailwind CSS | 4.x | 样式 | https://tailwindcss.com/ |
| Zod | 3.x | 类型校验 | https://zod.dev/ |
| dayjs | 1.x | 日期 | https://day.js.org/ |
| react-i18next | 14.x | 国际化(预留) | https://react.i18next.com/ |

## 四、内部知识库(项目级)

### 4.1 项目设计文档

| 文档 | 用途 |
|---|---|
| `01-业务需求文档 BRD.md` | 业务需求 |
| `REVIEW_需求确认书.md` | AI 理解确认 |
| `REVIEW_字段对齐分析.md` | 字段映射 |
| `业务流程图-订单创建.txt` | 主流程 |
| `业务流程图-订单状态流转.txt` | 状态机 |

### 4.2 知识库目录约定

```
/root/analysis-to-delivery/
├── examples/
│   ├── 01-wms-warehouse/         # 医药 WMS(Oracle + Spring Boot + Vue)
│   └── 02-saas-dashboard/        # SaaS 订单管理(本项目,PG + Node + React)
│       ├── knowledge-path.md     # 本文件
│       ├── tech-stack-path.md
│       └── ...
├── skills/                        # skill 集合(26 个)
│   ├── ask-delivery/
│   ├── to-brd/
│   └── ...
└── references/                    # [已迁移到 skills/]
```

## 五、第三方服务 API 文档

| 服务 | 用途 | 文档 |
|---|---|---|
| 支付宝 | 支付(国内)| https://opendocs.alipay.com/ |
| 支付宝沙箱 | 联调测试 | https://open.alipay.com/develop/sandbox/account |
| 微信支付 | 支付(国内)| https://pay.weixin.qq.com/wiki/doc/api/ |
| 微信支付 V3 | 最新 API | https://pay.weixin.qq.com/wiki/doc/apiv3/ |
| Stripe | 支付(国际)| https://stripe.com/docs/api |
| Stripe Testing | 测试卡 | https://stripe.com/docs/testing |
| 顺丰 | 物流 | https://open.sf-express.com/ |
| 快递鸟 | 物流聚合(备选)| https://www.kdniao.com/api-document |

## 六、性能 / 监控

| 工具 | 用途 | 文档 |
|---|---|---|
| Prometheus | 指标采集 | https://prometheus.io/docs/ |
| Grafana | 可视化 | https://grafana.com/docs/ |
| Loki | 日志聚合 | https://grafana.com/docs/loki/ |
| OpenTelemetry | 链路追踪 | https://opentelemetry.io/docs/ |
| Sentry | 前端错误 | https://docs.sentry.io/ |
| pgBadger | PG 慢查询 | https://pgbadger.darold.net/ |

## 七、关键注意事项(由 `/grill-task` 阶段 2 沉淀)

1. **PostgreSQL 13+** 才支持 `gen_random_uuid()`(免扩展)
2. **TIMESTAMPTZ 必带时区** — 不要混用 `TIMESTAMP`(无时区)
3. **NUMERIC 防浮点** — 金额计算必须用 `NUMERIC(12,2)`,禁止 `FLOAT`/`DOUBLE`
4. **多租户 `tenant_id` 必带索引** — 复合索引 `(tenant_id, created_at)` 性能最佳
5. **乐观锁 `version` 字段** — Prisma 用 `@version` 或手动 `WHERE version = ?`
6. **审计字段五件套** — 与 WMS 一致:`created_at` / `created_by` / `updated_at` / `updated_by` / `version`
7. **Express 5 异步** — 路由 async 函数抛错自动到 error 中间件,无需 `try/catch`
8. **React 19** — 旧版 StrictMode 双调用模式已禁用,可放心用 useEffect

## 八、ADR(架构决策记录)索引

| ADR | 决策 | 引用 |
|---|---|---|
| ADR-001 | 选 PostgreSQL 16 | `tech-stack-path.md` §2.3 |
| ADR-002 | 选 Prisma ORM | `tech-stack-path.md` §2.2 |
| ADR-003 | 多租户行级隔离 | `tech-stack-path.md` §七 |
| ADR-004 | 状态用字符串枚举 | `REVIEW_字段对齐分析.md` §四 |
| ADR-005 | T+1 数据看板 | `01-业务需求文档 BRD.md` §1.2 |
| ADR-006 | 走第三方支付 | `compliance-path.md` §三 |
