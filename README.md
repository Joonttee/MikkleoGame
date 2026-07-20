# Mikkleo Games — Коллекция игр MikkleoVT

Сайт-каталог стримов, прохождений и игровых проектов MikkleoVT.  
Оптимизированная, модульная версия (2026).

🔗 **Live:** `https://Joonttee.github.io/MikkleoGame/` (GitHub Pages)

---

## ✨ Что было улучшено (рефакторинг 2026)

### Проблемы до рефакторинга
- Всё в одном файле `index.html` ~380КБ (CSS+JS+данные)
- Дублирование шаблона в `build_index.py` (~85КБ) → рассинхрон
- `GAMES` массив внутри HTML — тяжело поддерживать, медленная загрузка
- `loadOverrides()` парсил `localStorage` на каждую карточку (O(n²))
- Статистика считалась 3× `filter()` на каждый рендер
- Twitch-фолбэк делал CORS-запрос на `twitch.tv` (всегда fail)
- CSS дублировал `@media` блоки, нет `content-visibility`
- Нет разделения на модули, нет `data/games.json`

### Что стало

**Структура репозитория:**

```
/ (root)
├── index.html              # 14KB, лёгкий скелет, подключает модули
├── data/
│   └── games.json          # 830 игр, отдельный файл (342KB)
├── assets/
│   ├── css/
│   │   └── style.css       # оптимизированный, дедуплицированные медиа-запросы
│   ├── js/
│   │   ├── app.js          # главный модуль (ESM)
│   │   ├── config.js       # константы STATUS_MAP, SEARCH_MAP, ключи
│   │   ├── utils.js        # esc, expandQuery, debounce, hashPin
│   │   ├── storage.js      # кэшированный loadOverrides, PIN
│   │   ├── theme.js        # переключение тем
│   │   ├── filters.js      # filterGames + sortGames (чистые функции)
│   │   ├── render.js       # рендер с DocumentFragment + single-pass stats
│   │   ├── modal.js        # модалка игры
│   │   ├── twitch.js       # проверка стрима без CORS fallback
│   │   ├── admin.js        # PIN-админка
│   │   └── data.js         # ESM fallback (автогенерация из JSON)
│   └── img/
│       ├── hero.jpg
│       ├── mikkleo-avatar.jpg
│       └── favicons
├── covers/                 # 827 обложек (246MB)
├── scripts/
│   ├── build_index.py      # валидация + генерация data.js
│   └── sync_covers.py      # матчинг обложек → JSON
├── build_index.py          # wrapper для совместимости
├── sync_covers.py          # wrapper
└── README.md
```

**Оптимизации кода:**

- ✅ **Кэширование overrides:** `storage.js` мемоизирует `localStorage` парсинг, инвалидация только на `save`
- ✅ **Single-pass stats:** раньше 3× `GAMES.filter()` → теперь 1 проход
- ✅ **DocumentFragment:** рендер 72+ карточек без thrashing
- ✅ **Debounce 120ms** на поиск + `scrollbar-gutter: stable`
- ✅ **Убран CORS fallback** на `twitch.tv`, оставлены только `api.ivr.fi` + `decapi.me`
- ✅ **CSS:** `contain: content; will-change: transform` на карточках, объединены медиа-запросы, сокращён с 37КБ до 31КБ
- ✅ **ES Modules:** `type="module"` → браузер кэширует отдельно CSS/JS/JSON
- ✅ **Async data loading:** `fetch('./data/games.json')` + fallback `data.js`
- ✅ **Чистые функции:** `filterGames`, `sortGames` легко тестировать
- ✅ **Python:** валидация, дедупликация ID, проверка year range, отчёт о missing covers

---

## 🚀 Локальный запуск

Просто откройте `index.html` через HTTP-сервер (из-за ESM и fetch нужен сервер, не `file://`):

```bash
# Python
python -m http.server 8000

# Node
npx serve .
```

Откройте `http://localhost:8000`

---

## 🛠 Скрипты

### `python scripts/build_index.py`
Валидирует `data/games.json`:
- Проверяет обязательные поля (`id`, `title`, `year`)
- Нормализует булевы флаги, статус
- Дедуплицирует `id`
- Сортирует по названию для детерминизма
- Генерирует `assets/js/data.js` (ESM fallback)

### `python scripts/sync_covers.py`
Сканирует `covers/` и сопоставляет файлы с играми по нормализованному названию:
- Учитывает `title` и `altTitle`
- Фаззи-матч по подстроке (≥4 символа)
- Обновляет `image` поле в JSON
- Вызывает `build_index.py` для регенерации `data.js`

```bash
python scripts/sync_covers.py
```

---

## 🎮 Добавление игры

1. Отредактируйте `data/games.json`:
```json
{
  "id": "my-game-2026",
  "title": "My New Game",
  "genre": "Инди, Приключения",
  "platform": "Steam/Epic",
  "year": 2026,
  "image": "covers/My New Game.jpg",
  "status": null,
  "isGacha": false,
  "isMultiplayer": false,
  "isCoop": false
}
```

2. Закиньте обложку в `covers/My New Game.jpg`

3. Запустите:
```bash
python scripts/sync_covers.py
```

Либо используйте админ-панель в браузере (Ctrl+Shift+A), задайте PIN и меняйте статусы локально. Экспорт → `mikkleo-overrides.json`.

---

## 🔐 Админ-панель

- Открыть: `Ctrl+Shift+A` или клик по шестерёнке (когда залогинен)
- PIN: 4–6 цифр, хранится только в браузере (hash `djb2`)
- Правки хранятся в `localStorage` (`mikkleo_streamer_overrides_v1`)
- Можно скачать JSON и перенести на другое устройство

---

## 🎨 Темы

7 тем: `cyan`, `pink`, `oled`, `amber`, `emerald`, `lavender`, `arctic`  
Переключение через `theme.js` → `localStorage` + `data-theme` атрибут.

---

## 📦 Деплой

Сайт — статика, деплоится через GitHub Pages из ветки `main` / `gh-pages`:
- `index.html` — entry
- `assets/`, `data/`, `covers/` — раздаются как статика
- `.nojekyll` оставлен чтобы GitHub не игнорировал папки с `_`

---

## 📝 Лицензия

Контент и обложки — собственность их правообладателей.  
Код — MIT (если не указано иное).

---

## 👤 Автор

MikkleoVT — стример & контент-мейкер  
- Twitch: https://twitch.tv/mikkleovt
- Telegram: https://telegram.me/mikkleo
- YouTube: https://www.youtube.com/@mikkleostream

Рефакторинг 2026 — модульная архитектура, оптимизация производительности, исправление багов.
