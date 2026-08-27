#!/usr/bin/env python3
"""Build web assets for the Dialect Money mark (Direction B, 话).

Two independent paths, both from the same font files so they agree:

  SVG  glyph outlines extracted with fontTools, so the vector files carry no
       font dependency - the logo renders identically on a machine that has
       never heard of Songti.
  PNG  drawn with Pillow at 4x and downsampled, which keeps small sizes crisp.

Run:  .venv/bin/python make-assets.py
Out:  assets/
"""

from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTCollection, TTFont
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent / "assets"
SONGTI = "/System/Library/Fonts/Supplemental/Songti.ttc"
SONGTI_BOLD_INDEX = 1          # Songti SC Bold
GEORGIA = "/System/Library/Fonts/Supplemental/Georgia.ttf"

GLYPH = "话"
WORDMARK = "Dialect Money"

BRASS = "#b8873f"
INK = "#2b2621"
PAPER = "#f7f4ee"

# Mark geometry, in a 100x100 box. Matches DirectionB.dc.html.
RING_R = 37.0
RING_W = 5.0
GLYPH_BOX = 39.0               # ringed variant: bbox fits this square, centred
GLYPH_BOX_SOLO = 68.0          # ringless small-size variant: no ring to collide with


# --------------------------------------------------------------------------
# SVG: real outlines, no font dependency
# --------------------------------------------------------------------------

def glyph_path(font, char, target_box, cx, cy):
    """Return an SVG <path d> for one character, scaled and centred.

    Font coordinates are Y-up; SVG is Y-down, so the transform flips Y.
    Centring uses the glyph's own bounding box rather than the em square, so
    the character sits optically centred in the ring.
    """
    glyphs = font.getGlyphSet()
    name = font.getBestCmap()[ord(char)]

    bounds = BoundsPen(glyphs)
    glyphs[name].draw(bounds)
    x0, y0, x1, y1 = bounds.bounds

    scale = target_box / max(x1 - x0, y1 - y0)
    # Flip Y, then place the bbox centre at (cx, cy).
    tx = cx - (x0 + x1) / 2 * scale
    ty = cy + (y0 + y1) / 2 * scale

    pen = SVGPathPen(glyphs)
    glyphs[name].draw(pen)
    return pen.getCommands(), f"translate({tx:.3f} {ty:.3f}) scale({scale:.5f} {-scale:.5f})"


def word_paths(font, text, cap_px):
    """Outline a run of text. Returns (list of (d, transform), total width).

    Uses plain advance widths - no kerning table lookup. Fine for a two-word
    logotype; if the spacing ever looks wrong, that is the reason.
    """
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()
    upem = font["head"].unitsPerEm
    scale = cap_px / upem

    out, x = [], 0.0
    for ch in text:
        name = cmap.get(ord(ch))
        if name is None:
            continue
        pen = SVGPathPen(glyphs)
        glyphs[name].draw(pen)
        d = pen.getCommands()
        if d.strip():
            out.append((d, f"translate({x:.3f} 0) scale({scale:.5f} {-scale:.5f})"))
        x += glyphs[name].width * scale
    return out, x


def write_mark_svg(path, ring_colour, glyph_colour, bg=None, ring=True):
    font = TTCollection(SONGTI).fonts[SONGTI_BOLD_INDEX]
    box = GLYPH_BOX if ring else GLYPH_BOX_SOLO
    d, transform = glyph_path(font, GLYPH, box, 50.0, 50.0)

    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" '
             'width="100" height="100" role="img" aria-label="Dialect Money">',
             '<title>Dialect Money</title>']
    if bg:
        parts.append(f'<rect width="100" height="100" rx="22.5" fill="{bg}"/>')
    if ring:
        parts.append(
            f'<circle cx="50" cy="50" r="{RING_R}" fill="none" '
            f'stroke="{ring_colour}" stroke-width="{RING_W}"/>')
    parts.append(f'<g transform="{transform}" fill="{glyph_colour}"><path d="{d}"/></g>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def ink_right(font, text, cap_px):
    """Right-most inked x of a text run, which is not the advance width."""
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()
    scale = cap_px / font["head"].unitsPerEm
    x, right = 0.0, 0.0
    for ch in text:
        name = cmap.get(ord(ch))
        if name is None:
            continue
        bounds = BoundsPen(glyphs)
        glyphs[name].draw(bounds)
        if bounds.bounds:
            right = max(right, x + bounds.bounds[2] * scale)
        x += glyphs[name].width * scale
    return right


def write_logo_svg(path, mark_colour, text_colour, bg=None):
    """Horizontal lockup: ring mark + outlined wordmark."""
    songti = TTCollection(SONGTI).fonts[SONGTI_BOLD_INDEX]
    georgia = TTFont(GEORGIA)

    mark_d, mark_tf = glyph_path(songti, GLYPH, GLYPH_BOX, 50.0, 50.0)
    cap = 46.0
    words, word_w = word_paths(georgia, WORDMARK, cap)

    gap = 26.0
    baseline_y = 50.0 + cap * 0.36          # optical centre of Georgia's x-height run

    # Tight viewBox with uniform padding, measured rather than guessed: the
    # ring's outer edge bounds top/left/bottom, the wordmark's inked right
    # edge bounds the right. Padding an assumed 100-unit box instead leaves
    # the right side visibly tighter than the other three.
    ring_out = RING_R + RING_W / 2
    ink_l, ink_t, ink_b = 50 - ring_out, 50 - ring_out, 50 + ring_out
    ink_r = 100 + gap + ink_right(georgia, WORDMARK, cap)
    pad = 10.0
    vb_x, vb_y = ink_l - pad, ink_t - pad
    vb_w, vb_h = (ink_r - ink_l) + pad * 2, (ink_b - ink_t) + pad * 2

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" '
             f'viewBox="{vb_x:.2f} {vb_y:.2f} {vb_w:.2f} {vb_h:.2f}" '
             f'width="{vb_w:.0f}" height="{vb_h:.0f}" '
             f'role="img" aria-label="Dialect Money">',
             '<title>Dialect Money</title>']
    if bg:
        parts.append(f'<rect x="{vb_x:.2f}" y="{vb_y:.2f}" width="{vb_w:.2f}" '
                     f'height="{vb_h:.2f}" fill="{bg}"/>')
    parts.append(f'<circle cx="50" cy="50" r="{RING_R}" fill="none" '
                 f'stroke="{mark_colour}" stroke-width="{RING_W}"/>')
    parts.append(f'<g transform="{mark_tf}" fill="{mark_colour}"><path d="{mark_d}"/></g>')

    parts.append(f'<g transform="translate({100 + gap:.3f} {baseline_y:.3f})" fill="{text_colour}">')
    for d, tf in words:
        parts.append(f'<g transform="{tf}"><path d="{d}"/></g>')
    parts.append("</g></svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


# --------------------------------------------------------------------------
# PNG: drawn at 4x, downsampled
# --------------------------------------------------------------------------

SS = 4  # supersample factor


def draw_mark(size, ring_colour, glyph_colour, bg=None, tile_radius=None, ring=True):
    """Render the mark into an RGBA image of `size` px."""
    n = size * SS
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if bg:
        if tile_radius is None:
            draw.rectangle([0, 0, n - 1, n - 1], fill=bg)
        else:
            draw.rounded_rectangle([0, 0, n - 1, n - 1],
                                   radius=int(n * tile_radius), fill=bg)

    unit = n / 100.0
    if ring:
        r, w = RING_R * unit, RING_W * unit
        draw.ellipse([50 * unit - r, 50 * unit - r, 50 * unit + r, 50 * unit + r],
                     outline=ring_colour, width=max(1, round(w)))

    # Size the glyph by its measured bbox so it matches the SVG exactly.
    px = int((GLYPH_BOX if ring else GLYPH_BOX_SOLO) * unit * 1.34)
    font = ImageFont.truetype(SONGTI, px, index=SONGTI_BOLD_INDEX)
    x0, y0, x1, y1 = draw.textbbox((0, 0), GLYPH, font=font)
    draw.text((50 * unit - (x0 + x1) / 2, 50 * unit - (y0 + y1) / 2),
              GLYPH, font=font, fill=glyph_colour)

    return img.resize((size, size), Image.LANCZOS)


def draw_og_card(path):
    """1200x630 link-preview card - what a helper sees when the link lands."""
    w, h = 1200 * 2, 630 * 2
    img = Image.new("RGB", (w, h), INK)
    draw = ImageDraw.Draw(img)

    mark = draw_mark(300 * 2, BRASS, BRASS)
    img.paste(mark, (110 * 2, 165 * 2), mark)

    title = ImageFont.truetype(GEORGIA, 92 * 2)
    body = ImageFont.truetype(GEORGIA, 38 * 2)
    x = 480 * 2
    draw.text((x, 215 * 2), "Dialect Money", font=title, fill=PAPER)
    draw.rectangle([x, 334 * 2, x + 64 * 2, 337 * 2], fill=BRASS)
    draw.text((x, 358 * 2), "Singapore money guidance,", font=body, fill="#a2988c")
    draw.text((x, 406 * 2), "spoken in your dialect.", font=body, fill="#a2988c")

    img.resize((1200, 630), Image.LANCZOS).save(path, "PNG")


def main():
    OUT.mkdir(exist_ok=True)

    write_mark_svg(OUT / "mark.svg", BRASS, BRASS)
    write_mark_svg(OUT / "mark-ink.svg", INK, INK)
    write_mark_svg(OUT / "icon-tile.svg", BRASS, BRASS, bg=INK)
    write_logo_svg(OUT / "logo.svg", BRASS, INK)
    write_logo_svg(OUT / "logo-on-dark.svg", BRASS, PAPER)

    # 话 is an eight-stroke character. Inside a ring it silts up below ~48px,
    # so small sizes drop the ring and give the glyph the whole tile.
    for size in (16, 32, 48, 64):
        draw_mark(size, BRASS, BRASS, bg=INK, tile_radius=0.18,
                  ring=(size >= 48)).save(OUT / f"favicon-{size}.png", "PNG")

    write_mark_svg(OUT / "mark-small.svg", BRASS, BRASS, ring=False)

    ico = draw_mark(64, BRASS, BRASS, bg=INK, tile_radius=0.18, ring=False)
    ico.save(OUT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

    # iOS masks its own corners, so ship a full square.
    draw_mark(180, BRASS, BRASS, bg=INK).save(OUT / "apple-touch-icon.png", "PNG")
    draw_mark(512, BRASS, BRASS, bg=INK, tile_radius=0.225).save(
        OUT / "icon-512.png", "PNG")
    draw_mark(512, BRASS, BRASS).save(OUT / "mark-512-transparent.png", "PNG")

    draw_og_card(OUT / "og-card.png")

    for f in sorted(OUT.iterdir()):
        print(f"{f.name:32} {f.stat().st_size / 1024:7.1f} KB")


if __name__ == "__main__":
    main()
