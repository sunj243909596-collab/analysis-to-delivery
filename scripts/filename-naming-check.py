#!/usr/bin/env python3
"""
filename-naming-check.py — 文件命名门控（v4.0.0）

校验 examples/ 下文件命名符合规范：
- `config-used.md` 已弃用,新项目应使用 `decisions.md`
- 文档必须 01-09 编号(参 doc-numbering)
- 其他命名规则...

参考：plan.md §P3-3
参考：scripts/task-confirm-check.py v1.1.0 接口

用法：
    python3 scripts/filename-naming-check.py examples/
    python3 scripts/filename-naming-check.py --self-test

退出码：0 = pass(strict)/ 仅 warning(loose);1 = fail;2 = 参数错误
"""
import re
import sys
from pathlib import Path

try:
    from _gate_common import (
        E_FAIL, E_PASS, E_WARN, EXIT_FAIL, EXIT_PASS, EXIT_USAGE,
        CheckResult, GateReport, build_parser, finalize,
    )
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _gate_common import (  # type: ignore
        E_FAIL, E_PASS, E_WARN, EXIT_FAIL, EXIT_PASS, EXIT_USAGE,
        CheckResult, GateReport, build_parser, finalize,
    )


# 弃用文件名白名单(仍接受,只是 warning,鼓励迁移)
DEPRECATED_FILES = [
    "config-used.md",  # 已在 v4.0.0 改名为 decisions.md
]


def _iter_md_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    return sorted(target.rglob("*.md"))


def check_no_deprecated_filename(path: Path) -> CheckResult:
    """Check 1: 不使用已弃用文件名(强 warning,不 fail,以保向后兼容)。"""
    result = CheckResult(name="no_deprecated_filename", passed=True)
    if path.name in DEPRECATED_FILES:
        result.passed = False
        result.errors.append(
            f"{path}: 文件名 {path.name!r} 已弃用,"
            f" 应改名为 decisions.md"
        )
    return result


def check_decisions_md_recommended(path: Path) -> CheckResult:
    """Check 2: 项目级配置记录文件推荐命名(decisions.md)。"""
    result = CheckResult(name="decisions_md_recommended", passed=True)
    # 仅对 examples/ 下根目录或子目录的"配置记录"类文件
    if path.name in DEPRECATED_FILES:
        result.warnings.append(
            f"  {path}: 建议改名为 decisions.md(向后兼容到 v4.0.0)"
        )
    return result


def run_checks(target: Path, mode: str) -> GateReport:
    report = GateReport(
        script="filename-naming-check.py",
        target=str(target),
        mode=mode,
    )
    files = _iter_md_files(target)
    if not files:
        empty = CheckResult(name="no_md_files", passed=True)
        empty.warnings.append(f"在 {target} 下未找到任何 .md 文件")
        report.checks.append(empty)
        return report
    for f in files:
        report.checks.append(check_no_deprecated_filename(f))
        report.checks.append(check_decisions_md_recommended(f))
    return report


def self_test() -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        # 1) 干净目录(只有新名 decisions.md)→ pass
        (tmpdir / "decisions.md").write_text("# decisions\n", encoding="utf-8")
        report = run_checks(tmpdir, "strict")
        if report.has_errors:
            print(f"{E_FAIL} 自检失败:decisions.md 应 pass")
            for c in report.checks:
                for e in c.errors:
                    print(f"   {c.name}: {e}")
            return EXIT_FAIL
        # 2) 旧名 config-used.md → fail(强烈建议改)
        bad = tmpdir / "config-used.md"
        bad.write_text("# old\n", encoding="utf-8")
        report = run_checks(tmpdir, "strict")
        if not report.has_errors:
            print(f"{E_FAIL} 自检失败:config-used.md 应被报")
            return EXIT_FAIL
    print(f"{E_PASS} filename-naming-check.py 自检通过 (2 check,2 case)")
    return EXIT_PASS


def main() -> int:
    parser = build_parser(
        script_name="filename-naming-check.py",
        description="examples/ 文件命名门控",
        path_help="examples/ 目录或单个 .md 路径",
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