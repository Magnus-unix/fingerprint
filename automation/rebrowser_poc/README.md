# Rebrowser Patches PoC

这个目录复用你之前的流程：

1. 打开 `https://magnus-unix.github.io/fingerprint/login.html`
2. 输入 `test/test` 并点击登录
3. 采集关键 anti-detect 指纹项
4. 输出截图和 JSON 报告

## 快速方式（官方 drop-in 包）

这里默认使用 `rebrowser-puppeteer`（官方推荐的 drop-in 体验）。
脚本会优先使用本机 Chrome 可执行文件（macOS 默认路径）。

安装与运行：

```bash
cd /Users/magnus/project/fingerprint/automation/rebrowser_poc
export PUPPETEER_SKIP_DOWNLOAD=1
npm install
npm run run
```

如果你之前安装失败过（下载包损坏），建议先清理后重装：

```bash
cd /Users/magnus/project/fingerprint/automation/rebrowser_poc
rm -rf node_modules package-lock.json
rm -rf ~/.cache/puppeteer
export PUPPETEER_SKIP_DOWNLOAD=1
npm install
npm run run
```

无头模式：

```bash
npm run run:headless
```

输出在 `outputs/`：

- `rebrowser_login_*.png`
- `rebrowser_login_*.json`

## 严格 patch 模式（直接使用 rebrowser-patches）

如果你想严格对 `puppeteer-core` 打补丁，可参考官方仓库命令流程：

```bash
npm i puppeteer-core rebrowser-patches
npx rebrowser-patches patch --packageName puppeteer-core
```

然后脚本里改为引入被补丁后的 `puppeteer-core` 启动浏览器即可。
