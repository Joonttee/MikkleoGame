#!/usr/bin/env python3
"""
Batch script: generate character-style covers for all 827 games.
Reference: anime girl with long BLUE hair, BLUE cat ears (matching hair),
heterochromia eyes (bright blue + bright green), wearing white shirt.
Uses game title + genre for exact style matching.
Creates prompts, updates index.html references, skips existing images.
Also writes batch_commands.txt for manual/automated image generation.
"""
import re, json, os, sys

INDEX_FILE = 'index.html'
PROMPTS_DIR = 'prompts'
REF_IMAGE = 'char-cover-ref.jpg'

with open(INDEX_FILE) as f:
    content = f.read()

match = re.search(r'const GAMES = (\[.*?\]);', content, re.DOTALL)
if not match:
    print('No GAMES array found')
    sys.exit(1)

games = json.loads(match.group(1))
ref_char = (
    "anime girl with long BLUE hair, BLUE cat ears matching hair exactly, "
    "heterochromia eyes (one bright blue, one bright green), wearing white shirt"
)

os.makedirs(PROMPTS_DIR, exist_ok=True)
generated = 0
skipped = 0
batch_lines = []

for g in games:
    cover_name = f"char-cover-{g['id']}.jpg"
    cover_path = cover_name
    prompt_path = f"{PROMPTS_DIR}/{g['id']}.txt"
    prompt = (
        f"Character art in the exact visual style of \"{g['title']}\" game ({g['genre']}): "
        f"{ref_char}, digital illustration, colorful, high detail, matching the game's art direction"
    )

    # Write/update prompt
    with open(prompt_path, 'w') as pf:
        pf.write(prompt)

    # Skip if cover already exists
    if os.path.exists(cover_path):
        skipped += 1
        continue

    # Update array reference
    g['image'] = cover_name
    generated += 1

    # Add batch command line
    batch_lines.append(
        f"generate_image -f \"{cover_path}\" -i \"{REF_IMAGE}\" -p \"{prompt}\""
    )

# Write batch commands file
with open('batch_commands.txt', 'w') as bf:
    bf.write('# Batch generation commands (run line by line or in batches)\n')
    for line in batch_lines:
        bf.write(line + '\n')

# Update index.html array
updated_json = json.dumps(games, ensure_ascii=False)
content = content.replace(match.group(1), updated_json)

with open(INDEX_FILE, 'w') as f:
    f.write(content)

print(f'Games in array: {len(games)}')
print(f'Covers already exist: {skipped}')
print(f'Missing covers to generate: {generated}')
print(f'Batch commands written: batch_commands.txt')
print(f'Prompts updated: {PROMPTS_DIR}/')
print(f'Reference: {REF_IMAGE}')
