#!/usr/bin/env python3
"""
Mikkleo Games — build_index.py (refactored 2026)

Responsibilities:
- Validate data/games.json
- Ensure required fields & defaults
- Deduplicate / sort sanity checks
- Regenerate assets/js/data.js (ESM fallback)
- Print report

Old behaviour (rebuilding entire index.html) is deprecated and removed
to avoid template drift. Use scripts/sync_covers.py to update covers.
"""
import json
import pathlib
import sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_JSON = ROOT / "data" / "games.json"
DATA_JS = ROOT / "assets" / "js" / "data.js"

REQUIRED_FIELDS = ["id", "title", "year"]

def normalize_game(g: dict, idx: int) -> dict:
    """Ensure defaults, sanitize types."""
    # id must exist and be string
    if not g.get("id"):
        # generate from title + idx
        base = (g.get("title") or f"game-{idx}").strip().lower()
        base = "".join(c if c.isalnum() else "-" for c in base)
        g["id"] = base[:64] or f"game-{idx}"

    g["title"] = str(g.get("title") or "Без названия").strip()
    g["altTitle"] = str(g.get("altTitle") or "").strip()
    g["genre"] = str(g.get("genre") or "Игра").strip()
    g["platform"] = str(g.get("platform") or "Steam/Epic").strip()

    # year: int or None
    try:
        year = int(g.get("year") or 0)
        g["year"] = year if 1970 <= year <= 2030 else 0
    except Exception:
        g["year"] = 0

    # booleans
    for flag in ("isGacha", "isMultiplayer", "isCoop"):
        g[flag] = bool(g.get(flag, False))

    # status: allow None or one of known, else None (means not started)
    status = g.get("status")
    if status not in (None, "none", "completed", "in_progress", "planned"):
        g["status"] = None
    else:
        # normalize string "none" -> None? Keep as "none" for backward compat,
        # but we store None as default for admin overrides.
        if status == "none":
            g["status"] = None
        else:
            g["status"] = status

    # image: keep if exists, else empty
    img = g.get("image") or ""
    # normalize path separators to forward slash
    g["image"] = str(img).replace("\\", "/").strip()

    # optional steam fields
    if g.get("steamAppId") is not None:
        try:
            g["steamAppId"] = str(g["steamAppId"]).strip()
        except Exception:
            pass

    # ensure id is slug-like unique later
    return g


def build():
    if not DATA_JSON.exists():
        print(f"[!] {DATA_JSON} not found. Creating empty file.", file=sys.stderr)
        DATA_JSON.parent.mkdir(parents=True, exist_ok=True)
        DATA_JSON.write_text("[]", encoding="utf-8")
        return

    raw = DATA_JSON.read_text(encoding="utf-8")
    try:
        games = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"[!] JSON parse error in {DATA_JSON}: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(games, list):
        print("[!] Expected list in games.json", file=sys.stderr)
        sys.exit(1)

    print(f"[i] Loaded {len(games)} games")

    normalized = []
    ids_seen = Counter()
    errors = []

    for idx, g in enumerate(games):
        if not isinstance(g, dict):
            errors.append(f"index {idx} is not an object")
            continue
        ng = normalize_game(dict(g), idx)
        # track duplicate ids
        ids_seen[ng["id"]] += 1
        # missing title check
        if not ng["title"] or ng["title"] == "Без названия":
            errors.append(f"{ng['id']}: missing title")
        normalized.append(ng)

    # report duplicates
    dups = [gid for gid, cnt in ids_seen.items() if cnt > 1]
    if dups:
        print(f"[!] Duplicate ids found: {dups[:10]}", file=sys.stderr)
        # make ids unique by appending counter
        seen = {}
        for g in normalized:
            gid = g["id"]
            if gid in seen:
                seen[gid] += 1
                g["id"] = f"{gid}-{seen[gid]}"
                print(f"  -> renamed duplicate {gid} to {g['id']}")
            else:
                seen[gid] = 0

    # sort by title for deterministic output (apps will re-sort at runtime anyway)
    normalized.sort(key=lambda x: x["title"].lower())

    # write back
    DATA_JSON.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[✓] Wrote {DATA_JSON} ({len(normalized)} games)")

    # generate ESM fallback
    DATA_JS.parent.mkdir(parents=True, exist_ok=True)
    # Keep file size reasonable: dump compact JSON inside ESM, not pretty
    js_payload = json.dumps(normalized, ensure_ascii=False)
    DATA_JS.write_text(f"// Auto-generated from data/games.json — do not edit manually\nexport const GAMES = {js_payload};\n", encoding="utf-8")
    print(f"[✓] Wrote {DATA_JS}")

    # summary
    platforms = Counter(g["platform"] for g in normalized)
    years = [g["year"] for g in normalized if g["year"]]
    print(f"[i] Platforms: {dict(platforms.most_common(5))}")
    if years:
        print(f"[i] Year range: {min(years)}–{max(years)}")
    if errors:
        print(f"[!] {len(errors)} validation warnings (showing first 10):")
        for e in errors[:10]:
            print(f"  - {e}")

    print("[✓] build_index completed")


if __name__ == "__main__":
    build()
