# AGENTS.md — VOXO

Guidance for AI agents (OpenAI/Codex, Cursor, and any AGENTS.md-aware tool) working with
**VOXO** — text-to-speech, voice cloning, multi-speaker dialogue, and transcription across
100+ languages, via one API key.

## Connect

- **MCP (preferred):** streamable-http endpoint `https://speech-mcp.mvpro.lt/mcp/` with header
  `Authorization: Bearer $VOXO_API_KEY`. Exposes all VOXO tools (`create_generation_job`,
  `list_voices`, `transcribe_audio`, `clone_voice`, …).
- **REST:** base `https://speech-api.mvpro.lt`, same `Authorization: Bearer` header. The bundled
  scripts in `skills/voxo/scripts/` (`tts.py`, `clone_and_speak.py`, `transcribe.py`) wrap it and
  need only Python 3 (stdlib).

Get a key from the VOXO dashboard → **Developers**. Set `export VOXO_API_KEY="amk_live_…"`.

## Rules that matter

- **Generation is asynchronous.** Create a job → **poll** `GET /v1/generations/{id}` until
  `status` is `succeeded` (or `failed`/`cancelled`) → download `outputs[0].download_url`.
  Never assume audio is ready from the create response.
- **Send an `Idempotency-Key`** (a fresh UUID) when creating a job so retries don't double-charge.
- **Credits** are reserved on create, captured on success; the user must have a **verified email**.
- **Cloned voices** return `status: "processing"` and must reach `enabled` before use.
- **Limits:** ≤ 5000 chars per TTS job, ≤ 40 dialogue turns, ≤ 5 active jobs.

## Delivery controls (optional)

- Whole-line: `emotion` (21 values, e.g. `enthusiasm`), `style` (`singing|shouting|whispering`),
  `prosody` (comma-separated, e.g. `speed_fast,pitch_high`).
- Inline in the text: sounds `<|sfx:laughter|>` / pauses `<|prosody:pause|>`.

## Deeper guidance

The full workflows, control catalog, voice list, and language codes live in the Agent Skill at
[`skills/voxo/SKILL.md`](skills/voxo/SKILL.md) and its `references/`. Docs: https://voxo.now/docs
