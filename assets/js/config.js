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
