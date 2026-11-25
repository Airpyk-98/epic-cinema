# Epic Cinema — Autonomous Grok Bot Cinema Production Skill

An end-to-end **Agent Skill** (`SKILL.md` + references + standalone Python production scripts) designed for **Grok Bot** (and any autonomous AI agent) to plan, storyboard, generate continuity-locked assets, render sequential videos with Grok's inbuilt video generator, and stitch finished short dramas or multi-hour feature films.

## What's Inside

| File | Purpose |
| :--- | :--- |
| [`SKILL.md`](SKILL.md) | Master Grok Bot skill specification (Step 0 intake → Rolling Series Memory → DramaBox scripting → Hard Approval Gate → 1K ChatGPT Image 2.5 via Kie.ai / Google Flow → Sequential Grok Video → FFmpeg Stitching) |
| [`references/cinema_rules.md`](references/cinema_rules.md) | DramaBox 4-phase arcs, Visible-Speaker Lip-Sync Lock, Fourth-Wall Eyeline Lock, and Vocal Mood / Prosody / Social-Status Lock |
| [`references/schemas.md`](references/schemas.md) | Exact JSON schemas for `series_memory.json`, `bible.json`, and `beats.json` (`2×2` four-panel `10s` beats) |
| [`references/prompt_templates.md`](references/prompt_templates.md) | Copy-paste templates for Stage A base sheets, Stage B outfit sheets, Stage C `2×2` grids (`1K` ChatGPT Image 2.5 / Google Flow), and Stage D Grok Video prompts |
| [`scripts/generate_assets_kie.py`](scripts/generate_assets_kie.py) | Standalone Python script for `1K` ChatGPT Image 2.5 (`gpt-image-2-5-sunburst`) via Kie.ai API with automatic checkpoint resume |
| [`scripts/compile_grok_prompts.py`](scripts/compile_grok_prompts.py) | Compiles `bible.json` + `beats.json` into sequential `@image1` Grok Video prompts (`output/grok_prompts.md` & `.json`) |
| [`scripts/stitch_movie.py`](scripts/stitch_movie.py) | Zero-`ffprobe` FFmpeg stitcher (uniform aspect ratio, `24fps`, `48kHz stereo`, `-14 LUFS` loudnorm) |

## Quick Start with Grok Bot

1. **Give [`SKILL.md`](SKILL.md)** (or point Grok Bot to this GitHub repo: `https://github.com/Airpyk-98/epic-cinema`) as its production skill.
2. Pitch your story idea. Grok Bot will:
   - Run **Step 0 Intake** (aspect ratio, runtime, single vs. episodic, Kie.ai API vs. Google Flow).
   - Draft your **Story Bible** (`bible.json`) + **4-cut `2×2` 10s beats** (`beats.json`) in safe 6-beat chapters with rolling Series Memory.
   - **Stop at the Hard Approval Gate** and show your estimated credit/asset count before generating anything.
3. Reply **"Go ahead"** — then prepare `1K` ChatGPT Image 2.5 sheets & `2×2` grids via Kie.ai API (or Google Flow):
   ```bash
   export KIE_API_KEY="your_kie_key"
   python scripts/generate_assets_kie.py --bible bible.json --beats beats.json --aspect-ratio 9:16
   ```
4. Compile sequential Grok Video prompts (or let Grok Bot invoke its inbuilt video generator beat-by-beat using each unsliced `2×2` grid as `@image1`):
   ```bash
   python scripts/compile_grok_prompts.py --bible bible.json --beats beats.json --aspect-ratio 9:16
   ```
5. Save clips sequentially as `output/clips/beat_001.mp4`, `beat_002.mp4`, … and stitch into your final film:
   ```bash
   python scripts/stitch_movie.py --clips-dir output/clips --output output/final_drama.mp4 --aspect-ratio 9:16 --resolution 720p
   ```
