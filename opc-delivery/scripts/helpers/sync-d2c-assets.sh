#!/usr/bin/env bash
# Copy D2C assets (icons/images) from .mg/<route>/asset/ to public/assets/<route>/.
# Used by restoration-workflow.md step 4.1 (both modes).
#
# Usage:
#   scripts/sync-d2c-assets.sh <src-dir> <dst-dir>
#     <src-dir>: D2C output root, e.g. .mg (or .mg_v2 for update flow)
#     <dst-dir>: target asset root, e.g. src/<project>/public/assets

set -euo pipefail

SRC="${1:-.mg}"
DST="${2:-public/assets}"

if [ ! -d "$SRC" ]; then
  echo "Error: source dir not found: $SRC" >&2
  exit 2
fi

ROUTES_DONE=0
for d in "$SRC"/*/; do
  [ -d "$d" ] || continue
  route=$(basename "$d")
  mkdir -p "$DST/$route/icons" "$DST/$route/images"
  if [ -d "$d/asset/icons" ]; then
    cp -r "$d/asset/icons/"* "$DST/$route/icons/" 2>/dev/null || true
  fi
  if [ -d "$d/asset/images" ]; then
    cp -r "$d/asset/images/"* "$DST/$route/images/" 2>/dev/null || true
  fi
  ROUTES_DONE=$((ROUTES_DONE + 1))
  echo "synced: $route"
done

echo "done: $ROUTES_DONE route(s) → $DST"
