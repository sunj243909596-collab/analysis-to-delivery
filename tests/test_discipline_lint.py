"""pytest 单元测试 for scripts/discipline-lint.py(legacy 兼容壳)

v4.0.0 起,discipline-lint.py 仅校验:
1. 7 个 legacy discipline 兼容壳存在
2. 兼容壳文本指向 canonical rules/*.md
3. 兼容壳行数不应过大(避免携带独立规则文本)

不再校验 `requires:` frontmatter 与 `- Required disciplines:` Contract 行
(新代码用 `- Required rules:` / `- Required paths:`,由 rules-path-lint.py 校验)。
"""
import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path


def _load_module():
    script = Path(__file__).parent.parent / "scripts" / "discipline-lint.py"
    spec = importlib.util.spec_from_file_location("discipline_lint", script)
    module = importlib.util.module_from_spec(spec)
    sys.modules["discipline_lint"] = module  # for dataclass-like attrs
    spec.loader.exec_module(module)
    return module


_mod = _load_module()
check_wrapper_files_exist = _mod.check_wrapper_files_exist
check_wrapper_points_to_canonical = _mod.check_wrapper_points_to_canonical
check_no_divergent_rule_text = _mod.check_no_divergent_rule_text
LEGACY_TO_CANONICAL = _mod.LEGACY_TO_CANONICAL


def _make_minimal(repo_root: Path) -> Path:
    """构造最小 skills 树(7 wrapper + 7 canonical rules)。

    生产布局:repo_root/skills/disciplines/<name>/SKILL.md
             repo_root/rules/<name>.md
    """
    skills_root = repo_root / "skills"
    disc_dir = skills_root / "disciplines"
    rules_dir = repo_root / "rules"
    disc_dir.mkdir(parents=True)
    rules_dir.mkdir()
    for disc_name, canonical_name in LEGACY_TO_CANONICAL.items():
        (disc_dir / disc_name).mkdir()
        (disc_dir / disc_name / "SKILL.md").write_text(
            f"# Compatibility Wrapper\n\n"
            f"deprecated; canonical is `rules/{canonical_name}.md`\n",
            encoding="utf-8",
        )
        (rules_dir / f"{canonical_name}.md").write_text(
            f"# {canonical_name}\n", encoding="utf-8",
        )
    return skills_root


# ===== Check 1: wrapper 文件存在 =====

def test_wrapper_files_exist_pass(tmp_path):
    skills_root = _make_minimal(tmp_path)
    result = check_wrapper_files_exist(skills_root)
    assert result.passed


def test_wrapper_files_exist_missing(tmp_path):
    skills_root = _make_minimal(tmp_path)
    shutil.rmtree(skills_root / "disciplines" / "stage-gate")
    result = check_wrapper_files_exist(skills_root)
    assert not result.passed
    assert any("stage-gate" in e for e in result.errors)


# ===== Check 2: 指向 canonical =====

def test_wrapper_points_to_canonical_pass(tmp_path):
    skills_root = _make_minimal(tmp_path)
    result = check_wrapper_points_to_canonical(skills_root)
    assert result.passed


def test_wrapper_points_to_canonical_missing_rule(tmp_path):
    skills_root = _make_minimal(tmp_path)
    (tmp_path / "rules" / "stage-gate.md").unlink()
    result = check_wrapper_points_to_canonical(skills_root)
    assert not result.passed


def test_wrapper_points_to_canonical_wrong_text(tmp_path):
    skills_root = _make_minimal(tmp_path)
    # 改 wrapper 文本,不再指向 canonical
    (skills_root / "disciplines" / "stage-gate" / "SKILL.md").write_text(
        "# Wrapper\n\n什么都没指向\n", encoding="utf-8",
    )
    result = check_wrapper_points_to_canonical(skills_root)
    assert not result.passed
    assert any("stage-gate" in e and "未指向" in e for e in result.errors)


# ===== Check 3: 无 divergent 文本 =====

def test_no_divergent_text_pass(tmp_path):
    skills_root = _make_minimal(tmp_path)
    result = check_no_divergent_rule_text(skills_root)
    assert result.passed


def test_no_divergent_text_too_long(tmp_path):
    skills_root = _make_minimal(tmp_path)
    # 写一个超长 wrapper,假装携带独立规则
    long_text = "# Wrapper\n\n" + "lorem ipsum\n" * 50
    (skills_root / "disciplines" / "stage-gate" / "SKILL.md").write_text(
        long_text, encoding="utf-8",
    )
    result = check_no_divergent_rule_text(skills_root)
    assert not result.passed
    assert any("stage-gate" in e and "行数" in e for e in result.errors)


# ===== self-test =====

def test_self_test_runs():
    r = subprocess.run(
        [sys.executable,
         str(Path(__file__).parent.parent / "scripts" / "discipline-lint.py"),
         "--self-test"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"stderr={r.stderr}\nstdout={r.stdout}"


# ===== 实际仓库集成测试 =====

def test_real_repo_passes():
    """真实仓库 skills/ 应通过 discipline-lint(legacy 兼容壳校验)。"""
    repo = Path(__file__).parent.parent
    r = subprocess.run(
        [sys.executable, str(repo / "scripts" / "discipline-lint.py"), "--strict",
         str(repo / "skills")],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"stderr={r.stderr}\nstdout={r.stdout}"
