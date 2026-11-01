"""Traitement de la voix : coupe des silences, puis accélération si nécessaire."""
import subprocess

import numpy as np

from .common import run

SR = 48000


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "s16le", "-ac", "1",
                          "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


def save(samples, path):
    pcm = (np.clip(samples, -1, 1) * 32767).astype(np.int16).tobytes()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1",
                    "-i", "-", str(path)], input=pcm, check=True)


def remove_silences(samples, threshold_db=-38.0, min_silence=0.12, keep=0.06, frame=0.01):
    """Raccourcit chaque silence plus long que `min_silence` à `keep` secondes.

    Début et fin sont coupés presque à zéro. Les silences courts (entre deux
    mots) sont gardés tels quels pour que la voix reste naturelle.
    """
    hop = int(SR * frame)
    n = len(samples) // hop
    if n == 0:
        return samples
    frames = samples[: n * hop].reshape(n, hop)
    rms = np.sqrt((frames ** 2).mean(axis=1) + 1e-12)
    db = 20 * np.log10(rms)
    # seuil relatif au niveau de la voix, pour marcher avec n'importe quel micro
    ref = np.percentile(db, 95)
    silent = db < max(threshold_db, ref - 35)

    keep_frames = np.ones(n, bool)
    i = 0
    while i < n:
        if not silent[i]:
            i += 1
            continue
        j = i
        while j < n and silent[j]:
            j += 1
        length = (j - i) * frame
        is_edge = i == 0 or j == n
        if is_edge:
            margin = int(0.04 / frame)
            if i == 0:
                keep_frames[i: max(i, j - margin)] = False
            else:
                keep_frames[min(j, i + margin): j] = False
        elif length > min_silence:
            half = max(1, int(keep / frame / 2))
            keep_frames[i + half: j - half] = False
        i = j

    # petits fondus aux raccords pour éviter les clics
    out, fade = [], int(0.004 * SR)
    ramp = np.linspace(0, 1, fade, dtype=np.float32)
    k = 0
    while k < n:
        if not keep_frames[k]:
            k += 1
            continue
        m = k
        while m < n and keep_frames[m]:
            m += 1
        seg = frames[k:m].reshape(-1).copy()
        if len(seg) > 2 * fade:
            seg[:fade] *= ramp
            seg[-fade:] *= ramp[::-1]
        out.append(seg)
        k = m
    return np.concatenate(out) if out else samples


def speed_up(in_path, out_path, factor):
    """Accélère sans changer la hauteur de la voix (atempo)."""
    filters, f = [], factor
    while f > 2.0:
        filters.append("atempo=2.0")
        f /= 2.0
    filters.append(f"atempo={f:.5f}")
    run(["ffmpeg", "-v", "error", "-y", "-i", str(in_path), "-af", ",".join(filters),
         "-ar", str(SR), str(out_path)])
    return out_path


def normalize(in_path, out_path):
    run(["ffmpeg", "-v", "error", "-y", "-i", str(in_path), "-af",
         "highpass=f=70,acompressor=threshold=-18dB:ratio=3:attack=5:release=80,"
         "loudnorm=I=-14:TP=-1.5:LRA=7", "-ar", str(SR), str(out_path)])
    return out_path


def process_voice(in_path, workdir, cfg, target_voice, window=(0.0, 1e9)):
    """Silences coupés → vitesse ajustée pour que la voix tombe pile dans la fenêtre.

    `target_voice` : durée visée. `window` : (min, max) acceptables. On n'accélère
    que si la voix dépasse le max, et on ralentit (très peu) seulement si elle est
    sous le min. Retourne (chemin_final, durée, facteur_appliqué).
    """
    workdir.mkdir(parents=True, exist_ok=True)
    s = load(in_path)
    before = len(s) / SR
    s = remove_silences(s, cfg["silence_threshold_db"], cfg["min_silence"], cfg["keep_silence"])
    tight = workdir / "voice_tight.wav"
    save(s, tight)
    dur = len(s) / SR
    print(f"   voix : {before:.1f}s → {dur:.1f}s après suppression des silences")

    factor = 1.0
    lo, hi = window
    if dur > hi or dur < lo:
        factor = dur / target_voice
        max_up, min_down = cfg["max_speedup"], cfg.get("min_speed", 0.94)
        if factor > max_up:
            print(f"   ⚠ il faudrait accélérer x{factor:.2f}, plafonné à x{max_up}. Raccourcis le script.")
            factor = max_up
        if factor < min_down:
            print(f"   ⚠ voix trop courte, ralentie au maximum (x{min_down}). Allonge le script.")
            factor = min_down
        speed_up(tight, workdir / "voice_fit.wav", factor)
        tight = workdir / "voice_fit.wav"
        print(f"   vitesse de la voix x{factor:.3f}")
    final = normalize(tight, workdir / "voice_final.wav")
    return final, len(load(final)) / SR, factor
