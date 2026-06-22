---
name: analysis-to-delivery
description: 通用需求分析到开发设计工作流 — 26 个独立 skill 自由组合(2 router + 9 动作 + 1 编排 + 7 bridge + 7 discipline)。跨行业、跨技术栈。Use when starting any new feature requiring structured analysis-to-delivery workflow.
category: software-development
version: 2.0.0-dev
created: 2026-06-22
updated: "2026-06-22: v2.0.0-dev 增加 2 个示例 + GitHub Actions + CONTRIBUTING + v3.0 工具链"
---

# Analysis to Delivery

> 26 个独立 skill 自由组合 — 走流程用 orchestration,做单件事用 action,纪律由 disciplines 自动加载。

## 快速开始

- **不知道用哪个?** → `/ask-delivery` (router)
- **走完整 9 阶段** → `/analysis-delivery-workflow`
- **进入开发实施** → `/using-superpowers` (router)

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
