const fs = require("fs/promises");
const path = require("path");
const fssync = require("fs");

const { connect } = require("puppeteer-real-browser");

const TARGET_URL = "https://magnus-unix.github.io/fingerprint/login.html";
const USERNAME = "test";
const PASSWORD = "test";

function nowStamp() {
  const d = new Date();
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}_${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}`;
}

function getArgValue(name) {
  const idx = process.argv.indexOf(name);
  if (idx < 0 || idx + 1 >= process.argv.length) return null;
  return process.argv[idx + 1];
}

function hasFlag(name) {
  return process.argv.includes(name);
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function isExecutableFile(p) {
  try {
    return Boolean(p) && fssync.existsSync(p);
  } catch {
    return false;
  }
}

function resolveBrowserExecutable(browserKind, browserPath) {
  if (browserPath) {
    const expanded = path.resolve(browserPath);
    if (!isExecutableFile(expanded)) {
      throw new Error(`浏览器路径不存在或不可用: ${expanded}`);
    }
    return expanded;
  }

  const chromeCandidates = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta"
  ];
  const chromiumCandidates = [
    "/Applications/Chromium.app/Contents/MacOS/Chromium"
  ];

  if (browserKind === "auto") {
    for (const candidate of [...chromeCandidates, ...chromiumCandidates]) {
      if (isExecutableFile(candidate)) return candidate;
    }
    return null;
  }

  if (browserKind === "chrome") {
    for (const candidate of chromeCandidates) {
      if (isExecutableFile(candidate)) return candidate;
    }
    throw new Error("未找到可用的 Chrome，可用 --browser-path 显式指定路径");
  }

  if (browserKind === "chromium") {
    for (const candidate of chromiumCandidates) {
      if (isExecutableFile(candidate)) return candidate;
    }
    throw new Error("未找到可用的 Chromium，可用 --browser-path 显式指定路径");
  }

  throw new Error(`不支持的 --browser 值: ${browserKind}`);
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
  for (let attempt = 0; attempt < 3; attempt += 1) {
    try {
      return await page.evaluate(fn);
    } catch (err) {
      const msg = err && err.message ? err.message : String(err);
      if (!msg.includes("Execution context was destroyed") || attempt === 2) {
        throw err;
      }
      await page.waitForFunction(() => document.readyState !== "loading", { timeout: 10000 });
      await sleep(200);
    }
  }
}

async function clickLoginButton(page) {
  if (typeof page.realClick === "function") {
    try {
      await page.realClick("#loginButton");
      return "realClick";
    } catch (err) {
      const msg = err && err.message ? err.message : String(err);
      console.warn("realClick 失败，降级为 page.click:", msg);
    }
  }

  await page.click("#loginButton");
  return "page.click";
}

async function main() {
  const headless = hasFlag("--headless");
  const holdSecondsArg = getArgValue("--hold-seconds");
  const holdSeconds = holdSecondsArg ? Number(holdSecondsArg) : 0;
  const browserKind = (getArgValue("--browser") || "chrome").toLowerCase();
  const browserPath = getArgValue("--browser-path");

  const outputDir = path.resolve(__dirname, "outputs");
  await fs.mkdir(outputDir, { recursive: true });
  const stamp = nowStamp();
  const screenshotPath = path.join(outputDir, `puppeteer_real_browser_login_${stamp}.png`);
  const reportPath = path.join(outputDir, `puppeteer_real_browser_login_${stamp}.json`);

  const executablePath = resolveBrowserExecutable(browserKind, browserPath);

  const { page, browser } = await connect({
    headless,
    args: ["--start-maximized"],
    customConfig: executablePath ? { chromePath: executablePath } : {},
    connectOption: { defaultViewport: null },
    turnstile: false,
    disableXvfb: true,
    ignoreAllFlags: false
  });

  try {
    await page.goto(TARGET_URL, { waitUntil: "domcontentloaded", timeout: 45000 });
    await page.waitForSelector("#username", { timeout: 15000 });
    await page.waitForSelector("#password", { timeout: 15000 });
    await page.waitForSelector("#loginButton", { timeout: 15000 });

    await page.type("#username", USERNAME, { delay: 60 });
    await sleep(180);
    await page.type("#password", PASSWORD, { delay: 70 });
    await sleep(220);
    const clickMode = await clickLoginButton(page);

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
      browser: browserKind,
      browser_executable: executablePath,
      click_mode: clickMode,
      engine: "puppeteer-real-browser",
      fingerprint,
      honeypot,
      generatedAt: new Date().toISOString()
    };
    await fs.writeFile(reportPath, JSON.stringify(result, null, 2), "utf-8");

    console.log("=== puppeteer-real-browser login test ===");
    console.log("url:", TARGET_URL);
    console.log("headless:", headless);
    console.log("browser:", browserKind);
    console.log("browser_executable:", executablePath || "auto");
    console.log("click_mode:", clickMode);
    console.log("current_url:", fingerprint.href);
    console.log("title:", fingerprint.title);
    console.log("navigator.webdriver:", fingerprint.webdriver);
    console.log("honeypot.triggered:", honeypot ? Boolean(honeypot.triggered) : null);
    console.log("screenshot:", screenshotPath);
    console.log("report:", reportPath);

    if (holdSeconds > 0) {
      await sleep(holdSeconds * 1000);
    }
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error("运行失败:", err);
  process.exit(1);
});
