#!/usr/bin/env python3
"""
bridge-completeness-check.py — bridge skill 实质化校验（v4.0.0）

校验 7 个 skills/orchestration/development/*/SKILL.md 是否含
降级方案(superpowers 未装时也能用)。

3 项 check:
1. has_degradation_section — 含 `## 降级方案(superpowers 未装时)` H2
2. has_install_hint — 含 `npx skills@latest add obra/superpowers-` 安装提示
3. has_discipline_summary — 含 `### 最小纪律摘要` H3 子章节

参考：plan.md §P1-1

用法：
    python3 scripts/bridge-completeness-check.py skills/orchestration/development/
    python3 scripts/bridge-completeness-check.py --self-test

退出码：0 = pass;1 = fail;2 = 参数错误
"""
import re
import sys
from pathlib import Path

try:
    from _gate_common import (
        E_FAIL, E_PASS, EXIT_FAIL, EXIT_PASS, EXIT_USAGE,
        CheckResult, GateReport, build_parser, finalize, read_text_or_empty,
    )
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _gate_common import (  # type: ignore
        E_FAIL, E_PASS, EXIT_FAIL, EXIT_PASS, EXIT_USAGE,
        CheckResult, GateReport, build_parser, finalize, read_text_or_empty,
    )


# 7 个 bridge skill(从 skills/orchestration/development/ 实测)
BRIDGE_SKILLS = [
    "brainstorming",
    "design-an-interface",
    "domain-modeling",
    "executing-plans",
    "tdd",
    "verification-before-completion",
    "writing-plans",
]


# ===== 3 项 check =====

def check_has_degradation_section(bridge_dir: Path) -> CheckResult:
    """Check 1: 含 `## 降级方案(superpowers 未装时)` H2。"""
    result = CheckResult(name="has_degradation_section", passed=True)
    for name in BRIDGE_SKILLS:
        p = bridge_dir / name / "SKILL.md"
        if not p.exists():
            result.passed = False
            result.errors.append(f"缺少 bridge skill: {p}")
            continue
        text = read_text_or_empty(p)
        # 匹配 H2: "## 降级方案(superpowers 未装时)" 或 "## 降级方案 ..." 都行
        if re.search(r"^##\s+降级方案[^\n]*$", text, re.MULTILINE):
            continue
        result.passed = False
        result.errors.append(f"{name}: 缺少 `## 降级方案` H2 章节")
    return result


def check_has_install_hint(bridge_dir: Path) -> CheckResult:
    """Check 2: 含 `npx skills@latest add obra/superpowers-` 安装提示。"""
    result = CheckResult(name="has_install_hint", passed=True)
    pattern = re.compile(r"npx\s+skills@latest\s+add\s+obra/superpowers-")
    for name in BRIDGE_SKILLS:
        p = bridge_dir / name / "SKILL.md"
        if not p.exists():
            continue
        text = read_text_or_empty(p)
        if pattern.search(text):
            continue
        result.passed = False
        result.errors.append(
            f"{name}: 缺少 `npx skills@latest add obra/superpowers-...` 安装提示"
        )
    return result


def check_has_discipline_summary(bridge_dir: Path) -> CheckResult:
    """Check 3: 含 `### 最小纪律摘要` H3 子章节(≥3 行 bullet)。"""
    result = CheckResult(name="has_discipline_summary", passed=True)
    for name in BRIDGE_SKILLS:
        p = bridge_dir / name / "SKILL.md"
        if not p.exists():
            continue
        text = read_text_or_empty(p)
        # 找 "### 最小纪律摘要" 段
        m = re.search(
            r"^###\s+最小纪律摘要[^\n]*\n((?:\s|.)*?)(?=^##\s|\Z)",
            text,
            re.MULTILINE,
        )
        if not m:
            result.passed = False
            result.errors.append(f"{name}: 缺少 `### 最小纪律摘要` H3 章节")
            continue
        section = m.group(1)
        # 数 bullet 行 (以 - 或 ❌ 开头)
        bullets = re.findall(r"^\s*[-❌][^\n]*$", section, re.MULTILINE)
        if len(bullets) < 3:
            result.passed = False
            result.errors.append(
                f"{name}: `最小纪律摘要` 至少 3 条 bullet,当前 {len(bullets)} 条"
            )
    return result


def run_checks(bridge_dir: Path, mode: str) -> GateReport:
    report = GateReport(
        script="bridge-completeness-check.py",
        target=str(bridge_dir),
        mode=mode,
    )
    report.checks = [
        check_has_degradation_section(bridge_dir),
        check_has_install_hint(bridge_dir),
        check_has_discipline_summary(bridge_dir),
    ]
    return report


def self_test() -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)

        # 1) 空目录 → 全部 fail
        report = run_checks(tmpdir, "strict")
        if not report.has_errors:
            print(f"{E_FAIL} 自检失败:空目录应全报")
            return EXIT_FAIL

        # 2) 建 1 个完整 bridge → 仍 fail(7 个缺 6 个)
        (tmpdir / "brainstorming").mkdir()
        (tmpdir / "brainstorming" / "SKILL.md").write_text(
            "# x\n\n## 降级方案(superpowers 未装时)\n\n"
            "### 最小纪律摘要\n- a\n- b\n- c\n\n"
            "```bash\nnpx skills@latest add obra/superpowers-brainstorming\n```\n",
            encoding="utf-8",
        )
        report = run_checks(tmpdir, "strict")
        if not report.has_errors:
            print(f"{E_FAIL} 自检失败:7 个缺 6 个应被报")
            return EXIT_FAIL

        # 3) 7 个齐全 → pass
        for n in BRIDGE_SKILLS:
            (tmpdir / n).mkdir(exist_ok=True)
            (tmpdir / n / "SKILL.md").write_text(
                f"# {n}\n\n## 降级方案(superpowers 未装时)\n\n"
                "### 最小纪律摘要\n- a\n- b\n- c\n\n"
                f"```bash\nnpx skills@latest add obra/superpowers-{n}\n```\n",
                encoding="utf-8",
            )
        report = run_checks(tmpdir, "strict")
        if report.has_errors:
            print(f"{E_FAIL} 自检失败:7 个齐应 pass")
            for c in report.checks:
                for e in c.errors:
                    print(f"   {c.name}: {e}")
            return EXIT_FAIL

        # 4) 缺最小纪律摘要 → Check 3 fail
        (tmpdir / "brainstorming" / "SKILL.md").write_text(
            "# x\n\n## 降级方案(superpowers 未装时)\n\n"
            "```bash\nnpx skills@latest add obra/superpowers-brainstorming\n```\n",
            encoding="utf-8",
        )
        report = run_checks(tmpdir, "strict")
        if not report.has_errors:
            print(f"{E_FAIL} 自检失败:缺最小纪律摘要应被报")
            return EXIT_FAIL

        # 5) 缺安装提示 → Check 2 fail
        (tmpdir / "brainstorming" / "SKILL.md").write_text(
            "# x\n\n## 降级方案(superpowers 未装时)\n\n"
            "### 最小纪律摘要\n- a\n- b\n- c\n",
            encoding="utf-8",
        )
        report = run_checks(tmpdir, "strict")
        if not report.has_errors:
            print(f"{E_FAIL} 自检失败:缺安装提示应被报")
            return EXIT_FAIL

        # 6) 纪律摘要 bullet 不够 3 条 → Check 3 fail
        (tmpdir / "brainstorming" / "SKILL.md").write_text(
            "# x\n\n## 降级方案(superpowers 未装时)\n\n"
            "### 最小纪律摘要\n- a\n\n"
            "```bash\nnpx skills@latest add obra/superpowers-brainstorming\n```\n",
            encoding="utf-8",
        )
        report = run_checks(tmpdir, "strict")
        if not report.has_errors:
            print(f"{E_FAIL} 自检失败:bullet < 3 应被报")
            return EXIT_FAIL

    print(f"{E_PASS} bridge-completeness-check.py 自检通过 (3 个 check,6 个 case)")
    return EXIT_PASS


def main() -> int:
    parser = build_parser(
        script_name="bridge-completeness-check.py",
        description="bridge skill 实质化校验",
        path_help="bridge skills 目录(默认当前仓库的 skills/orchestration/development/)",
    )
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    if not args.path:
        repo = Path(__file__).resolve().parent.parent / "skills" / "orchestration" / "development"
        if not repo.is_dir():
            parser.error("需要 path 参数,或使用 --self-test")
        bridge_dir = repo
    else:
        bridge_dir = Path(args.path)
        if not bridge_dir.is_dir():
            print(f"{E_FAIL} {bridge_dir} 不是目录", file=sys.stderr)
            return EXIT_USAGE

    report = run_checks(bridge_dir, args.mode)
    return finalize(report, as_json=args.json)


if __name__ == "__main__":
    sys.exit(main())