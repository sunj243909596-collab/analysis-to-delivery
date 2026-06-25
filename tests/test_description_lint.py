"""pytest 单元测试 for scripts/description-lint.py"""
import importlib.util
import sys
from pathlib import Path

import pytest


def _load_module():
    script = Path(__file__).parent.parent / "scripts" / "description-lint.py"
    spec = importlib.util.spec_from_file_location("description_lint", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_mod = _load_module()
_extract_description = _mod._extract_description
check_description_exists = _mod.check_description_exists
check_description_length = _mod.check_description_length
check_description_not_too_generic = _mod.check_description_not_too_generic
run_checks = _mod.run_checks
self_test = _mod.self_test
MIN_LEN = _mod.MIN_LEN
MAX_LEN = _mod.MAX_LEN


# ===== _extract_description =====

def test_extract_description_normal():
    p = Path("/tmp/_d1.md")
    p.write_text("---\ndescription: hello world\n---\n# body\n", encoding="utf-8")
    desc, n = _extract_description(p)
    assert desc == "hello world"
    assert n == 11


def test_extract_description_missing():
    p = Path("/tmp/_d2.md")
    p.write_text("---\nname: foo\n---\n", encoding="utf-8")
    desc, n = _extract_description(p)
    assert desc is None
    assert n == 0


def test_extract_description_no_frontmatter():
    p = Path("/tmp/_d3.md")
    p.write_text("# no frontmatter\n", encoding="utf-8")
    desc, _ = _extract_description(p)
    assert desc is None


def test_extract_description_chinese():
    p = Path("/tmp/_d4.md")
    p.write_text("---\ndescription: 中文描述\n---\n", encoding="utf-8")
    desc, n = _extract_description(p)
    assert desc == "中文描述"
    assert n == 4


# ===== check_description_exists =====

def test_check_description_exists_ok(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text("---\ndescription: x\n---\n", encoding="utf-8")
    r = check_description_exists(p)
    assert r.passed


def test_check_description_exists_missing(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text("---\nname: x\n---\n", encoding="utf-8")
    r = check_description_exists(p)
    assert not r.passed


# ===== check_description_length =====

def test_check_description_length_ok(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text(f"---\ndescription: {'中' * 100}\n---\n", encoding="utf-8")
    r = check_description_length(p)
    assert r.passed
    assert r.warnings  # 应有 warning 列出长度


def test_check_description_length_too_short(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text(f"---\ndescription: {'短' * 50}\n---\n", encoding="utf-8")
    r = check_description_length(p)
    assert not r.passed
    assert any(str(MIN_LEN) in e for e in r.errors)


def test_check_description_length_too_long(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text(f"---\ndescription: {'长' * 200}\n---\n", encoding="utf-8")
    r = check_description_length(p)
    assert not r.passed
    assert any(str(MAX_LEN) in e for e in r.errors)


def test_check_description_length_boundary_min(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text(f"---\ndescription: {'x' * MIN_LEN}\n---\n", encoding="utf-8")
    r = check_description_length(p)
    assert r.passed  # 边界 = MIN_LEN 应通过


def test_check_description_length_boundary_max(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text(f"---\ndescription: {'x' * MAX_LEN}\n---\n", encoding="utf-8")
    r = check_description_length(p)
    assert r.passed  # 边界 = MAX_LEN 应通过


# ===== check_description_not_too_generic =====

def test_check_description_not_generic_ok(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text(
        f"---\ndescription: {'具体描述' * 25}\n---\n",
        encoding="utf-8",
    )
    r = check_description_not_too_generic(p)
    assert r.passed


def test_check_description_not_generic_fail(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text("---\ndescription: XX 助手\n---\n", encoding="utf-8")
    r = check_description_not_too_generic(p)
    assert not r.passed
    assert any("空泛" in e for e in r.errors)


# ===== run_checks =====

def test_run_checks_dir_no_skill(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    r = run_checks(empty, "strict")
    assert r.has_errors


def test_run_checks_dir_mixed(tmp_path):
    (tmp_path / "ok.md").write_text(
        f"---\ndescription: {'合' * 100}\n---\n", encoding="utf-8"
    )
    (tmp_path / "bad.md").write_text(
        f"---\ndescription: {'短' * 50}\n---\n", encoding="utf-8"
    )
    r = run_checks(tmp_path, "strict")
    # 至少 1 个 error (来自 bad.md 的长度)
    assert r.has_errors


# ===== 真实仓库校验 =====

def test_real_repo_passes():
    """仓库根目录 skills/ 下所有 SKILL.md 应通过 description-lint。"""
    repo = Path(__file__).parent.parent
    skills_dir = repo / "skills"
    if not skills_dir.exists():
        pytest.skip("skills/ 不存在")
    r = run_checks(skills_dir, "strict")
    if r.has_errors:
        msgs = [f"  {c.name}: {e}" for c in r.checks for e in c.errors]
        pytest.fail(
            "真实仓库 description-lint 失败:\n" + "\n".join(msgs)
        )


def test_real_repo_break_on_modify(tmp_path):
    """模拟把 description 改坏,应被 lint 抓到。"""
    repo = Path(__file__).parent.parent
    skills_dir = repo / "skills"
    if not skills_dir.exists():
        pytest.skip("skills/ 不存在")
    # 复制一个 SKILL.md 到 tmp,改坏 description
    src = next(iter(skills_dir.rglob("SKILL.md")))
    bad = tmp_path / "SKILL.md"
    bad.write_text(
        f"---\ndescription: {'x' * 30}\n---\n# body\n",
        encoding="utf-8",
    )
    r = run_checks(bad, "strict")
    assert r.has_errors


# ===== self-test =====

def test_self_test_runs():
    rc = self_test()
    assert rc == 0