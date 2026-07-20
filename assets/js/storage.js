/**
 * LocalStorage handling with in-memory cache + remote overrides for streamers without repo access
 */
import { STORAGE_KEYS } from './config.js';
import { hashPin } from './utils.js';

let _overridesCache = null;
let _overridesRaw = null;

// Remote overrides (public, for streamers without repo access)
let _remoteOverrides = null;
let _remoteGames = null;
let _remoteLoaded = false;
let _remoteGamesUrl = null;

export function loadOverrides() {
  try {
    const raw = localStorage.getItem(STORAGE_KEYS.OVERRIDES);
    if (raw === _overridesRaw && _overridesCache) return _overridesCache;
    const parsed = JSON.parse(raw || '{}');
    _overridesCache = parsed;
    _overridesRaw = raw;
    return parsed;
  } catch {
    return {};
  }
}

export function saveOverrides(map) {
  try {
    const raw = JSON.stringify(map);
    localStorage.setItem(STORAGE_KEYS.OVERRIDES, raw);
    _overridesCache = map;
    _overridesRaw = raw;
  } catch {}
}

export function clearOverridesCache() {
  _overridesCache = null;
  _overridesRaw = null;
}

export function isAdmin() {
  try {
    return sessionStorage.getItem(STORAGE_KEYS.ADMIN_SESSION) === '1';
  } catch {
    return false;
  }
}

export function setAdmin(on) {
  try {
    if (on) sessionStorage.setItem(STORAGE_KEYS.ADMIN_SESSION, '1');
    else sessionStorage.removeItem(STORAGE_KEYS.ADMIN_SESSION);
  } catch {}
}

/** Remote overrides loader: for streamer without repo access
 *  Tries:
 *   1) localStorage key mikkleo_remote_overrides_url (if streamer sets custom gist/npoint)
 *   2) ./data/remote.json -> { overridesUrl: "https://..." }
 *   3) fallback ./data/overrides.json (can be filled by GitHub Action / bot)
 */
export async function loadRemoteOverrides() {
  if (_remoteLoaded) return _remoteOverrides;
  let overridesUrl = null;
  let gamesUrl = null;

  // 1) allow manual override via localStorage for testing / streamer personal gist
  try {
    const lsUrl = localStorage.getItem('mikkleo_remote_overrides_url');
    if (lsUrl) overridesUrl = lsUrl;
    const lsGamesUrl = localStorage.getItem('mikkleo_remote_games_url');
    if (lsGamesUrl) gamesUrl = lsGamesUrl;
  } catch {}

  if (!overridesUrl || !gamesUrl) {
    try {
      const cfgRes = await fetch('./data/remote.json', { cache: 'no-store' });
      if (cfgRes.ok) {
        const cfg = await cfgRes.json();
        if (!overridesUrl) overridesUrl = cfg.overridesUrl || cfg.url || cfg.remoteUrl || null;
        if (!gamesUrl) gamesUrl = cfg.gamesUrl || cfg.games_url || cfg.libraryUrl || null;
      }
    } catch {}
  }

  if (!overridesUrl) {
    // default file that can be updated by bot/action without code change
    overridesUrl = './data/overrides.json';
  }

  _remoteGamesUrl = gamesUrl;

  if (overridesUrl) {
    try {
      const res = await fetch(overridesUrl, { cache: 'no-store' });
      if (res.ok) {
        const json = await res.json();
        if (!json || typeof json !== 'object') {
          _remoteOverrides = {};
        } else if (json.overrides && typeof json.overrides === 'object') {
          _remoteOverrides = json.overrides;
        } else {
          _remoteOverrides = json;
        }
      } else {
        _remoteOverrides = {};
      }
    } catch (e) {
      _remoteOverrides = {};
    }
  }

  // Load remote games if configured
  if (gamesUrl) {
    try {
      const r = await fetch(gamesUrl, { cache: 'no-store' });
      if (r.ok) {
        const j = await r.json();
        // j can be Playnite raw array or already Mikkleo format
        _remoteGames = j;
      }
    } catch {
      _remoteGames = null;
    }
  }

  _remoteLoaded = true;
  return _remoteOverrides;
}

export function getRemoteOverrides() {
  return _remoteOverrides || {};
}

export function getRemoteGamesRaw() {
  return _remoteGames;
}

export function getRemoteGamesUrl() {
  return _remoteGamesUrl;
}

export function getEffectiveStatus(game) {
  // Local (browser) has highest priority — for streamer preview
  const local = loadOverrides();
  if (local[game.id] && Object.prototype.hasOwnProperty.call(local[game.id], 'status')) {
    return local[game.id].status;
  }
  // Then remote public overrides — for viewers, streamer without repo access
  const remote = _remoteOverrides || {};
  if (remote[game.id] && Object.prototype.hasOwnProperty.call(remote[game.id], 'status')) {
    return remote[game.id].status;
  }
  return game.status || 'none';
}

export function getEffectiveFlag(game, flag) {
  const local = loadOverrides();
  if (local[game.id] && Object.prototype.hasOwnProperty.call(local[game.id], flag)) {
    return !!local[game.id][flag];
  }
  const remote = _remoteOverrides || {};
  if (remote[game.id] && Object.prototype.hasOwnProperty.call(remote[game.id], flag)) {
    return !!remote[game.id][flag];
  }
  return !!game[flag];
}

// PIN handling
export function getStoredPinHash() {
  try {
    return localStorage.getItem(STORAGE_KEYS.ADMIN_PIN);
  } catch {
    return null;
  }
}

export function setStoredPinHash(h) {
  try {
    localStorage.setItem(STORAGE_KEYS.ADMIN_PIN, h);
  } catch {}
}

export function removeStoredPin() {
  try {
    localStorage.removeItem(STORAGE_KEYS.ADMIN_PIN);
  } catch {}
}

export function validateAndHashPin(pin) {
  if (!/^\d{4,6}$/.test(pin)) return null;
  return hashPin(pin);
}
