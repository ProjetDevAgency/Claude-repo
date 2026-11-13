"""Fauché-les-Oies, jour 4 : les règles, l'oie zombie dans la grotte, les dons, le village qui grandit (96 maisons,
pont réparé, commerces des habitants), l'économie, puis RPH contre le maire et le vote armée / poussins / remparts.
Voix à deux : le maire (narrateur) et rph.49 (voix_duo.py, scripts/village/ep04.dial)."""
import math

from PIL import Image, ImageDraw, ImageFilter

import facades
import iso
import rue
import village_ep2 as v2
from cartoon import (FA, GREEN, INK, RED, SS, WHITE, YEL, CartoonVideo, big_number, bubble, counter, dim, ease, flash,
                     push, shake, tag)
from engine import H, W
from facades import BASE, R, fenetre, poly
from village import ROUGE, bouton_abonner, gros_plan_maire, titre2

T = {}
P = v2.PERSOS
P.update({
    "rph.49": (dict(shirt=(120, 40, 60), pants=(40, 30, 40), hair=(70, 50, 30), mouth="grin", brows="colere", arm=0.9),
               ["couronne"], "SEIGNEUR DU CHÂTEAU"),
    "Mskoww_91": (dict(shirt=(30, 30, 36), pants=(60, 110, 210), hair=(25, 20, 18), mouth="grin"), [], "CONCESSION MOTOCROSS"),
    "pompier": (dict(shirt=(200, 30, 40), pants=(40, 40, 60), hair=(40, 30, 25), cap=(200, 30, 40), mouth="grin"), [],
                "FUTUR POMPIER VOLONTAIRE"),
    "E'": (dict(shirt=(0, 80, 170), pants=(40, 40, 50), hair=(120, 50, 30), long_hair=True, mouth="grin"), [],
           "PATRONNE DU LIDL"),
    "Maé": (dict(shirt=(210, 30, 40), pants=(40, 40, 50), hair=(30, 25, 20), cap=(255, 200, 0), mouth="grin", arm=0.9), [],
            "C'EST LUI LE PATRON"),
    "Anthony": (dict(shirt=(235, 220, 190), pants=(30, 60, 140), hair=(40, 30, 25), mouth="grin"), ["maillot"],
                "STADE DE RUGBY + MAILLOTS"),
    "edenix100": (dict(shirt=(40, 140, 70), pants=(250, 250, 250), hair=(30, 25, 20), mouth="grin"), ["ballon", "maillot"],
                  "FC FAUCHÉ-LES-OIES"),
    "clovis": (dict(shirt=(60, 60, 70), pants=(40, 40, 50), hair=(20, 18, 16), mouth="grin"), [], "À CÔTÉ DE @MSKOWW_91"),
    "Waillox": (dict(shirt=(70, 110, 200), pants=(40, 40, 50), hair=(30, 25, 20), glasses=True, mouth="smile"),
                ["diplome"], "INGÉNIEUR · L'AÉROPORT"),
})


# ───────────── nouvelles façades (même style que les autres) ─────────────

def caserne(d, cx=540):
    x0, x1 = cx - 420, cx + 420
    R(d, x0, BASE - 560, x1, BASE, (200, 40, 45))
    R(d, x0 + 40, BASE - 540, x1 - 40, BASE - 450, (250, 250, 250), 12)
    d.text((cx * SS, (BASE - 495) * SS), "SAPEURS-POMPIERS", font=FA(int(62 * SS)), fill=(200, 40, 45), anchor="mm")
    for k in range(3):
        gx = x0 + 60 + k * 260
        R(d, gx, BASE - 400, gx + 220, BASE, (235, 235, 240))
        for r in range(5):
            R(d, gx + 10, BASE - 390 + r * 76, gx + 210, BASE - 330 + r * 76, (200, 200, 210))
    R(d, x1 - 120, BASE - 760, x1 - 40, BASE - 560, (180, 35, 40))            # tour de séchage
    R(d, x1 - 110, BASE - 740, x1 - 50, BASE - 700, (255, 220, 70))


def lidl(d, cx=540):
    x0, x1 = cx - 430, cx + 430
    R(d, x0, BASE - 470, x1, BASE, (245, 245, 248))
    R(d, x0, BASE - 470, x1, BASE - 400, (0, 80, 170))                        # bandeau bleu
    R(d, x0 + 40, BASE - 360, x1 - 260, BASE - 40, (150, 205, 245))           # vitrine
    R(d, x1 - 220, BASE - 300, x1 - 40, BASE, (120, 170, 210))                # porte vitrée
    # le logo : carré bleu, rond jaune cerclé de rouge, « Lidl »
    lx, ly, s = cx + 230, BASE - 640, 150
    R(d, lx - s, ly - s, lx + s, ly + s, (0, 80, 170), 18)
    d.ellipse([(lx - s * 0.82) * SS, (ly - s * 0.82) * SS, (lx + s * 0.82) * SS, (ly + s * 0.82) * SS], fill=(230, 20, 40))
    d.ellipse([(lx - s * 0.7) * SS, (ly - s * 0.7) * SS, (lx + s * 0.7) * SS, (ly + s * 0.7) * SS], fill=(255, 225, 0))
    d.text((lx * SS, (ly + 6) * SS), "Lidl", font=FA(int(118 * SS)), fill=(0, 60, 150), anchor="mm")
    R(d, lx - 8, ly + s, lx + 8, BASE - 470, (90, 90, 100))


def mcdo(d, cx=540):
    x0, x1 = cx - 420, cx + 420
    R(d, x0, BASE - 430, x1, BASE, (200, 30, 35))
    R(d, x0 - 20, BASE - 470, x1 + 20, BASE - 410, (110, 70, 45))             # auvent bois
    R(d, x0 + 50, BASE - 360, cx + 120, BASE - 60, (255, 230, 150))           # baie vitrée
    R(d, cx + 180, BASE - 320, cx + 340, BASE, (120, 80, 50), 10)
    # le grand « M » jaune sur son mât
    mx, my = cx - 170, BASE - 760
    R(d, mx - 10, my + 90, mx + 10, BASE - 470, (90, 90, 100))
    R(d, mx - 190, my - 140, mx + 190, my + 110, (200, 30, 35), 30)
    w = 26
    for a in (-1, 1):
        cxa = mx + a * 70
        d.arc([(cxa - 70) * SS, (my - 110) * SS, (cxa + 70) * SS, (my + 160) * SS], 180, 360, fill=(255, 200, 0), width=w * SS)
        R(d, cxa - 70 - w / 2 + 1, my + 25, cxa - 70 + w / 2, my + 90, (255, 200, 0))
        R(d, cxa + 70 - w / 2, my + 25, cxa + 70 + w / 2 - 1, my + 90, (255, 200, 0))


def maillots(d, cx=540):
    # poteaux de rugby derrière la boutique
    for x in (cx - 360, cx + 360):
        R(d, x - 12, BASE - 980, x + 12, BASE - 300, WHITE)
    R(d, cx - 360, BASE - 640, cx + 360, BASE - 616, WHITE)
    facades.boutique(d, cx, "BOUTIQUE DE MAILLOTS", mur=(240, 225, 195), enseigne=(30, 60, 130), store=(30, 60, 130),
                     vitrine=_vit_maillots)


def _vit_maillots(d, x0, y0, x1, y1):
    for k in range(3):
        x = x0 + 30 + k * 110
        poly(d, [(x, y0 + 60), (x + 90, y0 + 60), (x + 110, y0 + 100), (x + 90, y0 + 110), (x + 90, y1 - 30),
                 (x, y1 - 30), (x, y0 + 110), (x - 20, y0 + 100)], [(30, 60, 130), (200, 40, 50), (240, 240, 240)][k])


def clubfoot(d, cx=540):
    x0, x1 = cx - 410, cx + 410
    for x in (x0 - 40, x1 + 40):                                              # projecteurs
        R(d, x - 10, BASE - 1000, x + 10, BASE - 300, (90, 90, 100))
        R(d, x - 60, BASE - 1040, x + 60, BASE - 990, (250, 250, 210), 8)
    R(d, x0, BASE - 440, x1, BASE, (40, 140, 70))
    R(d, x0 + 40, BASE - 420, x1 - 40, BASE - 330, WHITE, 12)
    d.text((cx * SS, (BASE - 375) * SS), "FC FAUCHÉ-LES-OIES", font=FA(int(64 * SS)), fill=(40, 140, 70), anchor="mm")
    d.ellipse([(cx - 90) * SS, (BASE - 300) * SS, (cx + 90) * SS, (BASE - 120) * SS], fill=WHITE)
    for a in range(5):
        an = a * 2 * math.pi / 5
        x, y = cx + 52 * math.cos(an), BASE - 210 + 52 * math.sin(an)
        d.ellipse([(x - 20) * SS, (y - 20) * SS, (x + 20) * SS, (y + 20) * SS], fill=INK)
    for x in (x0 + 40, x1 - 200):
        R(d, x, BASE - 260, x + 160, BASE, (120, 80, 50), 8)


def aeroport(d, cx=540):
    R(d, cx + 220, BASE - 900, cx + 300, BASE - 380, (220, 220, 228))        # tour de contrôle
    R(d, cx + 180, BASE - 980, cx + 340, BASE - 880, (120, 170, 210), 14)
    R(d, cx - 460, BASE - 380, cx + 460, BASE, (225, 228, 235))              # terminal
    R(d, cx - 460, BASE - 380, cx + 460, BASE - 320, (40, 90, 170))
    d.text((cx * SS, (BASE - 350) * SS), "AÉROPORT DE FAUCHÉ-LES-OIES", font=FA(int(42 * SS)), fill=WHITE, anchor="mm")
    R(d, cx - 420, BASE - 280, cx + 420, BASE - 60, (150, 205, 245))
    # un avion qui décolle au-dessus
    ax, ay = cx - 160, BASE - 760
    d.rounded_rectangle([(ax - 240) * SS, (ay - 34) * SS, (ax + 240) * SS, (ay + 34) * SS], radius=34 * SS, fill=WHITE)
    poly(d, [(ax - 40, ay), (ax + 60, ay), (ax - 60, ay + 140), (ax - 140, ay + 140)], (200, 205, 215))
    poly(d, [(ax - 220, ay - 20), (ax - 180, ay - 20), (ax - 230, ay - 120), (ax - 260, ay - 120)], (40, 90, 170))
    for k in range(6):
        d.ellipse([(ax - 100 + k * 50) * SS, (ay - 12) * SS, (ax - 80 + k * 50) * SS, (ay + 8) * SS], fill=(120, 170, 210))


def usine_clovis(d, cx=540):
    facades.motocross(d, cx - 240)
    y1 = BASE
    x0 = cx + 30
    R(d, x0, y1 - 470, x0 + 420, y1, (190, 195, 205))
    for k in range(3):
        poly(d, [(x0 + k * 140, y1 - 470), (x0 + k * 140 + 70, y1 - 560), (x0 + (k + 1) * 140, y1 - 470)], (150, 155, 170))
    R(d, x0 + 300, y1 - 760, x0 + 360, y1 - 470, (140, 140, 150))
    R(d, x0 + 20, y1 - 440, x0 + 400, y1 - 350, (90, 60, 160), 12)
    d.text(((x0 + 210) * SS, (y1 - 395) * SS), "USINE DE CLOVIS", font=FA(int(46 * SS)), fill=WHITE, anchor="mm")
    R(d, x0 + 40, y1 - 300, x0 + 220, y1, (110, 115, 130))


facades.DESSINS.update({"caserne": caserne, "lidl": lidl, "mcdo": mcdo, "maillots": maillots, "clubfoot": clubfoot,
                        "aeroport": aeroport, "usine_clovis": usine_clovis})


# ───────────── le village de 96 maisons, pont réparé ─────────────

def village_j4():
    occ = set(v2._OCC)
    extra = v2._placer([("x%d" % n, 1, 1) for n in range(96 - 53)], occ, marge=0)
    gen = v2.GENERIQUES + [((float(ci), float(cj)), v2._COUL[n % 8], v2._TOITS[n % 5])
                           for n, (ci, cj) in enumerate(extra.values())]
    ancien_gen, ancien_carte = v2.GENERIQUES, iso.carte
    v2.GENERIQUES = gen
    iso.carte = lambda etat: ancien_carte({**etat, "pont": True})
    try:
        return v2.village_j2(extra=("foot", "boulangerie", "boxe"))
    finally:
        v2.GENERIQUES, iso.carte = ancien_gen, ancien_carte


_carte = {}


def vue4(z, center):
    if "c" not in _carte:
        _carte["c"] = village_j4()
    return iso.camera(_carte["c"], z, center)


# ───────────── compteurs permanents (sous la barre TikTok) ─────────────

# Chaque mouvement de la caisse : (repère, décalage s, montant, raison). Tout est affiché à l'écran, rien de caché.
MOUVEMENTS = [("s_camera", 0.3, -500, "LES CAMÉRAS"), ("d_mosk", 0.0, 5000, "@MSKOWW_91"),
              ("d_koko", 0.0, 10000, "@KOKOLJII"), ("d_clovis", 0.0, 2000, "@CLOVIS"), ("d_t0", 0.0, 100000, "@T_0"),
              ("b_pont", 0.3, -2000, "LE PONT"),
              ("b_caserne", 0.3, -5000, "LA CASERNE"), ("s_eco", 1.6, 5000, "REVENUS DU JOUR")]
DEPART = 10615          # fin du jour 3 → arrivée : 125 115 €


def caisse(t):
    v = DEPART
    for cle, dt, montant, _ in MOUVEMENTS:
        if cle in T and t >= T[cle] + dt:
            v += montant * ease((t - T[cle] - dt) / 0.5)
    return int(round(v))


def compteur(img, t):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([30, 215, 470, 398], radius=20, fill=(20, 20, 26), outline=WHITE, width=3)
    d.text((54, 245), "HABITANTS", font=FA(26), fill=(200, 200, 210), anchor="lm")
    d.text((54, 292), "96", font=FA(60), fill=YEL, anchor="lm")
    d.text((140, 298), "/ 100", font=FA(32), fill=(150, 150, 160), anchor="lm")
    d.text((260, 245), "CAISSE", font=FA(26), fill=(200, 200, 210), anchor="lm")
    d.line([(240, 232), (240, 320)], fill=(80, 80, 90), width=3)
    d.text((54, 360), f"{caisse(t):,} €".replace(",", " "), font=FA(58), fill=GREEN, anchor="lm")
    d.text((260, 292), "DU VILLAGE", font=FA(26), fill=(150, 150, 160), anchor="lm")
    # le dernier mouvement, à droite du compteur, 1,8 s
    for cle, dt, montant, raison in MOUVEMENTS:
        if cle not in T:
            continue
        age = t - T[cle] - dt
        if 0 <= age < 1.8:
            k = ease(age / 0.2) * ease((1.8 - age) / 0.3)
            txt = f"{'+' if montant > 0 else '−'}{abs(montant):,} €".replace(",", " ")
            col = GREEN if montant > 0 else (230, 60, 60)
            lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
            ld = ImageDraw.Draw(lay)
            ld.rounded_rectangle([490, 290, 1050, 398], radius=22, fill=(20, 20, 26, int(235 * k)), outline=col + (int(255 * k),),
                                 width=4)
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


# ───────────── dessins : grotte, oie zombie, poussins ─────────────

_cav = {}


def caverne():
    """Intérieur de la grotte : roche sombre, stalactites, flaques."""
    if "c" in _cav:
        return _cav["c"].copy()
    im = Image.new("RGB", (W, H), (22, 18, 20))
    d = ImageDraw.Draw(im)
    for k in range(60):
        x, y, r = (k * 173) % 1180 - 50, (k * 97) % 1920, 120 + (k * 37) % 160
        c = 30 + (k * 13) % 30
        d.ellipse([x - r, y - r * 0.7, x + r, y + r * 0.7], fill=(c, c - 6, c - 4))
    for k in range(14):                                   # stalactites
        x = 40 + k * 78
        h = 160 + (k * 53) % 220
        d.polygon([(x - 34, 0), (x + 34, 0), (x + 4, h)], fill=(48, 42, 44))
    d.rectangle([0, 1480, W, H], fill=(30, 26, 26))
    for k in range(5):
        x = 120 + k * 210
        d.ellipse([x - 90, 1560 + (k % 2) * 60, x + 90, 1600 + (k % 2) * 60], fill=(40, 60, 70))
    _cav["c"] = im
    return im.copy()


def torche(img, x, y, ang, lt):
    """Faisceau de lampe qui tremble."""
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    a = ang + 0.06 * math.sin(lt * 9) + 0.03 * math.sin(lt * 23)
    L = 1500
    p1 = (x + L * math.cos(a - 0.28), y + L * math.sin(a - 0.28))
    p2 = (x + L * math.cos(a + 0.28), y + L * math.sin(a + 0.28))
    d.polygon([(x, y), p1, p2], fill=(255, 240, 180, 95))
    lay = lay.resize((W // 4, H // 4)).filter(ImageFilter.GaussianBlur(5)).resize((W, H), Image.BILINEAR)
    img.paste(lay, (0, 0), lay)


_vig = {}


def vignette(img, force=0.75):
    if "m" not in _vig:                       # le masque ne change pas : calculé une seule fois
        m = Image.new("L", (W // 4, H // 4), 0)
        ImageDraw.Draw(m).ellipse([-50, 25, W // 4 + 50, H // 4 - 25], fill=255)
        _vig["m"] = m.filter(ImageFilter.GaussianBlur(40)).resize((W, H), Image.BILINEAR)
    noir = Image.new("RGB", img.size, (0, 0, 0))
    return Image.composite(img, Image.blend(img, noir, force), _vig["m"])


def oie_zombie(cx, cy, s, lt, yeux=1.0):
    """Une oie au cou tordu, plumes arrachées, yeux verts qui brillent. Renvoie un calque RGBA (avec contour)."""
    lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)

    def P(x, y):
        return ((cx + x * s) * SS, (cy + y * s) * SS)

    corps = (200, 210, 195)
    d.ellipse([*P(-170, -40), *P(170, 150)], fill=corps)
    d.polygon([P(120, 0), P(230, -40), P(200, 60)], fill=corps)                       # queue
    for k in range(4):                                                                 # trous (plumes arrachées)
        x, y = -100 + k * 60, 20 + (k % 2) * 50
        d.ellipse([*P(x - 18, y - 14), *P(x + 18, y + 14)], fill=(140, 160, 120))
    tw = 0.25 * math.sin(lt * 5)
    pts = [P(-110, -10), P(-150, -140), P(-90 + 30 * tw, -230), P(-160, -320)]       # cou tordu
    d.line(pts, fill=corps, width=int(52 * s * SS), joint="curve")
    hx, hy = -175, -345
    d.ellipse([*P(hx - 55, hy - 45), *P(hx + 55, hy + 45)], fill=corps)
    d.polygon([P(hx - 50, hy + 5), P(hx - 140, hy + 25), P(hx - 48, hy + 35)], fill=(230, 140, 40))
    for k, (ex, ey) in enumerate(((hx - 18, hy - 10), (hx + 22, hy - 14))):
        d.ellipse([*P(ex - 14, ey - 14), *P(ex + 14, ey + 14)], fill=(int(60 + 140 * yeux), 255, int(60 + 60 * yeux)))
    for x in (-60, 40):                                                                 # pattes
        d.line([P(x, 140), P(x - 10, 230)], fill=(230, 140, 40), width=int(14 * s * SS))
        d.polygon([P(x - 50, 230), P(x + 30, 230), P(x - 10, 250)], fill=(230, 140, 40))
    lay = rue.contour(lay.resize((W, H), Image.LANCZOS), 6)
    # halo vert autour des yeux
    halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    gx, gy = cx + hx * s, cy + hy * s
    r = 120 * s * (1 + 0.15 * math.sin(lt * 7)) * yeux
    hd.ellipse([gx - r, gy - r, gx + r, gy + r], fill=(80, 255, 120, 110))
    halo = halo.resize((W // 4, H // 4)).filter(ImageFilter.GaussianBlur(10)).resize((W, H), Image.BILINEAR)
    halo.alpha_composite(lay)
    return halo


def poussin(d, x, y, s, lt, ph=0.0):
    b = abs(math.sin(lt * 10 + ph)) * 10 * s
    d.ellipse([x - 40 * s, y - 70 * s - b, x + 40 * s, y - b], fill=(255, 220, 40), outline=INK, width=4)
    d.ellipse([x - 26 * s, y - 112 * s - b, x + 26 * s, y - 62 * s - b], fill=(255, 225, 60), outline=INK, width=4)
    d.polygon([(x + 22 * s, y - 92 * s - b), (x + 44 * s, y - 86 * s - b), (x + 22 * s, y - 80 * s - b)], fill=(240, 140, 30))
    d.ellipse([x + 4 * s, y - 98 * s - b, x + 12 * s, y - 90 * s - b], fill=INK)
    d.line([(x - 10 * s, y - b), (x - 12 * s, y + 14 * s)], fill=(240, 140, 30), width=4)
    d.line([(x + 10 * s, y - b), (x + 12 * s, y + 14 * s)], fill=(240, 140, 30), width=4)


def rph_gros_plan(img, lt, mouth=None):
    v2.perso(img, "rph.49", lt, x=560, sc=2.1, base=2560)
    return img


# ───────────── scènes ─────────────

def s_regles(lt, dur):
    img = facades.decor().copy()
    tc, tp = T["r_com"] - T["s_regles"], T["r_par"] - T["s_regles"]
    if lt < tc:              # 1. abonné → une maison tombe du ciel
        bouton_abonner(img, 540, 450, lt / 0.25)
        k = ease((lt - 0.4) / 0.35)
        if k > 0:
            lay = facades.calque("maison")
            img.paste(lay, (0, int(-900 * (1 - k))), lay)
            if k >= 1:
                v2.poussiere(img, lt - 0.75, t0=0.0, duree=0.3)
                v2.etiquette(img, 540, 760, "@TOI")
        titre2(img, "TU T'ABONNES", "T'AS TA MAISON", k=(lt - 0.2) / 0.25, y=560)
        return shake(img, lt - 0.75, dur=0.25, amp=10)
    if lt < tp:              # 2. commentaire → maison sur mesure
        l = lt - tc
        lay = facades.calque("villa")
        facades.poser(img, lay, v2.pop_k(l, t0=0.3, duree=0.35))
        bubble(img, 540, 470, ["« JE VEUX", "UNE PISCINE ! »"], 58, l / 0.25, tail_x=640)
        titre2(img, "TU COMMENTES", "SUR MESURE", k=(l - 0.6) / 0.25, y=700)
        return shake(img, l - 0.3, dur=0.25, amp=10)
    l = lt - tp              # 3. partage → tu proposes ce qu'on construit
    facades.poser(img, facades.calque("villa"), 1.0)
    d = ImageDraw.Draw(img)
    k = ease(l / 0.3)
    d.rectangle([520, 1380 - 330 * k, 560, 1400], fill=(120, 80, 50))
    if k >= 1:
        d.rounded_rectangle([250, 960, 830, 1130], radius=20, fill=WHITE, outline=INK, width=6)
        d.text((540, 1010), "TA PROPOSITION", font=FA(46), fill=INK, anchor="mm")
        d.text((540, 1080), "ICI BIENTÔT", font=FA(40), fill=ROUGE, anchor="mm")
    tag(img, 540, 450, "↗ PARTAGER", 60, WHITE, INK, rot=-3, k=l / 0.2)
    titre2(img, "TU PARTAGES", "TU CHOISIS QUOI CONSTRUIRE", k=(l - 0.3) / 0.25, y=560)
    return img


def s_grotte(lt, dur):
    img = caverne()
    z = push(lt, dur, 1.0, 1.15)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    v2.perso(lay, "pkmoi", lt, x=380, sc=1.25, base=1900)
    img.paste(lay, (0, 0), lay)
    torche(img, 470, 1150, -0.55, lt)
    if z > 1.0:
        w, h = int(W / z), int(H / z)
        img = img.crop(((W - w) // 2, (H - h) // 2, (W - w) // 2 + w, (H - h) // 2 + h)).resize((W, H), Image.LANCZOS)
    img = vignette(img, 0.8)
    titre2(img, "CETTE NUIT", "PKMOI ENTRE DANS LA GROTTE", k=lt / 0.3, y=440)
    tr = T["ressorti"] - T["s_grotte"]
    if lt > tr:
        tag(img, 540, 760, "IL EST PAS RESSORTI SEUL…", 52, RED, WHITE, rot=-3, k=(lt - tr) / 0.25)
    return shake(img, lt, dur=0.3, amp=6)


def s_oie(lt, dur):
    img = caverne()
    img = Image.blend(img, Image.new("RGB", img.size, (0, 0, 0)), 0.5)
    yeux = ease(lt / 0.4)
    k = ease((lt - 0.6) / 0.6)
    oie = oie_zombie(600, 1250 - 120 * k, 1.5 + 0.35 * k, lt, yeux)
    img.paste(oie, (0, 0), oie)
    img = vignette(img, 0.7)
    tz = T["zombie"] - T["s_oie"]
    if lt > tz:
        big_number(img, (540, 480), "UNE OIE ZOMBIE", 120, (110, 255, 120), k=(lt - tz) / 0.25, rot=-3)
        return shake(flash(img, lt - tz), lt - tz, dur=0.5, amp=14)
    return shake(img, lt, dur=0.2, amp=4)


def s_camera(lt, dur):
    img = caverne()
    x = 1300 - 900 * ease(lt / max(dur, 0.1))
    oie = oie_zombie(x, 1300, 0.9, lt)
    img.paste(oie, (0, 0), oie)
    img = img.convert("L").convert("RGB")
    img = Image.blend(img, Image.new("RGB", img.size, (40, 90, 50)), 0.25)
    d = ImageDraw.Draw(img)
    for y in range(0, H, 6):                                    # lignes de balayage
        d.line([(0, y), (W, y)], fill=(0, 0, 0), width=2)
    if int(lt * 2) % 2 == 0:
        d.ellipse([70, 430, 110, 470], fill=(230, 30, 40))
    d.text((130, 450), "REC", font=FA(46), fill=WHITE, anchor="lm")
    d.text((1010, 450), "CAM 2 · GROTTE", font=FA(40), fill=WHITE, anchor="rm")
    d.text((1010, 1250), f"03:12:{47 + int(lt):02d}", font=FA(40), fill=WHITE, anchor="rm")
    tag(img, 540, 620, "ON A TOUT FILMÉ", 64, YEL, INK, rot=-3, k=lt / 0.25)
    tc = T["cameras"] - T["s_camera"]
    if lt > tc:
        tag(img, 540, 760, "LES CAMÉRAS · GRÂCE À VOS DONS", 46, WHITE, INK, rot=2, k=(lt - tc) / 0.25)
    return img


def s_dons(lt, dur):
    img, _ = vue4(1.0, (540, 960))
    img = dim(img, 0.85)
    titre2(img, "LES DONS", "ONT EXPLOSÉ", k=lt / 0.25, y=430)
    d = ImageDraw.Draw(img)
    rows = [("@MSKOWW_91", "", "+5 000 €", "d_mosk"), ("@KOKOLJII", "POUR PAS PAYER SES IMPÔTS", "+10 000 €", "d_koko"),
            ("@CLOVIS", "", "+2 000 €", "d_clovis"), ("@T_0", "POUR UNE MONTAGNE RUSSE", "+100 000 €", "d_t0")]
    for k, (qui, pourquoi, combien, cle) in enumerate(rows):
        t0 = T[cle] - T["s_dons"]
        if lt < t0:
            continue
        s = 0.7 + 0.3 * ease((lt - t0) / 0.2)
        y = 650 + k * 165
        d.rounded_rectangle([90, y, 990, y + 140], radius=26, fill=(250, 250, 252))
        d.text((130, y + (52 if pourquoi else 70)), qui, font=FA(int(46 * s)), fill=INK, anchor="lm")
        if pourquoi:
            d.text((130, y + 104), pourquoi, font=FA(26), fill=(120, 120, 130), anchor="lm")
        d.text((950, y + 70), combien, font=FA(int(60 * s)), fill=GREEN, anchor="rm")
    return img


CONSTRUIT = [  # repère, façade, pseudo (None = pas de perso), titre, rôle
    ("b_maisons", None, None, "96 MAISONS", "1 ABONNÉ = 1 MAISON"),
    ("b_pont", "pont", None, "LE PONT", "ENFIN RÉPARÉ"),
    ("b_caserne", "caserne", "pompier", "LA CASERNE", "DU FUTUR POMPIER"),
    ("b_lidl", "lidl", "E'", "LE LIDL", "DE @E'"),
    ("b_mcdo", "mcdo", "Maé", "LE MCDO DE @MAÉ", "C'EST LUI LE PATRON"),
    ("b_rugby", "maillots", "Anthony", "LE STADE DE RUGBY", "+ LA BOUTIQUE DE @ANTHONY"),
    ("b_foot", "clubfoot", "edenix100", "LE CLUB DE FOOT", "DE @EDENIX100"),
    ("b_aero", "aeroport", "Waillox", "L'AÉROPORT", "DE @WAILLOX, INGÉNIEUR"),
    ("b_usine", "usine_clovis", "clovis", "L'USINE DE @CLOVIS", "À CÔTÉ DE @MSKOWW_91"),
]


def pont_face(img, k):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1395, W, 1640], fill=(70, 140, 210))
    for y in range(1420, 1640, 40):
        d.line([(0, y), (W, y + 6)], fill=(110, 170, 230), width=4)
    if k <= 0:
        return
    s = 0.6 + 0.4 * k
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.rectangle([60, 1260, 1020, 1340], fill=(170, 165, 155))
    for x in (60, 380, 700):
        ld.chord([x, 1300, x + 320, 1600], 180, 360, fill=(70, 140, 210))
        ld.rectangle([x + 280, 1300, x + 340, 1640], fill=(170, 165, 155))
    ld.rectangle([60, 1230, 1020, 1262], fill=(140, 135, 128))
    lay = rue.contour(lay, 5)
    if s < 1:
        lay = lay.resize((int(W * s), int(H * s))).crop((0, 0, W, H))
    img.paste(lay, (0, 0), lay)


def s_construit(lt, dur):
    t0s = [T[c[0]] - T["s_construit"] for c in CONSTRUIT]
    n = max([i for i, t in enumerate(t0s) if lt >= t], default=-1)
    if n < 0:
        img = facades.decor().copy()
        titre2(img, "ALORS", "LE VILLAGE A CHANGÉ", k=lt / 0.25, y=470)
        return img
    cle, kind, pseudo, titre, role = CONSTRUIT[n]
    l = lt - t0s[n]
    img = facades.decor().copy()
    if kind is None:
        lay = rue.panneau_ville("FAUCHÉ-LES-OIES", 96, y=820, s=1.0).resize((W, H), Image.LANCZOS)
        img.paste(lay, (0, 0), lay)
    elif kind == "pont":
        pont_face(img, ease(l / 0.4))
    else:
        facades.poser(img, facades.calque(kind), v2.pop_k(l, t0=0.0, duree=0.35))
        v2.poussiere(img, l, t0=0.0, duree=0.35)
    if pseudo and l > 0.35:
        v2.perso(img, pseudo, l - 0.35, x=820, sc=0.8, base=1920)
    titre2(img, "LE VILLAGE A CHANGÉ", titre, k=1.0, y=430)
    tag(img, 540, 640, role, 44, ROUGE, WHITE, rot=-3, k=(l - 0.15) / 0.2)
    return shake(img, l - 0.3, dur=0.2, amp=12)


ECONOMIE = [("ÉPICERIE", 480), ("MCDO · @MAÉ", 400), ("LIDL · @E'", 500), ("MAILLOTS · @ANTHONY", 150),
            ("FOOT · @EDENIX100", 250), ("MONTAGNE RUSSE · @T_0", 1000), ("AÉROPORT · @WAILLOX", 1700),
            ("USINE · @CLOVIS", 520)]


def s_eco(lt, dur):
    img, _ = vue4(push(lt, dur, 1.0, 1.08), (540, 960))
    img = dim(img, 0.6, blur=6, dark=0.7)
    titre2(img, "L'ÉCONOMIE DU VILLAGE", "+" + counter(0, 5000, lt - 0.2, 1.4, "{:,} €").replace(",", " ") + " / JOUR",
           k=lt / 0.25, y=430)
    d = ImageDraw.Draw(img)
    for k, (nom, eur) in enumerate(ECONOMIE):
        t0 = 0.2 + k * 0.17
        if lt < t0:
            continue
        y = 700 + k * 78
        d.rounded_rectangle([110, y, 970, y + 64], radius=16, fill=(250, 250, 252))
        d.text((140, y + 32), nom, font=FA(34), fill=INK, anchor="lm")
        d.text((940, y + 32), f"+{eur:,} €".replace(",", " "), font=FA(36), fill=GREEN, anchor="rm")
    return img


def s_ricane(lt, dur):
    img = Image.blend(caverne(), Image.new("RGB", (W, H), (0, 0, 0)), 0.7)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(lay).ellipse([340, 900, 740, 1200], fill=(90, 255, 120, 90))
    lay = lay.filter(ImageFilter.GaussianBlur(60))
    img.paste(lay, (0, 0), lay)
    d = ImageDraw.Draw(img)
    for k in range(3):
        if lt > 0.25 + k * 0.3:
            x = 260 + k * 280 + 8 * math.sin(lt * 30 + k)
            d.text((x, 1040 + 10 * math.sin(lt * 20 + k)), "HÉ", font=FA(96), fill=(140, 255, 150), anchor="mm")
    tm = T["maxence"] - T["s_ricane"]
    if lt > tm:
        tag(img, 540, 620, "@MAXENCE ?", 80, (110, 255, 120), INK, rot=-4, k=(lt - tm) / 0.25)
    titre2(img, "MAIS AU FOND DE LA GROTTE", "QUELQU'UN RICANE", k=lt / 0.25, y=430)
    return shake(img, lt, dur=dur, amp=5)


def s_chateau(lt, dur):
    img = facades.decor().copy()
    facades.poser(img, facades.calque("chateau"), 1.0)
    x = 1180 - 360 * ease(lt / 0.8)
    v2.perso(img, "rph.49", lt, x=int(x), sc=0.85, base=1920)
    titre2(img, "ET LÀ…", "@RPH.49 DÉBARQUE", k=lt / 0.25, y=430)
    tag(img, 540, 640, "SEIGNEUR DU CHÂTEAU", 48, (120, 40, 60), WHITE, rot=-3, k=(lt - 0.5) / 0.25)
    return flash(img, lt)


def s_rph1(lt, dur):
    img = dim(facades.decor().copy(), 0.4, blur=8, dark=0.75)
    facades.poser(img, facades.calque("chateau"), 1.0)
    img = dim(img, 0.5, blur=6, dark=0.75)
    rph_gros_plan(img, lt)
    tm = T["moi_armee"] - T["s_rph1"]
    if lt < tm:
        bubble(img, 540, 520, ["DES POUSSINS ?", "PATHÉTIQUE."], 70, lt / 0.25, tail_x=600)
    else:
        bubble(img, 540, 520, ["MOI, UNE VRAIE ARMÉE :", "100 000 €.", "DES HOMMES, DES VRAIS."], 60, (lt - tm) / 0.25,
               tail_x=600)
    return shake(flash(img, lt), lt, dur=0.3, amp=8)


def s_maire(lt, dur):
    img, _ = vue4(1.3, (520, 950))
    img = dim(img, 0.4, blur=8, dark=0.85)
    tp = T["poussins"] - T["s_maire"]
    if lt < tp:
        lay = rue.panneau_ville("FAUCHÉ-LES-OIES", 96, y=560, s=0.9).resize((W, H), Image.LANCZOS)
        img.paste(lay, (0, 0), lay)
        tag(img, 540, 1080, "PAS ASSEZ D'HOMMES", 64, RED, WHITE, rot=-3, k=(lt - 0.6) / 0.25)
        return img
    l = lt - tp
    gros_plan_maire(img, l, arm=0.95, mouth="o" if int(l * 7) % 2 else "grin")
    d = ImageDraw.Draw(img)
    for k in range(10):
        if l > 0.1 * k:
            poussin(d, 90 + k * 100, 1880 - (k % 2) * 40, 1.1, l, ph=k)
    titre2(img, "LE MAIRE PROPOSE", "UNE ARMÉE DE POUSSINS", k=l / 0.25, y=430)
    big_number(img, (540, 700), "10 000 €", 130, GREEN, k=(l - 0.6) / 0.25, rot=-3)
    return shake(img, l, dur=0.3, amp=8)


def s_rph2(lt, dur):
    img = dim(facades.decor().copy(), 0.5, blur=8, dark=0.75)
    rph_gros_plan(img, lt)
    bubble(img, 540, 520, ["VOTEZ POUR LUI…", "ET VOUS FINIREZ", "EN OMELETTE"], 62, lt / 0.25, tail_x=600)
    d = ImageDraw.Draw(img)
    k = ease((lt - 0.8) / 0.3)
    if k > 0:                                         # l'œuf au plat
        cx, cy, r = 820, 900, 120 * k
        d.ellipse([cx - r * 1.3, cy - r, cx + r * 1.3, cy + r], fill=WHITE, outline=INK, width=5)
        d.ellipse([cx - r * 0.45, cy - r * 0.45, cx + r * 0.45, cy + r * 0.45], fill=(255, 190, 30), outline=INK, width=4)
    return shake(img, lt, dur=0.3, amp=8)


def s_vote(lt, dur):
    img, _ = vue4(1.15, (520, 960))
    img = dim(img, 0.6, blur=6, dark=0.75)
    titre2(img, "LA GROTTE CACHE UNE OIE ZOMBIE", "ON FAIT QUOI ?", k=lt / 0.25, y=430)
    choix = [("1", "L'ARMÉE DE @RPH.49", "100 000 €", RED, "v1"), ("2", "LES POUSSINS DU MAIRE", "10 000 €", GREEN, "v2"),
             ("3", "LES REMPARTS", "50 000 €", YEL, "v3")]
    d = ImageDraw.Draw(img)
    for k, (n, lab, prix, col, cle) in enumerate(choix):
        t0 = T[cle] - T["s_vote"]
        if lt < t0:
            continue
        s = ease((lt - t0) / 0.2)
        y = 680 + k * 190
        d.rounded_rectangle([80, y, 1000, y + 160], radius=28, fill=(250, 250, 252), outline=col, width=int(8 * s) + 1)
        d.text((140, y + 80), n, font=FA(90), fill=col, anchor="mm")
        d.text((210, y + 60), lab, font=FA(46), fill=INK, anchor="lm")
        d.text((210, y + 118), prix, font=FA(40), fill=(120, 120, 130), anchor="lm")
    tv = T["vote_com"] - T["s_vote"]
    if lt > tv:
        tag(img, 540, 1290, "VOTE EN COMMENTAIRE : 1, 2 OU 3", 50, YEL, INK, rot=-2, k=(lt - tv) / 0.25)
    return img


def main():
    v = CartoonVideo("village_ep04", "scripts/village/ep04.txt", "", "", corner="")
    v.length = (68.0, 76.0, 84.0)
    v.hook_head_start = 0.0
    v.sub_y = 0.69
    v.voice("output/_work_village_ep04/voice_duo.wav")
    sc = [("À Fauché-les-Oies, tu", s_regles), ("Et cette nuit", s_grotte), ("Une oie. Les yeux", s_oie),
          ("Et on a tout filmé", s_camera), ("Les dons ont explosé", s_dons), ("Alors le village a changé", s_construit),
          ("Toutes ces entreprises", s_eco), ("Mais au fond", s_ricane), ("Et là, R P H", s_chateau),
          ("Une oie zombie, et le maire", s_rph1), ("Sauf qu'on est", s_maire), ("Des poussins", s_rph2),
          ("Ou troisième choix", s_vote)]
    for phrase, fn in sc:
        T[fn.__name__] = v.at(phrase, after=T.get("s_maire", 0.0) if fn is s_rph2 else 0.0)
    T["r_com"], T["r_par"] = v.at("Tu commentes"), v.at("Tu partages")
    T["ressorti"], T["zombie"], T["cameras"] = v.at("Il est pas ressorti"), v.at("Une oie zombie"), v.at("Grâce à vos dons")
    T["d_mosk"], T["d_koko"] = v.at("Cinq mille de"), v.at("Dix mille de")
    T["d_clovis"], T["d_t0"] = v.at("Deux mille de"), v.at("Et cent mille de")
    for cle, ph in (("b_maisons", "Quatre-vingt-seize maisons"), ("b_pont", "Le pont"), ("b_caserne", "La caserne"),
                    ("b_lidl", "Le Lidl"), ("b_mcdo", "Le McDo"), ("b_rugby", "Le stade de rugby"),
                    ("b_foot", "Le club de foot"), ("b_aero", "L'aéroport"), ("b_usine", "Et l'usine")):
        T[cle] = v.at(ph)
    T["maxence"] = v.at("Maxence")
    T["moi_armee"] = v.at("Moi, je lève")
    T["poussins"] = v.at("Alors le maire propose")
    T["v3"] = v.at("on lève des remparts")
    T["v1"], T["v2"] = v.at("Un, l'armée"), v.at("Deux, les poussins")
    T["vote_com"] = v.at("Vote en commentaire")
    T["v3"] = min(T["v3"], T["v1"])
    for phrase, fn in sc:
        v.scenes.append((T[fn.__name__], avec_caisse(fn)))
    for t, nom, g in [(0.0, "pop", 0.8), (0.6, "impact", 0.8), (T["r_com"], "notif", 0.8), (T["r_par"], "whoosh", 0.7),
                      (T["s_grotte"], "rate", 0.7), (T["ressorti"], "impact", 0.8), (T["zombie"], "impact", 1.0),
                      (T["s_camera"], "ticks", 0.5), (T["d_mosk"], "ticks", 0.6), (T["d_koko"], "ticks", 0.6),
                      (T["d_clovis"], "ticks", 0.6), (T["d_t0"], "succes", 1.0), (T["s_eco"] + 0.2, "ticks", 0.7),
                      (T["s_eco"] + 1.6, "succes", 0.9), (T["s_ricane"], "rate", 0.8), (T["maxence"], "impact", 0.7),
                      (T["s_chateau"], "whoosh", 0.7), (T["s_rph1"], "impact", 0.8), (T["moi_armee"], "impact", 0.9),
                      (T["poussins"], "pop", 0.9), (T["s_rph2"], "rate", 0.8), (T["v1"], "pop", 0.8), (T["v2"], "pop", 0.8),
                      (T["v3"], "pop", 0.8), (T["vote_com"], "notif", 0.8)]:
        v.sfx(t, nom, g)
    for cle in ("b_maisons", "b_pont", "b_caserne", "b_lidl", "b_mcdo", "b_rugby", "b_foot", "b_aero", "b_usine"):
        v.sfx(T[cle], "marteau", 0.5)
        v.sfx(T[cle] + 0.3, "impact", 0.45)
    for t0, fn in sorted(v.scenes, key=lambda x: x[0]):
        print(f"   {t0:5.1f}s {fn.__name__}")
    v.render()


if __name__ == "__main__":
    main()
