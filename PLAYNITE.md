# Пополнение каталога через Playnite

Да, можно! Playnite — идеальный источник для Mikkleo Games, потому что уже хранит названия, жанры, год, платформу и обложки.

Мы сделали **два режима**:

1. **С доступом к репе** — `scripts/import_playnite.py` мерджит в `data/games.json` + копирует обложки в `covers/`
2. **Без доступа к репе** — `scripts/upload_playnite_remote.py` заливает конвертированный JSON в удалённое хранилище (рекомендуется Pantry — getpantry.cloud), сайт сам подтянет новые игры (см. `STREAMER_NO_REPO.md` раздел про `gamesUrl`). Заливка по умолчанию **аддитивная** — старые игры в хранилище не пропадут даже при неполном экспорте (полная замена — флаг `--replace`)

## Вариант А — Game Data Exporter (рекомендуется, авто-экспорт)

1. Скачай плагин: https://github.com/NicodeSS/playnite-game-data-exporter/releases
   - Файл `.pext` кинь прямо в окно Playnite
   - Перезапусти Playnite

2. Плагин начнёт автоматически создавать файл:
   ```
   %APPDATA%\Playnite\ExtensionsData\66b8eca4-3f39-4b79-a359-3cb98d5b18fd\library.json
   ```
   Найти папку: в Playnite `About Playnite > Go to... > User data folder` -> `ExtensionsData\66b8e...`

3. Импорт:
   ```bash
   python scripts/import_playnite.py --input "%APPDATA%\Playnite\ExtensionsData\66b8eca4-3f39-4b79-a359-3cb98d5b18fd\library.json" --library-dir "%APPDATA%\Playnite\library"
   ```

## Вариант B — JsonLibraryImportExport (разовый экспорт)

1. В Playnite: `Addons > Browse > Generic > найди "JsonLibraryImportExport"`
2. Установи, перезапусти
3. `Extensions > Json Library Import/Export > Export` — выбери куда сохранить `playnite-export.json`
4. Импорт той же командой:
   ```bash
   python scripts/import_playnite.py --input "C:/path/to/playnite-export.json" --library-dir "%APPDATA%\Playnite\library"
   ```

## Вариант C — Library Exporter Advanced (CSV)

Умеет CSV, но JSON удобнее. Если используешь CSV — конвертируй в JSON через `jq` или попроси добавить поддержку CSV (легко дописать).

## Что делает скрипт

- Читает все игры из Playnite экспорта (`Name`, `Genres`, `Platforms`, `Source`, `ReleaseDate`, `CoverImage`, `Features`)
- Нормализует заголовки (`normalize_title`) и проверяет дубликаты по каталогу `data/games.json`
- Новые игры добавляет с `id = slug(title)` + счётчик, `genre`, `platform`, `year`, `status = null`
- Автоматически проставляет 🕹️ `isMultiplayer` / 🤝 `isCoop` по `Features` из Playnite («Online Multiplayer» → MP, «Online Co-op» → Coop, MMO-жанры → MP) и по курируемому списку `data/mp_coop.json`
- Пытается найти файл обложки в `library/files/...` и копирует в `covers/Имя Игры.jpg` -> прописывает `image: "covers/Имя Игры.jpg"`
- Существующие игры не трогает (чтобы не затереть ручные статусы), но если у них нет обложки — докопирует
- После мержа вызывает `build_index.py` -> пересобирает `assets/js/data.js`

## Примеры

Сухо посмотреть что импортируется:
```bash
python scripts/import_playnite.py --input library.json --library-dir "%APPDATA%/Playnite/library" --dry-run
```

Реальный импорт:
```bash
python scripts/import_playnite.py --input library.json --library-dir "%APPDATA%/Playnite/library"
python scripts/sync_covers.py   # на всякий случай добьёт обложки по имени файла
```

## Частые вопросы

**Нужно ли удалять `covers/` перед импортом?** Нет, скрипт дозаписывает.

**Что если у игры в Playnite нет жанра?** Поставит `Игра`.

**Playnite хранит обложки в `library/files/` с рандомными именами** — да, поэтому мы ищем по `CoverImage` пути + рекурсивный поиск по имени файла в `library/files`.

**Как отметить статус Пройдено/В процессе?** 
- Локально через админку на сайте (Ctrl+Shift+A) — сохранится в localStorage
- Или прямо в `data/games.json` поле `status`: `completed`, `in_progress`, `planned`, `null`

**Можно ли автоматом синкать при каждом запуске Playnite?**
Да, Game Data Exporter авто-обновляет `library.json` при любом изменении библиотеки. Можно добавить в автозапуск `.bat`:
```bat
@echo off
python C:\path\to\MikkleoGame\scripts\import_playnite.py --input "%APPDATA%\Playnite\ExtensionsData\66b8eca4-3f39-4b79-a359-3cb98d5b18fd\library.json" --library-dir "%APPDATA%\Playnite\library"
```

**Подходит ли для 1000+ игр?** Да, тестировалось на 830 играх. Скрипт O(n), копирование обложек — самая долгая часть.

## Дальше

После импорта не забудь закоммитить:
```bash
git add data/games.json covers/ assets/js/data.js
git commit -m "feat: import from Playnite (N new games)"
git push
```

GitHub Pages подхватит изменения после пуша в `main`.
