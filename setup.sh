#!/bin/bash
# Assembles the deployable site: pulls the exported 3D assets out of Downloads
# and vendors model-viewer so the live page has no CDN dependency.
#
#   bash setup.sh
#
# Safe to re-run.

set -uo pipefail
cd "$(dirname "$0")"
mkdir -p assets

ok()   { printf "  \033[32m✓\033[0m %s\n" "$1"; }
warn() { printf "  \033[33m!\033[0m %s\n" "$1"; }
bad()  { printf "  \033[31m✗\033[0m %s\n" "$1"; }

echo "==> Collecting 3D assets"
DL="$HOME/Downloads"

if [ -f "$DL/wedding_reception_merged.glb" ]; then
  cp "$DL/wedding_reception_merged.glb" assets/wedding_reception.glb
  ok "wedding_reception.glb  ($(du -h assets/wedding_reception.glb | cut -f1))"
else
  bad "missing $DL/wedding_reception_merged.glb"
  bad "that is the single-clip export — re-run the merge step before deploying"
fi

if [ -f "$DL/wedding_reception.usdz" ]; then
  cp "$DL/wedding_reception.usdz" assets/wedding_reception.usdz
  ok "wedding_reception.usdz ($(du -h assets/wedding_reception.usdz | cut -f1))"
else
  warn "no USDZ found — iPhones will fall back to the in-page 3D view"
fi

echo
echo "==> Vendoring model-viewer (removes the runtime CDN dependency)"
MV="https://unpkg.com/@google/model-viewer@3.5.0/dist/model-viewer.min.js"
if curl -fsSL --max-time 60 -o assets/model-viewer.min.js "$MV"; then
  SZ=$(wc -c < assets/model-viewer.min.js)
  if [ "$SZ" -gt 200000 ]; then
    ok "model-viewer.min.js ($(du -h assets/model-viewer.min.js | cut -f1))"
  else
    rm -f assets/model-viewer.min.js
    warn "download looked truncated — page will use the CDN fallback instead"
  fi
else
  warn "could not fetch model-viewer — page will use the CDN fallback instead"
fi

echo
echo "==> Contents"
ls -lh assets/ | tail -n +2 | awk '{printf "  %-34s %s\n", $9, $5}'

echo
echo "Preview locally before deploying:"
echo "    python3 -m http.server 8080"
echo "    open http://localhost:8080"
echo
echo "Note: 'View in your room' only appears on a phone. On a desktop browser"
echo "you get the 3D viewer and Camera mode, which is expected."
