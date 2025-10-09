const WINDOW_MS = 500;
const MIN_PUSH_INTERVAL = 8; // 可调：如果事件非常密集，低于此间隔则尝试“合并”到最后一条，避免数组被刷爆

let mouseQueue = [];   // FIFO 队列，元素为 { x, y, t }
let lastPushTs = 0;

// 鼠标移动事件：只负责更新队列（即时 push + 清理过期）
function onMouseMove(e) {
  const now = Date.now();
  const x = e.clientX;
  const y = e.clientY;

  // 如果距离上次 push 很近，合并到最后一个点（减少条目但保留最新坐标）
  if (mouseQueue.length > 0 && (now - lastPushTs) < MIN_PUSH_INTERVAL) {
    const last = mouseQueue[mouseQueue.length - 1];
    last.x = x;
    last.y = y;
    last.t = now;
    lastPushTs = now;
    cleanup(now);
    return;
  }

  // 正常 push 新点
  mouseQueue.push({ x, y, t: now });
  lastPushTs = now;
  cleanup(now);
}

function cleanup(now = Date.now()) {
  const cutoff = now - WINDOW_MS;
  while (mouseQueue.length && mouseQueue[0].t < cutoff) {
    mouseQueue.shift();
  }
}

// 导出接口：返回当前窗口内的原始点（返回副本，避免外部修改内部队列）
function getMouseMovementData() {
  const now = Date.now();
  cleanup(now);
  return {
    raw: mouseQueue.slice(), 
    count: mouseQueue.length,
    timestamp: now,
    windowMs: WINDOW_MS
  };
}

// 分析函数
function analyzeMouseData(rawArray) {
  const features = [];
  if (!Array.isArray(rawArray) || rawArray.length < 2) return features;
  for (let i = 1; i < rawArray.length; i++) {
    const a = rawArray[i - 1];
    const b = rawArray[i];
    const dx = b.x - a.x;
    const dy = b.y - a.y;
    const dt = b.t - a.t;
    const speed = dt > 0 ? Math.hypot(dx, dy) / dt : 0; // px / ms
    features.push({ dx, dy, dt, speed });
  }
  return features;
}

window.getMouseMovementData = getMouseMovementData;

document.addEventListener('mousemove', onMouseMove, { passive: true });
