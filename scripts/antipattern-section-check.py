#!/usr/bin/env python3
"""
antipattern-section-check.py — 反模式章节门控（v3.1.0-dev）

校验 9 个 user-invoked SKILL.md 含 `## 反模式` 二级标题 + ≥3 条 ❌ 开头列表项。

参考：plan.md §P3-2
参考：scripts/task-confirm-check.py v1.1.0 接口

用法：
    python3 scripts/antipattern-section-check.py skills/user-invoked/
    python3 scripts/antipattern-section-check.py --self-test

退出码：0 = pass(strict)/ 仅 warning(loose);1 = fail;2 = 参数错误
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


# 9 个 user-invoked skill 名称白名单
USER_INVOKED_SKILLS = {
    "compliance-review",
    "dev-design",
    "grill-task",
    "handoff",
    "qa-audit",
    "setup-analysis-delivery",
    "test-case-design",
    "to-brd",
    "to-prd",
}

# 反模式段落正则
ANTIPATTERN_HEADING_RE = re.compile(r"^##\s+反模式\s*$", re.MULTILINE)
ANTIPATTERN_ITEM_RE = re.compile(r"^\s*-\s*❌\s+\S", re.MULTILINE)

MIN_ITEMS = 3


def _iter_user_invoked(target: Path) -> list[Path]:
    """收集 target 下所有 user-invoked SKILL.md。"""
    if target.is_file():
        return [target]
    out = []
    for name in USER_INVOKED_SKILLS:
        p = target / name / "SKILL.md"
        if p.exists():
            out.append(p)
    # 也收集其他在 user-invoked 下的(未来扩展)
    for p in sorted(target.rglob("SKILL.md")):
        if p not in out:
            out.append(p)
    return out


def check_antipattern_section(path: Path) -> CheckResult:
    """Check 1: SKILL.md 含 `## 反模式` 二级标题。"""
    result = CheckResult(name="antipattern_section_exists", passed=True)
    text = read_text_or_empty(path)
    if not ANTIPATTERN_HEADING_RE.search(text):
        result.passed = False
        result.errors.append(
            f"{path.parent.name}/SKILL.md 缺 '## 反模式' 二级标题"
        )
    return result


def check_antipattern_items(path: Path) -> CheckResult:
    """Check 2: `## 反模式` 段下 ≥3 条 `❌` 开头列表项。"""
    result = CheckResult(name="antipattern_items_min_3", passed=True)
    text = read_text_or_empty(path)
    m = ANTIPATTERN_HEADING_RE.search(text)
    if not m:
        # 已由 Check 1 报,跳过
        return result
    # 取 ## 反模式 段到下一个 ## 或文末
    after_start = m.end()
    rest = text[after_start:]
    next_h2 = re.search(r"^##\s+", rest, re.MULTILINE)
    section = rest[: next_h2.start()] if next_h2 else rest
    items = ANTIPATTERN_ITEM_RE.findall(section)
    if len(items) < MIN_ITEMS:
        result.passed = False
        result.errors.append(
            f"{path.parent.name}/SKILL.md: '## 反模式' 段仅 {len(items)} 条 ❌ "
            f"(要求 ≥ {MIN_ITEMS})"
        )
    else:
        result.warnings.append(f"  {path.parent.name}: {len(items)} 条 ❌")
    return result


def run_checks_for_file(path: Path) -> list[CheckResult]:
    return [
        check_antipattern_section(path),
        check_antipattern_items(path),
    ]


def run_checks(target: Path, mode: str) -> GateReport:
    report = GateReport(
        script="antipattern-section-check.py",
        target=str(target),
        mode=mode,
    )
    files = _iter_user_invoked(target)
    if not files:
        report.checks = [CheckResult(
            name="antipattern_section_exists",
            passed=False,
            errors=[f"在 {target} 下未找到任何 user-invoked SKILL.md"],
        )]
        return report
    for f in files:
        report.checks.extend(run_checks_for_file(f))
    return report


def self_test() -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        skill_dir = tmpdir / "grill-task"
        skill_dir.mkdir()
        # 1) 缺 ## 反模式 → fail
        bad1 = skill_dir / "SKILL.md"
        bad1.write_text("# grill-task\n\n## 结束条件\n- [ ] x\n", encoding="utf-8")
        report = run_checks(tmpdir, "strict")
        if not report.has_errors:
            print(f"{E_FAIL} 自检失败:缺 ## 反模式 应被报")
            return EXIT_FAIL
        # 2) ## 反模式 但 < 3 条 ❌ → fail
        bad2 = skill_dir / "SKILL.md"
        bad2.write_text(
            "# grill-task\n\n## 反模式\n- ❌ only one\n",
            encoding="utf-8",
        )
        report = run_checks(tmpdir, "strict")
        if not any("≥" in e for c in report.checks for e in c.errors):
            print(f"{E_FAIL} 自检失败:反模式条数不足应被报")
            return EXIT_FAIL
        # 3) 完整 → pass
        good = skill_dir / "SKILL.md"
        good.write_text(
            "# grill-task\n\n## 反模式\n"
            "- ❌ x1\n- ❌ x2\n- ❌ x3\n- ❌ x4\n\n## 结束条件\n",
            encoding="utf-8",
        )
        report = run_checks(tmpdir, "strict")
        if report.has_errors:
            print(f"{E_FAIL} 自检失败:完整反模式应 pass")
            for c in report.checks:
                for e in c.errors:
                    print(f"   {c.name}: {e}")
            return EXIT_FAIL
    print(f"{E_PASS} antipattern-section-check.py 自检通过 (2 check,3 case)")
    return EXIT_PASS


def main() -> int:
    parser = build_parser(
        script_name="antipattern-section-check.py",
        description="user-invoked SKILL.md 反模式章节门控",
        path_help="skills/user-invoked/ 目录",
    )
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    if not args.path:
        parser.error("需要 path 参数,或使用 --self-test")
    target = Path(args.path)
    if not target.exists():
        print(f"{E_FAIL} {target} 不存在", file=sys.stderr)
        return EXIT_USAGE
    report = run_checks(target, args.mode)
    return finalize(report, as_json=args.json)


if __name__ == "__main__":
    sys.exit(main())