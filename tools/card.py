#!/usr/bin/env python3
"""Header cards for the World State's posts: the sheet header of the Forecasts page, as a PNG.

  python3 tools/card.py forecast "Will X happen?" 0.63 --kicker "Q_20261019_04 · OPEN · RESOLVES BY 24 OCTOBER" --label ARCHIVE -o card.png
  python3 tools/card.py edition "Meta to spend more on AI after record ad sales" --kicker "EDITION OF 22 OCTOBER · 3 ISSUED · 20 OPEN" -o card.png

Gold ground, Archivo for the words, a hundred dots for the probability. Used by tools/worldstate.py; needs Pillow,
fonttools and brotli (the fonts in site/fonts are woff2 and are unpacked once into a temp folder).
"""
import argparse, io, os, tempfile
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, PAD = 1600, 900, 110
FOOT = "UBIK FORECAST · UBIKISTAN.ORG/WORLD-STATE"
FOOT_ED = "UBIK WORLD STATE · UBIKISTAN.ORG/WORLD-STATE"
GOLD, INK = (217, 162, 27), (14, 14, 14)
OFF = tuple(round(GOLD[i] + (INK[i] - GOLD[i]) * 0.22) for i in range(3))   # a dot that is not lit
_dir = None

def ttf(name):
    """Unpack site/fonts/<name>.woff2 to a .ttf once per run and return its path."""
    global _dir
    if _dir is None: _dir = tempfile.mkdtemp(prefix="ubik-fonts-")
    out = os.path.join(_dir, name + ".ttf")
    if not os.path.exists(out):
        from fontTools.ttLib import TTFont
        f = TTFont(os.path.join(ROOT, "site", "fonts", name + ".woff2")); f.flavor = None; f.save(out)
    return out

def font(name, size, wght=700, wdth=100):
    f = ImageFont.truetype(ttf(name), size)
    try: f.set_variation_by_axes([wght, wdth] if name == "archivo" else [wght])
    except Exception: pass
    return f

def tracked(draw, xy, text, f, fill, track):
    """Draw text with letter-spacing (a fraction of the size), the way the page's labels are set."""
    x, y = xy; step = track * f.size
    for ch in text:
        draw.text((x, y), ch, font=f, fill=fill); x += draw.textlength(ch, font=f) + step
    return x

def wrap(draw, text, f, width):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=f) <= width or not cur: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def fit(draw, text, width, max_lines=3, size=88, min_size=56):
    """The question or headline, Archivo 800, shrunk until it fits the lines allowed: (font, lines, line height)."""
    while True:
        f = font("archivo", size, 800); lines = wrap(draw, text, f, width)
        if len(lines) <= max_lines or size <= min_size: return f, lines, round(size * 1.08)
        size -= 6

def title_block(draw, x, y, f, lines, lh):
    for i, l in enumerate(lines): draw.text((x - f.size * 0.04, y + i * lh), l, font=f, fill=INK)
    return y + len(lines) * lh

def base(kicker, body_h, foot=FOOT):
    """Gold ground, the kicker, the footer; returns the image, its draw and the top of the body, centred."""
    im = Image.new("RGB", (W, H), GOLD); d = ImageDraw.Draw(im)
    top = max(PAD, (H - (28 + 42 + body_h)) // 2 - 10)
    tracked(d, (PAD, top), kicker.upper(), font("archivo", 28, 700), INK, 0.14)
    tracked(d, (PAD, H - PAD + 20), foot, font("archivo", 22, 700), tuple(round(GOLD[i] + (INK[i] - GOLD[i]) * 0.62) for i in range(3)), 0.14)
    return im, d, top + 70

def dots(d, x, y, size, pct):
    """Ten by ten, the lit ones counting the probability."""
    n = round(pct * 100); cell = size / 10; r = cell * 0.34
    for k in range(100):
        cx, cy = x + (k % 10) * cell + cell / 2, y + (k // 10) * cell + cell / 2
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=INK if k < n else OFF)

def forecast_card(claim, pct, kicker, label="ARCHIVE"):
    grid = 280; gx = W - PAD - grid
    big = font("archivo", 180, 800); ptxt = f"{round(pct * 100)}%" if pct is not None else "?"   # None: the figure is for key holders
    scratch = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    pw = scratch.textlength(ptxt, font=big) - 180 * 0.03 * (len(ptxt) - 1)
    if pct is None: pw = max(pw, scratch.textlength("50%", font=big) - 180 * 0.06)   # keep the label clear of the grid
    px = gx - 44 - pw
    f, lines, lh = fit(scratch, claim, px - 60 - PAD, max_lines=4)
    im, d, y = base(kicker, max(len(lines) * lh, grid))
    gy = y - 10
    d.ellipse((px, gy + 14, px + 26, gy + 40), fill=INK)
    tracked(d, (px + 38, gy), label.upper(), font("archivo", 28, 700), INK, 0.1)
    x = px
    for ch in ptxt: d.text((x, gy + 44), ch, font=big, fill=INK); x += d.textlength(ch, font=big) - 180 * 0.03
    dots(d, gx, gy, grid, pct or 0)
    title_block(d, PAD, y, f, lines, lh)
    return im

def edition_card(headline, kicker):
    r = 140; cx = W - PAD - r
    scratch = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    f, lines, lh = fit(scratch, headline, cx - r - 80 - PAD, max_lines=4, size=92)
    im, d, y = base(kicker, max(len(lines) * lh, 2 * r), FOOT_ED)
    cy = y + max(len(lines) * lh, 2 * r) // 2
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=INK, width=44)
    title_block(d, PAD, y, f, lines, lh)
    return im

def score_card(title, brier, marks, kicker):
    """The ledger: a sentence on the left; on the right the Brier score, and one dot per settled forecast (lit = leaned right)."""
    scratch = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    big = font("archivo", 180, 800); btxt = f"{brier:.3f}".lstrip("0") if brier < 1 else f"{brier:.2f}"
    bw = scratch.textlength(btxt, font=big) - 180 * 0.03 * (len(btxt) - 1)
    px = W - PAD - max(bw, 300)
    f, lines, lh = fit(scratch, title, px - 70 - PAD, max_lines=4)
    per = 10; cell = 32; rows = (len(marks) + per - 1) // per
    body = max(len(lines) * lh, 44 + 190 + 24 + rows * cell)
    im, d, y = base(kicker, body, FOOT_ED)
    gy = y - 10
    d.ellipse((px, gy + 14, px + 26, gy + 40), fill=INK)
    tracked(d, (px + 38, gy), "BRIER", font("archivo", 28, 700), INK, 0.1)
    x = px
    for ch in btxt: d.text((x, gy + 44), ch, font=big, fill=INK); x += d.textlength(ch, font=big) - 180 * 0.03
    r = cell * 0.34; my = gy + 44 + 190 + 24
    for k, ok in enumerate(marks):
        cx, cy = px + (k % per) * cell + cell / 2, my + (k // per) * cell + cell / 2
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=INK if ok else OFF)
    title_block(d, PAD, y, f, lines, lh)
    return im

def png(im):
    b = io.BytesIO(); im.save(b, "PNG", optimize=True); return b.getvalue()

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("kind", choices=["forecast", "edition"]); ap.add_argument("text")
    ap.add_argument("pct", nargs="?", type=float, default=0.5); ap.add_argument("--kicker", default=""); ap.add_argument("--label", default="ARCHIVE")
    ap.add_argument("-o", default="card.png"); a = ap.parse_args()
    im = forecast_card(a.text, a.pct, a.kicker, a.label) if a.kind == "forecast" else edition_card(a.text, a.kicker)
    im.save(a.o); print(a.o)
