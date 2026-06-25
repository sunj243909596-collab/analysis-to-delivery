#!/usr/bin/env python3
"""
prd-check.py — 阶段 6→7 PRD 验收门控（v3.1.0-dev）

校验 `05-产品需求文档 PRD.md` 8 节齐全 + §七 验收标准被签字：
- 一、产品概述
- 二、用户故事
- 三、功能需求
- 四、非功能需求
- 五、数据需求
- 六、合规要求
- 七、验收标准
- 八、风险与依赖

§七 必须含至少 1 条白名单话术签字：
- 我已全部确认,可以进入下一步
- 确认通过,进入 dev-design
- 全部完成,继续
- approved, proceed to next stage

参考：skills/user-invoked/to-prd/SKILL.md §3 填充内容 / §结束条件
参考：scripts/task-confirm-check.py v1.1.0 接口

用法：
    python3 scripts/prd-check.py <project_dir>
    python3 scripts/prd-check.py --self-test

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


PRD_REQUIRED_SECTIONS = [
    ("一", "产品概述"),
    ("二", "用户故事"),
    ("三", "功能需求"),
    ("四", "非功能需求"),
    ("五", "数据需求"),
    ("六", "合规要求"),
    ("七", "验收标准"),
    ("八", "风险与依赖"),
]

# 白名单签字话术(参考 disciplines/stage-gate §第 1 层 2→3 门控)
SIGN_OFF_WHITELIST = [
    r"我已全部确认.{0,3}可以进入下一步",
    r"确认通过.{0,3}进入 dev-design",
    r"确认通过.{0,3}进入下一阶段",
    r"全部完成.{0,3}继续",
    r"approved,?\s*proceed to next stage",
    r"approved,?\s*proceed to dev-design",
]


def _resolve_prd_path(target: Path) -> Path | None:
    if target.is_file():
        return target
    if target.is_dir():
        for name in ("05-产品需求文档 PRD.md", "05-PRD.md"):
            p = target / name
            if p.exists():
                return p
        for p in sorted(target.glob("05-*.md")):
            return p
    return None


def check_prd_sections(path: Path) -> CheckResult:
    """Check 1: 8 节齐全。"""
    result = CheckResult(name="prd_8_sections", passed=True)
    if not path.exists():
        result.passed = False
        result.errors.append(f"05-PRD.md 不存在: {path}")
        return result
    text = read_text_or_empty(path)
    missing = []
    for num, title in PRD_REQUIRED_SECTIONS:
        pattern = rf"^##\s*{re.escape(num)}[、.\s]+\S+"
        if not re.search(pattern, text, re.MULTILINE):
            missing.append(f"## {num}、{title}")
    if missing:
        result.passed = False
        result.errors.append(
            f"PRD 缺 {len(missing)}/8 章节: {', '.join(missing)}"
        )
    return result


def check_prd_section7_signoff(path: Path) -> CheckResult:
    """Check 2: §七 验收标准被白名单话术签字。"""
    result = CheckResult(name="prd_section7_signoff", passed=True)
    if not path.exists():
        return result
    text = read_text_or_empty(path)
    # 找 §七 章节
    m = re.search(
        r"^##\s*七[、.\s]+验收标准\s*$(.*?)(?=^##\s*八|^##\s+\S|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if not m:
        result.passed = False
        result.errors.append("找不到 §七 验收标准章节")
        return result
    section7 = m.group(1)
    # 找白名单话术
    found = []
    for pat in SIGN_OFF_WHITELIST:
        if re.search(pat, section7, re.IGNORECASE):
            found.append(pat)
    if not found:
        result.passed = False
        result.errors.append(
            "§七 验收标准未被白名单话术签字"
            "（需含 '我已全部确认,可以进入下一步' 之一）"
        )
    return result


def run_checks(path: Path, mode: str) -> GateReport:
    report = GateReport(
        script="prd-check.py",
        target=str(path),
        mode=mode,
    )
    report.checks = [
        check_prd_sections(path),
        check_prd_section7_signoff(path),
    ]
    return report


def self_test() -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        # 1) 缺文件 → fail (用 fake 路径)
        fake_path = tmpdir / "05-产品需求文档 PRD.md"
        report = run_checks(fake_path, "strict")
        if not report.has_errors:
            print(f"{E_FAIL} 自检失败:缺 05-PRD.md 应被报")
            return EXIT_FAIL
        # 2) 8 节齐但 §七 未签字 → fail
        bad = tmpdir / "05-产品需求文档 PRD.md"
        bad.write_text(
            "\n".join(f"## {n}、{t}\n\n内容\n" for n, t in PRD_REQUIRED_SECTIONS),
            encoding="utf-8",
        )
        report = run_checks(bad, "strict")
        if not report.has_errors:
            print(f"{E_FAIL} 自检失败:§七 未签字应被报")
            return EXIT_FAIL
        # 3) 8 节齐 + §七 含签字 → pass
        good = tmpdir / "05-产品需求文档 PRD.md"
        signed_section7 = (
            "## 七、验收标准\n\n"
            "1. 字段映射通过 field-alignment-check.py\n"
            "2. 三格式产物存在\n\n"
            "> 签字：我已全部确认,可以进入下一步\n"
        )
        content = ""
        for n, t in PRD_REQUIRED_SECTIONS:
            if n == "七":
                content += signed_section7
            else:
                content += f"## {n}、{t}\n\n内容\n\n"
        good.write_text(content, encoding="utf-8")
        report = run_checks(good, "strict")
        if report.has_errors:
            print(f"{E_FAIL} 自检失败:8 节齐 + §七 签字应 pass")
            for c in report.checks:
                for e in c.errors:
                    print(f"   {c.name}: {e}")
            return EXIT_FAIL
    print(f"{E_PASS} prd-check.py 自检通过 (2 个 check,3 个 case)")
    return EXIT_PASS


def main() -> int:
    parser = build_parser(
        script_name="prd-check.py",
        description="阶段 6→7 PRD 验收门控",
        path_help="项目根目录或 05-PRD.md 路径",
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
    path = _resolve_prd_path(target)
    if path is None:
        report = GateReport(
            script="prd-check.py",
            target=str(target),
            mode=args.mode,
            checks=[CheckResult(
                name="prd_8_sections",
                passed=False,
                errors=[f"未找到 05-*.md 在 {target}"],
            )],
        )
        return finalize(report, as_json=args.json)
    report = run_checks(path, args.mode)
    return finalize(report, as_json=args.json)


if __name__ == "__main__":
    sys.exit(main())
