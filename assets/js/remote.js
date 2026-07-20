/**
 * Remote JSON upload helpers — provider-aware (Pantry / npoint / jsonbin / generic).
 *
 * Зачем это нужно:
 * npoint.io больше не принимает запись через API для бинов, привязанных к аккаунту
 * (401 без платного токена, 402 без premium; PUT/PATCH там вообще не маршрутизируются → 404).
 * Поэтому рекомендуемое хранилище для записи — Pantry (getpantry.cloud):
 *   POST /apiv1/pantry/{ID}/basket/{NAME} — создать или ПОЛНОСТЬЮ заменить корзину.
 * Бесплатно, CORS открыт, ключей не надо. Корзина живёт, пока к ней обращаются
 * (TTL продлевается каждым GET/POST — при активных зрителях практически вечно).
 */

export function detectProvider(url) {
  const u = (url || '').toLowerCase();
  if (u.includes('getpantry.cloud')) return 'pantry';
  if (u.includes('jsonbin.io')) return 'jsonbin';
  if (u.includes('npoint.io')) return 'npoint';
  return 'generic';
}

/**
 * Авто-фикс частой ошибки: docs-ссылка npoint вместо API-ссылки.
 */
export function fixNpointDocsUrl(url) {
  const m = (url || '').match(/https?:\/\/www\.npoint\.io\/docs\/([a-f0-9]+)/i);
  if (m) return 'https://api.npoint.io/' + m[1];
  return (url || '').trim();
}

/**
 * Заливка JSON в удалённое хранилище с правильной семантикой под провайдера.
 *
 * @param {string} rawUrl - URL корзины/бина (pantry / npoint / jsonbin / любой другой)
 * @param {object|Array} data - JSON-данные
 * @returns {Promise<{ok:boolean, method?:string, status?:number, bodyText?:string, provider:string, fixedUrl:string}>}
 */
export async function uploadJsonToRemote(rawUrl, data) {
  const fixedUrl = fixNpointDocsUrl(rawUrl);
  const provider = detectProvider(fixedUrl);

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
  // - npoint:  только POST маршрутизируется; для бинов с владельцем вернёт 401/402
  //            (нужен платный токен) — см. STREAMER_NO_REPO.md.
  // - generic: старое поведение, перебираем всё подряд.
  const methods =
    provider === 'pantry' ? ['POST'] :
    provider === 'jsonbin' ? ['PUT'] :
    provider === 'npoint' ? ['POST'] :
    ['POST', 'PUT', 'PATCH'];

  let last = null;
  for (const method of methods) {
    try {
      const res = await fetch(fixedUrl, {
        method,
        headers,
        body: JSON.stringify(payload, null, 2)
      });
      const bodyText = await res.text().catch(() => '');
      if (res.ok) {
        return { ok: true, method, status: res.status, bodyText, provider, fixedUrl };
      }
      last = { ok: false, method, status: res.status, bodyText: bodyText.slice(0, 300), provider, fixedUrl };
      if (provider === 'npoint') break; // 401/402 — другие методы всё равно 404
    } catch (e) {
      last = { ok: false, method, status: 0, bodyText: String((e && e.message) || e), provider, fixedUrl };
    }
  }
  return last || { ok: false, method: '', status: 0, bodyText: 'no attempts', provider, fixedUrl };
}

/**
 * Понятное объяснение ошибки заливки для тоста/статуса.
 */
export function explainUploadFailure(result) {
  const { provider, status, bodyText, method } = result || {};
  const detail = ((method ? method + ' ' : '') + (status || '') + (bodyText ? ': ' + bodyText : '')).slice(0, 140);

  let hint;
  if (provider === 'npoint' && (status === 401 || status === 402 || status === 403)) {
    hint = 'npoint закрыл запись через API для бинов, привязанных к аккаунту (нужен платный токен). ' +
      'Решение: создай бесплатное хранилище на getpantry.cloud и укажи его URL (см. STREAMER_NO_REPO.md).';
  } else if (status === 401) {
    hint = 'Хранилище ответило 401 (нет доступа). Проверь URL/ключ. Для jsonbin сохрани ключ в localStorage mikkleo_jsonbin_key.';
  } else if (status === 404 || (bodyText || '').includes('Not Found')) {
    hint = 'Хранилище не найдено (404). Проверь URL: для Pantry — getpantry.cloud/apiv1/pantry/ID/basket/ИМЯ, бин должен существовать.';
  } else if (status === 400) {
    hint = 'Хранилище отклонило данные (400). Для Pantry — проверь, что pantry ID существует и payload влезает в лимит (1.44 МБ).';
  } else if (status === 403) {
    hint = 'Доступ запрещён (403) — проверь права или ключ.';
  } else if (!status || (bodyText || '').includes('Failed to fetch') || (bodyText || '').includes('NetworkError') || (bodyText || '').includes('CORS')) {
    hint = 'Сеть/CORS не пустили запрос — попробуй ещё раз или используй scripts/upload_playnite_remote.py.';
  } else {
    hint = 'Не удалось залить. Проверь URL хранилища (см. STREAMER_NO_REPO.md) и попробуй ещё раз.';
  }
  return detail ? hint + ' (' + detail + ')' : hint;
}
