"""pytest 单元测试 for scripts/flow-to-mermaid.py --ascii-strict 模式(plan §P1-2)"""
import importlib.util
import sys
from pathlib import Path


def _load_module():
    script = Path(__file__).parent.parent / "scripts" / "flow-to-mermaid.py"
    spec = importlib.util.spec_from_file_location("f2m", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_mod = _load_module()
check_ascii_has_backflow = _mod.check_ascii_has_backflow
check_mermaid_no_classdef = _mod.check_mermaid_no_classdef


# ===== 测试 fixtures =====

ASCII_NO_LOOP = """\
┌──────┐
│ 状态A │
└──────┘
   │
   ▼
┌──────┐
│ 状态B │
└──────┘
   │
   ▼
┌──────┐
│ 状态C │
└──────┘
"""

ASCII_WITH_LOOP = """\
┌──────┐
│ 状态A │
└──────┘
   │
   ▼
┌──────┐
│ 状态B │
└──────┘
   │
   ▼
┌──────┐
│ 状态A │
└──────┘
"""

MMD_WITH_CLASSDEF = """\
graph LR
    classDef foo fill:#f9f
    A["状态A"] --> B["状态B"]
"""

MMD_CLEAN = """\
graph LR
    A["状态A"] --> B["状态B"]
    B --> C["状态C"]
"""


# ===== ASCII 回流闭环检查 =====

def test_check_ascii_no_loop_fails():
    ok, msg = check_ascii_has_backflow(ASCII_NO_LOOP)
    assert not ok
    assert "回流闭环" in msg or "复用" in msg


def test_check_ascii_with_loop_passes():
    ok, msg = check_ascii_has_backflow(ASCII_WITH_LOOP)
    assert ok, f"应通过,实际: {msg}"
    assert "状态A" in msg


def test_check_ascii_empty_passes():
    """无 box 时不报错(让其它 check 决定)。"""
    ok, msg = check_ascii_has_backflow("# header\nonly text\n")
    assert ok
    assert "no boxes" in msg


# ===== Mermaid classDef 检查 =====

def test_check_mermaid_classdef_fails():
    ok, msg = check_mermaid_no_classdef(MMD_WITH_CLASSDEF)
    assert not ok
    assert "classDef" in msg


def test_check_mermaid_clean_passes():
    ok, msg = check_mermaid_no_classdef(MMD_CLEAN)
    assert ok, f"应通过,实际: {msg}"
    assert "无 classDef" in msg


# ===== self-test =====

def test_self_test_runs():
    import subprocess
    r = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "flow-to-mermaid.py"), "--self-test"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"stderr={r.stderr}\nstdout={r.stdout}"


# ===== 端到端 CLI =====

def test_cli_ascii_strict_no_loop(tmp_path):
    """--ascii-strict 对无回流的图应 exit 1。"""
    import subprocess
    src = tmp_path / "业务流程图-no-loop.txt"
    src.write_text(ASCII_NO_LOOP, encoding="utf-8")
    r = subprocess.run(
        [sys.executable,
         str(Path(__file__).parent.parent / "scripts" / "flow-to-mermaid.py"),
         "--ascii-strict", str(src)],
        capture_output=True, text=True,
    )
    assert r.returncode == 1, f"应 exit 1,实际 {r.returncode}\n{r.stdout}"


def test_cli_ascii_strict_with_loop(tmp_path):
    """--ascii-strict 对有回流的图应 exit 0。"""
    import subprocess
    src = tmp_path / "业务流程图-with-loop.txt"
    src.write_text(ASCII_WITH_LOOP, encoding="utf-8")
    r = subprocess.run(
        [sys.executable,
         str(Path(__file__).parent.parent / "scripts" / "flow-to-mermaid.py"),
         "--ascii-strict", str(src)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"应 exit 0,实际 {r.returncode}\n{r.stdout}"


def test_cli_default_still_works(tmp_path):
    """默认(无 --ascii-strict)行为不变:即使无回流也 exit 0。"""
    import subprocess
    src = tmp_path / "业务流程图-no-loop.txt"
    src.write_text(ASCII_NO_LOOP, encoding="utf-8")
    r = subprocess.run(
        [sys.executable,
         str(Path(__file__).parent.parent / "scripts" / "flow-to-mermaid.py"),
         str(src)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"默认模式应 exit 0,实际 {r.returncode}\n{r.stdout}"


def test_cli_json_output(tmp_path):
    """--json 输出应含 strict_results。"""
    import subprocess
    import json
    src = tmp_path / "业务流程图-with-loop.txt"
    src.write_text(ASCII_WITH_LOOP, encoding="utf-8")
    r = subprocess.run(
        [sys.executable,
         str(Path(__file__).parent.parent / "scripts" / "flow-to-mermaid.py"),
         "--ascii-strict", "--json", str(src)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert "strict_results" in data
    assert len(data["strict_results"]) == 1
    assert data["strict_results"][0]["passed"] is True