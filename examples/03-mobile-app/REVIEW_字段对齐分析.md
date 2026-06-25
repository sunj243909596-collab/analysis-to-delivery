# REVIEW 字段对齐分析:会员积分管理

> 项目:移动 App — 会员积分管理
> 日期:2026-06-22
> 状态:✅ 已对齐 / ⚠️ 需 JOIN / ❓ 待确认 / 🔴 缺失
> BLOCK 规则:🔴>0 或 ❓>0 → 禁止进入阶段 3(BRD)
>
> 说明:状态字段为四态可视化标签;BLOCK 判定以"对齐结论表"中的 ❓ 与 🔴 计数为准(task-confirm-check.py 解析该表的两行数字)。⚠️ 可保留(仅表示部分需 JOIN,不 BLOCK)。
> 后端:Firestore(从 `tech-stack-path.md` 读取)

## 一、字段对齐总览

| 业务概念 | Firestore 路径 | 数据类型 | 状态 |
|---|---|---|---|
| 用户 ID | `users/{uid}` | Document ID | ✅ 已对齐 |
| 积分余额 | `points_wallets/{uid}.balance` | number(int64) | ✅ 已对齐 |
| 积分流水 | `points_ledger/{uid}/entries/{entryId}` | 子集合 | ✅ 已对齐 |
| 积分批次 | `points_batches/{uid}/batches/{batchId}` | 子集合 | ✅ 已对齐 |
| 兑换订单 | `redemptions/{orderId}` | Document | ✅ 已对齐 |
| 兑换状态 | `redemptions.status` | string(枚举)| ✅ 已对齐 |
| 创建时间 | `*.created_at` | Timestamp | ✅ 已对齐 |
| 乐观锁 | `*.version` | number | ✅ 已对齐 |

## 二、与 SQL(Oracle / PostgreSQL)的差异

| 维度 | SQL | Firestore | 差异处理 |
|---|---|---|---|
| 表 | TABLE | Collection | 概念对应 |
| 行 | ROW | Document | 概念对应 |
| 关联查询 | JOIN | 不支持 | **反范式**(嵌套 / 冗余字段)|
| 事务 | ACID 全支持 | 单文档原子,跨文档限制 | **业务侧合并** |
| 聚合 | GROUP BY / COUNT | Cloud Functions 聚合 | **计算侧迁出** |
| 全文搜索 | 需扩展 | 需 Algolia / Typesense | **外部服务** |
| 排序 | ORDER BY | orderBy(需复合索引)| **配置索引** |
| 整数 | INT / BIGINT | number(64-bit int)| 注意精度 |
| 浮点 | FLOAT / NUMERIC | number(64-bit float)| **避免金额用浮点** |
| 布尔 | BOOLEAN | bool | 一致 |
| 字符串 | VARCHAR | string | 一致 |
| 时间 | TIMESTAMPTZ | Timestamp | 客户端需转换 |
| 主键 | SEQUENCE | Document ID(UUID 或自定义)| 推荐 UUID v4 |
| 软删除 | `is_deleted` | `is_deleted` | 一致 |

## 三、核心数据模型(待 `/dev-design` 阶段 7 详细设计)

### users(用户档案)

```typescript
// Firestore: /users/{uid}
interface UserDoc {
  uid: string;                    // Firebase Auth UID,Document ID
  phone?: string;                 // 手机号(可选)
  nickname: string;
  avatarUrl?: string;
  level: 'normal' | 'silver' | 'gold' | 'diamond';
  totalEarned: number;            // 累计获得积分
  registeredAt: Timestamp;
  lastLoginAt: Timestamp;
  isDeleted: boolean;             // 软删除
  // 审计字段
  createdAt: Timestamp;           // serverTimestamp
  updatedAt: Timestamp;
  createdBy: string;              // 触发者 UID
  version: number;                // 乐观锁
}
```

### points_wallets(积分钱包)

```typescript
// Firestore: /points_wallets/{uid}
interface PointsWalletDoc {
  uid: string;                    // Document ID
  balance: number;                // 当前可用积分(int64,禁止浮点)
  frozenBalance: number;          // 冻结积分(争议中)
  expiringSoon: number;           // 30 天内即将过期
  updatedAt: Timestamp;
  version: number;
}
```

### points_batches(积分批次 — FIFO 消耗)

```typescript
// Firestore: /points_batches/{uid}/batches/{batchId}
// 每获取一次积分,生成一个批次(带过期时间)
interface PointsBatchDoc {
  batchId: string;                // UUID
  uid: string;
  source: 'check_in' | 'purchase' | 'referral' | 'activity' | 'manual';
  amount: number;                 // 本批次总额
  remaining: number;              // 本批次剩余(随消耗递减)
  earnedAt: Timestamp;
  expiresAt: Timestamp;           // 通常 earnedAt + 2 年
  isExpired: boolean;
  isFrozen: boolean;
}
```

### points_ledger(积分流水 — 不可变)

```typescript
// Firestore: /points_ledger/{uid}/entries/{entryId}
// append-only,所有积分变动必须有流水记录
interface PointsLedgerEntry {
  entryId: string;
  uid: string;
  type: 'earn' | 'use' | 'expire' | 'freeze' | 'unfreeze';
  amount: number;                 // 正=获得,负=消耗
  balanceAfter: number;           // 变动后余额
  source: string;                 // 来源
  sourceId?: string;              // 来源 ID(批次 / 兑换单等)
  note?: string;
  createdAt: Timestamp;           // serverTimestamp
  createdBy: string;              // uid 或 'system'
}
```

### redemptions(兑换订单)

```typescript
// Firestore: /redemptions/{orderId}
interface RedemptionDoc {
  orderId: string;                // UUID
  uid: string;
  productId: string;
  productName: string;
  pointsCost: number;             // 消耗积分
  status: 'draft' | 'submitted' | 'approved'
        | 'fulfilled' | 'completed'
        | 'rejected' | 'cancelled';
  couponCode?: string;            // 核销码(fulfilled 后生成)
  qrCodeUrl?: string;             // 核销二维码 URL
  approvedBy?: string;            // 店员 UID
  approvedAt?: Timestamp;
  fulfilledAt?: Timestamp;
  rejectReason?: string;
  cancelReason?: string;
  createdAt: Timestamp;
  updatedAt: Timestamp;
  version: number;
}
```

## 四、严禁自创的字段(待用户确认)

- 积分用 `number`(int64),**禁止用浮点**(精度问题)
- 积分余额计算必须用 **FIFO 批次** 消耗(避免过期积分被先用)
- 所有积分变动必须有 **流水记录**(append-only)
- 过期时间用 `Timestamp`,**禁止存毫秒数**(跨时区混乱)
- 审计字段必带 `createdAt` / `updatedAt` / `createdBy` / `version`

## 五、跨文档一致性确认

- ✅ `tech-stack-path.md` 已标 Firestore
- ✅ `knowledge-path.md` 指向 Firestore 文档
- ✅ `doc-naming.md` 用 01-09 编号
- ✅ `compliance-path.md` 选 none(轻度 PIPL 自检)

## 六、关键索引(待 `/dev-design` 配置)

```javascript
// firestore.indexes.json(关键复合索引)
{
  "indexes": [
    {
      "collectionGroup": "entries",
      "queryScope": "COLLECTION",
      "fields": [
        { "fieldPath": "uid", "order": "ASCENDING" },
        { "fieldPath": "createdAt", "order": "DESCENDING" }
      ]
    },
    {
      "collectionGroup": "batches",
      "queryScope": "COLLECTION",
      "fields": [
        { "fieldPath": "uid", "order": "ASCENDING" },
        { "fieldPath": "expiresAt", "order": "ASCENDING" },
        { "fieldPath": "remaining", "order": "DESCENDING" }
      ]
    },
    {
      "collectionGroup": "redemptions",
      "queryScope": "COLLECTION",
      "fields": [
        { "fieldPath": "uid", "order": "ASCENDING" },
        { "fieldPath": "status", "order": "ASCENDING" },
        { "fieldPath": "createdAt", "order": "DESCENDING" }
      ]
    }
  ]
}
```

## 七、Firestore 安全规则(关键)

```javascript
// firestore.rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    // 钱包 — 只能读自己的,不能直接写(走 Cloud Functions)
    match /points_wallets/{uid} {
      allow read: if request.auth != null && request.auth.uid == uid;
      allow write: if false;  // 仅 Cloud Functions 用 Admin SDK 写
    }

    // 流水 — 只能读自己的
    match /points_ledger/{uid}/entries/{entryId} {
      allow read: if request.auth != null && request.auth.uid == uid;
      allow write: if false;
    }

    // 兑换订单 — 只能读自己的,只能创建 draft 状态
    match /redemptions/{orderId} {
      allow read: if request.auth != null && resource.data.uid == request.auth.uid;
      allow create: if request.auth != null
                    && request.resource.data.uid == request.auth.uid
                    && request.resource.data.status == 'draft';
      allow update: if request.auth != null
                    && resource.data.uid == request.auth.uid
                    && resource.data.status == 'draft'
                    && request.resource.data.status == 'submitted';
    }

    // 批次 — 仅 Cloud Functions 访问
    match /points_batches/{uid}/batches/{batchId} {
      allow read, write: if false;
    }
  }
}
```

## 八、对齐结论

| 类别 | 数量 |
|---|---|
| ✅ 已对齐 | 8 |
| ⚠️ 需 JOIN | 0 |
| ❓ 待确认 | 0 |
| 🔴 缺失 | 0 |

**结论**:
- ⬜ 🔴=0 且 ❓=0 → 可以进入阶段 3(BRD)

---

## 九、下一步

字段对齐通过 → 进入 `/to-brd` 生成 BRD。