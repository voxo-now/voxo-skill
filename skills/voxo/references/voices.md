# Voices

Three ways to pick a voice for a TTS job:

## 1. Preset voices (system, public — no setup)

Always resolve the **`voice_id`** at call time with `VOXO:list_voices` (or `GET /v1/voices`) —
IDs are stable but listing is authoritative. The presets (slug · language · gender):

| Name | Slug | Lang | Gender | Feel |
|---|---|---|---|---|
| Ava | `ava` | en | female | calm |
| Nova | `nova` | en | female | bright |
| Marek | `marek` | pl | male | calm |
| Ola | `ola` | pl | female | bright |
| Lena | `lena` | de | female | calm |
| Mila | `mila` | de | female | bright |
| Sofía | `sofia` | es | female | calm |
| Lucía | `lucia` | es | female | bright |
| Louis | `louis` | fr | male | calm |
| Hugo | `hugo` | fr | male | bright |

A preset works for **any** of the 102 languages, not only its native one — the language is set
by the job's `language` field. Native-language presets just sound most natural.

## 2. Zero-shot (no voice)

Omit `voice_id` entirely for a fresh synthetic voice. Pass a `seed` (any integer ≥ 0) to make
that voice **reproducible** across calls; omit or `-1` for random each time.

## 3. Cloned voices (your own)

Create from a clean **10–30 s** mono clip (see the "Clone a voice" workflow in SKILL.md). Cloned
voices are **private to the account** and come back `status: "processing"` until auto-transcription
finishes — wait for `enabled` before using. Manage with `VOXO:list_voices`, `VOXO:get_voice`,
`VOXO:get_voice_sample`, `VOXO:delete_voice`.

## Referencing a voice in a job

- Preset or cloned: pass `voice_id="voi_…"`.
- One-off clone without saving a voice: pass `reference_audio_asset_id` (+ optional
  `reference_text`) instead of `voice_id`.
