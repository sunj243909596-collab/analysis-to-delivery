"""pytest 单元测试 for scripts/discipline-lint.py"""
import importlib.util
import sys
from pathlib import Path

import pytest


def _load_module():
    script = Path(__file__).parent.parent / "scripts" / "discipline-lint.py"
    spec = importlib.util.spec_from_file_location("discipline_lint", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_mod = _load_module()
parse_frontmatter = _mod.parse_frontmatter
check_frontmatter_requires_present = _mod.check_frontmatter_requires_present
check_contract_block_consistent = _mod.check_contract_block_consistent
check_discipline_path_exists = _mod.check_discipline_path_exists
check_no_typo_in_name = _mod.check_no_typo_in_name
USER_INVOKED_SKILLS = _mod.USER_INVOKED_SKILLS
KNOWN_DISCIPLINES = _mod.KNOWN_DISCIPLINES


# ===== frontmatter 解析 =====

def test_parse_frontmatter_simple():
    text = "---\nname: foo\nversion: 3.0.1\n---\n\n# body\n"
    fm, body = parse_frontmatter(text)
    assert fm["name"] == "foo"
    assert fm["version"] == "3.0.1"
    assert "body" in body


def test_parse_frontmatter_array():
    text = "---\nname: foo\nrequires: [a, b, c]\n---\n"
    fm, _ = parse_frontmatter(text)
    assert fm["requires"] == ["a", "b", "c"]


def test_parse_frontmatter_array_empty():
    text = "---\nrequires: []\n---\n"
    fm, _ = parse_frontmatter(text)
    assert fm["requires"] == []


def test_parse_frontmatter_no_frontmatter():
    text = "# no frontmatter\n"
    fm, body = parse_frontmatter(text)
    assert fm == {}
    assert body == text


# ===== 构造测试 fixtures =====

def _make_skill(p: Path, requires: list[str] | None, contract_names: list[str] | None):
    p.parent.mkdir(parents=True, exist_ok=True)
    # None = 不写 requires: 行; [] / [...] = 显式写
    if requires is None:
        fm_requires = ""
    else:
        fm_requires = f"requires: [{', '.join(requires)}]\n"
    contract = ""
    if contract_names is not None:
        contract = (
            "## Contract\n\n- Required disciplines: "
            + ", ".join(f"`{n}`" for n in contract_names)
            + "\n"
        )
    p.write_text(
        f"---\nname: {p.parent.name}\ndescription: x\nversion: 3.0.1\n"
        "disable-model-invocation: true\n"
        f"{fm_requires}---\n\n{contract}",
        encoding="utf-8",
    )


def _make_skill_tree(tmp_path: Path) -> Path:
    """构造最小 skills 树(7 discipline + 9 user-invoked skills)。"""
    for d in KNOWN_DISCIPLINES:
        _make_skill(tmp_path / "disciplines" / d / "SKILL.md", None, None)
    return tmp_path


# ===== Check 1: frontmatter requires 存在 =====

def test_check1_all_present(tmp_path):
    _make_skill_tree(tmp_path)
    for n in USER_INVOKED_SKILLS:
        _make_skill(tmp_path / "user-invoked" / n / "SKILL.md", ["stage-gate"], ["stage-gate"])
    result = check_frontmatter_requires_present(tmp_path)
    assert result.passed, f"errors={result.errors}"


def test_check1_missing(tmp_path):
    _make_skill_tree(tmp_path)
    _make_skill(tmp_path / "user-invoked" / "grill-task" / "SKILL.md", None, None)
    for n in USER_INVOKED_SKILLS:
        if n == "grill-task":
            continue
        _make_skill(tmp_path / "user-invoked" / n / "SKILL.md", ["stage-gate"], ["stage-gate"])
    result = check_frontmatter_requires_present(tmp_path)
    assert not result.passed
    assert any("grill-task" in e for e in result.errors)


def test_check1_empty_array(tmp_path):
    _make_skill_tree(tmp_path)
    for n in USER_INVOKED_SKILLS:
        _make_skill(tmp_path / "user-invoked" / n / "SKILL.md", [], ["stage-gate"])
    result = check_frontmatter_requires_present(tmp_path)
    assert not result.passed
    assert any("空" in e for e in result.errors)


# ===== Check 2: 与 Contract 块一致 =====

def test_check2_consistent(tmp_path):
    _make_skill_tree(tmp_path)
    for n in USER_INVOKED_SKILLS:
        _make_skill(
            tmp_path / "user-invoked" / n / "SKILL.md",
            ["stage-gate", "doc-numbering"],
            ["stage-gate", "doc-numbering"],
        )
    result = check_contract_block_consistent(tmp_path)
    assert result.passed


def test_check2_inconsistent(tmp_path):
    _make_skill_tree(tmp_path)
    for n in USER_INVOKED_SKILLS:
        _make_skill(
            tmp_path / "user-invoked" / n / "SKILL.md",
            ["stage-gate", "doc-numbering"],
            ["stage-gate"],  # 缺 doc-numbering
        )
    result = check_contract_block_consistent(tmp_path)
    assert not result.passed


# ===== Check 3: discipline 路径存在 =====

def test_check3_path_exists(tmp_path):
    _make_skill_tree(tmp_path)
    for n in USER_INVOKED_SKILLS:
        _make_skill(tmp_path / "user-invoked" / n / "SKILL.md", ["stage-gate"], ["stage-gate"])
    result = check_discipline_path_exists(tmp_path)
    assert result.passed


def test_check3_missing_discipline(tmp_path):
    _make_skill_tree(tmp_path)
    # 删除一个 discipline 目录
    import shutil
    shutil.rmtree(tmp_path / "disciplines" / "stage-gate")
    for n in USER_INVOKED_SKILLS:
        _make_skill(tmp_path / "user-invoked" / n / "SKILL.md", ["stage-gate"], ["stage-gate"])
    result = check_discipline_path_exists(tmp_path)
    assert not result.passed
    assert any("stage-gate" in e and "不存在" in e for e in result.errors)


# ===== Check 4: 白名单 =====

def test_check4_in_whitelist(tmp_path):
    _make_skill_tree(tmp_path)
    for n in USER_INVOKED_SKILLS:
        _make_skill(tmp_path / "user-invoked" / n / "SKILL.md", ["stage-gate"], ["stage-gate"])
    result = check_no_typo_in_name(tmp_path)
    assert result.passed


def test_check4_typo(tmp_path):
    _make_skill_tree(tmp_path)
    for n in USER_INVOKED_SKILLS:
        _make_skill(
            tmp_path / "user-invoked" / n / "SKILL.md",
            ["stage-gate", "typo-bad-discipline"],
            ["stage-gate", "typo-bad-discipline"],
        )
    result = check_no_typo_in_name(tmp_path)
    assert not result.passed
    assert any("白名单" in e for e in result.errors)


# ===== self-test =====

def test_self_test_runs():
    import subprocess
    r = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "discipline-lint.py"), "--self-test"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"stderr={r.stderr}\nstdout={r.stdout}"


# ===== 实际仓库集成测试 =====

def test_real_repo_passes():
    """真实仓库 skills/ 应通过 discipline-lint。"""
    import subprocess
    repo = Path(__file__).parent.parent
    r = subprocess.run(
        [sys.executable, str(repo / "scripts" / "discipline-lint.py"), "--strict",
         str(repo / "skills")],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"stderr={r.stderr}\nstdout={r.stdout}"


def test_real_repo_break_on_modify():
    """故意改坏 grill-task 的 requires,跑 lint 应 exit 1。"""
    import subprocess
    import shutil
    repo = Path(__file__).parent.parent
    target = repo / "skills" / "user-invoked" / "grill-task" / "SKILL.md"
    backup = target.read_text(encoding="utf-8")
    broken = backup.replace(
        "requires: [context-pointer, no-field-guessing, no-self-invent, stage-gate]",
        "requires: [typo-discipline]",
    )
    if backup == broken:
        # 字段已经改了,跳过
        return
    try:
        target.write_text(broken, encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(repo / "scripts" / "discipline-lint.py"), "--strict",
             str(repo / "skills")],
            capture_output=True, text=True,
        )
        assert r.returncode == 1, f"应 exit 1,实际 {r.returncode}\nstdout={r.stdout}"
    finally:
        target.write_text(backup, encoding="utf-8")
