#!/usr/bin/env python3
"""THE WORLD TODAY - Friday 20 November 2026 in one image.

Entry program for make.fun bounty "news-image-20261120"
("Sum up 20 November's world news in one image").

The program draws a one-page newspaper-style summary of the world's news of
Friday 20 November 2026 and writes it to $MAKEFUN_OUTPUT_DIR/entry.png
(default /output/entry.png).  Pure Python standard library only: the grader
runs this file with python3.13 in the stock python image, with no network,
so the news is embedded below as data and the PNG is rendered pixel by pixel
and encoded with zlib.  The run is fully deterministic: no clock, no random,
no network - two runs write identical bytes.

TO UPDATE THE NEWS (final pass on the evening of 20 Nov): edit only the NEWS
structure directly below; the layout code further down never changes.
"""

import os
import struct
import zlib
from math import isqrt

# --------------------------------------------------------------------------
# THE NEWS OF FRIDAY 20 NOVEMBER 2026  (morning snapshot - refresh tonight)
# All strings are UPPERCASE; the built-in font covers A-Z 0-9 and .,'-&:!?/()%$
# --------------------------------------------------------------------------

NEWS = {
    "kicker_top": "ONE IMAGE · ONE DAY · THE WHOLE WORLD",
    "title": "THE WORLD TODAY",
    "date_line": "FRIDAY · 20 NOVEMBER 2026",
    "lead": {
        "kicker": "SHENZHEN · APEC SUMMIT - GEOPOLITICS",
        "headline": ["TRUMP, XI & PUTIN", "MEET IN CHINA"],
        "body": [
            "THE LEADERS OF THE US, CHINA AND RUSSIA SAT",
            "DOWN TOGETHER FOR THE FIRST TIME IN HISTORY,",
            "ISSUED A JOINT PEACE DECLARATION AND TALKED",
            "ABOUT UKRAINE. NO BIG BREAKTHROUGH EMERGED.",
        ],
        "flag_caption": "USA · CHINA · RUSSIA",
    },
    "court": {
        "kicker": "THE HAGUE · WORLD COURT - LAW & RIGHTS",
        "headline": ["MYANMAR COMMITTED GENOCIDE", "AGAINST THE ROHINGYA, ICJ RULES"],
        "body": [
            "FIRST TIME THE WORLD COURT HAS HELD A STATE RESPONSIBLE",
            "FOR GENOCIDE. THE CASE WAS BROUGHT BY GAMBIA.",
        ],
    },
    "panels": [
        {
            "kicker": "BUSINESS · NEW YORK",
            "headline": ["ANTHROPIC IPO IS", "LARGEST IN HISTORY"],
            "body": [
                "AI FIRM RAISES $81BN AT A",
                "$1.5 TRILLION VALUE; SHARES",
                "CLOSE AT $97, STOCKS FALL 2%",
            ],
            "icon": "chart",
        },
        {
            "kicker": "WASHINGTON · WAR POWERS",
            "headline": ["SENATE BACKS TRUMP", "ON IRAN WAR, 51-48"],
            "body": [
                "SENATORS REJECT A MOVE TO",
                "END THE IRAN WAR. TRUMP",
                "PUSHES DECISION TO 2027.",
            ],
            "icon": "vote",
        },
        {
            "kicker": "DEEP SPACE · NASA",
            "headline": ["VOYAGER 1 NOW ONE", "LIGHT-DAY FROM EARTH"],
            "body": [
                "ITS RADIO SIGNAL NOW TAKES A",
                "FULL DAY TO REACH US - A FIRST",
                "FOR ANY HUMAN-MADE OBJECT.",
            ],
            "icon": "probe",
        },
        {
            "kicker": "INDIA · CYCLONE AKVAN",
            "headline": ["300,000 EVACUATED", "AS CYCLONE NEARS"],
            "body": [
                "423 RESCUE TEAMS DEPLOYED IN",
                "ODISHA AND ANDHRA PRADESH AS",
                "AKVAN POUNDS THE COAST.",
            ],
            "icon": "cyclone",
        },
    ],
    "minis": [
        ["SENEGAL - DOZENS MISSING AS", "MIGRANT BOAT CAPSIZES AT SEA"],
        ["GAZA - ISRAEL BEGINS GROUND", "OPERATION IN CENTRAL GAZA"],
    ],
    "ticker": [
        "ALSO TODAY: EUROPE READY FOR TALKS WITH RUSSIA ON UKRAINE WAR",
        "HAYABUSA2 ABORTS LANDING · SEOUL COURT CLEARS EX-PM HAN · FIJI DROUGHT DISASTER",
    ],
    "footer": "FRIDAY 20 NOVEMBER 2026 - THE DAY'S WORLD NEWS IN ONE IMAGE",
}

# --------------------------------------------------------------------------
# 5x7 bitmap font (rows of 5 pixels), drawn by this program at any scale.
# --------------------------------------------------------------------------

FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "2": (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    "3": (".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".....", "..#.."),
    ",": (".....", ".....", ".....", ".....", ".....", "..#..", ".#..."),
    "'": ("..#..", "..#..", ".....", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    ":": (".....", "..#..", ".....", ".....", ".....", "..#..", "....."),
    ";": (".....", "..#..", ".....", ".....", ".....", "..#..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#...", "#..##"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "·": (".....", ".....", ".....", "..#..", ".....", ".....", "....."),
}

# --------------------------------------------------------------------------
# Framebuffer renderer.  Design space is 1024x1024; everything is drawn on a
# 2x supersampled canvas and box-downsampled, which smooths the artwork.
# --------------------------------------------------------------------------

SS = 2                      # supersampling factor
W = 1024                    # final image size (max allowed: 1024x1024)
CW = W * SS                 # canvas size
PX = bytearray(CW * CW * 3)

PAPER = (247, 242, 231)
INK = (20, 22, 26)
RED = (178, 34, 28)
NAVY = (27, 58, 99)
TEAL = (13, 107, 110)
GOLD = (176, 124, 16)
GRAY = (96, 102, 112)
PANEL_BG = (239, 233, 216)
COURT_BG = (231, 235, 239)
WHITE = (255, 255, 255)
SKY = (214, 226, 238)


def _set(px, py, rgb):
    if 0 <= px < CW and 0 <= py < CW:
        i = (py * CW + px) * 3
        PX[i] = rgb[0]
        PX[i + 1] = rgb[1]
        PX[i + 2] = rgb[2]


def rect(x, y, w, h, rgb):
    """Filled rectangle in design coordinates."""
    x0, y0 = int(x * SS), int(y * SS)
    x1, y1 = int((x + w) * SS), int((y + h) * SS)
    if x1 <= 0 or y1 <= 0 or x0 >= CW or y0 >= CW:
        return
    x0, y0 = max(x0, 0), max(y0, 0)
    x1, y1 = min(x1, CW), min(y1, CW)
    row = bytes(rgb) * (x1 - x0)
    for py in range(y0, y1):
        i = (py * CW + x0) * 3
        PX[i:i + len(row)] = row


def circle(cx, cy, r, rgb):
    """Filled circle in design coordinates."""
    cx, cy, r = cx * SS, cy * SS, r * SS
    ri = int(r)
    for dy in range(-ri, ri + 1):
        half = isqrt(max(0, ri * ri - dy * dy))
        y = int(cy) + dy
        if 0 <= y < CW:
            x0 = max(0, int(cx) - half)
            x1 = min(CW - 1, int(cx) + half)
            row = bytes(rgb) * (x1 - x0 + 1)
            i = (y * CW + x0) * 3
            PX[i:i + len(row)] = row


def ring(cx, cy, r, t, rgb):
    circle(cx, cy, r, rgb)
    circle(cx, cy, max(0.1, r - t), PAPER if rgb != PAPER else INK)


def line(x0, y0, x1, y1, t, rgb):
    """Thick line in design coordinates (t = thickness in design px)."""
    steps = int(max(abs(x1 - x0), abs(y1 - y0)) * SS) + 1
    r = t / 2.0
    for i in range(steps + 1):
        f = i / steps
        rect(x0 + (x1 - x0) * f - r, y0 + (y1 - y0) * f - r, t, t, rgb)


def poly(points, rgb):
    """Filled polygon in design coordinates (point-in-polygon per pixel)."""
    pts = [(x * SS, y * SS) for x, y in points]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1 = max(0, int(min(xs))), min(CW - 1, int(max(xs)))
    y0, y1 = max(0, int(min(ys))), min(CW - 1, int(max(ys)))
    n = len(pts)
    for py in range(y0, y1 + 1):
        for px in range(x0, x1 + 1):
            inside = False
            j = n - 1
            for i in range(n):
                xi, yi = pts[i]
                xj, yj = pts[j]
                if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi:
                    inside = not inside
                j = i
            if inside:
                _set(px, py, rgb)


def star(cx, cy, r, rgb):
    """Five-pointed star."""
    import math
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    poly(pts, rgb)


def text_w(s, scale):
    return len(s) * 6 * scale


def text(x, y, s, scale, rgb, bold=False, center_in=None):
    """Draw text; glyphs are 5x7, advance 6 units.  y is the top."""
    if center_in is not None:
        x = center_in[0] + (center_in[1] - center_in[0] - text_w(s, scale)) // 2
    for ch in s:
        glyph = FONT.get(ch, FONT[" "])
        for gy, rowbits in enumerate(glyph):
            for gx, bit in enumerate(rowbits):
                if bit == "#":
                    rect(x + gx * scale, y + gy * scale, scale, scale, rgb)
                    if bold:
                        rect(x + gx * scale + scale, y + gy * scale, scale, scale, rgb)
        x += 6 * scale


def text_lines(x, y, lines, scale, rgb, leading, bold=False):
    for ln in lines:
        text(x, y, ln, scale, rgb, bold=bold)
        y += 7 * scale + leading
    return y


# --------------------------------------------------------------------------
# Illustrations (all drawn by code - no photos, no downloaded art)
# --------------------------------------------------------------------------

def flag_us(x, y, w, h):
    rect(x, y, w, h, WHITE)
    sh = h / 13.0
    for i in range(0, 13, 2):
        rect(x, y + i * sh, w, sh + 0.6, (176, 34, 44))
    rect(x, y, w * 0.44, sh * 7, NAVY)
    for r in range(3):
        for c in range(4):
            circle(x + 8 + c * (w * 0.44 - 14) / 3.0, y + 8 + r * (sh * 7 - 16) / 2.0, 2.2, WHITE)


def flag_cn(x, y, w, h):
    rect(x, y, w, h, (222, 41, 16))
    star(x + w * 0.22, y + h * 0.28, h * 0.20, (255, 222, 0))
    for dx, dy in ((0.42, 0.14), (0.47, 0.30), (0.47, 0.47), (0.42, 0.62)):
        circle(x + w * dx, y + h * dy, 3.0, (255, 222, 0))


def flag_ru(x, y, w, h):
    rect(x, y, w, h / 3.0 + 0.6, WHITE)
    rect(x, y + h / 3.0, w, h / 3.0 + 0.6, (0, 57, 166))
    rect(x, y + 2 * h / 3.0, w, h / 3.0 + 0.6, (213, 43, 30))


def draw_flags(x, y, w, h):
    """The summit illustration: three flags over a conference table."""
    rect(x, y, w, h, SKY)
    rect(x, y, w, h, SKY)
    # sun / backdrop circle
    circle(x + w * 0.82, y + h * 0.24, 20, (245, 205, 92))
    fw, fh = 104, 68
    gap = (w - 3 * fw) / 4.0
    fy = y + 34
    for i, fn in enumerate((flag_us, flag_cn, flag_ru)):
        fx = x + gap + i * (fw + gap)
        line(fx + fw / 2, fy - 14, fx + fw / 2, y + h - 58, 3, INK)
        fn(fx, fy, fw, fh)
        circle(fx + fw / 2, fy - 17, 4, GOLD)
    # conference table (arc) and three seats
    ty = y + h - 52
    rect(x + 26, ty, w - 52, 10, NAVY)
    rect(x + 40, ty + 10, w - 80, 6, INK)
    for i in range(3):
        cx = x + gap + i * (fw + gap) + fw / 2
        circle(cx, ty - 12, 9, INK)
    text(x, y + h - 30, NEWS["lead"]["flag_caption"], 2, INK,
         center_in=(x, x + w))


def draw_scales(x, y, s):
    """Scales of justice icon inside a box of size s (design px)."""
    cx = x + s / 2.0
    line(cx, y + 10, cx, y + s - 18, 4, NAVY)
    line(x + 12, y + 18, x + s - 12, y + 18, 4, NAVY)
    circle(cx, y + 12, 5, NAVY)
    for px in (x + 16, x + s - 16):
        line(px, y + 18, px - 10, y + 46, 2, NAVY)
        line(px, y + 18, px + 10, y + 46, 2, NAVY)
        # pan: shallow bowl
        for t in range(0, 9):
            wdt = 22 - abs(t - 4) * 1.2
            rect(px - wdt / 2, y + 44 + t * 0.9, wdt, 1.6, NAVY)
    rect(cx - 16, y + s - 16, 32, 5, NAVY)
    rect(cx - 10, y + s - 22, 20, 6, NAVY)


def icon_chart(x, y):
    base = y + 62
    for i, bh in enumerate((18, 30, 44, 60)):
        rect(x + 4 + i * 18, base - bh, 13, bh, TEAL if i < 3 else GOLD)
    line(x + 2, base - 14, x + 66, base - 62, 3, RED)
    poly([(x + 66, y + 2), (x + 56, y + 4), (x + 64, y + 12)], RED)
    rect(x, base + 3, 74, 3, INK)


def icon_vote(x, y):
    text(x + 2, y + 2, "51", 2, NAVY, bold=True)
    rect(x + 30, y + 4, 44, 10, NAVY)
    text(x + 2, y + 26, "48", 2, RED, bold=True)
    rect(x + 30, y + 28, 41, 10, RED)
    rect(x, y + 50, 74, 3, INK)
    text(x + 2, y + 56, "SENATE", 1, GRAY)


def icon_probe(x, y):
    import math
    # dish
    circle(x + 24, y + 22, 15, NAVY)
    circle(x + 28, y + 22, 12, SKY)
    rect(x + 30, y + 30, 26, 5, INK)          # bus
    line(x + 44, y + 33, x + 70, y + 58, 3, INK)   # boom
    rect(x + 66, y + 54, 9, 9, GOLD)          # RTG
    line(x + 36, y + 34, x + 20, y + 56, 2, INK)   # antenna mast
    for sx, sy in ((58, 8), (68, 20), (52, 30), (72, 40)):
        circle(x + sx, y + sy, 1.8, GOLD)
    for r in (22, 30):                        # signal arcs toward Earth (left-down)
        for a in range(200, 261, 10):
            circle(x + 24 + r * math.cos(math.radians(a)) * 0.6,
                   y + 22 + r * math.sin(math.radians(a)) * 0.6, 1.6, TEAL)


def icon_cyclone(x, y):
    import math
    cx, cy = x + 37, y + 32
    for i in range(150):
        f = i / 150.0
        ang = f * 4.6 * math.pi
        r = 4 + f * 27
        circle(cx + r * math.cos(ang), cy + r * math.sin(ang) * 0.82, 2.6, TEAL)
    circle(cx, cy, 4, NAVY)
    for rx in (8, 26, 44, 60):                # rain
        line(x + rx, y + 66, x + rx - 5, y + 76, 2.4, NAVY)


ICONS = {"chart": icon_chart, "vote": icon_vote, "probe": icon_probe,
         "cyclone": icon_cyclone}

# --------------------------------------------------------------------------
# Layout
# --------------------------------------------------------------------------

M = 30                      # page margin
CWID = W - 2 * M            # content width


def draw():
    rect(0, 0, W, W, PAPER)
    n = NEWS

    # --- masthead ------------------------------------------------------
    text(M, 24, n["kicker_top"], 2, GRAY, center_in=(0, W))
    text(M, 48, n["title"], 9, INK, bold=True, center_in=(0, W))
    rect(M, 122, CWID, 5, RED)
    rect(M, 131, CWID, 2, INK)
    rect(0, 146, W, 52, INK)
    text(M, 159, n["date_line"], 4, PAPER, bold=True, center_in=(0, W))

    # --- lead story ----------------------------------------------------
    ly = 210
    text(M, ly, n["lead"]["kicker"], 2, RED, bold=True)
    text_lines(M, ly + 22, n["lead"]["headline"], 5, INK, 8, bold=True)
    text_lines(M, ly + 122, n["lead"]["body"], 2, INK, 5)
    draw_flags(618, ly, 376, 224)
    rect(M, 442, CWID, 2, INK)

    # --- world court band ----------------------------------------------
    cy = 450
    rect(M, cy, CWID, 152, COURT_BG)
    rect(M, cy, CWID, 3, NAVY)
    draw_scales(M + 14, cy + 26, 100)
    tx = M + 136
    text(tx, cy + 14, n["court"]["kicker"], 2, NAVY, bold=True)
    text_lines(tx, cy + 36, n["court"]["headline"], 4, INK, 6, bold=True)
    text_lines(tx, cy + 106, n["court"]["body"], 2, INK, 5)
    rect(M, 610, CWID, 2, INK)

    # --- four panels ----------------------------------------------------
    py = 618
    ph = 134
    pw = (CWID - 20) // 2
    for row in range(2):
        for col in range(2):
            p = n["panels"][row * 2 + col]
            x = M + col * (pw + 20)
            y = py + row * (ph + 10)
            rect(x, y, pw, ph, PANEL_BG)
            rect(x, y, pw, 4, (RED, TEAL, NAVY, GOLD)[row * 2 + col])
            ICONS[p["icon"]](x + pw - 86, y + 26)
            text(x + 14, y + 10, p["kicker"], 2, GRAY, bold=True)
            text_lines(x + 14, y + 28, p["headline"], 3, INK, 5, bold=True)
            text_lines(x + 14, y + 80, p["body"], 2, INK, 3)

    # --- two mini stories ------------------------------------------------
    my = 908
    for i, lines in enumerate(n["minis"]):
        x = M + i * (pw + 20)
        rect(x, my + 4, 12, 12, RED)
        text_lines(x + 22, my, lines, 2, INK, 4, bold=True)

    # --- ticker ----------------------------------------------------------
    ty = 948
    rect(M, ty, CWID, 2, INK)
    text(M, ty + 8, n["ticker"][0], 2, INK, center_in=(0, W))
    text(M, ty + 26, n["ticker"][1], 2, INK, center_in=(0, W))

    # --- footer ----------------------------------------------------------
    fy = 996
    rect(M, fy, CWID, 3, RED)
    text(M, fy + 7, n["footer"], 2, GRAY, center_in=(0, W))


# --------------------------------------------------------------------------
# PNG output (deterministic: fixed filter, fixed zlib stream)
# --------------------------------------------------------------------------

def downsample():
    out = bytearray(W * W * 3)
    for y in range(W):
        for x in range(W):
            i = (y * W + x) * 3
            acc0 = acc1 = acc2 = 0
            for dy in range(SS):
                base = ((y * SS + dy) * CW + x * SS) * 3
                for dx in range(SS):
                    j = base + dx * 3
                    acc0 += PX[j]
                    acc1 += PX[j + 1]
                    acc2 += PX[j + 2]
            q = SS * SS
            out[i] = acc0 // q
            out[i + 1] = acc1 // q
            out[i + 2] = acc2 // q
    return out


def write_png(path, pixels):
    raw = bytearray()
    stride = W * 3
    for y in range(W):
        raw.append(0)
        raw += pixels[y * stride:(y + 1) * stride]

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, W, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    draw()
    pixels = downsample()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    size = write_png(os.path.join(outdir, "entry.png"), pixels)
    print("entry.png written: %d bytes (%dx%d)" % (size, W, W))


if __name__ == "__main__":
    main()
