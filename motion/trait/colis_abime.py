"""Colis de Noël arrivé cassé, bon du livreur signé (script 43, scripts/modele/43_colis_abime.dial), moteur « trait ».
Kévin = Yann, la grande sœur = Natacha. Voix v4 accélérée à 64 s. Caméra « plans ».
TEST accroche « ouverture La Ficelle » (Kévin en pied + enjeu dès l'image 0, la sœur entre à 2 s, crash au ralenti) ;
TEST partage : le pote concerné (Yanis).

    python3 motion/trait/colis_abime.py                 → output/trait/colis_abime.mp4
    python3 motion/trait/colis_abime.py --stills 1,10
"""
import argparse
import math
import os
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import decors as D  # noqa: E402
import decors_colis as C  # noqa: E402
import ui  # noqa: E402
import voix  # noqa: E402
from accroches_demo import carton_vole, neige, sapin  # noqa: E402
from dessin import INK, LW, ROOT, back, circle, ease, ecrit, flat, paint, poly, rrect, stroke  # noqa: E402
from film import Film  # noqa: E402
from perso import Perso, traits_choc  # noqa: E402

DIAL = ROOT / "scripts/modele/43_colis_abime.dial"
VOIX = {"nar": (os.environ.get("YANN_VOICE_ID", voix.YANN), voix.REGLAGES_YANN),
        "soeur": ("Y2uuwzlt8SyNkjrPovVI", voix.REGLAGES_YANN)}           # Natacha (fr)

MARQUES = {0: [("Quatre cent cinquante euros", "[{}]")], 1: [("ma grande sœur", "{{{}}}")],
           3: [("c'est pas ton problème", "{{{}}}")], 4: [("fendu en deux", "{{{}}}")],
           6: [("Bravo le génie", "{{{}}}")], 8: [("Bravo le génie", "{{{}}}")],
           10: [("ça empêche pas de réclamer", "[{}]")], 11: [("un message écrit au vendeur", "[{}]")],
           14: [("Il avait tout jeté", "{{{}}}")], 15: [("une console neuve", "[{}]")],
           16: [("cabossé", "{{{}}}")], 18: [("Quatre cent cinquante euros", "[{}]")]}

KEVIN = dict(cheveux="boucles", couleur_cheveux=(30, 24, 30), peau=(198, 138, 98), haut="sweat",
             couleur_haut=(46, 170, 120), bas=(56, 70, 120), chaussures=(245, 245, 245), seed=1)
SOEUR = dict(cheveux="chignon", couleur_cheveux=(30, 24, 30), peau=(200, 142, 104), haut="sweat",
             couleur_haut=(150, 70, 170), bas=(50, 50, 70), seed=110)
YANIS = dict(cheveux="court", couleur_cheveux=(40, 30, 30), peau=(170, 110, 80), haut="sweat",
             couleur_haut=(240, 150, 40), bas=(50, 60, 90), seed=111)
LIVREUR = dict(cheveux="court", couleur_cheveux=(40, 30, 30), peau=(220, 170, 130), haut="polo",
               couleur_haut=(240, 170, 30), bas=(50, 50, 60), seed=90)


def console(ctx, x, y, s, fendu=0.0, rot=0.0):
    """Console de salon (écran portable) ; fendu 0 → 1 : la fissure se dessine."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    rrect(ctx, -330, -140, 660, 280, 70)
    paint(ctx, (40, 40, 50), LW, shade=0.9)
    for sx, c in ((-260, (230, 60, 70)), (260, (60, 120, 230))):
        rrect(ctx, sx - 60, -120, 120, 240, 50)
        paint(ctx, c, LW * 0.8, shade=0.85)
        circle(ctx, sx, -40, 24)
        flat(ctx, (30, 30, 36))
    rrect(ctx, -190, -110, 380, 220, 12)
    paint(ctx, (90, 160, 230), LW * 0.7, shade=1)
    if fendu > 0:
        pts = [(-170, -100), (-60, -20), (-90, 30), (40, 10), (10, 70), (170, 100)]
        n = max(2, int(len(pts) * min(1.0, fendu)))
        ctx.move_to(*pts[0])
        for p in pts[1:n]:
            ctx.line_to(*p)
        stroke(ctx, 7, (250, 250, 255))
        ctx.move_to(-60, -20)
        ctx.line_to(-40, -100)
        ctx.move_to(40, 10)
        ctx.line_to(120, -60)
        stroke(ctx, 4, (250, 250, 255), alpha=min(1.0, fendu))
    ctx.restore()


def lignes():
    out = []
    for ligne in open(DIAL, encoding="utf-8"):
        if ligne[:2] not in ("M:", "N:"):
            continue
        txt = ligne[2:].strip()
        for a, motif in MARQUES.get(len(out), []):
            assert a in txt, (len(out), a)
            txt = txt.replace(a, motif.format(a), 1)
        out.append(("soeur" if ligne[0] == "M" else "nar", txt))
    return out


def construire(work):
    voice, words = voix.build(lignes(), VOIX, work, gap=0.2, cible=voix.CIBLE)
    f = Film(voice, words)

    def L(li, k=0, fin=False):
        ws = [w for w in words if w["line"] == li]
        return ws[k]["t1" if fin else "t0"]

    def W(li, prefixe, n=0, fin=False):
        ws = [w for w in words if w["line"] == li and
              re.sub(r"[^\w'-]", "", w["w"].lower()).startswith(prefixe.lower())]
        return ws[n]["t1" if fin else "t0"]

    def plan(li, scene, *plans, hud=None):
        t0 = L(li, 0)
        cam = [(0 if ta is None else max(0.0, ta - t0 - 0.04), x, y, z) for ta, x, y, z in plans]
        f.plan(L(li, 0) if li else 0, scene, cam, fouet=bool(li), hud=hud)

    kev, soeur, yanis, livreur = Perso(**KEVIN), Perso(**SOEUR), Perso(**YANIS), Perso(**LIVREUR)
    f_t = [0.0]
    kev.objet = lambda c, x, y, s: D.telephone(c, x - 10, y - 60, 0.9, rot=-0.1)
    soeur.objet = lambda c, x, y, s: D.telephone(c, x - 10, y - 60, 0.8, rot=-0.1)
    yanis.objet = lambda c, x, y, s: None
    livreur.objet = lambda c, x, y, s: D.telephone(c, x + 30, y - 90, 0.8, rot=0.3)

    t_crash = 0.55
    kev.pose(0, "repos").emotion(0, "content").pose(t_crash, "leve").emotion(t_crash, "choc")
    kev.pose(L(2, 0), "repos").emotion(L(2, 0), "content").pose(L(4, 0), "objet").emotion(L(4, 0), "choc")
    kev.pose(L(5, 0), "pointe").emotion(L(5, 0), "colere").pose(L(7, 0), "repos").emotion(L(7, 0), "triste")
    kev.pose(L(12, 0), "haussement").pose(L(13, 0), "telephone").emotion(L(13, 0), "malin")
    kev.pose(L(15, 0), "leve").emotion(L(15, 0), "content").pose(L(16, 0), "repos").emotion(L(16, 0), "malin")
    soeur.pose(0, "mains_hanches").emotion(0, "malin").emotion(L(5, 0), "content").pose(L(6, 0), "pointe_g")
    soeur.emotion(L(6, 0), "content").pose(L(16, 0), "objet").emotion(L(16, 0), "triste")
    soeur.pose(L(17, 0), "telephone").emotion(L(17, 0), "triste")
    yanis.pose(0, "repos").emotion(0, "choc").emotion(W(14, "il", 0) if True else 0, "triste")
    livreur.pose(0, "pointe_g").emotion(0, "malin")

    def bouche(t, qui):
        return f.bouche(t, qui) * (0.7 if qui == "nar" else 1.0)

    tete = lambda x, y, s: (x, y - s * 880)          # noqa: E731

    def salon(ctx, t):
        D.salon(ctx, t)
        ctx.rectangle(-600, -600, 2400, 3200)
        flat(ctx, (20, 20, 60), 0.3)
        sapin(ctx, 960, 1560, 0.85, t)

    # ── scènes ──
    def s_hook(ctx, t, lt):
        f_t[0] = t
        C.palier(ctx, t, mot=False, colis=0)
        kev.draw(ctx, 260, 1880, 0.9, t)
        if t < t_crash:
            y = -250 + 1650 * (t / t_crash) ** 2
            carton_vole(ctx, 600, y, 0.95, 0.5 * t, 0, t)
        else:
            k = min((t - t_crash) / 0.6, 1.0) * 0.55
            carton_vole(ctx, 600, 1400, 0.95, 0, max(0.02, k), t)
            console(ctx, 600, 1450, 0.5, fendu=(t - t_crash) / 0.5, rot=-0.2)
        ui.panneau(ctx, 640, 520, "450 €", lt, rot=-0.05, size=120, fond=(255, 210, 40), bord=INK, col=INK)
        if t >= 1.6:                             # la sœur entre à 2 s
            x = 1250 - 400 * ease((t - 1.6) / 0.5)
            soeur.draw(ctx, x, 1860, 0.88, t, bouche=bouche(t, "soeur"))
        if t >= W(0, "quatre") - 0.1:
            ui.panneau(ctx, 540, 760, "À LA POUBELLE ?", t - W(0, "quatre") + 0.1, rot=0.04, size=70)

    def s_salon(ctx, t, lt):
        f_t[0] = t
        salon(ctx, t)
        soeur.draw(ctx, 760, 1840, 0.88, t, bouche=bouche(t, "soeur"))
        kev.draw(ctx, 280, 1880, 0.9, t, bouche=bouche(t, "nar"))
        if L(1, 0) <= t < L(2, 0) and t >= W(1, "ma"):
            ui.badge(ctx, 760, 1840 - 0.88 * 1150, "MA GRANDE SŒUR", t - W(1, "ma"))
        if L(5, 0) <= t < L(6, 0) and t >= W(5, "c'est"):
            ui.bulle(ctx, 540, 640, "C'est lui qui l'a balancé !", t - W(5, "c'est"), size=46)
        neige(ctx, t, n=25)

    def s_console(ctx, t, lt):
        f_t[0] = t
        salon(ctx, t)
        kev.draw(ctx, 300, 1880, 0.9, t, bouche=bouche(t, "nar"))
        console(ctx, 640, 900, 0.9 * back(lt / 0.3), rot=0.04)
        if t >= W(2, "six"):
            ui.panneau(ctx, 640, 1200, "6 MOIS D'ÉCONOMIES", t - W(2, "six"), rot=-0.04, size=66, fond=(255, 210, 40),
                       bord=INK, col=INK)
        neige(ctx, t, n=25)

    def s_livreur(ctx, t, lt):
        f_t[0] = t
        C.palier(ctx, t, mot=False, colis=0)
        livreur.draw(ctx, 820, 1820, 0.88, t)
        kev.draw(ctx, 280, 1880, 0.9, t, bouche=bouche(t, "nar"))
        k = min(1.0, lt / 1.0)
        if lt < 1.0:
            carton_vole(ctx, 800 - 300 * k, 900 + 600 * k * k - 400 * k, 0.8, 4 * k, 0, t)
        else:
            C.carton(ctx, 500, 1520, 0.8, rot=0.3, label="FRAGILE")
        if t >= W(3, "signe") - 0.1:
            ui.bulle(ctx, 540, 640, "Signe là, c'est pas ton problème !", t - W(3, "signe") + 0.1, size=44, cote=-1)

    def s_fendu(ctx, t, lt):
        f_t[0] = t
        D.fond_sombre(ctx, t, (30, 30, 50))
        console(ctx, 540, 900, 1.25, fendu=(t - W(4, "l'écran")) / 0.4 if t >= W(4, "l'écran") else 0.0,
                rot=-0.03 + 0.01 * math.sin(t * 2))
        if t >= W(4, "fendu"):
            ui.panneau(ctx, 540, 1250, "FENDU EN DEUX", t - W(4, "fendu"), rot=-0.05, size=90)

    def s_soeur(ctx, t, lt):
        f_t[0] = t
        salon(ctx, t)
        soeur.draw(ctx, 540, 1800, 0.95, t, bouche=bouche(t, "soeur"))
        traits_choc(ctx, 540, 1800 - 0.95 * 880, 160, lt)
        if t >= W(6, "bravo") - 0.05:
            ui.panneau(ctx, 540, 520, "« BRAVO LE GÉNIE »", t - W(6, "bravo") + 0.05, rot=0.04, size=72)

    def s_kev(ctx, t, lt):
        f_t[0] = t
        salon(ctx, t)
        kev.draw(ctx, 540, 1840, 0.95, t, bouche=bouche(t, "nar"))
        if t >= L(12, 0):
            ctx.rectangle(-600, -600, 2400, 3200)
            flat(ctx, (30, 20, 70), 0.3)
            if t >= W(12, "le", 0):
                ui.bulle(ctx, 540, 600, "Le vendeur a rien cassé…", t - W(12, "le", 0), size=46)

    def s_echo(ctx, t, lt):
        salon(ctx, t)
        ctx.rectangle(-600, -600, 2400, 3200)
        flat(ctx, (10, 10, 30), 0.5)
        ui.panneau(ctx, 540, 900, "BRAVO LE GÉNIE.", lt, rot=-0.05, size=100)

    def s_fond(ctx, t, lt):
        D.fond_sombre(ctx, t, (26, 40, 44))
        __import__("decors_liste").rayons(ctx, 540, 700, t * 2.5, (120, 200, 190), alpha=0.12)
        __import__("decors_liste").pieces_flottantes(ctx, t * 2.0, n=26)

    t_r = L(9, 0)

    def h_regle(ctx, t, lt):
        ctx.save()
        ctx.translate(18 * math.sin(t * 1.6), 22 * math.sin(t * 1.1))
        ctx.rotate(0.015 * math.sin(t * 1.3))
        ui.carte_regle(ctx, t - t_r, "LA RÈGLE", [
            (0.15, "Achat en ligne : le vendeur\nrépond jusqu'à ta porte", "le vendeur"),
            (W(10, "signer") - t_r, "Bon signé sans réserve ?\nTu peux quand même réclamer", "réclamer"),
            (W(10, "un", 0) - t_r, "Neuf et cassé : présumé\ndéfectueux dès la livraison", "présumé"),
        ], y0=300)
        ctx.restore()
        ecrit(ctx, "Code de la consommation, art. L221-15, L216-4 et L217-7", 540, 1150, 26, (230, 230, 236))

    def s_quoi(ctx, t, lt):
        s_fond(ctx, t, lt)
        k = back(lt / 0.3)
        ctx.save()
        ctx.translate(540 + 18 * math.sin(t * 1.6), 860 + 22 * math.sin(t * 1.1))
        ctx.rotate(0.02 * math.sin(t * 1.3))
        ctx.scale(k, k)
        rrect(ctx, -430, -320, 860, 640, 30)
        paint(ctx, (250, 248, 240), 6, shade=0.95)
        ecrit(ctx, "Je fais quoi ?", 0, -230, 60, INK, big=True)
        if t >= W(11, "des"):
            ecrit(ctx, "1. Photos du carton", -370, -90, 52, (40, 110, 200), big=True, ax=0)
            ecrit(ctx, "    et du produit", -370, -20, 52, (40, 110, 200), big=True, ax=0)
        if t >= W(11, "un"):
            ecrit(ctx, "2. Message écrit", -370, 80, 52, (40, 110, 200), big=True, ax=0)
            ecrit(ctx, "    au VENDEUR", -370, 150, 52, (40, 110, 200), big=True, ax=0)
        if t >= W(11, "tout") - 0.1:
            ecrit(ctx, "TOUT DE SUITE", 0, 250, 60, (210, 40, 50), big=True, scale=back((t - W(11, "tout") + 0.1) / 0.3))
        ctx.restore()

    def ecran_msg(c, x0, y0, w, h, t):
        ecrit(c, "20 déc. 21:40", x0 + w / 2, y0 + 30, 24, (120, 120, 130))
        C.bulle_msg(c, x0, y0 + 70, w, "Bonjour, console reçue l'écran fendu. Photos et film du livreur joints. "
                    "Je demande un échange.", True, ease((t - L(13, 0)) / 0.3), size=32)
        for i in range(2):
            rrect(c, x0 + 40 + i * 260, y0 + 370, 230, 300, 14)
            paint(c, (60, 70, 90), 3, shade=1)
        console(c, x0 + 155, y0 + 520, 0.3, fendu=1.0)
        ecrit(c, "▶", x0 + 415, y0 + 520, 80, (255, 255, 255), big=True)
        ecrit(c, "film voisine", x0 + 415, y0 + 630, 24, (255, 255, 255))

    def s_message(ctx, t, lt):
        C.chambre(ctx, t)
        ctx.rectangle(-600, -600, 2400, 3200)
        flat(ctx, (16, 18, 30), 0.6)
        C.grand_tel(ctx, 540, 900, 0.95, "Service client", couleur=(40, 110, 200),
                    contenu=lambda c, *a: ecran_msg(c, *a, t), t=t)

    def s_yanis(ctx, t, lt):                    # TEST partage : le pote concerné
        f_t[0] = t
        C.chambre(ctx, t)
        kev.draw(ctx, 330, 1880, 0.9, t)
        yanis.draw(ctx, 780, 1860, 0.88, t)
        ui.badge(ctx, 780, 1860 - 0.88 * 1150, "YANIS, MON POTE", lt)
        if t >= W(14, "sa"):
            ui.panneau(ctx, 640, 600, "SA TÉLÉ : FENDUE", t - W(14, "sa"), rot=-0.04, size=64)
        if t >= W(14, "il", 0) - 0.1:
            ui.panneau(ctx, 640, 780, "IL AVAIT TOUT JETÉ", t - W(14, "il", 0) + 0.1, rot=0.04, size=60,
                       fond=(250, 250, 250), bord=(210, 40, 50), col=(210, 40, 50))

    def s_neuve(ctx, t, lt):
        f_t[0] = t
        C.palier(ctx, t, mot=False, colis=0)
        livreur.draw(ctx, 840, 1820, 0.85, t)
        kev.draw(ctx, 300, 1880, 0.9, t, bouche=bouche(t, "nar"))
        console(ctx, 560, 1300, 0.55 * back(lt / 0.3), rot=0.05)
        if t >= W(15, "j'ouvre"):
            ui.panneau(ctx, 560, 600, "J'OUVRE DEVANT LE LIVREUR", t - W(15, "j'ouvre"), rot=-0.04, size=56,
                       fond=(70, 205, 115), bord=INK, col=INK)

    def s_porte(ctx, t, lt):
        f_t[0] = t
        C.palier(ctx, t, mot=False, colis=0)
        soeur.draw(ctx, 760, 1860, 0.9, t)
        C.carton(ctx, 560, 1560, 0.6, rot=-0.2, label="CABOSSÉ")
        kev.draw(ctx, 280, 1880, 0.9, t, bouche=bouche(t, "nar"))
        if t >= L(17, 0):
            ui.bulle(ctx, 540, 560, "Ton modèle de message ?", t - L(17, 0), size=42, cote=-1)

    def s_final(ctx, t, lt):
        f_t[0] = t
        salon(ctx, t)
        kev.draw(ctx, 380, 1880, 0.92, t, bouche=bouche(t, "nar"))
        console(ctx, 760, 1350, 0.5, rot=0.05)
        ui.panneau(ctx, 540, 520, "450 € SAUVÉS", lt, rot=-0.04, size=110, fond=(70, 205, 115), bord=INK, col=INK)
        if lt > 0.8:
            ui.panneau(ctx, 560, 720, "BRAVO LE GÉNIE", lt - 0.8, rot=0.04, size=70)
        neige(ctx, t, n=25)

    # ── plans (caméra « plans » : un gros plan calé sur chaque mot clé) ──
    plan(0, s_hook, (None, 540, 1050, 1.0), (t_crash + 0.05, 600, 1300, 1.45), (1.7, 620, 1100, 1.05),
         (W(0, "quatre"), 600, 900, 1.25))
    plan(1, s_salon, (None, 540, 1100, 1.0), (W(1, "ma"), 760, 1050, 1.45))
    plan(2, s_console, (None, 540, 1050, 1.0), (W(2, "six"), 640, 1000, 1.4))
    plan(3, s_livreur, (None, 540, 1100, 1.0), (W(3, "signe"), 700, 900, 1.35))
    plan(4, s_fendu, (None, 540, 960, 1.0), (W(4, "fendu"), 540, 1000, 1.3))
    plan(5, s_salon, (None, 540, 1100, 1.0), (W(5, "c'est"), 400, 900, 1.4), (W(5, "ma"), 760, 1050, 1.4))
    plan(6, s_soeur, (None, *tete(540, 1800, 0.95), 1.6), (W(6, "bravo"), 540, 700, 1.8))
    plan(7, s_kev, (None, *tete(540, 1840, 0.95), 1.7))
    plan(8, s_echo, (None, 540, 960, 1.0), (L(8, 0) + 0.5, 540, 900, 1.3))
    plan(9, s_fond, (None, 540, 960, 1.0), (W(10, "signer"), 560, 980, 1.25), (W(10, "un", 0), 520, 940, 1.12),
         hud=h_regle)
    plan(11, s_quoi, (None, 540, 860, 1.0), (W(11, "tout"), 540, 1060, 1.45))
    plan(12, s_kev, (None, 540, 1150, 1.0), (W(12, "le", 0), 540, 800, 1.4))
    plan(13, s_message, (None, 540, 900, 1.0), (W(13, "voisine"), 640, 1000, 1.4))
    plan(14, s_yanis, (None, 540, 1100, 1.0), (W(14, "sa"), 640, 700, 1.45), (W(14, "il", 0), 700, 1000, 1.3))
    plan(15, s_neuve, (None, 540, 1100, 1.0), (W(15, "une"), 560, 1200, 1.5), (W(15, "j'ouvre"), 540, 900, 1.15))
    plan(16, s_porte, (None, 540, 1100, 1.0), (W(16, "cabossé"), 620, 1300, 1.4), (L(17, 0), 600, 1000, 1.2))
    plan(18, s_final, (None, 540, 1050, 1.0), (W(18, "bravo"), 540, 900, 1.2))

    # ── compteur, sous-titres, sons ──
    f.ecran(lambda ctx, t: ui.compteur(ctx, t, "SAUVÉ PAR KÉVIN", [(0, 0), (W(15, "une") + 0.3, 450)],
                                       apparition=L(1, 0)))
    groupes = ui.decouper(words)
    f.ecran(lambda ctx, t: ui.sous_titres(ctx, t, groupes, y=1330))
    for tt, son, g in [(t_crash, "impact", 0.9), (t_crash + 0.05, "rate", 0.6), (1.6, "whoosh", 0.4),
                       (W(0, "quatre"), "tampon", 0.6), (W(2, "six"), "pop", 0.5), (W(3, "signe"), "pop", 0.5),
                       (W(4, "fendu"), "rate", 0.7), (W(6, "bravo"), "impact", 0.8), (L(8, 0), "ticks", 0.4),
                       (W(10, "signer"), "pop", 0.5), (W(11, "tout"), "tampon", 0.5), (L(13, 0), "notif", 0.7),
                       (W(14, "il", 0), "rate", 0.5), (W(15, "une"), "succes", 0.8), (W(16, "cabossé"), "impact", 0.6),
                       (L(18, 0), "tampon", 0.7)]:
        f.son(tt, son, g)
    f.secousse(t_crash, 16)
    f.secousse(L(6, 0), 14)
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills")
    ap.add_argument("--out", default=str(ROOT / "output/trait/colis_abime.mp4"))
    a = ap.parse_args()
    work = ROOT / "output/trait/_work_colis_abime"
    f = construire(work)
    print(f"durée {f.dur:.1f} s, {len(f.plans)} plans")
    if a.stills:
        f.stills([float(x) for x in a.stills.split(",")], work / "stills")
    else:
        print("→", f.render(a.out))


if __name__ == "__main__":
    main()
