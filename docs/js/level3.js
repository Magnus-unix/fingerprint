// static/level3.js
export async function getLevel3Signals() {
    const signals = {};

    // 1. 环境完整性
    try {
        signals.fontsCount = (document.fonts && document.fonts.size) || 0;
        signals.hasMediaDevices = !!(navigator.mediaDevices && navigator.mediaDevices.enumerateDevices);
        signals.hasSpeechSynthesis = typeof speechSynthesis !== 'undefined';
        signals.intlTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        signals.dateTimeZoneOffset = new Date().getTimezoneOffset();
    } catch (e) {
        signals.envError = e.toString();
    }

    // 2. 图形与音频
    try {
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl');
        if (gl) {
            const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
            signals.webglVendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
            signals.webglRenderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
        }
    } catch (e) {
        signals.webglError = e.toString();
    }

    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioCtx.createOscillator();
        const analyser = audioCtx.createAnalyser();
        oscillator.connect(analyser);
        oscillator.start();
        const array = new Float32Array(analyser.frequencyBinCount);
        analyser.getFloatFrequencyData(array);
        signals.audioSample = array.slice(0, 5); // 取前 5 个点作为 fingerprint
        oscillator.stop();
        audioCtx.close();
    } catch (e) {
        signals.audioError = e.toString();
    }

    // 3. 执行上下文
    signals.requestIdleCallbackSupported = typeof requestIdleCallback === 'function';
    signals.queueMicrotaskSupported = typeof queueMicrotask === 'function';
    signals.touchEventSupported = typeof TouchEvent !== 'undefined';
    signals.pointerEventSupported = typeof PointerEvent !== 'undefined';

    // 简单测试 requestIdleCallback 是否能执行
    signals.idleCallbackExecuted = false;
    if (signals.requestIdleCallbackSupported) {
        await new Promise(resolve => {
            requestIdleCallback(() => {
                signals.idleCallbackExecuted = true;
                resolve();
            }, { timeout: 100 });
        });
    }

    // 4. Chrome DevTools 残留
    signals.hasReactDevTools = !!window.__REACT_DEVTOOLS_GLOBAL_HOOK__;
    signals.hasDevtools = !!window.devtools;

    return signals;
}
