# P3 整体 Review — 测试 / 示例 / 双模式

> 日期：2026-06-24
> 覆盖 Task:P3-T1 / P3-T2 / P3-T3 / P3-T4(P3-T5 = 本文档)
> 关联 commit:`269ea80` / `bcffb19` / `0c4e13f` / `9ba51e4`

## 1. P3 改了什么

| Task | Commit | 内容 |
|------|--------|------|
| P3-T1 | `269ea80` | `tests/test_task_confirm_check.py`(18 case → 22 case)+ `tests/conftest.py` + CI workflow 加 pytest 步 |
| P3-T2 | `bcffb19` | `analysis-delivery-workflow/SKILL.md` 加"严禁自动推进" + 2→3 门控交叉引用 `task-confirm-check.py` |
| P3-T3 | `0c4e13f` | examples 0[1-3] REVIEW_*.md 全部对齐 v3.x(4 态状态字段 + 对齐结论表 + 第七/八节)|
| P3-T4 | `9ba51e4` | `task-confirm-check.py` v1.0.0 → v1.1.0:--strict / --loose 双模式 + argparse 互斥组 |

## 2. 拒绝的方案

- 方案 A:P3-T4 用 `--mode=strict|loose` 单参数
  - 拒绝理由:argparse 互斥组 (`--strict | --loose`) 更显式,且默认行为明确(`--strict` 为 default)

- 方案 B:`--loose` 跳过 Check 4 + Check 5(只跑 1/2/3)
  - 拒绝理由:用户场景是"早期 REVIEW 未完成时希望 warning 不 BLOCK",因此 Check 3/4/5 都应降级而非跳过

- 方案 C:为 `--loose` 单独写一个 `task-confirm-check-loose.py`
  - 拒绝理由:YAGNI,单脚本双模式更轻量;用户通过 `--strict` / `--loose` 即可切换

- 方案 D:在 pytest 中 mock subprocess
  - 拒绝理由:用真实 subprocess 跑 CLI,更接近 CI 行为,避免 mock 漂移

## 3. 边界情况考虑

- **边界 A**:`--strict --loose` 同时传 → argparse 自动拒绝(rc=2)— 已加 `test_cli_strict_loose_mutually_exclusive` 守护

- **边界 B**:模板 `templates/TASK_CONFIRM.md` 自指 `⬜` 占位符在 `--loose` 下仍被 Check 1 BLOCK(符合预期,模板不该误通过)— 已加人工验证

- **边界 C**:examples 三套文档的 REVIEW_字段对齐分析.md 第二节是表头表/字段表,可能干扰 Check 5 解析 — 已确认 Check 5 只扫描 "对齐结论表",而三套文档都在末尾显式列了 `## 对齐结论` + `❓=0 / 🔴=0`,通过

- **边界 D**:CI workflow 是否需要加 pytest 步? — 已加(P3-T1),`pip install pytest && pytest tests/ -v`,与 task-confirm-check.py + self-test 串行跑

- **边界 E**:`test_cli_template_rejected` 在 `--loose` 下也该通过(模板 Check 1 失败)— 已验证,template 在两种模式下都 exit 1

## 4. 最终集成验证

```
=== pytest (期望 22 passed) ===
22 passed in 0.39s

=== examples --strict (期望 3/3 PASS) ===
✅ 01-wms-warehouse: --strict PASS (5/5)
✅ 02-saas-dashboard: --strict PASS (5/5)
✅ 03-mobile-app: --strict PASS (5/5)

=== self-test (期望 exit 0) ===
✅ task-confirm-check.py 自检

=== --strict --loose (期望 argparse 拒绝 rc=2) ===
usage: task-confirm-check.py: error: argument --loose: not allowed with argument --strict

=== 模板 (期望两种模式都 exit 1) ===
--strict: ❌ 状态字段 = ⬜ → exit 1
--loose:  ❌ 状态字段 = ⬜ → exit 1
```

## 5. P0+P1+P2+P3 累计交付物

| 类别 | 数量 / 路径 |
|------|------------|
| 新增脚本 | `scripts/task-confirm-check.py` (v1.1.0) |
| 修改 SKILL | `skills/user-invoked/grill-task/` + `skills/disciplines/stage-gate/` + `skills/orchestration/analysis-delivery-workflow/` |
| 修改模板 | `templates/TASK_CONFIRM.md` + `templates/REVIEW_需求确认书.md` + `templates/REVIEW_字段对齐分析.md` |
| 修改示例 | `examples/0[1-3]/TASK_CONFIRM_*.md` (重写) + `examples/0[1-3]/REVIEW_*.md` (修订) |
| CI workflow | `.github/workflows/task-confirm-check.yml` |
| 测试 | `tests/test_task_confirm_check.py` (22 case) + `tests/conftest.py` |
| 文档 | `README.md` + `CHANGELOG.md` + `docs/superpowers/specs/2026-06-24-grill-task-bugfix-design.md` + `docs/plans/2026-06-24-grill-task-bugfix.md` |
| 留痕 | `logs/STEP-P0-review.md` + `logs/STEP-P1-review.md` + `logs/STEP-P2-review.md` + `logs/STEP-P3-review.md` |

## 6. 用户交付签字

> **grill-task 门控加固项目全部 18 个原始 Task + 4 个 P3 增强 Task 全部完成。**
>
> 累计 22 commits,pytest 22/22 通过,3 套示例 REVIEW 文档 5/5 check 通过,`--strict`/`--loose` 双模式 + 互斥组生效。
>
> **门控执行情况汇总**:
> - ✅ TASK_CONFIRM 状态字段硬约束 `⬜/✅` 二态(删 🟡)
> - ✅ 12 词 TBD 红线扫描 + `\b` 整词匹配(ID_TODO_FIELD 不误报)
> - ✅ 5 章节硬要求 + REVIEW 第七/八节空表检查
> - ✅ 字段对齐 `❓=0` / `🔴=0` BLOCK 规则
> - ✅ 4 句白名单话术用户签字才能进阶段 3
> - ✅ 双模式 + 互斥组(`--strict`/`--loose` 不可同时传)
> - ✅ CI workflow 自动化(self-test + pytest + 集成 + 模板拒绝)
>
> **请用户最终签字交付。**

---

## 7. 用户签字确认区

```
☑ 全部通过,可以发布 v3.0.0
□ 需要修改:___________
签字日期:2026-06-24
签字人:用户("确认" — 2026-06-24)
```