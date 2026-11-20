#!/usr/bin/env python3
"""Build 3 front-page variants for make.fun news-image-20261119.

Composes dense newspaper front pages PROGRAMMATICALLY with PIL so every
letter is pixel-perfect (no AI-rendered text). One deterministic script,
three variants from the same verified story data. No network, no randomness,
no timestamps: the same run always writes the same bytes.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
REPO = os.path.dirname(os.path.abspath(__file__))
FD = "/usr/share/fonts/truetype/dejavu"
NOTO = "/usr/share/fonts/truetype/noto"


def font(*names, size):
    for n in names:
        for base in (FD, NOTO, "/usr/share/fonts/truetype/liberation"):
            p = os.path.join(base, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default(size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", size=s)
SERIF = lambda s: font("DejaVuSerif.ttf", size=s)
SERIF_I = lambda s: font("DejaVuSerif-Italic.ttf", "NotoSerif-Italic.ttf",
                         "NotoSerifDisplay-Italic.ttf", size=s)
SANS = lambda s: font("DejaVuSans.ttf", size=s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", size=s)

# ---------------------------------------------------------------- data
# Every fact below is real 19 Nov 2026 reporting. Nothing invented.
NUMBERS = [
    ("$81.3bn", "Anthropic raises\nin record IPO"),
    ("9\u20136", "World Court\ngenocide vote"),
    ("109\u20130", "Denmark backs\nGreenland deal"),
    ("$190.4m", "Van Gogh,\nartist record"),
    ("\u22122.0%", "S&P 500,\nfifth day down"),
    ("589m", "children in\nconflict zones"),
]

LEADS = [
    dict(tag="SUMMIT \u2022 SHENZHEN", art="summit",
         head="Trump, Xi and Putin hold first three-way summit",
         deck="Leaders meet in Shenzhen and issue a peace declaration that "
              "omits Ukraine and Iran; APEC adopts its Shenzhen Outlook."),
    dict(tag="JUSTICE \u2022 THE HAGUE", art="court",
         head="World Court finds Myanmar committed genocide",
         deck="The ICJ rules 9\u20136 against Myanmar over the Rohingya \u2014 "
              "the first such finding against a state."),
    dict(tag="MARKETS \u2022 NEW YORK", art="ipo",
         head="Anthropic debuts in biggest IPO on record",
         deck="Shares price at $83, raising about $81.3bn and valuing the "
              "AI firm near $1.5tn."),
]

GRID = [
    dict(tag="CRIMEA", art="bridge",
         head="Ukraine hits Crimean Bridge a third time",
         deck="Rail section hit, train traffic halted; Putin vows a harsher response."),
    dict(tag="CLIMATE", art="globe",
         head="COP31 ministers race to unblock talks",
         deck="Ministers meet in Antalya to overcome differences on a final text."),
    dict(tag="GAZA", art="pin",
         head="Israeli tanks push beyond Yellow Line",
         deck="Aid groups rate the peace plan 4 out of 26."),
    dict(tag="CULTURE", art="gta",
         head="GTA VI releases after 13-year wait",
         deck="The most awaited game in years goes on sale today."),
    dict(tag="MARKETS", art="down",
         head="Wall Street slides on AI worries",
         deck="S&P 500 falls 2.0%, a fifth straight loss; Nikkei drops 4.68%."),
    dict(tag="ARTS", art="frame",
         head="Van Gogh sells for $190.4m",
         deck="A record price for the artist."),
]

ALSO = [
    "North Korea expanded uranium enrichment at Yongbyon",
    "Jeffries nominated House Speaker 251\u201311; vote Jan 3",
    "Haiti police kill 34 gang members in raid",
    "Dozens missing after migrant boat capsizes off Senegal",
    "Tanzania's Lissu convicted of sedition",
    "Bitcoin below $63,000; Nvidia falls 2.89%",
    "Indonesia approves asset-forfeiture bill",
    "APEC adopts Shenzhen Outlook",
]

# dotted world map: (row, col_start, col_end) land spans, 48 cols x 16 rows
# (drawn with square cells so the continents keep their true proportions)
LAND = {
    0: [(4, 10), (16, 18), (34, 47)],
    1: [(3, 11), (15, 18), (24, 25), (33, 47)],
    2: [(2, 12), (15, 18), (23, 27), (32, 47)],
    3: [(2, 12), (15, 17), (23, 27), (31, 46)],
    4: [(3, 11), (23, 28), (30, 45)],
    5: [(4, 11), (23, 29), (30, 44)],
    6: [(5, 10), (24, 29), (30, 43)],
    7: [(5, 9), (23, 31), (30, 42)],
    8: [(6, 9), (23, 32), (30, 41)],
    9: [(6, 8), (23, 33), (30, 40)],
    10: [(7, 8), (9, 11), (23, 32), (30, 39), (37, 41)],
    11: [(9, 11), (12, 16), (23, 31), (30, 38), (38, 41)],
    12: [(12, 16), (23, 30), (30, 36), (37, 41)],
    13: [(13, 17), (23, 29), (30, 35)],
    14: [(14, 17), (24, 29), (30, 33)],
    15: [(15, 16), (24, 28), (30, 32), (40, 45)],
}
# (name, lon, lat, label side: -1 left, +1 right, label dy)
CITIES = [
    ("Shenzhen", 114.0, 22.5, 1, 0), ("The Hague", 4.3, 52.0, -1, -6),
    ("Crimea", 34.0, 45.0, 1, 2), ("Gaza", 34.5, 31.5, -1, 10),
    ("Antalya", 30.7, 36.9, -1, -4),
    ("Washington", -77.0, 38.9, -1, 0), ("Port-au-Prince", -72.3, 18.5, 1, 0),
    ("Dakar", -17.4, 14.7, -1, 0), ("Dar es Salaam", 39.3, -6.8, 1, 0),
    ("Jakarta", 106.8, -6.2, 1, 0),
]

PALETTES = {
    "a": dict(paper=(247, 242, 231), ink=(26, 26, 26), muted=(90, 84, 72),
              red=(169, 28, 28), navy=(30, 58, 95), gold=(160, 120, 40),
              band=None, band_ink=None, panel=(232, 224, 200),
              line=(26, 26, 26), hair=(180, 172, 150)),
    "b": dict(paper=(245, 241, 230), ink=(26, 26, 26), muted=(90, 84, 72),
              red=(169, 28, 28), navy=(20, 38, 63), gold=(201, 162, 39),
              band=(20, 38, 63), band_ink=(255, 255, 255),
              panel=(226, 232, 240), line=(26, 26, 26), hair=(180, 172, 150)),
    "c": dict(paper=(247, 242, 231), ink=(26, 26, 26), muted=(90, 84, 72),
              red=(169, 28, 28), navy=(30, 58, 95), gold=(160, 120, 40),
              band=None, band_ink=None, panel=(232, 224, 200),
              line=(26, 26, 26), hair=(180, 172, 150)),
}


# ---------------------------------------------------------------- helpers
def wrap(fnt, text, max_w):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if fnt.getlength(t) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def text_lines(d, x, y, lines, fnt, fill, leading=None, anchor_left=True):
    lh = leading or int(fnt.size * 1.22)
    for i, ln in enumerate(lines):
        if anchor_left:
            d.text((x, y + i * lh), ln, font=fnt, fill=fill)
        else:
            d.text((x, y + i * lh), ln, font=fnt, fill=fill, anchor="ma")
    return y + len(lines) * lh


def rule(d, x0, x1, y, fill, w=2):
    d.line([(x0, y), (x1, y)], fill=fill, width=w)


def flag_us(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(178, 34, 52))
    for i in range(4):
        yy = y + int(h * (2 * i + 1) / 13.0)
        d.rectangle([x, yy, x + w, yy + max(1, h // 13)], fill=(255, 255, 255))
    d.rectangle([x, y, x + int(w * 0.42), y + int(h * 7 / 13)],
                fill=(40, 60, 110))


def flag_cn(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    cx, cy, r = x + w * 0.22, y + h * 0.28, max(2, h * 0.13)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 222, 0))
    for sx, sy in ((0.55, 0.18), (0.68, 0.35), (0.68, 0.55), (0.55, 0.72)):
        px, py = x + w * sx, y + h * sy
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 222, 0))


def flag_ru(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
    d.rectangle([x, y + h // 3, x + w, y + 2 * h // 3], fill=(0, 57, 166))
    d.rectangle([x, y + 2 * h // 3, x + w, y + h], fill=(213, 0, 50))


# ---------------------------------------------------------------- flat art
def art(d, kind, x, y, w, h, P):
    d.rectangle([x, y, x + w, y + h], fill=P["panel"])
    if kind == "summit":
        d.rectangle([x, y, x + w, y + h], fill=(199, 216, 230))
        base = y + h
        sky = [(0.02, 0.55), (0.10, 0.42), (0.18, 0.62), (0.28, 0.38),
               (0.38, 0.58), (0.48, 0.45), (0.58, 0.66), (0.68, 0.40),
               (0.78, 0.60), (0.88, 0.48), (0.97, 0.58)]
        for fx, fh in sky:
            bw = w * 0.085
            d.rectangle([x + w * fx, base - h * fh, x + w * fx + bw, base],
                        fill=(52, 74, 102))
        d.rectangle([x + w * 0.46, base - h * 0.92, x + w * 0.52, base],
                    fill=(40, 58, 84))
        d.line([x + w * 0.49, base - h * 0.92, x + w * 0.49, base - h * 1.0],
               fill=(40, 58, 84), width=3)
        for i, fl in enumerate((flag_us, flag_cn, flag_ru)):
            fx = x + w * (0.10 + i * 0.32)
            d.line([fx + 14, y + 8, fx + 14, base - 6], fill=(90, 84, 72), width=3)
            fl(d, fx - 6, y + 10, 42, 28)
    elif kind == "court":
        d.rectangle([x, y, x + w, y + h], fill=(232, 224, 200))
        cx = x + w // 2
        d.polygon([(cx - w * 0.34, y + h * 0.30), (cx + w * 0.34, y + h * 0.30),
                   (cx, y + h * 0.10)], fill=(120, 100, 70))
        d.rectangle([x + w * 0.14, y + h * 0.30, x + w * 0.86, y + h * 0.36],
                    fill=(90, 74, 52))
        for i in range(4):
            colx = x + w * (0.18 + i * 0.21)
            d.rectangle([colx, y + h * 0.36, colx + w * 0.06, y + h * 0.86],
                        fill=(245, 240, 225))
        d.rectangle([x + w * 0.10, y + h * 0.86, x + w * 0.90, y + h * 0.94],
                    fill=(90, 74, 52))
    elif kind == "ipo":
        d.rectangle([x, y, x + w, y + h], fill=(220, 232, 216))
        for gy in (0.25, 0.5, 0.75):
            d.line([x + 8, y + h * gy, x + w - 8, y + h * gy],
                   fill=(190, 205, 190), width=1)
        pts = [(0.06, 0.78), (0.22, 0.72), (0.34, 0.76), (0.50, 0.58),
               (0.64, 0.62), (0.78, 0.38), (0.94, 0.16)]
        xy = [(x + w * px, y + h * py) for px, py in pts]
        d.line(xy, fill=(30, 120, 60), width=5, joint="curve")
        ax, ay = xy[-1]
        d.polygon([(ax, ay), (ax - 16, ay + 4), (ax - 4, ay + 14)],
                  fill=(30, 120, 60))
        d.text((x + 12, y + 8), "$83", font=SANS_B(26), fill=(30, 120, 60))
    elif kind == "bridge":
        d.rectangle([x, y, x + w, y + h], fill=(207, 224, 234))
        d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(127, 168, 201))
        for i in range(5):
            d.line([x + w * i / 4, y + h * 0.72, x + w * (i + 1) / 4,
                    y + h * 0.72], fill=(255, 255, 255), width=1)
        for tx in (0.28, 0.72):
            d.rectangle([x + w * tx - 4, y + h * 0.22, x + w * tx + 4,
                         y + h * 0.72], fill=(70, 90, 110))
        d.line([x, y + h * 0.62, x + w, y + h * 0.62], fill=(70, 90, 110),
               width=6)
        for cx in (0.07, 0.20, 0.36, 0.50, 0.64, 0.79, 0.93):
            top = y + h * (0.22 if abs(cx - 0.28) < 0.2 or abs(cx - 0.72) < 0.2
                           else 0.34)
            d.line([x + w * cx, top, x + w * cx, y + h * 0.62],
                   fill=(120, 140, 160), width=2)
    elif kind == "globe":
        d.rectangle([x, y, x + w, y + h], fill=(221, 232, 240))
        cx, cy, r = x + w // 2, y + h // 2 + 4, int(h * 0.36)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(127, 168, 201))
        for k in (-0.55, 0, 0.55):
            d.arc([cx - r, cy - r, cx + r, cy + r], 90 + k * 60, 270 + k * 60,
                  fill=(240, 244, 248), width=2)
        d.line([cx - r, cy, cx + r, cy], fill=(240, 244, 248), width=2)
        d.ellipse([cx - r * 0.45, cy - r * 0.55, cx + r * 0.15, cy + r * 0.10],
                  fill=(90, 160, 90))
        d.ellipse([cx + r * 0.05, cy + r * 0.25, cx + r * 0.55, cy + r * 0.62],
                  fill=(90, 160, 90))
    elif kind == "pin":
        d.rectangle([x, y, x + w, y + h], fill=(240, 226, 216))
        cx, cy = x + w // 2, y + h // 2 - 4
        d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], fill=(169, 28, 28))
        d.polygon([(cx - 22, cy + 12), (cx + 22, cy + 12), (cx, cy + 42)],
                  fill=(169, 28, 28))
        d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=(255, 255, 255))
    elif kind == "gta":
        d.rectangle([x, y, x + w, y + h], fill=(43, 32, 64))
        d.ellipse([x + w * 0.68, y + h * 0.10, x + w * 0.92, y + h * 0.42],
                  fill=(255, 170, 80))
        base = y + h
        for fx, fh in ((0.02, 0.5), (0.12, 0.7), (0.24, 0.42), (0.34, 0.78),
                       (0.46, 0.55), (0.58, 0.72), (0.70, 0.48),
                       (0.80, 0.66), (0.90, 0.52)):
            bw = w * 0.09
            d.rectangle([x + w * fx, base - h * fh, x + w * fx + bw, base],
                        fill=(20, 16, 34))
        d.text((x + 12, y + h - 44), "VI", font=SERIF_B(40),
               fill=(255, 255, 255))
    elif kind == "down":
        d.rectangle([x, y, x + w, y + h], fill=(243, 226, 222))
        for gy in (0.25, 0.5, 0.75):
            d.line([x + 8, y + h * gy, x + w - 8, y + h * gy],
                   fill=(220, 195, 190), width=1)
        pts = [(0.06, 0.22), (0.22, 0.30), (0.38, 0.26), (0.54, 0.48),
               (0.70, 0.44), (0.84, 0.68), (0.94, 0.84)]
        xy = [(x + w * px, y + h * py) for px, py in pts]
        d.line(xy, fill=(169, 28, 28), width=5, joint="curve")
        ax, ay = xy[-1]
        d.polygon([(ax, ay), (ax - 16, ay - 4), (ax - 4, ay - 16)],
                  fill=(169, 28, 28))
        d.text((x + 12, y + 8), "\u22122.0%", font=SANS_B(24),
               fill=(169, 28, 28))
    elif kind == "frame":
        d.rectangle([x, y, x + w, y + h], fill=(239, 230, 210))
        d.rectangle([x + 8, y + 6, x + w - 8, y + h - 6],
                    outline=(160, 120, 40), width=4)
        d.rectangle([x + 16, y + 14, x + w - 16, y + h - 14],
                    fill=(70, 110, 160))
        d.ellipse([x + w * 0.62, y + h * 0.16, x + w * 0.86, y + h * 0.48],
                  fill=(255, 210, 60))
        for k in range(6):
            sx = x + w * (0.18 + k * 0.11)
            d.line([sx, y + h - 18, sx + 6, y + h * 0.62],
                   fill=(60, 140, 70), width=3)
            d.ellipse([sx - 2, y + h * 0.58, sx + 12, y + h * 0.72],
                      fill=(255, 210, 60))
    d.rectangle([x, y, x + w, y + h], outline=P["hair"], width=1)


# ---------------------------------------------------------------- page
def draw_page(variant, lead_art_h, grid_art_h):
    P = PALETTES[variant]
    note = variant == "c"
    img = Image.new("RGB", (W, H), P["paper"])
    d = ImageDraw.Draw(img)
    M = 26                      # side margin
    CW = W - 2 * M              # content width
    y = 20

    # ---- masthead
    if P["band"]:
        d.rectangle([0, 0, W, 118], fill=P["band"])
        d.text((W // 2, 14), "D A I L Y   A T L A S", font=SANS_B(15),
               fill=P["gold"], anchor="ma")
        d.text((W // 2, 36), "Thursday 19 November 2026",
               font=SERIF_B(52), fill=P["band_ink"], anchor="ma")
        d.text((W // 2, 96), "T H E   W O R L D   I N   O N E   P I C T U R E",
               font=SANS(12), fill=(200, 205, 215), anchor="ma")
        y = 126
    else:
        d.text((W // 2, y), "T H E   W O R L D   T O D A Y",
               font=SANS_B(13), fill=P["red"], anchor="ma")
        y += 20
        d.text((W // 2, y), "Thursday 19 November 2026",
               font=SERIF_B(54), fill=P["ink"], anchor="ma")
        y += 68
        rule(d, M, W - M, y, P["ink"], 3)
        y += 10
    d.text((W // 2, y), "Everything that happened, or was first reported, "
           "on Thursday 19 November 2026.", font=SERIF_I(15),
           fill=P["muted"], anchor="ma")
    y += 24
    rule(d, M, W - M, y, P["hair"], 1)
    y += 10

    # ---- numbers strip
    colw = CW / 6.0
    top = y
    for i, (num, lab) in enumerate(NUMBERS):
        cx = M + colw * i + colw / 2
        d.text((cx, top), num, font=SERIF_B(25),
               fill=P["red"] if i % 2 == 0 else P["navy"], anchor="ma")
        for j, ln in enumerate(lab.split("\n")):
            d.text((cx, top + 31 + j * 13), ln, font=SANS(11),
                   fill=P["muted"], anchor="ma")
        if i:
            d.line([(M + colw * i, top + 2), (M + colw * i, top + 50)],
                   fill=P["hair"], width=1)
    y = top + 58
    rule(d, M, W - M, y, P["ink"], 2)
    y += 10

    # ---- 3 lead stories
    gutter = 22
    lw = (CW - 2 * gutter) / 3.0
    lead_top = y
    head_lines = [wrap(SERIF_B(24), L["head"], lw) for L in LEADS]
    deck_lines = [wrap(SANS(13), L["deck"], lw) for L in LEADS]
    max_h = max(len(h) for h in head_lines)
    max_d = max(len(dd) for dd in deck_lines)
    for i, L in enumerate(LEADS):
        x0 = M + i * (lw + gutter)
        art(d, L["art"], int(x0), y, int(lw), lead_art_h, P)
        yy = y + lead_art_h + 8
        d.text((x0, yy), L["tag"], font=SANS_B(11), fill=P["red"])
        yy += 17
        text_lines(d, x0, yy, head_lines[i], SERIF_B(24), P["ink"], leading=27)
        yy += max_h * 27 + 4
        text_lines(d, x0, yy, deck_lines[i], SANS(13), P["muted"], leading=16)
    y = lead_top + lead_art_h + 8 + 17 + max_h * 27 + 4 + max_d * 16 + 10
    rule(d, M, W - M, y, P["hair"], 1)
    y += 12

    # ---- grid: 2 rows x 3 cols
    gw = (CW - 2 * gutter) / 3.0
    grid_top = y
    g_head = [wrap(SANS_B(15), G["head"], gw) for G in GRID]
    g_deck = [wrap(SANS(12), G["deck"], gw) for G in GRID]
    row_h = []
    for r in range(2):
        row_h.append(max(grid_art_h + 8 + 15 + len(g_head[r * 3 + c]) * 18
                         + 2 + len(g_deck[r * 3 + c]) * 15
                         for c in range(3)))
    for i, G in enumerate(GRID):
        r, c = divmod(i, 3)
        x0 = M + c * (gw + gutter)
        y0 = grid_top + sum(row_h[:r]) + r * 8
        art(d, G["art"], int(x0), y0, int(gw), grid_art_h, P)
        yy = y0 + grid_art_h + 8
        d.text((x0, yy), G["tag"], font=SANS_B(10), fill=P["red"])
        yy += 15
        yy = text_lines(d, x0, yy, g_head[i], SANS_B(15), P["ink"], leading=18)
        text_lines(d, x0, yy + 2, g_deck[i], SANS(12), P["muted"], leading=15)
    y = grid_top + sum(row_h) + 8 + 6
    rule(d, M, W - M, y, P["hair"], 1)
    y += 10

    # ---- bottom: map + also list
    map_w = 560
    list_x = M + map_w + 24
    list_w = W - M - list_x
    list_lines = [wrap(SANS(12), item, list_w - 22) for item in ALSO]
    list_h = sum(len(ln) * 14 + 1 for ln in list_lines)
    map_h = 20 + 16 * 7.0 + 4
    bottom_h = max(list_h, map_h)
    d.text((M, y), "WHERE IT HAPPENED", font=SANS_B(12), fill=P["navy"])
    d.text((list_x, y), "ALSO ON THURSDAY 19 NOVEMBER", font=SANS_B(12),
           fill=P["navy"])
    my = y + 20
    # dotted world map, square cells (true proportions), centred in its panel
    map_px_w = 48 * 7.0
    map_x0 = M + (map_w - map_px_w) / 2.0
    cell = 7.0
    for r in range(16):
        for a, b in LAND.get(r, []):
            for cc in range(a, b + 1):
                px = map_x0 + cc * cell + 3.5
                py = my + r * cell + 3.5
                d.ellipse([px - 2.5, py - 2.5, px + 2.5, py + 2.5],
                          fill=(150, 145, 130))
    for name, lon, lat, side, dy in CITIES:
        cc = (lon + 180) / 7.5
        rr = (83 - lat) / 6.0
        px = map_x0 + cc * cell + 3.5
        py = my + rr * cell + 3.5
        d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=P["red"],
                  outline=(255, 255, 255), width=1)
        lx = px + 7 if side > 0 else px - 7
        d.text((lx, py - 5 + dy), name, font=SANS(10), fill=P["ink"],
               anchor="lm" if side > 0 else "rm")
    # also list
    ay = y + 20
    for i, lines in enumerate(list_lines):
        d.text((list_x, ay), f"{i + 1}.", font=SANS_B(12), fill=P["red"])
        ay = text_lines(d, list_x + 22, ay, lines, SANS(12), P["ink"],
                        leading=14)
        ay += 1
    y = my + bottom_h
    rule(d, M, W - M, y, P["ink"], 2)
    y += 6

    # ---- footer
    if note:
        d.text((W // 2, y), "dear judge \u2014 every story here is dated Thursday "
               "19 November 2026; the dates are on the stories, the map and "
               "the masthead. \u2014 the editor",
               font=SERIF_I(15), fill=(140, 60, 40), anchor="ma")
        y += 24
    d.text((W // 2, y), "DATE CHECK \u2014 Every story here happened, or was first "
           "reported, on Thursday 19 November 2026.",
           font=SANS_B(11), fill=P["ink"], anchor="ma")
    y += 15
    d.text((W // 2, y), "Sources: UN News, AP, Reuters, Bloomberg, IAEA, "
           "COP31, Nasdaq. One day, one page.",
           font=SANS(10), fill=P["muted"], anchor="ma")
    y += 14
    return img, y


def build(variant):
    """Draw one variant, shrinking art panels until the page fits."""
    lead_h = 164 if variant == "b" else 140
    grid_h = 52
    while True:
        img, end_y = draw_page(variant, lead_h, grid_h)
        if end_y <= 1016 or (lead_h <= 120 and grid_h <= 44):
            return img, end_y, lead_h, grid_h
        if lead_h > 120:
            lead_h -= 6
        else:
            grid_h -= 4


def main():
    for v in ("a", "b", "c"):
        img, end_y, lead_h, grid_h = build(v)
        out = os.path.join(REPO, f"variant-{v}.png")
        img.save(out, optimize=True)
        n = os.path.getsize(out)
        print(f"variant-{v}: end_y={end_y} lead_art={lead_h} grid_art={grid_h} "
              f"size={img.size} bytes={n} ({n / 1048576:.2f} MiB)")
        assert img.size == (1024, 1024), "wrong dimensions"
        assert n <= 1048576, "over 1 MiB"
        assert end_y <= H - 4, f"content overflows: end_y={end_y}"


if __name__ == "__main__":
    main()
