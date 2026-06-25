# Example 3: 移动 App — 会员积分管理

> 蒸馏示例:跨平台移动 App(Flutter + Firebase)的"会员积分管理"模块。
> 演示 analysis-to-delivery skill 在移动端 / BaaS 场景的用法。

## 场景

- **类型**:B2C 移动 App(零售品牌会员)
- **技术栈**:Flutter 3.24 (Dart 3.5) + Firebase(Auth / Firestore / Functions / Storage / FCM / Analytics)
- **平台**:iOS 17+ / Android 14+
- **模块**:会员积分管理(获取 / 兑换 / 过期 / 推送)
- **合规**:轻度 — `config/compliance/none.md` + 自检《个人信息保护法》(PIPL)
- **特殊点**:实时同步(Firestore 实时监听)+ 离线优先(Offline-first)

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
| `TASK_CONFIRM_会员积分.md` | `/grill-task` §1 | 1 |
| `REVIEW_需求确认书.md` | `/grill-task` §2 | 1 |
| `REVIEW_字段对齐分析.md` | `/grill-task` §3 | 1.3 |
| `01-业务需求文档 BRD.md` | `/to-brd` | 2 |
| `业务流程图-积分获取.txt` | `/to-brd` §3 | 2 |
| `业务流程图-积分状态流转.txt` | `/to-brd` §3 | 2 |
| `knowledge-path.md` | `/setup-analysis-delivery` | 0 |
| `tech-stack-path.md` | `/setup-analysis-delivery` | 0 |
| `compliance-path.md` | `/setup-analysis-delivery` | 0 |
| `doc-naming.md` | `/setup-analysis-delivery` | 0 |
| `config-used.md` | 配置使用记录 / ADR | 1 |

## 与其他示例的差异

| 维度 | 01-wms-warehouse | 02-saas-dashboard | 03-mobile-app |
|---|---|---|---|
| 数据库 | Oracle | PostgreSQL | Cloud Firestore(NoSQL) |
| 后端 | Spring Boot | Express 5 | Firebase + Cloud Functions |
| 前端 | Vue 3 PC | React 19 Web | Flutter 3.24(原生编译) |
| 移动端 | uni-app 巴枪 | 响应式 Web | Flutter iOS + Android |
| 状态机 | 2 位码 | 字符串枚举 | Firestore 状态字段 |
| 合规 | GSP | None | PIPL 轻度 |
| 多租户 | 单租户 | 多租户(行级)| 单租户 + 用户维度 |
| 实时性 | 异步队列 | T+1 | 实时(Firestore listener) |
| 离线 | 不涉及 | 不涉及 | 必须(Offline-first) |
| 推送 | 不涉及 | 不涉及 | FCM 推送 |
| 字符分隔 | `\|\|` | `\|\|` | 不适用(NoSQL) |
| 审计字段 | 五件套 | 五件套 | Firestore 字段子集 |
| 文档编号 | 01-09 | 01-09 | 01-09 |

## Firestore 关键差异(NoSQL vs SQL)

| 维度 | SQL(Oracle/PG)| NoSQL(Firestore) |
|---|---|---|
| 表/集合 | TABLE | Collection |
| 行/文档 | ROW | Document |
| 字段类型 | 强类型(SCHEMA)| 弱类型(Map) |
| 关联查询 | JOIN | 不支持(需反范式)|
| 事务 | ACID | 限制(单文档原子,跨文档有限)|
| 索引 | B-Tree / 部分索引 | Composite Index(需手动配)|
| 全文搜索 | 需扩展 | 需 Algolia / Typesense |
| 排序 | `ORDER BY` | `orderBy`(需索引)|
| 聚合 | `GROUP BY` | 需 Cloud Functions 聚合 |
| 数据规模 | TB 级 | 单文档 1MB / 集合无限制 |

## 运行演示

```bash
# 1. 装 skill
npx skills@latest add <your-repo>

# 2. 在本目录调 skill
cd examples/03-mobile-app
/ask-delivery

# 3. 选 "走完整 9 阶段" → 看 skill 如何在移动端 / BaaS 场景跑通
```

## 不演示的

- 实际 Dart 代码(本示例只演示文档输出,不含 Flutter / Cloud Functions 代码)
- UI 设计稿(留给设计师 / Figma)
- 测试用例 / PRD(留给用户用 `/test-case-design` `/to-prd` 生成)

## 下一步

用户拿到本示例后,推荐:
1. 跑 `/to-fsd` (或 `/dev-design`)生成完整技术设计
2. 跑 `/using-superpowers` → `/brainstorming` → `/writing-plans` 出实施计划
3. 跑 `/tdd` + `/executing-plans` 写 Flutter 代码