#!/usr/bin/env bash
# Analysis to Delivery — Skill 自检脚本（v1.2+）
#
# 装完 skill 后跑一遍，立即知道装得对不对。
#
# 用法：
#   bash smoke-test.sh                     # 默认识别当前目录
#   bash smoke-test.sh /path/to/skill     # 指定 skill 根
#   bash smoke-test.sh --verbose          # 详细输出
#   bash smoke-test.sh --json             # JSON 输出（机器可读）
#   bash smoke-test.sh --help             # 帮助
set -e

# ---------- 默认配置 ----------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR=""
VERBOSE=false
JSON_MODE=false

# ---------- 颜色 ----------
if [ -t 1 ]; then
  RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
  BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'
else
  RED=''; GREEN=''; YELLOW=''; BLUE=''; CYAN=''; NC=''
fi

pass_count=0
warn_count=0
fail_count=0

json_results='[]'

# ---------- 帮助 ----------
usage() {
  cat <<EOF
Skill 自检脚本（v1.2+）

用法：
  bash smoke-test.sh [选项] [<skill 根目录>]

选项：
  --verbose          详细输出（每项检查都打印）
  --json             JSON 输出（机器可读，适合 CI）
  -h, --help         显示此帮助

示例：
  bash smoke-test.sh                     # 检当前目录
  bash smoke-test.sh ~/.claude/skills/analysis-to-delivery
  bash smoke-test.sh --json              # CI 集成

退出码：
  0 = 全部通过
  1 = 有警告（可继续，但建议关注）
  2 = 有错误（需修复）
EOF
}

# ---------- 参数解析 ----------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --verbose) VERBOSE=true; shift ;;
    --json) JSON_MODE=true; shift ;;
    -h|--help) usage; exit 0 ;;
    -*) echo "未知参数: $1"; usage; exit 2 ;;
    *) SKILL_DIR="$1"; shift ;;
  esac
done

# 默认 skill 目录
if [ -z "$SKILL_DIR" ]; then
  SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
fi

# record 始终定义（OK/warn/err 会调用它）
record() {
  # record "name" "status" "msg"
  local name="$1" status="$2" msg="$3"
  if [ "$JSON_MODE" = true ]; then
    json_results=$(echo "$json_results" | python3 -c "
import json, sys
arr = json.loads(sys.stdin.read())
arr.append({'check': '''$name''', 'status': '$status', 'message': '''$msg'''})
print(json.dumps(arr, ensure_ascii=False))
" 2>/dev/null) || true
  fi
}

# ---------- 工具函数 ----------
if [ "$JSON_MODE" = true ]; then
  ok()    { pass_count=$((pass_count+1)); record "${1}" "pass" ""; }
  warn()  { warn_count=$((warn_count+1)); record "${1}" "warn" ""; }
  err()   { fail_count=$((fail_count+1)); record "${1}" "fail" ""; }
  info()  { :; }
  section() { :; }
else
  ok()    { echo -e "  ${GREEN}✅${NC} $1"; pass_count=$((pass_count+1)); record "${1}" "pass" ""; }
  warn()  { echo -e "  ${YELLOW}⚠️ ${NC} $1"; warn_count=$((warn_count+1)); record "${1}" "warn" ""; }
  err()   { echo -e "  ${RED}❌${NC} $1"; fail_count=$((fail_count+1)); record "${1}" "fail" ""; }
  info()  { echo -e "  ${CYAN}ℹ${NC}  $1"; }
  section() { echo -e "\n${BLUE}━━━ $1 ━━━${NC}"; }
fi

# ---------- 检查函数 ----------
check_tool() {
  local name="$1" cmd="$2" min_version="$3"
  if command -v "$cmd" >/dev/null 2>&1; then
    if [ -n "$min_version" ]; then
      local ver
      ver=$("$cmd" --version 2>&1 | head -1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
      if [ -n "$ver" ]; then
        local major minor
        IFS='.' read -r major minor <<< "$ver"
        local need_major need_minor
        IFS='.' read -r need_major need_minor <<< "$min_version"
        if [ "$major" -gt "$need_major" ] || { [ "$major" -eq "$need_major" ] && [ "$minor" -ge "$need_minor" ]; }; then
          ok "$name 已安装 ($cmd $ver)"
        else
          warn "$name 版本过低（$ver < $min_version），建议升级"
        fi
      else
        ok "$name 已安装"
      fi
    else
      ok "$name 已安装"
    fi
  else
    err "$name 未安装（需要 $cmd）"
  fi
}

check_file() {
  local rel="$1" required="${2:-true}"
  local path="$SKILL_DIR/$rel"
  if [ -f "$path" ]; then
    ok "$rel 存在"
  else
    if [ "$required" = "true" ]; then
      err "$rel 缺失（必需）"
    else
      warn "$rel 缺失（可选）"
    fi
  fi
}

check_dir() {
  local rel="$1" required="${2:-true}"
  local path="$SKILL_DIR/$rel"
  if [ -d "$path" ]; then
    ok "$rel/ 目录存在"
  else
    if [ "$required" = "true" ]; then
      err "$rel/ 目录缺失（必需）"
    else
      warn "$rel/ 目录缺失（可选）"
    fi
  fi
}

check_exec() {
  local rel="$1"
  local path="$SKILL_DIR/$rel"
  if [ -f "$path" ]; then
    if [ -x "$path" ]; then
      ok "$rel 可执行"
    else
      warn "$rel 存在但不可执行（建议 chmod +x）"
    fi
  fi
}

check_count() {
  local dir="$1" pattern="$2" expected="$3" label="$4"
  local actual
  actual=$(find "$SKILL_DIR/$dir" -maxdepth 1 -name "$pattern" 2>/dev/null | wc -l)
  if [ "$actual" -ge "$expected" ]; then
    ok "$label（$actual 个，期望 ≥ $expected）"
  else
    warn "$label 不全（$actual 个，期望 ≥ $expected）"
  fi
}

# ---------- 开始检查 ----------
[ "$JSON_MODE" = false ] && echo -e "${BLUE}🔍 Analysis to Delivery — Skill 自检${NC}"
[ "$JSON_MODE" = false ] && echo -e "目标：${CYAN}$SKILL_DIR${NC}"

# 1. skill 根目录存在
section "1. 基础目录"
if [ -d "$SKILL_DIR" ]; then
  ok "skill 根目录存在"
else
  err "skill 根目录不存在：$SKILL_DIR"
  [ "$JSON_MODE" = true ] && echo "$json_results"
  exit 2
fi

# 2. 系统工具
section "2. 系统工具"
check_tool "git" git
check_tool "bash" bash
check_tool "python3" python3 "3.8"

# 3. 核心文档
section "3. 核心文档"
check_file "SKILL.md"
check_file "SPEC.md"
check_file "plan.md"
check_file "README.md"
check_file "CHANGELOG.md"
check_file "LICENSE"
check_file "install.sh"

# 4. templates 完整性
section "4. 模板完整性"
check_dir "templates"
check_count "templates" "*.md" 12 "通用模板"
check_dir "templates/project-config"
check_count "templates/project-config" "*.md" 4 "项目级 config 模板"
check_dir "templates/cookiecutter-analysis"
check_file "templates/cookiecutter-analysis/cookiecutter.json"

# 5. scripts 可执行性
section "5. 脚本"
check_dir "scripts"
check_exec "install.sh"
check_exec "init-project-config.sh"
check_exec "parallel-delegate.sh"
check_exec "smoke-test.sh"
check_exec "cookiecutter-gen.sh"
for f in field-alignment-check.py full-qa-audit.py sql-dialect-check.py postprocess_prd_html.py doc-validate.py; do
  check_file "scripts/$f" false
done

# 6. skills(26 个独立 skill)
section "6. skills 结构(v1.4+ 拆分)"
check_dir "skills"
check_dir "skills/ask-delivery"
check_dir "skills/using-superpowers"
check_dir "skills/user-invoked"
check_dir "skills/orchestration"
check_dir "skills/orchestration/analysis-delivery-workflow"
check_dir "skills/orchestration/development"
check_dir "skills/disciplines"
# 数量校验(用 find 递归查 SKILL.md,因为 check_count 只查顶层)
for d in ask-delivery:1 using-superpowers:1 user-invoked:9 orchestration:8 orchestration/development:7 disciplines:7; do
  dir="${d%:*}"
  expect="${d#*:}"
  actual=$(find "$SKILL_DIR/skills/$dir" -name "SKILL.md" 2>/dev/null | wc -l)
  if [ "$actual" -eq "$expect" ]; then
    ok "skills/$dir: $actual 个 SKILL.md(期望 $expect)"
  else
    err "skills/$dir: $actual 个 SKILL.md(期望 $expect)"
  fi
done
total=$(find "$SKILL_DIR/skills" -name "SKILL.md" 2>/dev/null | wc -l)
if [ "$total" -eq 26 ]; then
  ok "skills/ 总数 26 个"
else
  err "skills/ 总数 $total 个(期望 26)"
fi
# references 已迁移到 disciplines/
if [ -d "$SKILL_DIR/references" ]; then
  warn "references/ 仍存在(应已迁移到 skills/disciplines/)"
else
  ok "references/ 已迁移到 skills/disciplines/"
fi

# 7. config（skill 级 fallback）
section "7. skill 级 config"
check_dir "config"
check_dir "config/compliance"
check_dir "config/tech-stack"
check_file "config/compliance/template.md"
check_file "config/tech-stack/template.md"

# 8. examples
section "8. 示例"
check_dir "examples"
brd_count=$(find "$SKILL_DIR/examples" -name "*BRD*.md" -type f 2>/dev/null | wc -l)
if [ "$brd_count" -ge 1 ]; then
  ok "examples 含 BRD（$brd_count 个）"
else
  warn "examples 不含 BRD（建议补）"
fi

# 9. SKILL.md YAML frontmatter
section "9. SKILL.md 元数据"
if [ -f "$SKILL_DIR/SKILL.md" ]; then
  if head -20 "$SKILL_DIR/SKILL.md" | grep -qE '^---$' && head -20 "$SKILL_DIR/SKILL.md" | grep -qE '^name:'; then
    ok "SKILL.md 含 YAML frontmatter"
  else
    warn "SKILL.md 缺 YAML frontmatter 或格式不对"
  fi
  local_name=$(head -20 "$SKILL_DIR/SKILL.md" | grep -E '^name:' | head -1 | awk '{print $2}')
  if [ -n "$local_name" ]; then
    ok "name 字段：$local_name"
  else
    warn "name 字段缺失"
  fi
fi

# 10. 文档编号无冲突
section "10. 文档结构"
if [ -d "$SKILL_DIR/templates" ]; then
  dups=$(find "$SKILL_DIR/templates" -maxdepth 1 -name "0?-*.md" | awk -F/ '{print $NF}' | awk -F'-' '{print $1}' | sort | uniq -d)
  if [ -z "$dups" ]; then
    ok "templates/ 编号无冲突"
  else
    err "templates/ 编号冲突：$dups"
  fi
fi

# 11. 链接抽样（SKILL.md 内链接）
section "11. 内部链接（抽样）"
if [ -f "$SKILL_DIR/SKILL.md" ]; then
  link_count=0
  link_ok=0
  link_bad=0
  # 用 grep -oE 提取所有 markdown 链接
  while IFS= read -r link_path; do
    [ -z "$link_path" ] && continue
    # 跳过 http(s) 和纯锚点
    case "$link_path" in
      http://*|https://*|\#*) continue ;;
    esac
    link_count=$((link_count+1))
    # 去掉 anchor
    file_only="${link_path%%#*}"
    full="$SKILL_DIR/$file_only"
    if [ -f "$full" ] || [ -d "$full" ]; then
      link_ok=$((link_ok+1))
    else
      link_bad=$((link_bad+1))
      [ "$VERBOSE" = true ] && warn "  链接失效：$link_path"
    fi
  done < <(grep -oE '\]\([^)]+\)' "$SKILL_DIR/SKILL.md" | sed 's/^](\(.*\))$/\1/')
  if [ "$link_count" -eq 0 ]; then
    info "未发现内部链接"
  elif [ "$link_bad" -eq 0 ]; then
    ok "内部链接 $link_count 个全部有效"
  else
    warn "内部链接 $link_count 个，失效 $link_bad 个（--verbose 看详情）"
  fi
fi



# 12. 语义一致性
section "12. 语义一致性"
if [ -f "$SKILL_DIR/SKILL.md" ] && [ -f "$SKILL_DIR/README.md" ]; then
  skill_version=$(grep -E '^version:' "$SKILL_DIR/SKILL.md" | head -1 | awk '{print $2}' | tr -d '"')
  if grep -q "$skill_version" "$SKILL_DIR/README.md" && grep -q "$skill_version" "$SKILL_DIR/plan.md"; then
    ok "版本号一致：$skill_version"
  else
    warn "版本号不完全一致：SKILL.md=$skill_version"
  fi
fi
placeholder_hits=$(grep -R "v1.0 [占]位\|MVP [占]位" "$SKILL_DIR/scripts" 2>/dev/null || true)
if [ -z "$placeholder_hits" ]; then
  ok "scripts/ 无旧占位实现标记"
else
  warn "scripts/ 仍包含旧占位标记"
fi
for helper in doc-validate.py field-alignment-check.py full-qa-audit.py sql-dialect-check.py postprocess_prd_html.py; do
  if python3 "$SKILL_DIR/scripts/$helper" --help >/dev/null 2>&1; then
    ok "scripts/$helper --help 可运行"
  else
    warn "scripts/$helper --help 运行失败"
  fi
done
if bash "$SKILL_DIR/scripts/parallel-delegate.sh" --help >/dev/null 2>&1; then
  ok "scripts/parallel-delegate.sh --help 可运行"
else
  warn "scripts/parallel-delegate.sh --help 运行失败"
fi

# 13. v2.0 多领域示例 + CI 完整性
section "13. v2.0 多领域示例 + CI"
# 13.1 examples 完整性(至少 3 个,每个 ≥ 12 个文件)
example_dirs=$(find "$SKILL_DIR/examples" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | sort)
example_count=$(echo "$example_dirs" | grep -c . 2>/dev/null || echo 0)
if [ "$example_count" -ge 3 ]; then
  ok "examples/ 含 $example_count 个示例(期望 ≥ 3)"
else
  err "examples/ 仅含 $example_count 个示例(期望 ≥ 3)"
fi
for ed in $example_dirs; do
  ed_name=$(basename "$ed")
  file_count=$(find "$ed" -maxdepth 1 -type f 2>/dev/null | wc -l)
  if [ "$file_count" -ge 10 ]; then
    ok "examples/$ed_name 含 $file_count 个文件(≥ 10)"
  else
    warn "examples/$ed_name 仅含 $file_count 个文件(期望 ≥ 10)"
  fi
done

# 13.2 GitHub Actions workflows 完整性(5 个)
check_dir ".github"
check_dir ".github/workflows"
for wf in smoke-test.yml sql-dialect-check.yml doc-validate.yml field-alignment-check.yml full-qa-audit.yml; do
  check_file ".github/workflows/$wf"
done
wf_total=$(find "$SKILL_DIR/.github/workflows" -name "*.yml" 2>/dev/null | wc -l)
if [ "$wf_total" -ge 5 ]; then
  ok ".github/workflows/ 含 $wf_total 个 workflow(期望 ≥ 5)"
else
  err ".github/workflows/ 仅含 $wf_total 个 workflow(期望 ≥ 5)"
fi

# 13.3 社区文件
check_file "CONTRIBUTING.md"
check_dir ".github/ISSUE_TEMPLATE"
check_file ".github/ISSUE_TEMPLATE/bug_report.md"
check_file ".github/ISSUE_TEMPLATE/feature_request.md"
check_file ".github/PULL_REQUEST_TEMPLATE.md"

# 14. v3.0 工具链 + VSCode 扩展
section "14. v3.0 工具链 + VSCode 扩展"
# 14.1 流程图转换脚本
check_file "scripts/flow-to-mermaid.py"
check_file "scripts/flow-to-drawio.py"
check_file "scripts/flow-export.sh"
if python3 "$SKILL_DIR/scripts/flow-to-mermaid.py" --help >/dev/null 2>&1; then
  ok "scripts/flow-to-mermaid.py --help 可运行"
else
  warn "scripts/flow-to-mermaid.py --help 运行失败"
fi
if python3 "$SKILL_DIR/scripts/flow-to-drawio.py" --help >/dev/null 2>&1; then
  ok "scripts/flow-to-drawio.py --help 可运行"
else
  warn "scripts/flow-to-drawio.py --help 运行失败"
fi
if bash "$SKILL_DIR/scripts/flow-export.sh" --help >/dev/null 2>&1; then
  ok "scripts/flow-export.sh --help 可运行"
else
  warn "scripts/flow-export.sh --help 运行失败"
fi

# 14.2 VSCode 扩展 scaffold
check_dir "vscode-extension"
check_file "vscode-extension/package.json"
check_file "vscode-extension/src/extension.ts"
check_file "vscode-extension/tsconfig.json"
check_file "vscode-extension/README.md"
check_file "vscode-extension/CHANGELOG.md"
check_file "vscode-extension/resources/icon.svg"

# 14.3 README.md 完整性
check_file "README.md"
readme_size=$(wc -l < "$SKILL_DIR/README.md" 2>/dev/null || echo 0)
if [ "$readme_size" -ge 100 ]; then
  ok "README.md 详尽($readme_size 行)"
else
  warn "README.md 较短($readme_size 行)"
fi
# README 中含关键章节
for section in "26 个 skill" "知识库配置" "工具链" "GitHub Actions"; do
  if grep -q "$section" "$SKILL_DIR/README.md" 2>/dev/null; then
    ok "README.md 含「$section」章节"
  else
    warn "README.md 缺「$section」章节"
  fi
done

# ---------- 总结 ----------
if [ "$JSON_MODE" = true ]; then
  echo "{\"results\": $json_results, \"summary\": {\"pass\": $pass_count, \"warn\": $warn_count, \"fail\": $fail_count}}"
  if [ "$fail_count" -gt 0 ]; then exit 2; fi
  if [ "$warn_count" -gt 0 ]; then exit 1; fi
  exit 0
else
  echo ""
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "  ${GREEN}✅ 通过：$pass_count${NC}  ${YELLOW}⚠️  警告：$warn_count${NC}  ${RED}❌ 错误：$fail_count${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""
  if [ "$fail_count" -eq 0 ] && [ "$warn_count" -eq 0 ]; then
    echo -e "${GREEN}🎉 完美：skill 装得完全正确，可以放心使用。${NC}"
    exit 0
  elif [ "$fail_count" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  通过（有警告）：skill 可用，建议关注上面的警告项。${NC}"
    exit 1
  else
    echo -e "${RED}❌ 未通过：skill 安装有问题，请修复上面 ❌ 项后重试。${NC}"
    exit 2
  fi
fi
