# Analysis to Delivery — VSCode 扩展

> **注意**:各 agent 仍然是主入口。本扩展只是一个轻量包装,
> 把命令桥接到 `<SKILL_ROOT>/analysis-to-delivery` 下的脚本。

## 功能

提供 4 个命令:

| 命令 | 标题 | 说明 |
|---|---|---|
| `analysis-to-delivery.applySkill` | Apply Analysis-to-Delivery Skill | 弹出 skill 选择器,打开对应 SKILL.md,并复制 `/<skill>` 命令到剪贴板 |
| `analysis-to-delivery.runSmokeTest` | Run Smoke Test | 在终端跑 `smoke-test.sh`,验证 26 个 skill 完整性 |
| `analysis-to-delivery.renderFlowChart` | Render Flow Chart | 把 ASCII 流程图(.txt)转为 Mermaid → SVG/PNG |
| `analysis-to-delivery.openDocumentation` | Open Documentation | 快速打开 README / SKILL / plan / CHANGELOG |

## 安装

### 从源码安装(开发模式)

```bash
cd vscode-extension
npm install
npm run compile
# 在 VSCode 中按 F5 启动 Extension Development Host
```

### 打包 .vsix

```bash
cd vscode-extension
npm install
npm run package
# 生成 analysis-to-delivery-4.0.0.vsix
code --install-extension analysis-to-delivery-4.0.0.vsix
```

### 配置

打开 VSCode `settings.json`,加入:

```json
{
  "analysisToDelivery.skillsPath": "${userHome}/.codex/skills/analysis-to-delivery",
  "analysisToDelivery.mermaidCli": "mmdc",
  "analysisToDelivery.defaultFormat": "svg"
}
```

**前置依赖**:

1. **skill 已安装**:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/BlueprintOS/analysis-to-delivery/main/install.sh | bash
   ```

2. **mermaid-cli**(可选,仅 renderFlowChart 需要):
   ```bash
   npm install -g @mermaid-js/mermaid-cli
   ```

## 使用示例

### 1. 应用 skill

1. 按 `Ctrl+Shift+P`(macOS: `Cmd+Shift+P`)
2. 输入 "Analysis to Delivery: Apply Skill"
3. 选择 `to-brd`
4. VSCode 打开 `to-brd/SKILL.md`,命令已复制到剪贴板
5. 切换到你的 agent,粘贴 `/to-brd` 或用自然语言触发

### 2. 跑 smoke test

1. 命令面板 → "Analysis to Delivery: Run Smoke Test"
2. 终端显示 76 ✅ / 0 ⚠️ / 0 ❌ 即通过

### 3. 渲染流程图

1. 在 `examples/02-saas-dashboard/业务流程图-订单状态流转.txt` 上右键
2. 选择 "Analysis to Delivery: Render Flow Chart"
3. 或命令面板 → 同名命令 → 选择文件
4. 输出到 `examples/02-saas-dashboard/rendered/`

## 架构

```
VSCode 扩展 (本目录)
  ↓ 调用
<SKILL_ROOT>/analysis-to-delivery/scripts/
  ├── smoke-test.sh       ← runSmokeTest
  ├── flow-export.sh      ← renderFlowChart
  └── flow-to-mermaid.py  ← renderFlowChart(子步骤)
  ↓ 依赖
mermaid-cli (mmdc)
```

**设计原则**:扩展只做"命令转发 + 文件打开",所有业务逻辑仍在原 skill 脚本中。
这样 skill 升级时,扩展无需重新打包。

## 开发

### 目录结构

```
vscode-extension/
├── package.json          # 扩展清单
├── src/
│   └── extension.ts      # 入口
├── tsconfig.json
├── .eslintrc.json
├── .vscodeignore
├── resources/
│   └── icon.svg          # 扩展图标
└── README.md             # 本文件
```

### 调试

1. 在 VSCode 中打开本目录
2. 按 F5 → 启动 Extension Development Host
3. 在新窗口测试命令

### 发布

```bash
# 创建发布者(首次)
npm install -g @vscode/vsce
vsce create-publisher BlueprintOS

# 打包
vsce package

# 发布
vsce publish
```

## 路线图

| 版本 | 功能 |
|---|---|
| 4.0.0(当前)| 4 个基础命令 + 自动激活 |
| 0.2.0(计划)| 自定义 skill 面板(Webview)|
| 0.3.0(计划)| 集成 Claude API(直接对话)|
| 1.0.0(计划)| 发布到 VSCode Marketplace |

## 反馈

- 🐛 [GitHub Issues](https://github.com/BlueprintOS/analysis-to-delivery/issues)
- 💡 [Feature Request](https://github.com/BlueprintOS/analysis-to-delivery/issues/new?template=feature_request.md)

## 协议

MIT — 与主项目保持一致