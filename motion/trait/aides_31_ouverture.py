"""Ouverture (≈ 12 s) « 6 aides à récupérer avant le 31 décembre », avec Kévin, moteur « trait ».
Décors créés pour CETTE vidéo uniquement (règle du client : aucun décor réutilisé d'une vidéo à l'autre) :
appartement de nuit à baie vitrée + sol miroir, cascade de dominos, domino géant 1 000 €, station-service de nuit,
pompe et route du garage.

    python3 motion/trait/aides_31_ouverture.py                  # → output/trait/aides_31_ouverture.mp4
    python3 motion/trait/aides_31_ouverture.py --stills 1,4,9
"""
import argparse
import math
import random
import sys
from pathlib import Path

import cairo

sys.path.insert(0, str(Path(__file__).resolve().parent))

import decors as D  # noqa: E402  (seulement les petits objets génériques : calendrier, téléphone)
import ui  # noqa: E402
import voix  # noqa: E402
from dessin import (INK, LW, ROOT, back, circle, cone_lumiere, dark, ease, ease_out, ecrit, ellipse, flat, halo,  # noqa: E402
                    mix, paint, poly, rgb, rrect, stroke)
from film import Film  # noqa: E402
from perso import Perso, traits_choc  # noqa: E402

SOL = 1560
VOIX = {"nar": ("rlqCQzyNTVyUMPGBqC31", {"stability": 0.45, "similarity_boost": 0.8, "style": 0.2})}
LIGNES = [
    ("nar", "[6 aides] à récupérer avant le [31 décembre]."),
    ("nar", "La plus grosse vaut [1 000 euros], et ton patron t'en parlera {jamais.}"),
    ("nar", "Lundi matin, Kévin fait le plein avant d'aller au garage."),
    ("nar", "[90 euros], pour [20 kilomètres] de route."),
]
KEVIN = dict(cheveux="boucles", couleur_cheveux=(30, 24, 30), peau=(198, 138, 98), haut="sweat",
             couleur_haut=(46, 170, 120), bas=(56, 70, 120), chaussures=(245, 245, 245), seed=1)
PATRON = dict(cheveux="chauve", couleur_cheveux=(196, 196, 204), peau=(240, 200, 170), haut="chemise",
              couleur_haut=(40, 58, 112), bas=(34, 42, 78), chaussures=(28, 28, 34), moustache=True, lunettes=True, seed=3)


def degrade(ctx, x0, y0, x1, y1, c0, c1):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, *rgb(c0))
    g.add_color_stop_rgb(1, *rgb(c1))
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.set_source(g)
    ctx.fill()


def reflet(ctx, dessin, alpha=0.28):
    """Reflet sur un sol brillant : la scène retournée sous la ligne du sol, en transparence."""
    ctx.push_group()
    ctx.translate(0, 2 * SOL)
    ctx.scale(1, -1)
    dessin()
    pat = ctx.pop_group()
    ctx.save()
    ctx.rectangle(-2000, SOL, 9000, 2000)
    ctx.clip()
    ctx.set_source(pat)
    ctx.paint_with_alpha(alpha)
    ctx.restore()


# ═════════════ décor 1 : l'appartement de nuit, baie vitrée, sol miroir ═════════════
def appartement_nuit(ctx, t, camx):
    degrade(ctx, -1500, -600, 4500, SOL, (12, 18, 44), (36, 46, 88))
    rnd = random.Random(4)
    for _ in range(140):                                              # étoiles
        x, y = rnd.uniform(-1500, 4500), rnd.uniform(-600, 600)
        circle(ctx, x, y, rnd.uniform(1.2, 3.2))
        flat(ctx, (255, 255, 255), rnd.uniform(0.3, 0.9))
    ctx.save()
    ctx.translate(camx * 0.45, 0)                                     # ville lointaine : parallaxe lente
    rnd = random.Random(8)
    x = -1800
    while x < 4800:                                                   # immeubles avec fenêtres qui s'allument
        w, h = rnd.uniform(110, 230), rnd.uniform(380, 900)
        rrect(ctx, x, SOL - 120 - h, w, h + 120, 4)
        flat(ctx, mix((30, 42, 84), (42, 56, 104), rnd.random()))
        for wy in range(int(SOL - 100 - h), int(SOL - 140), 46):
            for wx in range(int(x) + 16, int(x + w) - 26, 34):
                k = math.sin(wx * 0.31 + wy * 0.17 + math.floor(t * 0.6 + wx % 7) * 1.3)
                if k > 0.35:
                    ctx.rectangle(wx, wy, 12, 16)
                    flat(ctx, (255, 206, 120), 0.85)
        x += w + 14
    ctx.restore()
    for mx in range(-1600, 4800, 470):                                # montants de la baie vitrée
        rrect(ctx, mx, -700, 36, SOL + 700, 6)
        paint(ctx, (16, 20, 42), LW, shade=0.85)
    rrect(ctx, -1600, 880, 6400, 64, 6)
    paint(ctx, (16, 20, 42), LW, shade=1)
    degrade(ctx, -1600, SOL, 4800, SOL + 900, (40, 48, 82), (14, 16, 32))   # sol brillant
    for lx in range(-1600, 4800, 300):                                # reflet de la ville sur le sol
        ctx.rectangle(lx, SOL + 6, 120, 260)
        flat(ctx, (255, 206, 120), 0.04)


def icone(ctx, nom, s):
    ctx.save()
    ctx.scale(s, s)
    lw = 5
    if nom == "pompe":
        rrect(ctx, -26, -38, 44, 74, 8); paint(ctx, (240, 130, 42), lw)
        rrect(ctx, -18, -30, 28, 18, 4); paint(ctx, (255, 246, 232), lw * 0.7, shade=1)
        ctx.move_to(18, -18); ctx.line_to(32, -8); ctx.line_to(32, 22); stroke(ctx, lw)
    elif nom == "flamme":
        ctx.move_to(0, -44); ctx.curve_to(40, -6, 34, 40, 0, 40); ctx.curve_to(-34, 40, -40, -4, 0, -44); paint(ctx, (44, 128, 230), lw)
        ctx.move_to(0, 4); ctx.curve_to(16, 16, 14, 34, 0, 34); ctx.curve_to(-14, 34, -16, 18, 0, 4); flat(ctx, (170, 216, 255))
    elif nom == "maison":
        poly(ctx, [(-40, -4), (0, -42), (40, -4), (30, -4), (30, 36), (-30, 36), (-30, -4)]); paint(ctx, (48, 160, 106), lw)
        ctx.move_to(0, 6); ctx.curve_to(-16, -8, -22, 14, 0, 26); ctx.curve_to(22, 14, 16, -8, 0, 6); flat(ctx, (255, 255, 255))
    elif nom == "coeur":
        ctx.move_to(0, 42); ctx.curve_to(-70, -4, -30, -60, 0, -20); ctx.curve_to(30, -60, 70, -4, 0, 42); paint(ctx, (230, 56, 66), lw)
    elif nom == "calendrier":
        rrect(ctx, -38, -34, 76, 70, 8); paint(ctx, (250, 250, 252), lw, shade=1)
        rrect(ctx, -38, -34, 76, 22, 6); paint(ctx, (140, 86, 232), lw, shade=1)
        ctx.move_to(-16, 10); ctx.line_to(-2, 24); ctx.line_to(20, -2); stroke(ctx, 8, (140, 86, 232))
    elif nom == "bus":
        rrect(ctx, -50, -50, 100, 92, 16); paint(ctx, (244, 182, 30), lw * 1.2)
        rrect(ctx, -38, -38, 76, 34, 8); paint(ctx, (214, 236, 255), lw, shade=1)
        for sx in (-26, 26):
            circle(ctx, sx, 22, 8); paint(ctx, (255, 255, 255), lw * 0.7, shade=1)
        for sx in (-30, 22):
            rrect(ctx, sx, 42, 18, 16, 4); flat(ctx, INK)
    ctx.restore()


def domino(ctx, x, w, h, ang, icon=None, jaune=False, texte=None):
    """Domino posé au sol : pivot = coin bas gauche (x, SOL) ; ang > 0 = penche vers la droite."""
    d, dy = w * 0.14, w * 0.075
    ctx.save()
    ctx.translate(x, SOL)
    ctx.rotate(ang)
    poly(ctx, [(w, 0), (w + d, -dy), (w + d, -h - dy), (w, -h)])
    paint(ctx, (236, 178, 26) if jaune else (206, 208, 218), LW, shade=0.85)
    poly(ctx, [(0, -h), (d, -h - dy), (w + d, -h - dy), (w, -h)])
    paint(ctx, (255, 214, 72) if jaune else (238, 240, 246), LW, shade=1)
    rrect(ctx, 0, -h, w, h, w * 0.08)
    paint(ctx, (255, 246, 206) if jaune else (250, 249, 244), LW * (1.25 if jaune else 1), shade=0.9)
    ctx.move_to(w * 0.14, -h / 2); ctx.line_to(w * 0.86, -h / 2); stroke(ctx, LW * 1.1)
    if jaune:
        circle(ctx, w / 2, -h * 0.8, w * 0.13); paint(ctx, (250, 200, 30), LW)
        ecrit(ctx, texte, w / 2, -h * 0.38, int(w * 0.27), INK, big=True)
        ctx.translate(w / 2, -h * 0.17); icone(ctx, "bus", w / 230)
    else:
        for qx, qy in ((0.27, 0.12), (0.73, 0.12), (0.5, 0.25), (0.27, 0.38), (0.73, 0.38)):
            circle(ctx, w * qx, -h + h * qy, w * 0.065); flat(ctx, INK)
        ctx.translate(w / 2, -h * 0.24); icone(ctx, icon, w / 140)
    ctx.restore()


# ═════════════ décor 2 : la station-service de nuit ═════════════
def station_nuit(ctx, t):
    degrade(ctx, -600, -600, 1700, SOL - 200, (6, 10, 22), (18, 26, 46))
    rnd = random.Random(2)
    for i in range(9):                                                # arbres sombres au fond
        x = -300 + i * 190 + rnd.uniform(-30, 30)
        poly(ctx, [(x - 110, SOL - 260), (x, SOL - 720 - rnd.uniform(0, 140)), (x + 110, SOL - 260)])
        flat(ctx, (10, 22, 20))
    rrect(ctx, 640, SOL - 520, 560, 300, 8); paint(ctx, (44, 48, 60), LW, shade=0.85)       # boutique
    rrect(ctx, 680, SOL - 470, 480, 170, 6); flat(ctx, (255, 232, 180))
    halo(ctx, 920, SOL - 380, 420, (255, 220, 160), 0.25)
    degrade(ctx, -600, SOL - 220, 1700, SOL + 900, (40, 46, 62), (10, 12, 22))              # sol mouillé
    for x in (120, 520, 920):                                         # piliers + pompes
        rrect(ctx, x - 22, 560, 44, SOL - 600, 6); paint(ctx, (226, 230, 238), LW, shade=0.8)
        rrect(ctx, x - 24, 860, 48, 120, 4); paint(ctx, (44, 84, 160), LW, shade=0.85)
        rrect(ctx, x + 50, SOL - 420, 120, 260, 12); paint(ctx, (238, 240, 245), LW, shade=0.82)
        rrect(ctx, x + 50, SOL - 420, 120, 50, 10); paint(ctx, (216, 40, 48), LW, shade=0.9)
        rrect(ctx, x + 72, SOL - 350, 76, 46, 6); flat(ctx, (70, 220, 130), 0.9)
        rrect(ctx, x + 30, SOL - 170, 160, 26, 6); paint(ctx, (180, 184, 196), LW, shade=0.9)
        ellipse(ctx, x + 110, SOL + 120, 230, 60); flat(ctx, (255, 250, 236), 0.10)          # flaque de lumière
    poly(ctx, [(-300, 420), (1400, 380), (1420, 540), (-320, 590)]); paint(ctx, (236, 240, 248), LW, shade=0.9)   # auvent
    poly(ctx, [(-300, 420), (1400, 380), (1400, 432), (-300, 476)]); paint(ctx, (255, 88, 30), LW, shade=1)
    halo(ctx, 540, 430, 900, (255, 110, 40), 0.20 + 0.02 * math.sin(t * 4))
    for x in (40, 300, 560, 820, 1080):                               # spots sous l'auvent
        rrect(ctx, x - 50, 530, 100, 16, 6); flat(ctx, (255, 255, 255))
        cone_lumiere(ctx, x, 545, 110, 520, 1000, 0.13, (240, 246, 255))


# ═════════════ décor 3 : la pompe, la route du garage ═════════════
def route_garage(ctx, t, ofs):
    degrade(ctx, -600, -600, 1800, 1100, (104, 102, 160), (240, 176, 140))                 # ciel du matin
    ctx.save()
    ctx.translate(-ofs * 0.3, 0)
    rnd = random.Random(13)
    x = -700
    while x < 2200:
        w, h = rnd.uniform(100, 210), rnd.uniform(240, 520)
        rrect(ctx, x, 1100 - h, w, h, 3); paint(ctx, (58, 72, 128), LW * 0.6, shade=0.9)
        for wy in range(int(1100 - h + 26), 1080, 46):
            for wx in range(int(x) + 16, int(x + w) - 22, 34):
                if rnd.random() < 0.3:
                    ctx.rectangle(wx, wy, 12, 16); flat(ctx, (255, 214, 140))
        x += w + 16
    ctx.restore()
    degrade(ctx, -600, 1100, 1800, 1240, (104, 108, 126), (86, 90, 108))                    # route
    for lx in range(-600, 1800, 240):
        rrect(ctx, lx - (ofs * 0.6) % 240, 1158, 130, 16, 6); flat(ctx, (238, 238, 244))
    degrade(ctx, -600, 1240, 1800, 2600, (78, 82, 100), (48, 50, 66))                      # parvis
    rrect(ctx, -600, -620, 2400, 150, 0); paint(ctx, (36, 38, 50), LW, shade=1)            # plafond de l'auvent
    for lx in range(-560, 1800, 330):
        rrect(ctx, lx, -458, 200, 18, 9); flat(ctx, (255, 255, 255))
        halo(ctx, lx + 100, -440, 220, (255, 255, 255), 0.18)


def panneau_garage(ctx, x, y, s):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    rrect(ctx, -14, 0, 28, 900, 6); paint(ctx, (150, 154, 168), LW)
    rrect(ctx, -210, -240, 420, 250, 18); paint(ctx, (252, 252, 252), LW * 1.2, shade=0.95)
    rrect(ctx, -192, -222, 384, 214, 10); stroke(ctx, LW * 0.8)
    ecrit(ctx, "GARAGE  →", 0, -168, 70, INK, big=True)
    ecrit(ctx, "20 km", 0, -66, 104, INK, big=True)
    ctx.restore()


def pompe(ctx, x, y, s, prix, t):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    rrect(ctx, -40, -10, 440, 40, 8); paint(ctx, (230, 226, 160), LW)
    rrect(ctx, 0, -920, 360, 920, 26); paint(ctx, (246, 247, 250), LW * 1.2, shade=0.82)
    rrect(ctx, 0, -920, 360, 70, 22); paint(ctx, (52, 120, 226), LW, shade=0.9)
    rrect(ctx, 30, -830, 300, 240, 16); paint(ctx, (14, 40, 26), LW, shade=1)
    halo(ctx, 180, -700, 220, (120, 255, 160), 0.12)
    ecrit(ctx, "À PAYER", 64, -788, 30, (140, 236, 170), ax=0)
    ecrit(ctx, prix, 180, -676, 96, (150, 255, 180), big=True)
    rrect(ctx, 30, -560, 142, 58, 10); paint(ctx, (60, 186, 106), LW)
    rrect(ctx, 188, -560, 142, 58, 10); paint(ctx, (244, 200, 30), LW)
    ecrit(ctx, "ESSENCE", 101, -531, 32, (255, 255, 255), big=True)
    ecrit(ctx, "DIESEL", 259, -531, 32, INK, big=True)
    for px in (40, 200):
        rrect(ctx, px, -470, 120, 160, 14); paint(ctx, (38, 40, 56), LW, shade=1)
    ctx.move_to(100, -320); ctx.curve_to(40, 20, 270, 90, 520, -140); stroke(ctx, 18, (24, 24, 32))
    ctx.restore()


def voiture(ctx, x, y, s):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    poly(ctx, [(0, -60), (0, -230), (90, -282), (220, -420), (620, -420), (760, -272), (880, -252), (930, -150), (930, -60)])
    paint(ctx, (44, 156, 152), LW * 1.2, shade=0.82)
    poly(ctx, [(250, -390), (410, -390), (410, -282), (150, -282)]); paint(ctx, (200, 232, 240), LW, shade=0.9)
    poly(ctx, [(440, -390), (600, -390), (700, -282), (440, -282)]); paint(ctx, (200, 232, 240), LW, shade=0.9)
    for wx in (200, 720):
        circle(ctx, wx, -50, 92); paint(ctx, (28, 28, 38), LW, shade=1)
        circle(ctx, wx, -50, 40); paint(ctx, (196, 200, 210), LW * 0.8, shade=0.85)
    rrect(ctx, -20, -152, 160, 48, 6); paint(ctx, (255, 255, 255), LW * 0.8, shade=1)
    ecrit(ctx, "AB-123-CD", 60, -128, 30, INK)
    ctx.restore()


def billets(ctx, t, x, y):
    for i in range(7):
        p = t * 1.1 - i * 0.07
        if p <= 0:
            continue
        ctx.save()
        ctx.translate(x + math.sin(i * 2.1 + p * 4) * 90, y + p * 520 + i * 26)
        ctx.rotate(math.sin(p * 5 + i) * 0.9)
        rrect(ctx, -84, -42, 168, 84, 8); paint(ctx, (150, 204, 188), LW * 0.7, shade=0.9)
        ecrit(ctx, "20", -50, 0, 38, (60, 104, 96), big=True)
        ctx.restore()


# ═════════════ le film ═════════════
def construire(work):
    voice, words = voix.build(LIGNES, VOIX, work)
    f = Film(voice, words)
    T = f.t
    kev, pat, kev2 = Perso(**KEVIN), Perso(**PATRON), Perso(**KEVIN)

    def tasse(ctx, x, y, s):
        ctx.save(); ctx.translate(x, y - 40); ctx.scale(s, s)
        rrect(ctx, -30, -56, 60, 76, 8); paint(ctx, (240, 232, 218), LW)
        rrect(ctx, -30, -56, 60, 16, 6); flat(ctx, (120, 76, 44))
        ctx.restore()
    pat.objet = tasse
    kev.emotion(0, "content").emotion(T("récupérer"), "choc").emotion(T("31"), "content")
    pat.pose(0, "repos").emotion(0, "neutre")
    pat.pose(T("plus"), "leve_d").emotion(T("plus"), "choc")
    pat.pose(T("patron"), "mains_hanches").emotion(T("patron"), "malin")
    kev2.pose(0, "repos").emotion(0, "content").emotion(T("90"), "choc").emotion(T("20"), "triste")

    DX, DW, DH = [430, 700, 970, 1240, 1510], 210, 420
    GX, GW, GH = 1840, 400, 820
    ICONES = ["pompe", "flamme", "maison", "coeur", "calendrier"]
    t_cascade = 0.3

    def objets_salle(ctx, t):
        kev.draw(ctx, 250, SOL, 0.95, t, regard=0.8)
        for i in range(5):
            t0 = t_cascade + i * 0.26
            gap = (DX[i + 1] if i < 4 else GX) - DX[i] - DW
            rest = math.asin(min(1.0, (gap + DW * 0.14) / DH)) + (0.03 if i < 4 else 0)
            domino(ctx, DX[i], DW, DH, rest * ease_out((t - t0) / 0.3), ICONES[i])
        ga = 0.0 if t < T("patron") else 0.24 * ease((t - T("patron")) / 0.9)
        domino(ctx, GX, GW, GH, ga, jaune=True, texte="1 000 €")
        pat.draw(ctx, 2480, SOL, 0.82, t, regard=-0.8)

    def salle(ctx, t, lt, camx=0):
        appartement_nuit(ctx, t, camx)
        reflet(ctx, lambda: objets_salle(ctx, t))
        if t > T("31") - 0.2:
            halo(ctx, GX + GW / 2, SOL - GH / 2, 700, (255, 236, 190), 0.22 * ease((t - T("31") + 0.2) / 0.6))
        objets_salle(ctx, t)
        if T("31") - 0.1 <= t < T("plus") + 0.35:                      # le calendrier tombe au bout d'un fil, puis remonte
            k = back((t - T("31") + 0.1) / 0.4)
            y = -600 + 1150 * k - 1300 * ease((t - T("plus") + 0.25) / 0.5)
            ctx.move_to(1720, -900); ctx.line_to(1720, y - 150); stroke(ctx, 3, (220, 220, 230))
            D.calendrier(ctx, 1720, y, 1.25 + 0.05 * math.sin(t * 3), "DÉC", "31")
        if T("plus") <= t < T("Lundi"):
            ui.badge(ctx, 2480, SOL - 0.82 * 1000 - 60, "LE PATRON", t - T("plus") - 0.2)
        if T("jamais") <= t < T("Lundi"):
            traits_choc(ctx, 250, SOL - 0.95 * 880, 150, t - T("jamais"))

    def scene_salle(cam_x):
        return lambda ctx, t, lt: salle(ctx, t, lt, cam_x)

    def station(ctx, t, lt):
        station_nuit(ctx, t)

    def pompe_scene(ctx, t, lt):
        route_garage(ctx, t, t * 60)
        panneau_garage(ctx, 900, 380, 1.0)
        voiture(ctx, 640, 1480, 0.85)
        prix = min(90.0, 30.69 + 59.31 * ease_out((t - T("plein")) / 1.9)) if t >= T("plein") else 30.69
        pompe(ctx, 60, 1500, 0.95, f"{prix:.2f} €".replace(".", ","), t)
        kev2.draw(ctx, 560, 1520, 0.8, t, regard=-0.6)
        if t >= T("90"):
            traits_choc(ctx, 560, 1520 - 0.8 * 880, 120, t - T("90"))
            billets(ctx, t - T("90") - 0.2, 640, 980)

    # plans : la caméra suit la cascade puis remonte vers le domino géant
    f.plan(0, scene_salle(0), [(0, 520, 1060, 1.0), (1.0, 760, 1100, 1.12)], fouet=False)
    f.plan("récupérer", scene_salle(-500), [(0, 1150, 1200, 1.8), (1.0, 1500, 1220, 1.85)])
    f.plan("31", scene_salle(-1300), [(0, 2080, 1100, 1.0), (1.2, 2120, 1100, 1.05)])
    f.plan("plus", scene_salle(-1400), [(0, 2180, 1120, 1.12), (1.6, 2200, 1120, 1.2)])
    f.plan("patron", scene_salle(-1450), [(0, 2240, 1080, 1.25), (1.5, 2260, 1060, 1.32)])
    f.plan("Lundi", station, [(0, 540, 980, 1.0), (1.2, 540, 960, 1.06)])
    f.plan("Kévin", pompe_scene, [(0, 560, 1000, 1.0), (1.4, 560, 1000, 1.03)])
    f.plan("90", pompe_scene, [(0, 400, 1000, 1.5), (1.2, 410, 1000, 1.56)])
    f.plan("20", pompe_scene, [(0, 900, 760, 1.25), (1.5, 900, 760, 1.3)])

    f.ecran(lambda ctx, t: ui.compteur(ctx, t, "RÉCUPÉRÉ AVANT LE 31/12", [(0, 0)], apparition=T("plus")))
    groupes = ui.decouper(words)
    f.ecran(lambda ctx, t: ui.sous_titres(ctx, t, groupes))
    for i in range(5):
        f.son(t_cascade + i * 0.26 + 0.26, "pop", 0.45)
    for mot, son, g in [("31", "pop", 0.8), ("1", "impact", 0.8), ("jamais", "impact", 0.9), ("90", "rate", 0.8)]:
        f.son(mot, son, g)
    f.secousse("jamais", 14)
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills")
    ap.add_argument("--out", default=str(ROOT / "output/trait/aides_31_ouverture.mp4"))
    a = ap.parse_args()
    work = ROOT / "output/trait/_work_aides_31"
    f = construire(work)
    print(f"durée {f.dur:.1f} s, {len(f.plans)} plans")
    if a.stills:
        f.stills([float(x) for x in a.stills.split(",")], work / "stills")
    else:
        print("→", f.render(a.out))


if __name__ == "__main__":
    main()
