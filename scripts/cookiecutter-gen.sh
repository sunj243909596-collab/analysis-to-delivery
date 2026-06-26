#!/usr/bin/env bash
# 一键生成项目文档骨架（v1.2+）
#
# 用法：
#   bash cookiecutter-gen.sh                              # 交互式生成到当前目录
#   bash cookiecutter-gen.sh --output ./projects/foo      # 指定输出目录
#   bash cookiecutter-gen.sh --name "WMS 收货管理" --slug wms-receive --code WMS-RCV
#   bash cookiecutter-gen.sh --list                       # 只列出模板变量
#   bash cookiecutter-gen.sh --dry-run                    # 不实际生成（cookiecutter 原生）
#   bash cookiecutter-gen.sh --help                       # 帮助
#
# 依赖：
#   - cookiecutter (pip install cookiecutter jinja2_time)
#   - bash 4+
set -e

# ---------- 默认配置 ----------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATE_DIR="$SKILL_DIR/templates/cookiecutter-analysis"
OUTPUT_DIR="$(pwd)"
DRY_RUN=false
LIST_ONLY=false
EXTRA_ARGS=()

# ---------- 帮助 ----------
usage() {
  cat <<EOF
一键生成项目文档骨架（v1.2+）

调用 cookiecutter 把 templates/cookiecutter-analysis/ 渲染到指定目录。

用法：
  bash cookiecutter-gen.sh [选项]

选项：
  --output <dir>      输出目录（默认当前目录）
  --name <name>       项目中文名（默认 "My Project"）
  --slug <slug>       项目目录名（默认从 name 生成）
  --code <code>       项目代号（默认 "MP"）
  --version <ver>     起始版本（默认 "4.0.0"）
  --owner <owner>     项目负责人（默认 "Project Lead"）
  --date <date>       启动日期（默认今天，格式 YYYY-MM-DD）
  --list              只列出 cookiecutter.json 中的变量
  --dry-run           不实际生成（cookiecutter 原生）
  -h, --help          显示此帮助

示例：
  # 交互式生成（cookiecutter 会逐个问）
  bash cookiecutter-gen.sh

  # 一键指定全部参数
  bash cookiecutter-gen.sh \\
      --output ./projects/wms-receive \\
      --name "WMS 收货管理" \\
      --slug wms-receive \\
      --code WMS-RCV \\
      --version 1.0.0 \\
      --owner "张三"

依赖：
  pip install --break-system-packages cookiecutter jinja2_time

退出码：
  0 = 生成成功
  1 = 缺少依赖 / 参数错
  2 = cookiecutter 执行失败
EOF
}

# ---------- 参数解析 ----------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --output) OUTPUT_DIR="$2"; shift 2 ;;
    --name)   EXTRA_ARGS+=("project_name=$2"); shift 2 ;;
    --slug)   EXTRA_ARGS+=("project_slug=$2"); shift 2 ;;
    --code)   EXTRA_ARGS+=("project_code=$2"); shift 2 ;;
    --version) EXTRA_ARGS+=("version=$2"); shift 2 ;;
    --owner)  EXTRA_ARGS+=("owner=$2"); shift 2 ;;
    --date)   EXTRA_ARGS+=("date=$2"); shift 2 ;;
    --list)   LIST_ONLY=true; shift ;;
    --dry-run) DRY_RUN=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "未知参数: $1"; usage; exit 1 ;;
  esac
done

# ---------- 检查 cookiecutter ----------
if ! command -v cookiecutter >/dev/null 2>&1; then
  echo "❌ cookiecutter 未安装"
  echo ""
  echo "请先安装："
  echo "  pip install --break-system-packages cookiecutter jinja2_time"
  echo ""
  echo "或者用 venv："
  echo "  python3 -m venv .venv && source .venv/bin/activate"
  echo "  pip install cookiecutter jinja2_time"
  exit 1
fi

# ---------- 检查模板目录 ----------
if [ ! -d "$TEMPLATE_DIR" ]; then
  echo "❌ 模板目录不存在：$TEMPLATE_DIR"
  exit 1
fi

if [ ! -f "$TEMPLATE_DIR/cookiecutter.json" ]; then
  echo "❌ cookiecutter.json 缺失：$TEMPLATE_DIR/cookiecutter.json"
  exit 1
fi

# ---------- 列出变量 ----------
if [ "$LIST_ONLY" = true ]; then
  echo "📋 cookiecutter 模板变量："
  echo "   模板路径：$TEMPLATE_DIR"
  echo ""
  python3 -c "
import json
with open('$TEMPLATE_DIR/cookiecutter.json', 'r', encoding='utf-8') as f:
    cfg = json.load(f)
for k, v in cfg.items():
    if k.startswith('_'): continue
    print(f'  {k:20s} = {v!r}')
"
  exit 0
fi

# ---------- 确保输出目录存在 ----------
mkdir -p "$OUTPUT_DIR"

# ---------- 调用 cookiecutter ----------
echo "🚀 生成项目骨架..."
echo "   模板：$TEMPLATE_DIR"
echo "   输出：$OUTPUT_DIR"
echo ""

CC_ARGS=(--output-dir "$OUTPUT_DIR" --no-input)
if [ "$DRY_RUN" = true ]; then
  CC_ARGS+=(--dry-run)
fi
CC_ARGS+=("${EXTRA_ARGS[@]}")

set +e
cookiecutter "$TEMPLATE_DIR" "${CC_ARGS[@]}"
RC=$?
set -e

if [ $RC -ne 0 ]; then
  echo ""
  echo "❌ cookiecutter 执行失败（exit=$RC）"
  exit 2
fi

echo ""
echo "✅ 项目骨架已生成"
echo ""
echo "📝 下一步："
echo "   1. 进入项目目录：cd $OUTPUT_DIR/<project_slug>"
echo "   2. 填写 TASK_CONFIRM.md（阶段 2：需求确认）"
echo "   3. 按编号顺序填充文档"
echo "   4. 文档写完后跑格式校验："
echo "        python3 $SKILL_DIR/scripts/doc-validate.py . --level P1"
