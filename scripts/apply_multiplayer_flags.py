#!/usr/bin/env python3
"""
Mikkleo Games — проставление флагов мультиплеера/коопа.

Читает курируемый список data/mp_coop.json:
  { "mp": [...titles], "coop": [...titles], "both": [...titles] }

и проставляет isMultiplayer / isCoop в data/games.json:
  mp   -> isMultiplayer = true
  coop -> isCoop = true
  both -> оба флага

Семантика вкладок на сайте:
  🕹️ MP  — соревновательный/PvP/социальный/ММО мультиплеер
  🤝 Coop — совместное прохождение / игра вместе против ИИ

Важно:
- Скрипт только ВКЛЮЧАЕТ флаги, ничего не выключает (не трогает ручные отметки
  стримера: админские оверрайды всё равно имеют приоритет над дефолтами каталога).
- Идемпотентен: повторный запуск ничего не меняет.
- Все тайтлы из mp_coop.json обязаны находиться в каталоге (матч по
  нормализованному названию) — иначе ошибка и выход с кодом 1, чтобы
  опечатки не терялись.

Запуск:
  python scripts/apply_multiplayer_flags.py [--dry-run]
"""
import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_JSON = ROOT / "data" / "games.json"
FLAGS_JSON = ROOT / "data" / "mp_coop.json"


def normalize_title(s: str) -> str:
    if not s:
        return ""
    return re.sub(r"[^0-9a-zA-Zа-яА-ЯёЁ]", "", s).lower()


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply curated MP/Coop flags to games.json")
    parser.add_argument("--dry-run", action="store_true", help="только показать изменения")
    args = parser.parse_args()

    flags = json.loads(FLAGS_JSON.read_text(encoding="utf-8"))
    games = json.loads(DATA_JSON.read_text(encoding="utf-8"))
    by_norm = {normalize_title(g.get("title", "")): g for g in games}

    plan = {}  # norm -> (isMultiplayer, isCoop, display_title)
    for key, mp, coop in (("mp", True, False), ("coop", False, True), ("both", True, True)):
        for title in flags.get(key, []):
            norm = normalize_title(title)
            if not norm:
                print(f"[!] Пустой тайтл в секции '{key}'", file=sys.stderr)
            if norm in plan:
                prev_mp, prev_coop, prev_title = plan[norm]
                plan[norm] = (prev_mp or mp, prev_coop or coop, title)
            else:
                plan[norm] = (mp, coop, title)

    missing = [(t, "") for norm, (_, _, t) in plan.items() if norm not in by_norm]
    dup_hints = []
    if missing:
        # подсказка похожих названий
        for t, _ in missing:
            nt = normalize_title(t)
            sims = [g["title"] for g in games if normalize_title(g.get("title", "")).startswith(nt[:6])][:3]
            if sims:
                dup_hints.append(f"    похожее: {sims}")
        print("[✗] Эти тайтлы не найдены в каталоге:", file=sys.stderr)
        for t, _ in missing:
            print(f"    '{t}'", file=sys.stderr)
        for h in dup_hints:
            print(h, file=sys.stderr)
        return 1

    changed = 0
    for norm, (mp, coop, title) in plan.items():
        g = by_norm[norm]
        new_mp = bool(g.get("isMultiplayer")) or mp
        new_coop = bool(g.get("isCoop")) or coop
        if new_mp != bool(g.get("isMultiplayer")) or new_coop != bool(g.get("isCoop")):
            changed += 1
        g["isMultiplayer"] = new_mp
        g["isCoop"] = new_coop
    mp_total = sum(1 for g in games if g.get("isMultiplayer"))
    coop_total = sum(1 for g in games if g.get("isCoop"))

    print(f"[i] Записей в списке: mp={len(flags.get('mp', []))}, coop={len(flags.get('coop', []))}, both={len(flags.get('both', []))}")
    print(f"[i] Игр изменено: {changed}")
    print(f"[i] Итого в каталоге: isMultiplayer={mp_total}, isCoop={coop_total} (из {len(games)})")

    if args.dry_run:
        print("[i] Dry run — games.json не изменён")
        return 0

    if changed:
        DATA_JSON.write_text(json.dumps(games, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[✓] Записан {DATA_JSON}")
        # пересобрать ESM-фолбэк data.js
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("build_index", str(ROOT / "scripts" / "build_index.py"))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mod.build()
            print("[✓] data.js пересобран")
        except Exception as e:
            print(f"[!] Не удалось пересобрать data.js: {e}", file=sys.stderr)
    else:
        print("[i] Изменений нет — games.json актуален")
    return 0


if __name__ == "__main__":
    sys.exit(main())
