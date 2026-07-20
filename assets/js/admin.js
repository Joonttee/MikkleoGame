/**
 * Admin panel — PIN-protected local overrides.
 * Refactored for performance: virtual-ish filtering, no full re-render on intype.
 */
import { STORAGE_KEYS } from './config.js';
import { esc } from './utils.js';
import {
  loadOverrides, saveOverrides, isAdmin, setAdmin,
  getEffectiveStatus, getEffectiveFlag,
  getStoredPinHash, setStoredPinHash, removeStoredPin,
  validateAndHashPin, clearOverridesCache
} from './storage.js';

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
  let remoteUrl = '';
  let remoteGamesUrl = '';
  try {
    remoteUrl = localStorage.getItem('mikkleo_remote_overrides_url') || '';
    remoteGamesUrl = localStorage.getItem('mikkleo_remote_games_url') || '';
  } catch {}
  const html = games.map(g => {
    const eff = getEffectiveStatus(g);
    const gachaOn = getEffectiveFlag(g, 'isGacha');
    const mpOn = getEffectiveFlag(g, 'isMultiplayer');
    const coopOn = getEffectiveFlag(g, 'isCoop');
    const isOverridden = !!overrides[g.id];
    const statusIsOverridden = isOverridden && overrides[g.id].status !== undefined;
    return `
      <div class="admin-row ${isOverridden ? 'has-override' : ''}" data-id="${esc(g.id)}" data-title="${esc((g.title || '').toLowerCase())}">
        <img class="admin-cover" src="${esc(g.image || '')}" alt="" onerror="this.style.visibility='hidden'">
        <div>
          <div class="admin-title">${esc(g.title || 'Без названия')}</div>
          <div style="font-size:11px; color:var(--muted); margin-top:2px;">${esc(g.genre || '')} · ${g.year || ''}</div>
        </div>
        <div class="admin-controls">
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
      <div><b>Для стримера без доступа к репе:</b> укажи URL удалённых JSON (gist, npoint.io). Тогда все зрители увидят статусы и новые игры без пуша в GitHub.</div>
      <div style="display:flex; gap:8px; flex-wrap:wrap; align-items:center;">
        <span style="font-size:11px; min-width:70px;">Статусы:</span>
        <input id="remoteUrlInput" type="text" value="${esc(remoteUrl)}" placeholder="https://api.npoint.io/.../overrides" style="flex:1; min-width:180px; height:36px; padding:0 12px; border-radius:10px; background:var(--card); border:1px solid var(--border); color:var(--text); font-size:12px;">
        <button class="btn-action" id="saveRemoteUrlBtn" style="height:36px;">💾 URL</button>
        <button class="btn-action" id="exportToRemoteBtn" style="height:36px; background:rgba(124,255,178,.15); color:var(--accent2); border-color:rgba(124,255,178,.3);">⬆️ Статусы</button>
      </div>
      <div style="display:flex; gap:8px; flex-wrap:wrap; align-items:center;">
        <span style="font-size:11px; min-width:70px;">Игры Playnite:</span>
        <input id="remoteGamesUrlInput" type="text" value="${esc(remoteGamesUrl)}" placeholder="https://api.npoint.io/.../games или gist raw library.json" style="flex:1; min-width:180px; height:36px; padding:0 12px; border-radius:10px; background:var(--card); border:1px solid var(--border); color:var(--text); font-size:12px;">
        <button class="btn-action" id="saveRemoteGamesUrlBtn" style="height:36px;">💾 URL</button>
      </div>
      <div style="font-size:11px; color:var(--muted); line-height:1.4;">
        Статусы: <b>${esc(remoteUrl || './data/overrides.json')}</b> | Игры: <b>${esc(remoteGamesUrl || '(не задано)')}</b><br>
        Скрипт для заливки игр без репы: <code>python scripts/upload_playnite_remote.py --input library.json --remote-url https://api.npoint.io/ID_GAMES</code><br>
        Инструкция: <code>PLAYNITE.md</code> и <code>STREAMER_NO_REPO.md</code>
      </div>
    </div>

    <div class="admin-list" id="adminList">${html}</div>
    <div class="admin-meta-info">
      Локальных правок: <b>${totalOverrides}</b>. Правки хранятся только в этом браузере.
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
        let url = '';
        try {
          url = localStorage.getItem('mikkleo_remote_overrides_url') || '';
        } catch {}
        if (!url) {
          showToast('Сначала сохрани URL удалённого хранилища');
          return;
        }
        url = url.trim();
        // Auto-fix common mistake: docs URL instead of API URL for npoint.io
        const docsMatch = url.match(/https?:\/\/www\.npoint\.io\/docs\/([a-f0-9]+)/);
        if (docsMatch) {
          url = 'https://api.npoint.io/' + docsMatch[1];
          showToast('URL исправлен: ' + url);
        }
        const data = loadOverrides();
        try {
          showToast('Заливаю...');
          // Try POST, PUT, PATCH (like Python script upload_playnite_remote.py)
          const methods = ['POST', 'PUT', 'PATCH'];
          let success = false;
          let lastErr = '';
          for (const method of methods) {
            try {
              const res = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data, null, 2)
              });
              if (res.ok) {
                showToast('✓ Удалённо сохранено! (' + method + ') Зрители увидят после перезагрузки');
                success = true;
                break;
              } else {
                const bodyText = await res.text().catch(() => '');
                lastErr = method + ' ' + res.status + ': ' + bodyText.slice(0, 200);
              }
            } catch (e) {
              lastErr = method + ' error: ' + (e.message || e);
            }
          }
          if (!success) {
            throw new Error(lastErr || 'All methods failed');
          }
        } catch (e) {
          const msg = (e && e.message) ? String(e.message) : String(e);
          let hint = 'Не удалось залить напрямую.';
          if (msg.includes('404') || msg.includes('Not Found')) {
            hint += ' Возможно, это docs-ссылка npoint.io (нужен api.npoint.io/...). Проверь URL.';
          } else if (msg.includes('403') || msg.includes('Forbidden')) {
            hint += ' Доступ запрещён — проверь права или токен.';
          } else if (msg.includes('CORS') || msg.includes('NetworkError')) {
            hint += ' CORS/сетевой блок — попробуй через gist или jsonbin, или используй Python-скрипт.';
          } else {
            hint += ' Нужен npoint/jsonbin. Проверь что URL правильный (api.npoint.io/ID) и попробуй ещё раз.';
          }
          showToast(hint + ' (' + msg.slice(0, 120) + ')');
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
          if (overrides[id][flag] === undefined) {
            overrides[id][flag] = !current;
            if (overrides[id][flag] === !!gameObj[flag]) delete overrides[id][flag];
          } else {
            overrides[id][flag] = !overrides[id][flag];
            if (overrides[id][flag] === !!gameObj[flag]) delete overrides[id][flag];
          }
          if (Object.keys(overrides[id]).length === 0) delete overrides[id];
          saveOverrides(overrides);
          // toggle button UI immediately
          const newVal = getEffectiveFlag(gameObj, flag);
          btn.classList.toggle('on', newVal);
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
