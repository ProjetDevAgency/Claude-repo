"""Décors de l'histoire du colis perdu : cuisine du père (horloge qui tourne), palier avec le mot sur la porte,
chambre-bureau de Kévin, grands écrans de téléphone (suivi, messages, groupe de famille, mail) et cartons."""
import math

import cairo

from dessin import INK, LW, W, back, circle, dark, ease, ecrit, ellipse, flat, halo, mix, paint, poly, rgb, rrect, \
    stroke, texte, blit

SOL = 1560


def _deg(ctx, x0, y0, x1, y1, c0, c1):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, *rgb(c0))
    g.add_color_stop_rgb(1, *rgb(c1))
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.set_source(g)
    ctx.fill()


def horloge(ctx, x, y, r, t, vite=1.0):
    circle(ctx, x, y, r)
    paint(ctx, (250, 250, 246), LW, shade=0.9)
    for i in range(12):
        a = i * math.pi / 6
        ctx.move_to(x + math.cos(a) * r * 0.78, y + math.sin(a) * r * 0.78)
        ctx.line_to(x + math.cos(a) * r * 0.9, y + math.sin(a) * r * 0.9)
    stroke(ctx, 4)
    for ang, lg, ep in ((t * 0.1 * vite - math.pi / 2, 0.5, 9), (t * 1.2 * vite - math.pi / 2, 0.75, 6)):
        ctx.move_to(x, y)
        ctx.line_to(x + math.cos(ang) * r * lg, y + math.sin(ang) * r * lg)
        stroke(ctx, ep)


def cuisine(ctx, t):
    """Chez le père, le soir."""
    _deg(ctx, -600, -600, 1700, SOL, (236, 214, 176), (214, 190, 150))
    ctx.rectangle(-600, 980, 2300, 240)
    flat(ctx, (90, 150, 160))
    for i in range(-10, 30):
        for j in range(4):
            ctx.rectangle(-600 + i * 60 + (j % 2) * 30, 980 + j * 60, 58, 58)
    stroke(ctx, 2, (255, 255, 255), alpha=0.5)
    rrect(ctx, 600, 320, 380, 420, 14)
    paint(ctx, (70, 60, 120), LW, shade=1)
    _deg(ctx, 610, 330, 970, 730, (60, 50, 110), (230, 130, 110))
    ctx.move_to(790, 320)
    ctx.line_to(790, 740)
    stroke(ctx, LW)
    for x in (-200, 160):
        rrect(ctx, x, 300, 320, 300, 10)
        paint(ctx, (200, 120, 80), LW, shade=0.85)
        circle(ctx, x + 160, 560, 10)
        flat(ctx, INK)
    horloge(ctx, 420, 220, 90, t, vite=3.0)
    _deg(ctx, -600, 1220, 1700, 1320, (180, 120, 80), (150, 100, 70))
    _deg(ctx, -600, SOL - 40, 1700, 2600, (160, 120, 90), (110, 80, 60))
    halo(ctx, 300, 0, 700, (255, 230, 170), 0.25)


def palier(ctx, t, mot=True, colis=0):
    """Couloir d'immeuble : la porte de Kévin, le mot scotché, et éventuellement une pile de colis."""
    _deg(ctx, -600, -600, 1700, SOL, (150, 160, 150), (120, 130, 124))
    ctx.rectangle(-600, 1100, 2300, 460)
    flat(ctx, (96, 110, 104))
    rrect(ctx, 300, 420, 480, 1150, 10)
    paint(ctx, (120, 70, 50), LW * 1.3, shade=0.85)
    for (x, y, w, h) in ((350, 480, 380, 460), (350, 990, 380, 520)):
        rrect(ctx, x, y, w, h, 8)
        stroke(ctx, LW * 0.8, dark((120, 70, 50), 0.7))
    circle(ctx, 720, 1000, 18)
    paint(ctx, (230, 190, 80), LW * 0.7, shade=1)
    rrect(ctx, 500, 360, 80, 40, 6)
    paint(ctx, (230, 230, 230), LW * 0.6, shade=1)
    ecrit(ctx, "12", 540, 380, 26, INK, big=True)
    # sonnette
    rrect(ctx, 840, 900, 70, 110, 10)
    paint(ctx, (230, 230, 236), LW * 0.8, shade=0.9)
    circle(ctx, 875, 955, 16)
    paint(ctx, (200, 60, 60), LW * 0.6, shade=1)
    if mot:
        ctx.save()
        ctx.translate(540, 720)
        ctx.rotate(-0.06 + 0.01 * math.sin(t * 2))
        rrect(ctx, -150, -100, 300, 200, 4)
        paint(ctx, (255, 245, 150), LW * 0.7, shade=0.95)
        ctx.rectangle(-60, -116, 120, 30)
        flat(ctx, (220, 220, 210), 0.8)
        ecrit(ctx, "SONNEZ", 0, -24, 66, INK, big=True)
        ecrit(ctx, "FORT !", 0, 50, 66, (200, 40, 50), big=True)
        ctx.restore()
    _deg(ctx, -600, SOL - 40, 1700, 2600, (110, 100, 96), (80, 72, 70))
    rrect(ctx, 380, SOL - 30, 320, 70, 10)
    flat(ctx, (160, 60, 60))
    # plafonnier qui grésille
    on = 0.75 + 0.25 * (math.sin(t * 13) > -0.8)
    halo(ctx, 540, 0, 800, (255, 250, 220), 0.25 * on)
    for i in range(colis):
        cx = 120 + (i % 4) * 230 + (i // 4) * 40
        cy = SOL + 10 - (i // 4) * 170
        carton(ctx, cx, cy, 0.95 - 0.05 * (i // 4), 0.06 * math.sin(i * 2.3))


def carton(ctx, x, y, s, rot=0.0, label=None):
    """Carton posé (x, y = milieu du bas)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    poly(ctx, [(-110, -170), (-70, -200), (130, -200), (90, -170)])
    paint(ctx, (214, 168, 112), LW, shade=1)
    poly(ctx, [(90, -170), (130, -200), (130, -30), (90, 0)])
    paint(ctx, (176, 132, 84), LW, shade=1)
    rrect(ctx, -110, -170, 200, 170, 4)
    paint(ctx, (200, 154, 100), LW, shade=0.92)
    ctx.rectangle(-30, -170, 40, 170)
    flat(ctx, (230, 200, 150), 0.8)
    rrect(ctx, -90, -80, 70, 50, 4)
    flat(ctx, (255, 255, 255), 0.9)
    for k in range(3):
        ctx.rectangle(-84, -72 + k * 14, 50, 5)
        flat(ctx, INK, 0.6)
    if label:
        ecrit(ctx, label, -10, -125, 30, INK, big=True)
    ctx.restore()


def chambre(ctx, t):
    """Studio de Kévin, le soir : bureau vide (pas d'ordi), croquis du logo, lampe."""
    _deg(ctx, -600, -600, 1700, SOL, (60, 70, 110), (76, 86, 128))
    rrect(ctx, 620, 260, 360, 460, 14)
    paint(ctx, (24, 30, 56), LW, shade=1)
    for i in range(18):
        circle(ctx, 640 + (i * 53) % 330, 290 + (i * 37) % 400, 3)
        flat(ctx, (255, 255, 255), 0.5 + 0.4 * math.sin(t * 2 + i))
    ctx.move_to(800, 260)
    ctx.line_to(800, 720)
    stroke(ctx, LW)
    for i, c in enumerate([(230, 120, 80), (90, 170, 200), (240, 200, 80)]):
        ctx.save()
        ctx.translate(110 + i * 150, 420)
        ctx.rotate(0.05 * (i - 1))
        rrect(ctx, -60, -80, 120, 160, 6)
        paint(ctx, c, LW * 0.7, shade=0.9)
        ctx.restore()
    _deg(ctx, -600, SOL - 40, 1700, 2600, (96, 74, 64), (66, 50, 44))


def bureau_vide(ctx, t, x=540, y=1240):
    """Le plateau du bureau (à dessiner devant Kévin) : place vide de l'ordi, croquis du croissant."""
    rrect(ctx, x - 520, y, 1040, 50, 10)
    paint(ctx, (180, 130, 90), LW, shade=0.85)
    ctx.rectangle(x - 480, y + 50, 40, 420)
    ctx.rectangle(x + 440, y + 50, 40, 420)
    flat(ctx, (150, 104, 70))
    rrect(ctx, x - 200, y - 14, 300, 14, 4)
    stroke(ctx, 4, (255, 255, 255), alpha=0.5)
    # croquis
    ctx.save()
    ctx.translate(x + 280, y - 20)
    ctx.rotate(-0.12)
    rrect(ctx, -110, -150, 220, 150, 4)
    paint(ctx, (250, 250, 245), LW * 0.7, shade=1)
    croissant(ctx, 0, -80, 0.55)
    ctx.restore()
    # lampe
    ctx.move_to(x - 380, y)
    ctx.line_to(x - 330, y - 260)
    ctx.line_to(x - 230, y - 300)
    stroke(ctx, 10)
    poly(ctx, [(x - 260, y - 330), (x - 170, y - 300), (x - 210, y - 230)])
    paint(ctx, (240, 200, 60), LW * 0.8, shade=1)
    halo(ctx, x - 200, y - 200, 330, (255, 220, 140), 0.3 + 0.03 * math.sin(t * 3))


def croissant(ctx, x, y, s):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(-110, 30)
    ctx.curve_to(-120, -60, 120, -60, 110, 30)
    ctx.curve_to(60, -10, -60, -10, -110, 30)
    paint(ctx, (230, 160, 70), 5, shade=0.85)
    for k in (-50, 0, 50):
        ctx.move_to(k - 10, -30)
        ctx.curve_to(k, -10, k, 0, k + 10, 0)
    stroke(ctx, 4, (160, 100, 40))
    ctx.restore()


# ───────────── grand téléphone avec interface lisible ─────────────

def grand_tel(ctx, cx, cy, s, titre, couleur=(40, 160, 90), contenu=None, t=0.0):
    """Téléphone en très gros plan, 640 x 1160 à s = 1 ; contenu(ctx, x0, y0, w, h) dessiné à taille réelle."""
    ctx.save()
    ctx.translate(cx + 12 * math.sin(t * 1.1), cy + 14 * math.sin(t * 1.7))      # tenu en main : il flotte
    ctx.rotate(0.03 * math.sin(t * 1.3))
    ctx.scale(s, s)
    rrect(ctx, -320 + 14, -580 + 18, 640, 1160, 70)
    flat(ctx, (0, 0, 0), 0.3)
    rrect(ctx, -320, -580, 640, 1160, 70)
    paint(ctx, (28, 28, 34), LW * 1.3, shade=1)
    rrect(ctx, -290, -550, 580, 1100, 50)
    flat(ctx, (238, 232, 222))
    ctx.save()
    rrect(ctx, -290, -550, 580, 1100, 50)
    ctx.clip()
    ctx.rectangle(-290, -550, 580, 140)
    flat(ctx, couleur)
    ecrit(ctx, titre, -200, -470, 40, (255, 255, 255), ax=0)
    circle(ctx, -240, -470, 30)
    flat(ctx, (255, 255, 255), 0.85)
    if contenu:
        contenu(ctx, -290, -410, 580, 960)
    ctx.restore()
    rrect(ctx, -70, -545, 140, 26, 13)
    flat(ctx, (28, 28, 34))
    ctx.restore()


def bulle_msg(ctx, x, y, w, txt, moi, k=1.0, size=34, couleur=None):
    """Bulle de messagerie qui pousse (k 0→1). x = bord gauche de la zone, w = largeur de la zone."""
    if k <= 0:
        return 0
    lignes = _couper(txt, size, w * 0.72)
    h = 30 + len(lignes) * size * 1.25
    lw = max(texte(l, size, INK).get_width() for l in lignes) + 44
    bx = x + w - lw - 20 if moi else x + 20
    sc = back(k)
    ctx.save()
    ctx.translate(bx + (lw if moi else 0), y + h)
    ctx.scale(sc, sc)
    ctx.translate(-(lw if moi else 0), -h)
    rrect(ctx, 0, 0, lw, h, 26)
    flat(ctx, couleur or ((210, 246, 200) if moi else (255, 255, 255)))
    for i, l in enumerate(lignes):
        ecrit(ctx, l, 22, 18 + size * 0.62 + i * size * 1.25, size, INK, ax=0)
    ctx.restore()
    return h + 18


def _couper(txt, size, largeur):
    mots, lignes, cur = txt.split(), [], ""
    for m in mots:
        essai = (cur + " " + m).strip()
        if cur and texte(essai, size, INK).get_width() > largeur:
            lignes.append(cur)
            cur = m
        else:
            cur = essai
    if cur:
        lignes.append(cur)
    return lignes


def vocal(ctx, x, y, w, t, k=1.0):
    """Bulle de message vocal avec forme d'onde qui avance."""
    if k <= 0:
        return 0
    sc = back(k)
    ctx.save()
    ctx.translate(x + 20, y)
    ctx.scale(sc, sc)
    rrect(ctx, 0, 0, w * 0.75, 100, 30)
    flat(ctx, (255, 255, 255))
    circle(ctx, 55, 50, 30)
    flat(ctx, (40, 160, 90))
    poly(ctx, [(46, 34), (46, 66), (72, 50)])
    flat(ctx, (255, 255, 255))
    n = 26
    for i in range(n):
        hgt = 10 + 30 * abs(math.sin(i * 1.7 + 0.3) * math.sin(i * 0.6))
        joue = (t * 0.25) % 1 > i / n
        ctx.rectangle(110 + i * 12, 50 - hgt / 2, 6, hgt)
        flat(ctx, (40, 160, 90) if joue else (180, 190, 196))
    ecrit(ctx, "0:07", w * 0.75 - 40, 78, 24, (120, 120, 130), ax=1)
    ctx.restore()
    return 118
