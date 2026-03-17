# llm_scraper_poc 安装与使用指南

本目录用于在你的 `automation` 体系里快速落地 [llm-scraper](https://github.com/mishushakov/llm-scraper) 方案。

目标：

1. 独立目录安装，不污染根目录依赖
2. 使用 Playwright + LLM 提取结构化数据
3. 保持和你其他 POC 一样的运行习惯

## 1. 环境要求

建议环境：

- macOS
- Node.js 20+
- npm 10+

检查版本：

```bash
node -v
npm -v
```

## 2. 进入目录

```bash
cd /Users/magnus/project/fingerprint/automation/llm_scraper_poc
```

## 3. 初始化 Node 项目

```bash
npm init -y
```

把 `package.json` 的 `type` 改为 `module`（llm-scraper 是 ESM 风格，更稳）。

你也可以直接执行：

```bash
npm pkg set type=module
```

## 4. 安装依赖

安装核心依赖：

```bash
npm i llm-scraper playwright ai zod @ai-sdk/openai
```

如果你想用本地模型（Ollama）而不是 OpenAI：

```bash
npm i llm-scraper playwright ai zod ollama-ai-provider-v2
```

## 5. 安装 Playwright 浏览器内核

```bash
npx playwright install
```

如果缺系统依赖（一般 macOS 不常见）：

```bash
npx playwright install-deps
```

## 6. 配置环境变量

创建 `.env` 文件（仅本目录使用）：

```bash
cat > .env << 'EOF'
OPENAI_API_KEY=your_api_key_here
EOF
```

## 7. 最小可运行示例（可选）

创建 `run.mjs`：

```js
import 'dotenv/config'
import { chromium } from 'playwright'
import { z } from 'zod'
import { Output } from 'ai'
import { openai } from '@ai-sdk/openai'
import LLMScraper from 'llm-scraper'

const browser = await chromium.launch({ headless: false })
const page = await browser.newPage()
await page.goto('https://magnus-unix.github.io/fingerprint/login.html', {
  waitUntil: 'domcontentloaded',
})

const model = openai('gpt-5.2')
const scraper = new LLMScraper(model)

const schema = z.object({
  title: z.string(),
  href: z.string(),
  hasLoginButton: z.boolean(),
})

const { data } = await scraper.run(
  page,
  Output.object({ schema }),
  {
    format: 'html',
  }
)

console.log(data)

await page.close()
await browser.close()
```

如果你用到了 `.env`，还需要安装：

```bash
npm i dotenv
```

运行：

```bash
npm run run
```

脚本会做三件事：

1. 自动以 `test/test` 登录页面
2. 登录后调用 `llm-scraper` 按 schema 做结构化抽取
3. 输出截图和 JSON 报告到 `outputs/`

输出文件示例：

- `outputs/login_after_*.png`
- `outputs/llm_crawl_*.json`
- `outputs/llm_extracted_*.json`

其中 `llm_crawl_*.json` 会包含：

- 登录状态和基础页面信息
- 图片加载统计（total/loaded/failed）
- LLM 提取的结构化数据（标题、链接、表单、摘要、下一步建议等）

`llm_extracted_*.json` 是纯爬取结果（只含结构化字段），便于你后续直接给别的脚本消费。

即使 LLM 调用失败，也会保留 `llm_crawl_*.json`，并在其中记录 `llmError` 方便排查。

## 8. 常见问题

### Q1: 报错 Cannot use import statement outside a module

说明项目不是 ESM 模式。确认：

- `package.json` 中存在 `"type": "module"`
- 使用的是 `.mjs` 或 ESM 风格的 `.js`

### Q2: Playwright 启动失败

先执行：

```bash
npx playwright install
```

再重试。

### Q3: OpenAI 鉴权失败

确认：

- `.env` 里的 `OPENAI_API_KEY` 正确
- 当前终端在本目录
- 网络可访问 OpenAI 接口

### Q4: APICallError / Connect Timeout（你明明开了代理）

这是 Node 进程未必自动读取代理环境变量导致的常见问题。你可以用下面命令强制走代理：

```bash
npm run run:proxy
```

如果要手动执行，也可以先导出大写变量再运行：

```bash
export HTTP_PROXY=http://127.0.0.1:7897
export HTTPS_PROXY=http://127.0.0.1:7897
export NODE_USE_ENV_PROXY=1
npm run run
```

快速判断思路：

- `curl https://api.openai.com/v1/models` 能返回 `401`，说明网络可达
- `node fetch` 仍超时，说明 Node 没走代理

## 9. 推荐目录结构

```text
llm_scraper_poc/
├─ README.md
├─ package.json
├─ package-lock.json
├─ .env
├─ run.mjs
└─ outputs/
```

你后续可以把抽取结果写入 `outputs/`，便于和 `camoufox_poc`、`rebrowser_poc` 做横向对比。
