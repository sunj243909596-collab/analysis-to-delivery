# 项目级知识库路径配置（示例：WMOS 收货管理）

> 这个文件演示一个真实项目根目录下的 `knowledge-path.md` 应该长什么样。
> 用户拿到本示例后，可直接复制到自己的项目根改路径即可。

## 路径列表

| 标签 | 路径 | 用途 | 必读？ |
|------|------|------|--------|
| wms-core | `/root/WMOS 知识库/01-WMOS核心/WMOS 数据表结构.md` | WMOS 原生表结构 | ✅ 阶段 1.3 / 8 |
| gsp-rules | `/root/WMOS 知识库/03-GSP法规/GSP 法规知识库索引.md` | GSP 法规条款 | ✅ 阶段 3 |
| bar-app-db | `/root/WMOS 知识库/巴枪 4A 架构/巴枪 PG 数据库字典/巴枪PG全量表结构字典_20260426.md` | 巴枪 PG 表结构 | ✅ 阶段 8 |
| prd-template | `/root/WMOS 知识库/PRD标准模板.md` | PRD 标准模板 | ✅ 阶段 6 |
| pc-ui-rules | `/root/WMOS 知识库/06-设计规范与模板/UI设计规范/PC端UI设计规范_速查版.md` | PC 端 UI 规范 | ✅ 阶段 4 |
| bar-ui-rules | `/root/WMOS 知识库/06-设计规范与模板/UI设计规范/安智储巴枪移动端UI设计规范_速查版.md` | 巴枪 UI 规范 | ✅ 阶段 4 |
| cool-old-system | `/root/WMOS 知识库/冷链旧系统/01_操作手册_提取文本.md` | 冷链旧系统参考 | ⚠️ 按需 |

## 加载规则

Claude 在阶段 1.3（字段对齐）和阶段 8（开发设计）时会按本文件加载上述知识库。

加载顺序：
1. 先读本文件的 `wms-core`（最常用）
2. 涉及 PG 巴枪表时读 `bar-app-db`
3. 阶段 3 合规评审时读 `gsp-rules`
4. 阶段 6 PRD 时读 `prd-template`
5. 阶段 4 系统方案时读 PC/巴枪 UI 规范

## 安全约束

- 全部为本地绝对路径，**禁止远程 URL**
- Claude 只读不写，不会修改这些知识库文件

## 维护

- 本文件纳入 git 版本控制（与项目代码一起 commit）
- 知识库文件本身**不在项目仓库内**（通常太大或涉密），只引用路径
- 当团队新增/移动知识库时，更新本文件并通知所有协作者

---

**生成时间**：2026-06-22
**关联模板**：[templates/project-config/knowledge-path.md](../../templates/project-config/knowledge-path.md)
