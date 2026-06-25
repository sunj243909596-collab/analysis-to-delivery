#!/usr/bin/env python3
"""
setup-check.py — 阶段 1→2 配置就绪门控（v3.1.0-dev）

校验项目根（或指定目录）下 4 个 `*-path.md` 配置存在且非空：
- knowledge-path.md
- compliance-path.md
- tech-stack-path.md
- doc-naming.md

且 knowledge-path.md 必须至少含 1 个真实路径（非注释、非占位符）。

参考：skills/user-invoked/setup-analysis-delivery/SKILL.md §3 / §5
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


CONFIG_FILES = [
    "knowledge-path.md",
    "compliance-path.md",
    "tech-stack-path.md",
    "doc-naming.md",
]

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


def check_config_files_exist(project_dir: Path) -> CheckResult:
    """Check 1: 4 个 *-path.md 全部存在。"""
    result = CheckResult(name="config_files_exist", passed=True)
    for name in CONFIG_FILES:
        p = project_dir / name
        if not p.exists():
            result.passed = False
            result.errors.append(f"缺少 {name}")
        elif p.stat().st_size == 0:
            result.passed = False
            result.errors.append(f"{name} 存在但为空")
    return result


def check_config_files_nonempty(project_dir: Path) -> CheckResult:
    """Check 2: 至少每个文件去掉占位符后还有实质内容。"""
    result = CheckResult(name="config_files_nonempty", passed=True)
    for name in CONFIG_FILES:
        p = project_dir / name
        if not p.exists():
            continue  # 已被 Check 1 捕获
        text = read_text_or_empty(p)
        substantive = [
            line for line in text.splitlines()
            if not _is_placeholder(line)
        ]
        if not substantive:
            result.passed = False
            result.errors.append(
                f"{name} 只有占位符/注释/空行,无实质内容"
            )
    return result


def check_knowledge_path_has_real_path(project_dir: Path) -> CheckResult:
    """Check 3: knowledge-path.md 必须含至少 1 个真实路径（绝对路径或 ~/ 开头）。"""
    result = CheckResult(name="knowledge_path_has_real_path", passed=True)
    kp = project_dir / "knowledge-path.md"
    if not kp.exists():
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
            "knowledge-path.md 必须至少含 1 个真实路径"
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
        # 2) 4 个文件都创建但只有注释 → 应 fail
        for name in CONFIG_FILES:
            (tmpdir / name).write_text(
                "<!-- 这是注释 -->\n\n# 标题\n",
                encoding="utf-8",
            )
        report = run_checks(tmpdir, "strict")
        if not report.has_errors:
            print(f"{E_FAIL} 自检失败:只有注释应被报为无实质内容")
            return EXIT_FAIL
        # 3) 写入有效内容(含真实路径)→ 应 pass
        (tmpdir / "knowledge-path.md").write_text(
            "## 知识库\n\n- /root/WMOS 知识库/01-WMOS核心/\n",
            encoding="utf-8",
        )
        (tmpdir / "compliance-path.md").write_text(
            "## 合规\n\n- config/compliance/GSP.md\n",
            encoding="utf-8",
        )
        (tmpdir / "tech-stack-path.md").write_text(
            "## 技术栈\n\n- Java + Spring Boot\n",
            encoding="utf-8",
        )
        (tmpdir / "doc-naming.md").write_text(
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
    print(f"{E_PASS} setup-check.py 自检通过 (3 个 check,3 个 case)")
    return EXIT_PASS


def main() -> int:
    parser = build_parser(
        script_name="setup-check.py",
        description="阶段 1→2 配置就绪门控",
        path_help="项目根目录（含 4 个 *-path.md）",
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
