"""« 6 aides avant le 31 décembre » v2 : même accroche, même déroulé (compte à rebours 6 → 1), même rythme que la
vidéo de La Ficelle (154 s), texte réécrit avec nos mots et nos personnages. Décors dessinés pour cette vidéo.

    python3 motion/trait/six_aides_v2.py --stills 0.5,8,15
    python3 motion/trait/six_aides_v2.py --jobs 4          → output/trait/six_aides_v2.mp4
"""
import argparse
import math
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import decors as DC  # noqa: E402
import decors_ville as V  # noqa: E402
import ui  # noqa: E402
import voix  # noqa: E402
from dessin import FPS, H, INK, LW, ROOT, W, back, circle, couche_floue, ease, ease_out, ecrit, flat, halo, mix, paint, \
    poly, rrect, stroke  # noqa: E402
from film import Film  # noqa: E402
from perso import Perso, traits_choc  # noqa: E402
from six_aides_31dec import (KEVIN, MECANOS, MERE, PATRON, SOL, Y_SOUS, assombrir, comptoir, deg, enseigne,  # noqa: E402
                             fenetre, feuille, horloge, lumiere_sol, piece, reflet_doux, ticket)
from six_aides_v2_texte import LIGNES, VITESSES, VOIX  # noqa: E402

OUT = ROOT / "output/trait/six_aides_v2.mp4"
WORK = ROOT / "output/trait/_work_six_v2"
INES = dict(cheveux="chignon", couleur_cheveux=(40, 28, 24), peau=(200, 140, 100), haut="sweat",
            couleur_haut=(190, 70, 70), bas=(60, 60, 90), chaussures=(240, 240, 240), seed=13, tete=0.84, mince=0.86)
PETITS = [("points", "essence"), ("soleil", "flamme"), ("points", "maison"), ("soleil", "coeur"),
          ("points", "calendrier")]
NOMS = ["AIDE CARBURANT", "CHÈQUE ÉNERGIE", "CENTRE D'ACTION SOCIALE", "DON À 75 %", "RACHAT DES RTT",
        "PRIME TRANSPORT"]
XD = [180 + i * 250 for i in range(5)]
XG, SG = 1500, 3.0
XPAT = 2480
XKEV = -170
GX = XG + 75 * SG


def ecran_texte(lignes, haut=(40, 120, 220), titre="MA BANQUE"):
    def e(c, w, h):
        c.rectangle(0, 0, w, h)
        c.set_source_rgb(0.97, 0.97, 0.99)
        c.fill()
        c.rectangle(0, 0, w, 36)
        c.set_source_rgb(*[v / 255 for v in haut])
        c.fill()
        ecrit(c, titre, w / 2, 18, 10, (255, 255, 255), big=True)
        for i, (txt, taille, col) in enumerate(lignes):
            ecrit(c, txt, w / 2, 70 + i * 36, taille, col, big=taille >= 16)
    return e


def construire(work):
    voice, words = voix.build(LIGNES, VOIX, work, vitesses=VITESSES)
    f = Film(voice, words)

    kev, pat, ines, mere = Perso(**KEVIN), Perso(**PATRON), Perso(**INES), Perso(**MERE)
    mecs = [Perso(**m) for m in MECANOS]

    # ── jeu des personnages ──
    kev.pose(0, "pointe").emotion(0, "content").emotion(2.2, "choc").pose(3.0, "repos")
    kev.emotion(7.9, "content").emotion(10.7, "choc").emotion(14.7, "content")
    kev.pose(52.0, "telephone").emotion(52.0, "content")
    kev.pose(98.1, "telephone").emotion(98.1, "neutre").emotion(101.4, "malin")
    kev.pose(121.8, "repos").emotion(123.9, "triste").emotion(128.1, "malin").pose(128.1, "pointe_g")
    kev.pose(140.5, "pointe").emotion(140.5, "malin").pose(149.7, "leve").emotion(149.7, "content")
    pat.pose(0, "mains_hanches").emotion(0, "neutre").pose(5.7, "pointe_g").emotion(5.7, "malin")
    pat.pose(121.8, "mains_hanches").emotion(121.8, "malin").pose(126.4, "haussement")
    pat.pose(139.5, "haussement").emotion(139.5, "content").pose(140.5, "mains_hanches").emotion(140.5, "neutre")
    pat.emotion(142.9, "choc").emotion(145.3, "triste").pose(149.4, "objet").emotion(149.7, "neutre")
    pat.objet = lambda c, x, y, s: (rrect(c, x - 110, y - 160, 220, 260, 8),
                                    paint(c, (252, 248, 236), LW, shade=0.95),
                                    ecrit(c, "PRIME", x, y - 120, 34, (220, 50, 60), big=True),
                                    ecrit(c, "1 000 €", x, y - 60, 44, INK, big=True))
    ines.pose(0, "repos").emotion(0, "triste").emotion(42.2, "neutre").pose(46.8, "telephone")
    ines.emotion(51.0, "content").pose(55.0, "repos").emotion(55.0, "neutre").emotion(60.4, "content")
    ines.objet = lambda c, x, y, s: DC.telephone(c, x, y - 40, 0.9)
    mere.pose(0, "objet").emotion(0, "neutre").emotion(79.0, "triste").emotion(86.0, "content")
    mere.objet = lambda c, x, y, s: V.billet(c, x, y - 40, 1.3, -0.1)
    for i, m in enumerate(mecs):
        m.pose(0, "repos").emotion(0, "neutre").emotion(142.9, "choc")
        m.pose(149.7 + 0.05 * i, "leve").emotion(149.7 + 0.05 * i, "content")

    def bp(t):
        return f.bouche(t, "pat")

    # ═════════ décor : la rangée de dominos devant la baie vitrée (accroche, numéros, total) ═════════
    def ang_petit(i, t, t0=0.1, pas=0.4):
        ti = t0 + i * pas
        if t < ti:
            return 0.0
        u = min(1.0, (t - ti) / pas)
        a = 0.62 * u * u
        if i < 4 and t > ti + pas:
            a = 0.62 + 0.7 * ease((t - ti - pas) / 0.4)
        return a

    def ang_geant(t):
        if 5.7 <= t < 7.9:
            return 0.19 * ease_out((t - 5.7) / 0.35)
        if t >= 151.3:
            return 1.45 * ease((t - 151.3) / 0.7)
        return 0.03 * math.exp(-max(0.0, t - 2.1) * 3) * math.sin(max(0.0, t - 2.1) * 18) if t > 2.1 else 0.0

    def dominos(ctx, t, lt, tombes=True, actif=None, gris=False, cal=True, chute=(0.1, 0.4)):
        piece(ctx, mur=(38, 44, 84), mur2=(20, 24, 50), sol=(34, 34, 56), x0=-2000, x1=4200)
        fenetre(ctx, t, -900, -200, 4500, 1300, seed=7, montants=10)

        def objets(c):
            if t < 8:
                kev.draw(c, XKEV, SOL, 0.78, t, regard=0.6)
            for i, (h, b) in enumerate(PETITS):
                a = ang_petit(i, t, *chute) if tombes else 0.0
                coul = (190, 190, 198) if gris else ((255, 240, 170) if actif == i else (250, 246, 232))
                V.domino(c, XD[i], SOL, 1.0, a, h, b, lueur=1.0 if actif == i else 0.0, couleur=coul)
            V.domino(c, XG, SOL, SG, ang_geant(t), "soleil", "bus", "1 000 €", lueur=0.0 if gris else 1.0,
                     couleur=(250, 236, 170))
            if t < 8 or t > 151:
                pat.draw(c, XPAT, SOL, 0.78, t)
        lumiere_sol(ctx, XG, 900, 0.22)
        reflet_doux(ctx, objets)
        objets(ctx)
        if cal and 2.0 <= t < 8:
            u = t - 2.0
            y = -900 + (SOL - 280 * SG - 200 + 900) * min(1.15, 1 - math.exp(-u * 6) * math.cos(u * 12))
            ctx.move_to(XG - 160, -1600)
            ctx.line_to(XG - 160, y - 150)
            stroke(ctx, 4)
            DC.calendrier(ctx, XG - 160, y, 0.9, "DÉC", "31")
        if 5.7 <= t < 7.9:
            traits_choc(ctx, XPAT, SOL - 0.78 * 880, 130, t - 5.7, color=(255, 255, 255))

    def cam_accroche(lt):
        k = ease(lt / 2.6)
        x = XKEV + 380 + (GX + 120 - XKEV - 380) * k
        z = 1.05 - 0.13 * k
        return x, SOL - 360 / z, z

    f.plan(0, dominos, cam_accroche, fouet=False)
    f.plan(3.2, dominos, [(0, GX + 60, SOL - 380 / 0.95, 0.95), (2.3, GX + 90, SOL - 380 / 1.0, 1.0)])
    f.plan(5.5, dominos, [(0, 2120, SOL - 400 / 1.02, 1.02), (2.4, 2160, SOL - 400 / 1.08, 1.08)])

    def numero(i):
        """Le domino de l'aide n° (6 - i) s'allume, gros titre en haut."""
        def scene(ctx, t, lt):
            dominos(ctx, t, lt, tombes=False, actif=i if i < 5 else None)
        if i < 5:
            cx, z = XD[i] + 75, 1.2
        else:
            cx, z = GX, 0.92
        hud = (lambda ctx, t, lt: ui.panneau(ctx, W / 2, 330, f"N° {6 - i} · {NOMS[i]}", lt - 0.05, rot=-0.03,
                                              size=64 if i != 2 else 52, fond=(255, 214, 60), bord=INK, col=INK))
        return scene, [(0, cx, SOL - 330 / z, z), (1.4, cx, SOL - 330 / z, z * 1.07)], hud

    # ═════════ décor : la station, le soir ═════════
    SOLX = 1560

    def montant(t):
        a, b = 8.9, 10.7
        return 90.0 * ease((t - a) / (b - a)) if t >= a else 0.0

    def dehors(ctx, t, lt, pompe=True, route=0.0):
        deg(ctx, -800, -900, 2000, SOLX - 300, (40, 52, 100), (226, 160, 140))
        couche_floue(ctx, lambda c: (V.immeubles(c, -700, 1900, SOLX - 220, t, seed=5, col=(84, 90, 140), hmin=260,
                                                 hmax=620),
                                     V.immeubles(c, -600, 1900, SOLX - 160, t, seed=9, col=(64, 70, 116), hmin=140,
                                                 hmax=380)), rayon=12, bord="constant")
        deg(ctx, -800, SOLX - 180, 2000, 2600, (74, 74, 90), (44, 44, 56))
        for i in range(-2, 8):
            x = i * 260 - (route * 900) % 260
            rrect(ctx, x, SOLX + 120, 140, 18, 8)
            flat(ctx, (240, 240, 240), 0.7)
        V.panneau_route(ctx, 860, 640, "GARAGE →", "20 km")
        if pompe:
            V.pompe(ctx, 290, SOLX, f"{montant(t):05.2f} €".replace(".", ","), t)
            V.voiture(ctx, 900, SOLX, 0.95, (40, 150, 170))
            kev.objet = None
            kev.draw(ctx, 640, SOLX, 0.84, t, regard=-0.8)
            if 10.7 <= t < 13:
                d = t - 10.7
                traits_choc(ctx, 640, SOLX - 0.84 * 900, 130, d, color=(255, 255, 255))
                for i in range(8):
                    a = -1.3 + i * 0.32
                    r = 120 + 800 * d * (0.7 + 0.1 * (i % 3))
                    V.billet(ctx, 290 + math.cos(a) * r * 0.8, 840 + math.sin(a) * r * 0.6 + 380 * d * d, 1.0,
                             d * (3 + i) * (1 if i % 2 else -1))

    f.plan(7.9, dehors, [(0, 540, 1000, 1.0), (2.6, 540, 1030, 1.07)])
    f.plan(10.7, dehors, [(0, 470, 960, 1.14), (0.9, 470, 960, 1.2)])
    f.plan(11.6, dehors, [(0, 820, 760, 1.25), (1.2, 820, 740, 1.34)])

    # ═════════ n° 6 : aide carburant ═════════
    sc, cam, hud = numero(0)
    f.plan(12.9, sc, cam, hud=hud)

    def route(ctx, t, lt):
        dehors(ctx, t, lt, pompe=False, route=lt)
        b = math.sin(lt * 14) * 4
        V.voiture(ctx, 520, SOLX + 40 + b, 1.15, (40, 150, 170))
        circle(ctx, 450, SOLX - 190 + b, 34)
        paint(ctx, (198, 138, 98), LW, shade=0.9)
    f.plan(14.7, route, [(0, 540, 1000, 1.0), (1.4, 580, 1000, 1.06)])

    def fond_feuille(fond, titre, lignes, surl=None, prix=None, tampon=None, t_tampon=1e9, couleur=(232, 52, 60),
                     dim=0.45):
        def s(ctx, t, lt):
            fond(ctx, t, lt)
            assombrir(ctx, dim)
            feuille(ctx, 540, 840, 1.12, titre, lignes, k=lt / 0.5, rot=-0.03, surl=surl, prix=prix, tampon=tampon,
                    tampon_k=max(0.0, (t - t_tampon) / 0.4), couleur=couleur)
        return s

    f.plan(16.1, fond_feuille(lambda c, t, lt: dehors(c, t, lt, pompe=True), "AIDE CARBURANT",
                              ["tu roules pour bosser", "revenu fiscal par part", "moins de 22 770 €"],
                              surl="moins de 22 770 €"), [(0, 540, 960, 1.0), (3.4, 540, 960, 1.04)])

    def tel(fond, ecran, etiq=None, t_etiq=0.9):
        def s(ctx, t, lt):
            fond(ctx, t, lt)
            assombrir(ctx, 0.3)
            DC.telephone(ctx, 540, 900, 3.4 * ease_out(lt / 0.3) + 0.01, ecran=ecran, t=t,
                         rot=-0.05 + 0.02 * math.sin(t * 2))
            if etiq and lt > t_etiq:
                DC.etiquette(ctx, 820, 500, 0.8, etiq, lt - t_etiq, couleur=(110, 220, 140))
        return s

    f.plan(19.6, tel(lambda c, t, lt: dehors(c, t, lt, pompe=True),
                     ecran_texte([("L'État verse", 11, INK), ("100,00 €", 22, (40, 160, 90)), ("aide carburant", 10, INK)],
                                 titre="IMPÔTS")), [(0, 540, 960, 1.0), (1.6, 540, 960, 1.04)])
    f.plan(21.2, fond_feuille(lambda c, t, lt: dehors(c, t, lt, pompe=True), "FORMULAIRE",
                              ["plaque d'immatriculation", "carte grise", "numéro fiscal"], surl="carte grise",
                              tampon="ENVOYÉ", t_tampon=23.7), [(0, 540, 960, 1.0), (3.0, 540, 960, 1.04)])
    f.plan(24.3, tel(lambda c, t, lt: dehors(c, t, lt, pompe=False),
                     ecran_texte([("Virement reçu", 11, INK), ("+100,00 €", 22, (40, 160, 90)), ("10 jours après", 10, INK)]),
                     etiq="+100 €", t_etiq=0.7), [(0, 540, 960, 1.0), (2.2, 540, 960, 1.04)])

    def calendrier_scene(haut, gros, titre, sous=None, couleur=(220, 50, 60)):
        def s(ctx, t, lt):
            deg(ctx, -400, -400, 1500, 2400, (30, 34, 60), (14, 16, 30))
            halo(ctx, 540, 860, 700, (255, 210, 120), 0.18)
            k = back(lt / 0.35)
            DC.calendrier(ctx, 540, 900, 2.2 * k + 0.01, haut, gros, couleur=couleur)
            ui.panneau(ctx, 540, 1300, titre, lt - 0.3, rot=-0.03, size=70, fond=(255, 214, 60), bord=INK, col=INK)
            if sous:
                ecrit(ctx, sous, 540, 470, 56, (255, 255, 255), big=True, alpha=ease((lt - 0.5) / 0.3))
        return s
    f.plan(26.6, calendrier_scene("DÉC", "31", "LE FORMULAIRE FERME", sous="J-41"),
           [(0, 540, 960, 1.0), (2.4, 540, 960, 1.05)])

    # ═════════ chez Inès : le froid ═════════
    def salon_froid(ctx, t, lt, chaud=0.0):
        piece(ctx, mur=(120, 140, 170), mur2=(80, 96, 130), sol=(110, 96, 90))
        fenetre(ctx, t, 620, 360, 360, 460, seed=17, ciel=((20, 26, 60), (60, 70, 120)))
        rrect(ctx, 640, 1000, 300, 190, 10)
        paint(ctx, mix((226, 230, 236), (255, 170, 110), chaud), LW, shade=0.85)
        for i in range(5):
            ctx.move_to(670 + i * 60, 1015)
            ctx.line_to(670 + i * 60, 1175)
            stroke(ctx, LW * 0.6, alpha=0.5)
        DC.canape(ctx, 330, SOL, 560, (120, 90, 140))
        ines.objet = None
        ines.draw(ctx, 330, SOL + 130, 0.8, t, regard=0.4)
        DC.canape_avant(ctx, 330, SOL, 560, (120, 90, 140))
        rrect(ctx, 70, 520, 70, 300, 35)
        paint(ctx, (250, 250, 250), LW, shade=0.9)
        rrect(ctx, 90, 680, 30, 120, 15)
        flat(ctx, (220, 60, 60))
        ecrit(ctx, "16°", 105, 470, 48, INK, big=True)
        for i in range(3):
            v = (t * 0.8 + i * 0.33) % 1
            circle(ctx, 360 + 30 * math.sin(v * 6 + i), 560 - 140 * v, 16 + 26 * v)
            flat(ctx, (255, 255, 255), 0.4 * (1 - v))
        if 33.8 <= t < 35.7:
            k = back((t - 33.8) / 0.3)
            for s_ in (1, -1):
                ctx.move_to(790 - 120 * k, 1095 - 80 * k * s_)
                ctx.line_to(790 + 120 * k, 1095 + 80 * k * s_)
                stroke(ctx, 18, (232, 52, 60))
    f.plan(29.0, salon_froid, [(0, 520, 900, 1.0), (1.4, 520, 900, 1.05)])
    f.plan(30.6, salon_froid, [(0, 120, 640, 1.9), (1.0, 120, 640, 1.95)])
    f.plan(31.6, salon_froid, [(0, 340, 700, 1.6), (1.7, 340, 700, 1.66)])
    f.plan(33.3, salon_froid, [(0, 660, 900, 1.3), (2.4, 640, 900, 1.36)])

    # ═════════ n° 5 : chèque énergie ═════════
    sc, cam, hud = numero(1)
    f.plan(35.7, sc, cam, hud=hud)

    def boites_lettres(ctx, t, lt):
        piece(ctx, mur=(120, 110, 100), mur2=(80, 72, 68), sol=(70, 64, 60))
        for bx, nom, plein in ((140, "ANCIENNE ADRESSE", True), (600, "NOUVELLE ADRESSE", False)):
            rrect(ctx, bx, 560, 360, 420, 14)
            paint(ctx, (200, 206, 214), LW, shade=0.85)
            rrect(ctx, bx + 40, 620, 280, 40, 8)
            flat(ctx, (40, 40, 50))
            ecrit(ctx, nom, bx + 180, 1030, 34, (250, 250, 250), big=True)
            if plein:
                u = ease_out(lt / 0.8)
                ex, ey = bx + 180 + 500 * (1 - u), 720 - 300 * (1 - u)
                rrect(ctx, ex - 120, ey - 60, 240, 130, 10)
                paint(ctx, (250, 246, 232), LW, shade=0.92)
                ecrit(ctx, "CHÈQUE", ex, ey - 20, 30, (220, 140, 30), big=True)
                ecrit(ctx, "ÉNERGIE", ex, ey + 22, 30, (220, 140, 30), big=True)
            elif t > 41.1:
                k = back((t - 41.1) / 0.3)
                for s_ in (1, -1):
                    ctx.move_to(bx + 180 - 110 * k, 770 - 110 * k * s_)
                    ctx.line_to(bx + 180 + 110 * k, 770 + 110 * k * s_)
                    stroke(ctx, 22, (232, 52, 60))
        ines.objet = None
        ines.draw(ctx, 1000, SOL + 160, 0.8, t, regard=-0.6)
    f.plan(37.7, boites_lettres, [(0, 560, 900, 1.0), (1.6, 560, 900, 1.04)])
    f.plan(39.3, boites_lettres, [(0, 330, 780, 1.45), (1.7, 330, 780, 1.5)])
    f.plan(41.1, boites_lettres, [(0, 700, 860, 1.25), (2.2, 700, 860, 1.3)])

    def studio_ines(ctx, t, lt):
        salon_froid(ctx, t, lt)

    f.plan(43.4, fond_feuille(studio_ines, "AVIS D'IMPÔT", ["revenu fiscal de référence", "seul : moins de 11 000 €",
                                                           "en couple : moins de 16 500 €"],
                              surl="seul : moins de 11 000 €", couleur=(40, 90, 170)),
           [(0, 540, 960, 1.0), (3.3, 540, 960, 1.04)])

    def ecran_cheque(c, w, h):
        c.rectangle(0, 0, w, h)
        c.set_source_rgb(0.97, 0.97, 0.99)
        c.fill()
        c.rectangle(0, 0, w, 40)
        c.set_source_rgb(0.95, 0.6, 0.15)
        c.fill()
        ecrit(c, "CHÈQUE ÉNERGIE", w / 2, 20, 10, (255, 255, 255), big=True)
        for i, l in enumerate(("N° fiscal", "N° du compteur", "Adresse")):
            rrect(c, 10, 56 + i * 34, w - 20, 24, 6)
            c.set_source_rgb(0.9, 0.9, 0.93)
            c.fill()
            ecrit(c, l, 18, 68 + i * 34, 9, INK, ax=0)
        rrect(c, 14, 160, w - 28, 26, 13)
        c.set_source_rgb(0.2, 0.7, 0.4)
        c.fill()
        ecrit(c, "RÉCLAMER", w / 2, 173, 10, (255, 255, 255), big=True)
    f.plan(46.8, tel(studio_ines, ecran_cheque), [(0, 540, 960, 1.0), (4.0, 540, 960, 1.04)])

    def gain(fond, txt):
        def s(ctx, t, lt):
            fond(ctx, t, lt)
            DC.etiquette(ctx, 760, 560, 1.1, txt, lt, couleur=(110, 220, 140))
        return s
    f.plan(51.0, gain(studio_ines, "48 €"), [(0, 560, 880, 1.08), (1.0, 560, 880, 1.12)])

    def ecran_message(c, w, h):
        c.rectangle(0, 0, w, h)
        c.set_source_rgb(0.95, 0.95, 0.97)
        c.fill()
        c.rectangle(0, 0, w, 36)
        c.set_source_rgb(0.3, 0.3, 0.38)
        c.fill()
        ecrit(c, "MA COUSINE", w / 2, 18, 10, (255, 255, 255), big=True)
        rrect(c, 18, 60, w - 26, 56, 12)
        c.set_source_rgb(0.16, 0.55, 0.95)
        c.fill()
        ecrit(c, "Réclame ton", w / 2 + 4, 78, 9, (255, 255, 255), big=True)
        ecrit(c, "chèque énergie", w / 2 + 4, 98, 9, (255, 255, 255), big=True)
        rrect(c, 18, 124, w - 26, 30, 12)
        c.set_source_rgb(0.16, 0.55, 0.95)
        c.fill()
        ecrit(c, "LIEN →", w / 2 + 4, 139, 9, (255, 255, 255), big=True)

    def studio_kevin(ctx, t, lt):
        piece(ctx, mur=(86, 110, 150), mur2=(56, 72, 110), sol=(120, 92, 70))
        fenetre(ctx, t, 560, 380, 420, 520, seed=11, ciel=((70, 90, 140), (170, 190, 220)), montants=2)
        kev.objet = lambda c, x, y, s: DC.telephone(c, x, y - 40, 0.9, t=t)
        kev.draw(ctx, 420, SOL + 100, 0.86, t, regard=0.3)
    f.plan(52.0, tel(studio_kevin, ecran_message), [(0, 540, 960, 1.0), (2.6, 540, 960, 1.04)])

    # ═════════ n° 4 : la mairie ═════════
    def mairie(ctx, t, lt):
        deg(ctx, -800, -900, 2000, SOL, (70, 110, 170), (190, 210, 230))
        couche_floue(ctx, lambda c: V.immeubles(c, -700, 1900, SOL - 300, t, seed=13, col=(140, 160, 190), hmin=200,
                                                hmax=500), rayon=12, bord="constant")
        rrect(ctx, 120, 360, 840, SOL - 360, 6)
        paint(ctx, (236, 226, 206), LW, shade=0.9)
        poly(ctx, [(90, 380), (540, 200), (990, 380)])
        paint(ctx, (210, 196, 176), LW, shade=0.9)
        enseigne(ctx, 540, 450, "MAIRIE", 1.0, fond=(40, 60, 120), col=(255, 255, 255))
        for i in range(4):
            rrect(ctx, 190 + i * 200, 560, 60, SOL - 560, 4)
            paint(ctx, (250, 246, 236), LW * 0.8, shade=0.88)
        rrect(ctx, 460, 980, 160, SOL - 980, 6)
        paint(ctx, (90, 60, 40), LW, shade=0.85)
        ctx.move_to(940, 380)
        ctx.line_to(940, 120)
        stroke(ctx, 8)
        for k_, c_ in enumerate(((40, 70, 170), (250, 250, 250), (220, 40, 50))):
            x0 = 944 + k_ * 50
            ond = math.sin(t * 5 + k_) * 10
            poly(ctx, [(x0, 130 + ond * 0.3), (x0 + 50, 130 + ond), (x0 + 50, 230 + ond), (x0, 230 + ond * 0.3)])
            flat(ctx, c_)
        deg(ctx, -800, SOL, 2000, 2600, (150, 150, 156), (90, 90, 96))
        enseigne(ctx, 540, 820, "CENTRE D'ACTION SOCIALE", 0.62, fond=(250, 250, 250))
        kev.objet = None
        ines.objet = None
        kev.draw(ctx, 240, SOL + 260, 0.9, t, regard=0.4)
        ines.draw(ctx, 820, SOL + 260, 0.86, t, regard=-0.4)
    f.plan(55.0, mairie, [(0, 540, 960, 0.95), (2.4, 540, 940, 1.02)])
    sc, cam, hud = numero(2)
    f.plan(57.5, sc, cam, hud=hud)
    f.plan(60.4, fond_feuille(mairie, "CENTRE D'ACTION SOCIALE", ["aide au chauffage", "colis de Noël",
                                                                 "selon ta ville"], surl="selon ta ville",
                              couleur=(40, 90, 170)), [(0, 540, 960, 1.0), (4.2, 540, 960, 1.04)])
    f.plan(64.8, calendrier_scene("DÉC", "1", "DOSSIERS DÈS DÉBUT DÉCEMBRE", couleur=(40, 90, 170)),
           [(0, 540, 960, 1.0), (2.8, 540, 960, 1.05)])

    def trois_papiers(ctx, t, lt):
        mairie(ctx, t, lt)
        assombrir(ctx, 0.45)
        for j, (t0, titre, x, rot) in enumerate(((68.5, "AVIS D'IMPÔT", 300, -0.12), (69.5, "DOMICILE", 560, 0.04),
                                                 (71.6, "FACTURE", 800, 0.14))):
            if t >= t0:
                feuille(ctx, x, 820 + j * 40, 0.42, titre, ["", ""], k=(t - t0) / 0.4, rot=rot)
        if t >= 73.0:
            ui.panneau(ctx, 540, 1180, "DOSSIER DÉPOSÉ", t - 73.0, rot=-0.06, size=80, fond=(110, 220, 140), bord=INK,
                       col=INK)
    f.plan(67.8, trois_papiers, [(0, 540, 960, 1.0), (6.2, 540, 960, 1.05)])

    # ═════════ n° 3 : le don ═════════
    def cuisine(ctx, t, lt):
        piece(ctx, mur=(230, 196, 150), mur2=(200, 160, 120), sol=(150, 110, 80))
        fenetre(ctx, t, 640, 320, 380, 420, seed=19, ciel=((30, 40, 90), (120, 90, 140)))
        # sapin
        for k_ in range(3):
            poly(ctx, [(140 - 110 + k_ * 22, 820 - k_ * 150), (140, 640 - k_ * 150), (140 + 110 - k_ * 22, 820 - k_ * 150)])
            paint(ctx, (40, 130, 80), LW, shade=0.85)
        for i in range(6):
            circle(ctx, 90 + (i * 37) % 110, 560 + (i * 53) % 220, 10)
            flat(ctx, (255, 214, 60) if i % 2 else (232, 52, 60))
        mere.draw(ctx, 380, SOL - 10, 0.8, t, regard=0.5)
        rrect(ctx, 80, SOL - 300, 920, 40, 8)
        paint(ctx, (120, 80, 50), LW, shade=0.85)
        for x in (120, 940):
            rrect(ctx, x, SOL - 260, 30, 260, 6)
            paint(ctx, (110, 72, 46), LW, shade=0.85)
        for bx, coul in ((150, (232, 52, 60)), (260, (60, 120, 220))):
            rrect(ctx, bx, SOL - 420, 100, 120, 8)
            paint(ctx, coul, LW, shade=0.85)
            ctx.rectangle(bx + 44, SOL - 420, 12, 120)
            flat(ctx, (255, 214, 60))
        rrect(ctx, 650, SOL - 520, 260, 220, 10)
        paint(ctx, (60, 140, 90), LW, shade=0.85)
        rrect(ctx, 700, SOL - 520, 160, 20, 6)
        flat(ctx, INK)
        ecrit(ctx, "AIDE", 780, SOL - 430, 40, (255, 255, 255), big=True)
        ecrit(ctx, "ALIMENTAIRE", 780, SOL - 380, 32, (255, 255, 255), big=True)
    f.plan(74.1, cuisine, [(0, 540, 900, 1.02), (2.0, 540, 900, 1.07)])
    f.plan(76.1, cuisine, [(0, 680, 820, 1.4), (2.9, 700, 820, 1.46)])
    f.plan(79.0, cuisine, [(0, 400, 640, 1.8), (2.3, 400, 640, 1.86)])
    sc, cam, hud = numero(3)
    f.plan(81.3, sc, cam, hud=hud)

    def don75(ctx, t, lt):
        cuisine(ctx, t, lt)
        assombrir(ctx, 0.4)
        ui.panneau(ctx, W / 2, 640, "75 % RENDUS", lt - 0.1, rot=-0.05, size=110, fond=(255, 214, 60), bord=INK,
                   col=INK)
        feuille(ctx, 540, 1010, 0.8, "IMPÔT", ["don à une asso d'aide", "75 % déduits"], k=(lt - 0.4) / 0.5, rot=0.05,
                surl="75 % déduits")
    f.plan(82.8, don75, [(0, 540, 960, 1.0), (5.9, 540, 960, 1.05)])

    def don25(ctx, t, lt):
        cuisine(ctx, t, lt)
        DC.etiquette(ctx, 280, 540, 0.9, "100 €", lt, couleur=(240, 240, 240))
        if lt > 0.5:
            k = ease((lt - 0.5) / 0.3)
            ctx.move_to(150, 600)
            ctx.line_to(150 + 300 * k, 600 - 80 * k)
            stroke(ctx, 16, (232, 52, 60))
        if lt > 1.1:
            DC.etiquette(ctx, 780, 540, 1.0, "25 €", lt - 1.1, couleur=(110, 220, 140))
    f.plan(88.7, don25, [(0, 540, 900, 1.06), (2.7, 540, 900, 1.1)])
    f.plan(91.4, fond_feuille(cuisine, "REÇU FISCAL", ["payer l'impôt", "garder le reçu", "donner avant le 31/12"],
                              surl="donner avant le 31/12", couleur=(40, 140, 90)),
           [(0, 540, 960, 1.0), (4.0, 540, 960, 1.04)])
    f.plan(95.4, calendrier_scene("JANV", "1", "= L'ANNÉE D'APRÈS", couleur=(40, 90, 170)),
           [(0, 540, 960, 1.0), (2.7, 540, 960, 1.05)])

    # ═════════ n° 2 : les RTT (au garage) ═════════
    def garage(ctx, t, lt, patron=False, porte=False, cal=False):
        piece(ctx, mur=(70, 84, 120), mur2=(40, 46, 76), sol=(56, 56, 70))
        fenetre(ctx, t, 640, 330, 380, 520, seed=3, ciel=((40, 50, 96), (200, 140, 130)))
        enseigne(ctx, 300, 300, "GARAGE · BUREAU", 0.95)
        horloge(ctx, 110, 560, 70, t)
        if cal:
            rrect(ctx, 200, 420, 400, 400, 12)
            paint(ctx, (250, 250, 250), LW, shade=0.95)
            rrect(ctx, 200, 420, 400, 70, 12)
            flat(ctx, (220, 50, 60))
            ecrit(ctx, "DÉCEMBRE", 400, 456, 44, (255, 255, 255), big=True)
            for d in range(31):
                cx, cy = 222 + (d % 7) * 54, 510 + (d // 7) * 58
                ecrit(ctx, str(d + 1), cx + 20, cy + 20, 20, INK)
                if d in (22, 23, 29):
                    u = max(0.0, t - 108.4)
                    ctx.save()
                    ctx.translate(cx + 20, cy + 20 + 600 * u * u)
                    ctx.rotate(u * 3)
                    rrect(ctx, -26, -24, 52, 48, 6)
                    flat(ctx, (255, 214, 60), max(0.0, 1 - u))
                    ecrit(ctx, "RTT", 0, 0, 18, INK, big=True, alpha=max(0.0, 1 - u))
                    ctx.restore()
        if porte:
            rrect(ctx, 760, 520, 300, SOL - 520, 6)
            flat(ctx, (24, 26, 40))
        if patron:
            pat.draw(ctx, 900, SOL + 30, 0.8, t, bouche=bp(t), regard=-0.6)
        if porte:
            ctx.rectangle(740, 500, 30, SOL - 500)
            paint(ctx, (180, 150, 110), LW, shade=0.9)
            ctx.rectangle(1050, 500, 40, SOL - 500)
            paint(ctx, (180, 150, 110), LW, shade=0.9)
            ctx.rectangle(740, 480, 350, 30)
            paint(ctx, (180, 150, 110), LW, shade=0.9)
        comptoir(ctx, 40, 560, h=280, texte=None)
        kev.objet = lambda c, x, y, s: DC.telephone(c, x, y - 40, 0.9, t=t)
        kev.draw(ctx, 760 if cal else 300, SOL + 120, 0.86, t, regard=-0.6 if cal else 0.6)

    def ecran_rtt(c, w, h):
        c.rectangle(0, 0, w, h)
        c.set_source_rgb(0.97, 0.97, 0.99)
        c.fill()
        c.rectangle(0, 0, w, 36)
        c.set_source_rgb(0.86, 0.2, 0.24)
        c.fill()
        ecrit(c, "MES CONGÉS", w / 2, 18, 10, (255, 255, 255), big=True)
        ecrit(c, "RTT restants", w / 2, 70, 11, INK)
        ecrit(c, "3", w / 2, 120, 40, (220, 50, 60), big=True)
        ecrit(c, "à poser avant le 31/12", w / 2, 165, 8, INK)
    f.plan(98.1, garage, [(0, 520, 900, 1.05), (1.4, 520, 900, 1.1)])
    f.plan(99.5, tel(garage, ecran_rtt), [(0, 540, 960, 1.0), (4.0, 540, 960, 1.04)])
    sc, cam, hud = numero(4)
    f.plan(103.6, sc, cam, hud=hud)
    f.plan(105.9, lambda c, t, lt: garage(c, t, lt, cal=True), [(0, 540, 760, 1.2), (3.8, 540, 760, 1.26)])
    f.plan(109.7, fond_feuille(lambda c, t, lt: garage(c, t, lt, cal=False), "RACHAT DE RTT",
                              ["jusqu'à fin 2026", "payé comme une heure sup", "+25 %, sans impôt"],
                              surl="+25 %, sans impôt"), [(0, 540, 960, 1.0), (7.1, 540, 960, 1.05)])
    f.plan(116.8, gain(garage, "450 €"), [(0, 540, 900, 1.06), (2.0, 540, 900, 1.1)])
    f.plan(118.8, fond_feuille(garage, "DEMANDE ÉCRITE", ["rachat de 3 RTT", "accord du patron"],
                              surl="accord du patron", tampon="ENVOYÉE", t_tampon=121.0),
           [(0, 540, 960, 1.0), (3.0, 540, 960, 1.04)])
    f.plan(121.8, lambda c, t, lt: garage(c, t, lt, patron=True, porte=True), [(0, 600, 900, 1.0), (2.8, 640, 880, 1.06)])
    f.plan(124.6, lambda c, t, lt: garage(c, t, lt, patron=True, porte=True),
           [(0, 900, 640, 1.8), (1.8, 900, 650, 1.86)])
    f.plan(126.4, lambda c, t, lt: garage(c, t, lt, patron=True, porte=True),
           [(0, 820, 760, 1.4), (1.7, 820, 760, 1.44)],
           hud=lambda ctx, t, lt: ui.panneau(ctx, W / 2, 420, "UNE PRIME DE NOËL ?", lt, rot=-0.05, size=80))
    f.plan(128.1, lambda c, t, lt: garage(c, t, lt, patron=True, porte=True),
           [(0, 300, 640, 1.9), (0.8, 300, 640, 1.95)])

    # ═════════ n° 1 : la prime transport ═════════
    sc, cam, hud = numero(5)
    f.plan(128.9, sc, cam, hud=hud)
    f.plan(130.8, fond_feuille(lambda c, t, lt: garage(c, t, lt, patron=True, porte=True), "DÉCRET DU 20 OCTOBRE",
                              ["prime transport", "jusqu'au 31 décembre"], surl="jusqu'au 31 décembre"),
           [(0, 540, 960, 1.0), (3.2, 540, 960, 1.04)])
    f.plan(134.0, fond_feuille(lambda c, t, lt: garage(c, t, lt, patron=True, porte=True), "PRIME TRANSPORT",
                              ["par salarié", "sans cotisations", "facultative"], surl="sans cotisations",
                              prix="1 000 €"), [(0, 540, 960, 1.0), (5.5, 540, 960, 1.04)])
    f.plan(139.5, lambda c, t, lt: garage(c, t, lt, patron=True, porte=True),
           [(0, 900, 640, 1.8), (1.0, 900, 650, 1.86)])

    def atelier(ctx, t, lt, tableau=True, signe=False):
        piece(ctx, mur=(96, 104, 120), mur2=(60, 66, 80), sol=(70, 70, 76), x0=-1600, x1=2800)
        fenetre(ctx, t, -300, 200, 800, 460, seed=29, ciel=((60, 80, 130), (200, 170, 150)), montants=4)
        enseigne(ctx, 1000, 260, "ATELIER", 1.0)
        if tableau:
            rrect(ctx, 600, 380, 620, 440, 10)
            paint(ctx, (250, 250, 250), LW, shade=0.95)
            k1, k2, k3 = (ease((t - a) / 0.5) for a in (141.0, 145.0, 146.1))
            ecrit(ctx, "AUGMENTATION 1 000 €", 910, 460, 44, INK, big=True, alpha=k1)
            ecrit(ctx, "+ CHARGES = BIEN PLUS", 910, 545, 46, (220, 50, 60), big=True, alpha=k2)
            ecrit(ctx, "PRIME = 1 000 € PILE", 910, 650, 50, (30, 150, 80), big=True, alpha=k3)
            if t > 146.6:
                rrect(ctx, 650, 610, 520, 84, 12)
                stroke(ctx, 8, (30, 150, 80), alpha=ease((t - 146.6) / 0.3))
        for i, m in enumerate(mecs):
            m.draw(ctx, -320 + i * 190, SOL + 20, 0.74, t, regard=0.5)
        pat.draw(ctx, 1320, SOL + 20, 0.8, t, regard=-0.6)
        kev.objet = None
        kev.draw(ctx, 470, SOL + 120, 0.86, t, regard=0.6)
        if signe and t > 148.4:
            feuille(ctx, 1040, 1010, 0.55, "PRIME TRANSPORT", ["tout l'atelier"], k=(t - 148.4) / 0.4, rot=0.06,
                    prix="1 000 €", tampon="SIGNÉ", tampon_k=max(0.0, (t - 149.7) / 0.4))
    f.plan(140.5, atelier, [(0, 500, 860, 0.82), (1.8, 540, 860, 0.86)])
    f.plan(142.3, atelier, [(0, 910, 640, 1.45), (3.8, 910, 650, 1.5)])
    f.plan(146.1, atelier, [(0, 910, 640, 1.5), (2.0, 910, 650, 1.55)])
    f.plan(148.1, lambda c, t, lt: atelier(c, t, lt, tableau=False, signe=True),
           [(0, 760, 860, 0.85), (3.0, 800, 860, 0.9)])

    def total(ctx, t, lt):
        dominos(ctx, t, lt, tombes=True, cal=False, chute=(149.9, 0.25))
        if lt > 0.1:
            assombrir(ctx, 0.25)
            ctx.save()
            ctx.identity_matrix()
            ui.panneau(ctx, W / 2, 620, "1 673 € RÉCUPÉRÉS", lt - 0.1, rot=-0.04, size=96, fond=(110, 220, 140),
                       bord=INK, col=INK)
            ctx.restore()
    f.plan(151.1, total, [(0, 1300, SOL - 370 / 0.6, 0.6), (3.0, 1400, SOL - 370 / 0.64, 0.64)])

    # ═════════ écran : compteur, étapes, sous-titres ═════════
    cles = [(0, 0), (25.0, 100), (51.0, 148), (90.5, 223), (117.8, 673), (149.9, 1673)]
    f.ecran(lambda ctx, t: ui.compteur(ctx, t, "RÉCUPÉRÉ AVANT LE 31/12", cles, apparition=4.6))
    debuts = [12.9, 35.7, 57.5, 81.3, 103.6, 128.9]

    def etapes(ctx, t):
        if t < 12.9 or t >= 151.1:
            return
        k = back((t - 12.9) / 0.35)
        actif = sum(1 for d in debuts if t >= d)
        ctx.save()
        ctx.translate(W - 430, 190)
        ctx.scale(k, k)
        for j in range(6):
            x = j * 74
            fait, cur = j + 1 < actif, j + 1 == actif
            circle(ctx, x, 0, 30 if cur else 24)
            paint(ctx, (255, 214, 60) if cur else ((110, 220, 140) if fait else (60, 60, 76)), LW * 0.8, shade=1)
            ecrit(ctx, str(6 - j), x, 2, 30 if cur else 24, INK if (cur or fait) else (200, 200, 210), big=True)
        ctx.restore()
    f.ecran(etapes)
    groupes = ui.decouper(words)
    f.ecran(lambda ctx, t: ui.sous_titres(ctx, t, groupes, y=Y_SOUS, size=60))

    for i in range(5):
        f.son(0.1 + (i + 1) * 0.4, "pop", 0.4)
    for t_, son, g in [(2.1, "impact", 0.8), (3.4, "succes", 0.5), (5.8, "pop", 0.6), (7.3, "rate", 0.5),
                       (10.7, "impact", 0.8), (12.9, "pop", 0.5), (25.0, "succes", 0.6), (35.7, "pop", 0.5),
                       (51.0, "succes", 0.6), (57.5, "pop", 0.5), (73.0, "succes", 0.5), (81.3, "pop", 0.5),
                       (90.5, "succes", 0.6), (103.6, "pop", 0.5), (108.4, "rate", 0.5), (117.8, "succes", 0.6),
                       (123.9, "rate", 0.5), (128.9, "pop", 0.5), (139.5, "rate", 0.5), (149.7, "succes", 0.8),
                       (151.1, "succes", 0.8)]:
        f.son(t_, son, g)
    f.secousse(2.1, 8)
    f.secousse(10.7, 14)
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
