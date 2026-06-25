/**
 * Analysis to Delivery — VSCode 扩展入口
 *
 * 提供 4 个命令:
 * - applySkill        应用 skill 到当前工作区
 * - runSmokeTest      跑 smoke-test.sh 自检
 * - renderFlowChart   ASCII 流程图 → Mermaid → SVG/PNG
 * - openDocumentation 打开文档
 *
 * 注意:本扩展是一个轻量包装,把命令桥接到 ~/.claude/skills/analysis-to-delivery
 * 下的脚本(smoke-test.sh / flow-export.sh)。Claude Code / Hermes 仍然是主入口,
 * 扩展只是提供一个 IDE 内的快捷方式。
 *
 * 详细使用见 README.md。
 */

import * as cp from "child_process";
import * as fs from "fs";
import * as path from "path";
import * as vscode from "vscode";

const SKILL_SCRIPTS = [
  "smoke-test.sh",
  "flow-export.sh",
  "flow-to-mermaid.py",
];

interface SkillConfig {
  skillsPath: string;
  mermaidCli: string;
  defaultFormat: "svg" | "png";
}

function getConfig(): SkillConfig {
  const cfg = vscode.workspace.getConfiguration("analysisToDelivery");
  return {
    skillsPath: cfg.get<string>("skillsPath") || "",
    mermaidCli: cfg.get<string>("mermaidCli") || "mmdc",
    defaultFormat: cfg.get<"svg" | "png">("defaultFormat") || "svg",
  };
}

function resolveSkillsPath(configPath: string): string | null {
  // 处理 ${userHome} 占位符
  const expanded = configPath.replace(/\$\{userHome\}/g, process.env.HOME || "");
  if (fs.existsSync(expanded) && fs.existsSync(path.join(expanded, "SKILL.md"))) {
    return expanded;
  }
  // 兜底:常见安装位置
  const candidates = [
    path.join(process.env.HOME || "", ".claude/skills/analysis-to-delivery"),
    path.join(process.env.HOME || "", ".hermes/skills/analysis-to-delivery"),
    "/usr/local/share/claude/skills/analysis-to-delivery",
  ];
  for (const c of candidates) {
    if (fs.existsSync(path.join(c, "SKILL.md"))) {
      return c;
    }
  }
  return null;
}

function execScript(
  scriptName: string,
  args: string[],
  cwd: string,
): Promise<{ stdout: string; stderr: string; code: number }> {
  return new Promise((resolve, reject) => {
    const proc = cp.spawn(scriptName, args, {
      cwd,
      env: { ...process.env, FORCE_COLOR: "0" },
    });
    let stdout = "";
    let stderr = "";
    proc.stdout.on("data", (d) => (stdout += d.toString()));
    proc.stderr.on("data", (d) => (stderr += d.toString()));
    proc.on("error", reject);
    proc.on("close", (code) => resolve({ stdout, stderr, code: code || 0 }));
  });
}

async function applySkillCommand(): Promise<void> {
  const cfg = getConfig();
  const skillsPath = resolveSkillsPath(cfg.skillsPath);
  if (!skillsPath) {
    void vscode.window.showErrorMessage(
      "Analysis to Delivery:未找到已安装的 skill。" +
        `请在配置中设置 analysisToDelivery.skillsPath,或将 skill 安装到 ~/.claude/skills/analysis-to-delivery/`,
    );
    return;
  }

  const skillNames = [
    "setup-analysis-delivery",
    "grill-task",
    "to-brd",
    "compliance-review",
    "test-case-design",
    "to-prd",
    "dev-design",
    "qa-audit",
    "handoff",
  ];

  const pick = await vscode.window.showQuickPick(skillNames, {
    title: "选择要应用的 skill",
    placeHolder: "9 个 user-invoked skill(v1.4+)",
  });
  if (!pick) {
    return;
  }

  const skillDir = path.join(skillsPath, "skills/user-invoked", pick);
  if (!fs.existsSync(path.join(skillDir, "SKILL.md"))) {
    void vscode.window.showErrorMessage(`Skill 不存在:${skillDir}`);
    return;
  }

  // 打开 SKILL.md 供 Claude 读取
  const doc = await vscode.workspace.openTextDocument(path.join(skillDir, "SKILL.md"));
  await vscode.window.showTextDocument(doc);

  // 提示用户在 Claude Chat 中触发
  const choice = await vscode.window.showInformationMessage(
    `已打开 skill:${pick}\n\n复制命令到 Claude:`,
    { modal: false },
    "复制到剪贴板",
    "打开 README",
  );

  if (choice === "复制到剪贴板") {
    await vscode.env.clipboard.writeText(`/${pick}`);
    void vscode.window.showInformationMessage("已复制到剪贴板。粘贴到 Claude Chat 即可触发。");
  } else if (choice === "打开 README") {
    await vscode.env.openExternal(
      vscode.Uri.parse("https://github.com/BlueprintOS/analysis-to-delivery"),
    );
  }
}

async function runSmokeTestCommand(): Promise<void> {
  const cfg = getConfig();
  const skillsPath = resolveSkillsPath(cfg.skillsPath);
  if (!skillsPath) {
    void vscode.window.showErrorMessage(
      "未找到 skill 路径。请在 settings.json 中设置 analysisToDelivery.skillsPath",
    );
    return;
  }

  const scriptPath = path.join(skillsPath, "scripts", "smoke-test.sh");
  if (!fs.existsSync(scriptPath)) {
    void vscode.window.showErrorMessage(`smoke-test.sh 不存在:${scriptPath}`);
    return;
  }

  const term = vscode.window.createTerminal({
    name: "Smoke Test",
    cwd: skillsPath,
  });
  term.show();
  term.sendText(`bash "${scriptPath}"`);
}

async function renderFlowChartCommand(uri?: vscode.Uri): Promise<void> {
  const cfg = getConfig();
  const skillsPath = resolveSkillsPath(cfg.skillsPath);
  if (!skillsPath) {
    void vscode.window.showErrorMessage("未找到 skill 路径。请在 settings.json 中设置 analysisToDelivery.skillsPath");
    return;
  }

  // 如果从右键菜单调用,uri 已传入;否则要求用户选择文件
  let target = uri;
  if (!target) {
    const picks = await vscode.window.showOpenDialog({
      title: "选择 ASCII 流程图文件(.txt)",
      filters: { "Text files": ["txt"] },
    });
    if (!picks || picks.length === 0) {
      return;
    }
    target = picks[0];
  }

  if (!target.fsPath.includes("业务流程图")) {
    void vscode.window.showWarningMessage("文件命名不以 '业务流程图-' 开头,可能不是流程图文件。继续执行...");
  }

  const scriptPath = path.join(skillsPath, "scripts", "flow-export.sh");
  if (!fs.existsSync(scriptPath)) {
    void vscode.window.showErrorMessage(`flow-export.sh 不存在:${scriptPath}`);
    return;
  }

  const outDir = path.join(path.dirname(target.fsPath), "rendered");
  const term = vscode.window.createTerminal({
    name: "Flow Export",
    cwd: path.dirname(target.fsPath),
  });
  term.show();
  term.sendText(`bash "${scriptPath}" "${target.fsPath}" ${cfg.defaultFormat} "${outDir}"`);

  // 提示用户查看输出
  const choice = await vscode.window.showInformationMessage(
    `渲染命令已发送。输出目录:${outDir}`,
    "打开输出目录",
  );
  if (choice === "打开输出目录") {
    void vscode.commands.executeCommand("revealFileInOS", vscode.Uri.file(outDir));
  }
}

async function openDocumentationCommand(): Promise<void> {
  const cfg = getConfig();
  const skillsPath = resolveSkillsPath(cfg.skillsPath);
  const readmePath = skillsPath ? path.join(skillsPath, "README.md") : null;

  const choices: vscode.QuickPickItem[] = [
    { label: "README.md", description: "项目主页" },
    { label: "SKILL.md", description: "Skill 入口说明" },
    { label: "plan.md", description: "项目路线图" },
    { label: "CHANGELOG.md", description: "版本历史" },
    { label: "CONTRIBUTING.md", description: "贡献指南" },
    { label: "examples/", description: "示例目录(3 个)" },
    { label: "GitHub Repository", description: "在线文档" },
  ];

  const pick = await vscode.window.showQuickPick(choices, {
    title: "打开文档",
  });
  if (!pick) {
    return;
  }

  if (pick.label === "GitHub Repository") {
    await vscode.env.openExternal(
      vscode.Uri.parse("https://github.com/BlueprintOS/analysis-to-delivery"),
    );
    return;
  }

  if (!skillsPath) {
    void vscode.window.showErrorMessage("未找到 skill 路径");
    return;
  }

  const p = pick.label === "examples/"
    ? path.join(skillsPath, "examples")
    : path.join(skillsPath, pick.label);

  if (fs.existsSync(p)) {
    if (fs.statSync(p).isDirectory()) {
      void vscode.commands.executeCommand("revealFileInOS", vscode.Uri.file(p));
    } else {
      const doc = await vscode.workspace.openTextDocument(p);
      await vscode.window.showTextDocument(doc);
    }
  } else {
    void vscode.window.showErrorMessage(`文件不存在:${p}`);
  }
}

export function activate(context: vscode.ExtensionContext): void {
  context.subscriptions.push(
    vscode.commands.registerCommand("analysis-to-delivery.applySkill", applySkillCommand),
    vscode.commands.registerCommand("analysis-to-delivery.runSmokeTest", runSmokeTestCommand),
    vscode.commands.registerCommand(
      "analysis-to-delivery.renderFlowChart",
      (uri?: vscode.Uri) => renderFlowChartCommand(uri),
    ),
    vscode.commands.registerCommand("analysis-to-delivery.openDocumentation", openDocumentationCommand),
  );

  // 激活时检查 skill 路径,缺失则提示
  const cfg = getConfig();
  if (!resolveSkillsPath(cfg.skillsPath)) {
    void vscode.window.showWarningMessage(
      "Analysis to Delivery:未检测到已安装的 skill。" +
        "运行 `bash install.sh` 安装,或在设置中调整 analysisToDelivery.skillsPath",
    );
  }
}

export function deactivate(): void {
  // 清理资源(如需)
}