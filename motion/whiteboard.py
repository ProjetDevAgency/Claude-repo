"""Style « tableau blanc » : fond papier, traits au feutre qui se dessinent, main qui suit le trait.

S'utilise comme engine.Video : chaque scène reçoit (d, img, lt, dur) et dessine avec un Pen,
qui révèle chaque trait ou texte entre t0 et t0 + dur (en secondes depuis le début de la scène).
La main est posée à la fin de l'image sur la pointe du dernier trait en cours.
"""
import math
import random
import re
import subprocess

from PIL import Image, ImageDraw

from engine import FPS, H, W, F, Video, ease, load_config, subtitles, ROOT

PAPER = (250, 250, 246)
INK = (28, 28, 34)
RED = (204, 32, 42)
BLUE = (40, 110, 200)
GREEN = (40, 150, 80)
GREY = (140, 140, 146)
TINT = {RED: (250, 214, 214), BLUE: (210, 226, 248), GREEN: (212, 238, 218), INK: (226, 226, 228),
        GREY: (232, 232, 234)}

_STATE = {"tip": None, "tip_t": -1}
_cache = {}


def mixp(col, a):
    """Couleur à l'opacité a sur le papier."""
    return tuple(int(PAPER[i] + (col[i] - PAPER[i]) * a) for i in range(3))


def _wobble(pts, amp=1.4, step=7):
    key = (tuple((round(x), round(y)) for x, y in pts), amp)
    if key in _cache:
        return _cache[key]
    rnd = random.Random(hash(key))
    out = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        for i in range(n):
            t = i / n
            out.append((x0 + (x1 - x0) * t + rnd.uniform(-amp, amp), y0 + (y1 - y0) * t + rnd.uniform(-amp, amp)))
    out.append(pts[-1])
    _cache[key] = out
    return out


def ellipse_pts(cx, cy, rx, ry, n=48, start=-1.75, turns=1.04):
    rnd = random.Random(hash((round(cx), round(cy), round(rx))))
    return [(cx + rx * math.cos(start + 2 * math.pi * turns * i / n) * rnd.uniform(.97, 1.03),
             cy + ry * math.sin(start + 2 * math.pi * turns * i / n) * rnd.uniform(.97, 1.03)) for i in range(n + 1)]


def _set_tip(lt_key, p):
    _STATE["tip"] = p


class Pen:
    """Dessine des traits qui se révèlent dans le temps. dx, dy décalent le dessin déjà tracé."""

    def __init__(self, d, img, lt, dx=0, dy=0):
        self.d, self.img, self.lt, self.dx, self.dy = d, img, lt, dx, dy

    def k(self, t0, dur):
        if self.lt < t0:
            return 0.0
        return 1.0 if dur <= 0 else min(1.0, (self.lt - t0) / dur)

    def strokes(self, paths, t0, dur, col=INK, w=8, wob=True):
        k = self.k(t0, dur)
        if k <= 0:
            return
        paths = [_wobble(p) if wob else p for p in paths]
        paths = [[(x + self.dx, y + self.dy) for x, y in p] for p in paths]
        lens = [sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(p, p[1:])) for p in paths]
        left = sum(lens) * k
        for p, L in zip(paths, lens):
            if left <= 0:
                break
            if k >= 1 or left >= L - 1e-6:
                if len(p) > 1:
                    self.d.line(p, fill=col, width=w, joint="curve")
                left -= L
                continue
            acc, part = 0, [p[0]]
            for a, b in zip(p, p[1:]):
                s = math.hypot(b[0] - a[0], b[1] - a[1])
                if acc + s >= left:
                    f = (left - acc) / s if s else 0
                    part.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
                    break
                acc += s
                part.append(b)
            if len(part) > 1:
                self.d.line(part, fill=col, width=w, joint="curve")
            _STATE["tip"] = part[-1]
            left = 0

    def line(self, pts, t0, dur, col=INK, w=8):
        self.strokes([pts], t0, dur, col, w)

    def rect(self, x0, y0, x1, y1, t0, dur, col=INK, w=8, fill=None):
        if fill and self.lt >= t0:
            a = min(1, (self.lt - t0) / max(dur, 0.01))
            self.d.rectangle([x0 + self.dx, y0 + self.dy, x1 + self.dx, y1 + self.dy], fill=mixp(fill, a))
        self.strokes([[(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0 - 4)]], t0, dur, col, w)

    def ellipse(self, cx, cy, rx, ry, t0, dur, col=INK, w=8):
        self.strokes([ellipse_pts(cx, cy, rx, ry)], t0, dur, col, w, wob=False)

    def arrow(self, x0, y0, x1, y1, t0, dur, col=INK, w=9):
        a = math.atan2(y1 - y0, x1 - x0)
        head = [(x1 - 40 * math.cos(a - 0.5), y1 - 40 * math.sin(a - 0.5)), (x1, y1),
                (x1 - 40 * math.cos(a + 0.5), y1 - 40 * math.sin(a + 0.5))]
        self.strokes([[(x0, y0), (x1, y1)], head], t0, dur, col, w)

    def underline(self, x0, x1, y, t0, dur, col=RED, w=8):
        self.strokes([[(x0, y), ((x0 + x1) / 2, y + 5), (x1, y - 3)]], t0, dur, col, w)

    def cross(self, x0, y0, x1, y1, t0, dur, col=RED, w=14):
        self.strokes([[(x0, y0), (x1, y1)], [(x1, y0), (x0, y1)]], t0, dur, col, w)

    def write(self, xy, s, size, col=INK, t0=0.0, dur=None, anchor="mm"):
        """Texte écrit de gauche à droite, la main suit la ligne."""
        if dur is None:
            dur = min(1.1, 0.035 * len(s) + 0.15)
        k = self.k(t0, dur)
        if k <= 0:
            return
        f = F(size)
        x, y = xy[0] + self.dx, xy[1] + self.dy
        l, t, r, b = self.d.textbbox((x, y), s, font=f, anchor=anchor)
        if k >= 1:
            self.d.text((x, y), s, font=f, fill=col, anchor=anchor)
            return
        lay = Image.new("RGBA", (int(r - l) + 8, int(b - t) + 8), (0, 0, 0, 0))
        ImageDraw.Draw(lay).text((4 - l + x, 4 - t + y), s, font=f, fill=col + (255,), anchor=anchor)
        cut = int(lay.width * k)
        if cut > 0:
            part = lay.crop((0, 0, cut, lay.height))
            self.img.paste(part, (int(l) - 4, int(t) - 4), part)
        _STATE["tip"] = (l + (r - l) * k, b - (b - t) * 0.25)

    def person(self, cx, cy, s, t0, dur, col=INK, hair=None, mood="neutre", arms="bas", w=9):
        """Personnage en bâtons. hair : 'court' (Julien), 'long' (Claire)."""
        hr = 0.38 * s
        hy = cy - 1.6 * s
        paths = [ellipse_pts(cx, hy, hr, hr * 1.05)]
        if hair == "long":
            paths += [[(cx - hr * 0.9, hy - hr * 0.5), (cx - hr * 1.15, hy + hr * 0.6), (cx - hr * 1.0, hy + hr * 1.5)],
                      [(cx + hr * 0.9, hy - hr * 0.5), (cx + hr * 1.15, hy + hr * 0.6), (cx + hr * 1.0, hy + hr * 1.5)],
                      [(cx - hr * 0.95, hy - hr * 0.4), (cx, hy - hr * 1.15), (cx + hr * 0.95, hy - hr * 0.4)]]
        elif hair == "court":
            paths += [[(cx - hr * 0.8 + i * hr * 0.4, hy - hr * 0.85), (cx - hr * 0.7 + i * hr * 0.4, hy - hr * 1.3)]
                      for i in range(5)]
        paths += [[(cx, cy - 1.2 * s), (cx, cy + 0.2 * s)],
                  [(cx - .45 * s, cy + 1.1 * s), (cx, cy + .2 * s), (cx + .45 * s, cy + 1.1 * s)]]
        if arms == "haut":
            paths.append([(cx - .65 * s, cy - 1.35 * s), (cx, cy - .8 * s), (cx + .65 * s, cy - 1.35 * s)])
        elif arms == "hanches":
            paths.append([(cx - .1 * s, cy - .1 * s), (cx - .5 * s, cy - .45 * s), (cx, cy - .8 * s),
                          (cx + .5 * s, cy - .45 * s), (cx + .1 * s, cy - .1 * s)])
        else:
            paths.append([(cx - .55 * s, cy - .05 * s), (cx, cy - .8 * s), (cx + .55 * s, cy - .05 * s)])
        my = hy + hr * 0.45
        if mood == "rire":
            paths.append([(cx - hr * .45, my - 4), (cx, my + hr * .3), (cx + hr * .45, my - 4)])
        elif mood == "triste":
            paths.append([(cx - hr * .4, my + hr * .2), (cx, my - hr * .05), (cx + hr * .4, my + hr * .2)])
        else:
            paths.append([(cx - hr * .35, my), (cx + hr * .35, my)])
        self.strokes(paths, t0, dur, col, w)
        if self.k(t0, dur) > 0.3:  # les yeux
            ey = hy - hr * 0.15 + (hr * 0.15 if mood == "triste" else 0)
            for ex in (cx - hr * 0.35, cx + hr * 0.35):
                self.d.ellipse([ex - 6 + self.dx, ey - 6 + self.dy, ex + 6 + self.dx, ey + 6 + self.dy], fill=col)

    def bubble(self, x, y, lines, size, t0, col=INK, tail="bas-gauche"):
        w = max(F(size).getlength(l) for l in lines) + 70
        h = len(lines) * (size + 16) + 50
        x0, y0, x1, y1 = x - w / 2, y - h / 2, x + w / 2, y + h / 2
        tx = x0 + w * 0.25 if tail == "bas-gauche" else x1 - w * 0.25
        tdx = -40 if tail == "bas-gauche" else 40
        path = [(tx + 30, y1), (x1 - 20, y1), (x1, y1 - 20), (x1, y0 + 20), (x1 - 20, y0), (x0 + 20, y0), (x0, y0 + 20),
                (x0, y1 - 20), (x0 + 20, y1), (tx - 10, y1), (tx + tdx, y1 + 55), (tx + 30, y1)]
        self.strokes([path], t0, 0.6, col, 7)
        for j, l in enumerate(lines):
            self.write((x, y0 + 25 + (size + 16) * (j + 0.5)), l, size, col, t0 + 0.6 + 0.5 * j)

    def doc(self, x, y, w, h, t0, title=None, tcol=RED, fill=(255, 255, 255)):
        """Feuille de papier avec coin corné."""
        x0, y0, x1, y1 = x - w / 2, y - h / 2, x + w / 2, y + h / 2
        if self.lt >= t0:
            self.d.rectangle([x0 + self.dx, y0 + self.dy, x1 + self.dx, y1 + self.dy], fill=fill)
        self.strokes([[(x0, y0), (x1 - 50, y0), (x1, y0 + 50), (x1, y1), (x0, y1), (x0, y0 - 3)],
                      [(x1 - 50, y0), (x1 - 50, y0 + 50), (x1, y0 + 50)]], t0, 0.7, INK, 7)
        if title:
            self.write((x, y0 + 60), title, 38, tcol, t0 + 0.7)
            self.underline(x - F(38).getlength(title) / 2, x + F(38).getlength(title) / 2, y0 + 95, t0 + 1.4, 0.3, tcol, 5)


def _hand_sprite():
    """Main tenant un feutre ; renvoie (image RGBA, position de la pointe dans l'image)."""
    S = 2
    im = Image.new("RGBA", (330 * S, 380 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    skin, line = (240, 204, 172, 255), INK + (255,)
    a = math.radians(58)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    tip = (20 * S, 20 * S)

    def P(t, s):
        return (tip[0] + (ux * t + px * s) * S, tip[1] + (uy * t + py * s) * S)

    d.polygon([P(0, 0), P(26, -9), P(26, 9)], fill=INK + (255,))
    d.polygon([P(26, -17), P(220, -17), P(220, 17), P(26, 17)], fill=(60, 60, 68, 255), outline=line)
    d.polygon([P(26, -17), P(60, -17), P(60, 17), P(26, 17)], fill=RED + (255,), outline=line)
    cx, cy = P(150, 30)
    d.ellipse([cx - 95 * S, cy - 80 * S, cx + 95 * S, cy + 105 * S], fill=skin, outline=line, width=4 * S)
    for j in range(3):
        fx, fy = P(95 + j * 32, -16)
        d.rounded_rectangle([fx - 26 * S, fy - 17 * S, fx + 26 * S, fy + 17 * S], radius=16 * S, fill=skin,
                            outline=line, width=4 * S)
    tx, ty = P(85, 22)
    d.rounded_rectangle([tx - 34 * S, ty - 15 * S, tx + 34 * S, ty + 15 * S], radius=15 * S, fill=skin,
                        outline=line, width=4 * S)
    im = im.resize((im.width // S, im.height // S), Image.LANCZOS)
    return im, (tip[0] // S, tip[1] // S)


class WhiteboardVideo(Video):
    """Même logique que Video (voix, timing, sous-titres), rendu façon tableau blanc."""

    def __init__(self, *a, hook_lines=None, **k):
        super().__init__(*a, **k)
        self.hook_lines = hook_lines  # [(texte, couleur), …] ; par défaut la 1re phrase du script

    def hook_box(self, img, alpha):
        lines = self.hook_lines
        if not lines:
            f, words, lines, cur = F(66), self.hook_text.upper().split(), [], ""
            for w in words:
                if f.getlength(f"{cur} {w}".strip()) <= 860:
                    cur = f"{cur} {w}".strip()
                else:
                    lines.append((cur, INK))
                    cur = w
            lines.append((cur, INK))
        lh, y0 = 100, 180
        h = lh * len(lines) + 60
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        A = int(255 * alpha)
        ld.rectangle([60, y0, W - 60, y0 + h], fill=PAPER + (A,))
        box = _wobble([(60, y0), (W - 60, y0), (W - 60, y0 + h), (60, y0 + h), (60, y0 - 3)], amp=1.2)
        ld.line(box, fill=INK + (A,), width=8, joint="curve")
        for j, (s, col) in enumerate(lines):
            ld.text((W / 2, y0 + 30 + lh / 2 + j * lh), s, font=F(72), fill=col + (A,), anchor="mm")
        img.paste(lay, (0, 0), lay)

    def header(self, d):
        d.text((50, 80), self.date_label, font=F(30), fill=GREY, anchor="lm")
        f = F(32)
        w = f.getlength(self.topic)
        x1 = W - 50
        d.rounded_rectangle([x1 - w - 40, 52, x1, 108], radius=14, outline=RED, width=5)
        d.text((x1 - w / 2 - 20, 80), self.topic, font=f, fill=RED, anchor="mm")

    def render(self):
        self.scenes.sort(key=lambda s: s[0])
        n_hook = len(self.hook_text.split())
        self.hook_end = max(2.5, self.words[min(n_hook, len(self.words)) - 1]["end"])
        cfg = load_config()
        sub_cfg = dict(cfg["subtitles"], position_y=0.80, size=84)
        ass = subtitles.write_ass(self.words, self.work / "subs.ass", sub_cfg, W, H, self.dur)
        out = ROOT / "output" / f"{self.name}.mp4"
        fonts = str(ROOT / "assets" / "fonts")
        ff = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
             "-r", str(FPS), "-i", "-", "-i", str(self.voice_path), "-af", "apad", "-t", f"{self.dur:.2f}",
             "-vf", f"ass='{ass}':fontsdir='{fonts}'", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
             "-maxrate", "2M", "-bufsize", "4M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
             "-movflags", "+faststart", str(out)], stdin=subprocess.PIPE)
        hand, (hx, hy) = _hand_sprite()
        for i in range(int(self.dur * FPS)):
            t = i / FPS
            img = Image.new("RGB", (W, H), PAPER)
            d = ImageDraw.Draw(img)
            _STATE["tip"] = None
            cur = [(t0, fn) for t0, fn in self.scenes if t0 <= t]
            if cur:
                t0, fn = cur[-1]
                nxt = [s0 for s0, _ in self.scenes if s0 > t0]
                end = nxt[0] if nxt else self.dur
                lt = t - t0
                if t0 == self.scenes[0][0]:
                    lt += self.hook_head_start
                fn(d, img, lt, end - t0)
            elif self.scenes:
                self.scenes[0][1](d, img, self.hook_head_start + t, 1.0)
            self.header(d)
            if t < self.hook_end + 0.4:
                self.hook_box(img, 1.0 if t < self.hook_end else 1 - (t - self.hook_end) / 0.4)
            if _STATE["tip"]:
                x, y = _STATE["tip"]
                img.paste(hand, (int(x - hx), int(y - hy)), hand)
            if t < 0.9:
                z = 1 + 0.10 * (1 - ease(t / 0.9))
                w2, h2 = int(W * z), int(H * z)
                big = img.resize((w2, h2))
                img = big.crop(((w2 - W) // 2, (h2 - H) // 2, (w2 - W) // 2 + W, (h2 - H) // 2 + H))
            ff.stdin.write(img.tobytes())
        ff.stdin.close()
        ff.wait()
        print("✅", out)
        return out
