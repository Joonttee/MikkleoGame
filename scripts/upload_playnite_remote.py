#!/usr/bin/env python3
"""
Mikkleo Games — загрузка игр из Playnite без доступа к репе (remote mode)

Сценарий для стримера у которого НЕТ доступа к репозиторию сайта:

1. Владелец один раз создаёт 2 хранилища на npoint.io (или gist):
   - для оверрайдов (статусы): https://api.npoint.io/<ID1>
   - для игр (library): https://api.npoint.io/<ID2>
   И прописывает их в data/remote.json:
   {
     "overridesUrl": "https://api.npoint.io/<ID1>",
     "gamesUrl": "https://api.npoint.io/<ID2>"
   }

2. Стример ставит Playnite + Game Data Exporter (см. PLAYNITE.md)
   -> получается library.json

3. Стример запускает ЭТОТ скрипт на своём ПК (без клонирования репы, достаточно скачать 2 файла):
   python upload_playnite_remote.py --input "%APPDATA%\Playnite\ExtensionsData\...\library.json" --remote-url https://api.npoint.io/<ID2>

   Скрипт:
   - конвертит Playnite library в формат Mikkleo (как import_playnite.py)
   - делает POST на указанный remote URL
   - теперь сайт автоматически подтянет новые игры (fetch gamesUrl) и покажет всем зрителям

4. Для статусов (Пройдено и т.д.) стример использует админку сайта:
   Ctrl+Shift+A -> меняет статусы -> в админке вставляет overridesUrl (ID1) -> Залить туда JSON

Всё — без единого git push, без доступа к репе.

Также поддерживает Gist:
- Создай gist с файлом games.json, возьми raw URL
- Используй --remote-url https://gist.github.com/... но для gist нужен другой способ заливки (через API gist.github.com, нужен токен)
- Для простоты используй npoint.io
"""

import argparse
import json
import pathlib
import re
import sys
import urllib.request
import urllib.error

def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r'[^0-9a-zA-Zа-яА-ЯёЁ]+', '-', s)
    s = re.sub(r'-{2,}', '-', s).strip('-')
    return s[:64] or "game"

def normalize_title(s: str) -> str:
    return re.sub(r'[^0-9a-zA-Zа-яА-ЯёЁ]', '', s or '').lower()

def extract_year(game: dict):
    for k in ("ReleaseDate", "releaseDate"):
        v = game.get(k)
        if not v:
            continue
        if isinstance(v, dict):
            v = v.get("ReleaseDate") or v.get("Date") or ""
        s = str(v)
        m = re.search(r'(19|20)\d{2}', s)
        if m:
            try:
                y = int(m.group(0))
                if 1970 <= y <= 2030:
                    return y
            except:
                pass
    for k in ("ReleaseYear", "Year", "year"):
        v = game.get(k)
        if isinstance(v, int) and 1970 <= v <= 2030:
            return v
    return 0

def extract_genres(game: dict):
    raw = game.get("Genres") or game.get("genres") or []
    out = []
    for g in raw if isinstance(raw, list) else [raw]:
        if isinstance(g, dict):
            n = g.get("Name") or g.get("name")
            if n:
                out.append(n)
        elif isinstance(g, str):
            out.append(g)
    if not out:
        for key in ("Categories", "Tags"):
            raw2 = game.get(key) or []
            for t in raw2:
                if isinstance(t, dict):
                    n = t.get("Name") or t.get("name")
                    if n:
                        out.append(n)
                elif isinstance(t, str):
                    out.append(t)
            if out:
                break
    return ", ".join(out[:4]) if out else "Игра"

def extract_platform(game: dict):
    src = game.get("Source")
    if isinstance(src, dict):
        n = src.get("Name") or src.get("name")
        if n:
            return n
    plats = game.get("Platforms") or []
    if plats:
        first = plats[0]
        if isinstance(first, dict):
            n = first.get("Name") or first.get("name")
            if n:
                return n
        elif isinstance(first, str):
            return first
    return "Steam/Epic"

def convert_playnite(playnite_games):
    out = []
    used = set()
    for pg in playnite_games:
        if not isinstance(pg, dict):
            continue
        name = pg.get("Name") or pg.get("name") or ""
        if not name or len(name.strip()) < 2:
            continue
        gid = slugify(name)
        base = gid
        c = 1
        while gid in used:
            c += 1
            gid = f"{base}-{c}"
        used.add(gid)
        out.append({
            "id": gid,
            "title": name.strip(),
            "genre": extract_genres(pg),
            "platform": extract_platform(pg),
            "year": extract_year(pg),
            "rating": 0,
            "image": "",  # обложки отдельно, без доступа к репе — через initials
            "desc": "",
            "createdAt": "",
            "altTitle": "",
            "status": None,
            "isGacha": False,
            "isMultiplayer": False,
            "isCoop": False,
        })
    return out

def main():
    parser = argparse.ArgumentParser(description="Загрузка игр из Playnite в удалённое хранилище без доступа к репе")
    parser.add_argument("--input", required=True, help="Путь к library.json из Playnite")
    parser.add_argument("--remote-url", required=True, help="URL удалённого хранилища (npoint.io, jsonbin, и т.д.) куда POSTить")
    parser.add_argument("--dry-run", action="store_true", help="Только показать, не заливать")
    args = parser.parse_args()

    p = pathlib.Path(args.input)
    if not p.exists():
        print(f"[!] Файл не найден: {p}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(p.read_text(encoding="utf-8"))
    # Normalize to list
    if isinstance(data, dict):
        if "Games" in data:
            arr = data["Games"]
        elif "games" in data:
            arr = data["games"]
        else:
            vals = list(data.values())
            arr = vals if vals and isinstance(vals[0], dict) and (vals[0].get("Name") or vals[0].get("name")) else []
    else:
        arr = data

    print(f"[i] Найдено {len(arr)} игр в Playnite")

    converted = convert_playnite(arr)
    print(f"[i] Сконвертировано {len(converted)} для Mikkleo")

    if args.dry_run:
        print(json.dumps(converted[:3], ensure_ascii=False, indent=2))
        print("[i] Dry run — не заливаю")
        return

    payload = json.dumps(converted, ensure_ascii=False, indent=2).encode("utf-8")
    print(f"[i] Заливаю на {args.remote_url} ({len(payload)} байт)...")

    # Try POST (npoint) and PUT
    for method in ("POST", "PUT", "PATCH"):
        try:
            req = urllib.request.Request(args.remote_url, data=payload, method=method, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = resp.read().decode("utf-8", errors="ignore")[:500]
                print(f"[✓] {method} OK {resp.status}: {body[:200]}")
                print(f"[✓] Готово! Сайт подтянет игры с {args.remote_url}")
                print(f"[i] Убедись что в data/remote.json прописано:\n{{\n  \"gamesUrl\": \"{args.remote_url}\"\n}}")
                return
        except urllib.error.HTTPError as e:
            print(f"[!] {method} failed {e.code}: {e.read().decode()[:300]}")
        except Exception as e:
            print(f"[!] {method} error: {e}")

    print("[!] Не удалось залить. Если используешь gist — нужен GitHub API с токеном. Для npoint попробуй создать новый ID.")

if __name__ == "__main__":
    main()
