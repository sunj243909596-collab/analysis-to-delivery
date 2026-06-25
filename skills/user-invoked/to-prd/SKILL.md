---
name: to-prd
description: 生成产品需求文档(PRD) — 含用户故事、功能需求、非功能需求、验收标准。Use when formalizing product requirements for handoff to design and dev.
disable-model-invocation: true
version: 3.0.1

---

# To-PRD — 产品需求文档生成

## Contract

- Inputs: signed BRD, compliance review, test cases, field alignment review
- Outputs: `05-产品需求文档 PRD.md`, optional `05-PRD.html`, optional `05-PRD.docx`, optional Figma design document
- Gates: PRD required sections complete; acceptance criteria signed; field mapping validates against knowledge source
- Required disciplines: `no-field-guessing`, `doc-numbering`, `stage-gate`
- Next: `/dev-design`

## 适用场景

- BRD + 合规评审 + 测试用例已通过
- 需要把业务需求翻译成产品视角
- 设计/开发团队需要可执行的需求输入

## 流程步骤

### 1. 加载模板

- `templates/PRD.md`(8 节必备章节)

### 2. 三格式输出

| 格式 | 用途 | 生成方式 |
|---|---|---|
| Markdown | 源文件、版本管理 | 手工编写 |
| HTML | 浏览器阅读、分享 | pandoc + `scripts/postprocess_prd_html.py` |
| DOCX | Word 阅读、批注 | pandoc |

### 3. 填充内容

按 PRD 模板逐节生成:

| 章节 | 内容来源 |
|---|---|
| 一、产品概述 | BRD §1 |
| 二、用户故事 | BRD §2 角色 + 业务场景 |
| 三、功能需求 | BRD §4 + 测试用例(用作验收) |
| 四、非功能需求 | BRD §7 |
| 五、数据需求 | BRD §5 + 字段对齐分析 |
| 六、合规要求 | 04-合规评审.md |
| 七、验收标准 | 07-测试用例设计.md |
| 八、风险与依赖 | BRD §8 |

### 4. 关键纪律

- **字段名必须与知识库定义一致**
- 业务同义不同名需在 PRD 注释中**显式标注**("业务上称为 X = 知识库定义的 Y")
- 严禁自行发明字段
- 用户故事格式:`As an <actor>, I want a <feature>, so that <benefit>`

### 5. Figma 设计文档引用(如适用)

- 简单需求(加字段/调规则)→ 跳过
- 中等需求(新增功能/页面改造)→ 需要 Figma 文档
- 复杂需求(跨模块/多角色/算法介入)→ 必须 Figma 文档

## 输出

- `05-PRD.md`(Markdown 源)
- `05-PRD.html`(可选,后处理)
- `05-PRD.docx`(可选)
- `Figma设计文档_{功能名}_{端}.md`(可选,不受编号约束)

## 调用的 discipline

- `disciplines/no-field-guessing` — 字段名必须查知识库
- `disciplines/doc-numbering` — 文档编号 05

## 结束条件

- [ ] PRD 8 个必备章节齐
- [ ] §七 验收标准签字
- [ ] 字段映射表通过 `field-alignment-check.py`
- [ ] 三格式产物存在(可选 HTML/DOCX)
- [ ] 用户签字进入 `/dev-design`
