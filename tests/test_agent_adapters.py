"""Tests for agent-neutral adapter support."""
import os
import subprocess
from pathlib import Path


REPO = Path(__file__).parent.parent
INSTALL = REPO / "install.sh"


def _run_install(tmp_path: Path, *args: str):
    env = os.environ.copy()
    env["HOME"] = str(tmp_path)
    env.pop("CODEX_HOME", None)
    env.pop("OPENCODE_HOME", None)
    return subprocess.run(
        ["bash", str(INSTALL), "--dry-run", *args],
        capture_output=True,
        text=True,
        env=env,
        cwd=REPO,
    )


def test_install_agent_codex_targets_codex_home(tmp_path):
    result = _run_install(tmp_path, "--agent", "codex")
    assert result.returncode == 0, result.stderr
    assert f"{tmp_path}/.codex/skills/analysis-to-delivery" in result.stdout


def test_install_agent_opencode_targets_opencode_home(tmp_path):
    result = _run_install(tmp_path, "--agent", "opencode")
    assert result.returncode == 0, result.stderr
    assert f"{tmp_path}/.opencode/skills/analysis-to-delivery" in result.stdout


def test_adapter_docs_exist_for_codex_and_opencode():
    assert (REPO / "docs" / "adapters" / "codex.md").exists()
    assert (REPO / "docs" / "adapters" / "opencode.md").exists()


def test_vscode_default_points_to_codex_adapter():
    package_json = (REPO / "vscode-extension" / "package.json").read_text(encoding="utf-8")
    assert "${userHome}/.codex/skills/analysis-to-delivery" in package_json
