"""Remake des 10 premières secondes de « 6 aides à récupérer avant le 31 décembre » (vidéo de @laficelle_off),
refaites dans notre style : même déroulé et même rythme, personnages / dessin / texte à nous.

    python3 motion/trait/aides_31dec_debut.py            → output/trait/aides_31dec_debut.mp4
    python3 motion/trait/aides_31dec_debut.py --stills 0.5,3,6
"""
import argparse
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import decors_ville as V  # noqa: E402
import ui  # noqa: E402
import voix  # noqa: E402
from dessin import ROOT, back, ease, halo  # noqa: E402
from film import Film  # noqa: E402
from perso import Perso, traits_choc  # noqa: E402

NARRATEUR = os.environ.get("ELEVENLABS_VOICE_ID", "cDpfdjuqlrxqLRo3BMFC")
VOIX = {"nar": (NARRATEUR, {"stability": 0.42, "similarity_boost": 0.8, "style": 0.25})}

LIGNES = [
    ("nar", "[Six aides] à récupérer avant le [31 décembre]. La plus grosse vaut jusqu'à [1 000 euros], "
            "et ton patron se gardera bien de t'en {parler}."),
    ("nar", "Lundi matin, Kévin fait le plein avant d'aller bosser. [90 euros], pour {20 kilomètres} de trajet."),
]

KEVIN = dict(cheveux="boucles", couleur_cheveux=(30, 24, 30), peau=(198, 138, 98), haut="sweat",
             couleur_haut=(46, 170, 120), bas=(56, 70, 120), chaussures=(245, 245, 245), seed=1)
PATRON = dict(cheveux="chauve", couleur_cheveux=(150, 150, 156), peau=(236, 186, 150), haut="chemise",
              couleur_haut=(44, 52, 86), bas=(36, 40, 60), chaussures=(30, 30, 36), lunettes=True, seed=3)

PETITS = [("points", "essence"), ("soleil", "flamme"), ("points", "maison"), ("soleil", "coeur"),
          ("points", "calendrier")]
X0, PAS, XG = 430, 200, 1450          # dominos : premier, écart, domino géant


def construire(work):
    voice, words = voix.build(LIGNES, VOIX, work, speed=1.15)
    f = Film(voice, words)
    T = f.t
    kev, pat, kev2 = Perso(**KEVIN), Perso(**PATRON), Perso(**KEVIN)
    kev.pose(0.15, "pointe").emotion(0, "neutre").emotion(1.4, "content")
    pat.pose(0, "mains_hanches").emotion(0, "neutre")
    pat.pose(T("patron"), "haussement").emotion(T("patron"), "malin")
    pat.emotion(T("parler"), "content")
    kev2.emotion(T("Kévin"), "neutre").emotion(T("90"), "choc")
    t31 = T("31")

    # ── la chaîne de dominos devant la ville ──
    def chaine_objets(ctx, t):
        for i, (h, b) in enumerate(PETITS):
            V.domino(ctx, X0 + i * PAS, V.SOL, 1.0, V.chute(t, 0.35 + i * 0.3), h, b)
        if t >= t31 - 0.25:
            k = back((t - t31 + 0.25) / 0.4)
            vac = 0.03 * math.sin(t * 9) if t >= T("patron") else 0.0
            V.domino(ctx, XG, V.SOL, 2.4 * k, vac, "soleil", "bus", "1 000 €",
                     lueur=1.0 if t >= T("plus") else 0.4, couleur=(250, 236, 170))
        kev.draw(ctx, 250, V.SOL, 0.72, t, regard=0.5)
        pat.draw(ctx, 2020, V.SOL, 0.72, t, regard=-0.6)

    def chaine(ctx, t, lt):
        V.ville_nuit(ctx, t)
        V.reflet(ctx, lambda c: chaine_objets(c, t))
        chaine_objets(ctx, t)
        if t >= t31:
            from decors import calendrier
            calendrier(ctx, XG - 160, 640, 0.9 * back((t - t31) / 0.3), "DÉC", "31")
        if t >= T("patron"):
            traits_choc(ctx, 2020, V.SOL - 0.72 * 880, 140, t - T("patron"), color=(255, 255, 255))

    # ── station-service la nuit ──
    def station(ctx, t, lt):
        V.station(ctx, t)
        x = -500 + 1050 * (1 - (1 - min(1.0, lt / 0.9)) ** 3)
        V.voiture(ctx, x, 1400, 0.62, (40, 150, 170))

    # ── à la pompe ──
    def montant(t):
        a, b = T("Kévin"), T("90")
        return 90.0 * ease((t - a) / (b - a)) if t >= a else 0.0

    def pompe(ctx, t, lt):
        V._deg(ctx, -400, -400, 1500, 1500, (60, 46, 100), (190, 110, 120))
        V.immeubles(ctx, -400, 1500, 1350, t, seed=5, col=(70, 60, 110), hmin=200, hmax=560)
        V._deg(ctx, -400, 1450, 1500, 2400, (70, 70, 84), (40, 40, 52))
        V.panneau_route(ctx, 900, 760, "BUREAU →", "20 km")
        V.voiture(ctx, 860, 1620, 1.05, (40, 150, 170))
        V.pompe(ctx, 290, 1620, f"{montant(t):05.2f} €".replace(".", ","), t)
        kev2.draw(ctx, 640, 1760, 0.88, t, regard=-0.8)
        if t >= T("90"):
            d = t - T("90")
            traits_choc(ctx, 640, 1760 - 0.88 * 880, 140, d)
            for i in range(9):
                a = -1.2 + i * 0.32
                r = 160 + 900 * d * (0.7 + 0.1 * (i % 3))
                V.billet(ctx, 290 + math.cos(a) * r * 0.8, 840 + math.sin(a) * r * 0.6 + 400 * d * d, 1.1,
                         d * (3 + i) * (1 if i % 2 else -1))

    f.plan(0, chaine, [(0, 420, 1080, 1.05), (t31 - 0.1, 1150, 1080, 1.05)], fouet=False)
    f.plan("31", chaine, [(0, 1560, 1040, 0.95), (1.0, 1600, 1030, 1.0)])
    f.plan("plus", chaine, [(0, 1640, 1110, 1.25), (1.4, 1660, 1100, 1.35)])
    f.plan("patron", chaine, [(0, 1880, 1000, 1.35), (1.6, 1900, 980, 1.5)])
    f.plan("Lundi", station, [(0, 540, 1050, 1.0), (1.2, 540, 1080, 1.12)])
    f.plan("Kévin", pompe, [(0, 560, 1040, 1.0), (2.0, 520, 1000, 1.12)])
    f.plan("90", pompe, [(0, 380, 900, 1.55), (1.2, 380, 900, 1.7)])
    f.plan("20", pompe, [(0, 820, 820, 1.6), (1.0, 820, 840, 1.7)])

    f.ecran(lambda ctx, t: ui.compteur(ctx, t, "RÉCUPÉRÉ AVANT LE 31/12", [(0, 0)], apparition=t31))
    groupes = ui.decouper(words)
    f.ecran(lambda ctx, t: ui.sous_titres(ctx, t, groupes, y=1450))
    for i in range(5):
        f.son(0.35 + i * 0.3 + 0.3, "pop", 0.5)
    for mot, son, g in [("31", "impact", 0.8), ("plus", "succes", 0.5), ("patron", "pop", 0.7),
                        ("parler", "rate", 0.6), ("Kévin", "ticks", 0.5), ("90", "impact", 0.9), ("20", "pop", 0.7)]:
        f.son(mot, son, g)
    f.secousse("31", 12)
    f.secousse("90", 18)
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills")
    ap.add_argument("--out", default=str(ROOT / "output/trait/aides_31dec_debut.mp4"))
    a = ap.parse_args()
    work = ROOT / "output/trait/_work_aides31"
    f = construire(work)
    print(f"durée {f.dur:.1f} s, {len(f.plans)} plans")
    if a.stills:
        f.stills([float(x) for x in a.stills.split(",")], work / "stills")
    else:
        print("→", f.render(a.out))


if __name__ == "__main__":
    main()
