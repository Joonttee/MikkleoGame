#!/usr/bin/env python3
"""
Mikkleo Games — Playnite importer (2026)

Как пополнять игры с помощью Playnite?

1. Установи плагин для экспорта в Playnite:
   - Вариант A (рекомендуется, авто-обновление): Game Data Exporter
     https://github.com/NicodeSS/playnite-game-data-exporter
     -> создает файл library.json в %APPDATA%\Playnite\ExtensionsData\66b8eca4-3f39-4b79-a359-3cb98d5b18fd\library.json
   - Вариант B: JsonLibraryImportExport
     https://github.com/sokolinthesky/JsonLibraryImportExport
     -> Extensions > Json Library Import/Export > Export
   - Вариант C: Library Exporter Advanced (CSV) — https://github.com/darklinkpower/PlayniteExtensionsCollection

2. Экспортируй библиотеку в JSON.

3. Запусти:
   python scripts/import_playnite.py --input "C:/Users/.../library.json" --library-dir "%APPDATA%/Playnite/library"

Скрипт:
- читает data/games.json (текущий каталог)
- мерджит игры из Playnite (по нормализованному названию)
- копирует обложки из library/files/... в covers/
- сохраняет обновлённый data/games.json и пересобирает assets/js/data.js

Поддерживаются поля Playnite: Name, Genres[], Platforms[], Source, ReleaseDate, CoverImage, BackgroundImage
"""

import argparse
import json
import pathlib
import re
import shutil
from collections import Counter
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_JSON = ROOT / "data" / "games.json"
FLAGS_JSON = ROOT / "data" / "mp_coop.json"
COVERS_DIR = ROOT / "covers"

# Курируемый набор флагов MP/Coop (см. data/mp_coop.json) — подхватывается для новых игр
def load_curated_flags() -> dict:
    """norm_title -> (isMultiplayer, isCoop) из data/mp_coop.json."""
    if not FLAGS_JSON.exists():
        return {}
    data = json.loads(FLAGS_JSON.read_text(encoding="utf-8"))
    out = {}
    for key, mp, coop in (("mp", True, False), ("coop", False, True), ("both", True, True)):
        for title in data.get(key, []):
            norm = normalize_title(title)
            if norm:
                pm, pc = out.get(norm, (False, False))
                out[norm] = (pm or mp, pc or coop)
    return out

def detect_flags(pg: dict, curated: dict) -> tuple:
    """Авто-детект isMultiplayer/isCoop для новой игры:
    1) курируемый список по нормализованному названию;
    2) Playnite Features («Multiplayer», «Online Co-op», «PvP», «Massively Multiplayer»...);
    3) жанр «Многопользовательские игры» / «Massively Multiplayer».
    Семантика: MP — PvP/соревновательный/ММО, Coop — совместное прохождение против ИИ.
    """
    norm = normalize_title(pg.get("Name") or pg.get("name") or pg.get("Title") or "")
    mp, coop = curated.get(norm, (False, False))

    feats = pg.get("Features") or pg.get("features") or []
    if isinstance(feats, dict):
        feats = [feats]
    names = []
    for f in feats:
        if isinstance(f, dict):
            n = f.get("Name") or f.get("name") or ""
        else:
            n = str(f or "")
        if n:
            names.append(n.lower())
    blob = " ".join(names)
    genres_blob = " ".join(
        (g.get("Name") or g.get("name") or "") if isinstance(g, dict) else str(g or "")
        for g in (pg.get("Genres") or pg.get("genres") or [])
    ).lower()

    has_coop = "co-op" in blob or "coop" in blob
    has_mp = (
        "pvp" in blob or "versus" in blob or "multiplayer" in blob
        or "mmo" in blob or "massively" in blob
        or "shared/split" in blob or "split screen" in blob
        or "многопользовательск" in genres_blob or "massively" in genres_blob
    )
    # «Online Co-op» не содержит слова multiplayer, поэтому чистый кооп не помечается MP
    if has_coop:
        coop = True
    if has_mp:
        mp = True
    return mp, coop

def slugify(s: str) -> str:
    s = s.strip().lower()
    # translit basic cyrillic? keep as is but replace non-alnum
    s = re.sub(r'[^0-9a-zA-Zа-яА-ЯёЁ]+', '-', s)
    s = re.sub(r'-{2,}', '-', s).strip('-')
    return s[:64] or "game"

def normalize_title(s: str) -> str:
    if not s:
        return ""
    return re.sub(r'[^0-9a-zA-Zа-яА-ЯёЁ]', '', s).lower()

def extract_year(game: dict):
    # Try ReleaseDate, ReleaseDate.ReleaseDate, etc.
    candidates = [
        game.get("ReleaseDate"),
        game.get("releaseDate"),
        (game.get("ReleaseDate") or {}).get("ReleaseDate") if isinstance(game.get("ReleaseDate"), dict) else None,
    ]
    for c in candidates:
        if not c:
            continue
        # c can be string "2020-12-01T00:00:00", or dict
        if isinstance(c, dict):
            c = c.get("ReleaseDate") or c.get("Date") or ""
        s = str(c)
        m = re.search(r'(19|20)\d{2}', s)
        if m:
            try:
                y = int(m.group(0))
                if 1970 <= y <= 2030:
                    return y
            except:
                pass
    # Try other field
    for k in ("ReleaseYear", "Year", "year"):
        v = game.get(k)
        if isinstance(v, int) and 1970 <= v <= 2030:
            return v
        if isinstance(v, str) and re.match(r'^\d{4}$', v):
            try:
                y = int(v)
                if 1970 <= y <= 2030:
                    return y
            except:
                pass
    return 0

def extract_genres(game: dict):
    # Genres can be list of objects or strings
    raw = game.get("Genres") or game.get("Genres") or game.get("genres") or []
    if isinstance(raw, dict):
        raw = [raw]
    genres = []
    for g in raw:
        if isinstance(g, dict):
            name = g.get("Name") or g.get("name") or ""
            if name:
                genres.append(name)
        elif isinstance(g, str):
            genres.append(g)
    # Fallback: Categories or Tags
    if not genres:
        for key in ("Categories", "Tags", "Features"):
            raw2 = game.get(key) or []
            for t in raw2:
                if isinstance(t, dict):
                    n = t.get("Name") or t.get("name")
                    if n:
                        genres.append(n)
                elif isinstance(t, str):
                    genres.append(t)
            if genres:
                break
    if not genres:
        return "Игра"
    # Join first 2-3
    return ", ".join(genres[:4])

def extract_platform(game: dict):
    # Source
    src = game.get("Source")
    if isinstance(src, dict):
        name = src.get("Name") or src.get("name")
        if name:
            return name
    # Platforms
    plats = game.get("Platforms") or game.get("platforms") or []
    if plats:
        first = plats[0]
        if isinstance(first, dict):
            n = first.get("Name") or first.get("name")
            if n:
                # Map common to our categories
                low = n.lower()
                if "switch" in low:
                    return "Switch"
                if "ubisoft" in low:
                    return "Ubisoft"
                return n
        elif isinstance(first, str):
            return first
    return "Steam/Epic"

def extract_cover_path(game: dict) -> str:
    # CoverImage can be path
    for k in ("CoverImage", "coverImage", "Cover", "Image", "BackgroundImage"):
        v = game.get(k)
        if not v:
            continue
        if isinstance(v, dict):
            # maybe object with path
            v = v.get("Path") or v.get("path") or ""
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""

def resolve_playnite_file(cover_path: str, library_dir: pathlib.Path):
    if not cover_path:
        return None
    p = pathlib.Path(cover_path)
    # If absolute and exists
    if p.is_absolute() and p.exists():
        return p
    # If relative to library dir
    if library_dir:
        # Playnite stores files under library/files/
        candidates = [
            library_dir / cover_path,
            library_dir / "files" / cover_path,
            library_dir / pathlib.Path(cover_path).name,  # maybe just filename
        ]
        for c in candidates:
            if c.exists():
                return c
        # Try recursive search for filename in library/files
        target_name = pathlib.Path(cover_path).name
        if target_name:
            # search in library/files/**/
            try:
                for found in (library_dir / "files").rglob(target_name):
                    if found.is_file():
                        return found
            except Exception:
                pass
    return None

def main():
    parser = argparse.ArgumentParser(description="Import games from Playnite export into Mikkleo Games")
    parser.add_argument("--input", required=True, help="Path to Playnite library.json")
    parser.add_argument("--library-dir", default="", help="Path to Playnite library folder (%%APPDATA%%/Playnite/library) for resolving cover files")
    parser.add_argument("--copy-covers", action="store_true", default=True, help="Copy cover images to covers/")
    parser.add_argument("--no-copy-covers", dest="copy_covers", action="store_false")
    parser.add_argument("--dry-run", action="store_true", help="Only show what would be imported")
    args = parser.parse_args()

    input_path = pathlib.Path(args.input)
    if not input_path.exists():
        print(f"[!] Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    library_dir = pathlib.Path(args.library_dir) if args.library_dir else None
    if library_dir and not library_dir.exists():
        print(f"[!] Library dir not found: {library_dir}, will not resolve covers", file=sys.stderr)
        library_dir = None

    try:
        raw = input_path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except Exception as e:
        print(f"[!] Failed to parse JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # Data can be list or dict with Games key
    if isinstance(data, dict):
        # GameDataExporter wraps? maybe list directly
        if "Games" in data:
            games_list = data["Games"]
        elif "games" in data:
            games_list = data["games"]
        else:
            # maybe single dict is one game? convert to list of values
            games_list = list(data.values()) if all(isinstance(v, dict) for v in data.values()) else [data]
    elif isinstance(data, list):
        games_list = data
    else:
        print("[!] Unexpected JSON structure", file=sys.stderr)
        sys.exit(1)

    print(f"[i] Found {len(games_list)} games in Playnite export")

    # Load existing
    if not DATA_JSON.exists():
        print(f"[!] {DATA_JSON} not found, creating new")
        existing = []
    else:
        existing = json.loads(DATA_JSON.read_text(encoding="utf-8"))

    existing_by_norm = {normalize_title(g.get("title","")): g for g in existing}
    existing_ids = set(g.get("id") for g in existing)

    new_count = 0
    updated_covers = 0
    to_add = []
    curated_flags = load_curated_flags()

    COVERS_DIR.mkdir(parents=True, exist_ok=True)

    for pg in games_list:
        if not isinstance(pg, dict):
            continue
        name = pg.get("Name") or pg.get("name") or pg.get("Title") or ""
        if not name or len(name.strip()) < 2:
            continue

        norm = normalize_title(name)
        if not norm:
            continue

        # Skip if already exists (by normalized title)
        if norm in existing_by_norm:
            # Optionally update year/genre/platform if missing?
            # We skip to preserve manual edits, but can update cover if missing
            existing_game = existing_by_norm[norm]
            if not existing_game.get("image"):
                cover_path = extract_cover_path(pg)
                resolved = resolve_playnite_file(cover_path, library_dir) if library_dir else None
                if resolved:
                    dest_name = f"{name}.jpg"
                    # sanitize filename for Windows
                    dest_name = re.sub(r'[<>:"/\\|?*]', '_', dest_name)
                    dest = COVERS_DIR / dest_name
                    if not args.dry_run:
                        try:
                            shutil.copy2(resolved, dest)
                            existing_game["image"] = f"covers/{dest_name}"
                            updated_covers += 1
                            print(f"[~] Updated cover for existing '{name}' -> {dest}")
                        except Exception as e:
                            print(f"[!] Failed to copy cover for {name}: {e}")
            continue

        year = extract_year(pg)
        genre = extract_genres(pg)
        platform = extract_platform(pg)

        # Generate unique id
        base_slug = slugify(name)
        gid = base_slug
        counter = 1
        while gid in existing_ids:
            counter += 1
            gid = f"{base_slug}-{counter}"

        mp_flag, coop_flag = detect_flags(pg, curated_flags)

        new_game = {
            "id": gid,
            "title": name.strip(),
            "genre": genre,
            "platform": platform,
            "year": year,
            "rating": 0,
            "image": "",
            "desc": "",
            "createdAt": "",
            "altTitle": "",
            "status": None,
            "isGacha": False,
            "isMultiplayer": mp_flag,
            "isCoop": coop_flag,
            "_playniteId": pg.get("Id") or pg.get("id") or ""
        }

        cover_path = extract_cover_path(pg)
        resolved = resolve_playnite_file(cover_path, library_dir) if library_dir else None
        if resolved and args.copy_covers:
            dest_name = f"{name}.jpg"
            dest_name = re.sub(r'[<>:"/\\|?*]', '_', dest_name)
            dest = COVERS_DIR / dest_name
            if not args.dry_run:
                try:
                    shutil.copy2(resolved, dest)
                    new_game["image"] = f"covers/{dest_name}"
                    updated_covers += 1
                except Exception as e:
                    print(f"[!] Copy failed for {name}: {e}")
        elif cover_path:
            # If we cannot resolve file, keep path as is maybe? But better leave empty
            # Try to use existing filename pattern
            pass

        to_add.append(new_game)
        existing_ids.add(gid)
        new_count += 1
        flags_str = (" 🕹️MP" if mp_flag else "") + (" 🤝Coop" if coop_flag else "")
        print(f"[+] New: {name} | {genre} | {year} | {platform}{flags_str}")

    print(f"\n[i] Summary: {new_count} new games, {updated_covers} covers copied/updated")

    if args.dry_run:
        print("[i] Dry run — not writing")
        return

    # Merge
    merged = existing + to_add
    # Sort by title
    merged.sort(key=lambda x: x["title"].lower())

    # Write
    DATA_JSON.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[✓] Wrote {DATA_JSON} ({len(merged)} total)")

    # Regenerate data.js
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("build_index", str(ROOT / "scripts" / "build_index.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.build()
    except Exception as e:
        print(f"[!] Failed to rebuild data.js: {e}")

    print("[✓] Done. Запусти python scripts/sync_covers.py если нужно доп. синхронизировать обложки.")

if __name__ == "__main__":
    main()
