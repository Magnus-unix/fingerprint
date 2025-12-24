(function () {
  const MAX_HISTORY_LENGTH = 1000;
  const ANALYSIS_WINDOW_MS = 10000;

  const stats = {
    qs: 0,
    layoutReads: 0,
    timestamps: [],
    ops: [],

    // --- 新增：行为耦合指标 ---
    domAfterHumanCount: 0,
    domDuringKeyCount: 0,
    preClickDomCount: 0
  };

  // --- 人类事件状态 ---
  let lastHumanEventTs = performance.now();
  let keydownActive = false;
  let lastClickTs = null;

  // --- 事件监听 ---
  ['mousemove', 'mousedown', 'keydown', 'keyup', 'scroll', 'touchstart'].forEach(e => {
    addEventListener(e, evt => {
      lastHumanEventTs = performance.now();
      if (evt.type === 'keydown') keydownActive = true;
      if (evt.type === 'keyup') keydownActive = false;
    }, { passive: true });
  });

  addEventListener('click', () => {
    lastClickTs = performance.now();
  }, { passive: true });

  function isIgnoredNode(node) {
    return node && node.closest && node.closest('[data-dom-ignore]');
  }

  function record(type, node) {
    if (node && isIgnoredNode(node)) return;
    const now = performance.now();

    stats[type]++;
    stats.timestamps.push(now);
    stats.ops.push(type === 'qs' ? 1 : 2);

    // --- ① DOM-after-Human ---
    if (now - lastHumanEventTs >= 0 && now - lastHumanEventTs <= 80) {
      stats.domAfterHumanCount++;
    }

    // --- ② DOM-during-Keydown ---
    if (keydownActive) {
      stats.domDuringKeyCount++;
    }

    // --- ③ Pre-click DOM ---
    if (lastClickTs && lastClickTs - now >= 0 && lastClickTs - now <= 120) {
      stats.preClickDomCount++;
    }

    // --- 内存保护 ---
    if (stats.timestamps.length > MAX_HISTORY_LENGTH) {
      stats.timestamps.shift();
      stats.ops.shift();
    }
  }

  // --- Hook DOM API ---
  const qs = Element.prototype.querySelector;
  Element.prototype.querySelector = function (sel) {
    record('qs', this);
    return qs.call(this, sel);
  };

  Element.prototype.getBoundingClientRect = function () {
    record('layoutReads', this);
    return gbr.call(this);
  };

  // --- 对外暴露 ---
  window.__domStats__ = stats;
  window.__domConfig__ = {
    ANALYSIS_WINDOW_MS
  };
})();


function analyzeBehavior() {
  const dom = window.__domStats__;
  const cfg = window.__domConfig__;
  if (!dom || !cfg) return null;

  const now = performance.now();
  const windowMs = cfg.ANALYSIS_WINDOW_MS;

  // 过滤最近 windowMs
  let startIndex = 0;
  for (let i = dom.timestamps.length - 1; i >= 0; i--) {
    if (now - dom.timestamps[i] > windowMs) {
      startIndex = i + 1;
      break;
    }
  }

  const recentTimestamps = dom.timestamps.slice(startIndex);
  const recentOps = dom.ops.slice(startIndex);

  let burstCount = 0;
  let layoutCount = 0;
  let minInterval = Infinity;

  for (let i = 1; i < recentTimestamps.length; i++) {
    const delta = recentTimestamps[i] - recentTimestamps[i - 1];
    if (delta < 4) burstCount++;
    if (delta < minInterval) minInterval = delta;
    if (recentOps[i] === 2) layoutCount++;
  }

  return {
    windowMs,
    dom: {
      totalAccess: recentTimestamps.length,
      qsCount: recentOps.filter(op => op === 1).length,
      layoutCount,
      burstCount,
      minInterval: isFinite(minInterval) ? minInterval : null,

      // --- 新增三项 ---
      domAfterHumanCount: dom.domAfterHumanCount,
      domDuringKeyCount: dom.domDuringKeyCount,
      preClickDomCount: dom.preClickDomCount
    }
  };
}

window.getDomAnomaly = analyzeBehavior;
