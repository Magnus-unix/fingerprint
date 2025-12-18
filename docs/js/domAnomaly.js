(function () {

  function initDOMAnomalyProbe() {
    const logs = [];

    function log(type, msg) {
      logs.push({
        type,
        msg,
        ts: Date.now()
      });
    }

    // ===============================
    // 启动监听（关键）
    // ===============================
    function start() {

      // A. 注入 honeypot
      const trap = document.createElement('input');
      trap.type = 'text';
      trap.name = 'email_confirmation';
      trap.tabIndex = -1;

      Object.assign(trap.style, {
        position: 'absolute',
        left: '-9999px',
        opacity: '0.01'
      });

      const trigger = () => log('honeypot', 'ghost input touched');
      trap.addEventListener('focus', trigger);
      trap.addEventListener('input', trigger);

      document.body.appendChild(trap);

      // B. 监听真实输入框
      document.querySelectorAll('input').forEach(input => {
        let last = 0;

        input.addEventListener('keydown', () => {
          const now = Date.now();
          if (last && now - last < 5) {
            log('speed', `superhuman typing: ${now - last}ms`);
          }
          last = now;
        });

        input.addEventListener('input', e => {
          if (!e.isTrusted) {
            log('untrusted', 'script-generated input');
          }
        });
      });
    }

    // ⚠️ 立即启动
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', start);
    } else {
      start();
    }

    // ===============================
    // 对外只暴露 export
    // ===============================
    return {
      type: 'dom_anomaly_probe',
      export() {
        return {
          logs: [...logs],
          count: logs.length,
          collectedAt: Date.now()
        };
      }
    };
  }

  window.initDOMAnomalyProbe = initDOMAnomalyProbe;

})();
