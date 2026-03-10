# GeekEZ Browser PoC (Attach Mode)

你已经安装了 release 版后，这里推荐用 **Attach Mode** 做自动化：

1. 手工打开 GeekEZ Browser
2. 在 profile 里开启 Remote Debugging（记下端口）
3. 脚本通过 CDP 端口接入，执行登录与信号采集

## 1) 安装依赖

```bash
cd /Users/magnus/project/fingerprint/automation/geekezbrowser_poc
npm install
```

## 2) 开启 GeekEZ 的远程调试

在 GeekEZ Browser 的 profile 配置里启用 remote debugging，记下端口（示例 `9222`）。
```bash
"/Applications/GeekEZ Browser.app/Contents/MacOS/GeekEZ Browser" --remote-debugging-port=9222
```

## 3) 运行自动化登录

```bash
cd /Users/magnus/project/fingerprint/automation/geekezbrowser_poc
export GEEKEZ_CDP_PORT=9222
npm run login
```

输出目录：`outputs/`

- `geekez_login_*.png`
- `geekez_login_*.json`

## 说明

- 这个脚本不负责启动 GeekEZ，而是附加到已启动实例。
- 如果报错 `Timeout connecting to .../json/version`，通常是端口未开启或端口号不对。
- 你之前出现的 `EADDRINUSE 127.0.0.1:12139` 是应用内部服务端口冲突，不是 CDP 端口本身。
