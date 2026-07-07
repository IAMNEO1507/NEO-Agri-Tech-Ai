(function () {
  const KEY = 'agritech-theme';
  const LEGACY_KEY = 'theme';

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(KEY, theme);
    localStorage.removeItem(LEGACY_KEY);
    const btn = document.getElementById('themeToggle');
    if (btn) {
      const label = theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode';
      btn.setAttribute('aria-label', label);
      btn.setAttribute('title', label);
    }
    window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));
  }

  // Apply immediately on script load (no flash)
  const saved = localStorage.getItem(KEY) || localStorage.getItem(LEGACY_KEY);
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const initialTheme = saved || (prefersDark ? 'dark' : 'light');

  if (saved && !localStorage.getItem(KEY)) {
    localStorage.setItem(KEY, saved);
  }

  applyTheme(initialTheme);

  document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById('themeToggle');
    if (btn) {
      btn.addEventListener('click', function () {
        const current = document.documentElement.getAttribute('data-theme') || 'light';
        applyTheme(current === 'light' ? 'dark' : 'light');
      });
    }
  });

  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
    if (!localStorage.getItem(KEY)) applyTheme(e.matches ? 'dark' : 'light');
  });

  // Keep public API for any page that uses window.themeManager
  window.themeManager = {
    setTheme: applyTheme,
    getCurrentTheme: () => document.documentElement.getAttribute('data-theme'),
    toggleTheme: () => {
      const current = document.documentElement.getAttribute('data-theme') || 'light';
      applyTheme(current === 'light' ? 'dark' : 'light');
    }
  };
})();