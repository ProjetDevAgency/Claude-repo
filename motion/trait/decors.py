"""Décors et objets du style « trait » (coordonnées monde 1080x1920, le sol vers y = 1560).

Les décors sont volontairement un peu ternes et sombres (les personnages et les chiffres ressortent),
avec des faisceaux de lumière et des objets qui bougent tout le temps (écrans, lampes, voitures dehors…).
"""
import math

from dessin import (H, INK, LW, W, circle, cone_lumiere, dark, ecrit, ellipse, flat, halo, mix, paint, poly, rgb,
                    rrect, stroke)

SOL = 1560


def _degrade(ctx, y0, y1, c0, c1):
    import cairo
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, *rgb(c0))
    g.add_color_stop_rgb(1, *rgb(c1))
    ctx.rectangle(-600, y0, W + 1200, y1 - y0)
    ctx.set_source(g)
    ctx.fill()


# ───────────── boutique d'opérateur mobile ─────────────

def boutique(ctx, t, marque="MOBI+"):
    _degrade(ctx, -400, SOL, (58, 52, 86), (78, 70, 108))
    # bandeau de marque
    rrect(ctx, 150, 120, 780, 150, 26)
    paint(ctx, (40, 34, 60), LW, shade=1)
    ecrit(ctx, marque, 540, 196, 110, (255, 214, 60), big=True)
    # présentoirs à téléphones (écrans qui changent)
    for row, y in enumerate((420, 640)):
        rrect(ctx, -60, y + 150, 1200, 26, 6)
        paint(ctx, (110, 96, 140), LW, shade=0.85)
        for i in range(7):
            x = -20 + i * 168
            rrect(ctx, x, y, 92, 152, 16)
            paint(ctx, (34, 34, 44), LW * 0.8, shade=1)
            k = (t * 0.7 + i * 0.37 + row * 0.5) % 1
            col = mix((70, 140, 230), (230, 90, 160), 0.5 + 0.5 * math.sin(2 * math.pi * k))
            rrect(ctx, x + 9, y + 12, 74, 120, 8)
            flat(ctx, col)
            ecrit(ctx, ("5G", "PROMO", "-50%", "NEW")[(i + row) % 4], x + 46, y + 72, 22, (255, 255, 255), big=True)
    # affiche promo
    rrect(ctx, 760, 900, 250, 330, 14)
    paint(ctx, (230, 70, 90), LW, shade=0.85)
    ecrit(ctx, "FORFAIT", 885, 980, 46, (255, 255, 255), big=True)
    ecrit(ctx, "XL", 885, 1080, 120, (255, 220, 70), big=True)
    ecrit(ctx, "*prix révisable", 885, 1190, 20, (255, 255, 255))
    # sol
    _degrade(ctx, SOL - 40, 2600, (96, 84, 110), (60, 52, 72))
    for i in range(-6, 16):
        ctx.move_to(540 + (i - 5) * 60, SOL - 40)
        ctx.line_to(540 + (i - 5) * 260, 2600)
        stroke(ctx, 2, (40, 34, 50), alpha=0.35)
    # projecteurs
    for x in (300, 780):
        rrect(ctx, x - 40, -10, 80, 34, 10)
        paint(ctx, (30, 28, 36), LW * 0.7, shade=1)
        cone_lumiere(ctx, x, 20, 90, 520, 1500, 0.10 + 0.02 * math.sin(t * 3 + x))


def comptoir(ctx, x, y, w=620, h=300, couleur=(240, 240, 246)):
    """Comptoir devant le vendeur (à dessiner APRÈS le vendeur)."""
    rrect(ctx, x - w / 2, y, w, h, 18)
    paint(ctx, couleur, LW, shade=0.82)
    rrect(ctx, x - w / 2 - 14, y - 22, w + 28, 36, 12)
    paint(ctx, (150, 70, 170), LW, shade=0.85)
    ecrit(ctx, "MOBI+", x, y + h / 2 + 10, 56, (150, 70, 170), big=True)


# ───────────── salon le soir ─────────────

def salon(ctx, t):
    _degrade(ctx, -400, SOL, (36, 46, 74), (52, 62, 92))
    # fenêtre : ville de nuit, lune
    rrect(ctx, 90, 280, 480, 620, 26)
    paint(ctx, (24, 30, 56), LW * 1.2, shade=1)
    ctx.save()
    rrect(ctx, 90, 280, 480, 620, 26)
    ctx.clip()
    circle(ctx, 470, 380, 46)
    flat(ctx, (250, 240, 200))
    halo(ctx, 470, 380, 140, (250, 240, 200), 0.18)
    for i, (bx, bw, bh) in enumerate([(100, 90, 300), (200, 70, 380), (280, 110, 250), (400, 80, 340), (480, 100, 280)]):
        rrect(ctx, bx, 900 - bh, bw, bh + 20, 4)
        flat(ctx, (40, 44, 78))
        for j in range(6):
            for k in range(2):
                on = (math.sin(i * 7.1 + j * 3.3 + k * 1.7 + math.floor(t * 0.8 + i) * 0.9) > 0.1)
                ctx.rectangle(bx + 14 + k * (bw / 2 - 6), 900 - bh + 22 + j * 46, bw / 2 - 26, 24)
                flat(ctx, (255, 214, 120) if on else (60, 64, 98))
    ctx.restore()
    ctx.move_to(330, 280)
    ctx.line_to(330, 900)
    ctx.move_to(90, 590)
    ctx.line_to(570, 590)
    stroke(ctx, LW * 1.4, (24, 30, 56))
    # cadre + étagère
    rrect(ctx, 720, 360, 220, 170, 10)
    paint(ctx, (200, 170, 120), LW, shade=0.85)
    rrect(ctx, 740, 380, 180, 130, 6)
    flat(ctx, (90, 150, 140))
    # lampe sur pied qui diffuse une lumière chaude
    ctx.move_to(930, SOL - 10)
    ctx.line_to(930, 760)
    stroke(ctx, 12, INK)
    poly(ctx, [(860, 760), (1000, 760), (970, 640), (890, 640)])
    paint(ctx, (250, 220, 150), LW, shade=0.9)
    halo(ctx, 930, 760, 420, (255, 200, 120), 0.22 + 0.02 * math.sin(t * 2.3))
    cone_lumiere(ctx, 930, 760, 140, 600, 800, 0.10, (255, 200, 120))
    # sol
    _degrade(ctx, SOL - 40, 2600, (90, 64, 52), (60, 42, 36))
    ellipse(ctx, 540, SOL + 120, 520, 90)
    flat(ctx, (150, 60, 70), 0.6)


def canape(ctx, x, y, w=760, couleur=(70, 96, 170)):
    """Canapé (le bas, à dessiner après le personnage assis)."""
    rrect(ctx, x - w / 2, y - 260, w, 200, 50)
    paint(ctx, dark(couleur, 0.9), LW, shade=0.85)


def canape_avant(ctx, x, y, w=760, couleur=(70, 96, 170)):
    rrect(ctx, x - w / 2 + 40, y - 120, w - 80, 120, 30)
    paint(ctx, couleur, LW, shade=0.82)
    for sx in (-1, 1):
        rrect(ctx, x + sx * (w / 2 - 50) - 55, y - 210, 110, 210, 40)
        paint(ctx, couleur, LW, shade=0.82)


# ───────────── fond sombre pour les cartes d'explication ─────────────

def fond_sombre(ctx, t, couleur=(28, 32, 44)):
    _degrade(ctx, -400, 2400, couleur, dark(couleur, 0.7))
    for i in range(-2, 14):
        x = i * 120 + (t * 14) % 120
        ctx.move_to(x, -400)
        ctx.line_to(x, 2400)
        stroke(ctx, 2, (255, 255, 255), alpha=0.035)
    for j in range(-4, 24):
        ctx.move_to(-600, j * 120)
        ctx.line_to(1700, j * 120)
        stroke(ctx, 2, (255, 255, 255), alpha=0.035)
    halo(ctx, 540, 900, 900, (90, 110, 170), 0.20)


# ───────────── objets ─────────────

def telephone(ctx, x, y, s, ecran=None, t=0.0, rot=0.0):
    """Téléphone tenu (s = 1 : 120 x 220). ecran(ctx, w, h) dessine le contenu."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    rrect(ctx, -60, -110, 120, 220, 18)
    paint(ctx, (30, 30, 38), LW, shade=1)
    rrect(ctx, -52, -98, 104, 196, 10)
    flat(ctx, (235, 240, 250))
    if ecran:
        ctx.save()
        ctx.translate(-52, -98)
        rrect(ctx, 0, 0, 104, 196, 10)
        ctx.clip()
        ecran(ctx, 104, 196)
        ctx.restore()
    ctx.restore()


def contrat(ctx, x, y, s, rot=0.0, lignes=None, tampon=None, tampon_k=0.0):
    """Feuille de contrat : lignes (texte, couleur) ; tampon = texte rouge qui claque (tampon_k 0→1)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    rrect(ctx, -170, -230, 340, 460, 10)
    paint(ctx, (250, 248, 240), LW, shade=0.92)
    ecrit(ctx, "CONTRAT", 0, -180, 40, INK, big=True)
    yy = -120
    for txt, col in (lignes or []):
        if txt:
            ecrit(ctx, txt, -140, yy, 25, col, ax=0)
        else:
            rrect(ctx, -140, yy - 6, 280, 12, 6)
            flat(ctx, (200, 200, 205))
        yy += 52
    if tampon and tampon_k > 0:
        from dessin import back
        k = back(min(1, tampon_k * 2.2))
        ctx.save()
        ctx.translate(20, 150)
        ctx.rotate(-0.18)
        ctx.scale(2.2 - 1.2 * k, 2.2 - 1.2 * k)
        rrect(ctx, -130, -46, 260, 92, 12)
        stroke(ctx, 8, (220, 40, 50), alpha=min(1, tampon_k * 3))
        ecrit(ctx, tampon, 0, 2, 62, (220, 40, 50), big=True, alpha=min(1, tampon_k * 3))
        ctx.restore()
    ctx.restore()


def etiquette(ctx, x, y, s, txt, t, couleur=(255, 214, 60), txt_col=INK):
    """Étiquette de prix accrochée par une ficelle, qui se balance."""
    a = math.sin(t * 3.1) * 0.12 * math.exp(-t * 0.4) + math.sin(t * 1.3) * 0.04
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(a)
    ctx.scale(s, s)
    ctx.move_to(0, -120)
    ctx.line_to(0, -40)
    stroke(ctx, 4)
    poly(ctx, [(-150, -40), (110, -40), (170, 30), (110, 100), (-150, 100)])
    paint(ctx, couleur, LW, shade=0.88)
    circle(ctx, 118, 30, 12)
    paint(ctx, (255, 255, 255), LW * 0.7, shade=1)
    ecrit(ctx, txt, -20, 32, 84, txt_col, big=True)
    ctx.restore()


def ampoule(ctx, x, y, s, t):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    halo(ctx, 0, 0, 200, (255, 230, 120), 0.45 + 0.1 * math.sin(t * 10))
    for i in range(8):
        a = i * math.pi / 4 + t * 0.6
        ctx.move_to(math.cos(a) * 95, math.sin(a) * 95)
        ctx.line_to(math.cos(a) * 130, math.sin(a) * 130)
        stroke(ctx, 9, (255, 214, 60))
    circle(ctx, 0, -10, 62)
    paint(ctx, (255, 236, 120), LW, shade=0.9)
    rrect(ctx, -30, 45, 60, 46, 8)
    paint(ctx, (170, 170, 180), LW, shade=0.85)
    ctx.restore()


def calendrier(ctx, x, y, s, haut, gros, t_chute=None, couleur=(220, 50, 60)):
    """Calendrier de bureau ; t_chute (0→1) fait tomber la page en tournant."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -140, -150, 280, 300, 16)
    paint(ctx, (250, 250, 250), LW, shade=0.9)
    rrect(ctx, -140, -150, 280, 80, 16)
    paint(ctx, couleur, LW, shade=0.9)
    ecrit(ctx, haut, 0, -112, 40, (255, 255, 255), big=True)
    ecrit(ctx, gros, 0, 40, 140, INK, big=True)
    ctx.restore()
