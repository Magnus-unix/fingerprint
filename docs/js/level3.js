// static/level3.js
import { getFontsFingerprint } from './fonts.js';
import { getWebGLFingerprint } from './webgl.js';
import { getCanvasFingerprint } from './canvas.js';
import { getAudioFingerprint } from './audio.js';

function average(arr) {
    if (!arr || arr.length === 0) return 0;
    return arr.reduce((a, b) => a + b, 0) / arr.length;
}

function stddev(arr) {
    if (!arr || arr.length === 0) return 0;
    const avg = average(arr);
    const variance = arr.reduce((sum, val) => sum + Math.pow(val - avg, 2), 0) / arr.length;
    return Math.sqrt(variance);
}

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
        const audioData = await getAudioFingerprint();
        signals.audioSample = audioData.sample ? audioData.sample.slice(0, 10) : [];
        signals.audioMean = average(signals.audioSample);
        signals.audioStd = stddev(signals.audioSample);
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
