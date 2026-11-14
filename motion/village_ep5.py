"""Fauché-les-Oies, jour 5 : les remparts (méthode v3, le maire raconte, rph.49 a sa voix).
Le village évolue : 114 maisons, remparts tout autour, ferme, kebab, armurerie, villas avec piscine géante, maisons sur
mesure, enclos à oies. Script : scripts/village/ep05.dial (voix : voix_duo.py)."""
import math

from PIL import Image, ImageDraw

import facades
import iso
import rue
import village_ep2 as v2
import village_ep4 as e4
from cartoon import FA, GREEN, INK, RED, SS, WHITE, YEL, CartoonVideo, big_number, bubble, counter, dim, ease, flash, \
    push, shake, tag
from engine import H, W
from facades import BASE, R, fenetre, poly
from village import ROUGE, gros_plan_maire, titre2

T = {}
P = v2.PERSOS
P.update({
    "Lil RP eh": (dict(shirt=(250, 250, 250), pants=(30, 30, 40), hair=(40, 30, 25), tie=True, mouth="grin", arm=0.9), [],
                  "ENTRE AU GOUVERNEMENT"),
    "Antoine": (dict(shirt=(60, 120, 60), pants=(60, 80, 140), hair=(140, 100, 50), cap=(60, 120, 60), mouth="grin"), [],
                "LA FERME DU VILLAGE"),
    "Al3ssio": (dict(shirt=(240, 240, 240), pants=(40, 40, 50), hair=(30, 25, 20), mouth="grin", arm=0.7), ["tablier"],
                "LE KEBAB + SAUNA ET JACUZZI"),
    "Issam": (dict(shirt=(30, 120, 60), pants=(250, 250, 250), hair=(20, 18, 16), mouth="grin"), ["lunettes_soleil"],
              "VILLA"),
    "tangui_31kk": (dict(shirt=(200, 40, 50), pants=(40, 40, 50), hair=(30, 25, 20), mouth="grin"), ["lunettes_soleil"],
                    "VILLA AVEC PISCINE GÉANTE"),
    "Mskoww_91": e4.P["Mskoww_91"],
})


# ───────────── façades (vues de face) des nouveaux bâtiments ─────────────

def ferme(d, cx=540):
    y1 = BASE
    R(d, cx - 330, y1 - 420, cx + 200, y1, (190, 50, 45))
    poly(d, [(cx - 360, y1 - 420), (cx - 65, y1 - 640), (cx + 230, y1 - 420)], (120, 40, 35))
    R(d, cx - 170, y1 - 300, cx + 40, y1, WHITE)
    R(d, cx - 160, y1 - 290, cx + 30, y1, (190, 50, 45))
    d.line([((cx - 160) * SS, (y1 - 290) * SS), ((cx + 30) * SS, y1 * SS)], fill=WHITE, width=12 * SS)
    d.line([((cx + 30) * SS, (y1 - 290) * SS), ((cx - 160) * SS, y1 * SS)], fill=WHITE, width=12 * SS)
    R(d, cx + 240, y1 - 620, cx + 400, y1, (200, 200, 205), 70)                      # silo
    poly(d, [(cx + 230, y1 - 610), (cx + 320, y1 - 700), (cx + 410, y1 - 610)], (150, 150, 160))


def kebab(d, cx=540):
    facades.boutique(d, cx, nom="KEBAB D'ALESSIO", mur=(250, 235, 210), enseigne=(200, 40, 40), store=(240, 180, 40))
    x = cx - 210
    R(d, x - 14, BASE - 250, x + 14, BASE - 60, (150, 150, 150))                    # la broche
    R(d, x - 60, BASE - 230, x + 60, BASE - 90, (190, 120, 60), 40)


def armurerie(d, cx=540):
    facades.maison(d, cx, 620, (210, 205, 195), (70, 70, 80))
    R(d, cx - 230, BASE - 520, cx + 230, BASE - 440, (40, 40, 48), 12)
    d.text((cx * SS, (BASE - 480) * SS), "ARMURERIE", font=FA(54 * SS), fill=YEL, anchor="mm")


def villa_geante(d, cx=540):
    facades.villa(d, cx)
    R(d, cx - 520, BASE - 40, cx + 520, BASE + 60, (250, 250, 250))                 # piscine géante devant
    R(d, cx - 500, BASE - 30, cx + 500, BASE + 50, (60, 180, 245))


def maison_noire(d, cx=540):
    facades.maison(d, cx, 620, (36, 36, 42), (15, 15, 18))
    R(d, cx - 80, BASE - 260, cx + 80, BASE, (200, 170, 60), 10)


def maison_ninja(d, cx=540):
    facades.maison(d, cx, 600, (250, 240, 220), (200, 40, 40))
    poly(d, [(cx - 380, BASE - 380), (cx, BASE - 600), (cx + 380, BASE - 380), (cx + 300, BASE - 420), (cx, BASE - 560),
             (cx - 300, BASE - 420)], (200, 40, 40))
    d.ellipse([(cx - 70) * SS, (BASE - 520) * SS, (cx + 70) * SS, (BASE - 380) * SS], fill=(250, 250, 250))
    pts = []                                                                       # un shuriken sur le fronton
    for k in range(8):
        r = 60 if k % 2 == 0 else 20
        a = math.radians(45 * k)
        pts.append(((cx + r * math.cos(a)) * SS, (BASE - 450 + r * math.sin(a)) * SS))
    d.polygon(pts, fill=(70, 70, 80))


def maison_sauna(d, cx=540):
    facades.maison(d, cx, 620, (230, 200, 160), (140, 90, 50))
    for k in range(3):                                                             # vapeur du jacuzzi
        x = cx + 230 + k * 40
        d.arc([(x - 30) * SS, (BASE - 300 - k * 40) * SS, (x + 30) * SS, (BASE - 220 - k * 40) * SS], 200, 340,
              fill=(250, 250, 250), width=10 * SS)
    R(d, cx + 180, BASE - 120, cx + 400, BASE, (60, 180, 245), 30)


facades.DESSINS.update({"ferme": ferme, "kebab": kebab, "armurerie": armurerie, "villa_geante": villa_geante,
                        "maison_noire": maison_noire, "maison_ninja": maison_ninja, "maison_sauna": maison_sauna})


# ───────────── le village de 114 maisons avec ses remparts (vue du dessus) ─────────────

PIERRE = (185, 180, 170)


def village_j5():
    occ = set(v2._OCC)
    extra = v2._placer([("x%d" % n, 1, 1) for n in range(114 - 53)], occ, marge=0)
    spe = v2._placer([("v1", 4, 3), ("v2", 4, 3), ("noire", 1, 1), ("ninja", 1, 1), ("sauna", 1, 1), ("ferme", 3, 2)],
                     occ, marge=0)
    gen = v2.GENERIQUES + [((float(ci), float(cj)), v2._COUL[n % 8], v2._TOITS[n % 5])
                           for n, (ci, cj) in enumerate(extra.values())]
    cases = [c for c, _, _ in gen] + [m[0] for m in v2.MAISONS.values()] + [(float(a), float(b)) for a, b in spe.values()]
    ia = max(-13, int(min(c[0] for c in cases)) - 1)
    ib = min(14, int(max(c[0] for c in cases)) + 2)
    ja = max(-13, int(min(c[1] for c in cases)) - 1)
    jb = min(14, int(max(c[1] for c in cases)) + 2)
    mur = set()
    for i in range(ia, ib + 1):
        mur.update({(i, ja), (i, jb)})
    for j in range(ja, jb + 1):
        mur.update({(ia, j), (ib, j)})
    portes = {c for c in mur if c[0] == 0 or c[1] == 0}
    mur = {c for c in mur if c not in portes and c[0] not in (iso.RIVIERE_I, iso.RIVIERE_I + 1)}

    orig_hab = v2.habillage

    def hab(d, objs, cs):
        orig_hab(d, objs, cs)
        for (i, j) in mur:
            objs.append((i + j + 1.0, lambda i=i, j=j: (iso.box(d, i, j, 1, 1, 42, PIERRE),
                                                         (i + j) % 2 == 0 and iso.box(d, i + 0.2, j + 0.2, 0.6, 0.6, 14,
                                                                                      PIERRE, z0=42))))
        for (i, j) in portes:                                   # une tour de chaque côté des portes
            for (a, b) in ((i - 1, j), (i + 1, j)) if j in (ja, jb) else ((i, j - 1), (i, j + 1)):
                objs.append((a + b + 1.2, lambda a=a, b=b: iso.box(d, a, b, 1, 1, 80, (170, 165, 155))))
        for nom, (i, j) in spe.items():
            if nom in ("v1", "v2"):
                objs.append((i + j + 3.6, lambda i=i, j=j: v2.villa(d, i + 0.5, j + 0.4, e=1.1)))
            elif nom == "noire":
                objs.append((i + j + 1, lambda i=i, j=j: iso.maison(d, i, j, 1.0, (45, 45, 50), (20, 20, 24))))
            elif nom == "ninja":
                objs.append((i + j + 1, lambda i=i, j=j: iso.maison(d, i, j, 1.0, (250, 240, 220), (200, 40, 40))))
            elif nom == "sauna":
                objs.append((i + j + 1, lambda i=i, j=j: iso.maison(d, i, j, 1.0, (230, 200, 160), (140, 90, 50))))
            elif nom == "ferme":
                objs.append((-50, lambda i=i, j=j: v2.champ(d, i, j, 3, 2, "ble")))
                objs.append((i + j + 1.5, lambda i=i, j=j: iso.box(d, i + 0.2, j + 0.2, 1.0, 0.8, 40, (190, 50, 45))))
        # l'enclos à oies de Moskow, collé au mur du fond
        for q in range(6):
            a, b = ia + 1.3 + q * 0.5, ja + 1.2 + (q % 2) * 0.3
            objs.append((a + b, lambda a=a, b=b, q=q: v2.oie(d, a, b, q % 2 == 0)))

    ancien_gen, ancien_carte = v2.GENERIQUES, iso.carte
    v2.GENERIQUES = gen
    v2.habillage = hab
    iso.carte = lambda etat: ancien_carte({**etat, "pont": True})
    try:
        return v2.village_j2(extra=("foot", "boulangerie", "boxe"))
    finally:
        v2.GENERIQUES, iso.carte, v2.habillage = ancien_gen, ancien_carte, orig_hab


_carte = {}


def vue5(z, center):
    if "c" not in _carte:
        _carte["c"] = village_j5()
    return iso.camera(_carte["c"], z, center)


# ───────────── vues de face : remparts, enclos, château abîmé ─────────────

def remparts_face(img, porte=True):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    y0, y1 = 880, BASE + 4
    d.rectangle([0, y0, W, y1], fill=PIERRE)
    for x in range(0, W, 130):
        d.rectangle([x, y0 - 70, x + 75, y0], fill=PIERRE)
    for row, y in enumerate(range(y0 + 50, y1, 64)):
        d.line([(0, y), (W, y)], fill=(150, 145, 135), width=3)
        for x in range(0 if row % 2 else 65, W, 130):
            d.line([(x, y), (x, y + 64)], fill=(150, 145, 135), width=3)
    if porte:
        d.chord([400, 1060, 680, 1340], 180, 360, fill=(100, 66, 40))
        d.rectangle([400, 1200, 680, y1], fill=(100, 66, 40))
        for x in range(430, 680, 50):
            d.line([(x, 1100), (x, y1)], fill=(80, 50, 30), width=4)
    lay = rue.contour(lay, 5)
    img.paste(lay, (0, 0), lay)


def oie_face(d, x, y, s=1.0, ph=0.0, lt=0.0, cri=False):
    b = abs(math.sin(lt * 6 + ph)) * 6 * s
    d.ellipse([x - 55 * s, y - 70 * s - b, x + 55 * s, y - b], fill=WHITE, outline=INK, width=4)
    d.line([(x + 25 * s, y - 50 * s - b), (x + 35 * s, y - 130 * s - b)], fill=WHITE, width=int(22 * s))
    d.ellipse([x + 15 * s, y - 160 * s - b, x + 60 * s, y - 115 * s - b], fill=WHITE, outline=INK, width=4)
    d.polygon([(x + 55 * s, y - 142 * s - b), (x + 90 * s, y - 134 * s - b), (x + 55 * s, y - 126 * s - b)],
              fill=(240, 150, 30))
    d.ellipse([x + 38 * s, y - 146 * s - b, x + 46 * s, y - 138 * s - b], fill=INK)
    if cri:
        d.text((x + 70 * s, y - 210 * s), "COUAC", font=FA(int(40 * s)), fill=YEL, anchor="mm", stroke_width=4,
               stroke_fill=INK)


def enclos(img, lt, cri=False):
    d = ImageDraw.Draw(img)
    for k in range(7):
        oie_face(d, 90 + k * 150, BASE + 150, 1.0, ph=k, lt=lt, cri=cri and k % 2 == 0)
    for x in range(20, W, 90):
        d.rectangle([x, BASE + 30, x + 18, BASE + 170], fill=(150, 100, 60), outline=INK, width=3)
    for y in (BASE + 60, BASE + 120):
        d.rectangle([0, y, W, y + 14], fill=(170, 120, 75), outline=INK, width=3)


def nuit(img, k=0.62):
    return Image.blend(img, Image.new("RGB", img.size, (10, 14, 40)), k)


def chateau_face(img, abime=False):
    facades.poser(img, facades.calque("chateau"), 1.0)
    if abime:
        d = ImageDraw.Draw(img)
        d.polygon([(560, 860), (700, 900), (760, 1010), (720, 1130), (790, 1250), (600, 1240), (540, 1100), (580, 990)],
                  fill=(50, 46, 42), outline=INK)
        for k in range(9):
            x = 520 + k * 38
            d.ellipse([x, BASE - 40 + (k % 3) * 8, x + 70, BASE + 20], fill=(170, 165, 155), outline=INK, width=3)


# ───────────── compteur (habitants + caisse, chaque mouvement affiché) ─────────────

MOUVEMENTS = [("s_couture", 1.0, -50000, "LES REMPARTS"), ("s_montee", 0.4, 5000, "REVENUS DU JOUR"),
              ("s_million", 0.5, 1000000, "@LIL RP EH"), ("s_enclos", 0.8, 10000, "@MSKOWW_91"),
              ("s_garde", 0.8, 2000, "@FUTUR POMPIER")]
DEPART = 125115           # fin du jour 4 → arrivée : 1 092 115 €


def caisse(t):
    v = DEPART
    for cle, dt, montant, _ in MOUVEMENTS:
        if cle in T and t >= T[cle] + dt:
            v += montant * ease((t - T[cle] - dt) / 0.6)
    return int(round(v))


def compteur(img, t):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([30, 215, 470, 398], radius=20, fill=(20, 20, 26), outline=WHITE, width=3)
    d.text((54, 245), "HABITANTS", font=FA(26), fill=(200, 200, 210), anchor="lm")
    d.text((54, 292), "114", font=FA(60), fill=YEL, anchor="lm")
    d.text((260, 245), "CAISSE", font=FA(26), fill=(200, 200, 210), anchor="lm")
    d.line([(240, 232), (240, 320)], fill=(80, 80, 90), width=3)
    d.text((54, 360), f"{caisse(t):,} €".replace(",", " "), font=FA(52), fill=GREEN, anchor="lm")
    d.text((260, 292), "DU VILLAGE", font=FA(26), fill=(150, 150, 160), anchor="lm")
    actifs = [(T[c] + dt, m, r) for c, dt, m, r in MOUVEMENTS if c in T and 0 <= t - T[c] - dt < 1.8]
    for debut, montant, raison in sorted(actifs)[-1:]:
        age = t - debut
        k = ease(age / 0.2) * ease((1.8 - age) / 0.3)
        txt = f"{'+' if montant > 0 else '−'}{abs(montant):,} €".replace(",", " ")
        col = GREEN if montant > 0 else (230, 60, 60)
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle([490, 290, 1050, 398], radius=22, fill=(20, 20, 26, int(235 * k)),
                             outline=col + (int(255 * k),), width=4)
        ld.text((515, 324), txt, font=FA(46), fill=col + (int(255 * k),), anchor="lm")
        ld.text((515, 372), raison, font=FA(28), fill=(220, 220, 230, int(255 * k)), anchor="lm")
        img.paste(lay, (0, 0), lay)


def avec_caisse(fn):
    def g(lt, dur):
        img = fn(lt, dur)
        compteur(img, T.get(fn.__name__, 0) + lt)
        return img
    g.__name__ = fn.__name__
    return g


def fond_remparts(lt=0.0):
    img = facades.decor().copy()
    remparts_face(img)
    return img


# ───────────── scènes ─────────────

def s_hook(lt, dur):
    img = dim(fond_remparts(), 0.5, blur=8, dark=0.7)
    e4.rph_gros_plan(img, lt)
    bubble(img, 540, 540, ["50 000 € DE REMPARTS ?", "JE LES FAIS TOMBER", "EN UNE NUIT"], 62, (lt + 0.3) / 0.3,
           tail_x=600)
    return shake(img, lt)


def s_couture(lt, dur):
    img, _ = vue5(push(lt, dur, 1.0, 1.15), (540, 960))
    titre2(img, "JOUR 5", "LES REMPARTS", k=lt / 0.25, y=470)
    tag(img, 540, 680, "114 HABITANTS · 114 MAISONS", 48, YEL, INK, rot=-3, k=(lt - 0.8) / 0.3)
    if lt > 2.6:
        tag(img, 540, 800, "ABONNÉ = TA MAISON · COMMENTAIRE = SUR MESURE", 34, WHITE, INK, rot=2, k=(lt - 2.6) / 0.3)
    return flash(img, lt)


MONTEE = [("m_ferme", "ferme", "Antoine", "LA FERME", "D'ANTOINE"),
          ("m_kebab", "kebab", "Al3ssio", "LE KEBAB", "D'ALESSIO"),
          ("m_armu", "armurerie", "clovis", "UNE ARMURERIE", "SOUS LA MAISON DE @CLOVIS"),
          ("m_villas", "villa_geante", "tangui_31kk", "DEUX VILLAS", "PISCINE GÉANTE · @ISSAM · @TANGUI_31KK")]
SUR_MESURE = [("maison_noire", "@MR X", "LUXE, TOUTE NOIRE"), ("maison_ninja", "@MKDLESIMPLE", "MAISON DE CHEF NINJA"),
              ("maison_sauna", "@AL3SSIO", "SAUNA + JACUZZI"), ("maison", "@TADINO", "SA MAISON")]


def s_montee(lt, dur):
    t0s = [T[c[0]] - T["s_montee"] for c in MONTEE]
    n = max([i for i, t in enumerate(t0s) if lt >= t], default=-1)
    if n < 0:
        img, _ = vue5(1.35, (560, 1000))
        titre2(img, "ET POURTANT", "LA PLUS BELLE JOURNÉE", k=lt / 0.25, y=470)
        return img
    l = lt - t0s[n]
    if n == len(MONTEE) - 1 and l > 0.9:                       # les maisons sur mesure des commentaires
        img = dim(facades.decor().copy(), 0.4, blur=4, dark=0.6)
        d = ImageDraw.Draw(img)
        titre2(img, "ET LES MAISONS", "SUR MESURE", k=1.0, y=470)
        for k, (kind, qui, quoi) in enumerate(SUR_MESURE):
            kk = ease((l - 0.9 - k * 0.15) / 0.2)
            if kk <= 0:
                continue
            x0, y0 = 70 + (k % 2) * 480, 640 + (k // 2) * 470
            d.rounded_rectangle([x0, y0, x0 + 460, y0 + 440], radius=24, fill=(250, 250, 252), outline=INK, width=5)
            vign = facades.decor().copy()
            facades.poser(vign, facades.calque(kind), 1.0)
            vign = vign.crop((0, 700, W, 1500)).resize((420, 311))
            img.paste(vign, (x0 + 20, y0 + 20))
            d.text((x0 + 230, y0 + 370), qui, font=FA(36), fill=INK, anchor="mm")
            d.text((x0 + 230, y0 + 412), quoi, font=FA(24), fill=(120, 120, 130), anchor="mm")
        return img
    cle, kind, pseudo, titre, role = MONTEE[n]
    img = facades.decor().copy()
    facades.poser(img, facades.calque(kind), v2.pop_k(l, t0=0.0, duree=0.35))
    v2.poussiere(img, l, t0=0.0, duree=0.35)
    if l > 0.35:
        v2.perso(img, pseudo, l - 0.35, x=840, sc=0.8, base=1920)
    titre2(img, "LE VILLAGE GRANDIT", titre, k=1.0, y=430)
    tag(img, 540, 640, role, 40, ROUGE, WHITE, rot=-3, k=(l - 0.15) / 0.2)
    return shake(img, l - 0.3, dur=0.2, amp=12)


def s_million(lt, dur):
    img, _ = vue5(1.2, (540, 960))
    img = dim(img, 0.6, blur=6, dark=0.75)
    tk = T["koko"] - T["s_million"]
    if lt < tk:
        v2.perso(img, "Lil RP eh", lt, x=760, sc=0.95, base=1960)
        big_number(img, (540, 560), counter(0, 1000000, lt - 0.3, 1.0, "{:,} €").replace(",", " "), 120, GREEN,
                   "@LIL RP EH", k=lt / 0.25)
        tag(img, 540, 760, "POUR ENTRER AU GOUVERNEMENT", 44, YEL, INK, rot=-3, k=(lt - 1.2) / 0.3)
        return flash(img, lt)
    l = lt - tk
    v2.perso(img, "kokoljii", l, x=760, sc=0.95, base=1960)
    titre2(img, "@KOKOLJII", "BRAS DROIT DU MAIRE", k=l / 0.25, y=480)
    return flash(img, l)


def s_descend(lt, dur):
    img = facades.decor().copy()
    chateau_face(img)
    x = 1180 - 360 * ease(lt / 0.8)
    v2.perso(img, "rph.49", lt, x=int(x), sc=0.85, base=1920)
    tag(img, 540, 470, "@RPH.49 DESCEND DE SON CHÂTEAU", 46, (120, 40, 60), WHITE, rot=-3, k=(lt - 0.3) / 0.25)
    return flash(img, lt)


def s_coup1(lt, dur):
    img = dim(fond_remparts(), 0.5, blur=8, dark=0.75)
    e4.rph_gros_plan(img, lt)
    bubble(img, 540, 540, ["DES REMPARTS EN CARTON.", "ÇA ARRÊTE MÊME PAS", "UN POUSSIN"], 60, lt / 0.25, tail_x=600)
    return shake(flash(img, lt), lt, dur=0.3, amp=8)


def s_remonte(lt, dur):
    img = facades.decor().copy()
    chateau_face(img)
    x = 820 + 360 * ease(lt / 1.2)
    v2.perso(img, "rph.49", lt, x=int(x), sc=0.85, base=1920)
    tag(img, 540, 470, "IL EN RAJOUTE", 56, RED, WHITE, rot=-3, k=(lt - 0.3) / 0.25)
    return img


def s_coup2(lt, dur):
    img = dim(facades.decor().copy(), 0.5, blur=8, dark=0.75)
    facades.poser(img, facades.calque("chateau"), 1.0)
    img = dim(img, 0.5, blur=6, dark=0.75)
    e4.rph_gros_plan(img, lt)
    bubble(img, 540, 540, ["UN MAIRE QUI VEND", "SES MINISTRES, ÇA FINIT", "DEHORS AVANT L'HIVER"], 58, lt / 0.25,
           tail_x=600)
    return shake(flash(img, lt), lt, dur=0.3, amp=8)


def s_silence(lt, dur):
    img = dim(fond_remparts(), 0.4, blur=6, dark=0.6)
    gros_plan_maire(img, lt, mouth="flat")
    return img


def s_echo(lt, dur):
    img = dim(fond_remparts(), 0.75, blur=10, dark=0.8)
    big_number(img, (540, 520), "« MÊME PAS UN POUSSIN »", 84, WHITE, k=1.0)
    d = ImageDraw.Draw(img)
    e4.poussin(d, 540, 1150, 3.0, lt)
    return img


def s_enclos(lt, dur):
    img = fond_remparts()
    enclos(img, lt)
    if lt > 1.2:
        v2.perso(img, "Mskoww_91", lt - 1.2, x=880, sc=0.75, base=1960)
    titre2(img, "L'IDÉE DE @MSKOWW_91", "UN ENCLOS À OIES", k=lt / 0.25, y=470)
    tag(img, 540, 680, "UNE OIE, ÇA ATTAQUE TOUT", 44, ROUGE, WHITE, rot=-3, k=(lt - 2.2) / 0.3)
    return img


def s_garde(lt, dur):
    img = nuit(fond_remparts(), 0.35)
    enclos(img, lt)
    v2.perso(img, "pompier", lt, x=300, sc=0.8, base=1960)
    titre2(img, "QUI GARDE LA PORTE ?", "LE FUTUR POMPIER", k=lt / 0.25, y=470)
    tag(img, 540, 680, "+2 000 € DE DON · 1RE GARDE", 44, YEL, INK, rot=-3, k=(lt - 1.4) / 0.3)
    return img


def s_doute(lt, dur):
    img, _ = vue5(1.25, (540, 960))
    img = dim(img, 0.5, blur=6, dark=0.7)
    gros_plan_maire(img, lt, mouth="flat")
    tag(img, 540, 470, "1 MILLION POUR UN FAUTEUIL…", 46, WHITE, INK, rot=-3, k=(lt - 0.6) / 0.3)
    return img


def s_nuit(lt, dur):
    img = nuit(fond_remparts(), 0.62)
    lay = e4.oie_zombie(int(1250 - 900 * ease(lt / 3.5)), 1180, 0.75, lt)
    img.paste(lay, (0, 0), lay)
    enclos(img, lt, cri=lt > 1.6)
    tag(img, 540, 470, "CETTE NUIT-LÀ", 60, (110, 255, 120), INK, rot=-3, k=lt / 0.25)
    if lt > 2.6:
        tag(img, 540, 620, "PAS UNE ENTRÉE", 52, WHITE, INK, rot=2, k=(lt - 2.6) / 0.3)
    return shake(img, lt - 1.6, dur=0.3, amp=6)


def s_chateau_nuit(lt, dur):
    img = facades.decor().copy()
    chateau_face(img)
    img = nuit(img, 0.62)
    lay = e4.oie_zombie(int(-200 + 520 * ease(lt / 2.0)), 1200, 0.7, lt)
    img.paste(lay, (0, 0), lay)
    tag(img, 540, 470, "LE SEUL ENDROIT DEHORS", 50, (110, 255, 120), INK, rot=-3, k=(lt - 0.3) / 0.3)
    return img


def s_matin(lt, dur):
    img = facades.decor().copy()
    chateau_face(img, abime=True)
    v2.perso(img, "rph.49", lt, x=220, sc=0.8, base=1960)
    titre2(img, "LE LENDEMAIN", "IL MANQUE UN MUR", k=lt / 0.25, y=470)
    tag(img, 540, 680, "@RPH.49 FRAPPE À LA PORTE", 46, (120, 40, 60), WHITE, rot=-3, k=(lt - 1.2) / 0.3)
    return shake(img, lt, dur=0.3, amp=8)


def s_vote(lt, dur):
    img, _ = vue5(1.15, (520, 960))
    img = dim(img, 0.6, blur=6, dark=0.75)
    titre2(img, "@RPH.49 VEUT RENTRER", "ON LUI OUVRE ?", k=lt / 0.25, y=470)
    d = ImageDraw.Draw(img)
    for k, (n, lab, col) in enumerate([("1", "OUI, ON LUI OUVRE", GREEN), ("2", "NON, IL RESTE DEHORS", RED)]):
        s = ease((lt - 0.6 - k * 0.5) / 0.2)
        if s <= 0:
            continue
        y = 700 + k * 200
        d.rounded_rectangle([80, y, 1000, y + 170], radius=28, fill=(250, 250, 252), outline=col, width=int(8 * s) + 1)
        d.text((150, y + 85), n, font=FA(96), fill=col, anchor="mm")
        d.text((230, y + 85), lab, font=FA(54), fill=INK, anchor="lm")
    if lt > 1.8:
        tag(img, 540, 1150, "VOTE EN COMMENTAIRE : 1 OU 2", 50, YEL, INK, rot=-2, k=(lt - 1.8) / 0.25)
    return img


SCENES = [("T'as claqué", s_hook), ("C'est ce que R P H", s_couture), ("Et pourtant c'était", s_montee),
          ("Le soir, Lil", s_million), ("R P H descend", s_descend), ("Des remparts en carton", s_coup1),
          ("Et en remontant", s_remonte), ("Un maire qui vend", s_coup2), ("Je dis rien", s_silence),
          ("Même pas un poussin", s_echo), ("Sauf qu'un mur", s_enclos), ("Mais alors qui garde", s_garde),
          ("Honnêtement", s_doute), ("Cette nuit-là", s_nuit), ("Alors elle va", s_chateau_nuit),
          ("Le lendemain", s_matin), ("On lui ouvre", s_vote)]


def main():
    import os
    v = CartoonVideo("village_ep05", "scripts/village/ep05.txt", "", "", corner="")
    v.length = (61.0, 63.0, 68.0)
    v.hook_head_start = 0.0
    v.sub_y = 0.69
    v.voice("output/_work_village_ep05/voice_duo.wav")
    apres = 0.0
    for k, (phrase, fn) in enumerate(SCENES):
        T[fn.__name__] = 0.0 if k == 0 else v.at(phrase, after=apres)
        apres = T[fn.__name__] + 0.01
    for cle, ph in (("m_ferme", "Antoine lance"), ("m_kebab", "Alessio son kebab"), ("m_armu", "Clovis une armurerie"),
                    ("m_villas", "et deux villas"), ("koko", "Kokoljii devient")):
        T[cle] = v.at(ph)
    for phrase, fn in SCENES:
        v.scenes.append((T[fn.__name__], avec_caisse(fn)))
    for t, nom, g in [(0.0, "impact", 1.0), (T["s_couture"], "whoosh", 0.7), (T["s_couture"] + 1.0, "tampon", 0.8),
                      (T["s_million"] + 0.5, "succes", 1.0), (T["koko"], "pop", 0.8), (T["s_descend"], "whoosh", 0.6),
                      (T["s_coup1"], "impact", 0.9), (T["s_coup2"], "impact", 1.0), (T["s_echo"], "rate", 0.7),
                      (T["s_enclos"], "pop", 0.8), (T["s_garde"], "notif", 0.7), (T["s_nuit"], "rate", 0.8),
                      (T["s_nuit"] + 1.6, "impact", 0.7), (T["s_chateau_nuit"], "whoosh", 0.7),
                      (T["s_matin"], "impact", 0.9), (T["s_vote"] + 0.6, "pop", 0.8), (T["s_vote"] + 1.1, "pop", 0.8),
                      (T["s_vote"] + 1.8, "notif", 0.8)]:
        v.sfx(t, nom, g)
    for cle in ("m_ferme", "m_kebab", "m_armu", "m_villas"):
        v.sfx(T[cle], "marteau", 0.5)
        v.sfx(T[cle] + 0.3, "impact", 0.45)
    for t0, fn in sorted(v.scenes, key=lambda x: x[0]):
        print(f"   {t0:5.1f}s {fn.__name__}")
    if os.environ.get("APERCU"):
        vues = []
        sc = sorted(v.scenes, key=lambda x: x[0])
        for k, (t0, fn) in enumerate(sc):
            fin = sc[k + 1][0] if k + 1 < len(sc) else v.dur
            t = t0 + min(2.6, (fin - t0) * 0.7)
            vues.append((t, v._image(int(t * 30)).convert("RGB").resize((270, 480))))
        if "m_villas" in T:
            t = T["m_villas"] + 1.9
            vues.append((t, v._image(int(t * 30)).convert("RGB").resize((270, 480))))
        pl = Image.new("RGB", (270 * 9, 480 * 2), (0, 0, 0))
        d = ImageDraw.Draw(pl)
        for k, (t, im) in enumerate(vues):
            pl.paste(im, ((k % 9) * 270, (k // 9) * 480))
            d.text(((k % 9) * 270 + 8, (k // 9) * 480 + 8), f"{t:.1f}s", font=FA(22), fill=YEL)
        pl.save(os.environ["APERCU"])
        print("planche :", os.environ["APERCU"])
        return
    v.render()


if __name__ == "__main__":
    main()
