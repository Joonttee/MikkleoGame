/**
 * Theme handling
 */
import { STORAGE_KEYS } from './config.js';

const THEMES = ['cyan', 'pink', 'oled', 'amber', 'emerald', 'lavender', 'arctic'];

export function setTheme(theme) {
  if (!THEMES.includes(theme)) theme = 'cyan';
  document.documentElement.setAttribute('data-theme', theme);
  try {
    localStorage.setItem(STORAGE_KEYS.THEME, theme);
  } catch {}
  document.querySelectorAll('.theme-btn').forEach(b => {
    b.classList.toggle('active', b.classList.contains('theme-' + theme));
  });
}

export function initTheme() {
  let saved = 'cyan';
  try {
    saved = localStorage.getItem(STORAGE_KEYS.THEME) || 'cyan';
  } catch {}
  setTheme(saved);
}

// Expose globally for inline onclick compatibility if needed
if (typeof window !== 'undefined') {
  window.setTheme = setTheme;
}
