#!/usr/bin/env bash
# 并行委派 Claude 子代理
# 状态：v1.0 占位 - MVP 阶段功能简化版

set -e

if [ $# -lt 1 ]; then
  echo "用法: bash parallel-delegate.sh <task_file1> [task_file2 ...]"
  echo "  示例: bash parallel-delegate.sh TASK_BRD.md TASK_FSD.md"
  exit 2
fi

echo "⚠️  parallel-delegate.sh 处于 MVP 占位状态"
echo "任务文件:"
for f in "$@"; do
  echo "  - $f"
done
echo ""
echo "v1.0 仅展示任务清单，v1.1 将实现完整的并行执行和监控"
exit 0
