# 技术栈路径(SaaS 后台 — 客户订单管理)

> 项目:SaaS 后台 — 客户订单管理
> 路径配置:本文档被 `/setup-analysis-delivery` 阶段 0 引用
> 用途:明确本项目的技术选型、版本、目录结构

## 一、整体架构

```
┌────────────────────────────────────────────────────────────────┐
│  客户端(Web 响应式)                                              │
│  React 19 + TypeScript 5.4 + Vite 6 + Tailwind 4 + shadcn/ui    │
│  状态:TanStack Query(服务端)+ Zustand(客户端)                   │
│  路由:React Router 7(数据路由 + 嵌套布局)                       │
└──────────────────┬─────────────────────────────────────────────┘
                   │ HTTPS / JSON / JWT
                   ▼
┌────────────────────────────────────────────────────────────────┐
│  后端 API(无状态)                                                │
│  Node.js 22 + Express 5 + TypeScript 5.4 + Prisma 5             │
│  分层:Controller → Service → Repository → Prisma ORM            │
│  中间件:helmet / cors / rate-limit / auth / tenantGuard          │
└──────────────────┬─────────────────────────────────────────────┘
                   │ Prisma SQL + 队列入队(BullMQ)
                   ▼
┌────────────────────────────────────────────────────────────────┐
│  数据层                                                          │
│  PostgreSQL 16(主库,主从)+ Redis 7(缓存 + 队列)                  │
└──────────────────┬─────────────────────────────────────────────┘
                   │ Webhook / HTTP
                   ▼
┌────────────────────────────────────────────────────────────────┐
│  第三方服务                                                       │
│  支付:支付宝 / 微信 / Stripe                                       │
│  物流:顺丰 API                                                    │
│  监控:Prometheus / Grafana / Loki                                │
└────────────────────────────────────────────────────────────────┘
```

## 二、技术选型清单

### 2.1 前端(React 19 + Vite 6)

| 类别 | 选型 | 版本 | 理由 |
|---|---|---|---|
| 框架 | React | 19.x | 生态成熟,Server Components 准备就绪 |
| 语言 | TypeScript | 5.4+ | 与后端共享类型 |
| 构建 | Vite | 6.x | 启动快,HMR 流畅,ESM 原生 |
| 路由 | React Router | 7.x | 数据路由 + 嵌套布局 + 类型安全 |
| 服务端状态 | TanStack Query | 5.x | 缓存/重试/失效控制/SSR 友好 |
| 客户端状态 | Zustand | 5.x | 轻量,无样板,易于测试 |
| 表单 | React Hook Form | 7.x | 性能好,易集成 Zod |
| 校验 | Zod | 3.x | 前后端共享 schema,类型推导 |
| UI 组件 | shadcn/ui | latest | 可复制可定制,Radix 底座 |
| 样式 | Tailwind CSS | 4.x | 原子化,与 shadcn 深度集成 |
| 图标 | Lucide React | latest | 与 shadcn 集成 |
| 通知 | Sonner | latest | 轻量,UI 美观 |
| 测试(单元)| Vitest | latest | Vite 原生,API 兼容 Jest |
| 测试(组件)| Testing Library | latest | 行为驱动 |
| E2E | Playwright | latest | 跨浏览器,可录屏 |
| 包管理 | pnpm | 9.x | 节省磁盘,monorepo 友好 |

### 2.2 后端(Node.js 22 + Express 5)

| 类别 | 选型 | 版本 | 理由 |
|---|---|---|---|
| 运行时 | Node.js | 22 LTS | 最新 LTS,原生 TS 支持,fetch 内置 |
| 框架 | Express | 5.x | 生态成熟,异步错误处理改进 |
| 语言 | TypeScript | 5.4+ | 与前端共享类型 |
| ORM | Prisma | 5.10+ | 类型安全,迁移工具完善 |
| 校验 | Zod | 3.x | 与前端共享 |
| 鉴权 | jsonwebtoken | 9.x | JWT 标准 |
| 密码 | bcrypt | 5.x | 安全 |
| 日志 | Pino | 9.x | 高性能(JSON 输出) |
| 队列 | BullMQ | 5.x | 基于 Redis,可靠,可观测 |
| 缓存 | ioredis | 5.x | Redis 客户端 |
| 限流 | express-rate-limit | 7.x | 防滥用 |
| 安全头 | helmet | 7.x | HTTP 安全头 |
| CORS | cors | 2.x | 跨域 |
| 测试 | Jest | 29.x | 成熟(mock / coverage)|
| Mock | MSW | 2.x | 网络层 mock |
| 文档 | OpenAPI 3.1 | - | 标准化 API 文档 |
| 包管理 | pnpm | 9.x | 与前端一致 |

### 2.3 数据层

| 类别 | 选型 | 版本 | 理由 |
|---|---|---|---|
| 主库 | PostgreSQL | 16.x | JSON / UUID / 物化视图 / 分区表 |
| 缓存 | Redis | 7.x | 高性能 KV + 队列后端 |
| ORM 工具 | Prisma Migrate | - | 迁移版本化 |
| 备份 | pg_dump + cron | - | 每日全量 + 增量 WAL |
| 监控 | pg_stat_statements | - | 慢查询分析 |

### 2.4 基础设施

| 类别 | 选型 | 备注 |
|---|---|---|
| 容器化 | Docker | 多阶段构建 |
| 编排 | Kubernetes 1.28+ | HPA 自动扩缩 |
| CI | GitHub Actions | 4 个 workflow |
| 镜像仓库 | GHCR | 私有仓库 |
| 监控 | Prometheus + Grafana | 业务指标 + 基础设施 |
| 日志聚合 | Loki + Promtail | 与 Grafana 集成 |
| 链路追踪 | OpenTelemetry + Jaeger | 跨服务追踪 |
| 错误追踪 | Sentry | 前端 + 后端 |
| 密钥管理 | Vault | 数据库密码 / API Key |

## 三、目录结构

### 3.1 后端

```
backend/
├── prisma/
│   ├── schema.prisma             # 数据模型定义
│   ├── migrations/               # 迁移历史
│   └── seed.ts                   # 种子数据
├── src/
│   ├── controllers/              # L5:HTTP 入口
│   │   ├── order.controller.ts
│   │   ├── payment.controller.ts
│   │   └── ...
│   ├── services/                 # L4:业务逻辑
│   │   ├── order.service.ts
│   │   ├── payment.service.ts
│   │   └── ...
│   ├── repositories/             # L3:数据访问
│   │   ├── order.repository.ts
│   │   └── ...
│   ├── entities/                 # L2:领域模型
│   ├── middlewares/              # 横切关注点
│   │   ├── auth.middleware.ts
│   │   ├── tenantGuard.middleware.ts
│   │   ├── error.middleware.ts
│   │   └── ...
│   ├── jobs/                     # BullMQ 队列消费者
│   │   ├── paymentCallback.job.ts
│   │   ├── shipmentTrack.job.ts
│   │   └── ...
│   ├── lib/                      # 第三方封装
│   │   ├── alipay.ts
│   │   ├── wechat.ts
│   │   ├── stripe.ts
│   │   └── sfExpress.ts
│   ├── config/                   # 配置
│   ├── utils/                    # 通用工具
│   ├── types/                    # 类型定义
│   ├── routes.ts                 # 路由注册
│   └── server.ts                 # 入口
├── tests/
│   ├── unit/                     # 单元测试
│   ├── integration/              # 集成测试(测试库)
│   └── e2e/                      # 端到端测试
├── scripts/
│   ├── migrate.sh
│   └── seed.sh
├── .env.example
├── package.json
├── tsconfig.json
└── Dockerfile
```

### 3.2 前端

```
frontend/
├── src/
│   ├── routes/                   # React Router 7 文件路由
│   │   ├── _layout.tsx
│   │   ├── orders._index.tsx
│   │   ├── orders.$id.tsx
│   │   └── ...
│   ├── pages/                    # 页面(被 routes 引用)
│   ├── components/               # 通用组件
│   │   ├── ui/                   # shadcn/ui 基础组件
│   │   └── ...
│   ├── features/                 # 业务功能模块
│   │   ├── orders/
│   │   │   ├── api.ts            # TanStack Query hooks
│   │   │   ├── components/       # 订单相关组件
│   │   │   ├── hooks/
│   │   │   ├── types.ts
│   │   │   └── validation.ts     # Zod schemas
│   │   ├── payments/
│   │   ├── customers/
│   │   └── ...
│   ├── hooks/                    # 自定义 Hook
│   ├── lib/                      # API 客户端 / 工具
│   │   ├── api.ts                # fetch 封装
│   │   ├── auth.ts
│   │   └── ...
│   ├── stores/                   # Zustand stores
│   ├── types/                    # 全局类型
│   ├── styles/                   # 全局样式
│   ├── App.tsx
│   └── main.tsx
├── tests/
│   ├── unit/
│   └── e2e/
├── public/
├── package.json
├── tailwind.config.ts
├── tsconfig.json
├── vite.config.ts
└── Dockerfile
```

### 3.3 仓库根

```
.
├── .github/
│   └── workflows/                # CI 配置
├── backend/                      # 后端
├── frontend/                     # 前端
├── docker-compose.yml            # 本地开发
├── docker-compose.prod.yml       # 生产
├── Makefile                      # 常用命令
├── pnpm-workspace.yaml           # pnpm 工作区
└── README.md
```

## 四、版本兼容矩阵

| 组件 | 版本要求 | 兼容性 |
|---|---|---|
| Node.js | ≥ 22.0 | LTS |
| TypeScript | 5.4+ | ES2022 target |
| Prisma | 5.10+ | Node 22 兼容 |
| React | 19.0+ | 需 React Compiler 启用 |
| Vite | 6.0+ | Node 22 兼容 |
| PostgreSQL | 16+ | gen_random_uuid() / 物化视图 |
| Redis | 7.0+ | BullMQ 5 兼容 |
| pnpm | 9.0+ | workspace 协议 |

## 五、关键依赖锁定

| 包 | 锁定版本 | 原因 |
|---|---|---|
| Prisma | 5.10.x | 修复 Node 22 原生 fetch 集成 bug |
| Express | 5.0.x | 与 4.x API 差异较大,锁定首版 |
| React | 19.0.x | 禁用旧版 StrictMode 双调用模式 |
| Tailwind | 4.0.x | PostCSS 插件机制变化 |
| Zod | 3.23.x | 与 Prisma 类型推导的兼容版本 |

## 六、环境要求

### 6.1 开发环境

- Node.js 22 LTS
- pnpm 9.x
- PostgreSQL 16(本地或 Docker)
- Redis 7(本地或 Docker)
- 8GB 内存,20GB 磁盘

### 6.2 生产环境

- Kubernetes 1.28+
- PostgreSQL 16(主从,32GB 起)
- Redis Cluster(16GB 起)
- 4 核 8GB 起,推荐 8 核 16GB
- 100GB+ SSD

## 七、ADR(架构决策记录)

### ADR-001:选 PostgreSQL 16 而非 MySQL 8

**决策**:PostgreSQL 16

**原因**:
- ✅ JSON 字段原生支持(订单扩展属性)
- ✅ UUID 原生支持(`gen_random_uuid()` 免扩展)
- ✅ 物化视图(数据看板 T+1 友好)
- ✅ 数组类型(简化多对多)
- ✅ 高级索引(部分索引 / 表达式索引)
- ❌ MySQL:JSON 支持弱,无物化视图,分区表限制多

**影响**:所有 SQL 用 PG 方言(COALESCE / LIMIT / BIGSERIAL)

### ADR-002:选 Prisma ORM 而非 TypeORM / Drizzle

**决策**:Prisma 5

**原因**:
- ✅ TypeScript 类型安全最佳
- ✅ 迁移工具完善(`prisma migrate`)
- ✅ 与 PostgreSQL 集成优秀
- ✅ Studio 可视化
- ❌ TypeORM:复杂关系时心智负担重,迁移工具弱
- ❌ Drizzle:生态较新,生产案例少

**影响**:数据模型用 `schema.prisma` DSL,迁移用 `prisma migrate`

### ADR-003:多租户行级隔离(`tenant_id`)

**决策**:行级 `tenant_id` 隔离

**原因**:
- ✅ 运维成本低(单库)
- ✅ 跨租户统计方便(数据看板)
- ✅ 资源利用率高
- ❌ 风险:代码漏带 `tenant_id` 致命
- 缓解:中间件 + lint 规则 + 代码审查重点

**影响**:每张表必有 `tenant_id`,所有查询强制带条件

### ADR-004:状态用字符串枚举

**决策**:`'draft'` / `'submitted'` / `'paid'` 等

**原因**:
- ✅ 可读性强
- ✅ 国际化友好
- ✅ TypeScript enum 类型安全
- ❌ 2 位数字码:可读性差,不友好

**影响**:`orders.status` 类型 `VARCHAR(20)`,TypeScript 同步定义

### ADR-005:T+1 数据看板

**决策**:离线数仓 + 定时任务

**原因**:
- ✅ 简单(夜间批处理)
- ✅ 性能压力小
- ✅ 历史数据可回溯
- ❌ 实时性差(隔天才能看)
- 缓解:v2 可加实时数仓(Kafka + Flink)

**影响**:`reports` 物化视图,每日 02:00 刷新

### ADR-006:走第三方支付(卡号不落库)

**决策**:所有卡号数据走支付宝 / 微信 / Stripe

**原因**:
- ✅ 避免 PCI-DSS 合规
- ✅ 集成工作由支付服务商承担
- ✅ 风控由支付服务商承担
- ❌ 需付手续费(0.6% - 2%)

**影响**:`payments` 表只存 `transaction_id`,不存卡号

## 八、与 WMS 示例(01-wms-warehouse)的技术栈对比

| 维度 | WMS(01)| SaaS(02)| 差异 |
|---|---|---|---|
| 数据库 | Oracle 19c | PostgreSQL 16 | **方言差异大** |
| 后端框架 | Spring Boot 3.x | Express 5 | **范式差异** |
| ORM | MyBatis-Plus | Prisma | **写 SQL 风格** |
| 前端框架 | Vue 3 + Element Plus | React 19 + shadcn/ui | **响应式风格** |
| 移动端 | uni-app 巴枪 | 无(响应式 Web) | **范围差异** |
| 鉴权 | Spring Security + JWT | jsonwebtoken | **实现差异** |
| 状态码 | 2 位数字 | 字符串枚举 | **可读性差异** |
| 队列 | Spring Cloud Stream / RocketMQ | BullMQ + Redis | **技术栈差异** |
| 多租户 | 单租户 | 多租户(行级)| **架构差异** |
| 审计字段 | 五件套 | 五件套 | 一致 |
| 文档编号 | 01-08 | 01-08 | 一致 |
