# Delivery controls

Two independent layers. **Whole-line** controls are passed as parameters (they colour the whole
utterance). **Inline** tokens are embedded in the text exactly where you want the effect.

## Whole-line controls (parameters, not in the text)

### `emotion` — one value per job (21)
`affection`, `amusement`, `anger`, `arousal`, `awe`, `bitterness`, `confusion`, `contemplation`,
`contentment`, `determination`, `disgust`, `elation`, `enthusiasm`, `fear`, `helplessness`,
`longing`, `pride`, `relief`, `sadness`, `shame`, `surprise`.

### `style` — one value per job (3)
`singing`, `shouting`, `whispering`.

### `prosody` — comma-separated, combine freely (10)
Speed: `speed_very_slow`, `speed_slow`, `speed_fast`, `speed_very_fast`.
Pitch: `pitch_low`, `pitch_high`. Expressiveness: `expressive_high`, `expressive_low`.
Pauses (as prosody): `pause`, `long_pause`.
Example: `prosody="speed_fast,pitch_high"`.

## Inline tokens (embedded in the text)

### Sound effects `<|sfx:NAME|>` (9)
`<|sfx:cough|>`, `<|sfx:laughter|>`, `<|sfx:crying|>`, `<|sfx:screaming|>`, `<|sfx:burping|>`,
`<|sfx:humming|>`, `<|sfx:sigh|>`, `<|sfx:sniff|>`, `<|sfx:sneeze|>`.

### Pauses
`<|prosody:pause|>` (short) and `<|prosody:long_pause|>` (long).

## Putting it together

```
create_generation_job(
  text="Great news <|sfx:laughter|> we shipped it. <|prosody:pause|> Finally.",
  voice_id="voi_…", language="en",
  emotion="elation", prosody="speed_fast",
)
```

Notes:
- Emotion/style/prosody are applied at the **start** of the line — you don't embed them in the text.
- Use inline `<|sfx:…|>` / `<|prosody:pause|>` for effects at a **specific point**.
- The live catalog is always available via `VOXO:get_capabilities` → `control_tokens`.
