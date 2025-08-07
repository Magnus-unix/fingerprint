// static/mousemove.js

const mouseMovements = [];
let lastEventTime = Date.now();

document.addEventListener('mousemove', (e) => {
    const now = Date.now();
    const x = e.clientX;
    const y = e.clientY;
    const dt = now - lastEventTime;
    lastEventTime = now;

    mouseMovements.push({ x, y, t: now });
});

function analyzeMouseData(data) {
    const features = [];

    for (let i = 1; i < data.length; i++) {
        const dx = data[i].x - data[i - 1].x;
        const dy = data[i].y - data[i - 1].y;
        const dt = data[i].t - data[i - 1].t;
        const distance = Math.sqrt(dx * dx + dy * dy);
        const speed = dt > 0 ? distance / dt : 0;

        features.push({ dx, dy, dt, speed });
    }

    return features;
}

export function getMouseMovementData() {
    return {
        raw: mouseMovements,
        features: analyzeMouseData(mouseMovements),
        timestamp: Date.now()
    };
}
