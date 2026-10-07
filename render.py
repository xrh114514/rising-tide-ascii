"""Rasterise a character frame to RGB pixels (preview PNGs and MP4 export)."""
import numpy as np
from PIL import Image, ImageFont

from engine import W, H, is_wide

CW, CH = 8, 16                      # 默认字符单元像素尺寸（8x16 -> 1280x720）
BG = (4, 8, 10)

MONO_FONTS = [
    "C:/Windows/Fonts/consola.ttf",
    "C:/Windows/Fonts/cour.ttf",
    "C:/Windows/Fonts/lucon.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
]
CJK_FONTS = [
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simsun.ttc",
    "C:/Windows/Fonts/simhei.ttf",
]


def _load(paths, size):
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


class GlyphAtlas:
    """Pre-rendered glyph masks so frames can be composited quickly.

    cw/ch set the pixel size of one character cell: 8x16 -> 1280x720,
    16x32 -> 2560x1440 (2K), 24x48 -> 3840x2160 (4K).
    """

    def __init__(self, cw=CW, ch=CH):
        self.cw, self.ch = cw, ch
        self.mono = _load(MONO_FONTS, int(ch * 0.875))
        self.cjk = _load(CJK_FONTS, int(ch * 0.9375))
        self.cache = {}

    def mask(self, ch):
        m = self.cache.get(ch)
        if m is not None:
            return m
        wide = is_wide(ch)
        font = self.cjk if wide else self.mono
        cw = self.cw * (2 if wide else 1)
        chh = self.ch
        try:
            gm = font.getmask(ch, mode="L")
            gw, gh = gm.size
            arr = np.array(gm, dtype=np.float32).reshape(gh, gw) / 255.0
        except Exception:
            arr = np.zeros((chh, cw), dtype=np.float32)
        out = np.zeros((chh, cw), dtype=np.float32)
        oy = max(0, (chh - arr.shape[0]) // 2 + 1)
        ox = max(0, (cw - arr.shape[1]) // 2)
        h = min(chh - oy, arr.shape[0])
        w = min(cw - ox, arr.shape[1])
        out[oy:oy + h, ox:ox + w] = arr[:h, :w]
        self.cache[ch] = out
        return out

    def render(self, cv):
        """cv: engine.Canvas -> (H*ch)x(W*cw)x3 uint8 numpy image."""
        cw, chh = self.cw, self.ch
        img = np.zeros((H * chh, W * cw, 3), dtype=np.float32)
        img[:, :] = BG
        ch_arr, fg_arr = cv.ch, cv.fg
        for y in range(H):
            base = y * W
            x = 0
            while x < W:
                i = base + x
                ch = ch_arr[i]
                fg = fg_arr[i]
                if ch != " ":
                    m = self.mask(ch)
                    mh, mw = m.shape
                    col = np.array([(fg >> 16) & 255, (fg >> 8) & 255, fg & 255],
                                   dtype=np.float32)
                    y0, x0 = y * chh, x * cw
                    tile = img[y0:y0 + mh, x0:x0 + mw]
                    hh, ww = tile.shape[:2]
                    if ww != mw or hh != mh:          # 画面边缘裁剪
                        m = m[:hh, :ww]
                    tile[:] = tile * (1 - m[..., None]) + col * m[..., None]
                    x += max(1, mw // cw)
                else:
                    x += 1
        return np.clip(img, 0, 255).astype(np.uint8)

    def image(self, cv):
        return Image.fromarray(self.render(cv), "RGB")


_ATLAS = {}


def atlas(cw=CW, ch=CH):
    key = (cw, ch)
    if key not in _ATLAS:
        _ATLAS[key] = GlyphAtlas(cw, ch)
    return _ATLAS[key]
