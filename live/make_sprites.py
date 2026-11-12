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

# ───────── fond : ciel, collines, herbe, trottoir (le décor des vidéos) ─────────
fa.decor().crop((0, 600, W, BASE + 120)).save(OUT / "decor.png", optimize=True)
meta["decor"] = dict(w=W, h=BASE + 120 - 600, sol=BASE - 600)

(OUT / "sprites.json").write_text(json.dumps(meta, indent=1))
print(len(meta), "sprites →", OUT)
