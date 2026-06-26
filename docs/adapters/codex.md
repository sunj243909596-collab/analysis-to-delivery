# Codex Adapter

Analysis to Delivery 在 Codex 中按 agent-neutral workflow 使用:Codex 读取 `SKILL.md` / `skills/**/SKILL.md`,按需运行 `scripts/` 中的门控脚本,项目级配置由 `AGENTS.md` 和 `paths/*.md` 提供。

## 安装

```bash
bash install.sh --agent codex
```

默认目标:

```text
${CODEX_HOME:-~/.codex}/skills/analysis-to-delivery
```

也可以显式指定:

```bash
bash install.sh --target /path/to/codex/skills/analysis-to-delivery
```

## 使用

Codex 不需要依赖 Claude 专用命令。推荐用自然语言触发:

```text
使用 analysis-to-delivery 分析这个新功能,先走 /setup-analysis-delivery,再进入 /grill-task。
```

如果项目根有 `AGENTS.md`,把本仓库位置写进去:

```markdown
## Analysis to Delivery

- Skill root: ~/.codex/skills/analysis-to-delivery
- Entry: read `SKILL.md`,then load the selected `skills/**/SKILL.md`
- Gates: run `python3 scripts/*-check.py` from the skill root
```

## 能力映射

| 能力 | Codex 接入方式 |
|---|---|
| 入口路由 | 读取 `SKILL.md` 后选择 `/ask-delivery` 或具体 skill |
| 项目规则 | 读取项目 `AGENTS.md` + `paths/*.md` |
| 门控脚本 | 直接运行 `scripts/` 下 Python/Bash 脚本 |
| Slash command | 可用自然语言替代 |
| 子代理并行 | 使用 Codex 当前可用的任务/子代理能力;无则顺序执行 |

## 已知限制

- `scripts/parallel-delegate.sh` 是 Claude CLI adapter,在 Codex 下不要直接使用。
- bridge 到 `superpowers` 的 skill 如本地不存在,按各 bridge SKILL.md 的降级步骤执行。
