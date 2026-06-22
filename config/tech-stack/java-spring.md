# Java + Spring Boot + MyBatis-Plus + Oracle 规范

## 技术栈
- 语言：Java 11+
- 框架：Spring Boot 2.x
- ORM：MyBatis-Plus 3.3.2+
- 数据库：Oracle 12c+
- 构建：Maven 3.6+
- JDK：OpenJDK 11

## 分层架构

```
L5 controller/   → 只依赖 L4 service, L2 core, common
L4 service/      → 业务核心层，不跨层依赖
L3 config/       → 依赖 L2 core, L4 service
L2 core/         → 横切关注点，不允许依赖业务包
L1 repository/   → 只依赖 L0 entity, common
L0 entity/       → 只依赖 common
```

## 命名规范
- **表命名**：业务表 `C_` 前缀，巴枪业务表 `APP_` 前缀，WMOS 原生表沿用
- **字段命名**：下划线分隔，全大写（Oracle 习惯）
- **状态码**：2 位码（如 10/20/30），不用 3 位（100/300）
- **审计字段**：5 件套（CREATE_DATE_TIME/CREATE_USER_ID/MOD_DATE_TIME/MOD_USER_ID/WM_VERSION_ID）
- **主键**：SEQUENCE，不用自增

## 关键约束

### SQL 编写
- ✅ 字符串连接用 `||`
- ✅ 多表 JOIN 必须用表别名前缀
- ✅ 绑定变量用 `#{param}`，严禁字符串拼接
- ❌ 严禁 `SELECT *`
- ❌ 严禁硬编码业务状态码
- ❌ 严禁猜测字段名（先查知识库）

### Oracle 特定
- 整数除法：`1/3` = 0，必须写 `1.0/3`
- 字符串函数：`NVL()` 不是 `COALESCE()`
- 日期函数：`SYSDATE` 不是 `NOW()`
- 分页：`ROWNUM` 不是 `LIMIT`

### 事务管理
- `@Transactional` 注解在 Service 层（不是 Controller）
- 事务边界要明确：哪些方法必须事务、哪些可以非事务
- 异常处理：RuntimeException 自动回滚，Checked Exception 需手动配置

## DDL 规范
- 每个字段必须 `COMMENT ON COLUMN ...`
- 常用查询字段建索引
- 不修改 WMOS 原生表结构（只新增或扩展）

## PIX 事务（如适用）
- PIX_TYPE/TRAN_TYPE/TRAN_CODE 严禁猜测
- 必须参考 WMOS 原生 PIX Matrix
