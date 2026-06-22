# Changelog

所有本项目的显著变更都会记录在此文件。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 变更
- 🎯 **阶段 8 简化**：去掉 V1（存储过程版）/ V2（代码实现版）双版本概念，统一为单一代码版工作流
  - FSD（功能规格）从"V1 配套产物"独立为阶段 8.1 通用产物，模板完全重写
  - 数据模型设计、开发设计说明书保持，归属从 `(V1)` `(V2)` 改为通用
  - `references/v1-v2-versioning.md` 重命名为 `references/dev-design-spec.md` 并重写
  - SKILL.md / SPEC.md 阶段 8 整段同步重写

### 新增
- 🆕 **项目级 config 体系**（v1.1 核心）
  - 4 个 `*-path.md` 模板（`templates/project-config/`）：knowledge / compliance / tech-stack / doc-naming
  - `scripts/init-project-config.sh`：一键在项目根生成 4 个空模板
  - SKILL.md 配置加载机制重写为三层优先级（项目级 > skill 级 > 默认）
  - SPEC.md §6.5 项目级配置契约
  - 示例 `examples/01-wms-warehouse/` 下加 4 个 `*-path.md` 演示

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
- **1.1.0**（开发中）：项目级 config 体系 + 阶段 8 简化
- **1.x.x**：配置库完善阶段，向完全可用演进
- **2.x.x**：多领域示例 + CI 阶段
- **3.x.x**：工具链集成 + 可视化阶段
