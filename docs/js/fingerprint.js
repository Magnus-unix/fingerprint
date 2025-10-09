// fingerprint.js
async function getFingerprint(username = '') {
    try {
        const startTime = performance.now();   

        const audioData = getAudioFingerprint();
        const canvasData = getCanvasFingerprint();
        const webglData = getWebGLFingerprint();
        const fontsData = getFontsFingerprint();
        const level1Signals = getLevelOneSignals();
        const level2Signals = await getLevel2Signals();
        const level3Signals = await getLevel3Signals();
        const mouseData = getMouseMovementData();
        const keyboardData = getKeyboardData();

        const endTime = performance.now();     
        const duration = endTime - startTime;

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
            startTime,
            endTime,
            duration
        };

        const url = window.location.href;

        const res = await fetch("https://skyeker.top/fingerprint", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, fingerprint, url }),
            credentials: 'include'
        });

        const data = await res.json();
        return data.fingerprint;
    } catch (e) {
        console.error('指纹上传失败:', e);
        return 'unknown';
    }
}

// 挂到全局
window.getFingerprint = getFingerprint;
