"""pytest 单元测试 for scripts/setup-check.py

覆盖 3 个 Check 的核心场景。
"""
import importlib.util
import sys
from pathlib import Path

import pytest


def _load_module():
    """动态加载 scripts/setup-check.py。"""
    script = Path(__file__).parent.parent / "scripts" / "setup-check.py"
    spec = importlib.util.spec_from_file_location("setup_check", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_mod = _load_module()
check_config_files_exist = _mod.check_config_files_exist
check_config_files_nonempty = _mod.check_config_files_nonempty
check_knowledge_path_has_real_path = _mod.check_knowledge_path_has_real_path
CONFIG_FILES = _mod.CONFIG_FILES


# ===== Check 1: 文件存在 =====

def test_check_files_exist_pass(tmp_path):
    for name in CONFIG_FILES:
        (tmp_path / name).write_text("# x", encoding="utf-8")
    result = check_config_files_exist(tmp_path)
    assert result.passed
    assert not result.errors


def test_check_files_exist_missing(tmp_path):
    # 不创建任何文件
    result = check_config_files_exist(tmp_path)
    assert not result.passed
    assert len(result.errors) == 4  # 4 个文件都缺


def test_check_files_exist_empty(tmp_path):
    for name in CONFIG_FILES:
        (tmp_path / name).write_text("", encoding="utf-8")
    result = check_config_files_exist(tmp_path)
    assert not result.passed
    assert any("为空" in e for e in result.errors)


# ===== Check 2: 实质内容(非占位符) =====

def test_check_nonempty_only_comments(tmp_path):
    for name in CONFIG_FILES:
        (tmp_path / name).write_text(
            "<!-- only comment -->\n\n# 标题\n",
            encoding="utf-8",
        )
    result = check_config_files_nonempty(tmp_path)
    assert not result.passed
    assert all("占位符" in e or "无实质内容" in e for e in result.errors)


def test_check_nonempty_with_content(tmp_path):
    for name in CONFIG_FILES:
        (tmp_path / name).write_text("## 配置\n\n- /root/foo\n", encoding="utf-8")
    result = check_config_files_nonempty(tmp_path)
    assert result.passed


# ===== Check 3: knowledge-path 真实路径 =====

def test_check_knowledge_path_no_real_path(tmp_path):
    (tmp_path / "knowledge-path.md").write_text(
        "## 知识库\n\n请在此填入真实路径\n",
        encoding="utf-8",
    )
    result = check_knowledge_path_has_real_path(tmp_path)
    assert not result.passed
    assert any("真实路径" in e for e in result.errors)


def test_check_knowledge_path_with_real_path(tmp_path):
    (tmp_path / "knowledge-path.md").write_text(
        "## 知识库\n\n- /root/WMOS 知识库/01-WMOS核心/\n",
        encoding="utf-8",
    )
    result = check_knowledge_path_has_real_path(tmp_path)
    assert result.passed


# ===== self-test 命令 =====

def test_self_test_runs():
    """--self-test 应 exit 0。"""
    import subprocess
    r = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "setup-check.py"), "--self-test"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"stderr={r.stderr}"
    assert "自检通过" in r.stdout


# ===== 现有 examples 集成测试 =====

def test_example_wms_passes():
    """examples/01-wms-warehouse 应通过 setup-check(strict)。"""
    import subprocess
    repo = Path(__file__).parent.parent
    r = subprocess.run(
        [sys.executable, str(repo / "scripts" / "setup-check.py"), "--strict",
         str(repo / "examples" / "01-wms-warehouse")],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"stderr={r.stderr}\nstdout={r.stdout}"
