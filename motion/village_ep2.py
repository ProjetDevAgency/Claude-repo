"""Le village des abonnés, épisode 2 : résultat, revenu de l'épicerie, chaque habitant avec SON personnage.

    python motion/village_ep2.py
"""
import math

from PIL import Image, ImageDraw

import iso
from cartoon import (FA, GREEN, INK, RED, SS, WHITE, YEL, CartoonVideo, back, big_number, character, counter, dim,
                     ease, flash, push, shake, tag)
from engine import H, W
from village import (BLANC, BLEU, ROUGE, bouton_abonner, foule, gros_plan_maire, panneau, pin, titre2)
import rue

GOLD = (235, 185, 40)
iso.TW, iso.TH = 76, 38
iso.HK = iso.TW / 96
iso.OY = 960
SKIN_D = (150, 100, 70)
T = {}

# ───────────── la carte du jour 2 ─────────────
# (case i, j) : routes sur i = 0 et j = 0, rivière sur i = -5 / -4.
EPICERIE = (2.0, 1.2)
FOOT = (-3.6, -3.4)
BOULANGERIE = (3.6, -1.6)
BOXE = (-3.4, -1.4)
GROTTE = (5.6, 1.6)

MAISONS = {  # pseudo : (case, couleur, toit, drapeau)
    "Amine.6919": ((1.3, 3.0), (245, 215, 150), (205, 75, 60), None),
    "Nelio": ((2.5, 3.0), (90, 140, 230), (205, 75, 60), None),
    "Mskoww_91": ((3.7, 3.0), (60, 110, 210), (205, 75, 60), None),
    "Alexis": ((1.3, 4.3), (210, 240, 200), (60, 80, 150), None),
    "Maël": ((2.5, 4.3), (250, 190, 190), (205, 75, 60), None),
    "Michael": ((3.7, 4.3), (230, 210, 250), (205, 75, 60), None),
    "You": ((-2.0, 1.4), (250, 250, 250), (205, 75, 60), "maroc"),
    "ghb_s91": ((-3.2, 1.4), (245, 225, 190), (205, 75, 60), "tunisie"),
    "kokoljii": ((-2.0, 2.6), (150, 90, 200), (90, 50, 140), None),
    "Waillox": ((-3.2, 2.6), (250, 230, 200), (205, 75, 60), None),
    "Kuromi": ((-1.6, -1.6), (250, 235, 200), (190, 130, 60), None),
    "SKR junior": ((-1.6, -3.0), (240, 200, 200), (205, 75, 60), None),
    "S2Z": ((-1.6, -4.4), (230, 245, 230), (40, 140, 70), None),
    "rph.49": ((-3.0, -4.6), (200, 225, 250), (205, 75, 60), None),
    "S'": ((1.4, -4.2), (110, 200, 110), (60, 140, 60), None),
}
VILLA_T0 = (2.0, 5.6)
VILLA_OUMAR = (4.4, 5.8)
PS5 = (0.6, 6.0)
VOITURE = (4.9, 3.0)


# ───────────── lotissement : chaque bâtiment sur sa parcelle, sans chevauchement ─────────────
# La carte est découpée en cases de 1×1. Les routes (i = 0, j = 0), la rivière, la mairie et l'épicerie
# sont réservées. Chaque bâtiment prend des cases libres et visibles à l'écran, au plus près du carrefour.

def _reserve():
    occ = set()
    for k in range(-15, 16):
        occ.add((0, k))
        occ.add((k, 0))
        for r in range(iso.RIVIERE_I, iso.RIVIERE_I + 2):
            occ.add((r, k))
    for i in range(1, 7):
        for j in range(-6, 0):
            occ.add((i, j))                      # mairie + son parvis + sa fontaine + de l'air autour
    for i in range(1, 5):
        for j in range(1, 4):
            occ.add((i, j))                      # épicerie + son trottoir
    occ.add((0, -1))
    return occ


def _visible(i, j):
    return abs(i - j) <= 13 and -20 <= i + j <= 30


def _cases(ci, cj, w, d):
    return [(ci + a, cj + b) for a in range(w) for b in range(d)]


def _placer(items, occ, marge=2):
    """items : [(nom, largeur, profondeur)] → {nom: (ci, cj)}.
    Les bâtiments s'alignent le long des deux routes (comme un vrai village), en partant du carrefour,
    avec une case vide entre deux bâtiments pour que chacun se voie bien."""
    def cle(c):
        i, j = c
        d_route = min(abs(i - 0.5), abs(j - 0.5))
        return (round(d_route), abs(i - 0.5) + abs(j - 0.5), j, i)
    cand = sorted(((i, j) for i in range(-14, 15) for j in range(-14, 15)), key=cle)
    out = {}
    for nom, w, d in items:
        for ci, cj in cand:
            cs = _cases(ci, cj, w, d)
            if all(c not in occ and _visible(*c) for c in cs):
                out[nom] = (ci, cj)
                occ.update(_cases(ci - marge, cj - marge, w + 2 * marge, d + 2 * marge))   # cases libres autour
                for k in range(-14, 15):                           # les routes restent des routes
                    occ.discard((0, k)) if False else None
                break
    return out


_OCC = _reserve()
# Paysage autour du village : un lac, des champs et des collines dans les zones libres de la périphérie.
def _zone(w, d, rmin, strict=False, marge=0):
    cand = sorted(((i, j) for i in range(-16, 17) for j in range(-16, 17)),
                  key=lambda c: (abs(c[0] - 0.5) + abs(c[1] - 0.5)))
    for ci, cj in cand:
        if abs(ci - 0.5) + abs(cj - 0.5) < rmin:
            continue
        cs = _cases(ci, cj, w, d)
        ok = (lambda c: _visible(*c)) if strict else (lambda c: abs(c[0] - c[1]) <= 15 and -22 <= c[0] + c[1] <= 32)
        if all(c not in _OCC and ok(c) for c in cs):
            _OCC.update(_cases(ci - marge, cj - marge, w + 2 * marge, d + 2 * marge))
            return (ci, cj)
    return None



_VT = _zone(7, 3, 6, strict=True, marge=2)
_VO = _zone(7, 3, 6, strict=True, marge=2)
VILLA_T0 = (_VT[0] + 0.5, _VT[1] + 0.4)
VILLA_OUMAR = (_VO[0] + 0.5, _VO[1] + 0.4)
_PETITS = _placer([(p, 1, 1) for p in MAISONS], _OCC)
_GRANDS = _placer([("ps5", 1, 1), ("voiture", 2, 1), ("grotte", 2, 3),
                   ("foot", 2, 2), ("boulangerie", 2, 2), ("boxe", 2, 2)], _OCC)
for _p, (_ci, _cj) in _PETITS.items():
    _case, _col, _toit, _fl = MAISONS[_p]
    MAISONS[_p] = ((float(_ci), float(_cj)), _col, _toit, _fl)
# 53 abonnés = 53 logements : les maisons nommées + les bâtiments spéciaux + des maisons « habitant »
NB_ABONNES = 53
_NOMMES = len(MAISONS) + 5                     # + villa T_0, villa Oumar, PS5, maison-voiture, grotte
_COUL = [(245, 215, 150), (200, 225, 250), (250, 190, 190), (210, 240, 200), (240, 240, 240), (250, 230, 170),
         (220, 205, 250), (190, 230, 230)]
_TOITS = [(205, 75, 60), (180, 90, 50), (90, 100, 140), (60, 120, 80), (150, 60, 60)]
_GEN = _placer([("hab%d" % n, 1, 1) for n in range(max(0, NB_ABONNES - _NOMMES))], _OCC, marge=1)
GENERIQUES = [((float(ci), float(cj)), _COUL[n % len(_COUL)], _TOITS[n % len(_TOITS)])
              for n, (ci, cj) in enumerate(_GEN.values())]
LAC = _zone(4, 3, 7, strict=True)
CHAMPS = [z + (w, d, kind) for (w, d, kind) in ((3, 2, "ble"), (2, 3, "colza"), (3, 2, "vigne"), (2, 2, "labour"),
                                                 (3, 2, "colza"), (2, 3, "ble"), (3, 2, "labour"), (2, 2, "vigne"))
          for z in [_zone(w, d, 8)] if z]
COLLINES = [(-16, -16, 8, 7), (-21, -10, 7, 7), (-10, -21, 7, 7),
            (20, 20, 8, 8), (26, 14, 7, 7), (14, 26, 7, 7), (19, 9, 5, 5), (9, 19, 5, 5)]


FOOT = (_GRANDS["foot"][0] + 0.2, _GRANDS["foot"][1] + 0.2)
BOULANGERIE = (_GRANDS["boulangerie"][0] + 0.4, _GRANDS["boulangerie"][1] + 0.4)
BOXE = (_GRANDS["boxe"][0] + 0.4, _GRANDS["boxe"][1] + 0.4)
GROTTE = (_GRANDS["grotte"][0] + 0.15, _GRANDS["grotte"][1])
VOITURE = (_GRANDS["voiture"][0] + 0.2, _GRANDS["voiture"][1])
PS5 = (_GRANDS["ps5"][0] + 0.05, _GRANDS["ps5"][1])
_libres = sorted(((i, j) for i in range(-12, 13) for j in range(-12, 13)
                  if (i, j) not in _OCC and _visible(i, j) and abs(i - 0.5) + abs(j - 0.5) > 6),
                 key=lambda c: (c[0] * 7 + c[1] * 13) % 11)
iso.ARBRES = [(i + 0.1, j + 0.1) for (i, j) in _libres[:26]]


def villa(d, i, j, toit=(250, 250, 250), k=1.0, piscine=True, palmiers=True, e=1.6):
    """Grande villa sur deux étages, toit-terrasse, grande piscine avec plage et palmiers."""
    iso.box(d, i, j, 1.6 * e, 1.2 * e, 50 * k * e, (250, 250, 245))
    if k > 0.5:
        iso.box(d, i + 0.2 * e, j + 0.1 * e, 1.2 * e, 0.9 * e, 40 * k * e, (240, 240, 235), z0=50 * k * e)
        iso.box(d, i + 0.15 * e, j + 0.05 * e, 1.3 * e, 1.0 * e, 6 * e, toit, z0=90 * k * e)
        for q in range(4):                      # baies vitrées sur deux niveaux
            a = i + (0.2 + q * 0.34) * e
            for z0, z1 in ((10, 40), (60, 82)):
                d.polygon([iso.P(a, j + 1.2 * e, z0 * e), iso.P(a + 0.24 * e, j + 1.2 * e, z0 * e),
                           iso.P(a + 0.24 * e, j + 1.2 * e, z1 * e), iso.P(a, j + 1.2 * e, z1 * e)], fill=(150, 200, 240))
    if piscine:
        iso.tile(d, i + 1.75 * e, j - 0.15 * e, (245, 235, 210), 1.7 * e, 1.6 * e)       # plage en bois clair
        iso.tile(d, i + 1.9 * e, j, (250, 250, 250), 1.4 * e, 1.3 * e)
        iso.tile(d, i + 1.97 * e, j + 0.07 * e, (60, 180, 245), 1.26 * e, 1.16 * e)
        for q in range(2):                                                         # transats
            iso.box(d, i + (2.05 + q * 0.4) * e, j + 1.32 * e, 0.28 * e, 0.12 * e, 5, (250, 120, 90))
    if palmiers:
        for (a, b) in ((i - 0.3 * e, j + 1.3 * e), (i + 3.5 * e, j + 1.4 * e), (i + 3.5 * e, j - 0.1 * e)):
            x, y = iso.iso(a, b)
            q = iso.HK * e
            d.line([x * SS, y * SS, (x + 8 * q) * SS, (y - 90 * q) * SS], fill=(130, 90, 50), width=int(7 * q * SS))
            for ang in range(0, 360, 60):
                r = math.radians(ang)
                d.line([(x + 8 * q) * SS, (y - 90 * q) * SS, (x + 8 * q + 40 * q * math.cos(r)) * SS,
                        (y - 90 * q + 22 * q * math.sin(r)) * SS], fill=(50, 160, 70), width=int(9 * q * SS))


def ps5(d, i, j, k=1.0):
    """La maison PS5 : console debout, deux coques blanches, cœur noir, liseré bleu (sans socle)."""
    h = 150 * k
    iso.box(d, i, j, 0.35, 1.0, h, (248, 248, 252))
    iso.box(d, i + 0.35, j + 0.08, 0.2, 0.84, h * 0.95, (25, 25, 32))
    iso.box(d, i + 0.55, j, 0.35, 1.0, h, (248, 248, 252))
    x, y = iso.iso(i + 0.45, j + 1.0, h * 0.55)
    q = iso.HK
    d.line([x * SS, (y - 40 * q) * SS, x * SS, (y + 40 * q) * SS], fill=(80, 170, 255), width=int(6 * q * SS))


def voiture(d, i, j, k=1.0):
    """Maison-voiture rouge, grande comme une maison."""
    iso.box(d, i, j, 1.6, 1.0, 40 * k, (220, 35, 45))
    if k > 0.5:
        iso.box(d, i + 0.35, j + 0.1, 0.9, 0.8, 32, (230, 50, 60), z0=40 * k)
        d.polygon([iso.P(i + 0.4, j + 0.9, 46), iso.P(i + 1.2, j + 0.9, 46), iso.P(i + 1.2, j + 0.9, 68),
                   iso.P(i + 0.4, j + 0.9, 68)], fill=(170, 215, 245))
    q = iso.HK
    for a in (0.3, 1.3):
        x, y = iso.iso(i + a, j + 1.0, 8)
        r = 16 * q
        d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=(25, 25, 30))
        d.ellipse([(x - r / 2) * SS, (y - r / 2) * SS, (x + r / 2) * SS, (y + r / 2) * SS], fill=(190, 190, 200))


def grotte(d, i, j, t=0.0):
    """Grotte : un amas de gros rochers arrondis, entrée sombre en arche face à la caméra, feu devant."""
    q, S = iso.HK, SS
    cx, cy = iso.iso(i + 1.0, j + 1.0)
    rochers = [(-70, -40, 75, (120, 115, 110)), (60, -45, 80, (128, 122, 116)), (0, -95, 90, (138, 132, 125)),
               (-40, -150, 60, (150, 144, 136)), (45, -140, 55, (145, 139, 131)), (-100, 5, 45, (110, 105, 100)),
               (100, 0, 50, (115, 110, 104))]
    for dx, dy, r, col in rochers:
        x, y, rr = cx + dx * q, cy + dy * q, r * q
        d.ellipse([(x - rr) * S, (y - rr * 0.85) * S, (x + rr) * S, (y + rr * 0.85) * S], fill=col)
        d.ellipse([(x - rr * 0.6) * S, (y - rr * 0.75) * S, (x + rr * 0.1) * S, (y - rr * 0.25) * S],
                  fill=tuple(min(255, c + 25) for c in col))
    ex, ey = cx, cy + 10 * q                                  # entrée de la grotte
    d.chord([(ex - 48 * q) * S, (ey - 95 * q) * S, (ex + 48 * q) * S, (ey + 40 * q) * S], 180, 360, fill=(30, 26, 24))
    d.rectangle([(ex - 48 * q) * S, (ey - 28 * q) * S, (ex + 48 * q) * S, ey * S], fill=(30, 26, 24))
    fx, fy = iso.iso(i + 1.3, j + 2.2)                        # feu de camp
    fl = 1 + 0.15 * math.sin(t * 12)
    for a in (-1, 1):
        d.line([(fx - 18 * q) * S, (fy + 4 * q * a) * S, (fx + 18 * q) * S, (fy - 4 * q * a) * S],
               fill=(110, 70, 40), width=int(6 * q * S))
    d.polygon([(fx - 16 * q) * S, fy * S, fx * S, (fy - 46 * q * fl) * S, (fx + 16 * q) * S, fy * S], fill=(250, 140, 30))
    d.polygon([(fx - 8 * q) * S, fy * S, fx * S, (fy - 26 * q * fl) * S, (fx + 8 * q) * S, fy * S], fill=(255, 220, 60))


def drapeau(d, i, j, kind, z=95):
    x, y = iso.iso(i + 0.5, j + 0.5, z)
    q, s = iso.HK * 1.6, SS
    d.line([x * s, y * s, x * s, (y - 60 * q) * s], fill=INK, width=int(3 * q * s))
    w, h = 40 * q, 26 * q
    d.rectangle([x * s, (y - 60 * q) * s, (x + w) * s, (y - 60 * q + h) * s], fill=(200, 30, 40))
    cx, cy = x + w / 2, y - 60 * q + h / 2
    if kind == "maroc":
        d.text((cx * s, cy * s), "★", font=FA(int(20 * q * s)), fill=(20, 120, 50), anchor="mm")
    else:
        r = 8 * q
        d.ellipse([(cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s], fill=WHITE)
        d.ellipse([(cx - r * 0.6) * s, (cy - r * 0.6) * s, (cx + r * 0.4) * s, (cy + r * 0.6) * s], fill=(200, 30, 40))


def boulangerie(d, i, j, k=1.0):
    iso.box(d, i, j, 1.2, 1.2, 50 * k, (250, 235, 200))
    if k > 0.6:
        iso.roof(d, i - 0.05, j - 0.05, 1.3, 1.3, 50 * k, 30, (190, 130, 60))


def club_boxe(d, i, j, k=1.0):
    iso.box(d, i, j, 1.2, 1.2, 52 * k, (235, 235, 240))
    if k > 0.6:
        iso.box(d, i - 0.05, j - 0.05, 1.3, 1.3, 8, (200, 30, 40), z0=52 * k)
        x, y = iso.iso(i + 0.6, j + 1.2, 34)
        q = iso.HK
        d.rounded_rectangle([(x - 34 * q) * SS, (y - 12 * q) * SS, (x + 34 * q) * SS, (y + 12 * q) * SS],
                            radius=int(4 * q * SS), fill=(200, 30, 40))
        d.text((x * SS, y * SS), "BOXE", font=FA(int(16 * q * SS)), fill=WHITE, anchor="mm")


def stade(d, i, j, k=1.0):
    iso.tile(d, i, j, (70, 170, 80), 1.6, 1.6)
    if k > 0:
        for a in (0.1, 1.5):
            iso.box(d, i + a, j + 0.6, 0.05, 0.4, 24, WHITE)


# ───────────── la mairie, version grandiose ─────────────

PIERRE = (240, 232, 214)
ARDOISE = (70, 85, 120)


def _face_j(d, jf, i0, i1, z0, z1, col):
    """Rectangle sur la façade avant (plan j = jf), de i0 à i1 et de z0 à z1."""
    d.polygon([iso.P(i0, jf, z0), iso.P(i1, jf, z0), iso.P(i1, jf, z1), iso.P(i0, jf, z1)], fill=col)


def mairie_grande(d, i, j):
    w, dd = 2.8, 1.8
    jf = j + dd                                                   # façade principale, tournée vers la route
    iso.tile(d, i - 0.3, jf, (215, 210, 200), w + 0.6, 1.2)      # parvis pavé
    for k in range(3):                                             # marches
        iso.box(d, i + 0.9 - 0.1 * k, jf + 0.05 * k, 1.0 + 0.2 * k, 0.12, 6 * (3 - k), (225, 220, 210))
    iso.box(d, i, j, w, dd, 78, PIERRE)                            # corps du bâtiment
    iso.box(d, i - 0.05, j - 0.05, w + 0.1, dd + 0.1, 8, (220, 210, 190), z0=78)   # corniche
    iso.box(d, i + 0.1, j + 0.1, w - 0.2, dd - 0.2, 26, ARDOISE, z0=86)            # toit mansardé
    iso.box(d, i + 0.95, j + dd - 0.05, 0.9, 0.25, 104, (248, 242, 228))           # avant-corps central
    # fronton triangulaire avec horloge
    a, b = i + 0.95, i + 1.85
    jf2 = j + dd + 0.2
    d.polygon([iso.P(a, jf2, 104), iso.P(b, jf2, 104), iso.P((a + b) / 2, jf2, 140)], fill=(248, 242, 228))
    cx, cy = iso.iso((a + b) / 2, jf2, 118)
    q = iso.HK
    r = 11 * q
    d.ellipse([(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS], fill=WHITE, outline=INK, width=int(2 * q * SS))
    d.line([cx * SS, cy * SS, cx * SS, (cy - r * 0.7) * SS], fill=INK, width=int(2 * q * SS))
    d.line([cx * SS, cy * SS, (cx + r * 0.5) * SS, cy * SS], fill=INK, width=int(2 * q * SS))
    # colonnes et porte
    for k in range(4):
        c0 = a + 0.08 + k * 0.23
        _face_j(d, jf2, c0, c0 + 0.07, 0, 96, (255, 252, 245))
    _face_j(d, jf2, a + 0.36, a + 0.54, 0, 42, (110, 75, 50))
    # fenêtres hautes de chaque côté
    for c0 in (i + 0.2, i + 0.55, i + 2.05, i + 2.4):
        _face_j(d, jf, c0, c0 + 0.2, 14, 40, (150, 200, 240))
        _face_j(d, jf, c0, c0 + 0.2, 50, 72, (150, 200, 240))
    # bandeau MAIRIE + devise
    x, y = iso.iso((a + b) / 2, jf2, 72)
    d.text((x * SS, y * SS), "MAIRIE", font=FA(int(15 * q * SS)), fill=INK, anchor="mm")
    x, y = iso.iso(i + w / 2, jf, 6)
    d.text((x * SS, (y - 2 * q) * SS), "LIBERTÉ · ÉGALITÉ · FRATERNITÉ", font=FA(int(7 * q * SS)), fill=(90, 80, 70),
           anchor="mm")
    # drapeaux tricolores sur le toit
    for (u, v) in ((i + 0.6, j + 0.9), (i + 2.2, j + 0.9)):
        x, y = iso.iso(u, v, 112)
        d.line([x * SS, y * SS, x * SS, (y - 55 * q) * SS], fill=INK, width=int(3 * q * SS))
        for k, c in enumerate((BLEU, BLANC, ROUGE)):
            d.rectangle([(x + k * 9 * q) * SS, (y - 55 * q) * SS, (x + (k + 1) * 9 * q) * SS, (y - 38 * q) * SS], fill=c)
    # fontaine sur la place
    fx, fy = iso.iso(i + w + 0.2, jf + 0.75)
    for rx, ry, col in ((34, 17, (200, 195, 185)), (28, 13, (90, 170, 235))):
        d.ellipse([(fx - rx * q) * SS, (fy - ry * q) * SS, (fx + rx * q) * SS, (fy + ry * q) * SS], fill=col)
    d.rectangle([(fx - 4 * q) * SS, (fy - 30 * q) * SS, (fx + 4 * q) * SS, fy * SS], fill=(200, 195, 185))
    for dx in (-10, 0, 10):
        d.line([fx * SS, (fy - 30 * q) * SS, (fx + dx * q) * SS, (fy - 12 * q) * SS], fill=(150, 210, 250),
               width=int(3 * q * SS))


iso.MAIRIE = (1.2, -3.6)
iso.mairie = mairie_grande


# ───────────── habillage « grandiose » : jardins, lampadaires, voitures, oies, fleurs, montagnes ─────────────

def jardin(d, i, j):
    """Jardin clôturé autour d'une maison (case i, j) + allée vers la route."""
    iso.tile(d, i - 0.35, j - 0.35, (135, 210, 110), 1.7, 1.7)
    pts = [iso.iso(i - 0.35, j - 0.35), iso.iso(i + 1.35, j - 0.35), iso.iso(i + 1.35, j + 1.35),
           iso.iso(i - 0.35, j + 1.35), iso.iso(i - 0.35, j - 0.35)]
    q = iso.HK
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = 7
        for k in range(n + 1):
            x, y = x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n
            d.line([x * SS, y * SS, x * SS, (y - 10 * q) * SS], fill=(250, 250, 245), width=int(3 * q * SS))
        d.line([x0 * SS, (y0 - 7 * q) * SS, x1 * SS, (y1 - 7 * q) * SS], fill=(250, 250, 245), width=int(3 * q * SS))


def fleurs(d, i, j, seed):
    q = iso.HK
    for k in range(5):
        a = ((seed * 7 + k * 13) % 10) / 10
        b = ((seed * 3 + k * 17) % 10) / 10
        x, y = iso.iso(i + a, j + b)
        col = [(250, 90, 120), (255, 220, 60), (250, 250, 250), (180, 120, 250)][(seed + k) % 4]
        r = 4 * q
        d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=col)


def buisson(d, i, j):
    x, y = iso.iso(i + 0.5, j + 0.5)
    q = iso.HK
    for dx, r in ((-10, 13), (8, 15), (0, 11)):
        d.ellipse([(x + dx * q - r * q) * SS, (y - 18 * q - r * q) * SS, (x + dx * q + r * q) * SS,
                   (y - 18 * q + r * q) * SS], fill=(70, 160, 75))


def lampadaire(d, i, j):
    x, y = iso.iso(i, j)
    q = iso.HK
    d.line([x * SS, y * SS, x * SS, (y - 70 * q) * SS], fill=(50, 50, 60), width=int(4 * q * SS))
    d.line([x * SS, (y - 70 * q) * SS, (x + 12 * q) * SS, (y - 72 * q) * SS], fill=(50, 50, 60), width=int(4 * q * SS))
    d.ellipse([(x + 6 * q) * SS, (y - 78 * q) * SS, (x + 20 * q) * SS, (y - 66 * q) * SS], fill=(255, 230, 120))


def auto(d, i, j, col, sens):
    """Petite voiture sur la route (sens 'i' ou 'j')."""
    if sens == "i":
        iso.box(d, i, j, 0.7, 0.35, 12, col)
        iso.box(d, i + 0.15, j + 0.03, 0.35, 0.3, 9, (190, 225, 245), z0=12)
    else:
        iso.box(d, i, j, 0.35, 0.7, 12, col)
        iso.box(d, i + 0.03, j + 0.15, 0.3, 0.35, 9, (190, 225, 245), z0=12)


def oie(d, i, j, flip=False):
    x, y = iso.iso(i, j)
    q = iso.HK
    s = -1 if flip else 1
    d.ellipse([(x - 12 * q) * SS, (y - 12 * q) * SS, (x + 12 * q) * SS, (y + 2 * q) * SS], fill=(250, 250, 250))
    d.line([(x + 8 * q * s) * SS, (y - 6 * q) * SS, (x + 12 * q * s) * SS, (y - 24 * q) * SS], fill=(250, 250, 250),
           width=int(5 * q * SS))
    d.ellipse([(x + 8 * q * s) * SS, (y - 30 * q) * SS, (x + 17 * q * s) * SS if s > 0 else (x + 8 * q * s) * SS,
               (y - 21 * q) * SS], fill=(250, 250, 250)) if False else None
    d.ellipse([(x + (12 * s - 5) * q) * SS, (y - 30 * q) * SS, (x + (12 * s + 5) * q) * SS, (y - 20 * q) * SS],
              fill=(250, 250, 250))
    d.polygon([(x + (12 * s + 4 * s) * q) * SS, (y - 26 * q) * SS, (x + (12 * s + 12 * s) * q) * SS,
               (y - 24 * q) * SS, (x + (12 * s + 4 * s) * q) * SS, (y - 22 * q) * SS], fill=(250, 150, 30))


def horizon(img):
    """Ciel et montagnes au fond, au-dessus du village (sur l'image finale)."""
    d = ImageDraw.Draw(img)
    for y in range(0, 470, 4):
        k = y / 470
        d.rectangle([0, y, W, y + 4], fill=(int(120 + 80 * k), int(190 + 40 * k), int(240 + 10 * k)))
    for (x0, x1, top, col) in ((-100, 520, 250, (150, 160, 190)), (300, 900, 200, (135, 145, 180)),
                               (700, 1200, 270, (150, 160, 190))):
        d.polygon([(x0, 470), ((x0 + x1) / 2, top), (x1, 470)], fill=col)
        d.polygon([((x0 + x1) / 2 - 40, top + 40), ((x0 + x1) / 2, top), ((x0 + x1) / 2 + 40, top + 40)],
                  fill=(250, 250, 255))
    d.rectangle([0, 440, W, 480], fill=(110, 180, 90))


def habillage(d, objs, maisons_cases):
    """Ajoute jardins (sol), fleurs, buissons, lampadaires, voitures et oies dans la liste d'objets à trier."""
    for n, (i, j) in enumerate(maisons_cases):
        jardin(d, i, j)
        fleurs(d, i - 0.3, j + 0.95, n)
        objs.append((i + j + 0.2, lambda i=i, j=j: buisson(d, i + 0.9, j - 0.3)))
    for k in range(-12, 13, 3):                              # lampadaires le long des routes
        if k not in (0,):
            objs.append((k + 1.0, lambda k=k: lampadaire(d, k + 0.5, 1.05)))
            if not -7 <= k <= 0:                               # pas de lampadaire devant la mairie
                objs.append((k + 1.0, lambda k=k: lampadaire(d, 1.05, k + 0.5)))
    for (i, j, c, sn) in ((-7.0, 0.1, (60, 120, 220), "i"), (5.5, 0.55, (240, 180, 40), "i"),
                          (0.1, 6.5, (230, 60, 60), "j"), (0.55, -8.0, (250, 250, 250), "j")):
        objs.append((i + j + 1, lambda i=i, j=j, c=c, sn=sn: auto(d, i, j, c, sn)))
    for (i, j, f) in ((-4.6, 4.0, False), (-4.2, 4.6, True), (-4.7, 6.2, False), (-3.6, -6.5, True),
                      (-4.3, -7.0, False), (2.2, 10.0, True), (2.8, 10.4, False)):
        objs.append((i + j, lambda i=i, j=j, f=f: oie(d, i, j, f)))


def champ(d, i, j, w, dd, kind):
    base = {"ble": (235, 205, 90), "colza": (245, 225, 40), "vigne": (150, 190, 90), "labour": (165, 120, 80)}[kind]
    ligne = {"ble": (215, 180, 70), "colza": (220, 200, 30), "vigne": (70, 130, 60), "labour": (130, 90, 60)}[kind]
    iso.tile(d, i + 0.1, j + 0.1, base, w - 0.2, dd - 0.2)
    q = iso.HK
    for k in range(1, int((dd - 0.2) * 4)):
        b = j + 0.1 + k * 0.25
        d.line([iso.P(i + 0.15, b), iso.P(i + w - 0.15, b)], fill=ligne, width=int((5 if kind == "vigne" else 3) * q * SS))


def lac(d, i, j, w, dd, t=0.0):
    cx, cj = i + w / 2, j + dd / 2
    pts_bord = [iso.P(cx + (w / 2) * math.cos(a), cj + (dd / 2) * math.sin(a)) for a in [x * math.pi / 12 for x in range(24)]]
    pts_eau = [iso.P(cx + (w / 2 - 0.25) * math.cos(a), cj + (dd / 2 - 0.25) * math.sin(a))
               for a in [x * math.pi / 12 for x in range(24)]]
    d.polygon(pts_bord, fill=(225, 210, 160))
    d.polygon(pts_eau, fill=(70, 160, 230))
    for k in range(3):                                   # reflets
        x, y = iso.iso(cx - 0.8 + k * 0.6, cj - 0.3 + k * 0.3)
        q = iso.HK
        d.line([(x - 14 * q) * SS, y * SS, (x + 14 * q) * SS, y * SS], fill=(160, 210, 250), width=int(3 * q * SS))
    iso.box(d, cx - 0.4, cj + 0.1, 0.6, 0.25, 8, (150, 100, 60))   # barque
    for (a, b, f) in ((cx + 0.6, cj - 0.4, False), (cx + 0.9, cj - 0.1, True), (cx - 1.0, cj - 0.6, False)):
        oie(d, a, b, f)


def colline(d, i, j, w, dd):
    cx, cj = i + w / 2, j + dd / 2
    h = 60 * min(w, dd) / 3
    for n in range(8):                                   # dôme : ellipses empilées qui rétrécissent
        k = n / 8
        rw, rd, z = (w / 2) * (1 - k * 0.85), (dd / 2) * (1 - k * 0.85), h * math.sin(k * math.pi / 2)
        g = int(150 + 50 * k)
        pts = [iso.P(cx + rw * math.cos(a), cj + rd * math.sin(a), z) for a in [x * math.pi / 10 for x in range(20)]]
        d.polygon(pts, fill=(int(g * 0.55), g, int(g * 0.45)))
    for (a, b) in ((cx - 0.6, cj - 0.4), (cx + 0.5, cj + 0.3), (cx - 0.1, cj + 0.8)):
        x, y = iso.iso(a, b, h * 0.7)
        q = iso.HK
        d.rectangle([(x - 3 * q) * SS, (y - 18 * q) * SS, (x + 3 * q) * SS, y * SS], fill=(110, 75, 50))
        d.ellipse([(x - 14 * q) * SS, (y - 46 * q) * SS, (x + 14 * q) * SS, (y - 14 * q) * SS], fill=(50, 135, 60))


def village_j2(etat=None, t=0.0, extra=None, skip=None):
    """Carte complète du jour 2 (toutes les maisons construites). extra : bâtiments du vote à montrer."""
    etat = etat or {}
    big = iso.carte(dict(maire=(0.6, -1.2), epicerie=1.0, maisons=[], terrains=False,
                         habitants=etat.get("habitants", [])))
    d = ImageDraw.Draw(big)
    objs = []
    for (i, j, w, dd, kind) in CHAMPS:
        champ(d, i, j, w, dd, kind)
    if LAC:
        lac(d, *LAC, 4, 3)
    for (i, j, w, dd) in COLLINES:
        objs.append((i + j + w / 2 + dd / 2, lambda i=i, j=j, w=w, dd=dd: colline(d, i, j, w, dd)))
    habillage(d, objs, [c for (c, _, _, _) in MAISONS.values()] + [c for (c, _, _) in GENERIQUES])
    for (i, j), col, toit in GENERIQUES:
        objs.append((i + j + 1, lambda i=i, j=j, c=col, r=toit: iso.maison(d, i, j, 1.0, c, r)))
    for pseudo, ((i, j), col, toit, flag) in MAISONS.items():
        if pseudo == skip:
            continue
        objs.append((i + j + 1, lambda i=i, j=j, c=col, r=toit, f=flag: (
            iso.maison(d, i, j, 1.0, c, r), f and drapeau(d, i, j, f))))
    if skip != 'villa_t0':
        objs.append((sum(VILLA_T0) + 3.6, lambda: villa(d, *VILLA_T0, toit=GOLD)))
    if skip != 'villa_oumar':
        objs.append((sum(VILLA_OUMAR) + 3.6, lambda: villa(d, *VILLA_OUMAR)))
    if skip != 'ps5':
        objs.append((sum(PS5) + 1, lambda: ps5(d, *PS5)))
    if skip != 'voiture':
        objs.append((sum(VOITURE) + 1.3, lambda: voiture(d, *VOITURE)))
    if skip != 'grotte':
        objs.append((sum(GROTTE) + 1.8, lambda: grotte(d, *GROTTE, t)))
    for name, fn, pos in (("foot", stade, FOOT), ("boulangerie", boulangerie, BOULANGERIE), ("boxe", club_boxe, BOXE)):
        if extra and name in extra:
            objs.append((sum(pos) + 1.5, lambda fn=fn, pos=pos: fn(d, *pos)))
        else:
            objs.append((-100, lambda pos=pos: iso.terrain(d, *pos, 1.2, 1.2)))
    for _, fn in sorted(objs, key=lambda o: o[0]):
        fn()
    return big


_cache = {}


def carte_j2(key="base", **kw):
    if key not in _cache:
        _cache[key] = village_j2(**kw)
    return _cache[key]


def vue(z, center, key="base", **kw):
    return iso.camera(carte_j2(key, **kw), z, center)


def zoom_sur(i, j, z=2.2, dz=-60, key="base", dx=0, **kw):
    x, y = iso.iso(i + 0.5, j + 0.5)
    return vue(z, (x + dx / z, y + dz), key, **kw)


# ───────────── les personnages ─────────────

def accessoires(d, cx, base, sc, acc, t):
    s = SS * sc

    def X(v):
        return cx * SS + v * s

    def Y(v):
        return base * SS + v * s

    for a in acc:
        if a == "medaille":
            d.line([X(-40), Y(-560), X(0), Y(-470), X(40), Y(-560)], fill=(40, 90, 200), width=int(10 * s))
            d.ellipse([X(-30), Y(-500), X(30), Y(-440)], fill=GOLD, outline=(180, 130, 20), width=int(5 * s))
            d.text((X(0), Y(-470)), "1", font=FA(int(40 * s)), fill=INK, anchor="mm")
        elif a == "couronne":
            d.polygon([(X(-70), Y(-820)), (X(-70), Y(-900)), (X(-35), Y(-850)), (X(0), Y(-920)), (X(35), Y(-850)),
                       (X(70), Y(-900)), (X(70), Y(-820))], fill=GOLD, outline=(180, 130, 20))
        elif a == "rosette":
            d.ellipse([X(-70), Y(-530), X(-20), Y(-480)], fill=BLEU)
            d.ellipse([X(-60), Y(-520), X(-30), Y(-490)], fill=BLANC)
            d.ellipse([X(-52), Y(-512), X(-38), Y(-498)], fill=ROUGE)
        elif a == "lunettes_soleil":
            d.rounded_rectangle([X(-75), Y(-725), X(75), Y(-680)], radius=int(14 * s), fill=(20, 20, 26))
        elif a == "chaine_or":
            d.arc([X(-60), Y(-600), X(60), Y(-440)], 20, 160, fill=GOLD, width=int(12 * s))
            d.ellipse([X(-16), Y(-460), X(16), Y(-428)], fill=GOLD)
        elif a == "toque":
            d.rounded_rectangle([X(-75), Y(-860), X(75), Y(-790)], radius=int(10 * s), fill=WHITE)
            for k in (-50, 0, 50):
                d.ellipse([X(k - 50), Y(-960), X(k + 50), Y(-850)], fill=WHITE)
        elif a == "baguette":
            d.rounded_rectangle([X(110), Y(-760), X(150), Y(-440)], radius=int(20 * s), fill=(220, 160, 80))
            for k in range(4):
                d.line([X(115), Y(-720 + k * 70), X(145), Y(-700 + k * 70)], fill=(180, 120, 50), width=int(5 * s))
        elif a == "gants":
            for sx in (-1, 1):
                d.ellipse([X(sx * 150 - 45), Y(-905), X(sx * 150 + 45), Y(-815)], fill=(210, 30, 40))
        elif a == "ballon":
            d.ellipse([X(-170), Y(-110), X(-70), Y(-10)], fill=WHITE, outline=INK, width=int(5 * s))
            d.polygon([(X(-130), Y(-75)), (X(-110), Y(-75)), (X(-102), Y(-55)), (X(-120), Y(-42)), (X(-138), Y(-55))],
                      fill=INK)
        elif a == "massue":
            d.line([X(130), Y(-300), X(190), Y(-760)], fill=(120, 80, 40), width=int(40 * s))
            d.ellipse([X(150), Y(-860), X(250), Y(-720)], fill=(120, 80, 40))
        elif a == "fourrure":
            for (u, v) in ((-50, -480), (30, -420), (-20, -340), (50, -520)):
                d.ellipse([X(u - 18), Y(v - 14), X(u + 18), Y(v + 14)], fill=(110, 70, 35))
        elif a in ("drapeau_maroc", "drapeau_tunisie"):
            d.line([X(150), Y(-300), X(150), Y(-980)], fill=INK, width=int(10 * s))
            d.rectangle([X(150), Y(-980), X(330), Y(-860)], fill=(200, 30, 40))
            if a == "drapeau_maroc":
                d.text((X(240), Y(-920)), "★", font=FA(int(80 * s)), fill=(20, 120, 50), anchor="mm")
            else:
                d.ellipse([X(205), Y(-955), X(275), Y(-885)], fill=WHITE)
                d.ellipse([X(218), Y(-942), X(262), Y(-898)], fill=(200, 30, 40))
        elif a == "casque_audio":
            d.arc([X(-110), Y(-830), X(110), Y(-620)], 180, 360, fill=INK, width=int(18 * s))
            d.rounded_rectangle([X(-125), Y(-740), X(-90), Y(-660)], radius=int(10 * s), fill=INK)
            d.rounded_rectangle([X(90), Y(-740), X(125), Y(-660)], radius=int(10 * s), fill=INK)
        elif a == "manette":
            d.rounded_rectangle([X(-90), Y(-420), X(70), Y(-360)], radius=int(26 * s), fill=(245, 245, 250), outline=INK,
                                width=int(5 * s))
        elif a == "diplome":
            d.polygon([(X(0), Y(-900)), (X(130), Y(-850)), (X(0), Y(-800)), (X(-130), Y(-850))], fill=INK)
            d.rectangle([X(-60), Y(-830), X(60), Y(-790)], fill=INK)
            d.line([X(100), Y(-850), X(110), Y(-760)], fill=GOLD, width=int(6 * s))
        elif a == "tablier":
            d.rounded_rectangle([X(-70), Y(-500), X(70), Y(-250)], radius=int(20 * s), fill=(250, 250, 250))
            d.text((X(0), Y(-380)), "ÉPICERIE", font=FA(int(26 * s)), fill=(210, 60, 60), anchor="mm")
        elif a == "maillot":
            d.text((X(0), Y(-400)), "10", font=FA(int(90 * s)), fill=WHITE, anchor="mm")


PERSOS = {  # pseudo : (look, accessoires, rôle)
    "vendeuse": (dict(shirt=(230, 120, 160), pants=(40, 40, 60), hair=(30, 25, 20), long_hair=True, mouth="grin"),
                 ["tablier"], "LA VENDEUSE DE L'ÉPICERIE"),
    "Amine.6919": (dict(shirt=(245, 245, 245), pants=(40, 40, 50), hair=(30, 25, 20), mouth="grin", arm=0.95),
                   ["medaille"], "1ER HABITANT · MAISON N°1"),
    "Alexis": (dict(shirt=(40, 50, 90), pants=(40, 50, 90), hair=(90, 60, 40), tie=True, mouth="smile"),
               ["rosette"], "ÉLU CONSEILLER MUNICIPAL"),
    "Maël": (dict(shirt=(250, 170, 200), pants=(240, 240, 240), hair=(60, 40, 30), mouth="grin", arm=0.6), [],
             "CANDIDAT ADJOINT"),
    "Michael": (dict(shirt=(60, 120, 90), pants=(40, 50, 40), hair=(30, 25, 20), mouth="grin", arm=0.6), [],
                "CANDIDAT ADJOINT"),
    "kokoljii": (dict(shirt=(110, 40, 160), pants=(40, 30, 60), hair=(20, 20, 25), mouth="grin", arm=0.9),
                 ["couronne"], "PREMIER MINISTRE AUTOPROCLAMÉ"),
    "S'": (dict(shirt=(250, 150, 190), pants=(80, 60, 120), hair=(30, 22, 18), long_hair=True, mouth="grin"), [],
           "LA FILLE DU MAIRE"),
    "T_0": (dict(shirt=(30, 30, 36), pants=(30, 30, 36), hair=(25, 20, 18), mouth="grin", arm=0.5),
            ["lunettes_soleil", "chaine_or"], "LE RICHE DU VILLAGE"),
    "oumar dansoko": (dict(shirt=(250, 210, 80), pants=(60, 160, 220), hair=(20, 18, 16), mouth="grin", arm=0.95),
                      ["lunettes_soleil"], "VILLA AVEC PISCINE"),
    "kova.zfr": (dict(shirt=(220, 35, 45), pants=(40, 40, 50), hair=(30, 25, 20), cap=(220, 35, 45), mouth="grin"),
                 [], "LA MAISON-VOITURE"),
    "ps5": (dict(shirt=(40, 60, 140), pants=(30, 30, 40), hair=(40, 30, 25), mouth="o"), ["casque_audio", "manette"],
            "LA MAISON PS5"),
    "pkmoi": (dict(shirt=(160, 110, 60), pants=(120, 80, 40), hair=(60, 40, 25), mouth="grin", brows="colere"),
              ["fourrure", "massue"], "L'HOMME DES CAVERNES"),
    "You": (dict(shirt=(250, 250, 250), pants=(40, 50, 90), hair=(30, 25, 20), mouth="grin"), ["drapeau_maroc"], ""),
    "ghb_s91": (dict(shirt=(220, 50, 60), pants=(40, 40, 50), hair=(30, 25, 20), mouth="grin"), ["drapeau_tunisie"], ""),
    "Waillox": (dict(shirt=(70, 110, 200), pants=(40, 40, 50), hair=(30, 25, 20), glasses=True, mouth="smile"),
                ["diplome"], "LE PLUS MALIN DU VILLAGE"),
    "Kuromi": (dict(shirt=(250, 250, 250), pants=(50, 50, 60), hair=(20, 20, 22), mouth="grin"),
               ["toque", "baguette"], "LE BOULANGER"),
    "SKR junior": (dict(shirt=(30, 30, 36), pants=(200, 30, 40), hair=(20, 18, 16), mouth="flat", brows="colere",
                        arms_up=True), ["gants"], "FUTUR CLUB DE BOXE"),
    "S2Z": (dict(shirt=(40, 140, 70), pants=(250, 250, 250), hair=(20, 18, 16), mouth="grin"), ["ballon", "maillot"],
            "PRÉSIDENT DU CLUB DE FOOT"),
}


def perso(img, pseudo, lt, x=540, base=2050, sc=1.45):
    """Dessine le personnage d'un habitant en gros plan par-dessus l'image."""
    look, acc, _ = PERSOS[pseudo]
    lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    bob = math.sin(lt * 2.6) * 6
    blink = (lt % 3.1) < 0.1
    pop = back(lt / 0.3)
    base = base + (1 - pop) * 300 + bob
    p = dict(look)
    p.setdefault("blink", blink)
    character(d, x, base, sc=sc, **p)
    accessoires(d, x, base, sc, acc, lt)
    lay = lay.resize((W, H), Image.LANCZOS)
    img.paste(lay, (0, 0), lay)


def batiment(d, nom, k):
    """Dessine le bâtiment d'un habitant à l'étape de construction k (0 → 1, avec rebond)."""
    if nom in MAISONS:
        (i, j), col, toit, flag = MAISONS[nom]
        iso.maison(d, i, j, max(0.05, k), col, toit)
        if flag and k >= 1:
            drapeau(d, i, j, flag)
    elif nom == "villa_t0":
        villa(d, *VILLA_T0, toit=GOLD, k=max(0.05, k), piscine=k > 0.6, palmiers=k > 0.9)
    elif nom == "villa_oumar":
        villa(d, *VILLA_OUMAR, k=max(0.05, k), piscine=k > 0.6, palmiers=k > 0.9)
    elif nom == "ps5":
        ps5(d, *PS5, k=max(0.05, k))
    elif nom == "voiture":
        voiture(d, *VOITURE, k=max(0.05, k))
    elif nom == "grotte" and k > 0.3:
        grotte(d, *GROTTE)


CASE = {"epicerie": EPICERIE, "villa_t0": VILLA_T0, "villa_oumar": VILLA_OUMAR, "ps5": PS5, "voiture": VOITURE, "grotte": GROTTE}


def case_de(nom):
    return MAISONS[nom][0] if nom in MAISONS else CASE[nom]


def construction(lt, nom, z, dx=230, dz=-60, t0=0.15, duree=0.7):
    """Plan sur la parcelle : le bâtiment sort de terre (rebond + poussière). Renvoie (image, fonction monde→écran)."""
    base = carte_j2("sans_" + nom, skip=nom)
    big = base.copy()
    d = ImageDraw.Draw(big)
    k = 0.0 if lt < t0 else min(1.12, back((lt - t0) / duree) if lt - t0 < duree else 1.0)
    i, j = case_de(nom)
    if lt > t0 and nom in MAISONS:                       # parcelle mise en valeur (halo jaune)
        a = min(1.0, (lt - t0) / 0.3)
        iso.tile(d, i - 0.3, j - 0.3, (255, 230, 120), 1.6, 1.6)
    if k > 0:
        batiment(d, nom, min(k, 1.12))
    if 0 < lt - t0 < duree + 0.4:                       # nuage de poussière au pied du bâtiment
        a = (lt - t0) / (duree + 0.4)
        x, y = iso.iso(i + 0.5, j + 1.0)
        q = iso.HK
        for n in range(7):
            ang = n * 0.9
            r = (14 + 22 * a) * q
            px, py = x + math.cos(ang) * 40 * a * q * 2, y + math.sin(ang) * 14 * a * q
            g = int(200 + 40 * a)
            d.ellipse([(px - r) * SS, (py - r * 0.6) * SS, (px + r) * SS, (py + r * 0.6) * SS], fill=(g, g - 10, g - 25))
    x, y = iso.iso(i + 0.5, j + 0.5)
    return iso.camera(big, z, (x + dx / z, y + dz / z))   # dx, dz en pixels d'écran


def fiche(lt, dur, pseudo, case=None, z=3.6, nom=None, role=None, x=770, sc=1.3, bat=None):
    """Moment de l'habitant : sa maison sort de terre, son pseudo s'affiche, son personnage arrive."""
    bat = bat or pseudo
    img, to = construction(lt, bat, push(lt, dur, z, z + 0.15))
    perso(img, pseudo, max(0.0, lt - 0.9), x=x, sc=sc, base=2000) if lt > 0.9 else None
    img = rue.contour_aretes(img, seuil=70, w=3)
    titre2(img, "HABITANT DE FAUCHÉ-LES-OIES" if nom is None else "", "@" + pseudo.upper() if nom is None else nom,
           k=lt / 0.25, y=190)
    r = role if role is not None else PERSOS[pseudo][2]
    if r:
        tag(img, 540, 420, r, 50, ROUGE, WHITE, rot=-3, k=(lt - 0.5) / 0.25)
    i, j = case_de(bat)
    hx, hy = to(i + 0.5, j + 0.5, 140)
    if lt > 0.8:
        tag(img, hx, hy, "@" + (pseudo if nom is None else pseudo), 34, WHITE, INK, rot=0, k=(lt - 0.8) / 0.2)
    return shake(flash(img, lt), lt - 0.85, dur=0.25, amp=10)



# ───────────── scènes ─────────────

def s_jour(lt, dur):
    img, _ = vue(1.0, (540, 1020))
    img = dim(img, 0.25, blur=5, dark=0.9)
    lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    panneau(ImageDraw.Draw(lay), 540, 820, "FAUCHÉ-LES-OIES")
    lay = lay.resize((W, H), Image.LANCZOS)
    sc = 1.25 * (0.7 + 0.3 * back(lt / 0.35))
    lay = lay.resize((int(W * sc), int(H * sc)), Image.LANCZOS)
    img.paste(lay, (int(540 - 540 * sc), int(820 - 820 * sc)), lay)
    titre2(img, "JOUR 2", "VOUS AVEZ VOTÉ", k=1.0, y=230)
    if lt > T["lu"] - T["s_jour"]:
        tag(img, 540, 1250, "LE MAIRE A LU TOUS VOS COMMENTAIRES", 50, YEL, INK, rot=-3,
            k=(lt - (T["lu"] - T["s_jour"])) / 0.25)
    return shake(img, lt)


def s_votes(lt, dur):
    img, _ = vue(1.0, (540, 1020))
    img = dim(img, 0.8)
    titre2(img, "RÉSULTAT", "64 VOTES", k=lt / 0.25)
    d = ImageDraw.Draw(img)
    rows = [("1 · RÉPARER LE PONT", 26, (120, 120, 132)), ("2 · OUVRIR UNE ÉPICERIE", 66, GREEN),
            ("3 · LA FÊTE DU VILLAGE", 8, (120, 120, 132))]
    for q, (lab, pct, col) in enumerate(rows):
        y = 620 + q * 210
        k = ease((lt - 0.3 - 0.25 * q) / 0.8)
        d.rounded_rectangle([90, y, 990, y + 120], radius=24, fill=(250, 250, 252))
        if k > 0:
            d.rounded_rectangle([90, y, 90 + max(48, 900 * pct / 100 * k), y + 120], radius=24, fill=col)
        d.text((120, y + 60), lab, font=FA(52), fill=INK, anchor="lm")
        d.text((960, y + 60), f"{int(pct * k)} %", font=FA(60), fill=INK, anchor="rm")
    return img


def s_vendeuse(lt, dur):
    return fiche(lt, dur, "vendeuse", bat="epicerie", z=3.0, nom="L'ÉPICERIE OUVRE", role="LA VENDEUSE EST À LA CAISSE")


def s_revenu(lt, dur):
    ex, ey = iso.iso(2.8, 1.8)
    img, _ = iso.camera(village_j2(dict(habitants=foule(lt, 18))), push(lt, dur, 1.45, 1.6), (ex, ey - 40))
    img = dim(img, 0.25, blur=4, dark=0.92)
    titre2(img, "L'ÉPICERIE RAPPORTE", "5 € / HABITANT / JOUR", k=lt / 0.25)
    t1, t2 = (T[k] - T["s_revenu"] for k in ("vous53", "caisse"))
    if lt > t1:
        big_number(img, (540, 640), "53 × 5 € = +265 €", 120, GREEN, "PAR JOUR", k=(lt - t1) / 0.25)
    if lt > t2:
        big_number(img, (540, 980), counter(300, 565, lt - t2, 0.8, "{:,} €"), 200, YEL, "DANS LA CAISSE", k=1.0, rot=-3)
    return flash(img, lt)


def s_habitants(lt, dur):
    img, _ = vue(1.0, (540, 1000))
    titre2(img, "MAINTENANT", "LES HABITANTS", k=lt / 0.25)
    return shake(img, lt, dur=0.3, amp=8)


def s_amine(lt, dur):
    return fiche(lt, dur, "Amine.6919", MAISONS["Amine.6919"][0])


def s_alexis(lt, dur):
    return fiche(lt, dur, "Alexis", MAISONS["Alexis"][0])


def s_adjoint(lt, dur):
    img, _ = construction(lt, "Maël", push(lt, dur, 3.2, 3.4), dx=0, dz=300)
    if lt > 0.9:
        perso(img, "Maël", lt - 0.9, x=290, sc=1.15)
        perso(img, "Michael", max(0, lt - 1.3), x=790, sc=1.15)
    img = rue.contour_aretes(img, seuil=70, w=3)
    titre2(img, "POSTE D'ADJOINT", "@MAËL VS @MICHAEL", k=lt / 0.25, y=190)
    big_number(img, (540, 900), "VS", 170, RED, k=(lt - 1.4) / 0.25)
    if lt > dur - 1.6:
        tag(img, 540, 520, "ÇA SE JOUERA AU VOTE", 56, YEL, INK, rot=-3, k=(lt - (dur - 1.6)) / 0.25)
    return shake(flash(img, lt), lt - 0.85, dur=0.25, amp=10)


def s_koko(lt, dur):
    img = fiche(lt, dur, "kokoljii", MAISONS["kokoljii"][0])
    if lt > dur - 2.2:
        tag(img, 540, 540, "PERSONNE SAIT CE QUE ÇA VEUT DIRE", 44, WHITE, INK, rot=3, k=(lt - (dur - 2.2)) / 0.25)
    return img


def s_fille(lt, dur):
    return fiche(lt, dur, "S'")


def s_t0(lt, dur):
    img = fiche(lt, dur, "T_0", bat="villa_t0", z=2.4)
    if lt > dur - 2.4:
        tag(img, 540, 540, "DON PROMIS · LE MAIRE ATTEND TOUJOURS", 42, YEL, INK, rot=-3, k=(lt - (dur - 2.4)) / 0.25)
    return img


def s_oumar(lt, dur):
    return fiche(lt, dur, "oumar dansoko", bat="villa_oumar", z=2.4)


def s_kova(lt, dur):
    return fiche(lt, dur, "kova.zfr", bat="voiture", z=3.2)


def s_ps5(lt, dur):
    return fiche(lt, dur, "ps5", bat="ps5", z=3.2, nom="LA MAISON PS5", role="SORTIE DE TERRE")


def s_pkmoi(lt, dur):
    img = fiche(lt, dur, "pkmoi", bat="grotte", z=2.8)
    if lt > 1.2:
        tag(img, 540, 540, "VEILLE SUR NOUS DEPUIS SA GROTTE", 46, YEL, INK, rot=3, k=(lt - 1.2) / 0.25)
    return img


def s_drapeaux(lt, dur):
    img, _ = construction(lt, "You", push(lt, dur, 3.2, 3.4), dx=0, dz=300)
    if lt > 0.9:
        perso(img, "You", lt - 0.9, x=290, sc=1.15)
        perso(img, "ghb_s91", max(0, lt - 1.3), x=780, sc=1.15)
    img = rue.contour_aretes(img, seuil=70, w=3)
    titre2(img, "MAROC ET TUNISIE", "@YOU & @GHB_S91", k=lt / 0.25, y=190)
    return shake(flash(img, lt), lt - 0.85, dur=0.25, amp=10)


def s_waillox(lt, dur):
    return fiche(lt, dur, "Waillox", MAISONS["Waillox"][0])


def s_kuromi(lt, dur):
    img = fiche(lt, dur, "Kuromi", MAISONS["Kuromi"][0])
    if lt > 1.2:
        tag(img, 540, 540, "CHERCHE UN AGRICULTEUR", 50, YEL, INK, rot=-3, k=(lt - 1.2) / 0.25)
    return img


def s_skr(lt, dur):
    img = fiche(lt, dur, "SKR junior", MAISONS["SKR junior"][0])
    if lt > T["sarrete"] - T["s_skr"]:
        tag(img, 540, 540, "IL S'ARRÊTERA PAS AVANT DE L'AVOIR", 46, RED, WHITE, rot=-3,
            k=(lt - (T["sarrete"] - T["s_skr"])) / 0.25)
        return shake(img, lt - (T["sarrete"] - T["s_skr"]))
    return img


CHOIX = [("1", "LE TERRAIN DE FOOT DE @S2Z", "250 €", FOOT, "foot"),
         ("2", "LA BOULANGERIE DE @KUROMI", "300 €", BOULANGERIE, "boulangerie"),
         ("3", "LE CLUB DE BOXE DE @SKR JUNIOR", "400 €", BOXE, "boxe")]


def s_vote(lt, dur):
    t0s = [T[k] - T["s_vote"] for k in ("c1", "c2", "c3")]
    shown = tuple(c[4] for c, t0 in zip(CHOIX, t0s) if lt >= t0)
    img, to = iso.camera(carte_j2("vote_" + "_".join(shown), extra=shown), 1.0, (540, 1000))
    titre2(img, "DEUXIÈME VOTE", "565 € DANS LA CAISSE", k=lt / 0.25)
    for q, ((n, lab, prix, (i, j), _), t0) in enumerate(zip(CHOIX, t0s)):
        pin(img, to(i + 0.6, j + 0.6), n, None, (lt - t0) / 0.25)
        tag(img, 540, 1420 + q * 95, f"{n}  ·  {lab}  ·  {prix}", 34, WHITE, INK, rot=0, k=(lt - t0) / 0.25)
    return img


def s_fin(lt, dur):
    img, _ = vue(1.0, (540, 1000), key="vote_foot_boulangerie_boxe", extra=("foot", "boulangerie", "boxe"))
    img = dim(img, 0.35, blur=8, dark=0.85)
    gros_plan_maire(img, lt, arm=0.95, mouth="o" if int(lt * 7) % 2 else "grin")
    titre2(img, "PLUS QUE 47 HABITANTS", "AVANT LA SURPRISE", k=lt / 0.25)
    tv = T["vote_fin"] - T["s_fin"]
    if lt > tv:
        titre2(img, "1, 2 OU 3 ?", "VOTE EN COMMENTAIRE", k=(lt - tv) / 0.25, y=560)
        bouton_abonner(img, 540, 1250, (lt - tv - 0.4) / 0.25)
    return shake(img, lt)


def main():
    v = CartoonVideo("village_ep02", "scripts/village/ep02.txt", "", "", corner="")
    v.length = (78.0, 82.0, 90.0)
    v.hook_head_start = 0.0
    v.voice("output/_work_village_ep02/voice_raw.mp3")
    sc = [("Jour deux", s_jour), ("Soixante-quatre votes", s_votes), ("Et sa vendeuse", s_vendeuse),
          ("L'épicerie rapporte", s_revenu), ("Maintenant, les habitants", s_habitants), ("Amine", s_amine),
          ("Alexis, élu", s_alexis), ("Pour le poste", s_adjoint), ("Kokoljii", s_koko), ("S, la fille", s_fille),
          ("T zéro", s_t0), ("Oumar", s_oumar), ("Kova", s_kova), ("Et la maison PS5", s_ps5),
          ("Au fond du village", s_pkmoi), ("You et Ghb", s_drapeaux), ("Waillox", s_waillox),
          ("Kuromi, le boulanger", s_kuromi), ("Et Skr junior", s_skr), ("Deuxième vote", s_vote),
          ("Plus que quarante-sept", s_fin)]
    for phrase, fn in sc:
        v.scene(phrase, fn)
        T[fn.__name__] = v.at(phrase)
    T["lu"] = v.at("Le maire a lu")
    T["vous53"], T["caisse"] = v.at("Vous êtes cinquante-trois"), v.at("La caisse remonte")
    T["sarrete"] = v.at("Il s'arrêtera")
    T["c1"], T["c2"], T["c3"] = v.at("Un, le terrain"), v.at("Deux, la boulangerie"), v.at("Trois, le club")
    T["vote_fin"] = v.at("Vote un, deux")
    v.sfx(0.0, "impact", 1.0)
    v.sfx(T["lu"], "pop", 0.8)
    v.sfx(T["s_votes"] + 0.3, "ticks", 0.6)
    v.sfx(T["s_vendeuse"], "succes", 0.9)
    v.sfx(T["caisse"], "ticks", 0.7)
    v.sfx(T["s_habitants"], "whoosh", 0.6)
    for k in ("s_amine", "s_alexis", "s_adjoint", "s_koko", "s_fille", "s_t0", "s_oumar", "s_kova", "s_ps5",
              "s_pkmoi", "s_drapeaux", "s_waillox", "s_kuromi", "s_skr"):
        v.sfx(T[k], "whoosh", 0.45)
        v.sfx(T[k] + 0.15, "marteau", 0.7)
        v.sfx(T[k] + 0.85, "impact", 0.6)
        v.sfx(T[k] + 0.95, "pop", 0.6)
    v.sfx(T["sarrete"], "impact", 0.8)
    for k in ("c1", "c2", "c3"):
        v.sfx(T[k], "pop", 0.7)
    v.sfx(T["vote_fin"], "impact", 0.9)
    for t0, fn in sorted(v.scenes, key=lambda x: x[0]):
        print(f"   {t0:5.1f}s {fn.__name__}")
    v.render()


if __name__ == "__main__":
    main()
