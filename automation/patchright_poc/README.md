# Patchright Anti-Detect PoC

这个目录使用 `patchright-python` 跑你之前相同的流程：

1. 打开 `https://magnus-unix.github.io/fingerprint/login.html`
2. 输入 `test/test` 并点击登录
3. 采集关键 anti-detect 指纹项
4. 保存截图和 JSON 报告

## 安装

```bash
cd /Users/magnus/project/fingerprint/automation/patchright_poc
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

安装浏览器（参考 Patchright/Playwright 的常见流程）：

```bash
python -m patchright install chromium
```

如果你本机有 Chrome，也可直接走 `channel="chrome"`（脚本默认）。

## 运行

```bash
python run.py
```

可选参数：

```bash
python run.py --headless
python run.py --hold-seconds 10
python run.py --use-chromium-fallback
```

输出目录默认 `outputs/`：

- `patchright_login_*.png`
- `patchright_login_*.json`
