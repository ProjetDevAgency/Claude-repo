"""Musique de fond générée (aucun droit d'auteur) : nappe douce + petite basse + arpège léger + rythmique feutrée,
en boucle, style « lo-fi explicatif ». Sert de lit sous la voix, comme dans les vidéos de référence."""
import numpy as np

SR = 48000
ACCORDS = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]        # La m, Fa, Do, Sol


def _hz(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def generer(duree, bpm=88, seed=3):
    rng = np.random.default_rng(seed)
    n = int(duree * SR)
    out = np.zeros(n, np.float32)
    temps = 60.0 / bpm
    mesure = 4 * temps
    t_all = np.arange(n) / SR
    for i in range(int(duree / mesure) + 1):
        acc = ACCORDS[i % 4]
        a, b = int(i * mesure * SR), min(n, int((i + 1) * mesure * SR))
        if a >= n:
            break
        t = t_all[a:b] - i * mesure
        env = np.minimum(1, t / 0.4) * np.minimum(1, (mesure - t) / 0.3)
        nappe = sum(np.sin(2 * np.pi * _hz(m) * t) + 0.3 * np.sin(4 * np.pi * _hz(m) * t) for m in acc)
        out[a:b] += 0.05 * env * nappe
        out[a:b] += 0.09 * env * np.sin(2 * np.pi * _hz(acc[0] - 12) * t)          # basse
        for k in range(8):                                                          # arpège
            tk = k * temps / 2
            m = acc[k % 3] + 12
            s0 = a + int(tk * SR)
            l = int(0.35 * SR)
            if s0 + l > n:
                continue
            tt = np.arange(l) / SR
            out[s0:s0 + l] += 0.035 * np.exp(-tt * 9) * np.sin(2 * np.pi * _hz(m) * tt)
        for k in range(4):                                                          # kick feutré + charleston
            s0 = a + int(k * temps * SR)
            l = int(0.18 * SR)
            if s0 + l > n:
                continue
            tt = np.arange(l) / SR
            out[s0:s0 + l] += 0.10 * np.exp(-tt * 22) * np.sin(2 * np.pi * (90 - 200 * tt) * tt)
            h = s0 + int(temps / 2 * SR)
            if h + 2000 < n:
                out[h:h + 2000] += 0.012 * rng.standard_normal(2000) * np.exp(-np.arange(2000) / 400)
    return out / (np.abs(out).max() + 1e-6)


def sous_voix(voix, musique, niveau_db=-32.0, baisse_db=-5.0):
    """Mélange la musique sous la voix, un peu baissée quand la voix parle (ducking)."""
    n = len(voix)
    m = np.resize(musique, n)
    env = np.abs(voix)
    k = int(0.15 * SR)
    env = np.convolve(env, np.ones(k) / k, mode="same")
    parle = np.clip(env / (env.max() * 0.08 + 1e-9), 0, 1)
    gain = 10 ** (niveau_db / 20) * 10 ** (baisse_db * parle / 20)
    return voix + m * gain
