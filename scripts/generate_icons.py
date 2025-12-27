#!/usr/bin/env python3
"""Generate PWA icons (192x192 and 512x512) and an apple-touch-icon from an existing image.

Usage:
  python scripts/generate_icons.py --src img/2025-m1.webp --dest img --force
"""
import os
import sys
import argparse
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument('--src', default='img/2025-m1.webp')
parser.add_argument('--dest', default='img')
parser.add_argument('--force', action='store_true')
args = parser.parse_args()

src = args.src
if not os.path.exists(src):
    # try to find first image in img/
    for root, dirs, files in os.walk('img'):
        for f in files:
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                src = os.path.join(root, f)
                break
        if src != args.src:
            break

out192 = os.path.join(args.dest, 'icon-192.png')
out512 = os.path.join(args.dest, 'icon-512.png')
apple = os.path.join(args.dest, 'apple-touch-icon.png')

if not os.path.exists(src):
    print('No source image found to generate icons.')
    sys.exit(1)

print(f'Using source: {src}')

with Image.open(src) as img:
    # ensure square crop from center
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    right = left + side
    bottom = top + side
    img_cropped = img.crop((left, top, right, bottom)).convert('RGBA')

    for size, out in ((192, out192), (512, out512)):
        if os.path.exists(out) and not args.force:
            print(f'Skipping existing: {out}')
            continue
        ico = img_cropped.resize((size, size), Image.LANCZOS)
        ico.save(out, format='PNG', optimize=True)
        print(f'Saved: {out}')

    if not os.path.exists(apple) or args.force:
        apple_img = img_cropped.resize((180, 180), Image.LANCZOS)
        apple_img.save(apple, format='PNG', optimize=True)
        print(f'Saved: {apple}')

print('Icons generation complete.')