/**
 * LocalStorage handling with in-memory cache to avoid parsing JSON on every card.
 */
import { STORAGE_KEYS } from './config.js';
import { hashPin } from './utils.js';

let _overridesCache = null;
let _overridesRaw = null;

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

export function getEffectiveStatus(game) {
  const overrides = loadOverrides();
  const o = overrides[game.id];
  if (o && Object.prototype.hasOwnProperty.call(o, 'status')) {
    return o.status;
  }
  return game.status || 'none';
}

export function getEffectiveFlag(game, flag) {
  const overrides = loadOverrides();
  const o = overrides[game.id];
  if (o && Object.prototype.hasOwnProperty.call(o, flag)) {
    return !!o[flag];
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
