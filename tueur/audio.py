"""Étape 1 : voix off + bruitages + timeline.

Produit build/audio.wav et build/timeline.json (utilisé par la scène 3D pour
caler caméra, sous-titres et événements sur la voix).

    python tueur/audio.py tueur/episodes/ep1.json
"""
import asyncio
import json
import os
import ssl
import subprocess
import sys
from pathlib import Path

import numpy as np

SR = 48000
rng = np.random.default_rng(3)
HERE = Path(__file__).parent
BUILD = HERE / "build"


# ---------- voix (Microsoft neural gratuite, via edge-tts) ----------
async def _tts(text, out, voice, rate):
    import edge_tts
    import edge_tts.communicate as c
    ca = "/root/.ccr/ca-bundle.crt"
    if os.path.exists(ca):  # proxy de l'environnement cloud
        c._SSL_CTX = ssl.create_default_context(cafile=ca)
    cm = edge_tts.Communicate(text, voice, rate=rate, pitch="-4Hz",
                              proxy=os.environ.get("HTTPS_PROXY"))
    await cm.save(str(out))


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).copy()
    # coupe les silences de début/fin
    idx = np.where(np.abs(x) > 0.01)[0]
    return x[max(0, idx[0] - 600): idx[-1] + 2400] if len(idx) else x


# ---------- bruitages (fabriqués, aucun droit) ----------
def t_(d):
    return np.arange(int(SR * d)) / SR


def env(n, a=0.005, r=0.2):
    t = np.arange(n) / SR
    return (np.minimum(1, t / a) * np.exp(-t / r)).astype(np.float32)


def lp(x, k):
    return np.convolve(x, np.ones(k) / k, mode="same").astype(np.float32) if k > 1 else x


def knock():
    t = t_(0.35)
    f = 180 * np.exp(-t * 25) + 70
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.001, 0.06)
    wood = lp(rng.standard_normal(len(t)).astype(np.float32), 4) * env(len(t), 0.0005, 0.012)
    return (body + 0.6 * wood) * 0.9


def buzz(d=1.1):
    t = t_(d)
    gate = (np.sin(2 * np.pi * 4 * t) > -0.2).astype(np.float32)
    x = np.sign(np.sin(2 * np.pi * 150 * t)) * 0.5 + np.sin(2 * np.pi * 300 * t) * 0.3
    return lp(x.astype(np.float32), 20) * gate * 0.35


def creak(d=1.6):
    t = t_(d)
    f = 520 + 160 * np.sin(2 * np.pi * 0.7 * t) + 40 * rng.standard_normal(len(t)).cumsum() / 400
    pulses = (np.sin(2 * np.pi * np.cumsum(f / 9) / SR) > 0.6).astype(np.float32)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * pulses
    e = np.sin(np.pi * np.linspace(0, 1, len(t))) ** 0.6
    return lp(tone.astype(np.float32), 3) * e * 0.22


def heartbeat(n_beats, bpm=72):
    one = np.zeros(int(SR * 60 / bpm), np.float32)
    for off, g in ((0, 1.0), (0.18, 0.7)):
        t = t_(0.18)
        b = np.sin(2 * np.pi * (55 * np.exp(-t * 6) + 30) * t) * env(len(t), 0.003, 0.05) * g
        i = int(off * SR)
        one[i:i + len(b)] += b
    return np.tile(one, n_beats) * 0.8


def sting():
    t = t_(2.5)
    x = sum(np.sin(2 * np.pi * f * t + p) for f, p in ((55, 0), (58.3, 1), (82.4, 2), (110.5, 0.5)))
    hit = lp(rng.standard_normal(len(t)).astype(np.float32), 30) * env(len(t), 0.002, 0.25) * 2
    return (x / 4 * env(len(t), 0.01, 1.0) + hit) * 0.55


def drone(d):
    t = t_(d)
    x = (np.sin(2 * np.pi * 43.65 * t) + 0.6 * np.sin(2 * np.pi * 65.4 * t + 1)
         + 0.25 * np.sin(2 * np.pi * 87.3 * t * (1 + 0.002 * np.sin(t))))
    wind = lp(rng.standard_normal(len(t)).astype(np.float32), 200) * 6
    return ((x * 0.07 + wind * 0.05) * np.minimum(1, t / 2)).astype(np.float32)


def place(buf, clip, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf):
        return
    clip = clip[: len(buf) - i]
    buf[i:i + len(clip)] += clip * gain


# ---------- montage ----------
def main(ep_path):
    ep = json.loads(Path(ep_path).read_text())
    BUILD.mkdir(exist_ok=True)
    voice, rate = ep.get("voice", "fr-FR-RemyMultilingualNeural"), ep.get("rate", "-6%")

    clips = []
    for i, ln in enumerate(ep["lines"]):
        mp3 = BUILD / f"line{i}.mp3"
        spoken = ln.get("say", ln["text"] + " " + ln.get("hi", ""))
        asyncio.run(_tts(spoken, mp3, voice, rate))
        clips.append(load(mp3))

    timeline, t = [], ep.get("intro", 1.4)
    for ln, c in zip(ep["lines"], clips):
        t += ln.get("pause_before", 0)
        d = len(c) / SR
        timeline.append({"id": ln["id"], "start": round(t, 3), "end": round(t + d, 3),
                         "text": ln["text"], "hi": ln.get("hi", ""), "voice": c})
        t += d + ln.get("gap", 0.45)
    total = t + ep.get("outro", 2.5)

    mix = drone(total)
    for seg in timeline:
        place(mix, seg.pop("voice"), seg["start"], 1.0)
    at = {s["id"]: s for s in timeline}
    events = {}
    for e in ep["sfx"]:
        when = at[e["line"]][e.get("anchor", "start")] + e.get("offset", 0)
        events.setdefault(e["name"], []).append(round(when, 3))
        clip = {"knock": knock, "buzz": buzz, "creak": creak, "sting": sting}[e["name"]]()
        place(mix, clip, when, e.get("gain", 1.0))
    hb_start = at[ep["heartbeat_from"]]["start"]
    place(mix, heartbeat(int((total - hb_start) * 72 / 60) + 1), hb_start, 0.6)

    mix = mix / max(1e-6, np.abs(mix).max()) * 0.9
    wav = BUILD / "audio.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1",
                    "-i", "-", str(wav)], input=mix.astype(np.float32).tobytes(), check=True)
    out = {"duration": round(total, 3), "lines": timeline, "events": events,
           "hud": ep.get("hud", {}), "choice": ep["choice"]}
    (BUILD / "timeline.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"audio {total:.1f}s -> {wav}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else HERE / "episodes" / "ep1.json")
