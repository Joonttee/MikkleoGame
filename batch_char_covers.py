#!/usr/bin/env python3
"""Batch update GAMES array to use character covers and generate prompts."""
import re, json, os

with open('index.html') as f:
    content = f.read()

match = re.search(r'const GAMES = (\[.*?\]);', content, re.DOTALL)
if not match:
    print('No GAMES array found')
    exit(1)

games = json.loads(match.group(1))
ref_char = "anime girl with long blue hair, white cat ears, heterochromia eyes (one bright blue, one bright green), wearing white shirt"

for g in games:
    prompt = f"Character art in the style of \"{g['title']}\" game ({g['genre']}): {ref_char}, digital illustration, colorful, high detail"
    # Save prompt for manual/automated generation
    prompt_path = f"prompts/{g['id']}.txt"
    os.makedirs('prompts', exist_ok=True)
    with open(prompt_path, 'w') as pf:
        pf.write(prompt)
    # Update image reference to character cover
    g['image'] = f"char-cover-{g['id']}.jpg"

updated_json = json.dumps(games, ensure_ascii=False)
content = content.replace(match.group(1), updated_json)

with open('index.html', 'w') as f:
    f.write(content)

print(f'Updated {len(games)} games with character cover references.')
print('Prompts saved in prompts/ folder.')
