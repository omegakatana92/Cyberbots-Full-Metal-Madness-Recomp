#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Draws the port's icon, tools/release/cybots.png (256x256): a mecha's head, front on, over the
port's own navy and orange. Everything here is arithmetic — no artwork from the game is used or
copied, so the releases ship none. Rebuild it with:

    python3 tools/release/make-icon.py

Each shape is rasterised with one bit per pixel at SS-times the final size, then averaged down, which
is what gives the edges their smoothness.
"""

import os
import struct
import zlib

W = H = 256
SS = 3          # sub-pixels per pixel, per axis
SW = W * SS     # the size the shapes are drawn at

# --- palette -------------------------------------------------------------------------------------
SKY_TOP = (8, 13, 30)
SKY_BOTTOM = (26, 38, 74)
GLOW = (120, 62, 24)           # a warm light behind the head
INK = (4, 6, 14)               # the outline
ARMOUR = (232, 138, 46)
ARMOUR_DARK = (176, 92, 26)    # the jaw and the collar, a step down from the helmet
VISOR = (10, 14, 26)
EYE = (150, 236, 255)


def mask_from_spans(rows):
    """Build a mask from {y: [(x0, x1), ...]} half-open spans, in final-pixel coordinates."""
    m = [0] * SW
    for y, spans in rows.items():
        ys = range(max(0, y * SS), min(SW, (y + 1) * SS))
        bits = 0
        for x0, x1 in spans:
            xa, xb = max(0, int(x0 * SS)), min(SW, int(x1 * SS))
            if xb > xa:
                bits |= ((1 << (xb - xa)) - 1) << xa
        for yy in ys:
            m[yy] |= bits
    return m


def polygon(points):
    """A filled polygon, as a mask."""
    spans = {}
    ys = [p[1] for p in points]
    for y in range(int(min(ys)), int(max(ys)) + 1):
        yc = y + 0.5
        xs = []
        for i in range(len(points)):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % len(points)]
            if (y0 <= yc < y1) or (y1 <= yc < y0):
                xs.append(x0 + (yc - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        spans[y] = [(xs[i], xs[i + 1]) for i in range(0, len(xs) - 1, 2)]
    return mask_from_spans(spans)


def ellipse(cx, cy, rx, ry):
    """A filled ellipse, as a mask."""
    spans = {}
    for y in range(int(cy - ry), int(cy + ry) + 1):
        dy = (y + 0.5 - cy) / ry
        if abs(dy) >= 1:
            continue
        dx = rx * (1 - dy * dy) ** 0.5
        spans[y] = [(cx - dx, cx + dx)]
    return mask_from_spans(spans)


def rect(x0, y0, x1, y1):
    return polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


def union(*masks):
    out = [0] * SW
    for m in masks:
        for y in range(SW):
            out[y] |= m[y]
    return out


def spread(mask, r):
    """Grow a mask by r sub-pixels (a square brush: indistinguishable from a round one here)."""
    out = mask[:]
    for dy in range(-r, r + 1):
        for y in range(SW):
            sy = y + dy
            if 0 <= sy < SW:
                out[y] |= mask[sy]
    for y in range(SW):
        row = out[y]
        acc = 0
        for dx in range(-r, r + 1):
            acc |= row << dx if dx > 0 else row >> -dx
        out[y] = acc & ((1 << SW) - 1)
    return out


def minus(a, b):
    return [a[y] & ~b[y] for y in range(SW)]


def coverage(mask):
    """How much of each final pixel is filled, 0..1."""
    cov = [[0.0] * W for _ in range(H)]
    group = (1 << SS) - 1
    for y in range(H):
        rows = mask[y * SS:(y + 1) * SS]
        for x in range(W):
            sh = x * SS
            n = 0
            for row in rows:
                n += bin((row >> sh) & group).count("1")
            cov[y][x] = n / float(SS * SS)
    return cov


# --- the shapes -----------------------------------------------------------------------------------

def helmet_mask():
    """The helmet, front on and symmetrical about x=128: a crest, a dome, two ear fins and a jaw."""
    return polygon([
        (122, 38), (134, 38),                       # the crest
        (134, 68), (150, 58),                       # down the crest, out along the dome
        (170, 74), (178, 98),                       # the upper right of the helmet
        (196, 112), (198, 146),                     # the ear fin
        (176, 154), (170, 182),                     # the cheek and the jaw
        (146, 202), (110, 202),                     # the chin
        (86, 182), (80, 154),                       # and the same on the left
        (58, 146), (60, 112),
        (78, 98), (86, 74),
        (106, 58), (122, 68),
    ])


def visor_mask():
    """The band across the face."""
    return polygon([(80, 118), (176, 118), (180, 138), (172, 152), (84, 152), (76, 138)])


def eye_mask():
    """Two slanted slits inside the visor, mirrored about x=128."""
    left = polygon([(90, 127), (122, 132), (122, 143), (94, 139)])
    right = polygon([(166, 127), (134, 132), (134, 143), (162, 139)])
    return union(left, right)


def vent_mask():
    """The mouth grill on the chin."""
    return union(rect(112, 176, 120, 196), rect(124, 176, 132, 196), rect(136, 176, 144, 196))


def background():
    """The port's navy, with a warm light behind the head."""
    img = [[[0.0] * 3 for _ in range(W)] for _ in range(H)]
    for y in range(H):
        t = y / float(H - 1)
        base = [SKY_TOP[i] + (SKY_BOTTOM[i] - SKY_TOP[i]) * t for i in range(3)]
        for x in range(W):
            d = (((x - 128) ** 2 + (y - 132) ** 2) ** 0.5) / 165.0
            glow = max(0.0, 1.0 - d) ** 2
            img[y][x] = [base[i] + (GLOW[i] - base[i]) * glow * 0.55 for i in range(3)]
    return img


def over(img, cov, colour):
    for y in range(H):
        for x in range(W):
            a = cov[y][x]
            if a:
                px = img[y][x]
                img[y][x] = [px[i] + (colour[i] - px[i]) * a for i in range(3)]


def main():
    helmet = helmet_mask()
    visor = visor_mask()
    eyes = eye_mask()
    vent = vent_mask()
    jaw = polygon([(170, 182), (146, 202), (110, 202), (86, 182), (86, 176), (170, 176)])
    collar = polygon([(104, 200), (152, 200), (160, 216), (96, 216)])

    # The outline: what the whole head grew over, minus the head itself.
    head = union(helmet, visor, collar)
    ring = minus(spread(head, 7), spread(head, 3))

    img = background()
    over(img, coverage(ring), INK)
    over(img, coverage(collar), ARMOUR_DARK)
    over(img, coverage(helmet), ARMOUR)
    over(img, coverage(jaw), ARMOUR_DARK)
    over(img, coverage(visor), VISOR)
    over(img, coverage(vent), VISOR)
    over(img, coverage(eyes), EYE)

    rows = []
    for y in range(H):
        row = bytearray()
        for x in range(W):
            for i in range(3):
                row.append(max(0, min(255, int(img[y][x][i] + 0.5))))
        rows.append(row)

    raw = b"".join(b"\x00" + bytes(r) for r in rows)

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cybots.png")
    with open(out, "wb") as f:
        f.write(png)
    print("wrote %s (%d bytes)" % (out, len(png)))


if __name__ == "__main__":
    main()
