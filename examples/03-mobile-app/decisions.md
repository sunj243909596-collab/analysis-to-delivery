# Decisions（ADR / 决策记录）— 移动 App 会员积分管理(v3.1.0)

> 项目:移动 App — 会员积分管理
> 版本:v3.1.0(2026-07,阶段 4-7 文档补齐;v3.1.0 起从 `config-used.md` 改名为 decisions.md)
> 文件身份:ADR / 决策记录,由 `/setup-analysis-delivery` 阶段 1 可选生成
> 注意:本文件不参与配置加载,配置加载只读取 4 个 `*-path.md`
> 用途:汇总本项目引用的全部配置路径 + 关键技术决策,便于审计与回溯

## 一、配置清单

| 配置项 | 路径 | 用途 |
|---|---|---|
| 合规 | `config/compliance/none.md` | 基础无合规(项目叠加 PIPL 自检) |
| 知识库 | `knowledge-path.md`(本目录)| Flutter + Firebase |
| 技术栈 | `tech-stack-path.md`(本目录)| Flutter 3.24 + Firebase |
| 合规 | `compliance-path.md`(本目录)| PIPL 自检清单 |
| 文档命名 | `doc-naming.md`(本目录)| 01-09 编号 |
| 配置使用记录 / ADR | `decisions.md`(本文件)| 不参与配置加载 |

## 二、与全局默认的差异

| 配置项 | 全局默认 | 本项目 | 差异 |
|---|---|---|---|
| 合规等级 | none | none + PIPL | **差异**:PIPL 自检 |
| 数据库方言 | Oracle | Firestore(NoSQL)| **重大差异** |
| 状态码 | 2 位数字 | 字符串枚举 | **差异**:`draft`/`submitted`/`paid` |
| 前端框架 | Vue 3 + Element Plus | Flutter 3.24 | **重大差异**:跨平台移动 |
| 后端框架 | Spring Boot + MyBatis-Plus | Cloud Functions(Node.js 20)| **重大差异** |
| 鉴权 | Spring Security + JWT | Firebase Auth | **差异**:BaaS |
| 主键策略 | SEQUENCE | Firestore Document ID(UUID)| **差异** |
| 多租户 | 单租户 | 单租户(用户维度)| 一致 |
| 字符分隔 | `\|\|` | 不适用 | **差异**:NoSQL |
| 整数除法 | `1.0/3` 必须 | 不适用(Dart 强类型)| **差异** |
| 审计字段 | 五件套 | 子集(4 件:`createdAt` / `updatedAt` / `createdBy` / `version`)| **差异** |
| 文档编号 | 01-09 | 01-09(省略 02/04/08/09)| 一致(SaaS 模式)|
| 实时性 | 异步队列 | 实时(Firestore listener)| **重大差异** |
| 离线 | 不涉及 | 必须 | **重大差异** |
| 推送 | 不涉及 | FCM 推送 | **重大差异** |

## 三、关键决策记录

### 3.1 为什么选 Flutter?

**背景**:B2C 移动 App 需同时支持 iOS + Android,团队规模小(2-3 人)。

**选项**:
- ✅ **Flutter 3.24**(本项目选)
- ❌ React Native:桥接性能损耗大,Firebase 集成复杂
- ❌ 原生(iOS + Android 双团队):成本翻倍,人不够
- ❌ uni-app:Vue 生态,跨端能力弱

**理由**:
- ✅ 跨平台性能接近原生(Skia 自渲染)
- ✅ Dart 强类型 + 空安全
- ✅ hot reload,开发效率高
- ✅ 单一代码库
- ✅ Firebase 集成完善(FlutterFire)
- ✅ 团队有 Dart 经验

### 3.2 为什么选 Firestore 而非 Realtime Database?

**选项**:
- ✅ **Cloud Firestore**(本项目选)
- ❌ Realtime Database:JSON 树,查询能力弱,无离线

**理由**:
- ✅ 文档模型,类 SQL 查询
- ✅ 复合索引,排序高效
- ✅ 离线支持完善
- ✅ 与 Cloud Functions 集成
- ✅ 安全规则强大
- ✅ 自动扩缩容

### 3.3 为什么 FIFO 批次消耗?

**背景**:积分有过期规则(2 年),如果不按过期顺序消耗,用户利益受损(过期积分长期占用)。

**选项**:
- ✅ **FIFO 批次消耗**(本项目选)
- ❌ LIFO 批次消耗:对用户不利
- ❌ 全局池:无法追溯,无法精确过期

**理由**:
- ✅ 用户利益最大化
- ✅ 财务清晰
- ✅ 过期处理精确

**复杂度成本**:
- ❌ 每次消耗需查最早过期批次
- ❌ 批次拆分的边界处理
- 缓解:封装 `PointsBatchService`,单测覆盖

### 3.4 为什么积分变动走 Cloud Functions?

**选项**:
- ✅ **钱包只能 Cloud Functions 写**(本项目选)
- ❌ 客户端直接写 Firestore:无业务逻辑

**理由**:
- ✅ 安全性(客户端不能绕过)
- ✅ 数据一致性(集中处理)
- ✅ 业务逻辑集中
- ✅ 流水必写(强制约束)
- ❌ 增加延迟(网络调用)

### 3.5 为什么离线优先?

**选项**:
- ✅ **关键路径支持离线**(本项目选)
- ❌ 完全在线:差

**理由**:
- ✅ 弱网环境可用(地铁 / 电梯)
- ✅ 减少等待感
- ✅ 用户体验好
- ❌ 冲突处理复杂

**离线范围**:
- ✅ 签到(本地缓存 + 网络恢复同步)
- ✅ 查看积分明细(本地缓存)
- ❌ 兑换(必须联网)
- ❌ 兑换核销(必须联网)

### 3.6 为什么 Riverpod?

**选项**:
- ✅ **Riverpod 2**(本项目选)
- ❌ Provider:无类型安全,BuildContext 依赖
- ❌ Bloc:样板代码多

**理由**:
- ✅ 类型安全
- ✅ 无 BuildContext 依赖(易测试)
- ✅ lazy + auto dispose
- ✅ 组合性优秀

## 四、配置继承关系

```
全局默认(config/)
├── compliance/
│   ├── gsp.md
│   └── none.md ←【本项目基础】
├── db-dialect/
│   ├── oracle.md
│   ├── postgresql.md
│   └── firestore.md ←【本项目使用】
└── ...

项目级(本目录)
├── compliance-path.md ← 引用 none.md + PIPL 自检
├── knowledge-path.md ← 引用 Flutter + Firebase 文档
├── tech-stack-path.md ← 引用 Flutter 3.24 + Firebase
├── doc-naming.md ← 引用全局 01-09 规则
└── decisions.md ←【ADR 记录,不参与配置加载】
```

## 五、回溯与审计

| 场景 | 查阅路径 |
|---|---|
| 为什么用 Flutter? | `tech-stack-path.md` §2.1 + `decisions.md` §3.1 |
| 为什么 Firestore? | `tech-stack-path.md` §二 + `decisions.md` §3.2 |
| 为什么 FIFO 批次? | `REVIEW_字段对齐分析.md` §三 + `decisions.md` §3.3 |
| 合规要求? | `compliance-path.md` §一-五 |
| 状态机定义? | `01-业务需求文档 BRD.md` §3.2 + `业务流程图-积分状态流转.txt` |
| 字段映射? | `REVIEW_字段对齐分析.md` |
| 文档编号规则? | `doc-naming.md` §一 |
| 离线范围? | `01-业务需求文档 BRD.md` §4.7 + `decisions.md` §3.5 |
| 推送策略? | `tech-stack-path.md` §2.2 + `knowledge-path.md` §3.2 |

## 六、与 WMS / SaaS 示例的配置差异(对比)

| 维度 | WMS | SaaS | App(本项目) | 备注 |
|---|---|---|---|---|
| 合规 | GSP | None | None + PIPL | 本项目轻度 |
| 数据库 | Oracle | PostgreSQL | Firestore | NoSQL |
| 后端 | Spring Boot | Express | Cloud Functions | FaaS |
| 前端 | Vue 3 | React 19 | Flutter 3.24 | 跨平台 |
| 移动端 | uni-app 巴枪 | 无 | Flutter iOS+Android | 双端 |
| 状态码 | 2 位数字 | 字符串 | 字符串 | 都一致 |
| 多租户 | 单租户 | 多租户 | 单租户 | 一致 |
| 实时性 | 异步队列 | T+1 | 实时(listener) | App 最佳 |
| 离线 | 不涉及 | 不涉及 | 必备 | App 必需 |
| 推送 | 不涉及 | 不涉及 | FCM | App 必需 |
| 字符分隔 | `\|\|` | `\|\|` | 不适用 | NoSQL |
| 整数除法 | `1.0/3` | `1.0/3` | 不适用 | 强类型 |
| 审计字段 | 五件套 | 五件套 | 子集(4 件)| Firestore 简化 |
| 文档编号 | 01-09 全 | 01-09 省 02/04/08/09 | 01-09 省 02/04/08/09 | 一致 |

## 七、配置变更流程

1. **小变更**(版本号、依赖升级)
   - 直接修改 `*.path.md` 文件
   - 在 `## 变更记录` 中追加
   - 提交 Git,无需审批

2. **中变更**(技术选型调整)
   - 评估影响范围
   - 更新 `*-path.md`,并在 `decisions.md` 追加 ADR
   - 提交 Git,需团队 review

3. **大变更**(合规、数据库切换)
   - 走 `/grill-task` 重新审视
   - 更新所有相关 `*.path.md` + BRD
   - 走 `/dev-design` 重新设计
   - 必须团队 review + 业务方确认

## 八、变更记录

| 日期 | 变更 | 原因 |
|---|---|---|
| 2026-06-22 | 初版配置 | 项目立项,确定移动 App 技术栈 |
| 2026-07-02 | v3.1.0 升级:新增 04/05/07 三文档 + PIPL/App Store/Google Play 合规清单 | 跟随 skill v3.1.0 阶段 4-7 补齐;涉及中国用户 + App 上架,需补合规 |

## v3.1.0 升级说明

本示例从 v3.0.1 升级到 v3.1.0,新增/升级了以下产物：

### 新增产物

| 文件 | 对应 skill | 阶段 | 说明 |
|---|---|---|---|
| [`04-合规评审.md`](./04-合规评审.md) | `/compliance-review` | 4 | PIPL/App Store/Google Play 10 条款合规性分析（严重 3 + 主要 5 + 一般 2）|
| [`05-产品需求文档 PRD.md`](./05-产品需求文档 PRD.md) | `/to-prd` | 6 | 8 节齐全 + §七 验收标准白名单签字 |
| [`07-测试用例设计.md`](./07-测试用例设计.md) | `/test-case-design` | 5 | 5 大类用例 47 条 + PIPL/App Store/Google Play 合规校验 + 离线签到 |

### 配套验证脚本

```bash
# 阶段 3→4 门控
python3 scripts/brd-check.py --strict examples/03-mobile-app/

# 阶段 4→5 门控
python3 scripts/compliance-check.py --strict examples/03-mobile-app/

# 阶段 5→6 门控
python3 scripts/testcase-coverage-check.py --strict examples/03-mobile-app/

# 阶段 6→7 门控
python3 scripts/prd-check.py --strict examples/03-mobile-app/
```

### 与 v3.0.1 的差异

| 维度 | v3.0.1 | v3.1.0 |
|---|---|---|
| 覆盖阶段 | 1-3 | 1-9（含 4-7） |
| 文档数 | 7 | 10（+3） |
| 合规评审 | ❌ 无 | ✅ PIPL/App Store/Google Play 10 条款全过 |
| PRD | ❌ 无 | ✅ 8 节齐 + §七 签字 |
| 测试用例 | ❌ 无 | ✅ 5 大类 47 条 |
| 自动化门控 | 2 个（setup + task-confirm） | 6 个（+brd/compliance/testcase/prd） |

### 已知未补全

- 阶段 7-8（`/dev-design` 6 大文档：FSD/数据模型/开发设计/回测/复盘/交接）— 留待后续升级
- 阶段 9（`/qa-audit` 全量 QA 审计）— 留待后续升级

### 已知 NoSQL 特有事项

- 字段映射不复用 SQL 工具链;Firestore 字段类型已在 PRD §三.1.4 + §五.2 标注
- 流程图用 ASCII + 可选 Mermaid(本目录含 `业务流程图-积分状态流转.mmd`)
- 集成测试用 `firebase_emulator_suite` 而非 Testcontainers
