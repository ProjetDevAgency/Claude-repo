"""Décors du chantier de plomberie : salle de bain en travaux, extérieur avec la maison et le camion, objets
(caisse à outils, pièces de monnaie, lettres de mise en demeure)."""
import math

import cairo

from dessin import INK, LW, circle, dark, ecrit, ellipse, flat, halo, mix, paint, poly, rgb, rrect, stroke

SOL = 1560


def _deg(ctx, x0, y0, x1, y1, c0, c1):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, *rgb(c0))
    g.add_color_stop_rgb(1, *rgb(c1))
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.set_source(g)
    ctx.fill()


def salle_de_bain(ctx, t):
    """Salle de bain en travaux : carrelage à moitié posé, tuyaux apparents, baignoire, seau."""
    _deg(ctx, -600, -600, 1700, SOL, (226, 222, 210), (200, 196, 184))
    # carrelage posé sur la moitié gauche
    for i in range(-10, 9):
        for j in range(0, 14):
            x, y = i * 70, 380 + j * 70
            if x > 400 - j * 18:
                continue
            ctx.rectangle(x, y, 68, 68)
            flat(ctx, (150, 196, 210) if (i + j) % 2 else (170, 210, 222))
    # tuyaux apparents (cuivre) qui serpentent
    for k, (x0, c) in enumerate(((700, (200, 120, 70)), (760, (90, 130, 200)))):
        ctx.move_to(x0, -200)
        ctx.line_to(x0, 700 + k * 40)
        ctx.line_to(x0 + 200, 700 + k * 40)
        ctx.line_to(x0 + 200, 1100)
        stroke(ctx, 26, INK)
        ctx.move_to(x0, -200)
        ctx.line_to(x0, 700 + k * 40)
        ctx.line_to(x0 + 200, 700 + k * 40)
        ctx.line_to(x0 + 200, 1100)
        stroke(ctx, 16, c)
    # goutte qui tombe d'un raccord
    k = (t * 0.9) % 1
    ellipse(ctx, 960, 1110 + k * 380, 9, 13)
    flat(ctx, (120, 190, 240), 1 - k * 0.5)
    # baignoire
    rrect(ctx, -200, 1180, 760, 300, 60)
    paint(ctx, (248, 248, 250), LW, shade=0.88)
    rrect(ctx, -170, 1200, 700, 60, 30)
    flat(ctx, (210, 220, 228))
    _deg(ctx, -600, SOL - 40, 1700, 2600, (170, 150, 130), (120, 104, 90))
    # seau et sac de colle
    rrect(ctx, 820, SOL - 150, 130, 150, 14)
    paint(ctx, (240, 160, 40), LW, shade=0.85)
    rrect(ctx, 960, SOL - 110, 140, 110, 10)
    paint(ctx, (200, 200, 190), LW, shade=0.85)
    halo(ctx, 300, 200, 700, (255, 250, 230), 0.2)


def exterieur(ctx, t, camion_x=None):
    """Devant la maison en chantier : ciel, maison avec échafaudage, trottoir, camion utilitaire."""
    _deg(ctx, -600, -600, 1700, 1000, (130, 190, 235), (210, 232, 245))
    for i, (cx, cy) in enumerate(((150, 180), (700, 120))):
        x = (cx + t * 10) % 1500 - 200
        for dx, dy, r in ((0, 0, 55), (55, -18, 65), (110, 0, 50)):
            circle(ctx, x + dx, cy + dy, r)
            flat(ctx, (255, 255, 255), 0.85)
    rrect(ctx, -100, 420, 720, 700, 6)
    paint(ctx, (236, 214, 180), LW, shade=0.85)
    poly(ctx, [(-140, 430), (260, 250), (660, 430)])
    paint(ctx, (180, 80, 60), LW, shade=0.85)
    for x in (40, 360):
        rrect(ctx, x, 560, 150, 170, 6)
        paint(ctx, (150, 200, 230), LW * 0.8, shade=0.9)
    # échafaudage
    for x in (560, 700):
        ctx.move_to(x, 380)
        ctx.line_to(x, 1130)
    for y in (560, 760, 960):
        ctx.move_to(540, y)
        ctx.line_to(720, y)
    stroke(ctx, 10, (90, 90, 100))
    _deg(ctx, -600, 1100, 1700, 1300, (150, 150, 156), (130, 130, 136))
    _deg(ctx, -600, 1300, 1700, 2600, (96, 96, 104), (70, 70, 78))
    for i in range(-2, 12):
        ctx.rectangle(i * 160 + (t * 0) % 160, 1420, 90, 14)
        flat(ctx, (230, 230, 230), 0.6)
    if camion_x is not None:
        camion(ctx, camion_x, 1380, 1.0)


def camion(ctx, x, y, s, neuf=True):
    """Camionnette utilitaire blanche toute neuve (x = milieu, y = sol)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -330, -330, 470, 300, 18)
    paint(ctx, (248, 248, 250), LW, shade=0.88)
    poly(ctx, [(140, -330), (230, -330), (330, -190), (330, -30), (140, -30)])
    paint(ctx, (248, 248, 250), LW, shade=0.88)
    poly(ctx, [(160, -310), (225, -310), (300, -200), (160, -200)])
    paint(ctx, (170, 210, 240), LW * 0.8, shade=0.9)
    rrect(ctx, -300, -260, 400, 70, 10)
    flat(ctx, (40, 90, 170))
    ecrit(ctx, "PLOMBERIE MARTIN", -100, -225, 34, (255, 255, 255), big=True)
    for wx in (-200, 220):
        circle(ctx, wx, -30, 56)
        paint(ctx, (34, 34, 40), LW, shade=1)
        circle(ctx, wx, -30, 22)
        paint(ctx, (190, 190, 200), LW * 0.7, shade=1)
    if neuf:
        for i in range(3):
            a = t_eclat(i)
            ctx.save()
            ctx.translate(-120 + i * 170, -340)
            ctx.scale(a, a)
            ctx.move_to(0, -24)
            ctx.line_to(6, -6)
            ctx.line_to(24, 0)
            ctx.line_to(6, 6)
            ctx.line_to(0, 24)
            ctx.line_to(-6, 6)
            ctx.line_to(-24, 0)
            ctx.line_to(-6, -6)
            ctx.close_path()
            flat(ctx, (255, 230, 120))
            ctx.restore()
    ctx.restore()


_T = [0.0]


def t_eclat(i):
    return 0.6 + 0.4 * math.sin(_T[0] * 4 + i * 2)


def caisse_outils(ctx, x, y, s):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -110, -80, 220, 80, 10)
    paint(ctx, (210, 50, 50), LW, shade=0.85)
    ctx.move_to(-50, -80)
    ctx.curve_to(-50, -130, 50, -130, 50, -80)
    stroke(ctx, 12)
    ctx.restore()


def pieces(ctx, x, y, t, n=6):
    """Petites pièces de monnaie qui tombent (« trois sous »)."""
    for i in range(n):
        k = ((t * 0.8) + i / n) % 1
        px = x + math.sin(i * 2.1) * 140
        py = y - 400 + k * 500
        ellipse(ctx, px, py, 34, 34 * abs(math.cos(t * 3 + i)) + 4)
        paint(ctx, (230, 190, 60), 4, shade=0.85)


def lettres(ctx, x, y, n, s=1.0):
    """Pile de lettres « MISE EN DEMEURE »."""
    for i in range(n):
        ctx.save()
        ctx.translate(x + math.sin(i * 1.9) * 40, y - i * 26)
        ctx.rotate(math.sin(i * 2.7) * 0.12)
        ctx.scale(s, s)
        rrect(ctx, -170, -110, 340, 220, 8)
        paint(ctx, (252, 252, 248), LW * 0.8, shade=0.95)
        ecrit(ctx, "MISE EN DEMEURE", 0, -60, 34, (200, 40, 50), big=True)
        for k in range(3):
            rrect(ctx, -130, -10 + k * 36, 260, 12, 6)
            flat(ctx, (200, 200, 206))
        ctx.restore()
