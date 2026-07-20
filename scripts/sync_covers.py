#!/usr/bin/env python3
"""
Mikkleo Games — sync_covers.py (refactored 2026)

Matches image files in covers/ (and optionally root) to game titles
and updates data/games.json image paths.

Improvements over legacy:
- Uses data/games.json instead of parsing index.html
- Robust normalization (unidecode-like without external dep, lower, alnum only)
- Handles altTitle matching
- Does not rebuild whole index.html
- Calls build_index logic to regenerate data.js

Usage:
  python scripts/sync_covers.py
"""
import glob
import json
import os
import pathlib
import re
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_JSON = ROOT / "data" / "games.json"
COVERS_DIR = ROOT / "covers"
ASSETS_IMG = ROOT / "assets" / "img"

# Files that are not covers
SYSTEM_ASSETS = {
    'hero.jpg', 'hero.png', 'mikkleo-avatar.jpg', 'favicon.png',
    'favicon.ico', 'apple-touch-icon.png', 'icon-192.png', 'icon-512.png',
    'mikkleo-avatar.png', 'hero.webp'
}

def normalize_name(s: str) -> str:
    """Lower, remove extension, keep alnum, cyrillic -> keep, drop spaces/punct."""
    if not s:
        return ""
    s = re.sub(r'\.(jpg|jpeg|png|webp|gif|bmp)$', '', s, flags=re.I)
    # Keep letters+digits (Latin + Cyrillic), drop others
    s = re.sub(r'[^0-9a-zA-Zа-яА-ЯёЁ]', '', s)
    return s.lower()

def normalize_for_fuzzy(s: str) -> str:
    """Even more aggressive: remove numbers, short words? For fallback."""
    return normalize_name(s)

def find_images():
    patterns = [
        str(COVERS_DIR / "*.jpg"),
        str(COVERS_DIR / "*.jpeg"),
        str(COVERS_DIR / "*.png"),
        str(COVERS_DIR / "*.webp"),
        # also check assets/img/covers? in case
        str(ROOT / "*.jpg"),
        str(ROOT / "*.png"),
        str(ROOT / "*.webp"),
    ]
    files = []
    for pat in patterns:
        files.extend(glob.glob(pat))
    # filter system assets
    out = []
    for f in files:
        bn = os.path.basename(f)
        if bn in SYSTEM_ASSETS:
            continue
        if bn.lower().startswith("hero") or bn.lower().startswith("mikkleo-avatar") or bn.lower().startswith("favicon") or bn.lower().startswith("icon-") or bn.lower().startswith("apple-"):
            continue
        out.append(f)
    # deduplicate by basename
    seen = {}
    for f in out:
        bn = os.path.basename(f)
        if bn not in seen:
            seen[bn] = f
    return list(seen.values())

def main():
    if not DATA_JSON.exists():
        print(f"[!] {DATA_JSON} not found, run build_index.py first")
        return

    games = json.loads(DATA_JSON.read_text(encoding="utf-8"))
    print(f"[i] Loaded {len(games)} games from {DATA_JSON}")

    image_files = find_images()
    print(f"[i] Found {len(image_files)} candidate cover files")

    # Build map: normalized basename -> relative path
    norm_to_path = {}
    basename_map = {}
    for img_path in image_files:
        p = pathlib.Path(img_path)
        # Make path relative to ROOT for storage in JSON, with forward slashes
        try:
            rel = p.relative_to(ROOT).as_posix()
        except ValueError:
            rel = p.as_posix()
        # Important: prefer covers/ prefix for consistency
        # If file is in root, keep as is but we have it in assets/img too
        # For covers dir, use covers/filename
        bn = p.name
        norm = normalize_name(bn)
        norm_to_path[norm] = rel
        basename_map[bn.lower()] = rel

    # Also build title normalization map
    matched = 0
    unmatched_games = []
    for g in games:
        title = g.get("title") or ""
        alt = g.get("altTitle") or ""
        # try direct normalized title
        candidates = [
            normalize_name(title),
            normalize_name(alt) if alt else None,
            # also try without "The" prefix? etc
        ]
        candidates = [c for c in candidates if c]

        found = None
        for cand in candidates:
            if cand in norm_to_path:
                found = norm_to_path[cand]
                break

        # fuzzy fallback: try if normalized file contains title or vice versa? but skip heavy fuzzy
        if not found:
            # try to find by substring: if title normalized is substring of file norm
            # This helps for e.g., "Witcher 3" vs "thewitcher3wildhunt"
            for f_norm, f_path in norm_to_path.items():
                for cand in candidates:
                    if cand and (cand in f_norm or f_norm in cand):
                        # avoid too short matches (<4 chars)
                        if len(cand) >= 4:
                            found = f_path
                            break
                if found:
                    break

        if found:
            old = g.get("image") or ""
            if old != found:
                g["image"] = found
                matched += 1
                print(f"[✓] Matched '{title}' -> {found}")
        else:
            unmatched_games.append(title)

    # Write back
    DATA_JSON.write_text(json.dumps(games, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[✓] Updated {DATA_JSON}: {matched} new matches")

    # Regenerate data.js via build_index
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("build_index", str(ROOT / "scripts" / "build_index.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.build()
    except Exception as e:
        print(f"[!] Failed to regenerate data.js: {e}")

    if unmatched_games:
        print(f"[i] {len(unmatched_games)} games without cover (showing 20):")
        for t in unmatched_games[:20]:
            print(f"  - {t}")

    print(f"[✓] Done: {len(games)-len(unmatched_games)}/{len(games)} games have covers, {len(image_files)} files scanned")

if __name__ == "__main__":
    main()
