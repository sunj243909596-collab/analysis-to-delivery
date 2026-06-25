#!/usr/bin/env python3
"""
description-lint.py — SKILL.md description 字段长度门控（v3.1.0-dev）

校验 `skills/` 下所有 SKILL.md 的 frontmatter `description:` 字段长度在
[80, 150] 字符范围内（中文计 1 字符、英文/数字/标点同计）。

参考：plan.md §P3-1
参考：scripts/task-confirm-check.py v1.1.0 接口

用法：
    python3 scripts/description-lint.py skills/
    python3 scripts/description-lint.py --self-test

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


# 长度阈值
MIN_LEN = 80
MAX_LEN = 150

# frontmatter 解析:取首个 --- 块
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
DESC_LINE_RE = re.compile(r"^description:\s*(.+?)\s*$", re.MULTILINE)


def _iter_skill_files(target: Path) -> list[Path]:
    """收集 target 下所有 SKILL.md。"""
    if target.is_file():
        return [target]
    return sorted(target.rglob("SKILL.md"))


def _extract_description(path: Path) -> tuple[str | None, int]:
    """返回 (description 文本, 长度) 或 (None, 0)。"""
    text = read_text_or_empty(path)
    m = FRONTMATTER_RE.search(text)
    if not m:
        return None, 0
    fm = m.group(1)
    dm = DESC_LINE_RE.search(fm)
    if not dm:
        return None, 0
    desc = dm.group(1).strip()
    return desc, len(desc)


def check_description_exists(path: Path) -> CheckResult:
    """Check 1: 每个 SKILL.md 必须有 description 字段。"""
    result = CheckResult(name="description_exists", passed=True)
    text = read_text_or_empty(path)
    if "description:" not in text.split("---", 2)[1] if "---" in text else False:
        result.passed = False
        result.errors.append(f"{path.name} frontmatter 缺 description 字段")
    return result


def check_description_length(path: Path) -> CheckResult:
    """Check 2: description 长度在 [80, 150] 范围。"""
    result = CheckResult(name="description_length_range", passed=True)
    desc, n = _extract_description(path)
    if desc is None:
        # 已由 Check 1 报,跳过
        return result
    if n < MIN_LEN:
        result.passed = False
        result.errors.append(
            f"{path.name}: description 长度 {n} < {MIN_LEN} 字符"
        )
    elif n > MAX_LEN:
        result.passed = False
        result.errors.append(
            f"{path.name}: description 长度 {n} > {MAX_LEN} 字符"
        )
    else:
        result.warnings.append(f"  {path.name}: {n} 字符 ✓")
    return result


def check_description_not_too_generic(path: Path) -> CheckResult:
    """Check 3: description 不能只是 'XX 助手' / 'XX 工具' 这种空泛描述。"""
    result = CheckResult(name="description_not_generic", passed=True)
    desc, _ = _extract_description(path)
    if desc is None:
        return result
    # 极端空泛描述白名单(已知违反模式)
    generic_patterns = [
        r"^XX 助手$",
        r"^通用工具$",
        r"^placeholder$",
    ]
    for pat in generic_patterns:
        if re.search(pat, desc):
            result.passed = False
            result.errors.append(
                f"{path.name}: description 过于空泛({desc!r}),"
                f" 应含具体场景/触发条件"
            )
            break
    return result


def run_checks_for_file(path: Path, mode: str) -> list[CheckResult]:
    """对单个 SKILL.md 跑所有 check。"""
    return [
        check_description_exists(path),
        check_description_length(path),
        check_description_not_too_generic(path),
    ]


def run_checks(target: Path, mode: str) -> GateReport:
    report = GateReport(
        script="description-lint.py",
        target=str(target),
        mode=mode,
    )
    files = _iter_skill_files(target)
    if not files:
        report.checks = [CheckResult(
            name="description_length_range",
            passed=False,
            errors=[f"在 {target} 下未找到任何 SKILL.md"],
        )]
        return report
    for f in files:
        report.checks.extend(run_checks_for_file(f, mode))
    return report


def self_test() -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        # 1) 缺 description → fail
        bad1 = tmpdir / "SKILL.md"
        bad1.write_text("---\nname: x\n---\n# x\n", encoding="utf-8")
        report = run_checks(tmpdir, "strict")
        if not report.has_errors:
            print(f"{E_FAIL} 自检失败:缺 description 应被报")
            return EXIT_FAIL
        # 2) 太短(<80) → fail
        bad2 = tmpdir / "SKILL.md"
        bad2.write_text(
            f"---\ndescription: {'短' * 20}\n---\n# x\n",
            encoding="utf-8",
        )
        report = run_checks(tmpdir, "strict")
        if not any("长度" in e for c in report.checks for e in c.errors):
            print(f"{E_FAIL} 自检失败:description 太短应被报")
            return EXIT_FAIL
        # 3) 太长(>150) → fail
        bad3 = tmpdir / "SKILL.md"
        bad3.write_text(
            f"---\ndescription: {'长' * 200}\n---\n# x\n",
            encoding="utf-8",
        )
        report = run_checks(tmpdir, "strict")
        if not any("长度" in e for c in report.checks for e in c.errors):
            print(f"{E_FAIL} 自检失败:description 太长应被报")
            return EXIT_FAIL
        # 4) 长度合规 → pass
        good = tmpdir / "SKILL.md"
        good.write_text(
            f"---\ndescription: {'中' * 100}\n---\n# x\n",
            encoding="utf-8",
        )
        report = run_checks(tmpdir, "strict")
        if report.has_errors:
            print(f"{E_FAIL} 自检失败:合规 description 应 pass")
            for c in report.checks:
                for e in c.errors:
                    print(f"   {c.name}: {e}")
            return EXIT_FAIL
        # 5) 空泛描述 → fail
        generic = tmpdir / "SKILL.md"
        generic.write_text(
            f"---\ndescription: {'合' * 100}\nname: x\n---\n# x\n",
            encoding="utf-8",
        )
        report = run_checks(tmpdir, "strict")
        # '合' * 100 = 100 字符合规,且不匹配空泛模式 → 不会报
        # 我们直接构造一个匹配空泛模式 + 长度合规的
        generic.write_text(
            f"---\ndescription: XX 助手\nname: x\n---\n# x\n",
            encoding="utf-8",
        )
        report = run_checks(tmpdir, "strict")
        if not any("空泛" in e for c in report.checks for e in c.errors):
            print(f"{E_FAIL} 自检失败:空泛 description 应被报")
            return EXIT_FAIL
    print(f"{E_PASS} description-lint.py 自检通过 (3 个 check,5 个 case)")
    return EXIT_PASS


def main() -> int:
    parser = build_parser(
        script_name="description-lint.py",
        description="SKILL.md description 字段长度门控",
        path_help="skills/ 目录或单个 SKILL.md 路径",
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