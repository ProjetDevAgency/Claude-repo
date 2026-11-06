"""Mode « respiration » : la voix parle par segments calés sur l'image, et
pendant les pauses on entend le bruit de travail de la vidéo d'origine.

Le script est un fichier YAML (voir scripts/rythme/) :
    segments:
      - t: 0.0          # seconde où le segment commence
        text: "Le hook."
      - t: 17.0
        text: "Une phrase technique, pile quand l'étape apparaît."

Étapes :
1. une seule synthèse vocale pour tout le texte (voix homogène) ;
2. Whisper donne le timing de chaque mot, on découpe la voix par segment ;
3. chaque segment est posé à son instant `t` (décalé si le précédent déborde) ;
4. le son d'origine est gardé, SAUF quand le créateur d'origine parle
   (sa voix est retirée), et il baisse sous notre voix (ducking) ;
5. les sous-titres disparaissent pendant les pauses.
"""
import subprocess

import numpy as np

from . import audio, subtitles
from .audio import SR


def _ramp_envelope(mask_on, ramp_s=0.2):
    """Lisse un masque 0/1 en enveloppe avec rampes (évite les coupures sèches)."""
    k = max(1, int(ramp_s * SR))
    kernel = np.ones(k, np.float32) / k
    return np.clip(np.convolve(mask_on.astype(np.float32), kernel, mode="same"), 0, 1)


def speech_mask(samples16):
    """Repère la parole (n'importe quelle langue) avec le VAD de faster-whisper."""
    from faster_whisper.vad import VadOptions, get_speech_timestamps
    opts = VadOptions(threshold=0.4, min_silence_duration_ms=300, speech_pad_ms=250)
    mask = np.zeros(len(samples16), bool)
    for r in get_speech_timestamps(samples16, opts):
        mask[r["start"]:r["end"]] = True
    return mask


def clean_ambient(source_video, skip_start, duration, n):
    """Bruit de travail de la vidéo, voix du créateur retirée.

    Là où il parlait, on bouche le trou avec du bruit de travail pris dans les
    passages sans parole de toute la vidéo (pas de silence numérique)."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(source_video), "-vn", "-f", "s16le",
                          "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    full = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    talk_full = np.repeat(speech_mask(full[::3].copy()), 3)
    talk_full = np.pad(talk_full, (0, max(0, len(full) - len(talk_full))))[: len(full)]
    i0 = int(skip_start * SR)
    amb = np.pad(full[i0:i0 + n], (0, max(0, n - len(full[i0:i0 + n]))))
    talk = np.pad(talk_full[i0:i0 + n], (0, max(0, n - len(talk_full[i0:i0 + n]))), constant_values=True)
    bed_src = full[~talk_full]
    if len(bed_src) > SR:
        reps = int(np.ceil(n / len(bed_src))) + 1
        bed = np.tile(bed_src, reps)[:n]
        # même niveau que le bruit de travail réel
        real = amb[~talk]
        if len(real) > SR and np.sqrt(np.mean(bed ** 2)) > 1e-6:
            bed *= np.sqrt(np.mean(real ** 2)) / np.sqrt(np.mean(bed ** 2))
    else:
        bed = np.zeros(n, np.float32)
    keep_env = _ramp_envelope(~talk, 0.15)
    print(f"   voix d'origine retirée sur {talk.sum() / SR:.1f}s (remplacée par du bruit de travail)")
    return amb * keep_env + bed * (1 - keep_env), np.ones(n, np.float32)


def place_segments(seg_audio, seg_words, starts, duration, gap=0.15):
    """Pose chaque segment à son instant ; renvoie la piste voix et les mots horodatés."""
    track = np.zeros(int(duration * SR) + SR, np.float32)
    words, cursor = [], 0.0
    for a, ws, t in zip(seg_audio, seg_words, starts):
        st = max(t, cursor + gap if cursor else t)
        i = int(st * SR)
        track[i:i + len(a)] += a[: max(0, len(track) - i)]
        for w in ws:
            words.append({**w, "start": w["start"] + st, "end": w["end"] + st})
        cursor = st + len(a) / SR
    return track[: int(duration * SR)], words, cursor


def build_audio(voice_raw, segments, source_video, skip_start, duration, workdir,
                vcfg, whisper_model="small", ambient_level=0.55, duck=0.12):
    workdir.mkdir(parents=True, exist_ok=True)
    texts = [s["text"].strip() for s in segments]
    full_text = " ".join(texts)

    # 1. voix serrée (silences longs raccourcis, comme le mode normal)
    s = audio.load(voice_raw)
    s = audio.remove_silences(s, vcfg["silence_threshold_db"], vcfg["min_silence"], vcfg["keep_silence"])
    tight = workdir / "voice_tight.wav"
    audio.save(s, tight)

    # 2. timing des mots puis découpe par segment
    words = subtitles.align(full_text, subtitles.transcribe_words(tight, whisper_model))
    counts = [len(t.split()) for t in texts]
    speed = 1.0
    for _ in range(4):
        src = s if speed == 1.0 else audio.load(audio.speed_up(tight, workdir / "voice_fit.wav", speed))
        seg_audio, seg_words, k = [], [], 0
        for c in counts:
            ws = [{**w, "start": w["start"] / speed, "end": w["end"] / speed} for w in words[k:k + c]]
            a0 = max(0.0, ws[0]["start"] - 0.06)
            a1 = (words[k + c]["start"] / speed - 0.02) if k + c < len(words) else len(src) / SR
            a1 = min(a1, ws[-1]["end"] + 0.25)
            seg = src[int(a0 * SR):int(a1 * SR)].copy()
            f = min(len(seg) // 2, int(0.01 * SR))
            if f:
                seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
            seg_audio.append(seg)
            seg_words.append([{**w, "start": w["start"] - a0, "end": w["end"] - a0} for w in ws])
            k += c
        track, placed, end = place_segments(seg_audio, seg_words, [x["t"] for x in segments], duration)
        over = end - (duration - 0.4)
        if over <= 0:
            break
        voiced = sum(len(a) for a in seg_audio) / SR
        speed *= 1 + over / voiced + 0.01
        print(f"   la voix déborde de {over:.1f}s → vitesse x{speed:.3f}")
    print(f"   voix posée : fin à {end:.1f}s, vitesse x{speed:.3f}")

    # 3. son d'origine sans la voix du créateur
    amb, keep_env = clean_ambient(source_video, skip_start, duration, len(track))

    # 4. ducking sous notre voix
    voiced = np.abs(track) > 1e-4
    voiced = np.convolve(voiced.astype(np.float32), np.ones(int(0.25 * SR)), mode="same") > 0
    duck_env = duck + (1 - duck) * _ramp_envelope(~voiced, 0.25)
    amb = amb * keep_env * duck_env

    # niveau : le bruit de travail en pause ≈ ambient_level × niveau de la voix
    v_rms = np.sqrt(np.mean(track[voiced] ** 2)) if voiced.any() else 0.1
    pause = (~voiced) & (keep_env > 0.9)
    a_rms = np.sqrt(np.mean(amb[pause] ** 2)) if pause.sum() > SR else 0
    if a_rms > 1e-5:
        amb *= ambient_level * v_rms / a_rms
    pause_s = pause.sum() / SR
    print(f"   {pause_s:.1f}s de bruit de travail audible pendant les pauses")

    mix = track + amb
    mix_wav = workdir / "mix.wav"
    audio.save(mix / max(1.0, np.max(np.abs(mix)) / 0.95), mix_wav)
    final = audio.normalize(mix_wav, workdir / "voice_final.wav")
    return final, placed, speed
