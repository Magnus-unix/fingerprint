# Selenium-Driverless Anti-Detect PoC

这个目录使用 [Selenium-Driverless](https://github.com/ttlns/Selenium-Driverless) 跑登录页自动化流程：

1. 打开 `https://magnus-unix.github.io/fingerprint/login.html`
2. 输入 `test/test` 并点击登录
3. 采集关键 anti-detect 指纹项
4. 保存截图和 JSON 报告

## 安装

```bash
cd /Users/magnus/project/fingerprint/automation/selenium_driverless_poc
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 运行

```bash
python run.py
```

可选参数：

```bash
python run.py --headless
python run.py --hold-seconds 10
python run.py --browser chrome
python run.py --browser chromium
python run.py --browser-path "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
```

说明：

- 默认 `--browser chrome`，优先使用本机 Chrome，避免自动选到魔改 Chromium。
- `--browser auto` 会按 Chrome -> Chromium 顺序探测可执行文件。
- 若登录后页面跳转较快，底层偶发上下文失效属于常见现象；脚本已内置自动重试。

输出目录默认 `outputs/`：

- `selenium_driverless_login_*.png`
- `selenium_driverless_login_*.json`
