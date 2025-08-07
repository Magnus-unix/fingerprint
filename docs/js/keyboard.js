// static/keyboard.js

const keystrokes = [];
let lastKeyTime = null;

document.addEventListener('keydown', (e) => {
    const now = Date.now();
    const interval = lastKeyTime ? now - lastKeyTime : 0;
    lastKeyTime = now;

    keystrokes.push({
        key: e.key.length === 1 ? '*' : e.key,
        timestamp: now,
        interval: interval
    });
});

export function getKeyboardData() {
    return {
        strokes: keystrokes,
        total: keystrokes.length,
        timestamp: Date.now()
    };
}
