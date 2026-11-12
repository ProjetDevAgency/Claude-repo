"""Exporte les dessins du village (style des vidéos) en sprites PNG pour la page du live.

Usage : python3 live/make_sprites.py  → live/public/sprites/*.png + sprites.json (ancrage au sol)
"""
import json
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "motion"))
import facades as fa  # noqa: E402
from cartoon import INK, SS, character  # noqa: E402
from engine import H, W  # noqa: E402
from facades import BASE, R, fenetre, poly  # noqa: E402
from rue import contour  # noqa: E402

OUT = Path(__file__).resolve().parent / "public" / "sprites"
OUT.mkdir(parents=True, exist_ok=True)


# ───────── nouveaux dessins (même style) ─────────
def arbre(d, cx=540):
    R(d, cx - 30, BASE - 260, cx + 30, BASE, (120, 80, 50))
    for (dx, dy, r, c) in ((-90, -330, 120, (80, 165, 70)), (90, -330, 120, (70, 150, 60)),
                           (0, -440, 140, (95, 180, 80))):
        d.ellipse([(cx + dx - r) * SS, (BASE + dy - r) * SS, (cx + dx + r) * SS, (BASE + dy + r) * SS], fill=c)


def cabane(d, cx=540):
    x0, x1 = cx - 230, cx + 230
    R(d, x0, BASE - 300, x1, BASE, (170, 115, 70))
    for k in range(6):
        R(d, x0, BASE - 300 + k * 50, x1, BASE - 296 + k * 50, (140, 92, 55))
    poly(d, [(x0 - 40, BASE - 290), (cx, BASE - 470), (x1 + 40, BASE - 290)], (120, 80, 50))
    R(d, cx - 55, BASE - 170, cx + 55, BASE, (90, 60, 40), 8)
    fenetre(d, x0 + 40, BASE - 240, 90, 80)


def immeuble(d, cx=540):
    x0, x1 = cx - 300, cx + 300
    R(d, x0, BASE - 1050, x1, BASE, (225, 205, 180))
    R(d, x0 - 20, BASE - 1080, x1 + 20, BASE - 1040, (150, 130, 120))
    for row in range(6):
        for col in range(3):
            fenetre(d, x0 + 60 + col * 180, BASE - 990 + row * 150, 110, 100)
    R(d, cx - 80, BASE - 180, cx + 80, BASE, (90, 110, 140), 8)


def maison_coul(col, toit):
    return lambda d, cx=540: fa.maison(d, cx, col=col, toit=toit)


DESSINS = {
    "arbre": arbre,
    "cabane": cabane,
    "maison_jaune": maison_coul((245, 215, 150), (205, 75, 60)),
    "maison_bleue": maison_coul((170, 205, 240), (70, 90, 150)),
    "maison_rose": maison_coul((245, 190, 200), (150, 70, 90)),
    "maison_verte": maison_coul((190, 225, 170), (80, 120, 70)),
    "villa": fa.villa,
    "immeuble": immeuble,
    "chateau": fa.chateau,
    "boulangerie": fa.boulangerie,
    "boxe": fa.boxe,
    "restaurant": fa.restaurant,
    "usine": fa.usine,
    "motocross": fa.motocross,
    "villa_spa": fa.villa_spa,
    "epicerie": fa.epicerie,
}

meta = {}
for nom, fn in DESSINS.items():
    lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    fn(ImageDraw.Draw(lay))
    lay = contour(lay, 10).resize((W, H), Image.LANCZOS)
    x0, y0, x1, y1 = lay.getbbox()
    spr = lay.crop((x0, y0, x1, y1))
    spr = spr.resize((spr.width // 2, spr.height // 2), Image.LANCZOS)   # moitié : assez net pour le live
    spr.save(OUT / f"{nom}.png", optimize=True)
    # ancrage : centre de la façade (x=540) et sol (BASE) en coordonnées du sprite réduit
    meta[nom] = dict(w=spr.width, h=spr.height, ax=(540 - x0) / 2, ay=(BASE - y0) / 2)

# ───────── habitants : 16 looks ─────────
random.seed(7)
CHEMISES = [(46, 150, 90), (230, 120, 160), (60, 120, 220), (240, 160, 40), (200, 60, 60), (150, 90, 200),
            (40, 170, 180), (250, 210, 60)]
CHEVEUX = [(60, 40, 28), (150, 90, 40), (30, 30, 34), (230, 190, 90)]
PANTS = [(40, 50, 90), (50, 50, 60), (70, 90, 130)]
looks = []
for k in range(16):
    look = dict(shirt=CHEMISES[k % 8], hair=CHEVEUX[(k * 3) % 4], pants=PANTS[k % 3],
                long_hair=k % 4 == 1, cap=(28, 28, 34) if k % 5 == 0 else None)
    for bouche, suf in (("smile", ""), ("o", "_parle")):
        big = Image.new("RGBA", (400 * SS, 760 * SS), (0, 0, 0, 0))
        character(ImageDraw.Draw(big), 200, 740, sc=0.82, mouth=bouche, **look)
        spr = contour(big.resize((400, 760), Image.LANCZOS), 5)
        x0, y0, x1, y1 = spr.getbbox()
        spr = spr.crop((x0, y0, x1, y1))
        spr.save(OUT / f"perso_{k:02d}{suf}.png", optimize=True)
        if not suf:
            meta[f"perso_{k:02d}"] = dict(w=spr.width, h=spr.height, ax=200 - x0, ay=740 - y0)

# ───────── icônes des cadeaux du barème (dessinées dans notre style, 160x160) ─────────
def icone(nom, dessin):
    T = 160 * 4
    im = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    dessin(d, T)
    im = contour(im.resize((160, 160), Image.LANCZOS), 4)
    im.save(OUT / f"{nom}.png", optimize=True)


def _coeur(d, cx, cy, r, col):
    d.ellipse([cx - r, cy - r * 0.9, cx + r * 0.1, cy + r * 0.2], fill=col)
    d.ellipse([cx - r * 0.1, cy - r * 0.9, cx + r, cy + r * 0.2], fill=col)
    d.polygon([(cx - r * 0.97, cy - r * 0.2), (cx + r * 0.97, cy - r * 0.2), (cx, cy + r * 1.05)], fill=col)


def rose(d, T):
    d.line([(T * .5, T * .45), (T * .48, T * .95)], fill=(60, 150, 70), width=int(T * .05))
    d.ellipse([T * .22, T * .62, T * .48, T * .74], fill=(80, 170, 80))
    d.ellipse([T * .5, T * .7, T * .76, T * .82], fill=(80, 170, 80))
    for k, (r, c) in enumerate([(.3, (200, 30, 50)), (.22, (225, 45, 65)), (.14, (245, 70, 90)), (.07, (200, 30, 50))]):
        d.ellipse([T * (.5 - r), T * (.32 - r * .9), T * (.5 + r), T * (.32 + r * .9)], fill=c)


def coeur(d, T):
    _coeur(d, T * .5, T * .45, T * .4, (255, 90, 150))
    d.ellipse([T * .26, T * .22, T * .38, T * .32], fill=(255, 190, 215))


def donut(d, T):
    d.ellipse([T * .08, T * .2, T * .92, T * .86], fill=(200, 140, 80))
    d.ellipse([T * .1, T * .16, T * .9, T * .78], fill=(255, 140, 190))
    d.ellipse([T * .38, T * .38, T * .62, T * .56], fill=(200, 140, 80))
    d.ellipse([T * .4, T * .4, T * .6, T * .54], fill=(0, 0, 0, 0))
    for i, c in enumerate([(255, 230, 80), (90, 200, 255), (255, 255, 255), (120, 220, 120)] * 3):
        x, y = T * (.2 + (i * 37 % 60) / 100), T * (.24 + (i * 23 % 40) / 100)
        if abs(x - T * .5) < T * .14 and abs(y - T * .47) < T * .1:
            continue
        d.rounded_rectangle([x, y, x + T * .07, y + T * .025], radius=6, fill=c)


def confettis(d, T):
    d.polygon([(T * .15, T * .9), (T * .45, T * .45), (T * .6, T * .6)], fill=(255, 200, 40))
    d.line([(T * .25, T * .75), (T * .5, T * .52)], fill=(240, 80, 80), width=int(T * .03))
    cols = [(240, 60, 80), (60, 160, 255), (80, 210, 120), (255, 220, 60), (190, 100, 255)]
    for i in range(16):
        x, y = T * (.45 + (i * 29 % 45) / 100), T * (.08 + (i * 17 % 42) / 100)
        d.rounded_rectangle([x, y, x + T * .06, y + T * .03], radius=4, fill=cols[i % 5])


def billets(d, T):
    for i, (dx, dy) in enumerate([(-.06, .1), (0, 0), (.06, -.1)]):
        x0, y0 = T * (.14 + dx), T * (.36 + dy)
        d.rounded_rectangle([x0, y0, x0 + T * .66, y0 + T * .34], radius=14, fill=(110, 190, 110), outline=(40, 110, 50), width=8)
        d.ellipse([x0 + T * .25, y0 + T * .07, x0 + T * .41, y0 + T * .27], outline=(40, 110, 50), width=8)


def baleine(d, T):
    d.ellipse([T * .1, T * .4, T * .8, T * .85], fill=(60, 120, 220))
    d.ellipse([T * .2, T * .62, T * .7, T * .85], fill=(170, 210, 250))
    d.polygon([(T * .72, T * .58), (T * .95, T * .38), (T * .92, T * .6), (T * .97, T * .78)], fill=(60, 120, 220))
    d.ellipse([T * .26, T * .52, T * .32, T * .58], fill=(20, 20, 30))
    for k in range(3):
        d.ellipse([T * (.36 + k * .08), T * (.1 + abs(k - 1) * .06), T * (.44 + k * .08), T * (.2 + abs(k - 1) * .06)], fill=(150, 210, 255))


for nom, f in [("cadeau_rose", rose), ("cadeau_coeur", coeur), ("cadeau_donut", donut), ("cadeau_confettis", confettis),
               ("cadeau_billets", billets), ("cadeau_baleine", baleine)]:
    icone(nom, f)
    meta[nom] = dict(w=160, h=160, ax=80, ay=160)

# ───────── fond : ciel, collines, herbe, trottoir (le décor des vidéos) ─────────
fa.decor().crop((0, 600, W, BASE + 120)).save(OUT / "decor.png", optimize=True)
meta["decor"] = dict(w=W, h=BASE + 120 - 600, sol=BASE - 600)

(OUT / "sprites.json").write_text(json.dumps(meta, indent=1))
print(len(meta), "sprites →", OUT)
