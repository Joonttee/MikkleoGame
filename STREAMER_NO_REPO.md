# Как подключить связку для стримера без доступа к репозиторию сайта

Сайт теперь поддерживает **удалённые оверрайды** — статусы игр (`Пройдено`, `В процессе` и т.д.) могут храниться не в `data/games.json` в репе, а в любом публичном JSON, который стример может редактировать сам, без пуша в GitHub.

---

## Схема 1 — Самый простой: Gist (без кода, 2 минуты)

Подходит если стример вообще не хочет ставить ничего, только браузер.

1. **Стример создаёт секретный Gist:**
   - Зайди на https://gist.github.com
   - Файл: `overrides.json`
   - Содержимое: `{}` (пустой объект для начала)
   - Create secret gist

2. **Получи Raw URL:**
   - Открой gist -> кнопка `Raw` -> скопируй URL
   - Пример: `https://gist.githubusercontent.com/USERNAME/abc123.../raw/overrides.json`

3. **Владелец сайта прописывает URL в `data/remote.json`:**
   ```json
   {
     "overridesUrl": "https://gist.githubusercontent.com/USERNAME/abc123.../raw/overrides.json"
   }
   ```
   И пушит один раз в `main`. Больше пушить не нужно.

4. **Стример работает:**
   - Открывает сайт `https://Joonttee.github.io/MikkleoGame/`
   - `Ctrl+Shift+A` -> вводит PIN (придумывает)
   - Меняет статусы игр
   - В админке в поле **Удалённый URL** вставляет тот же Raw gist URL -> `💾 Сохранить URL`
   - Кнопка `💾 Скачать JSON` -> скачивает `mikkleo-overrides.json`
   - Идёт в свой gist -> `Edit` -> вставляет содержимое скачанного файла -> `Update gist`
   - Через 5 минут (или сразу после Ctrl+F5) все зрители видят новые статусы — сайт тянет gist.

**Плюс:** стримеру не нужен GitHub доступ к репе сайта.
**Минус:** ручное копирование gist (можно автоматизировать через npoint).

---

## Схема 2 — Npoint.io (авто-заливка из админки, тоже без репы)

Npoint позволяет обновлять JSON одним POST-запросом прямо из браузера.

1. **Создай storage:**
   - Зайди на https://www.npoint.io
   - Вставь `{}` и нажми Save -> получишь ID, например `8d4c5e9a...`
   - URL будет `https://api.npoint.io/8d4c5e9a...`

2. **Пропиши URL в `data/remote.json` в репе** (один раз владельцем):
   ```json
   { "overridesUrl": "https://api.npoint.io/8d4c5e9a..." }
   ```

3. **Стример:**
   - На сайте в админке вставляет тот же URL в поле удалённого хранилища -> Сохранить
   - Меняет статусы
   - Жмёт **⬆️ Залить туда JSON** — скрипт делает `POST https://api.npoint.io/ID` с текущими оверрайдами
   - Готово, все видят.

**Плюс:** не нужно руками править gist, всё в один клик из админки.
**Минус:** npoint публичный, любой кто знает ID может перезаписать (поэтому используй сложный ID).

---

## Схема 3 — Playnite + Бот без доступа к репе

Если стример хочет пополнять **новые игры** из Playnite, но у него нет доступа к репе:

1. Стример ставит плагин **Game Data Exporter** в Playnite (см. `PLAYNITE.md`)
   - Файл `library.json` появляется в `%APPDATA%\Playnite\ExtensionsData\...`

2. Стример кидает `library.json` в:
   - Discord канал с вебхуком
   - Telegram боту
   - Или в общую папку Google Drive / Яндекс Диск

3. **Владелец сайта** ставит GitHub Action (уже в репе можно добавить):

```yaml
# .github/workflows/playnite-bot.yml
name: Playnite Auto Import
on:
  repository_dispatch:
    types: [playnite_library]
  workflow_dispatch:

jobs:
  import:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - name: Download library.json from gist/npoint/discord
        run: |
          curl -L "${{ secrets.PLAYNITE_JSON_URL }}" -o /tmp/library.json
      - name: Import
        run: |
          python scripts/import_playnite.py --input /tmp/library.json
      - name: Commit
        run: |
          git config user.name "playnite-bot"
          git config user.email "bot@mikkleogame"
          git add data/games.json covers/ assets/js/data.js data/overrides.json
          git commit -m "feat: auto import from Playnite (streamer)" || exit 0
          git push
```

Тогда стримеру достаточно обновить `PLAYNITE_JSON_URL` (gist с library.json) — Action сам заберёт и запушит игры, без прямого доступа к репе.

---

## Схема 4 — Только локально (если не нужно показывать всем)

Если стримеру нужно только для себя помечать статусы, а зрителям показывать дефолт:

- Админка `Ctrl+Shift+A` -> меняй статусы
- Они сохранятся в `localStorage` браузера стримера
- Никуда не улетают, репа не нужна вообще
- Для переноса на другой ПК — `💾 Скачать JSON` / загрузить на другом устройстве через импорт (можно добавить кнопку импорта — попроси, добавим)

---

## Как грузить НОВЫЕ игры из Playnite без доступа к репе

Статусы — это `overridesUrl`, а новые игры — `gamesUrl`. Теперь сайт умеет тянуть **оба**.

**В `data/remote.json` теперь два поля:**
```json
{
  "overridesUrl": "https://api.npoint.io/ID_STATUSES",
  "gamesUrl": "https://api.npoint.io/ID_GAMES"
}
```

**Флоу для стримера без репы (только Playnite):**

1. Владелец один раз создаёт 2 хранилища на npoint.io:
   - `ID_STATUSES` — для статусов (`{}` изначально)
   - `ID_GAMES` — для игр (`[]` изначально)
   И пушит их в `data/remote.json` (один раз).

2. Стример на своём ПК (без клонирования репы, достаточно скачать 2 .py файла):
   ```bash
   python upload_playnite_remote.py --input "%APPDATA%\Playnite\ExtensionsData\66b8eca4-3f39-4b79-a359-3cb98d5b18fd\library.json" --remote-url https://api.npoint.io/ID_GAMES
   ```
   Скрипт `scripts/upload_playnite_remote.py`:
   - конвертит Playnite экспорт в формат Mikkleo (Name, Genres, Year...)
   - делает `POST https://api.npoint.io/ID_GAMES`

3. Сайт при загрузке:
   - `loadGames()` → `data/games.json` (основной каталог)
   - `loadRemoteOverrides()` → тянет `gamesUrl` → парсит как Playnite или Mikkleo массив → `convertPlayniteToMikkleo()` → мерджит с основным, дедуплицирует по названию
   - Новые игры появляются у всех зрителей без пуша в репу!

4. Обложки: без доступа к репе обложки из `library/files/` не скопировать в `covers/` (они локальные). Поэтому в remote-режиме для новых игр показывается инициалы. Если стример хочет кастомные обложки — кидает ссылку на https:// в поле `image`, или владелец потом прогоняет `sync_covers.py` / `import_playnite.py` с доступом к library.

**Админка для игр:**
- В админке теперь второе поле `Игры Playnite` → вставь `https://api.npoint.io/ID_GAMES` → `💾 URL`
- После этого перезагрузи страницу — новые игры из npoint подтянутся.

Скрипты:
- `scripts/import_playnite.py` — для владельца с доступом к репе (копирует обложки в `covers/`)
- `scripts/upload_playnite_remote.py` — для стримера без доступа к репе (заливает JSON на npoint/gist)

---

## Что уже сделано в коде для поддержки

- `assets/js/storage.js`: `loadRemoteOverrides()` теперь грузит и `overridesUrl` и `gamesUrl`, кэширует `_remoteGames`
- `assets/js/playnite.js`: `convertPlayniteToMikkleo()` + `parsePlayniteJson()` — конвертация Playnite → Mikkleo в браузере
- `getEffectiveStatus()` / `getEffectiveFlag()`: **localStorage -> remote -> default**
- `app.js`: `Promise.all([loadGames(), loadRemoteOverrides()])` + мердж `getRemoteGamesRaw()` перед первым рендером
- `data/remote.json`: теперь два поля `overridesUrl` и `gamesUrl`, можно поменять на любой gist/npoint без пересборки JS
- `data/overrides.json`: fallback для статусов
- Админка: 2 поля URL (статусы + игры) + кнопки заливки

---

## Рекомендуемый флоу для Mikkleo

1. Владелец один раз пушит `data/remote.json` с npoint URL, который выдаст стриммеру.
2. Стример:
   - Ставит Playnite + Game Data Exporter
   - Раз в неделю экспортирует или бот делает авто
   - На сайте меняет статусы игр -> `Залить туда JSON` на npoint
3. Зрители всегда видят актуальные статусы с npoint, даже если стример никогда не трогал GitHub.

Если нужно — могу добавить GitHub Action + Discord бот шаблон.
