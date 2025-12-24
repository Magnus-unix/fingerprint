(function () {
  // 配置项
  window.__domConfig__ = {
    ANALYSIS_WINDOW_MS,   // 只分析最近 5 秒的行为
    MAX_HISTORY_LENGTH    // 只保留最近 1000 次 DOM 操作记录
  };

  const stats = {
    qs: 0,
    layoutReads: 0,
    // 改造：不再无限存储，而是虽然 push 但定期清理，或者用 RingBuffer
    timestamps: [],
    ops: [] // 额外记录操作类型，用于区分是 qs 还是 layout
  };

  function record(type) {
    const now = performance.now();
    stats[type]++;
    stats.timestamps.push(now);
    stats.ops.push(type === 'qs' ? 1 : 2); // 1: qs, 2: layout

    // 简单的内存保护：超过最大长度就剔除旧的
    if (stats.timestamps.length > MAX_HISTORY_LENGTH) {
      stats.timestamps.shift();
      stats.ops.shift();
    }
  }

  // Hook 逻辑保持不变...
  const qs = Element.prototype.querySelector;
  Element.prototype.querySelector = function (sel) {
    record('qs');
    return qs.call(this, sel);
  };

  const gbr = Element.prototype.getBoundingClientRect;
  Element.prototype.getBoundingClientRect = function () {
    record('layoutReads');
    return gbr.call(this);
  };

  window.__domStats__ = stats;
})();

// Human Hooks 保持不变...
let lastHumanEvent = { timestamp: performance.now(), type: 'load' };
['mousemove', 'mousedown', 'keydown', 'touchstart', 'scroll'].forEach(e => {
  addEventListener(e, (evt) => {
    lastHumanEvent.timestamp = performance.now();
    lastHumanEvent.type = evt.type;
  }, { passive: true });
});

// --- 改进后的分析逻辑 ---

function analyzeBehavior() {
  const dom = window.__domStats__;
  const config = window.__domConfig__;
  const now = performance.now();

  const windowMs = config.ANALYSIS_WINDOW_MS;
  if (!dom) return null;

  // 1. 只保留最近 ANALYSIS_WINDOW_MS
  let startIndex = 0;
  for (let i = dom.timestamps.length - 1; i >= 0; i--) {
    if (now - dom.timestamps[i] > windowMs) {
      startIndex = i + 1;
      break;
    }
  }

  const recentTimestamps = dom.timestamps.slice(startIndex);
  const recentOps = dom.ops.slice(startIndex);

  // 2. 统计指标
  let burstCount = 0;
  let layoutCount = 0;
  let layoutThrashingCount = 0;
  let minInterval = Infinity;

  for (let i = 1; i < recentTimestamps.length; i++) {
    const delta = recentTimestamps[i] - recentTimestamps[i - 1];

    if (delta < 4) burstCount++;
    if (delta < minInterval) minInterval = delta;

    if (recentOps[i] === 2) {
      layoutCount++;
      if (delta < 10) layoutThrashingCount++;
    }
  }

  const humanGap = now - lastHumanEvent.timestamp;

  return {
    windowMs: windowMs,
    dom: {
      totalAccess: recentTimestamps.length,
      qsCount: recentOps.filter(op => op === 1).length,
      layoutCount,
      burstCount,
      layoutThrashingCount,
      minInterval: isFinite(minInterval) ? minInterval : null
    },
    human: {
      timeSinceLastEvent: humanGap,
      lastEventType: lastHumanEvent.type
    }
  };
}

window.getDomAnomaly = analyzeBehavior;
