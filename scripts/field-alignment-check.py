#!/usr/bin/env python3
"""
字段对齐验证器

检查文档中引用的字段是否与知识库定义一致。

用法：
    python3 field-alignment-check.py <文档> <知识库文件>
    python3 field-alignment-check.py docs/PRD.md knowledge/schema.md

退出码：
    0 = 全部对齐
    1 = 发现不对齐
    2 = 参数错误

状态：v1.0 占位 - MVP 阶段功能简化版
"""
import sys
import re
from pathlib import Path

# 简单的字段名提取（占位）
FIELD_PATTERN = re.compile(r'`([A-Z][A-Z0-9_]+)`')

def extract_fields(content: str) -> set:
    """从文档中提取字段名。"""
    return set(FIELD_PATTERN.findall(content))

def main():
    if len(sys.argv) < 3:
        print("用法: python3 field-alignment-check.py <文档> <知识库文件>")
        sys.exit(2)

    doc_path = Path(sys.argv[1])
    kb_path = Path(sys.argv[2])

    if not doc_path.exists():
        print(f"❌ 文档不存在: {doc_path}")
        sys.exit(2)
    if not kb_path.exists():
        print(f"❌ 知识库不存在: {kb_path}")
        sys.exit(2)

    doc_fields = extract_fields(doc_path.read_text(encoding='utf-8'))
    kb_fields = extract_fields(kb_path.read_text(encoding='utf-8'))

    missing = doc_fields - kb_fields
    extra = kb_fields - doc_fields

    if missing:
        print(f"⚠️  文档引用但知识库未定义 ({len(missing)}):")
        for f in sorted(missing)[:20]:
            print(f"  - {f}")
        if len(missing) > 20:
            print(f"  ... 还有 {len(missing) - 20} 个")
        print("")
        print("⚠️  v1.0 占位 - 仅做简单字段名匹配，v1.1 增强类型/可空性检查")
        sys.exit(1)
    else:
        print(f"✅ 全部对齐：{len(doc_fields)} 个字段均在知识库中定义")
        sys.exit(0)

if __name__ == '__main__':
    main()
