/**
 * Filtering + sorting — pure-ish logic extracted for testability.
 */
import { expandQuery } from './utils.js';
import { getEffectiveStatus, getEffectiveFlag } from './storage.js';

export function filterGames(games, { tab, genreValue, eraValue, searchQuery }) {
  let out = [...games];

  // Tab filter
  if (tab === 'completed') out = out.filter(g => getEffectiveStatus(g) === 'completed');
  else if (tab === 'in_progress') out = out.filter(g => getEffectiveStatus(g) === 'in_progress');
  else if (tab === 'planned') out = out.filter(g => getEffectiveStatus(g) === 'planned');
  else if (tab === 'gacha') out = out.filter(g => getEffectiveFlag(g, 'isGacha'));
  else if (tab === 'mp') out = out.filter(g => getEffectiveFlag(g, 'isMultiplayer'));
  else if (tab === 'coop') out = out.filter(g => getEffectiveFlag(g, 'isCoop'));

  // Genre
  if (genreValue && genreValue !== 'all') {
    const gv = genreValue.toLowerCase();
    out = out.filter(g => g.genre && g.genre.toLowerCase().includes(gv));
  }

  // Era
  if (eraValue === 'new') out = out.filter(g => (g.year || 0) >= 2024);
  else if (eraValue === 'modern') out = out.filter(g => (g.year || 0) >= 2018 && (g.year || 0) <= 2023);
  else if (eraValue === 'retro') out = out.filter(g => (g.year || 0) < 2018);

  // Search
  const q = (searchQuery || '').toLowerCase().trim();
  if (q) {
    const terms = expandQuery(q);
    out = out.filter(g => {
      const text = `${g.title || ''} ${g.altTitle || ''} ${g.genre || ''} ${g.platform || ''} ${g.year || ''}`.toLowerCase();
      return terms.some(t => text.includes(t));
    });
  }

  return { filtered: out, normalizedQuery: q };
}

export function sortGames(games, sortValue) {
  const arr = [...games];
  if (sortValue === 'title-asc') arr.sort((a, b) => a.title.localeCompare(b.title, 'ru'));
  else if (sortValue === 'title-desc') arr.sort((a, b) => b.title.localeCompare(a.title, 'ru'));
  else if (sortValue === 'year-desc') arr.sort((a, b) => (b.year || 0) - (a.year || 0));
  else if (sortValue === 'year-asc') arr.sort((a, b) => (a.year || 0) - (b.year || 0));
  return arr;
}
