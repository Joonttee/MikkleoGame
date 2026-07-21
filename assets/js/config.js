/**
 * Mikkleo Games — Configuration constants
 * Centralised config to avoid scattering magic strings.
 */

export const STATUS_MAP = {
  completed: { label: 'Пройдено', emoji: '✅', class: 'status-completed' },
  in_progress: { label: 'В процессе', emoji: '⏳', class: 'status-in_progress' },
  planned: { label: 'В планах', emoji: '📌', class: 'status-planned' },
  none: { label: 'Не начато', emoji: '🆕', class: 'status-none' }
};

export const SEARCH_MAP = {
  'ведьмак': ['ведьмак', 'the witcher', 'witcher'],
  'witcher': ['witcher', 'ведьмак', 'the witcher'],
  'the witcher': ['the witcher', 'ведьмак', 'witcher'],
  'gwent': ['gwent', 'гвинт'],
  'гвинт': ['гвинт', 'gwent'],
  'кровная': ['кровная вражда', 'thronebreaker', 'the witcher tales'],
  'thronebreaker': ['thronebreaker', 'кровная вражда', 'ведьмак'],
  'бесконечное лето': ['бесконечное лето', 'everlasting summer'],
  'everlasting summer': ['everlasting summer', 'бесконечное лето'],
  'холат': ['холат', 'kholat'],
  'kholat': ['kholat', 'холат']
};

/**
 * Канонические жанровые группы.
 * В каталоге жанры смешанные: Playnite отдаёт русские («Экшены», «Ролевые игры»),
 * Steam-экспорт — английские («Action», «RPG»). tokens — lowercase-подстроки,
 * по которым строка жанра игры относится к группе (матч через includes).
 * Порядок групп важен: он задаёт приоритет при выборе «главного» жанра игры.
 */
export const GENRE_GROUPS = {
  action:     { label: 'Экшены',                  tokens: ['экшен', 'action'] },
  rpg:        { label: 'Ролевые (RPG)',           tokens: ['ролев', 'рпг', 'rpg', 'jrpg'] },
  adventure:  { label: 'Приключения',             tokens: ['приключен', 'adventure'] },
  indie:      { label: 'Инди',                    tokens: ['инди', 'indie'] },
  strategy:   { label: 'Стратегии',               tokens: ['стратег', 'strategy'] },
  simulation: { label: 'Симуляторы',              tokens: ['симулятор', 'simulation', 'simulator'] },
  casual:     { label: 'Казуальные',              tokens: ['казуал', 'casual'] },
  shooter:    { label: 'Шутеры',                  tokens: ['шутер', 'shooter', 'fps'] },
  platformer: { label: 'Платформеры',             tokens: ['платформер', 'platformer', 'метроидван', 'metroidvania'] },
  puzzle:     { label: 'Пазлы / Головоломки',     tokens: ['пазл', 'головоломк', 'puzzle'] },
  racing:     { label: 'Гонки',                   tokens: ['гонк', 'racing'] },
  sports:     { label: 'Спортивные',              tokens: ['спорт', 'sports'] },
  fighting:   { label: 'Файтинги',                tokens: ['файтинг', 'fighting'] },
  arcade:     { label: 'Аркады',                  tokens: ['аркад', 'arcade'] },
  card:       { label: 'Карточные / Настольные',  tokens: ['карточн', 'настольн', 'card', 'board games'] },
  mmo:        { label: 'Многопользовательские',   tokens: ['многопользовательск', 'massively', 'mmorpg', 'mmo', 'ммо'] },
  free:       { label: 'Бесплатные (F2P)',        tokens: ['бесплатн', 'free to play', 'f2p'] },
  early:      { label: 'Ранний доступ',           tokens: ['ранний доступ', 'early access'] }
};

export const STORAGE_KEYS = {
  OVERRIDES: 'mikkleo_streamer_overrides_v1',
  ADMIN_SESSION: 'mikkleo_admin_session',
  ADMIN_PIN: 'mikkleo_admin_pin_hash_v1',
  VIEW_MODE: 'mikkleo_view_mode',
  THEME: 'mikkleo_theme',
  STREAM_CACHE: 'mikkleo_stream_cache'
};

export const TWITCH = {
  CHANNEL: 'mikkleovt',
  ENDPOINTS: [
    `https://api.ivr.fi/v2/twitch/user?login=mikkleovt`,
    `https://decapi.me/twitch/uptime/mikkleovt`,
    `https://decapi.me/twitch/is_live/mikkleovt`
  ],
  CHECK_INTERVAL: 35 * 1000,
  CACHE_TTL: 3 * 60 * 1000
};

export const UI = {
  DEFAULT_VISIBLE: 72,
  LOAD_MORE_STEP: 72,
  SEARCH_DEBOUNCE: 120,
  TOAST_DURATION: 2600
};
