"""Façades vues de face (2D à contours noirs) pour présenter chaque maison derrière son habitant.

Chaque façade est dessinée en x2 sur un calque transparent, centrée en (540, BASE) où BASE est le sol.
"""
import math

from PIL import Image, ImageDraw

from cartoon import FA, INK, SS, WHITE, YEL
from engine import H, W
from rue import contour, nuage

BASE = 1380          # niveau du trottoir
GOLD = (235, 185, 40)
_cache = {}


def R(d, x0, y0, x1, y1, col, r=0):
    if r:
        d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], radius=int(r * SS), fill=col)
    else:
        d.rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], fill=col)


def poly(d, pts, col):
    d.polygon([(x * SS, y * SS) for x, y in pts], fill=col)


def fenetre(d, x, y, w, h, croix=True):
    R(d, x - 6, y - 6, x + w + 6, y + h + 6, (250, 250, 250))
    R(d, x, y, x + w, y + h, (150, 205, 245))
    if croix:
        R(d, x + w / 2 - 3, y, x + w / 2 + 3, y + h, (250, 250, 250))
        R(d, x, y + h / 2 - 3, x + w, y + h / 2 + 3, (250, 250, 250))


def drapeau(d, x, y, kind):
    R(d, x - 5, y, x + 5, y + 260, (60, 60, 70))
    R(d, x + 5, y, x + 175, y + 110, (200, 30, 40))
    if kind == "maroc":
        d.text(((x + 90) * SS, (y + 55) * SS), "★", font=FA(int(80 * SS)), fill=(20, 120, 50), anchor="mm")
    else:
        d.ellipse([(x + 55) * SS, (y + 20) * SS, (x + 125) * SS, (y + 90) * SS], fill=WHITE)
        d.ellipse([(x + 68) * SS, (y + 33) * SS, (x + 112) * SS, (y + 77) * SS], fill=(200, 30, 40))


def maison(d, cx=540, w=620, col=(245, 215, 150), toit=(205, 75, 60), flag=None):
    h = 380
    x0, x1, y1 = cx - w / 2, cx + w / 2, BASE
    y0 = y1 - h
    R(d, x1 - 150, y0 - 220, x1 - 90, y0 - 60, (150, 90, 70))                     # cheminée
    poly(d, [(x0 - 50, y0 + 10), (cx, y0 - 230), (x1 + 50, y0 + 10)], toit)        # toit
    R(d, x0, y0, x1, y1, col)                                                     # mur
    R(d, cx - 70, y1 - 210, cx + 70, y1, (120, 80, 50), 10)                        # porte
    d.ellipse([(cx + 40) * SS, (y1 - 110) * SS, (cx + 54) * SS, (y1 - 96) * SS], fill=YEL)
    fenetre(d, x0 + 50, y0 + 70, 120, 110)
    fenetre(d, x1 - 170, y0 + 70, 120, 110)
    R(d, x0 + 40, y0 + 190, x0 + 180, y0 + 215, (90, 160, 70), 8)                  # jardinières
    R(d, x1 - 180, y0 + 190, x1 - 40, y0 + 215, (90, 160, 70), 8)
    for k in range(5):
        for xx in (x0 + 55 + k * 28, x1 - 165 + k * 28):
            d.ellipse([xx * SS, (y0 + 178) * SS, (xx + 14) * SS, (y0 + 192) * SS],
                      fill=[(250, 90, 120), (255, 220, 60), (250, 250, 250)][k % 3])
    if flag:
        drapeau(d, x1 - 40, y0 - 380, flag)


def villa(d, cx=540, toit=(250, 250, 250)):
    x0, x1, y1 = cx - 440, cx + 440, BASE
    R(d, x0, y1 - 240, x1, y1, (250, 250, 245))                                   # rez-de-chaussée
    R(d, x0 + 80, y1 - 460, x1 - 80, y1 - 240, (242, 242, 236))                   # étage
    R(d, x0 + 60, y1 - 485, x1 - 60, y1 - 455, toit)                               # toit-terrasse
    R(d, x0 - 20, y1 - 265, x1 + 20, y1 - 240, toit)
    for k in range(4):
        R(d, x0 + 110 + k * 180, y1 - 430, x0 + 230 + k * 180, y1 - 280, (140, 200, 245))
    for k in range(3):
        R(d, x0 + 60 + k * 270, y1 - 210, x0 + 260 + k * 270, y1 - 30, (140, 200, 245))
    R(d, x0 - 80, y1 - 10, x1 + 80, y1 + 40, (245, 235, 210))                      # plage
    poly(d, [(x0 + 40, y1 + 40), (x1 - 40, y1 + 40), (x1 + 60, y1 + 170), (x0 - 60, y1 + 170)], (250, 250, 250))
    poly(d, [(x0 + 70, y1 + 55), (x1 - 70, y1 + 55), (x1 + 30, y1 + 158), (x0 - 30, y1 + 158)], (60, 180, 245))
    for xx in (x0 - 40, x1 + 40):                                                  # palmiers
        R(d, xx - 10, y1 - 520, xx + 10, y1, (130, 90, 50))
        for a in range(0, 360, 45):
            r = math.radians(a)
            d.line([xx * SS, (y1 - 520) * SS, (xx + 130 * math.cos(r)) * SS, (y1 - 520 + 60 * math.sin(r)) * SS],
                   fill=(50, 160, 70), width=int(22 * SS))


def ps5(d, cx=540):
    y1 = BASE
    R(d, cx - 260, y1 - 820, cx - 40, y1, (248, 248, 252), 120)
    R(d, cx + 40, y1 - 820, cx + 260, y1, (248, 248, 252), 120)
    R(d, cx - 50, y1 - 790, cx + 50, y1, (25, 25, 32), 30)
    R(d, cx - 8, y1 - 700, cx + 8, y1 - 120, (80, 170, 255), 8)
    R(d, cx - 140, y1 - 230, cx - 60, y1, (120, 80, 50), 10)                       # porte
    fenetre(d, cx + 100, y1 - 560, 100, 100, False)


def voiture(d, cx=540):
    y1 = BASE - 40
    R(d, cx - 470, y1 - 260, cx + 470, y1, (220, 35, 45), 70)
    poly(d, [(cx - 300, y1 - 250), (cx - 190, y1 - 470), (cx + 210, y1 - 470), (cx + 330, y1 - 250)], (220, 35, 45))
    poly(d, [(cx - 260, y1 - 260), (cx - 170, y1 - 440), (cx - 10, y1 - 440), (cx - 10, y1 - 260)], (170, 215, 245))
    poly(d, [(cx + 10, y1 - 260), (cx + 10, y1 - 440), (cx + 190, y1 - 440), (cx + 290, y1 - 260)], (170, 215, 245))
    R(d, cx - 60, y1 - 230, cx + 60, y1 - 30, (180, 25, 35), 14)                    # porte d'entrée
    for xx in (cx - 300, cx + 300):
        d.ellipse([(xx - 110) * SS, (y1 - 70) * SS, (xx + 110) * SS, (y1 + 150) * SS], fill=(25, 25, 30))
        d.ellipse([(xx - 50) * SS, (y1 - 10) * SS, (xx + 50) * SS, (y1 + 90) * SS], fill=(190, 190, 200))
    R(d, cx + 430, y1 - 200, cx + 470, y1 - 140, (255, 230, 120), 10)


def grotte(d, cx=540):
    y1 = BASE
    for dx, dy, r, col in ((-280, -150, 220, (120, 115, 110)), (260, -160, 230, (128, 122, 116)),
                           (0, -330, 280, (140, 134, 127)), (-130, -520, 170, (150, 144, 136)),
                           (150, -500, 160, (145, 139, 131))):
        d.ellipse([(cx + dx - r) * SS, (y1 + dy - r * 0.85) * SS, (cx + dx + r) * SS, (y1 + dy + r * 0.85) * SS], fill=col)
    d.chord([(cx - 170) * SS, (y1 - 420) * SS, (cx + 170) * SS, (y1 + 80) * SS], 180, 360, fill=(30, 26, 24))
    R(d, cx - 170, y1 - 170, cx + 170, y1, (30, 26, 24))
    fx = cx + 260
    poly(d, [(fx - 60, y1 + 20), (fx, y1 - 140), (fx + 60, y1 + 20)], (250, 140, 30))
    poly(d, [(fx - 30, y1 + 20), (fx, y1 - 70), (fx + 30, y1 + 20)], (255, 220, 60))


def epicerie(d, cx=540):
    x0, x1, y1 = cx - 400, cx + 400, BASE
    R(d, x0, y1 - 520, x1, y1, (250, 245, 230))
    R(d, x0 + 60, y1 - 500, x1 - 60, y1 - 400, (60, 60, 70), 14)
    d.text((cx * SS, (y1 - 450) * SS), "ÉPICERIE", font=FA(int(76 * SS)), fill=WHITE, anchor="mm")
    for k in range(10):                                                            # store rayé
        poly(d, [(x0 + k * 80, y1 - 390), (x0 + (k + 1) * 80, y1 - 390), (x0 + (k + 1) * 80 + 10, y1 - 300),
                 (x0 + k * 80 + 10, y1 - 300)], (220, 50, 60) if k % 2 == 0 else WHITE)
    R(d, x0 + 60, y1 - 280, cx - 40, y1 - 40, (150, 205, 245))
    for k in range(6):                                                             # fruits en vitrine
        d.ellipse([(x0 + 90 + k * 50) * SS, (y1 - 110) * SS, (x0 + 130 + k * 50) * SS, (y1 - 70) * SS],
                  fill=[(240, 80, 60), (255, 200, 40), (120, 200, 80)][k % 3])
    R(d, cx + 60, y1 - 280, cx + 220, y1, (120, 80, 50), 10)
    R(d, cx + 250, y1 - 160, cx + 330, y1 - 120, (200, 30, 40), 6)
    d.text(((cx + 290) * SS, (y1 - 140) * SS), "OUVERT", font=FA(int(20 * SS)), fill=WHITE, anchor="mm")


def decor():
    """Ciel, nuages, collines, herbe et trottoir (sans route) : le fond des plans « façade »."""
    if "decor" in _cache:
        return _cache["decor"]
    big = Image.new("RGBA", (W * SS, H * SS), (200, 230, 250, 255))
    d = ImageDraw.Draw(big)
    for y in range(0, 1100 * SS, 8):
        k = y / (1100 * SS)
        d.rectangle([0, y, W * SS, y + 8], fill=(int(120 + 80 * k), int(190 + 40 * k), int(240 + 10 * k), 255))
    nu = Image.new("RGBA", big.size, (0, 0, 0, 0))
    dn = ImageDraw.Draw(nu)
    for (x, y, s) in ((170, 300, 0.9), (650, 220, 1.1), (950, 380, 0.8)):
        nuage(dn, x, y, s)
    big.alpha_composite(contour(nu, 6))
    co = Image.new("RGBA", big.size, (0, 0, 0, 0))
    dc = ImageDraw.Draw(co)
    dc.ellipse([-300 * SS, 820 * SS, 650 * SS, 1500 * SS], fill=(130, 195, 105, 255))
    dc.ellipse([400 * SS, 860 * SS, 1450 * SS, 1500 * SS], fill=(120, 185, 95, 255))
    big.alpha_composite(contour(co, 6))
    d = ImageDraw.Draw(big)
    d.rectangle([0, 1080 * SS, W * SS, H * SS], fill=(110, 190, 80, 255))
    d.rectangle([0, (BASE - 4) * SS, W * SS, (BASE + 70) * SS], fill=(200, 200, 205, 255))
    d.rectangle([0, (BASE + 70) * SS, W * SS, (BASE + 86) * SS], fill=(160, 160, 168, 255))
    img = big.convert("RGB").resize((W, H), Image.LANCZOS)
    _cache["decor"] = img
    return img


DESSINS = {"maison": maison, "villa": villa, "ps5": ps5, "voiture": voiture, "grotte": grotte, "epicerie": epicerie}


def calque(kind, **kw):
    """Façade prête à coller (RGBA 1080x1920, contour noir), mise en cache."""
    key = (kind, tuple(sorted(kw.items())))
    if key not in _cache:
        lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
        DESSINS[kind](ImageDraw.Draw(lay), **kw)
        _cache[key] = contour(lay, 10).resize((W, H), Image.LANCZOS)
    return _cache[key]


def poser(img, lay, k=1.0, cx=540):
    """Colle une façade avec un effet « pop » (k de 0 à ~1.1), ancrée au sol."""
    if k <= 0:
        return
    if abs(k - 1) < 1e-3:
        img.paste(lay, (0, 0), lay)
        return
    w, h = int(W * k), int(H * k)
    sm = lay.resize((max(1, w), max(1, h)), Image.BILINEAR)
    img.paste(sm, (int(cx - cx * k), int(BASE - BASE * k)), sm)


# ───────────── façades du jour 3 ─────────────

def boutique(d, cx=540, nom="BOUTIQUE", mur=(250, 240, 220), enseigne=(60, 60, 70), store=(220, 50, 60), vitrine=None):
    """Commerce générique : enseigne, store rayé, vitrine avec objets, porte."""
    x0, x1, y1 = cx - 400, cx + 400, BASE
    R(d, x0, y1 - 540, x1, y1, mur)
    R(d, x0 + 50, y1 - 520, x1 - 50, y1 - 410, enseigne, 14)
    f = FA(int(min(80, 1400 / max(6, len(nom))) * SS))
    d.text((cx * SS, (y1 - 465) * SS), nom, font=f, fill=WHITE, anchor="mm")
    for k in range(10):
        poly(d, [(x0 + k * 80, y1 - 395), (x0 + (k + 1) * 80, y1 - 395), (x0 + (k + 1) * 80 + 10, y1 - 305),
                 (x0 + k * 80 + 10, y1 - 305)], store if k % 2 == 0 else WHITE)
    R(d, x0 + 60, y1 - 285, cx - 40, y1 - 40, (150, 205, 245))
    if vitrine:
        vitrine(d, x0 + 60, y1 - 285, cx - 40, y1 - 40)
    R(d, cx + 60, y1 - 285, cx + 220, y1, (120, 80, 50), 10)


def vit_pains(d, x0, y0, x1, y1):
    for k in range(5):
        R(d, x0 + 20 + k * 70, y1 - 70, x0 + 80 + k * 70, y1 - 40, (215, 160, 80), 14)
    for k in range(4):
        d.ellipse([(x0 + 30 + k * 85) * SS, (y1 - 150) * SS, (x0 + 100 + k * 85) * SS, (y1 - 95) * SS], fill=(200, 140, 60))


def vit_boxe(d, x0, y0, x1, y1):
    R(d, x0 + 150, y0 + 30, x0 + 175, y1 - 20, (60, 60, 70))
    R(d, x0 + 110, y0 + 70, x0 + 215, y1 - 60, (200, 30, 40), 40)
    for k, xx in enumerate((x0 + 40, x0 + 280)):
        d.ellipse([xx * SS, (y1 - 110) * SS, (xx + 70) * SS, (y1 - 40) * SS], fill=(210, 30, 40))


def vit_resto(d, x0, y0, x1, y1):
    for k in range(3):
        xx = x0 + 40 + k * 120
        R(d, xx, y1 - 80, xx + 90, y1 - 70, (120, 80, 50))
        d.ellipse([(xx + 15) * SS, (y1 - 120) * SS, (xx + 75) * SS, (y1 - 80) * SS], fill=WHITE)
        d.ellipse([(xx + 30) * SS, (y1 - 112) * SS, (xx + 60) * SS, (y1 - 88) * SS], fill=(230, 120, 60))


def vit_moto(d, x0, y0, x1, y1):
    for xx in (x0 + 90, x0 + 260):
        d.ellipse([(xx - 50) * SS, (y1 - 110) * SS, (xx + 10) * SS, (y1 - 50) * SS], outline=INK, width=int(12 * SS))
        d.ellipse([(xx + 50) * SS, (y1 - 110) * SS, (xx + 110) * SS, (y1 - 50) * SS], outline=INK, width=int(12 * SS))
        poly(d, [(xx - 20, y1 - 80), (xx + 30, y1 - 150), (xx + 80, y1 - 80)], (240, 120, 30))


def vit_elec(d, x0, y0, x1, y1):
    for k in range(3):
        xx = x0 + 30 + k * 125
        R(d, xx, y1 - 170, xx + 100, y1 - 60, (30, 30, 40), 10)
        R(d, xx + 8, y1 - 162, xx + 92, y1 - 72, (80, 180, 250), 6)


def chateau(d, cx=540):
    y1 = BASE
    pierre = (190, 185, 175)
    R(d, cx - 330, y1 - 520, cx + 330, y1, pierre)
    for tx in (cx - 430, cx + 330):
        R(d, tx, y1 - 760, tx + 100, y1, (175, 170, 160))
        poly(d, [(tx - 20, y1 - 760), (tx + 50, y1 - 920), (tx + 120, y1 - 760)], (60, 70, 120))
    for k in range(7):
        R(d, cx - 330 + k * 100, y1 - 570, cx - 270 + k * 100, y1 - 520, pierre)
    d.chord([(cx - 110) * SS, (y1 - 360) * SS, (cx + 110) * SS, (y1 - 140) * SS], 180, 360, fill=(90, 60, 40))
    R(d, cx - 110, y1 - 250, cx + 110, y1, (90, 60, 40))
    for xx in (cx - 250, cx + 170):
        R(d, xx, y1 - 420, xx + 80, y1 - 320, (40, 40, 50), 30)
    R(d, cx - 5, y1 - 700, cx + 5, y1 - 520, INK)
    R(d, cx + 5, y1 - 700, cx + 130, y1 - 630, (200, 30, 40))


def villa_spa(d, cx=540):
    villa(d, cx, toit=(250, 250, 250))
    R(d, cx - 400, BASE - 560, cx - 160, BASE - 500, (60, 180, 245), 14)
    d.text(((cx - 280) * SS, (BASE - 530) * SS), "SPA", font=FA(int(40 * SS)), fill=WHITE, anchor="mm")
    R(d, cx + 160, BASE - 560, cx + 400, BASE - 500, (240, 120, 30), 14)
    d.text(((cx + 280) * SS, (BASE - 530) * SS), "GYM", font=FA(int(40 * SS)), fill=WHITE, anchor="mm")
    d.text((cx * SS, (BASE - 210) * SS), "8 CHAMBRES", font=FA(int(34 * SS)), fill=INK, anchor="mm")


def boulangerie(d, cx=540):
    boutique(d, cx, "BOULANGERIE", mur=(250, 235, 200), enseigne=(150, 90, 40), store=(200, 140, 60), vitrine=vit_pains)


def boxe(d, cx=540):
    boutique(d, cx, "CLUB DE BOXE", mur=(235, 235, 240), enseigne=(30, 30, 36), store=(200, 30, 40), vitrine=vit_boxe)


def restaurant(d, cx=540):
    boutique(d, cx, "CHEZ AL", mur=(250, 240, 225), enseigne=(30, 90, 60), store=(40, 140, 80), vitrine=vit_resto)


def motocross(d, cx=540):
    boutique(d, cx, "MOTOCROSS 91", mur=(235, 235, 240), enseigne=(240, 120, 30), store=(30, 30, 36), vitrine=vit_moto)


def usine(d, cx=540):
    y1 = BASE
    R(d, cx - 450, y1 - 470, cx + 450, y1, (200, 205, 215))
    for k in range(4):
        poly(d, [(cx - 450 + k * 225, y1 - 470), (cx - 450 + k * 225 + 112, y1 - 560), (cx - 450 + (k + 1) * 225, y1 - 470)],
             (160, 165, 180))
    R(d, cx + 260, y1 - 780, cx + 340, y1 - 470, (150, 150, 160))
    R(d, cx - 380, y1 - 440, cx + 380, y1 - 340, (40, 110, 220), 14)
    d.text((cx * SS, (y1 - 390) * SS), "WAITROLLOX", font=FA(int(80 * SS)), fill=WHITE, anchor="mm")
    vit_elec(d, cx - 380, y1 - 320, cx, y1 - 20)
    R(d, cx + 80, y1 - 260, cx + 300, y1, (120, 120, 130), 8)


DESSINS.update({"chateau": chateau, "villa_spa": villa_spa, "boulangerie": boulangerie, "boxe": boxe,
                "restaurant": restaurant, "motocross": motocross, "usine": usine})
