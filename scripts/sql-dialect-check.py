#!/usr/bin/env python3
"""
SQL 方言混用检查器

检查 markdown 文档中是否混用不同数据库方言（Oracle/PG/MySQL）。

用法：
    python3 sql-dialect-check.py <markdown文件或glob>
    python3 sql-dialect-check.py "docs/*.md"

退出码：
    0 = 通过
    1 = 发现混用
    2 = 参数错误

状态：v1.0 占位 - MVP 阶段功能简化版
"""
import sys
import re
import glob
from pathlib import Path

# 35+ 种违规模式（节选）
ORACLE_PATTERNS = [
    (r'\bNVL\s*\(', 'Oracle NVL()'),
    (r'\bSYSDATE\b', 'Oracle SYSDATE'),
    (r'\bROWNUM\b', 'Oracle ROWNUM'),
    (r'\|\|', 'Oracle 字符串连接 ||'),
]

PG_PATTERNS = [
    (r'\bCOALESCE\s*\(', 'PostgreSQL COALESCE()'),
    (r'\bNOW\s*\(\)', 'PostgreSQL NOW()'),
    (r'\bLIMIT\s+\d+', 'PostgreSQL LIMIT'),
]

MYSQL_PATTERNS = [
    (r'\bIFNULL\s*\(', 'MySQL IFNULL()'),
    (r'\bLIMIT\s+\d+,\s*\d+', 'MySQL LIMIT offset,count'),
]

def check_file(path: str) -> list:
    """检查单个文件，返回违规列表。"""
    violations = []
    try:
        content = Path(path).read_text(encoding='utf-8')
    except Exception as e:
        return [(path, 0, f'读取失败: {e}')]

    # 检测每种方言
    found = {'oracle': [], 'pg': [], 'mysql': []}
    for pattern, name in ORACLE_PATTERNS:
        for m in re.finditer(pattern, content, re.IGNORECASE):
            found['oracle'].append((m.start(), name))
    for pattern, name in PG_PATTERNS:
        for m in re.finditer(pattern, content, re.IGNORECASE):
            found['pg'].append((m.start(), name))
    for pattern, name in MYSQL_PATTERNS:
        for m in re.finditer(pattern, content, re.IGNORECASE):
            found['mysql'].append((m.start(), name))

    # 检测混用
    active = [k for k, v in found.items() if v]
    if len(active) > 1:
        for dialect in active:
            for pos, name in found[dialect]:
                line = content[:pos].count('\n') + 1
                violations.append((path, line, f'混用{dialect.upper()}: {name}'))

    return violations

def main():
    if len(sys.argv) < 2:
        print("用法: python3 sql-dialect-check.py <文件或glob>")
        sys.exit(2)

    files = []
    for arg in sys.argv[1:]:
        if '*' in arg or '?' in arg:
            files.extend(glob.glob(arg))
        else:
            files.append(arg)

    if not files:
        print("❌ 未找到匹配的文件")
        sys.exit(2)

    all_violations = []
    for f in files:
        all_violations.extend(check_file(f))

    if all_violations:
        print(f"❌ 发现 {len(all_violations)} 处方言混用：")
        for path, line, msg in all_violations:
            print(f"  {path}:{line} - {msg}")
        sys.exit(1)
    else:
        print(f"✅ 通过：{len(files)} 个文件未发现方言混用")
        sys.exit(0)

if __name__ == '__main__':
    main()
