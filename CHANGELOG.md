# Changelog

所有本项目的显著变更都会记录在此文件。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.0.0-mvp] - 2026-06-22

### 新增
- 🎉 MVP 首发版本
- 10 阶段通用工作流（SKILL.md，16KB）
- install.sh 一键安装脚本（支持 dry-run、target、uninstall、version 参数）
- 配置目录（`config/`）：
  - 合规规则：gsp.md（医药示例）、none.md、template.md
  - 技术栈：java-spring.md、frontend-vue.md、template.md
  - 领域知识、文档命名：template.md
- 完整示例（`examples/01-wms-warehouse/`）：
  - 医药物流 WMS 收货管理迷你示例
  - 含 config-used.md / TASK_CONFIRM / REVIEW_需求确认书 / REVIEW_字段对齐分析 / BRD / 状态流转图 / 业务流程图
- 12 个文档模板（`templates/`）
- 10 个方法论文档（`references/`）占位
- 5 个自动化脚本（`scripts/`）占位
- 完整文档：README.md / plan.md / SPEC.md / LICENSE

### 已知限制
- 仅有 1 个领域示例（医药 WMS）
- 配置库不完整（仅有 2 个合规 + 2 个技术栈示例）
- 模板和脚本为占位（待 v1.1 完善）
- 无 GitHub Actions CI（待 v2.0）

### 计划
- v1.1：补 5-8 个合规规则 + 6-8 个技术栈
- v1.2：补完整模板和脚本 + skill 自检
- v2.0：补 2 个新示例 + GitHub Actions + CONTRIBUTING.md

---

## 版本说明

- **1.0.0-mvp**：MVP 首发。功能完整但配置库/模板/脚本不全，**生产环境慎用**
- **1.x.x**：配置库完善阶段，向完全可用演进
- **2.x.x**：多领域示例 + CI 阶段
- **3.x.x**：工具链集成 + 可视化阶段
