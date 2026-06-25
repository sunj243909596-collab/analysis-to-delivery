# 贡献指南(Contributing Guide)

> 感谢你有兴趣为 **analysis-to-delivery** skill 集合做贡献!
> 本文档面向所有贡献者(开发 / 文档 / 测试 / 设计 / Issue 报告者)。

## 一、行为准则

### 1.1 我们的承诺

为了营造一个开放和友好的环境,我们承诺:无论年龄、体型、残疾、种族、性别认同、经验水平、国籍、性别外表、种族、宗教或性取向如何,所有贡献者和维护者参与本项目的体验都是无骚扰的。

### 1.2 我们的标准

**积极行为**:
- ✅ 使用欢迎和包容的语言
- ✅ 尊重不同的观点和经验
- ✅ 优雅地接受建设性批评
- ✅ 关注对社区最有利的事情
- ✅ 对其他社区成员表示同理心

**不可接受的行为**:
- ❌ 使用性别化语言或图像,以及对性暗示的不必要的关注
- ❌ 挑衅、侮辱/贬低的评论,以及人身或政治攻击
- ❌ 公开或私下骚扰
- ❌ 未经明确许可,发布他人的私人信息(如地址或电子邮箱)
- ❌ 其他可合理视为不当的职业行为

## 二、我能贡献什么?

### 2.1 报告 Bug 🐛

发现 skill 输出有误?字段映射错误?文档不清晰?

→ 请开 [Issue](../issues/new?template=bug_report.md)

### 2.2 提出新功能 ✨

需要新的 skill?现有 skill 需要扩展?

→ 请开 [Feature Request](../issues/new?template=feature_request.md)

### 2.3 改进现有文档 📝

发现错别字 / 表述不清 / 示例过时?

→ 直接提交 PR(参见下文"开发流程")

### 2.4 贡献新示例 📚

希望为新的业务场景(B2B 电商 / 物流 / 医疗 SaaS / 工业 IoT 等)贡献示例?

→ 参见 [examples/ 目录结构](#五examples-目录约定) + 提 PR

### 2.5 完善脚本 🛠️

改进 `scripts/` 下的验证脚本(smoke-test / sql-dialect-check 等)?

→ 直接提 PR,需附测试用例

### 2.6 完善 CI ⚙️

改进 `.github/workflows/`?

→ 直接提 PR,需在 fork 仓库验证通过

## 三、开发流程

### 3.1 Fork & Clone

```bash
# 1. 在 GitHub 上 Fork 本仓库
# 2. Clone 你的 fork
git clone git@github.com:<your-username>/analysis-to-delivery.git
cd analysis-to-delivery

# 3. 添加 upstream 远程
git remote add upstream git@github.com:BlueprintOS/analysis-to-delivery.git

# 4. 验证
git remote -v
```

### 3.2 创建分支

```bash
# 从 main 拉最新
git fetch upstream
git checkout main
git rebase upstream/main

# 创建特性分支(命名规范见下文)
git checkout -b feat/<skill-name>-<short-desc>
# 或
git checkout -b fix/<issue-number>-<short-desc>
# 或
git checkout -b docs/<doc-name>-<short-desc>
# 或
git checkout -b example/<scenario-name>
```

#### 分支命名规范

| 前缀 | 用途 | 示例 |
|---|---|---|
| `feat/` | 新功能 / 新 skill | `feat/add-devops-skill` |
| `fix/` | 修复 bug | `fix/smoke-test-fail-count` |
| `docs/` | 文档改进 | `docs/clarify-brd-template` |
| `refactor/` | 重构(不改行为)| `refactor/split-monolith-skill` |
| `example/` | 新增示例 | `example/b2b-ecommerce` |
| `ci/` | CI / 脚本改进 | `ci/add-pr-validation` |

### 3.3 提交规范(Conventional Commits)

**格式**:`<type>(<scope>): <subject>`

**Type 类型**:
| Type | 说明 | 示例 |
|---|---|---|
| `feat` | 新功能 | `feat(skill): add dev-design 数据模型` |
| `fix` | 修复 | `fix(smoke-test): 修正 skill 计数错误` |
| `docs` | 文档 | `docs(README): 补充 examples 02/03 说明` |
| `refactor` | 重构 | `refactor(skill): 拆分为 26 个独立 skill` |
| `example` | 新示例 | `example(saas-dashboard): 新增 SaaS 订单管理示例` |
| `ci` | CI / 脚本 | `ci(workflows): 添加 full-qa-audit` |
| `test` | 测试 | `test(smoke-test): 补充边界场景测试` |
| `chore` | 杂项 | `chore: 更新 .gitignore` |

**Scope 范围**(可选):
- `skill` - skill 本身
- `examples/01-wms-warehouse`
- `examples/02-saas-dashboard`
- `examples/03-mobile-app`
- `scripts`
- `workflows`
- `docs`

**Subject 主语**:
- 简短(≤ 72 字符)
- 中文 / 英文均可(团队约定)
- 动词开头
- 首字母小写(英文)
- 末尾无句号

**示例**:
```bash
git commit -m "feat(skill): 新增 dev-design 数据模型设计"
git commit -m "fix(smoke-test): 修正 skill 计数期望值"
git commit -m "docs(README): 补充 examples 02 SaaS 场景说明"
git commit -m "refactor(skill): 拆分为 26 个独立 skill (mattpocock 风格)"
git commit -m "example(saas-dashboard): 新增 12 个 SaaS 订单管理示例文档"
git commit -m "ci(workflows): 添加 full-qa-audit 5 个 workflow"
```

### 3.4 推送 & 提 PR

```bash
# 1. 推送到你的 fork
git push origin feat/<branch-name>

# 2. 在 GitHub 上创建 Pull Request
#    目标: BlueprintOS/analysis-to-delivery:main
#    模板: .github/PULL_REQUEST_TEMPLATE.md
```

### 3.5 PR 验收标准

合并前必须满足:

| 标准 | 必需 |
|---|---|
| CI 全绿(smoke + dialect + doc + field + qa)| ✅ |
| 至少 1 位维护者 approve | ✅ |
| 与最新 main 无冲突 | ✅ |
| 描述清晰(用了 PR 模板)| ✅ |
| 改动与 title 一致(无夹带)| ✅ |
| 文档同步(代码改了,文档也改)| ✅ |
| 无遗留调试代码 / TODO 注释 | ✅ |

### 3.6 Review 周期

- **首次 review**:48 小时内
- **后续迭代**:24 小时内
- **超时无响应**:在 PR 下 @ 维护者

## 四、本地验证(开发必跑)

> ⚠️ **铁律**:提 PR 前必须在本地跑通所有验证!

### 4.1 必跑命令

```bash
# 1. Skill 集合结构
bash scripts/smoke-test.sh

# 2. SQL 方言
python3 scripts/sql-dialect-check.py "examples/**/*.md"

# 3. 文档格式
python3 scripts/doc-validate.py "examples/**/*.md"
python3 scripts/doc-validate.py "skills/**/*.md"

# 4. 字段对齐
python3 scripts/field-alignment-check.py "examples/**/*.md"

# 5. 全量 QA
python3 scripts/full-qa-audit.py "examples/**/*.md"
```

### 4.2 全量快速验证(推荐)

```bash
# 一键运行所有验证
bash scripts/smoke-test.sh && \
python3 scripts/sql-dialect-check.py "examples/**/*.md" && \
python3 scripts/doc-validate.py "examples/**/*.md" && \
python3 scripts/doc-validate.py "skills/**/*.md" && \
python3 scripts/field-alignment-check.py "examples/**/*.md" && \
python3 scripts/full-qa-audit.py "examples/**/*.md" && \
echo "✅ 全部验证通过"
```

### 4.3 修复迭代规则

1. **首次失败**:读错误输出 → 定位文件/行号 → 修复 → 重跑
2. **二次失败**:扩大搜索范围,检查关联文件 → 修复 → 重跑
3. **三次失败**:停止自动修复,输出完整错误报告 + 修复建议,等用户决策

## 五、examples/ 目录约定

### 5.1 命名规范

```
examples/
├── NN-<scenario-slug>/
```

| 示例 | 说明 |
|---|---|
| `01-wms-warehouse/` | 序号 + 业务场景(英文短词)|
| `02-saas-dashboard/` | 序号 + 业务场景 |
| `03-mobile-app/` | 序号 + 业务场景 |

### 5.2 必含文件(12 个起步)

```
examples/NN-<scenario>/
├── README.md                          # 必含:场景 + skill 链 + 差异对比
├── TASK_CONFIRM_<topic>.md            # 阶段 2 任务确认
├── REVIEW_需求确认书.md               # 阶段 2 AI 理解
├── REVIEW_字段对齐分析.md             # 阶段 2 字段对齐
├── 01-业务需求文档 BRD.md             # 阶段 3 BRD
├── 业务流程图-<topic1>.txt            # 阶段 3 业务流程
├── 业务流程图-<topic2>.txt            # 阶段 3 状态流转
├── knowledge-path.md                  # 阶段 1 知识库
├── tech-stack-path.md                 # 阶段 1 技术栈
├── compliance-path.md                 # 阶段 1 合规
├── doc-naming.md                      # 阶段 1 文档命名
└── config-used.md                     # 阶段 1 ADR 记录
```

### 5.3 新增示例的检查清单

- [ ] 12 个文件齐全
- [ ] README.md 中有"与其他示例的差异"对比表
- [ ] 业务流程图用 ASCII(不用 Mermaid / 图片)
- [ ] 状态机图用 ASCII + 转换矩阵
- [ ] 字段映射明确(数据库方言标注)
- [ ] 合规等级明确(GSP / None / 等)
- [ ] 与全局配置(`config/` 目录)的差异有说明
- [ ] 本地所有验证脚本通过

## 六、skills/ 目录约定

### 6.1 新增 skill 的检查清单

- [ ] 路径:`skills/<skill-name>/SKILL.md`
- [ ] frontmatter 合法(`name` / `description`)
- [ ] 描述简洁(≤ 200 字符)
- [ ] 主体内容(命令 / 触发场景 / 输出模板 / 注意事项)
- [ ] 平均行数 < 100(参考 mattpocock/skills 风格)
- [ ] 不复制 superpowers 内容(只引用 `~/.claude/skills/<name>/`)
- [ ] 与现有 skill 不重复

### 6.2 frontmatter 模板

```yaml
---
name: <skill-name>
description: <一句话描述,触发场景,适用对象>
---
```

### 6.3 User-invoked vs Model-invoked

| 类型 | frontmatter | 触发方式 | 用途 |
|---|---|---|---|
| **User-invoked** | `disable-model-invocation: true` | 用户 `/<name>` 显式调用 | 流程入口 |
| **Model-invoked** | 无 disable 字段 | AI 自动判断触发 | 工具型 skill |
| **Bridge** | 无 disable 字段,但内容是引用 | AI 自动判断 | 跨 skill 协作 |

## 七、scripts/ 目录约定

### 7.1 命名规范

- Python:`<verb>-<noun>.py`(例:`sql-dialect-check.py`)
- Bash:`<verb>-<noun>.sh`(例:`smoke-test.sh`)

### 7.2 输出规范

- 退出码:`0` = 成功,`1` = 失败
- stdout:结果(可解析)
- stderr:进度 / 警告
- 人类可读 + 机器可解析

### 7.3 测试要求

每个新脚本必须有:
- [ ] `--help` 显示用法
- [ ] 退出码测试
- [ ] 边界用例测试
- [ ] 性能可接受(< 30 秒)

## 八、CHANGELOG / plan.md 维护

- **CHANGELOG.md**:版本变更记录(用户视角)
- **plan.md**:开发计划 + 进度(开发者视角)
- 每次发版前必须同步更新两个文件

## 九、版本发布

### 9.1 SemVer 规范

```
<major>.<minor>.<patch>
```

- **major**:破坏性变更(breaking change)
- **minor**:新功能(向后兼容)
- **patch**:Bug 修复(向后兼容)

### 9.2 发布流程

1. 更新 `CHANGELOG.md`
2. 更新 `plan.md`(关闭已完成项)
3. 在 main 分支创建 tag:`v<version>`
4. CI 自动跑 full-qa-audit
5. 维护者 review + 合并
6. GitHub 自动创建 Release

## 十、社区

### 10.1 沟通渠道

- 🐛 **Bug 反馈**:[GitHub Issues](../issues)
- 💡 **功能请求**:[GitHub Issues](../issues)
- 💬 **讨论**:[GitHub Discussions](../discussions)
- 📧 **邮件**:jason.sun@example.com

### 10.2 维护者

| 角色 | GitHub | 职责 |
|---|---|---|
| Owner | @BlueprintOS | 决策 + 发布 |
| Maintainer | (招募中) | Review + 合并 |

### 10.3 致谢

感谢所有贡献者!🎉

---

## 附录 A:本地开发环境

### A.1 工具

| 工具 | 版本 | 用途 |
|---|---|---|
| Git | 2.40+ | 版本控制 |
| Bash | 5.x | shell |
| Python | 3.12+ | 验证脚本 |
| Node.js | 20+ | (可选)测试 skill |
| ripgrep | 14+ | 搜索 |

### A.2 IDE 推荐

- VS Code + Claude Code 扩展
- JetBrains IDE(可选)

## 附录 B:文档风格规范

### B.1 Markdown

- 标题:`#` / `##` / `###`(4 级以内)
- 表格:必须对齐 `|---|`
- 代码块:必须标注语言
- 强调:**粗体**(不用斜体)
- 警示:`⚠️` / `❌` / `✅`

### B.2 中文 / 英文

- 文档主语言:**中文**
- 代码 / 字段名:**英文**
- 注释:**中文**
- 国际化预留(预留 `l10n/`)

## 附录 C:常见问题

### C.1 提 PR 前是否必须开 Issue?

**建议但非强制**:
- 大改动(新 skill / 重构)→ **必须**先开 Issue 讨论
- 小改动(typo / 错别字 / 单文件修复)→ **无需** Issue,直接提 PR

### C.2 是否可以同时改多个文件?

**可以,但需**:
- PR 描述明确说明改了什么
- 改动相互关联(不是夹带)
- 通过 CI 检查

### C.3 CI 失败了怎么办?

1. 看 GitHub Actions 日志
2. 本地重跑对应脚本
3. 修复后 push,CI 自动重跑

### C.4 我不是专家,可以贡献吗?

**当然可以!**
- 文档改进(Bug 报告 / 错别字 / 翻译)非常欢迎
- 测试用例(边界场景)非常欢迎
- 任何贡献都视为有价值 ❤️

---

> 📝 **最后更新**:2026-06-22
> 维护者:Jason SUN(sunj243909596@gmail.com)