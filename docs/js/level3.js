// static/level3.js

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
async function getRealtimeAudioFingerprint(timeoutMs = 5000) {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) {
        return { sample: null, jitterVar: null, error: "unsupported" };
    }

    try {
        const ctx = new AudioCtx();

        // 若被挂起，则等待用户交互
        if (ctx.state === "suspended") {
            let resolved = false;

            // 监听一次用户交互
            const resumeOnGesture = () => {
                if (!resolved) {
                    resolved = true;
                    document.removeEventListener("click", resumeOnGesture);
                    document.removeEventListener("keydown", resumeOnGesture);
                    document.removeEventListener("touchstart", resumeOnGesture);
                    ctx.resume().then(runAnalysis).catch(() => {
                        resolveResult("blocked_by_autoplay_policy");
                    });
                }
            };

            const resolveResult = (errorType) => {
                resolved = true;
                document.removeEventListener("click", resumeOnGesture);
                document.removeEventListener("keydown", resumeOnGesture);
                document.removeEventListener("touchstart", resumeOnGesture);
                resolve({
                    sample: null,
                    jitterVar: null,
                    error: errorType,
                });
            };

            return await new Promise((resolve) => {
                const timer = setTimeout(() => {
                    if (!resolved) resolveResult("blocked_by_autoplay_policy");
                }, timeoutMs);

                document.addEventListener("click", resumeOnGesture);
                document.addEventListener("keydown", resumeOnGesture);
                document.addEventListener("touchstart", resumeOnGesture);

                async function runAnalysis() {
                    clearTimeout(timer);
                    const result = await analyzeAudio(ctx);
                    resolve(result);
                }
            });
        }

        // 若没被挂起，直接采集
        return await analyzeAudio(ctx);
    } catch (e) {
        return { sample: null, jitterVar: null, error: e.toString() };
    }

    // 实际音频采集逻辑
    async function analyzeAudio(ctx) {
        const oscillator = ctx.createOscillator();
        const analyser = ctx.createAnalyser();
        analyser.fftSize = 2048;
        oscillator.type = "sine";
        oscillator.frequency.value = 440;

        oscillator.connect(analyser);
        analyser.connect(ctx.destination);
        oscillator.start();

        await new Promise((r) => setTimeout(r, 200));

        const array = new Float32Array(analyser.frequencyBinCount);
        analyser.getFloatFrequencyData(array);

        const sample = Array.from(array.slice(0, 5));
        const diffs = [];
        for (let i = 1; i < sample.length; i++) diffs.push(sample[i] - sample[i - 1]);
        const mean = diffs.reduce((a, b) => a + b, 0) / diffs.length;
        const variance = diffs.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / diffs.length;

        oscillator.stop();
        ctx.close();

        return { sample, jitterVar: variance };
    }
}

async function getLevel3Signals() {
    const signals = {};

    // 1. 环境完整性
    try {
        const availableFonts = await getFontsFingerprint();
        signals.fontsCount = availableFonts.length;
        //signals.fontsList = availableFonts; // 如果要看具体字体，可以加上
    } catch (e) {
        signals.fontsError = e.toString();
    }

    try {
        signals.hasMediaDevices = !!(navigator.mediaDevices && navigator.mediaDevices.enumerateDevices);
        signals.hasSpeechSynthesis = typeof speechSynthesis !== 'undefined';
        signals.intlTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        signals.dateTimeZoneOffset = new Date().getTimezoneOffset();
    } catch (e) {
        signals.envError = e.toString();
    }

    // 2. 图形与音频
    try {
        const webglData = await getWebGLFingerprint();
        signals.gpuVendor = webglData.vendorUnmasked || webglData.vendor || "unknown";
        signals.gpuRenderer = webglData.rendererUnmasked || webglData.renderer || "unknown";
    } catch (e) {
        signals.gpuVendor = "error";
        signals.gpuRenderer = "error";
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

window.getLevel3Signals = getLevel3Signals;