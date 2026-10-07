"""Export the MV to MP4 (16:9) with the soundtrack muxed in.

    python export_mp4.py --out mv.mp4                        # 1280x720 @30
    python export_mp4.py --out mv-2k60.mp4 --size 2560x1440 --fps 60

Frames are rendered from the same code the terminal player uses, so the video
is exactly what plays in the console.  Cell size follows from the resolution:
160x45 character grid -> 8x16 px (720p), 16x32 px (2K), 24x48 px (4K).
"""
import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

import mv
import render
from engine import W as GRID_W, H as GRID_H

HERE = Path(__file__).resolve().parent


def find_audio():
    """仓库不附带音乐：依次在 media/、项目目录、上级目录寻找常见音频文件。"""
    for folder in (HERE / "media", HERE, HERE.parent):
        for ext in ("flac", "mp3", "wav", "m4a", "ogg"):
            for p in sorted(folder.glob("*.%s" % ext)):
                return str(p)
    return str(HERE / "media" / "song.flac")


def parse_size(s):
    w, _, h = s.lower().partition("x")
    return int(w), int(h)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="RisingTide_ColdWar_ASCII_MV.mp4")
    ap.add_argument("--audio", default=None, help="音乐文件（默认自动查找 media/ 目录）")
    ap.add_argument("--size", default="1280x720",
                    help="输出分辨率：1280x720 / 2560x1440 / 3840x2160 …（16:9，160x45 字符网格）")
    ap.add_argument("--fps", type=float, default=30.0, help="帧率（30 / 60）")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=0.0)
    ap.add_argument("--crf", default="18", help="x264 质量：越小越清晰（18-20 推荐）")
    ap.add_argument("--preset", default="medium", help="x264 速度/压缩权衡")
    a = ap.parse_args()

    ffmpeg = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")
    if not ffmpeg:
        print("ffmpeg not found in PATH", file=sys.stderr)
        return 2

    pw, ph = parse_size(a.size)
    if pw % GRID_W or ph % GRID_H or abs(pw / ph - 16 / 9) > 0.01:
        print("size must be 16:9 and divisible by the 160x45 character grid "
              "(e.g. 1280x720, 2560x1440, 3840x2160)", file=sys.stderr)
        return 2
    cw, ch = pw // GRID_W, ph // GRID_H

    end = a.end if a.end > 0 else mv.duration()
    nframes = int(round((end - a.start) * a.fps))

    level = "5.1" if ph >= 1440 or a.fps > 30 else "4.1"
    cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
           "-f", "rawvideo", "-pixel_format", "rgb24",
           "-video_size", "%dx%d" % (pw, ph), "-framerate", "%g" % a.fps,
           "-i", "-"]
    audio = Path(a.audio or find_audio())
    if audio.exists():
        cmd += ["-ss", "%0.3f" % a.start, "-i", str(audio), "-map", "0:v", "-map", "1:a",
                "-c:a", "aac", "-b:a", "256k"]
    else:
        cmd += ["-map", "0:v"]
        print("warning: no audio found (looked for media/*), exporting video only",
              file=sys.stderr)
    cmd += ["-c:v", "libx264", "-preset", a.preset, "-crf", a.crf,
            "-profile:v", "high", "-level", level, "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", "-shortest", a.out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    atlas = render.atlas(cw, ch)
    print("rendering %dx%d @ %gfps, cell %dx%d, %d frames"
          % (pw, ph, a.fps, cw, ch, nframes), flush=True)
    prev = None
    t0 = time.time()
    try:
        for k in range(nframes):
            t = a.start + k / a.fps
            cv = mv.render_frame(t, prev)
            prev = cv
            proc.stdin.write(atlas.render(cv).tobytes())
            if k % 300 == 0 and k:
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
