#!/usr/bin/env bash
# Analysis to Delivery 一键安装脚本
# 用法：
#   curl -fsSL https://raw.githubusercontent.com/BlueprintOS/analysis-to-delivery/main/install.sh | bash
#   bash install.sh                   # 安装到默认目录
#   bash install.sh --dry-run         # 只检查不安装
#   bash install.sh --target DIR      # 安装到指定目录
#   bash install.sh --agent codex     # 安装到指定 agent 的默认 skills 目录
#   bash install.sh --uninstall       # 卸载
set -e

# ---------- 默认配置 ----------
REPO="${ANALYSIS_TO_DELIVERY_REPO:-https://github.com/BlueprintOS/analysis-to-delivery.git}"
SKILL_NAME="analysis-to-delivery"
VERSION="${VERSION:-main}"
DRY_RUN=false
TARGET=""
UNINSTALL=false
AGENT="${ANALYSIS_TO_DELIVERY_AGENT:-auto}"

# ---------- 参数解析 ----------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true; shift ;;
    --target) TARGET="$2"; shift 2 ;;
    --agent) AGENT="$2"; shift 2 ;;
    --uninstall) UNINSTALL=true; shift ;;
    --repo) REPO="$2"; shift 2 ;;
    --version) VERSION="$2"; shift 2 ;;
    -h|--help)
      sed -n '2,12p' "$0" | sed 's/^# \?//'
      exit 0
      ;;
    *) echo "❌ 未知参数: $1"; exit 1 ;;
  esac
done

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

# ---------- 卸载 ----------
if [ "$UNINSTALL" = true ]; then
  for base in "$HOME/.claude/skills" "$HOME/.hermes/skills" "$HOME/.codex/skills" "$HOME/.opencode/skills"; do
    target="$base/$SKILL_NAME"
    if [ -d "$target" ]; then
      if [ "$DRY_RUN" = true ]; then
        info "将删除 $target"
      else
        rm -rf "$target"
        ok "已删除 $target"
      fi
    fi
  done
  exit 0
fi

# ---------- 检测目标目录 ----------
detect_target() {
  if [ -n "$TARGET" ]; then
    echo "$TARGET"
    return
  fi

  case "$AGENT" in
    claude) echo "$HOME/.claude/skills/$SKILL_NAME"; return ;;
    hermes) echo "$HOME/.hermes/skills/$SKILL_NAME"; return ;;
    codex) echo "${CODEX_HOME:-$HOME/.codex}/skills/$SKILL_NAME"; return ;;
    opencode) echo "${OPENCODE_HOME:-$HOME/.opencode}/skills/$SKILL_NAME"; return ;;
    auto) ;;
    *)
      err "未知 agent: $AGENT"
      err "可选: auto / claude / hermes / codex / opencode,或用 --target 指定目录"
      exit 1
      ;;
  esac

  for base in \
    "$HOME/.claude/skills" \
    "$HOME/.hermes/skills" \
    "${CODEX_HOME:-$HOME/.codex}/skills" \
    "${OPENCODE_HOME:-$HOME/.opencode}/skills"; do
    if [ -d "$base" ]; then
      echo "$base/$SKILL_NAME"
      return
    fi
  done

  for home_dir in "$HOME/.claude" "$HOME/.hermes" "${CODEX_HOME:-$HOME/.codex}" "${OPENCODE_HOME:-$HOME/.opencode}"; do
    if [ -d "$home_dir" ]; then
      echo "$home_dir/skills/$SKILL_NAME"
      return
    fi
  done

  err "未找到已知 agent 目录(~/.claude / ~/.hermes / ~/.codex / ~/.opencode)"
  err "请先安装对应 agent,或用 --agent / --target 指定目录"
  exit 1
}

TARGET_DIR=$(detect_target)
PARENT_DIR=$(dirname "$TARGET_DIR")

info "目标目录：$TARGET_DIR"
info "来源仓库：$REPO"
info "版本：$VERSION"

# ---------- 校验依赖 ----------
command -v git >/dev/null 2>&1 || { err "需要 git，请先安装"; exit 1; }

# ---------- Dry run ----------
if [ "$DRY_RUN" = true ]; then
  ok "Dry run 通过：以上配置可以正常安装"
  exit 0
fi

# ---------- 确保父目录存在 ----------
mkdir -p "$PARENT_DIR"

# ---------- 克隆或更新 ----------
if [ -d "$TARGET_DIR/.git" ]; then
  info "检测到已安装版本，更新中..."
  git -C "$TARGET_DIR" fetch --depth 1 origin "$VERSION" 2>/dev/null || \
    git -C "$TARGET_DIR" pull --depth 1
  ok "已更新到最新版本"
elif [ -d "$TARGET_DIR" ]; then
  warn "$TARGET_DIR 已存在但不是 git 仓库"
  warn "请手动处理：rm -rf $TARGET_DIR 后重试"
  exit 1
else
  info "克隆仓库中..."
  if ! git clone --depth 1 --branch "$VERSION" "$REPO" "$TARGET_DIR" 2>/dev/null; then
    warn "分支 $VERSION 不存在，回退到默认分支"
    git clone --depth 1 "$REPO" "$TARGET_DIR"
  fi
  ok "克隆完成"
fi

# ---------- 校验安装 ----------
if [ ! -f "$TARGET_DIR/SKILL.md" ]; then
  err "安装校验失败：$TARGET_DIR/SKILL.md 不存在"
  exit 1
fi

ok "安装成功：$TARGET_DIR"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📚 下一步："
echo ""
echo "  1. 在支持 slash command 的 agent 中调用："
echo "     /analysis-to-delivery 或 /analysis-delivery-workflow"
echo ""
echo "  2. 或直接告诉你的 agent："
echo "     \"使用 analysis-to-delivery 分析 XXX 需求\""
echo ""
echo "  3. 查阅 adapter 文档："
echo "     ls $TARGET_DIR/docs/adapters"
echo ""
echo "  4. 查阅主文档："
echo "     cat $TARGET_DIR/README.md"
echo "     cat $TARGET_DIR/plan.md"
echo "     cat $TARGET_DIR/SPEC.md"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
