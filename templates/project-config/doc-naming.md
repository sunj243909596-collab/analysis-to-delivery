# 项目级文档命名规范配置

> 作用：告诉 Claude 本项目**文档怎么编号、放在哪个目录、用什么前缀**。
> Claude 在阶段 2-9 产出文档时会按本文件规则命名。

## 使用方法

1. 复制本文件到**项目根目录**
2. 填入你团队的文档规范
3. 如果沿用 skill 默认，可保留 `inherit_default = true`

## 继承默认

```yaml
# 是否继承 skill 默认的 01-09 编号规范（true = 沿用 / false = 完全自定义）
inherit_default = true

# 自定义前缀（留空表示无前缀）
# 适用场景：P0 紧急项目、Sprint 分批、多团队合并
prefix = ""

# 文档存放根目录（相对项目根）
# 留空 = 直接放项目根；推荐用 docs/ 或 docs/requirements/
root_dir = ""
```

## 编号覆盖

> 当 `inherit_default = false` 时，下面表格**完全替换**默认：

| 编号 | 文档名 | 对应阶段 | 必有？ |
|------|--------|----------|--------|
| 01 | 业务需求文档 BRD.md | 阶段 3 | ✅ |
| 02 | 功能规格说明书 FSD.md | 阶段 7 | ✅ |
| 03 | 数据模型设计.md | 阶段 7 | ✅ |
| 04 | 合规评审.md | 阶段 4 | ⚠️ 按需 |
| 05 | 产品需求文档 PRD.md | 阶段 6 | ✅ |
| 06 | 开发设计说明书.md | 阶段 7 | ✅ |
| 07 | 测试用例设计.md | 阶段 5 | ✅ |
| 08 | 设计回测报告.md | 阶段 7 | ⚠️ 按需 |
| 09 | QA 审计报告.md | 阶段 8 | ✅ |

非编号文档(不占编号):

| 文档名 | 对应阶段 | 必有？ |
|--------|----------|--------|
| AGENTS.md | 阶段 7 | ⚠️ 按需 |
| TASK_CONFIRM_*.md | 阶段 2 | ✅ |
| REVIEW_*.md | 阶段 2 | ✅ |
| RETRO_*.md | 阶段 7 / 实施扩展 | ⚠️ 按需 |
| HANDOVER.md | 阶段 9 | ✅ |

## 自定义编号示例

```yaml
# 场景 1：Sprint 分批
prefix = "Sprint-1-"
# 实际文件名：Sprint-1-01-业务需求文档 BRD.md

# 场景 2：多团队合并
prefix = "team-a-"
# 实际文件名：team-a-01-业务需求文档 BRD.md

# 场景 3：日期分组
prefix = "2026Q3-"
# 实际文件名：2026Q3-01-业务需求文档 BRD.md
```

## 存放路径示例

```yaml
# 场景 1：直接根目录（小型项目）
root_dir = ""
# 实际路径：./01-业务需求文档 BRD.md

# 场景 2：docs/ 子目录（中型项目）
root_dir = "docs"
# 实际路径：./docs/01-业务需求文档 BRD.md

# 场景 3：按类型分目录（大型项目）
root_dir = "docs/requirements"
# 实际路径：./docs/requirements/01-业务需求文档 BRD.md
```

## Figma 设计文档（不受编号约束）

| 端 | 命名格式 | 示例 |
|----|---------|------|
| PC | `Figma设计文档_{功能名}_PC.md` | `Figma设计文档_{功能名}_PC.md` |
| 移动端 | `Figma设计文档_{功能名}_移动端.md` | `Figma设计文档_{功能名}_移动端.md` |
| Pad | `Figma设计文档_{功能名}_Pad.md` | - |

## 加载规则

Claude 按以下优先级加载命名规范：

1. **本文件**（项目级，最准）
2. skill 默认（当 `inherit_default = true`）
3. skill 内置 `config/doc-naming/{team}.md`（按团队名匹配，v1.1+）

## 冲突处理

- 发现编号冲突 → 立即 `mv` 重命名，文档内部标题同步修正
- `HANDOVER.md` / `AGENTS.md` / `REVIEW_*` / `TASK_CONFIRM_*` / `RETRO_*` 不占编号
- Figma 文档不受编号约束，独立命名

---

**示例**：见 `examples/01-wms-warehouse/doc-naming.md`
**默认规范**：见 `references/doc-numbering.md`
