# P0 整体 Review — 核心门控基础设施

> 日期：2026-06-24
> 覆盖 Task:1-8
> 执行人:Claude(subagent-driven-development 模式,直接执行因 plan 含完整代码)

## 1. P0 改了什么

| Commit | 内容 |
|--------|------|
| `e25c6f3` | Task 1: 脚本脚手架 + Check 1 状态字段 |
| `0f2b1da` | Task 2: Check 2 - 12 词 TBD 扫描 |
| `8d76ab9` | Task 3: Check 3 - 5 章节完整 |
| `83ffc40` | Task 4: Check 4 - REVIEW 第八节为空 |
| `b9d2e95` | Task 5: Check 5 - 字段对齐计数(修 marker+label 重复 bug) |
| `e10e999` | Task 6: 模板硬约束 + 脚本模板例外 |
| `8f3e0c8` | Task 7: grill-task SKILL hard gate |
| `28bc43f` | Task 8: stage-gate SKILL 2→3 门控拆 3 条 |

**净增文件**:
- 新建 `scripts/task-confirm-check.py`(~170 行,5 项 Check)

**净改文件**:
- `templates/TASK_CONFIRM.md`(状态二态 + 白名单话术 + 占位符改 `[待填写]`)
- `skills/user-invoked/grill-task/SKILL.md`(结束条件 7 条 + 2026-06-24 更新段)
- `skills/disciplines/stage-gate/SKILL.md`(2→3 门控拆 3 条 + 附加规则)

## 2. 拒绝的方案

- 方案 A:在 `field-alignment-check.py` 加 TASK_CONFIRM 分支
  - 拒绝理由:违反"新脚本独立"原则;field-alignment-check.py 的 docstring 已声明只校验 PRD/FSD

- 方案 B:保留 🟡 兼容老用户
  - 拒绝理由:用户选硬删除;breaking change 由 CHANGELOG 处理(v3.x)

- 方案 C:模板直接列举 12 词 TBD
  - 拒绝理由:模板自指,被 Check 2 误报自身。改用引用脚本路径

- 方案 D:把 ⬜ 占位符保留在模板里
  - 拒绝理由:`⬜` 既是占位符又是 TBD 词表成员,语义冲突。改为 `[待填写]`

## 3. 边界情况考虑

- **边界 A:模板文件例外** — 加 `templates/TASK_CONFIRM.md` 例外,跳过 Check 2/3,因为模板含自指占位符。例外的合理性:模板是源文档,不是用户填写结果
- **边界 B:Check 5 正则 bug** — 初版用 `marker+label` 拼出 `❓❓ 待确认`,匹配失败。修后仅用 `label`(已含 marker)。**记录到 P3:tests/ 加 pytest case 锁定该回归**
- **边界 C:example 02/03 用旧模板格式** — 不在 P0 范围,P2 Task 14 修
- **边界 D:`approved` 是英文白名单** — 国际化场景,CHANGELOG/CHANGELOG 注明

## 4. 集成验证结果

```
=== example 01 (WMS 收货管理) ===
✅ Check 1 通过:状态字段 = ✅
✅ Check 2 通过:无 12 词 TBD 残留
✅ Check 3 通过:5 章节完整
✅ Check 4 通过:REVIEW 第八节为空
✅ Check 5 通过:字段对齐 🔴=0, ❓=0
exit=0  ← 全过

=== example 02/03 (旧格式) ===
❌ 状态 = ⬜,章节用阿拉伯数字 1./2.,含"待确认"词
exit=1  ← 期望行为,P2 Task 14 修

=== templates/TASK_CONFIRM.md 本身 ===
ℹ️  模板文件例外,跳过 Check 2/3
❌ Check 1 状态 = ⬜
exit=1  ← 期望行为,模板是源不是结果
```

## 5. 用户签字位

**P0 整体签字**(8 个 Task):

用户：⬜ 已审 / 日期：____

签字后进入 P1 块(Task 10-13)。