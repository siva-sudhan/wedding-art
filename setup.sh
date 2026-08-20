#!/bin/bash
# Assembles the deployable site: pulls the exported 3D assets out of Downloads
# and vendors three.js so the live page has no CDN dependency.
#
#   bash setup.sh
#
# Safe to re-run.

set -uo pipefail
cd "$(dirname "$0")"
mkdir -p assets assets/three/loaders assets/three/controls \
         assets/three/environments assets/three/utils

ok()   { printf "  \033[32m✓\033[0m %s\n" "$1"; }
warn() { printf "  \033[33m!\033[0m %s\n" "$1"; }
bad()  { printf "  \033[31m✗\033[0m %s\n" "$1"; }

DL="$HOME/Downloads"
FAIL=0

echo "==> Collecting 3D assets"
copy() {   # src -> dst, minimum bytes
  if [ -f "$DL/$1" ]; then
    cp "$DL/$1" "assets/$2"
    ok "$2  ($(du -h "assets/$2" | cut -f1))"
  else
    bad "missing $DL/$1"; FAIL=1
  fi
}
copy wedding_reception_merged.glb  wedding_reception.glb          # AR build
copy wedding_reception_viewer.glb  wedding_reception_viewer.glb   # page build
copy wedding_reception.usdz        wedding_reception.usdz         # iOS AR

echo
echo "==> Vendoring three.js (no runtime CDN dependency)"
V=0.160.0
B="https://unpkg.com/three@$V"
get() {  # url-path  local-path  min-bytes
  if curl -fsSL --max-time 90 -o "$2" "$B/$1"; then
    SZ=$(wc -c < "$2")
    if [ "$SZ" -ge "$3" ]; then ok "$(basename "$2")  ($(du -h "$2" | cut -f1))"
    else rm -f "$2"; bad "$(basename "$2") looked truncated ($SZ bytes)"; FAIL=1; fi
  else
    bad "could not fetch $(basename "$2")"; FAIL=1
  fi
}
# Thresholds are deliberately loose — they exist to catch a truncated or
# error-page download, not to pin exact sizes. (A tight bound here already
# rejected a perfectly good OrbitControls.js once.)
get build/three.module.js                          assets/three/three.module.js               200000
get examples/jsm/loaders/GLTFLoader.js             assets/three/loaders/GLTFLoader.js          40000
get examples/jsm/controls/OrbitControls.js         assets/three/controls/OrbitControls.js      12000
get examples/jsm/environments/RoomEnvironment.js   assets/three/environments/RoomEnvironment.js 1500
get examples/jsm/utils/BufferGeometryUtils.js      assets/three/utils/BufferGeometryUtils.js   10000

# model-viewer is no longer used — remove it so it isn't shipped or committed
if [ -f assets/model-viewer.min.js ]; then
  rm -f assets/model-viewer.min.js
  ok "removed unused model-viewer.min.js (916K)"
fi

echo
echo "==> Checking the models"
python3 - <<'PY'
import json, struct, pathlib

def inspect(name, need_digits):
    p = pathlib.Path("assets") / name
    if not p.exists():
        print(f"  \033[31m✗\033[0m {name} missing"); return False
    b = p.read_bytes()
    jlen = struct.unpack("<I", b[12:16])[0]
    j = json.loads(b[20:20+jlen].decode("utf-8"))
    names = {n.get("name","") for n in j.get("nodes", [])}
    digits = sum(1 for d in range(10) if f"DIGIT_{d}" in names)
    labels = sum(1 for l in ("DAYS","HRS","MIN","SEC") if f"LBL_{l}" in names)
    anims  = len(j.get("animations", []))
    good = True
    print(f"  {name}  ({len(b)/1e6:.2f} MB, {len(j['nodes'])} nodes)")
    m = "✓" if anims == 1 else "✗"
    print(f"    {m} {anims} animation clip(s) — must be exactly 1")
    good &= anims == 1
    if need_digits:
        m = "✓" if digits == 10 and labels == 4 else "✗"
        print(f"    {m} digit library: {digits}/10 digits, {labels}/4 labels")
        good &= digits == 10 and labels == 4
    else:
        m = "✓" if digits == 0 else "✗"
        print(f"    {m} no digit library leaking into the AR build ({digits} found)")
        good &= digits == 0
    return good

a = inspect("wedding_reception_viewer.glb", True)
b = inspect("wedding_reception.glb", False)
raise SystemExit(0 if (a and b) else 3)
PY
[ $? -ne 0 ] && FAIL=1

echo
echo "==> Contents"
find assets -type f | sort | while read -r f; do
  printf "  %-46s %s\n" "$f" "$(du -h "$f" | cut -f1)"
done

echo
if [ "$FAIL" -eq 0 ]; then
  printf "\033[1;32mAll checks passed.\033[0m Preview with:\n"
else
  printf "\033[1;31mSomething is missing above — fix it before deploying.\033[0m\nPreview anyway with:\n"
fi
echo "    python3 -m http.server 8080"
echo "    open http://localhost:8080"
echo
echo "'View in your room' only appears on a phone. On desktop you get the"
echo "3D viewer and Camera mode, which is expected."
