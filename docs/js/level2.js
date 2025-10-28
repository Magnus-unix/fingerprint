// static/level2.js

async function getLevel2Signals() {
    const signals = {};

    // 基础属性
    signals.userAgent = navigator.userAgent || '';
    signals.platform = navigator.platform || '';
    signals.languages = navigator.languages || [];

    // UA 和 platform 一致性
    signals.uaPlatformMismatch = (signals.userAgent.includes("Windows") && signals.platform.toLowerCase().includes("linux")) ||
                                 (signals.userAgent.includes("Mac") && signals.platform.toLowerCase().includes("win")) ||
                                 (signals.userAgent.includes("linux") && signals.platform.toLocaleLowerCase().includes("mac"));

    // ✅ WebGL
    try {
        const webglData = await getWebGLFingerprint();
        signals.gpuVendor = webglData.vendorUnmasked || webglData.vendor || "unknown";
        signals.gpuRenderer = webglData.rendererUnmasked || webglData.renderer || "unknown";
    } catch (e) {
        signals.gpuVendor = "error";
        signals.gpuRenderer = "error";
    }
    
    // Permissions API
    try {
        const perm = await navigator.permissions.query({name: 'notifications'});
        signals.notificationPermission = perm.state;
    } catch {
        signals.notificationPermission = 'error';
    }

    // window.chrome 内部结构检测
    signals.hasChromeApp = !!(window.chrome && window.chrome.app);
    signals.hasChromeRuntime = !!(window.chrome && window.chrome.runtime);

    // 屏幕与窗口大小
    signals.screenVsWindowMismatch = (screen.width !== window.innerWidth) || (screen.height !== window.innerHeight);

    // deviceMemory 与 hardwareConcurrency
    signals.deviceMemory = navigator.deviceMemory || 0;
    signals.hardwareConcurrency = navigator.hardwareConcurrency || 0;

    return signals;
}

window.getLevel2Signals = getLevel2Signals;