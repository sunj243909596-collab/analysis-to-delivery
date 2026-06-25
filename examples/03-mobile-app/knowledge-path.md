# 知识库路径(移动 App — 会员积分管理)

> 项目:移动 App — 会员积分管理
> 路径配置:本文档被 `/setup-analysis-delivery` 阶段 1 引用
> 用途:指向该项目所依赖的官方文档 / 内部知识库 / 第三方资料

## 一、Flutter 3.24 知识库

### 1.1 官方文档

| 类别 | URL |
|---|---|
| Flutter 3.24 | https://docs.flutter.dev/ |
| Dart 3.5 | https://dart.dev/ |
| Widget Catalog | https://docs.flutter.dev/ui/widgets |
| State Management | https://docs.flutter.dev/data-and-backend/state-mgmt |
| Async / Future | https://dart.dev/codelabs/async-await |
| Stream | https://dart.dev/tutorials/language/streams |

### 1.2 项目关键库

| 库 | 版本 | 用途 | 文档 |
|---|---|---|---|
| firebase_core | 3.x | Firebase 初始化 | https://firebase.flutter.dev/ |
| firebase_auth | 5.x | 用户认证 | https://firebase.google.com/docs/auth |
| cloud_firestore | 5.x | Firestore 数据库 | https://firebase.google.com/docs/firestore |
| firebase_storage | 12.x | 文件存储 | https://firebase.google.com/docs/storage |
| firebase_messaging | 15.x | FCM 推送 | https://firebase.google.com/docs/cloud-messaging |
| firebase_analytics | 11.x | 数据分析 | https://firebase.google.com/docs/analytics |
| firebase_remote_config | 5.x | 远程配置 | https://firebase.google.com/docs/remote-config |
| riverpod | 2.x | 状态管理 | https://riverpod.dev/ |
| freezed | 2.x | 数据类 + 不可变 | https://pub.dev/packages/freezed |
| json_serializable | 6.x | JSON 序列化 | https://pub.dev/packages/json_serializable |
| go_router | 14.x | 路由 | https://pub.dev/packages/go_router |
| dio | 5.x | HTTP 客户端 | https://pub.dev/packages/dio |
| intl | 0.19.x | 国际化 | https://pub.dev/packages/intl |
| hive | 2.x | 本地存储 | https://pub.dev/packages/hive |
| sqflite | 2.x | SQLite(备选) | https://pub.dev/packages/sqflite |

## 二、Firebase 知识库

### 2.1 官方文档

| 服务 | URL |
|---|---|
| Firebase Console | https://console.firebase.google.com/ |
| Firebase 文档总索引 | https://firebase.google.com/docs |
| Authentication | https://firebase.google.com/docs/auth |
| Cloud Firestore | https://firebase.google.com/docs/firestore |
| Cloud Functions | https://firebase.google.com/docs/functions |
| Cloud Storage | https://firebase.google.com/docs/storage |
| Cloud Messaging | https://firebase.google.com/docs/cloud-messaging |
| Firebase Crashlytics | https://firebase.google.com/docs/crashlytics |
| Firebase Analytics | https://firebase.google.com/docs/analytics |
| Firebase Performance | https://firebase.google.com/docs/perf-mon |

### 2.2 Cloud Functions(Node.js 20)

| 类别 | URL |
|---|---|
| Functions 文档 | https://firebase.google.com/docs/functions |
| Firestore Triggers | https://firebase.google.com/docs/functions/firestore-events |
| Callable Functions | https://firebase.google.com/docs/functions/callable |
| Scheduled Functions | https://firebase.google.com/docs/functions/schedule-functions |
| 环境配置 | https://firebase.google.com/docs/functions/config-env |

### 2.3 关键概念(Firestore)

| 概念 | 说明 | 文档 |
|---|---|---|
| Document | 单条数据,最大 1 MiB | https://firebase.google.com/docs/firestore/manage-data/data-model |
| Collection | 文档集合 | 同上 |
| Subcollection | 嵌套集合 | https://firebase.google.com/docs/firestore/manage-data/structure-data |
| Query | 查询(支持 where / orderBy / limit)| https://firebase.google.com/docs/firestore/query-data/queries |
| Index | 复合索引(需手动配)| https://firebase.google.com/docs/firestore/query-data/index-overview |
| Transaction | 跨文档事务(最多 500 个文档)| https://firebase.google.com/docs/firestore/manage-data/transactions |
| Security Rules | 安全规则 | https://firebase.google.com/docs/firestore/security/get-started |
| Real-time Listener | 实时监听 | https://firebase.google.com/docs/firestore/query-data/listen |

## 三、移动端最佳实践

### 3.1 离线优先(Offline-first)

| 主题 | 文档 |
|---|---|
| Firestore 离线 | https://firebase.google.com/docs/firestore/manage-data/enable-offline |
| 本地缓存策略 | https://firebase.google.com/docs/firestore/manage-data/cache |
| 数据同步冲突 | https://firebase.google.com/docs/firestore/manage-data/add-data |

### 3.2 推送通知(FCM)

| 主题 | 文档 |
|---|---|
| FCM 总览 | https://firebase.google.com/docs/cloud-messaging/concept-options |
| iOS APNs 集成 | https://firebase.google.com/docs/cloud-messaging/ios/certs |
| Android 通知渠道 | https://firebase.google.com/docs/cloud-messaging/android/channels |
| 主题订阅 | https://firebase.google.com/docs/cloud-messaging/send-message#send_messages_to_topics |

### 3.3 App Store / Google Play 上架

| 主题 | URL |
|---|---|
| App Store 审核 | https://developer.apple.com/app-store/review/ |
| Google Play 政策 | https://support.google.com/googleplay/android-developer/answer/9888077 |
| 隐私政策要求 | https://developer.apple.com/app-store/app-privacy-details/ |
| 个人信息保护法 | http://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm |

## 四、安全与合规

### 4.1 Firebase 安全规则

| 主题 | URL |
|---|---|
| Rules 总览 | https://firebase.google.com/docs/rules |
| Firestore Rules | https://firebase.google.com/docs/firestore/security/get-started |
| Storage Rules | https://firebase.google.com/docs/storage/security/get-started |

### 4.2 隐私法规

| 法规 | 适用范围 | 文档 |
|---|---|---|
| GDPR(欧盟)| 海外用户 | https://gdpr-info.eu/ |
| CCPA(加州)| 加州用户 | https://oag.ca.gov/privacy/ccpa |
| PIPL(中国)| 中国用户 | http://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm |
| COPPA(儿童)| 13 岁以下 | https://www.ftc.gov/business-guidance/resources/complying-coppa-frequently-asked-questions |

## 五、监控与日志

| 工具 | 用途 | 文档 |
|---|---|---|
| Firebase Crashlytics | 崩溃监控 | https://firebase.google.com/docs/crashlytics |
| Firebase Performance | 性能监控 | https://firebase.google.com/docs/perf-mon |
| Firebase Analytics | 用户行为 | https://firebase.google.com/docs/analytics |
| Sentry | 错误追踪(可选)| https://docs.sentry.io/platforms/flutter/ |
| Google Cloud Logging | Cloud Functions 日志 | https://cloud.google.com/logging/docs |

## 六、CI/CD 与发布

| 工具 | 用途 | 文档 |
|---|---|---|
| Codemagic | Flutter CI/CD | https://docs.codemagic.io/ |
| Fastlane | iOS / Android 自动化 | https://docs.fastlane.tools/ |
| Firebase App Distribution | 内测分发 | https://firebase.google.com/docs/app-distribution |
| TestFlight | iOS 内测 | https://developer.apple.com/testflight/ |
| Google Play Internal Testing | Android 内测 | https://support.google.com/googleplay/android-developer/answer/9844674 |

## 七、测试工具

| 工具 | 用途 | 文档 |
|---|---|---|
| flutter_test | 单元测试 / Widget 测试 | https://docs.flutter.dev/testing |
| integration_test | 集成测试 | https://docs.flutter.dev/testing/integration-tests |
| mockito | Mock 框架 | https://pub.dev/packages/mockito |
| fake_cloud_firestore | Firestore 假实现 | https://pub.dev/packages/fake_cloud_firestore |
| patrol | E2E 测试 | https://patrol.leancode.co/ |

## 八、内部知识库(项目级)

### 8.1 项目设计文档

| 文档 | 用途 |
|---|---|
| `01-业务需求文档 BRD.md` | 业务需求 |
| `REVIEW_需求确认书.md` | AI 理解确认 |
| `REVIEW_字段对齐分析.md` | 字段映射(Firestore)|
| `业务流程图-积分获取.txt` | 主流程 |
| `业务流程图-积分状态流转.txt` | 状态机 |

### 8.2 知识库目录约定

```
/root/analysis-to-delivery/
├── examples/
│   ├── 01-wms-warehouse/         # Oracle + Spring Boot + Vue
│   ├── 02-saas-dashboard/        # PostgreSQL + Express + React
│   └── 03-mobile-app/            # Firestore + Flutter(本项目)
│       ├── knowledge-path.md     # 本文件
│       ├── tech-stack-path.md
│       └── ...
└── skills/                        # 26 个 skill
```

## 九、与 WMS / SaaS 示例的知识库对比

| 维度 | WMS | SaaS | App(本项目) |
|---|---|---|---|
| 数据库 | Oracle 文档 | PG 文档 | Firestore 文档 |
| 后端 | Spring Boot | Express | Cloud Functions |
| 前端 | Vue 3 | React 19 | Flutter |
| 状态管理 | Pinia | TanStack Query | Riverpod |
| 推送 | 不涉及 | 不涉及 | FCM(本项目核心) |
| 离线 | 不涉及 | 不涉及 | 必备(本项目核心) |
| 实时 | 异步队列 | 异步队列 | Firestore listener |
| 字符分隔 | `\|\|` | `\|\|` | 不适用 |
| 整数除法 | `1.0/3` | `1.0/3` | 不适用 |

## 十、关键注意事项

1. **Firestore 文档 1 MiB 限制** — 大字段存 Storage,文档存引用
2. **Firestore 单文档事务原子** — 跨文档事务限制 500,需业务侧合并
3. **Firestore 复合索引** — 排序 / 范围查询必须配索引
4. **FCM 推送 iOS 需 APNs 证书** — Android 自动,生产环境需配 .p8 key
5. **Flutter Offline 缓存** — 默认 40 MiB,大数据集需手动配置
6. **Dart 强类型** — 无 1.0/3 问题,但 number 是 double,积分用 int
7. **Firestore 安全规则必须配** — 客户端不能绕过 Admin SDK
8. **PIPL 合规** — 收集个人信息需用户同意 + 隐私政策

## 十一、ADR(架构决策记录)索引

| ADR | 决策 | 引用 |
|---|---|---|
| ADR-001 | 选 Flutter 3.24 | `tech-stack-path.md` §2.1 |
| ADR-002 | 选 Riverpod 状态管理 | `tech-stack-path.md` §2.1 |
| ADR-003 | Firestore + 本地缓存 | `tech-stack-path.md` §二 |
| ADR-004 | FCM 推送 | `tech-stack-path.md` §2.2 |
| ADR-005 | 积分 FIFO 批次 | `REVIEW_字段对齐分析.md` §三 |
| ADR-006 | 离线优先架构 | `01-业务需求文档 BRD.md` §6.3 |