# 文档命名规范(移动 App — 会员积分管理)

> 项目:移动 App — 会员积分管理
> 路径配置:本文档被 `/setup-analysis-delivery` 阶段 1 引用
> 用途:定义项目文档的编号 / 命名 / 目录结构

## 一、编号规则(01-09 强制)

| 编号 | 文档类型 | skill 入口 | 说明 |
|---|---|---|---|
| 01 | 业务需求文档 BRD | `/to-brd` | Business Requirements Document |
| 02 | 功能规格说明书 FSD | `/to-fsd`(可选)| Functional Specification Document |
| 03 | 数据模型设计 | `/dev-design` §8.2 | Firestore 集合结构 / 安全规则 |
| 04 | 合规检查清单 | `/compliance-review` | PIPL / GDPR 等 |
| 05 | 产品需求文档 PRD | `/to-prd` | Product Requirements Document |
| 06 | 开发设计说明书 | `/dev-design` | 包含数据模型 + API + 状态机 |
| 07 | 测试用例 | `/test-case-design` | Test Cases |
| 08 | 设计回测报告 | `/dev-design` | Design Backtest Report |
| 09 | QA 审计报告 | `/qa-audit` | QA Audit Report |

> ⚠️ **移动 App 项目可省略 02(FSD)**,BRD 直接到 PRD。
> ⚠️ 04(合规检查清单)轻度项目可省略,本项目 PIPL 自检清单在 `compliance-path.md`。

## 二、文件命名格式

### 2.1 标准格式

```
{编号}-{文档类型}{[空格]文档名}.md
```

### 2.2 命名示例(本项目,移动 App 场景)

| 实际文件名 | 类型 | 阶段 |
|---|---|---|
| `01-业务需求文档 BRD.md` | BRD | 阶段 3 |
| `03-数据模型设计.md` | 数据模型(Firestore)| 阶段 7(待生成)|
| `05-产品需求文档 PRD.md` | PRD | 阶段 6(待生成)|
| `06-开发设计说明书.md` | 开发设计 | 阶段 7(待生成)|
| `07-测试用例.md` | 测试用例 | 阶段 5(待生成)|
| `08-设计回测报告.md` | 设计回测 | 阶段 7(待生成)|
| `09-QA 审计报告.md` | QA 审计 | 阶段 8(待生成)|
| `REVIEW_需求确认书.md` | 阶段 2 确认 | 阶段 2 |
| `REVIEW_字段对齐分析.md` | 阶段 2 字段对齐 | 阶段 2 |
| `TASK_CONFIRM_会员积分.md` | 阶段 2 任务确认 | 阶段 2 |
| `业务流程图-积分获取.txt` | 业务图 | 阶段 2 |
| `业务流程图-积分状态流转.txt` | 业务图 | 阶段 2 |
| `knowledge-path.md` | 阶段 1 配置 | 阶段 1 |
| `tech-stack-path.md` | 阶段 1 配置 | 阶段 1 |
| `compliance-path.md` | 阶段 1 配置 | 阶段 1 |
| `doc-naming.md` | 阶段 1 配置(本文件)| 阶段 1 |
| `decisions.md` | 配置使用记录 / ADR | 阶段 1 |
| `README.md` | 项目说明 | 顶层 |

## 三、目录结构

```
examples/03-mobile-app/
├── README.md                          # 项目说明
├── TASK_CONFIRM_会员积分.md           # 阶段 2
├── REVIEW_需求确认书.md               # 阶段 2
├── REVIEW_字段对齐分析.md             # 阶段 2
├── 01-业务需求文档 BRD.md             # 阶段 3
├── 业务流程图-积分获取.txt            # 阶段 3
├── 业务流程图-积分状态流转.txt        # 阶段 3
├── knowledge-path.md                  # 阶段 1
├── tech-stack-path.md                 # 阶段 1
├── compliance-path.md                 # 阶段 1
├── doc-naming.md                      # 阶段 1(本文件)
├── decisions.md                     # 阶段 1 ADR 记录
├── 03-数据模型设计.md                 # 阶段 7(待生成)
├── 05-产品需求文档 PRD.md             # 阶段 6(待生成)
├── 06-开发设计说明书.md               # 阶段 7(待生成)
├── 07-测试用例.md                     # 阶段 5(待生成)
├── 08-设计回测报告.md                  # 阶段 7(待生成)
└── 09-QA 审计报告.md                  # 阶段 8(待生成)
```

## 四、命名禁区

| 禁用 | 原因 |
|---|---|
| 中文标点符号 | 跨平台兼容性,shell 友好 |
| 文件名中空格(用 `-` 替代)| shell 友好 |
| 大写扩展名(`.MD`)| 跨平台一致性 |
| `tmp` / `draft` / `final` 后缀 | 易混乱,改用 Git |
| 特殊字符(`!@#$%^&*`)| 编码问题 |
| 双重后缀(`.md.bak`)| 易混乱 |
| 中文数字序号(`第1版`)| 一致性差,用阿拉伯数字 |

## 五、版本管理

- 文档**不**在文件名加版本号,版本通过 Git 管理
- 重大变更在 `CHANGELOG.md` 中记录
- 草稿用 `.draft.md` 后缀,正式版删除后缀
- 同一文档的历史版本通过 `git log` 查看

## 六、跨项目一致性

| 维度 | WMS(01)| SaaS(02)| App(03)| 一致性 |
|---|---|---|---|---|
| 编号 01-09 | ✅ | ✅ | ✅ | **一致** |
| REVIEW_ 前缀 | ✅ | ✅ | ✅ | **一致** |
| 业务流程图-*.txt | ✅ | ✅ | ✅ | **一致** |
| 4 个项目级配置 + config-used ADR | ✅ | ✅ | ✅ | **一致** |
| 状态机图 | 必需 | 必需 | 必需 | **一致** |
| ASCII 流程图 | ✅ | ✅ | ✅ | **一致** |
| 状态码风格 | 2 位数字 | 字符串枚举 | 字符串枚举 | WMS 特殊 |
| 数据库方言 | Oracle | PostgreSQL | Firestore | 项目特性 |
| 文档语言 | 中文 | 中文 | 中文 | **一致** |
| Markdown 风格 | GFM | GFM | GFM | **一致** |

## 七、Markdown 风格规范

### 7.1 标题

```markdown
# 一级标题(文档标题,一个文件一个)
## 二级标题(章节)
### 三级标题(小节)
#### 四级标题(子小节)
```

### 7.2 表格

必须对齐(对齐 markdown 渲染):

```markdown
| 列1 | 列2 | 列3 |
|---|---|---|
| 内容 | 内容 | 内容 |
```

### 7.3 代码块

必须标注语言:

````markdown
```typescript
const x = 1;
```

```dart
final points = 100;
```

```bash
flutter pub get
```
````

### 7.4 强调

- 关键词用 **粗体**
- 代码片段 / 文件名用 `行内代码`
- 重要警示用 ⚠️ / ❌ / ✅
- 不使用斜体(可读性差)

## 八、文档生成顺序

按 skill 阶段顺序:

```
1. setup-analysis-delivery  → 4 个项目级配置 + README;可选 config-used ADR
2. grill-task              → TASK_CONFIRM + REVIEW_需求确认书 + REVIEW_字段对齐分析
3. to-brd                 → 01-BRD + 业务流程图-*.txt
4. compliance-review      → 04-合规评审(按需)
5. test-case-design       → 07-测试用例
6. to-prd                 → 05-PRD
7. dev-design             → 02/03/06/08 开发设计产物
8. qa-audit               → 09-QA 审计报告
9. handoff                → 交付清单
```

## 九、与 WMS / SaaS 示例的命名差异

| 文件类型 | WMS 命名 | SaaS 命名 | App 命名 | 说明 |
|---|---|---|---|---|
| BRD | `01-业务需求文档 BRD.md` | `01-业务需求文档 BRD.md` | `01-业务需求文档 BRD.md` | 一致 |
| FSD | `02-功能规格说明书 FSD.md` | (省略)| (省略)| 移动 App 简化为 BRD→PRD |
| 数据模型 | `03-数据模型设计.md` | `03-数据模型设计.md` | `03-数据模型设计.md` | 一致 |
| 合规 | `04-GSP合规检查清单.md` | (省略)| (省略)| 移动 App PIPL 轻度 |
| PRD | `05-产品需求文档 PRD.md` | `05-产品需求文档 PRD.md` | `05-产品需求文档 PRD.md` | 一致 |
| 开发设计 | `06-开发设计说明书.md` | `06-开发设计说明书.md` | `06-开发设计说明书.md` | 一致 |
| 测试用例 | `07-测试用例.md` | `07-测试用例.md` | `07-测试用例.md` | 一致 |
| 设计回测 | `08-设计回测报告.md` | `08-设计回测报告.md` | `08-设计回测报告.md` | 一致 |
| QA 审计 | `09-QA 审计报告.md` | `09-QA 审计报告.md` | `09-QA 审计报告.md` | 一致 |

## 十、变更记录

| 日期 | 变更 | 原因 |
|---|---|---|
| 2026-06-22 | 初版 | 项目立项,确定 01-09 编号 |
