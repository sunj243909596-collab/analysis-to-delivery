# Example 2: SaaS 后台 — 客户订单管理

> 蒸馏示例:SaaS 后台(Node + React + PostgreSQL)的"客户订单管理"模块。
> 演示 analysis-to-delivery skill 在 SaaS / Web 全栈场景的用法。

## 场景

- **类型**:B2B SaaS 后台
- **技术栈**:Node.js 22 (Express 5) + React 19 (TypeScript + Vite) + PostgreSQL 16
- **模块**:客户订单管理(创建/支付/发货/退款/数据看板)
- **合规**:`config/compliance/none.md`(无强合规,纯商业场景)
- **特殊点**:多租户(每个客户的订单数据隔离)

## 演示的 skill 链

```
/setup-analysis-delivery → /grill-task → /to-brd → /test-case-design
                      → /to-prd → /dev-design → /qa-audit → /handoff
                                  ↓ (用户决定)
                                  /using-superpowers → /brainstorming → /writing-plans
                                                    → /tdd → /executing-plans
```

## 文件结构(本目录)

| 文件 | 对应 skill | 阶段 |
|---|---|---|
| `TASK_CONFIRM_订单管理.md` | `/grill-task` §1 | 1 |
| `REVIEW_需求确认书.md` | `/grill-task` §2 | 1 |
| `REVIEW_字段对齐分析.md` | `/grill-task` §3 | 1.3 |
| `01-业务需求文档 BRD.md` | `/to-brd` | 2 |
| `业务流程图-订单创建.txt` | `/to-brd` §3 | 2 |
| `业务流程图-订单状态流转.txt` | `/to-brd` §3 | 2 |
| `knowledge-path.md` | `/setup-analysis-delivery` | 0 |
| `tech-stack-path.md` | `/setup-analysis-delivery` | 0 |
| `compliance-path.md` | `/setup-analysis-delivery` | 0 |
| `doc-naming.md` | `/setup-analysis-delivery` | 0 |
| `config-used.md` | 配置使用记录 / ADR | 1 |

## 与 WMS 示例的差异

| 维度 | 01-wms-warehouse | 02-saas-dashboard |
|---|---|---|
| 数据库 | Oracle | PostgreSQL |
| 前端 | Vue 3 PC + uni-app 巴枪 | React 19 SPA |
| 后端 | Spring Boot + MyBatis-Plus | Express 5 + Prisma |
| 状态机 | 2 位码(10/30/40) | 字符串枚举(`pending`/`paid`/`shipped`) |
| 合规 | GSP(医药追溯) | None |
| 多租户 | 单租户 | 多租户(行级隔离) |
| 字符分隔 | `\|\|` | `\|\|`(PG 也支持) |
| 整数除法 | `1.0/3` | `1.0/3`(PG 也需要) |
| 序列 | `SEQ.NEXTVAL` | `SERIAL` / `BIGSERIAL` |
| 审计字段五件套 | 必须 | 必须(同样) |
| 文档编号 | 01-09 强制 | 01-09 强制 |

## 运行演示

```bash
# 1. 装 skill
npx skills@latest add <your-repo>

# 2. 在本目录调 skill
cd examples/02-saas-dashboard
/ask-delivery

# 3. 选 "走完整 9 阶段" → 看 skill 如何在 SaaS 场景跑通
```

## 不演示的

- 实际业务代码(本示例只演示文档输出,不含 Express/Prisma 代码)
- FSD / 数据模型 / 开发设计说明书(留给用户用 `/dev-design` 生成)
- PRD / 测试用例(留给用户用 `/test-case-design` `/to-prd` 生成)

## 下一步

用户拿到本示例后,推荐:
1. 跑 `/to-fsd` (或 `/dev-design`)生成完整技术设计
2. 跑 `/using-superpowers` → `/brainstorming` → `/writing-plans` 出实施计划
3. 跑 `/tdd` + `/executing-plans` 写代码
