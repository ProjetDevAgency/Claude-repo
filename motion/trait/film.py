"""Montage et rendu du style « trait ».

Un film = une voix (avec le temps de chaque mot) + une liste de PLANS.
Un plan démarre sur un mot, dessine sa scène dans le monde (1080x1920) et a sa propre caméra :
    film.plan("pars", scene_fn, cam=[(0, 540, 960, 1.0), (1.2, 540, 700, 1.35)])
La caméra glisse entre ses clés (zoom lent, recadrage), chaque coupe arrive avec un coup de fouet
(flou de mouvement + whoosh), et les éléments d'interface (compteur, sous-titres) sont posés à l'écran.
"""
import math
import os
import subprocess
import sys
import wave
from pathlib import Path

import cairo
import numpy as np

from dessin import FPS, H, W, ease, vignette
import voix

sys.path.append(str(Path(__file__).resolve().parents[1]))   # après motion/trait : motion/decors.py ne doit pas masquer le nôtre
import sfx  # noqa: E402  (bruitages fabriqués par le code, motion/sfx.py)


# Saturation des couleurs au rendu (client, 21 nov. : « on peut augmenter la saturation ? ») : +35 %.
SATURATION = float(os.environ.get("TRAIT_SATURATION", "1.35"))
# Caméra (client, 21 nov.) : « plans » = coupes nettes + poussée lente + gros plans sur les mots (défaut, style La Ficelle) ;
# « zoom » = zooms / dézooms continus (refusé) ; « libre » = ancien mode glissé.
CAMERA = os.environ.get("TRAIT_CAMERA", "plans")
PUSH = 0.035
# Mesure du 22 nov. : une poussée continue fait glisser toute l'image (30 éléments qui bougent contre 15 chez La Ficelle).
# On la remplace par un petit zoom d'entrée de plan (+2,5 % en 0,6 s), puis plan FIXE.
ZOOM_ENTREE = 0.025
DUREE_ENTREE = 0.6
DUREE_PAN = 0.22

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
    def _camera(self, keys, lt, idx=0):
        if callable(keys):                      # caméra calculée image par image (travelling qui suit l'action)
            return keys(lt)
        if CAMERA == "plans":
            return self._plans_cam(keys, lt)
        if CAMERA == "zoom" and len(keys) > 1:
            return self._zoom(keys, lt, idx)
        if lt <= keys[0][0]:
            return keys[0][1:]
        for (ta, *a), (tb, *b) in zip(keys, keys[1:]):
            if ta <= lt < tb:
                k = ease((lt - ta) / (tb - ta))
                return [x + (y - x) * k for x, y in zip(a, b)]
        return keys[-1][1:]

    @staticmethod
    def _plans_cam(keys, lt):
        """Mode « plans » (client, 21 nov., d'après La Ficelle) : chaque clé est un PLAN. On coupe net d'un plan à
        l'autre (pas de glissement), et pendant le plan la caméra pousse très lentement vers le sujet (+3,5 % par
        seconde, 12 % maximum). Gros plan sur un mot = une clé serrée posée sur ce mot, puis une clé qui revient au
        large. Deux clés presque identiques (moins de 20 % de zoom et 150 px d'écart) ne font pas de coupe."""
        # Une clé peut porter un 5e élément « pan » : au lieu d'une coupe, PANORAMIQUE ÉCLAIR de 0,22 s depuis le plan
        # précédent, avec flou de mouvement (passage d'un personnage à l'autre, comme La Ficelle).
        garde = [keys[0]]
        for k in keys[1:]:
            _, x0, y0, z0 = garde[-1][:4]
            _, x1, y1, z1 = k[:4]
            if len(k) > 4 or abs(z1 - z0) / z0 >= 0.2 or math.hypot(x1 - x0, y1 - y0) * z0 >= 150:
                garde.append(k)
        i = 0
        for j, k in enumerate(garde):
            if lt >= k[0]:
                i = j
        ta, x, y, z = garde[i][:4]
        pousse = 1 + ZOOM_ENTREE * ease(min(1.0, max(0.0, lt - max(0.0, ta)) / DUREE_ENTREE))
        Film._flou_courant = 0.0
        if i > 0 and len(garde[i]) > 4 and lt < ta + DUREE_PAN:
            _, xp, yp, zp = garde[i - 1][:4]
            pp = 1 + ZOOM_ENTREE * ease(min(1.0, max(0.0, ta - max(0.0, garde[i - 1][0])) / DUREE_ENTREE))
            u = (lt - ta) / DUREE_PAN
            k = u * u * (3 - 2 * u)
            Film._flou_courant = (x - xp) * z * 4 * u * (1 - u) / DUREE_PAN * 0.06
            return [xp + (x - xp) * k, yp + (y - yp) * k, zp * pp + (z * pousse - zp * pp) * k]
        return [x, y, z * pousse]

    @staticmethod
    def _zoom(keys, lt, idx):
        """Mode « zoom » (client, 21 nov. : des zooms et des dézooms plutôt que des mouvements au hasard) :
        la caméra ne glisse plus, elle zoome droit vers le sujet du plan (la clé la plus serrée) ou s'en éloigne,
        un plan sur deux. Le sujet reste au même endroit de l'écran pendant tout le zoom."""
        zs = [k[3] for k in keys]
        kmax = keys[zs.index(max(zs))]
        kmin = keys[zs.index(min(zs))]
        px, py = kmax[1], kmax[2]
        zmin, zmax = kmin[3], max(kmax[3], kmin[3] + 0.18)
        sx = W / 2 + zmin * (px - kmin[1])          # position à l'écran du sujet, plan large
        sy = H / 2 + zmin * (py - kmin[2])
        duree = max(1.6, keys[-1][0])
        k = ease(min(1.0, lt / duree))
        if idx % 2:                                 # un plan sur deux : dézoom
            k = 1 - k
        z = zmin + (zmax - zmin) * k
        return [px - (sx - W / 2) / z, py - (sy - H / 2) / z, z]

    def frame(self, t):
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        ctx = cairo.Context(surf)
        ctx.set_source_rgb(0, 0, 0)
        ctx.paint()
        plan = [p for p in self.plans if p["t0"] <= t + 1e-6][-1]
        lt = t - plan["t0"]
        cx, cy, z = self._camera(plan["cam"], lt, self.plans.index(plan))
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
        Film._flou_courant = 0.0
        cx, cy, z = self._camera(plan["cam"], lt, self.plans.index(plan))
        ctx.restore()
        ctx.save()
        ctx.translate(W / 2 + sx, H / 2 + sy)
        ctx.scale(z, z)
        ctx.translate(-cx, -cy)
        plan["scene"](ctx, t, lt)
        ctx.restore()
        if abs(Film._flou_courant) > 1:
            surf = self._flou_h(surf, Film._flou_courant)
            ctx = cairo.Context(surf)
        vignette(ctx, 0.5)
        if plan["hud"]:
            plan["hud"](ctx, t, lt)
        if plan["fouet"] and plan["t0"] > 0 and lt < 0.16 and CAMERA != "plans":
            surf = self._fouet(surf, 1 - lt / 0.16)
            ctx = cairo.Context(surf)
        for fn in self.hud:
            fn(ctx, t)
        surf.flush()
        return surf

    _flou_courant = 0.0

    def combler(self, trous, pas=1.4):
        """Règle des 1 à 2 s : dans chaque passage trop long sans changement [(début, durée)], ajoute des coupes à
        intervalle `pas`, en alternant un gros plan (×1,3 sur le centre du cadrage en cours) et le retour au cadrage
        de départ. Les clés sont ajoutées au plan qui contient l'instant."""
        for a, g in trous:
            k, t = 0, a + pas
            while t < a + g - 0.4:
                plan = [p for p in self.plans if p["t0"] <= t][-1]
                cam = plan["cam"]
                if callable(cam):
                    break
                lt = t - plan["t0"]
                base = [c for c in cam if c[0] <= lt][-1] if any(c[0] <= lt for c in cam) else cam[0]
                _, x, y, z = base[:4]
                nz = z * 1.3 if k % 2 == 0 else z
                cam.append((lt, x, y - (60 if k % 2 == 0 else 0), nz))
                cam.sort(key=lambda c: c[0])
                k += 1
                t += pas
        return self


    @staticmethod
    def _flou_h(src, dx):
        """Flou de mouvement horizontal (panoramique éclair), dx en pixels (signe = sens)."""
        out = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        c = cairo.Context(out)
        n = 8
        for j in range(n):
            c.set_source_surface(src, -dx * (j / (n - 1) - 0.5), 0)
            c.paint_with_alpha(1.0 / (j + 1))
        return out

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
               "-i", "-", "-i", str(wav), "-vf", f"eq=saturation={SATURATION}", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
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
