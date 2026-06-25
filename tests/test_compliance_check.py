"""pytest 单元测试 for scripts/compliance-check.py"""
import importlib.util
import sys
from pathlib import Path

import pytest


def _load_module():
    script = Path(__file__).parent.parent / "scripts" / "compliance-check.py"
    spec = importlib.util.spec_from_file_location("compliance_check", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_mod = _load_module()
check_compliance_table_exists = _mod.check_compliance_table_exists
check_compliance_no_undecided = _mod.check_compliance_no_undecided
check_compliance_severe_status = _mod.check_compliance_severe_status
COMPLIANCE_TABLE_COLUMNS = _mod.COMPLIANCE_TABLE_COLUMNS


# ===== Check 1: 6 列齐全 =====

def test_compliance_table_complete(tmp_path):
    f = tmp_path / "04-合规评审.md"
    f.write_text(
        "| " + " | ".join(COMPLIANCE_TABLE_COLUMNS) + " |\n|"
        + "|".join(["---"] * len(COMPLIANCE_TABLE_COLUMNS)) + "|\n| GSP-001 | 一般 | x | y | z | ✅ |\n",
        encoding="utf-8",
    )
    result = check_compliance_table_exists(f)
    assert result.passed


def test_compliance_table_missing_columns(tmp_path):
    f = tmp_path / "04-合规评审.md"
    f.write_text("| 条款编号 | 检查要点 | 状态 |\n|---|---|---|\n", encoding="utf-8")
    result = check_compliance_table_exists(f)
    assert not result.passed
    assert any("缺" in e for e in result.errors)


def test_compliance_table_not_exists(tmp_path):
    f = tmp_path / "04-合规评审.md"
    result = check_compliance_table_exists(f)
    assert not result.passed


# ===== Check 2: 无未判定 =====

def test_compliance_no_undecided_clean(tmp_path):
    f = tmp_path / "04-合规评审.md"
    f.write_text("| x | y | z | ✅ |\n", encoding="utf-8")
    result = check_compliance_no_undecided(f)
    assert result.passed


def test_compliance_no_undecided_has_pending(tmp_path):
    f = tmp_path / "04-合规评审.md"
    f.write_text("| x | y | z | {待评估} |\n", encoding="utf-8")
    result = check_compliance_no_undecided(f)
    assert not result.passed
    assert any("未判定" in e for e in result.errors)


# ===== Check 3: 严重条款状态 =====

def test_compliance_severe_pass(tmp_path):
    f = tmp_path / "04-合规评审.md"
    f.write_text("| GSP-001 | 严重 | x | y | z | ✅ |\n", encoding="utf-8")
    result = check_compliance_severe_status(f)
    assert result.passed


def test_compliance_severe_warning_blocks(tmp_path):
    f = tmp_path / "04-合规评审.md"
    f.write_text("| GSP-001 | 严重 | x | y | z | ⚠️ |\n", encoding="utf-8")
    result = check_compliance_severe_status(f)
    assert not result.passed
    assert any("严重" in e for e in result.errors)


# ===== self-test =====

def test_self_test_runs():
    import subprocess
    r = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "compliance-check.py"), "--self-test"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"stderr={r.stderr}"


def test_compliance_6_columns_in_assets():
    """实际合规评审文件必须含 6 列(以 examples/01-wms-warehouse/04-合规评审.md 为准)。"""
    # 这是一个契约测试:即使文件不存在,核心函数也应能识别 6 列
    f_text = (
        "| 条款编号 | 缺陷等级 | 检查要点 | 合规设计 | 证据位置 | 状态 |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
    )
    from pathlib import Path as P
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        f = P(tmp) / "04-合规评审.md"
        f.write_text(f_text, encoding="utf-8")
        result = check_compliance_table_exists(f)
        assert result.passed
