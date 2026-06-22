#!/usr/bin/env python3
"""
PRD HTML 后处理脚本

将 pandoc 导出的中间 HTML 重组为带样式的最终 HTML。

用法：
    python3 postprocess_prd_html.py <input.html> <output.html>

状态：v1.0 占位 - MVP 阶段功能简化版
"""
import sys
from pathlib import Path

def main():
    if len(sys.argv) < 3:
        print("用法: python3 postprocess_prd_html.py <input.html> <output.html>")
        sys.exit(2)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not input_path.exists():
        print(f"❌ 输入文件不存在: {input_path}")
        sys.exit(2)

    # 占位：直接复制 + 加注释
    content = input_path.read_text(encoding='utf-8')
    # 注入一个 marker
    content = content.replace('<body>', '<body><!-- postprocessed by postprocess_prd_html.py v1.0-mvp -->')
    output_path.write_text(content, encoding='utf-8')

    print(f"✅ 处理完成: {output_path}")
    print("⚠️  v1.0 占位 - 仅做基本处理，v1.1 实现完整布局重组")
    sys.exit(0)

if __name__ == '__main__':
    main()
