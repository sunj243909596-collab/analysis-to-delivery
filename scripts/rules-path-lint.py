#!/usr/bin/env python3
"""
rules-path-lint.py — 校验 rules / paths 声明一致性（v4.0.0）

检查项：
1. 所有 rules/*.md 文件存在(目录里不能多也不能少)
2. 所有 paths/*.md 文件存在
3. 每个 user-invoked SKILL.md 恰好有 1 个 "Required rules:" 行
4. 每个 user-invoked SKILL.md 恰好有 1 个 "Required paths:" 行
5. skills/orchestration/analysis-delivery-workflow/SKILL.md 恰好有 1 个 "Required rules:" 行
6. skills/orchestration/analysis-delivery-workflow/SKILL.md 恰好有 1 个 "Required paths:" 行
7. 每个声明的 rule 名是 known
8. 每个声明的 path 名是 known
9. 兼容别名(legacy)不能再作为 canonical 声明出现(sql-dialect-discipline 必须改 sql-dialect)

Task 5 不强制 goal-boundary;Task 9 添加并更新 known-rule 集合。

用法：
    python3 scripts/rules-path-lint.py <skill_root>
    python3 scripts/rules-path-lint.py .               # 默认当前目录
    python3 scripts/rules-path-lint.py --self-test

退出码：0 = pass;1 = fail;2 = 参数错误
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ----- 已知 canonical rule 集合(Task 5) -----
# 注意：Task 9 会向 KNOWN_RULES 添加 "goal-boundary"
KNOWN_RULES: set[str] = {
    "stage-gate",
    "no-field-guessing",
    "no-self-invent",
    "ascii-flowchart",
    "sql-dialect",          # canonical
    "doc-numbering",
    "context-pointer",
    "goal-boundary",        # Task 9
}

# 已废弃 / 仅作兼容壳存在的旧名,任何 SKILL.md 都不应再声明
LEGACY_RULE_ALIASES: set[str] = {
    "sql-dialect-discipline",  # 用 sql-dialect
}

# ----- 已知 canonical path 集合 -----
KNOWN_PATHS: set[str] = {
    "knowledge-path",
    "compliance-path",
    "tech-stack-path",
    "doc-naming-path",
}

# ----- 哪些 SKILL.md 必须声明(required skills) -----
USER_INVOKED_SKILLS_DIR = "skills/user-invoked"
ORCHESTRATION_SKILL = "skills/orchestration/analysis-delivery-workflow/SKILL.md"

# ----- 解析 Required rules / Required paths 行 -----
# 格式：- Required rules: `a`, `b`, `c`
LINE_RE = re.compile(
    r"^\s*-\s*Required\s+(rules|paths)\s*:\s*(.+?)\s*$",
    re.IGNORECASE,
)


@dataclass
class Issue:
    severity: str  # "error" | "warning"
    location: str  # file:line 或 文件名
    message: str


@dataclass
class LintReport:
    errors: list[Issue] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.errors)

    def add_error(self, location: str, message: str) -> None:
        self.errors.append(Issue("error", location, message))

    def add_warning(self, location: str, message: str) -> None:
        self.warnings.append(Issue("warning", location, message))


def _list_skill_files(skill_root: Path) -> list[Path]:
    """列出所有 user-invoked SKILL.md 与编排工作流 SKILL.md。"""
    out: list[Path] = []
    ui = skill_root / USER_INVOKED_SKILLS_DIR
    if ui.is_dir():
        for sub in sorted(ui.iterdir()):
            if sub.is_dir() and (sub / "SKILL.md").exists():
                out.append(sub / "SKILL.md")
    orch = skill_root / ORCHESTRATION_SKILL
    if orch.exists():
        out.append(orch)
    return out


def _parse_declarations(skill_file: Path) -> tuple[list[tuple[str, str, int]], list[Issue]]:
    """从 SKILL.md 解析所有 Required rules / Required paths 行。

    返回 (declarations, issues):declarations 元素是 (kind, name, lineno)。
    """
    decls: list[tuple[str, str, int]] = []
    issues: list[Issue] = []
    text = skill_file.read_text(encoding="utf-8")
    rule_count = 0
    path_count = 0
    for i, line in enumerate(text.splitlines(), start=1):
        m = LINE_RE.match(line)
        if not m:
            continue
        kind = m.group(1).lower()
        names_str = m.group(2)
        # 名字用反引号包裹:`name`
        names = re.findall(r"`([^`]+)`", names_str)
        if kind == "rules":
            rule_count += 1
            if rule_count > 1:
                issues.append(Issue("error", f"{skill_file}:{i}",
                                    f"重复的 Required rules 声明(第 {rule_count} 处)"))
        else:
            path_count += 1
            if path_count > 1:
                issues.append(Issue("error", f"{skill_file}:{i}",
                                    f"重复的 Required paths 声明(第 {path_count} 处)"))
        for n in names:
            decls.append((kind, n.strip(), i))
    if rule_count == 0:
        issues.append(Issue("error", str(skill_file),
                            "缺少 Required rules: 声明"))
    if path_count == 0:
        issues.append(Issue("error", str(skill_file),
                            "缺少 Required paths: 声明"))
    return decls, issues


def lint(skill_root: Path) -> LintReport:
    report = LintReport()

    # 1) rules/*.md 必须存在
    rules_dir = skill_root / "rules"
    if not rules_dir.is_dir():
        report.add_error("rules/", "rules/ 目录不存在")
    else:
        actual_rules = {p.stem for p in rules_dir.glob("*.md")}
        missing = KNOWN_RULES - actual_rules
        extra = actual_rules - KNOWN_RULES
        for r in sorted(missing):
            report.add_error(f"rules/{r}.md", f"缺少已知规则文件 rules/{r}.md")
        for r in sorted(extra):
            report.add_warning(
                f"rules/{r}.md",
                f"rules/{r}.md 未在 KNOWN_RULES 中声明;linter 不会接受引用",
            )

    # 2) paths/*.md 必须存在
    paths_dir = skill_root / "paths"
    if not paths_dir.is_dir():
        report.add_error("paths/", "paths/ 目录不存在")
    else:
        actual_paths = {p.stem for p in paths_dir.glob("*.md")}
        missing_p = KNOWN_PATHS - actual_paths
        extra_p = actual_paths - KNOWN_PATHS
        for p in sorted(missing_p):
            report.add_error(f"paths/{p}.md", f"缺少已知路径文件 paths/{p}.md")
        for p in sorted(extra_p):
            report.add_warning(
                f"paths/{p}.md",
                f"paths/{p}.md 未在 KNOWN_PATHS 中声明;linter 不会接受引用",
            )

    # 3-9) 每个 SKILL.md 的 Required 声明
    for skill_file in _list_skill_files(skill_root):
        decls, issues = _parse_declarations(skill_file)
        for issue in issues:
            report.errors.append(issue)
        for kind, name, lineno in decls:
            if kind == "rules":
                if name in LEGACY_RULE_ALIASES:
                    report.add_error(
                        f"{skill_file}:{lineno}",
                        f"legacy 规则名 `{name}` 不应再被声明;canonical 是 `sql-dialect`",
                    )
                    continue
                if name not in KNOWN_RULES:
                    report.add_error(
                        f"{skill_file}:{lineno}",
                        f"未知规则 `{name}`(不在 KNOWN_RULES 集合内)",
                    )
            else:  # paths
                if name not in KNOWN_PATHS:
                    report.add_error(
                        f"{skill_file}:{lineno}",
                        f"未知路径 `{name}`(不在 KNOWN_PATHS 集合内)",
                    )

    return report


def _print_report(report: LintReport) -> None:
    print("=" * 70)
    print("rules-path-lint 结果")
    print("=" * 70)
    for issue in report.errors:
        print(f"[ERROR] {issue.location}: {issue.message}")
    for issue in report.warnings:
        print(f"[WARN]  {issue.location}: {issue.message}")
    print("-" * 70)
    print(f"errors={len(report.errors)}, warnings={len(report.warnings)}")


def self_test() -> int:
    """自检：覆盖 pass / unknown rule / unknown path / 重复 / legacy 名 / missing declaration。"""
    import tempfile

    # --- 准备最小可工作 skill_root 骨架 ---
    def make_minimal(root: Path) -> None:
        (root / "rules").mkdir()
        for r in KNOWN_RULES:
            (root / "rules" / f"{r}.md").write_text(f"# {r}\n", encoding="utf-8")
        (root / "paths").mkdir()
        for p in KNOWN_PATHS:
            (root / "paths" / f"{p}.md").write_text(f"# {p}\n", encoding="utf-8")
        ui = root / "skills" / "user-invoked"
        ui.mkdir(parents=True)
        (ui / "demo").mkdir()
        (ui / "demo" / "SKILL.md").write_text(
            "## Contract\n\n- Required rules: `stage-gate`, `no-field-guessing`\n"
            "- Required paths: `knowledge-path`, `doc-naming-path`\n",
            encoding="utf-8",
        )
        orch = root / "skills" / "orchestration" / "analysis-delivery-workflow"
        orch.mkdir(parents=True)
        (orch / "SKILL.md").write_text(
            "## Contract\n\n- Required rules: `stage-gate`, `doc-numbering`\n"
            "- Required paths: `knowledge-path`, `tech-stack-path`\n",
            encoding="utf-8",
        )

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "ok"
        root.mkdir()
        make_minimal(root)
        rep = lint(root)
        if rep.has_errors:
            print("[FAIL] minimal pass case has errors:")
            _print_report(rep)
            return 1
        # 注入未知 rule
        bad_rule = root / "skills" / "user-invoked" / "demo" / "SKILL.md"
        bad_rule.write_text(
            "## Contract\n\n- Required rules: `stage-gate`, `no-such-rule`\n"
            "- Required paths: `knowledge-path`, `doc-naming-path`\n",
            encoding="utf-8",
        )
        rep = lint(root)
        if not rep.has_errors:
            print("[FAIL] unknown rule should fail")
            return 1
        # 恢复并注入未知 path
        bad_rule.write_text(
            "## Contract\n\n- Required rules: `stage-gate`, `no-field-guessing`\n"
            "- Required paths: `knowledge-path`, `bogus-path`\n",
            encoding="utf-8",
        )
        rep = lint(root)
        if not rep.has_errors:
            print("[FAIL] unknown path should fail")
            return 1
        # 恢复并注入重复
        bad_rule.write_text(
            "## Contract\n\n"
            "- Required rules: `stage-gate`\n"
            "- Required rules: `no-field-guessing`\n"
            "- Required paths: `knowledge-path`\n",
            encoding="utf-8",
        )
        rep = lint(root)
        if not rep.has_errors:
            print("[FAIL] duplicate rules should fail")
            return 1
        # 恢复并注入 legacy 名
        bad_rule.write_text(
            "## Contract\n\n- Required rules: `sql-dialect-discipline`\n"
            "- Required paths: `knowledge-path`\n",
            encoding="utf-8",
        )
        rep = lint(root)
        if not rep.has_errors:
            print("[FAIL] legacy sql-dialect-discipline should fail")
            return 1
        # 恢复并注入 missing declaration
        bad_rule.write_text(
            "## Contract\n\n- Required rules: `stage-gate`\n",
            encoding="utf-8",
        )
        rep = lint(root)
        if not rep.has_errors:
            print("[FAIL] missing paths declaration should fail")
            return 1
        # 缺 rules/*.md 文件
        bad_rule.write_text(
            "## Contract\n\n- Required rules: `stage-gate`\n"
            "- Required paths: `knowledge-path`\n",
            encoding="utf-8",
        )
        (root / "rules" / "stage-gate.md").unlink()
        rep = lint(root)
        if not rep.has_errors:
            print("[FAIL] missing rules file should fail")
            return 1
    print("[PASS] rules-path-lint self-test")
    return 0


def main() -> int:
    args = sys.argv[1:]
    if "--self-test" in args:
        return self_test()
    skill_root = Path(args[0]) if args else Path(".")
    if not skill_root.is_dir():
        print(f"[ERROR] {skill_root} 不是目录", file=sys.stderr)
        return 2
    report = lint(skill_root)
    _print_report(report)
    return 1 if report.has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
