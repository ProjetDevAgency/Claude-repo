"""Décors du garage : atelier avec la Clio sur le pont, accueil avec comptoir et chaises de la salle d'attente,
la Clio vue de profil, la fiche d'ordre de réparation, la facture, le trousseau de clés."""
import math

import cairo

from dessin import INK, LW, circle, ecrit, ellipse, flat, halo, paint, poly, rgb, rrect, stroke

SOL = 1560
ORANGE = (236, 120, 40)


def _deg(ctx, x0, y0, x1, y1, c0, c1):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, *rgb(c0))
    g.add_color_stop_rgb(1, *rgb(c1))
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.set_source(g)
    ctx.fill()


def _neon(ctx, x, y, w, t):
    k = 0.85 + 0.15 * math.sin(t * 9) * (1 if int(t * 1.3) % 5 == 0 else 0)
    rrect(ctx, x - w / 2, y - 14, w, 28, 14)
    flat(ctx, (250, 252, 240), k)
    stroke(ctx, 5)
    halo(ctx, x, y + 40, w * 0.8, (240, 250, 255), 0.18 * k)


def voiture(ctx, x, y, s, couleur=(220, 60, 60), rot=0.0, t=0.0):
    """Petite citadine de profil (x = milieu, y = bas des roues)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    poly(ctx, [(-330, -70), (-320, -170), (-170, -190), (-90, -300), (130, -300), (230, -190), (330, -170),
               (340, -70)])
    paint(ctx, couleur, LW, shade=0.82)
    poly(ctx, [(-150, -195), (-80, -280), (10, -280), (10, -195)])
    paint(ctx, (170, 210, 240), LW * 0.8, shade=0.9)
    poly(ctx, [(30, -195), (30, -280), (120, -280), (200, -195)])
    paint(ctx, (170, 210, 240), LW * 0.8, shade=0.9)
    rrect(ctx, 290, -160, 46, 26, 8)
    flat(ctx, (255, 236, 150))
    ecrit(ctx, "CLIO", -230, -120, 30, (255, 255, 255), big=True)
    for wx in (-200, 210):
        circle(ctx, wx, -60, 62)
        paint(ctx, (34, 34, 40), LW, shade=1)
        circle(ctx, wx, -60, 26)
        paint(ctx, (190, 190, 200), LW * 0.7, shade=1)
        a = t * 6
        ctx.move_to(wx + 22 * math.cos(a), -60 + 22 * math.sin(a))
        ctx.line_to(wx - 22 * math.cos(a), -60 - 22 * math.sin(a))
        stroke(ctx, 4)
    ctx.restore()


def atelier(ctx, t, pont=0.6, voiture_on=True):
    """L'atelier : murs gris, panneau d'outils, pont élévateur avec la Clio levée, tache d'huile."""
    _deg(ctx, -600, -600, 1700, SOL, (176, 186, 200), (140, 150, 166))
    ctx.rectangle(-600, 900, 2300, 30)
    flat(ctx, ORANGE)
    # panneau d'outils avec silhouettes
    rrect(ctx, -60, 260, 520, 360, 10)
    paint(ctx, (120, 100, 80), LW, shade=0.9)
    for i, (dx, dy, w, h) in enumerate(((40, 40, 30, 200), (110, 60, 120, 30), (110, 130, 90, 26), (260, 40, 26, 220),
                                        (330, 60, 120, 120), (40, 270, 200, 30), (300, 230, 160, 40))):
        rrect(ctx, -60 + dx, 260 + dy, w, h, 8)
        paint(ctx, (200, 200, 210) if i % 2 else (230, 80, 60), 4, shade=0.85)
    ecrit(ctx, "GARAGE DU CENTRE", 760, 160, 60, (40, 50, 70), big=True)
    _neon(ctx, 760, 60, 360, t)
    # pont élévateur
    h = 140 + 420 * pont
    for x in (480, 1040):
        rrect(ctx, x - 28, SOL - h - 40, 56, h + 40, 8)
        paint(ctx, (230, 190, 50), LW, shade=0.85)
    rrect(ctx, 460, SOL - h - 60, 600, 32, 8)
    paint(ctx, (90, 90, 100), LW, shade=0.9)
    _deg(ctx, -600, SOL - 40, 1700, 2600, (120, 124, 130), (90, 94, 100))
    ellipse(ctx, 760, SOL + 120, 170, 34)
    flat(ctx, (40, 40, 48), 0.45)
    if voiture_on:
        voiture(ctx, 760, SOL - h - 60, 0.9, t=0)
        # goutte d'huile
        k = (t * 0.8) % 1
        ellipse(ctx, 700, SOL - h - 40 + k * (h + 120), 9, 13)
        flat(ctx, (30, 30, 36), 1 - k * 0.6)


def chaise(ctx, x, y, s=1.0, couleur=(60, 120, 190)):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -90, -340, 180, 200, 20)
    paint(ctx, couleur, LW, shade=0.85)
    rrect(ctx, -100, -160, 200, 44, 14)
    paint(ctx, couleur, LW, shade=0.85)
    for dx in (-70, 70):
        ctx.move_to(dx, -116)
        ctx.line_to(dx, 0)
    stroke(ctx, 10, (60, 60, 70))
    ctx.restore()


def accueil(ctx, t):
    """L'accueil du garage : vitre sur l'atelier, affiche des tarifs, distributeur, sol carrelé."""
    _deg(ctx, -600, -600, 1700, SOL, (232, 226, 214), (210, 204, 192))
    # vitre sur l'atelier
    rrect(ctx, 520, 220, 620, 560, 8)
    paint(ctx, (160, 176, 196), LW, shade=0.95)
    voiture(ctx, 860, 700, 0.55)
    ctx.move_to(520, 500)
    ctx.line_to(1140, 500)
    stroke(ctx, 8, (230, 236, 240), alpha=0.5)
    # affiche des tarifs
    rrect(ctx, 60, 260, 340, 420, 8)
    paint(ctx, (252, 250, 242), LW * 0.8, shade=0.95)
    ecrit(ctx, "TARIFS", 230, 310, 44, ORANGE, big=True)
    for k, (a, b) in enumerate((("Vidange", "89 €"), ("Plaquettes", "180 €"), ("Disques", "220 €"))):
        ecrit(ctx, a, 90, 390 + k * 80, 30, INK, ax=0)
        ecrit(ctx, b, 370, 390 + k * 80, 30, INK, ax=1)
    _neon(ctx, 540, 80, 420, t)
    _deg(ctx, -600, SOL - 40, 1700, 2600, (180, 170, 150), (140, 130, 116))
    for i in range(-6, 14):
        ctx.move_to(i * 120, SOL - 40)
        ctx.line_to(i * 180 - 300, 2600)
    stroke(ctx, 3, (120, 110, 100), alpha=0.5)
    halo(ctx, 540, 200, 700, (255, 250, 230), 0.15)


def comptoir(ctx, x, y, w=560, h=330):
    """Comptoir de l'accueil (à dessiner APRÈS le garagiste)."""
    rrect(ctx, x - w / 2, y, w, h, 14)
    paint(ctx, (70, 80, 100), LW, shade=0.85)
    rrect(ctx, x - w / 2 - 16, y - 24, w + 32, 38, 10)
    paint(ctx, ORANGE, LW, shade=0.85)
    ecrit(ctx, "ACCUEIL", x, y + h / 2, 50, (240, 240, 246), big=True)


def fiche(ctx, x, y, s, rot=0.0, signe=1.0, surligne=0.0):
    """Ordre de réparation signé : « VIDANGE SEULE — 89 € »."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    rrect(ctx, -200, -260, 400, 520, 8)
    paint(ctx, (252, 252, 246), LW * 0.8, shade=0.95)
    ecrit(ctx, "ORDRE DE", 0, -205, 34, INK, big=True)
    ecrit(ctx, "RÉPARATION", 0, -165, 34, INK, big=True)
    if surligne > 0:
        rrect(ctx, -175, -95, 350 * min(1, surligne), 70, 10)
        flat(ctx, (255, 226, 60), 0.85)
    ecrit(ctx, "VIDANGE SEULE", 0, -60, 40, (200, 40, 50), big=True)
    ecrit(ctx, "89 € TTC", 0, 20, 56, INK, big=True)
    for k in range(2):
        rrect(ctx, -160, 90 + k * 36, 320, 12, 6)
        flat(ctx, (205, 205, 210))
    if signe > 0:
        ctx.move_to(-100, 200)
        n = int(30 * min(1, signe))
        for i in range(n):
            u = i / 29
            ctx.line_to(-100 + 200 * u, 200 + 22 * math.sin(u * 14) * (1 - u * 0.5))
        stroke(ctx, 5, (30, 60, 160))
    ecrit(ctx, "Signature", -120, 238, 20, (130, 130, 140))
    ctx.restore()


def facture(ctx, x, y, s, lignes, t_lignes, t, barre=None):
    """Facture qui se remplit : lignes = [(libellé, prix)], t_lignes = instants d'apparition ; barre = (t0, idx...)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -380, -480, 760, 960, 10)
    paint(ctx, (252, 252, 246), LW, shade=0.95)
    ecrit(ctx, "FACTURE", 0, -410, 64, ORANGE, big=True)
    ecrit(ctx, "Garage du Centre", 0, -350, 28, (120, 120, 130))
    yy = -260
    for (lib, prix), tl in zip(lignes, t_lignes):
        if t < tl:
            break
        k = min(1, (t - tl) / 0.2)
        ecrit(ctx, lib, -320, yy, 44, INK, ax=0, alpha=k)
        ecrit(ctx, prix, 320, yy, 44, INK, ax=1, alpha=k)
        yy += 100
    ctx.move_to(-330, 300)
    ctx.line_to(330, 300)
    stroke(ctx, 4, (180, 180, 190))
    if t >= t_lignes[-1]:
        ecrit(ctx, "TOTAL", -320, 380, 56, INK, big=True, ax=0)
        ecrit(ctx, "640 €", 320, 380, 72, (210, 40, 50), big=True, ax=1)
    ctx.restore()


def cles(ctx, x, y, s, rot=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    circle(ctx, 0, 0, 34)
    stroke(ctx, 10, (200, 200, 210))
    rrect(ctx, 20, -16, 120, 32, 8)
    paint(ctx, (210, 210, 220), 5, shade=0.85)
    for dx in (90, 115):
        ctx.rectangle(20 + dx - 10, 16, 14, 20)
        flat(ctx, (190, 190, 200))
    rrect(ctx, -70, 20, 60, 80, 14)
    paint(ctx, (40, 40, 48), 5, shade=1)
    ctx.restore()


def pile_factures(ctx, x, y, n, t, s=1.0):
    """Pile de vieilles factures jaunies, chacune avec « PLAQUETTES »."""
    for i in range(n):
        ctx.save()
        ctx.translate(x + math.sin(i * 1.9) * 50, y - i * 30)
        ctx.rotate(math.sin(i * 2.7) * 0.14)
        ctx.scale(s, s)
        rrect(ctx, -170, -110, 340, 220, 8)
        paint(ctx, (248, 238, 206), LW * 0.8, shade=0.95)
        ecrit(ctx, "PLAQUETTES", 0, -50, 36, (200, 40, 50), big=True)
        ecrit(ctx, str(2006 + i * 2), 0, 20, 30, (120, 110, 90))
        ctx.restore()
