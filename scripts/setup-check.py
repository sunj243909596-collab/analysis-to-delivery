#!/usr/bin/env python3
"""
setup-check.py — 阶段 1→2 配置就绪门控（v3.2.0-dev / rules-and-paths refactor）

校验项目根（或指定目录）下项目级配置存在且非空：

- 规范路径(优先)：<project>/paths/{name}.md
- 兼容路径(回退)：<project>/{name}.md（仅遗留项目，新项目必须用规范路径）

文件清单：
- knowledge-path.md
- compliance-path.md
- tech-stack-path.md
- doc-naming-path.md (canonical)  /  doc-naming.md (legacy)

且 knowledge-path.md 必须至少含 1 个真实路径（非注释、非占位符）。

参考：skills/user-invoked/setup-analysis-delivery/SKILL.md §3 / §5
参考：paths/*.md（canonical path 配置入口）
参考：scripts/task-confirm-check.py v1.1.0 接口

用法：
    python3 scripts/setup-check.py <project_dir>
    python3 scripts/setup-check.py --self-test
    python3 scripts/setup-check.py --loose <project_dir>   # 警告而非 BLOCK

退出码：0 = pass(strict)/ 仅 warning(loose);1 = fail;2 = 参数错误
"""
import re
import sys
from pathlib import Path

# 允许 _gate_common 不可用（极简自检仍可跑）
try:
    from _gate_common import (
        E_FAIL, E_INFO, E_PASS, E_WARN, EXIT_FAIL, EXIT_PASS, EXIT_USAGE,
        CheckResult, GateReport, build_parser, finalize, read_text_or_empty,
        run_self_test,
    )
except ImportError:  # 直接 python3 scripts/setup-check.py 时 path 不在
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _gate_common import (  # type: ignore
        E_FAIL, E_INFO, E_PASS, E_WARN, EXIT_FAIL, EXIT_PASS, EXIT_USAGE,
        CheckResult, GateReport, build_parser, finalize, read_text_or_empty,
        run_self_test,
    )


# 规范路径(canonical):必须先在 <project>/paths/ 下找
# 兼容路径(legacy):项目根 *.md,仅作为 v1.1 既有项目的回退
PATH_ENTRIES = [
    ("knowledge-path.md", "knowledge-path.md"),
    ("compliance-path.md", "compliance-path.md"),
    ("tech-stack-path.md", "tech-stack-path.md"),
    ("doc-naming-path.md", "doc-naming.md"),  # canonical -> legacy alias
]
CANONICAL_DIR = "paths"

# 严格模式的占位符/注释关键词
PLACEHOLDER_PATTERNS = [
    r"^\s*<!--.*-->\s*$",  # HTML 注释
    r"^\s*#.*$",            # 仅 markdown 标题
    r"^\s*$",               # 空行
    r"^>\s*$",              # 空引用
]


def _is_placeholder(line: str) -> bool:
    for pat in PLACEHOLDER_PATTERNS:
        if re.match(pat, line):
            return True
    return False


def _resolve_paths(project_dir: Path):
    """对每个 entry 同时返回 (canonical_path, legacy_path, exists_canonical, exists_legacy)。"""
    rows = []
    for canonical_name, legacy_name in PATH_ENTRIES:
        canonical = project_dir / CANONICAL_DIR / canonical_name
        legacy = project_dir / legacy_name
        rows.append(
            (
                canonical_name,
                canonical,
                legacy,
                canonical.exists(),
                legacy.exists(),
            )
        )
    return rows


def check_config_files_exist(project_dir: Path) -> CheckResult:
    """Check 1: 4 个 path 文件存在(canonical 优先, legacy 回退)。"""
    result = CheckResult(name="config_files_exist", passed=True)
    for canonical_name, canonical, legacy, has_canon, has_legacy in _resolve_paths(project_dir):
        if has_canon:
            if canonical.stat().st_size == 0:
                result.passed = False
                result.errors.append(f"paths/{canonical_name} 存在但为空")
            continue
        if has_legacy:
            if legacy.stat().st_size == 0:
                result.passed = False
                result.errors.append(f"{legacy.name} 存在但为空")
                continue
            result.warnings.append(
                f"{legacy.name} 仅在项目根(legacy);推荐迁移到 paths/{canonical_name}"
            )
            continue
        result.passed = False
        result.errors.append(
            f"缺少 paths/{canonical_name}(canonical),"
            f"或 {legacy.name}(legacy 回退)"
        )
    return result


def _first_existing(canonical: Path, legacy: Path) -> Path | None:
    if canonical.exists():
        return canonical
    if legacy.exists():
        return legacy
    return None


def check_config_files_nonempty(project_dir: Path) -> CheckResult:
    """Check 2: 至少每个文件去掉占位符后还有实质内容。"""
    result = CheckResult(name="config_files_nonempty", passed=True)
    for canonical_name, canonical, legacy, _, _ in _resolve_paths(project_dir):
        target = _first_existing(canonical, legacy)
        if target is None:
            continue  # 已被 Check 1 捕获
        text = read_text_or_empty(target)
        substantive = [
            line for line in text.splitlines()
            if not _is_placeholder(line)
        ]
        if not substantive:
            result.passed = False
            result.errors.append(
                f"{target.name} 只有占位符/注释/空行,无实质内容"
            )
    return result


def check_knowledge_path_has_real_path(project_dir: Path) -> CheckResult:
    """Check 3: knowledge-path.md 必须含至少 1 个真实路径(绝对路径或 ~/ 开头)。"""
    result = CheckResult(name="knowledge_path_has_real_path", passed=True)
    kp = _first_existing(
        project_dir / CANONICAL_DIR / "knowledge-path.md",
        project_dir / "knowledge-path.md",
    )
    if kp is None:
        return result  # 已被 Check 1 捕获

    text = read_text_or_empty(kp)
    # 匹配: 绝对路径 /root/... 或 ~ 开头的用户目录路径
    path_pattern = re.compile(r"(/[\w./\-]+|~/[\w./\-]+)")
    found = path_pattern.findall(text)
    # 过滤掉显然是 markdown 链接/示例的短路径
    real_paths = [
        p for p in found
        if len(p) > 5 and not p.endswith(".md") or p.startswith("/")
    ]
    if not real_paths:
        result.passed = False
        result.errors.append(
            f"{kp.name} 必须至少含 1 个真实路径"
            "（如 `/root/WMOS 知识库/` 或 `~/docs/`）"
        )
    return result


def run_checks(project_dir: Path, mode: str) -> GateReport:
    report = GateReport(
        script="setup-check.py",
        target=str(project_dir),
        mode=mode,
    )
    report.checks = [
        check_config_files_exist(project_dir),
        check_config_files_nonempty(project_dir),
        check_knowledge_path_has_real_path(project_dir),
    ]
    return report


def self_test() -> int:
    """内置自检：构造临时项目目录，跑 3 个 check。"""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        # 1) 全空目录 → 应 fail
        report = run_checks(tmpdir, "strict")
        if not report.has_errors:
            print(f"{E_FAIL} 自检失败:空目录应被报为缺文件")
            return EXIT_FAIL
        # 2) 只有注释 → 应 fail
        (tmpdir / "paths").mkdir()
        for canonical_name, _, _, _, _ in _resolve_paths(tmpdir):
            (tmpdir / "paths" / canonical_name).write_text(
                "<!-- 这是注释 -->\n\n# 标题\n",
                encoding="utf-8",
            )
        report = run_checks(tmpdir, "strict")
        if not report.has_errors:
            print(f"{E_FAIL} 自检失败:只有注释应被报为无实质内容")
            return EXIT_FAIL
        # 3) 写入有效内容(含真实路径)→ 应 pass
        (tmpdir / "paths" / "knowledge-path.md").write_text(
            "## 知识库\n\n- /root/WMOS 知识库/01-WMOS核心/\n",
            encoding="utf-8",
        )
        (tmpdir / "paths" / "compliance-path.md").write_text(
            "## 合规\n\n- config/compliance/GSP.md\n",
            encoding="utf-8",
        )
        (tmpdir / "paths" / "tech-stack-path.md").write_text(
            "## 技术栈\n\n- Java + Spring Boot\n",
            encoding="utf-8",
        )
        (tmpdir / "paths" / "doc-naming-path.md").write_text(
            "## 文档命名\n\n- 编号 01-09\n",
            encoding="utf-8",
        )
        report = run_checks(tmpdir, "strict")
        if report.has_errors:
            print(f"{E_FAIL} 自检失败:有效项目目录应 pass")
            for c in report.checks:
                for e in c.errors:
                    print(f"   {c.name}: {e}")
            return EXIT_FAIL
        # 4) legacy 文件夹应通过(仅产生 warning)
        legacy_dir = Path(tmp) / "legacy_proj"
        legacy_dir.mkdir()
        for _, legacy_name, _, _, _ in [
            (None, "knowledge-path.md", None, None, None),
            (None, "compliance-path.md", None, None, None),
            (None, "tech-stack-path.md", None, None, None),
            (None, "doc-naming.md", None, None, None),
        ]:
            (legacy_dir / legacy_name).write_text(
                "## x\n\n- /root/foo\n" if legacy_name == "knowledge-path.md"
                else "## x\n\n- content\n",
                encoding="utf-8",
            )
        report = run_checks(legacy_dir, "strict")
        if report.has_errors:
            print(f"{E_FAIL} 自检失败:legacy 项目根文件应 pass(仅 warning)")
            for c in report.checks:
                for e in c.errors:
                    print(f"   {c.name}: {e}")
            return EXIT_FAIL
        if not any(c.warnings for c in report.checks):
            print(f"{E_FAIL} 自检失败:legacy 项目根文件应产生 warning")
            return EXIT_FAIL
    print(f"{E_PASS} setup-check.py 自检通过 (3 个 check,4 个 case)")
    return EXIT_PASS


def main() -> int:
    parser = build_parser(
        script_name="setup-check.py",
        description="阶段 1→2 配置就绪门控",
        path_help="项目根目录（含 paths/*.md 或兼容的 legacy *-path.md）",
    )
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    if not args.path:
        parser.error("需要 path 参数,或使用 --self-test")
    project_dir = Path(args.path)
    if not project_dir.is_dir():
        print(f"{E_FAIL} {project_dir} 不是目录", file=sys.stderr)
        return EXIT_USAGE

    report = run_checks(project_dir, args.mode)
    return finalize(report, as_json=args.json)


if __name__ == "__main__":
    sys.exit(main())
