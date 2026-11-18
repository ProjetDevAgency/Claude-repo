"""Où va ton argent ? — les 8 vidéos du 18 au 22 nov., moteur H1 complet (méchants proches).

    python3 motion/semaine_ct.py carte      → 27_carte_piratee.dial
    python3 motion/semaine_ct.py colis      → 28_colis_perdu.dial
    python3 motion/semaine_ct.py salaire    → 29_salaire_retard.dial
    python3 motion/semaine_ct.py voiture    → 30_voiture_occasion.dial
    python3 motion/semaine_ct.py dentiste   → 31_dentiste.dial
    python3 motion/semaine_ct.py retard     → 32_retard_retenue.dial
    python3 motion/semaine_ct.py smic       → 33_smic_decembre.dial
    python3 motion/semaine_ct.py garantie   → 34_garantie_legale.dial

Les scènes sont fabriquées par de petites usines (hook, plan, gros plan, écho, carte, téléphone, fin) : chaque vidéo
n'est qu'une liste de (début de phrase, scène, bruitage). Mêmes règles d'image que recit.py : aucun texte sur un
visage (bandeaux à y 420/560, bulles au-dessus des têtes), compteur en haut à gauche.
"""
import sys

import facades
from cartoon import FA, bubble, card, flash, phone_big, room, shake
from demission_ct import entrepot_bg
from heures_sup_ct import boutique_bg
from occasion_ct import garage_bg
from prime_ct import salon_bg
from recit import (BASE, GREEN, INK, KX, MX, RED, SS, WHITE, YEL, W, H, Image, ImageDraw, Recit, barres, big_number,
                   dim, gros_plan_kevin, gros_plan_mechant, mention, plan, push, tag)
from trop_percu_ct import headset
from vol_ct import badge, carte_sombre

BLEU, GRIS, VIOLET = (60, 110, 230), (120, 120, 135), (130, 80, 200)
_bg = {}


# ───────────── décors ─────────────

def _cache(cle, fabrique):
    if cle not in _bg:
        _bg[cle] = fabrique()
    return _bg[cle]


def _enseigne(d, txt, col=(30, 30, 36), fg=YEL, x0=240, x1=840):
    s = SS
    d.rounded_rectangle([x0 * s, 90 * s, x1 * s, 190 * s], radius=20 * s, fill=col)
    d.text(((x0 + x1) // 2 * s, 140 * s), txt, font=FA(int(50 * s)), fill=fg, anchor="mm")


def banque_bg():
    def f():
        im = room("vide").copy()
        _enseigne(ImageDraw.Draw(im), "BANQUE · AGENCE", (30, 60, 130), WHITE)
        return im
    return _cache("banque", f)


def guichet_fg(d, t):
    s = SS
    d.rectangle([0, 1260 * s, W * s, 1530 * s], fill=(70, 100, 160))
    d.rectangle([0, 1260 * s, W * s, 1290 * s], fill=(110, 140, 200))


def callcenter_bg():
    def f():
        im = room("bureau").copy()
        _enseigne(ImageDraw.Draw(im), "SERVICE CLIENT", (40, 40, 50), WHITE)
        return im
    return _cache("call", f)


def casque(d, t):
    headset(d, MX, BASE)


def chantier_bg(voiture=False):
    def f():
        s = SS
        im = Image.new("RGB", (W * s, H * s), (150, 200, 240))
        d = ImageDraw.Draw(im)
        d.rectangle([120 * s, 300 * s, 960 * s, 1400 * s], fill=(175, 175, 180))          # l'immeuble en béton
        for y in range(380, 1400, 200):
            for x in range(170, 940, 190):
                d.rectangle([x * s, y * s, (x + 120) * s, (y + 120) * s], fill=(90, 95, 110))
        for x in range(100, 1000, 170):                                                      # l'échafaudage
            d.rectangle([x * s, 260 * s, (x + 12) * s, 1400 * s], fill=(230, 130, 30))
        for y in range(300, 1400, 200):
            d.rectangle([90 * s, y * s, 990 * s, (y + 10) * s], fill=(230, 130, 30))
        d.rectangle([0, 1400 * s, W * s, H * s], fill=(150, 120, 90))
        d.rectangle([0, 1400 * s, W * s, 1416 * s], fill=(120, 95, 70))
        _enseigne(d, "CHANTIER · ACCÈS INTERDIT", (240, 200, 0), INK, 200, 880)
        if voiture:
            facades.voiture(d, 760)
        return im
    return _cache(f"chantier{voiture}", f)


def cabinet_bg():
    def f():
        s = SS
        im = Image.new("RGB", (W * s, H * s), (225, 238, 242))
        d = ImageDraw.Draw(im)
        d.rectangle([0, 1450 * s, W * s, H * s], fill=(190, 200, 205))
        d.rectangle([0, 1440 * s, W * s, 1455 * s], fill=(160, 170, 175))
        # le fauteuil dentaire, au fond au centre
        d.rounded_rectangle([430 * s, 1180 * s, 700 * s, 1300 * s], radius=40 * s, fill=(40, 160, 170))
        d.rounded_rectangle([380 * s, 1000 * s, 470 * s, 1290 * s], radius=40 * s, fill=(40, 160, 170))
        d.rectangle([540 * s, 1300 * s, 580 * s, 1450 * s], fill=(150, 150, 160))
        d.line([(600 * s, 1450 * s), (600 * s, 900 * s), (470 * s, 860 * s)], fill=(150, 150, 160), width=16 * s)
        d.ellipse([420 * s, 820 * s, 520 * s, 900 * s], fill=(250, 250, 220))
        _enseigne(d, "CABINET DENTAIRE", (40, 160, 170), WHITE)
        return im
    return _cache("cabinet", f)


def route_bg(arret=False):
    """La rocade / la rue du bus : ciel, immeubles au loin, glissière, route."""
    def f():
        s = SS
        im = Image.new("RGB", (W * s, H * s), (150, 200, 240))
        d = ImageDraw.Draw(im)
        for x, h in [(0, 520), (170, 380), (330, 600), (520, 450), (700, 560), (880, 400)]:
            d.rectangle([x * s, (1250 - h) * s, (x + 160) * s, 1250 * s], fill=(120, 130, 160))
            for wy in range(1250 - h + 40, 1230, 80):
                d.rectangle([(x + 30) * s, wy * s, (x + 60) * s, (wy + 30) * s], fill=(200, 210, 230))
        d.rectangle([0, 1250 * s, W * s, 1420 * s], fill=(110, 170, 90))
        d.rectangle([0, 1420 * s, W * s, H * s], fill=(70, 72, 80))
        for x in range(0, W, 180):
            d.rectangle([x * s, 1640 * s, (x + 90) * s, 1660 * s], fill=(250, 250, 250))
        if arret:
            d.rectangle([880 * s, 900 * s, 900 * s, 1420 * s], fill=(80, 80, 90))
            d.rounded_rectangle([820 * s, 880 * s, 960 * s, 1000 * s], radius=16 * s, fill=(30, 90, 200))
            d.text((890 * s, 940 * s), "BUS", font=FA(int(50 * s)), fill=WHITE, anchor="mm")
            d.rectangle([820 * s, 1020 * s, 960 * s, 1080 * s], fill=(220, 40, 40))
            d.text((890 * s, 1050 * s), "GRÈVE", font=FA(int(36 * s)), fill=WHITE, anchor="mm")
        else:
            d.rectangle([0, 1380 * s, W * s, 1400 * s], fill=(190, 190, 200))
            for x in range(40, W, 200):
                d.rectangle([x * s, 1380 * s, (x + 14) * s, 1430 * s], fill=(150, 150, 160))
        return im
    return _cache(f"route{arret}", f)


def atelier_bg():
    def f():
        s = SS
        im = entrepot_bg().copy()
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([470 * s, 1130 * s, 610 * s, 1470 * s], radius=14 * s, fill=(40, 40, 46))   # machine à café
        d.rectangle([495 * s, 1160 * s, 585 * s, 1230 * s], fill=(90, 160, 220))
        d.rectangle([505 * s, 1330 * s, 575 * s, 1400 * s], fill=(20, 20, 24))
        d.rectangle([525 * s, 1360 * s, 555 * s, 1400 * s], fill=(250, 250, 250))
        return im
    return _cache("atelier", f)


def machine(d, x, y, sc=1.0, fumee=False, t=0.0):
    """Machine à laver (coordonnées finales)."""
    s = SS * sc

    def P(a, b):
        return x * SS + a * s, y * SS + b * s
    d.rounded_rectangle([*P(-110, -260), *P(110, 0)], radius=int(18 * s), fill=(245, 245, 248), outline=INK, width=int(4 * s))
    d.rectangle([*P(-110, -260), *P(110, -210)], fill=(215, 215, 222))
    d.ellipse([*P(-70, -180), *P(70, -40)], fill=(150, 170, 200), outline=(120, 120, 130), width=int(10 * s))
    if fumee:
        for k in range(3):
            r = 26 + 10 * ((t * 1.5 + k * 0.33) % 1) * 3
            yy = -300 - 90 * ((t * 1.5 + k * 0.33) % 1) * 3
            d.ellipse([*P(-r + 20 * k - 20, yy - r), *P(r + 20 * k - 20, yy + r)], fill=(120, 120, 125))


def magasin_bg():
    def f():
        s = SS
        im = room("vide").copy()
        d = ImageDraw.Draw(im)
        for x in range(130, 1000, 250):
            machine(d, x, 1500, 0.8)
        _enseigne(d, "ÉLECTROMÉNAGER", (200, 40, 40), WHITE)
        return im
    return _cache("magasin", f)


def salon_machine(d, t):
    machine(d, 800, 1560)


def salon_fumee(d, t):
    machine(d, 800, 1560, fumee=True, t=t)


def radiateur(d, t):
    s = SS
    d.rounded_rectangle([600 * s, 1150 * s, 1000 * s, 1400 * s], radius=14 * s, fill=(235, 235, 240), outline=INK, width=4 * s)
    for k, col in enumerate([(250, 210, 220), (200, 230, 250), (250, 240, 190), (210, 240, 210)]):
        x = 630 + k * 95
        d.rounded_rectangle([x * s, 1120 * s, (x + 80) * s, 1240 * s], radius=20 * s, fill=col)


def gateau(d, t):
    s = SS
    d.rectangle([0, 1300 * s, W * s, 1560 * s], fill=(150, 104, 74))
    d.rounded_rectangle([420 * s, 1180 * s, 660 * s, 1300 * s], radius=16 * s, fill=(250, 230, 240), outline=INK, width=3 * s)
    d.rectangle([420 * s, 1230 * s, 660 * s, 1245 * s], fill=(230, 80, 120))
    for x in (480, 540, 600):
        d.rectangle([(x - 5) * s, 1140 * s, (x + 5) * s, 1180 * s], fill=(80, 160, 230))
        d.ellipse([(x - 9) * s, (1120 + 6 * ((t * 9 + x) % 2)) * s, (x + 9) * s, 1145 * s], fill=(255, 200, 40))


def pancarte(d, t):
    s = SS
    d.rectangle([520 * s, 1300 * s, 560 * s, 1500 * s], fill=(120, 80, 50))
    d.rectangle([300 * s, 1120 * s, 780 * s, 1320 * s], fill=(250, 250, 245), outline=INK, width=5 * s)
    d.text((540 * s, 1180 * s), "VENDUE ICI,", font=FA(int(64 * s)), fill=RED, anchor="mm")
    d.text((540 * s, 1260 * s), "EN L'ÉTAT", font=FA(int(64 * s)), fill=RED, anchor="mm")


# ───────────── usines à scènes ─────────────

def _n(f, nom):
    f.__name__ = nom
    return f


def _tags(img, lt, tags):
    for k, (txt, col, t0) in enumerate(tags):
        fg = INK if col in (YEL, WHITE, GREEN) else WHITE
        tag(img, 540, 420 + 140 * k, txt, 54 if len(txt) < 22 else 46, col, fg, rot=(-3, 2, -2)[k % 3],
            k=(lt - t0) / 0.3)


def echo_fit(img, txt):
    d = ImageDraw.Draw(img)
    t = f"« {txt} »"
    size = 92
    while FA(size).getlength(t) > 960 and size > 50:
        size -= 4
    big_number(img, (540, 470), t, size, WHITE, k=1.0)


class Video:
    """Les décors, les personnages et les usines à scènes d'une vidéo."""

    def __init__(self, fond, look, kextra=None):
        self.fond, self.look, self.kx = fond, look, kextra or {}

    def hook(self, nom, badge_txt, lignes, devant=None, **pose):
        def f(lt, dur):
            img = gros_plan_mechant(self.fond, self.look, lt, dur, arm=0.5, devant=devant, **pose)
            badge(img, 540, 1190, badge_txt)
            bubble(img, 540, 570, lignes, 58, (lt + 0.3) / 0.3, tail_x=660)
            return shake(img, lt)
        return _n(f, nom)

    def gp(self, nom, lignes, z=(1.95, 2.15), secoue=False, devant=None, fond=None, **pose):
        def f(lt, dur):
            img = gros_plan_mechant(fond or self.fond, self.look, lt, dur, z[0], z[1], devant=devant,
                                    **{"arm": 0.4, **pose})
            bubble(img, 540, 560, lignes, 56, lt / 0.25, tail_x=660)
            img = flash(img, lt)
            return shake(img, lt) if secoue else img
        return _n(f, nom)

    def scene(self, nom, kpose="neutre", tags=(), fond=None, mechant=None, autres=(), devant=None, z=(1.0, 1.06),
              kx=KX, mx=MX, sans_mechant=False, fx=True, **extra):
        def f(lt, dur):
            m = None if sans_mechant else (mechant or dict(mouth="flat"))
            img = plan(fond or self.fond, lt, kpose, kx=kx, mechant=m, look=self.look, mx=mx, autres=autres,
                       devant=devant, z=push(lt, dur, *z), center=(540, 1000), **{**self.kx, **extra})
            _tags(img, lt, tags)
            return flash(img, lt) if fx else img
        return _n(f, nom)

    def geste(self, nom, txt="IL EN RAJOUTE", fond=None, devant=None, kpose="triste", **pose):
        return self.scene(nom, kpose, [(txt, RED, 0.4)], fond=fond, devant=devant, z=(1.1, 1.2),
                          mechant={"mouth": "grin", "arm": 0.8, **pose}, mx=820)

    def silence(self, nom, kpose="triste", fond=None, devant=None, autres=(), mechant=None):
        return self.scene(nom, kpose, fond=fond, devant=devant, autres=autres, z=(1.0, 1.04), fx=False,
                          mechant=mechant or dict(mouth="grin"))

    def echo(self, nom, txt, fond=None, devant=None):
        def f(lt, dur):
            img = dim(gros_plan_kevin(fond or self.fond, lt, dur, devant=devant, **self.kx), 0.75)
            echo_fit(img, txt)
            return img
        return _n(f, nom)

    def carte(self, nom, titre, rows, sous=None, fond=None, kpose="telephone"):
        def f(lt, dur):
            img = dim(plan(fond or self.fond, lt, kpose, kx=540, **self.kx), 0.9)
            carte_sombre(img, titre, rows, lt, y0=470, sous=sous)
            return img
        return _n(f, nom)

    def gros_mots(self, nom, mots, fond=None, kpose="telephone"):
        """Des mots qui tombent un par un sur un plan assombri : mots = [(texte, couleur, t0)]."""
        def f(lt, dur):
            img = dim(plan(fond or self.fond, lt, kpose, kx=540, **self.kx), 0.85)
            for i, (txt, col, t0) in enumerate(mots):
                fg = INK if col in (YEL, WHITE, GREEN) else WHITE
                tag(img, 540, 520 + i * 160, txt, 62 if len(txt) < 20 else 50, col, fg, rot=(-3, 2, -2)[i % 3],
                    k=(lt - t0) / 0.25)
            return img
        return _n(f, nom)

    def tel(self, nom, heure, lignes, kpose="telephone", fond=None, tags=(), devant=None):
        def f(lt, dur):
            img = plan(fond or self.fond, lt, kpose, kx=270, devant=devant, **self.kx)
            phone_big(img, 700, 960, lt, heure, lignes)
            _tags(img, lt, tags)
            return flash(img, lt)
        return _n(f, nom)

    def fiche(self, nom, titre, sous, rows, kpose="telephone", fond=None, stamp=None, stamp_t=99.0):
        def f(lt, dur):
            img = dim(plan(fond or self.fond, lt, kpose, kx=540, **self.kx), 0.85)
            card(img, 540, 760, titre, sous, rows, lt, rot=2, stamp=stamp, stamp_t=stamp_t)
            return img
        return _n(f, nom)

    def calcul(self, nom, titre, items, sous=None, fond=None):
        def f(lt, dur):
            img = dim(plan(fond or self.fond, lt, "neutre", kx=540, **self.kx), 0.9)
            barres(img, titre, items, lt, sous=sous)
            return img
        return _n(f, nom)

    def doute(self, nom, txt, fond=None, devant=None):
        def f(lt, dur):
            img = plan(fond or self.fond, lt, "triste", kx=540, devant=devant, z=push(lt, dur, 1.1, 1.18),
                       center=(540, 1000), **self.kx)
            tag(img, 540, 420, txt, 50, WHITE, INK, rot=-3, k=(lt - 0.4) / 0.3)
            return img
        return _n(f, nom)

    def fin(self, nom, montant, sous, ref, fond=None):
        def f(lt, dur):
            img = dim(plan(fond or self.fond, lt, z=1.0), 0.6)
            big_number(img, (540, 470), montant, 150, GREEN, sous, k=lt / 0.25, rot=-3)
            mention(img, ref, lt)
            return img
        return _n(f, nom)


def recit(nom, dial, label, montant, phrase):
    return Recit(nom, f"scripts/modele/{dial}.txt", f"output/_work_{nom}/voice_duo.wav",
                 compteur=dict(label=label, depart=0, montant=montant, phrase=phrase))



# ───────────── décors de la v2 (moteur H1 complet : méchants proches) ─────────────

def table_fg(d, t, papiers=False):
    """La table du repas de famille, au premier plan : nappe, assiettes, pain."""
    s = SS
    d.rectangle([0, 1260 * s, W * s, 1560 * s], fill=(240, 236, 226))
    d.rectangle([0, 1260 * s, W * s, 1285 * s], fill=(200, 60, 60))
    for x in (180, 420, 660, 900):
        d.ellipse([(x - 70) * s, 1300 * s, (x + 70) * s, 1350 * s], fill=WHITE, outline=(170, 170, 175), width=3 * s)
    d.rounded_rectangle([500 * s, 1380 * s, 640 * s, 1420 * s], radius=18 * s, fill=(210, 160, 90))
    if papiers:
        d.rectangle([250 * s, 1395 * s, 400 * s, 1500 * s], fill=WHITE, outline=INK, width=3 * s)
        for y in (1415, 1440, 1465):
            d.line([265 * s, y * s, 385 * s, y * s], fill=(150, 150, 160), width=4 * s)
        d.rectangle([700 * s, 1390 * s, 880 * s, 1500 * s], fill=(60, 110, 200), outline=INK, width=3 * s)


def table_papiers(d, t):
    table_fg(d, t, papiers=True)


def porte_mot(d, t):
    s = SS
    d.rectangle([760 * s, 700 * s, 1000 * s, 1560 * s], fill=(150, 100, 60), outline=INK, width=5 * s)
    d.ellipse([780 * s, 1120 * s, 805 * s, 1145 * s], fill=YEL)
    d.rectangle([800 * s, 900 * s, 960 * s, 1010 * s], fill=WHITE, outline=INK, width=3 * s)
    d.text((880 * s, 935 * s), "SONNEZ", font=FA(int(34 * s)), fill=INK, anchor="mm")
    d.text((880 * s, 980 * s), "FORT", font=FA(int(34 * s)), fill=RED, anchor="mm")


def boulangerie_bg():
    def f():
        s = SS
        im = room("vide").copy()
        d = ImageDraw.Draw(im)
        for y in (1000, 1130):                                                   # étagères à pain
            d.rectangle([40 * s, y * s, 1040 * s, (y + 14) * s], fill=(120, 80, 50))
            for x in range(70, 1020, 95):
                d.rounded_rectangle([x * s, (y - 40) * s, (x + 75) * s, y * s], radius=18 * s, fill=(215, 160, 80))
        _enseigne(d, "BOULANGERIE", (120, 70, 40), WHITE)
        return im
    return _cache("boulangerie", f)


def comptoir_fg(d, t):
    s = SS
    d.rectangle([0, 1290 * s, W * s, 1560 * s], fill=(190, 140, 90))
    d.rectangle([0, 1290 * s, W * s, 1310 * s], fill=(230, 220, 200))
    for x in range(60, 1040, 110):                                               # les croissants
        d.chord([x * s, 1250 * s, (x + 90) * s, 1320 * s], 180, 360, fill=(225, 160, 70), outline=(160, 100, 40), width=3 * s)


def feuille_mur(d, t):
    s = SS
    d.rectangle([380 * s, 620 * s, 700 * s, 820 * s], fill=WHITE, outline=INK, width=4 * s)
    d.text((540 * s, 670 * s), "RETENUE", font=FA(int(46 * s)), fill=INK, anchor="mm")
    d.text((540 * s, 740 * s), "À LA MINUTE", font=FA(int(46 * s)), fill=RED, anchor="mm")


def salon_machine_d(d, t):
    machine(d, 960, 1560)


def bandeau_tv(img, lt, titre, citation):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1180, W, 1330], fill=(20, 40, 110))
    d.rectangle([0, 1180, 260, 1240], fill=(220, 40, 40))
    d.text((130, 1210), "DIRECT", font=FA(38), fill=WHITE, anchor="mm")
    d.text((300, 1210), titre, font=FA(38), fill=WHITE, anchor="lm")
    if lt > 0.6:
        d.text((540, 1285), citation, font=FA(46), fill=YEL, anchor="mm")


class V2(Video):
    def accroche(self, nom, badge_txt, tags, fond=None, autres=(), devant=None, kpose="choc", mechant=None, mx=MX):
        """L'accroche dite par Kévin : plan large, le méchant étiqueté, les mots du choc en gros."""
        def f(lt, dur):
            img = plan(fond or self.fond, lt, kpose, mechant=mechant or dict(mouth="grin"), look=self.look, mx=mx,
                       autres=autres, devant=devant, z=push(lt, dur, 1.0, 1.08), center=(540, 1000), **self.kx)
            badge(img, mx, 1205, badge_txt)
            _tags(img, lt, tags)
            return shake(img, lt)
        return _n(f, nom)

    def muet(self, nom, txt, fond=None, devant=None, **pose):
        """Le méchant réduit au silence : gros plan, bouche fermée, un seul mot à l'écran."""
        def f(lt, dur):
            img = gros_plan_mechant(fond or self.fond, self.look, lt, dur, 1.9, 2.15, devant=devant,
                                    **{"mouth": "flat", "brows": None, **pose})
            tag(img, 540, 430, txt, 56, WHITE, INK, rot=-3, k=(lt - 0.3) / 0.3)
            return img
        return _n(f, nom)

    def tv(self, nom, titre, citation, fond=None):
        def f(lt, dur):
            img = gros_plan_mechant(fond or self.fond, self.look, lt, dur, 1.7, 1.8, mouth="smile", arm=0.3)
            bandeau_tv(img, lt, titre, citation)
            return img
        return _n(f, nom)


# ═════════════ 27. La carte piratée de mamie (l'oncle) ═════════════

ONCLE = dict(shirt=(190, 170, 130), pants=(60, 60, 70), hair=(120, 110, 100), glasses=True)
MAMIE = dict(shirt=(170, 120, 170), pants=(60, 60, 80), hair=(215, 215, 222), long_hair=True, glasses=True)
TANTE = dict(shirt=(80, 150, 120), pants=(50, 50, 60), hair=(70, 40, 25), long_hair=True)
COUSINE = dict(shirt=(230, 120, 160), pants=(40, 50, 80), hair=(150, 90, 40), long_hair=True, sc=0.9)
V = V2(salon_bg, ONCLE)
M_TABLE = [(540, MAMIE, dict(mouth="flat", sc=0.92), 0.5)]
CARTE = (recit("s_carte", "27_carte_piratee", "RENDU À MAMIE", 3200, "Lettre signée lundi"), [
    ("Pour trois mille deux cents", V.hook("h", "MON ONCLE", ["POUR 3 200 € VOLÉS,", "MAMIE A PLU SA TÊTE,", "ON LA MET SOUS TUTELLE"], devant=table_fg, clipboard=True), ("impact", 1.0)),
    ("C'est ce que mon oncle", V.fiche("dossier", "DEMANDE DE TUTELLE", "DÉPÔT : VENDREDI", [("Pour : mamie, 84 ans", "", 0.2, False), ("Motif : argent perdu", "", 0.6, True)], kpose="choc"), ("whoosh", 0.4)),
    ("Un faux SMS", V.tel("sms", "14:07", [("SMS", "Livraison", "Colis bloqué, payez", GRIS), ("Banque", "Paiement carte", "− 3 200,00 €", RED)], "choc"), ("notif", 0.6)),
    ("Mamie, quatre-vingt-quatre", V.scene("montee", "neutre", [("MAMIE · 84 ANS", GREEN, 0.2), ("SES COMPTES AU CRAYON", YEL, 1.4)], sans_mechant=True, autres=[(780, MAMIE, dict(mouth="smile"), 0.4)]), ("pop", 0.8)),
    ("Je lui dis, mamie", V.scene("promesse", "parle", [("PAS BESOIN DE TUTEUR", WHITE, 1.8)], sans_mechant=True, autres=[(780, MAMIE, dict(mouth="grin"), 0.4)]), None),
    ("Dimanche, mon oncle", V.scene("dimanche", "neutre", [("LE REPAS DU DIMANCHE", YEL, 0.2)], mechant=dict(mouth="flat", clipboard=True), autres=M_TABLE, devant=table_fg), ("whoosh", 0.5)),
    ("Son cahier, c'est", V.gp("coup1", ["SON CAHIER, C'EST", "TROIS GRIBOUILLIS", "AU CRAYON"], devant=table_fg), ("impact", 0.8)),
    ("Et en allant chercher", V.geste("geste", devant=table_fg), ("whoosh", 0.5)),
    ("À son âge, on regarde", V.gp("coup2", ["À SON ÂGE, ON REGARDE", "LA TÉLÉ DANS SA CHAMBRE"], (2.2, 2.4), True, devant=table_fg, arm=0.8), ("impact", 1.0)),
    ("Je dis rien. Je coupe", V.silence("silence", devant=table_fg, autres=M_TABLE), None),
    ("Trois gribouillis", V.echo("echo", "TROIS GRIBOUILLIS", devant=table_fg), ("rate", 0.6)),
    ("Et pourtant, la banque", V.fiche("refus", "TA BANQUE", "RÉPONSE À LA RÉCLAMATION", [("Remboursement", "REFUSÉ", 0.3, True), ("Motif", "négligence grave", 1.0, False)], kpose="choc"), ("impact", 0.6)),
    ("Ce que peu de gens", V.carte("regle", "PAIEMENT PAS AUTORISÉ", [("La banque rembourse", 0.6, True), ("au plus tard le jour ouvrable", 2.2, False), ("suivant", 3.0, False)], "CODE MONÉTAIRE ET FINANCIER · L133-18"), ("pop", 0.8)),
    ("Mais alors, et la", V.carte("preuve", "LA NÉGLIGENCE GRAVE", [("C'est à la banque de la prouver", 1.4, True), ("Un faux SMS, ça suffit pas", 2.8, False)], "L133-19 · COUR DE CASSATION"), ("impact", 0.6)),
    ("Sauf que vendredi", V.tel("lettre", "09:30", [("Courrier", "Contestation", "Signée lundi", BLEU), ("Banque", "Mercredi", "+ 3 200,00 €", GREEN)]), ("ticks", 0.6)),
    ("Honnêtement", V.doute("doute", "ET S'IL AVAIT RAISON ?"), None),
    ("Jeudi, anniversaire", V.scene("riposte", "parle", [("12 PERSONNES À TABLE", YEL, 0.3), ("SON DOSSIER AU MILIEU DES PLATS", RED, 3.2)], mechant=dict(mouth="o"), devant=table_papiers, autres=[(540, MAMIE, dict(mouth="flat", sc=0.92), 0.5), (130, TANTE, dict(mouth="o", sc=0.8), 1.2, BASE - 50), (950, COUSINE, dict(mouth="o", sc=0.8), 2.0, BASE - 50)]), ("impact", 0.8)),
    ("Il lit. Il cherche", V.muet("muet", "PLU RIEN", devant=table_papiers), None),
    ("Vendredi, le dossier", V.scene("twist", "victoire", [("LE DOSSIER RESTE DANS LA VOITURE", WHITE, 0.2), ("+ 3 200 € DANS LE CAHIER", GREEN, 2.4)], sans_mechant=True, autres=[(780, MAMIE, dict(mouth="grin", arm=0.6), 0.4)]), ("succes", 0.8)),
    ("Trois mille deux cents euros, en", V.fin("fin", "3 200 €", "EN GRIBOUILLIS", "CAS TYPE · CODE MONÉTAIRE ET FINANCIER L133-18 ET L133-19"), ("impact", 0.9)),
])


# ═════════════ 28. Le colis jamais reçu (le père) ═════════════

PERE = dict(shirt=(70, 110, 160), pants=(50, 50, 60), hair=(150, 150, 150), glasses=True)
APPART = lambda: room("appart")  # noqa: E731
V = V2(salon_bg, PERE)
COLIS = (recit("s_colis", "28_colis_perdu", "REMBOURSÉ PAR LE SITE", 1200, "Mardi, le site"), [
    ("Tu me dois mille", V.hook("h", "MON PÈRE", ["TU ME DOIS 1 200 €", "POUR UN ORDI QUE T'ES", "PAS CAPABLE DE RECEVOIR"], phone=True), ("impact", 1.0)),
    ("C'est ce que mon père", V.tel("message", "21:12", [("Papa", "Message", "Tu me dois 1 200 €", GREEN)], "choc", fond=APPART), ("notif", 0.5)),
    ("Un ordi de graphiste", V.tel("suivi", "14:02", [("Suivi", "Colis 4471", "LIVRÉ · 14:02", GREEN)], "choc", fond=APPART, tags=[("PERSONNE A SONNÉ", RED, 2.6)]), ("notif", 0.6)),
    ("Lundi, je commence", V.scene("montee", "victoire", [("1re MISSION : LUNDI", GREEN, 0.2), ("LE LOGO D'UNE BOULANGERIE", YEL, 1.6)], fond=APPART, sans_mechant=True), ("pop", 0.8)),
    ("Mon père m'avait avancé", V.scene("avance", "parle", [("IL M'AVANCE L'ORDI", GREEN, 0.2), ("MON DEVIS IMPRIMÉ", YEL, 2.0)], mechant=dict(mouth="smile", clipboard=True)), ("pop", 0.6)),
    ("Sur la porte", V.scene("porte", "neutre", [("SUR LA PORTE", YEL, 0.2)], fond=APPART, sans_mechant=True, devant=porte_mot), None),
    ("Je lui réponds, papa", V.tel("reponse", "21:20", [("Moi", "À papa", "Je te rembourse", BLEU), ("Papa", "Vocal", "0:12", GREEN)], fond=APPART), ("notif", 0.6)),
    ("Un ordi à ce prix", V.gp("coup1", ["UN ORDI À CE PRIX", "POUR FAIRE DES", "PETITS DESSINS"], phone=True), ("impact", 0.8)),
    ("Et une heure après", V.geste("geste", "IL INSISTE", phone=True), ("whoosh", 0.5)),
    ("À vingt-quatre ans", V.gp("coup2", ["À 24 ANS, TU BOSSES", "DANS TA CHAMBRE"], (2.2, 2.4), True, phone=True), ("impact", 1.0)),
    ("Je réponds pas", V.scene("silence", "triste", fond=APPART, sans_mechant=True, z=(1.0, 1.04), fx=False), None),
    ("Des petits dessins", V.echo("echo", "DES PETITS DESSINS", fond=APPART), ("rate", 0.6)),
    ("Et pourtant, le site", V.tel("site", "10:15", [("Service client", "Le site", "Voyez avec le livreur", GRIS)], "choc", fond=APPART), ("notif", 0.6)),
    ("Ce que peu de gens", V.carte("regle", "ACHAT À DISTANCE", [("Tant que t'as pas le colis en main", 0.8, False), ("le risque est pour le VENDEUR", 2.6, True)], "CODE DE LA CONSOMMATION · L216-4", fond=APPART), ("pop", 0.8)),
    ("Mais alors, et le suivi", V.gros_mots("preuve", [("UNE SIGNATURE ?", WHITE, 1.4), ("UNE PHOTO ?", WHITE, 2.2), ("SINON, IL REMBOURSE", GREEN, 3.2)], fond=APPART), ("impact", 0.6)),
    ("Sauf que lundi approche", V.tel("mail", "19:40", [("Mail", "Au vendeur", "Réclamation envoyée", BLEU)], fond=APPART), ("ticks", 0.6)),
    ("Honnêtement", V.doute("doute", "C'EST LUI QUI A PAYÉ", fond=APPART), None),
    ("Mardi, le site", V.tel("rembourse", "11:02", [("Banque", "Remboursement", "+ 1 200,00 €", GREEN), ("Famille", "14 personnes", "Capture envoyée", GREEN)], "victoire", fond=APPART), ("succes", 0.8)),
    ("Il répond pas", V.tel("papa", "22:47", [("Papa", "Message", "Et le colis de ta mère ?", GREEN)], fond=APPART, tags=[("SILENCE TOUTE LA JOURNÉE", WHITE, 0.2)]), ("notif", 1.6)),
    ("Maintenant, toute la famille", V.scene("cascade", "parle", [("TOUTE LA FAMILLE", YEL, 0.2), ("M'ENVOIE SES COLIS", GREEN, 1.0)], fond=APPART, sans_mechant=True), ("pop", 0.5)),
    ("Mille deux cents euros, sans", V.fin("fin", "1 200 €", "SANS OUVRIR LA PORTE", "CAS TYPE · CODE DE LA CONSOMMATION L216-4 ET L221-15", fond=APPART), ("impact", 0.9)),
])


# ═════════════ 29. Le salaire en retard (le beau-père patron) ═════════════

BEAU_PERE = dict(shirt=(245, 245, 248), pants=(50, 50, 60), hair=(130, 120, 110), glasses=True)
GILET = dict(shirt=(230, 120, 40))
GARS = [dict(shirt=(230, 120, 40), pants=(40, 40, 60), hair=c, mouth="flat", sc=0.85)
        for c in ((30, 25, 20), (120, 70, 30), (90, 90, 95), (60, 40, 30))]
OUVRIERS = [(x, g, {}, 0.7 * i, BASE - 60) for i, (x, g) in enumerate(zip((520, 650, 780, 910), GARS))]
V = V2(chantier_bg, BEAU_PERE, GILET)
CHANTIER_V = lambda: chantier_bg(True)  # noqa: E731
SALAIRE = (recit("s_salaire", "29_salaire_retard", "RENDU PAR LE PATRON", 90, "Le premier, paie"), [
    ("J'ai payé quatre-vingt-dix", V.accroche("h", "MON BEAU-PÈRE ET PATRON", [("90 € DE FRAIS DE BANQUE", RED, 0.2), ("À CAUSE DE MON BEAU-PÈRE", YEL, 2.0)]), ("impact", 1.0)),
    ("Et j'ai gardé le vocal", V.tel("vocal", "18:03", [("Fichiers", "Enregistré", "vocal_patron.opus", BLEU)], tags=[("IL L'A EFFACÉ", RED, 0.8)]), ("notif", 0.5)),
    ("Douze jours de retard", V.fiche("rejet", "AVIS DE REJET", "TA BANQUE", [("Loyer", "rejeté", 0.3, False), ("Frais", "90 €", 1.0, True)]), ("pop", 0.5)),
    ("Deux ans de plomberie", V.scene("montee", "victoire", [("2 ANS DE CHANTIERS", GREEN, 0.2), ("TOUT GARDER PAR ÉCRIT", YEL, 1.6)], mechant=dict(mouth="smile", arm=0.4)), ("pop", 0.8)),
    ("Aux clients, il me présente", V.scene("gendre", "neutre", [("SON FUTUR GENDRE", GREEN, 0.3)], mechant=dict(mouth="grin", arm=0.6)), None),
    ("Lundi, il débarque", V.scene("demande", "parle", [("JUSTE LES FRAIS DE REJET", WHITE, 1.6)], mechant=dict(mouth="flat")), ("whoosh", 0.5)),
    ("Pour trois sous", V.gp("coup1", ["POUR TROIS SOUS DE FRAIS,", "TU ME FAIS UNE SCÈNE ?"]), ("impact", 0.8)),
    ("Et en remontant", V.geste("geste", fond=CHANTIER_V), ("whoosh", 0.5)),
    ("Si t'as même pas", V.gp("coup2", ["MA FILLE A PAS FINI", "DE PAYER POUR TOI,", "DANS VOTRE STUDIO"], (2.2, 2.4), True, fond=CHANTIER_V, arm=0.8), ("impact", 1.0)),
    ("Pas un mot", V.silence("silence", "carte", fond=CHANTIER_V), None),
    ("Trois sous", V.echo("echo", "TROIS SOUS"), ("rate", 0.6)),
    ("Sauf qu'un salaire", V.carte("regle", "SALAIRE EN RETARD", [("Des intérêts au taux légal", 0.4, True), ("dès la mise en demeure écrite", 2.0, False), ("automatiques", 3.4, False)], "CODE CIVIL · ARTICLE 1231-6", fond=salon_bg), ("pop", 0.8)),
    ("Mais alors, et les frais", V.carte("frais", "ET LES FRAIS DE BANQUE ?", [("1. Un préjudice à part", 1.4, False), ("2. Sa mauvaise foi", 2.6, True)], "LES DEUX, À PROUVER", fond=salon_bg), ("impact", 0.6)),
    ("Sur le papier", V.gros_mots("papier", [("SA MAUVAISE FOI ?", WHITE, 0.6), ("ÇA SE PROUVE JAMAIS", RED, 1.8)], fond=salon_bg), None),
    ("Honnêtement", V.doute("doute", "LE PATRON TRINQUE AUSSI", fond=salon_bg), None),
    ("Le lendemain, pause", V.scene("pause", "telephone", [("PAUSE DE MIDI · 6 GARS", YEL, 0.3), ("HAUT-PARLEUR", RED, 2.6)], sans_mechant=True, autres=OUVRIERS), ("ticks", 0.4)),
    ("Je les paie le douze", V.gp("vocal_joue", ["JE LES PAIE LE 12,", "ÇA ME FAIT DE", "LA TRÉSORERIE"], (1.9, 2.0), phone=True), ("impact", 0.6)),
    ("Le plus vieux arrête", V.scene("temoin", "neutre", [("SILENCE", WHITE, 0.2)], sans_mechant=True, autres=OUVRIERS, z=(1.1, 1.15), fx=False), None),
    ("Le soir, ma copine", V.tel("copine", "20:31", [("Ma copine", "Appel", "Les 6 gars ont écrit", GREEN)], fond=salon_bg, tags=[("SA PROPRE LEÇON", YEL, 3.6)]), ("notif", 0.6)),
    ("Le premier, paie", V.tel("twist", "08:01", [("Banque", "Salaire · le 1er", "+ paie + 90,00 €", GREEN)], "victoire", fond=salon_bg), ("succes", 0.6)),
    ("Quatre-vingt-dix euros, payés", V.fin("fin", "90 €", "PAYÉS PAR SA PROPRE LEÇON", "CAS TYPE · CODE CIVIL 1231-6 · CASS. SOC. 6 MAI 2025"), ("impact", 0.9)),
])


# ═════════════ 30. La voiture d'occasion (le cousin garagiste) ═════════════

COUSIN = dict(shirt=(60, 90, 140), pants=(60, 90, 140), hair=(215, 175, 70))   # blond : pas confondu avec Kévin
CLIENTS = [(560, dict(shirt=(200, 80, 60), pants=(40, 40, 60), hair=(60, 40, 30), sc=0.85), {}, 0.3, BASE - 60),
           (720, dict(shirt=(90, 160, 90), pants=(40, 40, 60), hair=(200, 160, 80), long_hair=True, sc=0.85), {}, 1.1, BASE - 60),
           (880, dict(shirt=(120, 120, 200), pants=(40, 40, 60), hair=(30, 25, 20), sc=0.85), {}, 1.9, BASE - 60)]
V = V2(garage_bg, COUSIN)
VOITURE = (recit("s_voiture", "30_voiture_occasion", "PAYÉ PAR LE COUSIN", 1800, "Deux heures après"), [
    ("Mon cousin garagiste", V.accroche("h", "MON COUSIN GARAGISTE", [("1 800 € L'EMBRAYAGE", RED, 0.2), ("DE LA VOITURE QU'IL M'A VENDUE", YEL, 2.2)]), ("impact", 1.0)),
    ("Lundi, je commence", V.gros_mots("verrou", [("CDI LUNDI", GREEN, 0.2), ("EN VOITURE", WHITE, 1.4), ("OU PAS DU TOUT", RED, 2.2)], kpose="choc"), ("pop", 0.6)),
    ("Une petite citadine", V.scene("panne", "choc", [("3 SEMAINES APRÈS", WHITE, 1.4), ("L'EMBRAYAGE LÂCHE", RED, 2.4)], fond=route_bg, sans_mechant=True), ("impact", 0.6)),
    ("Il m'avait fait", V.scene("montee", "victoire", [("UN PRIX DE FAMILLE", GREEN, 0.2), ("SAPIN À LA VANILLE", YEL, 1.6)], mechant=dict(mouth="smile", arm=0.5)), ("pop", 0.8)),
    ("Je lui ai dit, cousin", V.scene("merci", "parle", [("TU ME SAUVES, COUSIN", WHITE, 0.3)], mechant=dict(mouth="grin")), None),
    ("Le soir de la panne", V.tel("appel", "23:04", [("Cousin", "Appel", "Le devis", GREEN)], "choc", fond=salon_bg), ("notif", 0.6)),
    ("Une caisse à ce", V.gp("coup1", ["UNE CAISSE À CE PRIX,", "C'EST UN TICKET", "DE LOTERIE"], phone=True), ("impact", 0.8)),
    ("Et avant de raccrocher", V.geste("geste", phone=True), ("whoosh", 0.5)),
    ("Si t'as pas de quoi", V.gp("coup2", ["RETOURNE CHEZ TA MÈRE", "ET PRENDS LE BUS"], (2.2, 2.4), True, phone=True), ("impact", 1.0)),
    ("Je raccroche sans", V.scene("silence", "triste", fond=salon_bg, sans_mechant=True, z=(1.0, 1.04), fx=False), None),
    ("Un ticket de loterie", V.echo("echo", "UN TICKET DE LOTERIE", fond=salon_bg), ("rate", 0.6)),
    ("Et pourtant, en famille", V.fiche("facture", "FACTURE", "GARAGE · OCCASION", [("Citadine d'occasion", "", 0.3, False), ("Vendue en l'état", "", 1.4, True)], fond=salon_bg), ("pop", 0.5)),
    ("Ce que peu de gens", V.carte("regle", "UN GARAGE = UN PRO", [("Garantie légale de conformité", 0.8, True), ("même sur une occasion", 2.4, False), ("en l'état ou pas", 3.8, False)], "CODE DE LA CONSOMMATION · L217-3", fond=salon_bg), ("pop", 0.8)),
    ("Mais alors, faut prouver", V.gros_mots("preuve", [("LA PANNE ÉTAIT LÀ AVANT ?", WHITE, 0.4), ("1re ANNÉE : C'EST PRÉSUMÉ", GREEN, 2.0)], fond=salon_bg), ("impact", 0.6)),
    ("Sauf que lundi arrive", V.fiche("lettre", "LETTRE RECOMMANDÉE", "ENVOYÉE LE SOIR MÊME", [("Garantie légale de conformité", "", 0.3, True), ("Réparation à vos frais", "", 1.0, False)], fond=salon_bg), ("ticks", 0.6)),
    ("Honnêtement", V.doute("doute", "UNE OCCASION, ÇA CASSE", fond=salon_bg), None),
    ("Samedi, je fais déposer", V.scene("pancarte", None, [("DEVANT SON GARAGE", YEL, 0.3)], sans_mechant=True, devant=pancarte, z=(1.0, 1.08)), ("pop", 0.6)),
    ("s'arrêtent pour la lire", V.scene("clients", None, [("3 CLIENTS S'ARRÊTENT", WHITE, 0.2)], sans_mechant=True, devant=pancarte, autres=CLIENTS, z=(1.05, 1.1), fx=False), None),
    ("Deux heures après", V.tel("rappel", "13:12", [("Cousin", "Appel", "Embrayage refait · 0 €", GREEN), ("Cousin", "SMS", "Prêt pour lundi", BLEU)], "victoire", fond=salon_bg), ("succes", 0.8)),
    ("Le soir, son annonce", V.tel("annonce", "21:48", [("Leboncoin", "Citadine grise", "Garantie 1 an", (240, 120, 40))], "choc", fond=salon_bg, tags=[("GARANTIE UN AN, EN GROS", YEL, 2.0)]), ("notif", 0.5)),
    ("Mille huit cents euros, sauf", V.fin("fin", "1 800 €", "SAUF POUR LA FAMILLE", "CAS TYPE · CODE DE LA CONSOMMATION L217-3 ET L217-7"), ("impact", 0.9)),
])


# ═════════════ 31. La couronne de maman (la sœur assistante dentaire) ═════════════

SOEUR = dict(shirt=(240, 245, 250), pants=(90, 170, 190), hair=(200, 150, 80), long_hair=True)
MAMAN = dict(shirt=(150, 92, 165), pants=(50, 50, 70), hair=(110, 70, 40), long_hair=True)
PATIENTS = [(790, dict(shirt=(120, 120, 130), pants=(40, 40, 60), hair=(180, 180, 185), sc=0.82), dict(mouth="o"), 0.3, BASE - 70),
            (940, dict(shirt=(200, 160, 60), pants=(40, 40, 60), hair=(60, 40, 30), long_hair=True, sc=0.82), dict(mouth="o"), 1.3, BASE - 70)]
V = V2(cabinet_bg, SOEUR)
DENTISTE_V = (recit("s_dentiste", "31_dentiste", "ÉCONOMISÉ", 2400, "Le lendemain, la secrétaire"), [
    ("Ma sœur veut faire payer", V.accroche("h", "MA SŒUR, ASSISTANTE DENTAIRE", [("2 400 € DE COURONNES", RED, 0.2), ("POUR NOTRE MÈRE", YEL, 1.8)], autres=[(600, MAMAN, dict(mouth="flat", sc=0.92), 0.8)], mx=860), ("impact", 1.0)),
    ("Et maman fête sa retraite", V.scene("verrou", "neutre", [("SA RETRAITE DANS 3 SEMAINES", YEL, 0.2)], fond=salon_bg, sans_mechant=True, autres=[(780, MAMAN, dict(mouth="smile"), 0.8)]), ("pop", 0.5)),
    ("Deux couronnes en céramique", V.fiche("devis", "DEVIS · 2 COURONNES", "CABINET DENTAIRE", [("Céramique", "2 400 €", 0.3, True), ("Option 100 % Santé", "AUCUNE", 1.6, False)], kpose="carte", fond=salon_bg), None),
    ("Maman m'envoie la photo", V.scene("montee", "telephone", [("42 ANS DE CANTINE", GREEN, 0.4), ("SOURIRE SUR LES PHOTOS", YEL, 2.0)], fond=salon_bg, sans_mechant=True, autres=[(780, MAMAN, dict(mouth="smile"), 0.8)]), ("pop", 0.8)),
    ("Je lui dis, maman", V.scene("promesse", "parle", [("CETTE FOIS, TU MONTRES TES DENTS", WHITE, 0.4)], fond=salon_bg, sans_mechant=True, autres=[(780, MAMAN, dict(mouth="grin"), 0.8)]), None),
    ("J'appelle ma sœur", V.tel("appel", "19:15", [("Ma sœur", "Appel", "En cours", GREEN)], fond=salon_bg), ("notif", 0.5)),
    ("Le moins cher, c'est", V.gp("coup1", ["LE MOINS CHER, C'EST", "DES DENTS EN PLASTIQUE"], phone=True), ("impact", 0.8)),
    ("Elle rigole", V.geste("geste", "ELLE EN RAJOUTE", phone=True), ("whoosh", 0.5)),
    ("Toi qui vis encore", V.gp("coup2", ["TOI, DANS TA CHAMBRE", "D'ÉTUDIANT, VIENS PAS", "M'APPRENDRE MON MÉTIER"], (2.2, 2.4), True, phone=True), ("impact", 1.0)),
    ("Je dis rien. Maman", V.scene("silence", "triste", fond=salon_bg, sans_mechant=True, autres=[(780, MAMAN, dict(mouth="flat"), 0.8)], z=(1.0, 1.04), fx=False), None),
    ("Des dents en plastique", V.echo("echo", "DES DENTS EN PLASTIQUE", fond=salon_bg), ("rate", 0.6)),
    ("Ce que peu de gens", V.carte("regle", "COURONNE DENTAIRE", [("Le devis doit proposer", 0.6, False), ("une option 100 % Santé", 1.8, True), ("0 € avec une mutuelle responsable", 4.0, False)], "OBLIGATOIRE DEPUIS 2020 · DGCCRF", fond=salon_bg), ("pop", 0.8)),
    ("Mais alors, si le cabinet", V.gros_mots("ailleurs", [("IL DOIT L'ÉCRIRE", WHITE, 1.8), ("TU PEUX ALLER AILLEURS", GREEN, 3.0)], fond=salon_bg), ("impact", 0.6)),
    ("Sauf que la fête", V.gros_mots("urgence", [("LA FÊTE APPROCHE", YEL, 0.3), ("NOUVEAU DEVIS CETTE SEMAINE", WHITE, 1.4)], fond=salon_bg), ("ticks", 0.5)),
    ("Honnêtement", V.doute("doute", "C'EST SON MÉTIER", fond=salon_bg), None),
    ("Mardi, salle d'attente", V.scene("riposte", "parle", [("9 PATIENTS", YEL, 0.3), ("LE DEVIS AVEC L'OPTION, À VOIX HAUTE", WHITE, 2.6)], sans_mechant=True, autres=[(600, MAMAN, dict(mouth="flat", sc=0.92), 0.8)] + PATIENTS), ("impact", 0.6)),
    ("Ma sœur sort du couloir", V.scene("soeur", "neutre", [("MA SŒUR", RED, 0.2)], mechant=dict(mouth="o", arms_up=False), mx=820), None),
    ("Le lendemain, la secrétaire", V.tel("twist", "10:40", [("Cabinet", "Appel", "Nouveau devis · 0 €", GREEN)], "victoire", fond=salon_bg, tags=[("ELLE REFAIT CEUX DE TOUTE LA SEMAINE", YEL, 3.4)]), ("succes", 0.8)),
    ("À la fête, maman", V.scene("fete", "victoire", [("BONNE RETRAITE MAMAN", YEL, 0.2)], fond=salon_bg, mechant=dict(mouth="smile", phone=True), mx=900, devant=gateau, autres=[(600, MAMAN, dict(mouth="grin", arms_up=True), 0.8)]), ("pop", 0.6)),
    ("Deux mille quatre cents euros de", V.fin("fin", "2 400 €", "DE GAGNÉS", "CAS TYPE · 100 % SANTÉ · CODE DE LA SANTÉ PUBLIQUE · DGCCRF", fond=salon_bg), ("impact", 0.9)),
])


# ═════════════ 32. Une heure pour dix minutes (la tante boulangère) ═════════════

TATA = dict(shirt=(250, 250, 250), pants=(60, 60, 70), hair=(120, 70, 40), long_hair=True)
TABLIER = dict(shirt=(60, 110, 170))
COLLEGUES = [(x, dict(shirt=(250, 250, 250), pants=(60, 60, 70), hair=c, sc=0.8, **({"long_hair": True} if i % 2 else {})),
              {}, 0.6 * i, BASE - 60) for i, (x, c) in enumerate(zip((600, 730, 860, 990), ((30, 25, 20), (180, 120, 60), (90, 90, 95), (60, 40, 30))))]
V = V2(boulangerie_bg, TATA, TABLIER)
RETARD = (recit("s_retard", "32_retard_retenue", "RENDU PAR TATA", 90, "Ma tante me parle pas"), [
    ("Ma tante m'a retiré", V.accroche("h", "MA TANTE ET PATRONNE", [("108 € RETIRÉS", RED, 0.2), ("POUR 9 RETARDS DE 10 MIN", YEL, 1.6)], devant=comptoir_fg), ("impact", 1.0)),
    ("Et j'ai gardé la feuille", V.fiche("pointage", "FEUILLE DE POINTAGE", "TOUTE L'ÉQUIPE", [("6:10 · 6:10 · 6:10 · 6:10", "", 0.3, False), ("Gardée", "", 1.2, True)], kpose="carte"), ("pop", 0.5)),
    ("Trois semaines de grève", V.scene("greve", "choc", [("GRÈVE DES BUS", RED, 0.2), ("ARRIVÉE : 6 H 10", WHITE, 2.4)], fond=lambda: route_bg(True), sans_mechant=True), ("impact", 0.5)),
    ("Je pars à cinq heures", V.scene("montee", "marche", [("PARTI À 5 H", GREEN, 0.2), ("2 ARRÊTS À PIED", YEL, 1.2)], fond=lambda: route_bg(True), sans_mechant=True), ("pop", 0.6)),
    ("Vendredi, je dois payer", V.fiche("voyage", "VOYAGE SCOLAIRE", "À PAYER VENDREDI", [("Mon petit frère", "", 0.3, True)], kpose="neutre", fond=salon_bg), None),
    ("Le soir de la paie", V.tel("message", "20:02", [("Tata", "Photo", "C'est la règle.", GREEN)], "choc", fond=salon_bg), ("notif", 0.5)),
    ("Je lui réponds, tata", V.tel("reponse", "20:05", [("Moi", "À tata", "C'est la grève", BLEU), ("Tata", "Appel", "En cours", GREEN)], fond=salon_bg), ("notif", 1.4)),
    ("Une heure ou dix", V.gp("coup1", ["UNE HEURE OU DIX MINUTES,", "POUR UN VENDEUR DE", "CROISSANTS, ÇA CHANGE QUOI ?"], phone=True, devant=comptoir_fg), ("impact", 0.8)),
    ("Et avant de couper", V.geste("geste", "ELLE INSISTE", devant=comptoir_fg, phone=True), ("whoosh", 0.5)),
    ("Si t'étais sérieux", V.gp("coup2", ["SI T'ÉTAIS SÉRIEUX,", "TU DORMIRAIS", "DANS LE FOURNIL"], (2.2, 2.4), True, phone=True, devant=comptoir_fg), ("impact", 1.0)),
    ("Pas un mot", V.scene("silence", "triste", fond=salon_bg, sans_mechant=True, z=(1.0, 1.04), fx=False), None),
    ("Un vendeur de croissants", V.echo("echo", "UN VENDEUR DE CROISSANTS", fond=salon_bg), ("rate", 0.6)),
    ("Sur le papier", V.gros_mots("papier", [("SA BOUTIQUE", WHITE, 0.3), ("SES RÈGLES", RED, 1.0)], fond=salon_bg), None),
    ("Ce que peu de gens", V.carte("regle", "UN RETARD", [("On retire le temps exact", 0.8, True), ("pas une minute de plus", 2.6, False)], "CODE DU TRAVAIL · L1331-2", fond=salon_bg), ("pop", 0.8)),
    ("Mais alors, une heure", V.gros_mots("sanction", [("1 HEURE POUR 10 MIN ?", WHITE, 0.3), ("AMENDE SUR LE SALAIRE", RED, 1.8), ("INTERDITE", RED, 3.4)], fond=salon_bg), ("impact", 0.6)),
    ("Neuf fois dix minutes", V.calcul("calcul", "9 RETARDS DE 10 MIN", [("RÉEL", 90, "1 H 30", GREEN, 0.4), ("RETIRÉ", 540, "9 H", RED, 1.8)], "EN MINUTES", fond=salon_bg), ("ticks", 0.6)),
    ("Honnêtement", V.doute("doute", "SANS CROISSANTS, PAS DE CLIENTS", fond=salon_bg), None),
    ("Samedi", V.scene("riposte", "parle", [("5 COLLÈGUES", YEL, 0.3), ("LE CALCUL DE CHACUN, AVEC SON NOM", WHITE, 1.8)], sans_mechant=True, autres=COLLEGUES), ("pop", 0.6)),
    ("Le boulanger pose", V.scene("temoin", "neutre", [("SILENCE", WHITE, 0.2)], sans_mechant=True, autres=COLLEGUES, z=(1.1, 1.15), fx=False), None),
    ("Ma tante me parle pas", V.scene("note", None, [("3 JOURS SANS UN MOT", WHITE, 0.2)], sans_mechant=True, devant=feuille_mur, z=(1.0, 1.06)), ("pop", 2.2)),
    ("Et elle me confie", V.scene("twist", "victoire", [("ELLE ME CONFIE LES PAIES", GREEN, 0.2)], mechant=dict(mouth="smile", clipboard=True)), ("succes", 0.5)),
    ("Cent huit euros, recalculés", V.fin("fin", "108 €", "RECALCULÉS À LA MINUTE PRÈS", "CAS TYPE · CODE DU TRAVAIL L1331-2 · CASS. SOC. 24 NOV. 1992"), ("impact", 0.9)),
])


# ═════════════ 33. ACTU : le SMIC au 1er décembre (le patron) ═════════════

PATRON_A = dict(shirt=(60, 60, 70), pants=(40, 40, 50), hair=(50, 40, 30), glasses=True, tie=True)
BLEU_TRAVAIL = dict(shirt=(50, 80, 150))
GARS_A = [(x, dict(shirt=(50, 80, 150), pants=(40, 40, 60), hair=c, sc=0.85), {}, 0.6 * i, BASE - 60)
          for i, (x, c) in enumerate(zip((150, 300, 450), ((30, 25, 20), (120, 70, 30), (90, 90, 95))))]
V = V2(atelier_bg, PATRON_A, BLEU_TRAVAIL)
SMIC = (recit("s_smic", "33_smic_decembre", "EN PLUS PAR MOIS", 24, "Fin décembre"), [
    ("Mon patron veut garder", V.accroche("h", "MON PATRON", [("24 € PAR MOIS GARDÉS", RED, 0.2), ("SUR LA PAIE DE 8 OUVRIERS", YEL, 1.6)]), ("impact", 1.0)),
    ("Le premier décembre, soit", V.gros_mots("verrou", [("1er DÉCEMBRE", YEL, 0.2), ("LA LIGNE SUR LA FICHE", GREEN, 1.2), ("OU 8 DANS SON BUREAU", RED, 2.6)], kpose="neutre"), ("pop", 0.6)),
    ("Une hausse du SMIC", V.tel("actu", "07:45", [("Actu", "Gouvernement", "SMIC + 1,6 % au 1er déc.", BLEU)]), ("notif", 0.5)),
    ("Un mois plus tôt", V.scene("montee", "victoire", [("JUSTE AVANT NOËL", GREEN, 0.2), ("LES CADEAUX DE MES NIÈCES", YEL, 2.0)], sans_mechant=True), ("pop", 0.8)),
    ("Lundi, il débarque", V.scene("demande", "parle", [("SUR LA PAIE DE DÉCEMBRE, CHEF ?", WHITE, 0.8)], mechant=dict(mouth="flat")), ("whoosh", 0.4)),
    ("Ton SMIC, c'est", V.gp("coup1", ["TON SMIC, C'EST", "UNE ANNONCE À LA TÉLÉ"]), ("impact", 0.8)),
    ("Et en jetant son gobelet", V.geste("geste"), ("whoosh", 0.5)),
    ("Avec ce que tu fais", V.gp("coup2", ["DERRIÈRE TA RABOTEUSE,", "ESTIME-TOI DÉJÀ PAYÉ"], (2.2, 2.4), True, arm=0.8), ("impact", 1.0)),
    ("Je dis rien. Je finis", V.silence("silence"), None),
    ("Une annonce à la télé", V.echo("echo", "UNE ANNONCE À LA TÉLÉ"), ("rate", 0.6)),
    ("Et pourtant, le SMIC", V.gros_mots("prime", [("PAS UNE PRIME", WHITE, 0.8), ("PAS UN CADEAU", RED, 1.8)]), None),
    ("Ce que peu de gens", V.carte("regle", "LE SMIC", [("Un plancher fixé par l'État", 0.8, True), ("il monte pour tous", 2.8, False), ("sans l'accord du patron", 3.8, False)], "CODE DU TRAVAIL · L3231-2", fond=salon_bg), ("pop", 0.8)),
    ("Mais alors, ça fait", V.carte("montant", "AU 1er DÉCEMBRE 2026", [("≈ 1 502 € net par mois", 1.4, True), ("temps plein · décret à paraître", 3.0, False)], "ANNONCE DU GOUVERNEMENT · 9 NOV.", fond=salon_bg), ("ticks", 0.6)),
    ("Sauf que les paies", V.gros_mots("urgence", [("LES PAIES PARTENT AVANT NOËL", YEL, 0.3), ("ÇA SE RÈGLE CETTE SEMAINE", WHITE, 1.8)], fond=salon_bg), None),
    ("Honnêtement", V.doute("doute", "8 PAIES D'UN COUP, ÇA PÈSE", fond=salon_bg), None),
    ("Vendredi", V.scene("riposte", "carte", [("8 FICHES DE PAIE", YEL, 0.3), ("À LA MÊME MINUTE", WHITE, 2.2)], mechant=dict(mouth="o"), kx=560, autres=GARS_A), ("impact", 0.6)),
    ("Sa secrétaire arrête", V.muet("muet", "SILENCE"), None),
    ("Fin décembre", V.fiche("paie", "BULLETIN DE PAIE", "DÉCEMBRE", [("SMIC revalorisé", "≈ 1 502 € net", 0.4, True)], kpose="victoire", fond=salon_bg), ("succes", 0.6)),
    ("je le vois au journal", V.tv("tv", "JOURNAL RÉGIONAL", "« LE SMIC ? LA MOINDRE DES CHOSES »"), ("notif", 0.4)),
    ("Vingt-quatre euros, et c'est", V.fin("fin", "24 €", "ET C'EST LUI À LA TÉLÉ", "SMIC + 1,6 % AU 1er DÉC. 2026 · ANNONCE DU 9 NOV. · DÉCRET À PARAÎTRE"), ("impact", 0.9)),
])


# ═════════════ 34. La machine offerte (la belle-mère) ═════════════

BELLE_MERE = dict(shirt=(190, 60, 60), pants=(50, 50, 60), hair=(200, 190, 170), long_hair=True, glasses=True)
TECH = dict(shirt=(50, 80, 150), pants=(50, 80, 150), hair=(40, 30, 25), cap=(50, 80, 150))
BEAU_PERE_B = dict(shirt=(110, 120, 140), pants=(50, 50, 60), hair=(170, 170, 170), sc=0.85)
V = V2(salon_bg, BELLE_MERE)
GARANTIE = (recit("s_garantie", "34_garantie_legale", "PAYÉ PAR LE MAGASIN", 650, "Samedi, elle est"), [
    ("Ma belle-mère me réclame", V.accroche("h", "MA BELLE-MÈRE", [("650 € RÉCLAMÉS", RED, 0.2), ("POUR LA MACHINE QU'ELLE A OFFERTE", YEL, 1.6)], devant=salon_machine_d, mx=700), ("impact", 1.0)),
    ("Et samedi, elle revient", V.scene("verrou", "neutre", [("SAMEDI : LE BAIN DE LA PETITE", YEL, 0.2)], sans_mechant=True, devant=salon_machine_d), ("pop", 0.5)),
    ("Quatorze mois après", V.scene("panne", "choc", [("14 MOIS APRÈS", WHITE, 0.2), ("PLUS D'ESSORAGE", RED, 1.2)], sans_mechant=True, devant=salon_fumee), ("impact", 0.6)),
    ("C'était son cadeau", V.scene("montee", "victoire", [("SON CADEAU DE NAISSANCE", GREEN, 0.2)], mechant=dict(mouth="smile", arm=0.5), mx=700, devant=salon_machine_d), ("pop", 0.8)),
    ("Je lui ai dit, avec", V.scene("merci", "parle", [("TRANQUILLES DIX ANS", WHITE, 0.4)], mechant=dict(mouth="grin"), mx=700, devant=salon_machine_d), None),
    ("Elle passe tous les soirs", V.scene("entree", "neutre", [("ELLE A LES CLÉS", YEL, 0.3)], mechant=dict(mouth="grin"), mx=700, devant=salon_machine_d), ("whoosh", 0.5)),
    ("Tu la bourres", V.gp("coup1", ["TU LA BOURRES COMME", "UN SAC POUBELLE"]), ("impact", 0.8)),
    ("Et en refermant la porte", V.geste("geste", "ELLE EN RAJOUTE"), ("whoosh", 0.5)),
    ("Quand on vit à trois", V.gp("coup2", ["À TROIS DANS UN", "DEUX-PIÈCES, ON LAVE", "À LA MAIN"], (2.2, 2.4), True, arm=0.8), ("impact", 1.0)),
    ("Je laisse passer", V.scene("silence", "triste", sans_mechant=True, devant=radiateur, z=(1.0, 1.04), fx=False), None),
    ("Un sac poubelle", V.echo("echo", "UN SAC POUBELLE"), ("rate", 0.6)),
    ("Et pourtant, le magasin", V.tel("magasin", "16:20", [("Magasin", "Réponse", "Voyez avec la marque", GRIS)], "choc"), ("notif", 0.5)),
    ("Ce que peu de gens", V.carte("regle", "DEUX GARANTIES", [("La marque : 1 an", 0.8, False), ("La loi : 2 ans", 2.0, True), ("due par le VENDEUR", 3.4, False)], "CODE DE LA CONSOMMATION · L217-3"), ("pop", 0.8)),
    ("Mais alors, faut prouver", V.gros_mots("preuve", [("PROUVER QUE C'EST PAS MOI ?", WHITE, 0.3), ("NON", RED, 1.6), ("PRÉSUMÉE D'ORIGINE", GREEN, 2.4)]), ("impact", 0.6)),
    ("Sauf qu'il faut la facture", V.gros_mots("facture", [("IL FAUT LA FACTURE", YEL, 0.3), ("ELLE EST CHEZ ELLE", RED, 1.4)]), None),
    ("Honnêtement", V.doute("doute", "JE LA REMPLIS TROP ?"), None),
    ("Alors je la prends", V.fiche("tiroir", "FACTURE", "PRISE DANS SON TIROIR", [("Lave-linge", "650 €", 0.3, False), ("Réclamation au magasin", "", 1.4, True)], kpose="carte"), ("pop", 0.5)),
    ("Samedi, elle est", V.scene("technicien", "neutre", [("DÉFAUT DE FABRICATION", GREEN, 3.4)], mechant=dict(mouth="flat"), mx=850, devant=salon_machine_d, autres=[(520, TECH, dict(mouth="smile", arm=0.3), 1.1), (690, BEAU_PERE_B, dict(mouth="o"), 0.4, BASE - 50)]), ("succes", 0.8)),
    ("Ma belle-mère reste", V.muet("muet", "PLANTÉE LÀ"), None),
    ("Le lundi, elle m'envoie", V.tel("twist", "09:05", [("Belle-maman", "3 photos", "Factures de ses copines", GREEN)], "victoire"), ("notif", 0.5)),
    ("Six cent cinquante euros, son", V.fin("fin", "650 €", "SON CADEAU TOURNE ENCORE", "CAS TYPE · CODE DE LA CONSOMMATION L217-3 ET SUIVANTS"), ("impact", 0.9)),
])


VIDEOS = {"carte": CARTE, "colis": COLIS, "salaire": SALAIRE, "voiture": VOITURE, "dentiste": DENTISTE_V,
          "retard": RETARD, "smic": SMIC, "garantie": GARANTIE}

if __name__ == "__main__":
    rec, beats = VIDEOS[sys.argv[1]]
    rec.fabriquer(beats)
