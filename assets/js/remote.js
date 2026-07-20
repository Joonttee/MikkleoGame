/**
 * Remote JSON upload helpers — provider-aware (Pantry / jsonbin / generic).
 *
 * Рекомендуемое хранилище — Pantry (getpantry.cloud):
 *   POST /apiv1/pantry/{ID}/basket/{NAME} — создать или ПОЛНОСТЬЮ заменить корзину.
 * Бесплатно, CORS открыт, ключей не надо. Корзина живёт, пока к ней обращаются
 * (TTL продлевается каждым GET/POST — при активных зрителях практически вечно).
 */

export function detectProvider(url) {
  const u = (url || '').toLowerCase();
  if (u.includes('getpantry.cloud')) return 'pantry';
  if (u.includes('jsonbin.io')) return 'jsonbin';
  return 'generic';
}

/**
 * GET-хелпер: прочитать текущий список игр из удалённой корзины.
 * Разворачивает обёртки pantry ({ games: [...] }), jsonbin ({ record: ... }),
 * playnite-стиля ({ Games: [...] }) и сырой массив. При любой ошибке — [].
 */
export async function fetchRemoteGamesList(url) {
  try {
    const res = await fetch((url || '').trim(), { cache: 'no-store' });
    if (!res.ok) return [];
    const j = await res.json().catch(() => null);
    if (Array.isArray(j)) return j;
    if (j && typeof j === 'object') {
      if (Array.isArray(j.games)) return j.games;
      if (Array.isArray(j.Games)) return j.Games;
      if (Array.isArray(j.record)) return j.record;
      if (j.record && Array.isArray(j.record.games)) return j.record.games;
    }
    return [];
  } catch {
    return [];
  }
}

function normKey(g) {
  const t = (g && (g.title || g.Name || g.name)) || '';
  return t.replace(/[^0-9a-zA-Zа-яА-ЯёЁ]/g, '').toLowerCase();
}

/**
 * Аддитивная склейка списков без потерь: существующие записи сохраняются
 * первыми (вместе с их id — на них завязаны статусы в корзине статусов),
 * из входящих добавляются только отсутствующие по нормализованному названию.
 */
export function mergeGames(existing, incoming) {
  const out = [];
  const seen = new Set();
  for (const g of (existing || [])) {
    const k = normKey(g);
    if (!k || seen.has(k)) continue;
    seen.add(k);
    out.push(g);
  }
  for (const g of (incoming || [])) {
    const k = normKey(g);
    if (!k || seen.has(k)) continue;
    seen.add(k);
    out.push(g);
  }
  return out;
}

/**
 * Заливка JSON в удалённое хранилище с правильной семантикой под провайдера.
 *
 * @param {string} rawUrl - URL корзины/бина (pantry / jsonbin / любой другой)
 * @param {object|Array} data - JSON-данные
 * @returns {Promise<{ok:boolean, method?:string, status?:number, bodyText?:string, provider:string, url:string}>}
 */
export async function uploadJsonToRemote(rawUrl, data) {
  const url = (rawUrl || '').trim();
  const provider = detectProvider(url);

  let payload = data;
  if (provider === 'pantry' && Array.isArray(data)) {
    // Pantry надёжнее принимает верхнеуровневый объект — оборачиваем массив.
    // Сайт при чтении сам развернёт { games: [...] } (parsePlayniteJson).
    payload = { games: data };
  }

  const headers = { 'Content-Type': 'application/json' };
  if (provider === 'jsonbin') {
    try {
      const key = localStorage.getItem('mikkleo_jsonbin_key') || '';
      if (key) headers['X-Master-Key'] = key;
    } catch {}
  }

  // Порядок методов важен:
  // - pantry:  только POST = create/replace. PUT там — deep-merge: сброшенные статусы
  //            и удалённые игры НЕ исчезнут, поэтому PUT использовать нельзя совсем.
  // - jsonbin: PUT — задокументированный метод обновления бина.
  // - generic: перебираем всё подряд на случай неизвестного хранилища.
  const methods =
    provider === 'pantry' ? ['POST'] :
    provider === 'jsonbin' ? ['PUT'] :
    ['POST', 'PUT', 'PATCH'];

  let last = null;
  for (const method of methods) {
    try {
      const res = await fetch(url, {
        method,
        headers,
        body: JSON.stringify(payload, null, 2)
      });
      const bodyText = await res.text().catch(() => '');
      if (res.ok) {
        return { ok: true, method, status: res.status, bodyText, provider, url };
      }
      last = { ok: false, method, status: res.status, bodyText: bodyText.slice(0, 300), provider, url };
    } catch (e) {
      last = { ok: false, method, status: 0, bodyText: String((e && e.message) || e), provider, url };
    }
  }
  return last || { ok: false, method: '', status: 0, bodyText: 'no attempts', provider, url };
}

/**
 * Понятное объяснение ошибки заливки для тоста/статуса.
 */
export function explainUploadFailure(result) {
  const { status, bodyText, method } = result || {};
  const detail = ((method ? method + ' ' : '') + (status || '') + (bodyText ? ': ' + bodyText : '')).slice(0, 140);

  let hint;
  if (status === 401 || status === 402 || status === 403) {
    hint = 'Хранилище отказало в записи (' + status + '). Проверь URL/ключ, либо используй бесплатную Pantry — getpantry.cloud (см. STREAMER_NO_REPO.md).';
  } else if (status === 404 || (bodyText || '').includes('Not Found')) {
    hint = 'Хранилище не найдено (404). Проверь URL: для Pantry — getpantry.cloud/apiv1/pantry/ID/basket/ИМЯ, корзина создаётся первой заливкой.';
  } else if (status === 400) {
    hint = 'Хранилище отклонило данные (400). Для Pantry — проверь, что pantry ID существует и payload влезает в лимит (1.44 МБ).';
  } else if (!status || (bodyText || '').includes('Failed to fetch') || (bodyText || '').includes('NetworkError') || (bodyText || '').includes('CORS')) {
    hint = 'Сеть/CORS не пустили запрос — попробуй ещё раз или используй scripts/upload_playnite_remote.py.';
  } else {
    hint = 'Не удалось залить. Проверь URL хранилища (см. STREAMER_NO_REPO.md) и попробуй ещё раз.';
  }
  return detail ? hint + ' (' + detail + ')' : hint;
}
