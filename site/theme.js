(() => {
  const key = 'tommytai-theme';
  const root = document.documentElement;
  const button = document.querySelector('[data-theme-toggle]');
  if (!button) return;

  function refresh() {
    const light = root.dataset.theme === 'light';
    button.textContent = light ? 'Dark mode' : 'Light mode';
    button.setAttribute('aria-pressed', String(light));
    const themeColor = document.querySelector('meta[name="theme-color"]');
    if (themeColor) themeColor.content = light ? '#fcf8f5' : '#110d10';
  }

  button.addEventListener('click', () => {
    root.dataset.theme = root.dataset.theme === 'light' ? 'dark' : 'light';
    try { localStorage.setItem(key, root.dataset.theme); } catch {}
    refresh();
  });
  refresh();
})();
