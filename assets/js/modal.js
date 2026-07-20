/**
 * Game modal logic
 */
import { STATUS_MAP } from './config.js';
import { esc, copyText } from './utils.js';
import { getEffectiveStatus } from './storage.js';

let activeModalGame = null;

function getElements() {
  return {
    back: document.getElementById('modalBack'),
    title: document.getElementById('modalTitle'),
    altTitle: document.getElementById('modalAltTitle'),
    imgBg: document.getElementById('modalImgBg'),
    imgMain: document.getElementById('modalImgMain'),
    initials: document.getElementById('modalInitials'),
    badges: document.getElementById('modalBadges'),
    steamLink: document.getElementById('modalSteamLink'),
    ytLink: document.getElementById('modalYtLink'),
    shareBtn: document.getElementById('modalShareBtn'),
    closeBtn: document.getElementById('modalClose'),
    body: document.querySelector('.modal-body')
  };
}

export function openModal(game, showToast) {
  activeModalGame = game;
  try {
    window.location.hash = 'game-' + game.id;
  } catch {}

  const el = getElements();
  if (el.body) el.body.scrollTop = 0;

  el.title.textContent = game.title;
  el.altTitle.textContent = game.altTitle ? 'Альтернативное название: ' + game.altTitle : '';

  const initials = (game.title || 'Game').slice(0, 2).toUpperCase();

  // Новое отображение: в модалке обложка на всю панель, без искажений, без размытого фона
  // Grid использует cover для фикс размера, а модалка — contain на всю ширину для хорошей видимости
  if (game.image) {
    // Размытый фон больше не используем
    if (el.imgBg) el.imgBg.style.display = 'none';
    el.imgMain.src = game.image;
    el.imgMain.style.display = 'block';
    el.imgMain.alt = game.title;
    // Убираем ограничения, ставим на всю панель через CSS (contain)
    el.initials.style.display = 'none';
  } else {
    if (el.imgBg) el.imgBg.style.display = 'none';
    el.imgMain.style.display = 'none';
    el.initials.textContent = initials;
    el.initials.style.display = 'block';
  }

  const effStatus = getEffectiveStatus(game);
  const stInfo = STATUS_MAP[effStatus] || STATUS_MAP['none'];

  el.badges.innerHTML = `
    <span class="status-tag ${stInfo.class}" style="position:static;">${stInfo.emoji} ${stInfo.label}</span>
    <span class="meta-tag accent">${esc(game.genre)}</span>
    <span class="meta-tag">Год: ${game.year}</span>
  `;

  const steamQuery = game.altTitle || game.title;
  const qTitle = encodeURIComponent(steamQuery);

  if (game.steamUrl) {
    el.steamLink.href = game.steamUrl;
    el.steamLink.textContent = '🛒 Открыть в Steam';
  } else if (game.steamAppId) {
    el.steamLink.href = `https://store.steampowered.com/app/${game.steamAppId}`;
    el.steamLink.textContent = '🛒 Открыть в Steam';
  } else if (game.platform === 'Switch') {
    el.steamLink.href = `https://duckduckgo.com/?q=!ducky+site%3Anintendo.com+${qTitle}`;
    el.steamLink.textContent = '🎮 Nintendo eShop';
  } else if (game.platform === 'HoYoPlay') {
    el.steamLink.href = `https://duckduckgo.com/?q=!ducky+site%3Ahoyoverse.com+${qTitle}`;
    el.steamLink.textContent = '💫 Официальный сайт';
  } else if (game.platform === 'Ubisoft') {
    el.steamLink.href = `https://duckduckgo.com/?q=!ducky+site%3Astore.ubisoft.com+${qTitle}`;
    el.steamLink.textContent = '🌐 Ubisoft Store';
  } else {
    el.steamLink.href = `https://duckduckgo.com/?q=!ducky+site%3Astore.steampowered.com%2Fapp%2F+${qTitle}`;
    el.steamLink.textContent = '🛒 Открыть в Steam';
  }

  el.ytLink.href = `https://www.youtube.com/@mikkleostream/playlists?query=${qTitle}`;

  el.shareBtn.onclick = async () => {
    const shareUrl = window.location.origin + window.location.pathname + '#game-' + game.id;
    const ok = await copyText(shareUrl);
    showToast(ok ? 'Ссылка на игру скопирована!' : 'Ссылка: ' + shareUrl);
  };

  el.back.classList.add('open');
  document.body.style.overflow = 'hidden';
}

export function closeModal() {
  const el = getElements();
  el.back.classList.remove('open');
  document.body.style.overflow = '';
  if (window.location.hash.startsWith('#game-')) {
    try {
      history.replaceState(null, null, ' ');
    } catch {}
  }
}

export function initModal(showToast) {
  const el = getElements();
  el.back.addEventListener('click', e => {
    if (e.target.id === 'modalBack') closeModal();
  });
  el.closeBtn.onclick = closeModal;

  // expose for render module
  return { openModal: (g) => openModal(g, showToast), closeModal };
}
