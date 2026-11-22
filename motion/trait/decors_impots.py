"""Décors de la vidéo Ficelle n° 1 : accueil du centre des impôts (guichet, classeurs, horloge), calendrier compte à
rebours dont la page s'arrache, salle de pause avec machine à café, avis d'impôt, tableau du barème, modèle de
réclamation, certificats de scolarité."""
import math

import cairo

from dessin import INK, LW, back, circle, ease, ecrit, flat, halo, paint, poly, rgb, rrect, stroke

SOL = 1560


def _deg(ctx, x0, y0, x1, y1, c0, c1):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, *rgb(c0))
    g.add_color_stop_rgb(1, *rgb(c1))
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.set_source(g)
    ctx.fill()


def horloge(ctx, x, y, r, t):
    circle(ctx, x, y, r)
    paint(ctx, (250, 250, 250), LW, shade=0.95)
    for a, l, w in ((t * 0.5, r * 0.55, 8), (t * 6, r * 0.8, 5)):
        ctx.move_to(x, y)
        ctx.line_to(x + l * math.sin(a), y - l * math.cos(a))
        stroke(ctx, w)


def accueil(ctx, t, rideau=0.0):
    """Le fond derrière le guichet : mur bleu-gris, étagères de classeurs colorés, horloge, rideau métallique."""
    _deg(ctx, -600, -600, 1700, SOL, (150, 166, 186), (120, 136, 158))
    for r in range(3):
        y = 260 + r * 230
        ctx.rectangle(-300, y + 170, 1700, 18)
        flat(ctx, (90, 70, 60))
        for i in range(-6, 26):
            c = [(220, 70, 60), (240, 180, 40), (60, 130, 210), (70, 170, 110), (160, 90, 180)][(i * 3 + r) % 5]
            rrect(ctx, -300 + i * 62, y + 20, 52, 150, 5)
            paint(ctx, c, 3, shade=0.85)
    horloge(ctx, 880, 150, 70, t)
    if rideau > 0:
        h = 1000 * ease(min(1.0, rideau))
        ctx.rectangle(-300, 0, 1700, h)
        flat(ctx, (170, 174, 182))
        for k in range(int(h // 40)):
            ctx.move_to(-300, k * 40)
            ctx.line_to(1400, k * 40)
        stroke(ctx, 3, (130, 134, 142))
    _deg(ctx, -600, SOL - 40, 1700, 2600, (110, 100, 96), (80, 72, 70))


def guichet(ctx, x, y, w=760):
    """Comptoir du guichet (à dessiner APRÈS l'agent) avec la vitre et la plaque."""
    rrect(ctx, x - w / 2, y, w, 360, 12)
    paint(ctx, (60, 76, 110), LW, shade=0.85)
    rrect(ctx, x - w / 2 - 20, y - 26, w + 40, 40, 10)
    paint(ctx, (200, 206, 216), LW, shade=0.9)
    rrect(ctx, x - 200, y + 230, 400, 70, 8)
    paint(ctx, (240, 240, 244), 4, shade=0.95)
    ecrit(ctx, "ACCUEIL · IMPÔTS", x, y + 265, 34, INK, big=True)
    ctx.rectangle(x - w / 2, y - 560, w, 534)
    flat(ctx, (200, 230, 250), 0.18)
    ctx.move_to(x - w / 2 + 40, y - 520)
    ctx.line_to(x - w / 2 + 160, y - 380)
    stroke(ctx, 6, (255, 255, 255), alpha=0.35)


def calendrier(ctx, x, y, s, jour, t, t_arrache=None):
    """Calendrier « AVANT LE 31/12 » ; t_arrache : la page du dessus (jour + 1) s'envole en tournant."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for k in range(4):
        rrect(ctx, -150 + k * 3, -160 + k * 6, 300, 320, 14)
        paint(ctx, (236, 236, 236), 4, shade=0.95)

    def page(j):
        rrect(ctx, -150, -160, 300, 320, 14)
        paint(ctx, (252, 252, 252), LW, shade=0.92)
        rrect(ctx, -150, -160, 300, 80, 14)
        paint(ctx, (220, 50, 60), LW, shade=0.9)
        ecrit(ctx, "AVANT LE 31/12", 0, -120, 34, (255, 255, 255), big=True)
        ecrit(ctx, f"J-{j}", 0, 30, 130, INK, big=True)
        ecrit(ctx, "pour réclamer", 0, 120, 26, (120, 120, 130))
    page(jour)
    if t_arrache is not None and t < t_arrache + 0.6:
        k = max(0.0, (t - t_arrache) / 0.6)
        ctx.save()
        ctx.translate(-260 * k, -380 * k + 900 * k * k)
        ctx.rotate(-1.4 * k)
        page(jour + 1)
        ctx.restore()
    ctx.restore()


def salle_pause(ctx, t):
    """Salle de pause du boulot : machine à café qui fume, frigo, fenêtre."""
    _deg(ctx, -600, -600, 1700, SOL, (240, 226, 200), (222, 206, 178))
    rrect(ctx, 620, 240, 360, 360, 10)
    paint(ctx, (160, 210, 240), LW, shade=0.95)
    rrect(ctx, 80, 560, 300, 520, 18)
    paint(ctx, (60, 60, 70), LW, shade=0.9)
    rrect(ctx, 120, 620, 220, 120, 10)
    flat(ctx, (120, 220, 150))
    ecrit(ctx, "CAFÉ", 230, 680, 40, INK, big=True)
    rrect(ctx, 170, 880, 120, 140, 8)
    flat(ctx, (30, 30, 34))
    for i in range(3):
        k = (t * 0.6 + i / 3) % 1
        circle(ctx, 230 + 20 * math.sin(t * 2 + i), 860 - 160 * k, 16 + 14 * k)
        flat(ctx, (255, 255, 255), 0.5 * (1 - k))
    _deg(ctx, -600, 1080, 1700, 1140, (180, 140, 100), (150, 110, 80))
    _deg(ctx, -600, SOL - 40, 1700, 2600, (170, 150, 130), (130, 110, 96))


def avis(ctx, x, y, s, annee, ligne, valeur=None, rot=0.0, coche=0.0):
    """Avis d'impôt : en-tête, lignes grises, la ligne « Réduction scolarité » vide (ou remplie en vert)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    rrect(ctx, -260, -330, 520, 660, 8)
    paint(ctx, (252, 252, 246), LW * 0.8, shade=0.96)
    ecrit(ctx, f"AVIS D'IMPÔT {annee}", 0, -280, 36, (40, 80, 160), big=True)
    ecrit(ctx, ligne, 0, -235, 24, (120, 120, 130))
    for k in range(4):
        rrect(ctx, -220, -170 + k * 50, 440, 14, 7)
        flat(ctx, (206, 206, 212))
    rrect(ctx, -230, 60, 460, 70, 8)
    flat(ctx, (60, 190, 110) if valeur else (240, 220, 220), 0.9 if valeur else 1)
    ecrit(ctx, "Réduction scolarité", -210, 95, 28, INK, ax=0, big=True)
    ecrit(ctx, valeur or "0 €", 210, 95, 32, INK if valeur else (210, 40, 50), ax=1, big=True)
    for k in range(3):
        rrect(ctx, -220, 170 + k * 50, 440, 14, 7)
        flat(ctx, (206, 206, 212))
    ctx.restore()


def tableau(ctx, x, y, s, n, t):
    """Tableau noir du barème : n lignes visibles (collège, lycée, après le bac)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -330, -230, 660, 460, 14)
    paint(ctx, (120, 80, 50), LW, shade=0.9)
    rrect(ctx, -300, -200, 600, 400, 8)
    flat(ctx, (40, 70, 55))
    for i, (a, b) in enumerate((("Collège", "61 €"), ("Lycée", "153 €"), ("Après le bac", "183 €"))[:n]):
        ecrit(ctx, a, -260, -120 + i * 120, 52, (250, 250, 240), ax=0)
        ecrit(ctx, b, 260, -120 + i * 120, 58, (255, 220, 90), ax=1, big=True)
    ctx.restore()


def reclamation(ctx, x, y, s, n, t):
    """Modèle de message de réclamation, lisible (à garder) : n points visibles."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -400, -470, 800, 940, 12)
    paint(ctx, (252, 252, 246), LW, shade=0.96)
    ecrit(ctx, "RÉCLAMATION", -350, -400, 54, INK, big=True, ax=0)
    ecrit(ctx, "Espace particulier > Messagerie > Écrire", -350, -340, 26, (120, 120, 130), ax=0)
    items = ["J'ai oublié les frais de\nscolarité de mon enfant.", "Je demande la réduction\n(art. 199 quater F du CGI).",
             "Un message par année,\ncertificat de scolarité joint."]
    for i, txt in enumerate(items[:n]):
        yy = -230 + i * 210
        circle(ctx, -320, yy + 20, 30)
        flat(ctx, (220, 50, 60))
        ecrit(ctx, str(i + 1), -320, yy + 20, 36, (255, 255, 255), big=True)
        for k, l in enumerate(txt.split("\n")):
            ecrit(ctx, l, -260, yy + k * 48, 38, INK, ax=0)
    ctx.restore()


def certificats(ctx, x, y, s, n, t):
    """Certificats de scolarité en éventail (n de 0 à 3)."""
    for i in range(n):
        ctx.save()
        ctx.translate(x + (i - 1) * 170 * s, y)
        ctx.rotate((i - 1) * 0.18)
        ctx.scale(s, s)
        rrect(ctx, -170, -230, 340, 460, 8)
        paint(ctx, (250, 250, 240), LW * 0.8, shade=0.95)
        ecrit(ctx, "CERTIFICAT", 0, -180, 34, INK, big=True)
        ecrit(ctx, "DE SCOLARITÉ", 0, -140, 30, INK, big=True)
        ecrit(ctx, ["2023-2024", "2024-2025", "2025-2026"][i], 0, -60, 34, (40, 80, 160), big=True)
        ecrit(ctx, ["Collège", "Seconde", "Première"][i], 0, -10, 30, (90, 90, 100))
        circle(ctx, 90, 140, 50)
        stroke(ctx, 5, (40, 80, 160))
        ctx.restore()
