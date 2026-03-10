# nodriver anti-detect PoC

这个目录是一个最小可跑的 `nodriver` 试验，用来快速验证浏览器自动化下的指纹表现。

## 目录

- `run.py`: 启动浏览器，访问检测页，采集关键指纹字段，保存截图和 JSON 报告
- `requirements.txt`: Python 依赖
- `outputs/`: 运行后自动生成（截图 + 报告）

## 安装

```bash
cd /Users/magnus/project/fingerprint/automation/nodriver_poc
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 运行

默认访问 `https://bot.sannysoft.com`：

```bash
python run.py
```

常见参数：

```bash
# 指定检测 URL
python run.py --url https://arh.antoinevastel.com/bots/areyouheadless

# 无头模式
python run.py --headless

# 截图后停留 10 秒（方便观察）
python run.py --hold-seconds 10
```

运行成功后会打印：

- `navigator.webdriver` 值
- 截图路径
- JSON 报告路径

## 登录页自动登录测试

默认访问 `https://magnus-unix.github.io/fingerprint/login.html`，并使用 `test/test` 自动填写和点击登录：

```bash
python login_test.py
```

可选参数：

```bash
python login_test.py --headless
python login_test.py --hold-seconds 10
python login_test.py --username test --password test
```
