---
name: no-field-guessing
description: 严禁猜测字段名 — 数据库/接口字段必须从知识库或契约文档获取。Use when writing SQL, designing data models, generating API contracts, or any task that names database fields.
version: 3.0.1

---

# No-Field-Guessing — 严禁猜测字段名

## Contract

- Inputs: SQL, data model, API contract, field mapping text, `knowledge-path.md`
- Outputs: field names sourced from knowledge base or explicit placeholders
- Gates: no invented database/API fields; unresolved names use `EXT_FIELD_X`
- Required disciplines: `context-pointer`
- Next: calling skill continues

## 规则

### 1. 字段来源(优先级从高到低)

1. **项目级 `knowledge-path.md`** 指向的真实知识库(测试库表结构、API 文档)
2. **skill 级 `config/domain-knowledge/{领域}.md`** 引用的知识库
3. **业务同义不同名**:在文档注释中**显式标注**("业务上称为 X = 知识库定义的 Y")
4. **找不到**:用占位符 `EXT_FIELD_X`(待用户确认后改),**严禁编造**

### 2. 严禁做的事

- ❌ 看到需求里说"ASN 单号"就写 `ASN_ID` / `ASN_NBR`(正确是 `TC_ASN_ID`)
- ❌ 看到"货箱号"就写 `LPN_NBR`(正确是 `TC_LPN_ID`)
- ❌ 看到"批号"就写 `LOT_ID`(正确是 `BATCH_NBR`)
- ❌ 看到"ASN 明细关联"就写 `ASN_ID`(正确是 `ASN_DTL_ID`)

### 3. 必做

- ✅ 写任何 SQL / 数据模型 / API 契约前,先读 `knowledge-path.md`
- ✅ 字段映射表必须与知识库定义一致
- ✅ 跑 `python3 scripts/field-alignment-check.py` 验证

## 反例

```markdown
❌ 错误:
| ASN 单号 | ASN_ID |
| 货箱号 | LPN_NBR |
| 批号 | LOT_ID |

✅ 正确:
| ASN 单号 | ASN.TC_ASN_ID | ❌ 严禁用 ASN_NBR |
| 货箱号 | LPN.TC_LPN_ID | ❌ 严禁用 LPN_NBR |
| 批号 | ASN_DETAIL.BATCH_NBR | ❌ 严禁用 LOT_ID |
```

## 引用

- 来源:`references/workflow-discipline.md` 实战教训 2024-2026
- 字段名速查表:用户全局 `CLAUDE.md` 的"关键字段映射"小节
