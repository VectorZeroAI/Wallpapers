#!/usr/bin/env python3
import hashlib, os, sys
from collections import defaultdict
from pathlib import Path
from PIL import Image, ImageOps

EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".gif"}

def pixel_hash(path):
    with Image.open(path) as im:
        im = ImageOps.exif_transpose(im)   # respect rotation tags
        im = im.convert("RGBA")            # normalize mode so RGB/P/etc. compare equal
        h = hashlib.blake2b(digest_size=16)
        h.update(f"{im.size}".encode())
        h.update(im.tobytes())
        return h.hexdigest()

def main(root, delete=False):
    groups = defaultdict(list)
    for p in Path(root).rglob("*"):
        if p.suffix.lower() in EXTS and p.is_file():
            try:
                groups[pixel_hash(p)].append(p)
            except Exception as e:
                print(f"skip {p}: {e}", file=sys.stderr)

    freed = 0
    for paths in groups.values():
        if len(paths) < 2:
            continue
        # keep the shortest path (tiebreak: smallest string); change to taste
        paths.sort(key=lambda p: (len(str(p)), str(p)))
        keep, dupes = paths[0], paths[1:]
        print(f"KEEP {keep}")
        for d in dupes:
            print(f"  DUP {d}")
            freed += d.stat().st_size
            if delete:
                d.unlink()
    print(f"\n{'Deleted' if delete else 'Would delete'} ~{freed/1e6:.1f} MB")

if __name__ == "__main__":
    main(sys.argv[1], delete="--delete" in sys.argv)
