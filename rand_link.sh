#!/bin/sh
# Usage: randlink-all <source-base> <dest>

[ $# -eq 2 ] || { echo "Usage: $0 <source-base> <dest>" >&2; exit 1; }

srcdir=$(cd -- "$1" && pwd) || exit 1
dstdir=$(cd -- "$2" 2>/dev/null && pwd) || dstdir=$(cd -- "$(dirname -- "$2")" && pwd)/$(basename -- "$2")

[ -d "$srcdir" ] || { echo "Not a directory: $srcdir" >&2; exit 1; }

# Iterate subdirs of srcdir, but NEVER descend into dstdir
find "$srcdir" -mindepth 1 -maxdepth 1 -type d \
     -not -path "$dstdir" \
     -not -path "$dstdir/*" \
     | sort | while IFS= read -r sub; do

    name=$(basename "$sub")
    file=$(find -L "$sub" -maxdepth 1 -type f | shuf -n 1)

    if [ -z "$file" ] || [ ! -f "$file" ]; then
        printf 'skip  %s (no usable file)\n' "$name" >&2
        continue
    fi

    ln -s -- "$file" "$dstdir/$name"
    printf 'link  %-20s -> %s\n' "$name" "$file"
done
