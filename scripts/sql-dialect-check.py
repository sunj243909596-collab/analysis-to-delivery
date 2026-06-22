#!/usr/bin/env python3
"""
SQL 方言混用检查器（v1.3-dev）

检查 Markdown/SQL 文档中的 SQL 片段是否混用 Oracle/PostgreSQL/MySQL 方言。
支持文件、目录、glob、--dialect 和 --json。
"""
import argparse
import glob
import json
import re
import sys
from pathlib import Path

PATTERNS = {
    "oracle": [
        (r"\bNVL\s*\(", "Oracle NVL()"), (r"\bSYSDATE\b", "Oracle SYSDATE"),
        (r"\bROWNUM\b", "Oracle ROWNUM"), (r"\bVARCHAR2\b", "Oracle VARCHAR2"),
        (r"\bNUMBER\s*\(", "Oracle NUMBER"), (r"\bSEQUENCE\b", "Oracle SEQUENCE"),
    ],
    "postgres": [
        (r"\bCOALESCE\s*\(", "PostgreSQL COALESCE()"), (r"\bNOW\s*\(\)", "PostgreSQL NOW()"),
        (r"\bSERIAL\b", "PostgreSQL SERIAL"), (r"\bJSONB\b", "PostgreSQL JSONB"),
        (r"\bRETURNING\b", "PostgreSQL RETURNING"), (r"\bLIMIT\s+\d+", "PostgreSQL LIMIT"),
    ],
    "mysql": [
        (r"\bIFNULL\s*\(", "MySQL IFNULL()"), (r"\bAUTO_INCREMENT\b", "MySQL AUTO_INCREMENT"),
        (r"\bTINYINT\b", "MySQL TINYINT"), (r"\bENGINE\s*=", "MySQL ENGINE"),
        (r"\bLIMIT\s+\d+\s*,\s*\d+", "MySQL LIMIT offset,count"),
    ],
}

SQL_START = re.compile(r"\b(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|MERGE|WITH)\b", re.I)


def discover_files(args: list[str]) -> list[Path]:
    files: list[Path] = []
    for arg in args:
        matches = glob.glob(arg) if any(ch in arg for ch in "*?") else [arg]
        for item in matches:
            p = Path(item)
            if p.is_dir():
                files.extend(x for x in p.rglob("*") if x.suffix.lower() in {".md", ".sql"})
            elif p.is_file():
                files.append(p)
    return sorted(set(files))


def iter_sql_chunks(text: str) -> list[tuple[int, str]]:
    chunks: list[tuple[int, str]] = []
    code_re = re.compile(r"^```([^\n`]*)\n(.*?)^```", re.M | re.S)
    consumed = []
    for m in code_re.finditer(text):
        lang = m.group(1).strip().lower()
        body = m.group(2)
        if lang in {"sql", "plsql", "mysql", "postgres", "postgresql", "oracle"} or SQL_START.search(body):
            chunks.append((text[:m.start(2)].count("\n") + 1, body))
        consumed.append((m.start(), m.end()))
    text_without_code = text
    for start, end in reversed(consumed):
        text_without_code = text_without_code[:start] + "\n" * text_without_code[start:end].count("\n") + text_without_code[end:]
    for i, line in enumerate(text_without_code.splitlines(), 1):
        if SQL_START.search(line):
            chunks.append((i, line))
    return chunks


def check_file(path: Path, expected: str) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    findings = []
    for start_line, chunk in iter_sql_chunks(text):
        found = {dialect: [] for dialect in PATTERNS}
        for dialect, patterns in PATTERNS.items():
            for pattern, name in patterns:
                for m in re.finditer(pattern, chunk, re.I):
                    line = start_line + chunk[:m.start()].count("\n")
                    found[dialect].append({"line": line, "rule": name})
        active = [d for d, hits in found.items() if hits]
        if expected != "auto":
            for dialect in active:
                if dialect != expected:
                    for hit in found[dialect]:
                        findings.append({"file": str(path), "line": hit["line"], "dialect": dialect, "message": f"期望 {expected}，发现 {hit['rule']}"})
        elif len(active) > 1:
            for dialect in active:
                for hit in found[dialect]:
                    findings.append({"file": str(path), "line": hit["line"], "dialect": dialect, "message": f"混用方言：{hit['rule']}"})
    return findings


def main() -> None:
    parser = argparse.ArgumentParser(description="SQL 方言混用检查器")
    parser.add_argument("paths", nargs="+", help="文件、目录或 glob")
    parser.add_argument("--dialect", choices=["auto", "oracle", "postgres", "mysql"], default="auto")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    files = discover_files(args.paths)
    if not files:
        print("❌ 未找到匹配文件", file=sys.stderr)
        sys.exit(2)
    findings = []
    for path in files:
        findings.extend(check_file(path, args.dialect))
    result = {"files": len(files), "dialect": args.dialect, "violations": findings, "count": len(findings)}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif findings:
        print(f"❌ 发现 {len(findings)} 处 SQL 方言问题：")
        for item in findings:
            print(f"  {item['file']}:{item['line']} - {item['message']}")
    else:
        print(f"✅ 通过：{len(files)} 个文件未发现 SQL 方言问题")
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
