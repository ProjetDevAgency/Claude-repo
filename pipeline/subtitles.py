"""Sous-titres mot à mot, calés sur la voix réelle.

1. Whisper transcrit la voix finale avec l'horodatage de chaque mot.
2. On aligne ces mots sur le texte du script (l'orthographe vient du script,
   le timing vient de Whisper) : pas de faute de transcription à l'écran.
3. On écrit un fichier .ass (un mot à la fois, centré, gros contour noir).
"""
import difflib
import re
import unicodedata

import numpy as np

from .audio import load as load_audio

_MODEL = {}


def _norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", w)


def transcribe_words(audio_path, model_size="small"):
    from faster_whisper import WhisperModel
    if model_size not in _MODEL:
        _MODEL[model_size] = WhisperModel(model_size, device="cpu", compute_type="int8")
    samples = load_audio(audio_path)
    # faster-whisper attend du 16 kHz
    samples16 = np.interp(np.arange(0, len(samples), 3), np.arange(len(samples)), samples)
    segs, _ = _MODEL[model_size].transcribe(samples16.astype(np.float32), language="fr",
                                             word_timestamps=True, vad_filter=False)
    words = []
    for s in segs:
        for w in s.words or []:
            words.append({"text": w.word.strip(), "start": w.start, "end": w.end})
    return words


def align(script_text, whisper_words):
    """Donne à chaque mot du script un (start, end) issu de Whisper."""
    tokens = script_text.split()
    a = [_norm(t) for t in tokens]
    b = [_norm(w["text"]) for w in whisper_words]
    times = [None] * len(tokens)
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    for blk in sm.get_opcodes():
        tag, i1, i2, j1, j2 = blk
        if tag == "equal":
            for k in range(i2 - i1):
                w = whisper_words[j1 + k]
                times[i1 + k] = (w["start"], w["end"])
        elif tag == "replace" and j2 > j1:
            # répartit la plage Whisper sur les mots du script
            t0, t1 = whisper_words[j1]["start"], whisper_words[j2 - 1]["end"]
            n = i2 - i1
            for k in range(n):
                times[i1 + k] = (t0 + (t1 - t0) * k / n, t0 + (t1 - t0) * (k + 1) / n)
    # interpole les trous restants
    known = [i for i, t in enumerate(times) if t]
    if not known:
        raise RuntimeError("Alignement impossible : la voix ne correspond pas au script.")
    for i in range(len(times)):
        if times[i]:
            continue
        prev = max([k for k in known if k < i], default=None)
        nxt = min([k for k in known if k > i], default=None)
        t0 = times[prev][1] if prev is not None else 0.0
        t1 = times[nxt][0] if nxt is not None else t0 + 0.3
        span = (nxt if nxt is not None else i + 1) - (prev if prev is not None else -1)
        pos = i - (prev if prev is not None else -1)
        st = t0 + (t1 - t0) * (pos - 1) / span
        times[i] = (st, st + max(0.12, (t1 - t0) / span))
    return [{"text": t, "start": s, "end": e} for t, (s, e) in zip(tokens, times)]


def _ts(t):
    t = max(0.0, t)
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


_NUMBER_WORDS = {"euros", "euro", "cent", "cents", "mille", "million", "millions"}


def write_ass(words, out_path, cfg, width, height, end_time):
    size = cfg["size"]
    y = int(height * cfg["position_y"])
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Word,{cfg['font_name']},{size},{cfg['color']},&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,{cfg['outline']},{cfg['shadow']},5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for i, w in enumerate(words):
        start = w["start"]
        # le mot reste affiché jusqu'au suivant (pas de trou à l'écran)
        end = words[i + 1]["start"] if i + 1 < len(words) else min(end_time, w["end"] + 0.4)
        if end - start < 0.05:
            end = start + 0.05
        txt = re.sub(r"\b([Pp])lu\b", r"\1lus", w["text"])  # « plu » écrit pour la voix IA, « plus » à l'écran
        txt = txt.upper() if cfg.get("uppercase", True) else txt
        txt = txt.replace("{", "(").replace("}", ")")
        color = ""
        if _norm(w["text"]) in _NUMBER_WORDS or re.search(r"\d", w["text"]):
            color = f"\\c{cfg['highlight_color']}"
        pop = "\\fscx86\\fscy86\\t(0,70,\\fscx100\\fscy100)"
        lines.append(f"Dialogue: 0,{_ts(start)},{_ts(end)},Word,,0,0,0,,"
                     f"{{\\an5\\pos({width // 2},{y}){pop}{color}}}{txt}")
    out_path.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")
    return out_path
