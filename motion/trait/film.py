"""Montage et rendu du style « trait ».

Un film = une voix (avec le temps de chaque mot) + une liste de PLANS.
Un plan démarre sur un mot, dessine sa scène dans le monde (1080x1920) et a sa propre caméra :
    film.plan("pars", scene_fn, cam=[(0, 540, 960, 1.0), (1.2, 540, 700, 1.35)])
La caméra glisse entre ses clés (zoom lent, recadrage), chaque coupe arrive avec un coup de fouet
(flou de mouvement + whoosh), et les éléments d'interface (compteur, sous-titres) sont posés à l'écran.
"""
import subprocess
import sys
import wave
from pathlib import Path

import cairo
import numpy as np

from dessin import FPS, H, W, ease, vignette
import voix

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sfx  # noqa: E402  (bruitages fabriqués par le code, motion/sfx.py)


class Film:
    def __init__(self, voice, words, fin=None):
        self.voice, self.words = voice, words
        self.env = voix.enveloppe(voice, FPS)
        self.dur = fin or (len(voice) / voix.SR + 0.4)
        self.plans, self.hud, self.sons, self.secousses = [], [], [], []

    # ── temps des mots ──
    def t(self, mot, n=0, fin=False):
        """Temps du n-ième mot qui commence par `mot` (insensible à la casse et à la ponctuation)."""
        m = mot.lower()
        hits = [w for w in self.words if w["w"].lower().strip(",.!?…:;«»\"'").startswith(m)]
        if len(hits) <= n:
            raise KeyError(f"mot introuvable : {mot!r} (n={n})")
        return hits[n]["t1" if fin else "t0"]

    def _tt(self, x):
        return self.t(x) if isinstance(x, str) else (self.t(*x) if isinstance(x, tuple) else float(x))

    # ── construction ──
    def plan(self, debut, scene, cam=None, fouet=True, son="whoosh", hud=None):
        """hud(ctx, t, lt) : dessin à l'écran propre à ce plan (notification, carte…)."""
        t0 = 0.0 if debut == 0 else self._tt(debut)
        self.plans.append({"t0": t0, "scene": scene, "cam": cam or [(0, 540, 960, 1.0)], "fouet": fouet,
                           "hud": hud})
        self.plans.sort(key=lambda p: p["t0"])
        if fouet and t0 > 0 and son:
            self.son(t0 - 0.06, son, 0.55)
        return t0

    def ecran(self, fn):
        """fn(ctx, t) dessinée à l'écran (après la caméra) pendant tout le film."""
        self.hud.append(fn)

    def son(self, t, nom, gain=1.0):
        self.sons.append((max(0.0, self._tt(t)), nom, gain))

    def secousse(self, t, force=18):
        self.secousses.append((self._tt(t), force))

    def bouche(self, t, qui):
        """Ouverture de bouche (0-1) si `qui` est en train de parler à l'instant t."""
        for w in self.words:
            if w["who"] == qui and w["t0"] - 0.04 <= t <= w["t1"] + 0.04:
                i = min(int(t * FPS), len(self.env) - 1)
                return float(self.env[i]) * (0.75 + 0.25 * np.sin(t * 38))
        return 0.0

    # ── rendu ──
    def _camera(self, keys, lt):
        if lt <= keys[0][0]:
            return keys[0][1:]
        for (ta, *a), (tb, *b) in zip(keys, keys[1:]):
            if ta <= lt < tb:
                k = ease((lt - ta) / (tb - ta))
                return [x + (y - x) * k for x, y in zip(a, b)]
        return keys[-1][1:]

    def frame(self, t):
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        ctx = cairo.Context(surf)
        ctx.set_source_rgb(0, 0, 0)
        ctx.paint()
        plan = [p for p in self.plans if p["t0"] <= t + 1e-6][-1]
        lt = t - plan["t0"]
        cx, cy, z = self._camera(plan["cam"], lt)
        sx = sy = 0.0
        for ts, f in self.secousses:
            d = t - ts
            if 0 <= d < 0.4:
                a = f * (1 - d / 0.4)
                sx += a * np.sin(d * 90)
                sy += a * np.cos(d * 70)
        ctx.save()
        ctx.translate(W / 2 + sx, H / 2 + sy)
        ctx.scale(z, z)
        ctx.translate(-cx, -cy)
        plan["scene"](ctx, t, lt)
        ctx.restore()
        vignette(ctx, 0.5)
        if plan["hud"]:
            plan["hud"](ctx, t, lt)
        if plan["fouet"] and plan["t0"] > 0 and lt < 0.16:
            surf = self._fouet(surf, 1 - lt / 0.16)
            ctx = cairo.Context(surf)
        for fn in self.hud:
            fn(ctx, t)
        surf.flush()
        return surf

    @staticmethod
    def _fouet(src, k):
        out = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        c = cairo.Context(out)
        c.set_source_surface(src, 0, 0)
        c.paint()
        dx = 150 * k
        for j in range(1, 6):
            c.set_source_surface(src, -dx * j / 5, 0)
            c.paint_with_alpha(0.45 / j)
        return out

    def audio(self, path):
        evts = [(t, n, g) for t, n, g in self.sons]
        mix = sfx.mix(self.voice, evts, sfx_gain=0.5)
        n = int(self.dur * voix.SR)
        mix = np.pad(mix, (0, max(0, n - len(mix))))[:n]
        pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
        with wave.open(str(path), "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(voix.SR)
            f.writeframes(pcm.tobytes())

    def render(self, out, apercu=None):
        out = Path(out)
        out.parent.mkdir(parents=True, exist_ok=True)
        wav = out.with_suffix(".wav")
        self.audio(wav)
        n = int(self.dur * FPS)
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS),
               "-i", "-", "-i", str(wav), "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "192k", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-shortest",
               "-movflags", "+faststart", str(out)]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for f in range(n):
            s = self.frame(f / FPS)
            p.stdin.write(bytes(s.get_data()))
            if f % 150 == 0:
                print(f"  image {f}/{n}", flush=True)
        p.stdin.close()
        p.wait()
        wav.unlink(missing_ok=True)
        return out

    def stills(self, temps, dossier):
        dossier = Path(dossier)
        dossier.mkdir(parents=True, exist_ok=True)
        for t in temps:
            self.frame(t).write_to_png(str(dossier / f"t{t:05.2f}.png"))
