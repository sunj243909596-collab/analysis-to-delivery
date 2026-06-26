# OpenCode Adapter

Analysis to Delivery 在 OpenCode 中建议按项目级 `AGENTS.md` + CLI gate 使用。核心文件都是 Markdown 和脚本,不要求 Claude/Hermes 专用 runtime。

## 安装

如果你的 OpenCode 环境约定了 skills 目录:

```bash
bash install.sh --agent opencode
```

默认目标:

```text
${OPENCODE_HOME:-~/.opencode}/skills/analysis-to-delivery
```

如果 OpenCode 使用别的配置目录,请用:

```bash
bash install.sh --target /path/to/opencode/skills/analysis-to-delivery
```

## 项目级接入

在目标项目的 `AGENTS.md` 中增加:

```markdown
## Analysis to Delivery

- Skill root: /path/to/analysis-to-delivery
- Entry: read `SKILL.md`,then load only the selected `skills/**/SKILL.md`
- Required rules: load only the `rules/*.md` declared by the selected skill
- Required paths: load project `paths/*.md` first,then fallback to skill-level paths
- Gates: run `python3 <skill-root>/scripts/*-check.py <project>` before moving stages
```

## 使用

```text
使用 analysis-to-delivery 走完整 9 阶段工作流。当前项目技术栈是 Node + React + PostgreSQL。
```

或者指定单步:

```text
使用 analysis-to-delivery 的 grill-task 澄清这个需求,输出 TASK_CONFIRM。
```

## 已知限制

- slash command 是否可用取决于 OpenCode 本地配置;不可用时用自然语言替代。
- `scripts/parallel-delegate.sh` 是 Claude CLI adapter,在 OpenCode 下不要直接使用。
