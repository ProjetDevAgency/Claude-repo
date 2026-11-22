"""Décors du supermarché : rayons, caisse avec tapis et tiroir, vestiaire et casiers, fiche de paie, ticket de clôture."""
import math

import cairo

from dessin import INK, LW, circle, ease, ecrit, flat, halo, paint, poly, rgb, rrect, stroke

SOL = 1560


def _deg(ctx, x0, y0, x1, y1, c0, c1):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, *rgb(c0))
    g.add_color_stop_rgb(1, *rgb(c1))
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.set_source(g)
    ctx.fill()


COULEURS = [(230, 70, 60), (250, 190, 40), (60, 150, 220), (80, 180, 110), (240, 130, 50), (170, 90, 190)]


def magasin(ctx, t):
    """Fond du supermarché : néons, rayons pleins de produits colorés, pancarte « PROMO »."""
    _deg(ctx, -600, -600, 1700, SOL, (236, 238, 242), (214, 218, 226))
    for i in range(-2, 7):
        x = -200 + i * 240
        rrect(ctx, x - 40, 60, 260, 26, 12)
        flat(ctx, (250, 252, 255), 0.9 + 0.1 * math.sin(t * 7 + i))
        halo(ctx, x + 90, 120, 200, (255, 255, 255), 0.15)
    for r in range(4):
        y = 300 + r * 200
        ctx.rectangle(-600, y + 150, 2300, 16)
        flat(ctx, (150, 156, 170))
        for i in range(-12, 30):
            c = COULEURS[(i * 7 + r * 3) % 6]
            h = 90 + (i * 13 + r * 5) % 50
            rrect(ctx, i * 70 + 4, y + 150 - h, 58, h, 6)
            paint(ctx, c, 3, shade=0.85)
    ctx.save()
    ctx.translate(850, 150)
    ctx.rotate(0.12 * math.sin(t * 2.2))
    rrect(ctx, -150, 0, 300, 110, 12)
    paint(ctx, (230, 40, 50), LW, shade=0.9)
    ecrit(ctx, "PROMO", 0, 55, 64, (255, 255, 255), big=True)
    ctx.restore()
    passants(ctx, t)
    _deg(ctx, -600, SOL - 40, 1700, 2600, (200, 200, 206), (170, 170, 178))
    for i in range(-6, 14):
        ctx.move_to(i * 160, SOL - 40)
        ctx.line_to(i * 220 - 400, 2600)
    stroke(ctx, 3, (150, 150, 160), alpha=0.4)


def caisse(ctx, x, y, s, numero, tiroir=0.0, t=0.0, allume=True):
    """Poste de caisse (x = milieu, y = sol) : tapis, écran, tiroir-caisse qui sort (0 → 1), numéro lumineux."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -420, -420, 840, 420, 20)
    paint(ctx, (60, 70, 96), LW, shade=0.85)
    rrect(ctx, -440, -460, 600, 60, 14)
    paint(ctx, (40, 40, 48), LW, shade=1)
    for i in range(8):
        ctx.move_to(-430 + ((i * 80 + t * 120) % 580), -455)
        ctx.line_to(-430 + ((i * 80 + t * 120) % 580), -405)
    stroke(ctx, 4, (90, 90, 100))
    # écran
    ctx.move_to(260, -460)
    ctx.line_to(260, -620)
    stroke(ctx, 14, (80, 80, 90))
    rrect(ctx, 170, -760, 200, 150, 14)
    paint(ctx, (30, 34, 44), LW * 0.8, shade=1)
    rrect(ctx, 185, -745, 170, 120, 8)
    flat(ctx, (90, 200, 140) if allume else (40, 50, 60))
    # tiroir-caisse
    d = 220 * ease(min(1.0, tiroir))
    rrect(ctx, 120, -360 + d * 0.15, 260, 90 + d * 0.4, 10)
    paint(ctx, (180, 184, 196), LW * 0.8, shade=0.85)
    # numéro de caisse
    ctx.move_to(-300, -460)
    ctx.line_to(-300, -900)
    stroke(ctx, 10, (120, 120, 130))
    circle(ctx, -300, -950, 70)
    paint(ctx, (250, 200, 40), LW, shade=0.9)
    ecrit(ctx, str(numero), -300, -950, 80, INK, big=True)
    ctx.restore()


def casiers(ctx, t):
    """Vestiaire du personnel : rangée de casiers métalliques, banc, néon."""
    _deg(ctx, -600, -600, 1700, SOL, (200, 206, 214), (176, 184, 196))
    for i in range(-3, 9):
        x = -200 + i * 190
        rrect(ctx, x, 200, 180, 1200, 8)
        paint(ctx, (120, 150, 190), LW, shade=0.85)
        for k in range(3):
            rrect(ctx, x + 40, 260 + k * 22, 100, 8, 4)
            flat(ctx, (80, 100, 130))
        rrect(ctx, x + 140, 760, 18, 70, 6)
        flat(ctx, (60, 60, 70))
        ecrit(ctx, str(12 + i), x + 90, 360, 40, (240, 240, 246), big=True)
    rrect(ctx, -200, 1420, 1500, 50, 10)
    paint(ctx, (170, 120, 80), LW, shade=0.85)
    _deg(ctx, -600, SOL - 40, 1700, 2600, (150, 150, 160), (120, 120, 130))
    # faisceau de lumière qui balaie le vestiaire (néon qui grésille)
    x = 540 + 700 * math.sin(t * 0.9)
    poly(ctx, [(x - 60, -200), (x + 60, -200), (x + 420, 2200), (x - 420, 2200)])
    flat(ctx, (255, 250, 220), 0.16 + 0.05 * math.sin(t * 23))


def fiche_paie(ctx, x, y, s, rouge=1.0, rot=0.0, plus=False):
    """Fiche de paie : lignes grises, la ligne « ERREUR DE CAISSE −60,00 » surlignée en rouge (ou « +60,00 » en vert)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    rrect(ctx, -300, -420, 600, 840, 10)
    paint(ctx, (252, 252, 248), LW, shade=0.96)
    ecrit(ctx, "BULLETIN DE PAIE", 0, -360, 42, (40, 80, 160), big=True)
    ecrit(ctx, "Super Marché du Centre · Kévin", 0, -310, 24, (120, 120, 130))
    for i, (a, b) in enumerate((("Salaire de base", "1 398,70"), ("Heures sup.", "52,40"), ("Prime de panier", "24,00"))):
        ecrit(ctx, a, -260, -220 + i * 70, 30, INK, ax=0)
        ecrit(ctx, b, 260, -220 + i * 70, 30, INK, ax=1)
    yy = -10
    if rouge > 0:
        coul = (60, 190, 110) if plus else (230, 50, 60)
        rrect(ctx, -280, yy - 40, 560 * min(1.0, rouge), 80, 10)
        flat(ctx, coul, 0.85)
    ecrit(ctx, "Remboursement retenue" if plus else "ERREUR DE CAISSE", -260, yy, 32, INK, ax=0, big=True)
    ecrit(ctx, "+ 60,00" if plus else "− 60,00", 260, yy, 36, INK, ax=1, big=True)
    for k in range(4):
        rrect(ctx, -260, 90 + k * 60, 520, 14, 7)
        flat(ctx, (206, 206, 212))
    ecrit(ctx, "NET À PAYER", -260, 360, 34, INK, ax=0, big=True)
    ecrit(ctx, "1 375,10 €" if not plus else "1 495,10 €", 260, 360, 38, INK, ax=1, big=True)
    ctx.restore()


def ticket_cloture(ctx, x, y, s, rot=0.0, entoure=0.0):
    """Ticket de clôture de caisse : « CAISSE 4 », « ÉCART −60,00 », le 4 entouré au feutre (entoure 0 → 1)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    poly(ctx, [(-170, -320), (170, -320), (170, 300), (150, 320), (130, 300), (110, 320), (90, 300), (70, 320),
               (50, 300), (30, 320), (10, 300), (-10, 320), (-30, 300), (-50, 320), (-70, 300), (-90, 320),
               (-110, 300), (-130, 320), (-150, 300), (-170, 320)])
    paint(ctx, (252, 251, 246), 5, shade=0.97)
    ecrit(ctx, "CLÔTURE", 0, -270, 36, INK, big=True)
    ecrit(ctx, "vendredi 20:58", 0, -225, 22, (120, 120, 130))
    ecrit(ctx, "CAISSE 4", 0, -140, 52, INK, big=True)
    ecrit(ctx, "Opér. : JADE", 0, -80, 26, (90, 90, 100))
    for k in range(3):
        rrect(ctx, -130, -20 + k * 40, 260, 10, 5)
        flat(ctx, (206, 206, 212))
    ecrit(ctx, "ÉCART", -140, 170, 34, INK, ax=0, big=True)
    ecrit(ctx, "−60,00", 140, 170, 34, (210, 40, 50), ax=1, big=True)
    if entoure > 0:
        ctx.save()
        ctx.translate(95, -140)
        ctx.scale(1.0, 0.6)
        ctx.arc(0, 0, 70, -1.2, -1.2 + 6.6 * min(1.0, entoure))
        ctx.restore()
        stroke(ctx, 8, (210, 40, 50))
    ctx.restore()


def passants(ctx, t):
    """Clients qui traversent le fond du magasin avec leur chariot (silhouettes)."""
    for i, (v, y, c) in enumerate(((140, 1180, (90, 110, 160)), (-110, 1230, (170, 100, 90)), (190, 1200, (90, 150, 110)))):
        x = ((t * v + i * 700) % 2200) - 500
        ctx.save()
        ctx.translate(x, y)
        sgn = 1 if v > 0 else -1
        circle(ctx, 0, -330, 46)
        flat(ctx, (60, 60, 70), 0.55)
        rrect(ctx, -55, -280, 110, 230, 40)
        flat(ctx, c, 0.6)
        for k in (-1, 1):
            ctx.move_to(k * 25, -60)
            ctx.line_to(k * 25 + 30 * math.sin(t * 7 + i + k), 40)
        stroke(ctx, 16, (60, 60, 70), alpha=0.55)
        rrect(ctx, sgn * 90 - 80, -150, 160, 120, 10)
        stroke(ctx, 8, (150, 156, 170), alpha=0.8)
        for k in (-1, 1):
            circle(ctx, sgn * 90 + k * 55, -15, 16)
            flat(ctx, (60, 60, 70), 0.7)
        ctx.restore()
