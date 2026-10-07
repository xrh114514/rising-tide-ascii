"""Export the MV to MP4 (1280x720, 16:9) with the soundtrack muxed in.

    python export_mp4.py --out RisingTide_ColdWar_ASCII_MV.mp4

Frames are rendered from the same code the terminal player uses, so the video
is exactly what plays in the console.
"""
import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

import mv
import render

HERE = Path(__file__).resolve().parent
CW, CH = render.CW, render.CH


def find_audio():
    """仓库不附带音乐：依次在 media/、项目目录、上级目录寻找常见音频文件。"""
    for folder in (HERE / "media", HERE, HERE.parent):
        for ext in ("flac", "mp3", "wav", "m4a", "ogg"):
            for p in sorted(folder.glob("*.%s" % ext)):
                return str(p)
    return str(HERE / "media" / "song.flac")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="RisingTide_ColdWar_ASCII_MV.mp4")
    ap.add_argument("--audio", default=None, help="音乐文件（默认自动查找 media/ 目录）")
    ap.add_argument("--fps", type=float, default=30.0)
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=0.0)
    ap.add_argument("--crf", default="18")
    a = ap.parse_args()

    ffmpeg = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")
    if not ffmpeg:
        print("ffmpeg not found in PATH", file=sys.stderr)
        return 2

    W, H = __import__("engine").W, __import__("engine").H
    pw, ph = W * CW, H * CH
    end = a.end if a.end > 0 else mv.duration()
    nframes = int(round((end - a.start) * a.fps))

    cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
           "-f", "rawvideo", "-pixel_format", "rgb24",
           "-video_size", "%dx%d" % (pw, ph), "-framerate", "%g" % a.fps,
           "-i", "-"]
    audio = Path(a.audio or find_audio())
    if audio.exists():
        cmd += ["-ss", "%0.3f" % a.start, "-i", str(audio), "-map", "0:v", "-map", "1:a",
                "-c:a", "aac", "-b:a", "192k"]
    else:
        cmd += ["-map", "0:v"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", a.crf,
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-shortest",
            a.out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    atlas = render.atlas()
    prev = None
    t0 = time.time()
    try:
        for k in range(nframes):
            t = a.start + k / a.fps
            cv = mv.render_frame(t, prev)
            prev = cv
            proc.stdin.write(atlas.render(cv).tobytes())
            if k % 150 == 0 and k:
                el = time.time() - t0
                eta = el / k * (nframes - k)
                print("frame %d/%d  %.1f%%  elapsed %.0fs  eta %.0fs"
                      % (k, nframes, 100.0 * k / nframes, el, eta), flush=True)
    finally:
        proc.stdin.close()
        ret = proc.wait()
    print("done:", a.out, "frames:", nframes)
    return ret


if __name__ == "__main__":
    sys.exit(main())
