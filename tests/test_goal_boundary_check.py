"""pytest 单元测试 for scripts/goal-boundary-check.py

覆盖：
- TASK_CONFIRM §二 / §三 完整性
- PRD §七 验收映射
- TC §三 阶段 + AC 关联
- HANDOVER §二 已达成 / 延后 / 差距
- --self-test 退出码
"""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
SCRIPT = ROOT / "scripts" / "goal-boundary-check.py"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ============ 基础 fixture ============

TASK_CONFIRM_OK = (
    "## 二、需求目标与完成边界\n\n"
    "| 问题 | 你的回答 |\n|---|---|\n"
    "| 最终业务目标是什么？ | 提升收货效率 |\n"
    "| 本次交付做到什么程度才算完成？ | 关键场景全自动化 |\n"
    "| 本次明确不解决哪些问题？ | 报表导出 |\n"
    "| 是否允许分阶段交付？ | 是 |\n\n"
    "## 三、阶段目标\n\n"
    "| 阶段 | 目标 | 包含范围 | 不包含范围 | 交付物 | 验收条件 | 是否阻塞上线 |\n"
    "|---|---|---|---|---|---|---|\n"
    "| MVP | 自动收货 | 主流程 | 报表 | BRD+设计 | AC-001 | 是 |\n"
)

PRD_OK = (
    "## 七、验收标准\n\n"
    "| 验收编号 | 关联功能 | 验收条件 | 关联阶段 |\n|---|---|---|---|\n"
    "| AC-001 | 收货 | 自动化 | MVP |\n"
)

TC_OK = (
    "## 三、测试用例\n\n"
    "| 编号 | 场景 | 前置条件 | 操作步骤 | 预期结果 | 优先级 | 关联阶段 | 关联验收条件 |\n"
    "|---|---|---|---|---|---|---|---|\n"
    "| TC-N-001 | 主流程 | init | 1) | ✅ | P0 | MVP | AC-001 |\n"
)

HANDOVER_OK = (
    "## 二、阶段达成与剩余目标\n\n"
    "### 2.1 已达成阶段\n\n"
    "| 阶段 | 状态 | 达成时间 | 主要交付 |\n|---|---|---|---|\n"
    "| MVP / Phase 1 | ✅ | 2026-06-26 | BRD+设计 |\n\n"
    "### 2.2 延后阶段\n\n"
    "| 阶段 | 原因 | 计划时间 |\n|---|---|---|\n| Phase 2 | 待评估 | - |\n\n"
    "### 2.3 最终业务目标差距\n\n"
    "| 最终目标 | 当前达成 | 剩余差距 |\n|---|---|---|\n"
    "| 提升收货效率 | 70% | 报表缺失 |\n"
)


def _build_valid_project(tmp_path: Path) -> Path:
    proj = tmp_path / "p"
    proj.mkdir()
    _write(proj / "TASK_CONFIRM_x.md", TASK_CONFIRM_OK)
    _write(proj / "05-PRD.md", PRD_OK)
    _write(proj / "07-测试用例设计.md", TC_OK)
    _write(proj / "HANDOVER.md", HANDOVER_OK)
    return proj


def _run(proj: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(proj)],
        capture_output=True, text=True,
    )


# ============ pass ============

def test_valid_project_passes(tmp_path):
    proj = _build_valid_project(tmp_path)
    r = _run(proj)
    assert r.returncode == 0, f"stderr={r.stderr}\nstdout={r.stdout}"


# ============ TASK_CONFIRM 错误 ============

def test_missing_task_confirm_fails(tmp_path):
    proj = tmp_path / "p"
    proj.mkdir()
    r = _run(proj)
    assert r.returncode == 1
    assert "TASK_CONFIRM" in r.stdout


def test_missing_completion_field_fails(tmp_path):
    proj = _build_valid_project(tmp_path)
    _write(proj / "TASK_CONFIRM_x.md", TASK_CONFIRM_OK.replace(
        "| 本次交付做到什么程度才算完成？ | 关键场景全自动化 |",
        "| 本次交付做到什么程度才算完成？ | [待填写] |",
    ))
    r = _run(proj)
    assert r.returncode == 1
    assert "做到什么程度" in r.stdout


def test_missing_non_goals_field_fails(tmp_path):
    proj = _build_valid_project(tmp_path)
    _write(proj / "TASK_CONFIRM_x.md", TASK_CONFIRM_OK.replace(
        "| 本次明确不解决哪些问题？ | 报表导出 |",
        "| 本次明确不解决哪些问题？ |  |",
    ))
    r = _run(proj)
    assert r.returncode == 1
    assert "不解决" in r.stdout or "不解决哪些" in r.stdout


def test_staged_yes_but_no_mvp_fails(tmp_path):
    proj = _build_valid_project(tmp_path)
    # §三 改无 MVP 行
    _write(proj / "TASK_CONFIRM_x.md", TASK_CONFIRM_OK.replace(
        "| MVP | 自动收货 | 主流程 | 报表 | BRD+设计 | AC-001 | 是 |",
        "| Phase 2 | y | z | - | - | - | 否 |",
    ))
    r = _run(proj)
    assert r.returncode == 1
    assert "MVP" in r.stdout or "Phase 1" in r.stdout


def test_staged_decision_invalid_value_fails(tmp_path):
    proj = _build_valid_project(tmp_path)
    _write(proj / "TASK_CONFIRM_x.md", TASK_CONFIRM_OK.replace(
        "| 是否允许分阶段交付？ | 是 |",
        "| 是否允许分阶段交付？ | maybe |",
    ))
    r = _run(proj)
    assert r.returncode == 1
    assert "是/否" in r.stdout or "是否允许分阶段" in r.stdout


# ============ PRD 错误 ============

def test_prd_ac_without_phase_fails(tmp_path):
    proj = _build_valid_project(tmp_path)
    _write(proj / "05-PRD.md", PRD_OK.replace(
        "| AC-001 | 收货 | 自动化 | MVP |",
        "| AC-001 | 收货 | 自动化 | (空) |",
    ))
    r = _run(proj)
    assert r.returncode == 1
    assert "AC-001" in r.stdout


def test_prd_p0_not_treated_as_phase(tmp_path):
    """PRD 关联阶段列若是 P0(P 优先级),不应被识别为阶段。"""
    proj = _build_valid_project(tmp_path)
    _write(proj / "05-PRD.md", (
        "## 七、验收标准\n\n"
        "| 验收编号 | 关联功能 | 验收条件 | 关联阶段 |\n|---|---|---|---|\n"
        "| AC-001 | x | x | P0 |\n"
    ))
    r = _run(proj)
    assert r.returncode == 1
    assert "AC-001" in r.stdout


# ============ TC 错误 ============

def test_tc_without_phase_fails(tmp_path):
    """TC 缺 关联阶段 列(且无阶段关键词)应报错。"""
    proj = _build_valid_project(tmp_path)
    _write(proj / "07-测试用例设计.md", (
        "## 三、测试用例\n\n"
        "| 编号 | 场景 | 前置条件 | 操作步骤 | 预期结果 | 优先级 |\n"
        "|---|---|---|---|---|---|\n"
        "| TC-N-001 | 主流程 | init | 1) | ✅ | P0 |\n"
    ))
    r = _run(proj)
    assert r.returncode == 1
    assert "TC-N-001" in r.stdout


def test_tc_p0_not_treated_as_phase(tmp_path):
    """TC 优先级列 P0 不应被识别为阶段。"""
    proj = _build_valid_project(tmp_path)
    _write(proj / "07-测试用例设计.md", (
        "## 三、测试用例\n\n"
        "| 编号 | 场景 | 前置条件 | 操作步骤 | 预期结果 | 优先级 | 关联阶段 | 关联验收条件 |\n"
        "|---|---|---|---|---|---|---|---|\n"
        "| TC-N-001 | 主流程 | init | 1) | ✅ | P0 | (空) | (空) |\n"
    ))
    r = _run(proj)
    assert r.returncode == 1
    assert "TC-N-001" in r.stdout


def test_tc_with_mvp_passes_phase_check(tmp_path):
    """TC 关联阶段=MVP 应通过阶段检查(AC 缺失仅 warning)。"""
    proj = _build_valid_project(tmp_path)
    _write(proj / "07-测试用例设计.md", (
        "## 三、测试用例\n\n"
        "| 编号 | 场景 | 前置条件 | 操作步骤 | 预期结果 | 优先级 | 关联阶段 | 关联验收条件 |\n"
        "|---|---|---|---|---|---|---|---|\n"
        "| TC-N-001 | 主流程 | init | 1) | ✅ | P0 | MVP | (空) |\n"
    ))
    r = _run(proj)
    assert r.returncode == 0, f"stdout={r.stdout}\nstderr={r.stderr}"


# ============ HANDOVER 错误 ============

def test_handover_missing_achieved_warns(tmp_path):
    proj = _build_valid_project(tmp_path)
    # 已达成阶段表存在,但 状态 列都未填,触发"无 ✅ 行"警告
    _write(proj / "HANDOVER.md", (
        "## 二、阶段达成与剩余目标\n\n"
        "### 2.1 已达成阶段\n\n"
        "| 阶段 | 状态 | 达成时间 | 主要交付 |\n|---|---|---|---|\n"
        "| MVP / Phase 1 |  |  |  |\n"
    ))
    r = _run(proj)
    # HANDOVER 问题是 warning,rc 仍为 0
    assert r.returncode == 0
    assert "无" in r.stdout and "达成" in r.stdout


# ============ self-test ============

def test_self_test_passes():
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--self-test"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"stderr={r.stderr}\nstdout={r.stdout}"
    assert "PASS" in r.stdout
