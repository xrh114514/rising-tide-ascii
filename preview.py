"""Render single frames to PNG for inspection:  python preview.py --t 5,34.5,50,90,135,165,182"""
import argparse
from pathlib import Path

import mv
import render


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t", default="5,20,33.2,35.5,38,50,64,90,110,135,150,165,178,190")
    ap.add_argument("--out", default="preview")
    ap.add_argument("--prefix", default="t")
    a = ap.parse_args()

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    atlas = render.atlas()
    prev = None
    t_prev = None
    for ts in a.t.split(","):
        t = float(ts)
        # keep after-images coherent when times are sorted
        if t_prev is not None and t >= t_prev:
            step = 1 / 30.0
            tt = t_prev + step
            while tt < t:
                prev = mv.render_frame(tt, prev)
                tt += step
        cv = mv.render_frame(t, prev)
        prev, t_prev = cv, t
        p = out / ("%s%07.2f.png" % (a.prefix, t))
        atlas.image(cv).save(p)
        print("wrote", p)


if __name__ == "__main__":
    main()
