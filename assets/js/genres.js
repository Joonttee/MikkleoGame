/**
 * Жанровая логика — алиасы RU/EN, расширение поиска, подсчёты для фильтров.
 * Жанры в каталоге смешанные (Playnite → русские, Steam-экспорт → английские),
 * здесь всё сводится к каноническим группам из GENRE_GROUPS.
 */
import { GENRE_GROUPS } from './config.js';

const GROUP_ENTRIES = Object.entries(GENRE_GROUPS);

function hasToken(genreLower, token) {
  return genreLower.includes(token);
}

/**
 * Относится ли строка жанра игры к канонической группе.
 * Неизвестный groupKey — fallback на старое поведение (подстрока).
 */
export function matchGenreGroup(genreStr, groupKey) {
  const g = (genreStr || '').toLowerCase();
  const group = GENRE_GROUPS[groupKey];
  if (!group) return groupKey ? g.includes(String(groupKey).toLowerCase()) : true;
  return group.tokens.some(t => hasToken(g, t));
}

/**
 * Ключ канонической группы для игры — первая подходящая группа
 * (порядок групп в GENRE_GROUPS задаёт приоритет). null, если ни одна не подошла.
 */
export function getPrimaryGenreKey(genreStr) {
  const g = (genreStr || '').toLowerCase();
  if (!g) return null;
  for (const [key, group] of GROUP_ENTRIES) {
    if (group.tokens.some(t => hasToken(g, t))) return key;
  }
  return null;
}

/**
 * Человекочитаемое название жанра для бейджей: канонический label,
 * либо первый «сырой» жанр из строки, если ни одна группа не подошла.
 */
export function getPrimaryGenreLabel(genreStr) {
  const key = getPrimaryGenreKey(genreStr);
  if (key) return GENRE_GROUPS[key].label;
  const first = (genreStr || '').split(',')[0].trim();
  return first || '';
}

/**
 * Дополнительные подстроки для поиска, если слова запроса похожи на жанр:
 * «шутер»/«shooter»/«fps», «рпг»/«rpg», «гонки»/«racing», «головоломка»/«puzzle»…
 * Слова запроса сравниваются с токенами групп по префиксному сходству:
 * «шутеры» → token «шутер», «стратегия» → token «стратег», «sport» → token «sports».
 */
export function expandGenreQuery(q) {
  const words = (q || '').toLowerCase().split(/\s+/).filter(Boolean);
  const extra = new Set();
  for (const w of words) {
    for (const [, group] of GROUP_ENTRIES) {
      let hit = false;
      for (const t of group.tokens) {
        const similar = t === w || (w.length >= 3 && t.startsWith(w)) || (t.length >= 3 && w.startsWith(t));
        if (similar) { hit = true; break; }
      }
      if (hit) group.tokens.forEach(t => extra.add(t));
    }
  }
  return Array.from(extra);
}

/**
 * Счётчики игр по группам (игра может попасть в несколько групп).
 * Используется для построения выпадающего фильтра жанров с количеством.
 */
export function computeGenreGroupCounts(games) {
  const counts = {};
  for (const g of games) {
    const genre = (g.genre || '').toLowerCase();
    if (!genre) continue;
    for (const [key, group] of GROUP_ENTRIES) {
      if (group.tokens.some(t => hasToken(genre, t))) {
        counts[key] = (counts[key] || 0) + 1;
      }
    }
  }
  return counts;
}

/**
 * Счётчики по «главному» жанру игры (каждая игра — максимум в одной группе).
 * Используется для топ-3 жанров в сайдбаре, чтобы «Экшены» и «Action»
 * не считались разными жанрами.
 */
export function computePrimaryGenreCounts(games) {
  const counts = {};
  for (const g of games) {
    const key = getPrimaryGenreKey(g.genre);
    if (key) counts[key] = (counts[key] || 0) + 1;
  }
  return counts;
}
