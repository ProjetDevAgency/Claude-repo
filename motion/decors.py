"""Bibliothèque de décors « travaillés » (chantier du 20 nov. : dégradés, lumière, ombres, détails, saison).
Chaque décor renvoie une toile x2 (W*SS × H*SS) mise en cache, sol vers y = 1500 (personnages à BASE = 1560).
Style maison : aplats + contours, mais avec profondeur et éclairage. Jamais de logo de marque réelle.
"""
import math
import random

from PIL import Image, ImageDraw, ImageFilter

from cartoon import FA, SS
from engine import H, W

INK = (24, 24, 30)
_C = {}


def _cache(cle, f):
    if cle not in _C:
        _C[cle] = f()
    return _C[cle]


def degrade(im, box, haut, bas):
    """Dégradé vertical dans box (coordonnées x2)."""
    x0, y0, x1, y1 = [int(v) for v in box]
    d = ImageDraw.Draw(im)
    for y in range(y0, y1):
        k = (y - y0) / max(1, y1 - y0)
        d.line([x0, y, x1, y], fill=tuple(int(a + (b - a) * k) for a, b in zip(haut, bas)))


def lumiere(im, sommet, larg_bas, y_bas, col=(255, 230, 170), alpha=70, flou=30):
    """Cône de lumière translucide (lampe) du point sommet vers le bas."""
    s = SS
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x, y = sommet
    d.polygon([(x * s - 30 * s, y * s), (x * s + 30 * s, y * s), ((x + larg_bas / 2) * s, y_bas * s),
               ((x - larg_bas / 2) * s, y_bas * s)], fill=col + (alpha,))
    d.ellipse([(x - larg_bas / 2) * s, (y_bas - 40) * s, (x + larg_bas / 2) * s, (y_bas + 40) * s], fill=col + (alpha,))
    lay = lay.filter(ImageFilter.GaussianBlur(flou * s))
    base = im.convert("RGBA")
    base.alpha_composite(lay)
    return base.convert("RGB")


def ombre_sol(d, x, y, larg, h=26, col=(0, 0, 0)):
    s = SS
    d.ellipse([(x - larg / 2) * s, (y - h / 2) * s, (x + larg / 2) * s, (y + h / 2) * s], fill=col)


def carton(d, x, y, w, h, teinte=(196, 150, 96), etiquette=False):
    """Un carton de colis avec son scotch et son ombre propre (coordonnées finales, coin bas-gauche en (x, y))."""
    s = SS
    sombre = tuple(int(c * 0.8) for c in teinte)
    d.rectangle([x * s, (y - h) * s, (x + w) * s, y * s], fill=teinte, outline=INK, width=3 * s)
    d.rectangle([(x + w * 0.62) * s, (y - h) * s, (x + w) * s, y * s], fill=sombre)
    d.rectangle([(x + w * 0.42) * s, (y - h) * s, (x + w * 0.52) * s, y * s], fill=(222, 190, 130))
    if etiquette:
        d.rectangle([(x + 8) * s, (y - h + 10) * s, (x + w * 0.38) * s, (y - h + 10 + h * 0.3) * s], fill=(250, 250, 250))


# ───────────── l'entrepôt du transporteur ─────────────

def entrepot_bg():
    def f():
        s = SS
        im = Image.new("RGB", (W * s, H * s))
        degrade(im, (0, 0, W * s, 1500 * s), (38, 44, 58), (70, 76, 92))
        d = ImageDraw.Draw(im)
        for x in (60, 560):                                            # deux rayonnages en fond
            d.rectangle([x * s, 520 * s, (x + 460) * s, 1500 * s], fill=(52, 58, 74))
            for y in (760, 1000, 1240, 1480):
                d.rectangle([x * s, (y - 14) * s, (x + 460) * s, y * s], fill=(230, 120, 40))
                xx = x + 14
                rnd = random.Random(x * 7 + y)
                while xx < x + 430:
                    w = rnd.randint(60, 110)
                    h = rnd.randint(70, 170)
                    carton(d, xx, y - 14, w, h, (rnd.randint(170, 205), rnd.randint(125, 155), 90), rnd.random() < 0.4)
                    xx += w + 8
            for xv in (x, x + 452):
                d.rectangle([xv * s, 520 * s, (xv + 10) * s, 1500 * s], fill=(230, 120, 40))
        degrade(im, (0, 1500 * s, W * s, H * s), (110, 112, 118), (70, 72, 78))   # béton
        d = ImageDraw.Draw(im)
        for x in range(-40, W, 120):                                   # bandes de sécurité jaunes et noires
            d.polygon([(x * s, 1500 * s), ((x + 60) * s, 1500 * s), ((x + 30) * s, 1540 * s), ((x - 30) * s, 1540 * s)], fill=(250, 200, 40))
        d.rectangle([0, 1540 * s, W * s, 1548 * s], fill=(40, 40, 46))
        for lx in (270, 790):                                          # lampes industrielles
            d.line([lx * s, 0, lx * s, 300 * s], fill=INK, width=6 * s)
            d.chord([(lx - 90) * s, 280 * s, (lx + 90) * s, 400 * s], 180, 360, fill=(60, 64, 72), outline=INK, width=4 * s)
            d.ellipse([(lx - 40) * s, 320 * s, (lx + 40) * s, 360 * s], fill=(255, 236, 180))
        im = lumiere(im, (270, 340), 620, 1520, alpha=55)
        im = lumiere(im, (790, 340), 620, 1520, alpha=55)
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([340 * s, 120 * s, 740 * s, 220 * s], radius=16 * s, fill=(28, 28, 34), outline=(230, 120, 40), width=5 * s)
        d.text((540 * s, 170 * s), "ENTREPÔT · TRI", font=FA(int(54 * s)), fill=(250, 200, 40), anchor="mm")
        return im
    return _cache("entrepot", f)


def tapis_fg(d, t, y=1430, vitesse=180):
    """Premier plan de l'entrepôt : le tapis roulant avec les colis qui défilent (animé)."""
    s = SS
    d.rectangle([0, y * s, W * s, (y + 70) * s], fill=(44, 46, 54), outline=INK, width=4 * s)
    for k in range(0, W + 120, 60):                                    # rouleaux
        xx = (k + t * vitesse) % (W + 120) - 60
        d.line([xx * s, (y + 8) * s, xx * s, (y + 62) * s], fill=(90, 94, 104), width=6 * s)
    d.rectangle([0, (y + 70) * s, W * s, (y + 130) * s], fill=(230, 120, 40), outline=INK, width=4 * s)
    for k, (w, h) in enumerate([(130, 100), (90, 120), (150, 90), (110, 110), (120, 80)]):
        xx = (k * 260 + t * vitesse) % (W + 260) - 200
        carton(d, xx, y + 4, w, h, etiquette=True)


# ───────────── la rue et le point relais ─────────────

def rue_relais_bg():
    def f():
        s = SS
        im = Image.new("RGB", (W * s, H * s))
        degrade(im, (0, 0, W * s, 900 * s), (54, 72, 140), (240, 150, 110))          # ciel du soir
        d = ImageDraw.Draw(im)
        d.rectangle([80 * s, 260 * s, 1000 * s, 1500 * s], fill=(214, 196, 170), outline=INK, width=5 * s)   # immeuble
        for y in (300, 490):
            for x in (150, 420, 690):
                lit = (x + y) % 3 != 0
                d.rectangle([x * s, y * s, (x + 180) * s, (y + 150) * s], fill=(250, 214, 140) if lit else (70, 80, 110), outline=INK, width=4 * s)
                d.line([(x + 90) * s, y * s, (x + 90) * s, (y + 150) * s], fill=INK, width=3 * s)
                d.rectangle([(x - 10) * s, (y + 150) * s, (x + 190) * s, (y + 166) * s], fill=(190, 172, 150))
        d.rectangle([120 * s, 860 * s, 960 * s, 1500 * s], fill=(40, 90, 70), outline=INK, width=5 * s)     # devanture
        for k in range(8):                                                             # store rayé
            x = 120 + k * 105
            d.polygon([(x * s, 860 * s), ((x + 105) * s, 860 * s), ((x + 115) * s, 960 * s), ((x + 10) * s, 960 * s)],
                      fill=(250, 250, 245) if k % 2 else (40, 140, 100), outline=INK)
        d.rounded_rectangle([300 * s, 680 * s, 780 * s, 760 * s], radius=12 * s, fill=(250, 200, 40), outline=INK, width=4 * s)
        d.text((540 * s, 720 * s), "POINT RELAIS COLIS", font=FA(int(46 * s)), fill=INK, anchor="mm")
        d.rectangle([180 * s, 1010 * s, 560 * s, 1440 * s], fill=(255, 226, 160), outline=INK, width=5 * s)  # vitrine éclairée
        rnd = random.Random(3)
        for y in (1180, 1300, 1420):
            xx = 200
            while xx < 520:
                w = rnd.randint(50, 90)
                carton(d, xx, y, w, rnd.randint(50, 90))
                xx += w + 10
        d.rectangle([640 * s, 1010 * s, 900 * s, 1500 * s], fill=(30, 60, 50), outline=INK, width=5 * s)     # porte
        d.ellipse([860 * s, 1240 * s, 880 * s, 1260 * s], fill=(250, 200, 40))
        degrade(im, (0, 1500 * s, W * s, H * s), (150, 150, 158), (110, 110, 118))  # trottoir
        d = ImageDraw.Draw(im)
        d.rectangle([0, 1500 * s, W * s, 1512 * s], fill=(90, 90, 96))
        d.line([1010 * s, 520 * s, 1010 * s, 1500 * s], fill=INK, width=12 * s)        # lampadaire
        d.ellipse([975 * s, 480 * s, 1045 * s, 540 * s], fill=(255, 236, 170), outline=INK, width=4 * s)
        im = lumiere(im, (1010, 520), 520, 1520, alpha=45)
        im = lumiere(im, (370, 1000), 520, 1540, col=(255, 220, 150), alpha=40)
        return im
    return _cache("rue_relais", f)


# ───────────── le salon de Noël ─────────────

def sapin(d, x, base, t=0.0, h=520):
    """Sapin avec boules et guirlande lumineuse qui clignote (t)."""
    s = SS
    d.rectangle([(x - 30) * s, (base - 70) * s, (x + 30) * s, base * s], fill=(110, 70, 40), outline=INK, width=4 * s)
    for k, (w, y0) in enumerate([(380, base - 70), (300, base - 220), (220, base - 360)]):
        d.polygon([((x - w / 2) * s, y0 * s), ((x + w / 2) * s, y0 * s), (x * s, (y0 - 230) * s)], fill=(30, 120 - 10 * k, 70), outline=INK)
    d.polygon([(x * s, (base - h - 70) * s), ((x + 22) * s, (base - h - 30) * s), ((x - 22) * s, (base - h - 30) * s)], fill=(250, 200, 40), outline=INK)
    rnd = random.Random(x)
    for j in range(16):
        bx = x + rnd.randint(-140, 140)
        by = base - 90 - rnd.randint(0, 480)
        if abs(bx - x) > (base - by) * 0.38:
            continue
        on = int(t * 3 + j) % 2
        col = [(230, 52, 60), (250, 200, 40), (80, 160, 250), (250, 250, 250)][j % 4]
        r = 14 if j % 3 else 9
        d.ellipse([(bx - r) * s, (by - r) * s, (bx + r) * s, (by + r) * s], fill=col if on or j % 3 else (90, 90, 90), outline=INK, width=2 * s)


def salon_noel_bg():
    def f():
        s = SS
        im = Image.new("RGB", (W * s, H * s))
        degrade(im, (0, 0, W * s, 1500 * s), (120, 72, 60), (170, 108, 84))          # murs chauds
        d = ImageDraw.Draw(im)
        for x in range(0, W, 90):                                                    # papier peint rayé
            d.rectangle([x * s, 0, (x + 30) * s, 1500 * s], fill=(130, 80, 66))
        d.rectangle([600 * s, 360 * s, 980 * s, 900 * s], fill=(236, 230, 220), outline=INK, width=5 * s)   # fenêtre de nuit
        degrade(im, (618 * s, 378 * s, 962 * s, 882 * s), (24, 30, 70), (60, 70, 130))
        d = ImageDraw.Draw(im)
        rnd = random.Random(5)
        for _ in range(40):                                                            # neige
            x, y = rnd.randint(620, 960), rnd.randint(380, 880)
            d.ellipse([(x - 4) * s, (y - 4) * s, (x + 4) * s, (y + 4) * s], fill=(250, 250, 255))
        d.line([790 * s, 360 * s, 790 * s, 900 * s], fill=(236, 230, 220), width=12 * s)
        for k in range(12):                                                            # guirlande au plafond
            x = 40 + k * 90
            d.arc([x * s, 120 * s, (x + 90) * s, 200 * s], 0, 180, fill=(40, 120, 60), width=8 * s)
            d.ellipse([(x + 38) * s, 190 * s, (x + 52) * s, 204 * s], fill=[(230, 52, 60), (250, 200, 40), (80, 160, 250)][k % 3])
        degrade(im, (0, 1500 * s, W * s, H * s), (120, 80, 56), (90, 58, 40))          # parquet
        d = ImageDraw.Draw(im)
        for y in range(1530, H, 60):
            d.line([0, y * s, W * s, y * s], fill=(84, 54, 36), width=3 * s)
        d.ellipse([140 * s, 1540 * s, 940 * s, 1680 * s], fill=(160, 40, 50))          # tapis
        d.rounded_rectangle([60 * s, 1180 * s, 560 * s, 1480 * s], radius=50 * s, fill=(60, 90, 140), outline=INK, width=4 * s)  # canapé
        d.rounded_rectangle([60 * s, 1080 * s, 560 * s, 1260 * s], radius=50 * s, fill=(70, 104, 160), outline=INK, width=4 * s)
        d.line([200 * s, 600 * s, 200 * s, 1500 * s], fill=INK, width=8 * s)          # lampe sur pied
        d.polygon([(140 * s, 600 * s), (260 * s, 600 * s), (230 * s, 500 * s), (170 * s, 500 * s)], fill=(250, 220, 160), outline=INK)
        im = lumiere(im, (200, 600), 700, 1540, alpha=50)
        return im
    return _cache("salon_noel", f)


def sapin_fg(d, t):
    """Le sapin au premier plan à droite, guirlande qui clignote."""
    sapin(d, 900, 1500, t)


__all__ = ["entrepot_bg", "tapis_fg", "rue_relais_bg", "salon_noel_bg", "sapin_fg", "carton", "degrade", "lumiere"]
