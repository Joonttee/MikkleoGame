import json
import re

INDEX_FILE = 'index.html'

with open(INDEX_FILE, 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'const GAMES = (\[.*?\]);', text, re.DOTALL)
if not m:
    raise Exception("Could not find const GAMES in index.html")

games_json = m.group(1)
games_list = json.loads(games_json)
games_count = len(games_list)

new_html = f"""<!DOCTYPE html>
<html lang="ru">
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
:root {{
  --bg: #070D1A;
  --card: #111A2D;
  --card2: #16213A;
  --card-hover: #1A2846;
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
  --warning: #FF9500;
  --r2: 22px;
}}

* {{ margin:0; padding:0; box-sizing:border-box; }}

body {{
  background: var(--bg);
  color: var(--text);
  font-family: 'Manrope', system-ui, -apple-system, sans-serif;
  min-height: 100vh;
  overflow-x: hidden;
  line-height: 1.5;
}}

body::before {{
  content: '';
  position: fixed;
  inset: 0;
  background: 
    radial-gradient(900px 600px at 18% -5%, rgba(107, 231, 255, 0.18), transparent 65%),
    radial-gradient(700px 500px at 90% 5%, rgba(124, 255, 178, 0.12), transparent 60%),
    radial-gradient(800px 600px at 50% 115%, rgba(138, 180, 255, 0.14), transparent 70%);
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
  background: linear-gradient(135deg, var(--accent), #8AB4FF);
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
  box-shadow: 0 0 0 4px rgba(107, 231, 255, 0.15);
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

.header-actions {{
  display: flex;
  align-items: center;
  gap: 12px;
}}

.btn-roulette {{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 42px;
  padding: 0 18px;
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(255, 96, 168, 0.2), rgba(107, 231, 255, 0.2));
  border: 1px solid rgba(255, 96, 168, 0.4);
  color: #fff;
  font-weight: 800;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 16px rgba(255, 96, 168, 0.15);
}}

.btn-roulette:hover {{
  transform: translateY(-2px);
  background: linear-gradient(135deg, var(--accent3), var(--accent));
  color: #04101A;
  box-shadow: 0 6px 20px rgba(255, 96, 168, 0.35);
}}

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
  background: linear-gradient(180deg, rgba(7, 13, 26, 0.2) 0%, rgba(7, 13, 26, 0.95) 90%);
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
  border-color: rgba(107, 231, 255, 0.4);
  color: var(--text);
}}

.tab-btn.active-all {{
  background: linear-gradient(135deg, var(--accent), #8AB4FF);
  color: #04101A;
  font-weight: 900;
  border-color: rgba(107, 231, 255, 0.6);
  box-shadow: 0 4px 16px var(--accent-glow);
}}

.tab-btn.active-done {{
  background: rgba(124, 255, 178, 0.2);
  color: var(--accent2);
  font-weight: 900;
  border-color: rgba(124, 255, 178, 0.6);
  box-shadow: 0 4px 16px var(--accent2-glow);
}}

.tab-btn.active-gacha {{
  background: rgba(255, 96, 168, 0.2);
  color: var(--accent3);
  font-weight: 900;
  border-color: rgba(255, 96, 168, 0.6);
  box-shadow: 0 4px 16px var(--accent3-glow);
}}

.tab-btn.active-fav {{
  background: rgba(255, 149, 0, 0.2);
  color: var(--warning);
  font-weight: 900;
  border-color: rgba(255, 149, 0, 0.6);
  box-shadow: 0 4px 16px rgba(255, 149, 0, 0.25);
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
  border: 3px solid rgba(107, 231, 255, 0.6);
  box-shadow: 0 10px 28px rgba(107, 231, 255, 0.3);
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

/* Card Grid */
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
  border-color: rgba(107, 231, 255, 0.45);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.45), 0 0 20px rgba(107, 231, 255, 0.15);
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

/* Card Badges */
.card-platform-badge {{
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 4;
  font-size: 10px;
  font-weight: 800;
  padding: 4px 9px;
  border-radius: 999px;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  text-transform: uppercase;
  letter-spacing: 0.02em;
}}

.platform-steamepic {{ background: rgba(27, 40, 56, 0.85); color: #66C0F4; border: 1px solid rgba(102, 192, 244, 0.4); }}
.platform-switch {{ background: rgba(230, 0, 18, 0.85); color: #FFF; border: 1px solid rgba(255, 255, 255, 0.3); }}
.platform-hoyoplay {{ background: rgba(155, 81, 224, 0.85); color: #FFF; border: 1px solid rgba(255, 255, 255, 0.3); }}
.platform-ubisoft {{ background: rgba(0, 112, 209, 0.85); color: #FFF; border: 1px solid rgba(255, 255, 255, 0.3); }}

.card-rating-badge {{
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 4;
  font-size: 10px;
  font-weight: 800;
  padding: 4px 8px;
  border-radius: 999px;
  background: rgba(7, 13, 26, 0.85);
  color: #FFD700;
  border: 1px solid rgba(255, 215, 0, 0.3);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  gap: 3px;
}}

.card-fav-btn {{
  position: absolute;
  bottom: 12px;
  right: 12px;
  z-index: 5;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(7, 13, 26, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: var(--muted);
  display: grid;
  place-items: center;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}}

.card-fav-btn:hover, .card-fav-btn.active {{
  background: var(--warning);
  color: #04101A;
  border-color: var(--warning);
  transform: scale(1.1);
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
  box-shadow: 0 30px 90px rgba(0, 0, 0, 0.7), 0 0 40px rgba(107, 231, 255, 0.1);
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

/* Roulette Modal */
.roulette-box {{
  padding: 30px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
}}

.roulette-slot {{
  width: 100%;
  max-width: 320px;
  aspect-ratio: 3/4;
  border-radius: 20px;
  overflow: hidden;
  position: relative;
  border: 3px solid var(--accent);
  box-shadow: 0 0 30px var(--accent-glow);
  background: #0A1020;
}}

.roulette-slot img {{
  width: 100%;
  height: 100%;
  object-fit: cover;
}}

/* Floating Back-To-Top */
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

    <div class="header-actions">
      <button class="btn-roulette" onclick="openRandomModal()">
        <span>🎰</span>
        <span>Рулетка игр</span>
      </button>
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
        <div class="badge-stat">💻 Steam/Epic: <strong id="heroStatSteam">0</strong></div>
        <div class="badge-stat">🔴 Switch: <strong id="heroStatSwitch">0</strong></div>
        <div class="badge-stat">💫 HoYoPlay / Гача: <strong id="heroStatGacha">0</strong></div>
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

    <div class="stats-card">
      <div style="font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted);">Статистика</div>
      <div class="stat-row">
        <span>Всего в коллекции</span>
        <span class="stat-val highlight" id="statTotal">0</span>
      </div>
      <div class="stat-row">
        <span>Найдено</span>
        <span class="stat-val" id="statFiltered">0</span>
      </div>
      <div class="stat-row">
        <span>В Избранном</span>
        <span class="stat-val" id="statFavCount" style="color:var(--warning);">0</span>
      </div>
    </div>
  </aside>

  <main>
    <!-- Status Tabs -->
    <div class="tabs-bar">
      <button onclick="setTab('all')" id="tab-all" class="tab-btn active-all">🎮 Все игры</button>
      <button onclick="setTab('done')" id="tab-done" class="tab-btn">✅ Пройдены</button>
      <button onclick="setTab('gacha')" id="tab-gacha" class="tab-btn">💫 Гача & F2P</button>
      <button onclick="setTab('favorites')" id="tab-favorites" class="tab-btn">⭐ Избранное (<span id="tabFavBadge">0</span>)</button>
    </div>

    <!-- Filter Bar -->
    <div class="controls-bar">
      <div class="filter-group">
        <select id="platformSelect" class="select-custom" onchange="applyFilters()">
          <option value="all">Все платформы</option>
          <option value="Steam/Epic">Steam / Epic</option>
          <option value="Switch">Nintendo Switch</option>
          <option value="HoYoPlay">HoYoPlay (Genshin/StarRail)</option>
          <option value="Ubisoft">Ubisoft Connect</option>
        </select>

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

        <button id="btnResetFilters" class="btn-reset-filters" style="display:none;" onclick="resetAllFilters()">
          <span>✕</span> Сбросить фильтры
        </button>
      </div>

      <div>
        <select id="sortSelect" class="select-custom" onchange="applyFilters()">
          <option value="title-asc">Название (А → Я)</option>
          <option value="title-desc">Название (Я → А)</option>
          <option value="year-desc">Год выхода (Сначала новые)</option>
          <option value="year-asc">Год выхода (Сначала старые)</option>
        </select>
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
        <button id="modalFavBtn" class="btn-action" style="background:rgba(255,149,0,0.15); color:var(--warning); border-color:rgba(255,149,0,0.3)">⭐ В избранное</button>
      </div>
    </div>
  </div>
</div>

<!-- Random Roulette Modal -->
<div class="modal-back" id="rouletteBack">
  <div class="modal" style="max-width:480px;">
    <div class="modal-body roulette-box">
      <h2 style="font-family:'Nunito'; font-size:24px; font-weight:900;">🎰 Рулетка случайной игры</h2>
      <p style="font-size:13px; color:var(--muted)">Случайный выбор из текущего списка (<span id="rouletteTotalCount">{games_count}</span> доступно)</p>

      <div class="roulette-slot" id="rouletteSlot">
        <img id="rouletteImg" src="" alt="Game Slot">
      </div>

      <h3 id="rouletteTitle" style="font-family:'Nunito'; font-size:20px; font-weight:800; min-height:48px;">Крути рулетку!</h3>

      <div style="display:flex; gap:10px; width:100%; justify-content:center;">
        <button class="btn-roulette" style="height:44px;" onclick="spinRandomGame()">🎲 Скрутить еще раз</button>
        <button class="btn-action" onclick="closeRandomModal()">Закрыть</button>
      </div>
    </div>
  </div>
</div>

<!-- Floating Scroll to Top Button -->
<button id="backToTop" class="back-to-top" title="Наверх">↑</button>

<script>
const GAMES = {games_json};

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

// Favorites in LocalStorage
let favorites = new Set(JSON.parse(localStorage.getItem('mikkleo_favorites') || '[]'));

function saveFavorites() {{
  localStorage.setItem('mikkleo_favorites', JSON.stringify(Array.from(favorites)));
  updateFavCounters();
}}

function toggleFavorite(id, e) {{
  if(e) e.stopPropagation();
  if(favorites.has(id)) favorites.delete(id);
  else favorites.add(id);
  saveFavorites();
  applyFilters();
}}

function updateFavCounters() {{
  const count = favorites.size;
  const badge = document.getElementById('tabFavBadge');
  const stat = document.getElementById('statFavCount');
  if(badge) badge.textContent = count;
  if(stat) stat.textContent = count;
}}

let filtered = [...GAMES];
let currentTab = 'all';
let visibleCount = 72;
let active = {{ search: "", platform: "all", genre: "all", sort: "title-asc" }};

function esc(s){{ return String(s || '').replace(/[&<>"']/g,m=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}}[m]); }}

function setTab(tab){{
  currentTab = tab;
  document.querySelectorAll('.tab-btn').forEach(b => {{
    b.className = 'tab-btn';
  }});

  const btn = document.getElementById('tab-' + tab);
  if(btn) {{
    btn.className = 'tab-btn active-' + (tab === 'favorites' ? 'fav' : tab);
  }}
  visibleCount = 72;
  applyFilters();
}}

function resetAllFilters() {{
  currentTab = 'all';
  active = {{ search: "", platform: "all", genre: "all", sort: "title-asc" }};
  document.getElementById('searchInput').value = '';
  document.getElementById('platformSelect').value = 'all';
  document.getElementById('genreSelect').value = 'all';
  document.getElementById('sortSelect').value = 'title-asc';
  document.getElementById('searchClear').style.display = 'none';
  setTab('all');
}}

function applyFilters() {{
  let out = [...GAMES];

  // Apply tab filter
  if(currentTab === 'done') {{
    out = out.filter(g => g.platform === 'Steam/Epic');
  }} else if(currentTab === 'gacha') {{
    out = out.filter(g => g.platform === 'HoYoPlay' || (g.genre && (g.genre.includes('Free To Play') || g.genre.includes('Бесплатные'))));
  }} else if(currentTab === 'favorites') {{
    out = out.filter(g => favorites.has(g.id));
  }}

  // Platform Filter
  const pFilter = document.getElementById('platformSelect').value;
  if(pFilter && pFilter !== 'all') {{
    out = out.filter(g => g.platform === pFilter);
  }}

  // Genre Filter
  const gFilter = document.getElementById('genreSelect').value;
  if(gFilter && gFilter !== 'all') {{
    out = out.filter(g => g.genre && g.genre.toLowerCase().includes(gFilter.toLowerCase()));
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
  const hasActiveFilters = q || pFilter !== 'all' || gFilter !== 'all' || currentTab !== 'all';
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

  // Stats updates
  const st = document.getElementById('statTotal'); if(st) st.textContent = GAMES.length;
  const sf = document.getElementById('statFiltered'); if(sf) sf.textContent = filtered.length;
  const ht = document.getElementById('heroStatTotal'); if(ht) ht.textContent = GAMES.length;
  const hs = document.getElementById('heroStatSteam'); if(hs) hs.textContent = GAMES.filter(g=>g.platform==='Steam/Epic').length;
  const hsw = document.getElementById('heroStatSwitch'); if(hsw) hsw.textContent = GAMES.filter(g=>g.platform==='Switch').length;
  const hg = document.getElementById('heroStatGacha'); if(hg) hg.textContent = GAMES.filter(g=>g.platform==='HoYoPlay' || (g.genre && g.genre.includes('Free To Play'))).length;

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

    const isFav = favorites.has(g.id);
    const platformClass = 'platform-' + (g.platform || 'steam').toLowerCase().replace('/', '');

    const imgBlock = g.image 
      ? `<img class="cover-bg" src="${{esc(g.image)}}" loading="lazy">
         <img class="cover-main" src="${{esc(g.image)}}" loading="lazy" alt="${{esc(g.title)}}">` 
      : `<div style="display:grid; place-items:center; height:100%; font-family:'Nunito'; font-size:48px; color:var(--accent); font-weight:900;">${{esc(g.title.slice(0,2).toUpperCase())}}</div>`;

    const mainGenre = g.genre ? g.genre.split(',')[0].trim() : 'Игра';

    el.innerHTML = `
      <div class="card-cover">
        <span class="card-platform-badge ${{platformClass}}">${{esc(g.platform)}}</span>
        <span class="card-rating-badge">★ ${{g.rating || 80}}</span>
        <button class="card-fav-btn ${{isFav ? 'active' : ''}}" onclick="toggleFavorite('${{g.id}}', event)" title="В избранное">
          ${{isFav ? '★' : '☆'}}
        </button>
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
      <button class="btn-roulette" style="height:46px; padding:0 32px; font-size:14px; background:linear-gradient(135deg, var(--accent), #8AB4FF); color:#04101A;" onclick="visibleCount+=72; render();">
        Показать ещё 72 (Показано ${{visibleCount}} из ${{filtered.length}})
      </button>
    `;
    grid.appendChild(more);
  }}
}}

// Modal Logic
let currentModalGame = null;

function openModal(g) {{
  currentModalGame = g;
  document.getElementById('modalTitle').textContent = g.title;
  document.getElementById('modalAltTitle').textContent = g.altTitle ? 'Альтернативное название: ' + g.altTitle : '';

  const imgBg = document.getElementById('modalImgBg');
  const imgMain = document.getElementById('modalImgMain');
  imgBg.src = g.image || '';
  imgMain.src = g.image || '';

  const badges = document.getElementById('modalBadges');
  const platformClass = 'platform-' + (g.platform || 'steam').toLowerCase().replace('/', '');

  badges.innerHTML = `
    <span class="card-platform-badge ${{platformClass}}" style="position:static;">${{esc(g.platform)}}</span>
    <span class="meta-tag accent">${{esc(g.genre)}}</span>
    <span class="meta-tag">Год: ${{g.year}}</span>
    <span class="meta-tag" style="color:#FFD700;">★ Оценка: ${{g.rating || 80}}/100</span>
  `;

  // Action links
  const qTitle = encodeURIComponent(g.title);
  document.getElementById('modalSteamLink').href = `https://store.steampowered.com/search/?term=${{qTitle}}`;
  document.getElementById('modalYtLink').href = `https://www.youtube.com/results?search_query=${{qTitle}}+gameplay`;
  document.getElementById('modalTwitchLink').href = `https://www.twitch.tv/search?term=${{qTitle}}`;

  const favBtn = document.getElementById('modalFavBtn');
  const isFav = favorites.has(g.id);
  favBtn.innerHTML = isFav ? '★ В избранном' : '⭐ В избранное';
  favBtn.onclick = () => {{
    toggleFavorite(g.id);
    openModal(g);
  }};

  document.getElementById('modalBack').classList.add('open');
  document.body.style.overflow = 'hidden';
}}

function closeModal() {{
  document.getElementById('modalBack').classList.remove('open');
  document.body.style.overflow = '';
}}

// Roulette Logic
let rouletteInterval = null;

function openRandomModal() {{
  if(!filtered.length) return;
  const rouletteCount = document.getElementById('rouletteTotalCount');
  if(rouletteCount) rouletteCount.textContent = filtered.length;
  document.getElementById('rouletteBack').classList.add('open');
  document.body.style.overflow = 'hidden';
  spinRandomGame();
}}

function spinRandomGame() {{
  if(!filtered.length) return;
  if(rouletteInterval) clearInterval(rouletteInterval);

  let count = 0;
  const img = document.getElementById('rouletteImg');
  const title = document.getElementById('rouletteTitle');

  rouletteInterval = setInterval(() => {{
    const rand = filtered[Math.floor(Math.random() * filtered.length)];
    img.src = rand.image || '';
    title.textContent = rand.title;
    count++;

    if(count > 18) {{
      clearInterval(rouletteInterval);
      const finalGame = filtered[Math.floor(Math.random() * filtered.length)];
      img.src = finalGame.image || '';
      title.textContent = finalGame.title;
    }}
  }}, 80);
}}

function closeRandomModal() {{
  if(rouletteInterval) clearInterval(rouletteInterval);
  document.getElementById('rouletteBack').classList.remove('open');
  document.body.style.overflow = '';
}}

// Event Listeners
document.getElementById('modalBack').addEventListener('click', e => {{
  if(e.target.id === 'modalBack') closeModal();
}});
document.getElementById('modalClose').onclick = closeModal;

document.getElementById('rouletteBack').addEventListener('click', e => {{
  if(e.target.id === 'rouletteBack') closeRandomModal();
}});

document.addEventListener('keydown', e => {{
  if(e.key === 'Escape') {{
    closeModal();
    closeRandomModal();
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
updateFavCounters();
applyFilters();
</script>
</body>
</html>
"""

with open(INDEX_FILE, 'w', encoding='utf-8') as f:
    f.write(new_html)

print("index.html regenerated.")
