const fs = require('fs/promises');
const path = require('path');

let puppeteer;
let StealthPlugin;
try {
  puppeteer = require('puppeteer-extra');
  StealthPlugin = require('puppeteer-extra-plugin-stealth');
} catch (err) {
  console.error('缺少依赖：请先安装 puppeteer stealth 相关包');
  console.error('npm i puppeteer puppeteer-extra puppeteer-extra-plugin-stealth');
  process.exit(1);
}

puppeteer.use(StealthPlugin());

const TARGET_URL = 'https://magnus-unix.github.io/fingerprint/login.html';
const USERNAME = 'test';
const PASSWORD = 'test';
const IS_HEADLESS = process.argv.includes('--headless');

function nowStamp() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}_${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`;
}

function scoreAntiDetect(data) {
  let score = 0;
  const checks = [];

  const webdriverOk = data?.fingerprint?.webdriver === false;
  checks.push({ name: 'navigator.webdriver === false', pass: webdriverOk });
  if (webdriverOk) score += 40;

  const pluginsOk = Number(data?.fingerprint?.pluginsLength || 0) > 0;
  checks.push({ name: 'navigator.plugins.length > 0', pass: pluginsOk });
  if (pluginsOk) score += 20;

  const languagesOk = Array.isArray(data?.fingerprint?.languages) && data.fingerprint.languages.length > 0;
  checks.push({ name: 'navigator.languages 非空', pass: languagesOk });
  if (languagesOk) score += 10;

  const chromeObjOk = Boolean(data?.fingerprint?.hasChromeObject);
  checks.push({ name: 'window.chrome 存在', pass: chromeObjOk });
  if (chromeObjOk) score += 10;

  const loginClicked = Boolean(data?.loginResult?.clicked);
  checks.push({ name: '登录按钮已点击', pass: loginClicked });
  if (loginClicked) score += 10;

  const honeypotSafe = !(data?.honeypot?.triggered);
  checks.push({ name: '未触发 honeypot', pass: honeypotSafe });
  if (honeypotSafe) score += 10;

  let level = 'weak';
  if (score >= 85) level = 'strong';
  else if (score >= 65) level = 'medium';

  return { score, level, checks };
}

async function run() {
  const outputDir = path.resolve(__dirname, 'outputs');
  await fs.mkdir(outputDir, { recursive: true });
  const stamp = nowStamp();
  const screenshotPath = path.join(outputDir, `puppeteer_stealth_login_${stamp}.png`);
  const reportPath = path.join(outputDir, `puppeteer_stealth_login_${stamp}.json`);

  const browser = await puppeteer.launch({
    headless: IS_HEADLESS ? 'new' : false,
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
    defaultViewport: { width: 1366, height: 900 }
  });

  try {
    const page = await browser.newPage();
    await page.goto(TARGET_URL, { waitUntil: 'domcontentloaded', timeout: 45000 });
    await page.waitForSelector('#username', { timeout: 15000 });
    await page.waitForSelector('#password', { timeout: 15000 });
    await page.waitForSelector('#loginButton', { timeout: 15000 });

    await page.type('#username', USERNAME, { delay: 60 });
    await new Promise(resolve => setTimeout(resolve, 200));
    await page.type('#password', PASSWORD, { delay: 70 });
    await new Promise(resolve => setTimeout(resolve, 300));

    const loginResult = await page.evaluate(() => {
      const btn = document.querySelector('#loginButton');
      if (!btn) return { clicked: false, reason: 'missing_button' };
      btn.click();
      return { clicked: true, reason: 'clicked' };
    });

    await new Promise(resolve => setTimeout(resolve, 2200));

    const fingerprint = await page.evaluate(() => ({
      webdriver: navigator.webdriver,
      userAgent: navigator.userAgent,
      platform: navigator.platform,
      languages: navigator.languages,
      vendor: navigator.vendor,
      hardwareConcurrency: navigator.hardwareConcurrency,
      pluginsLength: navigator.plugins ? navigator.plugins.length : 0,
      hasChromeObject: typeof window.chrome !== 'undefined',
      title: document.title,
      href: location.href
    }));

    const honeypot = await page.evaluate(() => window.__honeypotStats__ || null);
    await page.screenshot({ path: screenshotPath, fullPage: true });

    const result = {
      url: TARGET_URL,
      username: USERNAME,
      headless: IS_HEADLESS,
      loginResult,
      fingerprint,
      honeypot,
      generatedAt: new Date().toISOString()
    };
    result.assessment = scoreAntiDetect(result);

    await fs.writeFile(reportPath, JSON.stringify(result, null, 2), 'utf-8');

    console.log('=== puppeteer stealth login test ===');
    console.log('url:', TARGET_URL);
    console.log('loginResult:', loginResult);
    console.log('navigator.webdriver:', fingerprint.webdriver);
    console.log('honeypot.triggered:', honeypot ? Boolean(honeypot.triggered) : null);
    console.log('assessment:', result.assessment);
    console.log('screenshot:', screenshotPath);
    console.log('report:', reportPath);
  } finally {
    await browser.close();
  }
}

run().catch((err) => {
  console.error('运行失败:', err);
  process.exit(1);
});
