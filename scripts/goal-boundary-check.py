#!/usr/bin/env python3
"""
goal-boundary-check.py — goal-boundary 目标边界与分期校验（v4.0.0）

> 配合 `rules/goal-boundary.md` 使用。

校验：
1. TASK_CONFIRM_*.md 含目标边界小节（§二 / §三）
2. "本次交付做到什么程度才算完成"非空
3. "可量化成功指标是什么"非空
4. "本次明确不解决哪些问题"非空
5. "是否允许分阶段交付"是 `是` 或 `否`
6. 若分阶段是,§三 至少 1 行(MVP / Phase 1 / Phase 2 / Later),每行有 goal + acceptance
7. PRD §七 验收编号必须映射到一个阶段
8. 测试用例 §三 用例必须关联到阶段 + 验收条件
9. HANDOVER §二 已达成 / 延后 / 剩余差距必须填写

用法：
    python3 scripts/goal-boundary-check.py <project_dir>
    python3 scripts/goal-boundary-check.py --self-test
    python3 scripts/goal-boundary-check.py --loose <project_dir>   # 警告而非 BLOCK

退出码：0 = pass(strict) / 仅 warning(loose);1 = fail;2 = 参数错误
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


# 阶段名关键词(用于"§三 至少 1 行包含阶段名")
# 注意:刻意不含 P0/P1/P2 —— 那是优先级,不是阶段
PHASE_KEYWORDS = (
    "MVP", "Phase 1", "Phase 2", "Phase 3", "Later",
)

# 是否分阶段 字段可接受值
STAGE_DECISION_VALUES = {"是", "否", "yes", "no", "Yes", "No", "YES", "NO"}


@dataclass
class Issue:
    severity: str  # "error" | "warning"
    location: str
    message: str


@dataclass
class GBReport:
    errors: list[Issue] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.errors)


def _is_filled(cell_text: str) -> bool:
    """判断单元格是否实质填写(非占位符/空)。"""
    t = cell_text.strip()
    if not t:
        return False
    if t.startswith("[") and t.endswith("]"):
        return False
    if t in ("-", "—", "N/A", "n/a", "/"):
        return False
    return True


def _split_md_row(line: str) -> list[str]:
    """简单 markdown 表格行拆分(以 | 分列)。"""
    s = line.strip()
    if not s.startswith("|"):
        return []
    return [c.strip() for c in s.strip("|").split("|")]


def _find_all_tables(text: str) -> list[tuple[int, list[str], list[list[str]]]]:
    """返回所有 markdown 表格,每个元素是 (header_line_no, header_cells, data_rows)。"""
    lines = text.splitlines()
    out: list[tuple[int, list[str], list[list[str]]]] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.lstrip().startswith("|"):
            i += 1
            continue
        # 期望下一行是分隔行 |---|---|
        if i + 1 >= len(lines) or not re.match(r"^\|[\s\-:|]+\|?\s*$", lines[i + 1]):
            i += 1
            continue
        header_cells = _split_md_row(line)
        rows: list[list[str]] = []
        j = i + 2
        while j < len(lines) and lines[j].lstrip().startswith("|"):
            cells = _split_md_row(lines[j])
            if cells:
                rows.append(cells)
            j += 1
        out.append((i, header_cells, rows))
        i = j
    return out


def _find_table_after(text: str, header_keywords: tuple[str, ...], start: int = 0) -> list[list[str]] | None:
    """从 text 的 start 开始,找第一个含 header_keywords 的表头,并返回该表的所有数据行。

    保留旧接口以便向后兼容(返回数据行)。
    """
    tables = _find_all_tables(text)
    for header_line, header_cells, rows in tables:
        if header_line < start:
            continue
        header_text = " | ".join(header_cells)
        if all(kw in header_text for kw in header_keywords):
            return rows
    return None


def _find_table_by_data_keyword(
    text: str, data_keyword: str,
) -> list[list[str]] | None:
    """找包含特定 data_keyword 的表(数据行第一列含该关键字),返回其所有数据行。"""
    for _header_line, _header_cells, rows in _find_all_tables(text):
        for row in rows:
            if data_keyword in row[0]:
                return rows
    return None


def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


# ============ TASK_CONFIRM 检查 ============

def check_task_confirm(project_dir: Path) -> list[Issue]:
    """检查 TASK_CONFIRM_*.md 目标边界 + 阶段目标。"""
    issues: list[Issue] = []
    files = sorted(project_dir.glob("TASK_CONFIRM*.md"))
    if not files:
        issues.append(Issue("error", "TASK_CONFIRM*.md",
                            "未找到 TASK_CONFIRM_*.md 文件"))
        return issues

    for fp in files:
        text = _read(fp)
        rel = fp.name

        # §二 需求目标与完成边界 表 —— 通过 data 行里的关键问题定位
        rows = _find_table_by_data_keyword(
            text, "本次交付做到什么程度才算完成",
        )
        if rows is None:
            issues.append(Issue("error", rel,
                                "缺少 §二 需求目标与完成边界 表格(无『做到什么程度才算完成』问题)"))
            continue

        # 表格列映射:问题 | 你的回答
        # 找每个问题对应的"你的回答"列(最后一列)
        answers: dict[str, str] = {}
        for row in rows:
            if len(row) < 2:
                continue
            question = row[0]
            answer = row[-1]
            answers[question] = answer

        # 关键问题
        delivery_completion_q = next(
            (q for q in answers if "做到什么程度才算完成" in q), None,
        )
        if delivery_completion_q is None:
            issues.append(Issue("error", rel,
                                "§二 缺『本次交付做到什么程度才算完成』问题"))
        elif not _is_filled(answers[delivery_completion_q]):
            issues.append(Issue("error", rel,
                                "§二『本次交付做到什么程度才算完成』未填写"))

        success_metric_q = next(
            (q for q in answers if "可量化成功指标" in q), None,
        )
        if success_metric_q is None:
            issues.append(Issue("error", rel,
                                "§二 缺『可量化成功指标是什么』问题"))
        elif not _is_filled(answers[success_metric_q]):
            issues.append(Issue("error", rel,
                                "§二『可量化成功指标是什么』未填写"))

        non_goals_q = next(
            (q for q in answers if "明确不解决" in q), None,
        )
        if non_goals_q is None:
            issues.append(Issue("error", rel,
                                "§二 缺『本次明确不解决哪些问题』问题"))
        elif not _is_filled(answers[non_goals_q]):
            issues.append(Issue("error", rel,
                                "§二『本次明确不解决哪些问题』未填写"))

        staged_q = next(
            (q for q in answers if "是否允许分阶段" in q), None,
        )
        if staged_q is None:
            issues.append(Issue("error", rel,
                                "§二 缺『是否允许分阶段交付』问题"))
        else:
            answer = answers[staged_q].strip()
            if answer not in STAGE_DECISION_VALUES:
                issues.append(Issue("error", rel,
                                    f"§二『是否允许分阶段交付』必须是 是/否,当前={answer!r}"))

        # 若分阶段,§三 必须有 ≥1 个 MVP/Phase 1 行
        if staged_q and answers[staged_q].strip() in {"是", "yes", "Yes", "YES"}:
            stage_rows = _find_table_after(
                text, ("阶段", "目标", "包含范围"),
            )
            if not stage_rows:
                issues.append(Issue("error", rel,
                                    "§三 阶段目标表缺失"))
                continue
            # 找至少 1 个 MVP/Phase 1 行
            has_mvp = False
            for row in stage_rows:
                if len(row) < 6:
                    continue
                phase_cell = row[0]
                if any(kw in phase_cell for kw in ("MVP", "Phase 1")):
                    if not _is_filled(row[1]):  # goal
                        issues.append(Issue("error", rel,
                                            f"§三 阶段『{phase_cell}』缺目标"))
                    elif not _is_filled(row[5]):  # acceptance
                        issues.append(Issue("error", rel,
                                            f"§三 阶段『{phase_cell}』缺验收条件"))
                    else:
                        has_mvp = True
            if not has_mvp:
                issues.append(Issue("error", rel,
                                    "分阶段是但 §三 无 MVP / Phase 1 行"))

    return issues


# ============ PRD 检查 ============

def check_prd(project_dir: Path) -> list[Issue]:
    """检查 PRD §七 验收编号是否映射到阶段。"""
    issues: list[Issue] = []
    files = list(project_dir.glob("05-*.md")) + list(project_dir.glob("*PRD*.md"))
    files = [f for f in files if f.exists()]
    if not files:
        return issues  # PRD 是阶段 6 产物,可能尚未生成;不阻断

    for fp in files:
        text = _read(fp)
        rel = fp.name
        any_ac = False
        for _header_line, header_cells, rows in _find_all_tables(text):
            # 找 关联阶段 列下标
            phase_col = None
            for ci, c in enumerate(header_cells):
                if "关联阶段" in c:
                    phase_col = ci
                    break
            for row in rows:
                if len(row) < 2:
                    continue
                if not re.search(r"\bAC-\d+\b", row[0]):
                    continue
                any_ac = True
                if phase_col is not None and phase_col < len(row):
                    phase_cell = row[phase_col]
                else:
                    # fallback:任意单元格;但必须非 P0/P1/P2 优先级
                    candidates = [c for c in row
                                  if any(kw in c for kw in PHASE_KEYWORDS)
                                  and c.strip() not in {"P0", "P1", "P2"}]
                    phase_cell = candidates[0] if candidates else ""
                if not _is_filled(phase_cell):
                    issues.append(Issue("error", rel,
                                        f"PRD §七 验收行 {row[0]} 未映射到阶段"))
                elif not any(kw in phase_cell for kw in PHASE_KEYWORDS):
                    issues.append(Issue("error", rel,
                                        f"PRD §七 验收行 {row[0]} 阶段值非法: {phase_cell!r}"))
        if not any_ac:
            continue
    return issues


# ============ TEST_CASE 检查 ============

def check_test_cases(project_dir: Path) -> list[Issue]:
    """检查测试用例 §三 是否每条都关联到阶段 + 验收条件。"""
    issues: list[Issue] = []
    files = list(project_dir.glob("07-*.md")) + list(project_dir.glob("*测试用例*.md"))
    files = [f for f in files if f.exists()]
    if not files:
        return issues

    for fp in files:
        text = _read(fp)
        rel = fp.name
        any_tc = False
        for _header_line, header_cells, rows in _find_all_tables(text):
            # 找 关联阶段 / 关联验收条件 列下标
            phase_col = None
            ac_col = None
            for ci, c in enumerate(header_cells):
                if "关联阶段" in c or "阶段" == c.strip():
                    phase_col = ci
                if "关联验收" in c or "关联 AC" in c or "AC" == c.strip():
                    ac_col = ci
            for row in rows:
                if len(row) < 3:
                    continue
                if not re.search(r"\bTC-[A-Z]-\d+\b", row[0]):
                    continue
                any_tc = True
                # 阶段判定:看 关联阶段 列,或(找不到时)任意列含阶段关键词
                phase_ok = False
                if phase_col is not None and phase_col < len(row):
                    phase_ok = _is_filled(row[phase_col]) and any(
                        kw in row[phase_col] for kw in PHASE_KEYWORDS
                    )
                else:
                    phase_ok = any(
                        any(kw in c for kw in PHASE_KEYWORDS) for c in row
                    ) and not any(
                        "P0" == c.strip() or "P1" == c.strip() or "P2" == c.strip()
                        for c in row
                    )
                ac_ok = False
                if ac_col is not None and ac_col < len(row):
                    ac_ok = bool(re.search(r"\bAC-\d+\b", row[ac_col]))
                else:
                    ac_ok = any(re.search(r"\bAC-\d+\b", c) for c in row)
                if not phase_ok:
                    issues.append(Issue("error", rel,
                                        f"用例 {row[0]} 未关联到阶段"))
                if not ac_ok:
                    issues.append(Issue("warning", rel,
                                        f"用例 {row[0]} 未关联到验收条件 AC-*"))
        if not any_tc:
            continue
    return issues


# ============ HANDOVER 检查 ============

def check_handover(project_dir: Path) -> list[Issue]:
    """检查 HANDOVER §二 已达成 / 延后 / 剩余差距。"""
    issues: list[Issue] = []
    fp = project_dir / "HANDOVER.md"
    if not fp.exists():
        return issues  # 没到阶段 9,不阻断
    text = _read(fp)
    rel = fp.name
    # §二.1 已达成阶段 —— 找含 "已达成" 或 "达成时间" 列的表
    achieved = None
    deferred = None
    gap = None
    for _hl, _hc, rows in _find_all_tables(text):
        header_text = " | ".join(_hc)
        if "已达成阶段" in header_text or "达成时间" in header_text:
            achieved = rows
        elif "延后阶段" in header_text or ("原因" in header_text and "计划时间" in header_text):
            deferred = rows
        elif "最终目标" in header_text and "当前达成" in header_text:
            gap = rows
    if achieved is None:
        issues.append(Issue("warning", rel,
                            "HANDOVER §二.1 已达成阶段表缺失"))
    elif not any(_is_filled(r[1]) if len(r) > 1 else False for r in achieved):
        issues.append(Issue("warning", rel,
                            "HANDOVER §二.1 已达成阶段无 ✅ 行"))
    if deferred is None:
        issues.append(Issue("warning", rel,
                            "HANDOVER §二.2 延后阶段表缺失"))
    if gap is None:
        issues.append(Issue("warning", rel,
                            "HANDOVER §二.3 最终业务目标差距表缺失"))
    return issues


# ============ main ============

def check_project(project_dir: Path) -> GBReport:
    rep = GBReport()
    for issue in check_task_confirm(project_dir):
        (rep.errors if issue.severity == "error" else rep.warnings).append(issue)
    for issue in check_prd(project_dir):
        (rep.errors if issue.severity == "error" else rep.warnings).append(issue)
    for issue in check_test_cases(project_dir):
        (rep.errors if issue.severity == "error" else rep.warnings).append(issue)
    for issue in check_handover(project_dir):
        (rep.errors if issue.severity == "error" else rep.warnings).append(issue)
    return rep


def self_test() -> int:
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        proj = Path(tmp) / "p"
        proj.mkdir()

        # 1) 完全无 TASK_CONFIRM → fail
        rep = check_project(proj)
        if not rep.has_errors:
            print("[FAIL] no TASK_CONFIRM should error")
            return 1

        # 2) 写一个 valid TASK_CONFIRM + 简单 PRD + 测试 + HANDOVER
        (proj / "TASK_CONFIRM_x.md").write_text(
            "## 二、需求目标与完成边界\n\n"
            "| 问题 | 你的回答 |\n"
            "|---|---|\n"
            "| 最终业务目标是什么？ | 提升收货效率 |\n"
            "| 本次交付做到什么程度才算完成？ | 关键场景全自动化 |\n"
            "| 可量化成功指标是什么？ | P95 < 3s |\n"
            "| 本次明确不解决哪些问题？ | 报表导出 |\n"
            "| 是否允许分阶段交付？ | 是 |\n\n"
            "## 三、阶段目标\n\n"
            "| 阶段 | 目标 | 包含范围 | 不包含范围 | 交付物 | 验收条件 | 是否阻塞上线 |\n"
            "|---|---|---|---|---|---|---|\n"
            "| MVP | 自动收货 | 主流程 | 报表 | BRD+设计 | AC-001 | 是 |\n",
            encoding="utf-8",
        )
        (proj / "05-PRD.md").write_text(
            "## 七、验收标准\n\n"
            "| 验收编号 | 关联功能 | 验收条件 | 关联阶段 |\n"
            "|---|---|---|---|\n"
            "| AC-001 | 收货 | 自动化 | MVP |\n",
            encoding="utf-8",
        )
        (proj / "07-测试用例设计.md").write_text(
            "## 三、测试用例\n\n"
            "| 编号 | 场景 | 前置条件 | 操作步骤 | 预期结果 | 优先级 | 关联阶段 | 关联验收条件 |\n"
            "|---|---|---|---|---|---|---|---|\n"
            "| TC-N-001 | 主流程 | init | 1)扫码 2)提交 | ✅ | P0 | MVP | AC-001 |\n",
            encoding="utf-8",
        )
        (proj / "HANDOVER.md").write_text(
            "## 二、阶段达成与剩余目标\n\n"
            "### 2.1 已达成阶段\n\n"
            "| 阶段 | 状态 | 达成时间 |\n|---|---|---|\n| MVP | ✅ | 2026-06-26 |\n\n"
            "### 2.2 延后阶段\n\n"
            "| 阶段 | 原因 | 计划时间 |\n|---|---|---|\n| Phase 2 | 待评估 | - |\n\n"
            "### 2.3 最终业务目标差距\n\n"
            "| 最终目标 | 当前达成 | 剩余差距 |\n|---|---|---|\n| 提升收货效率 | 70% | 报表缺失 |\n",
            encoding="utf-8",
        )
        rep = check_project(proj)
        if rep.has_errors:
            print("[FAIL] valid project should pass")
            for issue in rep.errors:
                print(f"  {issue.location}: {issue.message}")
            return 1

        # 3) 缺"做到什么程度"→ fail
        bad = proj / "TASK_CONFIRM_bad.md"
        bad.write_text(
            "## 二、需求目标与完成边界\n\n"
            "| 问题 | 你的回答 |\n|---|---|\n"
            "| 最终业务目标是什么？ | x |\n"
            "| 本次交付做到什么程度才算完成？ | [待填写] |\n"
            "| 可量化成功指标是什么？ | x |\n"
            "| 本次明确不解决哪些问题？ | x |\n"
            "| 是否允许分阶段交付？ | 是 |\n",
            encoding="utf-8",
        )
        rep = check_project(proj)
        if not rep.has_errors:
            print("[FAIL] missing completion should fail")
            return 1

        # 4) 分阶段是但无 MVP → fail
        bad.write_text(
            "## 二、需求目标与完成边界\n\n"
            "| 问题 | 你的回答 |\n|---|---|\n"
            "| 最终业务目标是什么？ | x |\n"
            "| 本次交付做到什么程度才算完成？ | x |\n"
            "| 可量化成功指标是什么？ | x |\n"
            "| 本次明确不解决哪些问题？ | x |\n"
            "| 是否允许分阶段交付？ | 是 |\n\n"
            "## 三、阶段目标\n\n"
            "| 阶段 | 目标 | 包含范围 | 不包含范围 | 交付物 | 验收条件 | 是否阻塞上线 |\n"
            "|---|---|---|---|---|---|---|\n"
            "| Phase 2 | y | z | - | - | - | 否 |\n",
            encoding="utf-8",
        )
        rep = check_project(proj)
        if not rep.has_errors:
            print("[FAIL] staged-but-no-MVP should fail")
            return 1

        # 5) PRD AC 未映射阶段 → fail
        bad.write_text(
            "## 二、需求目标与完成边界\n\n"
            "| 问题 | 你的回答 |\n|---|---|\n"
            "| 最终业务目标是什么？ | x |\n"
            "| 本次交付做到什么程度才算完成？ | x |\n"
            "| 可量化成功指标是什么？ | x |\n"
            "| 本次明确不解决哪些问题？ | x |\n"
            "| 是否允许分阶段交付？ | 否 |\n",
            encoding="utf-8",
        )
        (proj / "05-PRD.md").write_text(
            "## 七、验收标准\n\n"
            "| 验收编号 | 关联功能 | 验收条件 | 关联阶段 |\n"
            "|---|---|---|---|\n"
            "| AC-001 | 收货 | 自动化 | (空) |\n",
            encoding="utf-8",
        )
        rep = check_project(proj)
        if not rep.has_errors:
            print("[FAIL] PRD AC without phase should fail")
            return 1

        # 6) TC 缺阶段 → fail
        (proj / "05-PRD.md").write_text(
            "## 七、验收标准\n\n"
            "| 验收编号 | 关联功能 | 验收条件 | 关联阶段 |\n"
            "|---|---|---|---|\n"
            "| AC-001 | 收货 | 自动化 | MVP |\n",
            encoding="utf-8",
        )
        (proj / "07-测试用例设计.md").write_text(
            "## 三、测试用例\n\n"
            "| 编号 | 场景 | 前置条件 | 操作步骤 | 预期结果 | 优先级 |\n"
            "|---|---|---|---|---|---|\n"
            "| TC-N-001 | 主流程 | init | 1) | ✅ | P0 |\n",
            encoding="utf-8",
        )
        rep = check_project(proj)
        if not rep.has_errors:
            print("[FAIL] TC without phase should fail")
            return 1

    print("[PASS] goal-boundary-check self-test")
    return 0


def _print_report(rep: GBReport) -> None:
    print("=" * 70)
    print("goal-boundary-check 结果")
    print("=" * 70)
    for issue in rep.errors:
        print(f"[ERROR] {issue.location}: {issue.message}")
    for issue in rep.warnings:
        print(f"[WARN]  {issue.location}: {issue.message}")
    print("-" * 70)
    print(f"errors={len(rep.errors)}, warnings={len(rep.warnings)}")


def main() -> int:
    args = sys.argv[1:]
    if "--self-test" in args:
        return self_test()
    project_dir = None
    loose = "--loose" in args
    args = [a for a in args if a not in ("--loose",)]
    if args:
        project_dir = Path(args[0])
    else:
        project_dir = Path(".")
    if not project_dir.is_dir():
        print(f"[ERROR] {project_dir} 不是目录", file=sys.stderr)
        return 2

    rep = check_project(project_dir)
    _print_report(rep)
    if loose:
        return 0 if not rep.has_errors else 0  # loose: 仅 warning
    return 0 if not rep.has_errors else 1


if __name__ == "__main__":
    sys.exit(main())
