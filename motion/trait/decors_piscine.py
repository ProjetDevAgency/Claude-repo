"""Décors de l'histoire du pisciniste : jardin, piscine en perspective (feuilles, fissure, résine, eau qui monte,
dauphin en mosaïque), bureau, schéma en coupe, et quelques objets (chèque, brosse à dents, tuyau)."""
import math
import random

import cairo

from dessin import INK, LW, circle, dark, ecrit, ellipse, flat, halo, mix, paint, poly, rgb, rrect, stroke

# géométrie de la piscine (monde 1080 x 1920)
HAUT = [(270, 930), (810, 930), (1010, 1480), (70, 1480)]          # bord intérieur (niveau de l'eau pleine)
FOND = [(315, 1130), (765, 1130), (975, 1480), (105, 1480)]        # fond du bassin
EXT = [(220, 895), (860, 895), (1075, 1530), (5, 1530)]            # margelle extérieure
DAUPHIN = (540, 1310)
FISSURE = [(400, 1095), (430, 1150), (415, 1200), (470, 1255), (455, 1310), (520, 1370), (505, 1430), (560, 1480)]


def _lerp(a, b, k):
    return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)


def sur_fond(u, v):
    """Point du fond : u de gauche à droite, v du fond (loin) vers l'avant."""
    g = _lerp(FOND[0], FOND[3], v)
    d = _lerp(FOND[1], FOND[2], v)
    return _lerp(g, d, u)


def _quad(ctx, q):
    poly(ctx, q)


def _deg(ctx, x0, y0, x1, y1, c0, c1):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, *rgb(c0))
    g.add_color_stop_rgb(1, *rgb(c1))
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.set_source(g)
    ctx.fill()


_RNG = random.Random(4)
FEUILLES = [(_RNG.random(), _RNG.random() ** 0.8, _RNG.random() * 6.28, _RNG.choice(
    [(200, 120, 40), (170, 90, 30), (220, 160, 60), (140, 80, 40), (120, 110, 40)])) for _ in range(140)]


def feuille(ctx, x, y, s, a, c):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(a)
    ctx.scale(s, s * 0.6)
    ctx.move_to(-22, 0)
    ctx.curve_to(-8, -16, 8, -16, 22, 0)
    ctx.curve_to(8, 16, -8, 16, -22, 0)
    ctx.restore()
    paint(ctx, c, 2.5, shade=1)


def dauphin(ctx, x, y, s, propre=1.0, t=0.0):
    """Dauphin en mosaïque au fond (aplati par la perspective)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s * 0.55)
    halo(ctx, 0, 0, 240, (120, 220, 255), 0.25 * propre)

    def corps():
        ctx.move_to(-190, 14)
        ctx.curve_to(-170, 2, -150, -2, -120, -10)              # bec
        ctx.curve_to(-115, -50, -80, -62, -40, -62)             # front bombé
        ctx.curve_to(40, -62, 110, -40, 140, -12)               # dos
        ctx.line_to(196, -52)                                   # queue, lobe haut
        ctx.curve_to(186, -20, 186, 0, 172, 4)
        ctx.curve_to(186, 10, 196, 34, 200, 52)                 # lobe bas
        ctx.line_to(138, 14)
        ctx.curve_to(80, 44, -40, 50, -110, 30)                 # ventre
        ctx.curve_to(-140, 24, -170, 22, -190, 14)
        ctx.close_path()
    corps()
    ctx.move_to(-10, -60)
    ctx.curve_to(10, -90, 30, -112, 44, -116)                   # aileron
    ctx.curve_to(40, -90, 46, -70, 60, -56)
    ctx.close_path()
    ctx.move_to(-50, 36)
    ctx.line_to(-30, 80)
    ctx.line_to(-10, 40)
    ctx.close_path()
    col = mix((90, 90, 80), (40, 120, 220), propre)
    paint(ctx, col, 5, shade=0.85)
    ctx.save()
    corps()
    ctx.clip()
    ellipse(ctx, -40, 30, 150, 26)
    flat(ctx, mix((140, 140, 130), (170, 220, 250), propre))
    for i in range(-10, 11):
        ctx.move_to(i * 20, -130)
        ctx.line_to(i * 20, 80)
        ctx.move_to(-200, i * 20)
        ctx.line_to(210, i * 20)
    stroke(ctx, 2, (255, 255, 255), alpha=0.35)
    ctx.restore()
    circle(ctx, -110, -22, 8)
    flat(ctx, INK)
    ctx.restore()


def jardin(ctx, t, soir=0.0):
    _deg(ctx, -600, -600, 1700, 900, mix((120, 190, 240), (60, 50, 110), soir), mix((200, 230, 250), (240, 140, 110), soir))
    circle(ctx, 860, 260, 70)
    flat(ctx, mix((255, 240, 180), (255, 190, 120), soir))
    for i, (cx, cy, s) in enumerate([(200, 220, 1.0), (640, 140, 0.8), (1000, 330, 0.9)]):
        x = (cx + t * 12 * s) % 1500 - 200
        for dx, dy, r in ((0, 0, 60), (60, -20, 70), (120, 0, 55), (60, 20, 60)):
            circle(ctx, x + dx * s, cy + dy * s, r * s)
            flat(ctx, (255, 255, 255), 0.85 - 0.4 * soir)
    # maison à gauche
    rrect(ctx, -300, 380, 560, 560, 6)
    paint(ctx, (240, 222, 196), LW, shade=0.85)
    poly(ctx, [(-340, 390), (-20, 220), (300, 390)])
    paint(ctx, (190, 90, 70), LW, shade=0.85)
    for x in (-200, 60):
        rrect(ctx, x, 520, 130, 150, 6)
        paint(ctx, (150, 200, 230), LW * 0.8, shade=0.9)
        ctx.move_to(x + 65, 520)
        ctx.line_to(x + 65, 670)
        stroke(ctx, LW * 0.6)
    # haie + portail
    for i in range(14):
        circle(ctx, 240 + i * 70, 830 + math.sin(i * 1.7) * 14, 60)
        paint(ctx, (60, 130, 70), LW * 0.7, shade=1)
    ctx.rectangle(240, 830, 1300, 90)
    flat(ctx, (60, 130, 70))
    rrect(ctx, 880, 650, 200, 240, 6)
    stroke(ctx, LW * 1.2)
    for k in range(6):
        ctx.move_to(900 + k * 32, 660)
        ctx.line_to(900 + k * 32, 880)
    stroke(ctx, LW * 0.8)
    # pelouse
    _deg(ctx, -600, 880, 1700, 2600, mix((120, 190, 90), (60, 90, 70), soir), mix((80, 150, 70), (40, 60, 50), soir))


def piscine(ctx, t, feuilles=0.0, fissure=0.0, resine=0.0, eau=0.0, propre=0.0, soir=0.0):
    # margelle
    _quad(ctx, EXT)
    paint(ctx, (236, 226, 204), LW, shade=0.9)
    # parois
    sale = feuilles > 0.3
    c_paroi = mix((60, 150, 200), (110, 120, 100), 0.6 if sale else 0)
    c_fond = mix((120, 200, 230), (140, 140, 110), 0.6 if sale else 0)
    for q in ([HAUT[0], HAUT[1], FOND[1], FOND[0]], [HAUT[0], FOND[0], FOND[3], HAUT[3]],
              [HAUT[1], HAUT[2], FOND[2], FOND[1]]):
        _quad(ctx, q)
        paint(ctx, c_paroi, LW * 0.8, shade=0.9)
    _quad(ctx, FOND)
    paint(ctx, c_fond, LW * 0.8, shade=0.95)
    # carrelage du fond
    for i in range(1, 12):
        a, b = sur_fond(0, i / 12), sur_fond(1, i / 12)
        ctx.move_to(*a)
        ctx.line_to(*b)
        a, b = sur_fond(i / 12, 0), sur_fond(i / 12, 1)
        ctx.move_to(*a)
        ctx.line_to(*b)
    stroke(ctx, 2, (255, 255, 255), alpha=0.35)
    for k in range(1, 6):
        y = HAUT[0][1] + (FOND[0][1] - HAUT[0][1]) * k / 6
        ctx.move_to(HAUT[0][0] + (FOND[0][0] - HAUT[0][0]) * k / 6, y)
        ctx.line_to(HAUT[1][0] + (FOND[1][0] - HAUT[1][0]) * k / 6, y)
    stroke(ctx, 2, (255, 255, 255), alpha=0.3)
    dauphin(ctx, *DAUPHIN, 1.0, propre, t)
    # fissure (se dessine) puis résine grise par-dessus
    if fissure > 0:
        n = max(2, int(len(FISSURE) * min(1, fissure)))
        ctx.move_to(*FISSURE[0])
        for p in FISSURE[1:n]:
            ctx.line_to(*p)
        stroke(ctx, 7, (40, 30, 30))
    if resine > 0:
        n = max(2, int(len(FISSURE) * min(1, resine)))
        ctx.move_to(*FISSURE[0])
        for p in FISSURE[1:n]:
            ctx.line_to(*p)
        stroke(ctx, 16, (170, 172, 180))
    # feuilles mortes
    if feuilles > 0:
        for i, (u, v, a, c) in enumerate(FEUILLES[:int(len(FEUILLES) * feuilles)]):
            x, y = sur_fond(u, v)
            feuille(ctx, x, y + math.sin(t * 2 + i) * 1.5, 0.8 + 0.6 * v, a + math.sin(t + i) * 0.05, c)
    # eau
    if eau > 0:
        s = [_lerp(f, h, eau) for f, h in zip(FOND, HAUT)]
        ctx.push_group()
        for q in (s, [s[0], s[1], FOND[1], FOND[0]], [s[0], FOND[0], FOND[3], s[3]], [s[1], s[2], FOND[2], FOND[1]]):
            _quad(ctx, q)
            flat(ctx, (40, 170, 230))
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(0.5)
        ctx.save()
        _quad(ctx, s)
        ctx.clip()
        for j in range(14):
            y = s[0][1] + (s[3][1] - s[0][1]) * (j + 0.5) / 14
            ctx.move_to(-100, y)
            for x in range(-100, 1200, 40):
                ctx.line_to(x, y + math.sin(x * 0.03 + t * 2.2 + j) * 5)
            stroke(ctx, 3, (255, 255, 255), alpha=0.25)
        ctx.restore()
        _quad(ctx, s)
        stroke(ctx, 3, (255, 255, 255), alpha=0.6)
    # bord intérieur
    _quad(ctx, HAUT)
    stroke(ctx, LW)
    if soir > 0:
        ctx.rectangle(-600, -600, 2400, 3200)
        flat(ctx, (30, 20, 70), 0.35 * soir)


def tas_feuilles(ctx, x, y, w, t):
    """Feuilles devant les jambes (« jusqu'aux genoux »)."""
    r = random.Random(9)
    for i in range(70):
        dx = (r.random() - 0.5) * w
        dy = -r.random() ** 2 * 170
        feuille(ctx, x + dx, y + dy + math.sin(t * 2 + i) * 2, 1.4, r.random() * 6.3, FEUILLES[i][3])


def bureau(ctx, t):
    _deg(ctx, -600, -600, 1700, 1560, (200, 210, 222), (170, 180, 196))
    rrect(ctx, 560, 300, 420, 520, 12)
    paint(ctx, (150, 200, 240), LW, shade=0.95)
    for i in range(4):
        rrect(ctx, 600 + i * 95, 820 - 160 - i * 70, 80, 160 + i * 70, 4)
        flat(ctx, (110, 150, 190))
    ctx.move_to(770, 300)
    ctx.line_to(770, 820)
    ctx.move_to(560, 560)
    ctx.line_to(980, 560)
    stroke(ctx, LW)
    _deg(ctx, -600, 1560, 1700, 2600, (110, 100, 96), (80, 72, 70))
    rrect(ctx, -100, 1250, 1300, 60, 10)
    paint(ctx, (150, 110, 80), LW, shade=0.85)
    rrect(ctx, 80, 1020, 330, 220, 12)
    paint(ctx, (40, 40, 50), LW, shade=1)
    rrect(ctx, 100, 1040, 290, 180, 6)
    flat(ctx, (90, 140, 200))


def cheque(ctx, x, y, s, montant="6 000 €"):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(-0.08)
    ctx.scale(s, s)
    rrect(ctx, -180, -80, 360, 160, 10)
    paint(ctx, (250, 244, 220), LW, shade=0.92)
    ctx.rectangle(-180, -80, 360, 30)
    flat(ctx, (120, 170, 200), 0.6)
    ecrit(ctx, montant, 50, 10, 64, INK, big=True)
    ctx.move_to(-150, 50)
    ctx.curve_to(-120, 20, -90, 70, -60, 40)
    ctx.curve_to(-40, 20, -20, 60, 0, 45)
    stroke(ctx, 4, (40, 60, 160))
    ctx.restore()


def brosse(ctx, x, y, s, a):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(a)
    ctx.scale(s, s)
    rrect(ctx, -10, -150, 22, 170, 10)
    paint(ctx, (240, 80, 120), LW * 0.8, shade=0.9)
    rrect(ctx, -16, 10, 34, 40, 6)
    paint(ctx, (255, 255, 255), LW * 0.7, shade=1)
    ctx.restore()


def tuyau(ctx, t, x, y):
    ctx.move_to(-200, y - 300)
    ctx.curve_to(x - 300, y - 420, x - 80, y - 160, x, y - 120)
    stroke(ctx, 30, INK)
    ctx.move_to(-200, y - 300)
    ctx.curve_to(x - 300, y - 420, x - 80, y - 160, x, y - 120)
    stroke(ctx, 18, (60, 160, 80))
    for i in range(4):
        k = (t * 1.6 + i / 4) % 1
        ellipse(ctx, x + 6, y - 110 + k * 260, 9, 14)
        flat(ctx, (120, 200, 255), 1 - k * 0.6)


def coupe(ctx, t, k_eau, k_fissure, x=540, y=900):
    """Schéma en coupe : la terre pousse, l'eau monte trop vite, la paroi fend."""
    ctx.save()
    ctx.translate(x, y)
    rrect(ctx, -460, -260, 920, 620, 20)
    flat(ctx, (120, 84, 56))
    for i in range(30):
        circle(ctx, -430 + (i * 97) % 860, -220 + (i * 61) % 560, 8)
        flat(ctx, (90, 60, 40))
    poly(ctx, [(-300, -260), (300, -260), (260, 200), (-260, 200)])
    paint(ctx, (230, 230, 236), LW, shade=0.92)
    poly(ctx, [(-260, -260), (260, -260), (225, 160), (-225, 160)])
    flat(ctx, (250, 250, 252))
    if k_eau > 0:
        top = 160 - 420 * k_eau
        ctx.save()
        poly(ctx, [(-260, -260), (260, -260), (225, 160), (-225, 160)])
        ctx.clip()
        ctx.rectangle(-300, top, 600, 500)
        flat(ctx, (60, 170, 230), 0.85)
        ctx.restore()
    for sx in (-1, 1):
        for j in range(3):
            yy = -150 + j * 120
            ax = sx * (420 - 30 * math.sin(t * 6 + j))
            ctx.move_to(ax, yy)
            ctx.line_to(sx * 320, yy)
            stroke(ctx, 10, (255, 210, 40))
            poly(ctx, [(sx * 320, yy - 20), (sx * 290, yy), (sx * 320, yy + 20)])
            flat(ctx, (255, 210, 40))
    if k_fissure > 0:
        pts = [(-240, -60), (-215, -10), (-238, 40), (-212, 100)]
        n = max(2, int(len(pts) * min(1, k_fissure)) + 1)
        ctx.move_to(*pts[0])
        for p in pts[1:n]:
            ctx.line_to(*p)
        stroke(ctx, 9, (220, 40, 50))
    ctx.restore()
