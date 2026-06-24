"""pytest 单元测试 for scripts/task-confirm-check.py

覆盖 5 项 Check 的 12 个核心场景 + 边界情况。
"""

import importlib.util
import sys
from pathlib import Path

import pytest


def _load_module():
    """动态加载 scripts/task-confirm-check.py（避免 sys.path 冲突）。"""
    script = Path(__file__).parent.parent / "scripts" / "task-confirm-check.py"
    spec = importlib.util.spec_from_file_location("task_confirm_check", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_mod = _load_module()
check_status = _mod.check_status
check_tbd_keywords = _mod.check_tbd_keywords
check_sections = _mod.check_sections
check_review_pending_section = _mod.check_review_pending_section
check_field_alignment_counts = _mod.check_field_alignment_counts
TBD_KEYWORDS = _mod.TBD_KEYWORDS


# ===== Check 1: 状态字段 =====

def test_check_status_pass():
    text = "> 状态：✅ 已确认"
    assert check_status(text, "T") == []


def test_check_status_pending():
    text = "> 状态：⬜ 待填写"
    errors = check_status(text, "T")
    assert len(errors) == 1
    assert "⬜" in errors[0]


def test_check_status_yellow_legacy():
    """Bug #1 修复回归测试：🟡 必须被识别为废弃。"""
    text = "> 状态：🟡 部分填写"
    errors = check_status(text, "T")
    assert len(errors) == 1
    assert "🟡" in errors[0]


def test_check_status_missing():
    text = "# 没有状态字段"
    errors = check_status(text, "T")
    assert len(errors) == 1
    assert "找不到" in errors[0]


# ===== Check 2: TBD 关键词 =====

def test_check_tbd_clean():
    text = "# 干净的文档\n> 状态：✅ 已确认"
    assert check_tbd_keywords(text, "T") == []


def test_check_tbd_all_keywords():
    """12 词中每个都被扫描到。"""
    for keyword in TBD_KEYWORDS:
        text = f"# 测试\n含有关键词 {keyword}"
        errors = check_tbd_keywords(text, "T")
        assert len(errors) >= 1, f"关键词 '{keyword}' 未被扫描到"
        assert keyword in errors[0]


def test_check_tbd_word_boundary():
    """Bug #2 修复回归测试：ID_TODO_FIELD 不应被误报。"""
    text = "字段 ID_TODO_FIELD 不应触发"
    errors = check_tbd_keywords(text, "T")
    # TODO 在 ID_TODO_FIELD 里，整词匹配 \bTODO\b 不应命中
    assert len(errors) == 0


# ===== Check 3: 5 章节 =====

def test_check_sections_complete():
    text = "## 一、x\n## 二、x\n## 三、x\n## 四、x\n## 五、x"
    assert check_sections(text, "T") == []


def test_check_sections_missing_one():
    text = "## 一、x\n## 二、x\n## 三、x\n## 四、x\n## 六、x"
    errors = check_sections(text, "T")
    assert len(errors) == 1
    assert "4/5" in errors[0]
    assert "五、" in errors[0]


# ===== Check 4: REVIEW 第八节 =====

def test_check_review_pending_empty():
    text = "## 八、待明确事项\n| 编号 | 待明确事项 |\n|------|----------|"
    assert check_review_pending_section(text, "T") == []


def test_check_review_pending_has_t01():
    text = "## 八、待明确事项\n| T-01 | 待补充 |"
    errors = check_review_pending_section(text, "T")
    assert len(errors) == 1
    assert "T-01" in errors[0]


# ===== Check 5: 字段对齐 🔴/❓ 计数 =====

def test_check_field_alignment_clean():
    text = "| ❓ 待确认 | 0 |\n| 🔴 缺失 | 0 |"
    assert check_field_alignment_counts(text, "T") == []


def test_check_field_alignment_red():
    """Bug #3 修复回归测试：🔴=2 必须被识别。"""
    text = "| ❓ 待确认 | 0 |\n| 🔴 缺失 | 2 |"
    errors = check_field_alignment_counts(text, "T")
    assert len(errors) == 1
    assert "🔴" in errors[0]
    assert "2" in errors[0]


def test_check_field_alignment_q():
    text = "| ❓ 待确认 | 1 |\n| 🔴 缺失 | 0 |"
    errors = check_field_alignment_counts(text, "T")
    assert len(errors) == 1
    assert "❓" in errors[0]


def test_check_field_alignment_no_table():
    text = "# 没有对齐结论表"
    errors = check_field_alignment_counts(text, "T")
    assert len(errors) == 1
    assert "找不到" in errors[0] or "🔴" in errors[0]


# ===== CLI 集成测试 =====

def test_cli_self_test():
    """CLI --self-test 必须 exit 0。"""
    import subprocess
    result = subprocess.run(
        ["python3", "scripts/task-confirm-check.py", "--self-test"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )
    assert result.returncode == 0


def test_cli_example_pass(tmp_path):
    """真实 example 应通过 task-confirm-check.py。"""
    import subprocess
    rc = tmp_path / "rc.md"
    rf = tmp_path / "rf.md"
    rc.write_text("## 八、待明确事项\n| 编号 | 待明确事项 |\n|------|----------|", encoding="utf-8")
    rf.write_text("| ❓ 待确认 | 0 |\n| 🔴 缺失 | 0 |", encoding="utf-8")
    result = subprocess.run(
        [
            "python3",
            "scripts/task-confirm-check.py",
            "examples/01-wms-warehouse/TASK_CONFIRM_收货管理.md",
            str(rc),
            str(rf),
        ],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )
    assert result.returncode == 0, f"expected pass, got: {result.stdout}\n{result.stderr}"
    assert "✅ Check 1" in result.stdout


def test_cli_template_rejected(tmp_path):
    """模板本身应被 Check 1 拒绝。"""
    import subprocess
    rc = tmp_path / "rc.md"
    rf = tmp_path / "rf.md"
    rc.write_text("## 八、待明确事项\n| 编号 | 待明确事项 |\n|------|----------|", encoding="utf-8")
    rf.write_text("| ❓ 待确认 | 0 |\n| 🔴 缺失 | 0 |", encoding="utf-8")
    result = subprocess.run(
        [
            "python3",
            "scripts/task-confirm-check.py",
            "templates/TASK_CONFIRM.md",
            str(rc),
            str(rf),
        ],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )
    assert result.returncode == 1, f"expected fail, got: {result.stdout}"