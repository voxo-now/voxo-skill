# Languages

VOXO supports **102 languages**. Set the two/three-letter code in the job's `language` field
(e.g. `language="es"`). The authoritative code→name map is in `VOXO:get_capabilities`
(`languages`, `language_names`, and `language_tier2`).

## Common codes

| Code | Language | Code | Language | Code | Language |
|---|---|---|---|---|---|
| `en` | English | `es` | Spanish | `fr` | French |
| `de` | German | `it` | Italian | `pt` | Portuguese |
| `ru` | Russian | `uk` | Ukrainian | `pl` | Polish |
| `nl` | Dutch | `zh` | Chinese | `ja` | Japanese |
| `ko` | Korean | `ar` | Arabic | `hi` | Hindi |
| `tr` | Turkish | `lt` | Lithuanian | `sv` | Swedish |
| `da` | Danish | `no` | Norwegian | `fi` | Finnish |
| `cs` | Czech | `el` | Greek | `he` | Hebrew |
| `id` | Indonesian | `vi` | Vietnamese | `th` | Thai |
| `ro` | Romanian | `hu` | Hungarian | `fa` | Persian |

## Full code list (102)

```
lt en es fr de it pt ru uk pl nl zh ja ko ar hi tr af sq hy as ast az ba eu be bn bs bg ca
ceb ckb ny hr cs da mhr pa eo et fi gl lg ka el gu ht ha he hu is id ga jv kea kab kam kn kk
rw ky la lv ln luo lb mk ms ml mt mr mn mi ne no oc om ps fa ro nso sr sn sd sk sl so sw sv
tl tg ta te th umb ur ug uz vi cy xh zu
```

Notes:
- A voice from one language can speak any of these — the `language` field drives it.
- Quality is strongest on the tier-1 languages (the common table above); tier-2 codes still work.
- Auto-detect (for **transcription** only): pass an empty `language` and VOXO detects it.
