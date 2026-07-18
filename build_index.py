import json
import re, os

INDEX_FILE = 'index.html'

def rebuild_index(games_data=None):
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        text = f.read()

    m = re.search(r'const GAMES = (\[.*?\]);', text, re.DOTALL)
    if not m:
        raise Exception("Could not find const GAMES in index.html")

    if games_data is None:
        games_json = m.group(1)
        games_list = json.loads(games_json)
    else:
        games_list = games_data

    # Ensure status & category fields
    for g in games_list:
        # Reset status so the streamer can mark games themselves via the admin panel.
        # Existing local admin overrides still apply at runtime via getEffectiveStatus().
        g['status'] = None
        if 'isGacha' not in g:
            g['isGacha'] = False
        if 'isMultiplayer' not in g:
            g['isMultiplayer'] = False
        if 'isCoop' not in g:
            g['isCoop'] = False

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

html[data-theme="amber"] {{
  --bg: #150B04;
  --card: #2A1A0E;
  --card2: #3A2615;
  --border: #5A3A20;
  --border2: #7A4F2C;
  --text: #FFF4E0;
  --muted: #D6B48A;
  --accent: #FFB74D;
  --accent-glow: rgba(255, 183, 77, 0.4);
  --accent2: #FFD580;
  --accent2-glow: rgba(255, 213, 128, 0.28);
  --accent3: #FF6B6B;
  --accent3-glow: rgba(255, 107, 107, 0.28);
  --warning: #FFE066;
}}

html[data-theme="emerald"] {{
  --bg: #03110A;
  --card: #0A2018;
  --card2: #112E22;
  --border: #1E4530;
  --border2: #2D5C44;
  --text: #E8FFEC;
  --muted: #95C5A8;
  --accent: #4DE69C;
  --accent-glow: rgba(77, 230, 156, 0.4);
  --accent2: #7CFFB2;
  --accent2-glow: rgba(124, 255, 178, 0.28);
  --accent3: #FFB74D;
  --accent3-glow: rgba(255, 183, 77, 0.28);
  --warning: #FFD54A;
}}

html[data-theme="lavender"] {{
  --bg: #0A0820;
  --card: #16133A;
  --card2: #221C55;
  --border: #2F2870;
  --border2: #463C95;
  --text: #F0EBFF;
  --muted: #B0A6D9;
  --accent: #A78BFA;
  --accent-glow: rgba(167, 139, 250, 0.4);
  --accent2: #C4B5FD;
  --accent2-glow: rgba(196, 181, 253, 0.3);
  --accent3: #FF8FB3;
  --accent3-glow: rgba(255, 143, 179, 0.3);
  --warning: #FFD166;
}}

html[data-theme="arctic"] {{
  --bg: #F2F6FC;
  --card: #FFFFFF;
  --card2: #EBF0F7;
  --border: #D6DEE8;
  --border2: #B8C5D6;
  --text: #0F1A2A;
  --muted: #5A6B82;
  --accent: #2563EB;
  --accent-glow: rgba(37, 99, 235, 0.25);
  --accent2: #16A34A;
  --accent2-glow: rgba(22, 163, 74, 0.25);
  --accent3: #DB2777;
  --accent3-glow: rgba(219, 39, 119, 0.25);
  --warning: #D97706;
}}

/* Light-theme adjustments: use a tinted card-color glass header and lighter overlays */
html[data-theme="arctic"] .header {{ background: rgba(255, 255, 255, 0.78); border-bottom-color: var(--border); }}
html[data-theme="arctic"] .modal-back {{ background: rgba(15, 26, 42, 0.55); }}
html[data-theme="arctic"] .back-to-top {{ background: rgba(255, 255, 255, 0.95); color: var(--accent); }}
html[data-theme="arctic"] .hero-overlay {{
  background: linear-gradient(180deg, rgba(255,255,255,0.55) 0%, transparent 35%, transparent 55%, rgba(255,255,255,0.92) 100%);
}}
html[data-theme="arctic"] .hero-title {{ color: var(--text); text-shadow: 0 1px 0 rgba(255,255,255,0.6); }}

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
  gap: 8px;
  background: var(--card);
  border: 1px solid var(--border);
  padding: 5px;
  border-radius: 999px;
  flex-wrap: wrap;
}}

.theme-btn {{
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 2px solid var(--border2);
  cursor: pointer;
  display: grid;
  place-items: center;
  font-size: 14px;
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.25s ease;
  position: relative;
  flex-shrink: 0;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,0.04);
}}

.theme-btn:hover {{
  transform: scale(1.18);
  border-color: var(--text);
  box-shadow: 0 0 14px var(--accent-glow), inset 0 0 0 1px rgba(255,255,255,0.08);
}}

.theme-btn.active {{
  border-color: var(--text);
  box-shadow: 0 0 16px var(--accent-glow), inset 0 0 0 1px rgba(255,255,255,0.12);
  transform: scale(1.05);
}}

.theme-cyan    {{ background: linear-gradient(135deg, #070D1A 0%, #16213A 50%, #6BE7FF 100%); }}
.theme-pink    {{ background: linear-gradient(135deg, #120818 0%, #2B163B 50%, #FF60C8 100%); }}
.theme-oled    {{ background: linear-gradient(135deg, #000000 0%, #0D0D0D 50%, #00E676 100%); }}
.theme-amber   {{ background: linear-gradient(135deg, #150B04 0%, #3A2615 50%, #FFB74D 100%); }}
.theme-emerald {{ background: linear-gradient(135deg, #03110A 0%, #112E22 50%, #4DE69C 100%); }}
.theme-lavender{{ background: linear-gradient(135deg, #0A0820 0%, #221C55 50%, #A78BFA 100%); }}
.theme-arctic  {{ background: linear-gradient(135deg, #FFFFFF 0%, #D6DEE8 50%, #2563EB 100%); }}

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
  background: radial-gradient(circle at 50% 40%, var(--card2), var(--bg));
}}

.hero-img {{
  display: block;
  width: 100%;
  height: auto;
  max-height: 460px;
  object-fit: contain;
  object-position: center;
}}

.hero-overlay {{
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(7, 13, 26, 0.55) 0%, transparent 35%, transparent 55%, rgba(7, 13, 26, 0.92) 100%);
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 28px 36px;
  pointer-events: none;
}}

.hero-overlay > * {{ pointer-events: auto; }}

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
  .hero-img {{ max-height: 320px; }}
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

.tab-btn.active-mp {{
  background: rgba(167, 139, 250, 0.2);
  color: #A78BFA;
  font-weight: 900;
  border-color: #A78BFA;
  box-shadow: 0 4px 16px rgba(167, 139, 250, 0.25);
}}

.tab-btn.active-coop {{
  background: rgba(124, 255, 178, 0.2);
  color: var(--accent2);
  font-weight: 900;
  border-color: var(--accent2);
  box-shadow: 0 4px 16px var(--accent2-glow);
}}

html[data-theme="arctic"] .tab-btn.active-mp {{
  color: #7C3AED;
  border-color: #7C3AED;
  background: rgba(124, 58, 237, 0.12);
}}

/* Status Indicator Badges on Cards */
.status-tag {{
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 5;
  font-size: 10px;
  font-weight: 800;
  padding: 5px 11px;
  border-radius: 999px;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  box-shadow: 0 4px 14px rgba(0,0,0,0.55), 0 0 0 1px rgba(0,0,0,0.25);
  display: inline-flex;
  align-items: center;
  gap: 4px;
  letter-spacing: 0.02em;
  text-shadow: 0 1px 2px rgba(0,0,0,0.6);
}}

.status-completed {{
  background: rgba(8, 22, 16, 0.78);
  color: #7CFFB2;
  border: 1px solid rgba(124, 255, 178, 0.85);
}}

.status-in_progress {{
  background: rgba(7, 18, 30, 0.78);
  color: #6BE7FF;
  border: 1px solid rgba(107, 231, 255, 0.85);
}}

.status-planned {{
  background: rgba(28, 18, 4, 0.78);
  color: #FFC94A;
  border: 1px solid rgba(255, 184, 0, 0.85);
}}

.status-none {{
  background: rgba(20, 25, 35, 0.78);
  color: #B8C5D6;
  border: 1px solid rgba(184, 197, 214, 0.5);
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
  border-radius: 999px;
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
  border: 3px solid var(--bg);
  background: #FF3D3D;
  box-shadow: 0 0 10px #FF3D3D;
  transition: background 0.4s ease, box-shadow 0.4s ease;
}}

.status-indicator.live {{
  background: #00E676;
  box-shadow: 0 0 10px #00E676;
  animation: statusPulse 1.6s ease-in-out infinite;
}}

.status-indicator.unknown {{
  background: #8AA0BF;
  box-shadow: 0 0 8px rgba(138, 160, 191, 0.5);
}}

@keyframes statusPulse {{
  0%, 100% {{
    box-shadow: 0 0 10px #00E676, 0 0 0 0 rgba(0, 230, 118, 0.5);
  }}
  50% {{
    box-shadow: 0 0 14px #00E676, 0 0 0 8px rgba(0, 230, 118, 0);
  }}
}}

.profile-stream-status {{
  font-size: 11px;
  font-weight: 700;
  margin-top: 4px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 10px;
  border-radius: 999px;
  background: rgba(255, 61, 61, 0.14);
  border: 1px solid rgba(255, 61, 61, 0.32);
  color: #FF6363;
  transition: all 0.3s ease;
}}

.profile-stream-status.live {{
  background: rgba(0, 230, 118, 0.16);
  border-color: rgba(0, 230, 118, 0.4);
  color: #00E676;
}}

.profile-stream-status.unknown {{
  background: rgba(138, 160, 191, 0.14);
  border-color: rgba(138, 160, 191, 0.32);
  color: var(--muted);
}}

.profile-stream-status::before {{
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
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
.social-tw {{ grid-column: 1 / -1; background: linear-gradient(135deg, rgba(145, 70, 255, 0.18), rgba(169, 112, 255, 0.12)); border: 1px solid rgba(145, 70, 255, 0.4); color: #C9A6FF; font-weight: 800; }}
.social-tw.live {{ background: linear-gradient(135deg, rgba(0, 230, 118, 0.22), rgba(124, 255, 178, 0.16)); border-color: rgba(0, 230, 118, 0.5); color: #00E676; }}

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
  background: radial-gradient(circle at 50% 30%, var(--card2), #070D1A);
  display: grid;
  place-items: center;
}}

.card-cover .cover-bg {{
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: blur(28px) brightness(0.55) saturate(1.4);
  transform: scale(1.25);
  opacity: 0.9;
}}

.card-cover .cover-main {{
  position: absolute;
  inset: 0;
  z-index: 1;
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: center;
  transition: transform 0.4s ease;
  padding: 8px;
  box-sizing: border-box;
}}

.card-cover::after {{
  content: '';
  position: absolute;
  inset: 0;
  z-index: 2;
  pointer-events: none;
  background: linear-gradient(180deg, rgba(0,0,0,0.35) 0%, transparent 22%, transparent 75%, rgba(0,0,0,0.35) 100%);
}}

.card:hover .cover-main {{
  transform: scale(1.05);
}}

.cover-initials {{
  font-family: 'Nunito', sans-serif;
  font-size: 44px;
  font-weight: 900;
  color: var(--accent);
  opacity: 0.85;
  letter-spacing: -0.02em;
  text-shadow: 0 0 20px var(--accent-glow);
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
  gap: 14px;
  border-radius: 14px;
  position: relative;
}}

.grid.mode-list .card:hover {{
  transform: translateX(4px);
}}

.grid.mode-list .card-cover {{
  width: 56px;
  height: 76px;
  aspect-ratio: auto;
  border-radius: 10px;
  flex-shrink: 0;
  overflow: hidden;
}}

/* In list mode, use cover for the small thumbnail (crop is fine here) */
.grid.mode-list .cover-main {{
  padding: 0;
  object-fit: cover;
}}

.grid.mode-list .cover-bg {{
  display: none;
}}

.grid.mode-list .cover-initials {{
  font-size: 20px;
}}

/* Status tag in list mode: small inline pill, no absolute positioning */
.grid.mode-list .status-tag {{
  position: static;
  top: auto;
  left: auto;
  z-index: auto;
  font-size: 10px;
  padding: 3px 8px;
  letter-spacing: 0.02em;
  flex-shrink: 0;
  white-space: nowrap;
}}

.grid.mode-list .card-body {{
  padding: 0;
  background: transparent;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 12px;
  flex: 1;
  min-width: 0;
}}

.grid.mode-list .card-title {{
  min-height: auto;
  font-size: 15px;
  -webkit-line-clamp: 1;
  flex: 1;
  min-width: 0;
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

.modal-header-banner {{
  min-height: 220px;
  height: auto;
  position: relative;
  background: radial-gradient(circle at 50% 40%, var(--card2), var(--bg));
  display: grid;
  place-items: center;
  overflow: hidden;
  flex-shrink: 0;
  border-bottom: 1px solid var(--border);
  padding: 18px;
  box-sizing: border-box;
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

.modal-main-img {{
  position: relative;
  z-index: 1;
  display: block;
  max-width: 100%;
  max-height: 360px;
  width: auto;
  height: auto;
  object-fit: contain;
  object-position: center;
  border-radius: 14px;
  box-shadow: 0 12px 36px rgba(0,0,0,0.55);
}}

.modal-header-initials {{
  font-family: 'Nunito', sans-serif;
  font-size: 72px;
  font-weight: 900;
  color: var(--accent);
  text-shadow: 0 0 30px var(--accent-glow);
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

/* ===== Admin panel (hidden for guests) ===== */
.admin-fab {{
  position: fixed;
  bottom: 80px;
  right: 24px;
  width: 46px;
  height: 46px;
  border-radius: 50%;
  background: rgba(17, 26, 45, 0.92);
  border: 1px solid var(--accent3);
  color: var(--accent3);
  display: none;
  place-items: center;
  font-size: 20px;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
  z-index: 41;
  transition: transform 0.2s ease, background 0.2s ease;
}}
.admin-fab:hover {{ transform: scale(1.1) rotate(20deg); background: var(--accent3); color: #fff; }}
body.is-admin .admin-fab {{ display: grid; }}
html[data-theme="arctic"] .admin-fab {{ background: rgba(255,255,255,0.95); }}

.admin-modal {{
  width: min(820px, 100%);
  max-height: 88vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: linear-gradient(180deg, var(--card2), var(--card));
  border: 1px solid var(--border2);
  border-radius: 24px;
  box-shadow: 0 30px 90px rgba(0,0,0,0.7);
}}
.admin-modal-body {{ padding: 20px 24px; overflow-y: auto; flex: 1; }}
.admin-modal-header {{
  display: flex; align-items: center; justify-content: space-between; gap: 10px;
  padding: 18px 24px; border-bottom: 1px solid var(--border); flex-shrink: 0;
}}
.admin-modal-title {{ font-family: 'Nunito', sans-serif; font-weight: 900; font-size: 20px; }}
.admin-modal-actions {{ display: flex; gap: 8px; flex-wrap: wrap; }}

.admin-toolbar {{
  display: flex; gap: 10px; align-items: center; flex-wrap: wrap; margin-bottom: 16px;
  padding: 12px; background: var(--card2); border: 1px solid var(--border); border-radius: 14px;
}}
.admin-toolbar input {{
  flex: 1; min-width: 200px; height: 38px; padding: 0 14px; border-radius: 10px;
  background: var(--card); border: 1px solid var(--border); color: var(--text); font-size: 13px; outline: none;
}}
.admin-toolbar input:focus {{ border-color: var(--accent); }}

.admin-list {{ display: flex; flex-direction: column; gap: 6px; }}
.admin-row {{
  display: grid;
  grid-template-columns: 44px 1fr auto;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  transition: border-color 0.15s ease;
}}
.admin-row:hover {{ border-color: var(--accent); }}
.admin-row.has-override {{ border-color: var(--accent3); }}
.admin-row .admin-cover {{
  width: 44px; height: 58px; border-radius: 8px; object-fit: cover; background: var(--card2);
}}
.admin-row .admin-title {{
  font-weight: 700; font-size: 13px; line-height: 1.25;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}}
.admin-row .admin-controls {{ display: flex; gap: 5px; align-items: center; flex-wrap: wrap; justify-content: flex-end; }}
.admin-row .admin-controls .admin-flag {{
  display: inline-flex; align-items: center; gap: 4px; padding: 4px 8px; border-radius: 999px;
  background: var(--card2); border: 1px solid var(--border); color: var(--muted);
  font-size: 11px; font-weight: 700; cursor: pointer; user-select: none; transition: all 0.15s ease;
}}
.admin-row .admin-controls .admin-flag.on {{
  background: rgba(107, 231, 255, 0.18); color: var(--accent); border-color: var(--accent);
}}
.admin-row .admin-controls .admin-flag.mp.on {{ background: rgba(167,139,250,0.2); color: #A78BFA; border-color: #A78BFA; }}
.admin-row .admin-controls .admin-flag.coop.on {{ background: rgba(124,255,178,0.2); color: var(--accent2); border-color: var(--accent2); }}
.admin-row .admin-controls .admin-status {{
  height: 32px; padding: 0 10px; border-radius: 10px;
  background: var(--card2); border: 1px solid var(--border); color: var(--text);
  font-size: 12px; font-weight: 700; cursor: pointer; outline: none;
}}

.admin-prompt {{
  text-align: center; padding: 28px 20px;
  display: flex; flex-direction: column; gap: 14px; align-items: center;
}}
.admin-prompt p {{ color: var(--muted); font-size: 14px; }}
.admin-prompt input {{
  width: min(280px, 100%); height: 48px; padding: 0 16px; border-radius: 12px;
  background: var(--card); border: 1px solid var(--border); color: var(--text);
  font-size: 18px; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.4em;
  text-align: center; outline: none;
}}
.admin-prompt input:focus {{ border-color: var(--accent); box-shadow: 0 0 0 4px var(--accent-glow); }}
.admin-prompt .err {{ color: var(--accent3); font-size: 13px; font-weight: 700; min-height: 18px; }}

.admin-meta-info {{
  font-size: 11px; color: var(--muted); padding: 8px 12px; background: var(--card2);
  border: 1px solid var(--border); border-radius: 10px; margin-top: 12px;
}}
.admin-meta-info b {{ color: var(--accent); font-family: 'JetBrains Mono', monospace; }}
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
      <button class="theme-btn theme-amber" title="Amber Fire" onclick="setTheme('amber')"></button>
      <button class="theme-btn theme-emerald" title="Emerald Forest" onclick="setTheme('emerald')"></button>
      <button class="theme-btn theme-lavender" title="Lavender Dream" onclick="setTheme('lavender')"></button>
      <button class="theme-btn theme-arctic" title="Arctic Light" onclick="setTheme('arctic')"></button>
    </div>
  </div>
</header>

<div class="hero-container">
  <div class="hero-card">
    <img src="hero.jpg" alt="Mikkleo Games Header Banner" class="hero-img">
    <div class="hero-overlay">
      <h1 class="hero-title">Моя коллекция игр</h1>
      <p class="hero-subtitle">Каталог стримов, прохождений и игровых проектов MikkleoVT</p>
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
        <div id="streamIndicator" class="status-indicator" title="Статус стрима"></div>
      </div>
      <div>
        <div class="profile-name">MikkleoVT</div>
        <div style="font-size: 11px; color: var(--muted); margin-top: 2px;">Стример & Контент-мейкер</div>
        <div id="streamStatusText" class="profile-stream-status">Оффлайн</div>
      </div>

      <div class="social-grid">
        <a id="socialTwitchLink" href="https://www.twitch.tv/mikkleovt" target="_blank" class="social-link social-tw">
          <img src="https://cdn.simpleicons.org/twitch/C9A6FF" width="12" height="12" alt="">Twitch
        </a>
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
      <button onclick="setTab('gacha')" id="tab-gacha" class="tab-btn">💫 Гача</button>
      <button onclick="setTab('mp')" id="tab-mp" class="tab-btn">🕹️ MP</button>
      <button onclick="setTab('coop')" id="tab-coop" class="tab-btn">🤝 Coop</button>
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
    <div class="modal-header-banner" id="modalBanner">
      <button class="modal-close" id="modalClose">✕</button>
      <img id="modalImgBg" class="modal-cover-bg" alt="" style="display:none;">
      <img id="modalImgMain" class="modal-main-img" alt="" style="display:none;">
      <div id="modalInitials" class="modal-header-initials">MG</div>
    </div>
    <div class="modal-body">
      <h2 class="modal-title" id="modalTitle"></h2>
      <div class="modal-alt-title" id="modalAltTitle"></div>

      <div class="modal-badges" id="modalBadges"></div>

      <div class="modal-links">
        <a id="modalSteamLink" href="#" target="_blank" class="btn-action">🛒 Найти в Steam</a>
        <a id="modalYtLink" href="#" target="_blank" class="btn-action">🎬 Прохождение на YouTube</a>
        <button id="modalShareBtn" class="btn-action" style="background:rgba(107,231,255,0.15); color:var(--accent);">🔗 Поделиться ссылкой</button>
      </div>
    </div>
  </div>
</div>

<div id="toast" class="toast">Ссылка скопирована в буфер обмена!</div>

<!-- Floating Scroll to Top Button -->
<button id="backToTop" class="back-to-top" title="Наверх">↑</button>

<!-- Hidden admin floating button (visible only when admin is signed in) -->
<button id="adminFab" class="admin-fab" title="Админ-панель" onclick="openAdminPanel()">⚙</button>

<!-- Admin Modal -->
<div class="modal-back" id="adminBack">
  <div class="admin-modal">
    <div class="admin-modal-header">
      <div class="admin-modal-title">⚙️ Админ-панель стримера</div>
      <div class="admin-modal-actions">
        <button class="btn-action" style="height:36px; padding:0 14px; font-size:12px;" onclick="exportOverrides()">💾 Скачать JSON</button>
        <button class="btn-action" style="height:36px; padding:0 14px; font-size:12px; background:rgba(255,96,168,0.15); color:var(--accent3); border-color:rgba(255,96,168,0.3);" onclick="confirmReset()">🗑 Сброс</button>
        <button class="btn-action" style="height:36px; padding:0 14px; font-size:12px;" onclick="closeAdminPanel()">✕ Закрыть</button>
      </div>
    </div>
    <div class="admin-modal-body">
      <div id="adminContent"></div>
    </div>
  </div>
</div>

<script>
const GAMES = {games_json_updated};

const STATUS_MAP = {{
  'completed': {{ label: 'Пройдено', emoji: '✅', class: 'status-completed' }},
  'in_progress': {{ label: 'В процессе', emoji: '⏳', class: 'status-in_progress' }},
  'planned': {{ label: 'В планах', emoji: '📌', class: 'status-planned' }},
  'none': {{ label: 'Не начато', emoji: '🆕', class: 'status-none' }}
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

// ===== Local streamer edits (PIN-protected admin) =====
const STORAGE_KEY = 'mikkleo_streamer_overrides_v1';
const SESSION_KEY = 'mikkleo_admin_session';

function loadOverrides() {{
  try {{
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{{}}');
  }} catch (_) {{
    return {{}};
  }}
}}

function saveOverrides(map) {{
  try {{
    localStorage.setItem(STORAGE_KEY, JSON.stringify(map));
  }} catch (_) {{}}
}}

function isAdmin() {{
  try {{
    return sessionStorage.getItem(SESSION_KEY) === '1';
  }} catch (_) {{
    return false;
  }}
}}

function setAdmin(on) {{
  try {{
    if (on) sessionStorage.setItem(SESSION_KEY, '1');
    else sessionStorage.removeItem(SESSION_KEY);
  }} catch (_) {{}}
}}

function getEffectiveStatus(g) {{
  const overrides = loadOverrides();
  const o = overrides[g.id];
  if (o && Object.prototype.hasOwnProperty.call(o, 'status')) {{
    return o.status; // may be null
  }}
  return g.status || 'none';
}}

function getEffectiveFlag(g, flag) {{
  const overrides = loadOverrides();
  const o = overrides[g.id];
  if (o && Object.prototype.hasOwnProperty.call(o, flag)) {{
    return !!o[flag];
  }}
  return !!g[flag];
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
    out = out.filter(g => getEffectiveStatus(g) === 'completed');
  }} else if(currentTab === 'in_progress') {{
    out = out.filter(g => getEffectiveStatus(g) === 'in_progress');
  }} else if(currentTab === 'planned') {{
    out = out.filter(g => getEffectiveStatus(g) === 'planned');
  }} else if(currentTab === 'gacha') {{
    out = out.filter(g => getEffectiveFlag(g, 'isGacha'));
  }} else if(currentTab === 'mp') {{
    out = out.filter(g => getEffectiveFlag(g, 'isMultiplayer'));
  }} else if(currentTab === 'coop') {{
    out = out.filter(g => getEffectiveFlag(g, 'isCoop'));
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

  // Calculate Progress stats (use effective status so admin overrides are reflected)
  const completedCount = GAMES.filter(g => getEffectiveStatus(g) === 'completed').length;
  const inProgressCount = GAMES.filter(g => getEffectiveStatus(g) === 'in_progress').length;
  const plannedCount = GAMES.filter(g => getEffectiveStatus(g) === 'planned').length;
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

    const effStatus = getEffectiveStatus(g);
    const stInfo = STATUS_MAP[effStatus] || STATUS_MAP['none'];
    const initials = esc((g.title || 'Game').slice(0, 2).toUpperCase());

    const imgBlock = g.image 
      ? `<img class="cover-bg" src="${{esc(g.image)}}" loading="lazy">
         <img class="cover-main" src="${{esc(g.image)}}" loading="lazy" alt="${{esc(g.title)}}">` 
      : `<div class="cover-initials">${{initials}}</div>`;

    const mainGenre = g.genre ? g.genre.split(',')[0].trim() : 'Игра';

    const statusPill = `<span class="status-tag ${{stInfo.class}}">${{stInfo.emoji}} ${{stInfo.label}}</span>`;

    // (admin button next to title in list mode is rendered in the else branch)

    if(currentViewMode === 'list') {{
      // Compact list: cover is a small thumbnail, status pill is shown in the body so it isn't clipped by the cover's overflow
      el.innerHTML = `
        <div class="card-cover">
          ${{imgBlock}}
        </div>
        <div class="card-body">
          ${{statusPill}}
          <div class="card-title">${{esc(g.title)}}</div>
          <div class="card-meta">
            <span class="meta-tag accent">${{esc(mainGenre)}}</span>
            <span class="meta-tag">${{g.year}}</span>
          </div>
        </div>
      `;
    }} else {{
      el.innerHTML = `
        <div class="card-cover">
          ${{statusPill}}
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
    }}
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

  const initials = (g.title || 'Game').slice(0, 2).toUpperCase();
  const imgBg = document.getElementById('modalImgBg');
  const imgMain = document.getElementById('modalImgMain');
  const initialsEl = document.getElementById('modalInitials');

  if(g.image) {{
    imgBg.src = g.image; imgBg.style.display = 'block';
    imgMain.src = g.image; imgMain.style.display = 'block';
    initialsEl.style.display = 'none';
  }} else {{
    imgBg.style.display = 'none';
    imgMain.style.display = 'none';
    initialsEl.textContent = initials;
    initialsEl.style.display = 'block';
  }}

  const badges = document.getElementById('modalBadges');
  const effStatus = getEffectiveStatus(g);
  const stInfo = STATUS_MAP[effStatus] || STATUS_MAP['none'];

  badges.innerHTML = `
    <span class="status-tag ${{stInfo.class}}" style="position:static;">${{stInfo.emoji}} ${{stInfo.label}}</span>
    <span class="meta-tag accent">${{esc(g.genre)}}</span>
    <span class="meta-tag">Год: ${{g.year}}</span>
  `;

  // Action links
  // Steam: search with "Games" category filter (category1=998) for a more accurate game-only result
  const qTitle = encodeURIComponent(g.title);
  document.getElementById('modalSteamLink').href = `https://store.steampowered.com/search/?term=${{qTitle}}&category1=998`;

  // YouTube: search within @mikkleostream channel's playlists (прохождения) by appending the game title
  document.getElementById('modalYtLink').href = `https://www.youtube.com/@mikkleostream/playlists?query=${{qTitle}}`;

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

// ===== Admin Panel Logic =====
const ADMIN_PIN_KEY = 'mikkleo_admin_pin_hash_v1';

// Simple non-cryptographic hash for PIN (NOT for production security — this is a
// deterrent only since the data lives in the browser anyway).
function hashPin(pin) {{
  let h = 5381;
  for (let i = 0; i < pin.length; i++) {{
    h = ((h << 5) + h) + pin.charCodeAt(i);
    h = h & 0xFFFFFFFF;
  }}
  return 'h_' + (h >>> 0).toString(16);
}}

function getStoredPinHash() {{
  try {{ return localStorage.getItem(ADMIN_PIN_KEY); }} catch (_) {{ return null; }}
}}

function setStoredPinHash(h) {{
  try {{ localStorage.setItem(ADMIN_PIN_KEY, h); }} catch (_) {{}}
}}

function applyAdminVisibility() {{
  if (isAdmin()) document.body.classList.add('is-admin');
  else document.body.classList.remove('is-admin');
}}

function openAdminPanel() {{
  document.getElementById('adminBack').classList.add('open');
  document.body.style.overflow = 'hidden';
  renderAdminContent();
}}

function closeAdminPanel() {{
  document.getElementById('adminBack').classList.remove('open');
  document.body.style.overflow = '';
}}

function renderAdminContent() {{
  const root = document.getElementById('adminContent');
  if (!isAdmin()) {{
    root.innerHTML = renderAdminPrompt();
    const input = document.getElementById('adminPinInput');
    if (input) {{
      input.focus();
      input.addEventListener('keydown', (e) => {{ if (e.key === 'Enter') tryAdminLogin(); }});
    }}
    return;
  }}
  root.innerHTML = renderAdminList();
  const search = document.getElementById('adminSearch');
  if (search) {{
    search.addEventListener('input', () => {{
      const q = search.value.toLowerCase().trim();
      document.querySelectorAll('.admin-row').forEach(r => {{
        r.style.display = (!q || r.dataset.title.includes(q)) ? '' : 'none';
      }});
    }});
  }}
  // Attach change handlers to selects/checkboxes
  document.querySelectorAll('.admin-row').forEach(row => {{
    const id = row.dataset.id;
    const statusSel = row.querySelector('.admin-status');
    if (statusSel) {{
      statusSel.addEventListener('change', () => {{
        const v = statusSel.value;
        const overrides = loadOverrides();
        if (!overrides[id]) overrides[id] = {{}};
        if (v === '__default__') {{
          delete overrides[id].status;
        }} else {{
          overrides[id].status = v;
        }}
        saveOverrides(overrides);
        applyAdminVisibility();
        render();
        renderAdminContent();
      }});
    }}
    row.querySelectorAll('.admin-flag').forEach(btn => {{
      btn.addEventListener('click', () => {{
        const flag = btn.dataset.flag;
        const overrides = loadOverrides();
        if (!overrides[id]) overrides[id] = {{}};
        const current = getEffectiveFlag(GAMES.find(g => g.id === id), flag);
        if (overrides[id][flag] === undefined) {{
          // currently using default; toggling means setting the opposite
          overrides[id][flag] = !current;
          if (overrides[id][flag] === !!GAMES.find(g => g.id === id)[flag]) {{
            // back to default value — drop override
            delete overrides[id][flag];
          }}
        }} else {{
          overrides[id][flag] = !overrides[id][flag];
          if (overrides[id][flag] === !!GAMES.find(g => g.id === id)[flag]) delete overrides[id][flag];
        }}
        saveOverrides(overrides);
        render();
        renderAdminContent();
      }});
    }});
  }});
}}

function renderAdminPrompt() {{
  const hasPin = !!getStoredPinHash();
  return `
    <div class="admin-prompt">
      <div style="font-size: 36px;">🔐</div>
      <div style="font-weight:800; font-size:18px;">${{hasPin ? 'Введите PIN-код' : 'Задайте новый PIN-код'}}</div>
      <p>${{hasPin ? 'PIN хранится локально в этом браузере. 4–6 цифр.' : 'Придумайте 4–6 цифр. Этот PIN будет запрашиваться при открытии админки.'}}</p>
      <input id="adminPinInput" type="password" inputmode="numeric" pattern="[0-9]*" maxlength="6" placeholder="••••" autocomplete="off">
      <div class="err" id="adminPinErr"></div>
      <button class="btn-action" style="height:42px; padding:0 22px; font-size:13px; background:var(--accent); color:#04101A; border-color:var(--accent);" onclick="tryAdminLogin()">
        ${{hasPin ? 'Войти' : 'Задать PIN и войти'}}
      </button>
      ${{hasPin ? '<button class="btn-action" style="height:36px; padding:0 14px; font-size:12px; background:transparent; color:var(--muted); border-color:transparent;" onclick="forgetPin()">Забыли PIN? Сбросить</button>' : ''}}
    </div>
  `;
}}

function tryAdminLogin() {{
  const input = document.getElementById('adminPinInput');
  const err = document.getElementById('adminPinErr');
  const pin = (input?.value || '').trim();
  if (!/^\\d{{4,6}}$/.test(pin)) {{
    err.textContent = 'PIN должен быть 4–6 цифр';
    return;
  }}
  const stored = getStoredPinHash();
  const h = hashPin(pin);
  if (stored) {{
    if (stored === h) {{
      setAdmin(true);
      applyAdminVisibility();
      renderAdminContent();
    }} else {{
      err.textContent = 'Неверный PIN';
      input.value = '';
      input.focus();
    }}
  }} else {{
    setStoredPinHash(h);
    setAdmin(true);
    applyAdminVisibility();
    renderAdminContent();
  }}
}}

function forgetPin() {{
  if (!confirm('Сбросить PIN? Локальные правки статусов останутся.')) return;
  try {{ localStorage.removeItem(ADMIN_PIN_KEY); }} catch (_) {{}}
  setAdmin(false);
  applyAdminVisibility();
  renderAdminContent();
}}

function adminLogout() {{
  setAdmin(false);
  applyAdminVisibility();
  closeAdminPanel();
}}

function renderAdminList() {{
  const overrides = loadOverrides();
  const totalOverrides = Object.keys(overrides).length;
  const html = GAMES.map(g => {{
    const eff = getEffectiveStatus(g);
    const gachaOn = getEffectiveFlag(g, 'isGacha');
    const mpOn = getEffectiveFlag(g, 'isMultiplayer');
    const coopOn = getEffectiveFlag(g, 'isCoop');
    const isOverridden = !!overrides[g.id];
    return `
      <div class="admin-row ${{isOverridden ? 'has-override' : ''}}" data-id="${{esc(g.id)}}" data-title="${{esc((g.title||'').toLowerCase())}}">
        <img class="admin-cover" src="${{esc(g.image||'')}}" alt="" onerror="this.style.visibility='hidden'">
        <div>
          <div class="admin-title">${{esc(g.title||'Без названия')}}</div>
          <div style="font-size:11px; color:var(--muted); margin-top:2px;">${{esc(g.genre||'')}} · ${{g.year||''}}</div>
        </div>
        <div class="admin-controls">
          <button class="admin-flag ${{gachaOn ? 'on' : ''}}" data-flag="isGacha" title="Гача">💫</button>
          <button class="admin-flag mp ${{mpOn ? 'on' : ''}}" data-flag="isMultiplayer" title="Мультиплеер">🕹️</button>
          <button class="admin-flag coop ${{coopOn ? 'on' : ''}}" data-flag="isCoop" title="Кооп">🤝</button>
          <select class="admin-status" title="Статус">
            <option value="__default__" ${{!isOverridden || overrides[g.id].status === undefined ? 'selected' : ''}}>— дефолт —</option>
            <option value="in_progress" ${{eff === 'in_progress' && (isOverridden && overrides[g.id].status !== undefined) ? 'selected' : ''}}>⏳ В процессе</option>
            <option value="completed" ${{eff === 'completed' && (isOverridden && overrides[g.id].status !== undefined) ? 'selected' : ''}}>✅ Пройдено</option>
            <option value="planned" ${{eff === 'planned' && (isOverridden && overrides[g.id].status !== undefined) ? 'selected' : ''}}>📌 В планах</option>
            <option value="none" ${{eff === 'none' && (isOverridden && overrides[g.id].status !== undefined) ? 'selected' : ''}}>🆕 Не начато</option>
          </select>
        </div>
      </div>
    `;
  }}).join('');
  return `
    <div class="admin-toolbar">
      <input id="adminSearch" type="text" placeholder="🔍 Поиск по названию..." autocomplete="off">
      <button class="btn-action" style="height:36px; padding:0 14px; font-size:12px; background:transparent; color:var(--muted);" onclick="adminLogout()">🚪 Выйти</button>
    </div>
    <div class="admin-list">${{html}}</div>
    <div class="admin-meta-info">
      Локальных правок: <b>${{totalOverrides}}</b>. Правки хранятся только в этом браузере.
      Скачайте JSON, чтобы перенести на другое устройство.
    </div>
  `;
}}

function exportOverrides() {{
  const data = loadOverrides();
  const blob = new Blob([JSON.stringify(data, null, 2)], {{ type: 'application/json' }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'mikkleo-overrides.json';
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  showToast('Файл сохранён в загрузках');
}}

function confirmReset() {{
  if (!confirm('Удалить ВСЕ локальные правки? Это необратимо.')) return;
  try {{ localStorage.removeItem(STORAGE_KEY); }} catch (_) {{}}
  render();
  renderAdminContent();
  showToast('Локальные правки сброшены');
}}

// Hidden trigger: Ctrl+Shift+A opens admin panel
document.addEventListener('keydown', (e) => {{
  if (e.ctrlKey && e.shiftKey && (e.key === 'A' || e.key === 'a' || e.key === 'Ф' || e.key === 'ф')) {{
    e.preventDefault();
    openAdminPanel();
  }}
  if (e.key === 'Escape' && document.getElementById('adminBack').classList.contains('open')) {{
    closeAdminPanel();
  }}
}});

document.getElementById('adminBack').addEventListener('click', (e) => {{
  if (e.target.id === 'adminBack') closeAdminPanel();
}});

// Initialize
const savedTheme = localStorage.getItem('mikkleo_theme') || 'cyan';
setTheme(savedTheme);
setViewMode(currentViewMode);
applyAdminVisibility();

// Twitch Stream Status Indicator
const TWITCH_CHANNEL = 'mikkleovt';
const TWITCH_UPTIME_URL = `https://decapi.me/twitch/uptime/${{TWITCH_CHANNEL}}`;
const TWITCH_CHECK_INTERVAL = 60 * 1000; // 1 minute
const STREAM_CACHE_TTL = 5 * 60 * 1000;  // remember result for 5 min between reloads

const streamIndicator = document.getElementById('streamIndicator');
const streamStatusText = document.getElementById('streamStatusText');
const socialTwitchLink = document.getElementById('socialTwitchLink');

function applyStreamState(state) {{
  // state: 'live' | 'offline' | 'unknown'
  if (!streamIndicator || !streamStatusText) return;

  streamIndicator.classList.remove('live', 'unknown');
  streamStatusText.classList.remove('live', 'unknown');

  if (state === 'live') {{
    streamIndicator.classList.add('live');
    streamStatusText.classList.add('live');
    streamIndicator.title = 'Стрим сейчас в эфире на Twitch';
    streamStatusText.textContent = '🔴 В эфире';
    if (socialTwitchLink) {{
      socialTwitchLink.classList.add('live');
      socialTwitchLink.title = 'MikkleoVT сейчас стримит — нажмите, чтобы смотреть';
    }}
  }} else if (state === 'offline') {{
    streamIndicator.title = 'Стрим оффлайн';
    streamStatusText.textContent = 'Оффлайн';
    if (socialTwitchLink) {{
      socialTwitchLink.classList.remove('live');
      socialTwitchLink.title = 'Открыть канал MikkleoVT на Twitch';
    }}
  }} else {{
    streamIndicator.classList.add('unknown');
    streamStatusText.classList.add('unknown');
    streamIndicator.title = 'Не удалось проверить статус стрима';
    streamStatusText.textContent = 'Статус неизвестен';
    if (socialTwitchLink) {{
      socialTwitchLink.classList.remove('live');
    }}
  }}
}}

async function checkTwitchStatus() {{
  // Try to use cached state from previous recent visit
  try {{
    const cached = JSON.parse(localStorage.getItem('mikkleo_stream_cache') || 'null');
    if (cached && (Date.now() - cached.ts) < STREAM_CACHE_TTL) {{
      applyStreamState(cached.state);
    }}
  }} catch (_) {{}}

  try {{
    const controller = (typeof AbortController !== 'undefined') ? new AbortController() : null;
    const timeoutId = controller ? setTimeout(() => controller.abort(), 8000) : null;

    const fetchOpts = controller ? {{ signal: controller.signal, cache: 'no-store' }} : {{ cache: 'no-store' }};
    const resp = await fetch(TWITCH_UPTIME_URL, fetchOpts);
    if (timeoutId) clearTimeout(timeoutId);

    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    const text = (await resp.text()).trim().toLowerCase();

    let state;
    if (text.includes('offline') || text.includes('not live') || text.includes('канал не найден') || text.includes('channel not found')) {{
      state = 'offline';
    }} else if (text.includes('live') || text.includes('эфире') || text.includes('live for') || text.includes('uptime')) {{
      state = 'live';
    }} else if (text.length === 0) {{
      state = 'unknown';
    }} else {{
      // Unknown payload — be safe and treat as unknown rather than wrong state
      state = 'unknown';
    }}

    applyStreamState(state);
    try {{
      localStorage.setItem('mikkleo_stream_cache', JSON.stringify({{ state, ts: Date.now() }}));
    }} catch (_) {{}}
  }} catch (err) {{
    // Network error / timeout / CORS — keep current visual state, but if no cache was applied, mark as unknown
    if (streamIndicator && !streamIndicator.classList.contains('live')) {{
      try {{
        const cached = JSON.parse(localStorage.getItem('mikkleo_stream_cache') || 'null');
        if (!cached) applyStreamState('unknown');
      }} catch (_) {{
        applyStreamState('unknown');
      }}
    }}
  }}
}}

applyStreamState('unknown'); // start as offline-red until confirmed
checkTwitchStatus();
setInterval(checkTwitchStatus, TWITCH_CHECK_INTERVAL);
document.addEventListener('visibilitychange', () => {{
  if (!document.hidden) checkTwitchStatus();
}});

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

if __name__ == '__main__':
    rebuild_index()
    print("index.html rebuilt.")
