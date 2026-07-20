/**
 * Mikkleo Games — Main entry (ESM)
 * Optimized, modular, maintainable.
 */
import { STORAGE_KEYS, UI } from './config.js';
import { esc, debounce } from './utils.js';
import { loadOverrides, clearOverridesCache, loadRemoteOverrides } from './storage.js';
import { initTheme, setTheme } from './theme.js';
import { initTwitchStatus } from './twitch.js';
import { filterGames, sortGames } from './filters.js';
import { renderGrid, renderGenreBreakdown, updateStats } from './render.js';
import { initModal } from './modal.js';
import { createAdminPanel } from './admin.js';

// ---------------------------------------------------------
// Data loading — try fetch data/games.json, fallback to bundled data.js
let GAMES = [];

async function loadGames() {
  // Try dynamic import of data.js as fallback
  try {
    // Primary: fetch JSON (faster for browser caching, smaller initial module)
    const res = await fetch('./data/games.json', { cache: 'no-store' });
    if (res.ok) {
      const json = await res.json();
      if (Array.isArray(json) && json.length) {
        return json;
      }
    }
  } catch {}
  try {
    const mod = await import('./data.js');
    if (mod.GAMES && Array.isArray(mod.GAMES)) return mod.GAMES;
  } catch {}
  try {
    // Last resort: expect global injected? (legacy index.html)
    if (typeof window !== 'undefined' && window.GAMES && Array.isArray(window.GAMES)) {
      return window.GAMES;
    }
  } catch {}
  return [];
}

// State
let filtered = [];
let currentTab = 'all';
let visibleCount = UI.DEFAULT_VISIBLE;
let currentViewMode = 'grid';

// DOM cache
const els = {};

function cacheDom() {
  els.grid = document.getElementById('grid');
  els.searchInput = document.getElementById('searchInput');
  els.searchClear = document.getElementById('searchClear');
  els.genreSelect = document.getElementById('genreSelect');
  els.eraSelect = document.getElementById('eraSelect');
  els.sortSelect = document.getElementById('sortSelect');
  els.btnResetFilters = document.getElementById('btnResetFilters');
  els.viewBtnGrid = document.getElementById('viewBtnGrid');
  els.viewBtnList = document.getElementById('viewBtnList');
  els.backToTop = document.getElementById('backToTop');
  els.toast = document.getElementById('toast');
}

// Toast
function showToast(msg) {
  if (!els.toast) return;
  els.toast.textContent = msg;
  els.toast.classList.add('show');
  setTimeout(() => els.toast.classList.remove('show'), UI.TOAST_DURATION);
}

// View mode
function setViewMode(mode) {
  currentViewMode = mode;
  try { localStorage.setItem(STORAGE_KEYS.VIEW_MODE, mode); } catch {}
  els.viewBtnGrid?.classList.toggle('active', mode === 'grid');
  els.viewBtnList?.classList.toggle('active', mode === 'list');
  if (els.grid) {
    if (mode === 'list') els.grid.classList.add('mode-list');
    else els.grid.classList.remove('mode-list');
  }
  render();
}

// Tabs
function setTab(tab) {
  currentTab = tab;
  document.querySelectorAll('.tab-btn').forEach(b => { b.className = 'tab-btn'; });
  const btn = document.getElementById('tab-' + tab);
  if (btn) btn.className = 'tab-btn active-' + tab;
  visibleCount = UI.DEFAULT_VISIBLE;
  applyFilters();
}

// Reset
function resetAllFilters() {
  currentTab = 'all';
  if (els.searchInput) els.searchInput.value = '';
  if (els.genreSelect) els.genreSelect.value = 'all';
  if (els.eraSelect) els.eraSelect.value = 'all';
  if (els.sortSelect) els.sortSelect.value = 'title-asc';
  if (els.searchClear) els.searchClear.style.display = 'none';
  setTab('all');
}

// Filtering entry
function applyFilters() {
  if (!GAMES.length) return;

  const genreValue = els.genreSelect?.value || 'all';
  const eraValue = els.eraSelect?.value || 'all';
  const searchQuery = els.searchInput?.value || '';
  const sortValue = els.sortSelect?.value || 'title-asc';

  const { filtered: afterFilter, normalizedQuery } = filterGames(GAMES, {
    tab: currentTab,
    genreValue,
    eraValue,
    searchQuery
  });

  const sorted = sortGames(afterFilter, sortValue);
  filtered = sorted;

  // UI toggles
  if (els.searchClear) {
    els.searchClear.style.display = normalizedQuery ? 'flex' : 'none';
  }
  const hasActive = normalizedQuery || genreValue !== 'all' || eraValue !== 'all' || currentTab !== 'all';
  if (els.btnResetFilters) {
    els.btnResetFilters.style.display = hasActive ? 'inline-flex' : 'none';
  }

  render();
}

function render() {
  if (!GAMES.length) return;

  // Stats (single pass inside)
  updateStats(GAMES, filtered);
  // Genre breakdown only once internally cached, but call each render is cheap now
  renderGenreBreakdown(GAMES);

  const toShow = filtered.slice(0, visibleCount);

  renderGrid({
    gamesToShow: toShow,
    filteredFull: filtered,
    visibleCount,
    viewMode: currentViewMode,
    onCardClick: (g) => modalApi.openModal(g),
    onShowMore: () => {
      visibleCount += UI.LOAD_MORE_STEP;
      render();
    },
    resetFilters: resetAllFilters
  });
}

// Modal init placeholder
let modalApi = { openModal: () => {}, closeModal: () => {} };

// Init app after data loaded
async function init() {
  cacheDom();
  // Параллельно грузим игры и удалённые оверрайды (для стримера без доступа к репе)
  const [games] = await Promise.all([
    loadGames(),
    loadRemoteOverrides()
  ]);
  GAMES = games;

  if (!GAMES.length) {
    if (els.grid) {
      els.grid.innerHTML = `<div class="empty"><div class="empty-icon">⚠️</div><h3>Не удалось загрузить каталог</h3><p style="color:var(--muted);">Попробуйте перезагрузить страницу.</p></div>`;
    }
    return;
  }

  filtered = [...GAMES];

  // Theme
  initTheme();

  // View mode from storage
  try {
    currentViewMode = localStorage.getItem(STORAGE_KEYS.VIEW_MODE) || 'grid';
  } catch { currentViewMode = 'grid'; }
  setViewMode(currentViewMode);

  // Modal
  modalApi = initModal(showToast);

  // Search debounce
  const debouncedApply = debounce(() => {
    visibleCount = UI.DEFAULT_VISIBLE;
    applyFilters();
  }, UI.SEARCH_DEBOUNCE);

  els.searchInput?.addEventListener('input', debouncedApply);
  els.searchClear?.addEventListener('click', () => {
    if (els.searchInput) els.searchInput.value = '';
    applyFilters();
  });

  // Selects
  els.genreSelect?.addEventListener('change', () => { visibleCount = UI.DEFAULT_VISIBLE; applyFilters(); });
  els.eraSelect?.addEventListener('change', () => { visibleCount = UI.DEFAULT_VISIBLE; applyFilters(); });
  els.sortSelect?.addEventListener('change', applyFilters);
  els.btnResetFilters?.addEventListener('click', resetAllFilters);

  // View buttons
  els.viewBtnGrid?.addEventListener('click', () => setViewMode('grid'));
  els.viewBtnList?.addEventListener('click', () => setViewMode('list'));

  // Tabs — delegate via global function for backwards compat
  window.setTab = setTab;
  window.resetAllFilters = resetAllFilters;
  window.setViewMode = setViewMode;

  // Back to top
  if (els.backToTop) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 300) els.backToTop.classList.add('visible');
      else els.backToTop.classList.remove('visible');
    }, { passive: true });
    els.backToTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
  }

  // Keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') modalApi.closeModal();
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      els.searchInput?.focus();
    }
  });

  // Twitch
  initTwitchStatus();

  // Admin panel
  const adminPanel = createAdminPanel({
    games: GAMES,
    onDataChanged: () => {
      clearOverridesCache();
      // re-apply filters to reflect new status
      applyFilters();
    },
    showToast
  });
  adminPanel.applyAdminVisibility();

  // Hidden shortcut Ctrl+Shift+A
  document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.shiftKey && (e.key === 'A' || e.key === 'a' || e.key === 'Ф' || e.key === 'ф')) {
      e.preventDefault();
      adminPanel.open();
    }
    if (e.key === 'Escape') {
      const adminBack = document.getElementById('adminBack');
      if (adminBack?.classList.contains('open')) adminPanel.close();
    }
  });

  // Initial render
  applyFilters();

  // Deep-link to game modal
  const hash = window.location.hash;
  const m = hash.match(/^#game-(.+)$/);
  if (m) {
    const target = GAMES.find(g => g.id === m[1]);
    if (target) modalApi.openModal(target);
  }

  // Register service worker if present? (future PWA)
}

// Kick off
document.addEventListener('DOMContentLoaded', init);

// Expose for debugging
window._mikkleoDebug = { getGames: () => GAMES, getFiltered: () => filtered };
