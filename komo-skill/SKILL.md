# komo-skill — Komo Babies Episode Production

The proven end-to-end process for producing a Komo Babies episode: a 3D animated
preschool kids' show (YouTube / YouTube Kids), built exactly the way Episode 1
("What's Inside the Giant Mystery Box?") was produced and approved on 2026-11-26.

Cast: **Komo** (yellow hoodie, blue star), **Mimi** (pink heart t-shirt, purple
skirt, twin puffs), **Kiki** (orange t-shirt, teal shorts, green backwards cap),
**Reki** (rainbow hoodie), **Bobo** (cream lop-eared bunny, blue bow tie).
Settings: pastel indoor playroom, outdoor playground (from the environment sheets).

## Locked rules (the owner's — never break these)

1. **Exactly 5:00 per episode** — 30 beats × 10 seconds = 300s. Nothing less.
2. **One song per episode.** Each script has TWO music sections; combine them
   into a SINGLE lyrics/prompt so one generated song covers both sections.
   This is the standard pattern for all episodes.
3. **Transcripts are a production guide only — NEVER captions.** No transcript
   text is burned into or overlaid on any video. Transcripts steer who
   speaks/sings, what is said, and when, so lip-sync and actions land on the
   right words.
4. **Reference rule:** the character sheets for every character AND the
   environment sheet MUST be attached as references for every storyboard image.
5. **Cast-on-screen rule:** the screen never looks empty. Most frames show ALL
   FIVE characters together; sometimes three; a solo emphasis shot only for one
   or two consecutive beats, then back to the group.
6. **Storyboard = individual images**, one per beat — NOT multi-panel grids.
   Each image becomes one video.
7. **Images are made in Google Flow** (project per episode, e.g. "Komo Babies -
   Episode 1"); **videos are animated with the built-in generator**, not Flow video.
8. **Songs must have a beat behind them** — instant beat drop, zero slow intro.
9. Toddler/baby voices only in songs: cute toddler lead + young children's
   choir. Adult/mature voices are excluded via negative tags.

## Phase 1 — The song (Suno via KIE AI)

- Take the episode's two music sections from the script doc and merge their
  lyrics into ONE lyrics block, in episode order, **word-for-word verbatim**,
  keeping the square-bracket section tags ([Chorus], [Verse 1: Red Door], …).
  The natural join is where section 1 ends and section 2 begins.
- **Extend it:** one plain generation runs ~2:10 — too short for a 5-minute
  episode. Repeat the choruses and add instrumental breaks (intro, dance
  breaks between verses, celebration break, outro) where the characters keep
  acting/dancing on screen. An extended build lands ~3:40–3:50; the acting
  (interplay) sections fill the rest of the 5:00. Suno generations cap around
  ~4 minutes — do not promise a full 5:00 of song.
- Style prompt pattern (proven): "Happy cheerful preschool nursery rhyme pop
  song, G major, 122 BPM, bouncy marimba, punchy upright piano, playful
  woodblocks, bright handclaps, tuba bass bounce, bouncy brass hits, cheerful
  ukulele, cute toddler lead vocal with joyful young children's choir
  call-and-response, long instrumental dance breaks between sections, repeated
  choruses, playful sound-effect pauses. Zero slow intro, instant beat drop."
- Negative tags: EDM, trap, heavy rock, distorted guitars, aggressive drums,
  robotic vocals, heavy autotune, vocal fry, raspy vocals, adult male voice,
  adult female voice, mature voice, grown-up vocals, slow intro, abrupt cutoff.
- **NEVER put artist/brand names (e.g. "CoComelon") in the style prompt or
  tags — Suno rejects them.** Describe the sound instead.
- Generate via KIE AI (`api.kie.ai`, Suno model V5, customMode). The API key
  is supplied by the owner per session and used **transiently only — read it
  from stdin in the submit script, never write it to any file, never store it.**
- KIE/Suno ALWAYS returns **two versions** per generation. Download both,
  deliver both, let the owner choose.

## Phase 2 — Split and VERIFY the audio (do not skip)

- Split the chosen extended track at its **natural join** (the breath/pause
  right before section 2's opening chorus) into Part A and Part B, with a
  small fade on each side of the cut. The two parts must rejoin seamlessly —
  they came from one track. Part A plays, the characters act the in-between
  section, then Part B starts cleanly on its own first beat.
- **Transcribe the actual generated audio with timestamps** (faster-whisper)
  and correct the plan against the REAL singing. Never trust the written
  lyrics for timing: Suno stretches/compresses sections, drops planned
  instrumental breaks, and may add lines (Ep 1 gained a spoken "Thank you for
  watching!" in the outro — kept, it lands on the bye-bye beat). Whisper
  garbles toddler voices ("Shake" → "Shade"); the sung words are still the
  written lyrics — use the transcript for TIMINGS, the script for WORDS.
- Record the verified section boundaries (in episode time) in the plan doc;
  they supersede any estimates.

## Phase 3 — The 5:00 plan

Write a per-episode plan doc: 30 beats × 10s. Audio layout pattern:

| Block | Content |
|---|---|
| Interplay A (acting, no song) | Cold open + hook + first story act |
| Song Part A | First music section (incl. its instrumental breaks) |
| Interplay B (acting, no song) | Mid-episode pattern interrupt / comedy reset |
| Song Part B | Second music section through the finale + outro |

Block lengths come from the verified audio: interplay total = 300s − (Part A +
Part B). Every beat gets: time range, its **transcript** (exact dialogue or
lyric lines heard in those 10s, from the verified timings), the visual/action,
and its audio source (Part A/B timecode or "acting — no song"). Interactive
pauses (shout-alongs, count-to-three) sit inside their beats as held moments.

## Phase 4 — Storyboard images (Google Flow)

- One image per beat, 16:9, in the episode's Flow project.
- **Reuse-prompt method (owner's workflow):** hover the upper-right corner of
  an existing generation that already has all reference inputs attached, click
  the 3 dots, choose **"Reuse prompt"** — this loads the prompt AND all six
  reference sheets (4 characters + Bobo + environment). Remove any input image
  that is not necessary, edit the prompt text for the beat, submit.
- **Continuous input:** queue ALL prompts back to back — do NOT wait for one
  image to finish before sending the next.
- **PITFALL:** Flow's prompt field may APPEND instead of replacing, leaking
  fragments of earlier prompts into the next image (Ep 1 beats 7–10 were
  contaminated this way). Clear the field fully (Ctrl+A + Backspace) before
  typing each new prompt, and check each finished image in full view; regenerate
  contaminated ones cleanly and do not download the superseded versions.
- No text, captions or words anywhere in the images. Check every image:
  characters on-model, defining action/prop present, cast rule obeyed.
- Still images cost 0 Flow credits; downloads come at 1K (2K upscale may fail
  on Flow's side — accept 1K).

## Phase 5 — Animation (built-in generator)

- Animate each beat's image into a 10s 16:9 video with the built-in generator,
  in parallel batches. The prompt for each beat is built from its transcript:
  who speaks/sings, the exact lines with clear toddler-voice lip-sync, the
  actions landing on the words (knock on "knock", freeze on "FREEZE"), and
  "keep every character exactly as drawn; no text, no captions, no subtitles".
- Instrumental-break beats: prompt "no singing, nobody speaks" + the dance/
  acting the break carries.
- **Verify every video frame-by-frame** (extract frames at ~2s and ~8.5s plus
  a mid frame). Known generator flaw: it can briefly DUPLICATE a character
  (an extra pink-clad girl, a second bunny) for a few frames — flag it
  honestly to the owner; redo only on the owner's say-so.

## Phase 6 — Real-audio finish and stitch

- For every SONG beat, replace the generator's own audio with the exact slice
  of the real song: episode time − block offset = audio time in Part A/Part B
  (ffmpeg: cut the slice, mux over the beat's video, stream-copy video).
- Interplay beats keep their generated dialogue audio.
- Concatenate all 30 finished beats in story order (ffmpeg concat). Verify
  the final file: duration 300s (±1s), 1216×672 (16:9), video+audio streams
  present. Deliver the episode file itself in chat.

## File layout (per episode)

```
~/workspace/komo-babies/
  scripts/            # script docs (source of lyrics + dialogue)
  music/              # submit_*.py (key from stdin), song mp3s, splits, transcript
  production/
    episode-N-full-5min-plan.md   # the 30-beat plan with transcripts + verified timings
    epN-beats/        # beat_NN.jpg + beat_NN.mp4 per beat, previews, final episode file
```

## Worked example

Episode 1, produced 2026-11-26 — see `references/episode-1-example.md` for the
verified timings, block layout and lessons that this skill generalises.
