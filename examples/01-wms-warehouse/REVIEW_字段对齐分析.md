# 字段对齐分析：入库收货管理

> 生成时间：2026-06-22
> 来源：需求确认书 + WMOS 知识库
> 状态：✅ 已对齐（含 2 条待确认）

## 核心理念

**任何涉及 WMOS 原生表的 PRD/FSD/数据模型修改前，必须先核对真实表名+字段名+类型+可空性。**

## 涉及的 WMOS 原生表

### 表 1：ASN（ASN 单主表）

| 知识库定义字段 | 类型 | 可空 | PRD 中的引用 | 对齐状态 |
|---|---|---|---|---|
| ASN_ID | NUMBER | NO | ASN_ID | ✅ |
| TC_ASN_ID | VARCHAR2(50) | NO | TC_ASN_ID（ASN 单号） | ✅ |
| ASN_STATUS | NUMBER(3) | NO | ASN_STATUS（10/20/30/40/50/60/70） | ✅ |
| WHSE_CODE | VARCHAR2(20) | NO | WHSE_CODE（仓库编码） | ✅ |
| VENDOR_ID | NUMBER | NO | VENDOR_ID（供应商 ID） | ✅ |
| FTSR_NBR | VARCHAR2(50) | YES | FTSR_NBR（货主订单号 = 业务上的"订单组号"） | ✅ 已标注业务同义 |
| REF_FIELD_4 | VARCHAR2(200) | YES | （未引用） | - |
| CREATE_DATE_TIME | DATE | NO | CREATE_DATE_TIME | ✅ |
| CREATE_USER_ID | VARCHAR2(50) | NO | CREATE_USER_ID | ✅ |
| MOD_DATE_TIME | DATE | NO | MOD_DATE_TIME | ✅ |
| MOD_USER_ID | VARCHAR2(50) | NO | MOD_USER_ID | ✅ |
| WM_VERSION_ID | NUMBER | NO | WM_VERSION_ID | ✅ |

### 表 2：ASN_DETAIL（ASN 明细表）

| 知识库定义字段 | 类型 | 可空 | PRD 中的引用 | 对齐状态 |
|---|---|---|---|---|
| ASN_DETAIL_ID | NUMBER | NO | ASN_DETAIL_ID | ✅ |
| ASN_ID | NUMBER | NO | ASN_ID（关联主表） | ✅ |
| TC_ASN_ID | VARCHAR2(50) | NO | TC_ASN_ID（冗余存储，便于查询） | ✅ |
| SKU_ID | NUMBER | NO | SKU_ID | ✅ |
| BATCH_NBR | VARCHAR2(200) | NO | BATCH_NBR（批号） | ✅ |
| QTY_EXPECTED | NUMBER(16,4) | NO | QTY_EXPECTED（预计数量） | ✅ |
| QTY_RECEIVED | NUMBER(16,4) | NO | QTY_RECEIVED（已收数量） | ✅ |
| QTY_REJECTED | NUMBER(16,4) | NO | QTY_REJECTED（拒收数量） | ✅ |

> ⚠️ PRD 严禁用 `ASN_ID` 表示"ASN 明细关联 LPN"，必须是 `ASN_DTL_ID`（如果后续阶段涉及）

### 表 3：LPN（货箱表）

| 知识库定义字段 | 类型 | 可空 | PRD 中的引用 | 对齐状态 |
|---|---|---|---|---|
| LPN_ID | NUMBER | NO | LPN_ID | ✅ |
| TC_LPN_ID | VARCHAR2(50) | NO | TC_LPN_ID（货箱号） | ✅ |
| LPN_STATUS | NUMBER(3) | NO | LPN_STATUS（10=未上架, 30=已上架） | ✅ |
| ASN_DETAIL_ID | NUMBER | YES | ASN_DETAIL_ID（关联的 ASN 明细） | ✅ |

### 表 4：INVENTORY（库存表）

| 知识库定义字段 | 类型 | 可空 | PRD 中的引用 | 对齐状态 |
|---|---|---|---|---|
| INVENTORY_ID | NUMBER | NO | INVENTORY_ID | ✅ |
| SKU_ID | NUMBER | NO | SKU_ID | ✅ |
| LPN_ID | NUMBER | NO | LPN_ID（关联的货箱） | ✅ |
| BATCH_NBR | VARCHAR2(200) | NO | BATCH_NBR | ✅ |
| QTY_ON_HAND | NUMBER(16,4) | NO | QTY_ON_HAND（在手数量） | ✅ |
| QTY_AVAILABLE | NUMBER(16,4) | NO | QTY_AVAILABLE（可用数量） | ✅ |
| EXPIRE_DATE | DATE | YES | EXPIRE_DATE（效期） | ✅ |
| QUALITY_STATUS | VARCHAR2(10) | NO | QUALITY_STATUS（合格/待检/不合格） | ✅ |

## 待确认字段

| 字段 | 知识库定义 | PRD 中用法 | 疑问 |
|---|---|---|---|
| ASN.REF_FIELD_4 | 货主订单号 | 未引用 | 是否可用于本项目？T-02 待确认 |
| ASN_DETAIL.QTY_REJECTED | 拒收数量 | 直接引用 | 是否含"隔离"数量？待与用户确认 |

## 业务同义不同名（必须显式标注）

| PRD 字段 | 知识库定义 | 业务同义 | 标注方式 |
|---|---|---|---|
| ASN.FTSR_NBR | 货主订单号 | 订单组号（业务上叫法） | PRD 注释：`FTSR_NBR (货主订单号 = 业务上的订单组号)` |

## 自创字段检查

✅ **未发现自创字段**。所有字段均来自知识库定义。

如后续阶段需要扩展字段，使用 `REF_FIELD_1` ~ `REF_FIELD_5`（WMOS 预留扩展位）。

## 自创表检查

✅ **未发现自创表**。

如需新增巴枪业务表，按规范使用 `APP_` 前缀（如 `APP_RCV_HDR`、`APP_RCV_DTL`）。

## 对齐结论

| 类别 | 数量 |
|---|---|
| ✅ 已对齐 | 33 个字段 |
| ⚠️ 需 JOIN | 0 个 |
| ❓ 待确认 | 2 个（REF_FIELD_4、QTY_REJECTED 含义） |
| 🔴 缺失 | 0 个 |

**结论**：可以进入阶段 2（业务流程设计）。待确认字段不影响 BRD 设计，待 T-02 解决后再细化。

---

**检查清单**：
- [x] 表名与知识库定义一致
- [x] 字段名与知识库定义一致
- [x] 字段类型与知识库定义一致
- [x] 字段可空性与知识库定义一致
- [x] 业务同义不同名已显式标注
- [x] 无自创字段
- [x] 无自创表
- [x] 无修改 WMOS 原生表结构
