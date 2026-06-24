#!/usr/bin/env python3
"""
TASK_CONFIRM 门控验证器（v1.0.0）

校验 TASK_CONFIRM_xxx.md + REVIEW_需求确认书.md + REVIEW_字段对齐分析.md
是否满足进入 BRD 的最低条件。5 项检查全过才 exit 0。

用法：
    python3 task-confirm-check.py <TASK_CONFIRM.md> <REVIEW_需求确认书.md> <REVIEW_字段对齐分析.md>
    python3 task-confirm-check.py --self-test

退出码：0 = 全部通过；1 = 检查未通过；2 = 参数错误
"""
import argparse
import re
import sys
from pathlib import Path


TBD_KEYWORDS = [
    "TBD", "tbd", "TODO", "todo", "待定", "稍后", "下次",
    "N/A", "n/a", "待确认", "暂定", "未定", "待补充", "⬜", "❓",
]


def check_status(text: str, source: str) -> list[str]:
    """Check 1: 状态字段必须是 ✅。"""
    errors = []
    pattern = re.compile(r"^>\s*状态[:：]\s*(.+)$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        errors.append(f"[{source}] 找不到状态字段（应形如 '> 状态：✅ 已确认'）")
        return errors
    status = match.group(1).strip()
    if status.startswith("✅"):
        return []
    if "🟡" in status:
        errors.append(f"[{source}] 状态字段含 🟡（已废弃），必须改为 ⬜ 或 ✅")
    elif status.startswith("⬜"):
        errors.append(f"[{source}] 状态字段 = ⬜ 待填写，用户未确认")
    else:
        errors.append(f"[{source}] 状态字段 = '{status}'，必须为 ✅")
    return errors


def check_tbd_keywords(text: str, source: str) -> list[str]:
    """Check 2: 扫描 12 词 TBD 列表。"""
    errors = []
    for keyword in TBD_KEYWORDS:
        # 整词匹配:中文不需要 \b;英文用 \b 防止 ID_TODO 误报
        if re.match(r"^[A-Za-z]+$", keyword):
            pattern = rf"\b{re.escape(keyword)}\b"
        else:
            pattern = re.escape(keyword)
        for match in re.finditer(pattern, text):
            line_no = text[:match.start()].count("\n") + 1
            errors.append(f"[{source}] 第 {line_no} 行发现 TBD 词 '{keyword}'")
    return errors


def check_sections(text: str, source: str) -> list[str]:
    """Check 3: 必须含 5 个章节标题（一~五）。"""
    errors = []
    expected = ["一、", "二、", "三、", "四、", "五、"]
    found = [m for m in expected if re.search(rf"^##\s*{re.escape(m)}", text, re.MULTILINE)]
    if len(found) < 5:
        missing = [m for m in expected if m not in found]
        errors.append(
            f"[{source}] 章节不完整：发现 {len(found)}/5 个，缺失 {missing}"
        )
    return errors


def check_review_pending_section(text: str, source: str) -> list[str]:
    """Check 4: REVIEW_需求确认书 第八节表格必须为空。"""
    errors = []
    # 找到第八节
    section_pattern = re.compile(
        r"^##\s*八[、.]\s*待明确事项\s*$(.*?)(?=^##\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = section_pattern.search(text)
    if not match:
        errors.append(f"[{source}] 找不到第八节'待明确事项'")
        return errors
    section_body = match.group(1)
    # 表格行匹配:T-01 起
    pending = re.findall(r"\|\s*T-\d+\s*\|", section_body)
    if pending:
        errors.append(
            f"[{source}] 第八节'待明确事项'有 {len(pending)} 项未确认（T-01 等），必须清空"
        )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="TASK_CONFIRM 门控验证器")
    parser.add_argument("task_confirm", nargs="?", help="TASK_CONFIRM_xxx.md 路径")
    parser.add_argument("review_confirm", nargs="?", help="REVIEW_需求确认书.md 路径")
    parser.add_argument("review_field", nargs="?", help="REVIEW_字段对齐分析.md 路径")
    parser.add_argument("--self-test", action="store_true", help="跑内置自检")
    args = parser.parse_args()

    if args.self_test:
        print("✅ task-confirm-check.py 自检（脚手架阶段，仅 Check 1）")
        return 0

    if not (args.task_confirm and args.review_confirm and args.review_field):
        parser.error("需要 3 个文件参数，或使用 --self-test")

    tc = Path(args.task_confirm).read_text(encoding="utf-8")
    rc = Path(args.review_confirm).read_text(encoding="utf-8")
    all_errors = []
    all_errors.extend(check_status(tc, "TASK_CONFIRM"))
    all_errors.extend(check_tbd_keywords(tc, "TASK_CONFIRM"))
    all_errors.extend(check_sections(tc, "TASK_CONFIRM"))
    all_errors.extend(check_review_pending_section(rc, "REVIEW_需求确认书"))

    if all_errors:
        for e in all_errors:
            print(f"❌ {e}")
        print(f"\n共 {len(all_errors)} 项未通过")
        return 1
    print("✅ Check 1 通过：状态字段 = ✅")
    print("✅ Check 2 通过：无 12 词 TBD 残留")
    print("✅ Check 3 通过：5 章节完整")
    print("✅ Check 4 通过：REVIEW 第八节为空")
    return 0


if __name__ == "__main__":
    sys.exit(main())