#!/usr/bin/env python3
"""
PRD HTML 后处理脚本（v1.3-dev）

将 pandoc 或普通 HTML 重组为带封面、目录、章节容器、响应式样式和打印样式的 PRD HTML。
无第三方依赖。
"""
import argparse
import html
import re
import sys
from pathlib import Path

STYLE = r"""
:root { --ink:#1f2a37; --muted:#667085; --line:#d9e2ec; --brand:#0f766e; --paper:#fffdf8; --soft:#f2f7f5; }
* { box-sizing: border-box; }
body { margin:0; font:16px/1.72 Georgia, 'Noto Serif SC', 'Songti SC', serif; color:var(--ink); background:linear-gradient(135deg,#f8fafc,#eef7f4 45%,#fff8ea); }
.prd-shell { max-width:1180px; margin:0 auto; padding:40px 24px 72px; }
.prd-cover { padding:56px; border:1px solid var(--line); border-radius:28px; background:radial-gradient(circle at top right,#d6f5ec,transparent 34%), var(--paper); box-shadow:0 24px 80px rgba(15,118,110,.12); }
.prd-kicker { color:var(--brand); text-transform:uppercase; letter-spacing:.18em; font:700 13px/1.2 system-ui, sans-serif; }
.prd-cover h1 { margin:16px 0 12px; font-size:clamp(36px,6vw,72px); line-height:1.04; border:0; }
.prd-meta { color:var(--muted); font-family:system-ui, sans-serif; }
.prd-grid { display:grid; grid-template-columns:280px 1fr; gap:28px; margin-top:28px; align-items:start; }
.prd-toc { position:sticky; top:20px; padding:22px; border:1px solid var(--line); border-radius:22px; background:rgba(255,253,248,.86); backdrop-filter:blur(10px); }
.prd-toc h2 { margin:0 0 12px; font:800 15px/1.2 system-ui, sans-serif; border:0; }
.prd-toc a { display:block; padding:8px 0; color:var(--ink); text-decoration:none; border-bottom:1px dashed #e5e7eb; font-family:system-ui, sans-serif; font-size:14px; }
.prd-content { min-width:0; }
.prd-section { margin:0 0 24px; padding:30px; border:1px solid var(--line); border-radius:24px; background:rgba(255,255,255,.9); box-shadow:0 16px 36px rgba(31,42,55,.06); }
.prd-section h2:first-child { margin-top:0; }
h1,h2,h3 { font-family:'Noto Serif SC', Georgia, serif; } h2 { border-bottom:2px solid var(--soft); padding-bottom:10px; }
table { width:100%; border-collapse:collapse; margin:18px 0; font-family:system-ui, sans-serif; font-size:14px; } th,td { border:1px solid var(--line); padding:10px 12px; vertical-align:top; } th { background:var(--soft); }
code { background:#eef2f7; padding:.15em .35em; border-radius:6px; } pre { overflow:auto; padding:16px; border-radius:16px; background:#111827; color:#f9fafb; }
@media (max-width:860px){ .prd-shell{padding:20px 14px 48px}.prd-cover{padding:30px}.prd-grid{grid-template-columns:1fr}.prd-toc{position:static}.prd-section{padding:20px} }
@media print { body{background:white}.prd-shell{max-width:none;padding:0}.prd-cover,.prd-section,.prd-toc{box-shadow:none;border-color:#bbb}.prd-grid{display:block}.prd-toc{position:static;page-break-after:always} }
"""


def extract_body(raw: str) -> str:
    m = re.search(r"<body[^>]*>(.*?)</body>", raw, flags=re.I | re.S)
    return m.group(1) if m else raw


def extract_title(raw: str, body: str) -> str:
    for pattern in [r"<title[^>]*>(.*?)</title>", r"<h1[^>]*>(.*?)</h1>"]:
        m = re.search(pattern, raw if "title" in pattern else body, flags=re.I | re.S)
        if m:
            return re.sub(r"<[^>]+>", "", m.group(1)).strip() or "PRD"
    return "PRD"


def slugify(text: str, used: set[str]) -> str:
    base = re.sub(r"<[^>]+>", "", text).strip().lower()
    base = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", base).strip("-") or "section"
    slug = base
    i = 2
    while slug in used:
        slug = f"{base}-{i}"
        i += 1
    used.add(slug)
    return slug


def sectionize(body: str) -> tuple[str, str]:
    h2_re = re.compile(r"<h2([^>]*)>(.*?)</h2>", re.I | re.S)
    matches = list(h2_re.finditer(body))
    if not matches:
        return "<p>本文暂无二级目录。</p>", f'<article class="prd-section">{body}</article>'
    used: set[str] = set()
    toc_items = []
    parts = []
    prefix = body[:matches[0].start()].strip()
    if prefix:
        parts.append(f'<article class="prd-section prd-preface">{prefix}</article>')
    for idx, m in enumerate(matches):
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(body)
        title_html = m.group(2)
        title_text = re.sub(r"<[^>]+>", "", title_html).strip()
        sid = slugify(title_text, used)
        heading = f'<h2 id="{sid}"{m.group(1)}>{title_html}</h2>'
        content = heading + body[m.end():end]
        toc_items.append(f'<a href="#{sid}">{html.escape(title_text)}</a>')
        parts.append(f'<section class="prd-section">{content}</section>')
    return "\n".join(toc_items), "\n".join(parts)


def build_html(raw: str) -> str:
    body = extract_body(raw)
    title = extract_title(raw, body)
    body = re.sub(r"<h1[^>]*>.*?</h1>", "", body, count=1, flags=re.I | re.S).strip()
    toc, content = sectionize(body)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>{STYLE}</style>
</head>
<body>
<main class="prd-shell">
  <header class="prd-cover">
    <div class="prd-kicker">Product Requirements Document</div>
    <h1>{html.escape(title)}</h1>
    <div class="prd-meta">由 analysis-to-delivery 后处理生成 · 适合评审、归档与打印</div>
  </header>
  <div class="prd-grid">
    <nav class="prd-toc" aria-label="目录"><h2>目录</h2>{toc}</nav>
    <div class="prd-content">{content}</div>
  </div>
</main>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="PRD HTML 后处理脚本")
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    if not input_path.exists():
        print(f"❌ 输入文件不存在: {input_path}", file=sys.stderr)
        sys.exit(2)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_html(input_path.read_text(encoding="utf-8")), encoding="utf-8")
    print(f"✅ PRD HTML 已生成: {output_path}")


if __name__ == "__main__":
    main()
