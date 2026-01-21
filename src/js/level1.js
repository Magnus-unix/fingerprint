// static/bot_detection.js level1
function getLevelOneSignals() {
    const signals = {};

    try {
        signals.webdriver = navigator.webdriver || false;
        signals.pluginsLength = navigator.plugins ? navigator.plugins.length : 0;
        signals.languages = navigator.languages || [];
        signals.hasChrome = !!window.chrome;
        signals.hasChromeRuntime = !!(window.chrome && window.chrome.runtime);
        signals.mimeTypesLength = navigator.mimeTypes ? navigator.mimeTypes.length : 0;
        signals.hardwareConcurrency = navigator.hardwareConcurrency || 0;
        signals.outerVsScreenWidth = window.outerWidth - screen.width;
        signals.userAgent = navigator.userAgent || '';
    } catch (e) {
        console.error("Bot signal collection error:", e);
    }

    return signals;
}

window.getLevelOneSignals = getLevelOneSignals;