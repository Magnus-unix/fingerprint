# Camoufox Anti-Detect PoC

这个目录使用 `camoufox` 跑与你前面一致的流程：

1. 打开 `https://magnus-unix.github.io/fingerprint/login.html`
2. 输入 `test/test` 并点击登录
3. 采集关键 anti-detect 指纹项
4. 保存截图和 JSON 报告

## 重要说明

`Camoufox` 的核心是定制 Firefox 栈，不是本机 Chrome 驱动。
如果你要“优先本机 Chrome”，建议继续使用你已有的 `patchright_poc` / `seleniumbase_poc`。

## 安装

```bash
cd /Users/magnus/project/fingerprint/automation/camoufox_poc
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
```

输出目录默认在 `outputs/`：

- `camoufox_login_*.png`
- `camoufox_login_*.json`
