"""Normalize resolution, aspect ratio, and loudness before concatenating beat clips sequentially via FFmpeg.

Zero ffprobe dependency — probes duration and audio streams directly via `ffmpeg -i` (works with system ffmpeg
or static binaries bundled by `imageio-ffmpeg`).
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import shutil
import subprocess

_TARGET_DIMS = {
    ("9:16", "360p"): (360, 640),
    ("9:16", "480p"): (480, 854),
    ("9:16", "720p"): (720, 1280),
    ("9:16", "768p"): (768, 1366),
    ("9:16", "1080p"): (1080, 1920),
    ("16:9", "360p"): (640, 360),
    ("16:9", "480p"): (854, 480),
    ("16:9", "720p"): (1280, 720),
    ("16:9", "768p"): (1366, 768),
    ("16:9", "1080p"): (1920, 1080),
}


def _target_size(aspect_ratio: str, resolution: str) -> tuple[int, int]:
    return _TARGET_DIMS.get((aspect_ratio, resolution), (720, 1280) if aspect_ratio == "9:16" else (1280, 720))


def _resolve_ffmpeg_bin() -> str:
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg  # type: ignore
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:
        raise FileNotFoundError("ffmpeg binary not found on PATH or via imageio-ffmpeg") from exc


def _probe_via_ffmpeg(ffmpeg_bin: str, clip_path: Path) -> tuple[float, bool]:
    proc = subprocess.run(
        [ffmpeg_bin, "-hide_banner", "-i", str(clip_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    info = (proc.stderr or "") + "\n" + (proc.stdout or "")
    duration = 10.0
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", info)
    if m:
        hours, mins, secs = int(m.group(1)), int(m.group(2)), float(m.group(3))
        duration = max(0.5, hours * 3600.0 + mins * 60.0 + secs)
    has_audio = bool(re.search(r"Stream\s+#\d+:\d+.*:\s*Audio:", info))
    return duration, has_audio


def stitch_clips(
    clips_dir: str,
    output_file: str,
    aspect_ratio: str = "9:16",
    resolution: str = "720p",
) -> None:
    clips_path = Path(clips_dir)
    mp4s = sorted(clips_path.glob("beat_*.mp4"))
    if not mp4s:
        raise FileNotFoundError(f"No beat_*.mp4 files found in {clips_dir}")

    out_path = Path(output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    width, height = _target_size(aspect_ratio, resolution)
    ffmpeg_bin = _resolve_ffmpeg_bin()

    cmd = [ffmpeg_bin, "-y"]
    filter_parts: list[str] = []
    concat_inputs: list[str] = []

    for idx, mp4 in enumerate(mp4s):
        cmd.extend(["-i", str(mp4)])
        duration, has_audio = _probe_via_ffmpeg(ffmpeg_bin, mp4)
        filter_parts.append(
            f"[{idx}:v]scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},setsar=1,fps=24,format=yuv420p[v{idx}]"
        )
        if has_audio:
            filter_parts.append(f"[{idx}:a]aresample=48000,aformat=channel_layouts=stereo[a{idx}]")
        else:
            filter_parts.append(f"anullsrc=r=48000:cl=stereo:d={duration:.3f}[a{idx}]")
        concat_inputs.append(f"[v{idx}][a{idx}]")

    n = len(mp4s)
    filter_parts.append("".join(concat_inputs) + f"concat=n={n}:v=1:a=1[vcat][acat]")

    def _run_ffmpeg(use_loudnorm: bool) -> None:
        parts = list(filter_parts)
        if use_loudnorm:
            parts.append("[acat]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]")
        else:
            parts.append("[acat]aresample=48000[aout]")

        full_cmd = list(cmd) + [
            "-filter_complex", ";".join(parts),
            "-map", "[vcat]",
            "-map", "[aout]",
            "-c:v", "libx264",
            "-crf", "18",
            "-preset", "medium",
            "-c:a", "aac",
            "-ar", "48000",
            "-b:a", "192k",
            str(out_path),
        ]
        subprocess.run(full_cmd, check=True)

    try:
        _run_ffmpeg(use_loudnorm=True)
    except subprocess.CalledProcessError:
        _run_ffmpeg(use_loudnorm=False)
    print(f"Stitched {n} clips sequentially into {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize aspect ratio/audio and stitch beat_*.mp4 clips sequentially.")
    parser.add_argument("--clips-dir", default="output/clips", help="Directory containing beat_*.mp4")
    parser.add_argument("--output", default="output/final_drama.mp4", help="Output MP4 path")
    parser.add_argument("--aspect-ratio", default="9:16", choices=["16:9", "9:16"])
    parser.add_argument("--resolution", default="720p", choices=["360p", "480p", "720p", "768p", "1080p"])
    args = parser.parse_args()
    stitch_clips(args.clips_dir, args.output, aspect_ratio=args.aspect_ratio, resolution=args.resolution)


if __name__ == "__main__":
    main()
