#!/usr/bin/env python3
"""VOXO text-to-speech: create a job, poll until done, download the .wav. Stdlib only.

  export VOXO_API_KEY=amk_live_...
  python3 tts.py "Hello world" --voice voi_ava... --language en --out hello.wav
  python3 tts.py "Labas rytas" --language lt --emotion contentment --out labas.wav   # zero-shot
"""
import os, sys, json, time, uuid, argparse, urllib.request, urllib.error

API = os.environ.get("VOXO_API_URL", "https://speech-api.mvpro.lt").rstrip("/")
KEY = os.environ.get("VOXO_API_KEY")


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


def wait_job(job_id, timeout=300):
    deadline = time.time() + timeout
    job = req("GET", f"/v1/generations/{job_id}")
    while job.get("status") not in ("succeeded", "failed", "cancelled"):
        if time.time() > deadline:
            sys.exit("timeout waiting for job")
        time.sleep(3)
        job = req("GET", f"/v1/generations/{job_id}")
    return job


def main():
    ap = argparse.ArgumentParser(description="VOXO text-to-speech")
    ap.add_argument("text")
    ap.add_argument("--voice", default="", help="voice_id (omit for zero-shot)")
    ap.add_argument("--language", default="en")
    ap.add_argument("--emotion", default="")
    ap.add_argument("--style", default="", help="singing|shouting|whispering")
    ap.add_argument("--prosody", default="", help="comma-separated, e.g. speed_fast,pitch_high")
    ap.add_argument("--seed", type=int, default=-1, help="pin a zero-shot voice; -1 = random")
    ap.add_argument("--out", default="out.wav")
    a = ap.parse_args()
    if not KEY:
        sys.exit("set VOXO_API_KEY (dashboard → API & MCP)")

    controls = {}
    if a.emotion:
        controls["emotion"] = a.emotion
    if a.style:
        controls["style"] = a.style
    if a.prosody:
        controls["prosody"] = [p.strip() for p in a.prosody.split(",") if p.strip()]

    body = {"task_type": "tts_clone" if a.voice else "tts", "text": a.text,
            "language": a.language, "controls": controls}
    if a.voice:
        body["voice_id"] = a.voice
    if a.seed >= 0:
        body["seed"] = a.seed

    job = req("POST", "/v1/generations", body, {"Idempotency-Key": str(uuid.uuid4())})
    print(f"job {job['id']} created ({job.get('status')}) — waiting…", file=sys.stderr)
    job = wait_job(job["id"])
    if job["status"] != "succeeded":
        sys.exit(f"job {job['status']}: {job.get('error')}")

    outs = job.get("outputs") or []
    url = next((o.get("download_url") for o in outs if o.get("download_url")), None)
    if not url:
        sys.exit("job succeeded but no downloadable output")
    audio = req("GET", url)
    with open(a.out, "wb") as f:
        f.write(audio)
    print(f"saved {a.out} ({len(audio)} bytes, {outs[0].get('duration_s')} s)")


if __name__ == "__main__":
    main()
