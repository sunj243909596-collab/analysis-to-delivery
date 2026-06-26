"""pytest 单元测试 for scripts/setup-check.py

覆盖 3 个 Check 的核心场景 + canonical/legacy 双路径。
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
CANONICAL_DIR = _mod.CANONICAL_DIR
PATH_ENTRIES = _mod.PATH_ENTRIES


def _write_canonical(tmp_path: Path, mapping):
    """Helper:写 canonical paths/<name>.md 内容。"""
    paths_dir = tmp_path / "paths"
    paths_dir.mkdir(exist_ok=True)
    for name, content in mapping.items():
        (paths_dir / name).write_text(content, encoding="utf-8")


# ===== Check 1: 文件存在 =====

def test_check_files_exist_canonical_pass(tmp_path):
    _write_canonical(tmp_path, {
        "knowledge-path.md": "# x",
        "compliance-path.md": "# x",
        "tech-stack-path.md": "# x",
        "doc-naming-path.md": "# x",
    })
    result = check_config_files_exist(tmp_path)
    assert result.passed
    assert not result.errors


def test_check_files_exist_missing(tmp_path):
    # 不创建任何文件
    result = check_config_files_exist(tmp_path)
    assert not result.passed
    assert len(result.errors) == 4  # 4 个文件都缺


def test_check_files_exist_empty(tmp_path):
    _write_canonical(tmp_path, {
        "knowledge-path.md": "",
        "compliance-path.md": "",
        "tech-stack-path.md": "",
        "doc-naming-path.md": "",
    })
    result = check_config_files_exist(tmp_path)
    assert not result.passed
    assert any("为空" in e for e in result.errors)


def test_check_files_exist_legacy_warns_only(tmp_path):
    """项目根的 legacy *-path.md 应通过(仅产生 warning)。"""
    legacy_map = {
        "knowledge-path.md": "## x\n\n- /root/foo\n",
        "compliance-path.md": "## x\n",
        "tech-stack-path.md": "## x\n",
        "doc-naming.md": "## x\n",
    }
    for name, content in legacy_map.items():
        (tmp_path / name).write_text(content, encoding="utf-8")
    result = check_config_files_exist(tmp_path)
    assert result.passed, f"errors={result.errors}"
    assert result.warnings, "legacy 项目根文件应产生 warning"


# ===== Check 2: 实质内容(非占位符) =====

def test_check_nonempty_only_comments(tmp_path):
    _write_canonical(tmp_path, {
        "knowledge-path.md": "<!-- only comment -->\n\n# 标题\n",
        "compliance-path.md": "<!-- only comment -->\n\n# 标题\n",
        "tech-stack-path.md": "<!-- only comment -->\n\n# 标题\n",
        "doc-naming-path.md": "<!-- only comment -->\n\n# 标题\n",
    })
    result = check_config_files_nonempty(tmp_path)
    assert not result.passed
    assert all("占位符" in e or "无实质内容" in e for e in result.errors)


def test_check_nonempty_with_content(tmp_path):
    _write_canonical(tmp_path, {
        "knowledge-path.md": "## 配置\n\n- /root/foo\n",
        "compliance-path.md": "## 配置\n\n- /root/compliance\n",
        "tech-stack-path.md": "## 配置\n\n- Java + Spring Boot\n",
        "doc-naming-path.md": "## 配置\n\n- 编号 01-09\n",
    })
    result = check_config_files_nonempty(tmp_path)
    assert result.passed


def test_check_nonempty_legacy_with_content(tmp_path):
    """legacy 项目根文件被识别时也应检查非空。"""
    for name in ("knowledge-path.md", "compliance-path.md",
                 "tech-stack-path.md", "doc-naming.md"):
        (tmp_path / name).write_text(
            "## x\n\n<!-- comment only -->\n# h\n",
            encoding="utf-8",
        )
    result = check_config_files_nonempty(tmp_path)
    assert not result.passed


# ===== Check 3: knowledge-path 真实路径 =====

def test_check_knowledge_path_no_real_path(tmp_path):
    _write_canonical(tmp_path, {
        "knowledge-path.md": "## 知识库\n\n请在此填入真实路径\n",
    })
    result = check_knowledge_path_has_real_path(tmp_path)
    assert not result.passed
    assert any("真实路径" in e for e in result.errors)


def test_check_knowledge_path_with_real_path(tmp_path):
    _write_canonical(tmp_path, {
        "knowledge-path.md": "## 知识库\n\n- /root/WMOS 知识库/01-WMOS核心/\n",
    })
    result = check_knowledge_path_has_real_path(tmp_path)
    assert result.passed


def test_check_knowledge_path_legacy_with_real_path(tmp_path):
    """legacy 路径下也应检查真实路径。"""
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

def test_example_wms_passes_legacy():
    """examples/01-wms-warehouse 应通过 setup-check(strict)(legacy 项目根文件)。"""
    import subprocess
    repo = Path(__file__).parent.parent
    r = subprocess.run(
        [sys.executable, str(repo / "scripts" / "setup-check.py"), "--strict",
         str(repo / "examples" / "01-wms-warehouse")],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"stderr={r.stderr}\nstdout={r.stdout}"


def test_repo_root_paths_templates_present():
    """本仓库根目录下的 paths/*.md 模板存在(只是模板,不做 strict pass 检查)。"""
    repo = Path(__file__).parent.parent
    for name in ("knowledge-path.md", "compliance-path.md",
                 "tech-stack-path.md", "doc-naming-path.md"):
        assert (repo / "paths" / name).exists(), f"missing paths/{name}"
