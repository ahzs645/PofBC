#!/bin/bash
# usage: review.sh <raster under public/> <svg under public/> <review name>
set -e
P=$(cd "$(dirname "$0")/.." && pwd); PUB=$(cd "$P/../../../public" && pwd)
T=$(mktemp -d)
node "$P/scripts/render.mjs" "$PUB/$2" "$T/v.png" 400
python3 -I "$P/scripts/review.py" "$PUB/$1" "$T/v.png" "$P/review/$3.webp"
echo "$P/review/$3.webp"
