// static/level2.js
export async function getLevel2Signals() {
    const signals = {};

    // 基础属性
    signals.userAgent = navigator.userAgent || '';
    signals.platform = navigator.platform || '';
    signals.languages = navigator.languages || [];

    // UA 和 platform 一致性
    signals.uaPlatformMismatch = (signals.userAgent.includes("Windows") && signals.platform.toLowerCase().includes("linux")) ||
                                 (signals.userAgent.includes("Mac") && signals.platform.toLowerCase().includes("win"));

    // WebGL GPU 信息
    try {
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
        signals.gpuVendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
        signals.gpuRenderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
    } catch (e) {
        signals.gpuVendor = 'unknown';
        signals.gpuRenderer = 'unknown';
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
