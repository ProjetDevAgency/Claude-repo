"""Étape 1 : voix (ElevenLabs) + bruitages + timeline, à partir d'un script au format du moteur S1.

Produit build/audio.wav et build/timeline.json (caméra, sous-titres mot à mot, événements).

    python tueur/audio.py tueur/episodes/mon_loup_p1.json

Chaque réplique est mise en cache dans build/tts_cache : relancer ne consomme pas de crédits
ElevenLabs tant que le texte et la voix ne changent pas.
"""
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

import numpy as np

SR = 48000
rng = np.random.default_rng(3)
HERE = Path(__file__).parent
BUILD = HERE / "build"
CACHE = BUILD / "tts_cache"


# ---------- script ----------
def parse_script(text):
    items = []
    for raw in text.splitlines():
        l = raw.strip()
        if not l or (l.upper().startswith("PARTIE") and ">" not in l):
            continue
        if l.startswith("[") and l.endswith("]"):
            items.append({"type": "sfx", "name": l[1:-1].strip().upper()})
        elif ">" in l:
            who, txt = l.split(">", 1)
            items.append({"type": "line", "speaker": who.strip().upper(), "text": txt.strip()})
    return items


# ---------- voix ElevenLabs (avec minutage des caractères) ----------
def tts_elevenlabs(text, voice, model, prev_text=None, next_text=None):
    body = {"text": text, "model_id": model, "voice_settings": voice.get("settings", {})}
    if prev_text:
        body["previous_text"] = prev_text
    if next_text:
        body["next_text"] = next_text
    key = hashlib.sha1(json.dumps([voice["id"], body], sort_keys=True).encode()).hexdigest()[:16]
    f = CACHE / f"{key}.json"
    if f.exists():
        return json.loads(f.read_text())
    api_key = os.environ.get("ELEVENLABS_API_KEY", "proxy-injected")  # le proxy de l'environnement remplace la clé
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice['id']}/with-timestamps?output_format=mp3_44100_192",
        data=json.dumps(body).encode(), method="POST",
        headers={"xi-api-key": api_key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.loads(r.read())
    out = {"audio": d["audio_base64"], "alignment": d.get("alignment") or d.get("normalized_alignment")}
    CACHE.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(out))
    print(f"  voix générée ({len(text)} car.) : {text[:50]}")
    return out


FILTRES = {
    "porte": "lowpass=f=950,aecho=0.8:0.6:35|70:0.25|0.12,volume=1.6",
    "telephone": "highpass=f=380,lowpass=f=3300,acompressor,volume=1.3",
}


def decode(mp3_bytes, effet=None):
    af = ["-af", FILTRES[effet]] if effet else []
    raw = subprocess.run(["ffmpeg", "-v", "error", "-f", "mp3", "-i", "-", *af, "-ac", "1", "-ar", str(SR),
                          "-f", "f32le", "-"], input=mp3_bytes, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def words_from_alignment(al):
    words, cur, start = [], "", None
    chars, st, en = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
    for c, s, e in zip(chars, st, en):
        if c.isspace():
            if cur:
                words.append({"w": cur, "s": start, "e": last})
            cur, start = "", None
            continue
        if start is None:
            start = s
        cur += c
        last = e
    if cur:
        words.append({"w": cur, "s": start, "e": last})
    return words


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


def knock3():
    out = np.zeros(int(SR * 1.1), np.float32)
    for i, g in enumerate((1.0, 0.95, 1.05)):
        k = knock() * g
        j = int(i * 0.3 * SR)
        out[j:j + len(k)] += k
    return out


def buzz(d=1.1):
    t = t_(d)
    gate = (np.sin(2 * np.pi * 4 * t) > -0.2).astype(np.float32)
    x = np.sign(np.sin(2 * np.pi * 150 * t)) * 0.5 + np.sin(2 * np.pi * 300 * t) * 0.3
    return lp(x.astype(np.float32), 20) * gate * 0.35


def creak(d=1.5):
    t = t_(d)
    f = 520 + 160 * np.sin(2 * np.pi * 0.7 * t) + 40 * rng.standard_normal(len(t)).cumsum() / 400
    pulses = (np.sin(2 * np.pi * np.cumsum(f / 9) / SR) > 0.6).astype(np.float32)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * pulses
    e = np.sin(np.pi * np.linspace(0, 1, len(t))) ** 0.6
    return lp(tone.astype(np.float32), 3) * e * 0.22


def steps(n=6, gap=0.42):
    out = np.zeros(int(SR * (n * gap + 0.5)), np.float32)
    for i in range(n):
        t = t_(0.25)
        thud = np.sin(2 * np.pi * (70 * np.exp(-t * 20) + 45) * t) * env(len(t), 0.002, 0.05)
        scuff = lp(rng.standard_normal(len(t)).astype(np.float32), 12) * env(len(t), 0.001, 0.02) * 0.4
        s = (thud + scuff) * (0.25 + 0.75 * i / (n - 1))  # de plus en plus près
        j = int(i * gap * SR)
        out[j:j + len(s)] += s
    rev = np.zeros_like(out)  # petite réverbération de cage d'escalier
    for d, g in ((0.06, 0.4), (0.13, 0.25), (0.21, 0.12)):
        k = int(d * SR)
        rev[k:] += out[:-k] * g
    return (out + rev) * 0.8


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
    return ((x * 0.07 + wind * 0.05) * np.minimum(1, t / 1.5)).astype(np.float32)


SONS = {"knock3": knock3, "buzz": buzz, "creak": creak, "steps": steps, "sting": sting}
EVENT = {"knock3": "knock", "buzz": "buzz", "creak": "creak", "steps": "steps", "sting": "sting"}


def place(buf, clip, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf):
        return
    clip = clip[: len(buf) - i]
    buf[i:i + len(clip)] += clip * gain


# ---------- montage ----------
def layout(items, clips, ep, extra_pause=0.0):
    ry, sfx = ep["rythme"], ep["bruitages"]
    t, lines, events, prev = ry["debut"], [], {}, None
    for it in items:
        if it["type"] == "sfx":
            if it["name"] == "PAUSE":
                t += ry["pause"] + extra_pause
            else:
                s = sfx[it["name"]]
                events.setdefault(EVENT[s["son"]], []).append(round(t, 3))
                t += s.get("avance", 0.5)
            continue
        c = clips[len(lines)]
        if prev is not None:
            t += ry["entre_repliques"] + (0.1 if prev != it["speaker"] else 0)
        d = len(c["pcm"]) / SR
        lines.append({"i": len(lines) + 1, "speaker": it["speaker"], "text": it["text"],
                      "start": round(t, 3), "end": round(t + d, 3),
                      "words": [{"w": w["w"], "s": round(t + w["s"] - c["trim"], 3), "e": round(t + w["e"] - c["trim"], 3)}
                                for w in c["words"]]})
        t += d
        prev = it["speaker"]
    if "QUESTION" in sfx:
        events.setdefault("sting", []).append(round(lines[-1]["start"] - 0.1, 3))
    return lines, events, t + ry["tenue_finale"]


def main(ep_path):
    ep_path = Path(ep_path)
    ep = json.loads(ep_path.read_text(encoding="utf-8"))
    BUILD.mkdir(exist_ok=True)
    items = parse_script((HERE / ep["script"]).read_text(encoding="utf-8"))
    voix, model = ep["tts"]["voix"], ep["tts"]["model"]
    speech = [it for it in items if it["type"] == "line"]
    clips = []
    for k, it in enumerate(speech):
        v = voix[it["speaker"]]
        same = lambda j: 0 <= j < len(speech) and speech[j]["speaker"] == it["speaker"]
        d = tts_elevenlabs(it["text"], v, model,
                           speech[k - 1]["text"] if same(k - 1) else None,
                           speech[k + 1]["text"] if same(k + 1) else None)
        pcm = decode(base64.b64decode(d["audio"]), v.get("effet"))
        idx = np.where(np.abs(pcm) > 0.012)[0]
        a = max(0, idx[0] - int(0.03 * SR)) if len(idx) else 0
        b = min(len(pcm), idx[-1] + int(0.12 * SR)) if len(idx) else len(pcm)
        clips.append({"pcm": pcm[a:b], "trim": a / SR, "words": words_from_alignment(d["alignment"]),
                      "gain": v.get("gain", 1.0)})

    n_pauses = sum(1 for it in items if it.get("name") == "PAUSE")
    lines, events, total = layout(items, clips, ep)
    if total < ep["rythme"]["duree_min"] and n_pauses:  # jamais sous 61 s : on allonge les silences
        lines, events, total = layout(items, clips, ep, (ep["rythme"]["duree_min"] - total) / n_pauses)

    mix = drone(total)
    for ln, c in zip(lines, clips):
        place(mix, c["pcm"], ln["start"], c["gain"])
    for name, times in events.items():
        son = {v: k for k, v in EVENT.items()}[name]
        for at in times:
            place(mix, SONS[son](), at, 1.0 if name != "steps" else 0.9)
    hb = lines[ep["battements_depuis"] - 1]["start"]
    place(mix, heartbeat(int((total - hb) * 72 / 60) + 1), hb, 0.55)

    mix = mix / max(1e-6, np.abs(mix).max()) * 0.9
    wav = BUILD / "audio.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1",
                    "-i", "-", str(wav)], input=mix.astype(np.float32).tobytes(), check=True)
    plans = ep["plans"]
    assert len(plans) == len(lines), f"{len(plans)} plans pour {len(lines)} répliques"
    out = {"duration": round(total, 3), "lines": lines, "events": events,
           "plans": [{"name": p, "start": 0 if i == 0 else lines[i]["start"] - 0.05} for i, p in enumerate(plans)],
           "marques": {k: lines[v - 1]["start"] for k, v in ep["marques"].items()},
           "speakers": {k: {"texto": bool(v.get("texto")), "effet": v.get("effet")} for k, v in voix.items()},
           **{k: ep[k] for k in ("hud", "regle", "texto", "choix", "rouge", "sortie")}}
    out["regle"]["start"], out["regle"]["end"] = lines[ep["regle"]["ligne"] - 1]["start"], lines[ep["regle"]["ligne"] - 1]["end"]
    (BUILD / "timeline.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"audio {total:.1f} s, {len(lines)} répliques -> {wav}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else HERE / "episodes" / "mon_loup_p1.json")
