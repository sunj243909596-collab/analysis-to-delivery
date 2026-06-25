# ⚠️ DEPRECATED — 请改用 `decisions.md`

> 自 v3.1.0 起,本文件(`config-used.md`)改名为 `decisions.md`。
> 原名容易让人误以为是配置文件,实际是 ADR / 决策记录。

## 迁移指引

```bash
# 在项目根目录执行
mv config-used.md decisions.md
```

## 新模板

请使用 [`decisions.md`](./decisions.md) 替代本文件。

## 为什么不删除旧名

为保持向后兼容,旧名 `config-used.md` 仍然识别(由 `scripts/filename-naming-check.py` 白名单支持)。
新项目应直接使用 `decisions.md`;老项目可继续使用 `config-used.md`,下次清理时再改名。

## 变更记录

| 日期 | 变更 | 原因 |
|---|---|---|
| 2026-07-XX | 改名 `config-used.md` → `decisions.md` | 原名像 config 实际是 ADR,误导严重 |