# 项目级技术栈规范路径配置（示例：WMOS 收货管理）

> 这个文件演示一个真实项目根目录下的 `tech-stack-path.md` 应该长什么样。

## 后端

| 项 | 值 | 规范路径 |
|----|----|---------|
| 语言 | Java 11 | - |
| 框架 | Spring Boot 2.7.x | `/root/bar-local-workspace/local_backend/bar-local-wms/`（项目代码） |
| ORM | MyBatis-Plus 3.3.2 | （同上） |
| 构建 | Maven | - |
| 规范路径 | （团队自定义） | `templates/project-config/tech-stack-path.md` 顶部说明 |

> 加载 skill 内置模板：`java-spring` （作为参考）

## 前端

| 端 | 框架 | 规范路径 |
|----|------|---------|
| PC | Vue 3 + TS + Element Plus + Vite | `/root/bar-local-workspace/frontend_app/bar-local-pc/`（项目代码） |
| 巴枪/移动 | uni-app (Vue 2) + uView | `/root/bar-local-workspace/frontend_app/bar-app/`（项目代码） |
| Pad PDA | React 18 + MUI v7 + Tailwind v4 | `/root/PDA-Prototype-Design-Poc/`（原型） |

## 数据库

| 类型 | 名称 | 规范路径 |
|------|------|---------|
| 主库 | Oracle 19c | （同后端规范） |
| 巴枪库 | PostgreSQL 14 | `bar-app-db` 在 knowledge-path.md |
| 缓存 | Redis 7 | - |

## 中间件

| 类型 | 名称 | 用途 |
|------|------|------|
| 配置中心 | Nacos | 远程配置 |
| 注册中心 | Nacos | 服务发现 |
| 链路追踪 | SkyWalking | 监控 |

## 命名规范覆盖

| 项 | skill 默认 | 本项目 |
|----|-----------|--------|
| 主键策略 | SEQUENCE | SEQUENCE |
| 审计字段 | 5 件套 | 5 件套（CREATE_DATE_TIME / CREATE_USER_ID / MOD_DATE_TIME / MOD_USER_ID / WM_VERSION_ID） |
| 表前缀 | （按业务） | `APP_` 巴枪业务 / `C_` 新业务表 |
| 状态码 | （按业务） | 2 位码（ASN: 10/20/30/40/50/60/70；LPN: 10/30） |
| 序列号扫描 | 无强制 | 收货时强制（除非商品无序列号） |
| 巴枪扫码顺序 | 无强制 | 由业务方人工确认（不允许 Claude 自行推测） |

## 加载规则

Claude 在以下阶段会加载技术栈规范：
- 阶段 1：确认项目用 Java 后端 + Vue 前端
- 阶段 4：应用 PC/巴枪 UI 规范到 Figma 设计
- 阶段 8 V1：按 Oracle/PG 方言生成 SQL/PL-SQL
- 阶段 8 V2：按 Java 分层架构生成 Controller/Service/Repository

## 多方言注意

- Oracle 用 `NVL/SYSDATE/ROWNUM/||` 
- PG 用 `COALESCE/NOW()/LIMIT/concat()`
- Claude 会用 `scripts/sql-dialect-check.py` 自动校验不混用

---

**生成时间**：2026-06-22
**关联模板**：[templates/project-config/tech-stack-path.md](../../templates/project-config/tech-stack-path.md)
