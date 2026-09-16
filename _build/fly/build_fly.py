#!/usr/bin/env python3
"""
P6 hero fly-by: master clip -> the two encodes the page scrubs, plus a frame
index for each.

    python3 _build/fly/build_fly.py /path/to/kling30-master.mp4

The master is the Kling 3.0 generation from the upscaled render (1920x1080,
24 fps, 10 s; it lives in the Magnific account). Only the first 8 s are used:
after that the lens starts leaning wide-angle.

WHY AN INDEX
The page does not seek a <video>. It fetches the MP4 whole and decodes frames
itself with WebCodecs, so it can put a frame on screen on every display
refresh and blend neighbouring frames while you scroll. WebCodecs takes raw
encoded samples, not a file, so each MP4 gets a small JSON beside it: the
decoder config (codec string + avcC) and the byte range of every frame.

ENCODE CHOICES
- No B-frames: decode order equals display order, so a frame index is a
  timestamp and nothing has to be reordered.
- A keyframe every 12 frames: to show any frame the page decodes at most its
  12-frame group, and it only ever holds a few groups in memory.
- hqdn3d before scaling: generated foliage shimmers frame to frame, which
  looks like noise when scrubbed and costs bytes.
"""

import base64
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "assets", "fly")

FPS = 24
FRAMES = 192          # 8.0 s
GOP = 12

VARIANTS = {
    # desktop and tablets: the full 16:9 frame
    "wide": {"vf": "scale=1600:900:flags=lanczos", "crf": 28},
    # phones: the stage is roughly 4:5, so ship only the centre 4:5 of the
    # frame instead of paying for a 16:9 picture the phone would crop away
    "tall": {"vf": "crop=864:1080:528:0,scale=720:900:flags=lanczos", "crf": 27},
}


def run(*cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout


def avcc(data: bytes) -> bytes:
    """The avcC box payload (SPS/PPS) that WebCodecs wants as `description`."""
    i = data.find(b"avcC")
    if i < 4:
        sys.exit("no avcC box: not an H.264 MP4?")
    size = int.from_bytes(data[i - 4:i], "big")
    return data[i + 4:i - 4 + size]


def index(mp4: str) -> dict:
    data = open(mp4, "rb").read()
    desc = avcc(data)
    w, h = run("ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
               "stream=width,height", "-of", "csv=p=0", mp4).strip().split(",")
    frames = []
    for line in run("ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                    "packet=pos,size,flags", "-of", "csv=p=0", mp4).split():
        size, pos, flags = line.split(",")
        frames.append([int(pos), int(size), 1 if flags.startswith("K") else 0])
    # sanity: every sample starts with a 4-byte NAL length that fits inside it
    for pos, size, _ in frames:
        n = int.from_bytes(data[pos:pos + 4], "big")
        assert 0 < n <= size - 4, f"sample at {pos} does not look like AVCC"
    assert frames[0][2] == 1, "first frame must be a keyframe"
    return {
        "codec": "avc1.%02x%02x%02x" % (desc[1], desc[2], desc[3]),
        "width": int(w), "height": int(h), "fps": FPS,
        "description": base64.b64encode(desc).decode(),
        "frames": frames,
    }


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    master = sys.argv[1]
    os.makedirs(OUT, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        run("ffmpeg", "-y", "-i", master, "-frames:v", str(FRAMES),
            "-vf", "hqdn3d=1.5:1.5:7:7", os.path.join(tmp, "f%03d.png"))
        for name, v in VARIANTS.items():
            mp4 = os.path.join(OUT, f"p6-fly-{name}.mp4")
            run("ffmpeg", "-y", "-framerate", str(FPS), "-i", os.path.join(tmp, "f%03d.png"),
                "-vf", v["vf"], "-c:v", "libx264", "-profile:v", "high", "-preset", "slow",
                "-crf", str(v["crf"]), "-bf", "0", "-g", str(GOP), "-keyint_min", str(GOP),
                "-sc_threshold", "0", "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart", mp4)
            meta = index(mp4)
            with open(mp4[:-4] + ".json", "w") as f:
                json.dump(meta, f, separators=(",", ":"))
            print(f"{name}: {meta['width']}x{meta['height']} {len(meta['frames'])} frames "
                  f"{os.path.getsize(mp4) // 1024} KB, {meta['codec']}")


if __name__ == "__main__":
    main()
