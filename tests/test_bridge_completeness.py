"""pytest 单元测试 for scripts/bridge-completeness-check.py"""
import importlib.util
import sys
from pathlib import Path


def _load_module():
    script = Path(__file__).parent.parent / "scripts" / "bridge-completeness-check.py"
    spec = importlib.util.spec_from_file_location("bridge_check", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_mod = _load_module()
BRIDGE_SKILLS = _mod.BRIDGE_SKILLS
check_has_degradation_section = _mod.check_has_degradation_section
check_has_install_hint = _mod.check_has_install_hint
check_has_discipline_summary = _mod.check_has_discipline_summary


def _make_bridge(p: Path, *, with_degradation=True, with_install=True, with_summary=True,
                  summary_bullets: int = 4):
    p.parent.mkdir(parents=True, exist_ok=True)
    parts = [f"# {p.parent.name}\n"]
    if with_degradation:
        parts.append("\n## 降级方案(superpowers 未装时)\n")
    if with_summary:
        bullets = "\n".join(f"- rule {i}" for i in range(summary_bullets))
        parts.append(f"\n### 最小纪律摘要\n\n{bullets}\n")
    if with_install:
        parts.append(f"\n```bash\nnpx skills@latest add obra/superpowers-{p.parent.name}\n```\n")
    p.write_text("".join(parts), encoding="utf-8")


# ===== Check 1: 降级方案章节 =====

def test_check1_all_have_section(tmp_path):
    for n in BRIDGE_SKILLS:
        _make_bridge(tmp_path / n / "SKILL.md", with_degradation=True)
    r = check_has_degradation_section(tmp_path)
    assert r.passed, f"errors={r.errors}"


def test_check1_missing_one(tmp_path):
    for n in BRIDGE_SKILLS:
        _make_bridge(tmp_path / n / "SKILL.md", with_degradation=(n != "brainstorming"))
    r = check_has_degradation_section(tmp_path)
    assert not r.passed
    assert any("brainstorming" in e for e in r.errors)


def test_check1_missing_skill(tmp_path):
    _make_bridge(tmp_path / "brainstorming" / "SKILL.md", with_degradation=True)
    r = check_has_degradation_section(tmp_path)
    assert not r.passed
    assert any("缺少 bridge skill" in e for e in r.errors)


# ===== Check 2: 安装提示 =====

def test_check2_all_have_install(tmp_path):
    for n in BRIDGE_SKILLS:
        _make_bridge(tmp_path / n / "SKILL.md", with_install=True)
    r = check_has_install_hint(tmp_path)
    assert r.passed, f"errors={r.errors}"


def test_check2_missing_install(tmp_path):
    for n in BRIDGE_SKILLS:
        _make_bridge(tmp_path / n / "SKILL.md", with_install=(n != "tdd"))
    r = check_has_install_hint(tmp_path)
    assert not r.passed
    assert any("tdd" in e for e in r.errors)


def test_check2_wrong_format(tmp_path):
    for n in BRIDGE_SKILLS:
        _make_bridge(tmp_path / n / "SKILL.md")
    # 改成 npm 而不是 npx
    (tmp_path / "brainstorming" / "SKILL.md").write_text(
        "# x\n\n```bash\nnpm install obra/superpowers-brainstorming\n```\n",
        encoding="utf-8",
    )
    r = check_has_install_hint(tmp_path)
    assert not r.passed
    assert any("brainstorming" in e for e in r.errors)


# ===== Check 3: 最小纪律摘要 =====

def test_check3_all_have_summary(tmp_path):
    for n in BRIDGE_SKILLS:
        _make_bridge(tmp_path / n / "SKILL.md", with_summary=True, summary_bullets=4)
    r = check_has_discipline_summary(tmp_path)
    assert r.passed, f"errors={r.errors}"


def test_check3_missing_summary(tmp_path):
    for n in BRIDGE_SKILLS:
        _make_bridge(tmp_path / n / "SKILL.md", with_summary=(n != "verification-before-completion"))
    r = check_has_discipline_summary(tmp_path)
    assert not r.passed
    assert any("verification-before-completion" in e for e in r.errors)


def test_check3_too_few_bullets(tmp_path):
    for n in BRIDGE_SKILLS:
        _make_bridge(tmp_path / n / "SKILL.md", summary_bullets=4)
    # brainstorming 改为只有 2 条 bullet
    (tmp_path / "brainstorming" / "SKILL.md").write_text(
        "# x\n\n## 降级方案(superpowers 未装时)\n\n"
        "### 最小纪律摘要\n- a\n- b\n\n"
        "```bash\nnpx skills@latest add obra/superpowers-brainstorming\n```\n",
        encoding="utf-8",
    )
    r = check_has_discipline_summary(tmp_path)
    assert not r.passed
    assert any("brainstorming" in e and "3 条" in e for e in r.errors)


# ===== self-test =====

def test_self_test_runs():
    import subprocess
    r = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "bridge-completeness-check.py"), "--self-test"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"stderr={r.stderr}\nstdout={r.stdout}"


# ===== 真实仓库集成 =====

def test_real_repo_passes():
    """真实仓库 7 个 bridge 都已加降级方案,应通过。"""
    import subprocess
    repo = Path(__file__).parent.parent
    r = subprocess.run(
        [sys.executable, str(repo / "scripts" / "bridge-completeness-check.py"), "--strict"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"stderr={r.stderr}\nstdout={r.stdout}"


def test_real_repo_break_on_modify():
    """故意删 brainstorming 的降级章节,跑应 exit 1。"""
    import subprocess
    repo = Path(__file__).parent.parent
    target = repo / "skills" / "orchestration" / "development" / "brainstorming" / "SKILL.md"
    backup = target.read_text(encoding="utf-8")
    # 删 "## 降级方案" 段
    broken = backup.split("## 降级方案")[0]
    if backup == broken:
        return
    try:
        target.write_text(broken, encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(repo / "scripts" / "bridge-completeness-check.py"), "--strict"],
            capture_output=True, text=True,
        )
        assert r.returncode == 1, f"应 exit 1,实际 {r.returncode}\nstdout={r.stdout}"
    finally:
        target.write_text(backup, encoding="utf-8")