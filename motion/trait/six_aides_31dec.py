"""« 6 aides avant le 31 décembre » — vidéo complète, moteur trait, règles des 7 points du 20 nov.
Script : scripts/modele/40_six_aides_31_decembre.dial (chiffres en clair dans LIGNES pour les sous-titres).
Chaque décor est dessiné ici, pour cette vidéo (règle du client : pas de décor réutilisé).

    python3 motion/trait/six_aides_31dec.py --stills 0.5,8,15      → images d'aperçu
    python3 motion/trait/six_aides_31dec.py --jobs 6                → output/trait/six_aides_31dec.mp4
"""
import argparse
import math
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cairo  # noqa: E402

import decors as DC  # noqa: E402
import decors_ville as V  # noqa: E402
import ui  # noqa: E402
import voix  # noqa: E402
from dessin import (FPS, H, INK, LW, ROOT, W, back, circle, couche_floue, dark, ease, ease_out, ecrit, flat, halo,  # noqa: E402
                    mix, paint, poly, rrect, stroke)
from film import Film  # noqa: E402
from perso import Perso, traits_choc  # noqa: E402

NAR = ("rlqCQzyNTVyUMPGBqC31", {"stability": 0.42, "similarity_boost": 0.8, "style": 0.25})
PAT = ("5l4ttmr4SKNgi0HnOelT", {"stability": 0.38, "similarity_boost": 0.8, "style": 0.35})
VOIX = {"nar": NAR, "pat": PAT}
LIGNES = [
    ("pat", "Une prime de [1 000 euros] pour ton essence avant le [31], tu rêves ? Ici on paie les heures, pas tes {kilomètres}."),
    ("nar", "Sauf que d'ici le 31, c'est lui qui va payer ces [1 000 euros]. Et cinq autres aides avant."),
    ("nar", "Lundi, je fais le plein avant le garage. [90 euros] pour 20 kilomètres. Je lui montre le ticket. Je lui dis, y a des aides pour ça. Il me fait,"),
    ("pat", "Les aides, c'est pour les {assistés}. Toi, t'as un salaire."),
    ("nar", "Je dis rien."),
    ("nar", "{Pour les assistés.}"),
    ("nar", "Sauf que [six aides] s'arrêtent le [31 décembre]. Et pourtant presque personne les réclame."),
    ("nar", "D'abord, l'aide carburant. Revenu modeste et tu roules pour bosser ? L'État te verse [100 euros]. Formulaire aux impôts."),
    ("nar", "Ensuite, le chèque énergie. J'ai déménagé, je l'ai jamais reçu. Ce que peu de gens savent, c'est qu'il suit pas ton adresse. Il se réclame en ligne. Pour moi, [48 euros]."),
    ("nar", "La troisième, la mairie. Ma voisine garde son manteau chez elle. Le centre d'action sociale peut l'aider pour le chauffage, selon la ville."),
    ("nar", "La quatrième, le don. Ma mère hésitait à donner 100 euros à une asso d'aide alimentaire. Si tu payes l'impôt, l'État t'en rend [75 %]. Ses 100 euros lui coûtent [25]."),
    ("nar", "La cinquième, les RTT. Mon père en a trois qui sautent au 31. Il les revend à son patron, majorés d'un quart, sans impôt. [450 euros]."),
    ("nar", "Et la dernière, la plus grosse. Jusqu'au 31, un patron peut verser [1 000 euros] par salarié pour le trajet, sans cotisations. {Rien l'oblige.}"),
    ("nar", "Alors je lui fais le calcul, devant les quatre mécanos. Une augmentation lui coûterait bien plus, avec les charges."),
    ("nar", "Honnêtement, je l'ai peut-être un peu coincé devant ses gars."),
    ("nar", "Il signe pour tout l'atelier."),
    ("nar", "Total, [1 673 euros]. Dont [1 000 euros] signés par lui."),
]

SOL = 1330                     # ligne du sol À L'ÉCRAN pour toutes les scènes d'intérieur (caméra par défaut)
Y_SOUS = 1430                  # sous-titres toujours au même endroit, sur le sol
OUT = ROOT / "output/trait/six_aides_31dec.mp4"
WORK = ROOT / "output/trait/_work_six_aides"

KEVIN = dict(cheveux="boucles", couleur_cheveux=(30, 24, 30), peau=(198, 138, 98), haut="sweat",
             couleur_haut=(46, 170, 120), bas=(56, 70, 120), chaussures=(245, 245, 245), seed=1, tete=0.84, mince=0.86)
PATRON = dict(cheveux="chauve", couleur_cheveux=(150, 150, 156), peau=(236, 186, 150), haut="chemise",
              couleur_haut=(44, 52, 86), bas=(36, 40, 60), chaussures=(30, 30, 36), lunettes=True, moustache=True,
              seed=3, tete=0.84, mince=0.92)
MERE = dict(cheveux="chignon", couleur_cheveux=(80, 52, 36), peau=(205, 150, 110), haut="sweat",
            couleur_haut=(150, 90, 170), bas=(60, 60, 90), chaussures=(90, 60, 50), seed=5, tete=0.84, mince=0.86)
PERE = dict(cheveux="court", couleur_cheveux=(60, 50, 45), peau=(190, 130, 92), haut="chemise",
            couleur_haut=(90, 130, 170), bas=(50, 56, 70), chaussures=(40, 36, 34), barbe=True, seed=7, tete=0.84,
            mince=0.9)
VOISINE = dict(cheveux="chignon", couleur_cheveux=(205, 205, 210), peau=(236, 196, 170), haut="sweat",
               couleur_haut=(170, 60, 60), bas=(70, 60, 80), chaussures=(80, 50, 40), lunettes=True, seed=9, tete=0.84,
               mince=0.9)
CHEFFE = dict(cheveux="chignon", couleur_cheveux=(40, 30, 30), peau=(236, 186, 150), haut="chemise",
              couleur_haut=(60, 60, 70), bas=(40, 40, 50), chaussures=(30, 30, 36), lunettes=True, seed=11, tete=0.84,
              mince=0.86)
MECANOS = [dict(cheveux=c, couleur_cheveux=cc, peau=p, haut="sweat", couleur_haut=(46, 80, 140), bas=(46, 80, 140),
                chaussures=(40, 40, 46), seed=20 + i, tete=0.84, mince=0.88, barbe=(i == 2))
           for i, (c, cc, p) in enumerate([("court", (40, 30, 26), (236, 186, 150)), ("plaque", (20, 20, 24), (160, 110, 80)),
                                           ("court", (120, 80, 50), (220, 170, 130)), ("boucles", (60, 40, 30), (120, 80, 60))])]


# ═════════════ briques de décor (dessinées pour cette vidéo) ═════════════

def deg(ctx, x0, y0, x1, y1, c0, c1):
    V._deg(ctx, x0, y0, x1, y1, c0, c1)


def ville_floue(ctx, t, fx, fy, fw, fh, seed=1, ciel=((16, 22, 50), (70, 60, 110)), rayon=16, chaud=0.8):
    """Ville vue par une fenêtre, floue (profondeur de champ), découpée au cadre de la fenêtre."""
    def d(c):
        c.rectangle(fx, fy, fw, fh)
        c.clip()
        deg(c, fx, fy, fx + fw, fy + fh, *ciel)
        V.immeubles(c, fx - 60, fx + fw + 60, fy + fh * 0.95, t, seed=seed, col=(40, 46, 86), hmin=fh * 0.35,
                    hmax=fh * 0.8)
        V.immeubles(c, fx - 20, fx + fw + 60, fy + fh * 1.02, t, seed=seed + 4, col=(30, 34, 64), hmin=fh * 0.2,
                    hmax=fh * 0.5)
        for i in range(7):
            bx = fx + (i * 173 + seed * 61) % max(1, int(fw))
            by = fy + fh * (0.35 + 0.5 * ((i * 0.37 + seed * 0.13) % 1))
            halo(c, bx, by, 34 + (i % 3) * 14, (255, 200, 120) if i % 2 else (140, 170, 255), 0.55 * chaud)
    couche_floue(ctx, d, rayon=rayon, bord="constant")


def fenetre(ctx, t, x, y, w, h, seed=1, ciel=((16, 22, 50), (70, 60, 110)), montants=2):
    ville_floue(ctx, t, x, y, w, h, seed, ciel)
    ctx.rectangle(x, y, w, h)
    stroke(ctx, 16, (30, 30, 44))
    for i in range(1, montants):
        ctx.rectangle(x + w * i / montants - 6, y, 12, h)
        flat(ctx, (30, 30, 44))
    ctx.rectangle(x - 14, y + h, w + 28, 18)
    paint(ctx, (210, 210, 220), LW * 0.8, shade=0.9)


def piece(ctx, mur=(54, 62, 100), mur2=(32, 36, 66), sol=(40, 38, 58), x0=-1400, x1=3400):
    deg(ctx, x0, -1200, x1, SOL, mur2, mur)
    ctx.rectangle(x0, SOL - 22, x1 - x0, 22)
    flat(ctx, dark(mur2, 0.7))
    deg(ctx, x0, SOL, x1, 3200, sol, dark(sol, 0.45))


def lumiere_sol(ctx, x, rx=520, alpha=0.18):
    ctx.save()
    ctx.translate(x, SOL + 70)
    ctx.scale(1, 0.22)
    halo(ctx, 0, 0, rx, (255, 226, 170), alpha)
    ctx.restore()


def reflet_doux(ctx, dessin, alpha=0.32):
    m = ctx.get_matrix()
    ys = m.yy * SOL + m.y0
    g = cairo.LinearGradient(0, ys, 0, ys + 380 * m.yy)
    g.add_color_stop_rgba(0, 0, 0, 0, alpha)
    g.add_color_stop_rgba(1, 0, 0, 0, 0)

    def d(c):
        c.translate(0, 2 * SOL)
        c.scale(1, -1)
        dessin(c)
    couche_floue(ctx, d, rayon=10, bord="constant", masque=g)


def enseigne(ctx, x, y, txt, s=1.0, fond=(250, 250, 250), col=INK, bord=INK):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    from dessin import texte
    sf = texte(txt, 56, col, True)
    w = sf.get_width() + 70
    rrect(ctx, -w / 2, -52, w, 104, 12)
    paint(ctx, fond, LW, shade=0.92)
    rrect(ctx, -w / 2 + 10, -42, w - 20, 84, 8)
    stroke(ctx, LW * 0.5, bord, alpha=0.4)
    ecrit(ctx, txt, 0, 2, 56, col, big=True)
    ctx.restore()


def horloge(ctx, x, y, r, t):
    circle(ctx, x, y, r)
    paint(ctx, (250, 250, 250), LW, shade=0.9)
    for i in range(12):
        a = i * math.pi / 6
        ctx.move_to(x + math.cos(a) * r * 0.78, y + math.sin(a) * r * 0.78)
        ctx.line_to(x + math.cos(a) * r * 0.9, y + math.sin(a) * r * 0.9)
        stroke(ctx, 4)
    for ang, l, w in ((t * 0.5 - 1.2, 0.5, 8), (t * 3.0, 0.75, 5)):
        ctx.move_to(x, y)
        ctx.line_to(x + math.cos(ang) * r * l, y + math.sin(ang) * r * l)
        stroke(ctx, w)


def comptoir(ctx, x, w, h=330, coul=(70, 76, 96), dessus=(200, 204, 214), texte=None):
    rrect(ctx, x, SOL - h, w, h, 10)
    paint(ctx, coul, LW, shade=0.85)
    rrect(ctx, x - 20, SOL - h - 26, w + 40, 34, 8)
    paint(ctx, dessus, LW, shade=0.92)
    for i in range(1, 4):
        ctx.move_to(x + w * i / 4, SOL - h + 30)
        ctx.line_to(x + w * i / 4, SOL - 20)
        stroke(ctx, LW * 0.5, alpha=0.35)
    if texte:
        ecrit(ctx, texte, x + w / 2, SOL - h / 2, 44, (230, 232, 240), big=True)


def feuille(ctx, x, y, s, titre, lignes, k=1.0, rot=-0.04, surl=None, tampon=None, tampon_k=0.0, prix=None,
            couleur=(232, 52, 60)):
    """Feuille de papier crème : bandeau titre, lignes (le mot `surl` surligné jaune), prix en gros, tampon."""
    if k <= 0:
        return
    kk = back(min(1.0, k))
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s * kk, s * kk)
    hh = 170 + 86 * len(lignes) + (130 if prix else 0)
    rrect(ctx, -330 + 14, -hh / 2 + 16, 660, hh, 16)
    flat(ctx, (0, 0, 0), 0.28)
    rrect(ctx, -330, -hh / 2, 660, hh, 16)
    paint(ctx, (252, 248, 236), LW, shade=0.95)
    rrect(ctx, -330, -hh / 2, 660, 110, 16)
    flat(ctx, couleur)
    ctx.rectangle(-330, -hh / 2 + 70, 660, 40)
    flat(ctx, couleur)
    ctx.move_to(-330, -hh / 2 + 110)
    ctx.line_to(330, -hh / 2 + 110)
    stroke(ctx, LW)
    rrect(ctx, -330, -hh / 2, 660, hh, 16)
    stroke(ctx, LW)
    ecrit(ctx, titre, 0, -hh / 2 + 56, 54, (255, 255, 255), big=True)
    yy = -hh / 2 + 170
    from dessin import texte as tx
    for i, l in enumerate(lignes):
        a = ease((k - 0.25 - 0.18 * i) / 0.3)
        if a <= 0:
            yy += 86
            continue
        if surl and surl in l:
            sw = tx(l, 40, INK).get_width()
            rrect(ctx, -280, yy - 30, (sw + 20) * a, 60, 8)
            flat(ctx, (255, 214, 60), 0.9)
        circle(ctx, -300, yy, 8)
        flat(ctx, INK, a)
        ecrit(ctx, l, -270, yy, 40, INK, ax=0, alpha=a)
        yy += 86
    if prix:
        ecrit(ctx, prix, 0, yy + 30, 110, couleur, big=True)
    if tampon and tampon_k > 0:
        kt = back(min(1, tampon_k * 2.2))
        ctx.save()
        ctx.translate(120, hh / 2 - 90)
        ctx.rotate(-0.2)
        ctx.scale(2.0 - kt, 2.0 - kt)
        rrect(ctx, -170, -50, 340, 100, 12)
        stroke(ctx, 9, (30, 150, 80), alpha=min(1, tampon_k * 3))
        ecrit(ctx, tampon, 0, 2, 60, (30, 150, 80), big=True, alpha=min(1, tampon_k * 3))
        ctx.restore()
    ctx.restore()


def assombrir(ctx, a=0.45):
    ctx.save()
    ctx.identity_matrix()
    ctx.rectangle(0, 0, W, H)
    ctx.set_source_rgba(0.02, 0.02, 0.06, a)
    ctx.fill()
    ctx.restore()


def ticket(ctx, x, y, s):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    poly(ctx, [(-60, -90), (60, -90), (60, 80), (45, 92), (30, 80), (15, 92), (0, 80), (-15, 92), (-30, 80), (-45, 92),
               (-60, 80)])
    paint(ctx, (252, 252, 248), LW * 0.8, shade=0.92)
    ecrit(ctx, "CARBURANT", 0, -60, 20, INK, big=True)
    for i in range(3):
        rrect(ctx, -44, -30 + i * 20, 88, 8, 4)
        flat(ctx, (200, 200, 205))
    ecrit(ctx, "90,00 €", 0, 50, 34, INK, big=True)
    ctx.restore()


# ═════════════ le film ═════════════

def construire(work):
    voice, words = voix.build(LIGNES, VOIX, work)
    f = Film(voice, words)
    T = f.t
    t_fin = f.dur

    def tw(mot, apres=0.0):
        """Temps du 1er mot qui commence par `mot` APRÈS `apres` secondes (évite les homonymes du début)."""
        m = mot.lower()
        for w in words:
            if w["t0"] >= apres and w["w"].lower().strip(",.!?…:;«»\"'").startswith(m):
                return w["t0"]
        raise KeyError(mot)

    kev, pat = Perso(**KEVIN), Perso(**PATRON)
    mere, pere, voi, cheffe = Perso(**MERE), Perso(**PERE), Perso(**VOISINE), Perso(**CHEFFE)
    mecs = [Perso(**m) for m in MECANOS]

    # ── jeu des personnages calé sur les mots ──
    pat.pose(0, "repos").emotion(0, "malin")
    pat.pose(T("tu") - 0.8, "objet").pose(T("tu") - 0.12, "pointe").pose(T("Ici") - 0.1, "pointe_g").emotion(T("kilomètres") - 0.2, "colere")
    pat.pose(T("Sauf") + 0.2, "mains_hanches").emotion(T("Sauf"), "content")
    pat.pose(T("payer") - 0.05, "pointe_g").emotion(T("payer"), "choc")
    pat.pose(T("Lundi"), "repos").emotion(T("Lundi"), "neutre")
    pat.pose(T("fait") - 0.3, "mains_hanches").emotion(T("fait") - 0.3, "malin")
    pat.pose(T("assistés") - 0.1, "haussement").pose(T("Toi"), "pointe_cam")
    pat.pose(tw("Je", 25.0), "repos")
    pat.pose(T("dernière") , "mains_hanches").emotion(T("dernière"), "malin")
    pat.pose(tw("Rien", 89.0) - 0.1, "haussement").emotion(tw("Rien", 89.0), "content")
    pat.pose(T("Alors"), "mains_hanches").emotion(T("Alors"), "neutre")
    pat.emotion(T("augmentation"), "choc").emotion(T("charges"), "triste")
    pat.pose(T("signe") - 0.3, "objet").emotion(T("signe"), "neutre")
    pat.pose(T("Total"), "repos").emotion(T("Dont"), "triste")

    kev.pose(0, "repos").emotion(0, "neutre").emotion(T("tu") + 0.1, "triste").emotion(T("kilomètres"), "choc")
    kev.emotion(T("Lundi"), "content").emotion(T("90"), "choc")
    kev.pose(T("montre") - 0.2, "objet").pose(T("dis", 0) - 0.1, "pointe")
    kev.pose(T("assistés") - 1.0, "repos").emotion(T("assistés") + 0.2, "triste")
    kev.emotion(T("Sauf", 1), "malin")
    kev.pose(T("roules") - 0.2, "repos").emotion(T("roules"), "content")
    kev.pose(T("déménagé") - 0.2, "haussement").emotion(T("déménagé"), "triste")
    kev.pose(T("réclame", 1) - 0.2, "telephone").emotion(T("réclame", 1), "content")
    kev.pose(T("Alors"), "pointe").emotion(T("Alors"), "malin")
    kev.pose(T("Honnêtement"), "facepalm").emotion(T("Honnêtement"), "malin")
    kev.pose(T("signe"), "leve").emotion(T("signe"), "content")
    kev.pose(T("Total"), "repos")

    def objet_ticket(ctx, x, y, s):
        ticket(ctx, x, y - 40, 1.4)
    kev.objet = objet_ticket

    def objet_feuille(ctx, x, y, s):
        rrect(ctx, x - 110, y - 160, 220, 260, 8)
        paint(ctx, (252, 248, 236), LW, shade=0.95)
        ecrit(ctx, "PRIME", x, y - 120, 34, (220, 50, 60), big=True)
        ecrit(ctx, "1 000 €", x, y - 60, 44, INK, big=True)
    pat.objet = objet_feuille

    mere.pose(0, "objet").emotion(0, "triste").emotion(T("rend") , "content")
    mere.objet = lambda ctx, x, y, s: V.billet(ctx, x, y - 40, 1.3, -0.1)
    pere.pose(0, "repos").emotion(0, "triste").emotion(T("revend"), "content").pose(T("revend") - 0.2, "pointe")
    voi.pose(0, "repos").emotion(0, "triste").emotion(T("chauffage") + 0.3, "content")
    cheffe.pose(0, "mains_hanches").emotion(0, "neutre")
    for i, m in enumerate(mecs):
        m.pose(0, "repos").emotion(0, "neutre").emotion(T("augmentation"), "choc")
        m.pose(T("signe") + 0.05 * i, "leve").emotion(T("signe") + 0.05 * i, "content")

    def bp(t):
        return f.bouche(t, "pat")

    # ───────── décor 1 : l'accueil du garage ─────────
    def garage(ctx, t, lt, kev_x=230, crumple=True):
        piece(ctx, mur=(70, 84, 120), mur2=(40, 46, 76), sol=(56, 56, 70))
        fenetre(ctx, t, 640, 330, 520, 560, seed=3, ciel=((40, 50, 96), (200, 140, 130)))
        enseigne(ctx, 300, 300, "GARAGE · ACCUEIL", 0.95)
        horloge(ctx, 110, 560, 70, t)
        # affiche des tarifs
        rrect(ctx, 330, 470, 230, 300, 8)
        paint(ctx, (250, 246, 232), LW, shade=0.95)
        ecrit(ctx, "TARIFS", 445, 510, 36, (220, 50, 60), big=True)
        for i, (a, b) in enumerate((("Vidange", "79 €"), ("Pneus", "65 €"), ("Freins", "140 €"))):
            ecrit(ctx, a, 350, 570 + i * 60, 26, INK, ax=0)
            ecrit(ctx, b, 540, 570 + i * 60, 26, INK, ax=1, big=True)
        lumiere_sol(ctx, 560)

        def gens(c):
            pat.draw(c, 720, SOL - 40, 0.78, t, bouche=bp(t))
        reflet_doux(ctx, gens)
        gens(ctx)
        comptoir(ctx, 420, 600, texte="ACCUEIL")
        # la feuille de la prime sur le comptoir, puis froissée et jetée
        t_jet = T("tu") - 0.1
        if t < t_jet:
            feuille(ctx, 610, SOL - 420, 0.42, "PRIME TRANSPORT", ["jusqu'au 31/12"], k=1.0, rot=-0.1, prix="1 000 €")
        elif crumple and t < t_jet + 0.9:
            u = (t - t_jet) / 0.9
            bx, by = 610 + 380 * u, SOL - 430 - 260 * math.sin(math.pi * u) + 300 * u * u
            circle(ctx, bx, by, 40 - 8 * u)
            paint(ctx, (250, 246, 232), LW, shade=0.85)
        # poubelle
        poly(ctx, [(930, SOL - 150), (1050, SOL - 150), (1030, SOL), (950, SOL)])
        paint(ctx, (120, 126, 140), LW, shade=0.85)
        kev.objet = objet_ticket
        kev.draw(ctx, kev_x, SOL + 120, 0.86, t, regard=0.7)
        if T("kilomètres") - 0.1 <= t < T("Sauf"):
            traits_choc(ctx, kev_x, SOL + 120 - 0.86 * 900, 120, t - T("kilomètres"), color=(255, 214, 60))

    f.plan(0, garage, [(0, 600, 880, 1.06), (3.3, 620, 860, 1.12)], fouet=False)
    f.plan("tu", garage, [(0, 760, 760, 1.5), (1.0, 820, 820, 1.42)])
    f.plan("Ici", garage, [(0, 470, 900, 1.0), (1.3, 470, 900, 1.04)])
    f.plan("pas", garage, [(0, 690, 640, 1.8), (1.0, 690, 640, 1.9)])

    # ───────── décor 2 : les dominos (promesse) ─────────
    PETITS = [("points", "essence"), ("soleil", "flamme"), ("points", "maison"), ("soleil", "coeur"),
              ("points", "calendrier")]
    XD = [180 + i * 250 for i in range(5)]
    XG, SG = 1500, 3.0
    PIVOT = XG + 150 * SG
    XPAT = 2480
    t_chaine = T("Et", 0) + 0.15

    def ang_petit(i, t):
        t0 = t_chaine + i * 0.32
        if t < t0:
            return 0.0
        u = min(1.0, (t - t0) / 0.32)
        a = 0.62 * u * u
        if i < 4 and t > t0 + 0.32:
            a = 0.62 + 0.7 * ease((t - t0 - 0.32) / 0.4)
        return a

    def ang_geant(t):
        tp = T("payer") - 0.1
        if t < tp:
            return 0.0
        if t < tw("Sauf", 27.0):
            return 0.19 * ease_out((t - tp) / 0.35) - 0.015 * math.sin((t - tp) * 9) * math.exp(-(t - tp) * 3)
        return 0.0

    def dominos(ctx, t, lt, cal=True, gris=False):
        piece(ctx, mur=(38, 44, 84), mur2=(20, 24, 50), sol=(34, 34, 56), x0=-1800, x1=4200)
        fenetre(ctx, t, -600, -200, 4200, 1300, seed=7, montants=9)

        def objets(c):
            for i, (h, b) in enumerate(PETITS):
                V.domino(c, XD[i], SOL, 1.0, ang_petit(i, t) if not gris else 0.0, h, b,
                         couleur=(250, 246, 232) if not gris else (190, 190, 198))
            V.domino(c, XG, SOL, SG, ang_geant(t), "soleil", "bus", "1 000 €", lueur=0.0 if gris else 1.0,
                     couleur=(250, 236, 170) if not gris else (200, 196, 170))
            pat.draw(c, XPAT, SOL, 0.78, t)
        lumiere_sol(ctx, XG + 200, 900, 0.22)
        reflet_doux(ctx, objets)
        objets(ctx)
        if cal and t >= T("31", 1) - 0.1:
            u = t - (T("31", 1) - 0.1)
            y = -900 + (SOL - 280 * SG - 200 + 900) * min(1.15, 1 - math.exp(-u * 6) * math.cos(u * 12))
            ctx.move_to(XG - 120, -1600)
            ctx.line_to(XG - 120, y - 150)
            stroke(ctx, 4)
            DC.calendrier(ctx, XG - 120, y, 0.9, "DÉC", "31")
        if T("payer") <= t < tw("Sauf", 27.0):
            traits_choc(ctx, XPAT, SOL - 0.78 * 880, 130, t - T("payer"), color=(255, 255, 255))

    gx = XG + 75 * SG
    f.plan("Sauf", dominos, [(0, gx + 200, SOL - 380 / 0.92, 0.92), (1.6, gx + 300, SOL - 380 / 0.95, 0.95)])
    f.plan("payer", dominos, [(0, 2100, SOL - 400 / 1.05, 1.05), (1.2, 2140, SOL - 400 / 1.1, 1.1)])
    f.plan(("Et", 0), dominos, lambda lt: (XD[0] + 300 + 1100 * ease(lt / 1.8), SOL - 380 / 1.0, 1.0))

    # ───────── décor 3 : la station, le soir ─────────
    SOLX = 1560

    def montant(t):
        a, b = T("plein") , T("90")
        return 90.0 * ease((t - a) / (b - a)) if t >= a else 0.0

    def dehors(ctx, t, lt, pompe=True, route=0.0):
        deg(ctx, -800, -900, 2000, SOLX - 300, (40, 52, 100), (226, 160, 140))
        couche_floue(ctx, lambda c: (V.immeubles(c, -700, 1900, SOLX - 220, t, seed=5, col=(84, 90, 140), hmin=260,
                                                 hmax=620),
                                     V.immeubles(c, -600, 1900, SOLX - 160, t, seed=9, col=(64, 70, 116), hmin=140,
                                                 hmax=380)), rayon=12, bord="constant")
        deg(ctx, -800, SOLX - 180, 2000, 2600, (74, 74, 90), (44, 44, 56))
        for i in range(-2, 8):
            x = i * 260 - (route * 900) % 260
            rrect(ctx, x, SOLX + 120, 140, 18, 8)
            flat(ctx, (240, 240, 240), 0.7)
        V.panneau_route(ctx, 860, 640, "GARAGE →", "20 km")
        if pompe:
            V.pompe(ctx, 290, SOLX, f"{montant(t):05.2f} €".replace(".", ","), t)
            V.voiture(ctx, 900, SOLX, 0.95, (40, 150, 170))
            kev.draw(ctx, 640, SOLX, 0.84, t, regard=-0.8)
            if t >= T("90"):
                d = t - T("90")
                traits_choc(ctx, 640, SOLX - 0.84 * 900, 130, d, color=(255, 255, 255))
                for i in range(8):
                    a = -1.3 + i * 0.32
                    r = 120 + 800 * d * (0.7 + 0.1 * (i % 3))
                    V.billet(ctx, 290 + math.cos(a) * r * 0.8, 840 + math.sin(a) * r * 0.6 + 380 * d * d, 1.0,
                             d * (3 + i) * (1 if i % 2 else -1))

    f.plan("Lundi", dehors, [(0, 540, 1000, 1.0), (1.4, 540, 1020, 1.06)])
    f.plan("90", dehors, [(0, 470, 960, 1.14), (1.0, 470, 960, 1.2)])
    f.plan("20", dehors, [(0, 820, 760, 1.25), (1.0, 820, 740, 1.32)])

    # retour au garage : le ticket, puis la réplique du patron
    def garage2(ctx, t, lt):
        garage(ctx, t, lt, kev_x=300, crumple=False)

    f.plan("montre", garage2, [(0, 500, 860, 1.12), (1.4, 480, 860, 1.18)])
    f.plan(("Je", 2), garage2, [(0, 330, 780, 1.5), (1.8, 340, 790, 1.55)])
    f.plan("Il", garage2, [(0, 700, 740, 1.45), (0.8, 700, 740, 1.5)])
    f.plan("assistés", garage2, [(0, 710, 640, 1.85), (0.8, 710, 650, 1.95)])
    f.plan("Toi", garage2, [(0, 600, 820, 1.2), (1.4, 600, 820, 1.25)])
    f.plan(tw("Je", 25.0), garage2, [(0, 300, 640, 2.0), (0.9, 300, 640, 2.08)])
    f.plan(tw("Pour", 26.0), garage2, [(0, 300, 640, 2.1), (1.0, 300, 640, 2.15)],
           hud=lambda ctx, t, lt: (assombrir(ctx, 0.35),
                                   ui.panneau(ctx, W / 2, 620, "POUR LES ASSISTÉS", lt, rot=-0.05, size=86)))

    # ───────── les 6 aides alignées ─────────
    def six(ctx, t, lt):
        dominos_debout(ctx, t, lt, gris=t >= T("pourtant"))
        ctx.move_to(XG - 160, -1600)
        ctx.line_to(XG - 160, 140)
        stroke(ctx, 4)
        DC.calendrier(ctx, XG - 160, 290, 0.9, "DÉC", "31")
    f.plan(tw("Sauf", 27.0), six, [(0, 1100, SOL - 370 / 0.58, 0.58), (2.8, 1100, SOL - 370 / 0.62, 0.62)])
    f.plan("pourtant", six, [(0, 1050, SOL - 370 / 0.66, 0.66), (1.8, 1050, SOL - 370 / 0.68, 0.68)],
           hud=lambda ctx, t, lt: ui.panneau(ctx, W / 2, 560, "PERSONNE LES RÉCLAME", lt - 0.5, rot=-0.07, size=64))

    # zoom sur le domino de chaque aide (rappel visuel de l'étape)
    def zoom_domino(i):
        cx = XD[i] + 75 if i < 5 else gx
        z = 1.25 if i < 5 else 0.9
        return [(0, cx, SOL - 340 / z, z), (1.2, cx, SOL - 340 / z, z * 1.06)]

    def dominos_debout(ctx, t, lt, gris=False):
        piece(ctx, mur=(38, 44, 84), mur2=(20, 24, 50), sol=(34, 34, 56), x0=-1800, x1=4200)
        fenetre(ctx, t, -600, -200, 4200, 1300, seed=7, montants=9)

        def objets(c):
            for i, (h, b) in enumerate(PETITS):
                V.domino(c, XD[i], SOL, 1.0, 0.0, h, b, couleur=(190, 190, 198) if gris else (250, 246, 232))
            V.domino(c, XG, SOL, SG, 0.0, "soleil", "bus", "1 000 €", lueur=0.0 if gris else 1.0,
                     couleur=(200, 196, 170) if gris else (250, 236, 170))
        lumiere_sol(ctx, XG, 900, 0.22)
        reflet_doux(ctx, objets)
        objets(ctx)

    # ───────── aide 1 : carburant ─────────
    f.plan("D'abord", dominos_debout, zoom_domino(0))

    def route(ctx, t, lt):
        dehors(ctx, t, lt, pompe=False, route=lt)
        b = math.sin(lt * 14) * 4
        V.voiture(ctx, 520, SOLX + 40 + b, 1.15, (40, 150, 170))
        circle(ctx, 450, SOLX - 190 + b, 34)
        paint(ctx, (198, 138, 98), LW, shade=0.9)
    f.plan("Revenu", route, [(0, 540, 1000, 1.0), (2.2, 560, 1000, 1.05)])

    def ecran_virement(c, w, h):
        flat_bg = (245, 247, 252)
        c.rectangle(0, 0, w, h)
        c.set_source_rgb(*[v / 255 for v in flat_bg])
        c.fill()
        ecrit(c, "MA BANQUE", w / 2, 26, 12, (120, 120, 130), big=True)
        ecrit(c, "+100,00 €", w / 2, 90, 22, (40, 160, 90), big=True)
        ecrit(c, "Aide carburant", w / 2, 122, 10, INK)

    def telephone_scene(ctx, t, lt):
        dehors(ctx, t, lt, pompe=False, route=0.0)
        assombrir(ctx, 0.3)
        DC.telephone(ctx, 540, 900, 3.4 * ease_out(lt / 0.3) + 0.01, ecran=ecran_virement, t=t,
                     rot=-0.05 + 0.02 * math.sin(t * 2))
        if lt > 0.9:
            DC.etiquette(ctx, 830, 520, 0.8, "+100 €", lt - 0.9, couleur=(110, 220, 140))
    f.plan(("L'État", 0), telephone_scene, [(0, 540, 960, 1.0), (1.8, 540, 960, 1.04)])

    def formulaire(ctx, t, lt, titre, lignes, surl, tampon=None, t_tampon=99.0, fond=dehors, prix=None):
        fond(ctx, t, lt)
        assombrir(ctx, 0.45)
        feuille(ctx, 540, 840, 1.15, titre, lignes, k=lt / 0.5, rot=-0.03, surl=surl, tampon=tampon,
                tampon_k=max(0.0, (t - t_tampon) / 0.4), prix=prix)
    f.plan("Formulaire", lambda c, t, lt: formulaire(
        c, t, lt, "AIDE CARBURANT", ["N° fiscal", "plaque du véhicule", "avant le 31/12"], "avant le 31/12",
        tampon="ENVOYÉ", t_tampon=T("impôts") + 0.2, fond=lambda c2, t2, l2: dehors(c2, t2, l2, pompe=True)),
        [(0, 540, 960, 1.0), (1.4, 540, 960, 1.03)])

    # ───────── aide 2 : chèque énergie (le studio de Kévin) ─────────
    f.plan("Ensuite", dominos_debout, zoom_domino(1))

    def studio(ctx, t, lt, boites=True):
        piece(ctx, mur=(86, 110, 150), mur2=(56, 72, 110), sol=(120, 92, 70))
        fenetre(ctx, t, 560, 380, 420, 520, seed=11, ciel=((70, 90, 140), (170, 190, 220)), montants=2)
        # radiateur éteint
        rrect(ctx, 600, 1000, 340, 200, 10)
        paint(ctx, (226, 230, 236), LW, shade=0.85)
        for i in range(6):
            ctx.move_to(630 + i * 55, 1020)
            ctx.line_to(630 + i * 55, 1180)
            stroke(ctx, LW * 0.6, alpha=0.5)
        if boites:
            for i, (bx, by, bw) in enumerate(((60, SOL, 260), (120, SOL - 190, 200), (340, SOL, 200))):
                rrect(ctx, bx, by - 190, bw, 190, 6)
                paint(ctx, (196, 150, 100), LW, shade=0.85)
                ctx.move_to(bx + bw / 2, by - 190)
                ctx.line_to(bx + bw / 2, by - 120)
                stroke(ctx, LW * 0.7)
                if i == 0:
                    ecrit(ctx, "CARTONS", bx + bw / 2, by - 70, 34, INK, big=True)
        kev.objet = lambda c, x, y, s_: DC.telephone(c, x, y - 40, 0.9, t=t)
        kev.draw(ctx, 480, SOL + 100, 0.86, t, regard=0.3)
    f.plan("J'ai", studio, [(0, 520, 900, 1.05), (1.8, 520, 900, 1.1)])

    def boites_lettres(ctx, t, lt):
        piece(ctx, mur=(120, 110, 100), mur2=(80, 72, 68), sol=(70, 64, 60))
        for j, (bx, nom, plein) in enumerate(((140, "ANCIENNE ADRESSE", True), (600, "NOUVELLE ADRESSE", False))):
            rrect(ctx, bx, 560, 360, 420, 14)
            paint(ctx, (200, 206, 214), LW, shade=0.85)
            rrect(ctx, bx + 40, 620, 280, 40, 8)
            flat(ctx, (40, 40, 50))
            ecrit(ctx, nom, bx + 180, 1030, 34, (250, 250, 250), big=True)
            if plein:
                u = ease_out(lt / 0.8)
                ex, ey = bx + 180 + 500 * (1 - u), 720 - 300 * (1 - u)
                rrect(ctx, ex - 120, ey - 60, 240, 130, 10)
                paint(ctx, (250, 246, 232), LW, shade=0.92)
                ecrit(ctx, "CHÈQUE", ex, ey - 20, 30, (220, 140, 30), big=True)
                ecrit(ctx, "ÉNERGIE", ex, ey + 22, 30, (220, 140, 30), big=True)
            else:
                if lt > 1.0:
                    k = back((lt - 1.0) / 0.3)
                    for s_ in (1, -1):
                        ctx.move_to(bx + 180 - 110 * k, 770 - 110 * k * s_)
                        ctx.line_to(bx + 180 + 110 * k, 770 + 110 * k * s_)
                        stroke(ctx, 22, (232, 52, 60))
        kev.objet = None
        kev.draw(ctx, 1010, SOL + 160, 0.8, t, regard=-0.6)
    f.plan(tw("Ce", 43.0), boites_lettres, [(0, 540, 900, 1.0), (2.8, 540, 900, 1.05)])

    def ecran_cheque(c, w, h):
        c.rectangle(0, 0, w, h)
        c.set_source_rgb(0.97, 0.97, 0.99)
        c.fill()
        c.rectangle(0, 0, w, 40)
        c.set_source_rgb(0.95, 0.6, 0.15)
        c.fill()
        ecrit(c, "CHÈQUE ÉNERGIE", w / 2, 20, 10, (255, 255, 255), big=True)
        for i, l in enumerate(("N° fiscal", "Adresse", "Facture")):
            rrect(c, 10, 56 + i * 34, w - 20, 24, 6)
            c.set_source_rgb(0.9, 0.9, 0.93)
            c.fill()
            ecrit(c, l, 18, 68 + i * 34, 9, INK, ax=0)
        rrect(c, 14, 160, w - 28, 26, 13)
        c.set_source_rgb(0.2, 0.7, 0.4)
        c.fill()
        ecrit(c, "RÉCLAMER", w / 2, 173, 10, (255, 255, 255), big=True)

    def tel_cheque(ctx, t, lt):
        studio(ctx, t, lt)
        assombrir(ctx, 0.35)
        DC.telephone(ctx, 540, 860, 3.3 * ease_out(lt / 0.3) + 0.01, ecran=ecran_cheque, t=t, rot=0.04)
    f.plan(("Il", 1), tel_cheque, [(0, 540, 960, 1.0), (1.0, 540, 960, 1.03)])

    def gain48(ctx, t, lt):
        studio(ctx, t, lt)
        DC.etiquette(ctx, 760, 560, 1.0, "48 €", lt, couleur=(110, 220, 140))
    f.plan(tw("Pour", 47.5), gain48, [(0, 560, 860, 1.12), (1.8, 560, 860, 1.18)])

    # ───────── aide 3 : la mairie ─────────
    def mairie(ctx, t, lt):
        deg(ctx, -800, -900, 2000, SOL, (70, 110, 170), (190, 210, 230))
        couche_floue(ctx, lambda c: V.immeubles(c, -700, 1900, SOL - 300, t, seed=13, col=(140, 160, 190), hmin=200,
                                                hmax=500), rayon=12, bord="constant")
        rrect(ctx, 120, 360, 840, SOL - 360, 6)
        paint(ctx, (236, 226, 206), LW, shade=0.9)
        poly(ctx, [(90, 380), (540, 200), (990, 380)])
        paint(ctx, (210, 196, 176), LW, shade=0.9)
        enseigne(ctx, 540, 450, "MAIRIE", 1.0, fond=(40, 60, 120), col=(255, 255, 255))
        for i in range(4):
            rrect(ctx, 190 + i * 200, 560, 60, SOL - 560, 4)
            paint(ctx, (250, 246, 236), LW * 0.8, shade=0.88)
        rrect(ctx, 460, 980, 160, SOL - 980, 6)
        paint(ctx, (90, 60, 40), LW, shade=0.85)
        # drapeau
        ctx.move_to(940, 380)
        ctx.line_to(940, 120)
        stroke(ctx, 8)
        for k_, c_ in enumerate(((40, 70, 170), (250, 250, 250), (220, 40, 50))):
            x0 = 944 + k_ * 50
            ond = math.sin(t * 5 + k_) * 10
            poly(ctx, [(x0, 130 + ond * 0.3), (x0 + 50, 130 + ond), (x0 + 50, 230 + ond), (x0, 230 + ond * 0.3)])
            flat(ctx, c_)
        deg(ctx, -800, SOL, 2000, 2600, (150, 150, 156), (90, 90, 96))
        enseigne(ctx, 540, 820, "CENTRE D'ACTION SOCIALE", 0.62, fond=(250, 250, 250))
    f.plan("troisième", mairie, [(0, 540, 900, 1.0), (2.0, 540, 880, 1.06)])

    def salon_froid(ctx, t, lt, chaud=0.0):
        piece(ctx, mur=(120, 140, 170), mur2=(80, 96, 130), sol=(110, 96, 90))
        fenetre(ctx, t, 620, 360, 360, 460, seed=17, ciel=((20, 26, 60), (60, 70, 120)))
        rrect(ctx, 640, 1000, 300, 190, 10)
        paint(ctx, mix((226, 230, 236), (255, 170, 110), chaud), LW, shade=0.85)
        if chaud > 0:
            halo(ctx, 790, 1090, 380, (255, 150, 80), 0.35 * chaud)
        DC.canape(ctx, 330, SOL, 560, (120, 90, 140))
        voi.draw(ctx, 330, SOL + 130, 0.8, t, regard=0.4)
        DC.canape_avant(ctx, 330, SOL, 560, (120, 90, 140))
        # thermomètre
        rrect(ctx, 70, 520, 70, 300, 35)
        paint(ctx, (250, 250, 250), LW, shade=0.9)
        hh = 120 + 120 * chaud
        rrect(ctx, 90, 800 - hh, 30, hh, 15)
        flat(ctx, (220, 60, 60))
        ecrit(ctx, f"{16 + int(4 * chaud)}°", 105, 470, 48, INK, big=True)
        if chaud < 0.5:
            for i in range(3):
                v = (t * 0.8 + i * 0.33) % 1
                circle(ctx, 360 + 30 * math.sin(v * 6 + i), 560 - 140 * v, 16 + 26 * v)
                flat(ctx, (255, 255, 255), 0.4 * (1 - v))
    f.plan(tw("Ma", 52.0), salon_froid, [(0, 480, 900, 1.08), (2.2, 460, 880, 1.14)])

    def ccas(ctx, t, lt):
        chaud = ease((t - T("chauffage")) / 0.8) if t >= T("chauffage") else 0.0
        salon_froid(ctx, t, lt, chaud)
        if t < T("selon"):
            assombrir(ctx, 0.35)
            feuille(ctx, 540, 820, 1.1, "AIDE AU CHAUFFAGE", ["avis d'impôt", "justificatif de domicile",
                                                              "règles selon la ville"], k=lt / 0.5, rot=0.03,
                    surl="règles selon la ville", couleur=(40, 90, 170))
    f.plan(tw("Le", 54.5), ccas, [(0, 540, 960, 1.0), (2.2, 540, 940, 1.04)])
    f.plan("selon", ccas, [(0, 600, 900, 1.15), (0.8, 600, 900, 1.2)])

    # ───────── aide 4 : le don ─────────
    f.plan("quatrième", dominos_debout, zoom_domino(3))

    def cuisine(ctx, t, lt):
        piece(ctx, mur=(230, 196, 150), mur2=(200, 160, 120), sol=(150, 110, 80))
        fenetre(ctx, t, 640, 320, 380, 420, seed=19, ciel=((30, 40, 90), (120, 90, 140)))
        for i in range(6):
            rrect(ctx, 60 + i * 80, 380, 70, 70, 6)
            paint(ctx, (250, 250, 250), LW * 0.6, shade=0.95)
        mere.draw(ctx, 360, SOL - 10, 0.8, t, regard=0.5)
        # table + boîte de dons
        rrect(ctx, 80, SOL - 300, 920, 40, 8)
        paint(ctx, (120, 80, 50), LW, shade=0.85)
        for x in (120, 940):
            rrect(ctx, x, SOL - 260, 30, 260, 6)
            paint(ctx, (110, 72, 46), LW, shade=0.85)
        rrect(ctx, 650, SOL - 520, 260, 220, 10)
        paint(ctx, (60, 140, 90), LW, shade=0.85)
        rrect(ctx, 700, SOL - 520, 160, 20, 6)
        flat(ctx, INK)
        ecrit(ctx, "AIDE", 780, SOL - 430, 40, (255, 255, 255), big=True)
        ecrit(ctx, "ALIMENTAIRE", 780, SOL - 380, 32, (255, 255, 255), big=True)
    f.plan(tw("Ma", 60.0), cuisine, [(0, 520, 900, 1.08), (3.0, 520, 880, 1.14)])

    def don75(ctx, t, lt):
        cuisine(ctx, t, lt)
        assombrir(ctx, 0.4)
        ui.panneau(ctx, W / 2, 640, "75 % RENDUS", lt - 0.1, rot=-0.05, size=110, fond=(255, 214, 60), bord=INK,
                   col=INK)
        feuille(ctx, 540, 1010, 0.8, "REÇU FISCAL", ["don de 100 €", "réduction de 75 %"], k=(lt - 0.4) / 0.5,
                rot=0.05, surl="réduction de 75 %")
    f.plan(tw("Si", 64.0), don75, [(0, 540, 960, 1.0), (3.4, 540, 960, 1.04)])

    def don25(ctx, t, lt):
        cuisine(ctx, t, lt)
        DC.etiquette(ctx, 280, 540, 0.9, "100 €", lt, couleur=(240, 240, 240))
        if lt > 0.3:
            k = ease((lt - 0.3) / 0.3)
            ctx.move_to(150, 600)
            ctx.line_to(150 + 300 * k, 600 - 80 * k)
            stroke(ctx, 16, (232, 52, 60))
        if lt > 0.9:
            DC.etiquette(ctx, 780, 540, 1.0, "25 €", lt - 0.9, couleur=(110, 220, 140))
    f.plan(tw("Ses", 67.0), don25, [(0, 540, 900, 1.06), (1.8, 540, 900, 1.1)])

    # ───────── aide 5 : les RTT (le bureau du père) ─────────
    f.plan("cinquième", dominos_debout, zoom_domino(4))

    def bureau_pere(ctx, t, lt, cal=True):
        piece(ctx, mur=(196, 204, 214), mur2=(150, 160, 176), sol=(90, 96, 110))
        fenetre(ctx, t, 700, 300, 340, 520, seed=23, ciel=((90, 130, 190), (200, 220, 240)))
        if cal:
            rrect(ctx, 90, 300, 540, 520, 12)
            paint(ctx, (250, 250, 250), LW, shade=0.95)
            rrect(ctx, 90, 300, 540, 90, 12)
            flat(ctx, (220, 50, 60))
            ecrit(ctx, "DÉCEMBRE", 360, 345, 54, (255, 255, 255), big=True)
            t31 = tw("31", 74.0)
            for d in range(31):
                cx, cy = 130 + (d % 7) * 74, 430 + (d // 7) * 74
                ecrit(ctx, str(d + 1), cx + 26, cy + 26, 26, INK)
                if d in (22, 23, 29):
                    u = max(0.0, t - t31)
                    yy = cy + 600 * u * u
                    rot = u * 3
                    ctx.save()
                    ctx.translate(cx + 26, yy + 26)
                    ctx.rotate(rot)
                    rrect(ctx, -32, -30, 64, 60, 8)
                    flat(ctx, (255, 214, 60), max(0.0, 1 - u))
                    ecrit(ctx, "RTT", 0, 0, 22, INK, big=True, alpha=max(0.0, 1 - u))
                    ctx.restore()
        rrect(ctx, 60, SOL - 300, 960, 40, 8)
        paint(ctx, (200, 204, 210), LW, shade=0.9)
        pere.draw(ctx, 820 if cal else 330, SOL + 60, 0.84, t, regard=-0.5 if cal else 0.5)
    f.plan(tw("Mon", 72.0), bureau_pere, [(0, 540, 880, 1.0), (2.6, 500, 860, 1.06)])

    def rtt_feuille(ctx, t, lt):
        bureau_pere(ctx, t, lt, cal=False)
        cheffe.draw(ctx, 820, SOL + 40, 0.8, t, regard=-0.6)
        feuille(ctx, 560, 700, 0.75, "RACHAT DE RTT", ["3 jours", "+25 %", "sans impôt"], k=lt / 0.5, rot=-0.05,
                surl="sans impôt", tampon="ACCORD", tampon_k=max(0.0, (lt - 2.2) / 0.4))
    f.plan(("Il", 2), rtt_feuille, [(0, 560, 900, 1.0), (4.0, 560, 880, 1.06)])

    def gain450(ctx, t, lt):
        bureau_pere(ctx, t, lt, cal=False)
        DC.etiquette(ctx, 700, 560, 1.1, "450 €", lt, couleur=(110, 220, 140))
    f.plan("450", gain450, [(0, 520, 880, 1.1), (1.2, 520, 880, 1.15)])

    # ───────── aide 6 : la prime (retour au garage) ─────────
    f.plan("dernière", dominos_debout, zoom_domino(5))

    def prime(ctx, t, lt):
        garage(ctx, t, lt, kev_x=230, crumple=False)
        assombrir(ctx, 0.4)
        feuille(ctx, 540, 820, 1.05, "PRIME TRANSPORT", ["par salarié", "sans cotisations", "jusqu'au 31/12"],
                k=lt / 0.5, rot=-0.03, surl="sans cotisations", prix="1 000 €")
    f.plan("Jusqu'au", prime, [(0, 540, 960, 1.0), (5.0, 540, 960, 1.03)])
    f.plan(tw("Rien", 89.0), garage2, [(0, 700, 640, 1.85), (0.9, 700, 650, 1.92)])

    # ───────── le calcul devant les mécanos ─────────
    def atelier(ctx, t, lt, tableau=True):
        piece(ctx, mur=(96, 104, 120), mur2=(60, 66, 80), sol=(70, 70, 76), x0=-1600, x1=2800)
        fenetre(ctx, t, -300, 200, 800, 460, seed=29, ciel=((60, 80, 130), (200, 170, 150)), montants=4)
        enseigne(ctx, 1000, 260, "ATELIER", 1.0)
        if tableau:
            rrect(ctx, 600, 380, 620, 440, 10)
            paint(ctx, (250, 250, 250), LW, shade=0.95)
            k1 = ease((t - T("calcul")) / 0.5)
            k2 = ease((t - T("augmentation")) / 0.5)
            k3 = ease((t - T("charges")) / 0.5)
            ecrit(ctx, "AUGMENTATION 1 000 €", 910, 460, 44, INK, big=True, alpha=k1)
            ecrit(ctx, "+ CHARGES", 910, 540, 50, (220, 50, 60), big=True, alpha=k2)
            ecrit(ctx, "PRIME = 1 000 € PILE", 910, 650, 50, (30, 150, 80), big=True, alpha=k3)
        for i, m in enumerate(mecs):
            m.draw(ctx, -320 + i * 190, SOL + 20, 0.74, t, regard=0.5)
        pat.draw(ctx, 1320, SOL + 20, 0.8, t, regard=-0.6)
        kev.objet = None
        kev.draw(ctx, 470, SOL + 120, 0.86, t, regard=0.6)
    f.plan("Alors", atelier, [(0, 500, 860, 0.82), (3.0, 560, 860, 0.86)])
    f.plan(tw("Une", 93.0), atelier, [(0, 910, 640, 1.45), (2.8, 910, 650, 1.5)])
    f.plan("Honnêtement", atelier, [(0, 520, 660, 1.7), (2.4, 520, 670, 1.76)])

    def signature(ctx, t, lt):
        atelier(ctx, t, lt, tableau=False)
        if lt > 0.2:
            feuille(ctx, 1040, 1010, 0.55, "PRIME TRANSPORT", ["tout l'atelier"], k=(lt - 0.2) / 0.4, rot=0.06,
                    prix="1 000 €", tampon="SIGNÉ", tampon_k=max(0.0, (lt - 0.8) / 0.4))
    f.plan("signe", signature, [(0, 760, 860, 0.85), (1.6, 800, 860, 0.9)])

    def total(ctx, t, lt):
        dominos(ctx, t, lt, cal=False)
        if lt > 0.1:
            assombrir(ctx, 0.25)
            ctx.save()
            ctx.identity_matrix()
            ui.panneau(ctx, W / 2, 620, "1 673 € RÉCUPÉRÉS", lt - 0.1, rot=-0.04, size=96, fond=(110, 220, 140),
                       bord=INK, col=INK)
            ctx.restore()
    t_tot = T("Total")
    f.plan("Total", lambda c, t, lt: total(c, t, lt),
           [(0, 1500, SOL - 370 / 0.62, 0.62), (2.2, 1600, SOL - 370 / 0.66, 0.66)])
    f.plan("Dont", signature, [(0, 1180, 820, 1.2), (1.8, 1180, 820, 1.25)])

    # chute en chaîne pour le total : tous les dominos tombent
    _old = ang_petit

    # ───────── écran : compteur, étapes, sous-titres ─────────
    cles = [(0, 0), (T("100") + 0.2, 100), (T("48") + 0.3, 148), (T("25", 0) + 0.2, 223), (T("450") + 0.3, 673),
            (T("signe") + 0.4, 1673)]
    f.ecran(lambda ctx, t: ui.compteur(ctx, t, "RÉCUPÉRÉ AVANT LE 31/12", cles, apparition=T("payer")))
    debuts = [T("D'abord"), T("Ensuite"), T("troisième"), T("quatrième"), T("cinquième"), T("dernière")]

    def etapes(ctx, t):
        if t < T("six") or t >= t_tot:
            return
        k = back((t - T("six")) / 0.35)
        actif = sum(1 for d in debuts if t >= d)
        ctx.save()
        ctx.translate(W - 60, 190)
        ctx.scale(k, k)
        for i in range(6):
            x = -i * 74
            j = 5 - i
            fait = j + 1 < actif
            cur = j + 1 == actif
            circle(ctx, x, 0, 30 if cur else 24)
            paint(ctx, (255, 214, 60) if cur else ((110, 220, 140) if fait else (60, 60, 76)), LW * 0.8, shade=1)
            ecrit(ctx, str(j + 1), x, 2, 30 if cur else 24, INK if (cur or fait) else (200, 200, 210), big=True)
        ctx.restore()
    f.ecran(etapes)
    groupes = ui.decouper(words)
    f.ecran(lambda ctx, t: ui.sous_titres(ctx, t, groupes, y=Y_SOUS, size=60))

    # bruitages
    for mot, son, g in [("tu", "pop", 0.5), ("kilomètres", "impact", 0.6), ("payer", "impact", 0.8),
                        ("Et", "pop", 0.4), ("90", "impact", 0.8), ("assistés", "rate", 0.5),
                        (tw("Pour", 26.0), "impact", 0.6), ("100", "succes", 0.5), ("48", "succes", 0.5),
                        ("25", "succes", 0.5), ("450", "succes", 0.5), (tw("Rien", 89.0), "rate", 0.5),
                        ("signe", "succes", 0.7), ("Total", "succes", 0.8)]:
        try:
            f.son(mot, son, g)
        except KeyError:
            pass
    for i in range(5):
        f.son(t_chaine + i * 0.32 + 0.3, "pop", 0.35)
    f.secousse("payer", 10)
    f.secousse("90", 14)
    return f


# ═════════════ rendu en parallèle (morceaux), puis assemblage avec l'audio ═════════════

def _morceau(args):
    i0, i1, chemin = args
    f = construire(WORK)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", chemin]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for k in range(i0, i1):
        p.stdin.write(bytes(f.frame(k / FPS).get_data()))
    p.stdin.close()
    p.wait()
    return chemin


def rendre(jobs):
    f = construire(WORK)
    n = int(f.dur * FPS)
    parts = []
    pas = math.ceil(n / jobs)
    for j in range(jobs):
        parts.append((j * pas, min(n, (j + 1) * pas), str(WORK / f"part_{j:02d}.mp4")))
    with ProcessPoolExecutor(jobs) as ex:
        faits = list(ex.map(_morceau, parts))
    liste = WORK / "parts.txt"
    liste.write_text("".join(f"file '{p}'\n" for p in faits))
    wav = WORK / "mix.wav"
    f.audio(wav)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(liste), "-i", str(wav),
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-shortest",
                    "-movflags", "+faststart", str(OUT)], check=True)
    return OUT


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills")
    ap.add_argument("--jobs", type=int, default=6)
    a = ap.parse_args()
    if a.stills:
        f = construire(WORK)
        print(f"durée {f.dur:.1f} s, {len(f.plans)} plans")
        f.stills([float(x) for x in a.stills.split(",")], WORK / "stills")
    else:
        print("→", rendre(a.jobs))


if __name__ == "__main__":
    main()
