# PRD 输出规范

> 阶段 6：PRD 生成
> 三格式输出：Markdown + HTML + DOCX

## 三格式用途

| 格式 | 用途 | 生成方式 |
|---|---|---|
| Markdown | 源文件、版本管理 | 手工编写 |
| HTML | 浏览器阅读、分享 | pandoc + 后处理 |
| DOCX | Word 阅读、批注 | pandoc |

## Markdown 模板

详见 [templates/PRD.md](../templates/PRD.md)

## HTML 生成

### 工具链

- **pandoc**：MD → HTML
- **scripts/postprocess_prd_html.py**：HTML 后处理（macOS Apple 风格）

### 流程

```bash
# 1. pandoc 导出中间 HTML
pandoc PRD.md -o PRD-raw.html --toc --css=scripts/prd-style.css

# 2. 后处理（重组布局 + 内联 CSS/JS）
python3 scripts/postprocess_prd_html.py PRD-raw.html PRD.html

# 3. 验证
open PRD.html
```

## DOCX 生成

```bash
pandoc PRD.md -o PRD.docx --toc
```

## 关键纪律

### 字段一致性
- 字段名必须与知识库定义一致
- 业务同义不同名需在 PRD 注释中**显式标注**

### 严禁自创
- 严禁自行发明字段（如 `BIZ_FLAG`、`EXT_FIELD_X`）
- 严禁修改知识库已定义的字段含义

### 文档编号
- 文件名：`05-产品需求文档 PRD.md`
- 严禁其他命名（如 `PRD-v1.md`、`PRD-final.md`）

## 排版要点

- 表格列对齐（用 `|` 分隔）
- 代码块标注语言（` ```sql ` 而不是 ` ``` `）
- 中英文之间加空格（如 `Oracle 数据库`）
- 数字与单位之间加空格（如 `100 GB`）

## 实战教训

- 2026-05-12 实战：HTML 排版需后处理，pandoc 默认样式不够美观
- 2026-05-19 实战：DOCX 嵌套 HTML 标签会导致排版错乱（pandoc 限制）
