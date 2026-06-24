# Spec: grill-task 需求澄清门控加固设计

> 日期: 2026-06-24
> 作者: Claude (brainstorming session)
> 状态: 待用户审阅
> 关联版本: analysis-to-delivery v3.0.0-dev
> 相关 issue: grill-task 在 LLM 解读下可被"部分确认"放行进 BRD,导致未对齐需求进入设计阶段

---

## 1. 背景与动机

`grill-task` 是 analysis-to-delivery 工作流的需求澄清阶段(阶段 2)。当前 SKILL 文本、配套模板与脚本之间存在 7 个一致性 / 结构性 bug,使得 LLM 在执行时可"合法地"放行"用户只确认了部分需求"的状态,从而进入 BRD(阶段 3)。

**典型触发链**:
1. 用户填写 7/13 项,留 6 项空白,状态改为 🟡 部分填写
2. 用户说"已填写" → Claude 触发下一阶段(模板 L47 触发话术太弱)
3. `field-alignment-check.py` 被 SKILL 列为门控脚本,但它**根本不接 TASK_CONFIRM**(脚本 docstring 明确写"检查文档引用字段是否在知识库中定义",只对 PRD/FSD 生效)
4. REVIEW_需求确认书 第八节"待明确事项"非空,模板没说 BLOCK
5. Claude 解读"待明确事项"为"已知风险,继续走 BRD",放行

**本次修复目标**:在不重写 grill-task 流程的前提下,通过"模板硬约束 + 新脚本门控 + SKILL 文本对齐"三件套,堵住所有 7 个 bug,使"部分确认"状态**结构性地无法进入 BRD**。

---

## 2. 设计原则

| 原则 | 体现 |
|---|---|
| **Hard gate 优先** | 任何状态字段 / 文本标记 / 章节完整性 都通过脚本强制校验,不依赖 LLM 自律 |
| **三态变二态** | TASK_CONFIRM 状态字段从 ⬜/🟡/✅ 三态砍为 ⬜/✅ 二态,消除"中间状态合法存在"的可能 |
| **明确话术** | "已填写" 这类弱话术不再触发下一阶段;必须说"我已全部确认,可以进入下一步"等白名单话术 |
| **新脚本独立** | 不修改 `field-alignment-check.py` 的逻辑(避免回归),新增独立 `task-confirm-check.py` |
| **B+C 留痕** | 每个修复步骤产出 STEP-N-review.md,内含"改了什么 / 拒绝的方案 / 边界考虑 / 用户签字位"四节 |
| **全量同步** | 修复同时覆盖源码、example、CI、CHANGELOG、README,避免文档/代码漂移 |

---

## 3. 架构总览(修复后 grill-task 流程)

```
[用户] → STEP 1 (生成 TASK_CONFIRM) → STEP 2 (生成 REVIEW_需求确认书)
                                              ↓
                                       STEP 3 (跑 task-confirm-check.py)
                                              ↓
                                       STEP 4 (生成 REVIEW_字段对齐分析)
                                              ↓
                                       STEP 5 (跑 field-alignment-check.py)
                                              ↓
                                       HARD GATE: 用户白名单话术签字
                                              ↓
                                       /to-brd (阶段 3)
```

**关键变化**:
- STEP 1: 状态字段硬约束为 ⬜/✅ 二态(删 🟡)
- STEP 3: 新增 `task-confirm-check.py` 作为独立门控,5 项检查全过才放行
- HARD GATE: 用户必须说白名单话术,LLM 不再自由解释

---

## 4. 组件清单

### 4.1 新建文件

| 路径 | 用途 | 优先级 | 行数估算 |
|------|------|------|---------|
| `scripts/task-confirm-check.py` | TASK_CONFIRM + REVIEW 文档门控脚本 | P0 | ~180 行 |
| `tests/test_task_confirm_check.py` | pytest 单元测试 | P0 | ~150 行 / 12 用例 |
| `.github/workflows/task-confirm-check.yml` | CI 工作流 | P2 | ~40 行 |

### 4.2 修改文件

| 路径 | 修改动作 | 优先级 |
|------|---------|------|
| `skills/user-invoked/grill-task/SKILL.md` | 加 hard gate 文本(状态字段硬约束、白名单话术);"4 章节"→"5 章节";删 `field-alignment-check.py` 引用 | P0 |
| `skills/disciplines/stage-gate/SKILL.md` | 2→3 门控行拆为 3 条独立门:① 章节齐 ② ❓/🔴 清零 ③ 白名单话术签字 | P0 |
| `templates/TASK_CONFIRM.md` | 删 🟡 状态;改触发话术为白名单;加 12 词 TBD 注释行 | P0 |
| `templates/REVIEW_需求确认书.md` | "阶段 2"→"阶段 3(BRD)";第八节非空 → BLOCK | P1 |
| `templates/REVIEW_字段对齐分析.md` | 状态字段扩为 ✅/⚠️/❓/🔴 四态;🔴>0 或 ❓>0 → BLOCK;"阶段 2"→"阶段 3" | P1 |
| `scripts/field-alignment-check.py` | 仅改顶部 docstring,补一句"本脚本不检查 TASK_CONFIRM,仅校验 PRD/FSD/数据模型的字段引用" | P1 |
| `examples/01-wms-warehouse/TASK_CONFIRM_收货管理.md` | 已 ✅ 状态,验证新脚本能通过 | P2 |
| `examples/02-saas-dashboard/TASK_CONFIRM_订单管理.md` | 同上 | P2 |
| `examples/03-mobile-app/TASK_CONFIRM_会员积分.md` | 同上 | P2 |
| `CHANGELOG.md` | 加 v3.x breaking change 条目 | P2 |
| `README.md` | 引用新脚本 + 12 词列表 + 白名单话术 | P2 |

---

## 5. 核心组件设计

### 5.1 `scripts/task-confirm-check.py`(新建)

**职责**:校验 TASK_CONFIRM_xxx.md + REVIEW_需求确认书.md + REVIEW_字段对齐分析.md 三份文档是否满足进入 BRD 的最低条件。

**5 项检查**(全部通过才 exit 0):

| # | 检查项 | 实现方式 |
|---|--------|---------|
| 1 | **状态字段 == ✅** | 正则 `> 状态：✅` 严格匹配;若仍是 ⬜ 或 🟡 或其他 → fail |
| 2 | **12 词 TBD 扫描** | 全文 grep 以下关键词(大小写不敏感):`TBD, TODO, 待定, 稍后, 下次, N/A, 待确认, 暂定, 未定, 待补充, ⬜, ❓`;命中即 fail,报告行号 |
| 3 | **5 章节完整** | 必须存在 `## 一、` `## 二、` `## 三、` `## 四、` `## 五、` 五个标题(非空表) |
| 4 | **REVIEW 需求确认书 第八节为空** | 解析"## 八、待明确事项"表格,若有任何行(T-01 起) → fail |
| 5 | **REVIEW 字段对齐分析 🔴=0 且 ❓=0** | 解析对齐结论表中"❓ 待确认"和"🔴 缺失"两行的数字计数;任一 > 0 → fail |

**退出码**:
- `0` = 全部通过
- `1` = 检查项未通过(输出失败详情)
- `2` = 参数错误 / 文件不存在 / 解析异常

**CLI 接口**:
```bash
python3 scripts/task-confirm-check.py <TASK_CONFIRM_xxx.md> <REVIEW_需求确认书.md> <REVIEW_字段对齐分析.md>
python3 scripts/task-confirm-check.py --self-test   # 内置自检,跑 5 个 fixture
```

**12 词 TBD 列表(可配置)**:
```python
TBD_KEYWORDS = [
    "TBD", "tbd", "TODO", "todo", "待定", "稍后", "下次",
    "N/A", "n/a", "待确认", "暂定", "未定", "待补充",
    "⬜", "❓",
]
```

### 5.2 `templates/TASK_CONFIRM.md` 修改要点

**改前(L4)**:
```
> 状态：⬜ 待填写 / 🟡 部分填写 / ✅ 已确认
```

**改后**:
```
> 状态：⬜ 待填写 / ✅ 已确认（仅二态）
> 词表红线：本文件若出现以下任何词（TBD / TODO / 待定 / 稍后 / 下次 / N/A / 待确认 / 暂定 / 未定 / 待补充 / ⬜ / ❓）将无法进入下一阶段，请先全部解决。
```

**改前(L47)**:
```
**用户填写后操作**：将本文档保存并告知 Claude "已填写"，Claude 将读取并生成 `REVIEW_需求确认书.md`。
```

**改后**:
```
**用户填写后操作**：
1. 将本文档保存
2. 将状态字段改为 `✅ 已确认`
3. **必须**用以下白名单话术之一告知 Claude（仅说"已填写"不算签字）：
   - `我已全部确认，可以进入下一步`
   - `确认通过，进入 BRD`
   - `全部完成，继续`
   - `approved, proceed to next stage`
4. Claude 将自动跑 `task-confirm-check.py` 校验，5 项检查全过才生成后续文档
```

### 5.3 `skills/user-invoked/grill-task/SKILL.md` 修改要点

**结束条件改前**:
```
- [ ] TASK_CONFIRM 4 个必备章节填完
- [ ] REVIEW_需求确认书已签字
- [ ] REVIEW_字段对齐分析无 🔴 缺失项
- [ ] `field-alignment-check.py` 通过
```

**结束条件改后**:
```
- [ ] TASK_CONFIRM 状态字段 = ✅ 已确认（二态，无 🟡）
- [ ] TASK_CONFIRM 5 个必备章节（一~五）填完
- [ ] TASK_CONFIRM 无 12 词 TBD（见 task-confirm-check.py TBD_KEYWORDS）
- [ ] REVIEW_需求确认书 第八节"待明确事项"为空
- [ ] REVIEW_字段对齐分析 对齐结论表中 ❓=0 且 🔴=0（⚠️ 可保留，状态字段可为 ✅ 或 ⚠️）
- [ ] `task-confirm-check.py` exit 0
- [ ] 用户白名单话术签字（详见 templates/TASK_CONFIRM.md L47）
- [ ] ~~`field-alignment-check.py` 通过~~（已废弃此引用；该脚本不接 TASK_CONFIRM）
```

**关键纪律新增段**:
```
## 关键纪律（2026-06-24 更新）

- ❌ 删除"4 章节"表述——实际为 5 章节（一~五）
- ❌ 删除 `field-alignment-check.py` 作为门控脚本的引用——该脚本只校验 PRD/FSD 字段引用，不接 TASK_CONFIRM
- ✅ 新增 `task-confirm-check.py` 作为唯一门控脚本
- 🟡 删除：状态字段不再有 🟡 中间态，仅 ⬜/✅ 二态
- 🔒 HARD GATE：用户必须用白名单话术之一明确签字，LLM 不接受隐式同意
```

### 5.4 `skills/disciplines/stage-gate/SKILL.md` 修改要点

**改前(L27)**:
```
| 2→3(澄清→BRD) | TASK_CONFIRM + REVIEW 已签字 | 用户 |
```

**改后**:
```
| 2→3(澄清→BRD) | ① TASK_CONFIRM 状态=✅ ② ❓/🔴 清零 ③ 用户白名单话术签字 | 用户 |
```

**附加规则**:
```
- HARD GATE 2→3：上述 3 条独立门，任一未满足禁止进入 BRD
- 白名单话术：`我已全部确认，可以进入下一步` / `确认通过，进入 BRD` / `全部完成，继续` / `approved, proceed to next stage`
- LLM 不得自行解释"OK"/"好"/"继续"等模糊回复为签字
```

### 5.5 `templates/REVIEW_需求确认书.md` 修改要点

**L65-67 改前**:
```
用户审阅操作：
- ✅ 所有"是否正确"列填 ✅ → 进入阶段 2
- ⬜ 仍有未确认项 → 告知 Claude 重新确认
```

**改后**:
```
用户审阅操作：
- ✅ 所有"是否正确"列填 ✅ + 第八节"待明确事项"为空 → 进入阶段 3（BRD）
- ⬜ 仍有未确认项 或 第八节非空 → HARD BLOCK，必须返回 grill-task 重新确认
- 🔴 任一"是否正确"列未填 → HARD BLOCK
```

### 5.6 `templates/REVIEW_字段对齐分析.md` 修改要点

**L5 改前**:
```
> 状态：✅ 已对齐 / ⚠️ 部分待确认
```

**改后**:
```
> 状态：✅ 已对齐 / ⚠️ 需 JOIN / ❓ 待确认 / 🔴 缺失
> BLOCK 规则：🔴>0 或 ❓>0 → 禁止进入阶段 3（BRD）
>
> 说明：状态字段为四态可视化标签；BLOCK 判定以"对齐结论表"中的 ❓ 与 🔴 计数为准（task-confirm-check.py 解析该表的两行数字）。⚠️ 可保留（仅表示部分需 JOIN，不 BLOCK）。
```

**L49 改前**:
```
**结论**：⬜ 可以进入阶段 2 / ⬜ 需先解决待确认项
```

**改后**:
```
**结论**：
- ⬜ 🔴=0 且 ❓=0 → 可以进入阶段 3（BRD）
- ⬜ 🔴>0 或 ❓>0 → HARD BLOCK，需先解决待确认项
```

---

## 6. 数据流(STEP-N-review.md 留痕)

```
project/
├── TASK_CONFIRM_xxx.md                # 用户填写
├── REVIEW_需求确认书.md                # Claude 生成
├── REVIEW_字段对齐分析.md              # Claude 生成
├── field-alignment-report.json        # 脚本输出
├── task-confirm-report.json           # 脚本输出
└── logs/
    ├── STEP-1-review.md               # B+C 留痕
    ├── STEP-2-review.md
    ├── STEP-3-review.md
    ├── STEP-4-review.md
    └── STEP-5-review.md
```

每个 `STEP-N-review.md` 模板(强制 4 节):

```markdown
# STEP {N} Review — {标题}

> 日期：{日期}
> 关联 task：{task 编号}

## 1. 本次改了什么
- 文件 1：`{path}`，改动要点：...
- 文件 2：`{path}`，改动要点：...

## 2. 拒绝的方案（至少 1 个）
- 方案 X：{描述}；拒绝理由：{为什么}

## 3. 边界情况考虑（至少 2 个）
- 边界 A：{场景}；处理：{逻辑}
- 边界 B：{场景}；处理：{逻辑}

## 4. 用户签字位
用户：⬜ 已审 / 日期：____
```

---

## 7. 错误处理

| 失败模式 | 检测机制 | 错误信息 | 退出码 |
|---------|---------|---------|-------|
| TASK_CONFIRM 含 🟡 残留 | task-confirm-check.py 状态字段校验 | `❌ 状态字段必须是 ⬜ 或 ✅，发现 🟡 于第 X 行` | 1 |
| 12 词 TBD 触发 | task-confirm-check.py 词表扫描 | `❌ 发现 TBD 词 "{word}" 于第 X 行（{file}）` | 1 |
| ⬜ 占位符未替换 | task-confirm-check.py ⬜ 计数 | `❌ 发现 {N} 个 ⬜ 占位符未替换（{file}）` | 1 |
| 5 章节缺失 | task-confirm-check.py 标题计数 | `❌ 仅发现 {N} 个章节标题，需要 5 个` | 1 |
| REVIEW 需求确认书 第八节非空 | task-confirm-check.py 表格行扫描 | `❌ 第八节"待明确事项"非空（{N} 项未确认）` | 1 |
| REVIEW 字段对齐分析 🔴>0 或 ❓>0 | task-confirm-check.py 计数解析 | `❌ 字段对齐分析发现 {N} 个 ❓ / {M} 个 🔴，必须为 0` | 1 |
| 字段引用对不上知识库 | field-alignment-check.py（现有） | `❌ 知识库未定义字段 ({N}): {field_list}` | 1 |
| 脚本自身 crash | try/except + traceback | `❌ 脚本异常: {traceback}` | 2 |
| 参数缺失 | argparse | `usage: ...` | 2 |

---

## 8. 测试策略

### 8.1 单元测试(`tests/test_task_confirm_check.py`)

12 个 pytest case:

| # | 用例 | 输入 | 期望 |
|---|------|------|------|
| 1 | 状态 ✅ 通过 | TASK_CONFIRM 状态=✅ | exit 0 |
| 2 | 状态 ⬜ 失败 | TASK_CONFIRM 状态=⬜ | exit 1 |
| 3 | 状态 🟡 失败(老格式) | TASK_CONFIRM 状态=🟡 | exit 1 |
| 4 | TBD 触发 | TASK_CONFIRM 含 "TBD" | exit 1 |
| 5 | 12 词逐个扫描 | TASK_CONFIRM 含 12 词中每个 | 每个都 exit 1 |
| 6 | ⬜ 占位符残留 | TASK_CONFIRM 含 3 个 ⬜ | exit 1 |
| 7 | 5 章节完整 | TASK_CONFIRM 含一~五 | exit 0 |
| 8 | 5 章节缺失 | TASK_CONFIRM 只含一~四 | exit 1 |
| 9 | REVIEW 第八节为空 | REVIEW_需求确认书 第八节表格无行 | exit 0 |
| 10 | REVIEW 第八节非空 | REVIEW_需求确认书 第八节有 T-01 行 | exit 1 |
| 11 | 字段对齐 🔴=❓=0 | REVIEW_字段对齐分析 对齐结论表 ❓=0,🔴=0 | exit 0 |
| 12 | 字段对齐 🔴>0 | REVIEW_字段对齐分析 对齐结论表 🔴=2 | exit 1 |
| 13 | 字段对齐 ❓>0 | REVIEW_字段对齐分析 对齐结论表 ❓=1 | exit 1 |

### 8.2 集成测试(bash)

```bash
# 跑全部 3 个 example,确保新脚本通过
for example in examples/0*/TASK_CONFIRM_*.md; do
    python3 scripts/task-confirm-check.py "$example" \
        "${example%.md}_review_confirm.md" \
        "${example%.md}_review_field.md" || exit 1
done
```

### 8.3 CI(`.github/workflows/task-confirm-check.yml`)

```yaml
name: task-confirm-check
on: [pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install pytest
      - run: pytest tests/test_task_confirm_check.py -v
      - run: bash scripts/integration-test-examples.sh
```

### 8.4 端到端(手动)

按 9 阶段走一遍完整流程,每阶段人工核对状态字段和 STEP-N-review.md。

---

## 9. 实施顺序(高阶)

按 P0 → P1 → P2 线性分层,每个 P-block = 1 个 commit batch:

### P0(核心门控基础设施)
1. **Task A1**:新建 `scripts/task-confirm-check.py` + 5 项检查逻辑
2. **Task A2**:新建 `tests/test_task_confirm_check.py` + 12 用例
3. **Task A3**:修改 `templates/TASK_CONFIRM.md`(删 🟡、改话术、加词表)
4. **Task A4**:修改 `skills/user-invoked/grill-task/SKILL.md`(hard gate 文本)
5. **Task A5**:修改 `skills/disciplines/stage-gate/SKILL.md`(2→3 门控拆分)
6. **Task A6**:跑 pytest + 集成测试,产出 `logs/STEP-P0-review.md`

### P1(模板与 SKILL 文本对齐)
1. **Task B1**:修改 `templates/REVIEW_需求确认书.md`(阶段号 + BLOCK 规则)
2. **Task B2**:修改 `templates/REVIEW_字段对齐分析.md`(状态 4 态 + BLOCK)
3. **Task B3**:修改 `scripts/field-alignment-check.py` docstring(声明范围)
4. **Task B4**:跑全部 example + 集成测试,产出 `logs/STEP-P1-review.md`

### P2(文档与 CI 同步)
1. **Task C1**:跑 `task-confirm-check.py` 验证 3 个 example 通过
2. **Task C2**:新建 `.github/workflows/task-confirm-check.yml`
3. **Task C3**:修改 `CHANGELOG.md`(v3.x breaking change)
4. **Task C4**:修改 `README.md`(引用新脚本 + 12 词 + 白名单话术)
5. **Task C5**:本地跑全套验证(单元 + 集成 + CI lint),产出 `logs/STEP-P2-review.md`

---

## 10. 风险与缓解

| 风险 | 等级 | 缓解 |
|------|------|------|
| 硬删 🟡 是 breaking change,老用户文档不兼容 | 中 | CHANGELOG 明确写;README 加 migration 提示 |
| 12 词 TBD 可能误报(用户故意写"TBD 流程"作为标题) | 低 | 词表设计为整词匹配;CI 集成测试覆盖常见误报 |
| 白名单话术太严,用户用近义表达被拒 | 中 | 提供 5 个白名单话术(含中英文);CHANGELOG 列出 |
| `field-alignment-check.py` 仅改 docstring 可能不够清晰 | 低 | 同时在 `grill-task/SKILL.md` 显式标注"已废弃此引用" |
| examples 没有体现新模板的"二态"差异 | 低 | examples 已全填 ✅,验证新脚本即可 |

---

## 11. 默认选择(用户已批准)

- ✅ "逻辑审查" = B+C(用户签字门控 + STEP-N-review.md 留痕)
- ✅ 范围 = 全量同步(源码 + examples + tests + CI + docs)
- ✅ TBD 严格度 = 12 词最严格列表
- ✅ 🟡 状态 = 硬删除(不接受兼容)
- ✅ 触发话术 = 白名单列表(`已全部确认，可以进入下一步` / `确认通过，进入 BRD` / `全部完成，继续` / `approved, proceed to next stage`)
- ✅ `field-alignment-check.py` 仅改 docstring,不动逻辑
- ✅ `analysis-delivery-workflow` SKILL.md 不动(本次范围外)

---

## 12. 不在本次范围

- `analysis-delivery-workflow` SKILL.md 的"按顺序自动调"措辞问题(P3)
- `analysis-delivery-workflow` 的"严禁跳阶段"实际是软约束(P3)
- `disciplines/` 下的其他 6 个纪律的强化(P3)
- examples/ 下的 `*_review_*.md` 示例文档生成(目前 examples/ 没有这类文件,P3)
- 新脚本是否需要支持 `--strict/--loose` 双模式(本次仅 strict,P3)

---

## 13. 验收标准

- [ ] `pytest tests/test_task_confirm_check.py` 全 12 case 通过
- [ ] 3 个 example TASK_CONFIRM 全部通过新脚本
- [ ] CI workflow 文件可被 GitHub Actions 解析(`yamllint` 通过)
- [ ] CHANGELOG.md 含 v3.x breaking change 条目
- [ ] README.md 引用新脚本 + 12 词 + 白名单话术
- [ ] 3 个 `logs/STEP-P*-review.md` 全部签字
- [ ] 无新增 TODO / FIXME
- [ ] git diff 干净,无意外文件变动