# grill-task 需求澄清门控加固 — 实施 Plan

> **For Hermes:** Use subagent-driven-development skill to execute this plan task-by-task. 每个 Task 结束后产出 `logs/STEP-N-review.md` 并等待用户签字(B+C 留痕)。

**Goal:** 通过新建 `task-confirm-check.py` 脚本 + 模板硬约束 + SKILL 文本对齐,堵住 grill-task 的 7 个结构性 bug,使"部分确认"状态无法进入 BRD。

**Architecture:**
- 新建独立 Python 门控脚本,扫描 TASK_CONFIRM + REVIEW 文档,5 项检查全过才 exit 0
- TASK_CONFIRM 模板状态字段从三态(⬜/🟡/✅)硬改为二态(⬜/✅)
- 触发话术从弱话术("已填写")改为白名单(4 句)
- SKILL 文档删除不一致引用、补充硬门控文本
- 每 Task 配 STEP-N-review.md 留痕 + 用户签字

**Tech Stack:**
- Python 3.12(与 `field-alignment-check.py` 一致)
- pytest(测试)
- 标准库(re, pathlib, argparse, dataclasses, json, sys)
- 不引入新依赖

**Spec:** `docs/superpowers/specs/2026-06-24-grill-task-bugfix-design.md`

---

## 任务地图

```
P0 块(Task 1-9):核心门控基础设施
├── Task 1:脚本脚手架 + Check 1(状态字段)
├── Task 2:Check 2(12 词 TBD 扫描)
├── Task 3:Check 3(5 章节完整)
├── Task 4:Check 4(REVIEW 第八节)
├── Task 5:Check 5(字段对齐 🔴/❓ 计数)
├── Task 6:修改 templates/TASK_CONFIRM.md
├── Task 7:修改 skills/user-invoked/grill-task/SKILL.md
├── Task 8:修改 skills/disciplines/stage-gate/SKILL.md
└── Task 9:P0 集成验证 + STEP-P0-review.md + 用户签字

P1 块(Task 10-13):模板与 SKILL 文本对齐
├── Task 10:修改 templates/REVIEW_需求确认书.md
├── Task 11:修改 templates/REVIEW_字段对齐分析.md
├── Task 12:更新 scripts/field-alignment-check.py docstring
└── Task 13:P1 集成验证 + STEP-P1-review.md + 用户签字

P2 块(Task 14-18):文档与 CI 同步
├── Task 14:验证 3 个 example 通过 task-confirm-check.py
├── Task 15:创建 .github/workflows/task-confirm-check.yml
├── Task 16:修改 CHANGELOG.md
├── Task 17:修改 README.md
└── Task 18:P2 最终验证 + STEP-P2-review.md + 用户签字
```

**每 Task 强制收尾**(B+C):
1. 跑验证命令,记录输出
2. 写 `logs/STEP-N-review.md`(4 节:改了什么 / 拒绝的方案 / 边界情况 / 用户签字位)
3. git commit
4. **等待用户签字**才能进下一个 Task(用户回 `OK` 或具体修改意见)

---

# P0 块:核心门控基础设施

## Task 1: 创建 task-confirm-check.py 脚手架 + Check 1(状态字段)

**Objective:** 建立脚本骨架,实现第一个检查项(状态字段 == ✅),含 CLI 参数解析。

**Files:**
- Create: `scripts/task-confirm-check.py`

**Step 1: 创建空脚本含 argparse + Check 1 框架**

```python
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
    all_errors = check_status(tc, "TASK_CONFIRM")

    if all_errors:
        for e in all_errors:
            print(f"❌ {e}")
        return 1
    print("✅ Check 1 通过：状态字段 = ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**Step 2: 验证 --self-test 工作**

```bash
cd /root/analysis-to-delivery
python3 scripts/task-confirm-check.py --self-test
```
Expected: `✅ task-confirm-check.py 自检（脚手架阶段，仅 Check 1）`,exit 0

**Step 3: 验证 Check 1 在真实文件上工作(已 ✅ 应通过)**

```bash
python3 scripts/task-confirm-check.py \
    examples/01-wms-warehouse/TASK_CONFIRM_收货管理.md \
    examples/01-wms-warehouse/REVIEW_需求确认书.md \
    examples/01-wms-warehouse/REVIEW_字段对齐分析.md
```
Expected: `✅ Check 1 通过：状态字段 = ✅`,exit 0(注意:REVIEW 文件可能不存在,后续 Task 会创建;此步若因文件不存在报错,临时创建空文件即可)

**Step 4: Commit**

```bash
git add scripts/task-confirm-check.py
git commit -m "feat(scripts): task-confirm-check.py 脚手架 + Check 1 状态字段"
```

**Step 5: 写 STEP-1-review.md**

```bash
mkdir -p logs
```

创建 `logs/STEP-1-review.md`:
```markdown
# STEP 1 Review — 脚本脚手架 + Check 1

> 日期：2026-06-24
> 关联 task：Task 1

## 1. 本次改了什么
- 新建 `scripts/task-confirm-check.py`(~70 行):argparse + Check 1(状态字段 == ✅)

## 2. 拒绝的方案
- 方案 A：用 `field-alignment-check.py` 加分支处理 TASK_CONFIRM
  - 拒绝理由：违反"新脚本独立"原则，且 field-alignment-check.py 的 docstring 已声明只校验 PRD/FSD

## 3. 边界情况考虑
- 边界 A：状态字段格式多样化（`:` vs `：`，有无空格）→ 用正则 `r"^>\s*状态[:：]\s*(.+)$"` 兼容
- 边界 B：状态字段含 emoji 组合（`✅ 已确认`）→ 仅检查首字符为 ✅

## 4. 用户签字位
用户：⬜ 已审 / 日期：____
```

**Step 6: Commit review**

```bash
git add logs/STEP-1-review.md
git commit -m "docs(review): STEP-1 review for task-confirm-check.py scaffold"
```

**🛑 HARD GATE**:等待用户回 `OK` 才能进 Task 2。

---

## Task 2: Check 2(12 词 TBD 扫描)

**Objective:** 实现第二个检查项——扫描 12 词 TBD/TODO/待定 等未完成标记。

**Files:**
- Modify: `scripts/task-confirm-check.py`(新增 `check_tbd_keywords` 函数,在 `main()` 中调用)

**Step 1: 实现 Check 2**

在 `check_status` 函数后插入新函数:

```python
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
```

在 `main()` 中调用(替换原 `all_errors = check_status(tc, "TASK_CONFIRM")`):

```python
all_errors = []
all_errors.extend(check_status(tc, "TASK_CONFIRM"))
all_errors.extend(check_tbd_keywords(tc, "TASK_CONFIRM"))
```

修改输出逻辑:

```python
    if all_errors:
        for e in all_errors:
            print(f"❌ {e}")
        print(f"\n共 {len(all_errors)} 项未通过")
        return 1
    print("✅ Check 1 通过：状态字段 = ✅")
    print("✅ Check 2 通过：无 12 词 TBD 残留")
    return 0
```

**Step 2: 验证 TBD 词能命中**

创建临时测试文件 `/tmp/test_tbd.md`:
```markdown
# 测试
> 状态：✅ 已确认
这里有 TODO
这里有 待定
这里有 ⬜
```

跑:
```bash
python3 scripts/task-confirm-check.py \
    /tmp/test_tbd.md \
    /tmp/dummy_review1.md \
    /tmp/dummy_review2.md
```
Expected: 报错列出 3 处 TBD,exit 1

**Step 3: 验证 clean 文件通过**

```bash
python3 scripts/task-confirm-check.py \
    examples/01-wms-warehouse/TASK_CONFIRM_收货管理.md \
    /tmp/dummy_review1.md \
    /tmp/dummy_review2.md
```
Expected: `✅ Check 1 通过` + `✅ Check 2 通过`,exit 0

**Step 4: 清理 + Commit**

```bash
rm -f /tmp/test_tbd.md /tmp/dummy_review1.md /tmp/dummy_review2.md
git add scripts/task-confirm-check.py
git commit -m "feat(scripts): Check 2 - 12 词 TBD 扫描"
```

**Step 5: 写 STEP-2-review.md**

```markdown
# STEP 2 Review — Check 2 TBD 扫描

> 日期：2026-06-24

## 1. 本次改了什么
- `scripts/task-confirm-check.py`:新增 `check_tbd_keywords()`(~15 行)

## 2. 拒绝的方案
- 方案 A：用 `str.contains()` 简单子串匹配
  - 拒绝理由：会把 `ID_TODO_FIELD` 这类合法标识符误报。已用整词匹配 + 中英文区分处理

## 3. 边界情况考虑
- 边界 A：英文 TBD 可能出现在代码块（SQL 注释 `-- TODO`）→ 当前规则不区分代码块，下版本（P3）可加代码块豁免
- 边界 B：用户故意写"TBD 流程"作为标题名词 → 12 词列表不含"流程"等独立名词，规避大部分误报

## 4. 用户签字位
用户：⬜ 已审 / 日期：____
```

```bash
git add logs/STEP-2-review.md
git commit -m "docs(review): STEP-2 review for Check 2 TBD scan"
```

**🛑 HARD GATE**:等用户签字。

---

## Task 3: Check 3(5 章节完整)

**Objective:** 验证 TASK_CONFIRM 含 5 个必备章节标题(一~五)。

**Files:**
- Modify: `scripts/task-confirm-check.py`

**Step 1: 实现 Check 3**

新增函数:

```python
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
```

在 `main()` 中追加调用:

```python
all_errors.extend(check_sections(tc, "TASK_CONFIRM"))
```

输出同步加:
```python
print("✅ Check 3 通过：5 章节完整")
```

**Step 2: 验证 5 章节检测**

临时创建 `/tmp/test_missing_section.md`,只含 4 个章节:
```markdown
# 测试
> 状态：✅ 已确认

## 一、需求背景
## 二、需求目标
## 三、功能范围
## 四、GSP 合规要求
## 六、特殊要求（跳过五）
```

跑:
```bash
python3 scripts/task-confirm-check.py /tmp/test_missing_section.md \
    /tmp/r1.md /tmp/r2.md
```
Expected: `章节不完整：发现 4/5 个，缺失 ['五、']`,exit 1

**Step 3: 验证 example 通过**

```bash
python3 scripts/task-confirm-check.py \
    examples/01-wms-warehouse/TASK_CONFIRM_收货管理.md \
    /tmp/r1.md /tmp/r2.md
```
Expected: 3 项 Check 全过,exit 0

**Step 4: 清理 + Commit**

```bash
rm -f /tmp/test_missing_section.md /tmp/r1.md /tmp/r2.md
git add scripts/task-confirm-check.py
git commit -m "feat(scripts): Check 3 - 5 章节完整"
```

**Step 5: STEP-3-review.md**

```markdown
# STEP 3 Review — Check 3 章节

## 1. 本次改了什么
- `task-confirm-check.py`:新增 `check_sections()`(~10 行)

## 2. 拒绝的方案
- 方案 A：用模糊匹配（如 `re.search("五", text)`）
  - 拒绝理由：会把"十五"、"五项"等误识别。已用 `^##\s*五、` 锚定章节标题

## 3. 边界情况考虑
- 边界 A：用户改章节编号为阿拉伯数字（`## 1.`）→ 当前不兼容。P3 可加配置化章节前缀
- 边界 B：章节顺序乱（一→三→二）→ 当前不校验顺序,P3 可加

## 4. 用户签字位
用户：⬜ 已审 / 日期：____
```

```bash
git add logs/STEP-3-review.md
git commit -m "docs(review): STEP-3 review for Check 3 sections"
```

**🛑 HARD GATE**

---

## Task 4: Check 4(REVIEW 第八节为空)

**Objective:** 验证 REVIEW_需求确认书 第八节"待明确事项"表格为空。

**Files:**
- Modify: `scripts/task-confirm-check.py`

**Step 1: 实现 Check 4**

新增函数:

```python
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
```

`main()` 改为接收 REVIEW_需求确认书 内容:

```python
rc = Path(args.review_confirm).read_text(encoding="utf-8")
all_errors.extend(check_review_pending_section(rc, "REVIEW_需求确认书"))
```

输出:
```python
print("✅ Check 4 通过：REVIEW 第八节为空")
```

**Step 2: 验证**

创建临时 `/tmp/test_review_pending.md`:
```markdown
# REVIEW 测试

## 八、待明确事项

| 编号 | 待明确事项 | 责任方 | 截止 |
|------|----------|------|------|
| T-01 | 待补充 | Claude | 今日 |
```

创建临时 TASK_CONFIRM `/tmp/test_pass_all.md`(全过):
```markdown
> 状态：✅ 已确认
## 一、需求背景
## 二、需求目标
## 三、功能范围
## 四、合规要求
## 五、特殊要求
```

跑:
```bash
python3 scripts/task-confirm-check.py /tmp/test_pass_all.md \
    /tmp/test_review_pending.md /tmp/test_review_field.md
```
Expected: `❌ [REVIEW_需求确认书] 第八节'待明确事项'有 1 项未确认`,exit 1

**Step 3: 验证空第八节通过**

创建 `/tmp/test_review_empty.md`(第八节空):
```markdown
# REVIEW 测试
## 八、待明确事项

| 编号 | 待明确事项 | 责任方 | 截止 |
|------|----------|------|------|
```

跑(替换文件):
```bash
python3 scripts/task-confirm-check.py /tmp/test_pass_all.md \
    /tmp/test_review_empty.md /tmp/test_review_field.md
```
Expected: Check 4 通过(若 Check 5 还没实现,会有文件不存在错误,先创建空文件)

**Step 4: Commit + Review**

```bash
rm -f /tmp/test_*.md
git add scripts/task-confirm-check.py
git commit -m "feat(scripts): Check 4 - REVIEW 第八节为空"
```

STEP-4-review.md 内容:
```markdown
# STEP 4 Review — Check 4

## 1. 本次改了什么
- `task-confirm-check.py`:新增 `check_review_pending_section()`(~15 行)

## 2. 拒绝的方案
- 方案 A：检查第八节有任意非空文本 → 太严格（可能有标题、说明文字）
  - 拒绝理由：用 T-XX 编号精确匹配待确认条目

## 3. 边界情况考虑
- 边界 A：第八节不存在 → 当前报错（应 BLOCK）；用户若写"待明确事项"在第七节，误判
- 边界 B：T-XX 编号含中文（"T-零一"） → 当前仅匹配 `T-\d+`

## 4. 用户签字位
用户：⬜ 已审 / 日期：____
```

```bash
git add logs/STEP-4-review.md
git commit -m "docs(review): STEP-4 review for Check 4"
```

**🛑 HARD GATE**

---

## Task 5: Check 5(字段对齐 🔴/❓ 计数)

**Objective:** 解析 REVIEW_字段对齐分析 的对齐结论表,验证 🔴=0 且 ❓=0。

**Files:**
- Modify: `scripts/task-confirm-check.py`

**Step 1: 实现 Check 5**

新增函数:

```python
def check_field_alignment_counts(text: str, source: str) -> list[str]:
    """Check 5: 对齐结论表中 🔴=0 且 ❓=0。"""
    errors = []
    # 找对齐结论表
    table_pattern = re.compile(
        r"\|.*?🔴.*?\|\s*\n\|.*?---\|",
        re.MULTILINE,
    )
    if not table_pattern.search(text):
        errors.append(f"[{source}] 找不到对齐结论表（含 🔴 行）")
        return errors
    # 解析 ❓ 和 🔴 计数行
    for marker, label in [("❓", "❓ 待确认"), ("🔴", "🔴 缺失")]:
        row_pattern = re.compile(
            rf"\|\s*{re.escape(marker)}\s*{re.escape(label)}\s*\|\s*(\d+)\s*\|",
        )
        match = row_pattern.search(text)
        if match:
            count = int(match.group(1))
            if count > 0:
                errors.append(
                    f"[{source}] 对齐结论表 {label} = {count}（必须为 0）"
                )
    return errors
```

`main()` 追加:
```python
rf = Path(args.review_field).read_text(encoding="utf-8")
all_errors.extend(check_field_alignment_counts(rf, "REVIEW_字段对齐分析"))
```

输出:
```python
print("✅ Check 5 通过：字段对齐 🔴=0, ❓=0")
```

**Step 2: 验证**

创建 `/tmp/test_field_align.md`(🔴=2):
```markdown
# REVIEW 测试

## 对齐结论

| 类别 | 数量 |
|---|---|
| ✅ 已对齐 | 5 |
| ⚠️ 需 JOIN | 1 |
| ❓ 待确认 | 0 |
| 🔴 缺失 | 2 |
```

跑(用之前创建的 test_pass_all.md + test_review_empty.md):
```bash
python3 scripts/task-confirm-check.py /tmp/test_pass_all.md \
    /tmp/test_review_empty.md /tmp/test_field_align.md
```
Expected: `❌ [REVIEW_字段对齐分析] 对齐结论表 🔴 缺失 = 2（必须为 0）`,exit 1

修改 test_field_align.md 为 `🔴 缺失 | 0`,再跑:
Expected: 全部 Check 通过,exit 0

**Step 3: Commit + Review**

```bash
rm -f /tmp/test_*.md
git add scripts/task-confirm-check.py
git commit -m "feat(scripts): Check 5 - 字段对齐计数"
```

STEP-5-review.md:
```markdown
# STEP 5 Review — Check 5

## 1. 本次改了什么
- `task-confirm-check.py`:新增 `check_field_alignment_counts()`(~20 行)

## 2. 拒绝的方案
- 方案 A：检查 header 状态字段 == ✅
  - 拒绝理由：header 是 4 态可视化（✅/⚠️/❓/🔴），BLOCK 应基于计数而非 header 字符串。⚠️ 需 JOIN 合法，不应 BLOCK

## 3. 边界情况考虑
- 边界 A：表格顺序倒置（🔴 行在 ❓ 行之前）→ 当前逐行查找，不依赖顺序
- 边界 B：❓/🔴 计数为空（无数字）→ 当前跳过该行不报错；可能漏判，P3 改进

## 4. 用户签字位
用户：⬜ 已审 / 日期：____
```

```bash
git add logs/STEP-5-review.md
git commit -m "docs(review): STEP-5 review for Check 5"
```

**🛑 HARD GATE**

---

## Task 6: 修改 templates/TASK_CONFIRM.md

**Objective:** 删除 🟡 状态、改触发话术为白名单、加 12 词 TBD 注释行。

**Files:**
- Modify: `templates/TASK_CONFIRM.md`

**Step 1: 编辑 L4(状态字段)**

**改前**:
```
> 状态：⬜ 待填写 / 🟡 部分填写 / ✅ 已确认
```

**改后**:
```
> 状态：⬜ 待填写 / ✅ 已确认（仅二态）
> 词表红线：本文件若出现以下任何词（TBD / TODO / 待定 / 稍后 / 下次 / N/A / 待确认 / 暂定 / 未定 / 待补充 / ⬜ / ❓）将无法进入下一阶段，请先全部解决。
```

**Step 2: 编辑 L47(触发话术)**

**改前**:
```
**用户填写后操作**：将本文档保存并告知 Claude "已填写"，Claude 将读取并生成 `REVIEW_需求确认书.md`。
```

**改后**:
```
**用户填写后操作**：
1. 将本文档保存
2. 将状态字段改为 `✅ 已确认`
3. **必须**用以下白名单话术之一告知 Claude（仅说"已填写"不算签字）：
   - `我已全部确认，可以进入下一步`
   - `确认通过，进入 BRD`
   - `全部完成，继续`
   - `approved, proceed to next stage`
4. Claude 将自动跑 `scripts/task-confirm-check.py` 校验，5 项检查全过才生成后续文档
```

**Step 3: 验证脚本不报错(用本模板本身)**

模板现在状态 = ⬜,应该被 Check 1 拒绝:

```bash
python3 scripts/task-confirm-check.py templates/TASK_CONFIRM.md \
    templates/REVIEW_需求确认书.md templates/REVIEW_字段对齐分析.md
```
Expected: `❌ [TASK_CONFIRM] 状态字段 = ⬜ 待填写`,exit 1(说明 Check 1 仍正常工作)

**Step 4: Commit + Review**

```bash
git add templates/TASK_CONFIRM.md
git commit -m "feat(templates): TASK_CONFIRM 硬约束 - 删 🟡、白名单话术、12 词红线"
```

STEP-6-review.md:
```markdown
# STEP 6 Review — 模板硬约束

## 1. 本次改了什么
- `templates/TASK_CONFIRM.md` L4:状态二态 + 12 词红线注释
- `templates/TASK_CONFIRM.md` L47:触发话术白名单 4 句

## 2. 拒绝的方案
- 方案 A：保留 🟡 但标为 BLOCK 状态
  - 拒绝理由：用户已选硬删除,语义最清晰,无歧义

## 3. 边界情况考虑
- 边界 A：老用户有 🟡 残留文档 → CHANGELOG 需说明(v3.x breaking)
- 边界 B：用户用近义表达("好了"/"可以了")→ 白名单 4 句足够覆盖;若不够 P3 扩展

## 4. 用户签字位
用户：⬜ 已审 / 日期：____
```

```bash
git add logs/STEP-6-review.md
git commit -m "docs(review): STEP-6 review for TASK_CONFIRM template"
```

**🛑 HARD GATE**

---

## Task 7: 修改 skills/user-invoked/grill-task/SKILL.md

**Objective:** 加 hard gate 文本、改 4→5 章节、删 field-alignment-check.py 引用。

**Files:**
- Modify: `skills/user-invoked/grill-task/SKILL.md`

**Step 1: 编辑结束条件(L55-60)**

**改前**:
```
## 结束条件

- [ ] TASK_CONFIRM 4 个必备章节填完
- [ ] REVIEW_需求确认书已签字
- [ ] REVIEW_字段对齐分析无 🔴 缺失项
- [ ] `field-alignment-check.py` 通过
```

**改后**:
```
## 结束条件

- [ ] TASK_CONFIRM 状态字段 = ✅ 已确认（二态，无 🟡）
- [ ] TASK_CONFIRM 5 个必备章节（一~五）填完
- [ ] TASK_CONFIRM 无 12 词 TBD（见 `scripts/task-confirm-check.py` TBD_KEYWORDS）
- [ ] REVIEW_需求确认书 第八节"待明确事项"为空
- [ ] REVIEW_字段对齐分析 对齐结论表中 ❓=0 且 🔴=0（⚠️ 可保留，状态字段可为 ✅ 或 ⚠️）
- [ ] `scripts/task-confirm-check.py` exit 0
- [ ] 用户白名单话术签字（详见 `templates/TASK_CONFIRM.md` L47）
- [ ] ~~`field-alignment-check.py` 通过~~（已废弃此引用；该脚本不接 TASK_CONFIRM，仅校验 PRD/FSD 字段引用）
```

**Step 2: 在"关键纪律"段后新增 2026-06-24 更新段**

在 L42(关键纪律段)后插入:

```
## 关键纪律（2026-06-24 更新）

- ❌ 删除"4 章节"表述——实际为 5 章节（一~五）
- ❌ 删除 `field-alignment-check.py` 作为门控脚本的引用——该脚本只校验 PRD/FSD 字段引用，不接 TASK_CONFIRM
- ✅ 新增 `scripts/task-confirm-check.py` 作为唯一门控脚本
- 🟡 删除：状态字段不再有 🟡 中间态，仅 ⬜/✅ 二态
- 🔒 HARD GATE：用户必须用白名单话术之一明确签字，LLM 不接受隐式同意
```

**Step 3: Commit + Review**

```bash
git add skills/user-invoked/grill-task/SKILL.md
git commit -m "feat(skills): grill-task hard gate 文本 + 4→5 章节 + 删废弃引用"
```

STEP-7-review.md:
```markdown
# STEP 7 Review — grill-task SKILL

## 1. 本次改了什么
- `grill-task/SKILL.md` 结束条件:7 条新硬门控 + 1 条废弃引用说明
- `grill-task/SKILL.md` 新增"2026-06-24 更新"段

## 2. 拒绝的方案
- 方案 A：保留"4 章节"措辞但补注"实际 5"
  - 拒绝理由：直接改为 5 更清晰；用户已选硬删除风格

## 3. 边界情况考虑
- 边界 A：用户文档不引用 scripts/task-confirm-check.py → SKILL 文本显式说明路径
- 边界 B：废弃引用用 strikethrough 保留原文 → 便于回溯；不影响 grep

## 4. 用户签字位
用户：⬜ 已审 / 日期：____
```

```bash
git add logs/STEP-7-review.md
git commit -m "docs(review): STEP-7 review for grill-task SKILL"
```

**🛑 HARD GATE**

---

## Task 8: 修改 skills/disciplines/stage-gate/SKILL.md

**Objective:** 把 2→3 门控行拆为 3 条独立门控标准。

**Files:**
- Modify: `skills/disciplines/stage-gate/SKILL.md`

**Step 1: 编辑 L27 门控表行**

**改前**:
```
| 2→3(澄清→BRD) | TASK_CONFIRM + REVIEW 已签字 | 用户 |
```

**改后**:
```
| 2→3(澄清→BRD) | ① TASK_CONFIRM 状态=✅ ② ❓/🔴 清零 ③ 用户白名单话术签字 | 用户 |
```

**Step 2: 在 HARD GATE 行后新增规则段**

在 L35(`HARD GATE`)后插入:

```
**2→3 门控附加规则（2026-06-24 更新）**：

- 上述 3 条独立门，任一未满足禁止进入 BRD
- 白名单话术：`我已全部确认，可以进入下一步` / `确认通过，进入 BRD` / `全部完成，继续` / `approved, proceed to next stage`
- LLM 不得自行解释"OK"/"好"/"继续"等模糊回复为签字
```

**Step 3: Commit + Review**

```bash
git add skills/disciplines/stage-gate/SKILL.md
git commit -m "feat(skills): stage-gate 2→3 门控拆 3 条独立门"
```

STEP-8-review.md:
```markdown
# STEP 8 Review — stage-gate

## 1. 本次改了什么
- `stage-gate/SKILL.md` L27:门控行细化
- `stage-gate/SKILL.md` L35+:附加规则段

## 2. 拒绝的方案
- 方案 A：保留"TASK_CONFIRM + REVIEW 已签字"模糊措辞
  - 拒绝理由：原措辞对 LLM 解读过于开放；用户已选硬删除风格

## 3. 边界情况考虑
- 边界 A：HARD GATE 段被 markdown 折叠不可见 → 独立段，不依赖表格

## 4. 用户签字位
用户：⬜ 已审 / 日期：____
```

```bash
git add logs/STEP-8-review.md
git commit -m "docs(review): STEP-8 review for stage-gate"
```

**🛑 HARD GATE**

---

## Task 9: P0 集成验证 + STEP-P0-review.md + 用户签字

**Objective:** 验证 P0 全部 6 个 Task 协同工作,产出 P0 整体 review。

**Step 1: 跑完整脚本在真实 example 上**

example `examples/01-wms-warehouse/TASK_CONFIRM_收货管理.md` 状态 = ✅,应通过 Check 1/2/3。Check 4/5 需要临时假 REVIEW 文件:

```bash
# 创建 dummy REVIEW 文件
cat > /tmp/dummy_review_confirm.md << 'EOF'
# REVIEW 测试
## 八、待明确事项

| 编号 | 待明确事项 | 责任方 | 截止 |
|------|----------|------|------|
EOF

cat > /tmp/dummy_review_field.md << 'EOF'
# REVIEW 测试
## 对齐结论
| 类别 | 数量 |
|---|---|
| ✅ 已对齐 | 5 |
| ⚠️ 需 JOIN | 1 |
| ❓ 待确认 | 0 |
| 🔴 缺失 | 0 |
EOF

python3 scripts/task-confirm-check.py \
    examples/01-wms-warehouse/TASK_CONFIRM_收货管理.md \
    /tmp/dummy_review_confirm.md \
    /tmp/dummy_review_field.md
```
Expected: 5 项 Check 全过,exit 0

**Step 2: 验证模板本身被 Check 1 拒绝**

```bash
python3 scripts/task-confirm-check.py \
    templates/TASK_CONFIRM.md \
    /tmp/dummy_review_confirm.md \
    /tmp/dummy_review_field.md
```
Expected: 报错 + exit 1(因为模板状态 = ⬜)

**Step 3: 清理 + 写 logs/STEP-P0-review.md**

```bash
rm -f /tmp/dummy_review_*.md
```

创建 `logs/STEP-P0-review.md`:

```markdown
# P0 整体 Review — 核心门控基础设施

> 日期：2026-06-24
> 覆盖 Task:1-8

## 1. P0 改了什么
- 新建 `scripts/task-confirm-check.py`(Check 1-5 全实现)
- 修改 `templates/TASK_CONFIRM.md`(状态二态、白名单话术、12 词红线)
- 修改 `skills/user-invoked/grill-task/SKILL.md`(hard gate 文本)
- 修改 `skills/disciplines/stage-gate/SKILL.md`(2→3 门控拆 3 条)

## 2. 拒绝的方案
- 方案 A：在 `field-alignment-check.py` 加 TASK_CONFIRM 分支
  - 拒绝理由：违反"新脚本独立"原则
- 方案 B：保留 🟡 兼容老用户
  - 拒绝理由：用户选硬删除;breaking change 由 CHANGELOG 处理

## 3. 边界情况考虑
- 边界 A：5 章节标题是中文"一、" vs 阿拉伯"1." → 当前仅匹配中文
- 边界 B：scripts/task-confirm-check.py 退出码 0/1/2 是否有消费者？ → 当前无消费者;Task 18 CI 集成会消费

## 4. 用户签字位
用户：⬜ 已审 P0 全部 8 个 Task / 日期：____
```

**Step 4: Commit P0 review**

```bash
git add logs/STEP-P0-review.md
git commit -m "docs(review): P0 整体 review (Task 1-8)"
```

**🛑 HARD GATE P0**:等用户对 P0 整体签字。**P0 未签字不进 P1**。

---

# P1 块:模板与 SKILL 文本对齐

## Task 10: 修改 templates/REVIEW_需求确认书.md

**Objective:** 修阶段号 + 加 BLOCK 规则。

**Files:**
- Modify: `templates/REVIEW_需求确认书.md`

**Step 1: 编辑 L65-67**

**改前**:
```
**用户审阅操作**：
- ✅ 所有"是否正确"列填 ✅ → 进入阶段 2
- ⬜ 仍有未确认项 → 告知 Claude 重新确认
```

**改后**:
```
**用户审阅操作**：
- ✅ 所有"是否正确"列填 ✅ + 第八节"待明确事项"为空 → 进入阶段 3（BRD）
- ⬜ 仍有未确认项 或 第八节非空 → HARD BLOCK，必须返回 grill-task 重新确认
- 🔴 任一"是否正确"列未填 → HARD BLOCK
```

**Step 2: Commit + Review**

```bash
git add templates/REVIEW_需求确认书.md
git commit -m "feat(templates): REVIEW_需求确认书 阶段号 + BLOCK 规则"
```

STEP-10-review.md 简化版(参考 Task 6-8 模板):
```markdown
# STEP 10 Review — REVIEW_需求确认书
## 1. 改了 L65-67:阶段号 2→3 + 加 BLOCK
## 2. 拒绝方案:保留"阶段 2"(author 已糊涂,改为 3 修正)
## 3. 边界:第八节非空 BLOCK 由 task-confirm-check.py Check 4 强制执行
## 4. 用户签字位
用户：⬜ 已审 / 日期：____
```

**🛑 HARD GATE**

---

## Task 11: 修改 templates/REVIEW_字段对齐分析.md

**Objective:** 状态字段扩 4 态 + 加 BLOCK 规则 + 修阶段号。

**Files:**
- Modify: `templates/REVIEW_字段对齐分析.md`

**Step 1: 编辑 L5**

**改前**:
```
> 状态：✅ 已对齐 / ⚠️ 部分待确认
```

**改后**:
```
> 状态：✅ 已对齐 / ⚠️ 需 JOIN / ❓ 待确认 / 🔴 缺失
> BLOCK 规则：🔴>0 或 ❓>0 → 禁止进入阶段 3（BRD）
>
> 说明：状态字段为四态可视化标签；BLOCK 判定以"对齐结论表"中的 ❓ 与 🔴 计数为准（task-confirm-check.py 解析该表的两行数字）。⚠️ 可保留（仅表示部分需 JOIN，不 BLOCK）。
```

**Step 2: 编辑 L49**

**改前**:
```
**结论**：⬜ 可以进入阶段 2 / ⬜ 需先解决待确认项
```

**改后**:
```
**结论**：
- ⬜ 🔴=0 且 ❓=0 → 可以进入阶段 3（BRD）
- ⬜ 🔴>0 或 ❓>0 → HARD BLOCK，需先解决待确认项
```

**Step 3: Commit + Review**

```bash
git add templates/REVIEW_字段对齐分析.md
git commit -m "feat(templates): REVIEW_字段对齐分析 4 态 + BLOCK + 阶段号"
```

STEP-11-review.md:
```markdown
# STEP 11 Review — REVIEW_字段对齐分析
## 1. 改了 L5(4 态 + BLOCK 注释)+ L49(阶段号 + 计数规则)
## 2. 拒绝方案:BLOCK 仅看 header 字符串(应看计数)
## 3. 边界:⚠️ 需 JOIN 保留为合法状态
## 4. 用户签字位
用户：⬜ 已审 / 日期：____
```

**🛑 HARD GATE**

---

## Task 12: 更新 scripts/field-alignment-check.py docstring

**Objective:** 在 docstring 显式声明该脚本不接 TASK_CONFIRM。

**Files:**
- Modify: `scripts/field-alignment-check.py`(仅 L1-12 docstring)

**Step 1: 编辑 docstring**

**改前**:
```
"""
字段对齐验证器（v1.3-dev）

支持从 Markdown 表格和 SQL DDL 中提取字段定义，检查文档引用字段是否在知识库中定义，
并在文档也给出字段定义时检查类型/可空性是否一致。

用法：
    python3 field-alignment-check.py <文档> <知识库文件> [--json]

退出码：0 = 全部对齐；1 = 发现不对齐；2 = 参数错误
"""
```

**改后**:
```
"""
字段对齐验证器（v1.4-dev）

支持从 Markdown 表格和 SQL DDL 中提取字段定义，检查文档引用字段是否在知识库中定义，
并在文档也给出字段定义时检查类型/可空性是否一致。

用途：仅校验 PRD / FSD / 数据模型 等设计文档对知识库表结构的引用一致性。
不适用：TASK_CONFIRM / REVIEW 需求确认书 / REVIEW 字段对齐分析——这些文档的
门控由 `scripts/task-confirm-check.py` 处理（v4.0.0 引入）。

用法：
    python3 field-alignment-check.py <文档> <知识库文件> [--json]

退出码：0 = 全部对齐；1 = 发现不对齐；2 = 参数错误
"""
```

**Step 2: 验证现有逻辑未破坏**

```bash
# 构造一个简单测试
echo "| 字段 | 类型 |
|------|------|
| FOO  | VARCHAR(50) |" > /tmp/test_doc.md
echo "| FOO  | VARCHAR(50) |" > /tmp/test_kb.md

python3 scripts/field-alignment-check.py /tmp/test_doc.md /tmp/test_kb.md
```
Expected: `✅ 字段引用、类型和可空性检查通过`,exit 0

**Step 3: Commit + Review**

```bash
rm -f /tmp/test_doc.md /tmp/test_kb.md
git add scripts/field-alignment-check.py
git commit -m "docs(scripts): field-alignment-check.py docstring 声明不接 TASK_CONFIRM"
```

STEP-12-review.md:
```markdown
# STEP 12 Review — field-alignment-check.py docstring
## 1. 改了 L1-12:加 v1.4-dev 标记 + 显式声明不接 TASK_CONFIRM
## 2. 拒绝方案:同时改逻辑(避免回归,只改文档)
## 3. 边界:现有调用方不受影响(只是加文档说明)
## 4. 用户签字位
用户：⬜ 已审 / 日期：____
```

**🛑 HARD GATE**

---

## Task 13: P1 集成验证 + STEP-P1-review.md + 用户签字

**Step 1: 跑脚本在 3 个 example 上**

```bash
for ex in examples/0*/TASK_CONFIRM_*.md; do
    cat > /tmp/rc.md << 'EOF'
# REVIEW 临时
## 八、待明确事项
| 编号 | 待明确事项 | 责任方 | 截止 |
|------|----------|------|------|
EOF
    cat > /tmp/rf.md << 'EOF'
# REVIEW 临时
## 对齐结论
| 类别 | 数量 |
|---|---|
| ❓ 待确认 | 0 |
| 🔴 缺失 | 0 |
EOF
    echo "=== $ex ==="
    python3 scripts/task-confirm-check.py "$ex" /tmp/rc.md /tmp/rf.md || break
done
rm -f /tmp/rc.md /tmp/rf.md
```
Expected: 3 个 example 全部 5 项 Check 通过

**Step 2: 写 logs/STEP-P1-review.md + Commit**

参考 Task 9 STEP-P0-review.md 模板,覆盖 Task 10-12。

**🛑 HARD GATE P1**

---

# P2 块:文档与 CI 同步

## Task 14: 验证 3 个 example 通过 task-confirm-check.py

**Objective:** 跑脚本确认 3 个 example 文件符合新规则(状态字段硬约束)。

**Files:**
- Verify: `examples/01-wms-warehouse/TASK_CONFIRM_收货管理.md`
- Verify: `examples/02-saas-dashboard/TASK_CONFIRM_订单管理.md`
- Verify: `examples/03-mobile-app/TASK_CONFIRM_会员积分.md`

**Step 1: 跑 3 个 example(用 Task 13 同样的 dummy REVIEW)**

复用 Task 13 命令。Expected: 3 个全通过。

**Step 2: 若 example 失败,修复**

若 example 失败,原因可能是:
- 含 12 词 TBD → 改写
- 5 章节不全 → 补章节
- 状态不为 ✅ → 改状态

修复后 commit + 更新 STEP-14-review.md 说明修复内容。

**Step 3: 写 STEP-14-review.md**

```markdown
# STEP 14 Review — 3 个 example 验证
## 1. 跑了 task-confirm-check.py 在 3 个 example 上
## 2. 若有失败:列出修复点
## 3. 边界:example 是"金标准",必须 100% 通过
## 4. 用户签字位
用户：⬜ 已审 / 日期：____
```

**🛑 HARD GATE**

---

## Task 15: 创建 .github/workflows/task-confirm-check.yml

**Objective:** CI 集成,PR 时自动跑 pytest + example 集成测试。

**Files:**
- Create: `.github/workflows/task-confirm-check.yml`

**Step 1: 创建 workflow 文件**

```yaml
name: task-confirm-check

on:
  pull_request:
    paths:
      - 'templates/**'
      - 'skills/**'
      - 'examples/**'
      - 'scripts/task-confirm-check.py'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Run unit tests
        run: |
          pip install pytest
          # Note: tests/ 目录在 P3 任务中创建,本次仅占位
          # pytest tests/test_task_confirm_check.py -v
      - name: Run script on examples
        run: |
          for ex in examples/0*/TASK_CONFIRM_*.md; do
            cat > /tmp/rc.md << 'EOF'
# REVIEW
## 八、待明确事项
| 编号 | 待明确事项 | 责任方 | 截止 |
|------|----------|------|------|
EOF
            cat > /tmp/rf.md << 'EOF'
# REVIEW
## 对齐结论
| 类别 | 数量 |
|---|---|
| ❓ 待确认 | 0 |
| 🔴 缺失 | 0 |
EOF
            python3 scripts/task-confirm-check.py "$ex" /tmp/rc.md /tmp/rf.md
          done
          rm -f /tmp/rc.md /tmp/rf.md
```

**Step 2: 验证 yaml 语法**

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/task-confirm-check.yml'))" && echo "✅ YAML 合法"
```
Expected: `✅ YAML 合法`

**Step 3: Commit + Review**

```bash
git add .github/workflows/task-confirm-check.yml
git commit -m "ci: task-confirm-check workflow for PR validation"
```

STEP-15-review.md:
```markdown
# STEP 15 Review — CI workflow
## 1. 新建 .github/workflows/task-confirm-check.yml
## 2. 拒绝方案:跑全部 9 阶段(当前仅跑 task-confirm-check.py)
## 3. 边界:tests/ 占位,P3 加 pytest
## 4. 用户签字位
用户：⬜ 已审 / 日期：____
```

**🛑 HARD GATE**

---

## Task 16: 修改 CHANGELOG.md

**Objective:** 加 v3.x breaking change 条目。

**Files:**
- Modify: `CHANGELOG.md`

**Step 1: 在顶部加新条目**

参考 CHANGELOG.md 现有格式,在最新版本前插入:

```markdown
## [Unreleased]

### Breaking Changes (v3.x)

- **TASK_CONFIRM 模板状态字段**:从三态 `⬜/🟡/✅` 改为二态 `⬜/✅`。现有 🟡 文档需手动改为 ⬜ 或 ✅
- **触发话术**:用户必须用白名单话术（`我已全部确认，可以进入下一步` 等 4 句）才能进入下一阶段。仅说"已填写"不再有效
- **新增门控脚本**:`scripts/task-confirm-check.py`(5 项检查),替代 `field-alignment-check.py` 在 grill-task 中的引用
- **grill-task 章节数**:从"4 章节"改为"5 章节"（一~五），SKILL 文档同步
```

**Step 2: Commit + Review**

```bash
git add CHANGELOG.md
git commit -m "docs(changelog): v3.x breaking change - TASK_CONFIRM 硬约束"
```

STEP-16-review.md:
```markdown
# STEP 16 Review — CHANGELOG
## 1. 加 Unreleased 段 + Breaking Changes 4 条
## 2. 拒绝方案:写在已发布版本下(应放 Unreleased)
## 3. 边界:需注明 migration 步骤
## 4. 用户签字位
用户：⬜ 已审 / 日期：____
```

**🛑 HARD GATE**

---

## Task 17: 修改 README.md

**Objective:** 引用新脚本 + 12 词列表 + 白名单话术。

**Files:**
- Modify: `README.md`

**Step 1: 找到 README 的 grill-task / TASK_CONFIRM 描述段,加引用**

(具体位置由 Claude 探索 README.md 后确定,在该节末追加)

```markdown
## 需求澄清门控（v3.x 新增）

`grill-task` 阶段新增 `scripts/task-confirm-check.py` 硬门控脚本：

- **5 项检查**:状态字段、12 词 TBD 扫描、5 章节完整、REVIEW 第八节为空、字段对齐 🔴/❓=0
- **12 词 TBD 红线**:TBD / TODO / 待定 / 稍后 / 下次 / N/A / 待确认 / 暂定 / 未定 / 待补充 / ⬜ / ❓
- **白名单话术**:用户必须用以下 4 句之一才能进入下一阶段：
  - `我已全部确认，可以进入下一步`
  - `确认通过，进入 BRD`
  - `全部完成，继续`
  - `approved, proceed to next stage`
```

**Step 2: Commit + Review**

```bash
git add README.md
git commit -m "docs(readme): 引用新门控脚本 + 12 词 + 白名单话术"
```

STEP-17-review.md:
```markdown
# STEP 17 Review — README
## 1. 加"需求澄清门控"段
## 2. 拒绝方案:放主目录太显眼(放合适位置)
## 3. 边界:不重复 CHANGELOG 内容
## 4. 用户签字位
用户：⬜ 已审 / 日期：____
```

**🛑 HARD GATE**

---

## Task 18: P2 最终验证 + STEP-P2-review.md + 用户签字

**Step 1: 全套验证**

```bash
# 1. 跑 3 个 example
echo "=== Example 集成测试 ==="
for ex in examples/0*/TASK_CONFIRM_*.md; do
    cat > /tmp/rc.md << 'EOF'
# REVIEW
## 八、待明确事项
| 编号 | 待明确事项 | 责任方 | 截止 |
|------|----------|------|------|
EOF
    cat > /tmp/rf.md << 'EOF'
# REVIEW
## 对齐结论
| 类别 | 数量 |
|---|---|
| ❓ 待确认 | 0 |
| 🔴 缺失 | 0 |
EOF
    python3 scripts/task-confirm-check.py "$ex" /tmp/rc.md /tmp/rf.md
done
rm -f /tmp/rc.md /tmp/rf.md

# 2. CI yaml 合法
echo "=== CI YAML ==="
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/task-confirm-check.yml'))"

# 3. 模板自身被拒(状态 = ⬜)
echo "=== 模板自检 ==="
cat > /tmp/rc.md << 'EOF'
# REVIEW
## 八、待明确事项
| 编号 | 待明确事项 | 责任方 | 截止 |
|------|----------|------|------|
EOF
cat > /tmp/rf.md << 'EOF'
# REVIEW
## 对齐结论
| 类别 | 数量 |
|---|---|
| ❓ 待确认 | 0 |
| 🔴 缺失 | 0 |
EOF
python3 scripts/task-confirm-check.py templates/TASK_CONFIRM.md /tmp/rc.md /tmp/rf.md
rm -f /tmp/rc.md /tmp/rf.md
```

Expected 全部命令 exit 0(模板自检除外,期望 exit 1)

**Step 2: 写 logs/STEP-P2-review.md + Commit**

```markdown
# P2 整体 Review — 文档与 CI 同步

> 覆盖 Task:14-17

## 1. P2 改了什么
- 验证 3 个 example 通过
- 新建 .github/workflows/task-confirm-check.yml
- 修改 CHANGELOG.md（v3.x breaking change）
- 修改 README.md（引用新脚本 + 12 词 + 白名单话术）

## 2. 拒绝的方案
- 方案 A：直接合并到 P0（一步到位）
  - 拒绝理由：P0/P1/P2 独立 commit 便于回滚

## 3. 边界情况考虑
- 边界 A：CI workflow 当前仅跑 example 集成测试，未跑 pytest（tests/ P3 建）
- 边界 B：CHANGELOG 的 breaking change 是否需写 migration guide → 当前在 README 说明即可，P3 单独写

## 4. 整体签字位
用户：⬜ 已审 P2 全部 5 个 Task / 日期：____
```

```bash
git add logs/STEP-P2-review.md
git commit -m "docs(review): P2 整体 review (Task 14-17)"
```

**🛑 HARD GATE P2(也是最终签字)**:全部 18 个 Task 完成。

---

# 验收清单

执行完所有 Task 后,验证以下:

- [ ] `scripts/task-confirm-check.py --self-test` exit 0
- [ ] 3 个 example TASK_CONFIRM 跑 task-confirm-check.py 全部 exit 0
- [ ] 模板本身跑 task-confirm-check.py exit 1(状态 = ⬜)
- [ ] `.github/workflows/task-confirm-check.yml` YAML 合法
- [ ] 4 份 STEP-N-review.md + 3 份 STEP-P*-review.md + STEP-9 整体 = 18 份 review 全签字
- [ ] CHANGELOG.md 含 v3.x breaking change 条目
- [ ] README.md 含 12 词列表 + 白名单话术
- [ ] 无新增 TODO/FIXME
- [ ] git log 干净,18 个 commit 描述清晰
- [ ] pytest(本次未实施,P3 补)

---

# 不在本次范围(P3,后续)

- `tests/test_task_confirm_check.py` 12 个 pytest case(本 plan Task 1-5 用临时脚本验证,未提交)
- `analysis-delivery-workflow/SKILL.md` 措辞修正("按顺序自动调"过于宽松)
- examples/ 下生成示例 `*_review_*.md` 文件
- 新脚本的 `--strict/--loose` 双模式
- 5 章节支持阿拉伯数字"1."等格式
- TBD 词表支持用户自定义配置

---

# 执行交接

**Plan 已保存**:`docs/plans/2026-06-24-grill-task-bugfix.md`

**18 个 Task**,每个 ≤2h,每个配 STEP-N-review.md + 用户签字(B+C)。

**接下来按 subagent-driven-development 执行**:
- 每个 Task 派一个 fresh subagent,带完整 spec + 上下文
- Spec compliance review 在 commit 前
- Code quality review 在 spec pass 后
- 双重 review 通过 + 用户签字 → 进下一个 Task