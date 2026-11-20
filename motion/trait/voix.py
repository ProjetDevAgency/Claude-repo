"""Voix ElevenLabs AVEC le temps de chaque mot (endpoint /with-timestamps) : pas besoin de Whisper.

Une ligne = (voix, texte). Les lignes sont mises bout à bout avec une petite respiration.
Marquage du texte (retiré avant la synthèse, gardé pour les sous-titres) :
    [84 euros]   mot(s) clé(s) en JAUNE        {perdu}   mot(s) en ROUGE
Renvoie la piste mono 48 kHz (numpy) et la liste des mots : {"w", "t0", "t1", "mark", "line"}.
"""
import base64
import json
import os
import re
import subprocess
import urllib.request
from pathlib import Path

import numpy as np

SR = 48000
API = "https://api.elevenlabs.io/v1/text-to-speech/{}/with-timestamps?output_format=mp3_44100_192"


def _parse(text):
    """Texte marqué → (texte propre, [(mot, marque)])."""
    words = []
    for m in re.finditer(r"\[([^\]]+)\]|\{([^}]+)\}|(\S+)", text):
        if m.group(1):
            words += [(w, "y") for w in m.group(1).split()]
        elif m.group(2):
            words += [(w, "r") for w in m.group(2).split()]
        else:
            words.append((m.group(3), ""))
    # ponctuation collée à un groupe marqué : « [84 euros], » → le « , » rejoint le mot précédent
    out = []
    for w, k in words:
        if out and re.fullmatch(r"[,.;:!?…»]+", w):
            out[-1] = (out[-1][0] + w, out[-1][1])
        else:
            out.append((w, k))
    return " ".join(w for w, _ in out), out


def _tts(text, voice_id, model, cache: Path, settings):
    key = hashlib_key(text, voice_id, model, settings)
    f = cache / f"{key}.json"
    if not f.exists():
        body = json.dumps({"text": text, "model_id": model, "voice_settings": settings}).encode()
        req = urllib.request.Request(API.format(voice_id), data=body, method="POST", headers={
            "xi-api-key": os.environ.get("ELEVENLABS_API_KEY", "proxy"), "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=300) as r:
            f.write_bytes(r.read())
    d = json.loads(f.read_text())
    mp3 = cache / f"{key}.mp3"
    mp3.write_bytes(base64.b64decode(d["audio_base64"]))
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(mp3), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    al = d.get("normalized_alignment") or d["alignment"]
    return np.frombuffer(raw, np.float32).copy(), al


def hashlib_key(*a):
    import hashlib
    return hashlib.sha1(json.dumps(a, sort_keys=True).encode()).hexdigest()[:16]


def _trim(x, thr=0.012):
    """Coupe le silence au début et à la fin ; renvoie (piste, secondes coupées au début)."""
    idx = np.where(np.abs(x) > thr)[0]
    if not len(idx):
        return x, 0.0
    a = max(0, idx[0] - int(0.03 * SR))
    b = min(len(x), idx[-1] + int(0.08 * SR))
    return x[a:b], a / SR


def build(lines, voices, work: Path, model="eleven_multilingual_v2", gap=0.22, speed=1.0):
    """lines : [(clé de voix, texte marqué)] ; voices : {clé: (voice_id, réglages)}."""
    work.mkdir(parents=True, exist_ok=True)
    pistes, words, t = [], [], 0.0
    for li, (who, text) in enumerate(lines):
        clean, marked = _parse(text)
        vid, st = voices[who]
        audio, al = _tts(clean, vid, model, work, st)
        audio, cut = _trim(audio)
        chars, starts, ends = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
        # mots ElevenLabs (séparés par des espaces) → mêmes mots que le texte marqué
        spans, cur = [], None
        for c, s0, s1 in zip(chars, starts, ends):
            if c.isspace():
                if cur:
                    spans.append(cur)
                cur = None
            elif cur is None:
                cur = [s0, s1]
            else:
                cur[1] = s1
        if cur:
            spans.append(cur)
        if len(spans) != len(marked):           # sécurité : on répartit au prorata
            tot = len(audio) / SR
            spans = [[tot * i / len(marked), tot * (i + 1) / len(marked)] for i in range(len(marked))]
        for (w, k), (s0, s1) in zip(marked, spans):
            words.append({"w": w, "t0": t + max(0, s0 - cut) / speed, "t1": t + max(0, s1 - cut) / speed,
                          "mark": k, "line": li, "who": who})
        pistes.append(audio)
        pistes.append(np.zeros(int(gap * SR), np.float32))
        t += (len(audio) / SR + gap) / speed
    voice = np.concatenate(pistes)
    if speed != 1.0:
        tmp_in, tmp_out = work / "_v.f32", work / "_v2.f32"
        voice.tofile(tmp_in)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", str(tmp_in),
                        "-af", f"atempo={speed}", "-f", "f32le", str(tmp_out)], check=True)
        voice = np.fromfile(tmp_out, np.float32)
    return voice, words


def enveloppe(voice, fps=30):
    """Volume de la voix par image (0-1), pour faire bouger les bouches."""
    n = int(len(voice) / SR * fps) + 2
    hop = SR // fps
    env = np.array([np.sqrt(np.mean(voice[i * hop:(i + 1) * hop] ** 2) + 1e-12) for i in range(n)])
    env = np.nan_to_num(env)
    return np.clip(env / (np.percentile(env, 95) + 1e-9), 0, 1)
