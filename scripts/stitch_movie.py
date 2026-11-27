"""Normalize resolution, aspect ratio, and loudness before concatenating beat clips via FFmpeg."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from typing import Any

from PIL import Image, ImageDraw, ImageFont

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
    """Return a working ffmpeg binary path (PATH first, then imageio-ffmpeg static binary)."""
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg  # type: ignore
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:
        raise FileNotFoundError("ffmpeg binary not found on PATH or via imageio-ffmpeg") from exc


def _probe_via_ffmpeg(ffmpeg_bin: str, clip_path: Path) -> tuple[float, bool]:
    """Parse duration and audio stream presence directly from `ffmpeg -i` stderr (requires zero ffprobe)."""
    proc = subprocess.run(
        [ffmpeg_bin, "-hide_banner", "-i", str(clip_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    info = (proc.stderr or "") + "\n" + (proc.stdout or "")
    duration = 5.0
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", info)
    if m:
        hours, mins, secs = int(m.group(1)), int(m.group(2)), float(m.group(3))
        duration = max(0.5, hours * 3600.0 + mins * 60.0 + secs)
    has_audio = bool(re.search(r"Stream\s+#\d+:\d+.*:\s*Audio:", info))
    return duration, has_audio


def _clip_duration_and_audio(clip_path: Path, ffmpeg_bin: str | None = None) -> tuple[float, bool]:
    """Probe duration and whether an audio stream is present (uses ffprobe if installed, else ffmpeg -i)."""
    ffprobe_bin = shutil.which("ffprobe")
    if ffprobe_bin:
        dur_res = subprocess.run(
            [
                ffprobe_bin,
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(clip_path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        duration = float((dur_res.stdout or "5.0").strip() or 5.0)
        aud_res = subprocess.run(
            [
                ffprobe_bin,
                "-v", "error",
                "-select_streams", "a:0",
                "-show_entries", "stream=codec_type",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(clip_path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        has_audio = "audio" in (aud_res.stdout or "")
        return duration, has_audio
    return _probe_via_ffmpeg(ffmpeg_bin or _resolve_ffmpeg_bin(), clip_path)


def _load_cinema_font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a crisp TrueType font across Linux (GitHub Actions) and Windows runners with clean fallback."""
    candidates = (
        [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "C:/Windows/Fonts/segoeuib.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
        ]
        if bold
        else [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]
    )
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size=size)
            except Exception:
                continue
    return ImageFont.load_default()


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: Any, max_width: int) -> list[str]:
    words = str(text or "").split()
    if not words:
        return []
    lines: list[str] = []
    cur = words[0]
    for w in words[1:]:
        test = f"{cur} {w}"
        bbox = draw.textbbox((0, 0), test, font=font)
        if (bbox[2] - bbox[0]) <= max_width:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def _render_card_image(
    dest_png: Path,
    width: int,
    height: int,
    *,
    eyebrow: str,
    headline: str,
    body_lines: list[str] | None = None,
) -> None:
    """Render a sleek dark cinema title/cast/credit card PNG with gold accent rule."""
    img = Image.new("RGB", (width, height), (7, 8, 13))
    draw = ImageDraw.Draw(img)

    # Subtle cinematic vignette / top-bottom letterbox framing bars
    margin_x = int(width * 0.1)
    max_text_w = width - (margin_x * 2)
    accent = (245, 166, 35)
    muted = (165, 174, 192)
    fg = (245, 247, 252)

    base_unit = min(width, height)
    eyebrow_font = _load_cinema_font(max(16, int(base_unit * 0.036)), bold=True)
    head_font = _load_cinema_font(max(28, int(base_unit * 0.082)), bold=True)
    body_font = _load_cinema_font(max(18, int(base_unit * 0.044)), bold=False)

    head_wrapped = _wrap_text(draw, headline, head_font, max_text_w)
    body_wrapped: list[str] = []
    for raw_line in body_lines or []:
        body_wrapped.extend(_wrap_text(draw, raw_line, body_font, max_text_w))

    # Measure total vertical block to center cleanly
    line_gap = max(8, int(base_unit * 0.018))
    total_h = 0
    if eyebrow:
        eb = draw.textbbox((0, 0), eyebrow.upper(), font=eyebrow_font)
        total_h += (eb[3] - eb[1]) + line_gap * 2
    for hl in head_wrapped:
        hb = draw.textbbox((0, 0), hl, font=head_font)
        total_h += (hb[3] - hb[1]) + line_gap
    total_h += line_gap * 2 + 4  # gold divider rule
    for bl in body_wrapped:
        bb = draw.textbbox((0, 0), bl, font=body_font)
        total_h += (bb[3] - bb[1]) + int(line_gap * 0.9)

    y = max(int(height * 0.1), (height - total_h) // 2)

    if eyebrow:
        eb_txt = eyebrow.upper()
        eb = draw.textbbox((0, 0), eb_txt, font=eyebrow_font)
        tw = eb[2] - eb[0]
        draw.text(((width - tw) // 2, y), eb_txt, fill=accent, font=eyebrow_font)
        y += (eb[3] - eb[1]) + line_gap * 2

    for hl in head_wrapped:
        hb = draw.textbbox((0, 0), hl, font=head_font)
        tw = hb[2] - hb[0]
        draw.text(((width - tw) // 2, y), hl, fill=fg, font=head_font)
        y += (hb[3] - hb[1]) + line_gap

    # Centered gold hairline divider
    rule_w = max(80, int(width * 0.22))
    y += line_gap
    draw.rectangle(
        [(width - rule_w) // 2, y, (width + rule_w) // 2, y + 3],
        fill=accent,
    )
    y += line_gap * 2

    for bl in body_wrapped:
        bb = draw.textbbox((0, 0), bl, font=body_font)
        tw = bb[2] - bb[0]
        draw.text(((width - tw) // 2, y), bl, fill=muted, font=body_font)
        y += (bb[3] - bb[1]) + int(line_gap * 0.9)

    dest_png.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest_png, format="PNG")


def _png_to_video_clip(
    ffmpeg_bin: str,
    png_path: Path,
    out_mp4: Path,
    duration_sec: float,
    width: int,
    height: int,
) -> Path:
    """Turn a rendered cinema card PNG into a smooth fade-in/fade-out 24fps MP4 with silent 48kHz stereo audio."""
    fade_out_start = max(0.2, duration_sec - 0.65)
    vf = (
        f"scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},setsar=1,fps=24,format=yuv420p,"
        f"fade=t=in:st=0:d=0.6,fade=t=out:st={fade_out_start:.2f}:d=0.6"
    )
    subprocess.run(
        [
            ffmpeg_bin, "-y",
            "-loop", "1", "-t", f"{duration_sec:.2f}", "-i", str(png_path),
            "-f", "lavfi", "-t", f"{duration_sec:.2f}", "-i", "anullsrc=r=48000:cl=stereo",
            "-vf", vf,
            "-c:v", "libx264", "-crf", "18", "-preset", "fast",
            "-c:a", "aac", "-ar", "48000", "-b:a", "192k",
            "-shortest",
            str(out_mp4),
        ],
        check=True,
    )
    return out_mp4


def _build_30s_hook_trailer(
    ffmpeg_bin: str,
    mp4s: list[Path],
    out_mp4: Path,
    width: int,
    height: int,
    target_seconds: float = 30.0,
) -> Path:
    """Compile an intense fast-cut 30s thriller cold-open montage from the most dramatic moments across the movie."""
    if not mp4s:
        raise ValueError("Cannot build 30s thriller hook without movie clips.")

    # Measure clip durations and sample 2.5s high-energy excerpts evenly across the film up to 30s
    clip_infos = [(p, _clip_duration_and_audio(p, ffmpeg_bin=ffmpeg_bin)) for p in mp4s]
    total_movie_sec = sum(d for _, (d, _) in clip_infos)
    # Cap teaser to min(30s, 75% of total movie runtime) so very short 30s movies still stay snappy
    effective_target = min(target_seconds, max(8.0, total_movie_sec * 0.75)) if total_movie_sec < 45.0 else target_seconds

    segment_len = 2.5
    num_segments = max(3, min(12, int(round(effective_target / segment_len))))

    # Build evenly spaced (clip_path, start_sec, seg_dur, has_audio) excerpts prioritizing mid/late dramatic peaks
    picks: list[tuple[Path, float, float, bool]] = []
    n_clips = len(clip_infos)
    for i in range(num_segments):
        clip_idx = min(n_clips - 1, int((i * n_clips) / num_segments))
        clip_path, (dur, has_audio) = clip_infos[clip_idx]
        # Offset into the clip (alternate 20%, 50%, 70% into beats to capture climax/action cuts)
        frac = (0.2, 0.5, 0.7)[i % 3]
        seg_dur = min(segment_len, max(1.0, dur - 0.3))
        start_sec = min(max(0.0, dur - seg_dur - 0.1), dur * frac)
        picks.append((clip_path, start_sec, seg_dur, has_audio))

    cmd = [ffmpeg_bin, "-y"]
    filter_parts: list[str] = []
    concat_inputs: list[str] = []
    for idx, (clip_path, start_sec, seg_dur, has_audio) in enumerate(picks):
        cmd.extend(["-ss", f"{start_sec:.2f}", "-t", f"{seg_dur:.2f}", "-i", str(clip_path)])
        fade_in = ",fade=t=in:st=0:d=0.35" if idx == 0 else ""
        fade_out = f",fade=t=out:st={max(0.1, seg_dur - 0.5):.2f}:d=0.5" if idx == len(picks) - 1 else ""
        filter_parts.append(
            f"[{idx}:v]scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},setsar=1,fps=24,format=yuv420p,eq=contrast=1.08:saturation=1.06{fade_in}{fade_out}[v{idx}]"
        )
        if has_audio:
            filter_parts.append(f"[{idx}:a]aresample=48000,aformat=channel_layouts=stereo[a{idx}]")
        else:
            filter_parts.append(f"anullsrc=r=48000:cl=stereo:d={seg_dur:.3f}[a{idx}]")
        concat_inputs.append(f"[v{idx}][a{idx}]")

    filter_parts.append("".join(concat_inputs) + f"concat=n={len(picks)}:v=1:a=1[vcat][acat]")
    filter_parts.append("[acat]aresample=48000[aout]")
    subprocess.run(
        cmd + [
            "-filter_complex", ";".join(filter_parts),
            "-map", "[vcat]",
            "-map", "[aout]",
            "-c:v", "libx264", "-crf", "18", "-preset", "fast",
            "-c:a", "aac", "-ar", "48000", "-b:a", "192k",
            str(out_mp4),
        ],
        check=True,
    )
    return out_mp4


def stitch_clips(
    clips_dir: str,
    output_file: str,
    aspect_ratio: str = "16:9",
    resolution: str = "720p",
    *,
    packaging_options: dict[str, Any] | None = None,
    bible: dict[str, Any] | None = None,
) -> None:
    clips_path = Path(clips_dir)
    mp4s = sorted(clips_path.glob("beat_*.mp4"))
    if not mp4s:
        raise FileNotFoundError(f"No beat_*.mp4 files found in {clips_dir}")

    out_path = Path(output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    width, height = _target_size(aspect_ratio, resolution)
    ffmpeg_bin = _resolve_ffmpeg_bin()

    pkg = packaging_options if isinstance(packaging_options, dict) else {}
    bible_data = bible if isinstance(bible, dict) else {}
    movie_title = str(bible_data.get("title") or "UNTITLED DRAMA").strip()
    cast_names = [
        str(c.get("name") or c.get("id") or "").strip()
        for c in (bible_data.get("characters") or [])
        if str(c.get("name") or c.get("id") or "").strip()
    ]
    producer_line = str(pkg.get("produced_by_text") or "").strip() or "Short-Drama Studio"

    with tempfile.TemporaryDirectory() as pkg_tmp:
        tmp_dir = Path(pkg_tmp)
        ordered_segments: list[Path] = []

        # 1. Optional 30s Intense Thriller Hook Compilation right at the very beginning
        if pkg.get("include_hook_trailer_30s"):
            hook_mp4 = _build_30s_hook_trailer(
                ffmpeg_bin, mp4s, tmp_dir / "00_hook_trailer_30s.mp4", width, height, target_seconds=30.0
            )
            ordered_segments.append(hook_mp4)

        # 2. Optional Movie Title Appearance Card
        if pkg.get("include_title_card"):
            title_png = tmp_dir / "01_title_card.png"
            _render_card_image(
                title_png, width, height,
                eyebrow="NOW PRESENTING",
                headline=movie_title.upper(),
                body_lines=["A Short-Drama Original"],
            )
            ordered_segments.append(
                _png_to_video_clip(ffmpeg_bin, title_png, tmp_dir / "01_title_card.mp4", 4.0, width, height)
            )

        # 3. Main Movie Beats (sequential)
        ordered_segments.extend(mp4s)

        # 4. Optional Cast Scene listing all characters in the movie
        if pkg.get("include_cast_scene") and cast_names:
            # Paginate up to 6 names per card so every name stays crisp & readable
            page_size = 6
            for page_idx in range(0, len(cast_names), page_size):
                chunk = cast_names[page_idx : page_idx + page_size]
                cast_png = tmp_dir / f"90_cast_{page_idx}.png"
                _render_card_image(
                    cast_png, width, height,
                    eyebrow="STARRING" if page_idx == 0 else "FEATURING",
                    headline="CAST",
                    body_lines=chunk,
                )
                ordered_segments.append(
                    _png_to_video_clip(
                        ffmpeg_bin,
                        cast_png,
                        tmp_dir / f"90_cast_{page_idx}.mp4",
                        max(4.5, 1.0 * len(chunk) + 1.5),
                        width,
                        height,
                    )
                )

        # 5. Optional 'Produced by' Credit Scene
        if pkg.get("include_produced_by"):
            clean_prod = re.sub(r"^produced\s+by\s*:?\s*", "", producer_line, flags=re.IGNORECASE).strip() or producer_line
            prod_png = tmp_dir / "99_produced_by.png"
            _render_card_image(
                prod_png, width, height,
                eyebrow="PRODUCED BY",
                headline=clean_prod,
                body_lines=[movie_title],
            )
            ordered_segments.append(
                _png_to_video_clip(ffmpeg_bin, prod_png, tmp_dir / "99_produced_by.mp4", 4.0, width, height)
            )

        cmd = [ffmpeg_bin, "-y"]
        filter_parts: list[str] = []
        concat_inputs: list[str] = []

        for idx, mp4 in enumerate(ordered_segments):
            cmd.extend(["-i", str(mp4)])
            duration, has_audio = _clip_duration_and_audio(mp4, ffmpeg_bin=ffmpeg_bin)
            filter_parts.append(
                f"[{idx}:v]scale={width}:{height}:force_original_aspect_ratio=increase,"
                f"crop={width}:{height},setsar=1,fps=24,format=yuv420p[v{idx}]"
            )
            if has_audio:
                filter_parts.append(
                    f"[{idx}:a]aresample=48000,aformat=channel_layouts=stereo[a{idx}]"
                )
            else:
                filter_parts.append(
                    f"anullsrc=r=48000:cl=stereo:d={duration:.3f}[a{idx}]"
                )
            concat_inputs.append(f"[v{idx}][a{idx}]")

        n = len(ordered_segments)
        filter_parts.append(
            "".join(concat_inputs) + f"concat=n={n}:v=1:a=1[vcat][acat]"
        )

        def _run_ffmpeg(use_loudnorm: bool) -> None:
            parts = list(filter_parts)
            if use_loudnorm:
                parts.append("[acat]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]")
                audio_map = "[aout]"
            else:
                parts.append("[acat]aresample=48000[aout]")
                audio_map = "[aout]"

            full_cmd = list(cmd) + [
                "-filter_complex", ";".join(parts),
                "-map", "[vcat]",
                "-map", audio_map,
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
            # Purely silent streams can cause loudnorm to emit NaN on FFmpeg 8+; retry without loudnorm.
            _run_ffmpeg(use_loudnorm=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize aspect ratio/audio and stitch beat_*.mp4 clips.")
    parser.add_argument("--clips-dir", default="output/clips", help="Directory containing beat_*.mp4")
    parser.add_argument("--output", default="output/final_drama.mp4", help="Output MP4 path")
    parser.add_argument("--aspect-ratio", default="16:9", choices=["16:9", "9:16"])
    parser.add_argument("--resolution", default="720p", choices=["360p", "480p", "720p", "768p", "1080p"])
    parser.add_argument("--bible", default=None, help="Optional bible.json for title/cast packaging cards")
    parser.add_argument("--packaging-json", default=None, help="Optional JSON string/path with packaging_options")
    args = parser.parse_args()
    bible_obj = json.loads(Path(args.bible).read_text(encoding="utf-8")) if args.bible else None
    pkg_obj = None
    if args.packaging_json:
        p = Path(args.packaging_json)
        pkg_obj = json.loads(p.read_text(encoding="utf-8")) if p.exists() else json.loads(args.packaging_json)
    stitch_clips(
        args.clips_dir,
        args.output,
        aspect_ratio=args.aspect_ratio,
        resolution=args.resolution,
        packaging_options=pkg_obj,
        bible=bible_obj,
    )


if __name__ == "__main__":
    main()
