# AGENTS.md — {项目名}

> AI 助手项目级配置
> 渐进式披露：地图而非手册

## 🗺️ 项目地图

```
{项目目录}/
├── docs/
│   ├── 01-业务需求文档 BRD.md       # 业务背景
│   ├── 02-功能规格说明书 FSD.md      # 详细设计 V1
│   ├── 03-数据模型设计.md             # 数据模型
│   ├── 04-合规评审.md                # 合规检查
│   ├── 05-产品需求文档 PRD.md         # 产品需求
│   ├── 06-开发设计说明书.md            # 代码实现 V2
│   └── 07-测试用例设计.md             # 测试用例
├── src/
│   ├── backend/                      # 后端代码
│   ├── frontend/                     # PC 端
│   └── app/                          # 移动端
└── README.md
```

## ⚡ 快速命令

```bash
# 后端构建
mvn clean compile -DskipTests

# 前端构建
cd src/frontend && npm run build

# 跑测试
mvn test && npm run test
```

## 🚨 硬性规则（违反=代码错误）

1. 严禁猜测字段名 — 查 {知识库路径}
2. 严禁自创字段 — 用 `REF_FIELD_X` 占位
3. 严禁修改原生表 — 只新增或扩展
4. 审计字段 5 件套必须加全
5. 主键用 SEQUENCE，不用自增

## 📂 文档索引（按需读取）

| 需要什么 | 去哪读 |
|---|---|
| 业务背景 | `01-业务需求文档 BRD.md` |
| 数据模型 | `03-数据模型设计.md` |
| 产品需求 | `05-产品需求文档 PRD.md` |
| 代码设计 | `06-开发设计说明书.md` |

## 📐 分层架构规则

```
（按 config/tech-stack/ 加载）
```

## 🔗 工作流

```
需求 → 阶段 1-10
```

详细见 [analysis-to-delivery SKILL.md](https://github.com/<owner>/analysis-to-delivery/blob/main/SKILL.md)

## 领域特定规则

（如有，按 config/domain-knowledge/ 加载）
