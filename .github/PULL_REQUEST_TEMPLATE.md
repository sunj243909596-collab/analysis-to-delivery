# 拉取请求(Pull Request)模板

> 请填写以下所有 section。未填写的 PR 可能被退回。

## 改动类型

- [ ] 新功能(skill / 示例 / 脚本)
- [ ] Bug 修复
- [ ] 文档改进
- [ ] 重构(不改行为)
- [ ] CI / 脚本改进
- [ ] 其他(请说明):

## 改动摘要

一句话描述这个 PR 做了什么。

## 相关 Issue

- 关闭 #<issue_number>
- 关联 #<issue_number>(如有)

## 改动详情

详细说明改了什么,为什么这么改。

### 改动文件清单

| 文件 | 类型 | 说明 |
|---|---|---|
| `path/to/file1` | 新增/修改/删除 | 说明 |
| `path/to/file2` | 新增/修改/删除 | 说明 |

### 关键决策(如有)

- 决策 1:理由 + 备选方案
- 决策 2:理由 + 备选方案

## 测试

### 本地验证

- [ ] `bash scripts/smoke-test.sh` 通过
- [ ] `python3 scripts/sql-dialect-check.py "examples/**/*.md"` 通过
- [ ] `python3 scripts/doc-validate.py "examples/**/*.md"` 通过
- [ ] `python3 scripts/field-alignment-check.py "examples/**/*.md"` 通过
- [ ] `python3 scripts/full-qa-audit.py "examples/**/*.md"` 通过

### 新增测试(如有)

- 单元测试:
- 集成测试:
- 手动测试:

### 截图 / 录屏(如有 UI 改动)

(粘贴或链接)

## 文档同步

- [ ] 改动了 skill → 已更新 SKILL.md
- [ ] 改动了示例 → 已更新 README.md / 业务流程图
- [ ] 改动了脚本 → 已更新 README.md
- [ ] 改动了 CI → 已更新 workflows 注释
- [ ] 重大变更 → 已更新 CHANGELOG.md
- [ ] 重大变更 → 已更新 plan.md

## 兼容性

- [ ] 向后兼容(无破坏性变更)
- [ ] 破坏性变更 → 已在 description 中说明

## 检查清单

- [ ] 分支基于最新 main
- [ ] 提交信息遵循 Conventional Commits
- [ ] CI 全部通过
- [ ] 无遗留调试代码(console.log / debugger / TODO)
- [ ] 无夹带改动(改动与 title 一致)
- [ ] 已自审代码

## 致谢

(如有参考 / 借鉴,列出来源)

---

> 📝 提交前最后检查:对照 [CONTRIBUTING.md](../CONTRIBUTING.md) §3.5 PR 验收标准。