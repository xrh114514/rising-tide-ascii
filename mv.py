"""Main frame compositor: section timeline, transitions, CRT post, ANSI output."""
import json
import math
from pathlib import Path

from engine import (
    W, H, Canvas, rgb, mix, scale, rng, hash2, clamp, lerp, post_scanlines,
    post_vignette, post_flicker, post_noise, post_tear, post_glitch_blocks,
    post_ghost, beat_pulse, MAIN, DATA, BRIGHT, ALERT, WARN, GREEN, DIM,
)
import scenes1
import scenes2
import chronicle

_DURATION = 201.213

# section table: (start, end, title, renderer)
SECTIONS = [
    (0.0, 33.0, "GLOBAL SITUATION MONITOR", scenes1.scene_monitor),
    (33.0, 40.0, "SYSTEM REINDEX", scenes1.scene_title),
    (40.0, 79.0, "WAR GAME 7224", scenes1.scene_wargame),
    (79.0, 127.0, "INTELLIGENCE ARCHIVE", scenes2.scene_intel),
    (127.0, 158.0, "STRATEGIC ARMS / ORBITAL", scenes2.scene_nuclear),
    (158.0, 175.0, "STANDING DOWN", scenes2.scene_detente),
    (175.0, _DURATION + 1.0, "HISTORICAL ASSESSMENT", scenes2.scene_eval),
]

# boundaries that use a character dissolve (the title burst handles its own)
DISSOLVE = {40.0, 79.0, 127.0, 158.0, 175.0}
DISSOLVE_LEN = 0.9


class Music:
    """Beat map extracted from the soundtrack (see analyze_audio.py)."""

    def __init__(self, path=None):
        p = Path(path) if path else Path(__file__).resolve().parent / "beats.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        self.bpm = d.get("bpm", 120.0)
        self.dt = d.get("grid_dt", 0.0464)
        self.energy_arr = d.get("energy", [])
        self.flux_arr = d.get("flux", [])
        self.onsets = d.get("onsets", [])

    def _grid(self, arr, t):
        if not arr:
            return 0.5
        x = t / self.dt
        i = int(x)
        if i < 0:
            return arr[0]
        if i >= len(arr) - 1:
            return arr[-1]
        f = x - i
        return arr[i] * (1 - f) + arr[i + 1] * f

    def energy(self, t):
        return self._grid(self.energy_arr, t)

    def flux(self, t):
        return self._grid(self.flux_arr, t)

    def onset(self, t, window=0.09):
        """1.0 just after a detected onset, decaying over `window` seconds."""
        best = 0.0
        for ot in self.onsets:
            d = t - ot
            if 0 <= d < window:
                best = max(best, 1.0 - d / window)
            elif ot > t + window:
                break
        return best

    def pulse(self, t):
        """Beat-locked 0..1 pulse, emphasised at detected onsets."""
        p = beat_pulse(t, self.bpm)
        return clamp(0.55 * p + 0.75 * self.onset(t), 0.0, 1.0)


_MUSIC = Music()


def music():
    return _MUSIC


class State:
    """Facade passed to scene renderers."""

    def __init__(self, m=None):
        self.m = m or _MUSIC

    def pulse(self, t):
        return self.m.pulse(t)

    def energy(self, t):
        return self.m.energy(t)

    def onset(self, t):
        return self.m.onset(t)

    def snap(self, t, win=0.45):
        """把剪辑点对齐到最近的鼓点（onset），让镜头切换踩在节拍上。"""
        best, bd = t, win
        for ot in self.m.onsets:
            d = abs(ot - t)
            if d < bd:
                best, bd = ot, d
            elif ot > t + win:
                break
        return best


_STATE = State()


def section_index(t):
    for i, (a, b, _, _) in enumerate(SECTIONS):
        if a <= t < b:
            return i
    return len(SECTIONS) - 1


def _render_single(cv, t):
    i = section_index(t)
    _, _, _, fn = SECTIONS[i]
    fn(cv, t, _STATE)


def render_frame(t, prev=None):
    """Render one frame. `prev` is a previous Canvas used for after-images."""
    t = clamp(t, 0.0, _DURATION)
    cv = Canvas()
    i = section_index(t)

    # ---- scene (with character-dissolve transitions)
    blended = False
    for b in DISSOLVE:
        if b - DISSOLVE_LEN * 0.5 <= t < b + DISSOLVE_LEN * 0.5:
            u = (t - (b - DISSOLVE_LEN * 0.5)) / DISSOLVE_LEN
            a_idx = section_index(b - 0.01)
            b_idx = section_index(b + 0.01)
            tmp = Canvas()
            SECTIONS[a_idx][3](tmp, t, _STATE)
            SECTIONS[b_idx][3](cv, t, _STATE)
            for y in range(H):
                for x in range(W):
                    if hash2(x, y, int(b)) > u:
                        s = y * W + x
                        cv.ch[s] = tmp.ch[s]
                        cv.fg[s] = tmp.fg[s]
            blended = True
            break
    if not blended:
        _render_single(cv, t)

    # ---- thin system HUD (top status, bottom log strip)
    i = section_index(t)
    title = SECTIONS[i][2]
    mm, ss = int(t) // 60, int(t) % 60
    st_line = ("// STRATEGIC COMMAND TERMINAL // %s // T+%02d:%02d:%02d.%02d // %s"
               % (title, mm // 60, mm % 60, ss, int((t % 1) * 100), "STREAM OK"))
    cv.text(0, 0, st_line[:W], scale(DATA, 0.85))
    cv.text(W - 30, 0, "MUSIC: RISING TIDE", scale(DIM, 1.25))

    beat = _STATE.pulse(t)
    frac = int(beat * 30)
    ticker = ("|%-30s| NODES %04d  CLK %06d  ERR %03d  E %4.2f  BPS %5.1f"
              % ("#" * frac + "-" * (30 - frac),
                 int(120 + 30 * math.sin(t * 0.7)), int(t * 24),
                 int(4 + 3 * math.sin(t * 1.9)), _STATE.energy(t),
                 1200 + 500 * math.sin(t * 0.31)))
    cv.text(0, H - 1, ticker[:W], scale(DATA, 0.7))

    # ---- CRT / signal post
    energy = _STATE.energy(t)
    onset = _STATE.onset(t)
    if i == 1:                       # title re-index: violent signal
        post_tear(cv, t, 1.0)
        post_glitch_blocks(cv, t, 0.32)
        post_noise(cv, t, 0.0042)
        post_flicker(cv, t, 0.12)
    elif i == 4:                     # nuclear climax: maximum density
        post_tear(cv, t, 0.75 * (0.5 + energy))
        post_glitch_blocks(cv, t, 0.22 + 0.20 * onset)
        post_noise(cv, t, 0.007)
        post_flicker(cv, t, 0.10)
    elif i == 3:                     # intelligence: dark, quiet, dirty
        post_glitch_blocks(cv, t, 0.09)
        post_noise(cv, t, 0.0042)
        post_flicker(cv, t, 0.08)
    elif i == 5:                     # detente: easing off
        k = clamp((t - 158.0) / 15.0, 0, 1)
        post_tear(cv, t, 0.5 * (1 - k))
        post_noise(cv, t, 0.0042 * (1 - 0.7 * k))
        post_flicker(cv, t, 0.08 * (1 - k))
    elif i == 6:                     # evaluation: restrained
        post_noise(cv, t, 0.002)
        post_flicker(cv, t, 0.04)
    else:
        post_tear(cv, t, 0.35 * (0.3 + energy))
        post_glitch_blocks(cv, t, 0.05 + 0.15 * onset)
        post_noise(cv, t, 0.0035)
        post_flicker(cv, t, 0.08)

    post_scanlines(cv, t, 0.30, roll=True)
    post_vignette(cv)
    if prev is not None:
        post_ghost(cv, prev.ch, prev.fg, 0.30)

    # ---- bottom chronicle：后处理之后绘制，字幕区不受噪点/闪烁/撕裂影响
    chronicle.draw(cv, t)
    return cv


# ------------------------------------------------------------------ ansi
def _ansi_color(c, mode):
    if mode == "rgb":
        return "\x1b[38;2;%d;%d;%dm" % ((c >> 16) & 255, (c >> 8) & 255, c & 255)
    r, g, b = (c >> 16) & 255, (c >> 8) & 255, c & 255
    if mode == "256":
        r6, g6, b6 = int(r / 51), int(g / 51), int(b / 51)
        return "\x1b[38;5;%dm" % (16 + 36 * r6 + 6 * g6 + b6)
    # 16 colour fallback
    ri, gi, bi = r > 110, g > 110, b > 110
    idx = (4 if ri else 0) | (2 if gi else 0) | (1 if bi else 0)
    bright = 8 if (r + g + b) > 420 else 0
    return "\x1b[%dm" % (30 + bright + idx)


def canvas_to_ansi(cv, mode="rgb", pad_x=0, clear_eol=True):
    out = ["\x1b[?25l"]
    ceol = "\x1b[K" if clear_eol else ""
    pad = " " * pad_x
    for y in range(H):
        row = []
        base = y * W
        cur = -1
        line = [pad]
        for x in range(W):
            i = base + x
            fg = cv.fg[i]
            if fg != cur:
                line.append(_ansi_color(fg, mode))
                cur = fg
            line.append(cv.ch[i])
        line.append(ceol)
        out.append("".join(line))
        out.append("\n")
    return "".join(out)


def duration():
    return _DURATION
