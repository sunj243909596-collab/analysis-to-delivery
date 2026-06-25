"""pytest 单元测试 for scripts/analysis-state.py(plan §P1-3)"""
import importlib.util
import sys
from pathlib import Path


def _load_module():
    script = Path(__file__).parent.parent / "scripts" / "analysis-state.py"
    spec = importlib.util.spec_from_file_location("a_state", script)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


_mod = _load_module()
SIGNOFF_PHRASES = _mod.SIGNOFF_PHRASES
is_valid_signoff = _mod.is_valid_signoff
new_state = _mod.new_state
load_state = _mod.load_state
save_state = _mod.save_state
STAGES = _mod.STAGES


# ===== 白名单校验 =====

def test_signoff_whitelist_all_pass():
    for p in SIGNOFF_PHRASES:
        assert is_valid_signoff(p), f"应 accept: {p}"


def test_signoff_non_whitelist_rejected():
    for bad in ["OK", "好", "继续", "approved", "确认", "go", ""]:
        assert not is_valid_signoff(bad), f"应 reject: {bad!r}"


def test_signoff_whitelist_with_surrounding_space():
    """白名单前后允许空白(防 trailing newline)。"""
    assert is_valid_signoff("  我已全部确认,可以进入下一步\n")


# ===== state 创建 =====

def test_new_state_shape(tmp_path):
    st = new_state("demo", tmp_path)
    assert st["version"] == "1.0.0"
    assert st["project"]["name"] == "demo"
    assert st["current_stage"] == 1
    assert all(str(i) in st["stages"] for i in range(1, 10))
    # 9 个 stage 全部初始为 ⬜
    for i in range(1, 10):
        assert st["stages"][str(i)]["status"] == "⬜"
    # metrics 5 项
    assert "stage_durations_min" in st["metrics"]
    assert "gate_interjections" in st["metrics"]
    assert "retries_per_stage" in st["metrics"]
    assert "total_gates_run" in st["metrics"]
    assert "total_signoffs" in st["metrics"]


# ===== 5 子命令 =====

def test_init_creates_file(tmp_path):
    import subprocess
    r = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "analysis-state.py"),
         "init", "--project", "demo", "--project-root", str(tmp_path)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0
    assert (tmp_path / ".analysis-delivery-state.json").exists()


def test_init_double_fails(tmp_path):
    import subprocess
    subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "analysis-state.py"),
         "init", "--project", "demo", "--project-root", str(tmp_path)],
        capture_output=True, text=True,
    )
    r = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "analysis-state.py"),
         "init", "--project", "demo", "--project-root", str(tmp_path)],
        capture_output=True, text=True,
    )
    assert r.returncode == 1


def test_init_force_overwrites(tmp_path):
    import subprocess
    subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "analysis-state.py"),
         "init", "--project", "first", "--project-root", str(tmp_path)],
        capture_output=True, text=True,
    )
    r = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "analysis-state.py"),
         "init", "--project", "second", "--force", "--project-root", str(tmp_path)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0
    st = load_state(tmp_path)
    assert st["project"]["name"] == "second"


def test_record_gate_pass(tmp_path):
    import subprocess
    subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "analysis-state.py"),
         "init", "--project", "t", "--project-root", str(tmp_path)],
        capture_output=True,
    )
    r = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "analysis-state.py"),
         "record-gate", "--stage", "2", "--script", "task-confirm-check",
         "--result", "pass", "--project-root", str(tmp_path)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0
    st = load_state(tmp_path)
    assert st["stages"]["2"]["last_gate"] == "task-confirm-check"
    assert st["stages"]["2"]["errors"] == 0
    assert st["metrics"]["total_gates_run"] == 1


def test_record_gate_fail_increments_errors(tmp_path):
    import subprocess
    subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "analysis-state.py"),
         "init", "--project", "t", "--project-root", str(tmp_path)],
        capture_output=True,
    )
    subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "analysis-state.py"),
         "record-gate", "--stage", "2", "--script", "task-confirm-check",
         "--result", "fail", "--project-root", str(tmp_path)],
        capture_output=True,
    )
    st = load_state(tmp_path)
    assert st["stages"]["2"]["errors"] == 1
    assert st["stages"]["2"]["retries"] == 1
    assert st["metrics"]["retries_per_stage"]["2"] == 1
    assert st["metrics"]["gate_interjections"]["task-confirm-check"] == 1


def test_signoff_advances_current_stage(tmp_path):
    import subprocess
    subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "analysis-state.py"),
         "init", "--project", "t", "--project-root", str(tmp_path)],
        capture_output=True,
    )
    r = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "analysis-state.py"),
         "signoff", "--stage", "2", "--text", "确认通过",
         "--project-root", str(tmp_path)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0
    st = load_state(tmp_path)
    assert st["stages"]["2"]["status"] == "✅"
    assert st["stages"]["2"]["signoff_text"] == "确认通过"
    assert st["current_stage"] == 3
    assert st["metrics"]["total_signoffs"] == 1


def test_signoff_rejects_non_whitelist(tmp_path):
    import subprocess
    subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "analysis-state.py"),
         "init", "--project", "t", "--project-root", str(tmp_path)],
        capture_output=True,
    )
    r = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "analysis-state.py"),
         "signoff", "--stage", "2", "--text", "OK",
         "--project-root", str(tmp_path)],
        capture_output=True, text=True,
    )
    assert r.returncode == 1
    assert "白名单" in r.stderr


def test_status_command(tmp_path):
    import subprocess
    subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "analysis-state.py"),
         "init", "--project", "demo", "--project-root", str(tmp_path)],
        capture_output=True,
    )
    r = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "analysis-state.py"),
         "status", "--project-root", str(tmp_path)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0
    assert "demo" in r.stdout
    assert "Project" in r.stdout


def test_metrics_command(tmp_path):
    import subprocess
    subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "analysis-state.py"),
         "init", "--project", "t", "--project-root", str(tmp_path)],
        capture_output=True,
    )
    r = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "analysis-state.py"),
         "metrics", "--project-root", str(tmp_path)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0
    assert "Metrics" in r.stdout
    assert "总 gate" in r.stdout


def test_metrics_json(tmp_path):
    import subprocess
    import json
    subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "analysis-state.py"),
         "init", "--project", "t", "--project-root", str(tmp_path)],
        capture_output=True,
    )
    r = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "analysis-state.py"),
         "metrics", "--json", "--project-root", str(tmp_path)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert "total_gates_run" in data


# ===== self-test =====

def test_self_test_runs():
    import subprocess
    r = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "analysis-state.py"),
         "--self-test"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"stderr={r.stderr}\nstdout={r.stdout}"