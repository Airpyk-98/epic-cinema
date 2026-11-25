"""Compile bible.json + beats.json into sequential Grok Inbuilt Video Generator prompts (10s, 4-cut 2x2 grids).

Outputs:
  - output/grok_prompts.json (machine-readable list of beats with attached storyboard grid path/URL + prompt)
  - output/grok_prompts.md   (clean sequential playbook ready to feed directly into Grok Bot's inbuilt video generator)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _format_cut_audio(cut: dict[str, Any], char_voices: dict[str, tuple[str, str]]) -> str:
    mode = cut.get("audio_mode", "on_camera")
    speaker_id = (cut.get("speaker_id") or "").strip()
    speech = (cut.get("speech_text") or cut.get("dialogue") or "").strip()
    delivery = (cut.get("delivery") or "").strip()

    speaker_label = speaker_id
    voice_profile = ""
    if speaker_id in char_voices:
        name, vdesc = char_voices[speaker_id]
        speaker_label = name or speaker_id
        voice_profile = vdesc

    if mode == "silent_reaction" or not speech:
        return (
            "Audio: COMPLETELY SILENT BEAT (no spoken words, no lip movement; "
            "visible character's mouth remains firmly closed and lips sealed tight—hold on physical reaction/prop; "
            "natural quiet room tone, no upbeat music)."
        )

    vocal_parts = []
    if voice_profile:
        vocal_parts.append(f"voice: {voice_profile}")
    if delivery:
        vocal_parts.append(f"vocal delivery & mood: {delivery}")
    else:
        vocal_parts.append("vocal delivery & mood: grounded dramatic natural tone matching the scene's emotional tension")
    vocal_clause = "; ".join(vocal_parts)

    if mode in ("offscreen_l_cut", "offscreen_j_cut"):
        label = "Off-screen voiceover (L-Cut)" if mode == "offscreen_l_cut" else "Off-screen voiceover (J-Cut)"
        return (
            f"Audio ({label} — {speaker_label} speaks off-camera with {vocal_clause}): \"{speech}\" "
            "CRITICAL VISUAL LOCK: NO character shown on screen speaks—if any face is visible, their mouth stays firmly closed and lips sealed tight with zero lip movement."
        )
    return (
        f"Dialogue (ON-CAMERA ONLY — ONLY {speaker_label} visibly speaks with {vocal_clause}, "
        f"voice pitch, pace, and posture strictly matching this exact mood and social status, lips moving naturally in sync; "
        f"every other character in frame stays completely silent with mouth firmly closed): \"{speech}\""
    )


def compile_beat_prompt(beat: dict[str, Any], bible: dict[str, Any], aspect_ratio: str = "9:16") -> str:
    cuts = beat.get("cuts") or []
    if len(cuts) not in (4, 6):
        raise ValueError(f"Beat {beat.get('beat_id')} must have 4 cuts (2x2) or 6 cuts (legacy 2x3), got {len(cuts)}")
    panel_count = len(cuts)

    char_voices = {
        str(c.get("id") or "").strip(): (
            str(c.get("name") or c.get("id") or "").strip(),
            str(c.get("voice") or "").strip(),
        )
        for c in bible.get("characters", []) or []
        if c.get("id")
    }
    time_of_day = beat.get("time_of_day", "consistent scene lighting")
    outfits = beat.get("character_outfits") or {}
    outfit_note = (
        " Maintain exact character outfits: " + ", ".join(f"{k}={v}" for k, v in outfits.items()) + "."
        if outfits
        else ""
    )
    frame_rule = (
        "Strict vertical 9:16 portrait full-screen framing for every cut—never switch to 16:9 widescreen or letterbox."
        if aspect_ratio == "9:16"
        else f"Strict {aspect_ratio} full-frame framing for every cut—never letterbox or crop."
    )
    eyeline_lock = (
        "STRICT FOURTH-WALL & EYELINE LOCK: Candid narrative film footage. Characters maintain exact 3/4 profile or over-the-shoulder eyelines "
        "from the reference storyboard—eyes locked strictly on their scene partner, off-camera left/right eyeline, or a physical prop throughout the entire clip. "
        "Characters stay completely unaware of the camera and maintain off-lens gaze from start to finish."
    )
    speaker_lock = (
        "STRICT SPEAKER & LIP-SYNC LOCK: Only the explicitly named on-camera speaker moves their lips during their cut. "
        "Any non-speaking listener or silent reaction shot MUST keep their mouth firmly closed and lips unmoving—never transfer another character's dialogue onto a silent face."
    )
    prosody_lock = (
        "STRICT VOCAL MOOD & STATUS LOCK: Every spoken line MUST strictly obey its explicit vocal delivery, pitch, cadence, and social-status tone—"
        "sad or grieving lines sound fragile, quiet, slow, and subdued (never cheerful); deferential/servant lines sound soft, hesitant, and respectful (never commanding); "
        "ambient room tone only, NO cheerful or mismatched background music."
    )

    lines = [
        f"@image1 Full-frame candid narrative cinema, no split screen, no grid borders. {eyeline_lock} {frame_rule}",
        speaker_lock,
        prosody_lock,
        f"Consistent time of day and lighting: {time_of_day}.{outfit_note}",
        f"Animate the {panel_count}-panel storyboard grid sequentially in reading order across {panel_count} hard camera cuts:",
    ]
    for cut in cuts:
        micro = f" Expression: {cut['micro_expression']}." if cut.get("micro_expression") else ""
        audio = _format_cut_audio(cut, char_voices)
        sfx = f" SFX: {cut['sfx']}." if cut.get("sfx") else ""
        lines.append(
            f"[{cut['time_range']}] Cut {cut['panel']} ({cut['position']} panel, {cut['shot_type']}): "
            f"{cut['action']}{micro} {audio}{sfx}"
        )
    lines.append("AUDIO BOUNDARY: Realistic grounded cinematic dialogue and subtle ambient foley only; no intrusive background music.")
    return " ".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile sequential Grok Video prompts from bible.json & beats.json.")
    parser.add_argument("--bible", required=True, help="Path to bible.json")
    parser.add_argument("--beats", required=True, help="Path to beats.json")
    parser.add_argument("--aspect-ratio", default="9:16", choices=["9:16", "16:9"])
    parser.add_argument("--out-dir", default="output", help="Output directory for compiled prompt files")
    args = parser.parse_args()

    bible = json.loads(Path(args.bible).read_text(encoding="utf-8"))
    beats = json.loads(Path(args.beats).read_text(encoding="utf-8")).get("beats", [])
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    compiled = []
    md_sections = [f"# Sequential Grok Video Prompts — {bible.get('title', 'Epic Cinema')}\n"]
    for idx, beat in enumerate(beats, start=1):
        bid = beat["beat_id"]
        prompt = compile_beat_prompt(beat, bible, aspect_ratio=args.aspect_ratio)
        grid_ref = beat.get("storyboard_grid_url") or f"assets/storyboards/{bid}__grid.png"
        clip_name = f"output/clips/{bid}.mp4" if bid.startswith("beat_") else f"output/clips/beat_{idx:03d}_{bid}.mp4"
        compiled.append({
            "index": idx,
            "beat_id": bid,
            "duration": int(beat.get("duration") or 10),
            "aspect_ratio": args.aspect_ratio,
            "reference_grid": grid_ref,
            "target_clip_path": clip_name,
            "prompt": prompt,
        })
        md_sections.append(
            f"## {idx}. {bid} ({int(beat.get('duration') or 10)}s · {args.aspect_ratio})\n"
            f"- **Attach Reference Grid (`@image1`):** `{grid_ref}`\n"
            f"- **Save Output Clip As:** `{clip_name}`\n\n"
            f"```text\n{prompt}\n```\n"
        )

    (out_dir / "grok_prompts.json").write_text(json.dumps(compiled, indent=2), encoding="utf-8")
    (out_dir / "grok_prompts.md").write_text("\n".join(md_sections), encoding="utf-8")
    print(f"Compiled {len(compiled)} sequential Grok Video prompts to {out_dir / 'grok_prompts.md'}")


if __name__ == "__main__":
    main()
