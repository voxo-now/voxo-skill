#!/usr/bin/env python3
"""VOXO clone-and-speak: upload a reference clip, create a cloned voice, wait until it is
enabled, then synthesize text with it. Stdlib only. Use a clean 10-30 s single-speaker clip.

  export VOXO_API_KEY=amk_live_...
  python3 clone_and_speak.py sample.wav "Read this in my voice." --name "My Voice" --language en --out out.wav

You must have the right to clone the voice (consent is attested automatically).
"""
import os, sys, json, time, uuid, base64, argparse, urllib.request, urllib.error

API = os.environ.get("VOXO_API_URL", "https://api.voxo.now").rstrip("/")
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


def find_voice(voice_id):
    for v in req("GET", "/v1/voices").get("voices", []):
        if v.get("id") == voice_id:
            return v
    return None


def main():
    ap = argparse.ArgumentParser(description="VOXO clone a voice, then speak")
    ap.add_argument("reference_audio", help="clean 10-30 s single-speaker clip")
    ap.add_argument("text", help="what the cloned voice should say")
    ap.add_argument("--name", default="Cloned voice")
    ap.add_argument("--language", default="en")
    ap.add_argument("--gender", default="unknown")
    ap.add_argument("--reference-text", default="", help="optional transcript; else auto (Whisper)")
    ap.add_argument("--out", default="out.wav")
    a = ap.parse_args()
    if not KEY:
        sys.exit("set VOXO_API_KEY (dashboard → API & MCP)")

    ext = a.reference_audio.rsplit(".", 1)[-1].lower()
    with open(a.reference_audio, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    asset = req("POST", "/v1/assets/base64", {
        "data_base64": b64, "filename": os.path.basename(a.reference_audio),
        "kind": "reference_audio", "content_type": MIME.get(ext, "audio/wav")})
    print(f"uploaded reference asset {asset['id']}", file=sys.stderr)

    vbody = {"reference_audio_asset_id": asset["id"], "display_name": a.name,
             "gender": a.gender, "language": a.language, "consent": "confirmed"}
    if a.reference_text:
        vbody["reference_text"] = a.reference_text
    voice = req("POST", "/v1/voices", vbody)
    vid = voice["id"]
    print(f"voice {vid} created ({voice.get('status')}) — waiting to enable…", file=sys.stderr)

    deadline = time.time() + 180
    while voice and voice.get("status") == "processing":
        if time.time() > deadline:
            sys.exit("timeout waiting for the clone to enable")
        time.sleep(2)
        voice = find_voice(vid)
    if not voice or voice.get("status") != "enabled":
        sys.exit(f"clone not usable (status {voice.get('status') if voice else 'gone'})")

    job = req("POST", "/v1/generations",
              {"task_type": "tts_clone", "text": a.text, "language": a.language,
               "voice_id": vid, "controls": {}},
              {"Idempotency-Key": str(uuid.uuid4())})
    print(f"job {job['id']} created — waiting…", file=sys.stderr)
    deadline = time.time() + 300
    while job.get("status") not in ("succeeded", "failed", "cancelled"):
        if time.time() > deadline:
            sys.exit("timeout waiting for job")
        time.sleep(3)
        job = req("GET", f"/v1/generations/{job['id']}")
    if job["status"] != "succeeded":
        sys.exit(f"job {job['status']}: {job.get('error')}")

    outs = job.get("outputs") or []
    url = next((o.get("download_url") for o in outs if o.get("download_url")), None)
    if not url:
        sys.exit("job succeeded but no downloadable output")
    audio = req("GET", url)
    with open(a.out, "wb") as f:
        f.write(audio)
    print(f"voice_id={vid}\nsaved {a.out} ({len(audio)} bytes)")


if __name__ == "__main__":
    main()
