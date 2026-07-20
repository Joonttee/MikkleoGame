/**
 * Admin panel — PIN-protected local overrides.
 * Refactored for performance: virtual-ish filtering, no full re-render on intype.
 */
import { STORAGE_KEYS } from './config.js';
import { esc } from './utils.js';
import {
  loadOverrides, saveOverrides, isAdmin, setAdmin,
  getEffectiveStatus, getEffectiveFlag, getBaseFlag,
  getStoredPinHash, setStoredPinHash, removeStoredPin,
  validateAndHashPin, clearOverridesCache,
  getRemoteOverridesUrl, getRemoteGamesUrl
} from './storage.js';
import { uploadJsonToRemote, explainUploadFailure } from './remote.js';

function renderPrompt() {
  const hasPin = !!getStoredPinHash();
  return `
    <div class="admin-prompt">
      <div style="font-size: 36px;">🔐</div>
      <div style="font-weight:800; font-size:18px;">${hasPin ? 'Введите PIN-код' : 'Задайте новый PIN-код'}</div>
      <p>${hasPin ? 'PIN хранится локально в этом браузере. 4–6 цифр.' : 'Придумайте 4–6 цифр. Этот PIN будет запрашиваться при открытии админки.'}</p>
      <input id="adminPinInput" type="password" inputmode="numeric" pattern="[0-9]*" maxlength="6" placeholder="••••" autocomplete="off">
      <div class="err" id="adminPinErr"></div>
      <button class="btn-action" id="adminPinSubmit" style="height:42px; padding:0 22px; font-size:13px; background:var(--accent); color:#04101A; border-color:var(--accent);">
        ${hasPin ? 'Войти' : 'Задать PIN и войти'}
      </button>
      ${hasPin ? '<button class="btn-action" id="adminForgetPin" style="height:36px; padding:0 14px; font-size:12px; background:transparent; color:var(--muted); border-color:transparent;">Забыли PIN? Сбросить</button>' : ''}
    </div>
  `;
}

function renderList(games) {
  const overrides = loadOverrides();
  const totalOverrides = Object.keys(overrides).length;
  // Показываем эффективные URL: ручные (localStorage) > из data/remote.json
  let remoteUrl = '';
  let remoteGamesUrl = '';
  try {
    remoteUrl = localStorage.getItem('mikkleo_remote_overrides_url') || '';
    remoteGamesUrl = localStorage.getItem('mikkleo_remote_games_url') || '';
  } catch {}
  if (!remoteUrl) remoteUrl = getRemoteOverridesUrl() || '';
  if (!remoteGamesUrl) remoteGamesUrl = getRemoteGamesUrl() || '';
  const hiddenCount = games.filter(g => getEffectiveFlag(g, 'isHidden')).length;
  const html = games.map(g => {
    const eff = getEffectiveStatus(g);
    const gachaOn = getEffectiveFlag(g, 'isGacha');
    const mpOn = getEffectiveFlag(g, 'isMultiplayer');
    const coopOn = getEffectiveFlag(g, 'isCoop');
    const hiddenOn = getEffectiveFlag(g, 'isHidden');
    const isOverridden = !!overrides[g.id];
    const statusIsOverridden = isOverridden && overrides[g.id].status !== undefined;
    return `
      <div class="admin-row ${isOverridden ? 'has-override' : ''} ${hiddenOn ? 'admin-row-hidden' : ''}" data-id="${esc(g.id)}" data-title="${esc((g.title || '').toLowerCase())}">
        <img class="admin-cover" src="${esc(g.image || '')}" alt="" onerror="this.style.visibility='hidden'">
        <div>
          <div class="admin-title">${esc(g.title || 'Без названия')}</div>
          <div style="font-size:11px; color:var(--muted); margin-top:2px;">${esc(g.genre || '')} · ${g.year || ''}${hiddenOn ? ' · 🙈 скрыта от зрителей' : ''}</div>
        </div>
        <div class="admin-controls">
          <button class="admin-flag hide ${hiddenOn ? 'on' : ''}" data-flag="isHidden" title="Скрыть от зрителей / показать">🙈</button>
          <button class="admin-flag ${gachaOn ? 'on' : ''}" data-flag="isGacha" title="Гача">💫</button>
          <button class="admin-flag mp ${mpOn ? 'on' : ''}" data-flag="isMultiplayer" title="Мультиплеер">🕹️</button>
          <button class="admin-flag coop ${coopOn ? 'on' : ''}" data-flag="isCoop" title="Кооп">🤝</button>
          <select class="admin-status" title="Статус">
            <option value="__default__" ${!statusIsOverridden ? 'selected' : ''}>— дефолт —</option>
            <option value="in_progress" ${eff === 'in_progress' && statusIsOverridden ? 'selected' : ''}>⏳ В процессе</option>
            <option value="completed" ${eff === 'completed' && statusIsOverridden ? 'selected' : ''}>✅ Пройдено</option>
            <option value="planned" ${eff === 'planned' && statusIsOverridden ? 'selected' : ''}>📌 В планах</option>
            <option value="none" ${eff === 'none' && statusIsOverridden ? 'selected' : ''}>🆕 Не начато</option>
          </select>
        </div>
      </div>
    `;
  }).join('');

  return `
    <div class="admin-toolbar">
      <input id="adminSearch" type="text" placeholder="🔍 Поиск по названию..." autocomplete="off">
      <button class="btn-action" id="adminLogoutBtn" style="height:36px; padding:0 14px; font-size:12px; background:transparent; color:var(--muted);">🚪 Выйти</button>
    </div>

    <div class="admin-meta-info" style="margin-bottom:12px; display:flex; flex-direction:column; gap:10px;">
      <div><b>Для стримера без доступа к репе:</b> статусы и новые игры хранятся в удалённом JSON. Рекомендуемое хранилище — <b>Pantry</b> (getpantry.cloud, бесплатная запись из браузера).</div>
      <div style="display:flex; gap:8px; flex-wrap:wrap; align-items:center;">
        <span style="font-size:11px; min-width:70px;">Статусы:</span>
        <input id="remoteUrlInput" type="text" value="${esc(remoteUrl)}" placeholder="https://getpantry.cloud/apiv1/pantry/ID/basket/mikkleo-statuses" style="flex:1; min-width:180px; height:36px; padding:0 12px; border-radius:10px; background:var(--card); border:1px solid var(--border); color:var(--text); font-size:12px;">
        <button class="btn-action" id="saveRemoteUrlBtn" style="height:36px;">💾 URL</button>
        <button class="btn-action" id="exportToRemoteBtn" style="height:36px; background:rgba(124,255,178,.15); color:var(--accent2); border-color:rgba(124,255,178,.3);">⬆️ Статусы</button>
      </div>
      <div style="display:flex; gap:8px; flex-wrap:wrap; align-items:center;">
        <span style="font-size:11px; min-width:70px;">Игры Playnite:</span>
        <input id="remoteGamesUrlInput" type="text" value="${esc(remoteGamesUrl)}" placeholder="https://getpantry.cloud/apiv1/pantry/ID/basket/mikkleo-games" style="flex:1; min-width:180px; height:36px; padding:0 12px; border-radius:10px; background:var(--card); border:1px solid var(--border); color:var(--text); font-size:12px;">
        <button class="btn-action" id="saveRemoteGamesUrlBtn" style="height:36px;">💾 URL</button>
      </div>
      <div style="font-size:11px; color:var(--muted); line-height:1.4;">
        Статусы: <b>${esc(remoteUrl || './data/overrides.json')}</b> | Игры: <b>${esc(remoteGamesUrl || '(не задано)')}</b><br>
        Скрипт для заливки игр без репы: <code>python scripts/upload_playnite_remote.py --input library.json --remote-url https://getpantry.cloud/apiv1/pantry/ID/basket/mikkleo-games</code><br>
        Инструкция: <code>PLAYNITE.md</code> и <code>STREAMER_NO_REPO.md</code>
      </div>
    </div>

    <div class="admin-list" id="adminList">${html}</div>
    <div class="admin-meta-info">
      Локальных правок: <b>${totalOverrides}</b> · Скрыто от зрителей: <b>${hiddenCount}</b>.
      Правки хранятся только в этом браузере до заливки (⬆️ Статусы — тогда статусы и скрытые игры увидят все).
      Скачайте JSON, чтобы перенести на другое устройство. Для публикации без доступа к репе — используй удалённый URL выше.
    </div>
  `;
}

export function createAdminPanel({ games, onDataChanged, showToast }) {
  const backEl = document.getElementById('adminBack');
  const contentEl = document.getElementById('adminContent');

  function applyAdminVisibility() {
    if (isAdmin()) document.body.classList.add('is-admin');
    else document.body.classList.remove('is-admin');
  }

  function open() {
    backEl.classList.add('open');
    document.body.style.overflow = 'hidden';
    render();
  }

  function close() {
    backEl.classList.remove('open');
    document.body.style.overflow = '';
  }

  function tryLogin() {
    const input = document.getElementById('adminPinInput');
    const err = document.getElementById('adminPinErr');
    const pin = (input?.value || '').trim();
    const hashed = validateAndHashPin(pin);
    if (!hashed) {
      err.textContent = 'PIN должен быть 4–6 цифр';
      return;
    }
    const stored = getStoredPinHash();
    if (stored) {
      if (stored === hashed) {
        setAdmin(true);
        applyAdminVisibility();
        render();
      } else {
        err.textContent = 'Неверный PIN';
        input.value = '';
        input.focus();
      }
    } else {
      setStoredPinHash(hashed);
      setAdmin(true);
      applyAdminVisibility();
      render();
    }
  }

  function forgetPin() {
    if (!confirm('Сбросить PIN? Локальные правки статусов останутся.')) return;
    removeStoredPin();
    setAdmin(false);
    applyAdminVisibility();
    render();
  }

  function logout() {
    setAdmin(false);
    applyAdminVisibility();
    close();
  }

  function exportOverrides() {
    const data = loadOverrides();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'mikkleo-overrides.json';
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    showToast('Файл сохранён в загрузках');
  }

  function confirmReset() {
    if (!confirm('Удалить ВСЕ локальные правки? Это необратимо.')) return;
    try {
      localStorage.removeItem(STORAGE_KEYS.OVERRIDES);
      clearOverridesCache();
    } catch {}
    onDataChanged();
    render();
    showToast('Локальные правки сброшены');
  }

  function render() {
    if (!contentEl) return;
    if (!isAdmin()) {
      contentEl.innerHTML = renderPrompt();
      const input = document.getElementById('adminPinInput');
      const submit = document.getElementById('adminPinSubmit');
      const forget = document.getElementById('adminForgetPin');
      if (input) {
        input.focus();
        input.addEventListener('keydown', (e) => { if (e.key === 'Enter') tryLogin(); });
      }
      if (submit) submit.addEventListener('click', tryLogin);
      if (forget) forget.addEventListener('click', forgetPin);
      return;
    }

    contentEl.innerHTML = renderList(games);

    // Search filter — O(n) hide/show, not re-render
    const search = document.getElementById('adminSearch');
    if (search) {
      search.addEventListener('input', () => {
        const q = search.value.toLowerCase().trim();
        contentEl.querySelectorAll('.admin-row').forEach(r => {
          r.style.display = (!q || r.dataset.title.includes(q)) ? '' : 'none';
        });
      });
    }

    document.getElementById('adminLogoutBtn')?.addEventListener('click', logout);

    // Remote URL handling for streamer without repo access
    const remoteInput = document.getElementById('remoteUrlInput');
    const remoteGamesInput = document.getElementById('remoteGamesUrlInput');
    const saveRemoteBtn = document.getElementById('saveRemoteUrlBtn');
    const saveRemoteGamesBtn = document.getElementById('saveRemoteGamesUrlBtn');
    const exportRemoteBtn = document.getElementById('exportToRemoteBtn');

    if (saveRemoteBtn && remoteInput) {
      saveRemoteBtn.addEventListener('click', () => {
        const url = remoteInput.value.trim();
        try {
          if (url) localStorage.setItem('mikkleo_remote_overrides_url', url);
          else localStorage.removeItem('mikkleo_remote_overrides_url');
          showToast(url ? 'URL статусов сохранён' : 'URL статусов очищен');
        } catch {}
      });
    }

    if (saveRemoteGamesBtn && remoteGamesInput) {
      saveRemoteGamesBtn.addEventListener('click', () => {
        const url = remoteGamesInput.value.trim();
        try {
          if (url) localStorage.setItem('mikkleo_remote_games_url', url);
          else localStorage.removeItem('mikkleo_remote_games_url');
          showToast(url ? 'URL игр сохранён — перезагрузи страницу' : 'URL игр очищен');
        } catch {}
      });
    }

    if (exportRemoteBtn) {
      exportRemoteBtn.addEventListener('click', async () => {
        // URL для заливки: то, что сейчас в поле > localStorage > data/remote.json
        let url = (remoteInput && remoteInput.value.trim()) || '';
        if (!url) {
          try { url = localStorage.getItem('mikkleo_remote_overrides_url') || ''; } catch {}
        }
        if (!url) url = getRemoteOverridesUrl() || '';
        if (!url) {
          showToast('Сначала сохрани URL удалённого хранилища (или пропиши его в data/remote.json)');
          return;
        }
        const data = loadOverrides();
        if (!Object.keys(data).length) {
          const ok = confirm('Локально правок нет. Заливка ПОЛНОСТЬЮ ЗАМЕНИТ удалённое хранилище пустым набором — удалённые статусы и скрытые метки пропадут у зрителей. Продолжить?');
          if (!ok) return;
        }
        showToast('Заливаю на ' + url + ' ...');
        const result = await uploadJsonToRemote(url, data);
        if (result.ok) {
          showToast('✓ Удалённо сохранено! (' + result.method + ' → ' + result.provider + ') Зрители увидят после перезагрузки');
        } else {
          showToast(explainUploadFailure(result));
        }
      });
    }

    // Delegated handlers for performance
    contentEl.querySelectorAll('.admin-row').forEach(row => {
      const id = row.dataset.id;
      const statusSel = row.querySelector('.admin-status');
      if (statusSel) {
        statusSel.addEventListener('change', () => {
          const v = statusSel.value;
          const overrides = loadOverrides();
          if (!overrides[id]) overrides[id] = {};
          if (v === '__default__') delete overrides[id].status;
          else overrides[id].status = v;
          // cleanup empty object
          if (Object.keys(overrides[id]).length === 0) delete overrides[id];
          saveOverrides(overrides);
          onDataChanged();
          // lightweight UI update: mark row
          if (overrides[id]) row.classList.add('has-override');
          else row.classList.remove('has-override');
        });
      }
      row.querySelectorAll('.admin-flag').forEach(btn => {
        btn.addEventListener('click', () => {
          const flag = btn.dataset.flag;
          const gameObj = games.find(g => g.id === id);
          if (!gameObj) return;
          const overrides = loadOverrides();
          if (!overrides[id]) overrides[id] = {};
          const current = getEffectiveFlag(gameObj, flag);
          const base = getBaseFlag(gameObj, flag); // remote -> дефолт каталога
          const target = !current;
          // Локальный оверрайд нужен только если его значение отличается от базового
          // (иначе он бессмысленный). Так можно и СНЯТЬ удалённый флаг (local=false при
          // remote=true), и удалить свой ранее выставленный локальный флаг.
          if (target === base) delete overrides[id][flag];
          else overrides[id][flag] = target;
          if (Object.keys(overrides[id]).length === 0) delete overrides[id];
          saveOverrides(overrides);
          // toggle button UI immediately
          const newVal = getEffectiveFlag(gameObj, flag);
          btn.classList.toggle('on', newVal);
          if (flag === 'isHidden') row.classList.toggle('admin-row-hidden', newVal);
          if (overrides[id]) row.classList.add('has-override');
          else row.classList.remove('has-override');
          onDataChanged();
        });
      });
    });
  }

  // Attach global events (only once)
  backEl?.addEventListener('click', (e) => {
    if (e.target.id === 'adminBack') close();
  });

  // Expose methods globally for toolbar buttons that were inline before
  window.openAdminPanel = open;
  window.closeAdminPanel = close;
  window.exportOverrides = exportOverrides;
  window.confirmReset = confirmReset;
  window.adminLogout = logout;
  window.tryAdminLogin = tryLogin;
  window.forgetPin = forgetPin;

  return { open, close, render, applyAdminVisibility, exportOverrides, confirmReset };
}
