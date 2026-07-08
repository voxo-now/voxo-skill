# VOXO — agent integration kit

Everything an AI agent needs to use **[VOXO](https://voxo.now)** — text-to-speech, voice
cloning, multi-speaker dialogue, and transcription across 100+ languages — through one API key.

This repo is intentionally **not** a bespoke agent. It ships portable, standard artifacts so
**any** agent (Claude, ChatGPT/Codex, Cursor, or your own) can drive VOXO:

| File | For |
|---|---|
| [`skills/voxo/`](skills/voxo/) | An **Agent Skill** ([open standard](https://agentskills.io)) — `SKILL.md` + deterministic `scripts/` + `references/`. Works in Claude Code, the Claude API, and any skill-aware runtime. |
| [`AGENTS.md`](AGENTS.md) | Standing project instructions for the **AGENTS.md** ecosystem (OpenAI/Codex, Cursor, …). |
| [`server.json`](server.json) | MCP Registry manifest describing the hosted **MCP** endpoint. |

## Quick start

1. Get an API key: VOXO dashboard → **API & MCP**.
2. `export VOXO_API_KEY="amk_live_…"`
3. Use it one of these ways:

**As an MCP server** (agents — Claude Code shown):
```bash
claude mcp add voxo --transport http https://mcp.voxo.now/mcp/ \
  --header "Authorization: Bearer $VOXO_API_KEY"
```

**As an Agent Skill** (Claude Code): copy `skills/voxo` into `~/.claude/skills/` (or your
project's `.claude/skills/`). Claude loads it automatically when a task matches.

**As scripts** (no MCP, no skill — just Python 3, stdlib only):
```bash
python3 skills/voxo/scripts/tts.py "Hello from VOXO." --language en --out hello.wav
python3 skills/voxo/scripts/transcribe.py recording.mp3
python3 skills/voxo/scripts/clone_and_speak.py sample.wav "Read this in my voice." --name "Me"
```

## What's inside the skill

- **`SKILL.md`** — the workflows (generate → poll → download, cloning, dialogue, STT), the rules
  that matter (async jobs, credits, clone-wait), and delivery controls.
- **`references/`** — `voices.md` (presets + cloning), `controls.md` (21 emotions, prosody,
  styles, inline SFX), `languages.md` (the 102 codes).
- **`scripts/`** — self-contained, dependency-free helpers for the fragile multi-step loops.

## Links

- Docs: https://voxo.now/docs · API base: `https://api.voxo.now` · MCP: `https://mcp.voxo.now/mcp/`

## License

Apache-2.0 — see [LICENSE](LICENSE).
