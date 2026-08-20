#!/usr/bin/env python3
"""
Generate the print-ready QR code for the invitation card.

    pip install "qrcode[pil]"
    python3 make_qr.py https://YOURNAME.github.io/wedding-ar/

Writes qr_print.png (1800px, 300dpi -> 6in) and qr_card.png (600px, for
placing directly in an Illustrator/InDesign layout).

Use HIGH error correction and keep the URL short: the QR is printed small
and guests will scan it in dim reception lighting.
"""
import sys, pathlib
import qrcode
from qrcode.constants import ERROR_CORRECT_H

MAROON = (42, 10, 20)
CREAM  = (255, 255, 255)   # keep the quiet zone pure white for scan reliability


def build(url: str, px: int, path: str) -> None:
    qr = qrcode.QRCode(version=None, error_correction=ERROR_CORRECT_H,
                       box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color=MAROON, back_color=CREAM).convert("RGB")
    img = img.resize((px, px), 0)          # nearest-neighbour keeps modules crisp
    img.save(path, dpi=(300, 300))
    print(f"{path}  {px}x{px}px  ({px/300:.1f} in at 300dpi)  v{qr.version}")


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    url = sys.argv[1].strip()
    if not url.startswith(("http://", "https://")):
        print("URL must start with https://")
        return 1
    if not url.endswith("/") and "." not in url.rsplit("/", 1)[-1]:
        url += "/"                          # avoid a redirect hop when scanned
    here = pathlib.Path(__file__).parent
    build(url, 1800, str(here / "qr_print.png"))
    build(url,  600, str(here / "qr_card.png"))
    print("\nEncoded:", url)
    print("Scan-test both on an iPhone and an Android before sending to print.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
