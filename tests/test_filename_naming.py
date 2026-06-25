"""pytest 单元测试 for scripts/filename-naming-check.py"""
import importlib.util
from pathlib import Path

import pytest


def _load_module():
    script = Path(__file__).parent.parent / "scripts" / "filename-naming-check.py"
    spec = importlib.util.spec_from_file_location("filename_naming_check", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_mod = _load_module()
_iter_md_files = _mod._iter_md_files
check_no_deprecated_filename = _mod.check_no_deprecated_filename
check_decisions_md_recommended = _mod.check_decisions_md_recommended
run_checks = _mod.run_checks
self_test = _mod.self_test
DEPRECATED_FILES = _mod.DEPRECATED_FILES


# ===== _iter_md_files =====

def test_iter_md_files_dir(tmp_path):
    (tmp_path / "a.md").write_text("a", encoding="utf-8")
    (tmp_path / "b.md").write_text("b", encoding="utf-8")
    files = _iter_md_files(tmp_path)
    assert len(files) == 2
    assert {f.name for f in files} == {"a.md", "b.md"}


def test_iter_md_files_single_file(tmp_path):
    p = tmp_path / "x.md"
    p.write_text("x", encoding="utf-8")
    files = _iter_md_files(p)
    assert files == [p]


def test_iter_md_files_recursive(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    (tmp_path / "a.md").write_text("a", encoding="utf-8")
    (sub / "b.md").write_text("b", encoding="utf-8")
    files = _iter_md_files(tmp_path)
    assert len(files) == 2


# ===== check_no_deprecated_filename =====

def test_check_no_deprecated_filename_clean(tmp_path):
    p = tmp_path / "decisions.md"
    p.write_text("# ok\n", encoding="utf-8")
    r = check_no_deprecated_filename(p)
    assert r.passed
    assert not r.errors


def test_check_no_deprecated_filename_flagged(tmp_path):
    p = tmp_path / "config-used.md"
    p.write_text("# old\n", encoding="utf-8")
    r = check_no_deprecated_filename(p)
    assert not r.passed
    assert any("config-used.md" in e for e in r.errors)
    assert any("decisions.md" in e for e in r.errors)


# ===== check_decisions_md_recommended =====

def test_check_decisions_md_recommended_clean(tmp_path):
    p = tmp_path / "decisions.md"
    p.write_text("# ok\n", encoding="utf-8")
    r = check_decisions_md_recommended(p)
    assert r.passed
    assert not r.warnings


def test_check_decisions_md_recommended_suggest(tmp_path):
    p = tmp_path / "config-used.md"
    p.write_text("# old\n", encoding="utf-8")
    r = check_decisions_md_recommended(p)
    assert r.warnings
    assert any("decisions.md" in w for w in r.warnings)


# ===== run_checks =====

def test_run_checks_empty_dir(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    r = run_checks(empty, "strict")
    # 空目录 → 1 个 warning(空目录提示), 0 error
    assert r.has_warnings
    assert not r.has_errors


def test_run_checks_all_clean(tmp_path):
    (tmp_path / "decisions.md").write_text("# ok\n", encoding="utf-8")
    (tmp_path / "01-brd.md").write_text("# brd\n", encoding="utf-8")
    r = run_checks(tmp_path, "strict")
    assert not r.has_errors


def test_run_checks_with_deprecated(tmp_path):
    (tmp_path / "decisions.md").write_text("# ok\n", encoding="utf-8")
    (tmp_path / "config-used.md").write_text("# old\n", encoding="utf-8")
    r = run_checks(tmp_path, "strict")
    assert r.has_errors


# ===== 真实仓库校验 =====

def test_real_repo_passes():
    """examples/ 下不应有 config-used.md(已迁到 decisions.md)。"""
    repo = Path(__file__).parent.parent
    examples_dir = repo / "examples"
    if not examples_dir.exists():
        pytest.skip("examples/ 不存在")
    r = run_checks(examples_dir, "strict")
    if r.has_errors:
        msgs = [f"  {c.name}: {e}" for c in r.checks for e in c.errors]
        pytest.fail(
            "真实仓库 filename-naming 失败:\n" + "\n".join(msgs)
        )


def test_real_repo_3_examples_have_decisions_md():
    """三个 example 都应有自己的 decisions.md(而不是 config-used.md)。"""
    repo = Path(__file__).parent.parent
    examples = [
        repo / "examples" / "01-wms-warehouse",
        repo / "examples" / "02-saas-dashboard",
        repo / "examples" / "03-mobile-app",
    ]
    for ex in examples:
        if not ex.exists():
            continue
        assert (ex / "decisions.md").exists(), f"{ex} 应有 decisions.md"
        assert not (ex / "config-used.md").exists(), (
            f"{ex} 不应再有 config-used.md(已迁到 decisions.md)"
        )


def test_real_repo_break_on_revert(tmp_path):
    """模拟把 decisions.md 改回 config-used.md,应被 lint 抓到。"""
    p = tmp_path / "config-used.md"
    p.write_text("# old\n", encoding="utf-8")
    r = run_checks(p, "strict")
    assert r.has_errors


# ===== self-test =====

def test_self_test_runs():
    rc = self_test()
    assert rc == 0


# ===== 弃用白名单覆盖 =====

def test_deprecated_list_contains_config_used():
    """白名单应明确包含 config-used.md(防止新增弃用时漏掉)。"""
    assert "config-used.md" in DEPRECATED_FILES
