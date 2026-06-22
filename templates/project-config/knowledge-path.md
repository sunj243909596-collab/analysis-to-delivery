# 项目级知识库路径配置

> 作用：告诉 Claude 本项目涉及哪些**外部知识库**，以及它们在哪里。
> Claude 在阶段 1.3（字段对齐）和阶段 8（开发设计）时会按本文件加载。

## 使用方法

1. 复制本文件到**项目根目录**（与 `package.json` / `pom.xml` / `go.mod` 同级）
2. 按下面的格式，把你项目实际依赖的**真实**知识库文件路径填入
3. Claude 会自动读取并对齐字段、术语、状态码

## 路径列表

> 每行一个：`{标签} = {绝对路径}` 或 `{标签} = {相对路径（相对于项目根）}`
> 建议用**绝对路径**，避免 Claude 工作目录漂移时找不到。

| 标签 | 路径 | 用途 | 必读？ |
|------|------|------|--------|
| 示例：domain-core | `/path/to/your-domain/核心表结构.md` | 你的领域核心表结构 | ✅ 阶段 1.3 / 8 |
| 示例：compliance-rules | `/path/to/your-domain/合规规则.md` | 你的领域合规条款 | ✅ 阶段 3 |
| 示例：mobile-app-db | `/path/to/your-domain/移动端字典.md` | 移动端表结构（如适用） | ✅ 阶段 8 |
|  |  |  |  |

## 加载规则

Claude 按以下优先级加载知识库：

1. **本文件** 列出的路径（项目级，最高优先级）
2. skill 自带的 `config/domain-knowledge/*.md`（skill 级，仅当本文件为空时作为示例参考）
3. **不加载任何知识库**（Claude 必须停下来问用户，不得自行猜测）

## 安全约束

- 默认只接受**本地绝对路径**（如 `/Users/me/docs/` 或 `D:\projects\kb\`）
- HTTP/HTTPS URL **不被默认接受**；如确需远程知识库，在路径后加 ` # remote` 标记，并明确授权
- Claude 不会执行知识库文件中的任何代码——仅作为 Markdown 文本读取

## 维护

- 本文件应纳入版本控制（与 `package.json` 一起 commit）
- 知识库文件本身**不在项目仓库内**（通常太大或涉密），只引用路径
- 当团队新增/移动知识库时，更新本文件并通知所有协作者

---

**示例**：见 `examples/01-wms-warehouse/knowledge-path.md`
**更多字段对齐方法**：见 `references/field-alignment.md`
