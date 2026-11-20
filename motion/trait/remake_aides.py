"""REMAKE plan par plan de « 6 aides avant le 31 décembre » (règle : prompts/regle_remake.md ;
découpage : prompts/remakes/aides_31dec_decoupage.md). Chaque plan démarre au MÊME instant que dans l'original.
Seuls changent : nos personnages, notre texte (remake_aides_texte.py), quelques chiffres non vérifiés.

    python3 motion/trait/remake_aides.py --stills 1,5,20
    python3 motion/trait/remake_aides.py --jobs 4        → output/trait/remake_aides.mp4
"""
import argparse
import math
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cairo  # noqa: E402
from PIL import Image  # noqa: E402

import decors as DC  # noqa: E402
import decors_ville as V  # noqa: E402
import ui  # noqa: E402
import voix  # noqa: E402
from dessin import (FPS, H, INK, LW, ROOT, W, back, circle, couche_floue, dark, ease, ease_out, ecrit, flat, halo,  # noqa: E402
                    mix, paint, pil_to_surface, poly, rrect, stroke, texte, tube)
from film import Film  # noqa: E402
from perso import Perso, traits_choc  # noqa: E402
from remake_aides_texte import DUREE, MODELE, PHRASES, VOIX  # noqa: E402
from six_aides_31dec import KEVIN, MECANOS, PATRON, SOL, Y_SOUS, assombrir, deg, enseigne, fenetre, feuille, \
    horloge, lumiere_sol, piece, reflet_doux  # noqa: E402

OUT = ROOT / "output/trait/remake_aides.mp4"
WORK = ROOT / "output/trait/_work_remake_v4"
PHOTOS = ROOT / "assets/photos_libres"
VIE = {"pousse": 0.02, "derive": 8.0, "roulis": 0.0}      # caméra calme (client : « trop de mouvement caméra »)

YANIS = dict(cheveux="court", couleur_cheveux=(40, 30, 26), peau=(170, 120, 90), haut="sweat",
             couleur_haut=(90, 96, 110), bas=(50, 56, 70), chaussures=(40, 40, 46), lunettes=True, seed=31, tete=0.84,
             mince=0.9)
SARAH = dict(cheveux="chignon", couleur_cheveux=(90, 56, 30), peau=(236, 196, 160), haut="sweat",
             couleur_haut=(255, 196, 40), bas=(60, 60, 90), chaussures=(240, 240, 240), seed=33, tete=0.84, mince=0.86)
LEA = dict(cheveux="chignon", couleur_cheveux=(40, 28, 24), peau=(200, 140, 100), haut="sweat",
           couleur_haut=(120, 120, 130), bas=(50, 50, 60), chaussures=(240, 240, 240), seed=35, tete=0.84, mince=0.86)
AGENTE = dict(cheveux="chignon", couleur_cheveux=(170, 170, 176), peau=(236, 196, 170), haut="sweat",
              couleur_haut=(130, 30, 50), bas=(60, 40, 50), chaussures=(40, 30, 30), lunettes=True, seed=37, tete=0.84,
              mince=0.9)
COUL = {6: (240, 120, 40), 5: (60, 130, 240), 4: (60, 170, 110), 3: (230, 50, 70), 2: (130, 80, 210),
        1: (255, 196, 30)}
ICONE = {6: ("points", "essence"), 5: ("points", "flamme"), 4: ("points", "maison"), 3: ("points", "coeur"),
         2: ("points", "calendrier"), 1: ("soleil", "bus")}
ECH = {6: 0.8, 5: 0.92, 4: 1.06, 3: 1.22, 2: 1.4, 1: 1.7}      # le domino de chaque aide grossit


# ═════════════ outils d'écran ═════════════

@lru_cache(maxsize=8)
def photo(nom):
    return pil_to_surface(Image.open(PHOTOS / nom).convert("RGBA"))


def plan_photo(ctx, nom, lt, z0=1.0, z1=1.08, duree=2.0):
    s = photo(nom)
    k = min(1.0, lt / duree)
    z = (z0 + (z1 - z0) * k) * W / s.get_width()
    ctx.save()
    ctx.identity_matrix()
    ctx.translate(W / 2, H / 2)
    ctx.scale(z, z)
    ctx.set_source_surface(s, -s.get_width() / 2, -s.get_height() / 2)
    ctx.paint()
    ctx.restore()


def fond_sombre_flou(ctx, t, teinte=(26, 28, 44)):
    deg(ctx, -600, -600, 1700, 2600, mix(teinte, (0, 0, 0), 0.2), teinte)
    def bokeh(c):
        for i in range(14):
            x = (i * 211 + 60 * math.sin(t * 0.4 + i)) % 1300 - 100
            y = (i * 377) % 1900
            halo(c, x, y, 90 + (i % 4) * 40, (255, 200, 120) if i % 3 else (120, 150, 255), 0.22)
    couche_floue(ctx, bokeh, rayon=24, bord="constant")


def avatar(ctx, x, y, s=1.0, nom="LE PATRON"):
    """Vignette du patron (comme la petite tête « source » de l'original)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -60, -60, 120, 120, 24)
    paint(ctx, (60, 90, 150), LW, shade=0.9)
    circle(ctx, 0, 6, 40)
    paint(ctx, (236, 186, 150), LW * 0.8, shade=0.9)
    for sx in (-1, 1):
        circle(ctx, sx * 14, 0, 9)
        stroke(ctx, 3)
    ctx.move_to(-14, 24)
    ctx.curve_to(-6, 18, 6, 18, 14, 24)
    stroke(ctx, 4)
    rrect(ctx, -70, 52, 140, 34, 10)
    paint(ctx, (250, 250, 250), LW * 0.6, shade=1)
    ecrit(ctx, nom, 0, 69, 18, INK, big=True)
    ctx.restore()


def mains(ctx, xg, xd, y, couleur=(46, 170, 120)):
    """Deux mains (manches vertes de Kévin) qui tiennent une feuille par le bas."""
    for x, sx in ((xg, -1), (xd, 1)):
        tube(ctx, [(x + sx * 140, y + 420), (x + sx * 40, y + 120), (x, y + 10)], 70, couleur)
        circle(ctx, x, y, 40)
        paint(ctx, (198, 138, 98), LW, shade=0.9)


def doc_tenu(ctx, t, lt, titre, lignes, surl=(), couleur=(60, 110, 220), y=760, h=560, avatar_ok=True):
    """Document en gros plan tenu à deux mains ; les lignes de `surl` sont surlignées l'une après l'autre."""
    x0, w = 90, 900
    bob = 8 * math.sin(t * 2.0)
    ctx.save()
    ctx.translate(0, bob)
    ctx.rotate(-0.025 + 0.01 * math.sin(t * 1.3))
    rrect(ctx, x0 + 12, y + 12, w, h, 14)
    flat(ctx, (0, 0, 0), 0.3)
    rrect(ctx, x0, y, w, h, 14)
    paint(ctx, (252, 250, 244), LW, shade=0.96)
    rrect(ctx, x0, y, w, 110, 14)
    flat(ctx, couleur)
    ctx.rectangle(x0, y + 70, w, 40)
    flat(ctx, couleur)
    ecrit(ctx, titre, x0 + w / 2, y + 56, 60, (255, 255, 255), big=True)
    for i, l in enumerate(lignes):
        yy = y + 170 + i * 100
        for j, (ts, s) in enumerate(surl):
            if s == i and lt > ts:
                sw = texte(l, 44, INK).get_width()
                rrect(ctx, x0 + 50, yy - 34, (sw + 30) * ease((lt - ts) / 0.4), 68, 8)
                flat(ctx, (255, 214, 60), 0.95)
        ecrit(ctx, l, x0 + 64, yy, 44, INK, ax=0, big=i > 0)
    ctx.restore()
    mains(ctx, x0 + 60, x0 + w - 60, y + h - 40 + bob)
    if avatar_ok:
        avatar(ctx, W / 2, y - 120, 0.9)


def carte_numero(ctx, t, lt, n, nom, sous):
    """Carte d'une aide : pastilles 6..1, grand chiffre, nom, montant, domino qui arrive en tournant (de plus en plus gros)."""
    fond_sombre_flou(ctx, t)
    c = COUL[n]
    for j, m in enumerate((6, 5, 4, 3, 2, 1)):
        x = 110 + j * 64
        fait = m > n
        rrect(ctx, x - 24, 430, 48, 48, 10)
        paint(ctx, COUL[m] if m == n else ((90, 90, 104) if fait else (52, 52, 66)), LW * 0.6, shade=1)
        ecrit(ctx, str(m), x, 455, 28, INK if m == n else (200, 200, 210), big=True)
    k = back(lt / 0.4)
    if n == 1:
        ecrit(ctx, "LA PLUS GROSSE", 90, 560, 30, c, ax=0, big=True, alpha=min(1, lt * 4))
    else:
        ecrit(ctx, "AIDE", 90, 560, 30, c, ax=0, big=True, alpha=min(1, lt * 4))
    ecrit(ctx, str(n), 90, 700, 320, (255, 255, 255), ax=0, big=True, scale=k)
    ctx.rectangle(90, 820, 90 * ease(lt / 0.5), 10)
    flat(ctx, c)
    ecrit(ctx, nom, 90, 900, 84, (255, 255, 255), ax=0, big=True, alpha=ease((lt - 0.15) / 0.3))
    ecrit(ctx, sous, 90, 985, 44, (200, 200, 210), ax=0, alpha=ease((lt - 0.3) / 0.3))
    # domino qui arrive en tournant
    u = ease_out(lt / 0.6)
    s = ECH[n] * (0.6 + 0.4 * u)
    ang = (1 - u) * 1.4 - 0.25 + 0.04 * math.sin(t * 2)
    hx, bx = ICONE[n]
    halo(ctx, 800, 600, 320 * ECH[n], c, 0.25)
    ctx.save()
    ctx.translate(800 + 260 * (1 - u), 600 - 150 * ECH[n])
    ctx.rotate(ang)
    V.domino(ctx, -75 * s, 140 * s, s, 0.0, hx, bx, montant="1 000 €" if n == 1 else None,
             lueur=1.0 if n == 1 else 0.0, couleur=(250, 236, 170) if n == 1 else (250, 246, 232))
    ctx.restore()


def fiche(ctx, t, lt, n, nom, champs, limite, fond=None):
    """Fiche « AIDE N° n · À GARDER »."""
    if fond:
        fond(ctx, t, lt)
        assombrir(ctx, 0.45)
    else:
        fond_sombre_flou(ctx, t)
    c = COUL[n]
    k = back(lt / 0.35)
    ctx.save()
    ctx.translate(W / 2, 760 + 8 * math.sin(t * 1.8))
    ctx.scale(k, k)
    hh = 260 + 110 * len(champs)
    rrect(ctx, -440 + 12, -hh / 2 + 12, 880, hh, 24)
    flat(ctx, (0, 0, 0), 0.3)
    rrect(ctx, -440, -hh / 2, 880, hh, 24)
    paint(ctx, (252, 250, 246), LW, shade=0.97)
    rrect(ctx, -440, -hh / 2, 880, 14, 7)
    flat(ctx, c)
    circle(ctx, -370, -hh / 2 + 80, 34)
    paint(ctx, c, LW * 0.7, shade=1)
    ecrit(ctx, f"AIDE N° {n} · À GARDER", -320, -hh / 2 + 60, 24, c, ax=0, big=True)
    ecrit(ctx, nom, -320, -hh / 2 + 108, 60, INK, ax=0, big=True)
    for i, (lab, val) in enumerate(champs):
        yy = -hh / 2 + 190 + i * 110
        ecrit(ctx, lab.upper(), -380, yy, 26, (130, 130, 140), ax=0, big=True)
        ecrit(ctx, val, -380, yy + 44, 42, INK, ax=0, big=True)
    yy = hh / 2 - 70
    rrect(ctx, -400, yy - 30, 800, 60, 10)
    flat(ctx, (232, 52, 60), 0.12)
    ecrit(ctx, f"Date limite : {limite}", -370, yy, 30, (220, 40, 50), ax=0, big=True)
    ctx.restore()


def construire(work):
    voice, words = voix.build_cale(PHRASES, VOIX, work, model=MODELE, fin=DUREE, vmax=2.0)
    f = Film(voice, words, fin=DUREE + 0.2)
    _plan = f.plan
    f.plan = lambda debut, scene, cam=None, **kw: _plan(debut, scene, cam, **{**kw, 'fouet': False})
    f.vie = VIE

    kev, pat, yan, sar, lea, age = (Perso(**d) for d in (KEVIN, PATRON, YANIS, SARAH, LEA, AGENTE))
    mecs = [Perso(**m) for m in MECANOS]

    def bouche(t, qui):
        return f.bouche(t, qui)

    # ── jeu des personnages (temps de l'original) ──
    kev.pose(0, "repos").emotion(0, "neutre").emotion(7.5, "neutre").emotion(9.2, "choc")
    kev.emotion(13.3, "content").emotion(32.5, "neutre").pose(34.3, "leve").emotion(34.3, "choc").pose(35.5, "repos")
    kev.pose(43.4, "pointe_g").emotion(43.4, "malin").pose(48.0, "repos").pose(57.4, "leve").emotion(57.4, "content")
    kev.pose(58.4, "repos").emotion(71.0, "choc").emotion(73.0, "neutre").pose(85.1, "pointe").emotion(85.1, "malin")
    kev.pose(86.5, "repos").emotion(106.0, "neutre").emotion(112.0, "triste").emotion(121.2, "content")
    kev.emotion(127.0, "neutre").emotion(131.0, "malin").pose(142.0, "repos").emotion(144.2, "malin")
    kev.pose(144.2, "pointe").pose(152.0, "leve").emotion(152.0, "content")
    pat.pose(0, "mains_hanches").emotion(0, "neutre").pose(4.2, "pointe_g").emotion(4.2, "malin").pose(6.0, "repos")
    pat.pose(126.2, "repos").emotion(126.2, "malin").pose(129.6, "haussement").emotion(131.0, "neutre")
    pat.pose(142.0, "leve").emotion(142.0, "colere").pose(143.3, "mains_hanches").emotion(143.3, "malin")
    pat.pose(144.2, "repos").emotion(146.5, "choc").emotion(148.4, "neutre").pose(150.1, "objet").emotion(152.0, "content")
    pat.pose(152.0, "leve")
    pat.objet = lambda c, x, y, s: (rrect(c, x - 110, y - 160, 220, 260, 8), paint(c, (252, 248, 236), LW, shade=0.95),
                                    ecrit(c, "PRIME", x, y - 120, 34, (220, 50, 60), big=True),
                                    ecrit(c, "SIGNÉE", x, y - 60, 34, (30, 150, 80), big=True))
    yan.pose(0, "repos").emotion(0, "triste").emotion(36.7, "colere").emotion(38.4, "triste")
    yan.pose(53.0, "objet").emotion(57.4, "content").pose(57.4, "leve").pose(58.4, "repos")
    yan.emotion(65.4, "neutre").emotion(71.0, "choc").emotion(73.0, "neutre").pose(77.7, "leve").emotion(77.7, "content")
    yan.pose(78.7, "repos").pose(152.0, "leve").emotion(152.0, "content")
    yan.objet = lambda c, x, y, s: (rrect(c, x - 90, y - 70, 180, 110, 8), paint(c, (60, 64, 76), LW, shade=0.9),
                                    rrect(c, x - 76, y - 58, 152, 80, 4), flat(c, (150, 200, 240)))
    sar.pose(0, "repos").emotion(0, "neutre").pose(59.6, "leve").emotion(59.6, "content")
    lea.pose(0, "objet").emotion(0, "neutre").emotion(83.1, "triste").emotion(95.7, "content").pose(152.0, "leve")
    lea.objet = lambda c, x, y, s: V.billet(c, x, y - 40, 1.2, -0.1)
    age.pose(0, "repos").emotion(0, "content").pose(77.7, "pointe").pose(78.5, "repos")
    for i, m in enumerate(mecs):
        m.pose(0, "leve").emotion(0, "content")

    # ═════════ 0 – 6,4 : les dominos de plus en plus grands ═════════
    E = [1.16 * 1.236 ** i for i in range(6)]
    HT = [280 * s for s in E]
    LG = [150 * s for s in E]
    XD = [470.0]
    for i in range(5):
        XD.append(XD[-1] + LG[i] + 0.5 * HT[i])
    CENTRE = [x + w / 2 for x, w in zip(XD, LG)]
    A_CHOC = math.asin(0.5)
    X_PAT = XD[5] + LG[5] + 520
    PET = [("points", "essence"), ("points", "flamme"), ("points", "maison"), ("points", "coeur"),
           ("points", "calendrier")]

    def ang(i, t, pas=0.45):
        t0 = i * pas
        u = (t - t0) / pas
        if u <= 0:
            return 0.0
        if u < 1:
            return A_CHOC * u * u
        v = t - t0 - pas
        if i == 4:
            return A_CHOC - 0.05 * math.exp(-v * 10) * abs(math.sin(v * 24))
        return A_CHOC + (1.36 - A_CHOC) * ease(v / 0.6)

    def ang_geant(t):
        if t < 2.25:
            return 0.0
        if t < 4.0:
            v = t - 2.25
            return 0.03 * math.exp(-v * 3.5) * math.sin(v * 18)
        return 0.21 * ease_out((t - 4.0) / 0.5) - 0.012 * math.sin((t - 4.0) * 7) * math.exp(-(t - 4.0))

    def dominos(ctx, t, lt):
        piece(ctx, mur=(38, 44, 84), mur2=(20, 24, 50), sol=(34, 34, 56), x0=-800, x1=5600)
        fenetre(ctx, t, -300, -500, 5600, 1600, seed=7, montants=12)

        def objets(c):
            kev.draw(c, 300, SOL, 0.72, t, regard=0.6)
            for i, (hh, bb) in enumerate(PET):
                V.domino(c, XD[i], SOL, E[i], ang(i, t), hh, bb)
            V.domino(c, XD[5], SOL, E[5], ang_geant(t), "soleil", "bus", "1 000 €", lueur=1.0 if t > 3.2 else 0.0,
                     couleur=(250, 236, 170))
            pat.draw(c, X_PAT, SOL, 0.78, t, regard=-0.6)
        lumiere_sol(ctx, XD[5], 900, 0.22)
        reflet_doux(ctx, objets)
        objets(ctx)
        if t >= 2.0:
            u = t - 2.0
            y = -900 + (SOL - HT[5] - 200 + 900) * min(1.15, 1 - math.exp(-u * 6) * math.cos(u * 12))
            xc = XD[5] + 60
            ctx.move_to(xc, -1800)
            ctx.line_to(xc, y - 150)
            stroke(ctx, 4)
            DC.calendrier(ctx, xc, y, 0.9, "DÉC", "31")

    def cam_chaine(lt):
        fi = min(5.0, max(0.0, lt / 0.45 - 0.2 + 0.6 * ease(lt / 1.4)))
        i = min(4, int(fi))
        k = fi - i
        cx = CENTRE[i] + (CENTRE[i + 1] - CENTRE[i]) * k - 420 * (1 - ease(lt / 1.0))
        z = 1.18 * 1.236 ** (-0.38 * fi)
        return cx, SOL - 370 / z, z

    gx = XD[5] + LG[5] / 2
    f.plan(0, dominos, cam_chaine, fouet=False)
    f.plan(2.4, dominos, [(0, gx + 140, SOL - 380 / 0.95, 0.95), (1.6, gx + 200, SOL - 380 / 0.95, 0.95),
                          (3.4, gx + 330, SOL - 380 / 0.9, 0.9)], fouet=False)

    # ═════════ 6,4 – 18 : la station, la pompe, le panneau ═════════
    f.plan(6.43, lambda c, t, lt: plan_photo(c, "station_nuit.jpg", lt, 1.0, 1.08, 1.1))
    SX = 1560

    def montant(t):
        return 89.98 * ease((t - 7.6) / 2.2) if t >= 7.6 else 0.0

    def dehors(ctx, t, lt, pompe=True, prix=None, pistolet=False, medaille=False, pieces=False):
        deg(ctx, -800, -900, 2000, SX - 300, (40, 52, 100), (226, 160, 140))
        couche_floue(ctx, lambda c: (V.immeubles(c, -700, 1900, SX - 220, t, seed=5, col=(84, 90, 140), hmin=260, hmax=620),
                                     V.immeubles(c, -600, 1900, SX - 160, t, seed=9, col=(64, 70, 116), hmin=140, hmax=380)),
                     rayon=12, bord="constant")
        deg(ctx, -800, SX - 180, 2000, 2600, (74, 74, 90), (44, 44, 56))
        V.panneau_route(ctx, 860, 640, "BUREAU →", "20 km")
        if medaille and t > 14.0:
            k = back((t - 14.0) / 0.3)
            ctx.save()
            ctx.translate(930, 480)
            ctx.scale(k, k)
            circle(ctx, 0, 0, 80)
            paint(ctx, (60, 170, 110), LW, shade=0.9)
            ecrit(ctx, "TRAJET", 0, -14, 26, (255, 255, 255), big=True)
            ecrit(ctx, "TRAVAIL", 0, 20, 26, (255, 255, 255), big=True)
            ctx.restore()
        V.voiture(ctx, 900, SX, 0.95, (40, 150, 170))
        if pompe:
            V.pompe(ctx, 290, SX, prix or f"{montant(t):05.2f} €".replace(".", ","), t)
            kev.draw(ctx, 640, SX, 0.84, t, regard=-0.8)
        if pistolet and t > 8.0:
            k = back((t - 8.0) / 0.35)
            s = photo("pistolet.jpg")
            ctx.save()
            ctx.translate(760, 560)
            ctx.rotate(0.08)
            ctx.scale(k * 0.48, k * 0.48)
            rrect(ctx, -s.get_width() / 2 - 30, -s.get_height() / 2 - 30, s.get_width() + 60, s.get_height() + 120, 10)
            paint(ctx, (250, 250, 250), LW * 3, shade=1)
            ctx.set_source_surface(s, -s.get_width() / 2, -s.get_height() / 2)
            ctx.paint()
            ctx.restore()
        if 9.2 <= t < 11:
            d = t - 9.2
            for i in range(8):
                a = -1.3 + i * 0.32
                r = 120 + 800 * d * (0.7 + 0.1 * (i % 3))
                V.billet(ctx, 290 + math.cos(a) * r * 0.8, 840 + math.sin(a) * r * 0.6 + 380 * d * d, 1.0,
                         d * (3 + i) * (1 if i % 2 else -1))
        if pieces and t > 15.4:
            for i in range(10):
                v = ((t - 15.4) * 1.3 + i * 0.1) % 1
                circle(ctx, 140 + i * 30, 1300 + 260 * v, 18)
                paint(ctx, (230, 190, 70), LW * 0.6, shade=0.9)
        if pieces and t > 17.0:
            DC.etiquette(ctx, 720, 760, 0.8, "100 €", t - 17.0, couleur=(110, 220, 140))
    f.plan(7.5, lambda c, t, lt: dehors(c, t, lt, pistolet=True), [(0, 520, 1000, 1.0), (2.6, 500, 980, 1.08)])
    f.plan(10.17, lambda c, t, lt: dehors(c, t, lt), [(0, 820, 760, 1.25), (1.3, 820, 740, 1.32)])

    # ═════════ les cartes « numéro » et les fiches « à garder » ═════════
    NUM = {6: ("Aide carburant", "100 €"), 5: ("Chèque énergie", "jusqu'à 277 €"), 4: ("CCAS de ta mairie", "colis, chauffage"),
           3: ("Don à 75 %", "75 % rendus"), 2: ("Rachat de RTT", "+25 %, sans impôt"), 1: ("Prime transport", "jusqu'à 1 000 €")}
    for n, t0 in ((6, 11.47), (5, 38.37), (4, 64.0), (3, 87.6), (2, 110.0), (1, 132.0)):
        f.plan(t0, lambda c, t, lt, n=n: carte_numero(c, t, lt, n, *NUM[n]), [(0, 540, 960, 1.0)])

    f.plan(13.27, lambda c, t, lt: dehors(c, t, lt, medaille=True), [(0, 820, 760, 1.25), (2.1, 820, 760, 1.3)])
    f.plan(15.4, lambda c, t, lt: dehors(c, t, lt, prix="90,00 €", pieces=True), [(0, 440, 1000, 1.1), (2.7, 440, 980, 1.16)])

    # ═════════ 18 – 24 : le plafond de revenus ═════════
    def bareme(ctx, t, lt):
        fond_sombre_flou(ctx, t, (40, 34, 30))
        avatar(ctx, W / 2, 520)
        ctx.save()
        ctx.translate(0, 8 * math.sin(t * 1.7))
        rrect(ctx, 110, 640, 860, 520, 18)
        paint(ctx, (252, 250, 246), LW, shade=0.97)
        rrect(ctx, 110, 640, 860, 12, 6)
        flat(ctx, COUL[6])
        ecrit(ctx, "AIDE CARBURANT · CONDITION", 150, 700, 22, COUL[6], ax=0, big=True)
        ecrit(ctx, "Plafond de revenus", 150, 755, 60, INK, ax=0, big=True)
        for i, (lab, val, t0, c) in enumerate((("SEUL", "22 770 € / an", 20.0, (60, 120, 220)),
                                               ("EN COUPLE", "45 540 € / an", 22.3, (150, 80, 220)))):
            yy = 860 + i * 140
            ecrit(ctx, lab, 150, yy, 32, (130, 130, 140), ax=0, big=True)
            rrect(ctx, 150, yy + 40, 780, 30, 15)
            flat(ctx, (232, 232, 238))
            k = ease((t - t0) / 0.8)
            if k > 0:
                rrect(ctx, 150, yy + 40, 780 * 0.62 * k, 30, 15)
                flat(ctx, c)
                ecrit(ctx, val, 930, yy, 40, INK, ax=1, big=True, alpha=k)
        ctx.restore()
    f.plan(18.07, bareme, [(0, 540, 960, 1.0), (5.9, 540, 960, 1.05)])

    # ═════════ 24 – 30 : la demande en ligne ═════════
    def demande(ctx, t, lt):
        dehors(ctx, t, lt, pompe=False)
        assombrir(ctx, 0.35)
        jour = "5" if t < 28.0 else ("10" if t < 29.0 else "15")
        DC.calendrier(ctx, 230, 760, 0.95, "NOV", jour)
        if t >= 28.0:
            ecrit(ctx, "+5 jours" if t < 29.0 else "+10 jours", 230, 930, 30, (255, 214, 60), big=True)

        def ecran(c, w, h):
            c.rectangle(0, 0, w, h)
            c.set_source_rgb(0.98, 0.98, 1.0)
            c.fill()
            ecrit(c, "DEMANDE EN LIGNE", 10, 16, 7, (120, 120, 130), ax=0, big=True)
            ecrit(c, "Aide carburant", 10, 32, 11, INK, ax=0, big=True)
            for i, (lab, val, t0) in enumerate((("Plaque", "AB-123-CD", 26.0), ("N° de carte grise", "2026AB•••", 27.0))):
                ecrit(c, lab, 10, 56 + i * 40, 7, (120, 120, 130), ax=0)
                rrect(c, 8, 62 + i * 40, w - 16, 20, 4)
                c.set_source_rgb(0.92, 0.92, 0.95)
                c.fill()
                n = int(len(val) * min(1.0, max(0.0, (t - t0) / 0.7)))
                if n:
                    ecrit(c, val[:n], 14, 72 + i * 40, 8, INK, ax=0, big=True)
            if t < 29.0:
                rrect(c, 14, 150, w - 28, 24, 12)
                c.set_source_rgb(0.2, 0.5, 0.95) if t < 28.0 else c.set_source_rgb(0.2, 0.7, 0.4)
                c.fill()
                ecrit(c, "Valider" if t < 28.0 else "Demande envoyée", w / 2, 162, 8, (255, 255, 255), big=True)
            else:
                circle(c, 24, 160, 12)
                c.set_source_rgb(0.2, 0.7, 0.4)
                c.fill()
                ecrit(c, "Virement reçu + 100 €", 40, 160, 8, (30, 140, 70), ax=0, big=True)
        DC.telephone(ctx, 700, 840, 3.0, ecran=ecran, t=t, rot=0.03 * math.sin(t))
        rrect(ctx, 80, 1060, 330, 190, 12)
        paint(ctx, (120, 200, 150), LW, shade=0.92)
        ecrit(ctx, "CARTE GRISE", 245, 1100, 28, INK, big=True)
        ecrit(ctx, "AB-123-CD", 245, 1160, 34, INK, big=True)
        ecrit(ctx, "N° 2026AB•••", 245, 1210, 24, INK)
    f.plan(24.0, demande, [(0, 540, 960, 1.0), (6.1, 540, 960, 1.05)])

    f.plan(30.13, lambda c, t, lt: fiche(c, t, lt, 6, "Aide carburant",
                                         [("Montant", "100 €"), ("Pour qui", "revenu fiscal < 22 770 € / part"),
                                          ("Carburant", "essence ou diesel, trajet travail"), ("Où", "site des impôts")],
                                         "31/12", fond=lambda c2, t2, l2: dehors(c2, t2, l2, pompe=False)),
           [(0, 540, 960, 1.0)])

    # ═════════ 32,5 – 58,5 : chez Yanis ═════════
    def salon(ctx, t, lt, ordi=False, cercle=False, gain=False):
        piece(ctx, mur=(60, 66, 90), mur2=(36, 40, 60), sol=(70, 64, 70))
        fenetre(ctx, t, 60, 300, 380, 520, seed=41, ciel=((14, 18, 40), (40, 50, 90)))
        for i in range(30):                                     # neige derrière la fenêtre
            r = (i * 0.618) % 1
            circle(ctx, 80 + (r * 340 + 30 * math.sin(t + i)) % 340, 320 + ((i * 97 + 140 * t) % 490), 6)
            flat(ctx, (255, 255, 255), 0.7)
        rrect(ctx, 600, 330, 70, 380, 35)                       # thermomètre
        paint(ctx, (250, 250, 250), LW, shade=0.9)
        rrect(ctx, 620, 560, 30, 130, 15)
        flat(ctx, (60, 120, 230))
        ecrit(ctx, "16°", 730, 620, 56, (255, 255, 255), big=True)
        rrect(ctx, 760, 330, 200, 240, 14)                      # compteur électrique
        paint(ctx, (200, 204, 210), LW, shade=0.88)
        circle(ctx, 860, 450, 70)
        paint(ctx, (240, 240, 236), LW * 0.8, shade=0.9)
        ecrit(ctx, "001 284", 860, 450, 26, INK, big=True)
        if cercle and t > 54.0:
            circle(ctx, 860, 450, 110 + 6 * math.sin(t * 6))
            stroke(ctx, 10, (255, 214, 60))
        DC.canape(ctx, 330, SOL, 560, (60, 70, 100))
        yan.draw(ctx, 330, SOL + 130, 0.8, t, bouche=bouche(t, "yan"), regard=0.5)
        hd = yan.draw  # (le bonnet est dessiné après)
        DC.canape_avant(ctx, 330, SOL, 560, (60, 70, 100))
        for i in range(2):                                      # buée
            v = (t * 0.7 + i * 0.5) % 1
            circle(ctx, 360 + 20 * math.sin(v * 6), 600 - 120 * v, 14 + 22 * v)
            flat(ctx, (255, 255, 255), 0.35 * (1 - v))
        rrect(ctx, 880, SOL - 110, 140, 110, 10)                # carton
        paint(ctx, (196, 150, 100), LW, shade=0.85)
        kev.objet = None
        kev.draw(ctx, 820, SOL + 140, 0.86, t, regard=-0.6)
        if gain and t > 57.4:
            DC.etiquette(ctx, 600, 860, 0.9, "+48 €", t - 57.4, couleur=(110, 220, 140))
    f.plan(32.5, salon, [(0, 540, 900, 1.0), (1.8, 540, 880, 1.04)])
    f.plan(34.3, salon, [(0, 700, 760, 1.3), (2.4, 700, 760, 1.35)])
    f.plan(36.7, salon, [(0, 330, 760, 1.7), (1.6, 330, 760, 1.76)])
    f.plan(40.2, lambda c, t, lt: cartons(c, t, lt), [(0, 540, 960, 1.0), (1.8, 560, 960, 1.1)])

    def cartons(ctx, t, lt):
        deg(ctx, -600, -600, 1700, 2600, (120, 90, 60), (60, 44, 30))
        for i, (x, y, w_, h_, r) in enumerate(((-80, 200, 640, 520, -0.1), (480, 120, 620, 560, 0.08),
                                                (-120, 760, 700, 560, 0.05), (520, 720, 640, 600, -0.06),
                                                (100, 1300, 760, 640, 0.02))):
            ctx.save()
            ctx.translate(x + w_ / 2, y + h_ / 2)
            ctx.rotate(r + 0.01 * math.sin(t + i))
            rrect(ctx, -w_ / 2, -h_ / 2, w_, h_, 10)
            paint(ctx, (200, 154, 104), LW, shade=0.82)
            ctx.rectangle(-30, -h_ / 2, 60, h_)
            flat(ctx, (60, 90, 200), 0.8)
            ctx.restore()

    def boites(ctx, t, lt):
        deg(ctx, -600, -600, 1700, 2600, (200, 204, 196), (150, 156, 150))
        rrect(ctx, 120, 420, 840, 900, 16)
        paint(ctx, (120, 126, 136), LW, shade=0.9)
        for i in range(9):
            x, y = 160 + (i % 3) * 270, 470 + (i // 3) * 280
            rrect(ctx, x, y, 240, 250, 10)
            paint(ctx, (196, 200, 208), LW, shade=0.88)
            rrect(ctx, x + 30, y + 30, 180, 26, 6)
            flat(ctx, (50, 50, 60))
            rrect(ctx, x + 60, y + 190, 120, 34, 6)
            paint(ctx, (250, 250, 250), LW * 0.5, shade=1)
            if i == 4:
                ecrit(ctx, "YANIS", x + 120, y + 207, 22, INK, big=True)
        u = ease_out(lt / 0.5)
        ctx.save()
        ctx.translate(540, 520 + 200 * (1 - u))
        ctx.rotate(-0.08)
        rrect(ctx, -180, -90, 360, 180, 10)
        paint(ctx, (250, 248, 240), LW, shade=0.94)
        poly(ctx, [(-180, -90), (0, 20), (180, -90)], close=False)
        stroke(ctx, LW)
        rrect(ctx, -150, -60, 300, 50, 6)
        flat(ctx, (60, 120, 230))
        ecrit(ctx, "CHÈQUE ÉNERGIE", 0, -35, 30, (255, 255, 255), big=True)
        ctx.restore()
    f.plan(42.0, boites, [(0, 540, 900, 1.0), (1.4, 540, 880, 1.08)])
    f.plan(43.4, salon, [(0, 600, 860, 1.1), (4.8, 640, 860, 1.16)])
    f.plan(48.23, lambda c, t, lt: (fond_sombre_flou(c, t, (60, 44, 34)),
                                    doc_tenu(c, t, lt, "AVIS D'IMPÔT", ["Revenu fiscal de référence",
                                                                        "Seul : moins de 11 000 €",
                                                                        "Couple : moins de 16 500 €"],
                                             surl=[(0.4, 0), (1.6, 1), (3.0, 2)], couleur=(50, 110, 210))),
           [(0, 540, 960, 1.0), (4.6, 540, 960, 1.04)])
    f.plan(52.83, lambda c, t, lt: salon(c, t, lt, ordi=True, cercle=True, gain=True),
           [(0, 600, 820, 1.15), (2.2, 760, 600, 1.45), (4.5, 600, 860, 1.05)])

    # appel vidéo avec Sarah
    def appel(ctx, t, lt):
        deg(ctx, -600, -600, 1700, 2600, (24, 26, 36), (12, 12, 18))
        for j, (qui, y0, coul) in enumerate(((kev, 300, (110, 140, 190)), (sar, 960, (190, 160, 120)))):
            rrect(ctx, 90, y0, 900, 600, 28)
            ctx.save()
            ctx.clip_preserve()
            flat(ctx, coul)
            qui.objet = None
            qui.draw(ctx, 540, y0 + 1080, 1.05, t)
            ctx.restore()
            rrect(ctx, 90, y0, 900, 600, 28)
            stroke(ctx, 8, (255, 214, 60) if (j == 0 and t < 60.0) else (40, 40, 50))
            rrect(ctx, 110, y0 + 540, 150, 42, 10)
            flat(ctx, (0, 0, 0), 0.5)
            ecrit(ctx, "KÉVIN" if j == 0 else "SARAH", 185, y0 + 561, 24, (255, 255, 255), big=True)
        if t > 60.0:
            ui.panneau(ctx, 760, 1050, "LIEN REÇU", t - 60.0, rot=-0.08, size=56, fond=(255, 214, 60), bord=INK, col=INK)
        for i, c_ in enumerate(((240, 240, 240), (240, 240, 240), (232, 52, 60), (240, 240, 240))):
            if i == 2:
                rrect(ctx, 470, 1640, 140, 60, 30)
            else:
                circle(ctx, 330 + i * 140 - (40 if i > 2 else 0), 1670, 30)
            flat(ctx, c_)
    f.plan(58.5, appel, [(0, 540, 960, 1.0), (2.9, 540, 960, 1.04)])

    def mairie(ctx, t, lt, gens=False):
        deg(ctx, -800, -900, 2000, SOL, (90, 110, 150), (190, 200, 220))
        rrect(ctx, 80, 360, 920, SOL - 360, 6)
        paint(ctx, (226, 216, 196), LW, shade=0.9)
        poly(ctx, [(50, 380), (540, 190), (1030, 380)])
        paint(ctx, (206, 192, 172), LW, shade=0.9)
        enseigne(ctx, 540, 450, "MAIRIE", 1.0, fond=(40, 60, 120), col=(255, 255, 255))
        for i in range(5):
            rrect(ctx, 140 + i * 180, 560, 60, SOL - 560, 4)
            paint(ctx, (246, 240, 228), LW * 0.8, shade=0.88)
        rrect(ctx, 460, 980, 160, SOL - 980, 6)
        paint(ctx, (90, 60, 40), LW, shade=0.85)
        deg(ctx, -800, SOL, 2000, 2600, (150, 150, 156), (90, 90, 96))
        for i in range(60):
            circle(ctx, (i * 173 + 30 * math.sin(t + i)) % 1100, (i * 97 + 150 * t) % 1900, 6 + i % 6)
            flat(ctx, (255, 255, 255), 0.7)
        if gens:
            kev.draw(ctx, 260, SOL + 260, 0.9, t, regard=0.4)
            yan.draw(ctx, 820, SOL + 260, 0.86, t, regard=-0.4)
    f.plan(61.4, lambda c, t, lt: fiche(c, t, lt, 5, "Chèque énergie",
                                        [("Montant", "jusqu'à 277 €"), ("Seuil", "revenu fiscal < 11 000 € seul"),
                                         ("En couple", "revenu fiscal < 16 500 €"), ("À avoir", "n° fiscal + n° de compteur")],
                                        "31/12", fond=mairie), [(0, 540, 960, 1.0)])
    f.plan(63.6, lambda c, t, lt: mairie(c, t, lt, gens=True), [(0, 540, 960, 1.0), (0.4, 540, 940, 1.02)])

    # ═════════ 65,4 – 79 : le guichet du CCAS ═════════
    def guichet(ctx, t, lt, papiers=False):
        piece(ctx, mur=(150, 190, 180), mur2=(110, 150, 140), sol=(90, 96, 100))
        rrect(ctx, 300, 160, 520, 160, 14)
        paint(ctx, (40, 70, 140), LW, shade=0.9)
        ecrit(ctx, "CCAS", 560, 222, 90, (255, 255, 255), big=True)
        ecrit(ctx, "Centre communal d'action sociale", 560, 292, 26, (220, 230, 250))
        rrect(ctx, 120, 330, 840, 420, 10)                         # vitre du guichet
        flat(ctx, (220, 240, 240), 0.35)
        age.draw(ctx, 560, SOL - 120, 0.78, t, regard=0.0)
        rrect(ctx, 60, SOL - 330, 960, 330, 8)                     # comptoir en bois
        paint(ctx, (150, 104, 70), LW, shade=0.85)
        rrect(ctx, 40, SOL - 356, 1000, 34, 8)
        paint(ctx, (190, 140, 96), LW, shade=0.9)
        if t > 68.0:
            k = back((t - 68.0) / 0.3)
            ctx.save()
            ctx.translate(290, SOL - 430)
            ctx.scale(k, k)
            rrect(ctx, -90, -90, 180, 180, 20)
            paint(ctx, (250, 250, 250), LW, shade=0.95)
            V.icone(ctx, "flamme", 0, -10, 1.3)
            ecrit(ctx, "CHAUFFAGE", 0, 62, 22, INK, big=True)
            ctx.restore()
        if t > 69.0:
            k = back((t - 69.0) / 0.3)
            ctx.save()
            ctx.translate(820, SOL - 440)
            ctx.scale(k, k)
            rrect(ctx, -120, -80, 240, 160, 10)
            paint(ctx, (196, 150, 100), LW, shade=0.88)
            ctx.rectangle(-10, -80, 20, 160)
            flat(ctx, (232, 52, 60))
            ecrit(ctx, "COLIS DE NOËL", 0, 110, 24, INK, big=True)
            ctx.restore()
        if papiers:
            for j, (t0, tit) in enumerate(((74.3, "AVIS D'IMPÔT"), (75.6, "DOMICILE"), (76.9, "FACTURE"))):
                if t > t0:
                    feuille(ctx, 360 + j * 170, SOL - 420 + j * 10, 0.38, tit, ["", ""], k=(t - t0) / 0.35,
                            rot=-0.12 + j * 0.1)
            if t > 77.7:
                ctx.save()
                ctx.translate(540, SOL - 430)
                kk = back((t - 77.7) / 0.3)
                ctx.rotate(-0.15)
                ctx.scale(2.2 - 1.2 * kk, 2.2 - 1.2 * kk)
                rrect(ctx, -200, -60, 400, 120, 14)
                stroke(ctx, 10, (30, 150, 80))
                ecrit(ctx, "DÉPOSÉ", 0, 0, 80, (30, 150, 80), big=True)
                ctx.restore()
            kev.draw(ctx, 150, SOL + 200, 0.8, t, regard=0.5)
            yan.draw(ctx, 330, SOL + 200, 0.78, t, regard=0.5)
    f.plan(65.4, guichet, [(0, 560, 760, 1.25), (2.0, 560, 740, 1.3), (5.6, 540, 900, 1.0)])

    def ferme(ctx, t, lt):
        guichet(ctx, t, lt)
        assombrir(ctx, 0.3)
        rrect(ctx, 120, 300, 520, 560, 14)
        paint(ctx, (250, 250, 250), LW, shade=0.95)
        rrect(ctx, 120, 300, 520, 90, 14)
        flat(ctx, (220, 50, 60))
        ecrit(ctx, "DÉC", 380, 345, 50, (255, 255, 255), big=True)
        for d in range(31):
            ecrit(ctx, str(d + 1), 160 + (d % 7) * 70, 430 + (d // 7) * 80, 26, INK)
        if lt > 0.5:
            kk = back((lt - 0.5) / 0.3)
            ctx.save()
            ctx.translate(380, 600)
            ctx.rotate(-0.2)
            ctx.scale(2.2 - 1.2 * kk, 2.2 - 1.2 * kk)
            rrect(ctx, -170, -55, 340, 110, 14)
            stroke(ctx, 10, (220, 40, 50))
            ecrit(ctx, "FERMÉ", 0, 0, 80, (220, 40, 50), big=True)
            ctx.restore()
        kev.draw(ctx, 420, SOL + 300, 0.95, t, regard=0.3)
        yan.draw(ctx, 820, SOL + 300, 0.92, t, regard=-0.3)
    f.plan(71.0, ferme, [(0, 540, 960, 1.0), (2.0, 540, 940, 1.05)])
    f.plan(73.0, lambda c, t, lt: guichet(c, t, lt, papiers=True), [(0, 540, 900, 1.0), (6.0, 540, 880, 1.06)])
    f.plan(79.0, lambda c, t, lt: fiche(c, t, lt, 4, "CCAS de ta mairie",
                                        [("Aide", "chauffage ou colis de Noël"), ("Où", "CCAS de ta mairie"),
                                         ("Papiers", "avis d'impôt, domicile, facture")],
                                        "début décembre (selon la ville)"), [(0, 540, 960, 1.0)])

    # ═════════ 81 – 104 : le salon de Noël (le don) ═════════
    def noel(ctx, t, lt, recu=False, cal=True, kev_ok=False):
        piece(ctx, mur=(120, 70, 50), mur2=(80, 44, 34), sol=(90, 60, 44))
        def sapin(c):
            for i in range(26):
                halo(c, 760 + (i * 47) % 260, 300 + (i * 83) % 900, 46, (255, 210, 120), 0.5)
        couche_floue(ctx, sapin, rayon=18, bord="constant")
        for i in range(12):
            circle(ctx, 80 + i * 85, 120 + 18 * math.sin(i), 9)
            flat(ctx, (255, 220, 120), 0.6 + 0.4 * math.sin(t * 3 + i))
        if cal:
            jan = t > 102.8
            DC.calendrier(ctx, 860, 330, 0.8, "JANV" if jan else "DÉC", "1er" if jan else "31")
            if jan:
                ecrit(ctx, "année suivante", 860, 470, 26, (255, 255, 255), big=True)
        lea.draw(ctx, 300, SOL - 20, 0.8, t, bouche=bouche(t, "lea"), regard=0.4)
        rrect(ctx, 60, SOL - 300, 960, 40, 8)
        paint(ctx, (120, 80, 50), LW, shade=0.85)
        rrect(ctx, 120, SOL - 470, 150, 170, 10)                     # cadeau
        paint(ctx, (230, 230, 240), LW, shade=0.9)
        ctx.rectangle(184, SOL - 470, 22, 170)
        flat(ctx, (220, 60, 140))
        rrect(ctx, 520, SOL - 420, 240, 120, 10)                     # papier DON
        paint(ctx, (250, 250, 250), LW, shade=0.95)
        V.icone(ctx, "coeur", 570, SOL - 360, 0.7)
        ecrit(ctx, "DON", 680, SOL - 380, 34, INK, big=True)
        V.billet(ctx, 820, SOL - 330, 1.2, -0.08)
        ecrit(ctx, "100 €", 820, SOL - 330, 30, (30, 100, 50), big=True)
        if recu and t > 100.0:
            feuille(ctx, 720, SOL - 600, 0.4, "REÇU", ["", "", ""], k=(t - 100.0) / 0.35, rot=0.1, couleur=(40, 140, 90))
        if kev_ok:
            kev.draw(ctx, 540, SOL + 220, 0.9, t, regard=0.0)
    f.plan(81.0, noel, [(0, 540, 880, 1.0), (2.1, 560, 860, 1.06)])
    f.plan(83.1, noel, [(0, 300, 640, 1.75), (2.0, 300, 640, 1.8)])
    f.plan(85.1, lambda c, t, lt: noel(c, t, lt, kev_ok=True), [(0, 540, 940, 1.0), (2.5, 540, 920, 1.06)])
    f.plan(89.77, noel, [(0, 560, 900, 1.08), (2.2, 560, 880, 1.12)])

    def carnet(ctx, t, lt):
        fond_sombre_flou(ctx, t, (70, 46, 30))
        avatar(ctx, W / 2, 470)
        ctx.save()
        ctx.translate(0, 8 * math.sin(t * 1.6))
        rrect(ctx, 110, 600, 860, 760, 16)
        paint(ctx, (250, 246, 236), LW, shade=0.96)
        ctx.move_to(540, 600)
        ctx.line_to(540, 1360)
        stroke(ctx, LW * 0.6, alpha=0.3)
        rrect(ctx, 170, 650, 300, 110, 10)
        flat(ctx, (220, 50, 60))
        ecrit(ctx, "Art. 200", 320, 705, 60, (255, 255, 255), big=True)
        ecrit(ctx, "Code général des impôts", 170, 800, 30, INK, ax=0)
        ecrit(ctx, "Aide aux plus démunis :", 170, 880, 34, INK, ax=0, big=True)
        if t > 93.0:
            sw = texte("75 % du don en moins", 34, INK).get_width()
            rrect(ctx, 160, 920, (sw + 20) * ease((t - 93.0) / 0.4), 56, 8)
            flat(ctx, (255, 214, 60))
        ecrit(ctx, "75 % du don en moins", 170, 948, 34, INK, ax=0, big=True)
        ecrit(ctx, "sur l'impôt", 170, 1010, 34, INK, ax=0, big=True)
        ctx.restore()
    f.plan(91.87, carnet, [(0, 540, 960, 1.0), (4.0, 540, 960, 1.05)])

    def don_billets(ctx, t, lt):
        piece(ctx, mur=(110, 66, 46), mur2=(76, 44, 32), sol=(80, 56, 40))
        ui.panneau(ctx, 540, 420, "♥ DON 100 €", 1.0, rot=0, size=64, fond=(250, 250, 250), bord=INK, col=INK)
        for i in range(4):
            x = 240 + i * 200
            u = ease((t - 97.0 - i * 0.15) / 0.6) if i < 3 else 0.0
            y = 760 + 900 * u * u
            if u < 1:
                for k_ in range(5):
                    circle(ctx, x, y - k_ * 22, 54)
                    paint(ctx, (200, 210, 120), LW * 0.6, shade=0.9)
                rrect(ctx, x - 50, y + 60, 100, 44, 10)
                flat(ctx, (60, 170, 110))
                ecrit(ctx, "25 €", x, y + 82, 26, (255, 255, 255), big=True)
        if t > 97.4:
            ui.panneau(ctx, 380, 1040, "75 € rendus", t - 97.4, rot=-0.04, size=60, fond=(110, 220, 140), bord=INK,
                       col=INK)
    f.plan(95.7, don_billets, [(0, 540, 900, 1.0), (2.5, 540, 900, 1.05)])
    f.plan(98.23, lambda c, t, lt: noel(c, t, lt, recu=True), [(0, 520, 880, 1.06), (5.8, 520, 860, 1.12)])
    f.plan(104.0, lambda c, t, lt: fiche(c, t, lt, 3, "Don à 75 %",
                                         [("Coût réel", "100 € donnés = 25 € payés"), ("Pour", "asso d'aide aux plus démunis"),
                                          ("À garder", "le reçu de l'association")], "31/12",
                                         fond=lambda c2, t2, l2: noel(c2, t2, l2)), [(0, 540, 960, 1.0)])

    # ═════════ 106 – 131 : le bureau (RTT) ═════════
    def bureau(ctx, t, lt, rtt=3, perdu=False, ecran_txt=None, gain=False, patron=False):
        piece(ctx, mur=(200, 206, 214), mur2=(160, 168, 180), sol=(110, 116, 130))
        rrect(ctx, 220, 260, 640, 470, 12)                           # calendrier mural
        paint(ctx, (252, 252, 252), LW, shade=0.96)
        ecrit(ctx, "DÉCEMBRE", 540, 310, 50, INK, big=True)
        for j in range(3):
            x, y = 330 + j * 90, 400
            if perdu and t > 114.0:
                u = t - 114.0 - j * 0.15
                y += 700 * max(0.0, u) ** 2
            circle(ctx, x, y, 34)
            paint(ctx, (60, 170, 110), LW * 0.7, shade=0.9)
            ecrit(ctx, "RTT", x, y, 18, (255, 255, 255), big=True)
        if perdu and t > 114.4:
            ctx.save()
            ctx.translate(700, 420)
            ctx.rotate(-0.15)
            rrect(ctx, -140, -44, 280, 88, 10)
            stroke(ctx, 8, (220, 40, 50))
            ecrit(ctx, "PERDU", 0, 0, 60, (220, 40, 50), big=True)
            ctx.restore()
        if patron:
            pat.draw(ctx, 900, SOL + 10, 0.8, t, bouche=bouche(t, "pat"), regard=-0.6)
        rrect(ctx, 380, 780, 420, 300, 14)                            # écran
        paint(ctx, (40, 44, 56), LW, shade=1)
        rrect(ctx, 400, 800, 380, 260, 8)
        flat(ctx, (250, 250, 252))
        if ecran_txt is None:
            ecrit(ctx, "SOLDE RTT", 590, 850, 30, (120, 120, 130), big=True)
            ecrit(ctx, str(rtt), 590, 960, 120, (40, 160, 90), big=True)
        else:
            ecran_txt(ctx, t)
        rrect(ctx, 0, SOL - 230, 1080, 40, 8)                          # bureau
        paint(ctx, (230, 232, 236), LW, shade=0.9)
        kev.objet = None
        kev.draw(ctx, 190, SOL + 150, 0.82, t, regard=0.4)
        circle(ctx, 880, SOL - 260, 34)                                 # tasse
        paint(ctx, (250, 250, 250), LW, shade=0.9)
        if gain and t > 121.4:
            DC.etiquette(ctx, 380, 980, 0.8, "+400 €", t - 121.4, couleur=(110, 220, 140))
    f.plan(105.0, lambda c, t, lt: fiche(c, t, lt, 3, "Don à 75 %",
                                         [("Coût réel", "100 € donnés = 25 € payés"), ("Pour", "asso d'aide aux plus démunis"),
                                          ("À garder", "le reçu de l'association")], "31/12", fond=bureau), [(0, 540, 960, 1.0)])
    f.plan(106.3, bureau, [(0, 540, 900, 1.0), (3.7, 520, 880, 1.06)])
    f.plan(112.0, lambda c, t, lt: bureau(c, t, lt, perdu=True), [(0, 520, 760, 1.15), (3.2, 520, 740, 1.2)])
    f.plan(115.23, lambda c, t, lt: (fond_sombre_flou(c, t, (70, 50, 40)),
                                     doc_tenu(c, t, lt, "BULLETIN DE PAIE", ["Rachat de 3 RTT", "Majoration : +25 %",
                                                                             "Impôt : 0 €"],
                                              surl=[(1.6, 0), (3.6, 1), (4.6, 2)], couleur=(130, 80, 210))),
           [(0, 540, 960, 1.0), (6.0, 540, 960, 1.04)])
    f.plan(121.2, lambda c, t, lt: bureau(c, t, lt, gain=True), [(0, 520, 880, 1.06), (1.8, 520, 880, 1.1)])

    def ecran_message(ctx, t):
        rrect(ctx, 400, 800, 380, 50, 8)
        flat(ctx, (40, 110, 220))
        ecrit(ctx, "Nouveau message", 420, 825, 22, (255, 255, 255), ax=0, big=True)
        msg = "Objet : rachat de 3 RTT. Je demande le rachat de mes 3 jours de RTT."
        n = int(len(msg) * min(1.0, max(0.0, (t - 123.2) / 2.4)))
        lignes, cur = [], ""
        for mot in msg[:n].split(" "):
            if len(cur) + len(mot) > 22:
                lignes.append(cur)
                cur = mot
            else:
                cur = (cur + " " + mot).strip()
        lignes.append(cur)
        for i, l in enumerate(lignes[:5]):
            ecrit(ctx, l, 420, 880 + i * 34, 20, INK, ax=0)

    def ecran_envoye(ctx, t):
        circle(ctx, 590, 900, 60)
        flat(ctx, (40, 170, 90))
        ctx.move_to(560, 900)
        ctx.line_to(582, 925)
        ctx.line_to(625, 875)
        stroke(ctx, 14, (255, 255, 255))
        ecrit(ctx, "ENVOYÉ", 590, 1010, 34, (40, 170, 90), big=True)
    f.plan(123.0, lambda c, t, lt: bureau(c, t, lt, ecran_txt=ecran_message), [(0, 520, 900, 1.15), (3.0, 540, 900, 1.2)])
    f.plan(125.83, lambda c, t, lt: fiche(c, t, lt, 2, "Rachat de RTT",
                                          [("Gain", "+25 % par jour"), ("Impôt", "0 €"),
                                           ("Comment", "demande écrite au patron")], "31/12"), [(0, 540, 960, 1.0)])
    f.plan(127.0, lambda c, t, lt: bureau(c, t, lt, ecran_txt=ecran_envoye, patron=True),
           [(0, 620, 880, 1.0), (1.3, 700, 760, 1.3)])
    f.plan(128.4, lambda c, t, lt: bureau(c, t, lt, ecran_txt=ecran_envoye, patron=True),
           [(0, 880, 640, 1.8), (1.2, 880, 640, 1.86)])
    f.plan(129.6, lambda c, t, lt: bureau(c, t, lt, ecran_txt=ecran_envoye, patron=True),
           [(0, 880, 660, 1.6), (1.4, 880, 660, 1.66)])
    f.plan(131.07, lambda c, t, lt: bureau(c, t, lt, ecran_txt=ecran_envoye), [(0, 330, 760, 1.6), (0.9, 330, 760, 1.66)])

    # ═════════ 134 – 141 : le décret ═════════
    def decret(ctx, t, lt):
        fond_sombre_flou(ctx, t, (20, 30, 60))
        DC.calendrier(ctx, 300, 560, 0.85, "OCT", "20")
        DC.calendrier(ctx, 780, 560, 0.85, "DÉC", "31")
        avatar(ctx, 540, 560, 0.8)
        rrect(ctx, 220, 760, 640, 26, 13)
        flat(ctx, (60, 64, 90))
        rrect(ctx, 220, 760, 640 * ease((t - 134.6) / 2.6), 26, 13)
        flat(ctx, (255, 214, 60))
        if t > 137.6:
            ecrit(ctx, "par salarié, jusqu'à", 540, 860, 40, (255, 214, 60), big=True, alpha=ease((t - 137.6) / 0.3))
            ui.panneau(ctx, 540, 980, "1 000 €", t - 137.6, rot=0, size=110, fond=(255, 214, 60), bord=INK, col=INK)
    f.plan(134.0, decret, [(0, 540, 960, 1.0), (7.1, 540, 960, 1.06)])
    f.plan(141.1, lambda c, t, lt: plan_photo(c, "abribus_nuit.jpg", lt, 1.04, 1.1, 1.0))

    # ═════════ 142 – 152 : le bureau du patron, la balance ═════════
    def bureau_patron(ctx, t, lt):
        piece(ctx, mur=(70, 60, 90), mur2=(40, 34, 56), sol=(70, 50, 44))
        fenetre(ctx, t, 300, 260, 720, 520, seed=53, ciel=((14, 18, 40), (50, 50, 90)), montants=3)
        pat.draw(ctx, 820, SOL - 60, 0.8, t, regard=-0.5)
        rrect(ctx, 260, SOL - 330, 800, 330, 10)
        paint(ctx, (110, 70, 46), LW, shade=0.85)
        rrect(ctx, 240, SOL - 356, 840, 34, 8)
        paint(ctx, (140, 94, 64), LW, shade=0.9)
        rrect(ctx, 760, SOL - 420, 220, 70, 6)
        paint(ctx, (250, 248, 240), LW, shade=0.95)
        ecrit(ctx, "PRIME TRANSPORT", 870, SOL - 385, 20, INK, big=True)
        kev.draw(ctx, 160, SOL + 140, 0.86, t, regard=0.5)
        if t > 142.0 and t < 143.4:
            traits_choc(ctx, 820, SOL - 60 - 0.8 * 880, 120, t - 142.0, color=(255, 255, 255))
        if t > 145.0:                                                   # la balance
            k = back((t - 145.0) / 0.35)
            pen = 0.0 if t < 146.8 else -0.18 * ease((t - 146.8) / 0.6)
            if t > 149.0:
                pen = -0.18 + 0.18 * ease((t - 149.0) / 0.6)
            ctx.save()
            ctx.translate(560, SOL - 600)
            ctx.scale(k, k)
            ctx.rectangle(-8, 0, 16, 240)
            paint(ctx, (200, 160, 60), LW * 0.6, shade=0.9)
            ctx.rotate(pen)
            ctx.rectangle(-260, -8, 520, 16)
            paint(ctx, (220, 180, 70), LW * 0.6, shade=0.9)
            for sx, lab, sous in ((-1, "1 000 €", "AUGMENTATION"), (1, "1 000 €", "PRIME")):
                ctx.save()
                ctx.translate(sx * 240, 0)
                ctx.rotate(-pen)
                ctx.move_to(0, 0)
                ctx.line_to(0, 80)
                stroke(ctx, 3)
                rrect(ctx, -100, 80, 200, 70, 10)
                paint(ctx, (250, 250, 250), LW * 0.6, shade=1)
                ecrit(ctx, lab, 0, 115, 36, INK, big=True)
                ecrit(ctx, sous, 0, 175, 20, (250, 250, 250), big=True)
                if sx < 0 and t > 146.8:
                    for j in range(2):
                        rrect(ctx, -90, 10 - j * 50, 180, 44, 8)
                        flat(ctx, (232, 52, 60))
                        ecrit(ctx, "CHARGES", 0, 32 - j * 50, 22, (255, 255, 255), big=True)
                if sx > 0 and t > 149.6:
                    rrect(ctx, -60, 10, 120, 50, 8)
                    flat(ctx, (60, 170, 110))
                    ecrit(ctx, "PILE", 0, 35, 26, (255, 255, 255), big=True)
                ctx.restore()
            ctx.restore()
        if t > 151.0:
            feuille(ctx, 820, SOL - 520, 0.45, "PRIME TRANSPORT", ["toute l'équipe"], k=(t - 151.0) / 0.3, rot=0.06,
                    tampon="SIGNÉ", tampon_k=max(0.0, (t - 151.4) / 0.4))
    f.plan(141.57, bureau_patron, [(0, 600, 860, 1.0), (1.7, 640, 820, 1.08)])
    f.plan(143.3, bureau_patron, [(0, 800, 640, 1.6), (0.9, 800, 640, 1.65)])
    f.plan(144.2, bureau_patron, [(0, 560, 860, 1.0), (7.6, 560, 840, 1.08)])

    # ═════════ 152 – 157,7 : la fête, puis le récapitulatif ═════════
    def fete(ctx, t, lt):
        piece(ctx, mur=(38, 44, 84), mur2=(20, 24, 50), sol=(34, 34, 56), x0=-800, x1=2400)
        fenetre(ctx, t, -300, -200, 1800, 1100, seed=7, montants=4)
        V.domino(ctx, 560, SOL, 2.2, 1.45, "soleil", "bus", "1 000 €", lueur=1.0, couleur=(250, 236, 170))
        for i, m in enumerate(mecs[:3]):
            m.draw(ctx, -60 + i * 130, SOL + 60, 0.7, t)
        for p_, x_ in ((lea, 350), (yan, 470), (kev, 230)):
            p_.objet = None
            p_.draw(ctx, x_, SOL + 120, 0.78, t)
        pat.objet = None
        pat.draw(ctx, 900, SOL + 40, 0.8, t)
        for i in range(10):
            v = ((t - 152.0) * 0.8 + i * 0.13) % 1.2
            V.billet(ctx, (i * 113) % 1100, -200 + 2000 * v, 0.8, t * (2 + i % 4) * (1 if i % 2 else -1))
    f.plan(152.0, fete, [(0, 540, 900, 1.0), (3.7, 560, 880, 1.06)])

    def recap(ctx, t, lt):
        fond_sombre_flou(ctx, t)
        k = back(lt / 0.35)
        ctx.save()
        ctx.translate(W / 2, 860)
        ctx.scale(k, k)
        rrect(ctx, -430, -560, 860, 1120, 26)
        paint(ctx, (252, 250, 246), LW, shade=0.97)
        ecrit(ctx, "À GARDER · AVANT LE 31/12", -380, -500, 22, (220, 50, 60), ax=0, big=True)
        ecrit(ctx, "Les 6 aides de Kévin", -380, -450, 46, INK, ax=0, big=True)
        lignes = [(6, "Aide carburant", "100 €"), (5, "Chèque énergie", "jusqu'à 277 €"),
                  (4, "CCAS de ta mairie", "colis, chauffage"), (3, "Don à 75 %", "75 % rendus"),
                  (2, "Rachat de RTT", "+25 %, sans impôt"), (1, "Prime transport", "jusqu'à 1 000 €")]
        for i, (n, nom, val) in enumerate(lignes):
            yy = -340 + i * 120
            circle(ctx, -360, yy, 26)
            flat(ctx, COUL[n])
            ecrit(ctx, nom, -310, yy, 34, INK, ax=0, big=True)
            ecrit(ctx, val, 390, yy, 30, COUL[n] if n != 1 else (200, 150, 0), ax=1, big=True)
        rrect(ctx, -390, 400, 780, 110, 20)
        flat(ctx, (40, 160, 90))
        ecrit(ctx, "Total récupéré", -350, 455, 34, (255, 255, 255), ax=0, big=True)
        ecrit(ctx, "1 623 €", 350, 455, 52, (255, 255, 255), ax=1, big=True)
        ctx.restore()
    f.plan(155.7, recap, [(0, 540, 960, 1.0)])

    # ═════════ écran : compteur, sous-titres ═════════
    cles = [(0, 0), (29.0, 100), (58.0, 148), (98.0, 223), (122.2, 623), (153.5, 1623)]
    f.ecran(lambda ctx, t: ui.compteur(ctx, t, "RÉCUPÉRÉ AVANT LE 31/12", cles, apparition=3.0, toujours_vert=True))
    groupes = ui.decouper(words)
    f.ecran(lambda ctx, t: ui.sous_titres(ctx, t, groupes, y=Y_SOUS, size=58) if t < 155.7 else None)

    for i in range(5):
        f.son(i * 0.45 + 0.45, "pop", 0.35)
    for t_, s_, g_ in [(2.4, "impact", 0.8), (3.2, "succes", 0.5), (9.2, "impact", 0.8), (11.47, "pop", 0.5),
                       (29.0, "succes", 0.6), (30.13, "pop", 0.4), (38.37, "pop", 0.5), (58.0, "succes", 0.6),
                       (64.0, "pop", 0.5), (72.0, "rate", 0.5), (77.7, "succes", 0.6), (87.6, "pop", 0.5),
                       (98.0, "succes", 0.6), (110.0, "pop", 0.5), (114.4, "rate", 0.5), (122.2, "succes", 0.6),
                       (132.0, "pop", 0.5), (143.3, "rate", 0.5), (151.4, "succes", 0.8), (153.5, "succes", 0.8)]:
        f.son(t_, s_, g_)
    f.secousse(2.4, 8)
    f.secousse(9.2, 14)
    return f


def _morceau(args):
    i0, i1, chemin = args
    f = construire(WORK)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", chemin]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for k in range(i0, i1):
        p.stdin.write(bytes(f.frame(k / FPS).get_data()))
    p.stdin.close()
    p.wait()
    return chemin


def rendre(jobs):
    f = construire(WORK)
    n = int(f.dur * FPS)
    pas = math.ceil(n / jobs)
    parts = [(j * pas, min(n, (j + 1) * pas), str(WORK / f"part_{j:02d}.mp4")) for j in range(jobs)]
    with ProcessPoolExecutor(jobs) as ex:
        faits = list(ex.map(_morceau, parts))
    liste = WORK / "parts.txt"
    liste.write_text("".join(f"file '{p}'\n" for p in faits))
    wav = WORK / "mix.wav"
    f.audio(wav)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(liste), "-i", str(wav),
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-shortest",
                    "-movflags", "+faststart", str(OUT)], check=True)
    return OUT


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills")
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    if a.stills:
        f = construire(WORK)
        print(f"durée {f.dur:.1f} s, {len(f.plans)} plans")
        f.stills([float(x) for x in a.stills.split(",")], WORK / "stills")
    else:
        print("→", rendre(a.jobs))


if __name__ == "__main__":
    main()
