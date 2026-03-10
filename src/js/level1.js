// Level 1: Basic Attribute Detection
function getLevelOneSignals() {
    const signals = {};

    try {
        // Navigator & browser identity
        signals.userAgent = safeRead(() => navigator.userAgent, "");
        signals.appVersion = safeRead(() => navigator.appVersion, "");
        signals.buildID = safeRead(() => navigator.buildID || null, null); // Firefox-only in many cases
        signals.productSub = safeRead(() => navigator.productSub || null, null);
        signals.platform = safeRead(() => navigator.platform, "");
        signals.oscpu = safeRead(() => navigator.oscpu || null, null); // Usually Firefox-only
        signals.vendor = safeRead(() => navigator.vendor, "");
        signals.language = safeRead(() => navigator.language, "");
        signals.languages = safeRead(() => navigator.languages || [], []);

        // Screen basic info
        signals.screenColorDepth = safeRead(() => window.screen.colorDepth, null);

        // Hardware basic info
        signals.hardwareConcurrency = safeRead(() => navigator.hardwareConcurrency || 0, 0);
        signals.maxTouchPoints = safeRead(() => navigator.maxTouchPoints || 0, 0);

        // Storage/cookie status
        signals.storage = {
            localStorage: inspectStorage("localStorage"),
            sessionStorage: inspectStorage("sessionStorage"),
            cookie: inspectCookie()
        };
    } catch (e) {
        console.error("Level 1 signal collection error:", e);
    }

    return signals;
}

function safeRead(fn, fallback) {
    try {
        const value = fn();
        return value === undefined ? fallback : value;
    } catch (e) {
        return fallback;
    }
}

function inspectStorage(type) {
    const result = {
        supported: false,
        enabled: false,
        length: null,
        error: null
    };

    try {
        const store = window[type];
        result.supported = !!store;
        if (!store) return result;

        const probeKey = "__fp_probe__";
        store.setItem(probeKey, "1");
        result.enabled = store.getItem(probeKey) === "1";
        store.removeItem(probeKey);
        result.length = store.length;
        return result;
    } catch (e) {
        result.error = String(e);
        return result;
    }
}

function inspectCookie() {
    const result = {
        supported: safeRead(() => navigator.cookieEnabled, false),
        enabled: false,
        length: 0,
        error: null
    };

    try {
        const key = "__fp_cookie_probe__";
        document.cookie = `${key}=1; path=/; SameSite=Lax`;
        result.enabled = document.cookie.indexOf(`${key}=1`) !== -1;
        result.length = document.cookie ? document.cookie.length : 0;
        document.cookie = `${key}=; Max-Age=0; path=/; SameSite=Lax`;
        return result;
    } catch (e) {
        result.error = String(e);
        return result;
    }
}

window.getLevelOneSignals = getLevelOneSignals;
