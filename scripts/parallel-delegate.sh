#!/usr/bin/env bash
# 并行委派 Claude CLI 子任务（v1.3-dev）
set -euo pipefail

JOBS=3
OUT_DIR="delegate-logs"
TIMEOUT=""
DRY_RUN=false
TASKS=()

usage() {
  cat <<EOF
并行委派 Claude CLI 子任务

用法：
  bash parallel-delegate.sh [选项] <task_file1> [task_file2 ...]

选项：
  --jobs <n>       并发数（默认 3）
  --out-dir <dir>  日志目录（默认 delegate-logs）
  --timeout <sec>  单任务超时秒数（依赖 timeout 命令）
  --dry-run        只打印将执行的任务
  -h, --help       显示帮助

要求：本机存在 claude 命令。每个任务文件应包含完整委派提示词。
退出码：0 全部成功；1 有任务失败；2 参数或依赖错误。
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --jobs) JOBS="$2"; shift 2 ;;
    --out-dir) OUT_DIR="$2"; shift 2 ;;
    --timeout) TIMEOUT="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    -h|--help) usage; exit 0 ;;
    -*) echo "未知参数: $1" >&2; usage; exit 2 ;;
    *) TASKS+=("$1"); shift ;;
  esac
done

if [[ ${#TASKS[@]} -eq 0 ]]; then
  usage
  exit 2
fi

if ! [[ "$JOBS" =~ ^[0-9]+$ ]] || [[ "$JOBS" -lt 1 ]]; then
  echo "❌ --jobs 必须是正整数" >&2
  exit 2
fi

for task in "${TASKS[@]}"; do
  if [[ ! -f "$task" ]]; then
    echo "❌ 任务文件不存在: $task" >&2
    exit 2
  fi
done

if [[ "$DRY_RUN" = false ]] && ! command -v claude >/dev/null 2>&1; then
  echo "❌ 未找到 claude 命令；请安装 Claude CLI，或先用 --dry-run 检查任务" >&2
  exit 2
fi

mkdir -p "$OUT_DIR"

run_task() {
  local task="$1"
  local base log status
  base=$(basename "$task")
  base="${base%.*}"
  log="$OUT_DIR/${base}.log"
  status="$OUT_DIR/${base}.status"
  if [[ "$DRY_RUN" = true ]]; then
    echo "DRY RUN: claude < $task > $log"
    echo "dry-run" > "$status"
    return 0
  fi
  echo "▶ $task -> $log"
  if [[ -n "$TIMEOUT" ]]; then
    timeout "$TIMEOUT" claude < "$task" > "$log" 2>&1
  else
    claude < "$task" > "$log" 2>&1
  fi
  echo "ok" > "$status"
}

active=0
fail=0
pids=()
for task in "${TASKS[@]}"; do
  (run_task "$task") &
  pids+=("$!")
  active=$((active + 1))
  if [[ "$active" -ge "$JOBS" ]]; then
    if ! wait "${pids[0]}"; then fail=$((fail + 1)); fi
    pids=("${pids[@]:1}")
    active=$((active - 1))
  fi
done
for pid in "${pids[@]}"; do
  if ! wait "$pid"; then fail=$((fail + 1)); fi
done

if [[ "$fail" -gt 0 ]]; then
  echo "❌ 并行委派完成，但有 $fail 个任务失败。日志目录: $OUT_DIR"
  exit 1
fi

echo "✅ 并行委派完成：${#TASKS[@]} 个任务。日志目录: $OUT_DIR"
