#!/usr/bin/env python3
"""
brd-check.py — 阶段 3→4 BRD 章节齐全门控（v4.0.0）

校验 `01-业务需求文档 BRD.md` 的 9 个必备章节齐全：
- 一、项目概述
- 二、角色与职责
- 三、业务流程
- 四、功能模块
- 五、数据要求
- 六、合规要点
- 七、非功能需求
- 八、风险与约束
- 九、上线计划

参考：skills/user-invoked/to-brd/SKILL.md §2 / §结束条件
参考：scripts/task-confirm-check.py v1.1.0 接口

用法：
    python3 scripts/brd-check.py <project_dir_or_brd.md>
    python3 scripts/brd-check.py --self-test

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


BRD_REQUIRED_SECTIONS = [
    ("一", "项目概述"),
    ("二", "角色与职责"),
    ("三", "业务流程"),
    ("四", "功能模块"),
    ("五", "数据要求"),
    ("六", "合规要点"),
    ("七", "非功能需求"),
    ("八", "风险与约束"),
    ("九", "上线计划"),
]


def _resolve_brd_path(target: Path) -> Path | None:
    """target 可能是项目根（找 01-业务需求文档 BRD.md）或 BRD 文件本身。"""
    if target.is_file():
        return target
    if target.is_dir():
        # 优先匹配规范命名
        for name in ("01-业务需求文档 BRD.md", "01-业务需求文档BRD.md", "01-BRD.md"):
            p = target / name
            if p.exists():
                return p
        # 否则 glob 找 01-*BRD*.md
        for p in sorted(target.glob("01-*BRD*.md")):
            return p
    return None


def check_brd_sections(brd_path: Path) -> CheckResult:
    """Check 1: 9 个必备章节齐全。"""
    result = CheckResult(name="brd_9_sections", passed=True)
    if not brd_path.exists():
        result.passed = False
        result.errors.append(f"BRD 文件不存在: {brd_path}")
        return result
    text = read_text_or_empty(brd_path)
    missing = []
    for num, title in BRD_REQUIRED_SECTIONS:
        # 匹配 "## 一、项目概述" 或 "## 一 项目概述" 或 "## 一.项目概述"
        pattern = rf"^##\s*{re.escape(num)}[、.\s]+{re.escape(title)}"
        if not re.search(pattern, text, re.MULTILINE):
            # 也允许只写 "## 一 xxx" 不强求标题完全一致
            loose_pattern = rf"^##\s*{re.escape(num)}[、.\s]+\S+"
            if not re.search(loose_pattern, text, re.MULTILINE):
                missing.append(f"## {num}、{title}")
            else:
                # 章节存在但标题不一致,记为 warning
                result.warnings.append(
                    f"章节 {num} 存在但标题与规范 '{title}' 不一致"
                )
    if missing:
        result.passed = False
        result.errors.append(
            f"BRD 缺 {len(missing)}/9 章节: {', '.join(missing)}"
        )
    return result


def check_brd_not_template(brd_path: Path) -> CheckResult:
    """Check 2: BRD 不能是模板(去重的占位符过多 → 提示用户确认)。"""
    result = CheckResult(name="brd_not_template_placeholder", passed=True)
    if not brd_path.exists():
        return result
    text = read_text_or_empty(brd_path)
    placeholders = re.findall(r"\{\{[^}]+\}\}|TBD|TODO|占位", text)
    if len(placeholders) > 10:
        # 模板嫌疑,只 warning
        result.warnings.append(
            f"BRD 含 {len(placeholders)} 个占位符,疑似未填写完的模板"
        )
    return result


def run_checks(brd_path: Path, mode: str) -> GateReport:
    report = GateReport(
        script="brd-check.py",
        target=str(brd_path),
        mode=mode,
    )
    report.checks = [
        check_brd_sections(brd_path),
        check_brd_not_template(brd_path),
    ]
    return report


def self_test() -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        # 1) 没有 BRD → fail (直接构造缺失场景,不调 run_checks 避免传 dir)
        fake_path = tmpdir / "01-业务需求文档 BRD.md"
        report = run_checks(fake_path, "strict")
        if not report.has_errors:
            print(f"{E_FAIL} 自检失败:缺 BRD 应被报")
            return EXIT_FAIL
        # 2) BRD 缺 5 个章节 → fail
        bad = tmpdir / "01-业务需求文档 BRD.md"
        bad.write_text(
            "## 一、项目概述\n\n## 二、角色与职责\n\n## 三、业务流程\n\n## 四、功能模块\n\n",
            encoding="utf-8",
        )
        report = run_checks(bad, "strict")
        if not report.has_errors:
            print(f"{E_FAIL} 自检失败:缺 5 章节应被报")
            return EXIT_FAIL
        # 3) 完整 9 章节 → pass
        good_content = "\n".join(
            f"## {n}、{t}\n\n内容\n" for n, t in BRD_REQUIRED_SECTIONS
        )
        good = tmpdir / "01-业务需求文档 BRD.md"
        good.write_text(good_content, encoding="utf-8")
        report = run_checks(good, "strict")
        if report.has_errors:
            print(f"{E_FAIL} 自检失败:9 章节完整应 pass")
            for c in report.checks:
                for e in c.errors:
                    print(f"   {c.name}: {e}")
            return EXIT_FAIL
    print(f"{E_PASS} brd-check.py 自检通过 (2 个 check,3 个 case)")
    return EXIT_PASS


def main() -> int:
    parser = build_parser(
        script_name="brd-check.py",
        description="阶段 3→4 BRD 9 章节齐全门控",
        path_help="项目根目录或 BRD.md 路径",
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

    brd_path = _resolve_brd_path(target)
    if brd_path is None:
        # 整个目录都没 BRD
        report = GateReport(
            script="brd-check.py",
            target=str(target),
            mode=args.mode,
            checks=[CheckResult(
                name="brd_9_sections",
                passed=False,
                errors=[f"未找到 01-*BRD*.md 在 {target}"],
            )],
        )
        return finalize(report, as_json=args.json)

    report = run_checks(brd_path, args.mode)
    return finalize(report, as_json=args.json)


if __name__ == "__main__":
    sys.exit(main())
