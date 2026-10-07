"""Rendering engine for the ASCII MV.

A frame is a character grid (160x45) with per-cell 24-bit foreground colour.
Everything is a pure function of time so the terminal player and the video
exporter produce identical frames.
"""
import json
import math
import random
from pathlib import Path

W, H = 160, 45

_HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------- colour
def rgb(r, g, b):
    return (max(0, min(255, int(r))) << 16) | (max(0, min(255, int(g))) << 8) | max(0, min(255, int(b)))


def red(c):
    return (c >> 16) & 255


def green(c):
    return (c >> 8) & 255


def blue(c):
    return c & 255


def mix(a, b, t):
    if t <= 0:
        return a
    if t >= 1:
        return b
    return rgb(red(a) + (red(b) - red(a)) * t,
               green(a) + (green(b) - green(a)) * t,
               blue(a) + (blue(b) - blue(a)) * t)


def scale(c, f):
    if f >= 1.0:
        return c
    return rgb(red(c) * f, green(c) * f, blue(c) * f)


# cold-war terminal palette
DIM = rgb(28, 52, 64)
MAIN = rgb(120, 190, 215)
DATA = rgb(78, 132, 168)
BRIGHT = rgb(215, 240, 245)
ALERT = rgb(225, 88, 70)
WARN = rgb(225, 176, 92)
GREEN = rgb(110, 205, 150)
VIOLET = rgb(150, 130, 210)
AMBER = rgb(200, 150, 70)
WHITE = rgb(230, 240, 242)


# ---------------------------------------------------------------- canvas
class Canvas:
    __slots__ = ("ch", "fg")

    def __init__(self):
        self.ch = [" "] * (W * H)
        self.fg = [0] * (W * H)

    def clear(self, ch=" ", fg=0):
        self.ch[:] = [ch] * (W * H)
        self.fg[:] = [fg] * (W * H)

    def set(self, x, y, c, fg=MAIN):
        if 0 <= x < W and 0 <= y < H:
            i = y * W + x
            self.ch[i] = c
            self.fg[i] = fg

    def blend(self, x, y, c, fg):
        """Draw dimly over whatever is there (used for after-images)."""
        if 0 <= x < W and 0 <= y < H:
            i = y * W + x
            if self.ch[i] == " ":
                self.ch[i] = c
                self.fg[i] = fg

    def text(self, x, y, s, fg=MAIN):
        i0 = y * W + x
        for k, c in enumerate(s):
            j = i0 + k
            if 0 <= j < W * H and x + k < W:
                self.ch[j] = c
                self.fg[j] = fg

    def text_right(self, x_end, y, s, fg=MAIN):
        self.text(x_end - len(s) + 1, y, s, fg)

    def center(self, y, s, fg=MAIN):
        self.text((W - len(s)) // 2, y, s, fg)

    def box(self, x, y, w, h, title="", fg=DATA, fill=" "):
        if w < 2 or h < 2:
            return
        self.set(x, y, "+", fg)
        self.set(x + w - 1, y, "+", fg)
        self.set(x, y + h - 1, "+", fg)
        self.set(x + w - 1, y + h - 1, "+", fg)
        for i in range(1, w - 1):
            self.set(x + i, y, "-", fg)
            self.set(x + i, y + h - 1, "-", fg)
        for j in range(1, h - 1):
            self.set(x, y + j, "|", fg)
            self.set(x + w - 1, y + j, "|", fg)
            for i in range(1, w - 1):
                if fill != " ":
                    self.set(x + i, y + j, fill, fg)
        if title:
            self.text(x + 2, y, "[%s]" % title[: w - 5], fg)

    def rect_fill(self, x, y, w, h, c, fg):
        for j in range(h):
            for i in range(w):
                self.set(x + i, y + j, c, fg)

    def line(self, x0, y0, x1, y1, c, fg):
        steps = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for k in range(steps + 1):
            t = k / steps
            self.set(int(round(x0 + (x1 - x0) * t)), int(round(y0 + (y1 - y0) * t)), c, fg)


def is_wide(ch):
    """True for characters a terminal draws two cells wide (CJK etc.)."""
    o = ord(ch)
    return (0x1100 <= o <= 0x115F or 0x2E80 <= o <= 0xA4CF or 0xAC00 <= o <= 0xD7A3
            or 0xF900 <= o <= 0xFAFF or 0xFE30 <= o <= 0xFE4F or 0xFF00 <= o <= 0xFF60
            or 0xFFE0 <= o <= 0xFFE6)


def text_auto(cv, x, y, s, fg=MAIN):
    """Draw text where wide (CJK) characters occupy two cells."""
    for ch in s:
        if is_wide(ch):
            if x >= W - 1:
                break
            cv.set(x, y, ch, fg)
            cv.set(x + 1, y, " ", fg)      # placeholder so layouts stay aligned
            x += 2
        else:
            cv.set(x, y, ch, fg)
            x += 1


def width_of(s):
    return sum(2 if is_wide(ch) else 1 for ch in s)


# ---------------------------------------------------------------- helpers
def rng(t, salt=0):
    """Deterministic pseudo random generator for a moment in time."""
    return random.Random((int(t * 1000.0) * 2654435761 + salt * 40503) & 0xFFFFFFFF)


def hash2(x, y, salt=0):
    n = (x * 374761393 + y * 668265263 + salt * 2147483647) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    return (n ^ (n >> 16)) / 4294967296.0


def clamp(v, a, b):
    return a if v < a else b if v > b else v


def ease_out(t):
    t = clamp(t, 0.0, 1.0)
    return 1 - (1 - t) * (1 - t)


def ease_in(t):
    t = clamp(t, 0.0, 1.0)
    return t * t


def lerp(a, b, t):
    return a + (b - a) * clamp(t, 0.0, 1.0)


def beat_pulse(t, bpm=123.0, phase=0.0):
    """0..1 pulse locked to the beat grid."""
    x = (t * bpm / 60.0 + phase) % 1.0
    return max(0.0, 1.0 - x * 2.2)


# ---------------------------------------------------------------- big font
FONT57 = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "####.", "#...#", "#...#", "#...#", "####."),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."),
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
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": ("..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
}


def big_text_cells(s, x0, y0, sx=2, sy=2):
    """Return [(x, y, glyph_char)] for a big-font string (for particle targets)."""
    cells = []
    adv = 6 * sx
    for gi, ch in enumerate(s.upper()):
        g = FONT57.get(ch, FONT57[" "])
        for gy, row in enumerate(g):
            for gx, px in enumerate(row):
                if px == "#":
                    for dy in range(sy):
                        for dx in range(sx):
                            cells.append((x0 + gi * adv + gx * sx + dx,
                                          y0 + gy * sy + dy, ch))
    return cells


def big_text_width(s, sx=2):
    return len(s) * 6 * sx - sx


# ---------------------------------------------------------------- world map
MAP = json.loads((_HERE / "worldmap.json").read_text(encoding="utf-8"))
_MW, _MH = MAP["w"], MAP["h"]
_LAND = MAP["land"]
_BORDER = MAP["border"]
LON0, LON1, LAT0, LAT1 = MAP["lon0"], MAP["lon1"], MAP["lat0"], MAP["lat1"]


_COAST = [[False] * _MW for _ in range(_MH)]
for _r in range(_MH):
    for _c in range(_MW):
        if _LAND[_r][_c] != "#":
            continue
        for _dr, _dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            _rr, _cc = _r + _dr, _c + _dc
            if not (0 <= _rr < _MH and 0 <= _cc < _MW) or _LAND[_rr][_cc] != "#":
                _COAST[_r][_c] = True
                break


def map_cell(lon, lat):
    """(land, country_border, coastline) at lon/lat, nearest mask cell."""
    c = int((lon - LON0) / (LON1 - LON0) * _MW)
    r = int((lat - LAT0) / (LAT1 - LAT0) * _MH)
    if 0 <= c < _MW and 0 <= r < _MH:
        return _LAND[r][c] == "#", _BORDER[r][c] == "#", _COAST[r][c]
    return False, False, False


def equirect(lon, lat, x0, y0, w, h, lon0=None, lon1=None, lat0=None, lat1=None):
    """经纬度 -> 画布坐标（可指定取景窗口，用于镜头推拉）。"""
    a0 = LON0 if lon0 is None else lon0
    a1 = LON1 if lon1 is None else lon1
    b0 = LAT0 if lat0 is None else lat0
    b1 = LAT1 if lat1 is None else lat1
    x = x0 + (lon - a0) / (a1 - a0) * w
    y = y0 + (lat - b0) / (b1 - b0) * h
    return x, y


def polar(lon, lat, cx, cy, rmax, lat_edge=15.0):
    """Azimuthal projection from the north pole (used by the nuclear section)."""
    rr = rmax * (90.0 - lat) / (90.0 - lat_edge)
    a = math.radians(lon)
    return cx + rr * math.sin(a), cy + rr * math.cos(a) * 0.5


# ---------------------------------------------------------------- 剪辑点
def shot_index(t, cuts):
    """当前镜头序号（cuts 为剪辑时刻表）。"""
    i = 0
    for c in cuts:
        if t >= c:
            i += 1
    return i


def cut_effect(cv, t, cuts):
    """剪辑点的切换闪烁：扫光条 + 行撕裂，模拟切换镜头/频道。"""
    for c in cuts:
        d = t - (c - 0.12)
        if 0 <= d < 0.5:
            k = 1.0 - d / 0.5
            row = int(d * 2.4 * H) % H
            for dy in range(3):
                y = (row + dy) % H
                base = y * W
                for i in range(base, base + W):
                    cv.fg[i] = mix(cv.fg[i], BRIGHT, 0.45 * k)
            r = rng(t, int(c) & 0xFFFF)
            for _ in range(int(2 + 3 * k)):
                y = r.randrange(H)
                off = r.randrange(-12, 13)
                base = y * W
                rowc = cv.ch[base:base + W]
                rowf = cv.fg[base:base + W]
                cv.ch[base:base + W] = rowc[off:] + rowc[:off]
                cv.fg[base:base + W] = rowf[off:] + rowf[:off]
            break


# ---------------------------------------------------------------- CRT effects
_SCAN = " .:-=+*#%@"


def post_scanlines(cv, t, strength=0.22, roll=True):
    """Dim alternate rows + a bright scan bar travelling down the screen."""
    ch, fg = cv.ch, cv.fg
    for y in range(H):
        if y & 1:
            base = y * W
            for i in range(base, base + W):
                fg[i] = scale(fg[i], 1.0 - strength)
    if roll:
        bar = int((t * 6.5) % (H + 12)) - 6
        for dy in range(-2, 3):
            y = bar + dy
            if 0 <= y < H:
                k = 1.0 - abs(dy) / 3.2
                base = y * W
                for i in range(base, base + W):
                    fg[i] = rgb(min(255, red(fg[i]) + 42 * k),
                                min(255, green(fg[i]) + 52 * k),
                                min(255, blue(fg[i]) + 60 * k))


def post_vignette(cv):
    for y in range(H):
        dy = (y - H / 2) / (H / 2)
        for x in range(W):
            dx = (x - W / 2) / (W / 2)
            d = 1.0 - 0.38 * (dx * dx + dy * dy)
            if d < 1.0:
                i = y * W + x
                cv.fg[i] = scale(cv.fg[i], max(0.35, d))


def post_flicker(cv, t, amount=0.12):
    f = 1.0 - amount * (0.5 + 0.5 * math.sin(t * 31.7) * math.sin(t * 7.3))
    if f >= 0.999:
        return
    fg = cv.fg
    for i in range(W * H):
        fg[i] = scale(fg[i], f)


def post_noise(cv, t, amount=0.02, glyphs=None):
    """Randomly mutate a few cells (signal noise)."""
    if amount <= 0:
        return
    r = rng(t, 77)
    n = int(W * H * amount)
    gset = glyphs or ".,:;+*#%&$@01"
    ch, fg = cv.ch, cv.fg
    for _ in range(n):
        i = r.randrange(W * H)
        ch[i] = gset[r.randrange(len(gset))]
        fg[i] = mix(fg[i], BRIGHT, 0.35)


def post_tear(cv, t, strength=1.0):
    """Horizontal frame tearing: shift a few rows sideways."""
    if strength <= 0:
        return
    r = rng(t, 1234)
    count = int(2 + 3 * strength)
    ch, fg = cv.ch, cv.fg
    for _ in range(count):
        y = r.randrange(H)
        off = int((r.random() - 0.5) * 16 * strength)
        if off == 0:
            continue
        base = y * W
        rowc = ch[base:base + W]
        rowf = fg[base:base + W]
        ch[base:base + W] = rowc[-off:] + rowc[:-off] if off > 0 else rowc[-off:] + rowc[:-off]
        fg[base:base + W] = rowf[-off:] + rowf[:-off] if off > 0 else rowf[-off:] + rowf[:-off]


def post_glitch_blocks(cv, t, strength=0.5):
    """Replace random blocks of the screen with data garbage."""
    if strength <= 0:
        return
    r = rng(t, 4242)
    n = int(1 + 3 * strength)
    ch, fg = cv.ch, cv.fg
    for _ in range(n):
        bw = r.randrange(6, 40)
        bh = r.randrange(1, 3)
        x0 = r.randrange(0, W - bw)
        y0 = r.randrange(0, H - bh)
        col = mix(DATA, ALERT, r.random() * 0.6)
        for y in range(y0, y0 + bh):
            base = y * W + x0
            for i in range(base, base + bw):
                ch[i] = "0123456789ABCDEF#$%&*+=<>"[r.randrange(24)]
                fg[i] = col


def post_ghost(cv, prev_ch, prev_fg, fade=0.32):
    """After-image: keep the previous frame's characters where we now have blanks."""
    ch, fg = cv.ch, cv.fg
    for i in range(W * H):
        if ch[i] == " " and prev_ch[i] != " ":
            ch[i] = prev_ch[i]
            fg[i] = scale(prev_fg[i], fade)
