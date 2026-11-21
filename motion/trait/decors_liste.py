"""Décors de la vidéo liste « 5 remboursements » : quai de gare et TGV, bureau avec tiroir, tickets restaurant, relevé
bancaire, avion, salle à manger, enveloppes de remboursement et carton « Numéro X »."""
import math

import cairo

from dessin import INK, LW, back, circle, ease, ecrit, ellipse, flat, halo, paint, poly, rgb, rrect, stroke

SOL = 1560


def _deg(ctx, x0, y0, x1, y1, c0, c1):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, *rgb(c0))
    g.add_color_stop_rgb(1, *rgb(c1))
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.set_source(g)
    ctx.fill()


# ───────────── icônes simples (dessinées dans un carré de 100) ─────────────
def icone(ctx, nom, x, y, s=1.0, c=INK):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    if nom == "train":
        rrect(ctx, -40, -40, 80, 70, 18)
        paint(ctx, c, 5, shade=0.9)
        rrect(ctx, -28, -28, 56, 24, 6)
        flat(ctx, (255, 255, 255))
        for dx in (-20, 20):
            circle(ctx, dx, 42, 9)
            flat(ctx, INK)
    elif nom == "ticket":
        rrect(ctx, -45, -28, 90, 56, 8)
        paint(ctx, c, 5, shade=0.9)
        ecrit(ctx, "TR", 0, 0, 30, (255, 255, 255), big=True)
    elif nom == "banque":
        poly(ctx, [(-48, -14), (0, -46), (48, -14)])
        paint(ctx, c, 5, shade=0.9)
        for dx in (-30, 0, 30):
            ctx.rectangle(dx - 7, -10, 14, 44)
        flat(ctx, c)
        ctx.rectangle(-48, 34, 96, 10)
        flat(ctx, c)
    elif nom == "tel":
        rrect(ctx, -26, -46, 52, 92, 10)
        paint(ctx, c, 5, shade=0.9)
        rrect(ctx, -18, -36, 36, 64, 4)
        flat(ctx, (30, 30, 40))
    elif nom == "avion":
        poly(ctx, [(-50, 4), (40, -6), (52, 0), (40, 6), (-50, 0)])
        paint(ctx, c, 4, shade=0.9)
        poly(ctx, [(-4, 0), (18, -40), (28, -40), (14, 0)])
        paint(ctx, c, 4, shade=0.9)
        poly(ctx, [(-4, 2), (18, 40), (28, 40), (14, 2)])
        paint(ctx, c, 4, shade=0.9)
        poly(ctx, [(-46, 0), (-40, -22), (-32, -22), (-34, 0)])
        paint(ctx, c, 4, shade=0.9)
    ctx.restore()


def enveloppe(ctx, x, y, s, montant, icone_nom, couleur=(250, 246, 236), lueur=0.0, rot=0.0):
    """Enveloppe de remboursement debout (x = milieu, y = bas) : icône + montant."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    if lueur > 0:
        halo(ctx, 0, -160, 340, (255, 220, 110), 0.5 * lueur)
    rrect(ctx, -150 + 12, -320 + 16, 300, 320, 18)
    flat(ctx, (0, 0, 0), 0.25)
    rrect(ctx, -150, -320, 300, 320, 18)
    paint(ctx, couleur, LW, shade=0.88)
    poly(ctx, [(-150, -300), (0, -190), (150, -300)], close=False)
    stroke(ctx, LW * 0.8)
    icone(ctx, icone_nom, 0, -230 + 40, 0.9, (60, 110, 200))
    ecrit(ctx, montant, 0, -80, 70, INK, big=True)
    ctx.restore()


# ───────────── quai de gare + TGV ─────────────
def tgv(ctx, x, y, s, t=0.0):
    """TGV de profil, nez à droite (x = nez, y = rails)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for k in range(3):
        x0 = -460 - k * 900
        rrect(ctx, x0 - 880, -330, 900, 300, 30)
        paint(ctx, (238, 240, 246), LW, shade=0.88)
        ctx.rectangle(x0 - 880, -150, 900, 34)
        flat(ctx, (130, 40, 90))
        for w in range(6):
            rrect(ctx, x0 - 840 + w * 140, -280, 100, 80, 14)
            paint(ctx, (90, 120, 160), LW * 0.6, shade=0.9)
    poly(ctx, [(-460, -330), (-200, -320), (40, -150), (60, -60), (40, -30), (-460, -30)])
    paint(ctx, (238, 240, 246), LW, shade=0.88)
    poly(ctx, [(-300, -310), (-200, -300), (-60, -190), (-300, -190)])
    paint(ctx, (60, 80, 120), LW * 0.7, shade=0.9)
    poly(ctx, [(-460, -150), (-120, -150), (20, -110), (-460, -116)])
    flat(ctx, (130, 40, 90))
    ctx.restore()


def quai(ctx, t, train_x=None, retard=False):
    """Quai de gare le soir : verrière, panneau d'affichage, train qui arrive."""
    _deg(ctx, -600, -600, 1700, 1100, (40, 46, 80), (90, 96, 130))
    for i in range(-3, 10):
        ctx.move_to(i * 200, -200)
        ctx.line_to(i * 200 + 150, 700)
    stroke(ctx, 10, (70, 76, 110))
    # panneau d'affichage
    rrect(ctx, 520, 160, 520, 220, 12)
    paint(ctx, (20, 24, 40), LW, shade=1)
    ecrit(ctx, "LYON → PARIS", 780, 220, 40, (255, 220, 90), big=True)
    if retard:
        k = 0.6 + 0.4 * math.sin(t * 8)
        ecrit(ctx, "RETARD 45 MIN", 780, 310, 54, (255, 80, 70), big=True, alpha=k)
    else:
        ecrit(ctx, "21:12  À L'HEURE", 780, 310, 44, (120, 230, 140), big=True)
    _deg(ctx, -600, 1100, 1700, 1260, (60, 60, 70), (40, 40, 48))
    for i in range(-4, 16):
        ctx.rectangle(i * 120 + (-t * 0) % 120, 1180, 60, 14)
    flat(ctx, (150, 140, 120))
    if train_x is not None:
        tgv(ctx, train_x, 1230, 0.9, t)
    _deg(ctx, -600, 1230, 1700, 2600, (170, 170, 176), (130, 130, 136))
    ctx.rectangle(-600, 1240, 2300, 20)
    flat(ctx, (250, 220, 60))


# ───────────── bureau + tickets ─────────────
def ticket_resto(ctx, x, y, s, rot=0.0, perime=False):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    rrect(ctx, -120, -60, 240, 120, 8)
    paint(ctx, (255, 236, 200), LW * 0.7, shade=0.95)
    ecrit(ctx, "TITRE-RESTAURANT", 0, -28, 22, (200, 90, 40), big=True)
    ecrit(ctx, "9,00 €", 0, 16, 40, INK, big=True)
    ecrit(ctx, "valable jusqu'au 31/12/2025", 0, 46, 14, (120, 110, 100))
    if perime:
        ctx.save()
        ctx.rotate(-0.25)
        rrect(ctx, -100, -26, 200, 52, 8)
        stroke(ctx, 5, (210, 40, 50))
        ecrit(ctx, "PÉRIMÉ", 0, 0, 34, (210, 40, 50), big=True)
        ctx.restore()
    ctx.restore()


def bureau(ctx, t, tiroir=0.0):
    """Open space : mur, fenêtre, bureau avec tiroir qui s'ouvre (tiroir 0 → 1)."""
    _deg(ctx, -600, -600, 1700, SOL, (220, 226, 232), (196, 204, 214))
    rrect(ctx, 560, 200, 420, 460, 10)
    paint(ctx, (170, 210, 240), LW, shade=0.95)
    ctx.move_to(770, 200)
    ctx.line_to(770, 660)
    stroke(ctx, LW)
    _deg(ctx, -600, SOL - 40, 1700, 2600, (150, 150, 160), (120, 120, 130))
    # bureau
    rrect(ctx, -40, 1180, 1160, 50, 10)
    paint(ctx, (200, 160, 110), LW, shade=0.85)
    rrect(ctx, 640, 1230, 420, 360, 8)
    paint(ctx, (180, 140, 96), LW, shade=0.85)
    dx = 160 * ease(tiroir)
    rrect(ctx, 660 - dx * 0.2, 1270 + dx * 0.3, 380, 130, 8)
    paint(ctx, (196, 156, 110), LW, shade=0.85)
    rrect(ctx, 800 - dx * 0.2, 1320 + dx * 0.3, 100, 20, 8)
    flat(ctx, INK)
    # écran
    rrect(ctx, 80, 900, 420, 280, 14)
    paint(ctx, (40, 44, 56), LW, shade=1)
    rrect(ctx, 100, 920, 380, 230, 8)
    flat(ctx, (120, 180, 230))


# ───────────── relevé bancaire ─────────────
def releve(ctx, x, y, s, n, t0, t, total=None):
    """Relevé de compte : n lignes « COMMISSION D'INTERVENTION 8,00 € » qui apparaissent depuis t0."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -400, -560, 800, 1120, 10)
    paint(ctx, (252, 252, 248), LW, shade=0.96)
    ecrit(ctx, "RELEVÉ DE COMPTE", 0, -500, 44, (40, 80, 160), big=True)
    ecrit(ctx, "Novembre", 0, -450, 28, (120, 120, 130))
    k = int(max(0, min(n, (t - t0) * 9))) if t >= t0 else 0
    for i in range(k):
        yy = -390 + i * 52
        ecrit(ctx, "COMMISSION D'INTERVENTION", -360, yy, 26, INK, ax=0)
        ecrit(ctx, "- 8,00 €", 360, yy, 26, (210, 40, 50), ax=1, big=True)
    if total and k >= n:
        ctx.move_to(-360, 420)
        ctx.line_to(360, 420)
        stroke(ctx, 4, (180, 180, 190))
        ecrit(ctx, "TOTAL FRAIS", -360, 480, 40, INK, ax=0, big=True)
        ecrit(ctx, total, 360, 480, 56, (210, 40, 50), ax=1, big=True)
    ctx.restore()


# ───────────── salle à manger ─────────────
def salle_a_manger(ctx, t):
    _deg(ctx, -600, -600, 1700, SOL, (240, 222, 196), (222, 200, 170))
    rrect(ctx, 60, 220, 360, 420, 10)
    paint(ctx, (150, 200, 230), LW, shade=0.95)
    rrect(ctx, 620, 240, 300, 220, 8)
    paint(ctx, (200, 150, 110), LW, shade=0.9)
    ellipse(ctx, 770, 350, 90, 60)
    flat(ctx, (120, 170, 110))
    halo(ctx, 540, 120, 500, (255, 230, 170), 0.25)
    _deg(ctx, -600, SOL - 40, 1700, 2600, (170, 120, 80), (130, 90, 60))


def table(ctx, x, y, w=1100):
    """Table du déjeuner, à dessiner devant les personnages assis."""
    rrect(ctx, x - w / 2, y, w, 60, 14)
    paint(ctx, (250, 250, 246), LW, shade=0.92)
    ctx.rectangle(x - w / 2 + 20, y + 60, w - 40, 300)
    flat(ctx, (240, 236, 228))
    for dx in (-300, 0, 300):
        ellipse(ctx, x + dx, y + 10, 90, 26)
        paint(ctx, (255, 255, 255), 4, shade=0.95)
        ellipse(ctx, x + dx, y + 6, 54, 14)
        flat(ctx, (220, 150, 90))


def avion(ctx, x, y, s, rot=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    poly(ctx, [(-300, -20), (260, -40), (320, -10), (260, 20), (-300, 10)])
    paint(ctx, (248, 248, 252), LW, shade=0.88)
    poly(ctx, [(-40, -10), (90, -200), (140, -200), (60, -10)])
    paint(ctx, (230, 232, 240), LW, shade=0.88)
    poly(ctx, [(-280, -10), (-250, -130), (-200, -130), (-220, -10)])
    paint(ctx, (60, 110, 200), LW, shade=0.88)
    for i in range(8):
        circle(ctx, -180 + i * 55, -18, 9)
        flat(ctx, (90, 120, 160))
    ctx.restore()


# ───────────── carton « Numéro X » ─────────────
def carte_numero(ctx, t, lt, n, titre, montant, couleur=(255, 210, 40)):
    """Plein écran sombre : pastilles 5 → 1, gros chiffre, titre, montant max."""
    _deg(ctx, -600, -600, 1700, 2600, (20, 22, 34), (34, 36, 54))
    rayons(ctx, 540, 840, t, couleur)
    halo(ctx, 540, 820, 600, couleur, 0.12 + 0.05 * math.sin(t * 4))
    for i, k in enumerate((5, 4, 3, 2, 1)):
        x = 380 + i * 80
        circle(ctx, x, 520, 26)
        if k == n:
            flat(ctx, couleur)
            ecrit(ctx, str(k), x, 520, 30, INK, big=True)
        elif k > n:
            flat(ctx, (90, 90, 110))
            ecrit(ctx, "✓", x, 520, 28, (255, 255, 255), big=True)
        else:
            stroke(ctx, 4, (120, 120, 140))
    ecrit(ctx, "NUMÉRO", 540, 640, 46, (200, 200, 214), big=True, alpha=min(1, lt / 0.2))
    ecrit(ctx, str(n), 540, 840 + 14 * math.sin(t * 3), 300, couleur, big=True,
          scale=back(lt / 0.35) * (1 + 0.04 * math.sin(t * 5)))
    if lt > 0.25:
        ecrit(ctx, titre, 540, 1050, 60, (255, 255, 255), big=True, alpha=min(1, (lt - 0.25) / 0.2))
    if lt > 0.5 and montant:
        rrect(ctx, 340, 1110, 400, 80, 40)
        flat(ctx, couleur)
        ecrit(ctx, montant, 540, 1150, 42, INK, big=True)


def rayons(ctx, x, y, t, couleur, n=16, alpha=0.10):
    """Rayons qui tournent lentement (fond des cartons)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(t * 0.35)
    for i in range(n):
        a0 = i * 2 * math.pi / n
        ctx.move_to(0, 0)
        ctx.arc(0, 0, 1600, a0, a0 + math.pi / n)
        ctx.close_path()
    ctx.set_source_rgba(*rgb(couleur), alpha)
    ctx.fill()
    ctx.restore()


def pieces_flottantes(ctx, t, n=14, couleur=(230, 190, 60)):
    """Pièces qui montent doucement en tournant (fond des cartes « règle »)."""
    for i in range(n):
        k = (t * 0.12 + i / n) % 1
        x = (i * 173) % 1180 - 50 + 30 * math.sin(t + i)
        y = 2000 - k * 2400
        ellipse(ctx, x, y, 30, 30 * abs(math.cos(t * 2 + i)) + 3)
        paint(ctx, couleur, 4, shade=0.85, alpha=0.5)
