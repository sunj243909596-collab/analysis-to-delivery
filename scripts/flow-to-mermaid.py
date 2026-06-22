#!/usr/bin/env python3
"""ASCII flow → Mermaid 转换器(v3.0 工具链)

将 examples/*/业务流程图-*.txt 中的 ASCII 流程图转换为 Mermaid 源码,
供 mermaid-cli(mmdc)渲染为 SVG/PNG。

用法:
    python3 scripts/flow-to-mermaid.py <input.txt> [output.mmd]
    python3 scripts/flow-to-mermaid.py examples/02-saas-dashboard/业务流程图-订单状态流转.txt
    python3 scripts/flow-to-mermaid.py --batch examples/

支持图类型(自动检测):
- 状态机(垂直 ▼ 箭头 / 水平 ─► 箭头)
- 节点连接(┌──┐...└──┘)

输出:
- .mmd 文件 + 控制台摘要(节点数 / 箭头数 / 需手动补充的边)

限制:
- 复杂泳道图(swimlane)需手动整理
- 边检测为启发式,失败时输出节点 + 边注释模板
"""

import argparse
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="将 ASCII 流程图(.txt)转换为 Mermaid 源码(.mmd)"
    )
    parser.add_argument(
        "input",
        nargs="+",
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

    args = parser.parse_args()

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
    for src in inputs:
        if not src.exists():
            print(f"⚠️  跳过(不存在):{src}", file=sys.stderr)
            continue

        out_dir = Path(args.output) if args.output else src.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / (src.stem + ".mmd")

        mmd = convert(src)
        if not mmd:
            print(f"⚠️  跳过(未找到 box):{src}", file=sys.stderr)
            continue

        out_path.write_text(mmd, encoding="utf-8")

        # 统计
        n_lines = mmd.count("\n    ") + mmd.count("\ngraph")
        n_nodes = mmd.count('["')
        n_edges = mmd.count("-->|") + mmd.count("--> ")
        total_nodes += n_nodes
        total_edges += n_edges

        print(f"✅ {src.name} → {out_path.name}({n_nodes} 节点, {n_edges} 边)")

    print(f"\n📊 共 {len(inputs)} 个文件,{total_nodes} 节点,{total_edges} 边")
    return 0


if __name__ == "__main__":
    sys.exit(main())