#!/usr/bin/env python3
"""
discipline-lint.py — **legacy 兼容壳** discipline 校验（v3.2.0-dev）

> ⚠️ v3.2.0-dev 起,`discipline-lint.py` 不再是阶段依赖声明的真理来源。
> 新的真理来源是 `scripts/rules-path-lint.py`,它检查每个 SKILL.md 的
> `- Required rules:` 和 `- Required paths:` 声明。
>
> 本脚本仅作为 **legacy 兼容壳**,做两件事:
> 1. 验证 `skills/disciplines/*/SKILL.md` 兼容壳仍存在(7 个)
> 2. 验证兼容壳文本指向匹配的 canonical `rules/*.md`
>
> 不再校验:`requires:` frontmatter / `- Required disciplines:` Contract 行
> (因为新代码已不再写这些)。

参考：docs/plans/2026-06-25-rules-path-refactor.md Task 6

用法：
    python3 scripts/discipline-lint.py <skills_root>
    python3 scripts/discipline-lint.py skills/
    python3 scripts/discipline-lint.py --self-test

退出码：0 = pass;1 = fail;2 = 参数错误
"""
import re
import sys
from pathlib import Path

try:
    from _gate_common import (
        E_FAIL, E_PASS, E_WARN, EXIT_FAIL, EXIT_PASS, EXIT_USAGE,
        CheckResult, GateReport, build_parser, finalize, read_text_or_empty,
    )
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _gate_common import (  # type: ignore
        E_FAIL, E_PASS, E_WARN, EXIT_FAIL, EXIT_PASS, EXIT_USAGE,
        CheckResult, GateReport, build_parser, finalize, read_text_or_empty,
    )


# 7 个 legacy discipline -> canonical rule 的映射
# (legacy discipline 目录名, canonical rule 文件名)
LEGACY_TO_CANONICAL = {
    "ascii-flowchart": "ascii-flowchart",
    "context-pointer": "context-pointer",
    "doc-numbering": "doc-numbering",
    "no-field-guessing": "no-field-guessing",
    "no-self-invent": "no-self-invent",
    "sql-dialect-discipline": "sql-dialect",
    "stage-gate": "stage-gate",
}


def check_wrapper_files_exist(skills_root: Path) -> CheckResult:
    """Check 1: 7 个 legacy discipline 兼容壳文件全部存在。"""
    result = CheckResult(name="wrapper_files_exist", passed=True)
    for disc_name in LEGACY_TO_CANONICAL:
        p = skills_root / "disciplines" / disc_name / "SKILL.md"
        if not p.exists():
            result.passed = False
            result.errors.append(
                f"缺少 legacy 兼容壳 skills/disciplines/{disc_name}/SKILL.md"
            )
    return result


def check_wrapper_points_to_canonical(
    skills_root: Path, repo_root: Path | None = None,
) -> CheckResult:
    """Check 2: 每个兼容壳文本必须提到对应的 canonical rules/*.md。"""
    result = CheckResult(name="wrapper_points_to_canonical", passed=True)
    if repo_root is None:
        # 默认:仓库根 = skills_root.parent
        repo_root = skills_root.parent

    for disc_name, canonical_name in LEGACY_TO_CANONICAL.items():
        wrapper = skills_root / "disciplines" / disc_name / "SKILL.md"
        if not wrapper.exists():
            continue  # 已被 Check 1 捕获
        canonical = repo_root / "rules" / f"{canonical_name}.md"
        if not canonical.exists():
            result.passed = False
            result.errors.append(
                f"兼容壳 {disc_name} 指向的 {canonical} 不存在"
            )
            continue
        text = wrapper.read_text(encoding="utf-8")
        # 兼容壳必须提到 canonical 文件名
        if f"rules/{canonical_name}.md" not in text:
            result.passed = False
            result.errors.append(
                f"兼容壳 skills/disciplines/{disc_name}/SKILL.md 未指向 "
                f"rules/{canonical_name}.md"
            )
    return result


def check_no_divergent_rule_text(skills_root: Path) -> CheckResult:
    """Check 3: 兼容壳不应携带与 canonical 不一致的规则文本(粗略:行数不应过大)。"""
    result = CheckResult(name="no_divergent_rule_text", passed=True)
    MAX_WRAPPER_LINES = 30  # 兼容壳应当 < 30 行
    for disc_name in LEGACY_TO_CANONICAL:
        wrapper = skills_root / "disciplines" / disc_name / "SKILL.md"
        if not wrapper.exists():
            continue
        text = wrapper.read_text(encoding="utf-8")
        line_count = len([l for l in text.splitlines() if l.strip()])
        if line_count > MAX_WRAPPER_LINES:
            result.passed = False
            result.errors.append(
                f"兼容壳 skills/disciplines/{disc_name}/SKILL.md 行数 {line_count} "
                f"超过 {MAX_WRAPPER_LINES}(疑似携带独立规则文本,应迁移到 rules/{disc_name}.md)"
            )
    return result


def run_checks(skills_root: Path, mode: str) -> GateReport:
    report = GateReport(
        script="discipline-lint.py",
        target=str(skills_root),
        mode=mode,
    )
    report.checks = [
        check_wrapper_files_exist(skills_root),
        check_wrapper_points_to_canonical(skills_root),
        check_no_divergent_rule_text(skills_root),
    ]
    return report


def self_test() -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        repo_root = Path(tmp) / "repo"
        repo_root.mkdir()
        skills_root = repo_root / "skills"
        disc_dir = skills_root / "disciplines"
        disc_dir.mkdir(parents=True)
        rules_dir = repo_root / "rules"
        rules_dir.mkdir()
        for disc_name, canonical_name in LEGACY_TO_CANONICAL.items():
            # wrapper
            (disc_dir / disc_name).mkdir()
            (disc_dir / disc_name / "SKILL.md").write_text(
                f"# Compatibility Wrapper\n\n"
                f"deprecated; canonical is `rules/{canonical_name}.md`\n",
                encoding="utf-8",
            )
            # canonical
            (rules_dir / f"{canonical_name}.md").write_text(
                f"# {canonical_name}\n", encoding="utf-8",
            )

        # 1) 应 pass
        report = run_checks(skills_root, "strict")
        if report.has_errors:
            print(f"{E_FAIL} 自检失败:最小 wrapper 树应 pass")
            for c in report.checks:
                for e in c.errors:
                    print(f"   {c.name}: {e}")
            return EXIT_FAIL

        # 2) 删一个 wrapper → fail
        import shutil
        shutil.rmtree(disc_dir / "stage-gate")
        report = run_checks(skills_root, "strict")
        if not report.has_errors:
            print(f"{E_FAIL} 自检失败:删 wrapper 应被报")
            return EXIT_FAIL

        # 恢复并改 wrapper 文本让其不再指向 canonical
        (disc_dir / "stage-gate").mkdir()
        (disc_dir / "stage-gate" / "SKILL.md").write_text(
            "# Compatibility Wrapper\n\n指向错误的路径\n",
            encoding="utf-8",
        )
        report = run_checks(skills_root, "strict")
        if not report.has_errors:
            print(f"{E_FAIL} 自检失败:wrapper 未指向 canonical 应被报")
            return EXIT_FAIL

    print(f"{E_PASS} discipline-lint.py 自检通过 (3 个 check,3 个 case)")
    return EXIT_PASS


def main() -> int:
    parser = build_parser(
        script_name="discipline-lint.py",
        description="legacy discipline 兼容壳校验(非阶段依赖声明真理来源)",
        path_help="skills/ 根目录(默认当前仓库的 skills/)",
    )
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    if not args.path:
        repo = Path(__file__).resolve().parent.parent / "skills"
        if not repo.is_dir():
            parser.error("需要 path 参数,或使用 --self-test")
        skills_root = repo
    else:
        skills_root = Path(args.path)
        if not skills_root.is_dir():
            print(f"{E_FAIL} {skills_root} 不是目录", file=sys.stderr)
            return EXIT_USAGE

    report = run_checks(skills_root, args.mode)
    return finalize(report, as_json=args.json)


if __name__ == "__main__":
    sys.exit(main())
