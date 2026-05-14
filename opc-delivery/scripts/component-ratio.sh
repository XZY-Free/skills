#!/usr/bin/env bash
# Compute Codify component-library mapping ratio for a generated HTML file.
# Used by verification.md 3A.2 to decide whether design() should be rerun.
#
# Usage:
#   scripts/component-ratio.sh <html-file> [full-components|hybrid]
#
# Output (JSON): {"ui_component": N, "ui_icon": N, "div": N, "component_ratio": "P%"}

set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <html-file> [full-components|hybrid]" >&2
  exit 2
fi

FILE="$1"
STRATEGY="${2:-hybrid}"
if [ ! -f "$FILE" ]; then
  echo "Error: file not found: $FILE" >&2
  exit 2
fi

UI_COUNT=$(grep -oE '<ui-component\b' "$FILE" | wc -l | tr -d ' ')
ICON_COUNT=$(grep -oE '<ui-icon\b' "$FILE" | wc -l | tr -d ' ')
DIV_COUNT=$(grep -oE '<div\b' "$FILE" | wc -l | tr -d ' ')

TOTAL=$((UI_COUNT + ICON_COUNT + DIV_COUNT))
if [ "$TOTAL" -eq 0 ]; then
  RATIO="0"
else
  RATIO=$(awk -v u="$UI_COUNT" -v i="$ICON_COUNT" -v t="$TOTAL" \
    'BEGIN { printf "%.0f", (u + i) * 100 / t }')
fi

THRESHOLD=15
if [ "$STRATEGY" = "full-components" ]; then
  THRESHOLD=40
fi
OK=$(awk -v ratio="$RATIO" -v threshold="$THRESHOLD" 'BEGIN { print (ratio >= threshold ? "true" : "false") }')

printf '{"ui_component": %s, "ui_icon": %s, "div": %s, "component_ratio": "%s%%", "strategy": "%s", "threshold": %s, "ok": %s}\n' \
  "$UI_COUNT" "$ICON_COUNT" "$DIV_COUNT" "$RATIO" "$STRATEGY" "$THRESHOLD" "$OK"
