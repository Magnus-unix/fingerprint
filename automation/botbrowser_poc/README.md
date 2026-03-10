# BotBrowser PoC

这个 PoC 复用你之前的流程：

1. 打开 `https://magnus-unix.github.io/fingerprint/login.html`
2. 自动输入 `test/test` 并点击登录
3. 采集关键指纹项 + honeypot 状态
4. 保存截图和 JSON 报告

## 准备

这个脚本基于 `playwright-core` 启动 BotBrowser 可执行文件。

请先设置环境变量（按你的实际安装路径修改）：

```bash
export BOTBROWSER_EXEC_PATH="/Applications/BotBrowser.app/Contents/MacOS/BotBrowser"
# 可选：如果你有 bot profile 文件
export BOTBROWSER_PROFILE_PATH="/Users/magnus/project/fingerprint/automation/botbrowser_poc/chrome145_mac_arm64.enc"
```

## 安装与运行

```bash
cd /Users/magnus/project/fingerprint/automation/botbrowser_poc
npm install
npm run run
```

无头：

```bash
npm run run:headless
```

## 输出

输出目录：`outputs/`

- `botbrowser_login_*.png`
- `botbrowser_login_*.json`
