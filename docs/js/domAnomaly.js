(function () {

  function getDOMFingerprint() {
    const logs = [];

    function log(type, msg) {
      logs.push({
        type,
        msg,
        ts: Date.now()
      });
    }

    // ===============================
    // Strategy A: Ghost Honeypot
    // ===============================
    function injectHoneypot() {
      const trap = document.createElement('input');
      trap.type = 'text';
      trap.name = 'email_confirmation';
      trap.id = 'confirm_user_entry';
      trap.tabIndex = -1;
      trap.autocomplete = 'off';

      Object.assign(trap.style, {
        position: 'absolute',
        left: '-9999px',
        top: '0',
        opacity: '0.01',
        height: '1px',
        width: '1px',
        pointerEvents: 'none'
      });

      const handler = () => {
        log('ghost_interaction', 'ghost input was focused or modified');
      };

      trap.addEventListener('focus', handler);
      trap.addEventListener('input', handler);
      trap.addEventListener('change', handler);

      document.body.appendChild(trap);
    }

    // ===============================
    // Strategy B: Input Anomaly Monitor
    // ===============================
    function monitorInputs() {
      const inputs = document.querySelectorAll(
        'input[type="text"], input[type="password"]'
      );

      inputs.forEach(input => {
        let lastKeyTs = 0;

        input.addEventListener('keydown', () => {
          const now = Date.now();
          if (lastKeyTs && now - lastKeyTs < 5) {
            log('super_human_speed', `keystroke interval: ${now - lastKeyTs}ms`);
          }
          lastKeyTs = now;
        });

        input.addEventListener('input', (e) => {
          if (!e.isTrusted) {
            log('untrusted_event', 'input event is not trusted');
          }
          if (e.inputType === 'insertFromPaste') {
            log('paste_detected', 'paste detected');
          }
        });
      });
    }

    // ===============================
    // Execute (idempotent)
    // ===============================
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => {
        injectHoneypot();
        monitorInputs();
      });
    } else {
      injectHoneypot();
      monitorInputs();
    }

    // ===============================
    // Public result interface
    // ===============================
    return {
      type: 'dom_anomaly_probe',
      logs,
      collectedAt: Date.now()
    };
  }

  // 暴露统一接口（与 domTree 保持一致）
  window.getDOMFingerprint = getDOMFingerprint;

})();
