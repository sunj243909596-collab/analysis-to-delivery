"""pytest 单元测试 for scripts/dev-design-backtest.py"""
import importlib.util
import sys
from pathlib import Path

import pytest


def _load_module():
    script = Path(__file__).parent.parent / "scripts" / "dev-design-backtest.py"
    spec = importlib.util.spec_from_file_location("dev_design_backtest", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_mod = _load_module()
check_4_categories_present = _mod.check_4_categories_present
check_no_fail_marker = _mod.check_no_fail_marker
check_conclusion_present = _mod.check_conclusion_present
BACKTEST_CATEGORIES = _mod.BACKTEST_CATEGORIES


# ===== Check 1: 4 大类齐全 =====

def test_4_categories_complete(tmp_path):
    f = tmp_path / "08-设计回测报告.md"
    f.write_text(
        "# 设计回测\n\n"
        "## 数据模型回测\n✅\n\n"
        "## 业务规则回测\n✅\n\n"
        "## 状态机回测\n✅\n\n"
        "## 字段对齐回测\n✅\n",
        encoding="utf-8",
    )
    result = check_4_categories_present(f)
    assert result.passed


def test_4_categories_missing(tmp_path):
    f = tmp_path / "08-设计回测报告.md"
    f.write_text(
        "# 设计回测\n\n## 数据模型回测\n✅\n## 业务规则回测\n✅\n",
        encoding="utf-8",
    )
    result = check_4_categories_present(f)
    assert not result.passed
    assert any("缺" in e for e in result.errors)


# ===== Check 2: 无 ❌ =====

def test_no_fail_clean(tmp_path):
    f = tmp_path / "08-设计回测报告.md"
    f.write_text(
        "## 数据模型回测\n✅\n## 业务规则回测\n⚠️\n## 状态机回测\n✅\n## 字段对齐回测\n✅\n",
        encoding="utf-8",
    )
    result = check_no_fail_marker(f)
    assert result.passed


def test_no_fail_blocks(tmp_path):
    f = tmp_path / "08-设计回测报告.md"
    f.write_text(
        "## 数据模型回测\n❌ 失败\n## 业务规则回测\n✅\n## 状态机回测\n✅\n## 字段对齐回测\n✅\n",
        encoding="utf-8",
    )
    result = check_no_fail_marker(f)
    assert not result.passed
    assert any("❌" in e for e in result.errors)


# ===== Check 3: 整体结论 =====

def test_conclusion_pass(tmp_path):
    f = tmp_path / "08-设计回测报告.md"
    f.write_text("## 整体结论\n\n✅ 全部通过,可进入阶段 8\n", encoding="utf-8")
    result = check_conclusion_present(f)
    assert not any("未识别" in w for w in result.warnings)


def test_conclusion_missing(tmp_path):
    f = tmp_path / "08-设计回测报告.md"
    f.write_text("## 其它节\n内容\n", encoding="utf-8")
    result = check_conclusion_present(f)
    assert any("整体结论" in w or "未识别" in w for w in result.warnings)


# ===== self-test =====

def test_self_test_runs():
    import subprocess
    r = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "dev-design-backtest.py"), "--self-test"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"stderr={r.stderr}"
