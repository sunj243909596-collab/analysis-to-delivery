#!/usr/bin/env python3
"""
dev-design-backtest.py — 阶段 7→8 设计回测门控（v4.0.0）

校验 `08-设计回测报告.md` 4 大类回测无 ❌：
- 数据模型回测
- 业务规则回测
- 状态机回测
- 字段对齐回测

参考：skills/disciplines/stage-gate/SKILL.md §设计回测 4 大类
参考：scripts/task-confirm-check.py v1.1.0 接口

注意：这是 **门控脚本** —— 只校验"4 大类标题 + 无 ❌"。
真正的回测执行（连测试库、跑样本数据）超出本文档范围，
实际执行由 `dev-design` skill 在阶段 7 末尾手动跑（详见
references/design-backtest.md）。

用法：
    python3 scripts/dev-design-backtest.py <project_dir>
    python3 scripts/dev-design-backtest.py --self-test

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


BACKTEST_CATEGORIES = [
    "数据模型回测",
    "业务规则回测",
    "状态机回测",
    "字段对齐回测",
]


def _resolve_backtest_path(target: Path) -> Path | None:
    if target.is_file():
        return target
    if target.is_dir():
        for name in ("08-设计回测报告.md", "08-设计回测.md"):
            p = target / name
            if p.exists():
                return p
        for p in sorted(target.glob("08-*.md")):
            return p
    return None


def check_4_categories_present(path: Path) -> CheckResult:
    """Check 1: 4 大类回测章节都存在。"""
    result = CheckResult(name="backtest_4_categories", passed=True)
    if not path.exists():
        result.passed = False
        result.errors.append(f"08-设计回测报告.md 不存在: {path}")
        return result
    text = read_text_or_empty(path)
    missing = [c for c in BACKTEST_CATEGORIES if c not in text]
    if missing:
        result.passed = False
        result.errors.append(
            f"4 大类回测缺 {len(missing)} 类: {', '.join(missing)}"
        )
    return result


def check_no_fail_marker(path: Path) -> CheckResult:
    """Check 2: 4 大类下无 ❌ 判定(允许 ⚠️/✅)。"""
    result = CheckResult(name="backtest_no_fail", passed=True)
    if not path.exists():
        return result
    text = read_text_or_empty(path)
    # 找每类下第一个 ❌ 的行号
    for cat in BACKTEST_CATEGORIES:
        # 找该类标题
        m = re.search(
            rf"^#{{2,4}}\s+.*{re.escape(cat)}.*$",
            text,
            re.MULTILINE,
        )
        if not m:
            continue  # 已被 Check 1 捕获
        # 找该类下到下一同级标题之间的内容
        start = m.end()
        # 找下一个 # 标题
        next_h = re.search(r"^#{1,4}\s+\S+", text[start:], re.MULTILINE)
        end = start + next_h.start() if next_h else len(text)
        section = text[start:end]
        if "❌" in section:
            for line_no, line in enumerate(section.splitlines(), 1):
                if "❌" in line:
                    abs_line = text[:start].count("\n") + line_no
                    result.passed = False
                    result.errors.append(
                        f"{cat} 第 {abs_line} 行: 含 ❌,必须修复或豁免"
                    )
    return result


def check_conclusion_present(path: Path) -> CheckResult:
    """Check 3: 整体结论存在(✅/⚠️/❌)。"""
    result = CheckResult(name="backtest_conclusion", passed=True)
    if not path.exists():
        return result
    text = read_text_or_empty(path)
    # 找"整体结论"/"回测结论"行
    if not re.search(r"(整体结论|回测结论|结论[::])", text):
        result.warnings.append("未找到'整体结论'或'回测结论'章节")
    # 找 ✅ 整体通过或 ⚠️ 部分通过
    if "✅" in text and ("整体通过" in text or "全部通过" in text):
        return result
    if "⚠️" in text and ("部分通过" in text or "带条件通过" in text):
        return result
    if "❌" in text:
        result.warnings.append("整体结论含 ❌,可能被 Check 2 捕获")
    else:
        result.warnings.append("未识别到明确的整体结论 emoji")
    return result


def run_checks(path: Path, mode: str) -> GateReport:
    report = GateReport(
        script="dev-design-backtest.py",
        target=str(path),
        mode=mode,
    )
    report.checks = [
        check_4_categories_present(path),
        check_no_fail_marker(path),
        check_conclusion_present(path),
    ]
    return report


def self_test() -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        # 1) 缺文件 → fail (用 fake 路径)
        fake_path = tmpdir / "08-设计回测报告.md"
        report = run_checks(fake_path, "strict")
        if not report.has_errors:
            print(f"{E_FAIL} 自检失败:缺 08-设计回测报告.md 应被报")
            return EXIT_FAIL
        # 2) 4 类齐但其中一类有 ❌ → fail
        bad = tmpdir / "08-设计回测报告.md"
        bad.write_text(
            "# 设计回测\n\n"
            "## 数据模型回测\n✅ 全部通过\n\n"
            "## 业务规则回测\n❌ TC-001 失败\n\n"
            "## 状态机回测\n✅ 通过\n\n"
            "## 字段对齐回测\n✅ 通过\n",
            encoding="utf-8",
        )
        report = run_checks(bad, "strict")
        if not report.has_errors:
            print(f"{E_FAIL} 自检失败:含 ❌ 应被报")
            return EXIT_FAIL
        # 3) 完整 4 类 + 无 ❌ + 有结论 → pass
        good = tmpdir / "08-设计回测报告.md"
        good.write_text(
            "# 设计回测\n\n"
            "## 数据模型回测\n✅ DDL/索引/查询全过\n\n"
            "## 业务规则回测\n✅ 关键场景手工重跑过\n\n"
            "## 状态机回测\n✅ 历史单据回放通过\n\n"
            "## 字段对齐回测\n✅ 文档 vs 知识库 vs 生产库一致\n\n"
            "## 整体结论\n\n✅ 全部通过,可进入阶段 8 (QA)\n",
            encoding="utf-8",
        )
        report = run_checks(good, "strict")
        if report.has_errors:
            print(f"{E_FAIL} 自检失败:完整回测应 pass")
            for c in report.checks:
                for e in c.errors:
                    print(f"   {c.name}: {e}")
            return EXIT_FAIL
    print(f"{E_PASS} dev-design-backtest.py 自检通过 (3 个 check,3 个 case)")
    return EXIT_PASS


def main() -> int:
    parser = build_parser(
        script_name="dev-design-backtest.py",
        description="阶段 7→8 设计回测门控",
        path_help="项目根目录或 08-设计回测报告.md 路径",
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
    path = _resolve_backtest_path(target)
    if path is None:
        report = GateReport(
            script="dev-design-backtest.py",
            target=str(target),
            mode=args.mode,
            checks=[CheckResult(
                name="backtest_4_categories",
                passed=False,
                errors=[f"未找到 08-*.md 在 {target}"],
            )],
        )
        return finalize(report, as_json=args.json)
    report = run_checks(path, args.mode)
    return finalize(report, as_json=args.json)


if __name__ == "__main__":
    sys.exit(main())
