/**
 * Twitch live status checker — optimized, no CORS-breaking fallback.
 */
import { TWITCH, STORAGE_KEYS } from './config.js';
import { fetchJsonOrText } from './utils.js';

function parseIvr(data) {
  const user = Array.isArray(data) ? data[0] : data;
  if (!user) return 'unknown';
  if (user.stream) return 'live';
  if (user.isLive === true || user.live === true) return 'live';
  if (user.id) return 'offline';
  return 'unknown';
}

function parseDecapi(text) {
  if (!text) return 'unknown';
  const t = String(text).trim().toLowerCase();
  if (t.includes('offline') || t.includes('not live') || t.length < 3) return 'offline';
  if (t === 'true' || t === 'false') return t === 'true' ? 'live' : 'offline';
  if (t === '1' || t === '0') return t === '1' ? 'live' : 'offline';
  // decapi uptime returns time string like "2 hours, 30 minutes" when live
  if (/\d/.test(t) && (t.includes(':') || t.includes('hour') || t.includes('minute') || t.includes('second'))) return 'live';
  return 'unknown';
}

export function applyStreamState(state, elements) {
  const { indicator, statusText, twitchLink } = elements;
  if (!indicator || !statusText) return;

  indicator.classList.remove('live', 'unknown');
  statusText.classList.remove('live', 'unknown');

  if (state === 'live') {
    indicator.classList.add('live');
    statusText.classList.add('live');
    indicator.title = 'Стрим сейчас в эфире на Twitch';
    statusText.textContent = 'В эфире';
    if (twitchLink) {
      twitchLink.classList.add('live');
      twitchLink.title = 'MikkleoVT сейчас стримит — нажмите, чтобы смотреть';
      twitchLink.innerHTML = '<img src="https://cdn.simpleicons.org/twitch/FFFFFF" width="12" height="12" alt="">Twitch (В эфире)';
    }
  } else if (state === 'offline') {
    indicator.title = 'Стрим оффлайн';
    statusText.textContent = 'Оффлайн';
    if (twitchLink) {
      twitchLink.classList.remove('live');
      twitchLink.title = 'Открыть канал MikkleoVT на Twitch';
      twitchLink.innerHTML = '<img src="https://cdn.simpleicons.org/twitch/C9A6FF" width="12" height="12" alt="">Twitch';
    }
  } else {
    indicator.classList.add('unknown');
    statusText.classList.add('unknown');
    indicator.title = 'Не удалось проверить статус стрима';
    statusText.textContent = 'Статус неизвестен';
    if (twitchLink) {
      twitchLink.classList.remove('live');
      twitchLink.innerHTML = '<img src="https://cdn.simpleicons.org/twitch/C9A6FF" width="12" height="12" alt="">Twitch';
    }
  }
}

export async function checkTwitchStatus(elements) {
  // Fast cache paint
  try {
    const cached = JSON.parse(localStorage.getItem(STORAGE_KEYS.STREAM_CACHE) || 'null');
    if (cached && (Date.now() - cached.ts) < TWITCH.CACHE_TTL) {
      applyStreamState(cached.state, elements);
    }
  } catch {}

  let state = 'unknown';

  for (const url of TWITCH.ENDPOINTS) {
    try {
      const data = await fetchJsonOrText(url);
      if (typeof data === 'string') {
        const t = data.trim().toLowerCase();
        if (t === 'true' || t === '1') { state = 'live'; break; }
        if (t === 'false' || t === '0') { state = 'offline'; break; }
        state = parseDecapi(data);
      } else {
        state = parseIvr(data);
      }
      if (state !== 'unknown') break;
    } catch {
      // try next
    }
  }

  applyStreamState(state, elements);

  if (state !== 'unknown') {
    try {
      localStorage.setItem(STORAGE_KEYS.STREAM_CACHE, JSON.stringify({ state, ts: Date.now() }));
    } catch {}
  }
  return state;
}

export function initTwitchStatus() {
  const elements = {
    indicator: document.getElementById('streamIndicator'),
    statusText: document.getElementById('streamStatusText'),
    twitchLink: document.getElementById('socialTwitchLink')
  };
  if (!elements.indicator) return;

  applyStreamState('unknown', elements);
  checkTwitchStatus(elements);
  const interval = setInterval(() => checkTwitchStatus(elements), TWITCH.CHECK_INTERVAL);
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) checkTwitchStatus(elements);
  });

  // cleanup on page hide if needed
  return () => clearInterval(interval);
}
