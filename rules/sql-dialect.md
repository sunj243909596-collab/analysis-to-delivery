# SQL-Dialect — SQL 方言纪律

> 规范来源:`skills/disciplines/sql-dialect-discipline`(已迁移至此)。旧的 `skills/disciplines/sql-dialect-discipline/SKILL.md` 是本文件的兼容壳。
>
> 命名说明:canonical rule 名是 `sql-dialect`(无 `-discipline` 后缀);旧的 `sql-dialect-discipline` 仍作为兼容别名被识别。

## 目的

SQL 方言严格对齐 Target_DB — Oracle / PostgreSQL / MySQL 函数混用检查。

## Target_DB 标注(强制)

任何 SQL 必须在文件头部标注 Target_DB:

```markdown
<!-- Target_DB: ORACLE -->
SELECT NVL(status, 0) FROM ASN;
```

```markdown
<!-- Target_DB: POSTGRES -->
SELECT COALESCE(status, 0) FROM ASN;
```

## 关键方言差异

| 场景 | Oracle | PostgreSQL | MySQL |
|---|---|---|---|
| 空值替换 | `NVL(a, b)` | `COALESCE(a, b)` | `IFNULL(a, b)` 或 `COALESCE` |
| 当前时间 | `SYSDATE` | `NOW()` / `CURRENT_TIMESTAMP` | `NOW()` / `CURRENT_TIMESTAMP` |
| 行数限制 | `ROWNUM <= N` / `FETCH FIRST N ROWS ONLY` | `LIMIT N` | `LIMIT N` |
| 字符串连接 | `a \|\| b` | `a \|\| b` | `CONCAT(a, b)` |
| 分页 | `OFFSET N ROWS FETCH NEXT M ROWS ONLY` | `OFFSET N LIMIT M` | `OFFSET N LIMIT M` |
| 序列 | `SEQ.NEXTVAL` | `NEXTVAL('seq')` | `AUTO_INCREMENT` |
| 整数除法 | `1.0/3`(必须显式小数) | `1.0/3` | `1.0/3` |
| 真值 | `= 1` | `IS TRUE` | `= 1` |

## 硬性规则

1. **字符串连接用 `||`**(Oracle/PG 通用;MySQL 改 `CONCAT`)
2. **多表 JOIN 必须用表别名前缀**(`asn.TC_ASN_ID`,不是 `TC_ASN_ID`)
3. **绑定变量**:MyBatis 用 `#{param}`,JDBC/PL-SQL 用 `:param`;严禁字符串拼接 SQL
4. **DDL 注释 + 索引**:每个字段 `COMMENT ON COLUMN ...`,常用查询字段建索引
5. **禁止 `SELECT *`** — 必须明确列出字段
6. **审计字段五件套**:`CREATE_DATE_TIME`, `CREATE_USER_ID`, `MOD_DATE_TIME`, `MOD_USER_ID`, `WM_VERSION_ID`
7. **主键用 SEQUENCE** — 每表一个 SEQ,不依赖自增

## 自动检查

```bash
python3 ~/.claude/skills/analysis-to-delivery/scripts/sql-dialect-check.py <项目目录>
```

## 反例

```sql
-- ❌ 错误:Oracle 用 LIMIT
SELECT * FROM ASN LIMIT 10;

-- ✅ 正确:Oracle 用 ROWNUM
SELECT * FROM ASN WHERE ROWNUM <= 10;

-- ❌ 错误:PG 用 NVL
SELECT NVL(status, 0) FROM ASN;

-- ✅ 正确:PG 用 COALESCE
SELECT COALESCE(status, 0) FROM ASN;

-- ❌ 错误:Oracle 整数除法
SELECT 1/3 FROM DUAL;  -- 结果是 0!

-- ✅ 正确
SELECT 1.0/3 FROM DUAL;  -- 结果是 0.333...
```

## 引用

- 详细规范:原 `references/`,用户全局 `CLAUDE.md` "硬性规则"小节
