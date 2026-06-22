# Changelog

## [0.1.0] - 2026-06-22

### 新增
- 🆕 初始版本(v3.0 工具链集成)
- 🆕 4 个命令:
  - `applySkill` — 应用 skill 到当前工作区
  - `runSmokeTest` — 跑 smoke-test.sh 自检
  - `renderFlowChart` — ASCII 流程图 → Mermaid → SVG/PNG
  - `openDocumentation` — 快速打开项目文档
- 🆕 配置项:
  - `analysisToDelivery.skillsPath` — skill 安装路径
  - `analysisToDelivery.mermaidCli` — mermaid-cli 路径
  - `analysisToDelivery.defaultFormat` — 输出格式(svg/png)
- 🆕 上下文菜单集成(`.txt` 文件含"业务流程图"时显示 Render Flow Chart)
- 🆕 自动激活事件(workspace 包含 BRD / TASK_CONFIRM 时激活)