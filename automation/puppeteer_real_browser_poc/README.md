# Puppeteer Real Browser Anti-Detect PoC

这个目录使用 puppeteer-real-browser 跑和你前面一致的登录自动化流程：

1. 打开 https://magnus-unix.github.io/fingerprint/login.html
2. 输入 test/test 并点击登录
3. 采集关键 anti-detect 指纹项
4. 保存截图和 JSON 报告

## 安装

```bash
cd /Users/magnus/project/fingerprint/automation/puppeteer_real_browser_poc
npm install
```

## 运行

```bash
npm run run
```

可选参数：

```bash
node run.js --headless
node run.js --hold-seconds 10
node run.js --browser chrome
node run.js --browser chromium
node run.js --browser auto
node run.js --browser-path "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
```

说明：

- 默认使用 --browser chrome，优先本机 Chrome，避免自动选到魔改 Chromium。
- 登录后如果发生页面跳转，脚本内置 evaluate 重试来规避上下文销毁竞态。

输出目录默认 outputs：

- puppeteer_real_browser_login_*.png
- puppeteer_real_browser_login_*.json
