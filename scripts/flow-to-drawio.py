#!/usr/bin/env python3
"""ASCII 流程图 → drawio XML 转换器(v3.0 工具链,与 mermaid 并列)

将 examples/*/业务流程图-*.txt 中的 ASCII 流程图转换为 drawio 桌面格式
(.drawio 文件),可在 diagrams.net / drawio desktop 中打开编辑。

用法:
    python3 scripts/flow-to-drawio.py <input.txt> [output.drawio]
    python3 scripts/flow-to-drawio.py --batch examples/02-saas-dashboard/

输出:
    标准 drawio XML 格式,可直接拖入 https://app.diagrams.net/

布局策略:
    - 简单垂直布局:每个 box 按顺序垂直排列(间距 80px)
    - 边用 straight 直线连接
    - 样式:白底 + 圆角 + 蓝色边框(标准流程图风格)

限制:
    - 不做自动路由优化(简单直线)
    - 复杂分支布局需在 drawio 中手动调整
    - 与 flow-to-mermaid.py 互为补充(mermaid 适合网页/SVG, drawio 适合编辑)
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def is_clean_box_top(line: str) -> bool:
    """判断是否为简单 box 顶(┌...─┐,中间只含 ─ 与空格)。"""
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
    """扫描全文,收集所有 clean box 的 (start_line, end_line) 范围。"""
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


def clean_label(raw: str) -> str:
    """清理 label 中的 │、│ 等分隔符。"""
    s = re.sub(r"[│|┃]", " ", raw)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def extract_box_label(lines: List[str], top: int, bot: int) -> str:
    """提取 box 的 label(多行用 \\n 连接)。"""
    content: List[str] = []
    for k in range(top + 1, bot):
        if "│" in lines[k]:
            parts = lines[k].split("│")
            inner = "│".join(parts[1:-1]) if len(parts) >= 3 else ""
            cleaned = clean_label(inner)
            if cleaned:
                content.append(cleaned)
    return "\\n".join(content) if content else "node"


def detect_vertical_edges(
    lines: List[str],
    positions: List[Tuple[int, int]],
) -> List[Tuple[int, int, str]]:
    """检测垂直箭头 ▼ 的边。

    返回 [(from_idx, to_idx, label), ...]
    """
    edges: List[Tuple[int, int, str]] = []
    for idx in range(len(positions) - 1):
        top_end = positions[idx][1]
        bot_start = positions[idx + 1][0]
        for k in range(top_end, bot_start):
            if "▼" in lines[k]:
                # 向上找 label
                label_text = ""
                for back in range(k - 1, max(positions[idx][1], k - 4), -1):
                    bl = lines[back]
                    if "│" in bl and "▼" not in bl:
                        parts = bl.split("│")
                        inner = "│".join(parts[1:-1]).strip() if len(parts) >= 3 else bl.strip()
                        inner = clean_label(inner)
                        if inner and inner not in ("", "│"):
                            label_text = inner
                            break
                edges.append((idx, idx + 1, label_text))
                break
    return edges


def build_drawio_xml(nodes: List[str], edges: List[Tuple[int, int, str]]) -> str:
    """生成 drawio XML(简单垂直布局)。

    每个节点 120x60,垂直间距 80,左边距 200。
    """
    box_w = 120
    box_h = 60
    gap = 80
    margin_x = 200
    margin_y = 40

    xml_parts: List[str] = []
    xml_parts.append('<?xml version="1.0" encoding="UTF-8"?>')
    xml_parts.append(
        '<mxfile host="analysis-to-delivery" agent="flow-to-drawio.py" version="0.1.0">'
    )
    xml_parts.append('  <diagram id="flow" name="Flow">')
    xml_parts.append('    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="850" pageHeight="1100" math="0" shadow="0">')
    xml_parts.append("      <root>")
    xml_parts.append('        <mxCell id="0" />')
    xml_parts.append('        <mxCell id="1" parent="0" />')

    # 节点
    for idx, label in enumerate(nodes):
        x = margin_x
        y = margin_y + idx * (box_h + gap)
        # 转义 XML 特殊字符
        safe_label = (
            label.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
        xml_parts.append(
            f'        <mxCell id="node{idx}" value="{safe_label}" '
            f'style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#3b82f6;fontSize=12;" '
            f'vertex="1" parent="1">'
        )
        xml_parts.append(
            f'          <mxGeometry x="{x}" y="{y}" width="{box_w}" height="{box_h}" as="geometry" />'
        )
        xml_parts.append("        </mxCell>")

    # 边
    for edge_idx, (from_idx, to_idx, label) in enumerate(edges):
        safe_label = (
            label.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
        edge_id = f"edge{edge_idx}"
        label_attr = f'value="{safe_label}"' if safe_label else ""
        xml_parts.append(
            f'        <mxCell id="{edge_id}" {label_attr} '
            f'style="endArrow=classic;html=1;rounded=0;strokeColor=#64748b;fontSize=11;" '
            f'edge="1" parent="1" source="node{from_idx}" target="node{to_idx}">'
        )
        xml_parts.append(
            '          <mxGeometry relative="1" as="geometry" />'
        )
        xml_parts.append("        </mxCell>")

    xml_parts.append("      </root>")
    xml_parts.append("    </mxGraphModel>")
    xml_parts.append("  </diagram>")
    xml_parts.append("</mxfile>")

    return "\n".join(xml_parts)


def convert(src: Path) -> str:
    """转换单个文件为 drawio XML。"""
    text = src.read_text(encoding="utf-8")
    lines, positions = collect_boxes(text)

    if not positions:
        return ""

    nodes = [extract_box_label(lines, top, bot) for top, bot in positions]
    edges = detect_vertical_edges(lines, positions)
    return build_drawio_xml(nodes, edges)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="将 ASCII 流程图(.txt)转换为 drawio XML(.drawio)"
    )
    parser.add_argument("input", nargs="+", help="输入 .txt 文件")
    parser.add_argument(
        "--batch",
        action="store_true",
        help="批量模式:递归扫描 input 目录下的 业务流程图-*.txt",
    )
    parser.add_argument("--output", "-o", help="输出目录")

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

    total = 0
    for src in inputs:
        if not src.exists():
            print(f"⚠️  跳过(不存在):{src}", file=sys.stderr)
            continue

        out_dir = Path(args.output) if args.output else src.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / (src.stem + ".drawio")

        xml = convert(src)
        if not xml:
            print(f"⚠️  跳过(未找到 box):{src}", file=sys.stderr)
            continue

        out_path.write_text(xml, encoding="utf-8")
        total += 1
        print(f"✅ {src.name} → {out_path.name}")

    print(f"\n📊 共 {total} 个文件。可用 https://app.diagrams.net/ 打开。")
    return 0


if __name__ == "__main__":
    sys.exit(main())