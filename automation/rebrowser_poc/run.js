const fs = require("fs/promises");
const path = require("path");
const fssync = require("fs");

const puppeteer = require("rebrowser-puppeteer");

const TARGET_URL = "https://magnus-unix.github.io/fingerprint/login.html";
const USERNAME = "test";
const PASSWORD = "test";

function nowStamp() {
  const d = new Date();
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}_${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}`;
}

function hasFlag(name) {
  return process.argv.includes(name);
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function waitPostLoginStable(page) {
  try {
    await page.waitForFunction(
      () => location.pathname.endsWith("/test.html"),
      { timeout: 12000 }
    );
    await page.waitForNavigation({ waitUntil: "domcontentloaded", timeout: 10000 });
    return;
  } catch (_) {
    // Login may fail and stay on the same page; just ensure DOM is stable enough.
  }

  await page.waitForFunction(() => document.readyState !== "loading", { timeout: 10000 });
}

async function evaluateWithRetry(page, fn) {
  for (let attempt = 0; attempt < 2; attempt += 1) {
    try {
      return await page.evaluate(fn);
    } catch (err) {
      const msg = err && err.message ? err.message : String(err);
      if (!msg.includes("Execution context was destroyed") || attempt === 1) {
        throw err;
      }
      await page.waitForFunction(() => document.readyState !== "loading", { timeout: 10000 });
    }
  }
}

async function main() {
  const headless = hasFlag("--headless");
  const outputDir = path.resolve(__dirname, "outputs");
  await fs.mkdir(outputDir, { recursive: true });
  const stamp = nowStamp();
  const screenshotPath = path.join(outputDir, `rebrowser_login_${stamp}.png`);
  const reportPath = path.join(outputDir, `rebrowser_login_${stamp}.json`);

  const executablePath = findLocalChrome();
  const browser = await puppeteer.launch({
    headless: headless ? "new" : false,
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
    defaultViewport: { width: 1366, height: 900 },
    executablePath
  });

  try {
    const page = await browser.newPage();
    await page.goto(TARGET_URL, { waitUntil: "domcontentloaded", timeout: 45000 });
    await page.waitForSelector("#username", { timeout: 15000 });
    await page.waitForSelector("#password", { timeout: 15000 });
    await page.waitForSelector("#loginButton", { timeout: 15000 });

    await page.type("#username", USERNAME, { delay: 60 });
    await sleep(180);
    await page.type("#password", PASSWORD, { delay: 70 });
    await sleep(220);
    await page.click("#loginButton");
    await waitPostLoginStable(page);

    const fingerprint = await evaluateWithRetry(page, () => ({
      webdriver: navigator.webdriver,
      userAgent: navigator.userAgent,
      platform: navigator.platform,
      vendor: navigator.vendor,
      languages: navigator.languages,
      hardwareConcurrency: navigator.hardwareConcurrency,
      pluginsLength: navigator.plugins ? navigator.plugins.length : 0,
      hasChromeRuntime: !!(window.chrome && window.chrome.runtime),
      title: document.title,
      href: location.href
    }));

    const honeypot = await evaluateWithRetry(page, () => window.__honeypotStats__ || null);
    await page.screenshot({ path: screenshotPath, fullPage: true });

    const result = {
      url: TARGET_URL,
      username: USERNAME,
      headless,
      engine: "rebrowser-puppeteer",
      fingerprint,
      honeypot,
      generatedAt: new Date().toISOString()
    };
    await fs.writeFile(reportPath, JSON.stringify(result, null, 2), "utf-8");

    console.log("=== rebrowser patches login test ===");
    console.log("url:", TARGET_URL);
    console.log("headless:", headless);
    console.log("executablePath:", executablePath || "auto");
    console.log("current_url:", fingerprint.href);
    console.log("title:", fingerprint.title);
    console.log("navigator.webdriver:", fingerprint.webdriver);
    console.log("honeypot.triggered:", honeypot ? Boolean(honeypot.triggered) : null);
    console.log("screenshot:", screenshotPath);
    console.log("report:", reportPath);
  } finally {
    await browser.close();
  }
}

function findLocalChrome() {
  const candidates = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta",
    "/Applications/Chromium.app/Contents/MacOS/Chromium"
  ];
  for (const p of candidates) {
    if (fssync.existsSync(p)) return p;
  }
  return undefined;
}

main().catch((err) => {
  console.error("运行失败:", err);
  process.exit(1);
});
