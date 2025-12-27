#!/usr/bin/env python3
"""Generate resized WebP variants from originals.

Usage:
  python scripts/generate_webp.py --src img/original --dest img --width 800 --quality 80
"""
import os
import sys
import argparse
from PIL import Image


def process_file(src_path, dest_path, width, quality):
    try:
        with Image.open(src_path) as img:
            # Skip animated images to avoid complex handling
            if getattr(img, "is_animated", False):
                print(f"Skipping animated image: {src_path}")
                return False

            img = img.convert("RGB")
            # Resize maintaining aspect ratio
            img.thumbnail((width, width * 10), Image.LANCZOS)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            img.save(dest_path, "WEBP", quality=quality, method=6)
            print(f"Saved: {dest_path}")
            return True

    except Exception as e:
        print(f"Error processing {src_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default="img/original", help="Source folder with originals")
    parser.add_argument("--dest", default="img", help="Destination folder for resized webp files")
    parser.add_argument("--width", type=int, default=1080, help="Max width for resized images")
    parser.add_argument("--quality", type=int, default=100, help="WebP quality (0-100)")
    parser.add_argument("--force", default=True, action="store_true", help="Force overwrite even if output is up-to-date")
    args = parser.parse_args()

    src = args.src
    dest = args.dest
    processed = 0
    skipped = 0

    supported = (".jpg", ".jpeg", ".png", ".webp", ".tiff", ".bmp")

    if not os.path.exists(src):
        print(f"Source folder does not exist: {src}")
        sys.exit(1)

    for root, dirs, files in os.walk(src):
        rel = os.path.relpath(root, src)
        for f in files:
            name, ext = os.path.splitext(f)
            ext_lower = ext.lower()
            if ext_lower in supported:
                src_path = os.path.join(root, f)
                out_dir = os.path.join(dest, rel) if rel != "." else dest
                out_name = f"{name}.webp"
                out_path = os.path.join(out_dir, out_name)

                if os.path.exists(out_path) and not args.force:
                    if os.path.getmtime(out_path) >= os.path.getmtime(src_path):
                        skipped += 1
                        print(f"Skipping (up-to-date): {out_path}")
                        continue

                ok = process_file(src_path, out_path, args.width, args.quality)
                if ok:
                    processed += 1
                else:
                    skipped += 1
            else:
                print(f"Skipping unsupported file type: {f}")
                skipped += 1

    print(f"Done. Processed: {processed}, Skipped: {skipped}")


if __name__ == "__main__":
    main()
