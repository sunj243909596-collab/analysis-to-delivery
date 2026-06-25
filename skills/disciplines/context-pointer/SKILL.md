---
name: context-pointer
description: 项目级配置优先(读 *-path.md),skill 级 config 仅作 fallback,严禁编造配置。Use when needing to look up domain knowledge, compliance rules, or tech stack conventions.
version: 3.0.1

---

# Context-Pointer — 三层配置加载

## Contract

- Inputs: project root, `*-path.md`, skill-level config fallback
- Outputs: resolved knowledge/compliance/tech-stack/doc-naming sources
- Gates: project-level config preferred; missing facts trigger user question rather than invention
- Required disciplines: none
- Next: calling skill continues

## 三层优先级(从高到低)

```
┌─────────────────────────────────────────┐
│  Level 1:项目级(最高优先级)            │
│  位置:项目根目录                         │
│  文件:                                 │
│    knowledge-path.md                     │
│    compliance-path.md                    │
│    tech-stack-path.md                    │
│    doc-naming.md                         │
└──────────────┬──────────────────────────┘
               │ 项目级未填写 → fallback
               ▼
┌─────────────────────────────────────────┐
│  Level 2:skill 级(示例库 + fallback)  │
│  位置:skills/disciplines/../config/    │
│  文件:compliance/{gsp,none,...}.md 等    │
└──────────────┬──────────────────────────┘
               │ 仍不匹配 → fallback
               ▼
┌─────────────────────────────────────────┐
│  Level 3:默认(通用流程)                │
│  行为:Claude 主动询问用户                │
└─────────────────────────────────────────┘
```

## 加载规则

| 用户回答 / 项目状态 | 加载路径 |
|---|---|
| 项目根有 `knowledge-path.md`,列了真实路径 | **Level 1** 直接读项目填的路径 |
| 项目根没有 `*-path.md`,命中 skill 级 fallback | **Level 2** 用 `config/compliance/{行业}.md` 等 |
| 项目级 + skill 级都没有 | **Level 3** Claude 必须主动问用户,禁止编造 |

## 硬性规则

1. **严禁编造** — 任何合规规则、技术规范、领域知识,**必须从已加载的配置中读取**
2. **skill 级 config 仅作格式参考** — `config/compliance/gsp.md` 等不追求覆盖广度
3. **真实项目配置跟着项目走** — 不污染 skill 仓库
4. **缺失主动问** — 找不到配置时,Claude 必须问,不能猜

## 渐进式披露(Progressive Disclosure)

- SKILL.md 只放"何时调、怎么调、结束条件"
- 详细信息(知识库 / 合规条款 / 完整规则)放 context pointer 引用的文件
- 按需加载,避免 context 爆炸

## 反例

```markdown
❌ 错误:Claude 自己编造 GSP 条款
"GSP 第 12345 条要求..."

✅ 正确:读 compliance-path.md 指向的真实文件
读项目根 compliance-path.md → 加载引用的 GSP 法规文件
```

## 引用

- 详细规范:用户全局 `CLAUDE.md` "项目级配置"小节
- skill 仓库:原 SKILL.md "配置加载机制"小节
