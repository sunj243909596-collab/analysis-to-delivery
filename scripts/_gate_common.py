#!/usr/bin/env python3
"""
analysis-to-delivery 门控脚本共享工具（v4.0.0）

所有 stage-gate 门控脚本（setup-check / brd-check / compliance-check /
testcase-coverage-check / prd-check / dev-design-backtest-check /
discipline-lint / bridge-completeness-check / description-lint /
filename-naming-check）共享的：

- argparse 构造器（统一 --strict/--loose/--self-test/--json）
- 退出码常量
- JSON 输出 / 人类可读输出格式
- 状态 emoji 常量

参考: scripts/task-confirm-check.py v1.1.0
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional, Sequence


# 退出码
EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_USAGE = 2


# 状态 emoji
E_PASS = "✅"
E_FAIL = "❌"
E_WARN = "⚠️"
E_INFO = "ℹ️"


@dataclass
class CheckResult:
    """单条 check 的结果。"""

    name: str
    passed: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "passed": self.passed,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
        }


@dataclass
class GateReport:
    """一次门控运行的总报告。"""

    script: str
    target: str
    mode: str  # strict | loose
    checks: List[CheckResult] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(not c.passed for c in self.checks)

    @property
    def has_warnings(self) -> bool:
        return any(c.warnings for c in self.checks)

    def passed_checks(self) -> List[str]:
        return [c.name for c in self.checks if c.passed]

    def failed_checks(self) -> List[str]:
        return [c.name for c in self.checks if not c.passed]

    def to_dict(self) -> dict:
        return {
            "script": self.script,
            "target": self.target,
            "mode": self.mode,
            "checks": [c.to_dict() for c in self.checks],
            "summary": {
                "passed": len(self.passed_checks()),
                "failed": len(self.failed_checks()),
                "warnings": sum(len(c.warnings) for c in self.checks),
            },
        }


def build_parser(
    script_name: str,
    description: str,
    path_help: str = "目标项目目录或具体文档路径",
    extra_positionals: Sequence[argparse.ArgumentParser.add_argument] = (),
) -> argparse.ArgumentParser:
    """
    构造统一 argparse。

    用法:
        parser = build_parser("setup-check", "1→2 配置就绪门控")
        parser.add_argument("--foo")  # 在 main 里再补自定义参数
    """
    parser = argparse.ArgumentParser(description=description, prog=script_name)
    parser.add_argument("path", nargs="?", help=path_help)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="跑内置自检（不需要 path 参数）",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--strict",
        dest="mode",
        action="store_const",
        const="strict",
        default="strict",
        help="严格模式（默认）：任一错误即 exit 1",
    )
    mode.add_argument(
        "--loose",
        dest="mode",
        action="store_const",
        const="loose",
        help="宽松模式：部分 check 降级为 warning（不 BLOCK）",
    )
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    return parser


def emit_human(report: GateReport) -> None:
    """人类可读输出。"""
    for c in report.checks:
        if c.passed and not c.warnings:
            print(f"{E_PASS} {c.name} 通过")
        for e in c.errors:
            print(f"{E_FAIL} {c.name}: {e}")
        for w in c.warnings:
            print(f"{E_WARN}  {c.name}: {w}")
    if report.has_errors:
        s = report.to_dict()["summary"]
        print(
            f"\n共 {s['failed']} 项未通过 / {s['warnings']} 项警告"
        )
    elif report.has_warnings:
        print(f"\n{E_WARN}  全部硬指标通过；{sum(len(c.warnings) for c in report.checks)} 项 warning")


def emit_json(report: GateReport) -> None:
    """JSON 输出（stdout）。"""
    json.dump(report.to_dict(), sys.stdout, ensure_ascii=False, indent=2)
    print()  # 末尾换行


def finalize(report: GateReport, as_json: bool) -> int:
    """
    输出报告 + 返回退出码。

    退出码:
      0 = pass（strict: 全部硬指标通过；loose: 仅 warning 也算 pass）
      1 = fail（strict 模式有错误）
    """
    if as_json:
        emit_json(report)
    else:
        emit_human(report)
    if report.has_errors:
        return EXIT_FAIL
    return EXIT_PASS


def read_text(path: Path) -> str:
    """统一读 utf-8，文件不存在抛 FileNotFoundError。"""
    return path.read_text(encoding="utf-8")


def read_text_or_empty(path: Path) -> str:
    """读 utf-8，文件不存在返回空串（不抛）。"""
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def run_self_test(script_name: str, expected_checks: int) -> int:
    """
    内置自检：每个 gate 脚本都应该实现 --self-test。

    默认行为：打印自检 banner + exit 0。
    复杂的脚本可以在自己的 main 里 override。
    """
    print(
        f"{E_INFO}  {script_name} --self-test: 脚手架已就绪"
        f"（{expected_checks} 项 check 待业务接入）"
    )
    return EXIT_PASS
