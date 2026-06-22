#!/usr/bin/env python3
"""
全量 QA 审计工具（v1.3-dev）

对项目文档做静态 QA：文档格式、内部链接、占位符、编号冲突、SQL 方言、字段对齐。
不执行数据库 DDL/DML，不访问网络。
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> tuple[int, str, str]:
    p = subprocess.run(cmd, text=True, capture_output=True)
    return p.returncode, p.stdout, p.stderr


def md_files(path: Path) -> list[Path]:
    if path.is_file() and path.suffix.lower() == ".md":
        return [path]
    if path.is_dir():
        return sorted(path.rglob("*.md"))
    return []


def add_issue(issues: list[dict], level: str, file: str, msg: str, check: str) -> None:
    issues.append({"level": level, "file": file, "msg": msg, "check": check})


def audit_doc_validate(target: Path, issues: list[dict]) -> None:
    cmd = [sys.executable, str(ROOT / "scripts" / "doc-validate.py"), str(target), "--json"]
    if "templates" in target.parts or "cookiecutter" in str(target):
        cmd.append("--template-mode")
    rc, out, err = run(cmd)
    if rc == 2 and not out.strip():
        add_issue(issues, "P0", str(target), err.strip() or "doc-validate 执行失败", "doc-validate")
        return
    try:
        data = json.loads(out)
    except Exception as exc:
        add_issue(issues, "P0", str(target), f"doc-validate JSON 解析失败: {exc}", "doc-validate")
        return
    for result in data.get("results", []):
        for issue in result.get("issues", []):
            add_issue(issues, issue.get("level", "P2"), result.get("file", str(target)), issue.get("msg", ""), "doc-validate")


def audit_numbering(path: Path, issues: list[dict]) -> None:
    if not path.is_dir():
        return
    seen: dict[str, Path] = {}
    for f in path.glob("0?-*.md"):
        prefix = f.name.split("-", 1)[0]
        if prefix in seen:
            add_issue(issues, "P0", str(f), f"编号 {prefix} 与 {seen[prefix].name} 冲突", "numbering")
        else:
            seen[prefix] = f


def audit_required_docs(path: Path, issues: list[dict]) -> None:
    if not path.is_dir():
        return
    required = ["01", "05", "07"]
    existing = {f.name.split("-", 1)[0] for f in path.glob("0?-*.md")}
    for prefix in required:
        if prefix not in existing:
            add_issue(issues, "P1", str(path), f"建议包含编号 {prefix} 的核心文档", "required-docs")


def audit_sql(path: Path, issues: list[dict]) -> None:
    cmd = [sys.executable, str(ROOT / "scripts" / "sql-dialect-check.py"), str(path), "--json"]
    rc, out, err = run(cmd)
    if rc == 2:
        add_issue(issues, "P1", str(path), err.strip() or "SQL 检查跳过", "sql-dialect")
        return
    try:
        data = json.loads(out)
    except Exception:
        return
    for item in data.get("violations", []):
        add_issue(issues, "P1", f"{item.get('file')}:{item.get('line')}", item.get("message", "SQL 方言问题"), "sql-dialect")


def find_project_config(path: Path, name: str) -> Path | None:
    base = path if path.is_dir() else path.parent
    cur = base.resolve()
    for candidate in [cur, *cur.parents]:
        p = candidate / name
        if p.exists():
            return p
        if candidate == ROOT.resolve():
            break
    return None


def extract_paths_from_config(config: Path) -> list[Path]:
    paths = []
    text = config.read_text(encoding="utf-8")
    for raw in re.findall(r"`([^`]+\.(?:md|sql))`", text):
        p = (config.parent / raw).resolve() if not Path(raw).is_absolute() else Path(raw)
        if p.exists():
            paths.append(p)
    return paths


def audit_field_alignment(path: Path, issues: list[dict]) -> None:
    config = find_project_config(path, "knowledge-path.md")
    if not config:
        add_issue(issues, "P2", str(path), "未找到 knowledge-path.md，跳过字段对齐自动审计", "field-alignment")
        return
    kb_paths = extract_paths_from_config(config)
    if not kb_paths:
        add_issue(issues, "P2", str(config), "knowledge-path.md 未列出可读取的 .md/.sql 知识库路径", "field-alignment")
        return
    docs = md_files(path)
    for doc in docs:
        for kb in kb_paths:
            cmd = [sys.executable, str(ROOT / "scripts" / "field-alignment-check.py"), str(doc), str(kb), "--json"]
            rc, out, _ = run(cmd)
            if rc == 2:
                continue
            try:
                data = json.loads(out)
            except Exception:
                continue
            for f in data.get("missing", []):
                add_issue(issues, "P1", str(doc), f"字段 {f} 在知识库 {kb.name} 中未定义", "field-alignment")
            for item in data.get("type_mismatch", []):
                add_issue(issues, "P0", str(doc), f"字段 {item['field']} 类型不一致：文档={item['doc']} 知识库={item['knowledge']}", "field-alignment")
            for item in data.get("nullable_mismatch", []):
                add_issue(issues, "P1", str(doc), f"字段 {item['field']} 可空性不一致：文档={item['doc']} 知识库={item['knowledge']}", "field-alignment")


def main() -> None:
    parser = argparse.ArgumentParser(description="全量 QA 审计工具")
    parser.add_argument("path")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    target = Path(args.path)
    if not target.exists():
        print(f"❌ 路径不存在: {target}", file=sys.stderr)
        sys.exit(2)

    issues: list[dict] = []
    audit_doc_validate(target, issues)
    audit_numbering(target, issues)
    audit_required_docs(target, issues)
    audit_sql(target, issues)
    audit_field_alignment(target, issues)

    summary = {"P0": 0, "P1": 0, "P2": 0}
    for issue in issues:
        summary[issue["level"]] = summary.get(issue["level"], 0) + 1
    result = {"path": str(target), "files": len(md_files(target)), "summary": summary, "issues": issues}

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"📊 QA 审计：{target} | 文档 {result['files']} 个 | P0={summary['P0']} P1={summary['P1']} P2={summary['P2']}")
        for issue in issues:
            icon = {"P0": "❌", "P1": "⚠️ ", "P2": "💡"}.get(issue["level"], "-")
            print(f"  {icon} [{issue['level']}] {issue['file']} ({issue['check']}): {issue['msg']}")
        if summary["P0"]:
            print("❌ 有 P0 问题，禁止进入交接")
        else:
            print("✅ 无 P0 问题")
    sys.exit(1 if summary["P0"] else 0)


if __name__ == "__main__":
    main()
