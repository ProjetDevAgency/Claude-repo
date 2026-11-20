"""Décors et objets en plus : ville de nuit avec sol miroir, dominos, icônes, station-service, pompe, billets."""
import math

import cairo

from dessin import INK, LW, W, back, circle, cone_lumiere, dark, ecrit, ellipse, flat, halo, mix, paint, poly, rgb, \
    rrect, stroke

SOL = 1500


def _deg(ctx, x0, y0, x1, y1, c0, c1):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, *rgb(c0))
    g.add_color_stop_rgb(1, *rgb(c1))
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.set_source(g)
    ctx.fill()


def immeubles(ctx, x0, x1, base, t, seed=0, col=(34, 40, 74), hmin=300, hmax=700):
    x, i = x0, 0
    while x < x1:
        r = math.sin(i * 12.9898 + seed * 78.233) * 43758.5453
        r = r - math.floor(r)
        w = 110 + r * 120
        h = hmin + (hmax - hmin) * ((r * 7.3) % 1)
        rrect(ctx, x, base - h, w, h + 20, 4)
        flat(ctx, col)
        for j in range(int(h // 56)):
            for k in range(int(w // 46)):
                on = math.sin(i * 3.1 + j * 1.7 + k * 2.3 + seed + math.floor(t * 0.6 + j * 0.13)) > 0.2
                ctx.rectangle(x + 12 + k * 46, base - h + 20 + j * 56, 24, 30)
                flat(ctx, (255, 206, 120) if on else mix(col, (90, 100, 150), 0.4), 0.9 if on else 1)
        x += w + 14
        i += 1


def ville_nuit(ctx, t, x0=-800, x1=3200):
    """Grande baie vitrée sur la ville la nuit, sol sombre qui reflète."""
    _deg(ctx, x0, -600, x1, SOL, (14, 20, 46), (40, 48, 92))
    for i in range(40):
        sx = x0 + (i * 397) % (x1 - x0)
        sy = -400 + (i * 211) % 700
        circle(ctx, sx, sy, 2 + (i % 3))
        flat(ctx, (255, 255, 255), 0.4 + 0.3 * math.sin(t * 2 + i))
    immeubles(ctx, x0, x1, SOL - 220, t, seed=3, col=(28, 32, 62), hmin=500, hmax=1000)
    immeubles(ctx, x0 + 60, x1, SOL - 160, t, seed=7, col=(38, 44, 82), hmin=250, hmax=600)
    # montants de la baie vitrée
    for x in range(x0, x1, 420):
        ctx.rectangle(x, -600, 26, SOL + 600)
        flat(ctx, (16, 18, 30))
    ctx.rectangle(x0, SOL - 240, x1 - x0, 20)
    flat(ctx, (16, 18, 30))
    _deg(ctx, x0, SOL - 220, x1, SOL + 900, (30, 32, 52), (12, 12, 22))


def reflet(ctx, dessin, alpha=0.18):
    """Redessine `dessin(ctx)` à l'envers sous la ligne du sol, en transparence (sol miroir)."""
    ctx.push_group()
    ctx.translate(0, 2 * SOL)
    ctx.scale(1, -1)
    dessin(ctx)
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(alpha)


# ───────────── icônes ─────────────

def icone(ctx, nom, x, y, s=1.0, c=(40, 120, 230)):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    lw = LW * 0.8
    if nom == "essence":
        rrect(ctx, -28, -34, 44, 70, 6)
        paint(ctx, (240, 120, 40), lw, shade=1)
        rrect(ctx, -20, -26, 28, 20, 3)
        flat(ctx, (255, 255, 255))
        ctx.move_to(16, -20)
        ctx.line_to(32, -6)
        ctx.line_to(32, 24)
        stroke(ctx, lw)
    elif nom == "flamme":
        ctx.move_to(0, -40)
        ctx.curve_to(36, -6, 34, 38, 0, 40)
        ctx.curve_to(-34, 38, -36, 0, -12, -16)
        ctx.curve_to(-8, 0, 4, 0, 0, -40)
        paint(ctx, (60, 130, 240), lw, shade=1)
        ctx.move_to(0, 4)
        ctx.curve_to(16, 18, 12, 34, 0, 34)
        ctx.curve_to(-12, 34, -14, 18, 0, 4)
        flat(ctx, (170, 210, 255))
    elif nom == "maison":
        poly(ctx, [(-40, -2), (0, -38), (40, -2)])
        paint(ctx, (60, 170, 110), lw, shade=1)
        rrect(ctx, -30, -4, 60, 42, 4)
        paint(ctx, (60, 170, 110), lw, shade=1)
        poly(ctx, [(-12, 18), (0, 8), (12, 18), (12, 30), (-12, 30)])
        flat(ctx, (255, 255, 255))
    elif nom == "coeur":
        ctx.move_to(0, 34)
        ctx.curve_to(-60, -4, -30, -48, 0, -18)
        ctx.curve_to(30, -48, 60, -4, 0, 34)
        paint(ctx, (230, 50, 70), lw, shade=1)
    elif nom == "calendrier":
        rrect(ctx, -36, -32, 72, 66, 8)
        paint(ctx, (255, 255, 255), lw, shade=1)
        rrect(ctx, -36, -32, 72, 20, 6)
        paint(ctx, (130, 80, 210), lw, shade=1)
        ctx.move_to(-16, 12)
        ctx.line_to(-4, 22)
        ctx.line_to(18, 0)
        stroke(ctx, lw * 1.2, (130, 80, 210))
    elif nom == "bus":
        rrect(ctx, -40, -40, 80, 76, 14)
        paint(ctx, (255, 196, 30), lw, shade=1)
        rrect(ctx, -28, -28, 56, 26, 4)
        flat(ctx, (255, 255, 255))
        for sx in (-1, 1):
            circle(ctx, sx * 22, 20, 7)
            flat(ctx, INK)
            ctx.rectangle(sx * 26 - 7, 36, 14, 12)
            flat(ctx, INK)
    ctx.restore()


# ───────────── dominos ─────────────

def domino(ctx, x, y, s, angle=0.0, haut=None, bas=None, montant=None, lueur=0.0, couleur=(250, 246, 232)):
    """Domino debout : (x, y) = coin bas-GAUCHE ; il bascule autour du coin bas-droit (angle en radians, + = vers la droite)."""
    w, h, d = 150, 280, 26
    ctx.save()
    ctx.translate(x + w * s, y)
    ctx.rotate(angle)
    ctx.translate(-w * s, 0)
    ctx.scale(s, s)
    if lueur > 0:
        halo(ctx, w / 2, -h / 2, 360, (255, 220, 120), 0.35 * lueur)
    poly(ctx, [(w, -h + 10), (w + d, -h - 6), (w + d, -16), (w, 0)])
    paint(ctx, dark(couleur, 0.78), LW, shade=1)
    poly(ctx, [(10, -h), (w + d - 6, -h - 6 - 4), (w + d, -h - 6), (w, -h + 10)])
    rrect(ctx, 0, -h, w, h, 18)
    paint(ctx, couleur, LW, shade=0.9)
    ctx.move_to(18, -h / 2)
    ctx.line_to(w - 18, -h / 2)
    stroke(ctx, LW)
    if haut == "points":
        for px, py in ((-1, -1), (0, 0), (1, 1)):
            circle(ctx, w / 2 + px * 36, -h * 0.75 + py * 36, 11)
            flat(ctx, INK)
    elif haut == "soleil":
        circle(ctx, w / 2, -h * 0.75, 26)
        paint(ctx, (255, 206, 40), LW * 0.8, shade=1)
    elif haut:
        icone(ctx, haut, w / 2, -h * 0.75, 1.1)
    if montant:
        ecrit(ctx, montant, w / 2, -h * 0.42, 40, INK, big=True)
        if bas:
            icone(ctx, bas, w / 2, -h * 0.18, 0.75)
    elif bas:
        icone(ctx, bas, w / 2, -h * 0.25, 1.1)
    ctx.restore()


def chute(t, t0, duree=0.32, max_a=1.25):
    """Angle d'un domino qui tombe (gravité puis petit rebond contre le voisin)."""
    if t < t0:
        return 0.0
    u = (t - t0) / duree
    if u < 1:
        return max_a * u * u
    v = t - t0 - duree
    return max_a - 0.08 * math.exp(-v * 9) * abs(math.sin(v * 26))


# ───────────── station-service ─────────────

def station(ctx, t):
    """Plan large : station-service la nuit, auvent éclairé."""
    _deg(ctx, -400, -400, 1500, 1300, (8, 14, 30), (24, 34, 56))
    immeubles(ctx, -400, 1500, 1250, t, seed=11, col=(18, 24, 44), hmin=150, hmax=380)
    _deg(ctx, -400, 1250, 1500, 2400, (40, 44, 56), (20, 22, 30))
    # auvent
    poly(ctx, [(-60, 760), (1140, 700), (1160, 800), (-40, 870)])
    paint(ctx, (235, 235, 240), LW, shade=0.9)
    poly(ctx, [(-40, 870), (1160, 800), (1160, 840), (-40, 912)])
    paint(ctx, (236, 96, 40), LW, shade=0.9)
    for i in range(6):
        x = 60 + i * 190
        ctx.rectangle(x, 840 - i * 11 + 30, 90, 10)
        flat(ctx, (255, 250, 220))
        cone_lumiere(ctx, x + 45, 880 - i * 11, 90, 340, 620, 0.12 + 0.02 * math.sin(t * 4 + i))
    for x in (160, 900):
        ctx.rectangle(x, 900, 46, 450)
        paint(ctx, (210, 210, 218), LW, shade=0.85)
    for x in (380, 640):
        rrect(ctx, x, 1080, 110, 260, 12)
        paint(ctx, (230, 232, 238), LW, shade=0.85)
        rrect(ctx, x + 18, 1110, 74, 50, 6)
        flat(ctx, (30, 70, 50))
    ctx.rectangle(-400, 1340, 1900, 14)
    flat(ctx, (255, 255, 255), 0.15)


def billet(ctx, x, y, s, rot):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    rrect(ctx, -70, -38, 140, 76, 8)
    paint(ctx, (120, 200, 140), LW * 0.8, shade=0.85)
    circle(ctx, 0, 0, 22)
    stroke(ctx, LW * 0.6, (40, 110, 60))
    ecrit(ctx, "€", 0, 0, 30, (40, 110, 60), big=True)
    ctx.restore()


def pompe_ecran(ctx, x, y, montant, actif=True):
    rrect(ctx, x - 150, y - 90, 300, 180, 16)
    paint(ctx, (24, 40, 34), LW, shade=1)
    ecrit(ctx, "À PAYER", x, y - 52, 26, (140, 230, 160))
    ecrit(ctx, montant, x, y + 22, 84, (110, 255, 140) if actif else (60, 120, 70), big=True)


def pompe(ctx, x, y, montant, t):
    """Pompe à essence vue de près (x = milieu, y = sol)."""
    rrect(ctx, x - 190, y - 1020, 380, 1020, 30)
    paint(ctx, (226, 230, 238), LW, shade=0.84)
    rrect(ctx, x - 190, y - 1020, 380, 110, 30)
    paint(ctx, (236, 96, 40), LW, shade=0.9)
    pompe_ecran(ctx, x, y - 780, montant)
    for i, (lab, c) in enumerate((("SP95", (60, 170, 90)), ("GAZOLE", (240, 196, 40)))):
        rrect(ctx, x - 150 + i * 160, y - 640, 140, 60, 10)
        paint(ctx, c, LW * 0.8, shade=0.9)
        ecrit(ctx, lab, x - 80 + i * 160, y - 610, 30, INK, big=True)
    # pistolet et tuyau
    rrect(ctx, x + 120, y - 540, 70, 150, 14)
    paint(ctx, (40, 40, 48), LW, shade=1)
    ctx.move_to(x + 160, y - 390)
    ctx.curve_to(x + 260, y - 200, x + 120, y - 120, x + 60, y - 260)
    stroke(ctx, 22, INK)
    ctx.move_to(x + 160, y - 390)
    ctx.curve_to(x + 260, y - 200, x + 120, y - 120, x + 60, y - 260)
    stroke(ctx, 12, (70, 70, 80))


def voiture(ctx, x, y, s, couleur=(200, 60, 70)):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(-300, -70)
    ctx.curve_to(-290, -150, -200, -160, -150, -170)
    ctx.curve_to(-100, -260, 120, -260, 170, -170)
    ctx.curve_to(260, -160, 310, -130, 310, -70)
    ctx.line_to(310, -40)
    ctx.line_to(-300, -40)
    ctx.close_path()
    paint(ctx, couleur, LW, shade=0.82)
    poly(ctx, [(-120, -172), (-70, -236), (10, -236), (10, -172)])
    paint(ctx, (170, 210, 240), LW * 0.8, shade=0.9)
    poly(ctx, [(30, -172), (30, -236), (110, -236), (150, -172)])
    paint(ctx, (170, 210, 240), LW * 0.8, shade=0.9)
    for wx in (-180, 190):
        circle(ctx, wx, -40, 62)
        paint(ctx, (34, 34, 40), LW, shade=1)
        circle(ctx, wx, -40, 26)
        paint(ctx, (180, 180, 190), LW * 0.7, shade=1)
    ctx.restore()


def panneau_route(ctx, x, y, l1, l2, s=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.rectangle(-12, -40, 24, 640)
    paint(ctx, (150, 150, 160), LW, shade=0.85)
    poly(ctx, [(-150, -170), (120, -170), (170, -100), (120, -30), (-150, -30)])
    paint(ctx, (250, 250, 250), LW, shade=0.92)
    ecrit(ctx, l1, -20, -132, 38, INK, big=True)
    ecrit(ctx, l2, -20, -72, 52, INK, big=True)
    ctx.restore()
