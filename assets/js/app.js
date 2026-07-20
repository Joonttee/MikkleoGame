/**
 * Mikkleo Games — Main entry (ESM)
 * Optimized, modular, maintainable.
 */
import { STORAGE_KEYS, UI } from './config.js';
import { esc, debounce } from './utils.js';
import { loadOverrides, clearOverridesCache, loadRemoteOverrides, getRemoteGamesRaw, isAdmin, getEffectiveFlag } from './storage.js';
import { initTheme, setTheme } from './theme.js';
import { initTwitchStatus } from './twitch.js';
import { filterGames, sortGames } from './filters.js';
import { renderGrid, renderGenreBreakdown, updateStats } from './render.js';
import { initModal } from './modal.js';
import { createAdminPanel } from './admin.js';
import { convertPlayniteToMikkleo, parsePlayniteJson } from './playnite.js';

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
// Игры, видимые ТЕКУЩЕМУ пользователю: зрителям — без скрытых (isHidden),
// админу — все (скрытые подсвечиваются «призраком», чтобы их можно было вернуть)
let visibleGames = [];

// Пересчитывается при каждом applyFilters — после смены статусов/флагов в админке
function computeVisibleGames() {
  visibleGames = isAdmin() ? GAMES : GAMES.filter(g => !getEffectiveFlag(g, 'isHidden'));
}

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
  computeVisibleGames();

  const genreValue = els.genreSelect?.value || 'all';
  const eraValue = els.eraSelect?.value || 'all';
  const searchQuery = els.searchInput?.value || '';
  const sortValue = els.sortSelect?.value || 'title-asc';

  const { filtered: afterFilter, normalizedQuery } = filterGames(visibleGames, {
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

  // Статистика и топ жанров — тоже по видимым играм (скрытые не считаются у зрителей)
  const base = visibleGames.length ? visibleGames : GAMES;
  updateStats(base, filtered);
  renderGenreBreakdown(base);

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
  // Параллельно грузим игры и удалённые оверрайды/игры (для стримера без доступа к репе)
  const [games] = await Promise.all([
    loadGames(),
    loadRemoteOverrides()
  ]);
  GAMES = games;

  // Мерджим удалённые игры из Playnite (если стример без доступа залил library.json в pantry/gist)
  try {
    const remoteRaw = getRemoteGamesRaw();
    if (remoteRaw) {
      const playniteArray = parsePlayniteJson(remoteRaw);
      if (playniteArray && playniteArray.length) {
        const existingIds = new Set(GAMES.map(g => g.id));
        const existingNorms = new Set(GAMES.map(g => (g.title || '').replace(/[^0-9a-zA-Zа-яА-ЯёЁ]/g, '').toLowerCase()));
        // Если массив уже в формате Mikkleo (есть title+id), просто мерджим, иначе конвертим из Playnite.
        // Формат определяем по РАСПАРСЕННОМУ массиву (parsePlayniteJson уже развернул
        // обёртки вида { games: [...] }, в т.ч. от Pantry), а не по сырому remoteRaw.
        const first = playniteArray[0];
        const isMikkleoFormat = first && first.title !== undefined && first.id !== undefined;
        let converted = [];
        if (isMikkleoFormat) {
          converted = playniteArray.filter(r => {
            const norm = (r.title || '').replace(/[^0-9a-zA-Zа-яА-ЯёЁ]/g, '').toLowerCase();
            return norm && !existingNorms.has(norm);
          });
        } else {
          converted = convertPlayniteToMikkleo(playniteArray, existingIds, existingNorms);
        }
        if (converted.length) {
          console.log(`[remote games] +${converted.length} new games from remote`);
          GAMES = [...GAMES, ...converted];
        }
      }
    }
  } catch (e) {
    console.warn('remote games merge failed', e);
  }

  if (!GAMES.length) {
    if (els.grid) {
      els.grid.innerHTML = `<div class="empty"><div class="empty-icon">⚠️</div><h3>Не удалось загрузить каталог</h3><p style="color:var(--muted);">Попробуйте перезагрузить страницу.</p></div>`;
    }
    return;
  }

  filtered = [...GAMES];
  visibleGames = [...GAMES];

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
