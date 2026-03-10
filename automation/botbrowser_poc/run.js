const fs = require("fs/promises");
const fssync = require("fs");
const os = require("os");
const path = require("path");
const { chromium } = require("playwright-core");


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

function getExecutablePath() {
  const envPath = process.env.BOTBROWSER_EXEC_PATH;
  if (envPath && fssync.existsSync(envPath)) return envPath;

  const defaults = [
    "/Applications/BotBrowser.app/Contents/MacOS/BotBrowser",
    "/Applications/Bot Browser.app/Contents/MacOS/Bot Browser"
  ];
  for (const p of defaults) {
    if (fssync.existsSync(p)) return p;
  }
  return null;
}

async function main() {
  const headless = hasFlag("--headless");
  const executablePath = getExecutablePath();
  if (!executablePath) {
    throw new Error(
      "BotBrowser executable not found. Set BOTBROWSER_EXEC_PATH to your BotBrowser binary path."
    );
  }

  const botProfile = process.env.BOTBROWSER_PROFILE_PATH || "";
  const userDataDir = fssync.mkdtempSync(path.join(os.tmpdir(), "botbrowser-poc-"));

  const outputDir = path.resolve(__dirname, "outputs");
  await fs.mkdir(outputDir, { recursive: true });
  const stamp = nowStamp();
  const screenshotPath = path.join(outputDir, `botbrowser_login_${stamp}.png`);
  const reportPath = path.join(outputDir, `botbrowser_login_${stamp}.json`);

  const args = ["--no-sandbox", "--disable-setuid-sandbox"];
  if (botProfile) args.push(`--bot-profile=${botProfile}`);

  const browser = await chromium.launch({
    executablePath,
    headless,
    args
  });

  try {
    const context = await browser.newContext({
      viewport: { width: 1366, height: 900 }
    });

    // Common anti-detect hardening used with Playwright-based tools.
    await context.addInitScript(() => {
      delete globalThis.__pwInitScripts;
      delete globalThis.__playwright__binding__;
    });

    const page = await context.newPage();
    await page.goto(TARGET_URL, { waitUntil: "domcontentloaded", timeout: 45000 });
    await page.waitForSelector("#username", { timeout: 15000 });
    await page.waitForSelector("#password", { timeout: 15000 });
    await page.waitForSelector("#loginButton", { timeout: 15000 });

    await page.type("#username", USERNAME, { delay: 60 });
    await sleep(180);
    await page.type("#password", PASSWORD, { delay: 70 });
    await sleep(240);
    await page.click("#loginButton");
    await sleep(2200);

    const fingerprint = await page.evaluate(() => ({
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

    const honeypot = await page.evaluate(() => window.__honeypotStats__ || null);

    await page.screenshot({ path: screenshotPath, fullPage: true });

    const result = {
      url: TARGET_URL,
      username: USERNAME,
      headless,
      engine: "botbrowser+playwright-core",
      executablePath,
      botProfileUsed: botProfile || null,
      userDataDir,
      fingerprint,
      honeypot,
      generatedAt: new Date().toISOString()
    };

    await fs.writeFile(reportPath, JSON.stringify(result, null, 2), "utf-8");

    console.log("=== botbrowser login test ===");
    console.log("url:", TARGET_URL);
    console.log("headless:", headless);
    console.log("executablePath:", executablePath);
    console.log("botProfile:", botProfile || "(none)");
    console.log("current_url:", fingerprint.href);
    console.log("title:", fingerprint.title);
    console.log("navigator.webdriver:", fingerprint.webdriver);
    console.log("honeypot.triggered:", honeypot ? Boolean(honeypot.triggered) : null);
    console.log("screenshot:", screenshotPath);
    console.log("report:", reportPath);

    await context.close();
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error("运行失败:", err);
  process.exit(1);
});
