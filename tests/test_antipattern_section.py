"""pytest 单元测试 for scripts/antipattern-section-check.py"""
import importlib.util
from pathlib import Path

import pytest


def _load_module():
    script = Path(__file__).parent.parent / "scripts" / "antipattern-section-check.py"
    spec = importlib.util.spec_from_file_location(
        "antipattern_section_check", script
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_mod = _load_module()
check_antipattern_section = _mod.check_antipattern_section
check_antipattern_items = _mod.check_antipattern_items
run_checks = _mod.run_checks
self_test = _mod.self_test
USER_INVOKED_SKILLS = _mod.USER_INVOKED_SKILLS
MIN_ITEMS = _mod.MIN_ITEMS


# ===== check_antipattern_section =====

def test_section_present(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text("# x\n\n## 反模式\n- ❌ a\n- ❌ b\n- ❌ c\n", encoding="utf-8")
    r = check_antipattern_section(p)
    assert r.passed


def test_section_missing(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text("# x\n\n## 结束条件\n- [ ] y\n", encoding="utf-8")
    r = check_antipattern_section(p)
    assert not r.passed


# ===== check_antipattern_items =====

def test_items_enough(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text(
        "# x\n\n## 反模式\n- ❌ a\n- ❌ b\n- ❌ c\n- ❌ d\n\n## 结束\n",
        encoding="utf-8",
    )
    r = check_antipattern_items(p)
    assert r.passed


def test_items_too_few(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text("# x\n\n## 反模式\n- ❌ a\n- ❌ b\n\n## 结束\n", encoding="utf-8")
    r = check_antipattern_items(p)
    assert not r.passed
    assert any(str(MIN_ITEMS) in e for e in r.errors)


def test_items_no_section_no_check(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text("# x\n\n## 结束\n", encoding="utf-8")
    r = check_antipattern_items(p)
    # 没 section 时 Check 2 不报错(已由 Check 1 报)
    assert r.passed


def test_items_counted_per_section(tmp_path):
    """❌ 在 ## 反模式 之前的不应计入。"""
    p = tmp_path / "SKILL.md"
    p.write_text(
        "# x\n\n"
        "- ❌ outside\n- ❌ outside\n- ❌ outside\n\n"
        "## 反模式\n"
        "- ❌ in\n- ❌ in\n- ❌ in\n\n"
        "## 结束\n",
        encoding="utf-8",
    )
    r = check_antipattern_items(p)
    assert r.passed  # 段内 3 条 = MIN_ITEMS


def test_items_stops_at_next_h2(tmp_path):
    """❌ 在 ## 下一个段落 后不应计入。"""
    p = tmp_path / "SKILL.md"
    p.write_text(
        "# x\n\n## 反模式\n- ❌ in\n- ❌ in\n- ❌ in\n\n"
        "## 结束条件\n- ❌ outside\n",
        encoding="utf-8",
    )
    r = check_antipattern_items(p)
    assert r.passed  # 只数 ## 反模式 段内 3 条


# ===== run_checks =====

def test_run_checks_dir_no_user_invoked(tmp_path):
    r = run_checks(tmp_path, "strict")
    assert r.has_errors


def test_run_checks_mixed(tmp_path):
    good = tmp_path / "grill-task"
    good.mkdir()
    (good / "SKILL.md").write_text(
        "## 反模式\n- ❌ a\n- ❌ b\n- ❌ c\n", encoding="utf-8"
    )
    bad = tmp_path / "to-brd"
    bad.mkdir()
    (bad / "SKILL.md").write_text(
        "## 结束条件\n- [ ] y\n", encoding="utf-8"
    )
    r = run_checks(tmp_path, "strict")
    assert r.has_errors


# ===== 真实仓库 =====

def test_real_repo_all_user_invoked_have_section():
    """真实仓库 skills/user-invoked/ 下所有 SKILL.md 都应有 ## 反模式 + ≥3 ❌。"""
    repo = Path(__file__).parent.parent
    target = repo / "skills" / "user-invoked"
    if not target.exists():
        pytest.skip("skills/user-invoked/ 不存在")
    r = run_checks(target, "strict")
    if r.has_errors:
        msgs = [f"  {c.name}: {e}" for c in r.checks for e in c.errors]
        pytest.fail(
            "真实仓库反模式章节校验失败:\n" + "\n".join(msgs)
        )


def test_real_repo_9_user_invoked_covered():
    """USER_INVOKED_SKILLS 9 个白名单都必须在仓库存在。"""
    repo = Path(__file__).parent.parent
    target = repo / "skills" / "user-invoked"
    if not target.exists():
        pytest.skip("skills/user-invoked/ 不存在")
    missing = [s for s in USER_INVOKED_SKILLS if not (target / s / "SKILL.md").exists()]
    assert not missing, f"9 个 user-invoked skill 缺: {missing}"


def test_real_repo_break_on_delete():
    """删除某个 skill 的 ## 反模式 段 → 应被 lint 抓到。"""
    import tempfile
    repo = Path(__file__).parent.parent
    target = repo / "skills" / "user-invoked"
    if not target.exists():
        pytest.skip("skills/user-invoked/ 不存在")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        # 复制 grill-task 到 tmpdir
        src_skill = target / "grill-task"
        if not src_skill.exists():
            pytest.skip("grill-task 不存在")
        dst = tmp_path / "grill-task"
        dst.mkdir()
        text = (src_skill / "SKILL.md").read_text(encoding="utf-8")
        # 故意删 ## 反模式 段
        import re
        text = re.sub(r"^##\s+反模式\s*\n.*?(?=^##\s+|\Z)", "", text, flags=re.MULTILINE | re.DOTALL)
        (dst / "SKILL.md").write_text(text, encoding="utf-8")
        r = run_checks(tmp_path, "strict")
        assert r.has_errors


# ===== self-test =====

def test_self_test_runs():
    rc = self_test()
    assert rc == 0