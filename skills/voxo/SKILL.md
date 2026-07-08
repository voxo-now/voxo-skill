---
name: voxo
description: Generate speech (text-to-speech), clone a voice, build multi-speaker dialogues, and transcribe audio with VOXO. Use whenever the user wants to turn text into natural voiceover, narrate a script or article, create or clone an AI voice, produce audio in another language, dub a character, or transcribe/subtitle an audio file — via the VOXO MCP tools or its REST API. Trigger on "voiceover", "text to speech", "TTS", "read this aloud", "narration", "clone my voice", "AI voice", "dialogue audio", "transcribe", "subtitles".
license: Apache-2.0
compatibility: Needs network access to the VOXO API and a VOXO_API_KEY. Bundled scripts use Python 3 standard library only (no pip installs).
metadata:
  author: VOXO
  version: "1.0"
  homepage: https://voxo.now
---

# VOXO — speech for agents

VOXO turns text into natural speech (100+ languages), clones voices from a short clip,
builds multi-speaker dialogues, and transcribes audio. Everything runs through **one API
key** and a **credit** balance. There are two equivalent ways to call it — use whichever
is available:

- **MCP tools** (preferred when a VOXO MCP server is connected). Tool names below are shown
  fully-qualified as `VOXO:tool_name`.
- **REST via the bundled scripts** in `scripts/` (no MCP needed — just `python3` + a key).

## Setup

Set the API key once in the environment (both paths read it):

```bash
export VOXO_API_KEY="amk_live_…"          # from the VOXO dashboard → Developers
export VOXO_API_URL="https://speech-api.mvpro.lt"   # optional; this is the default
```

MCP endpoint (streamable-http): `https://speech-mcp.mvpro.lt/mcp/` with header
`Authorization: Bearer $VOXO_API_KEY`.

## Rules that will save you (read first)

- **Generation is async.** You **create a job**, then **poll** it until `status` is
  `succeeded` (or `failed`/`cancelled`). Never assume audio is ready from the create call.
  MCP: `VOXO:wait_for_generation_job` blocks for you. Scripts poll for you.
- **Credits are reserved on create, captured on success.** Call `VOXO:estimate_generation`
  before large jobs. A user must have **verified their email** before generating.
- **Fresh clones aren't instant.** A cloned voice comes back `status: "processing"` while it
  auto-transcribes; **wait for `enabled`** (`VOXO:wait_for_voice`) before generating with it.
- **Limits:** ≤ 5000 chars per TTS job, ≤ 40 dialogue turns, ≤ 5 active jobs at once.
- **Idempotency:** creating a job takes an `Idempotency-Key` — the scripts send one; if you
  call REST directly, send a fresh UUID so retries don't double-charge.

## Workflow 1 — Text to speech (single voice)

1. Pick a voice (see `references/voices.md`): a **preset** (`voice_id`), a **cloned** voice,
   or **zero-shot** (omit voice, optionally pin a `seed`).
2. Optionally add delivery controls (see `references/controls.md`).
3. Generate and wait:
   - **MCP:** `VOXO:create_generation_job(text, voice_id, language, emotion?, style?, prosody?)`
     → then `VOXO:wait_for_generation_job(job_id)` → `VOXO:download_output(job_id)`.
   - **Script:** `python3 scripts/tts.py "Your text here" --voice voi_… --language en --out out.wav`

Example (MCP): `VOXO:create_generation_job(text="Welcome to the show.", voice_id="voi_…", language="en", emotion="enthusiasm")`.

## Workflow 2 — Clone a voice, then speak

1. Get a **clean 10–30 s** mono clip of the target voice (one speaker, no music).
2. Create the voice (transcript optional — VOXO transcribes with Whisper if omitted):
   - **MCP:** `VOXO:clone_voice(display_name, data_base64, language, consent="confirmed")`.
   - **Script:** `python3 scripts/clone_and_speak.py sample.wav "Read this in my voice." --name "My Voice" --language en --out out.wav`
3. **Wait for `enabled`** (`VOXO:wait_for_voice`), then generate as in Workflow 1 with the new `voice_id`.

`consent` **must** be `"confirmed"` — you attest you have the right to clone this voice.

## Workflow 3 — Multi-speaker dialogue

One audio file, speakers alternating. Each turn has its own voice + delivery.

- **MCP:** `VOXO:create_dialogue_job(turns=[{voice_id, text, emotion?}, …], language="en")` → wait → download.
- Turns list is `[{"voice_id":"voi_A","text":"Hi!"}, {"voice_id":"voi_B","text":"Hello."}]`.
  Inline `<|sfx:…|>` / `<|prosody:pause|>` work inside a turn's text too.

## Workflow 4 — Transcription (speech to text)

- **MCP:** upload with `VOXO:upload_audio` (or `VOXO:transcribe_file` does upload+transcribe+wait
  in one call). `language` empty = auto-detect. Returns transcript + timestamped segments.
- **Script:** `python3 scripts/transcribe.py recording.mp3 --language en`

## Delivery controls (brief — full catalog in references/controls.md)

Two independent layers:
- **Whole-line mood** (applied at the start, passed as parameters, *not* embedded in text):
  `emotion` (e.g. `elation`, `contentment`), `style` (`singing`|`shouting`|`whispering`),
  `prosody` (comma-separated, e.g. `speed_fast,pitch_high`).
- **Inline effects** (dropped exactly where you want them, embedded in the text):
  sounds `<|sfx:laughter|>` `<|sfx:sigh|>` …, pauses `<|prosody:pause|>` `<|prosody:long_pause|>`.
  Example text: `"Great news <|sfx:laughter|> we shipped it. <|prosody:pause|> Finally."`

## Voices & languages

- **Presets:** Ava/Nova (en), Marek/Ola (pl), Lena/Mila (de), Sofía/Lucía (es), Louis/Hugo (fr).
  List live voices with `VOXO:list_voices` (or `GET /v1/voices`). Details in `references/voices.md`.
- **Languages:** 102 supported; set the `language` code (e.g. `en`, `es`, `de`, `fr`, `lt`, `ja`).
  Full list + names in `references/languages.md`.

## When something fails

- `402`/insufficient credits → tell the user to top up. `403` email-unverified → verify first.
- Job `status: "failed"` → read `error`; usually text too long (>5000) or a bad control token.
- Voice stuck `processing` → the reference clip was too short/noisy; try a cleaner 10–30 s clip.
- Prefer `VOXO:estimate_generation` before anything large to show the user the cost.
