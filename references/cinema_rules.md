# Epic Cinema — DramaBox Story Arc, Lip-Sync, Eyeline & Vocal Prosody Bible

Follow every rule below when writing scripts (`beats.json`) and compiling image/video prompts so every clip looks and sounds like live-action cinema rather than generic AI video.

---

## 1. DramaBox-Tier Story Arc Architecture
- **In Media Res Visual Hook (Beat 1, Cuts 1–2):** Open inside active conflict—mid-confrontation, mid-betrayal, or mid-discovery—legible even with sound muted in the first 3 seconds. Never waste Beat 1 on slow setup or travel.
- **"BUT / THEREFORE" Causal Chain:** Never link beats with flat *"and then"* sequencing. Every beat escalates pressure or flips power.
- **4-Phase Micro-Drama Arc (per Episode or Short Film):**
  1. **Status Trap / Confrontation:** Antagonist asserts power or corners the protagonist; a recurring prop anchors the stakes.
  2. **Hidden Pressure:** Protagonist absorbs or deflects while a clue hints at hidden leverage or danger.
  3. **The Turn (Power Shift):** A sudden arrival, leaked message, document, or prop reveal flips control mid-scene.
  4. **Cliffhanger End (Final Panel 4 of Final Beat):** Cut abruptly on an interrupted reveal (*"Wait, that signature belongs to—"*), overheard truth, mid-action decision, or shock arrival.

---

## 2. Visible-Speaker Lip-Sync Architecture (Anti-Wrong-Speaker Lock)
Grok's inbuilt video generator (and Seedance / MiniMax / Kling / Wan) synthesizes audio and visual lip movements simultaneously in one pass. It naturally maps **any quoted speech in a cut onto whichever face is visible on screen**.

1. **On-Camera Speaker Only (`on_camera`):** Whenever a character speaks, that exact speaking character MUST be visibly on camera (`Medium Close-Up`, `Close-Up`, `Over-the-Shoulder` facing the speaker, or `Medium Wide`). Keep spoken lines concise (**5–10 words** per `2.5s` cut) so speech finishes cleanly before the cut.
2. **Two-Shot / OTS Isolation:** When two characters share a frame during an `on_camera` line, explicitly state which character speaks AND explicitly lock the other character silent: *"mouth firmly closed, lips sealed tight, completely silent."*
3. **Silent Listener Reactions (`silent_reaction`):** NEVER put off-screen dialogue over a listener's face! Set `audio_mode: "silent_reaction"`, `speaker_id: ""`, `speech_text: ""`, and write physical closed-mouth cues (*lips sealed tight, jaw clenched, eyes narrowing, subtle sharp exhale*).
4. **Face-Free Off-Screen Voiceover Only (`offscreen_l_cut` / `offscreen_j_cut`):** Allowed **strictly** on panels showing NO human face (tight `Close-Up` on a contract, ring, phone screen, teacup, or empty doorway).

---

## 3. Fourth-Wall & Eyeline Lock (Zero Awkward Camera-Staring)
Grok Video exhibits a "lurk-to-camera" drift near the end of clips if characters look into empty space or start in a frontal portrait. Negative prompts alone (*"don't look at the camera"*) fail because models latch onto the word "camera."

**3-Layer Fix:**
1. **Storyboard Pre-Control (`2×2` Grid):** Compose every character panel in **3/4 view, side profile, or over-the-shoulder geometry** — never a straight-on vlog/mugshot portrait.
2. **Front-Load Within First 20 Words:** Grok weights the opening 20 words heaviest. Always open the video prompt with candid narrative film framing and off-lens eyeline lock.
3. **Concrete Physical Gaze Target on Every Cut:** Always pair head orientation + exact target in `cut.action` and `micro_expression`:
   - *Good:* `"3/4 profile angled right, eyes locked intently on Marcus across the mahogany desk"`
   - *Good:* `"Head tilted down in side profile, gaze fixed on the folded bank statement in her trembling hands"`
   - *Bad:* `"Standing in the room looking sad"` *(Grok will snap eyes straight into the lens)*

---

## 4. Vocal Mood, Prosody & Social-Status Lock
Native-audio video generators default to bright, upbeat, or flat delivery when given vague one-word emotion tags like `"sad"` or `"nervous"`.

**Always combine 3 signals on every spoken cut:**
1. **Character Voice Baseline (`bible.characters[].voice`):** Timbre, accent, pitch, and register (e.g., *"soft humble low-volume alto"*, *"deep gravelly baritone"*).
2. **Acoustic Delivery Tag (`cut.delivery`) placed right before the quoted line:** Pitch + pace/cadence + vocal texture + social posture.
3. **Matching Physical Action + Expressive Punctuation + No-Music Boundary:**
   - Use ellipses (`...`) for grief/hesitation and dashes (`—`) for sharp interruptions.
   - Always close the video prompt with: `AUDIO BOUNDARY: Realistic grounded cinematic dialogue and subtle ambient foley only; no intrusive background music.`

### Ready-to-Use Vocal Delivery Cheat Sheet

| Scene Mood / Social Status | `delivery` Tag | Matching Physical Action (`cut.action`) |
| :--- | :--- | :--- |
| **Sad / Grieving / Broken** | `soft trembling whisper, slow halting cadence, tearful breathy voice, defeated sorrowful tone` | Lowered gaze, quivering lower lip, shoulders slumped inward |
| **Servant / Subordinate / Deferential** | `quiet hesitant respectful voice, soft apologetic cadence, humble deferential tone` | Head slightly bowed, hands folded neatly, eyes downcast respectfully |
| **Cold Boss / Threatening** | `low resonant baritone, slow measured condescending cadence, icy deadpan authority` | Still upright posture, narrow unblinking stare across desk |
| **Panicked / Pleading** | `breathless shaky higher pitch, urgent rushed cadence, desperate trembling voice` | Rapid shallow breathing, leaning forward tensely, gripping sleeve/table edge |
| **Sarcastic / Dismissive** | `dry flat cadence, condescending inflection, sharp mocking drop at end` | Slight side smirk, glancing sideways without raising voice |
| **Conspiratorial / Secret** | `sub-vocal raspy whisper, deliberate hushed pace, tense secretive tone` | Leaning close in 3/4 profile, eyes flicking toward doorway |

---

## 5. Strict 4-Angle Camera Selection
- **`Medium Wide`:** Spatial power dynamics, entrances, posture, and environment/time-of-day grounding.
- **`Over-the-Shoulder`:** Verbal sparring, intimidation, and guaranteed natural eyelines (only the face-visible character speaks).
- **`Medium Close-Up`:** Primary clean on-camera dialogue delivery where expression + posture read together.
- **`Close-Up`:** Raw emotion, whispered lines, **silent closed-mouth listener reactions**, and **face-free decisive props**.
