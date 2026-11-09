"""Bruitages fabriqués par le code (aucun fichier externe, donc aucun problème de droits).

Chaque fonction renvoie un tableau mono float32 à SR Hz. mix() pose les bruitages sur la voix.
"""
import numpy as np

SR = 48000
_rng = np.random.default_rng(7)


def _t(d):
    return np.arange(int(SR * d)) / SR


def _env(n, a=0.005, r=0.2):
    """Enveloppe attaque rapide + décroissance exponentielle."""
    t = np.arange(n) / SR
    e = np.minimum(1.0, t / max(a, 1e-4)) * np.exp(-t / max(r, 1e-4))
    return e.astype(np.float32)


def _lowpass(x, k):
    """Passe-bas simple (moyenne glissante), k échantillons."""
    if k <= 1:
        return x
    return np.convolve(x, np.ones(k) / k, mode="same").astype(np.float32)


def impact():
    """Coup sourd : grosse caisse grave + souffle court."""
    t = _t(0.7)
    f = 120 * np.exp(-t * 9) + 38
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(len(t), 0.002, 0.28)
    noise = _lowpass(_rng.standard_normal(len(t)).astype(np.float32), 6) * _env(len(t), 0.001, 0.05)
    return (0.95 * boom + 0.35 * noise).astype(np.float32)


def whoosh(d=0.45):
    """Souffle qui monte puis retombe (changement de scène)."""
    n = int(SR * d)
    x = _rng.standard_normal(n).astype(np.float32)
    out = np.zeros(n, np.float32)
    seg = n // 12
    for i in range(12):  # filtre qui s'ouvre puis se referme
        k = int(30 - 26 * np.sin(np.pi * i / 11))
        out[i * seg:(i + 1) * seg] = _lowpass(x, k)[i * seg:(i + 1) * seg]
    env = np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    return (out * env * 0.9).astype(np.float32)


def pop():
    """Petit « pop » pour une étiquette importante."""
    t = _t(0.12)
    f = 900 * np.exp(-t * 30) + 300
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(len(t), 0.001, 0.03) * 0.7).astype(np.float32)


def ticks(d=0.6, rate=22):
    """Tic-tic de compteur qui défile."""
    n = int(SR * d)
    out = np.zeros(n, np.float32)
    click = (np.sin(2 * np.pi * 2600 * _t(0.012)) * _env(int(SR * 0.012), 0.0005, 0.003)).astype(np.float32)
    step = int(SR / rate)
    for i in range(0, n - len(click), step):
        out[i:i + len(click)] += click * 0.5
    return out


def notif():
    """Notification de téléphone : deux notes claires."""
    out = np.zeros(int(SR * 0.45), np.float32)
    for k, (f, t0) in enumerate([(1318.5, 0.0), (1760.0, 0.11)]):
        t = _t(0.3)
        tone = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * _env(len(t), 0.003, 0.09)
        i = int(SR * t0)
        out[i:i + len(t)] += tone.astype(np.float32) * 0.45
    return out


def hold_music(d=2.4):
    """Musique d'attente de standard téléphonique : petite mélodie aigrelette, filtrée « téléphone »."""
    notes = [659, 784, 880, 784, 659, 587, 659, 523]
    nd = d / len(notes)
    out = np.zeros(int(SR * d) + 10, np.float32)
    for j, f in enumerate(notes):
        t = _t(nd * 0.95)
        tone = np.sign(np.sin(2 * np.pi * f * t)) * 0.25 + np.sin(2 * np.pi * f * t) * 0.5
        tone = tone * _env(len(t), 0.01, nd * 0.8)
        i = int(SR * j * nd)
        out[i:i + len(t)] += tone.astype(np.float32)
    out = _lowpass(out, 5) - _lowpass(out, 60)  # bande étroite type combiné
    return (out * 0.35).astype(np.float32)


def stamp():
    """Tampon : coup mat + claquement."""
    t = _t(0.35)
    thud = np.sin(2 * np.pi * 90 * t) * _env(len(t), 0.001, 0.07)
    clack = _lowpass(_rng.standard_normal(len(t)).astype(np.float32), 2) * _env(len(t), 0.0005, 0.015)
    return (0.9 * thud + 0.6 * clack).astype(np.float32)


def success():
    """Son de réussite : arpège montant."""
    out = np.zeros(int(SR * 0.9), np.float32)
    for j, f in enumerate([523, 659, 784, 1047]):
        t = _t(0.5)
        tone = (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)) * _env(len(t), 0.004, 0.18)
        i = int(SR * 0.09 * j)
        out[i:i + len(t)] += tone.astype(np.float32) * 0.32
    return out


def fail():
    """Son « raté » : deux notes qui descendent (pour le 0 €, la mauvaise nouvelle)."""
    out = np.zeros(int(SR * 0.7), np.float32)
    for j, f in enumerate([392, 311]):
        t = _t(0.35)
        tone = np.sin(2 * np.pi * f * t) * _env(len(t), 0.005, 0.2)
        out[int(SR * 0.17 * j):int(SR * 0.17 * j) + len(t)] += tone.astype(np.float32) * 0.4
    return out


BANK = {"impact": impact, "whoosh": whoosh, "pop": pop, "ticks": ticks, "notif": notif,
        "attente": hold_music, "tampon": stamp, "succes": success, "rate": fail}


def mix(voice, events, sfx_gain=0.55):
    """voice : tableau mono. events : [(temps s, nom, gain)]. Les bruitages passent sous la voix."""
    out = voice.astype(np.float32).copy()
    for t0, name, g in events:
        s = BANK[name]()
        s = s / (np.max(np.abs(s)) + 1e-9) * 0.8 * g * sfx_gain
        i = int(t0 * SR)
        if i >= len(out):
            continue
        j = min(len(out), i + len(s))
        out[i:j] += s[:j - i]
    peak = np.max(np.abs(out))
    if peak > 0.98:
        out *= 0.98 / peak
    return out
