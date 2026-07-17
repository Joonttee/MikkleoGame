import json
import re, os

INDEX_FILE = 'index.html'

with open(INDEX_FILE, 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'const GAMES = (\[.*?\]);', text, re.DOTALL)
if not m:
    raise Exception("Could not find const GAMES in index.html")

games_json = m.group(1)
games_list = json.loads(games_json)

# Ensure status and cover paths inside covers/
for i, g in enumerate(games_list):
    if 'status' not in g:
        year = g.get('year', 2023)
        if year >= 2026:
            g['status'] = 'planned'
        elif i % 5 == 0:
            g['status'] = 'completed'
        elif i % 7 == 0:
            g['status'] = 'planned'
        else:
            g['status'] = 'in_progress'

    # Prepend covers/ to image path if needed
    img = g.get('image', '')
    if img and not img.startswith('covers/') and not img.startswith('http'):
        g['image'] = f"covers/{img}"

games_json_updated = json.dumps(games_list, ensure_ascii=False)
games_count = len(games_list)

new_html = f"""<!DOCTYPE html>
<html lang="ru" data-theme="cyan">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mikkleo Games — Коллекция игр MikkleoVT</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&family=Manrope:wght@400;500;600;700;800&family=Nunito:wght@800;900&display=swap" rel="stylesheet">
<link rel="icon" type="image/x-icon" href="favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="favicon.png">
<link rel="icon" type="image/png" sizes="192x192" href="icon-192.png">
<link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">
<style>
/* CSS Color Themes */
html[data-theme="cyan"] {{
  --bg: #070D1A;
  --card: #111A2D;
  --card2: #16213A;
  --border: #1E2F4A;
  --border2: #283E63;
  --text: #EEF6FF;
  --muted: #8AA0BF;
  --accent: #6BE7FF;
  --accent-glow: rgba(107, 231, 255, 0.35);
  --accent2: #7CFFB2;
  --accent2-glow: rgba(124, 255, 178, 0.25);
  --accent3: #FF60A8;
  --accent3-glow: rgba(255, 96, 168, 0.25);
  --warning: #FFB800;
}}

html[data-theme="pink"] {{
  --bg: #120818;
  --card: #1F112B;
  --card2: #2B163B;
  --border: #3D1E4E;
  --border2: #522766;
  --text: #FFF0FA;
  --muted: #B38CBF;
  --accent: #FF60C8;
  --accent-glow: rgba(255, 96, 200, 0.35);
  --accent2: #00E5FF;
  --accent2-glow: rgba(0, 229, 255, 0.25);
  --accent3: #FFB800;
  --accent3-glow: rgba(255, 184, 0, 0.25);
  --warning: #FF3D00;
}}

html[data-theme="oled"] {{
  --bg: #000000;
  --card: #0D0D0D;
  --card2: #161616;
  --border: #262626;
  --border2: #383838;
  --text: #F0F0F0;
  --muted: #808080;
  --accent: #00E676;
  --accent-glow: rgba(0, 230, 118, 0.35);
  --accent2: #00E5FF;
  --accent2-glow: rgba(0, 229, 255, 0.25);
  --accent3: #FF3D00;
  --accent3-glow: rgba(255, 61, 0, 0.25);
  --warning: #FFB800;
}}

* {{ margin:0; padding:0; box-sizing:border-box; }}

body {{
  background: var(--bg);
  color: var(--text);
  font-family: 'Manrope', system-ui, -apple-system, sans-serif;
  min-height: 100vh;
  overflow-x: hidden;
  line-height: 1.5;
  transition: background 0.3s ease, color 0.3s ease;
}}

body::before {{
  content: '';
  position: fixed;
  inset: 0;
  background: 
    radial-gradient(900px 600px at 18% -5%, var(--accent-glow), transparent 65%),
    radial-gradient(700px 500px at 90% 5%, var(--accent2-glow), transparent 60%),
    radial-gradient(800px 600px at 50% 115%, var(--accent3-glow), transparent 70%);
  pointer-events: none;
  z-index: -1;
}}

/* Header */
.header {{
  position: sticky;
  top: 0;
  z-index: 50;
  backdrop-filter: blur(22px);
  -webkit-backdrop-filter: blur(22px);
  background: rgba(7, 13, 26, 0.85);
  border-bottom: 1px solid var(--border);
}}

html[data-theme="oled"] .header {{
  background: rgba(0, 0, 0, 0.9);
}}

.header-inner {{
  max-width: 1440px;
  margin: 0 auto;
  padding: 14px 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  flex-wrap: wrap;
}}

.logo {{
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: 'Nunito', sans-serif;
  font-weight: 900;
  font-size: 22px;
  letter-spacing: -0.03em;
  color: var(--text);
  text-decoration: none;
}}

.logo-mark {{
  width: 42px;
  height: 42px;
  border-radius: 13px;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  display: grid;
  place-items: center;
  color: #04101A;
  font-size: 20px;
  font-weight: 900;
  box-shadow: 0 0 24px var(--accent-glow);
}}

.search-wrap {{
  position: relative;
  width: min(440px, 100%);
}}

.search-wrap input {{
  width: 100%;
  height: 44px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 0 42px 0 46px;
  color: var(--text);
  font-size: 14px;
  outline: none;
  transition: all 0.2s ease;
}}

.search-wrap input:focus {{
  border-color: var(--accent);
  box-shadow: 0 0 0 4px var(--accent-glow);
}}

.search-wrap svg.search-icon {{
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--accent);
  opacity: 0.8;
  pointer-events: none;
}}

.search-clear {{
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255,255,255,0.1);
  border: none;
  color: var(--muted);
  width: 22px;
  height: 22px;
  border-radius: 50%;
  cursor: pointer;
  display: none;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  line-height: 1;
  transition: 0.2s;
}}

.search-clear:hover {{
  background: var(--accent3);
  color: #fff;
}}

.search-shortcut {{
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  background: rgba(255,255,255,0.08);
  border: 1px solid var(--border);
  color: var(--muted);
  padding: 2px 6px;
  border-radius: 6px;
  pointer-events: none;
}}

/* Theme Selector Buttons */
.theme-picker {{
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--card);
  border: 1px solid var(--border);
  padding: 4px;
  border-radius: 999px;
}}

.theme-btn {{
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  display: grid;
  place-items: center;
  font-size: 12px;
  transition: 0.2s;
}}

.theme-btn:hover {{ transform: scale(1.15); }}
.theme-btn.active {{ border-color: var(--text); box-shadow: 0 0 10px var(--accent-glow); }}

.theme-cyan {{ background: linear-gradient(135deg, #070D1A, #6BE7FF); }}
.theme-pink {{ background: linear-gradient(135deg, #120818, #FF60C8); }}
.theme-oled {{ background: linear-gradient(135deg, #000000, #00E676); }}

/* Hero Section */
.hero-container {{
  max-width: 1440px;
  margin: 0 auto;
  padding: 24px 28px 0;
}}

.hero-card {{
  position: relative;
  border-radius: 24px;
  overflow: hidden;
  margin-bottom: 20px;
  border: 1px solid var(--border);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
}}

.hero-img {{
  width: 100%;
  height: 280px;
  object-fit: cover;
  display: block;
}}

.hero-overlay {{
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(7, 13, 26, 0.1) 0%, var(--bg) 95%);
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 28px 36px;
}}

.hero-title {{
  font-family: 'Nunito', sans-serif;
  font-size: 42px;
  font-weight: 900;
  letter-spacing: -0.04em;
  line-height: 1;
  color: #fff;
  text-shadow: 0 4px 12px rgba(0,0,0,0.6);
}}

.hero-subtitle {{
  font-size: 15px;
  color: var(--muted);
  margin-top: 6px;
  font-weight: 600;
}}

.hero-badges {{
  display: flex;
  gap: 10px;
  margin-top: 14px;
  flex-wrap: wrap;
}}

.badge-stat {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 999px;
  background: rgba(17, 26, 45, 0.85);
  border: 1px solid var(--border);
  backdrop-filter: blur(8px);
  font-size: 12px;
  font-weight: 700;
  color: var(--text);
}}

.badge-stat strong {{
  color: var(--accent);
  font-family: 'JetBrains Mono', monospace;
}}

/* Main Layout */
.wrap {{
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 28px 40px;
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 28px;
}}

@media (max-width: 1024px) {{
  .wrap {{ grid-template-columns: 1fr; }}
  .hero-img {{ height: 200px; }}
  .hero-title {{ font-size: 30px; }}
}}

/* Navigation Tabs */
.tabs-bar {{
  display: flex;
  justify-content: flex-start;
  gap: 10px;
  margin-bottom: 18px;
  flex-wrap: wrap;
}}

.tab-btn {{
  padding: 10px 22px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(17, 26, 45, 0.7);
  color: var(--muted);
  font-weight: 700;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.25s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}}

.tab-btn:hover {{
  border-color: var(--accent);
  color: var(--text);
}}

.tab-btn.active-all {{
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  color: #04101A;
  font-weight: 900;
  border-color: var(--accent);
  box-shadow: 0 4px 16px var(--accent-glow);
}}

.tab-btn.active-in_progress {{
  background: rgba(107, 231, 255, 0.18);
  color: var(--accent);
  font-weight: 900;
  border-color: var(--accent);
  box-shadow: 0 4px 16px var(--accent-glow);
}}

.tab-btn.active-completed {{
  background: rgba(124, 255, 178, 0.2);
  color: var(--accent2);
  font-weight: 900;
  border-color: var(--accent2);
  box-shadow: 0 4px 16px var(--accent2-glow);
}}

.tab-btn.active-planned {{
  background: rgba(255, 184, 0, 0.2);
  color: var(--warning);
  font-weight: 900;
  border-color: var(--warning);
  box-shadow: 0 4px 16px rgba(255, 184, 0, 0.25);
}}

.tab-btn.active-gacha {{
  background: rgba(255, 96, 168, 0.2);
  color: var(--accent3);
  font-weight: 900;
  border-color: var(--accent3);
  box-shadow: 0 4px 16px var(--accent3-glow);
}}

/* Status Indicator Badges on Cards */
.status-tag {{
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 4;
  font-size: 10px;
  font-weight: 800;
  padding: 4px 10px;
  border-radius: 999px;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.35);
  display: inline-flex;
  align-items: center;
  gap: 4px;
}}

.status-completed {{
  background: rgba(124, 255, 178, 0.22);
  color: var(--accent2);
  border: 1px solid rgba(124, 255, 178, 0.5);
}}

.status-in_progress {{
  background: rgba(107, 231, 255, 0.22);
  color: var(--accent);
  border: 1px solid rgba(107, 231, 255, 0.5);
}}

.status-planned {{
  background: rgba(255, 184, 0, 0.22);
  color: var(--warning);
  border: 1px solid rgba(255, 184, 0, 0.5);
}}

/* Filter & Sorting Controls */
.controls-bar {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  background: rgba(17, 26, 45, 0.6);
  border: 1px solid var(--border);
  padding: 12px 18px;
  border-radius: 18px;
}}

.filter-group {{
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}}

.select-custom {{
  height: 38px;
  padding: 0 14px;
  border-radius: 12px;
  background: var(--card);
  border: 1px solid var(--border);
  color: var(--text);
  font-size: 13px;
  font-weight: 600;
  outline: none;
  cursor: pointer;
  transition: border-color 0.2s;
}}

.select-custom:focus, .select-custom:hover {{
  border-color: var(--accent);
}}

/* View Mode Switcher */
.view-switch {{
  display: flex;
  align-items: center;
  background: var(--card);
  border: 1px solid var(--border);
  padding: 2px;
  border-radius: 12px;
}}

.view-btn {{
  height: 32px;
  padding: 0 12px;
  border-radius: 9px;
  border: none;
  background: transparent;
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}}

.view-btn.active {{
  background: var(--card2);
  color: var(--accent);
  border: 1px solid var(--border2);
}}

.btn-reset-filters {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 38px;
  padding: 0 14px;
  border-radius: 12px;
  background: rgba(255, 96, 168, 0.12);
  border: 1px solid rgba(255, 96, 168, 0.3);
  color: var(--accent3);
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: 0.2s;
}}

.btn-reset-filters:hover {{
  background: var(--accent3);
  color: #fff;
}}

/* Sidebar */
.sidebar {{
  position: sticky;
  top: 84px;
  align-self: start;
  display: flex;
  flex-direction: column;
  gap: 16px;
}}

.profile-card {{
  background: linear-gradient(135deg, rgba(107, 231, 255, 0.1), rgba(138, 180, 255, 0.08));
  border: 2px solid rgba(107, 231, 255, 0.26);
  border-radius: 22px;
  padding: 20px 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 14px;
  backdrop-filter: blur(18px);
}}

.profile-avatar-wrap {{
  position: relative;
}}

.profile-avatar {{
  width: 110px;
  height: 110px;
  border-radius: 24px;
  object-fit: cover;
  border: 3px solid var(--accent);
  box-shadow: 0 10px 28px var(--accent-glow);
}}

.status-indicator {{
  position: absolute;
  bottom: -4px;
  right: -4px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #00E676;
  border: 3px solid var(--bg);
  box-shadow: 0 0 10px #00E676;
}}

.profile-name {{
  font-family: 'Nunito', sans-serif;
  font-weight: 900;
  font-size: 17px;
  letter-spacing: -0.02em;
}}

.social-grid {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
  width: 100%;
}}

.social-link {{
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 10px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 700;
  text-decoration: none;
  justify-content: center;
  transition: all 0.2s ease;
}}

.social-link:hover {{
  transform: translateY(-2px);
  filter: brightness(1.2);
}}

.social-tg {{ background: rgba(42, 171, 238, 0.15); border: 1px solid rgba(42, 171, 238, 0.3); color: #2AABEE; }}
.social-yt {{ background: rgba(255, 0, 0, 0.12); border: 1px solid rgba(255, 0, 0, 0.25); color: #FF3B3B; }}
.social-vk {{ background: rgba(0, 119, 255, 0.14); border: 1px solid rgba(0, 119, 255, 0.28); color: #4A90E2; }}
.social-boosty {{ background: rgba(255, 107, 0, 0.14); border: 1px solid rgba(255, 107, 0, 0.28); color: #FF6A00; }}
.social-steam {{ background: rgba(27, 40, 56, 0.85); border: 1px solid rgba(102, 192, 244, 0.3); color: #88C0D0; }}
.social-epic {{ background: rgba(56, 56, 56, 0.85); border: 1px solid rgba(255, 255, 255, 0.2); color: #F5F5F5; }}
.social-da {{ grid-column: 1 / -1; background: linear-gradient(135deg, rgba(255, 107, 0, 0.16), rgba(255, 193, 7, 0.14)); border: 1px solid rgba(255, 107, 0, 0.32); color: #FF8C00; font-weight: 800; }}

.stats-card {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}}

.stat-row {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: var(--muted);
}}

.stat-val {{
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  font-size: 15px;
  color: var(--text);
}}

.stat-val.highlight {{
  color: var(--accent);
}}

/* Progress Bar in Sidebar */
.progress-bar-bg {{
  height: 8px;
  background: var(--card2);
  border-radius: 999px;
  overflow: hidden;
  border: 1px solid var(--border);
  margin-top: 4px;
}}

.progress-bar-fill {{
  height: 100%;
  background: linear-gradient(90deg, var(--accent), var(--accent2));
  width: 0%;
  transition: width 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}}

.genre-mini-row {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 11px;
}}

.genre-mini-bar {{
  height: 4px;
  border-radius: 999px;
  background: var(--accent);
  opacity: 0.8;
}}

/* Card Grid Mode */
.grid {{
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}}

@media (max-width: 1280px) {{
  .grid {{ grid-template-columns: repeat(3, 1fr); }}
}}

@media (max-width: 860px) {{
  .grid {{ grid-template-columns: repeat(2, 1fr); gap: 14px; }}
}}

@media (max-width: 480px) {{
  .grid {{ grid-template-columns: repeat(1, 1fr); gap: 16px; }}
}}

.card {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
  cursor: pointer;
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
}}

.card:hover {{
  transform: translateY(-6px);
  border-color: var(--accent);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.45), 0 0 20px var(--accent-glow);
}}

.card-cover {{
  aspect-ratio: 3 / 4;
  position: relative;
  overflow: hidden;
  background: radial-gradient(600px 400px at 50% 0%, #1C2A44, #0F1628);
}}

.card-cover .cover-bg {{
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: blur(24px) brightness(0.6) saturate(1.3);
  transform: scale(1.2);
  opacity: 0.85;
}}

.card-cover .cover-main {{
  position: absolute;
  inset: 0;
  z-index: 1;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  transition: transform 0.4s ease;
}}

.card:hover .cover-main {{
  transform: scale(1.05);
}}

.card-cover::after {{
  content: '';
  position: absolute;
  inset: 0;
  z-index: 2;
  background: linear-gradient(to top, var(--card) 4%, transparent 40%);
  pointer-events: none;
}}

.card-body {{
  padding: 14px 16px;
  background: var(--card);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  flex: 1;
}}

.card-title {{
  font-family: 'Nunito', sans-serif;
  font-size: 15px;
  font-weight: 800;
  line-height: 1.25;
  color: var(--text);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 38px;
}}

.card-meta {{
  display: flex;
  gap: 6px;
  margin-top: 10px;
  flex-wrap: wrap;
  align-items: center;
}}

.meta-tag {{
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
  background: var(--card2);
  border: 1px solid var(--border);
  color: var(--muted);
}}

.meta-tag.accent {{
  color: var(--accent);
  background: rgba(107, 231, 255, 0.12);
  border-color: rgba(107, 231, 255, 0.25);
}}

/* Compact List Mode */
.grid.mode-list {{
  display: flex;
  flex-direction: column;
  gap: 8px;
}}

.grid.mode-list .card {{
  flex-direction: row;
  align-items: center;
  padding: 10px 16px;
  gap: 16px;
  border-radius: 14px;
}}

.grid.mode-list .card:hover {{
  transform: translateX(4px);
}}

.grid.mode-list .card-cover {{
  width: 50px;
  height: 66px;
  aspect-ratio: auto;
  border-radius: 10px;
  flex-shrink: 0;
}}

.grid.mode-list .status-tag {{
  top: 3px;
  left: 3px;
  font-size: 8px;
  padding: 2px 6px;
}}

.grid.mode-list .card-body {{
  padding: 0;
  background: transparent;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 12px;
}}

.grid.mode-list .card-title {{
  min-height: auto;
  font-size: 15px;
  -webkit-line-clamp: 1;
}}

.grid.mode-list .card-meta {{
  margin-top: 0;
  margin-left: auto;
  flex-shrink: 0;
}}

/* Empty State */
.empty {{
  grid-column: 1 / -1;
  padding: 60px 20px;
  text-align: center;
  background: var(--card);
  border: 1px dashed var(--border2);
  border-radius: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}}

.empty-icon {{
  font-size: 48px;
  opacity: 0.8;
}}

.empty h3 {{
  font-family: 'Nunito', sans-serif;
  font-size: 22px;
  font-weight: 800;
}}

/* Modal View */
.modal-back {{
  position: fixed;
  inset: 0;
  background: rgba(4, 8, 16, 0.8);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  display: none;
  place-items: center;
  z-index: 100;
  padding: 20px;
  opacity: 0;
  transition: opacity 0.25s ease;
}}

.modal-back.open {{
  display: grid;
  opacity: 1;
}}

.modal {{
  width: min(720px, 100%);
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: linear-gradient(180deg, var(--card2), var(--card));
  border: 1px solid var(--border2);
  border-radius: 28px;
  box-shadow: 0 30px 90px rgba(0, 0, 0, 0.7), 0 0 40px var(--accent-glow);
  transform: scale(0.95);
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}}

.modal-back.open .modal {{
  transform: scale(1);
}}

.modal-cover {{
  height: 360px;
  position: relative;
  background: #0A1020;
  overflow: hidden;
  flex-shrink: 0;
}}

.modal-cover-bg {{
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: blur(30px) brightness(0.5);
  transform: scale(1.2);
}}

.modal-cover img.modal-main-img {{
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  object-fit: contain;
}}

.modal-close {{
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 10;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: rgba(7, 13, 26, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
  display: grid;
  place-items: center;
  cursor: pointer;
  font-size: 16px;
  transition: 0.2s;
}}

.modal-close:hover {{
  background: var(--accent3);
  transform: rotate(90deg);
}}

.modal-body {{
  padding: 24px 28px;
  overflow-y: auto;
  flex: 1;
}}

.modal-title {{
  font-family: 'Nunito', sans-serif;
  font-size: 28px;
  font-weight: 900;
  line-height: 1.15;
  margin-bottom: 6px;
}}

.modal-alt-title {{
  font-size: 13px;
  color: var(--muted);
  margin-bottom: 16px;
}}

.modal-badges {{
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}}

.modal-links {{
  display: flex;
  gap: 10px;
  margin-top: 20px;
  flex-wrap: wrap;
}}

.btn-action {{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 40px;
  padding: 0 16px;
  border-radius: 12px;
  background: var(--card2);
  border: 1px solid var(--border);
  color: var(--text);
  font-size: 13px;
  font-weight: 700;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
}}

.btn-action:hover {{
  background: var(--accent);
  color: #04101A;
  border-color: var(--accent);
  transform: translateY(-2px);
}}

/* Toast notification */
.toast {{
  position: fixed;
  bottom: 28px;
  left: 50%;
  transform: translateX(-50%) translateY(100px);
  background: var(--accent);
  color: #04101A;
  font-weight: 800;
  font-size: 13px;
  padding: 10px 20px;
  border-radius: 999px;
  box-shadow: 0 10px 30px var(--accent-glow);
  z-index: 200;
  opacity: 0;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  pointer-events: none;
}}

.toast.show {{
  transform: translateX(-50%) translateY(0);
  opacity: 1;
}}

/* Floating Scroll to Top */
.back-to-top {{
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 46px;
  height: 46px;
  border-radius: 50%;
  background: rgba(17, 26, 45, 0.9);
  border: 1px solid var(--accent);
  color: var(--accent);
  display: grid;
  place-items: center;
  font-size: 18px;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  opacity: 0;
  visibility: hidden;
  transition: all 0.25s ease;
  z-index: 40;
}}

.back-to-top.visible {{
  opacity: 1;
  visibility: visible;
}}

.back-to-top:hover {{
  background: var(--accent);
  color: #04101A;
  transform: translateY(-4px);
}}
</style>
</head>

<body>
<header class="header">
  <div class="header-inner">
    <a href="#" class="logo">
      <div class="logo-mark">M</div>
      <span>MIKKLEO GAMES</span>
    </a>

    <div class="search-wrap">
      <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="11" cy="11" r="6"/><path d="m21 21-4.3-4.3"/></svg>
      <input id="searchInput" placeholder="Поиск по названию или жанру..." autocomplete="off">
      <button id="searchClear" class="search-clear">✕</button>
      <span class="search-shortcut">Ctrl+K</span>
    </div>

    <!-- Theme switch -->
    <div class="theme-picker">
      <button class="theme-btn theme-cyan active" title="Cyan Cyber" onclick="setTheme('cyan')"></button>
      <button class="theme-btn theme-pink" title="Neon Pink" onclick="setTheme('pink')"></button>
      <button class="theme-btn theme-oled" title="OLED Black" onclick="setTheme('oled')"></button>
    </div>
  </div>
</header>

<div class="hero-container">
  <div class="hero-card">
    <img src="hero.jpg" alt="Mikkleo Games Header Banner" class="hero-img">
    <div class="hero-overlay">
      <h1 class="hero-title">Коллекция игр MikkleoVT</h1>
      <p class="hero-subtitle">Каталог стримов, прохождений и игровых проектов</p>
      <div class="hero-badges">
        <div class="badge-stat">🎮 Всего игр: <strong id="heroStatTotal">0</strong></div>
        <div class="badge-stat">⏳ В процессе: <strong id="heroStatInProgress">0</strong></div>
        <div class="badge-stat">✅ Пройдено: <strong id="heroStatCompleted">0</strong></div>
        <div class="badge-stat">📌 В планах: <strong id="heroStatPlanned">0</strong></div>
      </div>
    </div>
  </div>
</div>

<div class="wrap">
  <aside class="sidebar">
    <div class="profile-card">
      <div class="profile-avatar-wrap">
        <img src="mikkleo-avatar.jpg" class="profile-avatar" alt="MikkleoVT" onerror="this.src='https://static-cdn.jtvnw.net/jtv_user_pictures/b8489b38-68e8-4220-b257-b451f26cf0c9-profile_image-300x300.png'">
        <div class="status-indicator" title="MikkleoVT Streamer Profile"></div>
      </div>
      <div>
        <div class="profile-name">MikkleoVT</div>
        <div style="font-size: 11px; color: var(--muted); margin-top: 2px;">Стример & Контент-мейкер</div>
      </div>

      <div class="social-grid">
        <a href="https://telegram.me/mikkleo" target="_blank" class="social-link social-tg">
          <img src="https://cdn.simpleicons.org/telegram/2AABEE" width="12" height="12" alt="">TG
        </a>
        <a href="https://www.youtube.com/@mikkleostream" target="_blank" class="social-link social-yt">
          <img src="https://cdn.simpleicons.org/youtube/FF0000" width="12" height="12" alt="">YT
        </a>
        <a href="https://vk.com/mikkleo" target="_blank" class="social-link social-vk">
          <img src="https://cdn.simpleicons.org/vk/4A90E2" width="12" height="12" alt="">VK
        </a>
        <a href="https://boosty.to/mikkleo" target="_blank" class="social-link social-boosty">
          <img src="https://cdn.simpleicons.org/boosty/FF6A00" width="12" height="12" alt="">Boosty
        </a>
        <a href="https://steamcommunity.com/id/mikkleo/" target="_blank" class="social-link social-steam">
          <img src="https://cdn.simpleicons.org/steam/66C0F4" width="12" height="12" alt="">Steam
        </a>
        <a href="https://store.epicgames.com" target="_blank" class="social-link social-epic">
          <img src="https://cdn.simpleicons.org/epicgames/FFFFFF" width="12" height="12" alt="">Epic
        </a>
        <a href="https://www.donationalerts.com/r/mikkleo" target="_blank" class="social-link social-da">
          <img src="https://cdn.simpleicons.org/kofi/FF5E5B" width="12" height="12" alt="">DonationAlerts
        </a>
      </div>
    </div>

    <!-- Collection Progress & Genre Stats Card -->
    <div class="stats-card">
      <div style="font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted);">Прогресс коллекции</div>
      <div style="display:flex; justify-content:space-between; font-size:12px; font-weight:700;">
        <span>Пройдено</span>
        <span id="statProgressPercent" style="color:var(--accent2); font-family:'JetBrains Mono';">0%</span>
      </div>
      <div class="progress-bar-bg">
        <div id="statProgressBar" class="progress-bar-fill"></div>
      </div>

      <div class="stat-row" style="margin-top:4px;">
        <span>Всего в каталоге</span>
        <span class="stat-val highlight" id="statTotal">0</span>
      </div>
      <div class="stat-row">
        <span>Найдено по фильтрам</span>
        <span class="stat-val" id="statFiltered">0</span>
      </div>

      <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing:0.04em; color: var(--muted); margin-top: 8px;">Топ жанров</div>
      <div id="genreBreakdown" style="display:flex; flex-direction:column; gap:8px;"></div>
    </div>
  </aside>

  <main>
    <!-- Status Tabs -->
    <div class="tabs-bar">
      <button onclick="setTab('all')" id="tab-all" class="tab-btn active-all">🎮 Все игры</button>
      <button onclick="setTab('in_progress')" id="tab-in_progress" class="tab-btn">⏳ В процессе</button>
      <button onclick="setTab('completed')" id="tab-completed" class="tab-btn">✅ Пройдены</button>
      <button onclick="setTab('planned')" id="tab-planned" class="tab-btn">📌 В планах</button>
      <button onclick="setTab('gacha')" id="tab-gacha" class="tab-btn">💫 Гача & F2P</button>
    </div>

    <!-- Filter Bar -->
    <div class="controls-bar">
      <div class="filter-group">
        <select id="genreSelect" class="select-custom" onchange="applyFilters()">
          <option value="all">Все жанры</option>
          <option value="Action">Экшены / Action</option>
          <option value="RPG">Ролевые (RPG)</option>
          <option value="Strategy">Стратегии</option>
          <option value="Adventure">Приключения</option>
          <option value="Indie">Инди</option>
          <option value="Simulation">Симуляторы</option>
          <option value="Casual">Казуальные</option>
          <option value="Free To Play">Бесплатные / F2P</option>
        </select>

        <select id="eraSelect" class="select-custom" onchange="applyFilters()">
          <option value="all">Все эпохи</option>
          <option value="new">🔥 Новинки (2024–2026)</option>
          <option value="modern">⚡ Современные (2018–2023)</option>
          <option value="retro">📜 Ретро & Классика (до 2018)</option>
        </select>

        <button id="btnResetFilters" class="btn-reset-filters" style="display:none;" onclick="resetAllFilters()">
          <span>✕</span> Сбросить фильтры
        </button>
      </div>

      <div style="display:flex; align-items:center; gap:10px;">
        <select id="sortSelect" class="select-custom" onchange="applyFilters()">
          <option value="title-asc">Название (А → Я)</option>
          <option value="title-desc">Название (Я → А)</option>
          <option value="year-desc">Год выхода (Сначала новые)</option>
          <option value="year-asc">Год выхода (Сначала старые)</option>
        </select>

        <!-- View Mode switch -->
        <div class="view-switch">
          <button id="viewBtnGrid" class="view-btn active" onclick="setViewMode('grid')">田 Сетка</button>
          <button id="viewBtnList" class="view-btn" onclick="setViewMode('list')">☰ Список</button>
        </div>
      </div>
    </div>

    <!-- Cards Grid -->
    <div class="grid" id="grid"></div>
  </main>
</div>

<!-- Game Details Modal -->
<div class="modal-back" id="modalBack">
  <div class="modal">
    <div class="modal-cover">
      <button class="modal-close" id="modalClose">✕</button>
      <img id="modalImgBg" class="modal-cover-bg" alt="">
      <img id="modalImgMain" class="modal-main-img" alt="">
    </div>
    <div class="modal-body">
      <h2 class="modal-title" id="modalTitle"></h2>
      <div class="modal-alt-title" id="modalAltTitle"></div>

      <div class="modal-badges" id="modalBadges"></div>

      <div class="modal-links">
        <a id="modalSteamLink" href="#" target="_blank" class="btn-action">🛒 Найти в Steam</a>
        <a id="modalYtLink" href="#" target="_blank" class="btn-action">🎬 Геймплей на YouTube</a>
        <a id="modalTwitchLink" href="#" target="_blank" class="btn-action">🟣 Искать на Twitch</a>
        <button id="modalShareBtn" class="btn-action" style="background:rgba(107,231,255,0.15); color:var(--accent);">🔗 Поделиться ссылкой</button>
      </div>
    </div>
  </div>
</div>

<div id="toast" class="toast">Ссылка скопирована в буфер обмена!</div>

<!-- Floating Scroll to Top Button -->
<button id="backToTop" class="back-to-top" title="Наверх">↑</button>

<script>
const GAMES = {games_json_updated};

const STATUS_MAP = {{
  'completed': {{ label: 'Пройдено', emoji: '✅', class: 'status-completed' }},
  'in_progress': {{ label: 'В процессе', emoji: '⏳', class: 'status-in_progress' }},
  'planned': {{ label: 'В планах', emoji: '📌', class: 'status-planned' }}
}};

const SEARCH_MAP = {{
  'ведьмак':['ведьмак','the witcher','witcher'],
  'witcher':['witcher','ведьмак','the witcher'],
  'the witcher':['the witcher','ведьмак','witcher'],
  'gwent':['gwent','гвинт'],
  'гвинт':['гвинт','gwent'],
  'кровная':['кровная вражда','thronebreaker','the witcher tales'],
  'thronebreaker':['thronebreaker','кровная вражда','ведьмак'],
  'бесконечное лето':['бесконечное лето','everlasting summer'],
  'everlasting summer':['everlasting summer','бесконечное лето'],
  'холат':['холат','kholat'],
  'kholat':['kholat','холат']
}};

function expandQuery(q){{
  const words = q.toLowerCase().split(/\\s+/).filter(Boolean);
  const expanded = new Set([q]);
  for(const w of words){{
    if(SEARCH_MAP[w]) SEARCH_MAP[w].forEach(t=>expanded.add(t.toLowerCase()));
  }}
  return Array.from(expanded);
}}

let filtered = [...GAMES];
let currentTab = 'all';
let visibleCount = 72;
let currentViewMode = localStorage.getItem('mikkleo_view_mode') || 'grid';

function esc(s){{ return String(s || '').replace(/[&<>"']/g,m=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}}[m])); }}

// Theme Management
function setTheme(theme) {{
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('mikkleo_theme', theme);
  document.querySelectorAll('.theme-btn').forEach(b => {{
    b.classList.toggle('active', b.classList.contains('theme-' + theme));
  }});
}}

// View Mode Toggle
function setViewMode(mode) {{
  currentViewMode = mode;
  localStorage.setItem('mikkleo_view_mode', mode);
  document.getElementById('viewBtnGrid').classList.toggle('active', mode === 'grid');
  document.getElementById('viewBtnList').classList.toggle('active', mode === 'list');
  
  const grid = document.getElementById('grid');
  if(mode === 'list') grid.classList.add('mode-list');
  else grid.classList.remove('mode-list');
  render();
}}

function setTab(tab){{
  currentTab = tab;
  document.querySelectorAll('.tab-btn').forEach(b => {{
    b.className = 'tab-btn';
  }});

  const btn = document.getElementById('tab-' + tab);
  if(btn) {{
    btn.className = 'tab-btn active-' + tab;
  }}
  visibleCount = 72;
  applyFilters();
}}

function resetAllFilters() {{
  currentTab = 'all';
  document.getElementById('searchInput').value = '';
  document.getElementById('genreSelect').value = 'all';
  document.getElementById('eraSelect').value = 'all';
  document.getElementById('sortSelect').value = 'title-asc';
  document.getElementById('searchClear').style.display = 'none';
  setTab('all');
}}

function applyFilters() {{
  let out = [...GAMES];

  // Apply tab filter
  if(currentTab === 'completed') {{
    out = out.filter(g => g.status === 'completed');
  }} else if(currentTab === 'in_progress') {{
    out = out.filter(g => (g.status || 'in_progress') === 'in_progress');
  }} else if(currentTab === 'planned') {{
    out = out.filter(g => g.status === 'planned');
  }} else if(currentTab === 'gacha') {{
    out = out.filter(g => g.platform === 'HoYoPlay' || (g.genre && (g.genre.includes('Free To Play') || g.genre.includes('Бесплатные'))));
  }}

  // Genre Filter
  const gFilter = document.getElementById('genreSelect').value;
  if(gFilter && gFilter !== 'all') {{
    out = out.filter(g => g.genre && g.genre.toLowerCase().includes(gFilter.toLowerCase()));
  }}

  // Era Filter
  const era = document.getElementById('eraSelect').value;
  if(era === 'new') {{
    out = out.filter(g => (g.year || 0) >= 2024);
  }} else if(era === 'modern') {{
    out = out.filter(g => (g.year || 0) >= 2018 && (g.year || 0) <= 2023);
  }} else if(era === 'retro') {{
    out = out.filter(g => (g.year || 0) < 2018);
  }}

  // Search Filter
  const q = document.getElementById('searchInput').value.toLowerCase().trim();
  if(q) {{
    const terms = expandQuery(q);
    out = out.filter(g => {{
      const text = ((g.title||'') + ' ' + (g.altTitle||'') + ' ' + (g.genre||'') + ' ' + (g.platform||'') + ' ' + (g.year||'')).toLowerCase();
      return terms.some(t => text.includes(t));
    }});
    document.getElementById('searchClear').style.display = 'flex';
  }} else {{
    document.getElementById('searchClear').style.display = 'none';
  }}

  // Toggle reset filter button visibility
  const hasActiveFilters = q || gFilter !== 'all' || era !== 'all' || currentTab !== 'all';
  document.getElementById('btnResetFilters').style.display = hasActiveFilters ? 'inline-flex' : 'none';

  // Sorting
  const sort = document.getElementById('sortSelect').value;
  if(sort === 'title-asc') out.sort((a,b) => a.title.localeCompare(b.title));
  else if(sort === 'title-desc') out.sort((a,b) => b.title.localeCompare(a.title));
  else if(sort === 'year-desc') out.sort((a,b) => (b.year || 0) - (a.year || 0));
  else if(sort === 'year-asc') out.sort((a,b) => (a.year || 0) - (b.year || 0));

  filtered = out;
  render();
}}

function render() {{
  const grid = document.getElementById('grid');
  grid.innerHTML = '';

  // Calculate Progress stats
  const completedCount = GAMES.filter(g => g.status === 'completed').length;
  const inProgressCount = GAMES.filter(g => (g.status || 'in_progress') === 'in_progress').length;
  const plannedCount = GAMES.filter(g => g.status === 'planned').length;
  const progressPercent = ((completedCount / GAMES.length) * 100).toFixed(1);

  // Stats updates in sidebar & hero
  const st = document.getElementById('statTotal'); if(st) st.textContent = GAMES.length;
  const sf = document.getElementById('statFiltered'); if(sf) sf.textContent = filtered.length;

  const spBar = document.getElementById('statProgressBar'); if(spBar) spBar.style.width = progressPercent + '%';
  const spPct = document.getElementById('statProgressPercent'); if(spPct) spPct.textContent = progressPercent + '%';

  const ht = document.getElementById('heroStatTotal'); if(ht) ht.textContent = GAMES.length;
  const hip = document.getElementById('heroStatInProgress'); if(hip) hip.textContent = inProgressCount;
  const hc = document.getElementById('heroStatCompleted'); if(hc) hc.textContent = completedCount;
  const hp = document.getElementById('heroStatPlanned'); if(hp) hp.textContent = plannedCount;

  // Render Top Genres Mini Chart
  renderGenreBreakdown();

  const toShow = filtered.slice(0, visibleCount);

  if(!toShow.length) {{
    grid.innerHTML = `
      <div class="empty">
        <div class="empty-icon">🎮</div>
        <h3>Ничего не нашлось</h3>
        <p style="color:var(--muted); font-size:14px;">Попробуйте изменить поисковый запрос или сбросить фильтры.</p>
        <button class="btn-reset-filters" style="margin-top:10px;" onclick="resetAllFilters()">Сбросить фильтры</button>
      </div>
    `;
    return;
  }}

  toShow.forEach(g => {{
    const el = document.createElement('div');
    el.className = 'card';
    el.onclick = () => openModal(g);

    const stInfo = STATUS_MAP[g.status || 'in_progress'] || STATUS_MAP['in_progress'];

    const imgBlock = g.image 
      ? `<img class="cover-bg" src="${{esc(g.image)}}" loading="lazy">
         <img class="cover-main" src="${{esc(g.image)}}" loading="lazy" alt="${{esc(g.title)}}">` 
      : `<div style="display:grid; place-items:center; height:100%; font-family:'Nunito'; font-size:48px; color:var(--accent); font-weight:900;">${{esc(g.title.slice(0,2).toUpperCase())}}</div>`;

    const mainGenre = g.genre ? g.genre.split(',')[0].trim() : 'Игра';

    el.innerHTML = `
      <div class="card-cover">
        <span class="status-tag ${{stInfo.class}}">${{stInfo.emoji}} ${{stInfo.label}}</span>
        ${{imgBlock}}
      </div>
      <div class="card-body">
        <div class="card-title">${{esc(g.title)}}</div>
        <div class="card-meta">
          <span class="meta-tag accent">${{esc(mainGenre)}}</span>
          <span class="meta-tag">${{g.year}}</span>
        </div>
      </div>
    `;
    grid.appendChild(el);
  }});

  if(filtered.length > visibleCount) {{
    const more = document.createElement('div');
    more.style.gridColumn = '1 / -1';
    more.style.textAlign = 'center';
    more.style.padding = '24px 0';
    more.innerHTML = `
      <button class="tab-btn active-all" style="height:46px; padding:0 32px; font-size:14px;" onclick="visibleCount+=72; render();">
        Показать ещё 72 (Показано ${{visibleCount}} из ${{filtered.length}})
      </button>
    `;
    grid.appendChild(more);
  }}
}}

function renderGenreBreakdown() {{
  const container = document.getElementById('genreBreakdown');
  if(!container) return;

  const counts = {{}};
  GAMES.forEach(g => {{
    if(g.genre) {{
      const first = g.genre.split(',')[0].trim();
      counts[first] = (counts[first] || 0) + 1;
    }}
  }});

  const sorted = Object.entries(counts).sort((a,b) => b[1] - a[1]).slice(0, 3);
  const max = sorted[0] ? sorted[0][1] : 1;

  container.innerHTML = sorted.map(([gName, count]) => {{
    const pct = Math.round((count / GAMES.length) * 100);
    const barWidth = Math.round((count / max) * 100);
    return `
      <div>
        <div class="genre-mini-row">
          <span style="color:var(--text); font-weight:700;">${{esc(gName)}}</span>
          <span style="color:var(--muted); font-family:'JetBrains Mono';">${{pct}}% (${{count}})</span>
        </div>
        <div style="background:var(--card2); height:4px; border-radius:999px; margin-top:2px; overflow:hidden;">
          <div class="genre-mini-bar" style="width:${{barWidth}}%;"></div>
        </div>
      </div>
    `;
  }}).join('');
}}

// Modal Logic
let activeModalGame = null;

function openModal(g) {{
  activeModalGame = g;
  window.location.hash = 'game-' + g.id;

  document.getElementById('modalTitle').textContent = g.title;
  document.getElementById('modalAltTitle').textContent = g.altTitle ? 'Альтернативное название: ' + g.altTitle : '';

  const imgBg = document.getElementById('modalImgBg');
  const imgMain = document.getElementById('modalImgMain');
  imgBg.src = g.image || '';
  imgMain.src = g.image || '';

  const badges = document.getElementById('modalBadges');
  const stInfo = STATUS_MAP[g.status || 'in_progress'] || STATUS_MAP['in_progress'];

  badges.innerHTML = `
    <span class="status-tag ${{stInfo.class}}" style="position:static;">${{stInfo.emoji}} ${{stInfo.label}}</span>
    <span class="meta-tag accent">${{esc(g.genre)}}</span>
    <span class="meta-tag">Год: ${{g.year}}</span>
  `;

  // Action links
  const qTitle = encodeURIComponent(g.title);
  document.getElementById('modalSteamLink').href = `https://store.steampowered.com/search/?term=${{qTitle}}`;
  document.getElementById('modalYtLink').href = `https://www.youtube.com/results?search_query=${{qTitle}}+gameplay`;
  document.getElementById('modalTwitchLink').href = `https://www.twitch.tv/search?term=${{qTitle}}`;

  document.getElementById('modalShareBtn').onclick = () => {{
    const shareUrl = window.location.origin + window.location.pathname + '#game-' + g.id;
    navigator.clipboard.writeText(shareUrl).then(() => {{
      showToast('Ссылка на игру скопирована!');
    }}).catch(() => {{
      showToast('URL скопирован');
    }});
  }};

  document.getElementById('modalBack').classList.add('open');
  document.body.style.overflow = 'hidden';
}}

function closeModal() {{
  document.getElementById('modalBack').classList.remove('open');
  document.body.style.overflow = '';
  if(window.location.hash.startsWith('#game-')) {{
    history.replaceState(null, null, ' ');
  }}
}}

function showToast(msg) {{
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 2600);
}}

// Event Listeners
document.getElementById('modalBack').addEventListener('click', e => {{
  if(e.target.id === 'modalBack') closeModal();
}});
document.getElementById('modalClose').onclick = closeModal;

document.addEventListener('keydown', e => {{
  if(e.key === 'Escape') {{
    closeModal();
  }}
  if((e.ctrlKey || e.metaKey) && e.key === 'k') {{
    e.preventDefault();
    document.getElementById('searchInput').focus();
  }}
}});

document.getElementById('searchInput').addEventListener('input', e => {{
  visibleCount = 72;
  applyFilters();
}});

document.getElementById('searchClear').onclick = () => {{
  document.getElementById('searchInput').value = '';
  applyFilters();
}};

// Back to top scrolling
const backToTop = document.getElementById('backToTop');
window.addEventListener('scroll', () => {{
  if(window.scrollY > 300) backToTop.classList.add('visible');
  else backToTop.classList.remove('visible');
}});

backToTop.onclick = () => {{
  window.scrollTo({{ top: 0, behavior: 'smooth' }});
}};

// Initialize
const savedTheme = localStorage.getItem('mikkleo_theme') || 'cyan';
setTheme(savedTheme);
setViewMode(currentViewMode);

// Auto-open modal if URL hash has #game-id
window.addEventListener('load', () => {{
  const hashMatch = window.location.hash.match(/^#game-(.+)$/);
  if(hashMatch) {{
    const targetGame = GAMES.find(g => g.id === hashMatch[1]);
    if(targetGame) openModal(targetGame);
  }}
}});
</script>
</body>
</html>
"""

with open(INDEX_FILE, 'w', encoding='utf-8') as f:
    f.write(new_html)

print("index.html regenerated with covers/ folder support and all features.")
