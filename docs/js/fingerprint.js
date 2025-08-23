import { getAudioFingerprint } from './audio.js';
import { getFontsFingerprint } from './fonts.js';
import { getCanvasFingerprint } from './canvas.js';
import { getWebGLFingerprint } from './webgl.js';
import { getMouseMovementData } from './mousemove.js';
import { getKeyboardData } from './keyboard.js';
import { getLevelOneSignals } from './level1.js';
import { getLevel2Signals } from './level2.js';
import { getLevel3Signals } from './level3.js';

function getBeijingTime() {
    return new Date().toLocaleString("zh-CN", { timeZone: "Asia/Shanghai" });
}

export async function getFingerprint(username = '') {
    try {
        const startTime = getBeijingTime();

        const audio = await getAudioFingerprint();
        const fonts = await getFontsFingerprint();
        const canvas = await getCanvasFingerprint();
        const webgl = await getWebGLFingerprint();
        const mouse = getMouseMovementData();
        const keyboard = getKeyboardData();
        const level1Signals = getLevelOneSignals();
        const level2Signals = await getLevel2Signals();
        const level3Signals = await getLevel3Signals();

        const endTime = getBeijingTime();

        const fingerprint = {
            audio,
            fonts,
            canvas,
            webgl,
            mouse,
            keyboard,
            level1Signals,
            level2Signals,
            level3Signals,
            startTime,   // 👈 新增
            endTime      // 👈 新增
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
