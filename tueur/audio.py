"""Étape 1 : voix (ElevenLabs) + bruitages + timeline, à partir d'un script au format du moteur S1.

Produit build/<sortie>/audio.wav et build/<sortie>/timeline.json (caméra, sous-titres mot à mot, événements).

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
    "rideau": "lowpass=f=4200,aecho=0.6:0.4:18|31:0.2|0.1,volume=1.25",  # tout près, derrière un tissu, dans une pièce carrelée
}


def decode(mp3_bytes):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-f", "mp3", "-i", "-", "-ac", "1", "-ar", str(SR),
                          "-f", "f32le", "-"], input=mp3_bytes, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def ffilter(pcm, af):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", af,
                          "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], input=pcm.astype(np.float32).tobytes(),
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def tighten(pcm, bounds, ry, phrases=()):
    """Resserre la voix comme la chaîne repost : chaque silence trop long est ramené à une durée courte
    (un peu plus longue entre deux répliques qu'à l'intérieur d'une phrase). Renvoie l'audio et une
    fonction qui convertit un temps d'origine en temps resserré, pour garder les sous-titres calés."""
    fr = int(0.01 * SR)
    n = len(pcm) // fr
    rms = np.sqrt(np.mean(pcm[: n * fr].reshape(n, fr) ** 2, axis=1) + 1e-12)
    silent = 20 * np.log10(rms) < ry.get("seuil_silence_db", -40)
    keep_mask = np.ones(n, bool)
    i = 0
    while i < n:
        if not silent[i]:
            i += 1
            continue
        j = i
        while j < n and silent[j]:
            j += 1
        dur = (j - i) * 0.01
        t0, t1 = i * 0.01, j * 0.01
        if i == 0:
            keep = 0.03
        elif j == n:
            keep = 0.10
        elif any(t0 - 0.05 <= b <= t1 + 0.05 for b in bounds):
            keep = ry.get("silence_garde_ligne", 0.22)
        elif any(t0 - 0.05 <= b <= t1 + 0.05 for b in phrases):  # fin de phrase : une vraie petite pause
            keep = ry.get("silence_garde_phrase", ry.get("silence_garde", 0.12))
        else:
            keep = ry.get("silence_garde", 0.12)
        if dur > max(keep, ry.get("silence_min", 0.16)) or i == 0 or j == n:
            k = int(round(keep / 0.01))
            a, b = i + k // 2, j - (k - k // 2)
            if b > a:
                keep_mask[a:b] = False
        i = j
    seg_o, seg_n, out, tn = [], [], [], 0.0
    for f in range(n):
        if keep_mask[f]:
            seg_o.append(f * 0.01); seg_n.append(tn); out.append(pcm[f * fr:(f + 1) * fr]); tn += 0.01
    seg_o, seg_n = np.array(seg_o), np.array(seg_n)

    def tmap(t):
        k = np.searchsorted(seg_o, t, side="right") - 1
        if k < 0:
            return 0.0
        return float(seg_n[k] + min(0.01, t - seg_o[k]))
    return (np.concatenate(out) if out else pcm), tmap


TAG = re.compile(r"\[[^\]]*\]")


def strip_tags(t):
    return re.sub(r"\s+", " ", TAG.sub("", t)).strip()


def words_from_alignment(al):
    words, cur, start, depth = [], "", None, 0
    chars, st, en = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
    for c, s, e in zip(chars, st, en):
        if c == "[":
            depth += 1
            continue
        if c == "]":
            depth = max(0, depth - 1)
            continue
        if depth:  # balise d'émotion : jouée, pas affichée
            continue
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


def boost_breaths(pcm, al, gain):
    """Remonte le volume des respirations et halètements demandés par balise ([heavy breathing], [gasps]…).
    ElevenLabs les joue environ 18 dB sous la voix, la musique les couvre sinon."""
    if gain == 1.0:
        return pcm
    chars, st, en = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
    text = "".join(chars)
    out = pcm.copy()
    for m in TAG.finditer(text):
        if not re.search(r"breath|gasp|pant|sigh", m.group(), re.I):
            continue
        a = st[m.start()]
        nxt = next((j for j in range(m.end(), len(chars)) if not chars[j].isspace()), None)
        b = st[nxt] if nxt is not None else en[m.end() - 1]  # jusqu'au premier mot qui suit
        i0, i1 = int(a * SR), min(len(out), int(b * SR))
        if i1 - i0 < int(0.08 * SR):
            continue
        ramp = int(0.03 * SR)
        g = np.full(i1 - i0, gain, np.float32)
        g[:ramp] = np.linspace(1, gain, ramp); g[-ramp:] = np.linspace(gain, 1, ramp)
        out[i0:i1] *= g
    return np.clip(out, -1, 1)


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


def rideau(d=0.9):
    """Les anneaux du rideau de douche qui glissent sur la tringle."""
    out = np.zeros(int(SR * d), np.float32)
    for i in range(9):
        t = t_(0.06)
        f = 2600 + rng.uniform(-400, 600)
        click = np.sin(2 * np.pi * f * t) * env(len(t), 0.0005, 0.012) * rng.uniform(0.4, 0.8)
        j = int((0.05 + i * 0.07 + rng.uniform(0, 0.02)) * SR)
        out[j:j + len(click)] += click
    swish = lp(rng.standard_normal(len(out)).astype(np.float32), 8) * np.sin(np.pi * np.linspace(0, 1, len(out))) * 0.12
    return (out + swish) * 0.7


def ding():
    """Le ding de l'ascenseur, deux notes."""
    out = np.zeros(int(SR * 1.6), np.float32)
    for k, (f, at) in enumerate(((1046.5, 0.0), (830.6, 0.32))):
        t = t_(1.2)
        tone = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)) * env(len(t), 0.003, 0.45)
        j = int(at * SR)
        out[j:j + len(tone)] += tone * 0.45
    return out


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


SONS = {"knock3": knock3, "buzz": buzz, "creak": creak, "steps": steps, "sting": sting, "rideau": rideau, "ding": ding}
EVENT = {"knock3": "knock", "buzz": "buzz", "creak": "creak", "steps": "steps", "sting": "sting", "rideau": "rideau", "ding": "ding"}


def place(buf, clip, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf):
        return
    clip = clip[: len(buf) - i]
    buf[i:i + len(clip)] += clip * gain


# ---------- montage ----------
def make_blocks(items):
    """Regroupe les répliques consécutives d'une même voix, sans bruitage ni pause entre elles :
    elles sont générées d'un seul tenant, pour une intonation continue, comme quelqu'un qui raconte."""
    blocks, cur = [], None
    for it in items:
        if it["type"] == "line" and cur and cur["speaker"] == it["speaker"]:
            cur["lines"].append(it)
            continue
        if it["type"] == "line":
            cur = {"speaker": it["speaker"], "lines": [it]}
            blocks.append(cur)
        else:
            cur = None
            blocks.append(it)
    return blocks


def voice_block(blk, k, blocks, ep, n0, vitesse):
    v = ep["tts"]["voix"][blk["speaker"]]
    jeu = ep.get("jeu", {})
    spoken = []
    for j, ln in enumerate(blk["lines"]):
        t = jeu.get(str(n0 + j + 1), ln["text"])
        assert strip_tags(t) == ln["text"], f"réplique {n0 + j + 1} : le jeu ne correspond pas au script"
        spoken.append(t)
    text = " ".join(spoken)
    near = lambda d: next((" ".join(l["text"] for l in blocks[i]["lines"]) for i in range(k + d, -1 if d < 0 else len(blocks), d)
                           if "lines" in blocks[i]), None)
    d = tts_elevenlabs(text, v, ep["tts"]["model"], near(-1), near(1))
    al = d["alignment"]
    pcm = boost_breaths(decode(base64.b64decode(d["audio"])), al, ep["rythme"].get("gain_souffle", 1.0))
    # position de chaque réplique dans le texte envoyé, puis dans le temps d'origine
    st, en, spans, o = al["character_start_times_seconds"], al["character_end_times_seconds"], [], 0
    for t in spoken:
        spans.append((o, o + len(t))); o += len(t) + 1
    bounds = [en[min(len(en) - 1, e - 1)] for _, e in spans[:-1]]
    chars = al["characters"]
    phrases = [en[i] for i, c in enumerate(chars) if c in ".?!" and i + 1 < len(chars)]
    pcm, tmap = tighten(pcm, bounds, ep["rythme"], phrases)
    if abs(vitesse - 1.0) > 0.005:
        pcm = ffilter(pcm, f"atempo={vitesse:.3f}")
    if v.get("traitement"):  # retouche propre à la voix (hauteur, égaliseur), sans changer le minutage
        pcm = ffilter(pcm, v["traitement"])
    if v.get("effet"):
        pcm = ffilter(pcm, FILTRES[v["effet"]])
    T = lambda x: tmap(x) / vitesse
    lines = []
    for (s0, s1), ln in zip(spans, blk["lines"]):
        sub = {key: al[key][s0:s1] for key in ("characters", "character_start_times_seconds", "character_end_times_seconds")}
        ws = [{"w": w["w"], "s": T(w["s"]), "e": T(w["e"])} for w in words_from_alignment(sub)]
        lines.append({"speaker": blk["speaker"], "text": ln["text"], "s": ws[0]["s"] - 0.03 if ws else T(st[s0]),
                      "e": ws[-1]["e"] if ws else T(en[s1 - 1]), "words": ws})
    return {"pcm": pcm, "gain": v.get("gain", 1.0), "lines": lines}


def layout(blocks, voiced, ep, extra_pause=0.0):
    ry, sfx = ep["rythme"], ep["bruitages"]
    t, lines, events, prev, placed = ry["debut"], [], {}, None, []
    for blk in blocks:
        if "lines" not in blk:
            if blk["name"] == "PAUSE":
                t += ry["pause"] + extra_pause
            else:
                s = sfx[blk["name"]]
                events.setdefault(EVENT[s["son"]], []).append(round(t, 3))
                t += s.get("avance", 0.5)
            continue
        vb = voiced[id(blk)]
        if prev is not None:
            t += ry["entre_repliques"] + (0.05 if prev != blk["speaker"] else 0)
        for ln in vb["lines"]:
            lines.append({"i": len(lines) + 1, "speaker": ln["speaker"], "text": ln["text"],
                          "start": round(t + max(0, ln["s"]), 3), "end": round(t + ln["e"], 3),
                          "words": [{"w": w["w"], "s": round(t + w["s"], 3), "e": round(t + w["e"], 3)} for w in ln["words"]]})
        placed.append((t, vb))
        t += len(vb["pcm"]) / SR
        prev = blk["speaker"]
    if "QUESTION" in sfx:
        events.setdefault("sting", []).append(round(lines[-1]["start"] - 0.1, 3))
    for sd in ep.get("sons_sous_voix", []):  # bruitages posés sous la voix, sans arrêter le récit
        events.setdefault(EVENT[sd["son"]], []).append(round(sd["a"], 3))
    return lines, events, t + ry["tenue_finale"], placed


def main(ep_path):
    ep_path = Path(ep_path)
    ep = json.loads(ep_path.read_text(encoding="utf-8"))
    out_dir = BUILD / ep["sortie"]
    out_dir.mkdir(parents=True, exist_ok=True)
    items = parse_script((HERE / ep["script"]).read_text(encoding="utf-8"))
    blocks = make_blocks(items)
    ry = ep["rythme"]

    def voice_all(vitesse):
        voiced, n0 = {}, 0
        for k, blk in enumerate(blocks):
            if "lines" in blk:
                voiced[id(blk)] = voice_block(blk, k, blocks, ep, n0, vitesse)
                n0 += len(blk["lines"])
        return voiced

    vitesse = ry.get("vitesse", 1.0)
    n_pauses = sum(1 for it in items if it.get("name") == "PAUSE")
    pause_max = ry.get("pause_max", 1.4)

    def fit(voiced):
        lines, events, total, placed = layout(blocks, voiced, ep)
        if total < ry["duree_min"] and n_pauses:  # d'abord : allonger un peu les pauses dramatiques, sans dépasser pause_max
            extra = min((ry["duree_min"] - total) / n_pauses, max(0.0, pause_max - ry["pause"]))
            lines, events, total, placed = layout(blocks, voiced, ep, extra)
        return lines, events, total, placed

    voiced = voice_all(vitesse)
    lines, events, total, placed = fit(voiced)
    while total < ry["duree_min"] and vitesse > 1.0:  # ensuite seulement : ralentir la voix, par petits pas
        vitesse = round(max(1.0, vitesse - 0.02), 3)
        voiced = voice_all(vitesse)
        lines, events, total, placed = fit(voiced)
    if total < ry["duree_min"] - 0.5:
        manque = ry["duree_min"] - total
        print(f"ATTENTION : {total:.1f} s, il manque {manque:.1f} s. Ajoute environ {int(manque * 15)} caractères "
              f"d'histoire au script (pas de description), comme le prévoit le moteur.")

    mix = drone(total)
    for t0, vb in placed:
        place(mix, vb["pcm"], t0, vb["gain"])
    for name, times in events.items():
        son = {v: k for k, v in EVENT.items()}[name]
        for at in times:
            place(mix, SONS[son](), at, 1.0 if name != "steps" else 0.9)
    hb = lines[ep["battements_depuis"] - 1]["start"]
    place(mix, heartbeat(int((total - hb) * 72 / 60) + 1), hb, 0.55)

    mix = mix / max(1e-6, np.abs(mix).max()) * 0.9
    wav = out_dir / "audio.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1",
                    "-i", "-", str(wav)], input=mix.astype(np.float32).tobytes(), check=True)
    voix = ep["tts"]["voix"]
    plans = ep["plans"]
    assert len(plans) == len(lines), f"{len(plans)} plans pour {len(lines)} répliques"
    out = {"duration": round(total, 3), "lines": lines, "events": events, "vitesse": vitesse,
           "plans": [{"name": p, "start": 0 if i == 0 else lines[i]["start"] - 0.05} for i, p in enumerate(plans)],
           "marques": {k: lines[v - 1]["start"] for k, v in ep["marques"].items()},
           "speakers": {k: {"texto": bool(v.get("texto")), "effet": v.get("effet")} for k, v in voix.items()},
           "scene": ep.get("scene", ep["sortie"]),
           **{k: ep[k] for k in ("hud", "regle", "texto", "choix", "rouge", "sortie")}}
    out["regle"]["start"], out["regle"]["end"] = lines[ep["regle"]["ligne"] - 1]["start"], lines[ep["regle"]["ligne"] - 1]["end"]
    (out_dir / "timeline.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"audio {total:.1f} s, {len(lines)} répliques, vitesse {vitesse} -> {wav}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else HERE / "episodes" / "mon_loup_p1.json")
