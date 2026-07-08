#!/usr/bin/env python3
"""VOXO transcription (STT): upload an audio file, transcribe, print transcript + segments.
Stdlib only. Empty --language = auto-detect.

  export VOXO_API_KEY=amk_live_...
  python3 transcribe.py recording.mp3 --language en
  python3 transcribe.py interview.wav            # auto-detect language
"""
import os, sys, json, time, uuid, base64, argparse, urllib.request, urllib.error

API = os.environ.get("VOXO_API_URL", "https://speech-api.mvpro.lt").rstrip("/")
KEY = os.environ.get("VOXO_API_KEY")
MIME = {"wav": "audio/wav", "mp3": "audio/mpeg", "ogg": "audio/ogg", "m4a": "audio/mp4",
        "flac": "audio/flac", "webm": "audio/webm"}


def req(method, path, body=None, headers=None):
    url = path if path.startswith("http") else API + path
    data = json.dumps(body).encode() if body is not None else None
    auth = KEY if (KEY or "").lower().startswith("bearer ") else f"Bearer {KEY}"
    h = {"Authorization": auth, "Content-Type": "application/json"}
    if headers:
        h.update(headers)
    r = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=120) as resp:
            raw = resp.read()
            return json.loads(raw) if "json" in resp.headers.get("content-type", "") else raw
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode(errors='replace')[:500]}")


def main():
    ap = argparse.ArgumentParser(description="VOXO transcription")
    ap.add_argument("audio")
    ap.add_argument("--language", default="", help="empty = auto-detect")
    ap.add_argument("--json", action="store_true", help="print the full job JSON")
    a = ap.parse_args()
    if not KEY:
        sys.exit("set VOXO_API_KEY (dashboard → API & MCP)")

    ext = a.audio.rsplit(".", 1)[-1].lower()
    with open(a.audio, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    asset = req("POST", "/v1/assets/base64", {
        "data_base64": b64, "filename": os.path.basename(a.audio),
        "kind": "source_audio", "content_type": MIME.get(ext, "audio/wav")})
    print(f"uploaded {asset['id']} — transcribing…", file=sys.stderr)

    body = {"task_type": "transcribe", "audio_asset_id": asset["id"]}
    if a.language:
        body["language"] = a.language
    job = req("POST", "/v1/generations", body, {"Idempotency-Key": str(uuid.uuid4())})

    deadline = time.time() + 300
    while job.get("status") not in ("succeeded", "failed", "cancelled"):
        if time.time() > deadline:
            sys.exit("timeout waiting for transcription")
        time.sleep(3)
        job = req("GET", f"/v1/generations/{job['id']}")
    if job["status"] != "succeeded":
        sys.exit(f"job {job['status']}: {job.get('error')}")

    if a.json:
        print(json.dumps(job, ensure_ascii=False, indent=2))
        return
    result = job.get("result") or job.get("transcript") or {}
    text = result.get("text") if isinstance(result, dict) else result
    print(text or "(no transcript field — re-run with --json to inspect)")
    segs = (result.get("segments") if isinstance(result, dict) else None) or []
    for s in segs:
        print(f"[{s.get('start'):>7}s → {s.get('end'):>7}s] {s.get('text')}", file=sys.stderr)


if __name__ == "__main__":
    main()
