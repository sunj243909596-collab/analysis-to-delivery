#!/usr/bin/env python3
"""
discipline-lint.py — discipline 强制加载校验（v3.1.0-dev）

校验：
1. frontmatter_requires_present — 9 个 user-invoked skill 的 frontmatter
   必须有 `requires:` 字段(数组)
2. contract_block_consistent — frontmatter `requires` 数组与正文
   `## Contract` 块的 `- Required disciplines: ...` 行**逐项一致**
3. discipline_path_exists — 每个被 requires 的 discipline 都对应
   `skills/disciplines/<name>/SKILL.md` 实际文件
4. no_typo_in_name — discipline 名必须从已知 7 个白名单之一

参考：plan.md §P0-2
参考：scripts/task-confirm-check.py v1.1.0 接口

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


# 7 个已知 discipline 白名单(从 skills/disciplines/ 实测)
KNOWN_DISCIPLINES = {
    "ascii-flowchart",
    "context-pointer",
    "doc-numbering",
    "no-field-guessing",
    "no-self-invent",
    "sql-dialect-discipline",
    "stage-gate",
}

# 9 个 user-invoked skill(从 skills/user-invoked/ 实测)
USER_INVOKED_SKILLS = [
    "compliance-review",
    "dev-design",
    "grill-task",
    "handoff",
    "qa-audit",
    "setup-analysis-delivery",
    "test-case-design",
    "to-brd",
    "to-prd",
]


# ===== frontmatter 解析 =====

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """
    解析简单 YAML frontmatter(只支持 key: value 和 key: [array])。
    返回 (frontmatter_dict, body_text)。
    """
    if not text.startswith("---"):
        return {}, text
    # 找第二个 ---
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm_text = text[3:end].strip()
    body = text[end + 4 :]
    fm: dict = {}
    current_key: str | None = None
    for line in fm_text.splitlines():
        # 数组续行: "  - xxx"
        m_arr = re.match(r"^\s+-\s+(.+?)\s*$", line)
        if m_arr and current_key and isinstance(fm.get(current_key), list):
            fm[current_key].append(m_arr.group(1).strip().strip("'\""))
            continue
        # key: value
        m_kv = re.match(r"^([\w-]+)\s*:\s*(.*?)\s*$", line)
        if m_kv:
            key, val = m_kv.group(1), m_kv.group(2)
            val = val.strip()
            if val.startswith("[") and val.endswith("]"):
                # 数组字面量
                inner = val[1:-1].strip()
                if not inner:
                    fm[key] = []
                else:
                    items = [
                        s.strip().strip("'\"")
                        for s in inner.split(",")
                    ]
                    fm[key] = items
                current_key = None
            else:
                fm[key] = val
                current_key = key
            continue
        # 其他(注释等)
        current_key = None
    return fm, body


# ===== 4 项 check =====

def _read_skill(skills_root: Path, name: str) -> tuple[Path | None, dict, str]:
    """读 SKILL.md,返回 (path, frontmatter, body)。"""
    p = skills_root / "user-invoked" / name / "SKILL.md"
    if not p.exists():
        return None, {}, ""
    text = read_text_or_empty(p)
    fm, body = parse_frontmatter(text)
    return p, fm, body


def check_frontmatter_requires_present(skills_root: Path) -> CheckResult:
    """Check 1: 9 个 skill frontmatter 必须有 requires: 字段。"""
    result = CheckResult(name="frontmatter_requires_present", passed=True)
    for name in USER_INVOKED_SKILLS:
        p, fm, _ = _read_skill(skills_root, name)
        if p is None:
            result.passed = False
            result.errors.append(f"缺少 skill 文件: skills/user-invoked/{name}/SKILL.md")
            continue
        if "requires" not in fm:
            result.passed = False
            result.errors.append(
                f"{name}: frontmatter 缺 `requires:` 字段"
            )
        elif not isinstance(fm["requires"], list):
            result.passed = False
            result.errors.append(
                f"{name}: `requires:` 必须是数组,当前是 {type(fm['requires']).__name__}"
            )
        elif not fm["requires"]:
            result.passed = False
            result.errors.append(
                f"{name}: `requires:` 数组为空(至少 1 项)"
            )
    return result


def check_contract_block_consistent(skills_root: Path) -> CheckResult:
    """Check 2: frontmatter requires 数组与 Contract 块 - Required disciplines: 行一致。"""
    result = CheckResult(name="contract_block_consistent", passed=True)
    for name in USER_INVOKED_SKILLS:
        p, fm, body = _read_skill(skills_root, name)
        if p is None or "requires" not in fm:
            continue  # 已被 Check 1 捕获
        # 找 Contract 块的 Required disciplines 行
        m = re.search(
            r"^-\s*Required disciplines:\s*(.+?)$",
            body,
            re.MULTILINE,
        )
        if not m:
            result.passed = False
            result.errors.append(
                f"{name}: 找不到 `- Required disciplines:` 行"
            )
            continue
        contract_line = m.group(1)
        # 解析 contract_line 里的 `name` 形式
        contract_names = re.findall(r"`([\w-]+)`", contract_line)
        fm_names = fm["requires"]
        # 集合比较(顺序无关,允许空白)
        if set(contract_names) != set(fm_names):
            result.passed = False
            result.errors.append(
                f"{name}: frontmatter requires {fm_names} "
                f"≠ Contract 块 {contract_names}"
            )
    return result


def check_discipline_path_exists(skills_root: Path) -> CheckResult:
    """Check 3: 每个被 requires 的 discipline 都对应 skills/disciplines/<name>/SKILL.md。"""
    result = CheckResult(name="discipline_path_exists", passed=True)
    seen_disciplines: set[str] = set()
    for name in USER_INVOKED_SKILLS:
        p, fm, _ = _read_skill(skills_root, name)
        if p is None or "requires" not in fm:
            continue
        for d in fm["requires"]:
            if d in seen_disciplines:
                continue
            seen_disciplines.add(d)
            dp = skills_root / "disciplines" / d / "SKILL.md"
            if not dp.exists():
                result.passed = False
                result.errors.append(
                    f"{name} requires `{d}` 但 skills/disciplines/{d}/SKILL.md 不存在"
                )
    return result


def check_no_typo_in_name(skills_root: Path) -> CheckResult:
    """Check 4: discipline 名必须从 7 个已知白名单。"""
    result = CheckResult(name="no_typo_in_name", passed=True)
    seen: set[str] = set()
    for name in USER_INVOKED_SKILLS:
        p, fm, _ = _read_skill(skills_root, name)
        if p is None or "requires" not in fm:
            continue
        for d in fm["requires"]:
            if d in seen:
                continue
            seen.add(d)
            if d not in KNOWN_DISCIPLINES:
                result.passed = False
                result.errors.append(
                    f"{name} requires `{d}` 不在 7 个白名单中 "
                    f"(已知: {sorted(KNOWN_DISCIPLINES)})"
                )
    return result


def run_checks(skills_root: Path, mode: str) -> GateReport:
    report = GateReport(
        script="discipline-lint.py",
        target=str(skills_root),
        mode=mode,
    )
    report.checks = [
        check_frontmatter_requires_present(skills_root),
        check_contract_block_consistent(skills_root),
        check_discipline_path_exists(skills_root),
        check_no_typo_in_name(skills_root),
    ]
    return report


def self_test() -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        # 建一个最小 skills 树
        user_dir = tmpdir / "user-invoked"
        disc_dir = tmpdir / "disciplines"
        disc_dir.mkdir(parents=True)
        for d in KNOWN_DISCIPLINES:
            (disc_dir / d).mkdir()
            (disc_dir / d / "SKILL.md").write_text("# x\n", encoding="utf-8")

        # 1) 缺所有 skill → fail
        report = run_checks(tmpdir, "strict")
        if not report.has_errors:
            print(f"{E_FAIL} 自检失败:9 个 skill 缺应全报")
            return EXIT_FAIL

        # 2) 建 9 个 skill,只 1 个有 requires → fail
        user_dir.mkdir()
        for n in USER_INVOKED_SKILLS:
            (user_dir / n).mkdir()
            (user_dir / n / "SKILL.md").write_text(
                "---\nname: x\ndescription: x\nversion: 3.0.1\n"
                "disable-model-invocation: true\n---\n\n# x\n",
                encoding="utf-8",
            )
        # 给 grill-task 加 requires
        (user_dir / "grill-task" / "SKILL.md").write_text(
            "---\nname: grill-task\ndescription: x\nversion: 3.0.1\n"
            "disable-model-invocation: true\n"
            "requires: [context-pointer]\n---\n\n"
            "## Contract\n\n- Required disciplines: `context-pointer`\n",
            encoding="utf-8",
        )
        report = run_checks(tmpdir, "strict")
        if not report.has_errors:
            print(f"{E_FAIL} 自检失败:只 1 个有 requires 应被报")
            return EXIT_FAIL

        # 3) 9 个都加 requires,与 Contract 块一致 → pass
        for n in USER_INVOKED_SKILLS:
            (user_dir / n / "SKILL.md").write_text(
                f"---\nname: {n}\ndescription: x\nversion: 3.0.1\n"
                "disable-model-invocation: true\n"
                "requires: [stage-gate]\n---\n\n"
                "## Contract\n\n- Required disciplines: `stage-gate`\n",
                encoding="utf-8",
            )
        report = run_checks(tmpdir, "strict")
        if report.has_errors:
            print(f"{E_FAIL} 自检失败:9 个齐 + 一致应 pass")
            for c in report.checks:
                for e in c.errors:
                    print(f"   {c.name}: {e}")
            return EXIT_FAIL

        # 4) requires 与 Contract 块不一致 → fail
        (user_dir / "grill-task" / "SKILL.md").write_text(
            "---\nname: grill-task\ndescription: x\nversion: 3.0.1\n"
            "disable-model-invocation: true\n"
            "requires: [stage-gate, doc-numbering]\n---\n\n"
            "## Contract\n\n- Required disciplines: `stage-gate`\n",
            encoding="utf-8",
        )
        report = run_checks(tmpdir, "strict")
        if not report.has_errors:
            print(f"{E_FAIL} 自检失败:requires vs Contract 不一致应被报")
            return EXIT_FAIL

        # 5) requires 引用不存在的 discipline → fail
        (user_dir / "grill-task" / "SKILL.md").write_text(
            "---\nname: grill-task\ndescription: x\nversion: 3.0.1\n"
            "disable-model-invocation: true\n"
            "requires: [stage-gate, typo-discipline]\n---\n\n"
            "## Contract\n\n- Required disciplines: `stage-gate`, `typo-discipline`\n",
            encoding="utf-8",
        )
        report = run_checks(tmpdir, "strict")
        if not report.has_errors:
            print(f"{E_FAIL} 自检失败:typo-discipline 应被报")
            return EXIT_FAIL

    print(f"{E_PASS} discipline-lint.py 自检通过 (4 个 check,5 个 case)")
    return EXIT_PASS


def main() -> int:
    parser = build_parser(
        script_name="discipline-lint.py",
        description="discipline 强制加载校验",
        path_help="skills/ 根目录(默认当前仓库的 skills/)",
    )
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    if not args.path:
        # 默认:脚本所在仓库的 skills/
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
