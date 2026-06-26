#!/usr/bin/env python3
"""
字段对齐验证器（v1.4-dev）

支持从 Markdown 表格和 SQL DDL 中提取字段定义，检查文档引用字段是否在知识库中定义，
并在文档也给出字段定义时检查类型/可空性是否一致。

用途：仅校验 PRD / FSD / 数据模型 等设计文档对知识库表结构的引用一致性。
不适用：TASK_CONFIRM / REVIEW 需求确认书 / REVIEW 字段对齐分析——这些文档的
门控由 `scripts/task-confirm-check.py` 处理（v4.0.0 引入）。

用法：
    python3 field-alignment-check.py <文档> <知识库文件> [--json]

退出码：0 = 全部对齐；1 = 发现不对齐；2 = 参数错误
"""
import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FieldDef:
    table: str
    name: str
    type: str = ""
    nullable: str = ""
    source: str = ""
    line: int = 0


def norm_name(value: str) -> str:
    return value.strip().strip("`[]\"'").upper()


def norm_type(value: str) -> str:
    value = value.strip().upper()
    value = re.sub(r"\s+", " ", value)
    aliases = {
        "VARCHAR2": "VARCHAR", "CHARACTER VARYING": "VARCHAR", "INT": "INTEGER",
        "NUMBER": "DECIMAL", "NUMERIC": "DECIMAL", "TIMESTAMP WITHOUT TIME ZONE": "TIMESTAMP",
    }
    base = re.sub(r"\(.*\)", "", value).strip()
    return value.replace(base, aliases.get(base, base), 1) if base else value


def norm_nullable(value: str) -> str:
    v = value.strip().lower()
    if not v:
        return ""
    if any(x in v for x in ["否", "not null", "no", "n", "必填", "不可空"]):
        return "NO"
    if any(x in v for x in ["是", "null", "yes", "y", "可空"]):
        return "YES"
    return ""


def strip_code_blocks(text: str, keep_sql: bool = True) -> str:
    if keep_sql:
        return text
    return re.sub(r"^```.*?^```", "", text, flags=re.MULTILINE | re.DOTALL)


def add_field(fields: dict[str, FieldDef], field: FieldDef) -> None:
    if not field.name:
        return
    key = field.name
    existing = fields.get(key)
    if not existing or (field.type and not existing.type):
        fields[key] = field


def parse_markdown_tables(text: str, source: str) -> dict[str, FieldDef]:
    fields: dict[str, FieldDef] = {}
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        if "|" not in line or idx + 1 >= len(lines) or "---" not in lines[idx + 1]:
            continue
        headers = [h.strip().lower() for h in line.strip().strip("|").split("|")]
        col_field = next((i for i, h in enumerate(headers) if any(k in h for k in ["字段", "field", "column", "列名"])), None)
        if col_field is None:
            continue
        col_table = next((i for i, h in enumerate(headers) if any(k in h for k in ["表", "table"])), None)
        col_type = next((i for i, h in enumerate(headers) if any(k in h for k in ["类型", "type", "datatype"])), None)
        col_null = next((i for i, h in enumerate(headers) if any(k in h for k in ["可空", "nullable", "null", "必填"])), None)
        j = idx + 2
        while j < len(lines) and "|" in lines[j]:
            cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
            if len(cells) >= len(headers):
                name = norm_name(cells[col_field])
                if re.match(r"^[A-Z][A-Z0-9_]*$", name):
                    add_field(fields, FieldDef(
                        table=norm_name(cells[col_table]) if col_table is not None and col_table < len(cells) else "",
                        name=name,
                        type=norm_type(cells[col_type]) if col_type is not None and col_type < len(cells) else "",
                        nullable=norm_nullable(cells[col_null]) if col_null is not None and col_null < len(cells) else "",
                        source=source,
                        line=j + 1,
                    ))
            j += 1
    return fields


def parse_sql_ddl(text: str, source: str) -> dict[str, FieldDef]:
    fields: dict[str, FieldDef] = {}
    create_pattern = re.compile(r"CREATE\s+TABLE\s+([\w.\"`]+)\s*\((.*?)\)\s*;", re.IGNORECASE | re.DOTALL)
    for match in create_pattern.finditer(text):
        table = norm_name(match.group(1).split(".")[-1])
        body = match.group(2)
        body_start_line = text[:match.start(2)].count("\n") + 1
        for offset, raw in enumerate(body.splitlines()):
            line = raw.strip().rstrip(",")
            if not line or line.startswith("--"):
                continue
            if re.match(r"^(CONSTRAINT|PRIMARY|FOREIGN|UNIQUE|KEY|INDEX|CHECK)\b", line, re.IGNORECASE):
                continue
            m = re.match(r'[`"]?([A-Za-z][A-Za-z0-9_]*)[`"]?\s+([A-Za-z][A-Za-z0-9_]*(?:\s*\([^)]*\))?)', line)
            if not m:
                continue
            add_field(fields, FieldDef(
                table=table,
                name=norm_name(m.group(1)),
                type=norm_type(m.group(2)),
                nullable="NO" if re.search(r"NOT\s+NULL", line, re.IGNORECASE) else ("YES" if re.search(r"\bNULL\b", line, re.IGNORECASE) else ""),
                source=source,
                line=body_start_line + offset,
            ))
    return fields


def extract_references(text: str) -> set[str]:
    text_no_code = strip_code_blocks(text, keep_sql=False)
    refs = set(norm_name(x) for x in re.findall(r"`([A-Za-z][A-Za-z0-9_]{1,})`", text_no_code))
    return {r for r in refs if not r.startswith(("HTTP", "TODO", "SQL", "API", "PRD", "FSD", "BRD", "DDL", "DML"))}


def extract_defs(path: Path) -> dict[str, FieldDef]:
    text = path.read_text(encoding="utf-8")
    fields = {}
    for parser in (parse_markdown_tables, parse_sql_ddl):
        fields.update(parser(text, str(path)))
    return fields


def main() -> None:
    parser = argparse.ArgumentParser(description="字段对齐验证器（Markdown 表格 + SQL DDL）")
    parser.add_argument("doc")
    parser.add_argument("knowledge")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    doc_path = Path(args.doc)
    kb_path = Path(args.knowledge)
    if not doc_path.exists() or not kb_path.exists():
        print("❌ 文档或知识库不存在", file=sys.stderr)
        sys.exit(2)

    doc_text = doc_path.read_text(encoding="utf-8")
    doc_refs = extract_references(doc_text)
    doc_defs = extract_defs(doc_path)
    doc_refs.update(doc_defs.keys())
    kb_defs = extract_defs(kb_path)

    missing = sorted(f for f in doc_refs if f not in kb_defs)
    type_mismatch = []
    nullable_mismatch = []
    for name, doc_def in doc_defs.items():
        kb_def = kb_defs.get(name)
        if not kb_def:
            continue
        if doc_def.type and kb_def.type and norm_type(doc_def.type) != norm_type(kb_def.type):
            type_mismatch.append({"field": name, "doc": doc_def.type, "knowledge": kb_def.type, "line": doc_def.line})
        if doc_def.nullable and kb_def.nullable and doc_def.nullable != kb_def.nullable:
            nullable_mismatch.append({"field": name, "doc": doc_def.nullable, "knowledge": kb_def.nullable, "line": doc_def.line})

    result = {
        "doc": str(doc_path),
        "knowledge": str(kb_path),
        "referenced_fields": sorted(doc_refs),
        "knowledge_fields": sorted(kb_defs),
        "missing": missing,
        "type_mismatch": type_mismatch,
        "nullable_mismatch": nullable_mismatch,
        "summary": {
            "refs": len(doc_refs),
            "knowledge": len(kb_defs),
            "missing": len(missing),
            "type_mismatch": len(type_mismatch),
            "nullable_mismatch": len(nullable_mismatch),
        },
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"📊 字段对齐：引用 {len(doc_refs)} 个，知识库 {len(kb_defs)} 个")
        if missing:
            print(f"❌ 知识库未定义字段 ({len(missing)}):")
            for f in missing[:50]:
                print(f"  - {f}")
        for item in type_mismatch:
            print(f"❌ 类型不一致 {item['field']}: 文档={item['doc']} 知识库={item['knowledge']}")
        for item in nullable_mismatch:
            print(f"⚠️  可空性不一致 {item['field']}: 文档={item['doc']} 知识库={item['knowledge']}")
        if not missing and not type_mismatch and not nullable_mismatch:
            print("✅ 字段引用、类型和可空性检查通过")

    sys.exit(1 if missing or type_mismatch or nullable_mismatch else 0)


if __name__ == "__main__":
    main()
