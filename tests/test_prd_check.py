"""pytest 单元测试 for scripts/prd-check.py"""
import importlib.util
import sys
from pathlib import Path

import pytest


def _load_module():
    script = Path(__file__).parent.parent / "scripts" / "prd-check.py"
    spec = importlib.util.spec_from_file_location("prd_check", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_mod = _load_module()
check_prd_sections = _mod.check_prd_sections
check_prd_section7_signoff = _mod.check_prd_section7_signoff
PRD_REQUIRED_SECTIONS = _mod.PRD_REQUIRED_SECTIONS


# ===== Check 1: 8 章节齐全 =====

def test_prd_sections_complete(tmp_path):
    f = tmp_path / "05-产品需求文档 PRD.md"
    f.write_text(
        "\n".join(f"## {n}、{t}\n\n内容\n" for n, t in PRD_REQUIRED_SECTIONS),
        encoding="utf-8",
    )
    result = check_prd_sections(f)
    assert result.passed


def test_prd_sections_missing_3(tmp_path):
    f = tmp_path / "05-产品需求文档 PRD.md"
    f.write_text(
        "## 一、产品概述\n## 二、用户故事\n## 三、功能需求\n## 四、非功能需求\n## 五、数据需求\n",
        encoding="utf-8",
    )
    result = check_prd_sections(f)
    assert not result.passed
    assert any("缺 3" in e for e in result.errors)


# ===== Check 2: §七 白名单话术签字 =====

def test_section7_signed_pass(tmp_path):
    f = tmp_path / "05-产品需求文档 PRD.md"
    content = ""
    for n, t in PRD_REQUIRED_SECTIONS:
        if n == "七":
            content += "## 七、验收标准\n\n> 签字: 我已全部确认,可以进入下一步\n\n"
        else:
            content += f"## {n}、{t}\n\n内容\n\n"
    f.write_text(content, encoding="utf-8")
    result = check_prd_section7_signoff(f)
    assert result.passed, f"errors={result.errors}"


def test_section7_no_signoff(tmp_path):
    f = tmp_path / "05-产品需求文档 PRD.md"
    content = ""
    for n, t in PRD_REQUIRED_SECTIONS:
        if n == "七":
            content += "## 七、验收标准\n\n1. AC-1\n2. AC-2\n\n"
        else:
            content += f"## {n}、{t}\n\n内容\n\n"
    f.write_text(content, encoding="utf-8")
    result = check_prd_section7_signoff(f)
    assert not result.passed
    assert any("白名单话术" in e for e in result.errors)


def test_section7_weak_signoff_rejected(tmp_path):
    """'OK'/'好' 等模糊话术不能算签字。"""
    f = tmp_path / "05-产品需求文档 PRD.md"
    content = ""
    for n, t in PRD_REQUIRED_SECTIONS:
        if n == "七":
            content += "## 七、验收标准\n\n> 用户：好,继续\n\n"
        else:
            content += f"## {n}、{t}\n\n内容\n\n"
    f.write_text(content, encoding="utf-8")
    result = check_prd_section7_signoff(f)
    assert not result.passed


# ===== self-test =====

def test_self_test_runs():
    import subprocess
    r = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "prd-check.py"), "--self-test"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"stderr={r.stderr}"


# ===== 反例:严禁接受英文 OK/LGTM 当签字 =====

def test_section7_english_ok_rejected(tmp_path):
    f = tmp_path / "05-产品需求文档 PRD.md"
    content = ""
    for n, t in PRD_REQUIRED_SECTIONS:
        if n == "七":
            content += "## 七、验收标准\n\n> LGTM\n> OK\n\n"
        else:
            content += f"## {n}、{t}\n\n内容\n\n"
    f.write_text(content, encoding="utf-8")
    result = check_prd_section7_signoff(f)
    assert not result.passed
