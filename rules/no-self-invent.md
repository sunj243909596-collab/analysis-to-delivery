# No-Self-Invent — 严禁自创

> 规范来源:`skills/disciplines/no-self-invent`(已迁移至此)。旧的 `skills/disciplines/no-self-invent/SKILL.md` 是本文件的兼容壳。

## 目的

字段、表名、状态码严禁自创 — 字段从知识库来,表名带 `C_`/`APP_` 前缀,状态码引用配置常量。

## 规则

### 1. 字段

- ❌ 严禁自创字段
- ✅ 必须用知识库定义的字段,或 `EXT_FIELD_X` 占位(知识库允许时)

### 2. 表名

- ❌ 严禁自创表名
- ✅ 引用 WMOS 原生表(只读)
- ✅ 新业务表用 `C_` 前缀(如 `C_RECEIVE_TASK`)
- ✅ 巴枪业务表用 `APP_` 前缀(如 `APP_RCV_TASK`)
- ✅ 冷链表用 `APP_COOL_` 前缀(`_MODEL_HDR`=型号 / `_ITEM_HDR`=实物 / `CASE`=套箱 / `THRMT`=温度计 / `MAT`=包材)

### 3. 状态码

- ❌ 严禁硬编码业务状态码(如 `if status == 10`)
- ✅ 使用 `paths/tech-stack-path.md` 引用的常量(如 `ASNStatus.OPEN = 10`)
- ✅ 复用现有系统的状态码,不要发明新码
- ✅ WMOS 状态码是 2 位码(10/20/30/40/50/60/70),不是 3 位

### 4. 既有系统原生表

- ❌ 严禁修改 WMOS 原生表结构
- ✅ 只新增表或扩展(`ALTER TABLE`)

## 反例

```sql
-- ❌ 错误:自创表名
CREATE TABLE RECEIVE_TASK (
    task_id VARCHAR2(20),
    status  NUMBER
);

-- ✅ 正确:用 C_ 前缀
CREATE TABLE C_RECEIVE_TASK (
    task_id  VARCHAR2(20),
    status   NUMBER DEFAULT 10  -- ASNStatus.OPEN
);
```

```java
// ❌ 错误:硬编码状态码
if (asn.getStatus() == 10) { ... }

// ✅ 正确:引用常量
if (asn.getStatus() == ASNStatus.OPEN) { ... }
```

## 引用

- 来源:`references/workflow-discipline.md` 实战教训
- 表名前缀规范:用户全局 agent 指令(如 `CLAUDE.md` / `AGENTS.md`)
