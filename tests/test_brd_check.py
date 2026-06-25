"""pytest 单元测试 for scripts/brd-check.py"""
import importlib.util
import sys
from pathlib import Path

import pytest


def _load_module():
    script = Path(__file__).parent.parent / "scripts" / "brd-check.py"
    spec = importlib.util.spec_from_file_location("brd_check", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_mod = _load_module()
check_brd_sections = _mod.check_brd_sections
check_brd_not_template = _mod.check_brd_not_template
BRD_REQUIRED_SECTIONS = _mod.BRD_REQUIRED_SECTIONS


# ===== Check 1: 9 章节齐全 =====

def test_brd_sections_complete(tmp_path):
    f = tmp_path / "01-业务需求文档 BRD.md"
    f.write_text(
        "\n".join(f"## {n}、{t}\n\n内容\n" for n, t in BRD_REQUIRED_SECTIONS),
        encoding="utf-8",
    )
    result = check_brd_sections(f)
    assert result.passed, f"errors={result.errors}"


def test_brd_sections_missing_5(tmp_path):
    f = tmp_path / "01-业务需求文档 BRD.md"
    f.write_text(
        "## 一、项目概述\n## 二、角色\n## 三、业务流程\n## 四、功能\n",
        encoding="utf-8",
    )
    result = check_brd_sections(f)
    assert not result.passed
    assert any("缺 5" in e for e in result.errors)


def test_brd_sections_file_not_exists(tmp_path):
    f = tmp_path / "01-业务需求文档 BRD.md"
    result = check_brd_sections(f)
    assert not result.passed
    assert any("不存在" in e for e in result.errors)


def test_brd_sections_heading_mismatch_warning(tmp_path):
    """章节存在但标题名与规范不一致 → warning 不 block。"""
    f = tmp_path / "01-业务需求文档 BRD.md"
    # 9 节都有,只是 6-9 节标题不同
    f.write_text(
        "## 一、项目概述\n## 二、角色与职责\n## 三、业务流程\n## 四、功能模块\n"
        "## 五、数据要求\n## 六、合规要求\n## 七、性能\n## 八、上线\n## 九、计划\n",
        encoding="utf-8",
    )
    result = check_brd_sections(f)
    assert result.passed  # 章节都在
    assert any("不一致" in w for w in result.warnings)


# ===== Check 2: 非模板 =====

def test_brd_not_template_warning(tmp_path):
    f = tmp_path / "01-业务需求文档 BRD.md"
    f.write_text(
        "\n".join(
            [f"## {n}、{t}\n\n{{{{ placeholder }}}} TBD TODO 占位\n" for n, t in BRD_REQUIRED_SECTIONS]
        ),
        encoding="utf-8",
    )
    result = check_brd_not_template(f)
    assert any("占位符" in w for w in result.warnings)


def test_brd_not_template_no_warning(tmp_path):
    f = tmp_path / "01-业务需求文档 BRD.md"
    f.write_text(
        "\n".join(f"## {n}、{t}\n\n实际内容\n" for n, t in BRD_REQUIRED_SECTIONS),
        encoding="utf-8",
    )
    result = check_brd_not_template(f)
    assert not result.warnings


# ===== self-test =====

def test_self_test_runs():
    import subprocess
    r = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "brd-check.py"), "--self-test"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"stderr={r.stderr}"
    assert "自检通过" in r.stdout


# ===== example 集成 =====

def test_example_wms_passes_strict():
    import subprocess
    repo = Path(__file__).parent.parent
    r = subprocess.run(
        [sys.executable, str(repo / "scripts" / "brd-check.py"), "--strict",
         str(repo / "examples" / "01-wms-warehouse")],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"stderr={r.stderr}\nstdout={r.stdout}"
