"""Style « cartoon plat » : décor de nuit, personnages en aplat, gros chiffres, notifs, fiches de loi.

Une scène est une fonction fn(lt, dur) qui RENVOIE une image RGB 1080x1920.
On dessine le décor et les personnages en x2 (SS) puis on réduit (bords lisses),
et on pose ensuite les éléments graphiques (chiffres, étiquettes, cartes) à la taille finale.
"""
import math
import subprocess

from PIL import Image, ImageDraw, ImageFilter

from engine import FPS, H, W, F, ROOT, Video, load_config, subtitles

SS = 2
WALL = (44, 52, 104)
WALL2 = (38, 45, 92)
FLOOR = (92, 58, 40)
YEL = (255, 204, 40)
RED = (232, 52, 60)
GREEN = (80, 215, 120)
WHITE = (250, 250, 252)
INK = (24, 24, 30)
GREY = (120, 120, 132)
SKIN = (243, 196, 160)
SKIN2 = (205, 150, 112)
TEAL = (38, 160, 150)
SUIT = (32, 32, 42)


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def back(t):
    t = max(0.0, min(1.0, t))
    c = 1.7
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


# ───────────── décors (dessinés une fois, en x2) ─────────────

_rooms = {}


def room(kind="appart"):
    if kind in _rooms:
        return _rooms[kind]
    s = SS
    im = Image.new("RGB", (W * s, H * s), WALL)
    d = ImageDraw.Draw(im)
    for x in range(0, W * s, 70 * s):
        d.rectangle([x, 1050 * s, x + 34 * s, 1500 * s], fill=WALL2)
    d.rectangle([0, 1500 * s, W * s, H * s], fill=FLOOR)
    d.rectangle([0, 1490 * s, W * s, 1510 * s], fill=(70, 44, 30))
    x0, y0, x1, y1 = 620 * s, 380 * s, 980 * s, 900 * s
    d.rectangle([x0 - 18 * s, y0 - 18 * s, x1 + 18 * s, y1 + 18 * s], fill=(210, 220, 240))
    d.rectangle([x0, y0, x1, y1], fill=(60, 80, 150))
    for bx, bh in [(0, 300), (70, 420), (150, 260), (220, 380), (290, 330)]:
        d.rectangle([x0 + bx * s, y1 - bh * s, x0 + (bx + 60) * s, y1], fill=(34, 44, 90))
        for wy in range(int(y1 - bh * s + 20 * s), int(y1 - 10 * s), 40 * s):
            if (wy // s + bx) % 3:
                d.rectangle([x0 + (bx + 12) * s, wy, x0 + (bx + 22) * s, wy + 14 * s], fill=(250, 210, 120))
    d.rectangle([(x0 + x1) // 2 - 8 * s, y0, (x0 + x1) // 2 + 8 * s, y1], fill=(210, 220, 240))
    d.line([300 * s, 0, 300 * s, 260 * s], fill=(20, 20, 30), width=6 * s)
    d.ellipse([270 * s, 250 * s, 330 * s, 310 * s], fill=(255, 220, 140))
    if kind == "appart":
        for bx, by, bw, bh in [(40, 1300, 220, 200), (70, 1120, 170, 180)]:
            d.rectangle([bx * s, by * s, (bx + bw) * s, (by + bh) * s], fill=(196, 150, 96))
            d.rectangle([(bx + bw // 2 - 14) * s, by * s, (bx + bw // 2 + 14) * s, (by + bh) * s], fill=(170, 126, 78))
    if kind == "bureau":
        d.rectangle([0, 1180 * s, W * s, 1230 * s], fill=(120, 80, 56))
        d.rectangle([0, 1230 * s, W * s, 1500 * s], fill=(100, 66, 46))
    _rooms[kind] = im
    return im


# ───────────── personnages ─────────────

def character(d, cx, base, sc=1.0, shirt=TEAL, pants=(40, 60, 120), hair=(60, 36, 26), long_hair=False,
              tie=False, glasses=False, mouth="smile", arm=0.0, phone=False, clipboard=False, brows=None):
    """Personnage en aplat, pieds en (cx, base) en coordonnées finales. arm : bras droit levé (0 à 1)."""
    s = SS * sc

    def X(v):
        return cx * SS + v * s

    def Y(v):
        return base * SS + v * s

    if long_hair:
        d.rounded_rectangle([X(-108), Y(-790), X(108), Y(-540)], radius=int(60 * s), fill=hair)
    d.rounded_rectangle([X(-55), Y(-260), X(-8), Y(-10)], radius=int(18 * s), fill=pants)
    d.rounded_rectangle([X(8), Y(-260), X(55), Y(-10)], radius=int(18 * s), fill=pants)
    d.ellipse([X(-75), Y(-30), X(-5), Y(8)], fill=INK)
    d.ellipse([X(5), Y(-30), X(75), Y(8)], fill=INK)
    d.rounded_rectangle([X(-90), Y(-560), X(90), Y(-240)], radius=int(60 * s), fill=shirt)
    if tie:
        d.polygon([(X(-40), Y(-560)), (X(40), Y(-560)), (X(0), Y(-470))], fill=WHITE)
        d.polygon([(X(-12), Y(-540)), (X(12), Y(-540)), (X(18), Y(-330)), (X(0), Y(-300)), (X(-18), Y(-330))], fill=RED)
    # bras gauche (côté écran gauche) : le long du corps, ou plié avec téléphone / porte-documents
    if phone or clipboard:
        d.line([X(-106), Y(-520), X(-120), Y(-400), X(-40), Y(-420)], fill=shirt, width=int(48 * s), joint="curve")
        d.ellipse([X(-66), Y(-448), X(-14), Y(-396)], fill=SKIN)
        if phone:
            d.rounded_rectangle([X(-62), Y(-520), X(-6), Y(-410)], radius=int(10 * s), fill=INK)
            d.rounded_rectangle([X(-56), Y(-512), X(-12), Y(-420)], radius=int(6 * s), fill=(120, 180, 255))
        if clipboard:
            d.rectangle([X(-90), Y(-520), X(10), Y(-390)], fill=(190, 140, 90))
            d.rectangle([X(-80), Y(-505), X(0), Y(-400)], fill=WHITE)
            for j in range(4):
                d.line([X(-70), Y(-485 + j * 22), X(-10), Y(-485 + j * 22)], fill=GREY, width=int(4 * s))
    else:
        d.rounded_rectangle([X(-130), Y(-540), X(-82), Y(-300)], radius=int(24 * s), fill=shirt)
        d.ellipse([X(-134), Y(-320), X(-80), Y(-266)], fill=SKIN)
    a = math.radians(10 + 120 * arm)
    ex, ey = X(106), Y(-520)
    hx, hy = ex + math.sin(a) * 230 * s, ey + math.cos(a) * 230 * s
    d.line([ex, ey, hx, hy], fill=shirt, width=int(50 * s))
    d.ellipse([hx - 27 * s, hy - 27 * s, hx + 27 * s, hy + 27 * s], fill=SKIN)
    d.rounded_rectangle([X(-22), Y(-600), X(22), Y(-550)], radius=int(10 * s), fill=SKIN2)
    d.ellipse([X(-95), Y(-800), X(95), Y(-590)], fill=SKIN)
    d.ellipse([X(-110), Y(-720), X(-80), Y(-670)], fill=SKIN)
    d.ellipse([X(80), Y(-720), X(110), Y(-670)], fill=SKIN)
    d.chord([X(-100), Y(-830), X(100), Y(-660)], 180, 360, fill=hair)
    d.ellipse([X(-100), Y(-790), X(-40), Y(-700)], fill=hair)
    for ex_ in (-38, 38):
        d.ellipse([X(ex_ - 11), Y(-712), X(ex_ + 11), Y(-686)], fill=INK)
        d.ellipse([X(ex_ - 3), Y(-708), X(ex_ + 4), Y(-700)], fill=WHITE)
        if glasses:
            d.ellipse([X(ex_ - 30), Y(-728), X(ex_ + 30), Y(-670)], outline=INK, width=int(6 * s))
        if brows == "colere":
            d.line([X(ex_ - 22), Y(-748 + (8 if ex_ < 0 else -8) * -1), X(ex_ + 22), Y(-740 - (8 if ex_ < 0 else -8))],
                   fill=INK, width=int(8 * s))
        elif brows == "triste":
            d.line([X(ex_ - 22), Y(-740 - (6 if ex_ < 0 else -6)), X(ex_ + 22), Y(-740 + (6 if ex_ < 0 else -6))],
                   fill=INK, width=int(8 * s))
    if glasses:
        d.line([X(-8), Y(-700), X(8), Y(-700)], fill=INK, width=int(6 * s))
    if mouth == "smile":
        d.arc([X(-32), Y(-680), X(32), Y(-630)], 20, 160, fill=INK, width=int(7 * s))
    elif mouth == "grin":
        d.chord([X(-36), Y(-676), X(36), Y(-620)], 0, 180, fill=INK)
    elif mouth == "o":
        d.ellipse([X(-14), Y(-660), X(14), Y(-626)], fill=INK)
    elif mouth == "sad":
        d.arc([X(-28), Y(-646), X(28), Y(-616)], 200, 340, fill=INK, width=int(7 * s))
    else:
        d.line([X(-24), Y(-646), X(24), Y(-646)], fill=INK, width=int(7 * s))


NADIA = dict(shirt=TEAL, pants=(40, 60, 120), hair=(40, 26, 20), long_hair=True)
PROPRIO = dict(shirt=SUIT, pants=SUIT, hair=(30, 30, 30), tie=True, glasses=True)


def shot(big, z=1.0, fy=0.33):
    """Cadre la toile x2 avec un zoom z (1 = plan large) et la réduit en 1080x1920."""
    w2, h2 = int(W * SS / z), int(H * SS / z)
    x0 = (W * SS - w2) // 2
    y0 = int((H * SS - h2) * fy)
    return big.crop((x0, y0, x0 + w2, y0 + h2)).resize((W, H), Image.LANCZOS)


def dim(img, k, blur=14, dark=0.55):
    """Floute et assombrit le fond (pour poser une carte ou un gros chiffre)."""
    if k <= 0:
        return img
    b = img.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * dark))
    return Image.blend(img, b, min(1.0, k))


# ───────────── éléments graphiques (taille finale) ─────────────

def big_number(img, xy, txt, size, col, sub=None, k=1.0, strike=0.0, rot=0, subcol=WHITE):
    if k <= 0:
        return
    sz = max(10, int(size * (0.5 + 0.5 * back(k))))
    lay = Image.new("RGBA", (W, 460), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.text((W // 2 + 6, 156), txt, font=F(sz), fill=(0, 0, 0, 120), anchor="mm")
    d.text((W // 2, 150), txt, font=F(sz), fill=col + (255,), anchor="mm")
    if strike > 0:
        w = F(sz).getlength(txt)
        d.line([W // 2 - w / 2 - 10, 175, W // 2 - w / 2 - 10 + (w + 20) * min(1, strike), 175 - 55 * min(1, strike)],
               fill=RED + (255,), width=16)
    if sub:
        d.text((W // 2 + 3, 153 + sz * 0.66), sub, font=F(int(size * 0.3)), fill=(0, 0, 0, 120), anchor="mm")
        d.text((W // 2, 150 + sz * 0.66), sub, font=F(int(size * 0.3)), fill=subcol + (255,), anchor="mm")
    if rot:
        lay = lay.rotate(rot, resample=Image.BICUBIC)
    img.paste(lay, (int(xy[0] - W // 2), int(xy[1] - 150)), lay)


def tag(img, x, y, txt, size, bg=YEL, fg=INK, rot=-4, k=1.0):
    if k <= 0:
        return
    f = F(size)
    w = f.getlength(txt)
    pad = size * 0.55
    lay = Image.new("RGBA", (int(w + 2 * pad + 40), int(size * 2 + 40)), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([20, 20, 20 + w + 2 * pad, 20 + size * 1.7], radius=int(size * 0.85), fill=bg + (255,))
    d.text((20 + pad + w / 2, 20 + size * 0.85), txt, font=f, fill=fg + (255,), anchor="mm")
    lay = lay.rotate(rot, expand=True, resample=Image.BICUBIC)
    sc = 0.6 + 0.4 * back(k)
    lay = lay.resize((max(1, int(lay.width * sc)), max(1, int(lay.height * sc))))
    img.paste(lay, (int(x - lay.width / 2), int(y - lay.height / 2)), lay)


def notif(img, x, y, app, title, msg, k, col=(52, 199, 89)):
    """Notification de téléphone qui descend du haut."""
    if k <= 0:
        return
    lay = Image.new("RGBA", (800, 190), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([0, 0, 799, 189], radius=40, fill=(246, 246, 250, 248))
    d.rounded_rectangle([28, 46, 112, 130], radius=24, fill=col + (255,))
    d.text((70, 88), app[0], font=F(44), fill=WHITE + (255,), anchor="mm")
    d.text((140, 62), title, font=F(38), fill=INK + (255,), anchor="lm")
    d.text((140, 126), msg, font=F(32), fill=(100, 100, 110, 255), anchor="lm")
    d.text((770, 62), "maintenant", font=F(24), fill=(150, 150, 160, 255), anchor="rm")
    oy = int((1 - ease(k / 1.0)) * -260)
    img.paste(lay, (int(x - 400), int(y + oy)), lay)


def card(img, cx, cy, title, sub, rows, lt, w=880, rot=2, stamp=None, stamp_t=99.0):
    """Fiche blanche (loi, lettre…). rows : [(gauche, droite, t0, surligné?)]."""
    k = ease(lt / 0.4)
    if k <= 0:
        return
    h = 170 + 85 * len(rows) + 30
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rectangle([0, 0, w - 1, h - 1], fill=(252, 252, 250, 255))
    d.text((40, 62), title, font=F(42), fill=INK + (255,), anchor="lm")
    if sub:
        d.text((40, 108), sub, font=F(26), fill=(120, 120, 130, 255), anchor="lm")
    d.line([40, 145, w - 40, 145], fill=(210, 210, 215, 255), width=3)
    for j, (a, b, t0, hl) in enumerate(rows):
        y = 205 + j * 85
        if hl and lt > t0 + 0.3:
            hk = ease((lt - t0 - 0.3) / 0.4)
            d.rectangle([28, y - 34, 28 + (w - 56) * hk, y + 34], fill=(255, 220, 70, 255))
        if lt > t0:
            d.text((44, y), a, font=F(34), fill=INK + (255,), anchor="lm")
            if b:
                d.text((w - 44, y), b, font=F(34), fill=INK + (255,), anchor="rm")
    if stamp and lt > stamp_t:
        sk = back((lt - stamp_t) / 0.3)
        f = F(int(56 * (1.6 - 0.6 * sk)))
        sl = Image.new("RGBA", (420, 140), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sl)
        sd.rounded_rectangle([6, 6, 413, 133], radius=16, outline=RED + (255,), width=8)
        sd.text((210, 70), stamp, font=f, fill=RED + (255,), anchor="mm")
        sl = sl.rotate(12, expand=True, resample=Image.BICUBIC)
        lay.paste(sl, (w - sl.width - 10, h - sl.height + 10), sl)
    lay = lay.rotate(rot, expand=True, resample=Image.BICUBIC)
    sc = 0.85 + 0.15 * back(lt / 0.4)
    lay = lay.resize((int(lay.width * sc), int(lay.height * sc)))
    img.paste(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)), lay)


def bubble(img, x, y, lines, size, k, tail_x=None, col=WHITE):
    """Bulle de dialogue blanche ; la pointe descend vers tail_x."""
    if k <= 0:
        return
    f = F(size)
    w = max(f.getlength(l) for l in lines) + 80
    h = len(lines) * (size + 16) + 56
    lay = Image.new("RGBA", (int(w) + 20, int(h) + 90), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([10, 10, w + 10, h + 10], radius=40, fill=col + (255,))
    tx = (tail_x - (x - w / 2) + 10) if tail_x is not None else w * 0.3
    tx = max(60, min(w - 40, tx))
    d.polygon([(tx - 30, h + 5), (tx + 30, h + 5), (tx - 10, h + 80)], fill=col + (255,))
    for j, l in enumerate(lines):
        d.text((w / 2 + 10, 10 + 28 + (size + 16) * (j + 0.5)), l, font=f, fill=INK + (255,), anchor="mm")
    sc = 0.5 + 0.5 * back(k)
    lay = lay.resize((max(1, int(lay.width * sc)), max(1, int(lay.height * sc))))
    img.paste(lay, (int(x - lay.width / 2), int(y - lay.height / 2)), lay)


def phone_big(img, cx, cy, lt, clock, lines, k=None):
    """Grand téléphone au centre (écran de verrouillage avec une notif)."""
    k = ease(lt / 0.4) if k is None else k
    if k <= 0:
        return
    pw, ph = 520, 980
    lay = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([0, 0, pw - 1, ph - 1], radius=70, fill=(20, 20, 26, 255))
    d.rounded_rectangle([18, 18, pw - 19, ph - 19], radius=56, fill=(40, 50, 90, 255))
    d.rounded_rectangle([pw / 2 - 70, 34, pw / 2 + 70, 70], radius=18, fill=(20, 20, 26, 255))
    d.text((pw / 2, 200), clock, font=F(110), fill=WHITE + (255,), anchor="mm")
    y = 330
    for app, title, msg, col in lines:
        d.rounded_rectangle([36, y, pw - 36, y + 150], radius=30, fill=(246, 246, 250, 240))
        d.rounded_rectangle([56, y + 36, 126, y + 106], radius=18, fill=col + (255,))
        d.text((91, y + 71), app[0], font=F(36), fill=WHITE + (255,), anchor="mm")
        d.text((146, y + 52), title, font=F(30), fill=INK + (255,), anchor="lm")
        d.text((146, y + 104), msg, font=F(28), fill=(100, 100, 110, 255), anchor="lm")
        y += 175
    sc = 0.8 + 0.2 * back(lt / 0.4) if k < 1 or lt < 0.6 else 1.0
    lay = lay.resize((int(pw * sc), int(ph * sc)))
    img.paste(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)), lay)


def corner_tag(img, txt):
    """Petite étiquette de rubrique en haut à gauche."""
    d = ImageDraw.Draw(img)
    f = F(34)
    w = f.getlength(txt)
    d.rounded_rectangle([40, 50, 40 + w + 44, 112], radius=12, fill=(60, 110, 230))
    d.text((62 + w / 2, 81), txt, font=f, fill=WHITE, anchor="mm")


class CartoonVideo(Video):
    def __init__(self, *a, corner="", **k):
        super().__init__(*a, **k)
        self.corner = corner

    def render(self):
        self.scenes.sort(key=lambda s: s[0])
        cfg = load_config()
        sub_cfg = dict(cfg["subtitles"], position_y=0.80, size=80)
        ass = subtitles.write_ass(self.words, self.work / "subs.ass", sub_cfg, W, H, self.dur)
        out = ROOT / "output" / f"{self.name}.mp4"
        fonts = str(ROOT / "assets" / "fonts")
        ff = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
             "-r", str(FPS), "-i", "-", "-i", str(self.voice_path), "-af", "apad", "-t", f"{self.dur:.2f}",
             "-vf", f"ass='{ass}':fontsdir='{fonts}'", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
             "-maxrate", "2M", "-bufsize", "4M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
             "-movflags", "+faststart", str(out)], stdin=subprocess.PIPE)
        for i in range(int(self.dur * FPS)):
            t = i / FPS
            cur = [(t0, fn) for t0, fn in self.scenes if t0 <= t]
            if cur:
                t0, fn = cur[-1]
                nxt = [s0 for s0, _ in self.scenes if s0 > t0]
                end = nxt[0] if nxt else self.dur
                lt = t - t0
                if t0 == self.scenes[0][0]:
                    lt += self.hook_head_start
                img = fn(lt, end - t0)
            else:
                img = self.scenes[0][1](self.hook_head_start + t, 1.0)
            if self.corner:
                corner_tag(img, self.corner)
            ff.stdin.write(img.tobytes())
        ff.stdin.close()
        ff.wait()
        print("✅", out)
        return out
