# Epic Cinema — Data & Continuity Schemas

Use these exact JSON structures for `series_memory.json`, `bible.json`, and `beats.json` so assets, episodes, and `scripts/` stay 100% deterministic.

---

## 1. `series_memory.json` (Rolling Canon Ledger — Zero Context Drift)
```json
{
  "premise_and_tone": "Grounded modern corporate-family betrayal drama; calm restrained performances, no melodrama.",
  "episode_recaps": [
    "Episode 1: Marcus secretly forged the clinic deed; Denise discovered the mismatched signature on the closing copy.",
    "Episode 2: Kiara warned Denise in the church parking lot; Mama Ruth collapsed after seeing the eviction notice."
  ],
  "active_plot_threads": [
    "Denise holds the notarized original deed hidden in her coat lining.",
    "Marcus does not yet know Kiara switched sides."
  ],
  "user_directives": [
    "Keep Denise calm and calculating, never screaming.",
    "Servant and junior staff lines must sound quiet, hesitant, and deferential.",
    "Reuse Episode 1 & 2 character/outfit sheets verbatim in Episode 3."
  ]
}
```

---

## 2. `bible.json` (Locked Cast, Multi-Outfit Sheets, Environments & Props)
Every character gets one `base_sheet_url` (`<char_id>__base.png`), and **each outfit gets its own `sheet_url`** (`<char_id>__<outfit_id>.png`) generated from that base face at `1K` resolution on ChatGPT Image 2.5.

```json
{
  "title": "The Silent Heir",
  "visual_style": "Hyperrealistic live-action 35mm film cinematography, real human actors, photorealistic skin and fabric textures, shallow depth of field, high-contrast natural lighting",
  "characters": [
    {
      "id": "denise",
      "name": "Denise Okafor",
      "appearance": "Early 30s Black woman, poised sharp features, warm dark brown skin, sleek low bun, subtle gold stud earrings, medium build",
      "voice": "Calm controlled mezzo-soprano, measured deliberate cadence",
      "base_sheet_url": ""
    },
    {
      "id": "bola",
      "name": "Bola (Housekeeper)",
      "appearance": "Mid-40s West African woman, tired gentle eyes, neat braided hair under dark scarf, modest build",
      "voice": "Soft humble low-volume alto, polite deferential cadence",
      "base_sheet_url": ""
    }
  ],
  "outfits": [
    {
      "id": "denise_navy_blazer",
      "character_id": "denise",
      "description": "Tailored navy wool blazer over crisp ivory silk blouse, slim wristwatch",
      "scenes": ["scene_01"],
      "sheet_url": ""
    },
    {
      "id": "bola_apron",
      "character_id": "bola",
      "description": "Neat muted grey cotton dress with clean dark linen house apron",
      "scenes": ["scene_01"],
      "sheet_url": ""
    }
  ],
  "environments": [
    {
      "id": "study_night",
      "name": "Executive Study at Night",
      "time_of_day": "night",
      "lighting_lock": "Warm brass desk lamp key light against deep cool moonlight through rain-streaked curtains",
      "description": "Dark walnut executive study, leather desk blotter, tall bookshelves, heavy drapery"
    }
  ],
  "props": [
    {
      "id": "deed_envelope",
      "name": "Wax-Sealed Cream Deed Envelope",
      "description": "Thick cream legal envelope with a cracked burgundy wax seal and visible notary stamp",
      "scenes": ["scene_01"]
    }
  ]
}
```

---

## 3. `beats.json` (`2×2` Four-Panel · `10s` Beats)
- **`duration`:** strictly `10` seconds per beat (`6` beats = `60s`, `30` beats = `5m`, `720` beats = `2h`).
- **`cuts`:** strictly **4 cuts** (`panel` `1..4`, `position` = `top-left` | `top-right` | `bottom-left` | `bottom-right`).
- **`shot_type`:** `Medium Wide` | `Over-the-Shoulder` | `Medium Close-Up` | `Close-Up`.
- **`audio_mode`:** `on_camera` | `silent_reaction` | `offscreen_l_cut` *(face-free prop/env ONLY)* | `offscreen_j_cut` *(face-free prop/env ONLY)*.

```json
{
  "beats": [
    {
      "beat_id": "beat_001",
      "episode": 1,
      "scene_id": "scene_01",
      "environment_id": "study_night",
      "time_of_day": "night",
      "active_character_ids": ["denise", "bola"],
      "character_outfits": {
        "denise": "denise_navy_blazer",
        "bola": "bola_apron"
      },
      "active_prop_ids": ["deed_envelope"],
      "duration": 10,
      "storyboard_grid_url": "",
      "cuts": [
        {
          "panel": 1,
          "position": "top-left",
          "time_range": "0.0s-2.5s",
          "shot_type": "Medium Wide",
          "dramatic_function": "hook",
          "action": "Bola steps timidly inside the dimly lit study doorway in 3/4 profile facing right, head slightly bowed, holding the cream envelope toward Denise seated at the desk.",
          "audio_mode": "on_camera",
          "speaker_id": "bola",
          "speech_text": "Ma'am... this arrived from the bank just now.",
          "delivery": "quiet hesitant respectful voice, soft apologetic cadence, humble deferential tone",
          "micro_expression": "Bola keeps eyes respectfully lowered toward the envelope; Denise stays silent with lips closed",
          "sfx": "Soft footsteps on hardwood, rain tapping glass"
        },
        {
          "panel": 2,
          "position": "top-right",
          "time_range": "2.5s-5.0s",
          "shot_type": "Close-Up",
          "dramatic_function": "status_trap",
          "action": "Tight close-up on the wax-sealed cream deed envelope sliding onto the leather desk blotter under warm lamp light (no faces visible).",
          "audio_mode": "offscreen_l_cut",
          "speaker_id": "bola",
          "speech_text": "The courier said... Mr. Marcus must not see it.",
          "delivery": "hushed trembling deferential whisper, cautious quiet cadence",
          "micro_expression": "Bola's fingers tremble slightly releasing the paper corner",
          "sfx": "Crisp paper sliding on leather"
        },
        {
          "panel": 3,
          "position": "bottom-left",
          "time_range": "5.0s-7.5s",
          "shot_type": "Medium Close-Up",
          "dramatic_function": "escalation",
          "action": "3/4 profile of Denise angled left looking up from the envelope toward Bola, fingers resting firmly on the broken wax seal.",
          "audio_mode": "on_camera",
          "speaker_id": "denise",
          "speech_text": "Lock the front gate. Say nothing to anyone.",
          "delivery": "low calm controlled voice, steady deliberate cadence, quiet steel authority",
          "micro_expression": "Eyes narrow with cold clarity, subtle poised nod",
          "sfx": "Low room tone, distant muffled thunder"
        },
        {
          "panel": 4,
          "position": "bottom-right",
          "time_range": "7.5s-10.0s",
          "shot_type": "Close-Up",
          "dramatic_function": "cliffhanger",
          "action": "3/4 profile close-up of Bola nodding submissively with eyes downcast toward the floor before turning toward the hallway.",
          "audio_mode": "silent_reaction",
          "speaker_id": "",
          "speech_text": "",
          "delivery": "",
          "micro_expression": "Lips firmly closed and sealed tight, worried shallow exhale, eyes glistening nervously",
          "sfx": "Heavy study door latch clicking softly"
        }
      ]
    }
  ]
}
```
