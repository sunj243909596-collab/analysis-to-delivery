#!/usr/bin/env python3
"""
analysis-state.py — 9 阶段流程状态持久化(plan §P1-3, v3.1.0-dev)

在项目根维护 `.analysis-delivery-state.json`,提供:
- init      初始化(已有则报错)
- record-gate  记录某阶段最后一次 gate 脚本的运行结果
- signoff   记录某阶段的白名单签字
- status    显示当前状态
- metrics   输出 5 项度量指标

签字白名单(只接受 4 句之一,其他一律 reject):
- "我已全部确认,可以进入下一步"
- "确认通过"
- "全部完成,继续"
- "approved, proceed to next stage"

退出码:0 = OK;1 = fail;2 = 参数错误
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


STATE_FILENAME = ".analysis-delivery-state.json"
SCHEMA_VERSION = "1.0.0"

# 9 个阶段(与 analysis-delivery-workflow SKILL.md 对齐)
STAGES = list(range(1, 10))

# 阶段名(只用于显示)
STAGE_NAMES = {
    1: "项目配置",
    2: "需求澄清",
    3: "BRD",
    4: "合规评审",
    5: "测试用例",
    6: "PRD",
    7: "开发设计",
    8: "QA 审计",
    9: "交接",
}

# 4 句白名单(plan §stage-gate discipline)
SIGNOFF_PHRASES = [
    "我已全部确认,可以进入下一步",
    "确认通过",
    "全部完成,继续",
    "approved, proceed to next stage",
]

# 已知 gate 脚本白名单(防止 typo)
KNOWN_GATES = {
    "setup-check", "task-confirm-check", "brd-check", "compliance-check",
    "testcase-coverage-check", "prd-check", "dev-design-backtest",
    "field-alignment-check", "sql-dialect-check", "full-qa-audit",
    "doc-validate", "bridge-completeness-check", "discipline-lint",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ===== 原子读写 =====

def load_state(project_root: Path) -> dict:
    p = project_root / STATE_FILENAME
    if not p.exists():
        raise FileNotFoundError(
            f"未找到 {p},请先运行 `python3 scripts/analysis-state.py init --project <name>`"
        )
    return json.loads(p.read_text(encoding="utf-8"))


def save_state(project_root: Path, state: dict) -> None:
    p = project_root / STATE_FILENAME
    p.write_text(
        json.dumps(state, ensure_ascii=False, indent=2, sort_keys=False),
        encoding="utf-8",
    )


def new_state(project: str, project_root: Path) -> dict:
    return {
        "version": SCHEMA_VERSION,
        "project": {
            "name": project,
            "root": str(project_root),
            "started_at": now_iso(),
        },
        "current_stage": 1,
        "stages": {
            str(i): {
                "status": "⬜",
                "name": STAGE_NAMES[i],
                "signed_at": None,
                "signoff_text": None,
                "last_gate": None,
                "last_run": None,
                "errors": 0,
                "retries": 0,
            }
            for i in STAGES
        },
        "metrics": {
            "stage_durations_min": {str(i): None for i in STAGES},
            "gate_interjections": {g: 0 for g in KNOWN_GATES},
            "retries_per_stage": {str(i): 0 for i in STAGES},
            "total_gates_run": 0,
            "total_signoffs": 0,
        },
        "artifacts": {},
    }


# ===== 白名单校验 =====

def is_valid_signoff(text: str) -> bool:
    text = text.strip()
    return text in SIGNOFF_PHRASES


# ===== 5 个子命令 =====

def cmd_init(args) -> int:
    root = Path(args.project_root).resolve()
    p = root / STATE_FILENAME
    if p.exists() and not args.force:
        print(f"❌ {p} 已存在,加 --force 覆盖", file=sys.stderr)
        return 1
    state = new_state(args.project, root)
    save_state(root, state)
    print(f"✅ 已初始化 {p}")
    print(f"   project = {args.project}")
    print(f"   root    = {root}")
    return 0


def cmd_record_gate(args) -> int:
    root = Path(args.project_root).resolve()
    try:
        state = load_state(root)
    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        return 1
    if args.stage not in STAGES:
        print(f"❌ stage 必须在 1-9,实际 {args.stage}", file=sys.stderr)
        return 2
    if args.script not in KNOWN_GATES:
        print(f"⚠️  script '{args.script}' 不在已知白名单,仍记录", file=sys.stderr)
    s = state["stages"][str(args.stage)]
    s["last_gate"] = args.script
    s["last_run"] = now_iso()
    if args.result == "fail":
        s["errors"] += 1
        s["retries"] += 1
        state["metrics"]["retries_per_stage"][str(args.stage)] += 1
        # 拦截计数
        if args.script in state["metrics"]["gate_interjections"]:
            state["metrics"]["gate_interjections"][args.script] += 1
    state["metrics"]["total_gates_run"] += 1
    # 注意:不要回退 current_stage,signoff 才会推进
    save_state(root, state)
    print(f"✅ stage {args.stage} ({s['name']}) 记录 gate={args.script} result={args.result}")
    return 0


def cmd_signoff(args) -> int:
    root = Path(args.project_root).resolve()
    try:
        state = load_state(root)
    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        return 1
    if args.stage not in STAGES:
        print(f"❌ stage 必须在 1-9,实际 {args.stage}", file=sys.stderr)
        return 2
    if not is_valid_signoff(args.text):
        print(f"❌ 签字文本不在白名单中(plan §stage-gate)", file=sys.stderr)
        print(f"   只接受 4 句:", file=sys.stderr)
        for p in SIGNOFF_PHRASES:
            print(f"     - {p}", file=sys.stderr)
        print(f"   收到: {args.text!r}", file=sys.stderr)
        return 1
    s = state["stages"][str(args.stage)]
    s["status"] = "✅"
    s["signed_at"] = now_iso()
    s["signoff_text"] = args.text.strip()
    state["metrics"]["total_signoffs"] += 1
    # 推进 current_stage(只前进不后退)
    next_stage = min(args.stage + 1, 9)
    if next_stage > state["current_stage"]:
        state["current_stage"] = next_stage
    save_state(root, state)
    print(f"✅ stage {args.stage} ({s['name']}) 已签字")
    print(f"   signoff: {s['signoff_text']}")
    print(f"   next stage: {state['current_stage']}")
    return 0


def cmd_status(args) -> int:
    root = Path(args.project_root).resolve()
    try:
        state = load_state(root)
    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        return 1
    p = state["project"]
    print(f"📦 Project: {p['name']}")
    print(f"📁 Root:    {p['root']}")
    print(f"🕒 Started: {p['started_at']}")
    print(f"🚦 Current stage: {state['current_stage']} ({STAGE_NAMES.get(state['current_stage'], '?')})")
    print(f"\n📋 Stages:")
    for i in STAGES:
        s = state["stages"][str(i)]
        mark = "→" if i == state["current_stage"] else " "
        gate_info = f"last_gate={s['last_gate']} errors={s['errors']}" if s["last_gate"] else "no gate yet"
        print(f"  {mark} [{i}] {s['status']} {s['name']:8s}  {gate_info}")
    return 0


def cmd_metrics(args) -> int:
    root = Path(args.project_root).resolve()
    try:
        state = load_state(root)
    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        return 1
    m = state["metrics"]

    # --json 模式:只输出 JSON 到 stdout,其它都走 stderr
    out = sys.stderr if args.json else sys.stdout

    def _print(s):
        print(s, file=out)

    _print(f"📊 Metrics:")
    _print(f"\n  1. 总 gate 调用次数:        {m['total_gates_run']}")
    _print(f"  2. 总签字次数:               {m['total_signoffs']}")
    _print(f"\n  3. 各阶段 gate 拦截次数:")
    for g, c in m["gate_interjections"].items():
        if c > 0:
            _print(f"     - {g}: {c}")
    _print(f"\n  4. 各阶段重试次数:")
    for i in STAGES:
        c = m["retries_per_stage"][str(i)]
        if c > 0:
            _print(f"     - stage {i} ({STAGE_NAMES[i]}): {c}")
    _print(f"\n  5. 阶段用时(分钟,已签字的):")
    for i in STAGES:
        d = m["stage_durations_min"][str(i)]
        if d is not None:
            _print(f"     - stage {i} ({STAGE_NAMES[i]}): {d} min")
    if args.json:
        # json 输出(stdout)
        print(json.dumps(m, ensure_ascii=False, indent=2))
    return 0


# ===== self-test =====

def self_test() -> int:
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)

        # 1) init
        rc = _run_subprocess(["init", "--project", "t1", "--project-root", str(root)])
        if rc != 0:
            print("❌ self_test fail: init")
            return 1

        # 2) 二次 init 应 fail(无 --force)
        rc = _run_subprocess(["init", "--project", "t1", "--project-root", str(root)])
        if rc != 1:
            print("❌ self_test fail: 二次 init 应 fail")
            return 1

        # 3) record-gate stage 2 fail
        rc = _run_subprocess(["record-gate", "--stage", "2", "--script", "task-confirm-check", "--result", "fail", "--project-root", str(root)])
        if rc != 0:
            print("❌ self_test fail: record-gate fail")
            return 1

        # 4) signoff stage 2 with non-whitelist text → fail
        rc = _run_subprocess(["signoff", "--stage", "2", "--text", "OK", "--project-root", str(root)])
        if rc != 1:
            print("❌ self_test fail: 非白名单签字应 fail")
            return 1

        # 5) signoff stage 2 with whitelist text → ok
        rc = _run_subprocess(["signoff", "--stage", "2", "--text", "我已全部确认,可以进入下一步", "--project-root", str(root)])
        if rc != 0:
            print("❌ self_test fail: 白名单签字")
            return 1

        # 6) status & metrics should work
        rc = _run_subprocess(["status", "--project-root", str(root)])
        if rc != 0:
            print("❌ self_test fail: status")
            return 1
        rc = _run_subprocess(["metrics", "--project-root", str(root)])
        if rc != 0:
            print("❌ self_test fail: metrics")
            return 1

        # 7) load_state 应反映 stage 2 = ✅,current = 3
        st = load_state(root)
        if st["stages"]["2"]["status"] != "✅":
            print("❌ self_test fail: stage 2 status")
            return 1
        if st["current_stage"] != 3:
            print(f"❌ self_test fail: current_stage 应为 3,实际 {st['current_stage']}")
            return 1
        if st["metrics"]["total_signoffs"] != 1:
            print("❌ self_test fail: total_signoffs")
            return 1
        if st["stages"]["2"]["errors"] != 1:
            print("❌ self_test fail: stage 2 errors (应 1,因 record-gate fail)")
            return 1

    print("✅ analysis-state.py self-test 通过 (5 子命令,7 case)")
    return 0


def _run_subprocess(args_list: list[str]) -> int:
    """self_test 内部:用 subprocess 调用自身。"""
    import subprocess
    cmd = [sys.executable, str(Path(__file__))] + args_list
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 and "self_test fail" not in r.stdout:
        print(f"  stderr={r.stderr}\n  stdout={r.stdout}")
    return r.returncode


# ===== main =====

def main() -> int:
    parser = argparse.ArgumentParser(
        description="9 阶段流程状态持久化(plan §P1-3)",
    )
    parser.add_argument("--self-test", action="store_true", help="运行自检")

    sub = parser.add_subparsers(dest="cmd", required=False)

    def _add_root(p):
        p.add_argument("--project-root", default=".",
                       help="项目根(默认当前目录)")

    p_init = sub.add_parser("init", help="初始化")
    p_init.add_argument("--project", required=True, help="项目名")
    p_init.add_argument("--force", action="store_true", help="覆盖已存在状态")
    _add_root(p_init)

    p_rg = sub.add_parser("record-gate", help="记录 gate 脚本结果")
    p_rg.add_argument("--stage", type=int, required=True, choices=STAGES)
    p_rg.add_argument("--script", required=True, help="gate 脚本名")
    p_rg.add_argument("--result", choices=["pass", "fail"], required=True)
    _add_root(p_rg)

    p_so = sub.add_parser("signoff", help="记录阶段签字")
    p_so.add_argument("--stage", type=int, required=True, choices=STAGES)
    p_so.add_argument("--text", required=True, help="签字文本(必须 4 句白名单之一)")
    _add_root(p_so)

    p_st = sub.add_parser("status", help="显示状态")
    _add_root(p_st)

    p_me = sub.add_parser("metrics", help="输出 5 项度量")
    p_me.add_argument("--json", action="store_true")
    _add_root(p_me)

    args = parser.parse_args()
    if args.self_test:
        return self_test()

    if not args.cmd:
        parser.print_help()
        return 2

    cmd_map = {
        "init": cmd_init,
        "record-gate": cmd_record_gate,
        "signoff": cmd_signoff,
        "status": cmd_status,
        "metrics": cmd_metrics,
    }
    return cmd_map[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())