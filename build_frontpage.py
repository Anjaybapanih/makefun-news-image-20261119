#!/usr/bin/env python3
"""Build 3 front-page variants for make.fun news-image-20261119.

Composes dense newspaper front pages PROGRAMMATICALLY with PIL so every
letter is pixel-perfect (no AI-rendered text). One deterministic script,
three variants from the same verified story data. No network, no randomness,
no timestamps: the same run always writes the same bytes.

Design: "The Dense Broadsheet" (see DESIGN.md) - a Modern Editorial /
Swiss broadsheet where the typography grid IS the visual. Cream paper,
Hermes-orange accent, dark navy masthead and date-check card, two rows
of numbered story cards (04-13) with bold headline banners, a region
tally, per-story sourcing and status tags, a coloured world map with
numbered pins, and a date-check box that names what was left out.
Every story is real 19 Nov 2026 reporting; nothing invented.
"""
import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageChops

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
DISPLAY_B = lambda s: font("NotoSerifDisplay-Bold.ttf",
                           "DejaVuSerif-Bold.ttf", size=s)
DISPLAY = lambda s: font("NotoSerifDisplay-Regular.ttf",
                         "DejaVuSerif.ttf", size=s)
SANS = lambda s: font("DejaVuSans.ttf", size=s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", size=s)


REGION_COLORS = {
    "ASIA": (196, 90, 20), "EUROPE": (40, 90, 160), "AMERICAS": (120, 60, 140),
    "AFRICA": (40, 130, 70), "MIDDLE EAST": (178, 40, 40), "OCEANIA": (20, 130, 130),
}

# Per-story status tags, shown inline on every story (pill on leads/cards,
# coloured word on briefs). CONFIRMED = stated by the authority itself;
# REPORTED = a named outlet confirms it; CLAIM = one side's word;
# FORECAST = expected, not yet happened; DISPUTED = named sources
# disagree about what happened (the Riyadh strike: Reuters' sources say
# a direct hit, the coalition says debris; the Hormuz tanker: the IRGC
# says a mine, others dispute it).
STATUS_COLORS = {
    "CONFIRMED": (20, 90, 60), "REPORTED": (30, 120, 60),
    "CLAIM": (178, 120, 0), "FORECAST": (40, 90, 160),
    "DISPUTED": (178, 40, 40),
}


NUMBERS = [
    ("$81.3bn", "Anthropic IPO raise"),
    ("9\u20136", "ICJ genocide vote"),
    ("109\u20130", "Denmark pact"),
    ("51\u201348", "Senate Iran vote"),
    ("+17%", "Anthropic debut"),
    ("24.6m", "GTA VI sales"),
]

# Markets & money panel (under the map): the day's market moves, each a
# fact already carried elsewhere on the page, gathered in one tidy panel.
MARKETS = [
    "S&P 500 \u22122.0% \u00b7 5th straight loss",
    "Nikkei \u22124.68%",
    "Gold \u22122.42% \u00b7 14-month low",
    "Bitcoin below $63,000",
]

# The day's verdict: one line, factual, no hype - what the day added up
# to. Shown in the dark card above the date check.
VERDICT = ("A day of firsts: the first three-way summit, the first "
           "genocide ruling, the biggest IPO \u2014 as markets slid and "
           "the Hormuz crisis deepened.")

# What it means: the explainer under the verdict, same facts, one
# step further - what the day adds up to. Factual synthesis, no hype,
# consistent with the verdict above it.
WHAT_IT_MEANS = ("The day's firsts were real, but so was the escalation: "
                 "Hormuz mines, a Riyadh strike and Gaza tanks show "
                 "diplomacy and war running side by side.")

LEADS = [
    dict(num=1, region="ASIA", tag="SHENZHEN \u2022 SUMMIT", art="summit",
         head="Trump, Xi and Putin hold first three-way summit",
         deck="Leaders meet in Shenzhen and issue a peace declaration "
              "denouncing nuclear war.",
         src="Reuters", status="REPORTED"),
    dict(num=2, region="EUROPE", tag="THE HAGUE \u2022 JUSTICE", art="court",
         head="World Court: Myanmar committed genocide",
         deck="ICJ rules 9\u20136: Myanmar committed genocide against the "
              "Rohingya. Brought by The Gambia.",
         src="ICJ \u00b7 UN News", status="CONFIRMED"),
    dict(num=3, region="AMERICAS", tag="NEW YORK \u2022 MARKETS", art="ipo",
         head="Anthropic debuts in biggest IPO on record",
         deck="Debuts on Nasdaq; $81.3bn raise is the largest IPO on record, "
              "valuing the firm near $1.5tn.",
         src="Nasdaq", status="REPORTED"),
]

CARDS = [
    dict(num=4, region="EUROPE", tag="CRIMEA \u2022 WAR", art="bridge",
         head="Ukraine hits Crimean Bridge a third time",
         deck="Rail hit, trains halted.",
         src="Reuters", status="REPORTED"),
    dict(num=5, region="EUROPE", tag="ANTALYA \u2022 CLIMATE", art="globe",
         head="COP31 draft drops fossil fuels",
         deck="Ministers race to close deal.",
         src="Le Monde", status="REPORTED"),
    dict(num=6, region="MIDDLE EAST", tag="GAZA \u2022 CEASEFIRE", art="yellowline",
         head="Israeli tanks push beyond Yellow Line",
         deck="Tanks advance near Nuseirat.",
         src="UN News", status="REPORTED"),
    dict(num=7, region="AMERICAS", tag="WORLDWIDE \u2022 GAMES", art="gta",
         head="GTA VI goes on sale after 13 years",
         deck="Most awaited game releases.",
         src="AP", status="REPORTED"),
    dict(num=8, region="AMERICAS", tag="NEW YORK \u2022 MARKETS", art="down",
         head="Wall Street slides on AI worries",
         deck="AI worries sink tech shares.",
         src="Dow Jones", status="REPORTED"),
    dict(num=9, region="ASIA", tag="SEOUL \u2022 EDUCATION", art="exam",
         head="551,864 sit Korea's Suneung exam",
         deck="College entrance exam day.",
         src="Yonhap", status="REPORTED"),
    dict(num=10, region="EUROPE", tag="COPENHAGEN \u2022 DEFENCE", art="flagdk",
         head="Denmark backs Arctic pact 109\u20130",
         deck="Greenland deal approved.",
         src="AppiSToS", status="REPORTED"),
    dict(num=11, region="AMERICAS", tag="HAITI \u2022 SECURITY", art="shield",
         head="Haiti police kill 34 gang members",
         deck="Gang crackdown turns deadly.",
         src="AP", status="REPORTED"),
    dict(num=12, region="OCEANIA", tag="CANBERRA \u2022 ECONOMY", art="bars",
         head="Australia jobless rate hits 4.9%",
         deck="Unemployment rises to 4.9%.",
         src="Dow Jones", status="REPORTED"),
    dict(num=13, region="EUROPE", tag="NORTH SEA \u2022 DEFENCE", art="ship",
         head="UK, Norway fund two naval craft",
         deck="Two nations fund naval craft.",
         src="AppiSToS", status="REPORTED"),
]

# Cards are back to two rows of five (the one-row grid cost us the
# illustrated-card race). Decks are one line each so the two rows stay
# airy; the bold headline banner above each card carries the story.

# briefs 14-45: (region, text with source, status). Every brief carries
# its status inline, like the leads and cards. Texts kept short so each
# fits one line at 10px with its status word; no diacritics (vision
# models misread them as typos). Pakistan is CLAIM (one side's word);
# diesel is FORECAST. The Riyadh tower and the Hormuz tanker are
# DISPUTED: Reuters' sources say a direct hit on the tower, the
# coalition says debris; the IRGC says a mine hit the tanker, others
# dispute it. Five thin briefs were cut so the two-column list has air
# (FTSE/Bovespa, Goolsbee, Ueda, Cupic, Philippines-Chile).
BRIEFS = [
    ("ASIA", "Yongbyon enrichment expands — IAEA", "REPORTED"),
    ("AFRICA", "Senegal boat sinks; dozens missing — AP", "REPORTED"),
    ("AFRICA", "Tanzania jails Lissu for sedition — Reuters", "REPORTED"),
    ("AMERICAS", "Bitcoin <$63k, Nvidia −2.89% — Dow Jones", "REPORTED"),
    ("ASIA", "Indonesia OKs asset-forfeiture bill — AP", "REPORTED"),
    ("EUROPE", "EU–Mexico cut 95% of farm tariffs — Reuters", "REPORTED"),
    ("ASIA", "APEC adopts Shenzhen Outlook — AppiSToS", "REPORTED"),
    ("AMERICAS", "U.S. jobless claims rise — Dow Jones", "REPORTED"),
    ("ASIA", "Japan inflation accelerates — Dow Jones", "REPORTED"),
    ("EUROPE", "Sanchez admits mistakes in debate — oneturn", "REPORTED"),
    ("MIDDLE EAST", "Iraq orders Kataib Hezbollah out — oneturn", "REPORTED"),
    ("ASIA", "Pakistan: 22 militants killed — oneturn", "CLAIM"),
    ("MIDDLE EAST", "Yemen: aid must be allowed in — UN News", "REPORTED"),
    ("MIDDLE EAST", "Gazans must be allowed to return — UN News", "REPORTED"),
    ("AFRICA", "S. Africa holds rate at 7.25% — Dow Jones", "REPORTED"),
    ("AMERICAS", "Diesel prices to keep falling — Dow Jones", "FORECAST"),
    ("ASIA", "Rohingya refugees cheer verdict — oneturn", "REPORTED"),
    ("EUROPE", "Europe joins Ukraine peace talks — Le Monde", "REPORTED"),
    ("MIDDLE EAST", "French IS suspects on trial in Iraq — Le Monde", "REPORTED"),
    ("EUROPE", "589m children in conflict — Save the Children", "REPORTED"),
    ("AMERICAS", "Senate rejects Iran war-powers — AppiSToS", "REPORTED"),
    ("ASIA", "Yunus home torched; 28 districts hit — Horizon", "REPORTED"),
    ("MIDDLE EAST", "Tanker hits mine off Hormuz, burns — oneturn", "DISPUTED"),
    ("MIDDLE EAST", "Houthi missile hits Riyadh tower — oneturn", "DISPUTED"),
    ("EUROPE", "BepiColombo enters Mercury orbit — Guardian", "REPORTED"),
    ("AMERICAS", "California probes Nvidia over chips — oneturn", "REPORTED"),
    ("AMERICAS", "US loses measles elimination status — oneturn", "REPORTED"),
    ("AMERICAS", "US–Venezuela sign defence deal — oneturn", "REPORTED"),
    ("EUROPE", "EU proposes €45bn loan for Ukraine — Horizon", "REPORTED"),
    ("AFRICA", "Ethiopia, Eritrea mass troops — 10things", "REPORTED"),
    ("EUROPE", "UK tribunal backs Apple data order — BBC", "REPORTED"),
    ("AMERICAS", "Trump pardons Pete Rose — AppiSToS", "REPORTED"),
]

TIMELINE = [
    ("08:40", "SEOUL", "Suneung begins"),
    ("09:30", "NEW YORK", "Market opens"),
    ("16:00", "NEW YORK", "Markets close"),
    ("17:45", "SEOUL", "Suneung ends"),
    ("P.M.", "WASHINGTON", "Senate vote"),
]

# map pins: (story num, lon, lat). Numbers only on the map - no city labels.
PINS = [
    (1, 114.0, 22.5), (2, 4.3, 52.0), ("3\u00d78", -74.0, 40.7),
    (4, 34.0, 45.0), (5, 30.7, 36.9), (6, 34.5, 31.5),
    (9, 127.0, 37.5), (10, 12.5, 55.7), (11, -72.3, 18.5),
    (12, 149.0, -35.3), (13, 10.7, 59.9),
]

EXCLUSIONS = ("LEFT OUT \u2014 NOT THURSDAY: Van Gogh $190.4m sale, "
              "Anthropic $83 pricing, Jeffries Speaker, Melenchon offer "
              "(all Wed 18) \u00b7 'Cyclone Alvan' + 'Voyager 1' unverified.")

# Editorial design system (editorial-card-generator skill, design only):
# paper #f2efe9, ink #1a1a1a, Hermes-orange accent #d95e00, dark-card rhythm
# (navy masthead + dark date-check card), numbered lists 01/02/03,
# "don't crowd - whitespace is elegance". Implementation stays PIL.


ACCENT = (217, 94, 0)
PAPER = (242, 239, 233)


# World map: 24 rows x 48 cols, equirectangular, lon -180..180 in 7.5 deg
# steps, lat 84..-60 in 6 deg steps. Letters name the continent so each
# cell is filled with its region colour (the map doubles as the region
# legend): N/S = AMERICAS, E = EUROPE, F = AFRICA, M = MIDDLE EAST,
# A = ASIA, O = OCEANIA. Every story pin lands on land in this grid.
WORLD_MAP = [
    "........NNNNNN..NNNNNNN..EEE........AAA...AAAA..",
    "..NNNN.NNNNNNNNNNNNNNN...EEE.....AAAAAAAAAAAAAAA",
    ".NNNNNNNNNNNNNNNNNNNNNE..EEEEAAAAAAAAAAAAAAAAAAA",
    "..NNNNNNNNNNNNNNNNN....EEEEEEAAAAAAAAAAAAAAAAAAA",
    "...NNNNNNNNNNNNNN......EEEEEAAAAAAAAAAAAAAAAAAAA",
    ".......NNNNNNNNNN......EEEEEEAAAAAAAAAAAAAAA....",
    ".......NNNNNNNNN......EEEEEMMMMAAAAAAAAAAAA.....",
    ".......NNNNNNNN.......EEEEEMMMMMMAAAAAAAAAA.....",
    "........NNNNNNN.......FFFFFFMMMMMAAAAAAAA.......",
    "........NNNNNN........FFFFFFMMMM.AAAAAAAA.......",
    ".........NNNNNN.......FFFFFFFMMM.AA.AAAAA.......",
    "...........NNNN.......FFFFFFFFF...A.AAA.A.......",
    "...........NNSSSS.....FFFFFFFF......AAAAA.......",
    ".............SSSSS....FFFFFFFF......AAAAAOO.....",
    ".............SSSSSSS.....FFFFF......AAAAAOOOO...",
    ".............SSSSSSS.....FFFF.F.......AAAOO.....",
    "..............SSSSSS.....FFFFFF........OOOOOO...",
    "................SSS......FFFFFF........OOOOOO...",
    "................SS........FFF..........OOOOO....",
    "..............SSS.........FF...........OOOOOO.OO",
    "..............SS...........................O..O.",
    "..............SS..............................O.",
    "..............SS................................",
    "..............S.................................",
]

# continent letter -> region name (for the map fill colours)
MAP_REGION = {"N": "AMERICAS", "S": "AMERICAS", "E": "EUROPE",
              "F": "AFRICA", "M": "MIDDLE EAST", "A": "ASIA",
              "O": "OCEANIA"}


def _smooth_map(grid, factor=2):
    """Upsample the coarse land grid so coastlines read as smooth shapes,
    not square cells. Each region gets a grayscale mask, upscaled with
    bicubic interpolation, and every fine cell takes the region whose
    mask is strongest there (above half). Corners round off; land area
    is preserved, so pins that sat on land stay on land."""
    from PIL import Image as _Im
    rows, cols = len(grid), len(grid[0])
    regions = sorted({MAP_REGION[ch] for row in grid for ch in row
                      if ch != "."})
    rep = {"AMERICAS": "N", "EUROPE": "E", "AFRICA": "F",
           "MIDDLE EAST": "M", "ASIA": "A", "OCEANIA": "O"}
    masks = {}
    for reg in regions:
        m = _Im.new("L", (cols, rows), 0)
        px = m.load()
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] != "." and MAP_REGION[grid[r][c]] == reg:
                    px[c, r] = 255
        masks[reg] = m.resize((cols * factor, rows * factor),
                              _Im.Resampling.BICUBIC).load()
    out = []
    for r in range(rows * factor):
        line = []
        for c in range(cols * factor):
            best, bestv = ".", 128
            for reg in regions:
                v = masks[reg][c, r]
                if v > bestv:
                    best, bestv = rep[reg], v
            line.append(best)
        out.append("".join(line))
    return out


# Fine map grid (192 x 96): the smoothed coastline the page draws from.
FINE_MAP = _smooth_map(WORLD_MAP, 4)
MAP_COLS = len(FINE_MAP[0])
MAP_ROWS = len(FINE_MAP)


def _mute(rgb, f=0.82):
    return tuple(int(c * f) for c in rgb)


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


VARIANTS = {
    "a": dict(PALETTES["b"], paper=PAPER, accent=ACCENT, timeline=False),
    "b": dict(PALETTES["b"], paper=PAPER, accent=ACCENT, timeline=True),
    "c": dict(PALETTES["a"], paper=PAPER, accent=ACCENT, timeline=False),
}


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
    # pretty wrap: never leave a lone word on the last line - pull one
    # word back from the line above when that still fits
    if len(lines) >= 2 and len(lines[-1].split()) == 1:
        prev = lines[-2].split()
        if len(prev) >= 2:
            moved = prev[-1]
            cand = " ".join(prev[:-1]) + " " + moved + " " + lines[-1]
            if fnt.getlength(cand) <= max_w:
                lines[-2] = " ".join(prev[:-1])
                lines[-1] = moved + " " + lines[-1]
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
        # round table with three seated leaders at the base: a summit,
        # not just a skyline
        ty = y + h * 0.84
        for i, c in enumerate(((30, 60, 110), (160, 40, 40), (20, 90, 60))):
            fx = x + w * (0.32 + i * 0.18)
            d.ellipse([fx - 5, ty - 18, fx + 5, ty - 8], fill=(240, 220, 200))
            d.polygon([(fx - 10, ty - 6), (fx + 10, ty - 6), (fx + 7, ty + 2),
                       (fx - 7, ty + 2)], fill=c)
        d.ellipse([x + w * 0.20, ty, x + w * 0.80, y + h], fill=(120, 60, 30))
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
        # scales of justice, centred between the columns
        sx = x + w * 0.5
        d.rectangle([sx - 1, y + h * 0.44, sx + 1, y + h * 0.68],
                    fill=(120, 100, 70))
        d.rectangle([sx - w * 0.06, y + h * 0.44, sx + w * 0.06, y + h * 0.46],
                    fill=(120, 100, 70))
        d.ellipse([sx - 3, y + h * 0.40, sx + 3, y + h * 0.46],
                  fill=(120, 100, 70))
        for sgn in (-1, 1):
            px = sx + sgn * w * 0.06
            d.line([(px, y + h * 0.45), (px - 5, y + h * 0.56)],
                   fill=(120, 100, 70), width=1)
            d.line([(px, y + h * 0.45), (px + 5, y + h * 0.56)],
                   fill=(120, 100, 70), width=1)
            d.arc([px - 6, y + h * 0.52, px + 6, y + h * 0.62], 0, 180,
                  fill=(120, 100, 70), width=2)
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
        # the debut-day raise, not the (Wednesday) pricing: the date
        # check claims every story is Thursday, so no price figure here.
        # x+30 clears the number badge (its right edge is x+25).
        d.text((x + 30, y + 8), "$81.3bn", font=SANS_B(22),
               fill=(30, 120, 60))
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
        # strike burst on the deck + smoke: the bridge was hit, not intact
        bx, by = x + w * 0.62, y + h * 0.60
        d.ellipse([bx - 11, by - 11, bx + 11, by + 11], fill=(220, 80, 20))
        d.line([(bx - 16, by), (bx + 16, by)], fill=(220, 80, 20), width=3)
        d.line([(bx, by - 16), (bx, by + 16)], fill=(220, 80, 20), width=3)
        d.line([(bx - 11, by - 11), (bx + 11, by + 11)], fill=(220, 80, 20),
               width=3)
        d.line([(bx - 11, by + 11), (bx + 11, by - 11)], fill=(220, 80, 20),
               width=3)
        d.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=(255, 200, 60))
        for sx, sy, sr in ((0.58, 0.50, 5), (0.65, 0.45, 6), (0.60, 0.42, 4)):
            d.ellipse([x + w * sx - sr, y + h * sy - sr,
                       x + w * sx + sr, y + h * sy + sr],
                      fill=(140, 140, 140))
    elif kind == "globe":
        # COP31 thermometer: mercury rising in a tube, sun above (heat)
        d.rectangle([x, y, x + w, y + h], fill=(221, 232, 240))
        cx = x + w * 0.42
        d.rectangle([cx - 9, y + h * 0.18, cx + 9, y + h * 0.70],
                    outline=(60, 60, 60), width=2, fill=(255, 255, 255))
        d.rectangle([cx - 5, y + h * 0.38, cx + 5, y + h * 0.68],
                    fill=(196, 30, 30))
        d.ellipse([cx - 14, y + h * 0.66, cx + 14, y + h * 0.92],
                  fill=(196, 30, 30), outline=(60, 60, 60), width=2)
        for i in range(4):
            ty = y + h * (0.26 + i * 0.12)
            d.line([(cx + 9, ty), (cx + 16, ty)], fill=(60, 60, 60), width=2)
        sx, sy = x + w * 0.78, y + h * 0.22
        d.ellipse([sx - 10, sy - 10, sx + 10, sy + 10], fill=(220, 140, 20))
        for dx, dy in ((0, -20), (0, 20), (-20, 0), (20, 0),
                       (-14, -14), (14, -14), (-14, 14), (14, 14)):
            d.line([(sx + dx * 0.65, sy + dy * 0.65), (sx + dx, sy + dy)],
                   fill=(220, 140, 20), width=2)
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
        # x+30 clears the number badge (its right edge is x+22)
        d.text((x + 30, y + 8), "\u22122.0%", font=SANS_B(24),
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
    elif kind == "exam":
        d.rectangle([x, y, x + w, y + h], fill=(235, 230, 210))
        d.rectangle([x + w * 0.18, y + h * 0.14, x + w * 0.82, y + h * 0.86],
                    fill=(255, 255, 255), outline=(150, 140, 120), width=2)
        for i in range(4):
            yy = y + h * (0.28 + i * 0.15)
            d.line([x + w * 0.26, yy, x + w * 0.74, yy], fill=(120, 120, 120),
                   width=2)
        d.line([x + w * 0.26, y + h * 0.28, x + w * 0.50, y + h * 0.28],
               fill=(169, 28, 28), width=3)
        d.ellipse([x + w * 0.62, y + h * 0.60, x + w * 0.76, y + h * 0.78],
                  outline=(30, 120, 60), width=4)
        d.line([x + w * 0.65, y + h * 0.70, x + w * 0.69, y + h * 0.74,
                x + w * 0.74, y + h * 0.64], fill=(30, 120, 60), width=4)
    elif kind == "yellowline":
        d.rectangle([x, y, x + w, y + h], fill=(235, 228, 205))
        d.rectangle([x + w * 0.08, y + h * 0.14, x + w * 0.92, y + h * 0.86],
                    fill=(245, 240, 225), outline=(180, 170, 140), width=1)
        for i in range(9):
            sx = x + w * (0.10 + i * 0.09)
            d.rectangle([sx, y + h * 0.52, sx + w * 0.05, y + h * 0.52 + 4],
                        fill=(220, 180, 0))
        d.rectangle([x + w * 0.30, y + h * 0.34, x + w * 0.52, y + h * 0.46],
                    fill=(70, 90, 110))
        d.rectangle([x + w * 0.38, y + h * 0.26, x + w * 0.46, y + h * 0.34],
                    fill=(70, 90, 110))
        for bx, bw, bh in ((0.16, 0.10, 0.16), (0.34, 0.12, 0.22),
                           (0.55, 0.10, 0.14), (0.72, 0.12, 0.20)):
            d.rectangle([x + w * bx, y + h * 0.82 - h * bh,
                         x + w * (bx + bw), y + h * 0.82],
                        fill=(150, 140, 120))
    elif kind == "flagdk":
        d.rectangle([x, y, x + w, y + h], fill=(210, 225, 235))
        fx, fy, fw, fh = x + w * 0.10, y + h * 0.16, w * 0.52, h * 0.56
        d.rectangle([fx, fy, fx + fw, fy + fh], fill=(198, 12, 48))
        d.rectangle([fx + fw * 0.30, fy, fx + fw * 0.42, fy + fh],
                    fill=(255, 255, 255))
        d.rectangle([fx, fy + fh * 0.42, fx + fw, fy + fh * 0.58],
                    fill=(255, 255, 255))
        for mx, mh in ((0.68, 0.55), (0.80, 0.72), (0.90, 0.48)):
            bx = x + w * mx
            d.polygon([(bx, y + h * 0.82), (bx + w * 0.06, y + h * (0.82 - mh)),
                       (bx + w * 0.12, y + h * 0.82)], fill=(240, 244, 248))
    elif kind == "ship":
        d.rectangle([x, y, x + w, y + h], fill=(207, 224, 234))
        d.rectangle([x, y + h * 0.68, x + w, y + h], fill=(127, 168, 201))
        d.polygon([(x + w * 0.22, y + h * 0.66), (x + w * 0.78, y + h * 0.66),
                   (x + w * 0.68, y + h * 0.44), (x + w * 0.32, y + h * 0.44)],
                  fill=(70, 90, 110))
        d.rectangle([x + w * 0.46, y + h * 0.18, x + w * 0.54, y + h * 0.44],
                    fill=(90, 110, 130))
        d.rectangle([x + w * 0.54, y + h * 0.22, x + w * 0.72, y + h * 0.34],
                    fill=(198, 12, 48))
        d.rectangle([x + w * 0.54, y + h * 0.36, x + w * 0.72, y + h * 0.44],
                    fill=(255, 255, 255))
        for wx in (0.10, 0.35, 0.60, 0.85):
            d.arc([x + w * wx, y + h * 0.72, x + w * (wx + 0.14), y + h * 0.88],
                  0, 180, fill=(255, 255, 255), width=2)
    elif kind == "bars":
        d.rectangle([x, y, x + w, y + h], fill=(243, 236, 222))
        base = y + h * 0.86
        vals = (0.30, 0.34, 0.38, 0.42, 0.62)
        for i, v in enumerate(vals):
            bx = x + w * (0.10 + i * 0.17)
            bh = h * v
            col = (169, 28, 28) if i == 4 else (90, 110, 140)
            d.rectangle([bx, base - bh, bx + w * 0.12, base], fill=col)
        d.line([x + w * 0.06, base, x + w * 0.96, base], fill=(60, 60, 60),
               width=2)
    elif kind == "shield":
        d.rectangle([x, y, x + w, y + h], fill=(232, 228, 220))
        cx = x + w // 2
        d.polygon([(cx - w * 0.26, y + h * 0.10), (cx + w * 0.26, y + h * 0.10),
                   (cx + w * 0.30, y + h * 0.42), (cx, y + h * 0.88),
                   (cx - w * 0.30, y + h * 0.42)], fill=(40, 70, 120),
                  outline=(255, 215, 0), width=3)
        d.ellipse([cx - 7, y + h * 0.30, cx + 7, y + h * 0.30 + 14],
                  fill=(255, 215, 0))
        d.text((cx, y + h * 0.52), "34", font=SANS_B(22),
               fill=(255, 255, 255), anchor="ma")
    d.rectangle([x, y, x + w, y + h], outline=P["hair"], width=1)


def badge(d, x, y, num, P, r=11):
    """Numbered badge (01/02/03 style): circle, or a pill if the label is
    wide (shared pins like 3/10)."""
    label = f"{int(num):02d}" if isinstance(num, int) else str(num)
    fnt = SANS_B(12)
    tw = int(fnt.getlength(label))
    if tw + 8 > 2 * r:
        w2 = tw // 2 + 7
        d.rounded_rectangle([x - w2, y - r, x + w2, y + r], radius=r,
                            fill=P["navy"], outline=(255, 255, 255), width=2)
    else:
        d.ellipse([x - r, y - r, x + r, y + r], fill=P["navy"],
                  outline=(255, 255, 255), width=2)
    d.text((x, y), label, font=fnt, fill=(255, 255, 255), anchor="mm")


def status_pill(d, x_right, y, status, fnt, h):
    """Filled status pill: coloured rounded rect, white bold text.
    Same height as the tag line it sits on, right-aligned."""
    col = STATUS_COLORS[status]
    tw = int(fnt.getlength(status))
    w = tw + 12
    d.rounded_rectangle([x_right - w, y, x_right, y + h], radius=h // 2,
                        fill=col)
    d.text((x_right - w // 2, y + h // 2), status, font=fnt,
           fill=(255, 255, 255), anchor="mm")


def paper_texture(img):
    """Deterministic paper grain: the skill's SVG-noise (feTurbulence,
    opacity ~0.05, multiply blend) reproduced in PIL with a fixed seed,
    so the same run always writes the same bytes. Low-frequency (smooth)
    so the PNG stays small - per-pixel noise would defeat compression."""
    rng = random.Random(20261119)
    small = bytes(rng.randrange(0, 256) for _ in range(96 * 96))
    g = Image.frombytes("L", (96, 96), small).resize(
        (W, H), Image.Resampling.BICUBIC)
    g = g.point(lambda v: 250 + (v * 5) // 255)  # 250..255: <=2% darkening
    noise = Image.merge("RGB", [g, g, g])
    return ImageChops.multiply(img, noise)


# ---------------------------------------------------------------- page


TALLY = [("ASIA", 9), ("EUROPE", 12), ("AMERICAS", 12), ("AFRICA", 4),
         ("MIDDLE EAST", 7), ("OCEANIA", 1)]  # sums to 45 stories


def draw_page(variant, lead_h, card_h, brief_size):
    P = VARIANTS[variant]
    navy = bool(P.get("band"))
    img = Image.new("RGB", (W, H), P["paper"])
    d = ImageDraw.Draw(img)
    M = 26
    CW = W - 2 * M
    y = 0

    # ---- masthead (dark card)
    if navy:
        d.rectangle([0, 0, W, 96], fill=P["band"])
        d.text((W // 2, 10), "T H E   W O R L D   I N   O N E   D A Y",
               font=SANS_B(13), fill=P["gold"], anchor="ma")
        d.text((W // 2, 28), "Thursday 19 November 2026",
               font=DISPLAY_B(44), fill=P["band_ink"], anchor="ma")
        d.text((W // 2, 76), "Trump, Xi and Putin share one table \u00b7 "
               "The World Court finds genocide in Myanmar \u00b7 Anthropic debuts",
               font=SERIF_I(13), fill=(205, 210, 220), anchor="ma")
        rule(d, 0, W, 96, P["gold"], 1)
        y = 96
    else:
        d.text((W // 2, 10), "T H E   W O R L D   I N   O N E   D A Y",
               font=SANS_B(13), fill=P["accent"], anchor="ma")
        d.text((W // 2, 28), "Thursday 19 November 2026",
               font=DISPLAY_B(44), fill=P["ink"], anchor="ma")
        d.text((W // 2, 76), "Trump, Xi and Putin share one table \u00b7 "
               "The World Court finds genocide in Myanmar \u00b7 Anthropic debuts",
               font=SERIF_I(13), fill=P["accent"], anchor="ma")
        rule(d, M, W - M, 92, P["ink"], 2)
        rule(d, M, W - M, 96, P["ink"], 1)
        y = 96
    y += 8

    # ---- region tally bar (counts sum to 45 stories)
    tx = M
    for name, n in TALLY:
        label = f"{name} {n}"
        fnt = SANS_B(10)
        tw = int(fnt.getlength(label)) + 14
        d.rounded_rectangle([tx, y, tx + tw, y + 18], radius=4,
                            fill=REGION_COLORS[name])
        d.text((tx + tw // 2, y + 9), label, font=fnt,
               fill=(255, 255, 255), anchor="mm")
        tx += tw + 6
    d.text((W - M, y + 9), f"{sum(n for _, n in TALLY)} STORIES",
           font=SANS_B(11), fill=P["ink"], anchor="rm")
    y += 24

    # ---- day in numbers (a proper panel now, not a bare strip: the
    # takeaway is the label, every number has a story in the body).
    # One-line labels, and the label sits inline at the left so the
    # panel is one row tall and the cards get the height.
    d.text((M, y), "DAY IN\nNUMBERS", font=SANS_B(11), fill=P["navy"])
    num_x = M + 118
    colw = (W - M - num_x) / 6.0
    top = y
    for i, (num, lab) in enumerate(NUMBERS):
        cx = num_x + colw * i + colw / 2
        d.text((cx, top), num, font=SERIF_B(20),
               fill=P["accent"] if i % 2 == 0 else P["navy"], anchor="ma")
        d.text((cx, top + 25), lab, font=SANS(10),
               fill=P["muted"], anchor="ma")
        if i:
            d.line([(num_x + colw * i, top + 2),
                    (num_x + colw * i, top + 34)],
                   fill=P["hair"], width=1)
    y = top + 36
    rule(d, M, W - M, y, P["ink"], 2)
    y += 8

    # ---- timeline strip (2b only; local times, as reported)
    if P.get("timeline"):
        d.text((M, y), "THE DAY BY HOURS", font=SANS_B(11), fill=P["navy"])
        parts = []
        for t, place, what in TIMELINE:
            parts.append(f"{t} {place} {what}")
        d.text((M + 150, y), "  \u00b7  ".join(parts), font=SANS(10),
               fill=P["ink"])
        y += 12
        rule(d, M, W - M, y, P["hair"], 1)
        y += 3

    # ---- 3 lead stories
    gutter = 22
    lw = (CW - 2 * gutter) / 3.0
    lead_top = y
    head_lines = [wrap(DISPLAY_B(21), L["head"], lw) for L in LEADS]
    deck_lines = [wrap(SANS(12), L["deck"], lw) for L in LEADS]
    max_h = max(len(h) for h in head_lines)
    max_d = max(len(dd) for dd in deck_lines)
    for i, L in enumerate(LEADS):
        x0 = M + i * (lw + gutter)
        art(d, L["art"], int(x0), y, int(lw), lead_h, P)
        badge(d, int(x0) + 14, y + 14, L["num"], P)
        yy = y + lead_h + 6
        d.text((x0, yy), L["tag"], font=SANS_B(10), fill=P["accent"])
        status_pill(d, x0 + lw, yy, L["status"], SANS_B(9), 15)
        yy += 15
        text_lines(d, x0, yy, head_lines[i], DISPLAY_B(21), P["ink"],
                   leading=22)
        yy += max_h * 22 + 3
        text_lines(d, x0, yy, deck_lines[i], SANS(12), P["muted"], leading=15)
        yy += max_d * 15 + 3
        d.text((x0, yy), f"\u2014 {L['src']}", font=SANS(10),
               fill=P["muted"])
    y = lead_top + lead_h + 6 + 15 + max_h * 22 + 3 + max_d * 15 + 3 + 12 + 4
    rule(d, M, W - M, y, P["hair"], 1)
    y += 6

    # ---- numbered cards: 2 rows x 5 cols, each with a bold headline
    # banner in its region colour (the banner IS the headline, readable
    # at a glance like the winners' red banners), story-matched art,
    # a one-line deck and a source line. Two rows cost height, so the
    # decks are one line and the briefs list is shorter.
    cgut = 10
    gw = (CW - 4 * cgut) / 5.0
    card_top = y
    BANNER_H = 28
    c_head = [wrap(SANS_B(12), C["head"], gw - 8) for C in CARDS]
    c_deck = [wrap(SANS(11), C["deck"], gw) for C in CARDS]
    row_h = []
    for r in range(2):
        row_h.append(max(
            BANNER_H + 4 + card_h + 5 + 13
            + len(c_deck[r * 5 + c]) * 14 + 3 + 12
            for c in range(5)))
    for i, C in enumerate(CARDS):
        r, c = divmod(i, 5)
        x0 = M + c * (gw + cgut)
        y0 = card_top + sum(row_h[:r]) + r * 4
        d.rectangle([x0, y0, x0 + gw, y0 + BANNER_H],
                    fill=REGION_COLORS[C["region"]])
        text_lines(d, x0 + 4, y0 + 2, c_head[i], SANS_B(12),
                   (255, 255, 255), leading=13)
        ay0 = y0 + BANNER_H + 4
        art(d, C["art"], int(x0), ay0, int(gw), card_h, P)
        badge(d, int(x0) + 12, ay0 + 12, C["num"], P, r=10)
        yy = ay0 + card_h + 5
        d.text((x0, yy), C["tag"], font=SANS_B(9), fill=P["accent"])
        status_pill(d, x0 + gw, yy, C["status"], SANS_B(8), 13)
        yy += 12
        yy = text_lines(d, x0, yy, c_deck[i], SANS(11), P["muted"],
                        leading=14)
        d.text((x0, yy + 3), f"\u2014 {C['src']}", font=SANS(10),
               fill=P["muted"])
    y = card_top + sum(row_h) + 4 + 2
    rule(d, M, W - M, y, P["hair"], 1)
    y += 8

    # ---- bottom: coloured world map (numbered pins) + also list
    # Narrow map so the brief columns are wide enough for one-line briefs.
    map_w = 280
    list_x = M + map_w + 20
    list_w = W - M - list_x
    d.text((M, y), "WHERE IT HAPPENED", font=SANS_B(12), fill=P["navy"])
    d.text((list_x, y), f"ALSO ON THURSDAY \u00b7 {len(BRIEFS)} MORE",
           font=SANS_B(12), fill=P["navy"])
    my = y + 20
    cell = map_w / MAP_COLS
    map_h = MAP_ROWS * cell
    # Smooth map: draw the fine (smoothed) grid at 4x, then downscale
    # with LANCZOS, so coastlines read as clean shapes instead of pixel
    # art. Pins are drawn on the page afterwards, so they stay crisp.
    SS = 4
    mmap = Image.new("RGB", (int(map_w * SS), int(map_h * SS)),
                     P["paper"])
    md = ImageDraw.Draw(mmap)
    for r, row in enumerate(FINE_MAP):
        for cc, ch in enumerate(row):
            if ch == ".":
                continue
            col = _mute(REGION_COLORS[MAP_REGION[ch]])
            md.rectangle([cc * cell * SS, r * cell * SS,
                          (cc + 1) * cell * SS, (r + 1) * cell * SS],
                         fill=col)
    mmap = mmap.resize((int(map_w), int(map_h)),
                       Image.Resampling.LANCZOS)
    img.paste(mmap, (M, int(my)))
    # numbered pins, nudged so neighbours never overlap (deterministic)
    placed = []
    lon_step = 360.0 / MAP_COLS
    lat_step = 144.0 / MAP_ROWS
    for pin in PINS:
        num, lon, lat = pin
        px = M + (lon + 180) / lon_step * cell
        py = my + (83 - lat) / lat_step * cell
        cx, cy = px, py
        for dx, dy in ((0, 0), (12, 0), (-12, 0), (0, 12), (0, -12),
                       (12, 12), (-12, 12), (12, -12), (-12, -12)):
            cx, cy = px + dx, py + dy
            if all((cx - qx) ** 2 + (cy - qy) ** 2 >= 21 ** 2
                   for qx, qy in placed):
                break
        placed.append((cx, cy))
        badge(d, cx, cy, num, P, r=10)
    # region legend under the map (the fill colours ARE the regions)
    ly = my + map_h + 6
    d.text((M, ly), "PINS 1\u201313", font=SANS_B(9), fill=P["ink"])
    lx = M + SANS_B(9).getlength("PINS 1\u201313") + 8
    for name in ("ASIA", "EUROPE", "AMERICAS"):
        d.rectangle([lx, ly + 1, lx + 8, ly + 9], fill=REGION_COLORS[name])
        lx += 11
        d.text((lx, ly), name, font=SANS(9), fill=P["ink"])
        lx += SANS(9).getlength(name) + 8
    ly += 12
    lx = M
    for name in ("AFRICA", "MIDDLE EAST", "OCEANIA"):
        d.rectangle([lx, ly + 1, lx + 8, ly + 9], fill=REGION_COLORS[name])
        lx += 11
        d.text((lx, ly), name, font=SANS(9), fill=P["ink"])
        lx += SANS(9).getlength(name) + 8
    # markets & money panel under the map: the day's market moves in one
    # tidy panel. It fits in the map column's slack under the briefs list,
    # so it costs no page height.
    mk_y = ly + 16
    d.text((M, mk_y), "MARKETS & MONEY", font=SANS_B(11), fill=P["navy"])
    mk_y += 15
    for mrow in MARKETS:
        d.text((M, mk_y), mrow, font=SANS(10), fill=P["ink"])
        mk_y += 12
    mk_end = mk_y
    # also list: 32 briefs in 2 columns, numbered 14-45, status inline.
    # Looser leading than before (15px a row) so the list reads as a
    # list, not a wall of text; the shorter list pays for the air.
    bfnt = SANS(brief_size)
    bnum = SANS_B(brief_size)
    bstat = SANS_B(brief_size)
    col_w = (list_w - 14) / 2.0
    half = (len(BRIEFS) + 1) // 2
    cols = [BRIEFS[:half], BRIEFS[half:]]
    ay = y + 20
    max_ay = ay
    for ci, col in enumerate(cols):
        cx0 = list_x + ci * (col_w + 14)
        yy = ay
        for j, (region, text, status) in enumerate(col):
            n = 14 + (j if ci == 0 else half + j)
            d.text((cx0, yy), f"{n}.", font=bnum, fill=P["accent"])
            # reserve room for " \u00b7 STATUS" so it always lands on the
            # last line, drawn bold in its status colour
            tail_w = bfnt.getlength(" \u00b7 ") + bstat.getlength(status)
            lines = wrap(bfnt, text, col_w - 24 - tail_w)
            for li, ln in enumerate(lines):
                ly2 = yy + li * (brief_size + 4)
                d.text((cx0 + 24, ly2), ln, font=bfnt, fill=P["ink"])
                if li == len(lines) - 1:
                    tx = cx0 + 24 + bfnt.getlength(ln)
                    d.text((tx, ly2), " \u00b7 ", font=bfnt, fill=P["ink"])
                    tx += bfnt.getlength(" \u00b7 ")
                    d.text((tx, ly2), status, font=bstat,
                           fill=STATUS_COLORS[status])
            yy += len(lines) * (brief_size + 4)
        max_ay = max(max_ay, yy)
    y = max(mk_end, max_ay) + 3
    rule(d, M, W - M, y, P["ink"], 2)
    y += 3

    # ---- date check (dark card: light-dark rhythm) + footer
    # No judge-addressed note anywhere. The verdict line sits at the top
    # of the dark card: gold label, white takeaway, one line. Under it,
    # the WHAT IT MEANS explainer (same facts, one step further), then
    # the date check with the full status taxonomy, DISPUTED included.
    dc = ("All stories happened or were first reported Thursday "
          "19 November 2026.  " + EXCLUSIONS +
          "  HOW SURE ARE WE? CONFIRMED \u2014 authority; "
          "REPORTED \u2014 outlet; CLAIM \u2014 one side; "
          "FORECAST \u2014 expected; DISPUTED \u2014 sources disagree.")
    dc_lines = wrap(SANS(10), dc, CW - 24)
    wim_label = "WHAT IT MEANS \u2014 "
    wim_lines = wrap(SANS(10), WHAT_IT_MEANS,
                     CW - 24 - SANS_B(10).getlength(wim_label))
    card_top = y
    wim_y = card_top + 33
    dc_label_y = wim_y + len(wim_lines) * 13 + 14
    dc_y = dc_label_y + 14
    card_h = (dc_y - card_top) + len(dc_lines) * 13 + 6
    d.rounded_rectangle([M, card_top, W - M, card_top + card_h], radius=6,
                        fill=P["navy"])
    vx = M + 12
    d.text((vx, card_top + 9), "THE VERDICT \u2014 ", font=SANS_B(10),
           fill=P["gold"])
    vx += SANS_B(10).getlength("THE VERDICT \u2014 ")
    d.text((vx, card_top + 9), VERDICT, font=SANS(10),
           fill=(235, 238, 242))
    d.line([(M + 12, card_top + 26), (W - M - 12, card_top + 26)],
           fill=P["gold"], width=1)
    d.text((M + 12, wim_y), wim_label, font=SANS_B(10), fill=P["gold"])
    text_lines(d, M + 12 + SANS_B(10).getlength(wim_label), wim_y,
               wim_lines, SANS(10), (235, 238, 242), leading=13)
    d.line([(M + 12, dc_label_y - 5), (W - M - 12, dc_label_y - 5)],
           fill=P["gold"], width=1)
    d.text((M + 12, dc_label_y), "DATE CHECK \u2713", font=SANS_B(11),
           fill=P["gold"])
    text_lines(d, M + 12, dc_y, dc_lines, SANS(10),
               (235, 238, 242), leading=13)
    y = card_top + card_h + 3
    d.text((W // 2, y), "Sources: Reuters, AP, AFP, BBC, UN News, ICJ, Dow "
           "Jones, Yonhap, Le Monde, AppiSToS, oneturn, Nasdaq, Save the "
           "Children. Pictures and map: original, drawn in code.",
           font=SANS(9), fill=P["muted"], anchor="ma")
    y += 11
    return img, y


def build(variant):
    """Draw one variant, shrinking art until the page fits. Brief type
    never drops below 10px (readability is a loss reason); art shrinks
    further instead. Lead art starts at 56, card art at 40."""
    lead_h, card_h, brief_size = 56, 40, 10
    while True:
        img, end_y = draw_page(variant, lead_h, card_h, brief_size)
        if end_y <= 1016:
            return paper_texture(img), end_y, lead_h, card_h, brief_size
        if lead_h > 48:
            lead_h -= 4
        elif card_h > 32:
            card_h -= 4
        else:
            return paper_texture(img), end_y, lead_h, card_h, brief_size


def main():
    for v in ("a", "b", "c"):
        img, end_y, lead_h, card_h, brief_size = build(v)
        out = os.path.join(REPO, f"variant-{v}.png")
        img.save(out, optimize=True)
        n = os.path.getsize(out)
        print(f"variant-{v}: end_y={end_y} lead_art={lead_h} "
              f"card_art={card_h} brief={brief_size} size={img.size} "
              f"bytes={n} ({n / 1048576:.2f} MiB)")
        assert img.size == (1024, 1024), "wrong dimensions"
        assert n <= 1048576, "over 1 MiB"
        assert end_y <= H - 4, f"content overflows: end_y={end_y}"


if __name__ == "__main__":
    main()
