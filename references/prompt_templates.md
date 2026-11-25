# Epic Cinema — Production Prompt Templates

Use these exact prompt templates for **ChatGPT Image 2.5 (`1K`, Kie.ai API or Google Flow)** and **Grok Bot's Inbuilt Video Generator**.

---

## Stage A: Base Character Sheet (`1K` · `gpt-image-2-5-sunburst-text-to-image` or Google Flow)

```text
Hyperrealistic live-action film casting reference sheet of {character.name}: {character.appearance}.
Visual style lock: {bible.visual_style}.
STRICT LIVE-ACTION PHOTOGRAPHY LOCK: real human actor photographed on 35mm cinema camera, natural skin pores, realistic hair and fabric texture, authentic cinema lighting — strictly NO cartoon, NO anime, NO illustration, NO 2D/3D render.
Show three clean views side by side on a neutral studio cyclorama background: front portrait, 3/4 profile view, and full-body neutral pose in simple plain studio attire.
Consistent facial bone structure, exact hair and eye details, clean neutral softbox lighting.
No text labels, no watermarks, no frame numbers.
```

---

## Stage B: Per-Outfit Character Sheet (`1K` · `gpt-image-2-5-sunburst-image-to-image` with `input_urls: [base_sheet_url]`)

```text
Using the attached base reference sheet for {character.name}, keep the EXACT same face, skin tone, hair, age, and body build 100% identical.
Visual style lock: {bible.visual_style}.
STRICT LIVE-ACTION PHOTOGRAPHY LOCK: real human actor photographed on 35mm film, photorealistic fabric weave and skin texture — strictly NO cartoon, NO anime, NO illustration.
Dress {character.name} in this exact wardrobe: {outfit.description}.
Show three clean views on a neutral studio background: front upper-body portrait, 3/4 view, and full-body view showing the complete outfit clearly.
No text labels, no watermarks, no borders.
```

---

## Stage C: Unsliced `2×2` Four-Panel Storyboard Grid (`1K` · `gpt-image-2-5-sunburst-image-to-image` with `input_urls: [active outfit sheet URLs]`)

```text
Single unsliced 2x2 four-panel cinema contact sheet of 4 hyperrealistic live-action film stills strictly divided into 2 equal columns and 2 equal rows (Top Row: Panel 1 top-left, Panel 2 top-right; Bottom Row: Panel 3 bottom-left, Panel 4 bottom-right) in {bible.visual_style}.
{Vertical 9:16 portrait canvas; compose EVERY one of the 4 panels in vertical 9:16 portrait framing. | Full 16:9 widescreen canvas; compose EVERY one of the 4 panels in 16:9 framing.}
Separate each of the 4 cells cleanly with ultra-thin hairline dividers, never overlapping or repeating panels.
STRICT LIVE-ACTION PHOTOGRAPHY LOCK: real human actors captured on 35mm cinema lens, photorealistic skin/hair/fabric textures, real film lighting — strictly NO cartoon, NO anime, NO illustration.
STRICT CINEMATIC EYELINE & FOURTH-WALL LOCK: Compose every panel like candid narrative cinema — characters appear in 3/4 view, side profile, or over-the-shoulder angles with their eyes locked onto their scene partner or a physical prop, NEVER staring straight into the camera lens.
Environment lock ({env.id}): {env.description}.
Time of day & lighting lock: {beat.time_of_day}. {env.lighting_lock}.
Match exact character faces and outfits from input reference sheets: {Name wears outfit_description; ...}.
Recurring props continuity: {Prop: description; ...}.
Do not render panel numbers, text captions, speech bubbles, subtitles, or watermarks.
Panel 1 (top-left, {cut1.shot_type}): {cut1.action}. Micro-expression: {cut1.micro_expression}.
Panel 2 (top-right, {cut2.shot_type}): {cut2.action}. Micro-expression: {cut2.micro_expression}.
Panel 3 (bottom-left, {cut3.shot_type}): {cut3.action}. Micro-expression: {cut3.micro_expression}.
Panel 4 (bottom-right, {cut4.shot_type}): {cut4.action}. Micro-expression: {cut4.micro_expression}.
```

---

## Stage D: Grok Inbuilt Video Generator Prompt (`10s` Beat · Attach ONLY the Unsliced `2×2` Grid as `@image1`)

```text
@image1 Full-frame candid narrative cinema, no split screen, no grid borders.
STRICT FOURTH-WALL & EYELINE LOCK: Candid narrative film footage. Characters maintain exact 3/4 profile or over-the-shoulder eyelines from the reference storyboard — eyes locked strictly on their scene partner, off-camera left/right eyeline, or a physical prop throughout the entire clip. Characters stay completely unaware of the camera and maintain off-lens gaze from start to finish.
Strict {9:16 vertical portrait | 16:9 widescreen} full-frame framing for every cut — never letterbox or crop.
STRICT SPEAKER & LIP-SYNC LOCK: Only the explicitly named on-camera speaker moves their lips during their cut. Any non-speaking listener or silent reaction shot MUST keep their mouth firmly closed and lips unmoving — never transfer another character's dialogue onto a silent face.
STRICT VOCAL MOOD & STATUS LOCK: Every spoken line MUST strictly obey its explicit vocal delivery, pitch, cadence, and social-status tone — sad or grieving lines sound fragile, quiet, slow, and subdued (never cheerful); deferential/servant lines sound soft, hesitant, and respectful (never commanding); ambient room tone only, NO cheerful or mismatched background music.
Consistent time of day and lighting: {beat.time_of_day}. Maintain exact character outfits: {char=outfit, ...}.
Animate the 4-panel storyboard grid sequentially in reading order across 4 hard camera cuts:

[0.0s-2.5s] Cut 1 (top-left panel, {cut1.shot_type}): {cut1.action} Expression: {cut1.micro_expression}. {Formatted Audio Directive} SFX: {cut1.sfx}.
[2.5s-5.0s] Cut 2 (top-right panel, {cut2.shot_type}): {cut2.action} Expression: {cut2.micro_expression}. {Formatted Audio Directive} SFX: {cut2.sfx}.
[5.0s-7.5s] Cut 3 (bottom-left panel, {cut3.shot_type}): {cut3.action} Expression: {cut3.micro_expression}. {Formatted Audio Directive} SFX: {cut3.sfx}.
[7.5s-10.0s] Cut 4 (bottom-right panel, {cut4.shot_type}): {cut4.action} Expression: {cut4.micro_expression}. {Formatted Audio Directive} SFX: {cut4.sfx}.

AUDIO BOUNDARY: Realistic grounded cinematic dialogue and subtle ambient foley only; no intrusive background music.
```

### Formatted Audio Directive Variants (per Cut)
- **On-Camera Dialogue (`on_camera`):**
  `Dialogue (ON-CAMERA ONLY — ONLY {speaker_name} visibly speaks with voice: {voice_profile}; vocal delivery & mood: {delivery}, voice pitch, pace, and posture strictly matching this exact mood and social status, lips moving naturally in sync; every other character in frame stays completely silent with mouth firmly closed): "{speech_text}"`
- **Silent Listener Reaction (`silent_reaction`):**
  `Audio: COMPLETELY SILENT BEAT (no spoken words, no lip movement; visible character's mouth remains firmly closed and lips sealed tight — hold on physical reaction/prop; natural quiet room tone, no upbeat music).`
- **Face-Free Prop/Env Offscreen Voiceover (`offscreen_l_cut` / `offscreen_j_cut`):**
  `Audio (Off-screen voiceover — {speaker_name} speaks off-camera with voice: {voice_profile}; vocal delivery & mood: {delivery}): "{speech_text}" CRITICAL VISUAL LOCK: NO character shown on screen speaks.`
