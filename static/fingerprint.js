// static/fingerprint.js
import { getAudioFingerprint } from './audio.js';
import { getFontsFingerprint } from './fonts.js';
import { getCanvasFingerprint } from './canvas.js';
import { getWebGLFingerprint } from './webgl.js';
import { getMouseMovementData } from './mousemove.js';
import { getKeyboardData } from './keyboard.js';
import { getDOMFingerprint } from './domtree.js';

export async function getFingerprint(username = '') {
    try {
            const audio = await getAudioFingerprint();
            const fonts = await getFontsFingerprint();
            const canvas = await getCanvasFingerprint();
            const webgl = await getWebGLFingerprint();
            const mouse = getMouseMovementData();
            const keyboard = getKeyboardData();
            const dom = getDOMFingerprint();
    
            const fingerprint = { audio, fonts, canvas, webgl, mouse, keyboard, dom };
    
            const res = await fetch('http://localhost:8081/fingerprint', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, fingerprint })
            });
    
            const data = await res.json();
            return data.fingerprint;  
        } catch (e) {
            console.error('指纹上传失败:', e);
            return 'unknown';
    }
}
    
