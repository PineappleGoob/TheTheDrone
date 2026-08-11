"""make_markers.py - build the printable course markers for the project.

Creates one page per marker (black square at exactly 150 mm, white quiet zone kept)
and saves them as markers/course_markers.pdf, plus a PNG of each. US Letter by default
(this is a US camp); set PAGE_MM to A4 if you print on A4.

Print at 100 percent / actual size. Do NOT use "fit to page" or detection sizes will be off.

Run:  python make_markers.py
"""
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Which markers the course uses, and what each one means. Matches settings.SIM_WORLD_MARKERS.
MARKERS = [
    (10, "SAMPLE A"),
    (20, "SAMPLE B"),
    (30, "WAYPOINT 1"),
    (40, "WAYPOINT 2"),
    (42, "HOME BASE"),
]

DPI = 300
MM = DPI / 25.4
PAGE_MM = (215.9, 279.4)                     # US Letter portrait. For A4 use (210, 297).
PAGE = (round(PAGE_MM[0] * MM), round(PAGE_MM[1] * MM))
BLACK_MM = 150.0
MARKER_PX = 1200                            # black marker resolution
QUIET = 150                                 # white border px around the marker
FULL_PX = MARKER_PX + 2 * QUIET
TOTAL_MM = BLACK_MM * FULL_PX / MARKER_PX   # printed size of the full white square
total_px = round(TOTAL_MM * MM)

OUT = Path("markers")
OUT.mkdir(exist_ok=True)


def _font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


F_TITLE = _font("C:/Windows/Fonts/arialbd.ttf", round(10 * MM))
F_BODY = _font("C:/Windows/Fonts/arial.ttf", round(4.5 * MM))


def make_marker_png(marker_id):
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    img = cv2.aruco.generateImageMarker(dictionary, marker_id, MARKER_PX)
    canvas = np.full((FULL_PX, FULL_PX), 255, dtype=np.uint8)
    canvas[QUIET:QUIET + MARKER_PX, QUIET:QUIET + MARKER_PX] = img
    path = OUT / f"aruco_id_{marker_id}.png"
    cv2.imwrite(str(path), canvas)
    return path


def center_text(draw, cx, y, text, font, fill=(0, 0, 0)):
    w = draw.textbbox((0, 0), text, font=font)[2]
    draw.text((cx - w / 2, y), text, font=font, fill=fill)


def build_page(marker_id, label, png_path):
    page = Image.new("RGB", PAGE, "white")
    draw = ImageDraw.Draw(page)
    cx = PAGE[0] // 2

    y = round(14 * MM)
    center_text(draw, cx, y, f"MARKER {marker_id}", F_TITLE)
    y += round(13 * MM)
    center_text(draw, cx, y, label, F_BODY, fill=(0x86, 0x1F, 0x41))
    y += round(9 * MM)

    marker = Image.open(png_path).resize((total_px, total_px))
    mx = (PAGE[0] - total_px) // 2
    page.paste(marker, (mx, y))
    y += total_px + round(8 * MM)

    center_text(draw, cx, y, "Print at 100% (actual size). Keep the white border.", F_BODY,
                fill=(0x5B, 0x6A, 0x86))
    return page


def main():
    pages = []
    for marker_id, label in MARKERS:
        png = make_marker_png(marker_id)
        pages.append(build_page(marker_id, label, png))
    out_pdf = OUT / "course_markers.pdf"
    pages[0].save(out_pdf, save_all=True, append_images=pages[1:], resolution=DPI)
    print(f"Saved {out_pdf}  ({len(pages)} pages: {[m for m, _ in MARKERS]})")


if __name__ == "__main__":
    main()
