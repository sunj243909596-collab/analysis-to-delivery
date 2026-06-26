"""pytest 单元测试 for scripts/rules-path-lint.py

覆盖：pass / unknown rule / unknown path / 重复 declaration / legacy 名 / missing declaration。
"""
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "rules_path_lint",
        Path(__file__).parent.parent / "scripts" / "rules-path-lint.py",
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["rules_path_lint"] = mod  # dataclass 需要 module 已注册
    spec.loader.exec_module(mod)
    return mod


_mod = _load_module()
lint = _mod.lint
KNOWN_RULES = _mod.KNOWN_RULES
KNOWN_PATHS = _mod.KNOWN_PATHS


def _build_minimal_skill(root: Path) -> None:
    """构建一个最小可工作 skill_root。"""
    (root / "rules").mkdir()
    for r in KNOWN_RULES:
        (root / "rules" / f"{r}.md").write_text(f"# {r}\n", encoding="utf-8")
    (root / "paths").mkdir()
    for p in KNOWN_PATHS:
        (root / "paths" / f"{p}.md").write_text(f"# {p}\n", encoding="utf-8")
    ui = root / "skills" / "user-invoked" / "demo"
    ui.mkdir(parents=True)
    (ui / "SKILL.md").write_text(
        "## Contract\n\n"
        "- Required rules: `stage-gate`, `no-field-guessing`\n"
        "- Required paths: `knowledge-path`, `doc-naming-path`\n",
        encoding="utf-8",
    )
    orch = root / "skills" / "orchestration" / "analysis-delivery-workflow"
    orch.mkdir(parents=True)
    (orch / "SKILL.md").write_text(
        "## Contract\n\n"
        "- Required rules: `stage-gate`, `doc-numbering`\n"
        "- Required paths: `knowledge-path`, `tech-stack-path`\n",
        encoding="utf-8",
    )


def _write_skill(root: Path, rules_block: str, paths_block: str) -> None:
    text = f"## Contract\n\n{rules_block}\n{paths_block}\n"
    (root / "skills" / "user-invoked" / "demo" / "SKILL.md").write_text(
        text, encoding="utf-8",
    )


# ===== pass =====

def test_lint_minimal_pass(tmp_path):
    _build_minimal_skill(tmp_path)
    rep = lint(tmp_path)
    assert not rep.has_errors, [str(e) for e in rep.errors]


# ===== unknown rule =====

def test_lint_unknown_rule_fails(tmp_path):
    _build_minimal_skill(tmp_path)
    _write_skill(
        tmp_path,
        "- Required rules: `stage-gate`, `no-such-rule`",
        "- Required paths: `knowledge-path`, `doc-naming-path`",
    )
    rep = lint(tmp_path)
    assert rep.has_errors
    assert any("no-such-rule" in e.message for e in rep.errors)


# ===== unknown path =====

def test_lint_unknown_path_fails(tmp_path):
    _build_minimal_skill(tmp_path)
    _write_skill(
        tmp_path,
        "- Required rules: `stage-gate`, `no-field-guessing`",
        "- Required paths: `knowledge-path`, `bogus-path`",
    )
    rep = lint(tmp_path)
    assert rep.has_errors
    assert any("bogus-path" in e.message for e in rep.errors)


# ===== missing declaration =====

def test_lint_missing_paths_declaration_fails(tmp_path):
    _build_minimal_skill(tmp_path)
    _write_skill(
        tmp_path,
        "- Required rules: `stage-gate`, `no-field-guessing`",
        "",  # 缺 paths
    )
    rep = lint(tmp_path)
    assert rep.has_errors
    assert any("Required paths" in e.message for e in rep.errors)


def test_lint_missing_rules_declaration_fails(tmp_path):
    _build_minimal_skill(tmp_path)
    _write_skill(
        tmp_path,
        "",
        "- Required paths: `knowledge-path`, `doc-naming-path`",
    )
    rep = lint(tmp_path)
    assert rep.has_errors
    assert any("Required rules" in e.message for e in rep.errors)


# ===== duplicate declaration =====

def test_lint_duplicate_rules_fails(tmp_path):
    _build_minimal_skill(tmp_path)
    _write_skill(
        tmp_path,
        "- Required rules: `stage-gate`\n- Required rules: `no-field-guessing`",
        "- Required paths: `knowledge-path`, `doc-naming-path`",
    )
    rep = lint(tmp_path)
    assert rep.has_errors
    assert any("重复的 Required rules" in e.message for e in rep.errors)


def test_lint_duplicate_paths_fails(tmp_path):
    _build_minimal_skill(tmp_path)
    _write_skill(
        tmp_path,
        "- Required rules: `stage-gate`, `no-field-guessing`",
        "- Required paths: `knowledge-path`\n- Required paths: `doc-naming-path`",
    )
    rep = lint(tmp_path)
    assert rep.has_errors
    assert any("重复的 Required paths" in e.message for e in rep.errors)


# ===== legacy name =====

def test_lint_legacy_sql_dialect_fails(tmp_path):
    _build_minimal_skill(tmp_path)
    _write_skill(
        tmp_path,
        "- Required rules: `sql-dialect-discipline`",
        "- Required paths: `knowledge-path`, `doc-naming-path`",
    )
    rep = lint(tmp_path)
    assert rep.has_errors
    assert any("sql-dialect-discipline" in e.message for e in rep.errors)


# ===== missing rules/*.md file =====

def test_lint_missing_rules_file_fails(tmp_path):
    _build_minimal_skill(tmp_path)
    (tmp_path / "rules" / "stage-gate.md").unlink()
    rep = lint(tmp_path)
    assert rep.has_errors
    assert any("stage-gate.md" in e.message for e in rep.errors)


def test_lint_missing_paths_file_fails(tmp_path):
    _build_minimal_skill(tmp_path)
    (tmp_path / "paths" / "knowledge-path.md").unlink()
    rep = lint(tmp_path)
    assert rep.has_errors
    assert any("knowledge-path.md" in e.message for e in rep.errors)


# ===== self-test command =====

def test_self_test_runs():
    r = subprocess.run(
        [sys.executable,
         str(Path(__file__).parent.parent / "scripts" / "rules-path-lint.py"),
         "--self-test"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"stderr={r.stderr}"
    assert "self-test" in r.stdout


# ===== repo 集成测试 =====

def test_repo_passes_lint():
    """本仓库自身应通过 rules-path-lint。"""
    r = subprocess.run(
        [sys.executable,
         str(Path(__file__).parent.parent / "scripts" / "rules-path-lint.py"),
         str(Path(__file__).parent.parent)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"stderr={r.stderr}\nstdout={r.stdout}"
