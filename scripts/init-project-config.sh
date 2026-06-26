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
# Canonical 模板：仓库根 paths/
CANONICAL_TEMPLATE_DIR="$SKILL_DIR/paths"
# Legacy 模板：仅供 v1.1 既有项目回退（仍可读,但新项目不应再用）
LEGACY_TEMPLATE_DIR="$SKILL_DIR/templates/project-config"

# Canonical 输出位置(默认):<project>/paths/
# Legacy 输出位置:<project>/{name}.md
# 通过 --legacy 切换到 legacy 输出
MODE="canonical"
FORCE=false
TARGET=""

# ---------- canonical 模板与 legacy 模板的对应关系 ----------
# format: <canonical_basename>|<legacy_basename>
PATH_FILES=(
  "knowledge-path.md|knowledge-path.md"
  "compliance-path.md|compliance-path.md"
  "tech-stack-path.md|tech-stack-path.md"
  "doc-naming-path.md|doc-naming.md"
)

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
项目级 config 一键初始化（v4.0.0 / rules-and-paths refactor）

默认写到 canonical 位置 <项目根>/paths/*.md。
用 --legacy 写到兼容位置 <项目根>/*.md（旧项目）。

用法：
  bash init-project-config.sh [选项] <项目根目录>

选项：
  --force          覆盖已存在的文件
  --legacy         写到兼容位置（项目根 *.md），仅用于 v1.1 既有项目
  -h, --help       显示此帮助

示例：
  bash init-project-config.sh /path/to/your-project
  bash init-project-config.sh .               # 当前目录
  bash init-project-config.sh --force ./my-app
  bash init-project-config.sh --legacy /path/to/old-project

默认会在 <项目根>/paths/ 下生成 4 个文件：
  knowledge-path.md
  compliance-path.md
  tech-stack-path.md
  doc-naming-path.md

每个文件都带示例注释，填入你项目的真实路径/规范即可。
EOF
}

# ---------- 参数解析 ----------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --force) FORCE=true; shift ;;
    --legacy) MODE="legacy"; shift ;;
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

# ---------- 选择模板目录 ----------
if [ "$MODE" = "legacy" ]; then
  TEMPLATE_DIR="$LEGACY_TEMPLATE_DIR"
else
  TEMPLATE_DIR="$CANONICAL_TEMPLATE_DIR"
fi

# ---------- 校验模板 ----------
if [ ! -d "$TEMPLATE_DIR" ]; then
  err "找不到模板目录：$TEMPLATE_DIR"
  err "请确认 skill 已正确安装"
  exit 1
fi

info "目标项目根：$TARGET"
info "模板目录：  $TEMPLATE_DIR"
info "模式：      $MODE"
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

# ---------- 准备输出目录 ----------
if [ "$MODE" = "canonical" ]; then
  OUT_DIR="$TARGET/paths"
  mkdir -p "$OUT_DIR"
fi

# ---------- 复制文件 ----------
GENERATED=0
SKIPPED=0
for entry in "${PATH_FILES[@]}"; do
  IFS='|' read -r canonical_name legacy_name <<< "$entry"
  src="$TEMPLATE_DIR/$canonical_name"
  if [ "$MODE" = "canonical" ]; then
    dst="$TARGET/paths/$canonical_name"
  else
    dst="$TARGET/$legacy_name"
  fi

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
if [ "$MODE" = "canonical" ]; then
  echo "  1. 编辑 4 个文件，填入你项目的真实路径/规范"
  echo "     $TARGET/paths/knowledge-path.md"
  echo "     $TARGET/paths/compliance-path.md"
  echo "     $TARGET/paths/tech-stack-path.md"
  echo "     $TARGET/paths/doc-naming-path.md"
else
  echo "  1. 编辑 4 个文件，填入你项目的真实路径/规范"
  echo "     $TARGET/knowledge-path.md"
  echo "     $TARGET/compliance-path.md"
  echo "     $TARGET/tech-stack-path.md"
  echo "     $TARGET/doc-naming.md"
  echo ""
  warn "  提示：legacy 模式仅用于 v1.1 既有项目。新项目请改用 --canonical"
fi
echo ""
echo "  2. 把它们 commit 到项目 git 仓库"
echo ""
echo "  3. 调用 skill 开干："
echo "     /analysis-to-delivery"
echo ""
echo "  4. 完整文档："
echo "     cat $SKILL_DIR/SKILL.md"
echo "     cat $SKILL_DIR/SPEC.md"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
