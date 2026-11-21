"""Garage qui facture des travaux non demandés (script 41, scripts/modele/41_garage_travaux.dial, bras TEST du T1)
en dessin animé, moteur « trait ». Kévin = Yann, le garagiste = Paul K. Voix v4 accélérée à 64 s.

    python3 motion/trait/garage_travaux.py                 → output/trait/garage_travaux.mp4
    python3 motion/trait/garage_travaux.py --stills 1,10
"""
import argparse
import math
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import decors as D  # noqa: E402
import decors_colis as C  # noqa: E402
import decors_garage as G  # noqa: E402
import ui  # noqa: E402
import voix  # noqa: E402
from dessin import INK, ROOT, back, ease, ecrit, flat, paint, rrect, stroke  # noqa: E402
from film import Film  # noqa: E402
from perso import Perso, traits_choc  # noqa: E402

DIAL = ROOT / "scripts/modele/41_garage_travaux.dial"
VOIX = {"nar": (os.environ.get("YANN_VOICE_ID", voix.YANN), voix.REGLAGES_YANN),
        "garagiste": (os.environ.get("MECHANT_VOICE_ID", "5l4ttmr4SKNgi0HnOelT"), voix.REGLAGES_YANN)}

MARQUES = {0: [("cinq cent cinquante et un euros", "[{}]")], 1: [("Quatre-vingt-neuf euros", "[{}]")],
           2: [("Six cent quarante euros", "{{{}}}")], 3: [("J'avais rien demandé", "{{{}}}")],
           5: [("c'était du carton", "{{{}}}")], 9: [("Du carton", "{{{}}}")],
           11: [("c'est à lui de prouver", "[{}]")], 12: [("par écrit", "[{}]")],
           14: [("vidange seule", "[{}]")], 16: [("quatre-vingt-neuf euros", "[{}]")],
           17: [("Onze fois des plaquettes", "{{{}}}")], 19: [("Cinq cent cinquante et un euros", "[{}]")]}

KEVIN = dict(cheveux="boucles", couleur_cheveux=(30, 24, 30), peau=(198, 138, 98), haut="sweat",
             couleur_haut=(46, 170, 120), bas=(56, 70, 120), chaussures=(245, 245, 245), seed=1)
GARAGISTE = dict(cheveux="chauve", couleur_cheveux=(120, 110, 100), peau=(232, 186, 150), haut="uni",
                 couleur_haut=(40, 80, 150), bas=(40, 80, 150), chaussures=(30, 30, 36), moustache=True, seed=60)
MERE = dict(cheveux="chignon", couleur_cheveux=(60, 46, 40), peau=(200, 140, 100), haut="gilet",
            couleur_haut=(190, 90, 110), bas=(70, 60, 90), seed=61)
CLIENTS = [dict(cheveux=h, couleur_cheveux=cc, peau=p, haut="uni", couleur_haut=c, bas=(70, 70, 84), seed=70 + i)
           for i, (h, cc, p, c) in enumerate([("court", (60, 40, 30), (230, 180, 140), (200, 120, 60)),
                                               ("chignon", (200, 200, 204), (236, 196, 166), (80, 150, 200)),
                                               ("plaque", (40, 40, 40), (170, 110, 80), (120, 160, 90))])]


def lignes():
    out = []
    for ligne in open(DIAL, encoding="utf-8"):
        if ligne[:2] not in ("M:", "N:"):
            continue
        txt = ligne[2:].strip()
        for a, motif in MARQUES.get(len(out), []):
            assert a in txt, (len(out), a)
            txt = txt.replace(a, motif.format(a), 1)
        out.append(("garagiste" if ligne[0] == "M" else "nar", txt))
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

    kev, gar, mere = Perso(**KEVIN), Perso(**GARAGISTE), Perso(**MERE)
    clients = [Perso(**c) for c in CLIENTS]
    f_t = [0.0]

    def objet_kev(ctx, x, y, s):
        t = f_t[0]
        if L(14, 0) <= t < L(16, 0):
            G.fiche(ctx, x, y - 90, 0.5, rot=-0.06)
        elif L(16, 0) <= t < L(17, 0):
            G.cles(ctx, x, y - 70, 0.9, rot=0.3 * math.sin(t * 5))
        else:
            D.telephone(ctx, x - 10, y - 60, 0.9, rot=-0.1)

    kev.objet = objet_kev
    gar.objet = lambda ctx, x, y, s: D.telephone(ctx, x + 35, y - 95, 0.7, rot=0.35)
    mere.objet = lambda ctx, x, y, s: None

    kev.pose(0, "leve_d").emotion(0, "content").pose(L(1, 0), "repos").emotion(L(1, 0), "neutre")
    kev.pose(L(2, 0), "oreille").emotion(L(2, 0), "choc").pose(L(4, 0), "pointe").emotion(L(4, 0), "neutre")
    kev.pose(L(8, 0), "repos").emotion(L(8, 0), "triste").emotion(L(13, 0), "triste").pose(L(13, 0), "haussement")
    kev.pose(L(14, 0), "objet").emotion(L(14, 0), "malin").pose(L(16, 0), "objet").emotion(L(16, 0), "content")
    kev.pose(L(17, 0), "repos").emotion(L(17, 0), "choc").pose(L(19, 0), "leve").emotion(L(19, 0), "content")
    gar.pose(0, "mains_hanches").emotion(0, "malin").pose(L(2, 0), "oreille").pose(L(4, 0), "mains_hanches")
    gar.emotion(L(5, 0), "content").emotion(L(7, 0), "colere").pose(L(7, 0), "pointe_g")
    gar.pose(L(14, 0), "repos").emotion(L(14, 0), "choc").emotion(L(15, 0), "triste").pose(L(15, 0), "haussement")
    mere.pose(0, "repos").emotion(0, "neutre").emotion(W(17, "onze"), "choc").pose(L(18, 0), "mains_hanches")
    mere.emotion(L(18, 0), "colere")
    for i, c in enumerate(clients):
        c.emotion(0, "neutre").emotion(L(7, 0), "choc").emotion(L(15, 0), "malin" if i else "content")

    def bouche(t, qui):
        return f.bouche(t, qui) * (0.7 if qui == "nar" else 1.0)

    tete = lambda x, y, s: (x, y - s * 880)          # noqa: E731

    def fond_flou(ctx, t, decor):
        decor(ctx, t)
        ctx.rectangle(-600, -600, 2400, 3200)
        flat(ctx, (16, 18, 30), 0.6)

    def accueil_complet(ctx, t, parle_g=True, k_x=320, g_x=780):
        G.accueil(ctx, t)
        for i, c in enumerate(clients):
            G.chaise(ctx, -40 + i * 170, 1620, 0.7, couleur=(60, 120, 190))
            c.draw(ctx, -40 + i * 170, 1560, 0.5, t)
        gar.draw(ctx, g_x, 1760, 0.9, t, bouche=bouche(t, "garagiste") if parle_g else 0.0)
        G.comptoir(ctx, g_x, 1380)
        kev.draw(ctx, k_x, 1860, 0.95, t, bouche=bouche(t, "nar"))

    # ── scènes ──
    def s_hook(ctx, t, lt):
        f_t[0] = t
        G.atelier(ctx, t, pont=0.0)
        kev.draw(ctx, 300, 1860, 0.95, t, bouche=bouche(t, "nar"))
        gar.draw(ctx, 800, 1820, 0.85, t)
        if t >= W(0, "cinq") - 0.1:
            ui.panneau(ctx, 560, 560, "551 € ÉCONOMISÉS", t - W(0, "cinq") + 0.1, rot=-0.04, size=72,
                       fond=(255, 210, 40), bord=INK, col=INK)
        if t >= W(0, "garagiste"):
            ui.badge(ctx, 760, 1820 - 0.85 * 1150, "LE GARAGISTE", t - W(0, "garagiste"))

    def s_depot(ctx, t, lt):
        f_t[0] = t
        G.atelier(ctx, t, pont=ease(lt / 3.0) * 0.7)
        kev.draw(ctx, 200, 1860, 0.85, t, bouche=bouche(t, "nar"))
        if t >= W(1, "vingt") and t < W(1, "quatre"):
            ui.panneau(ctx, 600, 640, "20 ANS", t - W(1, "vingt"), rot=0.04, size=90)
        if t >= W(1, "quatre") - 0.1:
            G.fiche(ctx, 760, 560, 0.85 * back((t - W(1, "quatre") + 0.1) / 0.3), rot=0.05,
                    signe=(t - W(1, "signée") + 0.2) / 0.5 if t >= W(1, "signée") - 0.2 else 0.0)

    def ecran_appel(c, x0, y0, w, h, t):
        ecrit(c, "Garage du Centre", x0 + w / 2, y0 + 120, 46, INK, big=True)
        ecrit(c, "appel en cours · 0:%02d" % min(59, int(max(0, t - L(2, 0)))), x0 + w / 2, y0 + 190, 28,
              (120, 120, 130))
        if t >= W(2, "six") - 0.1:
            k = back((t - W(2, "six") + 0.1) / 0.3)
            ecrit(c, "640 €", x0 + w / 2, y0 + 480, 150, (210, 40, 50), big=True, scale=k)
        elif t >= W(2, "prêt"):
            ecrit(c, "« C'est prêt »", x0 + w / 2, y0 + 480, 60, (40, 150, 80), big=True)

    def s_tel(ctx, t, lt):
        fond_flou(ctx, t, C.chambre)
        C.grand_tel(ctx, 540, 900, 0.95, "Appel", couleur=(236, 120, 40),
                    contenu=lambda c, *a: ecran_appel(c, *a, t), t=t)

    def s_facture(ctx, t, lt):
        D.fond_sombre(ctx, t, (40, 30, 36))
        lig = [("Vidange", "89 €"), ("Plaquettes", "180 €"), ("Disques", "220 €"), ("Essuie-glaces", "36 €"),
               ("Batterie", "115 €")]
        tl = [L(3, 0) - 0.4, W(3, "plaq"), W(3, "disq"), W(3, "essu"), W(3, "batt")]
        G.facture(ctx, 540, 720, 0.82 * back(lt / 0.3), lig, tl, t)
        if t >= W(3, "rien") - 0.2:
            ui.panneau(ctx, 560, 900, "NON DEMANDÉ", t - W(3, "rien") + 0.2, rot=-0.12, size=96,
                       fond=(250, 250, 250), bord=(210, 40, 50), col=(210, 40, 50))

    def s_accueil(ctx, t, lt):
        f_t[0] = t
        accueil_complet(ctx, t)
        if L(4, 0) <= t < L(5, 0) and t >= W(4, "trois"):
            ui.panneau(ctx, 260, 760, "3 CLIENTS", t - W(4, "trois"), rot=-0.05, size=70, fond=(255, 210, 40),
                       bord=INK, col=INK)

    def s_gar(ctx, t, lt):
        f_t[0] = t
        G.accueil(ctx, t)
        gar.draw(ctx, 540, 1800, 0.95, t, bouche=bouche(t, "garagiste"))
        G.comptoir(ctx, 540, 1420, w=700)
        if L(5, 0) <= t < L(6, 0) and t >= W(5, "c'était") - 0.05:
            ui.panneau(ctx, 540, 520, "« DU CARTON »", t - W(5, "c'était") + 0.05, rot=-0.04, size=80)
        if L(7, 0) <= t < L(8, 0):
            traits_choc(ctx, 540, 1800 - 0.95 * 880, 160, t - L(7, 0))
            if t >= W(7, "jeunes"):
                ui.panneau(ctx, 540, 500, "« LES JEUNES »", t - W(7, "jeunes"), rot=0.05, size=80)
        if t >= L(15, 0):
            ctx.rectangle(-600, -600, 2400, 3200)
            flat(ctx, (20, 20, 40), 0.15)

    def s_kev(ctx, t, lt):
        f_t[0] = t
        G.accueil(ctx, t)
        kev.draw(ctx, 540, 1800, 0.95, t, bouche=bouche(t, "nar"))
        if t >= L(13, 0):
            ctx.rectangle(-600, -600, 2400, 3200)
            flat(ctx, (30, 20, 70), 0.3)
            if t >= W(13, "freins"):
                ui.bulle(ctx, 560, 600, "freins neufs ?", t - W(13, "freins"), size=50)

    def s_echo(ctx, t, lt):
        G.accueil(ctx, t)
        ctx.rectangle(-600, -600, 2400, 3200)
        flat(ctx, (10, 10, 30), 0.45)
        ui.panneau(ctx, 540, 900, "DU CARTON", lt, rot=-0.05, size=110)

    t_carte = L(10, 0)

    def s_regle(ctx, t, lt):
        D.fond_sombre(ctx, t, (26, 40, 44))

    def h_regle(ctx, t, lt):
        ui.carte_regle(ctx, t - t_carte, "LA RÈGLE", [
            (0.15, "Il facture que\nce que t'as accepté", "ce que t'as accepté"),
            (W(11, "pour") - t_carte, "Travaux en plus ?", "en plus"),
            (W(11, "c'est") - t_carte, "C'est à LUI de prouver\nque t'as dit oui", "à LUI"),
        ], y0=330)
        ecrit(ctx, "Code civil, art. 1353 · Cass. civ. 1re, 25 mars 1997 et 2 nov. 2005", 540, 1140, 26,
              (230, 230, 236))

    def s_plan(ctx, t, lt):
        D.fond_sombre(ctx, t, (24, 34, 50))
        k = back(lt / 0.3)
        ctx.save()
        ctx.translate(540, 880)
        ctx.scale(k, k)
        rrect(ctx, -430, -340, 860, 680, 30)
        paint(ctx, (250, 248, 240), 6, shade=0.95)
        ecrit(ctx, "Il appelle pas avant ?", 0, -250, 54, INK, big=True)
        if t >= W(12, "tu"):
            ecrit(ctx, "1. Tu paies le signé", -360, -100, 56, (40, 150, 80), big=True, ax=0)
            ecrit(ctx, "89 €", 360, -100, 56, (40, 150, 80), big=True, ax=1)
        if t >= W(12, "reste"):
            ecrit(ctx, "2. Le reste :", -360, 40, 56, (210, 40, 50), big=True, ax=0)
            ecrit(ctx, "551 €", 360, 40, 56, (210, 40, 50), big=True, ax=1)
        if t >= W(12, "écrit") - 0.2:
            ecrit(ctx, "contesté PAR ÉCRIT", 0, 180, 66, INK, big=True,
                  scale=back((t - W(12, "écrit") + 0.2) / 0.3))
        ctx.restore()

    def s_fiche(ctx, t, lt):
        f_t[0] = t
        accueil_complet(ctx, t, parle_g=False)
        if t >= W(14, "vidange") - 0.1:
            G.fiche(ctx, 540, 760, 0.9 * back((t - W(14, "vidange") + 0.1) / 0.3), rot=-0.04,
                    surligne=ease((t - W(14, "vidange")) / 0.5))

    def s_cles(ctx, t, lt):
        f_t[0] = t
        accueil_complet(ctx, t, parle_g=False, k_x=420, g_x=820)
        if t >= W(16, "quatre") - 0.1:
            ui.panneau(ctx, 560, 560, "PAYÉ : 89 €", t - W(16, "quatre") + 0.1, rot=-0.04, size=90,
                       fond=(70, 205, 115), bord=INK, col=INK)

    def s_mere(ctx, t, lt):
        f_t[0] = t
        C.cuisine(ctx, t)
        n = min(11, int(max(0, t - W(17, "factures") + 0.2) * 5)) if t >= W(17, "factures") - 0.2 else 0
        G.pile_factures(ctx, 700, 1300, n, t, s=0.75)
        mere.draw(ctx, 300, 1820, 0.9, t)
        if t >= W(17, "onze") - 0.1:
            ui.panneau(ctx, 640, 520, "11 FOIS", t - W(17, "onze") + 0.1, rot=0.05, size=110, fond=(255, 210, 40),
                       bord=INK, col=INK)
        if t >= W(17, "dimanche"):
            ui.panneau(ctx, 640, 700, "ROULE LE DIMANCHE", t - W(17, "dimanche"), rot=-0.04, size=56)

    def s_mere_kev(ctx, t, lt):
        f_t[0] = t
        C.cuisine(ctx, t)
        mere.draw(ctx, 340, 1820, 0.9, t)
        kev.draw(ctx, 780, 1840, 0.9, t, bouche=bouche(t, "nar"))
        if t >= W(18, "lundi"):
            ui.panneau(ctx, 540, 560, "LUNDI, AU GARAGE", t - W(18, "lundi"), rot=0.04, size=70)

    def s_final(ctx, t, lt):
        f_t[0] = t
        G.atelier(ctx, t, pont=0.0)
        G.voiture(ctx, 820, 1600, 0.75, t=t)
        kev.draw(ctx, 300, 1860, 0.95, t, bouche=bouche(t, "nar"))
        ui.panneau(ctx, 540, 520, "640 €", lt, rot=-0.04, size=120, fond=(250, 250, 250), bord=(210, 40, 50),
                   col=INK)
        if lt > 0.6:
            ctx.move_to(380, 520)
            ctx.line_to(380 + 320 * ease((lt - 0.6) / 0.3), 520)
            stroke(ctx, 14, (210, 40, 50))
            ui.panneau(ctx, 560, 700, "89 €", lt - 0.8, rot=0.04, size=120, fond=(70, 205, 115), bord=INK, col=INK)

    # ── plans ──
    f.plan(0, s_hook, [(0, 540, 1000, 1.0), (2.5, 540, 1000, 1.08), (4.0, 420, 1100, 1.2)], fouet=False)
    f.plan(L(1, 0), s_depot, [(0, 540, 1100, 1.0), (2.5, 640, 1000, 1.2), (5.0, 700, 760, 1.35)])
    f.plan(L(2, 0), s_tel, [(0, 540, 760, 1.0), (1.5, 560, 880, 1.35), (3.0, 520, 960, 1.25)])
    f.plan(L(3, 0), s_facture, [(0, 540, 640, 1.25), (1.5, 540, 860, 1.0), (3.0, 540, 900, 1.1)])
    f.plan(L(4, 0), s_accueil, [(0, 260, 1150, 1.25), (2.5, 540, 1150, 1.0), (5.0, 700, 1050, 1.2)])
    f.plan(L(5, 0), s_gar, [(0, *tete(540, 1800, 0.95), 1.6), (2.0, *tete(540, 1810, 0.95), 1.8)])
    f.plan(L(6, 0), s_accueil, [(0, 200, 1250, 1.4), (1.5, 360, 1200, 1.2)])
    f.plan(L(7, 0), s_gar, [(0, *tete(540, 1790, 0.95), 1.9), (2.0, *tete(540, 1800, 0.95), 2.1)])
    f.plan(L(8, 0), s_kev, [(0, *tete(540, 1800, 0.95), 1.9), (1.2, *tete(540, 1800, 0.95), 2.05)])
    f.plan(L(9, 0), s_echo, [(0, 540, 960, 1.0), (1.2, 540, 960, 1.12)])
    f.plan(L(10, 0), s_regle, [(0, 540, 960, 1.0), (3, 620, 1000, 1.3), (6, 480, 920, 1.12), (9, 560, 980, 1.25)],
           hud=h_regle)
    f.plan(L(12, 0), s_plan, [(0, 540, 700, 1.35), (2.5, 540, 860, 1.0), (4.5, 540, 960, 1.3), (6.5, 540, 1040, 1.4)])
    f.plan(L(13, 0), s_kev, [(0, 540, 1150, 1.0), (2.0, *tete(540, 1800, 0.95), 1.7), (4.0, *tete(560, 1800, 0.95), 1.9)])
    f.plan(L(14, 0), s_fiche, [(0, 320, 1150, 1.3), (2.0, 540, 900, 1.15), (4.0, 560, 820, 1.35)])
    f.plan(L(15, 0), s_gar, [(0, *tete(540, 1800, 0.95), 1.9), (1.5, *tete(540, 1800, 0.95), 2.05)])
    f.plan(L(16, 0), s_cles, [(0, 420, 1100, 1.25), (2.0, 560, 1000, 1.05)])
    f.plan(L(17, 0), s_mere, [(0, 540, 1100, 1.0), (2.5, 640, 900, 1.2), (5.0, 600, 760, 1.35)])
    f.plan(L(18, 0), s_mere_kev, [(0, 540, 1150, 1.0), (2.0, 560, 1100, 1.15)])
    f.plan(L(19, 0), s_final, [(0, *tete(300, 1860, 0.95), 1.3), (2.0, 520, 1000, 1.1)])

    # ── compteur, sous-titres, sons ──
    f.ecran(lambda ctx, t: ui.compteur(ctx, t, "ÉCONOMISÉ PAR KÉVIN", [(0, 0), (W(16, "quatre") + 0.3, 551)],
                                       apparition=L(1, 0)))
    groupes = ui.decouper(words)
    f.ecran(lambda ctx, t: ui.sous_titres(ctx, t, groupes, y=1330))
    for tt, son, g in [(W(0, "cinq"), "pop", 0.7), (W(1, "quatre"), "pop", 0.6), (L(2, 0), "notif", 0.7),
                       (W(2, "six"), "impact", 0.8), (W(3, "plaq"), "pop", 0.5), (W(3, "disq"), "pop", 0.5),
                       (W(3, "essu"), "pop", 0.5), (W(3, "batt"), "pop", 0.5), (W(3, "rien"), "tampon", 0.7),
                       (W(5, "c'était"), "impact", 0.7), (L(7, 0), "impact", 0.8), (L(9, 0), "ticks", 0.4),
                       (W(11, "c'est"), "pop", 0.6), (W(12, "tu"), "pop", 0.5), (W(12, "écrit"), "succes", 0.5),
                       (W(14, "vidange"), "tampon", 0.7), (W(16, "quatre"), "succes", 0.8),
                       (W(17, "onze"), "impact", 0.7), (L(19, 0), "tampon", 0.6)]:
        f.son(tt, son, g)
    f.secousse(L(7, 0), 14)
    f.secousse(W(2, "six"), 8)
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills")
    ap.add_argument("--out", default=str(ROOT / "output/trait/garage_travaux.mp4"))
    a = ap.parse_args()
    work = ROOT / "output/trait/_work_garage"
    f = construire(work)
    print(f"durée {f.dur:.1f} s, {len(f.plans)} plans")
    if a.stills:
        f.stills([float(x) for x in a.stills.split(",")], work / "stills")
    else:
        print("→", f.render(a.out))


if __name__ == "__main__":
    main()
