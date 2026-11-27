# Worked example — Episode 1: "What's Inside the Giant Mystery Box?"

Produced and approved 2026-11-26. This is the reference run komo-skill generalises.

## Audio layout (verified against the real song)

| Block | Episode time | Length | Source |
|---|---|---|---|
| Interplay A — acting | 0:00–0:35 | 35s | Cold open ("WHOA! Did you hear that?!"), "Shout YES!" hook, three doors, red-door knock |
| Song Part A | 0:35–2:23 | 108s | `ep1-extended-v2-partA-mystery-box.mp3` |
| Interplay B — acting | 2:23–3:00 | 37s | Bobo's Silly Mix-Up: record scratch, "MOO! QUACK! BEEP-BEEP!", count to three, Bobo's "TA-DAA!" |
| Song Part B | 3:00–5:00 | 120s | `ep1-extended-v2-partB-animal-party.mp3` (0.8s tail trimmed) |

## Verified song timings (episode time, from transcribing the real audio)

Part A: intro instrumental 0:35–0:44.5 · Chorus 0:44.5–1:00 · Chorus repeat
1:00–1:15.3 · Verse 1 Puppy 1:15.6–1:30.4 · dance break 1:30.4–1:38.4 ·
Verse 2 Duck 1:38.4–1:53.3 · Chorus (Peek-a-boo) 1:53.6–2:08.4 · Chorus repeat
louder 2:08.4–2:23.7. Split point confirmed: "Pop goes the box!" begins at
audio 1:49.3.

Part B ("Pop" lands at 3:01.3 — the Part B file has a 1.3s instrumental
lead-in): Pop chorus 3:01.3–3:14.6 · repeat 3:15–3:29.6 · Verse 3 Elephant
3:29.6–3:44.8 · Bridge 3:45.1–3:59.1 · Bridge repeat 3:59.1–4:13.7 · Final
Chorus 4:14.3–4:28.4 · Final Chorus repeat 4:28.9–4:44.2 · outro instrumental
4:44.2–4:56.3 · spoken "Thank you for watching!" 4:56.3–4:59.4.

## Lessons baked into the skill

- Estimated timings were wrong by up to ~10s per section (puppy verse half a
  beat late; final chorus over a beat early) — always transcribe the real audio.
- The planned duck and elephant dance breaks did NOT exist in the generated
  song; only the intro, post-puppy break and outro breaks materialised.
- Flow prompt field appended text instead of replacing it on beats 7–10;
  fixed by clearing fully (Ctrl+A + Backspace) and regenerating.
- The built-in video generator briefly duplicated Mimi in beat 5 and added an
  extra girl/second bunny in the earlier intro test — frame-check everything.
- Suno rejected the first song attempt because the style prompt contained the
  brand name "CoComelon" — describe sounds, never name brands/artists.
- Final deliverable: `production/episode-1-final.mp4` — 30 beats, exactly
  5:00, real song audio over all song beats.
