"""Standalone 3-Stage 1K ChatGPT Image 2.5 (gpt-image-2-5-sunburst) Asset Generator via Kie.ai API.

Generates:
  Stage A: Base character identity sheets (assets/chars/<char_id>__base.png)
  Stage B: Per-outfit character sheets anchored to base face (assets/chars/<char_id>__<outfit_id>.png)
  Stage C: Unsliced 2x2 four-panel storyboard grids (assets/storyboards/<beat_id>__grid.png)

Automatically resumes completed checkpoints (skips any character/outfit/beat that already has a saved URL
for the same aspect ratio) and writes updated URLs back into bible.json and beats.json after EVERY image.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import time
from typing import Any
import urllib.error
import urllib.request

KIE_CREATE_TASK_URL = "https://api.kie.ai/api/v1/jobs/createTask"
KIE_RECORD_INFO_URL = "https://api.kie.ai/api/v1/jobs/recordInfo"
MODEL_T2I = "gpt-image-2-5-sunburst-text-to-image"
MODEL_I2I = "gpt-image-2-5-sunburst-image-to-image"

STYLIZED_KEYWORDS = (
    "cartoon", "anime", "animation", "animated", "2d", "3d", "pixar", "disney",
    "comic", "manga", "cel-shaded", "illustration", "watercolor", "claymation", "stylized",
)
DEFAULT_PHOTOREAL_STYLE = (
    "Hyperrealistic live-action 35mm film cinematography, real human actors, "
    "photorealistic skin and fabric textures, shallow depth of field, natural cinematic lighting"
)


def _is_stylized(style: str) -> bool:
    low = (style or "").lower()
    return any(k in low for k in STYLIZED_KEYWORDS)


def _style_lock(visual_style: str) -> tuple[str, bool, str]:
    raw = (visual_style or "").strip() or DEFAULT_PHOTOREAL_STYLE
    stylized = _is_stylized(raw)
    if stylized:
        return raw, True, f"Consistent stylized aesthetic lock: {raw}."
    return (
        raw,
        False,
        "STRICT LIVE-ACTION PHOTOGRAPHY LOCK: real human actors captured on 35mm cinema camera, "
        "natural skin pores, realistic hair and fabric weave, real film lighting — strictly NO cartoon, "
        "NO anime, NO illustration, NO 2D/3D render.",
    )


def _kie_request(url: str, api_key: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST" if payload is not None else "GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Kie HTTP {exc.code}: {detail}") from exc
    if isinstance(body, dict) and body.get("code") not in (None, 200):
        raise RuntimeError(f"Kie API error {body.get('code')}: {body.get('msg') or body}")
    return body


def _poll_task(task_id: str, api_key: str, interval: float = 4.0, timeout: float = 300.0) -> str:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        info = _kie_request(f"{KIE_RECORD_INFO_URL}?taskId={task_id}", api_key)
        data = info.get("data") or {}
        state = str(data.get("state") or data.get("status") or "").lower()
        if state in {"success", "completed", "succeeded"}:
            result_json = data.get("resultJson") or data.get("result")
            if isinstance(result_json, str):
                try:
                    result_json = json.loads(result_json)
                except json.JSONDecodeError:
                    pass
            urls = []
            if isinstance(result_json, dict):
                urls = result_json.get("resultUrls") or result_json.get("urls") or []
            if not urls and isinstance(data.get("resultUrls"), list):
                urls = data["resultUrls"]
            if urls:
                return str(urls[0])
            raise RuntimeError(f"Kie task {task_id} succeeded without resultUrls: {data}")
        if state in {"fail", "failed", "error", "canceled", "cancelled"}:
            raise RuntimeError(f"Kie task {task_id} failed: {data.get('failMsg') or data}")
        time.sleep(interval)
    raise RuntimeError(f"Timed out polling Kie task {task_id} after {timeout:.0f}s")


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "epic-cinema/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        dest.write_bytes(resp.read())


def _generate_1k_image(
    prompt: str,
    api_key: str,
    aspect_ratio: str,
    dest: Path,
    input_urls: list[str] | None = None,
    dry_run: bool = False,
) -> str:
    model = MODEL_I2I if input_urls else MODEL_T2I
    input_block: dict[str, Any] = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "resolution": "1K",
        "background": "opaque",
    }
    if input_urls:
        input_block["input_urls"] = input_urls[:5]
    payload = {"model": model, "input": input_block}

    if dry_run:
        print(f"[DRY-RUN] {dest.name} -> model={model} refs={len(input_urls or [])}")
        return f"https://dry-run.local/{dest.name}"

    created = _kie_request(KIE_CREATE_TASK_URL, api_key, payload)
    task_id = (created.get("data") or {}).get("taskId")
    if not task_id:
        raise RuntimeError(f"No taskId returned for {dest.name}: {created}")
    remote_url = _poll_task(task_id, api_key)
    _download(remote_url, dest)
    print(f"[OK] Saved {dest} ({remote_url})")
    return remote_url


def build_base_prompt(visual_style: str, char: dict[str, Any]) -> str:
    style, _, lock = _style_lock(visual_style)
    return (
        f"Film casting reference sheet of {char.get('name', char['id'])}: {char.get('appearance', '')}. "
        f"Visual style lock: {style}. {lock} "
        "Show three clean views side by side on a neutral studio cyclorama background: front portrait, "
        "3/4 profile view, and full-body neutral pose in simple plain studio attire. "
        "Consistent facial bone structure, hair, and build. No text labels, no watermarks."
    )


def build_outfit_prompt(visual_style: str, char: dict[str, Any], outfit: dict[str, Any]) -> str:
    style, _, lock = _style_lock(visual_style)
    return (
        f"Using the attached base reference sheet for {char.get('name', char['id'])}, keep the EXACT same face, "
        f"skin tone, hair, age, and body build 100% identical. Visual style lock: {style}. {lock} "
        f"Dress {char.get('name', char['id'])} in this exact wardrobe: {outfit.get('description', '')}. "
        "Show three clean views on a neutral studio background: front upper-body portrait, 3/4 view, and full-body view. "
        "No text labels, no watermarks, no borders."
    )


def build_grid_prompt(
    bible: dict[str, Any],
    beat: dict[str, Any],
    env: dict[str, Any],
    props: list[dict[str, Any]],
    aspect_ratio: str,
) -> str:
    style, stylized, lock = _style_lock(str(bible.get("visual_style") or ""))
    char_names = {c["id"]: c.get("name", c["id"]) for c in bible.get("characters", [])}
    outfits_map = {(o["character_id"], o["id"]): o for o in bible.get("outfits", [])}
    outfit_clauses = [
        f"{char_names.get(cid, cid)} wears {outfits_map.get((cid, oid), {}).get('description', oid)}"
        for cid, oid in (beat.get("character_outfits") or {}).items()
    ]
    prop_clauses = [f"{p.get('name', p['id'])}: {p.get('description', '')}" for p in props]

    cuts = beat.get("cuts") or []
    panel_count = len(cuts) if len(cuts) in (4, 6) else 4
    grid_layout = (
        "2x2 four-panel",
        "2 equal columns and 2 equal rows (Top Row: Panel 1 top-left, Panel 2 top-right; Bottom Row: Panel 3 bottom-left, Panel 4 bottom-right)",
    ) if panel_count == 4 else (
        "2x3 six-panel",
        "2 equal columns and 3 equal rows (Top Row: Panel 1 top-left, Panel 2 top-right; Middle Row: Panel 3 middle-left, Panel 4 middle-right; Bottom Row: Panel 5 bottom-left, Panel 6 bottom-right)",
    )

    frame_lock = (
        f"Vertical 9:16 portrait canvas; compose EVERY one of the {panel_count} panels in vertical 9:16 portrait framing."
        if aspect_ratio == "9:16"
        else f"Full {aspect_ratio} widescreen canvas; compose EVERY one of the {panel_count} panels in {aspect_ratio} framing."
    )
    header = (
        f"Single unsliced {grid_layout[0]} {'animation' if stylized else 'cinema'} contact sheet of {panel_count} stills "
        f"strictly divided into {grid_layout[1]} in {style}."
    )
    parts = [
        header,
        frame_lock,
        f"Separate each of the {panel_count} cells cleanly with ultra-thin hairline dividers, never overlapping or repeating panels.",
        lock,
        (
            "STRICT CINEMATIC EYELINE & FOURTH-WALL LOCK: Compose every panel like candid narrative cinema — "
            "characters appear in 3/4 view, side profile, or over-the-shoulder angles with their eyes locked onto "
            "their scene partner or a physical prop, NEVER staring straight into the camera lens."
        ),
        f"Environment lock ({env.get('id', 'scene')}): {env.get('description', env.get('name', ''))}.",
        f"Time of day & lighting lock: {beat.get('time_of_day') or env.get('time_of_day', 'night')}. {env.get('lighting_lock', '')}".strip(),
    ]
    if outfit_clauses:
        parts.append("Match exact character faces and outfits from input reference sheets: " + "; ".join(outfit_clauses) + ".")
    if prop_clauses:
        parts.append("Recurring props continuity: " + "; ".join(prop_clauses) + ".")
    parts.append("Do not render panel numbers, text captions, speech bubbles, subtitles, or watermarks.")
    for cut in cuts:
        micro = f" Micro-expression: {cut['micro_expression']}." if cut.get("micro_expression") else ""
        parts.append(f"Panel {cut['panel']} ({cut['position']}, {cut['shot_type']}): {cut['action']}.{micro}")
    return " ".join(parts)


def run_asset_pipeline(
    bible_path: Path,
    beats_path: Path,
    output_dir: Path,
    aspect_ratio: str,
    api_key: str,
    force: bool = False,
    dry_run: bool = False,
) -> None:
    bible = json.loads(bible_path.read_text(encoding="utf-8"))
    beats_doc = json.loads(beats_path.read_text(encoding="utf-8"))
    style = str(bible.get("visual_style") or "")

    def _save_all() -> None:
        if not dry_run:
            bible_path.write_text(json.dumps(bible, indent=2), encoding="utf-8")
            beats_path.write_text(json.dumps(beats_doc, indent=2), encoding="utf-8")

    # Stage A: Base character sheets
    chars_by_id = {c["id"]: c for c in bible.get("characters", [])}
    for char in bible.get("characters", []):
        cid = char["id"]
        if not force and char.get("base_sheet_url"):
            print(f"[SKIP] base:{cid} already linked ({char['base_sheet_url']})")
            continue
        url = _generate_1k_image(
            build_base_prompt(style, char),
            api_key,
            aspect_ratio,
            output_dir / "chars" / f"{cid}__base.png",
            dry_run=dry_run,
        )
        char["base_sheet_url"] = url
        char["aspect_ratio"] = aspect_ratio
        _save_all()

    # Stage B: Per-outfit sheets
    outfits_by_key: dict[tuple[str, str], dict[str, Any]] = {}
    for outfit in bible.get("outfits", []):
        cid, oid = outfit["character_id"], outfit["id"]
        outfits_by_key[(cid, oid)] = outfit
        if not force and outfit.get("sheet_url"):
            print(f"[SKIP] outfit:{cid}__{oid} already linked ({outfit['sheet_url']})")
            continue
        char = chars_by_id[cid]
        url = _generate_1k_image(
            build_outfit_prompt(style, char, outfit),
            api_key,
            aspect_ratio,
            output_dir / "chars" / f"{cid}__{oid}.png",
            input_urls=[char["base_sheet_url"]],
            dry_run=dry_run,
        )
        outfit["sheet_url"] = url
        outfit["aspect_ratio"] = aspect_ratio
        _save_all()

    # Stage C: Unsliced 2x2 storyboard grids
    envs_by_id = {e["id"]: e for e in bible.get("environments", [])}
    props_by_id = {p["id"]: p for p in bible.get("props", [])}
    for beat in beats_doc.get("beats", []):
        bid = beat["beat_id"]
        if not force and beat.get("storyboard_grid_url"):
            print(f"[SKIP] grid:{bid} already linked ({beat['storyboard_grid_url']})")
            continue
        refs: list[str] = []
        for cid, oid in (beat.get("character_outfits") or {}).items():
            sheet_url = (outfits_by_key.get((cid, oid)) or {}).get("sheet_url") or (chars_by_id.get(cid) or {}).get("base_sheet_url")
            if sheet_url and sheet_url not in refs:
                refs.append(sheet_url)
        env = envs_by_id.get(beat.get("environment_id", ""), {"id": beat.get("environment_id", "scene")})
        active_props = [props_by_id[pid] for pid in beat.get("active_prop_ids", []) if pid in props_by_id]
        url = _generate_1k_image(
            build_grid_prompt(bible, beat, env, active_props, aspect_ratio),
            api_key,
            aspect_ratio,
            output_dir / "storyboards" / f"{bid}__grid.png",
            input_urls=refs,
            dry_run=dry_run,
        )
        beat["storyboard_grid_url"] = url
        beat["rendered_aspect_ratio"] = aspect_ratio
        _save_all()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate 1K ChatGPT Image 2.5 continuity assets via Kie.ai API.")
    parser.add_argument("--bible", required=True, help="Path to bible.json")
    parser.add_argument("--beats", required=True, help="Path to beats.json")
    parser.add_argument("--output-dir", default="assets", help="Output directory for PNG assets")
    parser.add_argument("--aspect-ratio", default="9:16", choices=["9:16", "16:9"])
    parser.add_argument("--force", action="store_true", help="Regenerate assets even if URLs already exist")
    parser.add_argument("--dry-run", action="store_true", help="Print planned tasks without calling Kie.ai")
    args = parser.parse_args()

    api_key = os.environ.get("KIE_API_KEY", "").strip()
    if not args.dry_run and not api_key:
        raise SystemExit("KIE_API_KEY environment variable is required unless --dry-run is set.")

    run_asset_pipeline(
        bible_path=Path(args.bible),
        beats_path=Path(args.beats),
        output_dir=Path(args.output_dir),
        aspect_ratio=args.aspect_ratio,
        api_key=api_key,
        force=args.force,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
