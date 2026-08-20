# Shiva & Meena — AR Reception Invitation

A scannable AR invitation. Guests scan the QR on the printed card, the page opens
in their phone browser, and the 3D lettering reveals itself line by line before
five firework bursts go off above it.

**Sunday, 25 October 2026 · 6 PM onwards**

---

## What's in here

| File | Purpose |
|---|---|
| `index.html` | The whole experience — one self-contained page |
| `assets/wedding_reception.glb` | Animated 3D scene, Android Scene Viewer + in-page viewer |
| `assets/wedding_reception.usdz` | Same scene for iOS AR Quick Look |
| `assets/poster.jpg` | Still shown while the model loads |
| `assets/model-viewer.min.js` | Vendored renderer (created by `setup.sh`) |
| `setup.sh` | Collects the exports and vendors model-viewer |
| `make_qr.py` | Generates the print-ready QR once you know your URL |

The animation is a single 10.3-second clip named `Reveal`: 318 channels driving
161 objects. Nothing is a particle system — every spark is keyframed geometry, so
it survives both the glTF and USDZ pipelines.

---

## Deploy to GitHub Pages

**1. Assemble the assets**

```bash
cd wedding-ar
bash setup.sh
```

**2. Check it locally first**

```bash
python3 -m http.server 8080
open http://localhost:8080
```

You should see the lettering reveal and the fireworks. On a desktop browser the
"View in your room" button stays hidden — that is correct, it only appears on a
phone that supports native AR.

**3. Push to GitHub**

```bash
git init
git add .
git commit -m "AR wedding reception invitation"
git branch -M main
git remote add origin https://github.com/siva-sudhan/wedding-art.git
git push -u origin main
```

**4. Turn on Pages**

Repo → **Settings** → **Pages** → Source: **Deploy from a branch** → Branch:
`main`, folder `/ (root)` → **Save**.

Give it a minute, then your URL is:

```
https://siva-sudhan.github.io/wedding-art/
```

The repo must be **public** for Pages to work on a free account.

**5. The QR is already generated**

`qr/` holds the codes for exactly that URL, all decode-verified:

| File | Size at 300 dpi | Use |
|---|---|---|
| `qr_30mm.png` | 33 mm | The recommended printed size |
| `qr_card.png` | 51 mm | Larger placement |
| `qr_print.png` | 152 mm | Scale down in your layout |
| `qr_with_caption.png` | — | Ready-made block with caption |

Only regenerate if the URL changes:

```bash
pip install "qrcode[pil]"
python3 make_qr.py https://siva-sudhan.github.io/wedding-art/
```

---

## Before you send it to print

- [ ] Scan the QR from a **printed** proof, not from a screen — screens are far more forgiving
- [ ] Test on an **iPhone** (Safari) and an **Android** (Chrome)
- [ ] Test on **cellular data**, not just wifi — the GLB is ~3.7 MB
- [ ] Check it in **dim light**, since receptions are dim
- [ ] Print the QR at **25 mm minimum**, ideally 30–35 mm
- [ ] Keep the white margin around the QR — that quiet zone is what makes it scan

Add a line of text under the QR so guests know what it does, e.g.
*"Scan to see our invitation come alive"*. Without it, most people won't bother.

---

## How the AR paths work

| Device | What happens |
|---|---|
| iPhone / iPad (Safari) | Native **AR Quick Look** via the USDZ — places the text on a real wall |
| Android (Chrome) | Native **Scene Viewer** via the GLB |
| Anything else | In-page 3D viewer, drag to orbit; **Camera mode** puts it over the camera feed |

Camera mode is the universal fallback. It composites the 3D scene over a live
camera feed without surface tracking — it works on essentially any phone with a
camera and a browser, which matters when your guest list spans a lot of hardware.

---

## Changing things later

The Blender source is `wedding_ar.blend`. After editing:

1. Export GLB: `File → Export → glTF 2.0`, format **GLB**, +Y up, Animation on,
   mode **Scene**, and **turn Draco off** (it would add a runtime decoder dependency).
2. Blender writes one animation clip *per object*, which no AR viewer will play.
   Re-run the merge step to collapse them into a single `Reveal` clip.
3. Export USDZ: `File → Export → Universal Scene Description`, `.usdz`, animation on.
4. `bash setup.sh`, commit, push.

The QR does not need regenerating unless the URL changes.
