"""pytest 单元测试 for scripts/testcase-coverage-check.py"""
import importlib.util
import sys
from pathlib import Path

import pytest


def _load_module():
    script = Path(__file__).parent.parent / "scripts" / "testcase-coverage-check.py"
    spec = importlib.util.spec_from_file_location("testcase_check", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_mod = _load_module()
check_5_categories_covered = _mod.check_5_categories_covered
check_each_testcase_has_id = _mod.check_each_testcase_has_id


# ===== Check 1: 5 大类齐全 =====

def test_5_categories_complete(tmp_path):
    f = tmp_path / "07-测试用例设计.md"
    f.write_text(
        "# 用例\n\n"
        "## 正常路径\nTC-001 happy\n\n"
        "## 边界条件\nTC-002 极值\n\n"
        "## 异常路径\nTC-003 错误\n\n"
        "## 合规校验\nTC-004 GSP\n\n"
        "## 性能/安全\nTC-005 并发\n",
        encoding="utf-8",
    )
    result = check_5_categories_covered(f)
    assert result.passed, f"errors={result.errors}"


def test_5_categories_missing_2(tmp_path):
    f = tmp_path / "07-测试用例设计.md"
    f.write_text(
        "# 用例\n\n"
        "## 正常路径\nTC-001\n\n"
        "## 边界条件\nTC-002\n\n"
        "## 异常路径\nTC-003\n",
        encoding="utf-8",
    )
    result = check_5_categories_covered(f)
    assert not result.passed
    assert any("缺" in e for e in result.errors)


def test_5_categories_file_not_exists(tmp_path):
    f = tmp_path / "07-测试用例设计.md"
    result = check_5_categories_covered(f)
    assert not result.passed
    assert any("不存在" in e for e in result.errors)


# ===== Check 2: TC 编号足够 =====

def test_tc_id_enough(tmp_path):
    f = tmp_path / "07-测试用例设计.md"
    f.write_text(
        "TC-001 x\nTC-002 x\nTC-003 x\nTC-004 x\nTC-005 x\n",
        encoding="utf-8",
    )
    result = check_each_testcase_has_id(f)
    assert result.passed


def test_tc_id_too_few(tmp_path):
    f = tmp_path / "07-测试用例设计.md"
    f.write_text("TC-001 x\nTC-002 x\n", encoding="utf-8")
    result = check_each_testcase_has_id(f)
    assert not result.passed
    assert any("至少 5" in e for e in result.errors)


# ===== self-test =====

def test_self_test_runs():
    import subprocess
    r = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "testcase-coverage-check.py"), "--self-test"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"stderr={r.stderr}"


# ===== 关键反例:严禁把"中英文"当两类 =====

def test_categories_dedup():
    """5 大类是单数概念:即使文档用同义词(如'边界'/'边界条件'),也只算一类。"""
    from pathlib import Path as P
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        f = P(tmp) / "07-测试用例设计.md"
        f.write_text(
            "# 用例\n\n"
            "## 正常路径\nTC-001\n\n"
            "## 边界\nTC-002\n\n"  # '边界' 算作 '边界条件'
            "## 异常\nTC-003\n\n"
            "## 合规\nTC-004\n\n"
            "## 性能\nTC-005\n",
            encoding="utf-8",
        )
        result = check_5_categories_covered(f)
        assert result.passed, f"errors={result.errors}"
