# 项目级技术栈规范路径配置

> 作用：告诉 Claude 本项目用什么**后端 / 前端 / 数据库 / 中间件**，以及它们的规范文档在哪。
> Claude 在阶段 1（确认技术栈）至阶段 8（开发设计）会按本文件加载。

## 使用方法

1. 复制本文件到**项目根目录**
2. 填入你项目使用的技术栈名称 + 规范文档路径
3. Claude 会自动应用对应的分层架构、命名规范、审计字段等约束

## 后端

| 项 | 值 | 规范路径 |
|----|----|---------|
| 语言 | Java 11 | - |
| 框架 | Spring Boot 2.7.x | `~/docs/standards/java-spring.md` |
| ORM | MyBatis-Plus 3.3.2 | （同上） |
| 构建 | Maven | - |
| 规范路径 | `/path/to/your-team/java-spring-standards.md` | - |

> 支持的 skill 内置模板：`java-spring` / `node-nestjs` / `python-django` / `go-gin` / `dotnet-core` / `rust-actix`

## 前端

| 端 | 框架 | 规范路径 |
|----|------|---------|
| PC | （如 Vue 3 + TS + Element Plus + Vite） | `/path/to/your-pc-standards.md` |
| 移动端 / APP | （如 uni-app + uView） | `/path/to/your-mobile-standards.md` |
| Pad | （无） | - |

## 数据库

| 类型 | 名称 | 规范路径 |
|------|------|---------|
| 主库 | Oracle 19c | （同后端规范） |
| 缓存 | Redis 7 | - |
| 消息 | RabbitMQ | - |

> 多方言混用时，Claude 会用 `scripts/sql-dialect-check.py` 校验。

## 中间件

| 类型 | 名称 | 用途 |
|------|------|------|
| 配置中心 | Nacos | 远程配置 |
| 注册中心 | Nacos | 服务发现 |
| 链路追踪 | SkyWalking | 监控 |

## 命名规范覆盖

> 如果 skill 内置规则与你们团队不符，**在这里覆盖**：

| 项 | skill 默认 | 本项目 |
|----|-----------|--------|
| 主键策略 | SEQUENCE | SEQUENCE |
| 审计字段 | 5 件套 | 5 件套 |
| 表前缀 | （按业务） | `APP_` 移动端 / `C_` 业务 |
| 状态码 | （按业务） | 2 位码 |

## 加载规则

Claude 按以下优先级加载技术栈：

1. **本文件 paths 列出的规范文档**（项目级，最准）
2. skill 自带的 `config/tech-stack/{name}.md`（按 `name` 匹配）
3. 全部缺失 → 询问用户

## 多技术栈支持

一个项目可以同时有**多个后端 + 多个前端**，例如：

- 后端：Java（主业务）+ Python（报表）
- 前端：PC（Vue 3）+ 移动端（uni-app）+ 小程序（uni-app）

只需在对应小节**重复添加行**，Claude 会按端分别应用。

---

**示例**：见 `examples/01-wms-warehouse/tech-stack-path.md`
**skill 内置规范**：见 `config/tech-stack/`
