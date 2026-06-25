---
name: analysis-to-delivery
description: 通用需求分析到开发设计工作流 — 26 个独立 skill 自由组合(2 router + 9 动作 + 1 编排 + 7 bridge + 7 discipline)。跨行业、跨技术栈。Use when starting any new feature requiring structured analysis-to-delivery workflow.
category: software-development
version: 3.1.0
created: 2026-06-22
updated: "2026-07-02: v3.1.0 P0-P3 共 12 项修复(6 门控脚本 + discipline lint + bridge 降级 + flow strict + state 持久化 + 数字统一 + README 降级 + 快速通道 + 3 example 升级 + description 精简 + 反模式 + 改名 decisions)"
---

# Analysis to Delivery

## Contract

- Inputs: new feature / project delivery request, domain, tech stack, optional project `*-path.md`
- Outputs: routed skill recommendation or full 9-stage analysis-to-delivery workflow
- Gates: use `/analysis-delivery-workflow` for full process; stage gates enforced by child skills
- Required disciplines: `context-pointer`, `stage-gate`, `doc-numbering`, `no-field-guessing` as invoked by child skills
- Next: `/ask-delivery`, `/analysis-delivery-workflow`, or a specific user-invoked skill

> 26 个独立 skill 自由组合 — 走流程用 orchestration,做单件事用 action,纪律由 disciplines 自动加载。

## 快速开始

- **不知道用哪个?** → `/ask-delivery` (router)
- **走完整 9 阶段** → `/analysis-delivery-workflow`
- **进入开发实施** → `/using-superpowers` (router)

## 快速通道

跳过 router,直接按你的目标选:

| 你想要 | 直接调 |
|---|---|
| 配置项目(知识库/技术栈/合规/命名) | `/setup-analysis-delivery` |
| 跑 5 项门控全套 | `bash scripts/smoke-test.sh` |
| 看项目走到哪个阶段 | `python3 scripts/analysis-state.py status` |
| 把 ASCII 流程图转成 Mermaid | `python3 scripts/flow-to-mermaid.py file.txt` |
| 校验所有 skill 是否合规 | `python3 scripts/discipline-lint.py skills/` |

## 逆向使用

不是从需求 → 设计,而是**已有产物需要后向追溯 / 修复**:

| 已有产物 | 逆向动作 |
|---|---|
| 有 `01-BRD.md`,但不确定字段是否对 | `python3 scripts/field-alignment-check.py <project>` |
| 有 `05-PRD.md`,但发现 PRD 与 BRD 冲突 | 回到 `/grill-task` 重对齐 |
| 有 `06-开发设计.md`,但代码已写完 | 直接进 `/qa-audit` 找设计偏差 |
| 有 `09-QA审计报告.md` P0 列表 | 逐项修复后重跑 `python3 scripts/full-qa-audit.py` |
| 状态文件还在(`.analysis-delivery-state.json`) | `python3 scripts/analysis-state.py status` 看中断在哪个阶段 |

## 度量

`scripts/analysis-state.py metrics [--json]` 输出 5 项指标(项目级,持久化到 `.analysis-delivery-state.json`):

| # | 指标 | 含义 |
|---|---|---|
| 1 | 总 gate 调用次数 | 整套流程跑了多少次自动化门控 |
| 2 | 总签字次数 | 用户白名单话术累计签字次数 |
| 3 | gate 拦截次数 | 每个 gate 脚本失败的次数(按脚本名分) |
| 4 | 各阶段重试次数 | 哪些阶段需要反复回去修 |
| 5 | 阶段用时(分钟) | 已签字阶段的耗时(开始 → 签字) |

**用途**:发现流程瓶颈(哪阶段重试最多)、门控过严/过松(gate 拦截频率)。

## 结构

```
skills/
├── ask-delivery/                    # Router 1: 9 动作 + 1 编排
├── using-superpowers/               # Router 2: 7 个 superpowers skill
├── user-invoked/                    # 9 个动作
│   ├── setup-analysis-delivery/     # 1: 项目配置
│   ├── grill-task/                  # 2: 需求澄清 + 字段对齐
│   ├── to-brd/                      # 3: BRD
│   ├── compliance-review/           # 4: 合规评审
│   ├── test-case-design/            # 5: 测试用例
│   ├── to-prd/                      # 6: PRD
│   ├── dev-design/                  # 7: FSD+数据模型+开发设计+回测+复盘
│   ├── qa-audit/                    # 8: QA 审计
│   └── handoff/                     # 9: 交接
├── orchestration/                   # 1 + 7, 嵌套
│   ├── analysis-delivery-workflow/  # 9 阶段流程编排
│   └── development/                 # 7 个 superpowers bridge
│       ├── brainstorming/
│       ├── design-an-interface/
│       ├── domain-modeling/
│       ├── writing-plans/
│       ├── tdd/
│       ├── executing-plans/
│       └── verification-before-completion/
└── disciplines/                     # 7 个纪律 (model-invoked)
    ├── no-field-guessing/
    ├── no-self-invent/
    ├── ascii-flowchart/
    ├── stage-gate/
    ├── sql-dialect-discipline/
    ├── doc-numbering/
    └── context-pointer/
```

## 设计哲学

参考 [mattpocock/skills](https://github.com/mattpocock/skills) 风格:
- **小而精**:每个 skill < 300 行,职责单一
- **可组合**:自由调用任意 skill,不强制流程
- **不拥有流程**:把控制权留给用户
- **易改易适配**:改一个不影响其他

## 详细文档

- [README.md](README.md) — 完整使用说明
- [plan.md](plan.md) — 路线图
- [CHANGELOG.md](CHANGELOG.md) — 版本历史

## 安装

```bash
npx skills@latest add <your-repo>
```

## 纪律(自动加载)

`disciplines/` 下的 7 个纪律 model-invoked,会被任意 user-invoked skill 自动调用,无需手动触发。
