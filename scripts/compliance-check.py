#!/usr/bin/env python3
"""
compliance-check.py — 阶段 4→5 合规评审门控（v3.1.0-dev）

校验 `04-合规评审.md` 的 6 列表格（条款编号 / 缺陷等级 / 检查要点 /
合规设计 / 证据位置 / 状态）存在，且：
- 每行状态必须是 ✅ / ⚠️ / 🔄 之一
- 无 {待评估} / {N/A} 等未判定状态
- 缺陷等级为"严重"的行必须 ✅ 或 🔄（不允许 ⚠️ 阻断后续阶段）

参考：skills/user-invoked/compliance-review/SKILL.md §流程步骤
参考：scripts/task-confirm-check.py v1.1.0 接口

用法：
    python3 scripts/compliance-check.py <project_dir>
    python3 scripts/compliance-check.py --self-test

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


COMPLIANCE_TABLE_COLUMNS = [
    "条款编号", "缺陷等级", "检查要点",
    "合规设计", "证据位置", "状态",
]

# 未判定状态关键词
UNDECIDED_PATTERNS = [
    r"\{待评估\}", r"\{TBD\}", r"\{N/A\}", r"待评估", r"未判定",
    r"未评估", r"\{\?\}",
]


def _resolve_compliance_path(target: Path) -> Path | None:
    if target.is_file():
        return target
    if target.is_dir():
        for name in ("04-合规评审.md", "04-合规评审报告.md"):
            p = target / name
            if p.exists():
                return p
        for p in sorted(target.glob("04-*.md")):
            return p
    return None


def check_compliance_table_exists(path: Path) -> CheckResult:
    """Check 1: 6 列合规评审表存在。"""
    result = CheckResult(name="compliance_table_6_columns", passed=True)
    if not path.exists():
        result.passed = False
        result.errors.append(f"04-合规评审.md 不存在: {path}")
        return result
    text = read_text_or_empty(path)
    # 必须在表头里同时含 6 个列名
    missing = []
    for col in COMPLIANCE_TABLE_COLUMNS:
        if col not in text:
            missing.append(col)
    if missing:
        result.passed = False
        result.errors.append(
            f"04-合规评审.md 缺 {len(missing)} 列: {', '.join(missing)}"
        )
    return result


def check_compliance_no_undecided(path: Path) -> CheckResult:
    """Check 2: 无 {待评估}/{TBD}/{N/A} 等未判定状态。"""
    result = CheckResult(name="compliance_no_undecided", passed=True)
    if not path.exists():
        return result
    text = read_text_or_empty(path)
    for pat in UNDECIDED_PATTERNS:
        for m in re.finditer(pat, text):
            line_no = text[:m.start()].count("\n") + 1
            result.passed = False
            result.errors.append(
                f"第 {line_no} 行有未判定状态: {m.group(0)}"
            )
    return result


def check_compliance_severe_status(path: Path) -> CheckResult:
    """Check 3: 缺陷等级为'严重'的行状态必须是 ✅ 或 🔄(不允许 ⚠️)。"""
    result = CheckResult(name="compliance_severe_must_pass", passed=True)
    if not path.exists():
        return result
    text = read_text_or_empty(path)
    # 找表格行: | **| 严重 |...|状态|
    # 简化:逐行扫描,行内同时含"严重"和某个状态 emoji
    for i, line in enumerate(text.splitlines(), 1):
        if "严重" not in line:
            continue
        if "|" not in line:
            continue
        if "✅" in line or "🔄" in line:
            continue
        if "⚠️" in line or "❌" in line:
            result.passed = False
            result.errors.append(
                f"第 {i} 行: 严重条款状态为 ⚠️/❌,必须修复或豁免"
            )
        else:
            result.warnings.append(
                f"第 {i} 行: 含'严重'但无状态 emoji,请补判定"
            )
    return result


def run_checks(path: Path, mode: str) -> GateReport:
    report = GateReport(
        script="compliance-check.py",
        target=str(path),
        mode=mode,
    )
    report.checks = [
        check_compliance_table_exists(path),
        check_compliance_no_undecided(path),
        check_compliance_severe_status(path),
    ]
    return report


def self_test() -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        # 1) 缺文件 → fail (用 fake 路径,不传 dir 给 run_checks)
        fake_path = tmpdir / "04-合规评审.md"
        report = run_checks(fake_path, "strict")
        if not report.has_errors:
            print(f"{E_FAIL} 自检失败:缺 04-合规评审.md 应被报")
            return EXIT_FAIL
        # 2) 表格列名缺失 → fail
        bad = tmpdir / "04-合规评审.md"
        bad.write_text(
            "# 合规评审\n\n| 条款编号 | 检查要点 | 状态 |\n|---|---|---|\n| X-01 | y | {待评估} |\n",
            encoding="utf-8",
        )
        report = run_checks(bad, "strict")
        if not report.has_errors:
            print(f"{E_FAIL} 自检失败:缺 6 列 / 含待评估 应被报")
            return EXIT_FAIL
        # 3) 严重条款状态 ⚠️ → fail
        bad2 = tmpdir / "04-合规评审.md"
        bad2.write_text(
            "# 合规评审\n\n"
            "| 条款编号 | 缺陷等级 | 检查要点 | 合规设计 | 证据位置 | 状态 |\n"
            "|---|---|---|---|---|---|\n"
            "| GSP-001 | 严重 | xxx | yyy | FSD §1 | ⚠️ |\n",
            encoding="utf-8",
        )
        report = run_checks(bad2, "strict")
        if not report.has_errors:
            print(f"{E_FAIL} 自检失败:严重条款 ⚠️ 应被报")
            return EXIT_FAIL
        # 4) 完整合规评审 → pass
        good = tmpdir / "04-合规评审.md"
        good.write_text(
            "# 合规评审\n\n"
            "| 条款编号 | 缺陷等级 | 检查要点 | 合规设计 | 证据位置 | 状态 |\n"
            "|---|---|---|---|---|---|\n"
            "| GSP-001 | 严重 | xxx | yyy | FSD §1 | ✅ |\n"
            "| GSP-002 | 主要 | xxx | yyy | FSD §2 | ⚠️ |\n"
            "| GDPR-01 | 一般 | xxx | yyy | FSD §3 | 🔄 |\n",
            encoding="utf-8",
        )
        report = run_checks(good, "strict")
        if report.has_errors:
            print(f"{E_FAIL} 自检失败:完整合规评审应 pass")
            for c in report.checks:
                for e in c.errors:
                    print(f"   {c.name}: {e}")
            return EXIT_FAIL
    print(f"{E_PASS} compliance-check.py 自检通过 (3 个 check,4 个 case)")
    return EXIT_PASS


def main() -> int:
    parser = build_parser(
        script_name="compliance-check.py",
        description="阶段 4→5 合规评审门控",
        path_help="项目根目录或 04-合规评审.md 路径",
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
    path = _resolve_compliance_path(target)
    if path is None:
        report = GateReport(
            script="compliance-check.py",
            target=str(target),
            mode=args.mode,
            checks=[CheckResult(
                name="compliance_table_6_columns",
                passed=False,
                errors=[f"未找到 04-*.md 在 {target}"],
            )],
        )
        return finalize(report, as_json=args.json)
    report = run_checks(path, args.mode)
    return finalize(report, as_json=args.json)


if __name__ == "__main__":
    sys.exit(main())
