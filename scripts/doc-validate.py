#!/usr/bin/env python3
"""
单文档快速校验（v1.2+）

对单个或一组 markdown 文档做轻量级格式校验：
- YAML frontmatter（如适用）
- 内部链接（相对路径）是否存在
- 代码块是否有语言标签
- 未替换的占位符（{xxx}）
- 必备章节（按文档类型）

用法：
    python3 doc-validate.py docs/01-BRD.md
    python3 doc-validate.py docs/                    # 整个目录
    python3 doc-validate.py --type BRD docs/         # 按类型校必备章节
    python3 doc-validate.py --json docs/             # JSON 输出
    python3 doc-validate.py --help

退出码：
    0 = 通过（无 P0）
    1 = 有 P1 警告
    2 = 有 P0 错误

P0 = 致命（章节缺失、链接指向明显错的地方）
P1 = 警告（占位符遗留、链接失效、frontmatter 字段缺失）
P2 = 建议（代码块无语言标签）

状态：v1.2 实现
"""
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

# 模板类型 → 必备 H2 章节前缀
REQUIRED_SECTIONS = {
    "BRD":    ["一、项目概述", "二、角色与职责", "三、业务流程", "四、功能模块", "五、数据要求"],
    "FSD":    ["一、模块清单", "二、功能详述", "三、接口契约", "四、状态机", "五、数据模型概览", "六、错误码字典"],
    "PRD":    ["一、产品概述", "二、用户故事", "三、功能需求", "七、验收标准"],
    "DATA":   ["一、模型概览", "二、表清单", "三、表设计"],
    "DEV":    ["一、架构设计", "二、模块设计", "三、联调说明", "四、Checklist"],
    "TASK":   ["一、需求背景", "二、需求目标", "三、功能范围"],
    "REVIEW": ["一、需求背景确认", "二、需求目标确认", "三、功能范围确认"],
    "TEST":   ["一、测试范围", "二、测试策略", "三、测试用例"],
    "COMPL":  ["一、基本信息", "二、合规性分析", "五、综合判定"],
    "HANDOVER": ["一、已完成文档", "二、待办事项"],
}

# 类型关键词（用于从文件名推断 type）
TYPE_HINTS = {
    "BRD":     ["业务需求", "BRD"],
    "FSD":     ["功能规格", "FSD"],
    "PRD":     ["产品需求", "PRD"],
    "DATA":    ["数据模型"],
    "DEV":     ["开发设计", "开发设计说明书"],
    "TASK":    ["TASK_CONFIRM"],
    "REVIEW":  ["REVIEW_需求确认书", "需求确认书"],  # 字段对齐分析独立，不归入 REVIEW
    "TEST":    ["测试用例", "TEST_CASE"],
    "COMPL":   ["合规评审"],
    "HANDOVER": ["HANDOVER"],
}


def detect_type(path: Path) -> str | None:
    """从文件名启发式判断文档类型。"""
    name = path.name
    for t, hints in TYPE_HINTS.items():
        for h in hints:
            if h in name:
                return t
    return None


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """解析 YAML frontmatter，返回 (dict, 正文)。"""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    fm_text = text[4:end]
    body = text[end + 5:]
    fm = {}
    for line in fm_text.splitlines():
        m = re.match(r"^([\w-]+):\s*(.*)$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip()
    return fm, body


def check_frontmatter(text: str) -> list[dict]:
    """检查 YAML frontmatter（仅当存在时）。"""
    issues = []
    if not text.startswith("---\n"):
        return issues
    fm, _ = parse_frontmatter(text)
    if not fm:
        issues.append({"level": "P0", "msg": "YAML frontmatter 格式错误（缺少 name / version 等字段）"})
        return issues
    if "name" not in fm:
        issues.append({"level": "P1", "msg": "YAML frontmatter 缺少 name 字段"})
    if "version" not in fm:
        issues.append({"level": "P1", "msg": "YAML frontmatter 缺少 version 字段"})
    return issues


def check_internal_links(text: str, base: Path) -> list[dict]:
    """检查内部 markdown 链接的目标是否存在。"""
    issues = []
    pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    for m in pattern.finditer(text):
        target = m.group(2)
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        # 去掉 anchor
        target_clean = target.split("#", 1)[0]
        if not target_clean:
            continue
        # URL 解码（处理 %20 等编码）
        target_clean = unquote(target_clean)
        # 链接相对当前文件所在目录解析
        target_path = (base / target_clean)
        if not target_path.exists():
            issues.append({"level": "P1", "msg": f"内部链接失效：[{m.group(1)}]({target})"})
    return issues


def check_code_blocks(text: str) -> list[dict]:
    """检查代码块是否有语言标签。"""
    issues = []
    pattern = re.compile(r"^```\s*$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    for i, m in enumerate(matches):
        # 这是结束标记，跳过；开始标记是奇数位置（0, 2, 4...）
        if i % 2 == 0:
            # 检查下一行是不是语言标识（如果不是空行 + 文本，就是没有语言标签）
            after_start = text[m.end():m.end()+100].split("\n", 1)
            if len(after_start) > 1 and after_start[1].startswith("```"):
                # 这是空代码块如 ```\n```，无效但不算
                continue
            if after_start[0].strip() == "":
                # ``` 后第一行是空，可能是 ```\n空\n```，再看下一行
                continue
    # 简化：检查 ```\n 后下一行是不是 ```（即闭合）。其实 python 解析简单
    # 改用配对检测
    code_blocks = re.findall(r"^```(\w*)\n(.*?)^```", text, re.MULTILINE | re.DOTALL)
    for lang, _ in code_blocks:
        if not lang:
            issues.append({"level": "P2", "msg": "代码块缺语言标签（建议加 ```python / ```bash 等）"})
    return issues


def check_placeholders(text: str) -> list[dict]:
    """检查未替换的占位符。"""
    issues = []
    # 排除在代码块内的占位符
    text_no_code = re.sub(r"^```.*?^```", "", text, flags=re.MULTILINE | re.DOTALL)
    # 排除 Jinja2 语法（{{ ... }}、{% ... %}）
    text_no_code = re.sub(r"\{\{[^}]*\}\}", "", text_no_code)
    text_no_code = re.sub(r"\{%[^}]*%\}", "", text_no_code)
    placeholders = re.findall(r"\{([^{}]{1,30})\}", text_no_code)
    suspicious = []
    for p in placeholders:
        # 跳过常见非占位符模式（如 {n}、{i}、{0}、{1} 等是 format string）
        if re.match(r"^\d+$|^\d+,\d+$|^[a-z]$", p):
            continue
        # 跳过日志占位符等
        if p in ("YYYY", "MM", "DD", "HH", "mm", "ss"):
            continue
        suspicious.append(p)
    if suspicious:
        unique = sorted(set(suspicious))[:5]
        issues.append({
            "level": "P1",
            "msg": f"发现 {len(set(suspicious))} 个未替换的占位符：{', '.join(unique)}{'...' if len(set(suspicious)) > 5 else ''}",
        })
    return issues


def check_required_sections(text: str, doc_type: str) -> list[dict]:
    """检查必备 H2 章节。"""
    issues = []
    if doc_type not in REQUIRED_SECTIONS:
        return issues
    # 提取所有 ## 章节
    headings = re.findall(r"^##\s+(.+)$", text, re.MULTILINE)
    for required in REQUIRED_SECTIONS[doc_type]:
        if not any(required in h for h in headings):
            issues.append({"level": "P0", "msg": f"必备章节缺失：## {required}"})
    return issues


def check_h1(text: str) -> list[dict]:
    """检查是否只有一个 H1。"""
    issues = []
    h1s = re.findall(r"^#\s+(.+)$", text, re.MULTILINE)
    if not h1s:
        issues.append({"level": "P1", "msg": "缺少 H1 标题（# xxx）"})
    elif len(h1s) > 1:
        issues.append({"level": "P2", "msg": f"多个 H1 标题（{len(h1s)} 个），建议只保留 1 个"})
    return issues


def validate_file(path: Path, base: Path, doc_type: str | None) -> dict:
    """校验单个文档，返回结果。"""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return {"file": str(path), "error": str(e), "issues": []}

    # 推断 type
    if doc_type is None:
        doc_type = detect_type(path)

    issues = []
    issues.extend(check_h1(text))
    issues.extend(check_frontmatter(text))
    issues.extend(check_internal_links(text, path.parent))  # 相对当前文件所在目录
    issues.extend(check_code_blocks(text))
    issues.extend(check_placeholders(text))
    if doc_type:
        issues.extend(check_required_sections(text, doc_type))

    return {
        "file": str(path.relative_to(base)) if base in path.parents else str(path),
        "type": doc_type,
        "issues": issues,
    }


def main():
    parser = argparse.ArgumentParser(description="单文档快速校验（v1.2+）")
    parser.add_argument("paths", nargs="+", help="文件或目录")
    parser.add_argument("--type", choices=list(REQUIRED_SECTIONS.keys()), help="指定文档类型（用于必备章节检查）")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--level", choices=["P0", "P1", "P2"], default="P2", help="只显示 ≤ 此严重度的问题（P2=全显示，P0=只看致命）")
    args = parser.parse_args()

    level_rank = {"P0": 0, "P1": 1, "P2": 2}
    max_rank = level_rank[args.level]  # 用户选的级别；rank 越小越严重

    files = []
    base = Path.cwd()
    for p_str in args.paths:
        p = Path(p_str)
        if p.is_file():
            files.append(p)
            if p.parent != base:
                base = p.parent
        elif p.is_dir():
            files.extend(p.rglob("*.md"))

    if not files:
        print("❌ 未找到任何 markdown 文件")
        sys.exit(2)

    all_results = []
    p0_count = 0
    p1_count = 0
    p2_count = 0

    for f in sorted(files):
        result = validate_file(f, base, args.type)
        all_results.append(result)
        for issue in result["issues"]:
            rank = level_rank.get(issue["level"], 2)
            if issue["level"] == "P0": p0_count += 1
            elif issue["level"] == "P1": p1_count += 1
            elif issue["level"] == "P2": p2_count += 1
            if rank > max_rank:  # noqa
                continue
            if args.json:
                continue  # JSON 模式汇总输出
            icon = {"P0": "❌", "P1": "⚠️ ", "P2": "💡"}[issue["level"]]
            print(f"  {icon} [{issue['level']}] {result['file']}: {issue['msg']}")

    if args.json:
        summary = {"files": len(all_results), "p0": p0_count, "p1": p1_count, "p2": p2_count, "results": all_results}
        print(json.dumps(summary, ensure_ascii=False, indent=2))

    if not args.json:
        print(f"\n📊 校验结果：{len(files)} 个文档 | P0={p0_count} P1={p1_count} P2={p2_count}")
        if p0_count > 0:
            print("❌ 有 P0 问题，需修复")
            sys.exit(2)
        elif p1_count > 0:
            print("⚠️  有 P1 警告，建议关注")
            sys.exit(1)
        else:
            print("✅ 全部通过")
            sys.exit(0)


if __name__ == "__main__":
    main()
