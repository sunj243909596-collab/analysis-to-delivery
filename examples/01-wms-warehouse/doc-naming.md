# 项目级文档命名规范配置（示例：WMOS 收货管理）

> 这个文件演示一个真实项目根目录下的 `doc-naming.md` 应该长什么样。

## 继承默认

```yaml
# 沿用 skill 默认的 01-07 编号规范
inherit_default = true

# 无自定义前缀
prefix = ""

# 文档直接放项目根（与示例一致）
root_dir = ""
```

## 编号覆盖

沿用默认（无需修改）。

## 自定义场景示例（参考）

如果未来 WMOS 团队要做 Sprint 分批：

```yaml
prefix = "Sprint-2-"
# 实际文件名：Sprint-2-01-业务需求文档 BRD.md
```

如果团队决定统一放 docs/：

```yaml
root_dir = "docs"
# 实际路径：./docs/01-业务需求文档 BRD.md
```

## Figma 设计文档（本项目相关）

| 端 | 命名 | 状态 |
|----|------|------|
| PC | `Figma设计文档_入库收货_PC.md` | ⬜ 待出 |
| 巴枪 | `Figma设计文档_入库收货_巴枪.md` | ⬜ 待出 |

## 加载规则

Claude 在阶段 2-10 产出文档时按本文件命名。当前示例用默认，所以文件名直接是 `01-业务需求文档 BRD.md` 等。

---

**生成时间**：2026-06-22
**关联模板**：[templates/project-config/doc-naming.md](../../templates/project-config/doc-naming.md)
**默认规范**：[references/doc-numbering.md](../../references/doc-numbering.md)
