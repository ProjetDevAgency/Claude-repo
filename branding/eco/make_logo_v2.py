"""Propositions de nouveau logo « Où va ton argent ? » (800x800, lisible en rond à 48 px).

Usage : python3 branding/eco/make_logo_v2.py   → branding/eco/logo_v2_{a,b,c,d}.png + logo_v2_apercu.png
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "motion"))
import cartoon  # noqa: E402
import rue  # noqa: E402
from cartoon import KEVIN, character  # noqa: E402

OUT = Path(__file__).resolve().parent
S = 800
SS = cartoon.SS
INK = (22, 22, 28)
YEL, RED, GREEN, WHITE = (255, 206, 0), (214, 40, 48), (46, 150, 90), (250, 250, 250)
BILL = (120, 196, 120)


def F(n, anton=False):
    f = "Anton-Regular.ttf" if anton else "Montserrat-ExtraBold.ttf"
    return ImageFont.truetype(str(ROOT / "assets/fonts" / f), n)


def kevin(bg, cx, base, sc, **kw):
    """Kévin dessiné en x2 puis réduit, contour noir."""
    big = Image.new("RGBA", (S * SS, S * SS), (0, 0, 0, 0))
    character(ImageDraw.Draw(big), cx, base, sc=sc, **{**KEVIN, **kw})
    lay = big.resize((S, S), Image.LANCZOS)
    lay = rue.contour(lay, 7)
    bg.alpha_composite(lay)


def billet(sc=1.0, rot=0, color=BILL):
    w, h = int(230 * sc), int(120 * sc)
    im = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([8, 8, w + 8, h + 8], radius=int(12 * sc), fill=color, outline=INK, width=max(4, int(6 * sc)))
    d.ellipse([w / 2 - h * 0.3 + 8, h * 0.2 + 8, w / 2 + h * 0.3 + 8, h * 0.8 + 8], outline=INK, width=max(3, int(5 * sc)))
    d.text((w / 2 + 8, h / 2 + 8), "€", font=F(int(h * 0.45)), fill=INK, anchor="mm")
    return im.rotate(rot, expand=True, resample=Image.BICUBIC)


def ailes(im, sc=1.0):
    """Billet qui s'envole : deux ailes blanches."""
    w, h = im.size
    out = Image.new("RGBA", (w + int(200 * sc), h + int(80 * sc)), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    ox, oy = int(100 * sc), int(70 * sc)
    for sgn in (-1, 1):
        cx = ox + w / 2 + sgn * w * 0.42
        pts = [(cx, oy + h * 0.45)]
        for k in range(4):
            a = math.radians(200 + 35 * k) if sgn < 0 else math.radians(-20 - 35 * k)
            r = (110 - 12 * k) * sc
            pts.append((cx + math.cos(a) * r, oy + h * 0.2 - abs(math.sin(a)) * r * 0.8))
        pts.append((cx + sgn * 10 * sc, oy + h * 0.1))
        d.polygon(pts, fill=WHITE, outline=INK, width=max(4, int(6 * sc)))
    out.alpha_composite(im, (ox, oy))
    return out


def coin(sc=1.0):
    r = int(70 * sc)
    im = Image.new("RGBA", (2 * r + 12, 2 * r + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([6, 6, 2 * r + 6, 2 * r + 6], fill=YEL, outline=INK, width=max(4, int(7 * sc)))
    d.text((r + 6, r + 8), "€", font=F(int(r * 1.1)), fill=INK, anchor="mm")
    return im


def pose(bg, im, cx, cy):
    bg.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def fond(c):
    return Image.new("RGBA", (S, S), c + (255,))


def rayons(img, c, n=16):
    d = ImageDraw.Draw(img)
    for k in range(0, n, 2):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        d.polygon([(S / 2, S / 2), (S / 2 + 900 * math.cos(a0), S / 2 + 900 * math.sin(a0)),
                   (S / 2 + 900 * math.cos(a1), S / 2 + 900 * math.sin(a1))], fill=c)


# A — Kévin choqué, billets ailés qui s'envolent, fond jaune à rayons
a = fond(YEL)
rayons(a, (255, 222, 70))
kevin(a, 400, 1210, 1.3, mouth="o", brows="haut")
pose(a, ailes(billet(0.55, 14), 0.55), 150, 330)
pose(a, ailes(billet(0.5, -16), 0.5), 680, 370)
pose(a, coin(0.5), 130, 520)

# B — Kévin sourire + grosse pièce, fond vert
b = fond((34, 120, 74))
rayons(b, (44, 138, 86))
kevin(b, 360, 1150, 1.2, mouth="grin")
pose(b, coin(1.55), 590, 520)
d = ImageDraw.Draw(b)

# C — typo empilée sur rouge, billet ailé
c = fond(RED)
d = ImageDraw.Draw(c)
for txt, y, n, col in [("OÙ VA", 300, 120, WHITE), ("TON", 420, 120, WHITE), ("ARGENT ?", 545, 140, YEL)]:
    d.text((400, y), txt, font=F(n, anton=True), fill=col, anchor="mm", stroke_width=8, stroke_fill=INK)
pose(c, ailes(billet(0.75, 10), 0.75), 400, 150)

# D — gros billet ailé + « ? », fond jaune (icône pure)
dd = fond(YEL)
rayons(dd, (255, 222, 70))
pose(dd, ailes(billet(1.6, 10), 1.6), 400, 400)
ImageDraw.Draw(dd).text((640, 600), "?", font=F(260, anton=True), fill=RED, anchor="mm", stroke_width=10, stroke_fill=INK)

props = {"a": a, "b": b, "c": c, "d": dd}
for k, im in props.items():
    im.convert("RGB").save(OUT / f"logo_v2_{k}.png")

# aperçu : chaque logo en grand rond + en petit (taille réelle TikTok/YouTube)
ap = Image.new("RGB", (4 * 420, 560), (245, 245, 248))
da = ImageDraw.Draw(ap)
mask = Image.new("L", (S, S), 0)
ImageDraw.Draw(mask).ellipse([0, 0, S, S], fill=255)
for i, (k, im) in enumerate(props.items()):
    rond = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    rond.paste(im, (0, 0), mask)
    ap.paste(rond.resize((380, 380), Image.LANCZOS), (i * 420 + 20, 20), rond.resize((380, 380)).split()[3])
    petit = rond.resize((64, 64), Image.LANCZOS)
    ap.paste(petit, (i * 420 + 178, 420), petit.split()[3])
    da.text((i * 420 + 210, 530), k.upper(), font=F(30), fill=INK, anchor="mm")
ap.save(OUT / "logo_v2_apercu.png")
print("ok")
