# REVIEW 字段对齐分析:客户订单管理

> 项目:SaaS 后台 — 客户订单管理
> 日期:2026-06-22
> 状态:✅ 已对齐 / ⚠️ 需 JOIN / ❓ 待确认 / 🔴 缺失
> BLOCK 规则:🔴>0 或 ❓>0 → 禁止进入阶段 3(BRD)
>
> 说明:状态字段为四态可视化标签;BLOCK 判定以"对齐结论表"中的 ❓ 与 🔴 计数为准(task-confirm-check.py 解析该表的两行数字)。⚠️ 可保留(仅表示部分需 JOIN,不 BLOCK)。
> 数据库:PostgreSQL 16(从 `tech-stack-path.md` 读取)

## 一、字段对齐总览

| 业务概念 | 字段 | 知识库来源 | 状态 |
|---|---|---|---|
| 订单号 | `orders.order_no` | 自建表 | ✅ 已对齐 |
| 客户 ID | `orders.customer_id` | 自建表 | ✅ 已对齐 |
| 多租户 ID | `orders.tenant_id` | 自建表 | ✅ 已对齐 |
| 订单状态 | `orders.status` | 自建表(字符串枚举) | ✅ 已对齐 |
| 创建时间 | `orders.created_at` | TIMESTAMPTZ | ✅ 已对齐 |
| 乐观锁 | `orders.version` | INTEGER | ✅ 已对齐 |
| 订单金额 | `order_items.subtotal` | NUMERIC(12,2) | ✅ 已对齐 |
| 支付流水 | `payments.transaction_id` | VARCHAR(64) | ✅ 已对齐 |

## 二、与 WMS(Oracle)的差异

| 维度 | Oracle | PostgreSQL | 差异处理 |
|---|---|---|---|
| 空值替换 | `NVL(a, b)` | `COALESCE(a, b)` | 改用 COALESCE |
| 当前时间 | `SYSDATE` | `NOW()` / `CURRENT_TIMESTAMP` | 改用 `NOW()` |
| 行数限制 | `ROWNUM <= N` | `LIMIT N` | 改用 `LIMIT` |
| 字符串连接 | `a \|\| b` | `a \|\| b` | 一致 |
| 序列 | `SEQ.NEXTVAL` | `NEXTVAL('seq_name')` | 改用函数式 |
| 整数除法 | `1.0/3` 必须 | `1.0/3` 必须 | 一致 |
| 审计字段 | DATE 类型 | TIMESTAMPTZ 类型 | 改用时区感知 |
| 主键策略 | SEQUENCE | SERIAL / BIGSERIAL / UUID | 推荐 UUID(v4) |

## 三、新增表(待 `/dev-design` 阶段 7 详细设计)

### orders(订单主表)

```sql
CREATE TABLE orders (
    id          BIGSERIAL PRIMARY KEY,
    order_no    VARCHAR(20) UNIQUE NOT NULL,
    tenant_id   BIGINT NOT NULL,
    customer_id BIGINT NOT NULL,
    status      VARCHAR(20) NOT NULL DEFAULT 'draft',
    total       NUMERIC(12, 2) NOT NULL DEFAULT 0,
    version     INTEGER NOT NULL DEFAULT 1,  -- 乐观锁
    -- 审计字段五件套
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by  BIGINT,
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by  BIGINT,
    is_deleted  BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE INDEX idx_orders_tenant ON orders(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_orders_customer ON orders(customer_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_orders_status ON orders(status) WHERE is_deleted = FALSE;
```

### order_items(订单明细)

```sql
CREATE TABLE order_items (
    id          BIGSERIAL PRIMARY KEY,
    order_id    BIGINT NOT NULL REFERENCES orders(id),
    product_id  BIGINT NOT NULL,
    quantity    INTEGER NOT NULL CHECK (quantity > 0),
    unit_price  NUMERIC(10, 2) NOT NULL,
    subtotal    NUMERIC(12, 2) NOT NULL,
    -- 审计字段
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by  BIGINT,
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by  BIGINT,
    is_deleted  BOOLEAN NOT NULL DEFAULT FALSE
);
```

## 四、严禁自创的字段(待用户确认)

- `orders.status` 是字符串枚举,不是 2 位数字码(与 WMS 不同)
- 多租户必须每张表带 `tenant_id`(无例外)
- 审计字段必须五件套(无例外)
- 金额用 NUMERIC(12,2),不用 FLOAT(浮点精度)

## 五、跨文档一致性确认

- ✅ `tech-stack-path.md` 已标 PostgreSQL
- ✅ `knowledge-path.md` 指向 PostgreSQL 16 文档
- ✅ `doc-naming.md` 用 01-09 编号
- ✅ `compliance-path.md` 选 none

## 六、对齐结论

| 类别 | 数量 |
|---|---|
| ✅ 已对齐 | 8 |
| ⚠️ 需 JOIN | 0 |
| ❓ 待确认 | 0 |
| 🔴 缺失 | 0 |

**结论**:
- ⬜ 🔴=0 且 ❓=0 → 可以进入阶段 3(BRD)

---

## 七、下一步

字段对齐通过 → 进入 `/to-brd` 生成 BRD。
