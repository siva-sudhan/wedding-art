#!/usr/bin/env python3
"""
Rewrite the day count baked into the AR models.

    python3 update_countdown.py            # use today's date
    python3 update_countdown.py --check    # report only, change nothing
    python3 update_countdown.py --days 42  # force a value (testing)

Both AR files carry ten digit meshes per slot, stacked in the same place.
Exactly one per slot is at visible scale; the rest sit at 1e-5. Changing the
displayed number is therefore a pure transform edit — no re-export, no Blender.

  assets/wedding_reception.glb   (Android Scene Viewer)  -> patch node scale
  assets/wedding_reception.usdz  (iOS AR Quick Look)     -> patch xformOp:scale

The web page is unaffected: it computes a live countdown in JavaScript and
never reads these values.
"""
import argparse, datetime, json, os, pathlib, struct, sys

ROOT    = pathlib.Path(__file__).resolve().parent
GLB     = ROOT / "assets" / "wedding_reception.glb"
USDZ    = ROOT / "assets" / "wedding_reception.usdz"
TARGET  = datetime.datetime(2026, 10, 25, 12, 30, tzinfo=datetime.timezone.utc)
VISIBLE = 1.15
HIDDEN  = 1e-5


def days_left(now=None):
    now = now or datetime.datetime.now(datetime.timezone.utc)
    return max(0, int((TARGET - now).total_seconds() // 86400))


def wanted(days):
    """(slot0 digit, slot1 digit) for a two-slot display, clamped at 99."""
    d = min(days, 99)
    return d // 10, d % 10


# ------------------------------------------------------------------ glTF
def read_glb(path):
    b = bytearray(path.read_bytes())
    magic, _, length = struct.unpack("<III", bytes(b[:12]))
    if magic != 0x46546C67:
        raise ValueError(f"{path.name} is not a GLB")
    off, chunks = 12, []
    while off < length:
        clen, ctype = struct.unpack("<II", bytes(b[off:off + 8]))
        chunks.append((ctype, off + 8, clen))
        off += 8 + clen
    _, jo, jl = next(c for c in chunks if c[0] == 0x4E4F534A)
    _, bo, bl = next(c for c in chunks if c[0] == 0x004E4942)
    return b, json.loads(bytes(b[jo:jo + jl]).decode()), bo, bl


def write_glb(path, j, blob):
    nj = json.dumps(j, separators=(",", ":")).encode()
    nj += b" " * ((4 - len(nj) % 4) % 4)
    blob = blob + b"\x00" * ((4 - len(blob) % 4) % 4)
    body = (struct.pack("<II", len(nj), 0x4E4F534A) + nj +
            struct.pack("<II", len(blob), 0x004E4942) + blob)
    path.write_bytes(struct.pack("<III", 0x46546C67, 2, 12 + len(body)) + body)


def patch_glb(s0, s1, check=False):
    b, j, bo, bl = read_glb(GLB)
    blob = bytes(b[bo:bo + bl])
    shown, changed = [], 0
    for node in j["nodes"]:
        name = node.get("name", "")
        if not name.startswith("ARD_S"):
            continue
        try:
            slot, digit = int(name[5]), int(name[7])
        except (ValueError, IndexError):
            continue
        on = digit == (s0 if slot == 0 else s1)
        target = [VISIBLE] * 3 if on else [HIDDEN] * 3
        if on:
            shown.append(name)
        cur = node.get("scale", [1, 1, 1])
        if any(abs(a - c) > 1e-6 for a, c in zip(target, cur)):
            changed += 1
            if not check:
                node["scale"] = target
    if changed and not check:
        write_glb(GLB, j, blob)
    return sorted(shown), changed


# ------------------------------------------------------------------ USDZ
def patch_usdz(s0, s1, check=False):
    try:
        from pxr import Usd, UsdGeom, UsdUtils, Sdf, Gf
    except ImportError:
        return None, "usd-core not installed  (pip install usd-core)"

    import shutil, tempfile, zipfile
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="usdz-"))
    try:
        with zipfile.ZipFile(USDZ) as z:
            z.extractall(tmp)
            names = z.namelist()
        usdc = next(p for p in names if p.endswith((".usdc", ".usda")))
        stage = Usd.Stage.Open(str(tmp / usdc))

        shown, changed = [], 0
        for prim in stage.Traverse():
            name = prim.GetName()
            if not name.startswith("ARD_S"):
                continue
            try:
                slot, digit = int(name[5]), int(name[7])
            except (ValueError, IndexError):
                continue
            on = digit == (s0 if slot == 0 else s1)
            want = Gf.Vec3f(VISIBLE if on else HIDDEN)
            if on:
                shown.append(name)
            op = next((o for o in UsdGeom.Xformable(prim).GetOrderedXformOps()
                       if o.GetOpName() == "xformOp:scale"), None)
            if op is None:
                continue
            if Gf.IsClose(op.Get(), want, 1e-6):
                continue
            changed += 1
            if not check:
                op.Set(want)

        if changed and not check:
            stage.GetRootLayer().Save()
            del stage                      # release the layer before repacking
            out = tmp / "repack.usdz"
            # CreateNewUsdzPackage localises referenced assets and applies the
            # 64-byte alignment usdz requires. Hand-rolling the zip gets that
            # wrong in ways Quick Look rejects silently.
            if not UsdUtils.CreateNewUsdzPackage(
                    Sdf.AssetPath(str(tmp / usdc)), str(out)):
                raise RuntimeError("CreateNewUsdzPackage failed")
            shutil.copy(out, USDZ)
        return sorted(shown), changed
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report only")
    ap.add_argument("--days", type=int, help="override the computed day count")
    a = ap.parse_args()

    days = a.days if a.days is not None else days_left()
    s0, s1 = wanted(days)
    print(f"target   : {TARGET.isoformat()}")
    print(f"days left: {days}  -> slot0={s0} slot1={s1}")

    ok = True
    shown, changed = patch_glb(s0, s1, a.check)
    print(f"GLB      : showing {shown}  ({changed} node(s) "
          f"{'would change' if a.check else 'updated'})")

    res, changed = patch_usdz(s0, s1, a.check)
    if res is None:
        print(f"USDZ     : SKIPPED — {changed}")
        ok = False
    else:
        print(f"USDZ     : showing {res}  ({changed} prim(s) "
              f"{'would change' if a.check else 'updated'})")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
