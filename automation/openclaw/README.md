# OpenClaw 自动化浏览器 PoC

这个目录使用 `openclaw` 代理编排框架测试自动化浏览器的反指纹防御能力：

1. 打开 `https://magnus-unix.github.io/fingerprint/login.html`
2. 输入 `test/test` 并点击登录
3. 监控指纹采集请求 POST `/fingerprint`
4. 分析 Honeypot 陷阱触发情况
5. 保存截图和 JSON 报告

## 安装

```bash
cd /Users/magnus/project/fingerprint/automation/openclaw
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 运行

### 基础使用（默认配置）

```bash
python run.py
```

### 进阶选项

```bash
# 无头模式
python run.py --headless

# 登录后停留 10 秒（便于观察）
python run.py --hold-seconds 10

# 自定义登录信息
python run.py --username admin --password 123456

# 自定义输出目录
python run.py --output-dir my_results

# 多次迭代测试（对标性能）
python run.py --iterations 5
```

## 输出

默认输出目录 `outputs/`：

- `openclaw_login_*.png` - 登录页面截图
- `openclaw_login_*.json` - 指纹和 Honeypot 数据
- `openclaw_summary_*.json` - 汇总报告（多次迭代时）

## 测试指标

| 指标 | 说明 |
|------|------|
| `webdriver` | 是否被检测为自动化（应为 false） |
| `honeypot_triggered` | 是否触发了隐藏陷阱（应为 false） |
| `ua_consistency` | UA 与实际属性一致性评分 |
| `audio_jitter` | 音频指纹抖动率 |
| `login_success` | 是否成功跳转至 /test |

## 与其他 POC 对标

- **nodriver_poc**: 轻量级 async Python 框架，专注指纹检测
- **patchright_poc**: Playwright 增强版，支持 Chrome persistent context
- **seleniumbase_poc**: UC 不可检测模式，最强反检测能力
- **openclaw**: 代理编排框架，支持多种协议和代理配置
