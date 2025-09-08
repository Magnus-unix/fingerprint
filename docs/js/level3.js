// static/level3.js
// static/level3.js (audio 部分改进)

async function getAudioFingerprint() {
    try {
        // 使用 OfflineAudioContext 生成离线音频数据
        const OfflineCtx = window.OfflineAudioContext || window.AudioContext;
        if (!OfflineCtx) {
            return { error: "OfflineAudioContext not supported" };
        }

        // 参数: 1 个声道, 5000 采样点, 采样率 44100Hz
        const context = new OfflineCtx(1, 5000, 44100);

        // 创建振荡器 (OscillatorNode) 作为信号源
        const oscillator = context.createOscillator();
        oscillator.type = "sine";   // 正弦波
        oscillator.frequency.value = 1000; // 频率 1kHz

        // 创建滤波器 (BiquadFilterNode)
        const filter = context.createBiquadFilter();
        filter.type = "lowpass"; // 低通滤波器
        filter.frequency.value = 1500;

        // 链接音频图：oscillator -> filter -> destination
        oscillator.connect(filter);
        filter.connect(context.destination);

        oscillator.start(0);

        // 渲染离线音频
        const buffer = await context.startRendering();

        // 取出前 10 个采样点作为 fingerprint
        const channelData = buffer.getChannelData(0);
        const sample = Array.from(channelData.slice(0, 10));

        // 简单计算「抖动特征」: 相邻差值方差
        let diffs = [];
        for (let i = 1; i < sample.length; i++) {
            diffs.push(sample[i] - sample[i - 1]);
        }
        const mean = diffs.reduce((a, b) => a + b, 0) / diffs.length;
        const variance = diffs.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / diffs.length;

        return {
            sample: sample.map(v => Number(v.toFixed(6))), // 固定精度
            jitterVariance: Number(variance.toFixed(8)),   // 抖动方差
        };
    } catch (e) {
        return { error: e.toString() };
    }
}

async function getRealtimeAudioFingerprint() {
    try {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (!AudioCtx) return { sample: null, jitterVar: null, error: "unsupported" };

        const ctx = new AudioCtx();
        const oscillator = ctx.createOscillator();
        const analyser = ctx.createAnalyser();

        // 配置
        analyser.fftSize = 2048; // 默认是 2048，越大频率分辨率越高
        oscillator.type = "sine";
        oscillator.frequency.value = 440; // A4 音

        oscillator.connect(analyser);
        analyser.connect(ctx.destination);
        oscillator.start();

        // 等待一段时间，确保缓冲区有数据
        await new Promise(resolve => setTimeout(resolve, 200));

        const array = new Float32Array(analyser.frequencyBinCount);
        analyser.getFloatFrequencyData(array);

        const sample = Array.from(array.slice(0, 5));

        // 计算 jitter 方差
        const diffs = [];
        for (let i = 1; i < 5; i++) {
            diffs.push(array[i] - array[i - 1]);
        }
        const mean = diffs.reduce((a, b) => a + b, 0) / diffs.length;
        const variance = diffs.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / diffs.length;

        oscillator.stop();
        ctx.close();

        return {
            sample,
            jitterVar: variance
        };

    } catch (e) {
        return { sample: null, jitterVar: null, error: e.toString() };
    }
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
        signals.audioSample = audioData.sample || [];
        signals.audioJitterVar = audioData.jitterVariance || 0;
    } catch (e) {
        signals.audioError = e.toString();
    }

    try{
        const audioResult = await getRealtimeAudioFingerprint();
        signals.realtimeAudioSample = audioResult.sample;
        signals.realtimeAudioJitterVar = audioResult.jitterVar;
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
