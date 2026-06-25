# REVIEW 需求确认书:会员积分管理

> 项目:移动 App — 会员积分管理
> 日期:2026-06-22
> 状态:✅ AI 理解已确认(待用户最终签字)

## 一、需求背景确认（AI 助手的理解）

### 1.1 业务目标理解

| 用户原话 | AI 理解 | 置信度 |
|---|---|---|
| "积分全流程在线化" | 用户从获取到兑换全在 App 内完成,无纸质卡 / 微信群 | 95% |
| "提升复购率 30%" | 通过积分感知 + 过期提醒,提升用户复购 | 85% |
| "激活沉睡用户" | 通过积分过期提醒 + Push 召回 | 90% |

### 1.2 角色理解

6 角色,与 WMS 4 角色、SaaS 5 角色都不同。重点:**用户端 + 店员扫码端** 双端架构。

### 1.3 状态机理解

**双状态机**:
- 积分生命周期(`earn` / `active` / `used` / `expired` / `frozen`)
- 兑换订单(`draft` / `submitted` / `approved` / `fulfilled` / `completed` / `rejected` / `cancelled`)

## 二、需求目标确认（待确认的设计假设）

| 假设 | 默认值 | 影响 | 需确认 |
|---|---|---|---|
| 登录方式 | 手机号 + 微信 + Apple ID | 集成工作量 | ⚠️ |
| 积分有效期 | 2 年 | 业务规则 | ✅ |
| 积分过期提醒 | 到期前 7 天 Push | 推送频率 | ✅ |
| 邀请奖励 | 双向(邀请人 100,被邀请 50)| 业务规则 | ⚠️ |
| 多语言 | 中文 only(v1) | 不需要 i18n | ✅ |
| 离线支持 | 签到 + 明细可离线 | 复杂度 | ✅ |
| 数据存储 | Firestore + 本地缓存 | 双写一致性 | ⚠️ |
| 实时性 | 实时(Firestore listener)| 体验 | ✅ |
| 推送通道 | FCM(Android + iOS)| 统一 | ✅ |
| 会员等级 | 4 级(普通/银/金/钻石) | 业务规则 | ✅ |

## 三、功能范围确认（与 WMS / SaaS 示例的差异说明）

| 维度 | 假设差异 | 处理方式 |
|---|---|---|
| 数据库 | Oracle / PG → Firestore(NoSQL)| 不写 SQL,写 Firestore 规则 + 数据模型 |
| 后端 | Spring Boot / Express → Firebase | 写 Cloud Functions(Node.js 20)|
| 前端 | Vue / React → Flutter(Dart)| 跨平台编译 |
| 状态码 | 2 位 / 字符串 → Firestore 状态字段 | 用 TypeScript-like 枚举 |
| 字符分隔 | `\|\|` | 不适用 |
| 整数除法 | `1.0/3` 必须 | 不适用(强类型 Dart)|
| 审计字段 | 五件套 | Firestore 字段子集(`created_at` / `updated_at` / `created_by` / `version`)|
| 事务 | ACID | 单文档原子,跨文档用 Firestore transaction(限制 500)|

## 四、合规要求确认（字段映射预测,待阶段 2 字段对齐）

| 业务概念 | Firestore 字段 | 备注 |
|---|---|---|
| 用户 ID | `users.uid` | Firebase Auth UID |
| 积分余额 | `points_wallets.balance` | 整数(非浮点)|
| 积分流水 | `points_ledger.entries` | 子集合,append-only |
| 积分批次 | `points_batches` | 带 `expires_at`,FIFO 消耗 |
| 兑换单号 | `redemptions.order_no` | Firestore ID + 自定义 |
| 过期时间 | Timestamp | Firestore Timestamp 类型 |
| 软删除 | `is_deleted` | Firestore 字段 |
| 创建时间 | `created_at` | serverTimestamp() |

## 五、特殊要求确认（AI 助手待用户确认）

1. 登录方式选择?
2. 积分有效期?
3. 邀请奖励规则?
4. 离线范围?
5. 多语言?
6. 推送通道(FCM vs JPush vs 个推)?
7. 兑换商品来源(自营 / 第三方券)?
8. 退款时积分如何处理?

## 六、下一步

用户确认 → 进入 `/to-brd` 生成 BRD。
字段对齐分析 → `/grill-task` §3(`REVIEW_字段对齐分析.md`)。

## 七、AI 助手补充确认项(设计假设)

| 编号 | 确认项 | 设计假设 | 是否正确? |
|------|------|---------|---------|
| H-01 | 后端选型 | Firebase(Cloud Functions + Firestore) | ✅ |
| H-02 | 积分单位 | 整数 int64(禁止浮点) | ✅ |
| H-03 | 积分消耗策略 | FIFO 批次(过期优先用) | ✅ |
| H-04 | 审计字段 | 四件套(createdAt/updatedAt/createdBy/version) | ✅ |
| H-05 | 离线范围 | 签到 + 流水明细可离线 | ✅ |

## 八、待明确事项

| 编号 | 待明确事项 | 责任方 | 截止 |
|------|----------|------|------|