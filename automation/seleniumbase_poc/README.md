# SeleniumBase Anti-Detect PoC (UC Mode)

这个目录用于测试 `SeleniumBase` 在登录场景下的 anti-detect 表现。

目标页面：

- `https://magnus-unix.github.io/fingerprint/login.html`

默认账号密码：

- `test / test`

## 1) 安装

```bash
cd /Users/magnus/project/fingerprint/automation/seleniumbase_poc
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2) 运行

```bash
python run.py
```

可选参数：

```bash
python run.py --headless
python run.py --hold-seconds 10
python run.py --username test --password test
```

## 3) 输出

运行后会在 `outputs/` 生成：

- `seleniumbase_login_*.png`（截图）
- `seleniumbase_login_*.json`（检测结果：`navigator.webdriver`、UA、`window.chrome.runtime`、honeypot 状态等）
