/**
 * Utility helpers — XSS escape, query expansion, debounce, etc.
 */
import { SEARCH_MAP } from './config.js';

const ESCAPE_MAP = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#039;'
};

export function esc(str) {
  return String(str || '').replace(/[&<>"']/g, m => ESCAPE_MAP[m]);
}

/**
 * Expands search query using SEARCH_MAP synonyms.
 */
export function expandQuery(q) {
  const lower = q.toLowerCase();
  const words = lower.split(/\s+/).filter(Boolean);
  const expanded = new Set([lower]);
  for (const w of words) {
    if (SEARCH_MAP[w]) {
      SEARCH_MAP[w].forEach(t => expanded.add(t.toLowerCase()));
    }
  }
  return Array.from(expanded);
}

/**
 * Simple non-crypto hash for PIN — deterrent only, data is local anyway.
 */
export function hashPin(pin) {
  let h = 5381;
  for (let i = 0; i < pin.length; i++) {
    h = ((h << 5) + h) + pin.charCodeAt(i);
    h = h & 0xFFFFFFFF;
  }
  return 'h_' + (h >>> 0).toString(16);
}

/**
 * Debounce wrapper.
 */
export function debounce(fn, delay = 120) {
  let t;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), delay);
  };
}

/**
 * Fetch with timeout (6.5s) and JSON/text auto-detection.
 */
export async function fetchJsonOrText(url, opts = {}) {
  const controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
  const timeoutId = controller ? setTimeout(() => controller.abort(), 6500) : null;
  try {
    const res = await fetch(url, { ...opts, signal: controller?.signal, cache: 'no-store' });
    if (timeoutId) clearTimeout(timeoutId);
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const ct = res.headers.get('content-type') || '';
    if (ct.includes('json')) return await res.json();
    return await res.text();
  } catch (e) {
    if (timeoutId) clearTimeout(timeoutId);
    throw e;
  }
}

/**
 * Safe clipboard copy with fallback.
 */
export async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    // fallback for old browsers
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try {
      document.execCommand('copy');
      return true;
    } catch {
      return false;
    } finally {
      ta.remove();
    }
  }
}
