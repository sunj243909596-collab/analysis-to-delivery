# Compliance Path — 合规规则路径

## 目的

指向项目自有的合规约束与评审证据,作为阶段 4 合规评审与阶段 8 QA 审计的输入。

## 必填条目

| 规则集 | 启用 | 路径 | 何时读取 | 责任人 |
|---|---|---|---|---|
| 通用合规 | true | `docs/compliance/general.md` | 合规评审与 QA 审计前 | 合规负责人 |
| 行业规则 | false | `docs/compliance/industry.md` | 项目属于强监管领域时 | 合规负责人 |
| 隐私规则 | false | `docs/compliance/privacy.md` | 涉及敏感数据时 | 安全负责人 |

## 规则

1. **只读取已启用**(`启用 = true`)的条目;`false` 条目默认不加载
2. 启用状态变更需在 commit message 中说明,并同步更新责任人
3. 若全部禁用,需在项目根 `decisions.md` 中写明原因(避免误以为遗漏)
4. 内置示例**不**等同于法律建议或权威政策;具体合规判定以本文件指向的真实文档为准
5. 新增规则集时:补一行 + 填 `路径` + 在对应 `config/compliance/{行业}.md` 补充细则
