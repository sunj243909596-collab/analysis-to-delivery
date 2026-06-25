#!/usr/bin/env python3
"""
testcase-coverage-check.py — 阶段 5→6 测试用例覆盖门控（v3.1.0-dev）

校验 `07-测试用例设计.md` 5 大类用例各至少 1 条：
- 正常路径
- 边界条件
- 异常路径
- 合规校验
- 性能/安全

每条用例必须带 TC 编号（TC-001 / TC-1 / 1.1 等格式）。

参考：skills/user-invoked/test-case-design/SKILL.md §2 覆盖范围
参考：scripts/task-confirm-check.py v1.1.0 接口

用法：
    python3 scripts/testcase-coverage-check.py <project_dir>
    python3 scripts/testcase-coverage-check.py --self-test

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


# 5 大类及其常见标题关键词（任一匹配即视为该类存在）
CATEGORIES = [
    ("正常路径", ["正常路径", "正常", "happy path", "主流程", "正常场景"]),
    ("边界条件", ["边界条件", "边界", "极值", "边界值"]),
    ("异常路径", ["异常路径", "异常", "错误处理", "异常场景"]),
    ("合规校验", ["合规校验", "合规", "GSP", "HIPAA", "GDPR", "合规性"]),
    ("性能/安全", ["性能/安全", "性能", "安全", "性能安全", "并发"]),
]

# 用例编号正则:支持 TC-001 / TC-N-001 / TC_N-001 / TC001 / 1.1 多种格式
TC_ID_PATTERN = re.compile(r"\bTC[-_]?[A-Za-z]?[-_]?\d+\b|\b\d+\.\d+\b")


def _resolve_testcase_path(target: Path) -> Path | None:
    if target.is_file():
        return target
    if target.is_dir():
        for name in ("07-测试用例设计.md", "07-测试用例.md", "07-TEST_CASE.md"):
            p = target / name
            if p.exists():
                return p
        for p in sorted(target.glob("07-*.md")):
            return p
    return None


def _find_categories(text: str) -> dict[str, list[str]]:
    """
    返回 {类别: [匹配该类的行号]}。
    匹配规则: 行内同时含"## 类别名" 2 级标题 或 "### 类别名" 3 级标题,
    直到下一个 2 级标题为止算该类。
    """
    lines = text.splitlines()
    cat_lines: dict[str, list[int]] = {c: [] for c, _ in CATEGORIES}
    current_cat: str | None = None
    for i, line in enumerate(lines, 1):
        m = re.match(r"^#{2,3}\s+(.+?)\s*$", line)
        if m:
            heading = m.group(1).strip()
            current_cat = None
            for cat, keywords in CATEGORIES:
                if any(kw in heading for kw in keywords):
                    current_cat = cat
                    break
            continue
        if current_cat and TC_ID_PATTERN.search(line):
            cat_lines[current_cat].append(i)
    return cat_lines


def check_5_categories_covered(path: Path) -> CheckResult:
    """Check 1: 5 大类各至少 1 条用例。"""
    result = CheckResult(name="testcase_5_categories", passed=True)
    if not path.exists():
        result.passed = False
        result.errors.append(f"07-测试用例设计.md 不存在: {path}")
        return result
    text = read_text_or_empty(path)
    cat_lines = _find_categories(text)
    missing = [c for c in CATEGORIES if not cat_lines[c[0]]]
    if missing:
        result.passed = False
        result.errors.append(
            f"5 大类缺 {len(missing)} 类: {', '.join(c[0] for c in missing)}"
        )
    # 统计
    for cat, _ in CATEGORIES:
        n = len(cat_lines[cat])
        if n > 0:
            result.warnings.append(f"  {cat}: {n} 条用例")
    return result


def check_each_testcase_has_id(path: Path) -> CheckResult:
    """Check 2: 至少有 5 个 TC 编号(粗略校验:每条用例都有 ID)。"""
    result = CheckResult(name="testcase_has_id", passed=True)
    if not path.exists():
        return result
    text = read_text_or_empty(path)
    tc_ids = set(TC_ID_PATTERN.findall(text))
    if len(tc_ids) < 5:
        result.passed = False
        result.errors.append(
            f"仅找到 {len(tc_ids)} 个 TC 编号(至少 5 个)"
        )
    return result


def run_checks(path: Path, mode: str) -> GateReport:
    report = GateReport(
        script="testcase-coverage-check.py",
        target=str(path),
        mode=mode,
    )
    report.checks = [
        check_5_categories_covered(path),
        check_each_testcase_has_id(path),
    ]
    return report


def self_test() -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        # 1) 缺文件 → fail (用 fake 路径)
        fake_path = tmpdir / "07-测试用例设计.md"
        report = run_checks(fake_path, "strict")
        if not report.has_errors:
            print(f"{E_FAIL} 自检失败:缺 07-测试用例设计.md 应被报")
            return EXIT_FAIL
        # 2) 只 3 大类 → fail
        bad = tmpdir / "07-测试用例设计.md"
        bad.write_text(
            "# 测试用例\n\n"
            "## 正常路径\nTC-001 xxx\nTC-002 yyy\n\n"
            "## 边界条件\nTC-003 zzz\n\n"
            "## 异常路径\nTC-004 www\n",
            encoding="utf-8",
        )
        report = run_checks(bad, "strict")
        if not report.has_errors:
            print(f"{E_FAIL} 自检失败:只 3 大类应被报")
            return EXIT_FAIL
        # 3) 5 大类齐 → pass
        good = tmpdir / "07-测试用例设计.md"
        good.write_text(
            "# 测试用例\n\n"
            "## 正常路径\nTC-001 主流程\nTC-002 happy path\n\n"
            "## 边界条件\nTC-003 空值\nTC-004 极值\n\n"
            "## 异常路径\nTC-005 错误输入\nTC-006 超时\n\n"
            "## 合规校验\nTC-007 GSP-001 审计字段\n\n"
            "## 性能/安全\nTC-008 并发 100\nTC-009 SQL 注入\n",
            encoding="utf-8",
        )
        report = run_checks(good, "strict")
        if report.has_errors:
            print(f"{E_FAIL} 自检失败:5 大类齐应 pass")
            for c in report.checks:
                for e in c.errors:
                    print(f"   {c.name}: {e}")
            return EXIT_FAIL
    print(f"{E_PASS} testcase-coverage-check.py 自检通过 (2 个 check,3 个 case)")
    return EXIT_PASS


def main() -> int:
    parser = build_parser(
        script_name="testcase-coverage-check.py",
        description="阶段 5→6 测试用例覆盖门控",
        path_help="项目根目录或 07-测试用例设计.md 路径",
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
    path = _resolve_testcase_path(target)
    if path is None:
        report = GateReport(
            script="testcase-coverage-check.py",
            target=str(target),
            mode=args.mode,
            checks=[CheckResult(
                name="testcase_5_categories",
                passed=False,
                errors=[f"未找到 07-*.md 在 {target}"],
            )],
        )
        return finalize(report, as_json=args.json)
    report = run_checks(path, args.mode)
    return finalize(report, as_json=args.json)


if __name__ == "__main__":
    sys.exit(main())
