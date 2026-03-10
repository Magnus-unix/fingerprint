const fs = require('fs/promises');
const path = require('path');
const http = require('http');
const { chromium } = require('playwright-core');

const TARGET_URL = 'https://magnus-unix.github.io/fingerprint/login.html';
const USERNAME = 'test';
const PASSWORD = 'test';

function nowStamp() {
  const d = new Date();
  const p = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}_${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}`;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function hasFlag(name) {
  return process.argv.includes(name);
}

async function getWsEndpoint(port) {
  const url = `http://127.0.0.1:${port}/json/version`;
  return new Promise((resolve, reject) => {
    const req = http.get(url, (res) => {
      if (res.statusCode !== 200) {
        reject(new Error(`CDP endpoint status ${res.statusCode} from ${url}`));
        return;
      }
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          if (!json.webSocketDebuggerUrl) {
            reject(new Error(`No webSocketDebuggerUrl in ${url}`));
            return;
          }
          resolve(json.webSocketDebuggerUrl);
        } catch (e) {
          reject(e);
        }
      });
    });
    req.on('error', reject);
    req.setTimeout(3000, () => {
      req.destroy(new Error(`Timeout connecting to ${url}`));
    });
  });
}

async function main() {
  const port = Number(process.env.GEEKEZ_CDP_PORT || process.env.DEBUG_PORT || 9222);
  const headlessHint = hasFlag('--headless');
  const outputDir = path.resolve(__dirname, 'outputs');
  await fs.mkdir(outputDir, { recursive: true });

  const stamp = nowStamp();
  const screenshotPath = path.join(outputDir, `geekez_login_${stamp}.png`);
  const reportPath = path.join(outputDir, `geekez_login_${stamp}.json`);

  const wsEndpoint = await getWsEndpoint(port);
  const browser = await chromium.connectOverCDP(wsEndpoint);

  let context;
  let page;
  try {
    context = browser.contexts()[0] || (await browser.newContext());
    page = context.pages()[0] || (await context.newPage());

    await page.goto(TARGET_URL, { waitUntil: 'domcontentloaded', timeout: 45000 });
    await page.waitForSelector('#username', { timeout: 15000 });
    await page.waitForSelector('#password', { timeout: 15000 });
    await page.waitForSelector('#loginButton', { timeout: 15000 });

    await page.fill('#username', USERNAME);
    await sleep(250);
    await page.fill('#password', PASSWORD);
    await sleep(300);
    await page.click('#loginButton');
    await sleep(2200);

    const fingerprint = await page.evaluate(() => ({
      webdriver: navigator.webdriver,
      userAgent: navigator.userAgent,
      platform: navigator.platform,
      vendor: navigator.vendor,
      language: navigator.language,
      languages: navigator.languages,
      hardwareConcurrency: navigator.hardwareConcurrency,
      pluginsLength: navigator.plugins ? navigator.plugins.length : 0,
      hasChromeRuntime: !!(window.chrome && window.chrome.runtime),
      title: document.title,
      href: location.href
    }));

    const honeypot = await page.evaluate(() => window.__honeypotStats__ || null);
    await page.screenshot({ path: screenshotPath, fullPage: true });

    const result = {
      cdpPort: port,
      wsEndpoint,
      headlessHint,
      url: TARGET_URL,
      username: USERNAME,
      fingerprint,
      honeypot,
      generatedAt: new Date().toISOString()
    };
    await fs.writeFile(reportPath, JSON.stringify(result, null, 2), 'utf-8');

    console.log('=== geekez browser attach login test ===');
    console.log('cdp_port:', port);
    console.log('ws_endpoint:', wsEndpoint);
    console.log('current_url:', fingerprint.href);
    console.log('title:', fingerprint.title);
    console.log('navigator.webdriver:', fingerprint.webdriver);
    console.log('honeypot.triggered:', honeypot ? Boolean(honeypot.triggered) : null);
    console.log('screenshot:', screenshotPath);
    console.log('report:', reportPath);
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error('运行失败:', err.message || err);
  console.error('提示: 先在 GeekEZ Browser profile 设置里开启 Remote Debugging，并确认端口。');
  process.exit(1);
});
