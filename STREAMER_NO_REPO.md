# Как подключить связку для стримера без доступа к репозиторию сайта

Сайт поддерживает **удалённые оверрайды** — статусы игр (`Пройдено`, `В процессе` и т.д.) и новые игры могут храниться не в `data/games.json` в репе, а в публичном JSON-хранилище, которое стример может обновлять сам, без пуша в GitHub.

> ⚠️ **Важно (июль 2026):** npoint.io закрыл запись через API для бинов, привязанных к аккаунту — POST отвечает **401** (нужен платный токен + premium). Поэтому рекомендуемая схема переехала на **Pantry** (getpantry.cloud) — там запись из браузера работает бесплатно и без ключей.

---

## Схема 1 — Рекомендуемая: Pantry (авто-заливка из админки, без репы)

Pantry позволяет создавать и перезаписывать JSON-корзины одним POST-запросом прямо из браузера.

1. **Создай pantry:**
   - Зайди на https://getpantry.cloud
   - Введи email → получишь **PANTRY_ID** (вида `a35e4a4e-22cb-...`)
   - Больше ничего создавать не надо — корзины появятся при первой заливке.

2. **Владелец сайта прописывает URL в `data/remote.json`** (один раз):
   ```json
   {
     "overridesUrl": "https://getpantry.cloud/apiv1/pantry/PANTRY_ID/basket/mikkleo-statuses",
     "gamesUrl": "https://getpantry.cloud/apiv1/pantry/PANTRY_ID/basket/mikkleo-games"
   }
   ```
   И пушит в `main`. Больше пушить не нужно.

3. **Стример работает (статусы):**
   - Открывает сайт → `Ctrl+Shift+A` → вводит PIN
   - Меняет статусы игр
   - Жмёт **⬆️ Статусы** — сайт делает `POST` на pantry и **полностью заменяет** корзину текущими статусами
   - Готово — все зрители видят статусы после перезагрузки (Ctrl+F5).

   > URL подхватывается из `data/remote.json` автоматически — вручную ничего вставлять не надо. Если хочешь другой URL (свой тестовый pantry) — вставь в поле «Статусы» в админке и нажми «💾 URL».

4. **Стример заливает новые игры из Playnite** — см. раздел ниже.

**Плюс:** всё в один клик из админки, ключей/токенов нет.
**Минус:** pantry публичная — любой, кто знает PANTRY_ID, может перезаписать корзину (не сообщай ID зрителям; ID лежит в открытом `data/remote.json`, поэтому считай данные публично-записываемыми — для статусов и списка игр это приемлемо).

> ℹ️ **Срок жизни корзины:** Pantry удаляет корзины после ~3 суток без обращений, но каждый GET/POST продлевает срок. Сайт при каждой загрузке читает обе корзины — при активных зрителях они живут вечно. Если корзина вдруг удалась — просто залей заново из админки.

---

## Схема 2 — Gist (без кода, 2 минуты, но вручную)

Подходит если стример вообще не хочет ничего настраивать, но готов копировать JSON руками.

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
   - Кнопка `💾 Скачать JSON` -> скачивает `mikkleo-overrides.json`
   - Идёт в свой gist -> `Edit` -> вставляет содержимое скачанного файла -> `Update gist`
   - После Ctrl+F5 все зрители видят новые статусы — сайт тянет gist.

**Плюс:** ничего настраивать не надо.
**Минус:** ручное копирование gist (автоматизируй через Pantry — Схема 1).

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

Статусы — это `overridesUrl`, а новые игры — `gamesUrl`. Сайт умеет тянуть **оба**.

**В `data/remote.json` два поля:**
```json
{
  "overridesUrl": "https://getpantry.cloud/apiv1/pantry/PANTRY_ID/basket/mikkleo-statuses",
  "gamesUrl": "https://getpantry.cloud/apiv1/pantry/PANTRY_ID/basket/mikkleo-games"
}
```

**Флоу для стримера без репы (только Playnite):**

1. Владелец один раз настраивает pantry и пушит `data/remote.json` (см. Схему 1).

2. Стример на своём ПК (без клонирования репы, достаточно скачать один .py файл):
   ```bash
   python upload_playnite_remote.py --input "%APPDATA%\Playnite\ExtensionsData\66b8eca4-3f39-4b79-a359-3cb98d5b18fd\library.json" --remote-url https://getpantry.cloud/apiv1/pantry/PANTRY_ID/basket/mikkleo-games
   ```
   Скрипт `scripts/upload_playnite_remote.py`:
   - конвертит Playnite экспорт в формат Mikkleo (Name, Genres, Year...)
   - делает `POST` на pantry (массив игр оборачивается в `{"games": [...]}` — сайт сам развернёт при чтении)

   Либо без скрипта, прямо в браузере: открой `uploader.html` на сайте и перетащи `library.json`.

3. Сайт при загрузке:
   - `loadGames()` → `data/games.json` (основной каталог)
   - `loadRemoteOverrides()` → тянет `gamesUrl` → парсит как Playnite, Mikkleo массив или `{games:[...]}` → мерджит с основным, дедуплицирует по названию
   - Новые игры появляются у всех зрителей без пуша в репу!

4. Обложки: без доступа к репе обложки из `library/files/` не скопировать в `covers/` (они локальные). Поэтому в remote-режиме для новых игр показываются инициалы. Если стример хочет кастомные обложки — кидает ссылку на https:// в поле `image`, или владелец потом прогоняет `sync_covers.py` / `import_playnite.py` с доступом к library.

**Админка для игр:**
- В админке поле `Игры Playnite` показывает URL из `data/remote.json` — менять не надо, если владелец всё настроил
- После смены URL перезагрузи страницу — новые игры подтянутся.

Скрипты:
- `scripts/import_playnite.py` — для владельца с доступом к репе (копирует обложки в `covers/`)
- `scripts/upload_playnite_remote.py` — для стримера без доступа к репе (заливает JSON на pantry)

---

## Устаревшая схема — npoint.io (только анонимные бины)

Раньше использовался npoint.io, но:

- **Бины, привязанные к аккаунту npoint** (наш случай): запись через API закрыта — POST отвечает **401** (нужен платный токен + premium подписка). GET работает как раньше.
- **Анонимные бины** (созданные без логина): POST пока работает, но npoint называет API-запись «private beta» и может закрыть её в любой момент.
- `PUT`/`PATCH` на npoint вообще не поддерживаются (404).

Если очень хочется остаться на npoint — можно пересоздать бины **без логина** и обновить `data/remote.json`. Но надёжный путь — Pantry (Схема 1).

---

## Что сделано в коде для поддержки

- `assets/js/storage.js`: `loadRemoteOverrides()` грузит и `overridesUrl` и `gamesUrl`, кэширует `_remoteGames`; `getRemoteOverridesUrl()` отдаёт публичный URL статусов для админки
- `assets/js/remote.js`: `uploadJsonToRemote()` — заливка с правильной семантикой под провайдера (Pantry = POST create/replace; массивы оборачиваются в `{games:[...]}`), `explainUploadFailure()` — понятные тексты ошибок
- `assets/js/playnite.js`: `convertPlayniteToMikkleo()` + `parsePlayniteJson()` — конвертация Playnite → Mikkleo в браузере (понимает и обёртку `{games: [...]}`)
- `getEffectiveStatus()` / `getEffectiveFlag()`: **localStorage -> remote -> default**
- `app.js`: `Promise.all([loadGames(), loadRemoteOverrides()])` + мердж `getRemoteGamesRaw()` перед первым рендером
- `data/remote.json`: два поля `overridesUrl` и `gamesUrl`, можно поменять на любой pantry/gist без пересборки JS
- `data/overrides.json`: fallback для статусов
- Админка: 2 поля URL (статусы + игры, подхватываются из `data/remote.json`) + кнопка заливки статусов

---

## Рекомендуемый флоу для Mikkleo

1. Владелец один раз создаёт pantry и пушит `data/remote.json` с двум URL.
2. Стример:
   - Ставит Playnite + Game Data Exporter
   - Раз в неделю заливает игры через `upload_playnite_remote.py` или `uploader.html`
   - На сайте меняет статусы игр -> `⬆️ Статусы`
3. Зрители всегда видят актуальные статусы и новые игры, даже если стример никогда не трогал GitHub.

Если нужно — могу добавить GitHub Action + Discord бот шаблон.
