// Apply the preference before the stylesheet loads to avoid a theme flash.
(() => {
  const key = 'skill-library-theme';
  const root = document.documentElement;
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  const themeColor = document.querySelector('meta[name="theme-color"]');
  const valid = value => value === 'light' || value === 'dark';
  let preference = null;
  let toggle;

  try {
    const saved = localStorage.getItem(key);
    if (valid(saved)) preference = saved;
  } catch {
    // The switch remains usable when browser storage is unavailable.
  }

  function apply() {
    const theme = preference || (system.matches ? 'dark' : 'light');
    root.dataset.theme = theme;
    themeColor?.setAttribute('content', theme === 'dark' ? '#080c16' : '#f5f6f2');
    if (toggle) {
      toggle.setAttribute('aria-checked', String(theme === 'dark'));
      toggle.title = theme === 'dark' ? '切換為淺色模式' : '切換為深色模式';
      toggle.querySelector('.theme-label').textContent = theme === 'dark' ? '深色' : '淺色';
    }
  }

  apply();
  system.addEventListener('change', () => {
    if (!preference) apply();
  });
  window.addEventListener('storage', event => {
    if (event.key !== key && event.key !== null) return;
    preference = valid(event.newValue) ? event.newValue : null;
    apply();
  });

  document.addEventListener('DOMContentLoaded', () => {
    toggle = document.getElementById('theme-toggle');
    if (!toggle) return;
    apply();
    toggle.hidden = false;
    toggle.addEventListener('click', () => {
      preference = root.dataset.theme === 'dark' ? 'light' : 'dark';
      try {
        localStorage.setItem(key, preference);
      } catch {
        // Keep the manual choice for this page even if it cannot be saved.
      }
      apply();
    });
  });
})();
