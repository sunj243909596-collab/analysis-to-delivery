# 产品需求文档（PRD）：移动 App — 会员积分管理

> 版本：v0.1
> 日期：2026-07-08
> 状态：✅ 已确认

## 一、产品概述

### 1.1 背景
B2C 零售品牌当前用纸质会员卡 + 微信群发积分,易丢失、感知弱、兑换难、复购低、数据散。详见 `01-业务需求文档 BRD.md` §一。

### 1.2 目标
- 积分全流程在线化(App 内完成所有操作)
- 复购率提升 30%
- 沉睡用户激活率 20%
- 积分过期主动提醒(到期前 7 天 Push)
- 离线签到成功率 > 95%
- 推送送达率 > 90%
- PIPL + App Store/Google Play 政策合规

### 1.3 范围
**包含**：用户体系(注册/登录/会员等级)、积分获取(签到/消费返/邀请/活动)、积分兑换(商品/优惠券)、积分明细、积分过期(FIFO)、推送(FCM)、离线支持、店员核销端。
**不包含**：支付集成、物流配送、客服 IM、数据分析后台。

## 二、用户故事

| 角色 | 场景 | 需求 | 优先级 |
|---|---|---|---|
| 游客 | 浏览首页 | 不登录可看商品列表 | P2 |
| 会员 | 每日签到 | 打开 App → 点"签到" → 获得 1-10 分(连续签到奖励) | P0 |
| 会员 | 查看积分 | 实时看到积分余额 + 明细 | P0 |
| 会员 | 兑换商品/券 | 选商品 → 确认兑换 → 生成券码 → 到店核销 | P0 |
| VIP 会员 | 专属兑换 | 看 VIP 专属商品池 + 优先客服 | P1 |
| 会员 | 邀请好友 | 分享邀请码 → 双方各得积分(邀请人 100,被邀请 50) | P1 |
| 店员 | 扫码核销 | 扫用户券码 → 标记 completed | P0 |
| 运营 | 配置活动 | 后台配置积分倍率/活动商品/推送文案 | P1 |
| 管理员 | 用户管理 | 封禁违规用户 + 查看审计日志 | P1 |

## 三、功能需求

### 3.1 每日签到

#### 3.1.1 功能说明
会员每日打开 App → 点击"签到" → 系统写 check_ins 集合 → Cloud Functions 触发 earnPoints → 写 points_ledger + 更新 points_wallets。

#### 3.1.2 业务流程
详见 BRD §三.3.1 泳道图 + `业务流程图-积分获取.txt`。

#### 3.1.3 界面设计
（Flutter 移动端,首页顶部"签到"卡片 + 连续签到日历热力图；屏幕 6 寸,大按钮 ≥ 48dp）

#### 3.1.4 字段定义

| 字段名 | 类型 | 必填 | 校验 | 数据来源 | 备注 |
|---|---|---|---|---|---|
| uid | string | 是 | Firebase Auth UID | Firebase Auth | |
| checkInDate | Timestamp | 是 | 当日 00:00-23:59 | serverTimestamp() | |
| pointsEarned | number(int64) | 是 | 1-10(连续天数相关) | 计算 | **禁止浮点** |
| consecutiveDays | number | 是 | ≥ 1 | 计算 | |
| createdAt | Timestamp | 是 | serverTimestamp() | DB | |

#### 3.1.5 业务规则
- 每日仅可签到 1 次(服务端幂等:uid + checkInDate 唯一索引)
- 连续签到奖励:1-3 天 1 分,4-6 天 5 分,7 天 10 分,循环
- 离线签到:本地暂存到 check_ins_offline,联网后回放(去重)
- 积分批次:每次签到生成新批次,默认 2 年后过期

#### 3.1.6 异常处理

| 异常 | 提示 | 处理 |
|---|---|---|
| 重复签到 | "今日已签到" | 拦截 |
| 离线签到 | "已暂存,联网后同步" | 本地缓存,联网回放 |
| 同步冲突 | "签到冲突,以服务端为准" | 服务端 last-write-wins |
| 网络中断 | "签到失败,请重试" | 客户端重试 |

#### 3.1.7 权限控制
- 会员：可签到、看自己的签到记录
- 店员：不可签到
- 运营：不可签到,但可看全员签到统计

### 3.2 积分兑换

#### 3.2.1 功能说明
会员选商品/优惠券 → 创建 redemption(draft) → 确认兑换(submitted) → Cloud Functions redeemPoints → FIFO 消耗批次 → 扣减 wallet → 生成券码 → fulfilled。

#### 3.2.2 业务规则
- 兑换状态机:draft → submitted → approved → fulfilled → completed
- FIFO 批次消耗:按 expiresAt 升序消耗(先过期先用)
- 单文档事务:wallet.balance 校验 + 扣减 在 Cloud Functions 事务中
- 券码生成:16 位 Base32 随机串(规避 0/1/O/I 等易混字符)
- 兑换需联网(不允许离线)
- 兑换撤回:仅 draft/submitted 状态可撤回,approved/fulfilled 不可撤回(走退款)

#### 3.2.3 字段定义

| 字段名 | 类型 | 必填 | 校验 | 数据来源 |
|---|---|---|---|---|
| orderId | string | 是 | UUID | 系统生成 |
| uid | string | 是 | 存在 | Firebase Auth |
| productId | string | 是 | 存在 | products |
| pointsCost | number(int64) | 是 | > 0,≤ wallet.balance | products |
| status | string | 是 | 枚举 | 状态机 |
| couponCode | string | 条件 | fulfilled 时生成 | 计算 |
| createdAt | Timestamp | 是 | serverTimestamp() | DB |
| version | number | 是 | ≥ 0 | 自增 |

#### 3.2.4 权限控制
- 会员：可创建/查看/撤回自己的兑换单
- 店员：可改 status 为 completed(扫码核销)
- 运营：可改 status 为 refunded(异常处理)

### 3.3 推送通知

#### 3.3.1 功能说明
- 签到提醒:每日 09:00 推送给未签到用户
- 积分到账:实时推送(收到积分立即)
- 兑换成功:实时推送
- 过期提醒:到期前 7 天推送
- 活动推送:运营后台配置

#### 3.3.2 业务规则
- FCM 送达率 > 90%(目标)
- 多通道兜底:FCM → APNs → 极光(按优先级)
- 用户可关闭非关键推送(签到/到账/兑换不可关)
- 推送频次限制:同类型 ≤ 3 条/天(避免骚扰)

## 四、非功能需求

### 4.1 性能
- 签到响应 < 500ms(P95)
- 积分查询 < 300ms(Firestore listener 实时)
- 兑换流程 < 3s
- App 启动 < 2s
- 推送送达延迟 < 5s

### 4.2 可靠性
- 离线签到成功率 > 95%
- 积分流水不可丢失(append-only 子集合)
- 兑换订单状态严格流转(Cloud Functions 事务)
- 过期处理每日定时(02:00 cron)
- Crashlytics 崩溃自动上报

### 4.3 实时性
- 积分变动实时同步(Firestore listener)
- 兑换状态实时推送
- 离线 → 在线自动同步(回放队列)

### 4.4 安全
- Firestore 安全规则(规则级权限控制)
- Cloud Functions Admin SDK(服务端授权)
- 手机号加密存储(Firestore field-level encryption)
- 敏感操作日志(consent_log / operation_log 子集合)
- Sign in with Apple(iOS 强制要求)

### 4.5 兼容性
- iOS 14+ / Android 8+
- Flutter 3.24 / Dart 3.5
- Firebase(Auth / Firestore / Functions / Storage / FCM / Analytics)

## 五、数据需求

参考：
- `03-数据模型设计.md`（Firestore collections + composite indexes）
- `REVIEW_字段对齐分析.md`（NoSQL/Firestore 字段映射）

主要集合(Firestore):
- users / points_wallets / points_ledger(子集合)/ points_batches(子集合)/ redemptions / products / coupons / referrals / check_ins / notifications / staff_users / consent_log / operation_log

## 六、合规要求

参考：`04-合规评审.md`
- PIPL 严重条款第 4 条 100% 符合
- App Store Guidelines 5.1 100% 符合(隐私政策)
- Google Play Data Safety 100% 符合
- 主要条款(PIPL 第 24/47 条 + App Store 5.1.1 + Google Play Family + 04001-隐私)100% 符合
- 综合判定：✅ 符合

## 七、验收标准

| # | 验收项 | 验收方式 | 通过标准 |
|---|---|---|---|
| 1 | BRD 9 章节齐全 | `brd-check.py --strict` | exit 0 |
| 2 | 合规评审 10 条款(PIPL + App Store + Google Play) | `compliance-check.py --strict` | exit 0 |
| 3 | 测试用例 5 大类 | `testcase-coverage-check.py --strict` | exit 0 |
| 4 | 字段映射无错 | `field-alignment-check.py` | exit 0 |
| 5 | 流程图无回流闭环 | `flow-to-mermaid.py --ascii-strict` | exit 0 |
| 6 | Firestore 安全规则测试 | emulator + 自动化测试 | 通过 |
| 7 | 离线签到测试 | 飞行模式 + 30 笔签到 + 联网回放 | 100% 同步 |
| 8 | FIFO 批次过期测试 | 单元测试覆盖 | 100% |

> 签字：**我已全部确认,可以进入下一步**（2026-07-08 黄噜噜）

## 八、风险与依赖

| 风险 | 影响 | 缓解 | 责任方 |
|---|---|---|---|
| 积分并发扣减 | 超扣 / 数据不一致 | Cloud Functions 事务 + 乐观锁 | 后端 |
| FIFO 过期计算错误 | 用户投诉 | 单元测试覆盖 + 每日对账 | 后端 |
| 离线签到冲突 | 重复签到 | 客户端去重 + 服务端幂等 | 客户端 + 后端 |
| FCM 送达率低 | 提醒失效 | 多通道兜底(APNs / 极光)| 运维 |
| Firestore 跨文档事务限制 | 复杂业务难实现 | 业务侧合并 + 单文档原子 | 架构 |
| App Store 审核驳回 | 上线延期 | 上架前合规自检 + TestFlight 内测 | PM |
| Google Play 数据安全声明 | 商店拒绝上架 | Play Console 完整填写 | PM |