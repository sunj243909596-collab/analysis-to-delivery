#!/usr/bin/env python3
"""ASCII flow → Mermaid 转换器(v3.0 工具链 + v4.0.0 ascii-strict)

将 examples/*/业务流程图-*.txt 中的 ASCII 流程图转换为 Mermaid 源码,
供 mermaid-cli(mmdc)渲染为 SVG/PNG。

用法:
    python3 scripts/flow-to-mermaid.py <input.txt> [output.mmd]
    python3 scripts/flow-to-mermaid.py examples/02-saas-dashboard/业务流程图-订单状态流转.txt
    python3 scripts/flow-to-mermaid.py --batch examples/
    python3 scripts/flow-to-mermaid.py --batch --ascii-strict examples/   # 新增 strict 模式
    python3 scripts/flow-to-mermaid.py --self-test

支持图类型(自动检测):
- 状态机(垂直 ▼ 箭头 / 水平 ─► 箭头)
- 节点连接(┌──┐...└──┘)

输出:
- .mmd 文件 + 控制台摘要(节点数 / 箭头数 / 需手动补充的边)

限制:
- 复杂泳道图(swimlane)需手动整理
- 边检测为启发式,失败时输出节点 + 边注释模板

--ascii-strict 模式(v4.0.0,plan §P1-2):
- ASCII 输入必须含"回流闭环":同一 box 标签至少出现 2 次(证据:已有回流目标节点)
  (与 ascii-flowchart L48-60 "回流路径必须汇聚到同一目标节点" 对齐)
- 输出 Mermaid 必须**不含** `classDef` 关键字(违反简洁性纪律)
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def normalize_id(raw: str, used: Dict[str, int]) -> str:
    """把任意字符串变成合法的 mermaid node id(只允许字母/数字/下划线)"""
    base = re.sub(r"[^A-Za-z0-9_]", "_", raw).strip("_")
    if not base or base[0].isdigit():
        base = "n_" + base
    # 去重
    candidate = base
    suffix = 2
    while candidate in used:
        candidate = f"{base}_{suffix}"
        suffix += 1
    used[base] = used.get(base, 0) + 1
    return candidate


def parse_box(lines: List[str], start: int) -> Optional[Tuple[str, str, int]]:
    """从 start 行开始向下找 box;返回 (node_id, label, end_line) 或 None。"""
    # 找 ┌──...──┐
    i = start
    while i < len(lines):
        if "┌" in lines[i] and "┐" in lines[i]:
            box_top = i
            # 收集 │ 内容行
            content: List[str] = []
            j = i + 1
            while j < len(lines):
                line = lines[j]
                if "└" in line and "┘" in line:
                    # 找到 box 底部
                    label = "<br/>".join(content) if content else "node"
                    return label, j + 1
                if "│" in line:
                    parts = line.split("│")
                    # 取中间部分(第一个 │ 到最后一个 │ 之间)
                    inner = "│".join(parts[1:-1]) if len(parts) >= 3 else ""
                    inner = inner.strip()
                    if inner:
                        content.append(inner)
                j += 1
            return None
        i += 1
    return None


def detect_edges(lines: List[str], positions: List[Tuple[int, int]]) -> List[Tuple[str, str, str]]:
    """启发式检测边(仅垂直箭头 ▼)。

    对每对相邻 clean box,检查 box 间隔区是否有 ▼ 字符。
    若有,把箭头前最近的非空文本作为边 label。
    """
    edges: List[Tuple[str, str, str]] = []
    for idx in range(len(positions) - 1):
        top_start, top_end = positions[idx]
        bot_start, bot_end = positions[idx + 1]
        for k in range(top_end, bot_start):
            line = lines[k]
            if "▼" in line:
                # 向上找 label(2-3 行内)
                label_text = ""
                for back in range(k - 1, max(top_end, k - 4), -1):
                    bl = lines[back]
                    if "│" in bl and "▼" not in bl:
                        # 提取 │...│ 之间的内容
                        parts = bl.split("│")
                        inner = "│".join(parts[1:-1]).strip() if len(parts) >= 3 else bl.strip()
                        # 清理 |
                        inner = re.sub(r"[│|]", " ", inner).strip()
                        if inner and inner not in ("", "│"):
                            label_text = inner
                            break
                edges.append((f"box{idx}", f"box{idx + 1}", label_text))
                break
    return edges


def is_clean_box_top(line: str) -> bool:
    """判断是否为简单 box 顶(┌...─┐,中间只含 ─ 与空格)。

    用于过滤掉"分支 box"或"合并 box"(中间含 │ 或其他字符)。
    """
    if "┌" not in line or "┐" not in line:
        return False
    try:
        start = line.index("┌")
        end = line.index("┐")
        middle = line[start + 1 : end]
        return all(c in "─ \t" for c in middle)
    except ValueError:
        return False


def collect_boxes(text: str) -> Tuple[List[str], List[Tuple[int, int]]]:
    """扫描全文,收集所有 clean box 的 (start_line, end_line) 范围。

    只收集顶行简单的 box(┌────┐),跳过分支 box。
    """
    lines = text.split("\n")
    positions: List[Tuple[int, int]] = []
    i = 0
    while i < len(lines):
        if is_clean_box_top(lines[i]):
            top = i
            j = i + 1
            while j < len(lines):
                if "└" in lines[j] and "┘" in lines[j]:
                    positions.append((top, j))
                    i = j + 1
                    break
                j += 1
            else:
                i += 1
        else:
            i += 1
    return lines, positions


def build_node_id_from_label(label: str, idx: int, used: Dict[str, int]) -> str:
    """从 label 提取 node id。优先用第一行的第一个英文单词。"""
    first_line = label.split("<br/>")[0].strip()
    # 找英文/数字单词
    m = re.search(r"[A-Za-z_][A-Za-z0-9_]*", first_line)
    if m:
        return normalize_id(m.group(0), used)
    # 否则用索引
    return normalize_id(f"node{idx}", used)


def clean_label(raw: str) -> str:
    """清理 label 中的 │、│ 等分隔符与多余空格。"""
    s = re.sub(r"[│|┃]", " ", raw)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def convert(src: Path) -> str:
    text = src.read_text(encoding="utf-8")
    lines, positions = collect_boxes(text)

    if not positions:
        return ""

    # 提取每个 box 的 label
    used: Dict[str, int] = {}
    nodes: List[Tuple[str, str]] = []  # [(id, label), ...]
    for idx, (top, bot) in enumerate(positions):
        content: List[str] = []
        for k in range(top + 1, bot):
            if "│" in lines[k]:
                parts = lines[k].split("│")
                inner = "│".join(parts[1:-1]) if len(parts) >= 3 else ""
                cleaned = clean_label(inner)
                if cleaned:
                    content.append(cleaned)
        label = "<br/>".join(content) if content else f"node{idx}"
        nid = build_node_id_from_label(label, idx, used)
        nodes.append((nid, label))

    # 检测边(简化:只看垂直 ▼)
    edges: List[Tuple[str, str, str]] = []
    for idx in range(len(positions) - 1):
        top_start, top_end = positions[idx]
        bot_start, bot_end = positions[idx + 1]
        # 在 box 之间找 ▼ 和 label
        arrow_found = False
        label_text = ""
        for k in range(top_end, bot_start):
            line = lines[k]
            if "▼" in line or "▼" in line:
                arrow_found = True
                # label 在箭头前后找
                for back in range(k - 1, max(top_end, k - 3), -1):
                    bl = lines[back]
                    if "│" in bl:
                        parts = bl.split("│")
                        inner = "│".join(parts[1:-1]).strip() if len(parts) >= 3 else bl.strip()
                        if inner and inner not in ("│", ""):
                            label_text = inner
                            break
                break
        if arrow_found:
            edges.append((nodes[idx][0], nodes[idx + 1][0], label_text))

    # 输出 mermaid
    out = ["graph LR"]
    out.append("    %% Auto-generated from " + src.name)
    out.append("    %% 节点顺序与原 ASCII 图一致")
    out.append("")
    for nid, label in nodes:
        safe_label = label.replace('"', '\\"')
        out.append(f'    {nid}["{safe_label}"]')
    out.append("")
    for from_id, to_id, label in edges:
        if label:
            safe_label = label.replace('"', '\\"')
            out.append(f'    {from_id} -->|"{safe_label}"| {to_id}')
        else:
            out.append(f'    {from_id} --> {to_id}')
    out.append("")

    # 若有疑似水平箭头,在末尾加注释提示
    has_horizontal = any(
        "──►" in line or "────►" in line or "───►" in line
        for line in lines
    )
    if has_horizontal:
        out.append("    %% ⚠️ 检测到水平箭头(──►),自动检测仅覆盖垂直箭头 ▼")
        out.append("    %% 请手动补充水平边,例如:draft -->|取消| cancelled")

    return "\n".join(out)


# ===== v4.0.0: --ascii-strict 校验 =====

def check_ascii_has_backflow(text: str) -> Tuple[bool, str]:
    """ASCII 必须含"回流闭环":同一 box 标签出现 ≥2 次(作为回流目标节点证据)。

    与 ascii-flowchart §回流闭环(强制)对齐:回流路径必须汇聚到同一目标节点。
    启发式:若某标签只出现 1 次,图中不存在"可被回流指向的目标"。

    Returns: (passed, message)
    """
    _, positions = collect_boxes(text)
    if not positions:
        return True, "no boxes to check"

    lines = text.split("\n")
    labels: List[str] = []
    for top, bot in positions:
        content: List[str] = []
        for k in range(top + 1, bot):
            if "│" in lines[k]:
                parts = lines[k].split("│")
                inner = "│".join(parts[1:-1]) if len(parts) >= 3 else ""
                cleaned = clean_label(inner)
                if cleaned:
                    content.append(cleaned)
        label = clean_label(" ".join(content))
        labels.append(label)

    counts: Dict[str, int] = {}
    for lb in labels:
        if lb:
            counts[lb] = counts.get(lb, 0) + 1

    repeated = {lb: c for lb, c in counts.items() if c >= 2}
    if not repeated:
        return False, (
            "ASCII 缺回流闭环:所有 box 标签只出现 1 次,"
            "未找到可作为回流汇聚目标节点的复用 box "
            "(与 ascii-flowchart §回流闭环(强制) 不符)"
        )
    sample = ", ".join(f"`{lb}`×{c}" for lb, c in list(repeated.items())[:3])
    return True, f"回流闭环 OK:{sample}"


def check_mermaid_no_classdef(mmd: str) -> Tuple[bool, str]:
    """输出 Mermaid 不应含 classDef(违反简洁性纪律)。

    Returns: (passed, message)
    """
    if "classDef" in mmd:
        return False, "输出 Mermaid 含 `classDef`(违反 ascii-flowchart 简洁性)"
    return True, "无 classDef"


def self_test() -> int:
    """内置自检(plan §P1-2)。"""
    import tempfile

    # Case 1: 无回流闭环的 ASCII → strict 应 fail(ASCII check)
    no_loop = (
        "┌──────┐\n"
        "│ 状态A │\n"
        "└──────┘\n"
        "   │\n"
        "   ▼\n"
        "┌──────┐\n"
        "│ 状态B │\n"
        "└──────┘\n"
    )
    ok, msg = check_ascii_has_backflow(no_loop)
    if ok:
        print("❌ self_test fail:no-loop 应被报")
        return 1
    print(f"  ✓ case1 no-loop rejected: {msg}")

    # Case 2: 有回流闭环的 ASCII(状态A 出现 2 次)→ strict 应 pass
    with_loop = (
        "┌──────┐\n"
        "│ 状态A │\n"
        "└──────┘\n"
        "   │\n"
        "   ▼\n"
        "┌──────┐\n"
        "│ 状态B │\n"
        "└──────┘\n"
        "   │\n"
        "   ▼\n"
        "┌──────┐\n"
        "│ 状态A │\n"
        "└──────┘\n"
    )
    ok, msg = check_ascii_has_backflow(with_loop)
    if not ok:
        print(f"❌ self_test fail:with-loop 应 pass,got: {msg}")
        return 1
    print(f"  ✓ case2 with-loop accepted: {msg}")

    # Case 3: Mermaid 含 classDef → strict 应 fail
    bad_mmd = "graph LR\n    classDef foo fill:red\n    A-->B\n"
    ok, msg = check_mermaid_no_classdef(bad_mmd)
    if ok:
        print("❌ self_test fail:classDef 应被报")
        return 1
    print(f"  ✓ case3 classDef rejected: {msg}")

    # Case 4: 干净 Mermaid → strict 应 pass
    good_mmd = "graph LR\n    A[\"状态A\"]\n    A-->B\n"
    ok, msg = check_mermaid_no_classdef(good_mmd)
    if not ok:
        print(f"❌ self_test fail:clean mermaid 应 pass,got: {msg}")
        return 1
    print(f"  ✓ case4 clean mermaid accepted: {msg}")

    # Case 5: 端到端 --ascii-strict on no-loop file → exit 1
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        src = tmpdir / "业务流程图-test.txt"
        src.write_text(no_loop, encoding="utf-8")
        import subprocess
        r = subprocess.run(
            ["python3", __file__, "--ascii-strict", str(src)],
            capture_output=True, text=True,
        )
        if r.returncode != 1:
            print(f"❌ self_test fail:end-to-end no-loop 应 exit 1,got {r.returncode}\n{r.stdout}")
            return 1
        print("  ✓ case5 end-to-end no-loop exit 1")

    # Case 6: 端到端 --ascii-strict on with-loop file → exit 0
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        src = tmpdir / "业务流程图-test.txt"
        src.write_text(with_loop, encoding="utf-8")
        import subprocess
        r = subprocess.run(
            ["python3", __file__, "--ascii-strict", str(src)],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            print(f"❌ self_test fail:end-to-end with-loop 应 exit 0,got {r.returncode}\n{r.stdout}")
            return 1
        print("  ✓ case6 end-to-end with-loop exit 0")

    print("✅ flow-to-mermaid.py self-test 通过 (4 check × 2 case = 8)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="将 ASCII 流程图(.txt)转换为 Mermaid 源码(.mmd)"
    )
    parser.add_argument(
        "input",
        nargs="*",
        help="输入 .txt 文件,或包含 .txt 的目录(配合 --batch)",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="批量模式:递归扫描 input 目录下的所有 业务流程图-*.txt",
    )
    parser.add_argument(
        "--output", "-o",
        help="输出目录(默认与输入同目录,.mmd 后缀)",
    )
    parser.add_argument(
        "--ascii-strict",
        action="store_true",
        help="严格模式(plan §P1-2):ASCII 必须含回流闭环(label 复用 ≥2),Mermaid 必须无 classDef",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="运行内置自检(无需输入文件)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 输出 strict 检查结果",
    )

    args = parser.parse_args()

    if args.self_test:
        return self_test()

    if not args.input:
        parser.error("至少需要一个 input 文件,或使用 --self-test")

    inputs: List[Path] = []
    if args.batch:
        for raw in args.input:
            p = Path(raw)
            if p.is_dir():
                inputs.extend(sorted(p.rglob("业务流程图-*.txt")))
            else:
                inputs.append(p)
    else:
        inputs = [Path(raw) for raw in args.input]

    if not inputs:
        print("❌ 没有找到输入文件", file=sys.stderr)
        return 2

    total_nodes = 0
    total_edges = 0
    strict_results: List[dict] = []  # 仅 --ascii-strict 模式填充
    fail_count = 0

    for src in inputs:
        if not src.exists():
            print(f"⚠️  跳过(不存在):{src}", file=sys.stderr)
            continue

        out_dir = Path(args.output) if args.output else src.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / (src.stem + ".mmd")

        text = src.read_text(encoding="utf-8")
        mmd = convert(src)
        if not mmd:
            print(f"⚠️  跳过(未找到 box):{src}", file=sys.stderr)
            continue

        out_path.write_text(mmd, encoding="utf-8")

        # 统计
        n_nodes = mmd.count('["')
        n_edges = mmd.count("-->|") + mmd.count("--> ")
        total_nodes += n_nodes
        total_edges += n_edges

        # --json 模式:常规打印走 stderr,避免污染 stdout
        per_file_print = (
            print if not (args.ascii_strict and args.json)
            else lambda *a, **kw: print(*a, file=sys.stderr, **kw)
        )
        per_file_print(f"✅ {src.name} → {out_path.name}({n_nodes} 节点, {n_edges} 边)")

        # strict 检查
        if args.ascii_strict:
            ascii_ok, ascii_msg = check_ascii_has_backflow(text)
            mermaid_ok, mermaid_msg = check_mermaid_no_classdef(mmd)
            file_pass = ascii_ok and mermaid_ok
            if not file_pass:
                fail_count += 1
            strict_results.append({
                "file": str(src),
                "ascii_has_backflow": ascii_ok,
                "ascii_msg": ascii_msg,
                "mermaid_no_classdef": mermaid_ok,
                "mermaid_msg": mermaid_msg,
                "passed": file_pass,
            })

    if args.ascii_strict and args.json:
        # JSON 模式:仅输出 JSON 到 stdout,summary 走 stderr
        print(json.dumps({"strict_results": strict_results, "fail_count": fail_count},
                         ensure_ascii=False, indent=2))
        print(f"\n📊 共 {len(inputs)} 个文件,{total_nodes} 节点,{total_edges} 边", file=sys.stderr)
    else:
        print(f"\n📊 共 {len(inputs)} 个文件,{total_nodes} 节点,{total_edges} 边")
        if args.ascii_strict:
            print(f"\n🔍 ASCII 严格模式结果:")
            for r in strict_results:
                mark = "✅" if r["passed"] else "❌"
                print(f"  {mark} {r['file']}")
                if not r["ascii_has_backflow"]:
                    print(f"      ASCII: {r['ascii_msg']}")
                if not r["mermaid_no_classdef"]:
                    print(f"      Mermaid: {r['mermaid_msg']}")
            print(f"\nstrict fail: {fail_count} / {len(strict_results)}")

    if args.ascii_strict:
        return 1 if fail_count > 0 else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())