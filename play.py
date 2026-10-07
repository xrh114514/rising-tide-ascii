"""Terminal player for the ASCII MV.

    python play.py                       play from 0:00 with audio
    python play.py --start 33            start at 0:33
    python play.py --no-audio            silent preview
    python play.py --color 256           256-colour terminals
    python play.py --offset -0.15        nudge audio sync (seconds)

Audio clock drives the frames: the picture is rendered for the moment the
music is at, so the two stay together for the whole 3:21.
"""
import argparse
import ctypes
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import mv
from engine import W, H

HERE = Path(__file__).resolve().parent


def find_audio():
    """仓库不附带音乐：依次在 media/、项目目录、上级目录寻找常见音频文件。"""
    for folder in (HERE / "media", HERE, HERE.parent):
        for ext in ("flac", "mp3", "wav", "m4a", "ogg"):
            for p in sorted(folder.glob("*.%s" % ext)):
                return str(p)
    return str(HERE / "media" / "song.flac")


def enable_vt():
    if sys.platform != "win32":
        return
    try:
        k32 = ctypes.windll.kernel32
        h = k32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if k32.GetConsoleMode(h, ctypes.byref(mode)):
            k32.SetConsoleMode(h, mode.value | 0x0004)
    except Exception:
        pass


def find_player():
    for name in ("ffplay", "ffplay.exe"):
        p = shutil.which(name)
        if p:
            return p
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", default=None, help="音乐文件（默认自动查找 media/ 目录）")
    ap.add_argument("--no-audio", action="store_true")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--offset", type=float, default=0.22,
                    help="audio latency compensation in seconds")
    ap.add_argument("--fps", type=float, default=30.0)
    ap.add_argument("--color", choices=("rgb", "256", "16"), default="rgb")
    a = ap.parse_args()

    enable_vt()
    cols = shutil.get_terminal_size((W + 2, H + 2)).columns
    pad_x = max(0, (cols - W) // 2)

    audio = None
    if not a.no_audio:
        path = Path(a.audio or find_audio())
        if not path.exists():
            print("audio file not found:", path, file=sys.stderr)
            return 2
        player = find_player()
        if player:
            audio = subprocess.Popen(
                [player, "-nodisp", "-autoexit", "-loglevel", "quiet",
                 "-ss", "%0.3f" % a.start, str(path)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            print("ffplay not found - running silent (install ffmpeg for audio)",
                  file=sys.stderr)

    out = sys.stdout
    out.write("\x1b[2J\x1b[H\x1b[?25l")
    out.flush()

    t0 = time.perf_counter() + a.offset
    frame_dt = 1.0 / a.fps
    prev = None
    next_t = a.start
    try:
        while next_t < mv.duration():
            now = time.perf_counter() - t0 + a.start
            if now < next_t - 0.002:
                time.sleep(min(frame_dt, next_t - now))
                continue
            cv = mv.render_frame(next_t, prev)
            prev = cv
            out.write("\x1b[H")
            out.write(mv.canvas_to_ansi(cv, mode=a.color, pad_x=pad_x))
            out.flush()
            next_t += frame_dt
            late = (time.perf_counter() - t0 + a.start) - next_t
            if late > 0.5:            # fell behind badly: skip frames
                next_t += late
    except KeyboardInterrupt:
        pass
    finally:
        out.write("\x1b[0m\x1b[?25h\n")
        out.flush()
        if audio and audio.poll() is None:
            audio.terminate()
    return 0


if __name__ == "__main__":
    sys.exit(main())
