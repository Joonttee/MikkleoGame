/**
 * Rendering — optimized with DocumentFragment and single stats pass
 */
import { STATUS_MAP, UI, GENRE_GROUPS } from './config.js';
import { esc } from './utils.js';
import { getEffectiveStatus, getEffectiveFlag, isAdmin } from './storage.js';
import { getPrimaryGenreLabel, computePrimaryGenreCounts } from './genres.js';

/**
 * Renders genre breakdown (top 3) — по каноническим группам,
 * чтобы «Экшены» и «Action» не считались разными жанрами.
 */
export function renderGenreBreakdown(games) {
  const container = document.getElementById('genreBreakdown');
  if (!container) return;
  const counts = computePrimaryGenreCounts(games);
  const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 3);
  const max = sorted[0] ? sorted[0][1] : 1;

  container.innerHTML = sorted.map(([gKey, count]) => {
    const gName = GENRE_GROUPS[gKey]?.label || gKey;
    const pct = Math.round((count / games.length) * 100);
    const barWidth = Math.round((count / max) * 100);
    return `
      <div>
        <div class="genre-mini-row">
          <span style="color:var(--text); font-weight:700;">${esc(gName)}</span>
          <span style="color:var(--muted); font-family:'JetBrains Mono';">${pct}% (${count})</span>
        </div>
        <div style="background:var(--card2); height:4px; border-radius:999px; margin-top:2px; overflow:hidden;">
          <div class="genre-mini-bar" style="width:${barWidth}%;"></div>
        </div>
      </div>
    `;
  }).join('');
}

/**
 * Updates sidebar + hero stats — single pass over GAMES for performance.
 */
export function updateStats(games, filtered) {
  let completed = 0, inProg = 0, planned = 0;
  const overridesCache = {}; // we will compute via getEffectiveStatus in loop but cache not needed; we do single pass
  // We use getEffectiveStatus which reads cache; acceptable
  for (const g of games) {
    const s = getEffectiveStatus(g);
    if (s === 'completed') completed++;
    else if (s === 'in_progress') inProg++;
    else if (s === 'planned') planned++;
  }
  const progressPercent = games.length ? ((completed / games.length) * 100).toFixed(1) : '0';

  const setText = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  };

  setText('statTotal', games.length);
  setText('statFiltered', filtered.length);
  setText('heroStatTotal', games.length);
  setText('heroStatInProgress', inProg);
  setText('heroStatCompleted', completed);
  setText('heroStatPlanned', planned);

  const spBar = document.getElementById('statProgressBar');
  if (spBar) spBar.style.width = progressPercent + '%';
  setText('statProgressPercent', progressPercent + '%');
}

/**
 * Renders games grid with fragment for perf.
 * @param {Array} gamesToShow - slice of filtered games to render
 * @param {Array} filteredFull - full filtered array (for more button)
 * @param {number} visibleCount - currently visible count
 * @param {string} viewMode - 'grid' | 'list'
 * @param {Function} onCardClick - (game)=>void
 * @param {Function} onShowMore - ()=>void
 * @param {Function} resetFilters - ()=>void
 */
export function renderGrid({ gamesToShow, filteredFull, visibleCount, viewMode, onCardClick, onShowMore, resetFilters }) {
  const grid = document.getElementById('grid');
  if (!grid) return;
  grid.innerHTML = '';

  // Админ видит скрытые игры «призраком» (зрителям они вообще не рендерятся)
  const adminMode = isAdmin();

  if (!gamesToShow.length) {
    grid.innerHTML = `
      <div class="empty">
        <div class="empty-icon">🎮</div>
        <h3>Ничего не нашлось</h3>
        <p style="color:var(--muted); font-size:14px;">Попробуйте изменить поисковый запрос или сбросить фильтры.</p>
        <button class="btn-reset-filters" style="margin-top:10px;">Сбросить фильтры</button>
      </div>
    `;
    const btn = grid.querySelector('.btn-reset-filters');
    if (btn) btn.addEventListener('click', resetFilters);
    return;
  }

  const frag = document.createDocumentFragment();

  for (const g of gamesToShow) {
    const el = document.createElement('div');
    el.className = 'card';
    const hiddenGh = adminMode && getEffectiveFlag(g, 'isHidden');
    if (hiddenGh) el.classList.add('card-hidden');
    el.tabIndex = 0;
    el.setAttribute('role', 'button');
    el.setAttribute('aria-label', g.title);

    const effStatus = getEffectiveStatus(g);
    const stInfo = STATUS_MAP[effStatus] || STATUS_MAP['none'];
    const initials = esc((g.title || 'Game').slice(0, 2).toUpperCase());

    // В сетке — только один слой, фикс размер, без размытого фона (оптимизация + не прыгает размер)
    // В списке — тот же img, но в маленьком контейнере (cover)
    const imgBlock = g.image
      ? `<img class="cover-main" src="${esc(g.image)}" loading="lazy" decoding="async" alt="${esc(g.title)}">`
      : `<div class="cover-initials">${initials}</div>`;

    const mainGenre = getPrimaryGenreLabel(g.genre) || 'Игра';
    const statusPill = `<span class="status-tag ${stInfo.class}">${stInfo.emoji} ${stInfo.label}</span>`;
    const hiddenTag = hiddenGh ? `<span class="meta-tag" title="Скрыта от зрителей">🙈 скрыта</span>` : '';

    if (viewMode === 'list') {
      el.innerHTML = `
        <div class="card-cover">${imgBlock}</div>
        <div class="card-body">
          ${statusPill}
          <div class="card-title">${esc(g.title)}</div>
          <div class="card-meta">
            <span class="meta-tag accent">${esc(mainGenre)}</span>
            <span class="meta-tag">${g.year || ''}</span>
            ${hiddenTag}
          </div>
        </div>
      `;
    } else {
      el.innerHTML = `
        <div class="card-cover">
          ${statusPill}
          ${imgBlock}
        </div>
        <div class="card-body">
          <div class="card-title">${esc(g.title)}</div>
          <div class="card-meta">
            <span class="meta-tag accent">${esc(mainGenre)}</span>
            <span class="meta-tag">${g.year || ''}</span>
            ${hiddenTag}
          </div>
        </div>
      `;
    }

    el.addEventListener('click', () => onCardClick(g));
    el.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        onCardClick(g);
      }
    });
    frag.appendChild(el);
  }

  grid.appendChild(frag);

  if (filteredFull.length > visibleCount) {
    const more = document.createElement('div');
    more.style.gridColumn = '1 / -1';
    more.style.textAlign = 'center';
    more.style.padding = '24px 0';
    more.innerHTML = `
      <button class="tab-btn active-all" style="height:46px; padding:0 32px; font-size:14px;">
        Показать ещё ${UI.LOAD_MORE_STEP} (Показано ${visibleCount} из ${filteredFull.length})
      </button>
    `;
    const btn = more.querySelector('button');
    if (btn) btn.addEventListener('click', onShowMore);
    grid.appendChild(more);
  }
}
