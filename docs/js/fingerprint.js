// fingerprint.js
async function getFingerprint(username = '') {
    try {
        const startTime = performance.now();   

        const level1Signals = getLevelOneSignals();
        const level2Signals = await getLevel2Signals();
        const level3Signals = await getLevel3Signals();

        const endTime = performance.now();     
        const duration = endTime - startTime;

        const fingerprint = {
            level1Signals,
            level2Signals,
            level3Signals,
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
