# 项目级合规规则路径配置

> 作用：告诉 Claude 本项目需要遵守哪些**合规规则**（GSP / HIPAA / SOX / 等保 2.0 / GDPR …）。
> Claude 在阶段 3（合规性评审）会按本文件加载。

## 使用方法

1. 复制本文件到**项目根目录**
2. 填入你项目适用的合规规则文件路径
3. 如果项目无强制合规（普通内部工具），把 `enabled = false`

## 启用开关

```yaml
# 是否启用合规评审（true = 必须评审 / false = 跳过阶段 3）
enabled = true

# 合规模式（一对一，不允许多选）
# 可选: gsp（中国医药） / hipaa（美国医疗） / sox（金融） / 
#       等保2.0（中国信息安全） / gdpr（欧盟隐私） / pci-dss（支付卡） / 
#       none（无强合规） / custom（自定义规则）
mode = gsp
```

## 路径列表

| 标签 | 路径 | 缺陷等级覆盖 | 备注 |
|------|------|------|------|
| 示例：gsp-rules | `/root/WMOS 知识库/03-GSP法规/GSP 法规知识库索引.md` | 严重 / 主要 / 一般 | WMOS 项目使用 |
|  |  |  |  |

## 内置合规规则（skill 自带）

如果你的项目落在以下行业，可**直接使用 skill 级 fallback**，无需自定义：

| 行业 | skill 级路径 | 触发关键词 |
|------|--------------|-----------|
| 中国医药物流 | `config/compliance/gsp.md` | "GSP"、"药品"、"医药" |
| 美国医疗 | `config/compliance/hipaa.md` | "HIPAA"、"PHI" |
| 金融支付 | `config/compliance/sox.md` | "SOX"、"金融"、"支付" |
| 欧盟隐私 | `config/compliance/gdpr.md` | "GDPR"、"欧盟用户" |
| 无强制合规 | `config/compliance/none.md` | "内部工具"、"无合规" |

> 当本文件的 `enabled = true` 且 `paths` 为空时，Claude 会询问你"用内置还是自定义"。

## 加载规则

Claude 按以下优先级加载合规规则：

1. **本文件 paths 列出的路径**（项目级，最准）
2. skill 自带的 `config/compliance/{mode}.md`（按 `mode` 字段匹配）
3. `enabled = false` → **跳过阶段 3**
4. 全部缺失 → 询问用户

## 评审输出

加载后，Claude 会按 `references/workflow-discipline.md` 中的格式产出 `04-合规评审.md`：

| 条款编号 | 缺陷等级 | 检查要点 | 合规设计 | 证据位置 | 状态 |

---

**示例**：见 `examples/01-wms-warehouse/compliance-path.md`
**skill 自带规则**：见 `config/compliance/`
