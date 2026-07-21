/**
 * Playnite -> Mikkleo Games converter (client-side)
 * Same logic as scripts/import_playnite.py but in JS
 * Supports both formats: GameDataExporter (library.json) and JsonLibraryImportExport
 */

function slugify(str) {
  return str.toLowerCase()
    .replace(/[^0-9a-zA-Zа-яА-ЯёЁ]+/g, '-')
    .replace(/-{2,}/g, '-')
    .replace(/^-|-$/g, '')
    .slice(0, 64) || 'game';
}

function normalizeTitle(s) {
  return (s || '').replace(/[^0-9a-zA-Zа-яА-ЯёЁ]/g, '').toLowerCase();
}

function extractYear(game) {
  const candidates = [
    game.ReleaseDate,
    game.releaseDate,
    game.ReleaseDate && typeof game.ReleaseDate === 'object' ? game.ReleaseDate.ReleaseDate : null,
    game.ReleaseYear,
    game.Year,
    game.year
  ];
  for (const c of candidates) {
    if (!c) continue;
    const str = typeof c === 'object' ? JSON.stringify(c) : String(c);
    const m = str.match(/(19|20)\d{2}/);
    if (m) {
      const y = parseInt(m[0], 10);
      if (y >= 1970 && y <= 2030) return y;
    }
    if (typeof c === 'number' && c >= 1970 && c <= 2030) return c;
  }
  return 0;
}

function extractGenres(game) {
  const raw = game.Genres || game.genres || game.Categories || game.Tags || [];
  const list = Array.isArray(raw) ? raw : [raw];
  const out = [];
  for (const g of list) {
    if (!g) continue;
    if (typeof g === 'object') {
      const name = g.Name || g.name;
      if (name) out.push(name);
    } else if (typeof g === 'string') {
      out.push(g);
    }
  }
  return out.length ? out.slice(0, 4).join(', ') : 'Игра';
}

function extractPlatform(game) {
  const src = game.Source;
  if (src && typeof src === 'object') {
    const name = src.Name || src.name;
    if (name) return name;
  }
  const plats = game.Platforms || game.platforms || [];
  if (plats.length) {
    const first = plats[0];
    if (typeof first === 'object') {
      const n = first.Name || first.name;
      if (n) {
        const low = n.toLowerCase();
        if (low.includes('switch')) return 'Switch';
        if (low.includes('ubisoft')) return 'Ubisoft';
        return n;
      }
    } else if (typeof first === 'string') {
      return first;
    }
  }
  return 'Steam/Epic';
}

function extractCoverPath(game) {
  const keys = ['CoverImage', 'coverImage', 'Cover', 'Image', 'BackgroundImage'];
  for (const k of keys) {
    const v = game[k];
    if (!v) continue;
    if (typeof v === 'object') {
      const p = v.Path || v.path;
      if (p) return String(p);
    }
    if (typeof v === 'string' && v.trim()) return v.trim();
  }
  return '';
}

/**
 * Авто-детект флагов MP/Coop из Playnite Features + жанров.
 * MP — PvP/соревновательный/ММО; Coop — совместное прохождение против ИИ.
 * «Online Co-op» не содержит слова multiplayer — чистый кооп не помечается MP.
 */
function detectFlags(game, genreStr) {
  const feats = game.Features || game.features || [];
  const list = Array.isArray(feats) ? feats : [feats];
  const blob = list.map(f => {
    if (!f) return '';
    return typeof f === 'object' ? (f.Name || f.name || '') : String(f);
  }).join(' ').toLowerCase();
  const genres = (genreStr || '').toLowerCase();

  const hasCoop = blob.includes('co-op') || blob.includes('coop');
  const hasMp = blob.includes('pvp') || blob.includes('versus') || blob.includes('multiplayer')
    || blob.includes('mmo') || blob.includes('massively')
    || blob.includes('shared/split') || blob.includes('split screen')
    || genres.includes('многопользовательск') || genres.includes('massively');
  return { isMultiplayer: hasMp, isCoop: hasCoop };
}

/**
 * Convert Playnite game list to Mikkleo format
 * @param {Array} playniteGames - raw array from library.json
 * @param {Set} existingIds - set of existing ids to avoid collision
 * @param {Set} existingNorms - set of normalized titles already in catalog
 * @returns {Array} array of new games in Mikkleo format
 */
export function convertPlayniteToMikkleo(playniteGames, existingIds = new Set(), existingNorms = new Set()) {
  const out = [];
  const usedIds = new Set(existingIds);

  for (const pg of playniteGames) {
    if (!pg || typeof pg !== 'object') continue;
    const name = pg.Name || pg.name || pg.Title || '';
    if (!name || name.trim().length < 2) continue;

    const norm = normalizeTitle(name);
    if (!norm) continue;
    if (existingNorms.has(norm)) continue; // already exists

    const year = extractYear(pg);
    const genre = extractGenres(pg);
    const platform = extractPlatform(pg);
    const coverPath = extractCoverPath(pg);
    const flags = detectFlags(pg, genre);

    let baseSlug = slugify(name);
    let gid = baseSlug;
    let counter = 1;
    while (usedIds.has(gid)) {
      counter++;
      gid = `${baseSlug}-${counter}`;
    }
    usedIds.add(gid);

    // For remote mode without repo access, cover cannot be resolved locally
    // If coverPath looks like http URL, keep it, otherwise leave empty (initials fallback)
    let image = '';
    if (coverPath && /^https?:\/\//.test(coverPath)) {
      image = coverPath;
    } else if (coverPath) {
      // If it's a filename, we can't resolve without library dir, leave empty
      // But we keep original filename hint in _playniteCover for debugging
      image = '';
    }

    out.push({
      id: gid,
      title: name.trim(),
      genre,
      platform,
      year,
      rating: 0,
      image,
      desc: '',
      createdAt: new Date().toISOString(),
      altTitle: '',
      status: null,
      isGacha: false,
      isMultiplayer: flags.isMultiplayer,
      isCoop: flags.isCoop,
      _playniteId: pg.Id || pg.id || '',
      _playniteCover: coverPath
    });
  }

  return out;
}

/**
 * Try to parse various JSON structures into array
 */
export function parsePlayniteJson(data) {
  if (Array.isArray(data)) return data;
  if (data && typeof data === 'object') {
    if (Array.isArray(data.Games)) return data.Games;
    if (Array.isArray(data.games)) return data.games;
    // Maybe it's a dict of games
    const vals = Object.values(data);
    if (vals.length && vals.every(v => typeof v === 'object' && (v.Name || v.name))) {
      return vals;
    }
  }
  return [];
}
