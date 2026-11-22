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
    """Fond derrière le guichet, calme et profond (corrigé le 22 nov. d'après La Ficelle) : mur gris-bleu, cloison vitrée,
    petite étagère de 5 classeurs, horloge, casier à courrier, lampe et son faisceau, rideau métallique qui descend."""
    _deg(ctx, -600, -600, 1700, SOL, (176, 186, 200), (150, 160, 176))
    # cloison vitrée du bureau du fond
    rrect(ctx, 120, 330, 840, 700, 8)
    paint(ctx, (120, 136, 156), LW, shade=0.95)
    rrect(ctx, 150, 360, 780, 640, 6)
    flat(ctx, (96, 112, 134))
    for k in range(2):
        ctx.move_to(220 + k * 160, 380)
        ctx.line_to(360 + k * 160, 560)
    stroke(ctx, 8, (255, 255, 255), alpha=0.22)
    # petite étagère : 5 classeurs
    ctx.rectangle(200, 610, 300, 16)
    flat(ctx, (90, 72, 60))
    for i, c in enumerate(((220, 70, 60), (240, 180, 40), (60, 130, 210), (70, 170, 110), (160, 90, 180))):
        rrect(ctx, 212 + i * 56, 470, 46, 140, 5)
        paint(ctx, c, 3, shade=0.85)
    # casier à courrier
    rrect(ctx, 760, 420, 170, 220, 6)
    paint(ctx, (200, 196, 186), LW * 0.8, shade=0.9)
    ecrit(ctx, "COURRIER", 845, 445, 22, INK, big=True)
    for r in range(3):
        for c in range(2):
            rrect(ctx, 775 + c * 75, 470 + r * 55, 65, 45, 4)
            stroke(ctx, 4, (120, 116, 110))
    # horloge et lampe avec son faisceau
    horloge(ctx, 540, 190, 62, t)
    poly(ctx, [(500, -40), (580, -40), (600, 30), (480, 30)])
    paint(ctx, (70, 74, 86), LW * 0.8, shade=1)
    poly(ctx, [(490, 30), (590, 30), (760, 1100), (320, 1100)])
    flat(ctx, (255, 250, 230), 0.10)
    # écran « numéro appelé », affiche, plante
    rrect(ctx, -180, 380, 230, 150, 10)
    paint(ctx, (30, 34, 44), LW * 0.8, shade=1)
    ecrit(ctx, "N°", -120, 425, 30, (255, 120, 80), big=True)
    ecrit(ctx, str(47 + int(t // 9) % 3), -40, 465, 70, (255, 120, 80), big=True)
    rrect(ctx, 1000, 380, 220, 300, 6)
    paint(ctx, (250, 246, 236), LW * 0.8, shade=0.95)
    ecrit(ctx, "IMPÔT 2026", 1110, 420, 28, (200, 40, 50), big=True)
    for k in range(5):
        rrect(ctx, 1025, 460 + k * 38, 170, 12, 6)
        flat(ctx, (200, 200, 206))
    rrect(ctx, 1040, 1180, 120, 140, 14)
    paint(ctx, (180, 110, 70), LW * 0.8, shade=0.85)
    for k in range(6):
        a = -2.4 + k * 0.33
        ctx.save()
        ctx.translate(1100, 1180)
        ctx.rotate(a + 1.57)
        poly(ctx, [(0, 0), (30, -170), (0, -250), (-30, -170)])
        paint(ctx, (70, 150, 90), 4, shade=0.85)
        ctx.restore()
    _deg(ctx, -600, SOL - 40, 1700, 2600, (120, 116, 112), (92, 88, 86))


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


def page_volante(ctx, x, y, s, jour, k):
    """Page arrachée qui vole VERS la caméra, devant les personnages (k 0 → 1) : à dessiner en DERNIER."""
    if not 0 <= k < 1:
        return
    ctx.save()
    ctx.translate(x - 420 * k, y - 260 * k + 520 * k * k)
    ctx.rotate(-0.4 - 1.6 * k)
    sc = s * (1 + 2.2 * k)
    ctx.scale(sc, sc)
    rrect(ctx, -150, -160, 300, 320, 14)
    paint(ctx, (252, 252, 252), LW, shade=0.92)
    rrect(ctx, -150, -160, 300, 80, 14)
    paint(ctx, (220, 50, 60), LW, shade=0.9)
    ecrit(ctx, "AVANT LE 31/12", 0, -120, 34, (255, 255, 255), big=True)
    ecrit(ctx, f"J-{jour}", 0, 30, 130, INK, big=True)
    ctx.restore()


def plaque(ctx, x, y, s, txt):
    """Plaque de prix posée sur le comptoir (présentoir jaune)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    poly(ctx, [(-150, 0), (150, 0), (120, -70), (-120, -70)])
    paint(ctx, (230, 180, 60), LW, shade=0.85)
    rrect(ctx, -110, -62, 220, 54, 8)
    paint(ctx, (255, 220, 60), 4, shade=0.95)
    ecrit(ctx, txt, 0, -35, 44, INK, big=True)
    ctx.restore()


def rideau_guichet(ctx, x, w, y_haut, y_bas, k):
    """Rideau métallique du guichet, qui descend DEVANT l'agent (à dessiner après lui, avant le comptoir)."""
    if k <= 0:
        return
    h = (y_bas - y_haut) * ease(min(1.0, k))
    rrect(ctx, x - w / 2 - 14, y_haut - 40, w + 28, 46, 8)
    paint(ctx, (110, 114, 124), LW * 0.8, shade=1)
    ctx.rectangle(x - w / 2, y_haut, w, h)
    flat(ctx, (186, 190, 198))
    for i in range(int(h // 34)):
        ctx.move_to(x - w / 2, y_haut + i * 34)
        ctx.line_to(x + w / 2, y_haut + i * 34)
    stroke(ctx, 3, (146, 150, 158))
    rrect(ctx, x - w / 2, y_haut + h - 22, w, 22, 4)
    paint(ctx, (150, 154, 164), 4, shade=0.9)
    rrect(ctx, x - 40, y_haut + h - 18, 80, 14, 6)
    flat(ctx, (70, 70, 80))


def accessoires_comptoir(ctx, t):
    """Sur le comptoir : présentoir à dépliants, stylo à chaînette, tampon."""
    rrect(ctx, 920, 1200, 120, 110, 6)
    paint(ctx, (90, 100, 120), 4, shade=0.9)
    for i, c in enumerate(((240, 200, 80), (120, 180, 230), (240, 140, 120))):
        rrect(ctx, 932 + i * 34, 1170 - i * 6, 30, 90, 3)
        paint(ctx, c, 3, shade=0.9)
    ctx.move_to(260, 1302)
    ctx.curve_to(280, 1270, 320, 1290, 340, 1262)
    stroke(ctx, 3, (120, 120, 130))
    poly(ctx, [(330, 1270), (420, 1236), (426, 1248), (336, 1282)])
    paint(ctx, (40, 60, 120), 3, shade=0.9)
    rrect(ctx, 560, 1268, 70, 34, 6)
    paint(ctx, (200, 50, 60), 3, shade=0.9)
    rrect(ctx, 582, 1240, 26, 30, 4)
    paint(ctx, (80, 60, 50), 3, shade=0.9)


def poteau_file(ctx, x, y, s, t):
    """Poteau de file d'attente avec corde rouge (premier plan, à dessiner en dernier)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ellipse = None
    rrect(ctx, -60, -20, 120, 30, 12)
    paint(ctx, (150, 150, 160), LW, shade=0.85)
    rrect(ctx, -16, -560, 32, 545, 10)
    paint(ctx, (190, 190, 200), LW, shade=0.85)
    circle(ctx, 0, -575, 26)
    paint(ctx, (210, 210, 220), LW, shade=0.85)
    ctx.move_to(-10, -520)
    ctx.curve_to(-200, -380 + 6 * math.sin(t * 2), -420, -380, -620, -520)
    stroke(ctx, 26, INK)
    ctx.move_to(-10, -520)
    ctx.curve_to(-200, -380 + 6 * math.sin(t * 2), -420, -380, -620, -520)
    stroke(ctx, 16, (200, 40, 50))
    ctx.restore()
