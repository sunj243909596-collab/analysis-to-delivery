#!/usr/bin/env bash
# Analysis to Delivery — 项目级 config 一键初始化
# 用法：
#   bash init-project-config.sh /path/to/your-project
#   bash init-project-config.sh .                       # 当前目录
#   bash init-project-config.sh                         # 交互式询问
#   bash init-project-config.sh --force /path/to/project  # 覆盖已存在的文件
set -e

# ---------- 默认配置 ----------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATE_DIR="$SKILL_DIR/templates/project-config"

FILES=(
  "knowledge-path.md"
  "compliance-path.md"
  "tech-stack-path.md"
  "doc-naming.md"
)

TARGET=""
FORCE=false

# ---------- 颜色 ----------
if [ -t 1 ]; then
  RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
  BLUE='\033[0;34m'; NC='\033[0m'
else
  RED=''; GREEN=''; YELLOW=''; BLUE=''; NC=''
fi

info()  { echo -e "${BLUE}ℹ${NC} $1"; }
ok()    { echo -e "${GREEN}✅${NC} $1"; }
warn()  { echo -e "${YELLOW}⚠${NC}  $1"; }
err()   { echo -e "${RED}❌${NC} $1"; }

# ---------- 帮助 ----------
usage() {
  cat <<EOF
项目级 config 一键初始化（v1.1+）

用法：
  bash init-project-config.sh [选项] <项目根目录>

选项：
  --force          覆盖已存在的 *-path.md 文件
  -h, --help       显示此帮助

示例：
  bash init-project-config.sh /path/to/your-project
  bash init-project-config.sh .               # 当前目录
  bash init-project-config.sh --force ./my-app

会在 <项目根目录> 下生成 4 个文件：
  knowledge-path.md
  compliance-path.md
  tech-stack-path.md
  doc-naming.md

每个文件都带示例注释，填入你项目的真实路径/规范即可。
EOF
}

# ---------- 参数解析 ----------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --force) FORCE=true; shift ;;
    -h|--help) usage; exit 0 ;;
    -*) err "未知参数: $1"; usage; exit 1 ;;
    *) TARGET="$1"; shift ;;
  esac
done

# ---------- 交互式询问 ----------
if [ -z "$TARGET" ]; then
  if [ -t 0 ]; then
    read -rp "请输入项目根目录路径（直接回车用当前目录）: " TARGET
    TARGET="${TARGET:-.}"
  else
    err "缺少参数：请指定项目根目录"
    usage
    exit 1
  fi
fi

# ---------- 规范化路径 ----------
TARGET="$(cd "$TARGET" 2>/dev/null && pwd || echo "$TARGET")"

# ---------- 校验模板 ----------
if [ ! -d "$TEMPLATE_DIR" ]; then
  err "找不到模板目录：$TEMPLATE_DIR"
  err "请确认 skill 已正确安装"
  exit 1
fi

info "目标项目根：$TARGET"
info "模板目录：  $TEMPLATE_DIR"
echo ""

# ---------- 确保目标存在 ----------
if [ ! -d "$TARGET" ]; then
  warn "目标目录不存在：$TARGET"
  if [ -t 0 ]; then
    read -rp "是否创建？[y/N] " CONFIRM
    case "$CONFIRM" in
      y|Y|yes|YES) mkdir -p "$TARGET"; ok "已创建 $TARGET" ;;
      *) err "已取消"; exit 1 ;;
    esac
  else
    err "目标目录不存在且非交互模式，请先创建"
    exit 1
  fi
fi

# ---------- 复制文件 ----------
GENERATED=0
SKIPPED=0
for fname in "${FILES[@]}"; do
  src="$TEMPLATE_DIR/$fname"
  dst="$TARGET/$fname"

  if [ ! -f "$src" ]; then
    err "模板缺失：$src"
    exit 1
  fi

  if [ -f "$dst" ]; then
    if [ "$FORCE" = true ]; then
      cp "$src" "$dst"
      ok "[覆盖] $dst"
      GENERATED=$((GENERATED + 1))
    else
      warn "[跳过] $dst 已存在（用 --force 覆盖）"
      SKIPPED=$((SKIPPED + 1))
    fi
  else
    cp "$src" "$dst"
    ok "[生成] $dst"
    GENERATED=$((GENERATED + 1))
  fi
done

echo ""
ok "完成：生成 $GENERATED 个 / 跳过 $SKIPPED 个"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📚 下一步："
echo ""
echo "  1. 编辑 4 个文件，填入你项目的真实路径/规范"
echo "     $TARGET/knowledge-path.md"
echo "     $TARGET/compliance-path.md"
echo "     $TARGET/tech-stack-path.md"
echo "     $TARGET/doc-naming.md"
echo ""
echo "  2. 把它们 commit 到项目 git 仓库"
echo ""
echo "  3. 调用 skill 开干："
echo "     /analysis-to-delivery"
echo ""
echo "  4. 完整文档："
echo "     cat $SKILL_DIR/SKILL.md"
echo "     cat $SKILL_DIR/SPEC.md#65-项目级配置-v11"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
