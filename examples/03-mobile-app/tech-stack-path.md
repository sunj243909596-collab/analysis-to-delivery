# 技术栈路径(移动 App — 会员积分管理)

> 项目:移动 App — 会员积分管理
> 路径配置:本文档被 `/setup-analysis-delivery` 阶段 1 引用
> 用途:明确本项目的技术选型、版本、目录结构

## 一、整体架构

```
┌────────────────────────────────────────────────────────────────┐
│  客户端(iOS 17+ / Android 14+)                                   │
│  Flutter 3.24 (Dart 3.5)                                        │
│  状态管理:Riverpod 2                                             │
│  路由:go_router 14                                              │
│  本地缓存:Hive 2 / Firestore 离线                              │
└──────────────────┬─────────────────────────────────────────────┘
                   │ HTTPS / Firebase SDK
                   ▼
┌────────────────────────────────────────────────────────────────┐
│  Firebase 平台                                                    │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  Firebase Auth(手机号/微信/Apple ID)                       │   │
│  ├────────────────────────────────────────────────────────┤   │
│  │  Cloud Firestore(数据存储 + 实时同步 + 离线)               │   │
│  ├────────────────────────────────────────────────────────┤   │
│  │  Cloud Storage(头像/二维码图片)                            │   │
│  ├────────────────────────────────────────────────────────┤   │
│  │  Cloud Functions for Firebase(Node.js 20 业务逻辑)        │   │
│  │  Triggers:onCreate / onUpdate / onCall / Scheduled       │   │
│  ├────────────────────────────────────────────────────────┤   │
│  │  FCM(推送通知 iOS + Android)                              │   │
│  ├────────────────────────────────────────────────────────┤   │
│  │  Crashlytics(崩溃监控)+ Performance(性能监控)            │   │
│  └────────────────────────────────────────────────────────┘   │
└──────────────────┬─────────────────────────────────────────────┘
                   │ (Firebase 自动管理基础设施)
                   ▼
┌────────────────────────────────────────────────────────────────┐
│  Google Cloud Platform(GCP 后端)                                 │
│  Cloud Functions 运行环境 / Cloud Scheduler / Cloud Logging     │
└────────────────────────────────────────────────────────────────┘
```

## 二、技术选型清单

### 2.1 客户端(Flutter 3.24)

| 类别 | 选型 | 版本 | 理由 |
|---|---|---|---|
| 框架 | Flutter | 3.24.x | 跨平台,性能接近原生 |
| 语言 | Dart | 3.5+ | 强类型,async/await 优秀 |
| 状态管理 | Riverpod | 2.x | 类型安全,可测试,无 BuildContext 依赖 |
| 不可变数据 | freezed | 2.x | 数据类 + union types |
| JSON 序列化 | json_serializable + build_runner | 6.x | 自动生成 |
| 路由 | go_router | 14.x | 声明式,支持 deep link |
| HTTP | dio | 5.x | 拦截器 / 取消 / 重试 |
| 本地缓存 | Hive | 2.x | 轻量,纯 Dart,无需 Native |
| 国际化 | intl + flutter_localizations | 0.19+ | 官方推荐 |
| 图片 | cached_network_image | 3.x | 缓存 + 占位 + 错误 |
| 二维码 | qr_flutter | 4.x | 生成 + 扫描 |
| 扫码 | mobile_scanner | 5.x | ML Kit 底座 |
| 签名 | signature | 5.x | 手写签名(兑换确认) |
| 单元测试 | flutter_test | - | 内置 |
| Mock | mockito | 5.x | 标准 |
| 集成测试 | integration_test | - | 官方 |

### 2.2 后端 / Firebase 平台

| 类别 | 选型 | 版本 | 理由 |
|---|---|---|---|
| BaaS | Firebase | latest | 一站式后端 |
| 数据库 | Cloud Firestore | - | NoSQL + 实时 + 离线 |
| 鉴权 | Firebase Auth | - | 多平台登录 |
| 文件存储 | Cloud Storage | - | 图片 / 文件 |
| 业务逻辑 | Cloud Functions | Node.js 20 | 触发器 / Callable |
| 推送 | FCM | - | iOS + Android 统一 |
| 监控 | Crashlytics + Performance | - | 错误 + 性能 |
| 分析 | Firebase Analytics + BigQuery | - | 行为分析 |
| 远程配置 | Remote Config | - | 灰度 / 开关 |
| 定时任务 | Cloud Scheduler + Pub/Sub | - | 每日 02:00 过期处理 |

### 2.3 CI/CD

| 类别 | 选型 | 备注 |
|---|---|---|
| CI | GitHub Actions | 与本仓库一致 |
| iOS 构建 | Codemagic / Fastlane | Xcode 15+ |
| Android 构建 | Codemagic / Gradle | JDK 17+ |
| 内测分发 | Firebase App Distribution | 跨平台 |
| iOS 测试 | TestFlight | Apple 官方 |
| Android 测试 | Google Play Internal Testing | 官方 |

## 三、目录结构

### 3.1 Flutter 客户端

```
mobile/
├── lib/
│   ├── main.dart                       # 入口
│   ├── app.dart                        # App 根
│   ├── core/                           # 核心层
│   │   ├── config/                     # 配置(环境 / 主题)
│   │   ├── constants/                  # 常量
│   │   ├── errors/                     # 错误类型
│   │   ├── utils/                      # 工具
│   │   ├── extensions/                 # 扩展方法
│   │   └── logging/                    # 日志
│   ├── data/                           # 数据层
│   │   ├── models/                     # 数据模型(freezed)
│   │   ├── repositories/               # 仓储
│   │   │   ├── user_repository.dart
│   │   │   ├── points_repository.dart
│   │   │   └── redemption_repository.dart
│   │   ├── datasources/                # 数据源
│   │   │   ├── firestore/              # Firestore
│   │   │   ├── functions/              # Cloud Functions
│   │   │   └── local/                  # 本地缓存
│   │   └── services/                   # 服务
│   │       ├── auth_service.dart
│   │       ├── fcm_service.dart
│   │       └── analytics_service.dart
│   ├── domain/                         # 领域层
│   │   ├── entities/                   # 实体
│   │   ├── usecases/                   # 用例
│   │   └── validators/                 # 校验
│   ├── presentation/                   # 表现层
│   │   ├── providers/                  # Riverpod providers
│   │   ├── pages/                      # 页面
│   │   │   ├── home/
│   │   │   ├── points/
│   │   │   ├── redemption/
│   │   │   ├── profile/
│   │   │   └── auth/
│   │   ├── widgets/                    # 通用组件
│   │   └── dialogs/                    # 弹窗
│   ├── routes/                         # go_router 配置
│   ├── l10n/                           # 国际化
│   └── generated/                      # 生成代码(intl / json)
├── test/
│   ├── unit/
│   ├── widget/
│   └── integration/
├── android/                            # Android 原生
├── ios/                                # iOS 原生
├── assets/                             # 资源(图片 / 字体)
├── pubspec.yaml
├── analysis_options.yaml               # Lint
└── firebase.json
```

### 3.2 Cloud Functions

```
functions/
├── src/
│   ├── index.ts                        # 入口
│   ├── triggers/                       # 触发器
│   │   ├── onUserCreated.ts
│   │   ├── onRedemptionCreated.ts
│   │   └── ...
│   ├── callables/                      # Callable
│   │   ├── checkIn.ts
│   │   ├── bindReceipt.ts
│   │   ├── redeem.ts
│   │   └── ...
│   ├── scheduled/                      # 定时
│   │   ├── expirePoints.ts            # 每日 02:00
│   │   └── sendExpiryReminder.ts      # 每日 09:00
│   ├── core/                           # 核心
│   │   ├── points.ts                  # 积分计算
│   │   ├── batch.ts                   # FIFO 批次
│   │   ├── ledger.ts                  # 流水
│   │   └── errors.ts
│   ├── repositories/                   # 仓储
│   ├── models/                         # 类型
│   └── utils/
├── test/
├── package.json
├── tsconfig.json
└── .firebaserc
```

### 3.3 仓库根

```
.
├── .github/
│   └── workflows/
├── mobile/                             # Flutter 客户端
├── functions/                          # Cloud Functions
├── firestore.rules                     # Firestore 安全规则
├── firestore.indexes.json              # Firestore 索引
├── firebase.json                       # Firebase 配置
├── .firebaserc                         # Firebase 项目别名
└── README.md
```

## 四、版本兼容矩阵

| 组件 | 版本要求 | 兼容性 |
|---|---|---|
| Flutter | 3.24+ | Dart 3.5+ |
| Dart | 3.5+ | null safety |
| iOS | 17+ | Flutter 3.24 |
| Android | 14+ (API 34) | Flutter 3.24 |
| Node.js (Functions) | 20 LTS | Firebase Functions |
| Firebase CLI | 13+ | FlutterFire CLI 1.x |

## 五、关键依赖锁定

| 包 | 锁定版本 | 原因 |
|---|---|---|
| flutter | 3.24.x | null safety 稳定 |
| firebase_core | 3.x | 与 Flutter 3.24 兼容 |
| cloud_firestore | 5.x | 与 firebase_core 3 匹配 |
| firebase_auth | 5.x | 同上 |
| riverpod | 2.5+ | 移除 Provider 旧 API |
| freezed | 2.5+ | 与 Dart 3.5 匹配 |
| go_router | 14.x | 新版 deep link 语法 |
| Node.js | 20 LTS | Functions 运行时 |

## 六、环境要求

### 6.1 开发

- Flutter SDK 3.24.x
- Dart 3.5+
- Android Studio Hedgehog+
- Xcode 15+
- Firebase CLI 13+
- FlutterFire CLI 1.x
- Java 17
- CocoaPods 1.13+

### 6.2 生产

- Firebase 项目(Blaze 计划,按量付费)
- iOS App Store 开发者账号($99/年)
- Google Play 开发者账号($25 一次性)
- APNs 证书(.p8 key,3 年有效)
- FCM 服务端密钥

## 七、ADR(架构决策记录)

### ADR-001:选 Flutter 3.24 而非 React Native / 原生

**决策**:Flutter 3.24

**原因**:
- ✅ 跨平台性能接近原生(Skia 渲染)
- ✅ Dart 强类型,空安全成熟
- ✅ hot reload 开发效率高
- ✅ 单一代码库,降低维护成本
- ✅ Firebase 集成完善(FlutterFire)
- ❌ React Native:桥接性能损耗,TypeScript 集成复杂
- ❌ 双原生开发:成本翻倍

### ADR-002:选 Riverpod 而非 Provider / Bloc

**决策**:Riverpod 2

**原因**:
- ✅ 类型安全,无 BuildContext 依赖
- ✅ 可测试(无需 Widget tree)
- ✅ lazy 加载,自动 dispose
- ✅ 组合性优于 Provider
- ❌ Bloc:样板代码多

### ADR-003:选 Firestore 而非 Realtime Database

**决策**:Cloud Firestore

**原因**:
- ✅ 文档模型,查询能力更强
- ✅ 离线支持更好
- ✅ 复合索引,排序高效
- ✅ 与 Cloud Functions 深度集成
- ❌ Realtime Database:JSON 树,查询弱,无离线

### ADR-004:积分用 FIFO 批次

**决策**:每获取积分生成批次,消耗按过期时间升序

**原因**:
- ✅ 用户利益最大化(先过期先用)
- ✅ 避免过期积分长期占用
- ✅ 财务清晰(每批可追溯)
- ❌ 复杂度高

### ADR-005:积分变动走 Cloud Functions

**决策**:钱包更新只能在 Cloud Functions(Admin SDK)

**原因**:
- ✅ 安全性(客户端不能绕过)
- ✅ 数据一致性(集中处理)
- ✅ 业务逻辑集中
- ❌ 增加延迟(网络调用)

### ADR-006:离线优先架构

**决策**:关键路径(签到 / 查看)支持离线

**原因**:
- ✅ 弱网环境可用
- ✅ 减少等待
- ✅ 用户体验好
- ❌ 冲突处理复杂

## 八、与 WMS / SaaS 示例的技术栈对比

| 维度 | WMS | SaaS | App(本项目) |
|---|---|---|---|
| 数据库 | Oracle | PostgreSQL | Cloud Firestore |
| 后端 | Spring Boot | Express | Cloud Functions(Node.js 20) |
| 前端框架 | Vue 3 | React 19 | Flutter 3.24 |
| 状态管理 | Pinia | TanStack Query | Riverpod 2 |
| 鉴权 | Spring Security + JWT | jsonwebtoken | Firebase Auth |
| 实时性 | 异步队列 | T+1 | 实时(Firestore listener) |
| 离线 | 不涉及 | 不涉及 | 必备 |
| 推送 | 不涉及 | 不涉及 | FCM |
| 字符分隔 | `\|\|` | `\|\|` | 不适用 |
| 整数除法 | `1.0/3` | `1.0/3` | 不适用(Dart 强类型) |
| 审计字段 | 五件套 | 五件套 | 子集(4 件)|
| 文档编号 | 01-09 | 01-09 | 01-09 |