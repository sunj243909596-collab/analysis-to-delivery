#!/usr/bin/env bash
# ASCII 流程图 → Mermaid → SVG/PNG 渲染器(v3.0 工具链)
#
# 用法:
#   bash flow-export.sh <input.txt> [svg|png] [output_dir]
#   bash flow-export.sh --all examples/  svg  ./rendered
#   bash flow-export.sh --batch examples/02-saas-dashboard/
#
# 依赖:
#   - Python 3.8+(调用 flow-to-mermaid.py)
#   - mermaid-cli(mmdc):npm install -g @mermaid-js/mermaid-cli
#
# 注意:
#   mmdc 首次运行会下载 puppeteer + Chromium(~300MB),耐心等待。
#   在 CI 环境可设置 PUPPETEER_SKIP_DOWNLOAD=true 提前下载后复用。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---------- 默认配置 ----------
FORMAT="svg"
OUTPUT_DIR=""
BATCH_MODE=false
ALL_MODE=false

# ---------- 颜色 ----------
if [ -t 1 ]; then
  RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
else
  RED=''; GREEN=''; YELLOW=''; CYAN=''; NC=''
fi

# ---------- 帮助 ----------
usage() {
  cat <<EOF
ASCII 流程图渲染器(v3.0)

用法:
  bash flow-export.sh <input.txt> [svg|png] [output_dir]
  bash flow-export.sh --batch <dir> [svg|png] [output_dir]
  bash flow-export.sh --all <dir> [svg|png] [output_dir]

参数:
  input.txt       单个 ASCII 流程图文件
  --batch <dir>   批量处理目录下所有 业务流程图-*.txt
  --all <dir>     递归处理目录下所有 .txt 流程图
  svg|png         输出格式(默认 svg)
  output_dir      输出目录(默认 <input>/rendered/)

示例:
  bash flow-export.sh examples/02-saas-dashboard/业务流程图-订单状态流转.txt
  bash flow-export.sh examples/02-saas-dashboard/业务流程图-订单状态流转.txt png
  bash flow-export.sh --batch examples/02-saas-dashboard/ png ./diagrams

依赖:
  mmdc(mermaid-cli):npm install -g @mermaid-js/mermaid-cli
EOF
}

# ---------- 依赖检查 ----------
check_deps() {
  local missing=0
  if ! command -v python3 >/dev/null 2>&1; then
    echo -e "${RED}❌ python3 未安装${NC}" >&2
    missing=1
  fi
  if ! command -v mmdc >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  mmdc(mermaid-cli)未安装${NC}" >&2
    echo "  安装方法:npm install -g @mermaid-js/mermaid-cli" >&2
    missing=1
  fi
  return $missing
}

# ---------- 参数解析 ----------
POSITIONAL=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --batch) BATCH_MODE=true; shift; POSITIONAL+=("$1"); shift ;;
    --all) ALL_MODE=true; shift; POSITIONAL+=("$1"); shift ;;
    svg|png) FORMAT="$1"; shift ;;
    -*) echo -e "${RED}❌ 未知参数:$1${NC}" >&2; usage; exit 2 ;;
    *) POSITIONAL+=("$1"); shift ;;
  esac
done

if [ ${#POSITIONAL[@]} -eq 0 ]; then
  usage
  exit 1
fi

INPUT="${POSITIONAL[0]}"
if [ ${#POSITIONAL[@]} -ge 2 ]; then
  OUTPUT_DIR="${POSITIONAL[1]}"
fi

# ---------- 准备 ----------
check_deps || {
  echo -e "${RED}❌ 缺少依赖,无法继续${NC}" >&2
  exit 1
}

# ---------- 处理单个文件 ----------
process_one() {
  local txt="$1"
  local mmd_out
  local rendered_out

  # 1. .txt → .mmd
  mmd_out="$(dirname "$txt")/$(basename "$txt" .txt).mmd"
  echo -e "${CYAN}▶${NC} 转换:$txt → $mmd_out"
  python3 "$SCRIPT_DIR/flow-to-mermaid.py" "$txt"

  # 2. .mmd → .svg / .png
  local out_dir
  if [ -n "$OUTPUT_DIR" ]; then
    out_dir="$OUTPUT_DIR"
  else
    out_dir="$(dirname "$txt")/rendered"
  fi
  mkdir -p "$out_dir"
  rendered_out="$out_dir/$(basename "$txt" .txt).$FORMAT"

  echo -e "${CYAN}▶${NC} 渲染:$mmd_out → $rendered_out"
  if mmdc -i "$mmd_out" -o "$rendered_out" -t neutral -b transparent 2>/dev/null; then
    echo -e "${GREEN}✅${NC} 完成:$rendered_out"
  else
    echo -e "${YELLOW}⚠️${NC}  mmdc 渲染失败(可能是浏览器依赖问题),跳过:$rendered_out"
    return 1
  fi
}

# ---------- 入口 ----------
if [ "$BATCH_MODE" = true ] || [ "$ALL_MODE" = true ]; then
  if [ ! -d "$INPUT" ]; then
    echo -e "${RED}❌ 目录不存在:$INPUT${NC}" >&2
    exit 1
  fi
  if [ "$ALL_MODE" = true ]; then
    mapfile -t files < <(find "$INPUT" -name "业务流程图-*.txt" -o -name "*flow*.txt" 2>/dev/null | sort)
  else
    mapfile -t files < <(find "$INPUT" -maxdepth 2 -name "业务流程图-*.txt" 2>/dev/null | sort)
  fi
  if [ ${#files[@]} -eq 0 ]; then
    echo -e "${YELLOW}⚠️${NC} 未找到 业务流程图-*.txt 文件:$INPUT"
    exit 0
  fi
  echo -e "${CYAN}▶${NC} 批量处理 ${#files[@]} 个文件,格式=$FORMAT"
  for f in "${files[@]}"; do
    process_one "$f"
  done
  echo ""
  echo -e "${GREEN}🎉 完成:共处理 ${#files[@]} 个文件${NC}"
  if [ -n "$OUTPUT_DIR" ]; then
    echo -e "  输出目录:${CYAN}$OUTPUT_DIR${NC}"
  fi
else
  if [ ! -f "$INPUT" ]; then
    echo -e "${RED}❌ 文件不存在:$INPUT${NC}" >&2
    exit 1
  fi
  process_one "$INPUT"
fi