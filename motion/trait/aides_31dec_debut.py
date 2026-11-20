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

# Chaque domino est 1,236 fois plus grand que le précédent (comme l'original : le 1er arrive au genou,
# le 6e dépasse le héros). L'écart = la moitié de la hauteur, pour que chacun tombe pile sur le suivant.
ECH = [1.16 * 1.236 ** i for i in range(6)]
HT = [280 * s for s in ECH]
LG = [150 * s for s in ECH]
XD = [470.0]
for _i in range(5):
    XD.append(XD[-1] + LG[_i] + 0.5 * HT[_i])
CENTRE = [x + w / 2 for x, w in zip(XD, LG)]
A_CHOC = math.asin(0.5)            # angle où le haut du domino touche le suivant
X_PATRON = XD[5] + LG[5] + 250


def construire(work):
    voice, words = voix.build(LIGNES, VOIX, work, speed=1.15)
    f = Film(voice, words)
    T = f.t
    kev, pat, kev2 = Perso(**KEVIN), Perso(**PATRON), Perso(**KEVIN)
    kev.emotion(0, "neutre").emotion(1.0, "content")
    pat.pose(0, "mains_hanches").emotion(0, "neutre")
    pat.pose(T("patron"), "haussement").emotion(T("patron"), "malin")
    pat.emotion(T("parler"), "content")
    kev2.emotion(T("Kévin"), "neutre").emotion(T("90"), "choc")
    t31 = T("31")
    # le 1er domino penche déjà à t = 0 ; le 5e frappe le géant pile sur « 31 »
    DEB = -0.15
    D = (t31 - DEB) / 5

    def angle(i, t):
        t0 = DEB + i * D
        u = (t - t0) / D
        if u <= 0:
            return 0.0
        if u < 1:
            return A_CHOC * u * u                                    # chute qui accélère
        v = t - t0 - D
        rebond = 0.05 * math.exp(-v * 10) * abs(math.sin(v * 24))
        if i == 4:
            return A_CHOC - rebond                                   # reste appuyé contre le géant
        return A_CHOC + (1.36 - A_CHOC) * ease(v / (D * 1.3)) - rebond   # s'affaisse quand le suivant part

    def angle_geant(t):
        if t < t31:
            return 0.0
        v = t - t31
        return 0.03 * math.exp(-v * 3.5) * math.sin(v * 18)

    def cam_chaine(lt):
        t = lt
        fi = min(5.0, max(0.0, (t - DEB) / D - 0.35 + 0.95 * ease(t / 1.6)))   # démarre doucement puis devance la chute
        i = min(4, int(fi))
        k = fi - i
        cx = CENTRE[i] + (CENTRE[i + 1] - CENTRE[i]) * k - 190 * (1 - ease(t / 1.2))   # héros entier au début
        z = 1.18 * 1.236 ** (-0.35 * fi)
        if t > t31:
            cx -= 160 * ease((t - t31) / 0.8)
            z *= 1 + 0.025 * (t - t31)
        return cx, V.SOL - 230 / z, z

    # ── la chaîne de dominos devant la ville ──
    def chaine_objets(ctx, t):
        for i, (h, b) in enumerate(PETITS):
            V.domino(ctx, XD[i], V.SOL, ECH[i], angle(i, t), h, b)
        V.domino(ctx, XD[5], V.SOL, ECH[5], angle_geant(t), "soleil", "bus", "1 000 €",
                 lueur=1.0 if t >= T("plus") else 0.0, couleur=(250, 236, 170))
        kev.draw(ctx, 300, V.SOL, 0.72, t, regard=0.6)
        pat.draw(ctx, X_PATRON, V.SOL, 0.72, t, regard=-0.6)

    def chaine(ctx, t, lt):
        V.ville_nuit(ctx, t, x1=4700)
        V.reflet(ctx, lambda c: chaine_objets(c, t))
        chaine_objets(ctx, t)
        tc = T("avant") - 0.15                                      # le calendrier descend au bout d'une ficelle
        if t >= tc:
            from decors import calendrier
            y = -500 + (V.SOL - HT[5] - 30 + 500) * min(1.2, max(0.0, 1 - math.exp(-(t - tc) * 6)
                                                              * math.cos((t - tc) * 14)))
            xc = XD[5] - 170
            ctx.move_to(xc, -1500)
            ctx.line_to(xc, y - 150)
            from dessin import stroke
            stroke(ctx, 5)
            calendrier(ctx, xc, y, 1.0, "DÉC", "31")
        if t >= T("patron"):
            traits_choc(ctx, X_PATRON, V.SOL - 0.72 * 880, 140, t - T("patron"), color=(255, 255, 255))

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

    gx = XD[5] + LG[5] / 2
    f.plan(0, chaine, cam_chaine, fouet=False)                       # un seul travelling jusqu'à « La plus grosse »
    f.plan("plus", chaine, [(0, gx + 100, V.SOL - 440, 1.1), (1.4, gx + 120, V.SOL - 450, 1.18)])
    f.plan("patron", chaine, [(0, X_PATRON - 120, V.SOL - 520, 1.35), (1.6, X_PATRON - 100, V.SOL - 530, 1.45)])
    f.plan("Lundi", station, [(0, 540, 1050, 1.0), (1.2, 540, 1080, 1.12)])
    f.plan("Kévin", pompe, [(0, 560, 1040, 1.0), (2.0, 520, 1000, 1.12)])
    f.plan("90", pompe, [(0, 380, 900, 1.55), (1.2, 380, 900, 1.7)])
    f.plan("20", pompe, [(0, 820, 820, 1.6), (1.0, 820, 840, 1.7)])

    f.ecran(lambda ctx, t: ui.compteur(ctx, t, "RÉCUPÉRÉ AVANT LE 31/12", [(0, 0)], apparition=T("plus")))
    groupes = ui.decouper(words)
    f.ecran(lambda ctx, t: ui.sous_titres(ctx, t, groupes, y=1300))
    for i in range(4):
        f.son(DEB + (i + 1) * D, "pop", 0.45)                       # clac de chaque domino
    for mot, son, g in [("31", "impact", 0.8), ("plus", "succes", 0.5), ("patron", "pop", 0.7),
                        ("parler", "rate", 0.6), ("Kévin", "ticks", 0.5), ("90", "impact", 0.9), ("20", "pop", 0.7)]:
        f.son(mot, son, g)
    f.secousse("31", 8)
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
