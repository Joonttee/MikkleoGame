#!/usr/bin/env python3
"""
Sync script: automatically matches newly uploaded image files
with game titles in index.html/GAMES data and updates cover image paths.
"""
import os, glob, re, json

INDEX_FILE = 'index.html'

def normalize_name(s):
    # Remove extensions, special characters, extra spaces, and convert to lower
    s = re.sub(r'\.(jpg|jpeg|png|webp)$', '', s, flags=re.IGNORECASE)
    s = re.sub(r'[^a-zA-Z0-9а-яА-ЯёЁ]', '', s)
    return s.lower()

def main():
    if not os.path.exists(INDEX_FILE):
        print("index.html not found!")
        return

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    m = re.search(r'const GAMES = (\[.*?\]);', content, re.DOTALL)
    if not m:
        print("GAMES array not found in index.html!")
        return

    games = json.loads(m.group(1))

    # Exclude system assets
    system_assets = {
        'hero.jpg', 'hero.png', 'mikkleo-avatar.jpg', 'favicon.png',
        'favicon.ico', 'apple-touch-icon.png', 'icon-192.png', 'icon-512.png'
    }

    # Gather all images in root or covers/
    image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp', 'covers/*.jpg', 'covers/*.png', 'covers/*.webp']:
        image_files.extend(glob.glob(ext))

    image_files = [f for f in image_files if os.path.basename(f) not in system_assets]

    # Create mapping of normalized filenames to original paths
    norm_file_map = {}
    for img in image_files:
        norm = normalize_name(os.path.basename(img))
        norm_file_map[norm] = img

    matched_count = 0
    updated_games = []

    for g in games:
        title_norm = normalize_name(g.get('title', ''))
        alt_norm = normalize_name(g.get('altTitle', ''))

        matched_img = norm_file_map.get(title_norm) or (norm_file_map.get(alt_norm) if alt_norm else None)

        if matched_img:
            g['image'] = matched_img
            matched_count += 1
            print(f"✓ Matched '{g['title']}' -> {matched_img}")

        updated_games.append(g)

    # Rebuild index.html with updated image paths
    if matched_count:
        import build_index
        build_index.rebuild_index(updated_games)
    else:
        print("No covers matched! Filenames must match game titles (or alt titles).")
    print(f"\nCompleted! Successfully matched {matched_count} cover images to games out of {len(image_files)} uploaded files.")

if __name__ == '__main__':
    main()
