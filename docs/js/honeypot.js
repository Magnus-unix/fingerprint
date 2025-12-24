// honeypot.js
(function () {
  const CONFIG = {
    CONTAINER_ID: 'layout-helper-wrapper-' + Math.random().toString(36).slice(2, 7),
    LINK_ID: 'skip-nav-' + Math.random().toString(36).slice(2, 7),
    INPUT_NAME: 'website_url_honeypot'
  };

  const report = {
    trapRendered: false,
    triggered: false,
    triggers: [],
    renderedAt: null
  };

  function markTriggered(type, detail) {
    report.triggered = true;
    report.triggers.push({
      type,
      detail,
      ts: performance.now()
    });
  }

  function createTrap() {
    const container = document.createElement('div');
    container.id = CONFIG.CONTAINER_ID;

    Object.assign(container.style, {
      position: 'absolute',
      left: '-9999px',
      top: '-9999px',
      width: '1px',
      height: '1px',
      overflow: 'hidden',
      opacity: '0.01',
      pointerEvents: 'none',
      zIndex: '-1'
    });

    // --- trap link ---
    const trapLink = document.createElement('a');
    trapLink.href = '#verify-session';
    trapLink.id = CONFIG.LINK_ID;
    trapLink.textContent = 'Click to verify user session';
    trapLink.tabIndex = -1;

    trapLink.addEventListener('click', e => {
      e.preventDefault();
      markTriggered('trap_click', { id: trapLink.id });
    });

    // --- trap input ---
    const trapInput = document.createElement('input');
    trapInput.type = 'text';
    trapInput.name = CONFIG.INPUT_NAME;
    trapInput.autocomplete = 'off';
    trapInput.tabIndex = -1;

    trapInput.addEventListener('focus', () => {
      markTriggered('trap_focus', { name: CONFIG.INPUT_NAME });
    });

    trapInput.addEventListener('input', e => {
      markTriggered('trap_fill', { valueLength: e.target.value.length });
    });

    container.appendChild(trapLink);
    container.appendChild(trapInput);
    document.body.appendChild(container);

    report.trapRendered = true;
    report.renderedAt = performance.now();
  }

  // 确保 DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createTrap);
  } else {
    createTrap();
  }

  // --- 对外只暴露 getter ---
  Object.defineProperty(window, '__honeypotStats__', {
    get() {
      return {
        trapRendered: report.trapRendered,
        triggered: report.triggered,
        triggerCount: report.triggers.length,
        triggers: report.triggers
      };
    }
  });
})();

function analyzeBehavior() {
  return {
    honeypot: window.__honeypotStats__ || null
  };
}

window.getHoneypot = analyzeBehavior;

