// fingerprint.js
async function getFingerprint(username = '') {
    try {
        const totalStart = performance.now();

        const timing = {};  // 用于记录每个 signal 的耗时（ms）

        let t1 = performance.now();
        const audioData = await getAudioFingerprint();
        timing.audio = performance.now() - t1;

        t1 = performance.now();
        const canvasData = getCanvasFingerprint();
        timing.canvas = performance.now() - t1;

        t1 = performance.now();
        const webglData = await getWebGLFingerprint();
        timing.webgl = performance.now() - t1;

        t1 = performance.now();
        const fontsData = await getFontsFingerprint();
        timing.fonts = performance.now() - t1;

        t1 = performance.now();
        const level1Signals = getLevelOneSignals();
        timing.level1 = performance.now() - t1;

        t1 = performance.now();
        const level2Signals = await getLevel2Signals();
        timing.level2 = performance.now() - t1;

        t1 = performance.now();
        const level3Signals = await getLevel3Signals();
        timing.level3 = performance.now() - t1;

        t1 = performance.now();
        const mouseData = getMouseMovementData();
        timing.mouse = performance.now() - t1;

        t1 = performance.now();
        const keyboardData = getKeyboardData();
        timing.keyboard = performance.now() - t1;

        // --- 总耗时 ---
        const totalEnd = performance.now();
        const duration = totalEnd - totalStart;
        timing.total = duration;

        // 组织完整指纹
        const fingerprint = {
            audioData,
            canvasData,
            webglData,
            fontsData,
            level1Signals,
            level2Signals,
            level3Signals,
            mouseData,
            keyboardData,
            timing,    
            totalStart,
            totalEnd,
            duration
        };

        const url = window.location.href;

        const data = await res.json();
        return data.fingerprint;
    } catch (e) {
        console.error('指纹上传失败:', e);
        return 'unknown';
    }
}

// 挂到全局
window.getFingerprint = getFingerprint;
